import numpy as np
import pandas as pd

df = pd.read_csv('output.csv')
df.info()

"""### Редкость"""

for v in df['редкость'].unique():
    print(v)
df['редкость'] = df['редкость'].replace({
    "очень частая": 5,
    "редко": 2,
    "1": 1,
    "2": 2,
    "часто": 4,
    "4": 4,
    "5": 5,
    "обычная": 3,
    "часто (хардмод)": 4,
    "прислужник босса": 3,
    np.nan: 3
})
for v in df['редкость'].unique():
    print(v)

"""### Время появления"""

for v in df['время появления'].unique():
    print(v)
df['время появления'] = df['время появления'].replace({
    "снежный биом + ночь": "ночь",
    "хардмод, любое время суток": "любое время суток",
    "всегда, хардмод": "всегда",
    np.nan: "часто"
})
for v in df['время появления'].unique():
    print(v)

"""### Без влияния гравитации"""

for v in df['без влияния гравитации'].unique():
    print(v)
df['без влияния гравитации'] = df['без влияния гравитации'].replace({
    np.nan: False
})
for v in df['без влияния гравитации'].unique():
    print(v)

"""### Проходит сквозь блоки"""

for v in df['проходит сквозь блоки'].unique():
    print(v)
df['проходит сквозь блоки'] = df['проходит сквозь блоки'].replace({
    np.nan: False
})
for v in df['проходит сквозь блоки'].unique():
    print(v)

"""### Итог"""

df.info()
df.to_csv('output_processed.csv', index=False)