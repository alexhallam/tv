from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional, Tuple

import numpy as np
import pandas as pd

from .formula import build_matrices
from .models import (
	fit_ols,
	fit_ridge,
	fit_lasso,
	fit_huber,
	fit_quantile,
)
from .conformal import (
	ConformalSettings,
	compute_conformal_band,
	auto_select_conformal_mode,
)
from .summary import format_model_summary
from .viewing import view as _view

try:  # Optional JAX acceleration
	import jax  # type: ignore
	import jax.numpy as jnp  # type: ignore
	_HAS_JAX = True
except Exception:  # pragma: no cover
	_HAS_JAX = False
	jax = None  # type: ignore
	jnp = None  # type: ignore


@dataclass
class RegressModel:
	formula: str
	family: str
	method: str
	date_col: Optional[str]
	coefs: np.ndarray
	feature_names: list[str]
	dof_resid: int
	sigma2: Optional[float]
	xtx_inv: Optional[np.ndarray]
	hat_diag: Optional[np.ndarray]
	conformal_mode: Optional[str]
	conformal_quantiles: Optional[Dict[str, float]]
	coverage: Optional[float]
	training_rows: int
	calibration_rows: int
	_predict_jit: Optional[Any] = None

	def predict(self, new_data: pd.DataFrame, alpha_levels: Tuple[float, ...] = (0.1, 0.05)) -> pd.DataFrame:
		X_new, feature_names = build_matrices(self.formula, new_data, rhs_only=True)
		if feature_names != self.feature_names:
			raise ValueError("Feature mismatch between training and new_data.")
		if self._predict_jit is not None:
			yhat = np.asarray(self._predict_jit(X_new))
		else:
			yhat = X_new @ self.coefs

		# Build conformal intervals if available
		results = {
			"prediction": yhat,
		}
		if self.conformal_quantiles is not None:
			for a in alpha_levels:
				q = self.conformal_quantiles.get(f"q_{a}")
				if q is None:
					continue
				lower = yhat - q
				upper = yhat + q
				results[f"lower_{int((1-a)*100)}"] = lower
				results[f"upper_{int((1-a)*100)}"] = upper

		return pd.DataFrame(results)

	def forecast(self, horizon: int, future_exog: Optional[pd.DataFrame] = None, alpha_levels: Tuple[float, ...] = (0.1, 0.05)) -> pd.DataFrame:
		"""Forecast for a number of future steps.

		If the model only has an intercept, forecasts are repeated intercept values.
		Otherwise, provide future_exog with the RHS variables required by the formula.
		"""
		if len(self.feature_names) == 1 and self.feature_names[0] == "Intercept":
			X_new = np.ones((horizon, 1))
			new_df = pd.DataFrame({})
		else:
			if future_exog is None:
				raise ValueError("future_exog is required for forecasting with exogenous features.")
			X_new, feature_names = build_matrices(self.formula, future_exog, rhs_only=True)
			if feature_names != self.feature_names:
				raise ValueError("Feature mismatch between training and future_exog.")
			yhat = X_new @ self.coefs if self._predict_jit is None else np.asarray(self._predict_jit(X_new))
			new_df = future_exog.copy()
			results = {"prediction": yhat}
			if self.conformal_quantiles is not None:
				for a in alpha_levels:
					q = self.conformal_quantiles.get(f"q_{a}")
					if q is None:
						continue
					results[f"lower_{int((1-a)*100)}"] = yhat - q
					results[f"upper_{int((1-a)*100)}"] = yhat + q
			return pd.concat([new_df.reset_index(drop=True), pd.DataFrame(results)], axis=1)

		# Intercept-only path
		yhat = X_new @ self.coefs if self._predict_jit is None else np.asarray(self._predict_jit(X_new))
		results = {"prediction": yhat}
		if self.conformal_quantiles is not None:
			for a in alpha_levels:
				q = self.conformal_quantiles.get(f"q_{a}")
				if q is None:
					continue
				results[f"lower_{int((1-a)*100)}"] = yhat - q
				results[f"upper_{int((1-a)*100)}"] = yhat + q
		return pd.DataFrame(results)

	@property
	def coefficients(self) -> pd.DataFrame:
		return pd.DataFrame({
			"term": self.feature_names,
			"estimate": self.coefs,
		}).set_index("term")

	def __repr__(self) -> str:
		return format_model_summary(self)


def regress(
	formula: str,
	data: pd.DataFrame,
	*,
	family: str = "gaussian",
	method: str = "ols",
	alpha: Optional[float] = None,
	date_col: Optional[str] = None,
	uncertainty: Optional[str] = None,
	cv_method: Optional[str] = None,
	tau: float = 0.5,
	alpha_levels: Tuple[float, ...] = (0.1, 0.05),
	**kwargs: Any,
) -> RegressModel:
	"""Fit a regression model using formula syntax and optional conformal intervals.

	Parameters
	----------
	formula : str
		R-like formula (e.g., "y ~ x1 + x2 + x1:x2").
	data : pd.DataFrame
		Training data.
	family : str
		Distribution family (currently informational; 'gaussian' recommended).
	method : str
		One of {"ols", "ridge", "lasso", "quantile", "robust"}.
	date_col : Optional[str]
		Name of date column to enable temporal handling.
	uncertainty : Optional[str]
		Conformal mode: {None, "conformal", "conformal_thinning", "conformal_split", "conformal_temporal"}.
	cv_method : Optional[str]
		Temporal CV method (e.g., "rolling_origin").
	tau : float
		Quantile for quantile regression.
	alpha_levels : tuple of float
		Alpha levels for prediction bands.
	"""
	if date_col is not None and date_col not in data.columns:
		raise ValueError(f"date_col '{date_col}' not found in data")

	y, X, feature_names = build_matrices(formula, data)
	m, n = X.shape

	if method == "ols":
		coefs, sigma2, xtx_inv, hat_diag = fit_ols(X, y)
	elif method == "ridge":
		alpha_ridge = float(kwargs.get("alpha", 1.0))
		coefs, sigma2, xtx_inv, hat_diag = fit_ridge(X, y, alpha_ridge)
	elif method == "lasso":
		alpha_lasso = float(kwargs.get("alpha", 1.0))
		coefs, sigma2, xtx_inv, hat_diag = fit_lasso(X, y, alpha_lasso)
	elif method == "robust":
		loss = str(kwargs.get("loss", "huber"))
		coefs, sigma2, xtx_inv, hat_diag = fit_huber(X, y)
	elif method == "quantile":
		coefs, sigma2, xtx_inv, hat_diag = fit_quantile(X, y, tau=tau)
	else:
		raise ValueError(f"Unknown method: {method}")

	# Optional JAX-jitted predict
	predict_jit = None
	if _HAS_JAX:
		coefs_jax = jnp.asarray(coefs)
		def _pred(X_in):
			return jnp.asarray(X_in) @ coefs_jax
		predict_jit = jax.jit(_pred)

	conformal_mode = None
	conformal_quantiles: Optional[Dict[str, float]] = None
	coverage: Optional[float] = None
	training_rows = m
	calibration_rows = 0

	if uncertainty is not None:
		mode = uncertainty
		if mode == "conformal":
			mode = auto_select_conformal_mode(method=method, family=family, n=m)

		settings = ConformalSettings(
			mode=mode,
			alpha_levels=alpha_levels,
			date_col=date_col,
			cv_method=cv_method,
		)

		conformal_quantiles, coverage, training_rows, calibration_rows = compute_conformal_band(
			X, y, coefs, hat_diag, data=data, settings=settings
		)
		conformal_mode = settings.mode

	model = RegressModel(
		formula=formula,
		family=family,
		method=method,
		date_col=date_col,
		coefs=coefs,
		feature_names=feature_names,
		dof_resid=max(m - len(coefs), 1),
		sigma2=sigma2,
		xtx_inv=xtx_inv,
		hat_diag=hat_diag,
		conformal_mode=conformal_mode,
		conformal_quantiles=conformal_quantiles,
		coverage=coverage,
		training_rows=training_rows,
		calibration_rows=calibration_rows,
		_predict_jit=predict_jit,
	)
	return model


def view(df: pd.DataFrame) -> None:
	_view(df)