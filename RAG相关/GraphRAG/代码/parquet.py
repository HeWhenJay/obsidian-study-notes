# pip install pandas

import pandas as pd
from IPython.display import display

# documents_df = pd.read_parquet("D:\graghrag\output\documents.parquet")
# display(documents_df.head().to_string())
text_unit_df = pd.read_parquet("D:\graghrag\output/documents.parquet")
display(text_unit_df.head().to_string())