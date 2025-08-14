from __future__ import annotations

from typing import Optional, Tuple

import numpy as np

try:
	import randlapack as rlap  # type: ignore
	exists_randlapack = True
except Exception:  # pragma: no cover
	exists_randlapack = False
	rlap = None  # type: ignore


def weighted_lstsq(X: np.ndarray, y: np.ndarray, w: Optional[np.ndarray] = None) -> Tuple[np.ndarray, float, np.ndarray, np.ndarray]:
	"""Solve WLS using either randlapack (if available) or numpy lstsq.

	Returns (beta, sigma2, xtx_inv, hat_diag)
	"""
	m, n = X.shape
	if w is not None:
		w = np.asarray(w).reshape(-1)
		W_half = np.sqrt(w)
		Xw = X * W_half[:, None]
		yw = y * W_half
	else:
		Xw = X
		yw = y

	# Use numpy lstsq which relies on LAPACK under the hood
	beta, residuals, rank, s = np.linalg.lstsq(Xw, yw, rcond=None)

	# Compute sigma^2 and (X'X)^{-1}
	if w is None:
		XtX = X.T @ X
	else:
		XtX = X.T @ (X * w[:, None])
	try:
		XtX_inv = np.linalg.inv(XtX)
	except np.linalg.LinAlgError:
		XtX_inv = np.linalg.pinv(XtX)

	yhat = X @ beta
	e = y - yhat
	# Hat matrix diagonal via QR: H = X (X^T X)^{-1} X^T
	hat_diag = np.sum((X @ XtX_inv) * X, axis=1)
	dof = max(m - n, 1)
	sigma2 = float((e @ e) / dof)
	return beta, sigma2, XtX_inv, hat_diag