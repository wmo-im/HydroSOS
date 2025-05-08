# %% [markdown]
# The purpose of this notebook is to check that all the scripts/excel files are giving the same results.

# %%
import pandas as pd
import numpy as np

# %%
output_R_directory = "./example_data/output_R/"
output_Python_directory = "./example_data/output_Python/"
output_Excel_directory = "./example_data/output_Excel/"

# %% [markdown]
# Test the R script matches the Python outputs

# %%
outputs = ("cat_12001","cat_33035","cat_39001","cat_44008")
for output in outputs:
    print(output)
    R_output = pd.read_csv(f"{output_R_directory}{output}.csv")
    #R_output.rename(columns={"rankperc":"weibell_rank"}, inplace=True)
    Python_output = pd.read_csv(f"{output_Python_directory}{output}.csv")
    #print(R_output.compare(Python_output))
    #Python_output.drop(columns='weibell_rank', inplace=True)
    #R_output.drop(columns='weibell_rank', inplace=True)
    assert R_output.equals(Python_output)
    print()

# %% [markdown]
# Finally test that the R/Python outputs match the excel outputs 

# %%
outputs = ["cat_39001_exceltest", "cat_12001_exceltest","cat_44008_exceltest"]
encoding = {'Low flow':1,'Below normal':2,'Normal range':3,'Above normal':4,'High flow':5,np.nan:pd.NA}
for output in outputs:
    print(output)
    R_output = pd.read_csv(f"{output_Python_directory}{output}.csv")
    R_output['date'] = pd.to_datetime(R_output['date'])
    Excel_output = pd.read_excel(f"{output_Excel_directory}{output}.xlsx", sheet_name='Test')
    Excel_output.columns = ['date','flowcategory']
    for i in Excel_output.index:
        Excel_output.loc[i,'flowcat'] = encoding[Excel_output.loc[i,'flowcategory']]
    Excel_output['flowcat'] = Excel_output['flowcat'].astype('Int64')
    Excel_output.drop(columns='flowcategory', inplace=True)
    Excel_output.rename(columns={'flowcat':'flowcat_excel'}, inplace=True)
    R_output.rename(columns={'flowcat':'flowcat_R'}, inplace=True)
    mergedData = R_output.merge(Excel_output, left_on='date', right_on='date')
    print(mergedData['flowcat_R'].compare(mergedData['flowcat_excel']))



