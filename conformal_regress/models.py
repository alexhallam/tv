from __future__ import annotations

from typing import Optional, Tuple

import numpy as np

from .linalg import weighted_lstsq


def fit_ols(X: np.ndarray, y: np.ndarray) -> Tuple[np.ndarray, float, np.ndarray, np.ndarray]:
	return weighted_lstsq(X, y, w=None)


def fit_ridge(X: np.ndarray, y: np.ndarray, alpha: float = 1.0) -> Tuple[np.ndarray, float, np.ndarray, np.ndarray]:
	m, n = X.shape
	XtX = X.T @ X
	reg = alpha * np.eye(n)
	A = XtX + reg
	Xty = X.T @ y
	beta = np.linalg.solve(A, Xty)
	# Diagnostics
	try:
		A_inv = np.linalg.inv(A)
	except np.linalg.LinAlgError:
		A_inv = np.linalg.pinv(A)
	yhat = X @ beta
	e = y - yhat
	dof = max(m - n, 1)
	sigma2 = float((e @ e) / dof)
	hat_diag = np.sum((X @ A_inv) * X, axis=1)
	return beta, sigma2, A_inv, hat_diag


def fit_lasso(X: np.ndarray, y: np.ndarray, alpha: float = 1.0, max_iter: int = 1000, tol: float = 1e-6) -> Tuple[np.ndarray, float, np.ndarray, np.ndarray]:
	m, n = X.shape
	beta = np.zeros(n)
	X_col_norm2 = (X ** 2).sum(axis=0)
	for it in range(max_iter):
		beta_old = beta.copy()
		for j in range(n):
			residual = y - (X @ beta) + X[:, j] * beta[j]
			rho_j = X[:, j].dot(residual)
			if X_col_norm2[j] == 0:
				continue
			# Soft-thresholding
			if rho_j < -alpha:
				beta[j] = (rho_j + alpha) / X_col_norm2[j]
			elif rho_j > alpha:
				beta[j] = (rho_j - alpha) / X_col_norm2[j]
			else:
				beta[j] = 0.0
		if np.linalg.norm(beta - beta_old, ord=np.inf) < tol:
			break
	# Diagnostics
	XtX = X.T @ X
	try:
		XtX_inv = np.linalg.inv(XtX)
	except np.linalg.LinAlgError:
		XtX_inv = np.linalg.pinv(XtX)
	yhat = X @ beta
	e = y - yhat
	dof = max(m - (beta != 0).sum(), 1)
	sigma2 = float((e @ e) / dof)
	hat_diag = np.sum((X @ XtX_inv) * X, axis=1)
	return beta, sigma2, XtX_inv, hat_diag


def fit_huber(X: np.ndarray, y: np.ndarray, delta: float = 1.345, max_iter: int = 100, tol: float = 1e-6) -> Tuple[np.ndarray, float, np.ndarray, np.ndarray]:
	# IRLS for Huber loss
	m, n = X.shape
	beta, sigma2, XtX_inv, hat_diag = fit_ols(X, y)
	for it in range(max_iter):
		e = y - X @ beta
		# Scale estimate
		s = 1.4826 * np.median(np.abs(e - np.median(e))) + 1e-12
		u = e / (s * delta)
		w = 1.0 / np.maximum(1.0, np.abs(u))
		beta_new, sigma2, XtX_inv, hat_diag = weighted_lstsq(X, y, w=w)
		if np.linalg.norm(beta_new - beta, ord=np.inf) < tol:
			beta = beta_new
			break
		beta = beta_new
	return beta, sigma2, XtX_inv, hat_diag


def fit_quantile(X: np.ndarray, y: np.ndarray, tau: float = 0.5, max_iter: int = 2000, lr: float = 0.1) -> Tuple[np.ndarray, float, np.ndarray, np.ndarray]:
	# Simple gradient descent on pinball loss with small L2 to stabilize
	m, n = X.shape
	beta = np.zeros(n)
	l2 = 1e-6
	for it in range(max_iter):
		e = y - X @ beta
		grad = - (tau - (e < 0).astype(float)) @ X / m + 2 * l2 * beta
		beta -= lr * grad
		if np.linalg.norm(lr * grad) < 1e-6:
			break
	# Diagnostics from OLS around the solution
	XtX = X.T @ X
	try:
		XtX_inv = np.linalg.inv(XtX)
	except np.linalg.LinAlgError:
		XtX_inv = np.linalg.pinv(XtX)
	yhat = X @ beta
	e = y - yhat
	dof = max(m - n, 1)
	sigma2 = float((e @ e) / dof)
	hat_diag = np.sum((X @ XtX_inv) * X, axis=1)
	return beta, sigma2, XtX_inv, hat_diag