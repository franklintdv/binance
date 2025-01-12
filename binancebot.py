import pandas as pd

# Leia o arquivo CSV
df = pd.read_csv('custom_interval.csv', header=None, names=['number'])

# Remova os duplicados
df_unique = df.drop_duplicates()

# Salve o resultado em um novo arquivo CSV
df_unique.to_csv('custom_interval_unique.csv', index=False, header=False)