import pandas as pd
import glob

files = glob.glob("snapshots/*.parquet")
df = pd.concat([pd.read_parquet(f) for f in files])

print(df.head(20))