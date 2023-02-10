import pandas as pd

temp = []
df = pd.read_csv("Main_df.csv")
path = df['path']
temp.append(path)

print(temp)
for i in temp:
    var = set(i)
    print(var)

# df = df.drop_duplicates(subset="path",keep=False, inplace=True)

# print(df)