import polars as pl
df = pl.DataFrame({"a": [1.1, 2.2, 2.3, 3.4, 3.5, 3.6, 4.0, 5.0]})
h = df["a"].hist(bin_count=5)
print(h)
