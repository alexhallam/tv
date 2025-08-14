from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Optional, Sequence, Tuple

import numpy as np
import pandas as pd


@dataclass
class ConformalSettings:
	mode: str
	alpha_levels: Tuple[float, ...]
	date_col: Optional[str] = None
	cv_method: Optional[str] = None


def auto_select_conformal_mode(method: str, family: str, n: int) -> str:
	# Prefer thinning when OLS + gaussian; cross-conformal for tiny n
	if n < 100:
		return "conformal_cross"
	if method == "ols" and family == "gaussian":
		return "conformal_thinning"
	return "conformal_split"


def compute_conformal_band(
	X: np.ndarray,
	y: np.ndarray,
	beta: np.ndarray,
	hat_diag: Optional[np.ndarray],
	*,
	data: pd.DataFrame,
	settings: ConformalSettings,
) -> Tuple[Dict[str, float], Optional[float], int, int]:
	mode = settings.mode
	alpha_levels = settings.alpha_levels
	date_col = settings.date_col

	if mode == "conformal_thinning":
		if hat_diag is None:
			raise ValueError("hat_diag required for thinning")
		e = y - X @ beta
		adj = np.maximum(1.0 - hat_diag, 1e-8)
		loo_resid = np.abs(e) / adj
		qs = {f"q_{a}": float(np.quantile(loo_resid, 1 - a)) for a in alpha_levels}
		# Approximate coverage using empirical fraction within 1 - min(alpha)
		min_a = min(alpha_levels)
		q_min = qs[f"q_{min_a}"]
		coverage = float(np.mean(np.abs(e) <= q_min))
		return qs, coverage, len(y), 0

	elif mode == "conformal_split":
		# 80/20 random split
		n = len(y)
		idx = np.arange(n)
		rng = np.random.default_rng(12345)
		rng.shuffle(idx)
		cut = int(0.8 * n)
		train_idx, cal_idx = idx[:cut], idx[cut:]
		beta_cal = _refit(X[train_idx], y[train_idx])
		resid = np.abs(y[cal_idx] - X[cal_idx] @ beta_cal)
		qs = {f"q_{a}": float(np.quantile(resid, 1 - a)) for a in alpha_levels}
		min_a = min(alpha_levels)
		q_min = qs[f"q_{min_a}"]
		coverage = float(np.mean(resid <= q_min))
		return qs, coverage, len(train_idx), len(cal_idx)

	elif mode == "conformal_cross":
		# 5-fold CV residuals
		n = len(y)
		k = min(5, max(2, n))
		idx = np.arange(n)
		rng = np.random.default_rng(12345)
		rng.shuffle(idx)
		folds = np.array_split(idx, k)
		resids = []
		for i in range(k):
			cal_idx = folds[i]
			train_idx = np.hstack([folds[j] for j in range(k) if j != i])
			beta_cv = _refit(X[train_idx], y[train_idx])
			resids.append(np.abs(y[cal_idx] - X[cal_idx] @ beta_cv))
		resid = np.concatenate(resids)
		qs = {f"q_{a}": float(np.quantile(resid, 1 - a)) for a in alpha_levels}
		min_a = min(alpha_levels)
		q_min = qs[f"q_{min_a}"]
		coverage = float(np.mean(resid <= q_min))
		return qs, coverage, n - len(resid), len(resid)

	elif mode == "conformal_temporal":
		if date_col is None or date_col not in data.columns:
			raise ValueError("date_col must be provided and present in data for temporal conformal")
		# Order by time, split 80/20 preserving order
		ordered = data.sort_values(by=date_col, kind="stable").reset_index(drop=True)
		# Rebuild matrices to honor the order
		# Warning: This assumes caller provided consistent X, y ordering originally
		n = len(ordered)
		cut = int(0.8 * n)
		train_idx = np.arange(cut)
		cal_idx = np.arange(cut, n)
		X_ord = X[np.argsort(data[date_col].to_numpy(), kind="stable")]
		y_ord = y[np.argsort(data[date_col].to_numpy(), kind="stable")]
		beta_cal = _refit(X_ord[train_idx], y_ord[train_idx])
		resid = np.abs(y_ord[cal_idx] - X_ord[cal_idx] @ beta_cal)
		qs = {f"q_{a}": float(np.quantile(resid, 1 - a)) for a in alpha_levels}
		min_a = min(alpha_levels)
		q_min = qs[f"q_{min_a}"]
		coverage = float(np.mean(resid <= q_min))
		return qs, coverage, len(train_idx), len(cal_idx)

	else:
		raise ValueError(f"Unknown conformal mode: {mode}")


def _refit(X: np.ndarray, y: np.ndarray) -> np.ndarray:
	# Light OLS refit for conformal routines
	beta, _, _, _ = np.linalg.lstsq(X, y, rcond=None)
	return beta