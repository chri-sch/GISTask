import pandas as pd
import os

file = r"C:\_data\vexcel\dsm\dsm_index.csv"

out_path = r"C:\_data\vexcel\dsm"
df = pd.read_csv(file)

for i in range(df.shape[0]):
    row_df = df[i:i + 1]
    file_name = row_df.location.values[0].split("/")[-1]
    out_file = os.path.join(out_path, file_name).replace("_DSM", "DSM")

    row_df.to_csv(out_file)
