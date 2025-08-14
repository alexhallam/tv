import numpy as np
import pandas as pd
import conformal_regress as cr

rng = np.random.default_rng(0)
n = 200
x = rng.normal(size=n)
y = 3.0 + 2.0 * x + rng.normal(scale=1.0, size=n)

df = pd.DataFrame({"y": y, "x": x})

model = cr.regress("y ~ x", data=df, uncertainty="conformal", family="gaussian")
print(model)

new_df = pd.DataFrame({"x": [-1.0, 0.0, 1.0]})
preds = model.predict(new_df)
print(preds)