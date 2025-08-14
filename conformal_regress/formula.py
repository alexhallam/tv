from __future__ import annotations

from typing import List, Tuple

import numpy as np
import pandas as pd

try:
	from formulaic import model_matrix as f_model_matrix
	has_formulaic = True
except Exception as e:  # pragma: no cover
	has_formulaic = False
	f_model_matrix = None  # type: ignore


def _fallback_parse(formula: str, data: pd.DataFrame, rhs_only: bool = False) -> Tuple[np.ndarray, ...]:
	# Very simple parser: 'y ~ x1 + x2' with intercept
	lhs, rhs = [s.strip() for s in formula.split("~", 1)]
	terms = [t.strip() for t in rhs.split("+") if t.strip()]
	X_cols = [np.ones(len(data))]
	feature_names = ["Intercept"]
	for t in terms:
		if t == "1":
			continue
		if t in ("0", "-1"):
			X_cols = []
			feature_names = []
			continue
		if t not in data.columns:
			raise ValueError(f"Unknown term in formula: {t}")
		X_cols.append(np.asarray(data[t], dtype=float))
		feature_names.append(t)
	X = np.vstack(X_cols).T if X_cols else np.zeros((len(data), 0))
	if rhs_only:
		return X, feature_names
	y = np.asarray(data[lhs], dtype=float)
	return y, X, feature_names


def build_matrices(formula: str, data: pd.DataFrame, rhs_only: bool = False) -> Tuple[np.ndarray, ...]:
	"""Build design matrices from a formula and DataFrame.

	If rhs_only is True, returns (X, feature_names). Otherwise returns (y, X, feature_names).
	Falls back to a minimal parser if formulaic is unavailable.
	"""
	lhs, rhs = [s.strip() for s in formula.split("~", 1)]
	if not has_formulaic:
		return _fallback_parse(formula, data, rhs_only=rhs_only)
	# Use formulaic for RHS design
	design_df = f_model_matrix(rhs, data)
	X = design_df.values
	feature_names: List[str] = list(design_df.columns)
	if rhs_only:
		return X, feature_names
	y = np.asarray(data[lhs], dtype=float)
	return y, X, feature_names