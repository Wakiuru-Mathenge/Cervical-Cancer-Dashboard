import geopandas as gpd
import pandas as pd

# Load your cleaned cancer data
df = pd.read_csv("cleaned_cancer_2019.csv")  # if you saved it after cleaning

# Load Kenya counties GeoJSON
gdf = gpd.read_file(r"C:\Users\IDEAPAD\OneDrive\Desktop\DS\kenya-county\Shapefile\ke_county.shp")

# Print column names to identify the correct one
print(gdf.columns)

 # Ensure matching case and names
df['County'] = df['County'].str.strip().str.upper()
gdf['COUNTY'] = gdf['county'].str.strip().str.upper()

# Merge spatial and cancer data
merged_gdf = gdf.merge(df, left_on='COUNTY', right_on='County')

# Save for visualization
merged_gdf.to_file(r"C:\Users\IDEAPAD\OneDrive\Desktop\DS\kenya_cancer_2019.geojson", driver="GeoJSON")
