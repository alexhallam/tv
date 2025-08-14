from __future__ import annotations

import pandas as pd

try:
	from tidy_viewer_py import view as tv_view  # hypothetical package name
	has_tv = True
except Exception:  # pragma: no cover
	has_tv = False
	tv_view = None  # type: ignore


def view(df: pd.DataFrame) -> None:
	if has_tv:
		try:
			tv_view(df)
			return
		except Exception:
			pass
	print(df)