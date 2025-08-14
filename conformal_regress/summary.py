from __future__ import annotations

from typing import Any, Optional

import numpy as np


def _format_p_value(p: float) -> str:
	if p < 2e-16:
		return "< 2e-16"
	return f"{p:.3g}"


def _t_p_values(t_stats: np.ndarray, dof: int) -> np.ndarray:
	# Use normal approximation for simplicity; avoids SciPy dependency
	from math import erf, sqrt
	cdf = lambda x: 0.5 * (1.0 + erf(x / sqrt(2)))
	p_two_sided = 2 * (1 - np.vectorize(cdf)(np.abs(t_stats)))
	return p_two_sided


def format_model_summary(model: Any) -> str:
	lines = []
	lines.append(f"Formula: {model.formula}")
	lines.append("")
	lines.append("Coefficients:")
	# Compute SE and t-values if available
	if model.sigma2 is not None and model.xtx_inv is not None:
		se = np.sqrt(np.clip(model.sigma2 * np.diag(model.xtx_inv), 0, None))
		with np.errstate(divide='ignore', invalid='ignore'):
			t_vals = np.where(se > 0, model.coefs / se, 0.0)
		p_vals = _t_p_values(t_vals, dof=model.dof_resid)
	else:
		se = np.full_like(model.coefs, np.nan)
		t_vals = np.full_like(model.coefs, np.nan)
		p_vals = np.full_like(model.coefs, np.nan)

	headers = f"{'':14s}{'Estimate':>12s} {'Std. Error':>12s} {'t value':>8s} {'Pr(>|t|)':>10s}"
	lines.append(headers)
	for name, est, se_i, t_i, p_i in zip(model.feature_names, model.coefs, se, t_vals, p_vals):
		p_str = _format_p_value(float(p_i)) if np.isfinite(p_i) else "NA"
		lines.append(f"{name:14s}{est:12.3f} {se_i:12.3f} {t_i:8.3f} {p_str:>10s}")
	lines.append("")
	if model.conformal_mode is not None:
		lines.append(f"Conformal Coverage: {model.coverage if model.coverage is not None else 'NA'} (method: {model.conformal_mode})")
	lines.append(f"Residual standard error: {np.sqrt(model.sigma2) if model.sigma2 is not None else float('nan'):.3f} on {model.dof_resid} degrees of freedom")
	return "\n".join(lines)