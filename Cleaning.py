import pandas as pd

# Load the Excel file
df = pd.read_excel("Cancer 2014-2019.xlsx")

# Filter for the year 2019
df_2019 = df[df['Year'] == 2019].copy()

# Drop unnecessary columns
df_2019 = df_2019.drop(columns=['Unnamed: 4', 'UID'])

# Rename for easier reference
df_2019.columns = ['Year', 'County', 'Women_Screened', 'Women_Positive']

# Calculate positivity rate
df_2019['Positivity_Rate'] = (df_2019['Women_Positive'] / df_2019['Women_Screened']) * 100
df_2019['Positivity_Rate'] = df_2019['Positivity_Rate'].round(2)

# View results
print(df_2019.head())

df_2019.to_csv(r"C:\Users\IDEAPAD\OneDrive\Desktop\DS\cleaned_cancer_2019.csv", index=False)