from pathlib import Path

import pandas as pd

ABS = Path(__file__).resolve().parents[2]

df = pd.read_csv(ABS / 'map.csv')


a = 'a1'.upper()
print(a)
