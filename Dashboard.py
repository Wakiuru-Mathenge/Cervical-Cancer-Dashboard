import streamlit as st
import geopandas as gpd
import pandas as pd
import folium
from streamlit_folium import folium_static
import altair as alt

# Set up the app
st.set_page_config(page_title="Cervical Cancer Surveillance - Kenya", layout="wide")
st.title("🧬 Cervical Cancer Surveillance in Kenya (2019)")

# Load merged GeoDataFrame
gdf = gpd.read_file("kenya_cancer_2019.geojson")

# Metric selector
metric_option = st.selectbox(
    "Choose metric to display:",
    ("Women_Positive", "Women_Screened", "Positivity_Rate")
)

# County selector
county_options = ["All Counties"] + sorted(gdf["County"].unique())
selected_county = st.selectbox("Select County:", county_options)

# Filter data
if selected_county != "All Counties":
    filtered_gdf = gdf[gdf["County"] == selected_county]
else:
    filtered_gdf = gdf.copy()

# Create map object (initial empty)
m = folium.Map(tiles="CartoDB positron", control_scale=True)


# Fit to the counties
bounds = filtered_gdf.total_bounds
m.fit_bounds([[bounds[1], bounds[0]], [bounds[3], bounds[2]]])

# Inject JavaScript to restrict panning/zooming outside Kenya
max_bounds_js = f"""
<script>
    var map = window.map;
    map.setMaxBounds([
        [{bounds[1]}, {bounds[0]}],
        [{bounds[3]}, {bounds[2]}]
    ]);
</script>
"""
m.get_root().html.add_child(folium.Element(max_bounds_js))


# # Fit map to the filtered counties
# bounds = filtered_gdf.total_bounds  # [minx, miny, maxx, maxy]
# m.fit_bounds([[bounds[1], bounds[0]], [bounds[3], bounds[2]]])

# Add tooltip
tooltip = folium.GeoJsonTooltip(fields=["County", metric_option],
                                aliases=["County:", f"{metric_option.replace('_', ' ')}:"])

# Add data layer
geojson = folium.GeoJson(filtered_gdf, tooltip=tooltip).add_to(m)

# Show choropleth only if all counties are selected
if selected_county == "All Counties":
    folium.Choropleth(
        geo_data=filtered_gdf,
        data=filtered_gdf,
        columns=["County", metric_option],
        key_on="feature.properties.County",
        fill_color="YlOrRd",
        fill_opacity=0.7,
        line_opacity=0.2,
        legend_name=f"{metric_option.replace('_', ' ')} (2019)",
    ).add_to(m)

# Add a title or map key/legend using HTML
caption_html = f"""
<div style="position: fixed; bottom: 30px; left: 50px; width: 300px; z-index:9999; font-size:14px;
     background-color:white; padding:10px; border:1px solid #ccc; border-radius:5px;">
    <strong>🗺️ Map Legend:</strong><br>
    This map shows <strong>{metric_option.replace('_', ' ')}</strong><br>
    per county in Kenya for 2019.<br>
    Hover over a county to view values.
</div>
"""
m.get_root().html.add_child(folium.Element(caption_html))

# Display the map
folium_static(m)

# Show summary metric
total_value = filtered_gdf[metric_option].sum()
st.metric(f"Total {metric_option.replace('_', ' ')} (2019)", int(total_value))

# # Show bar chart
# if selected_county == "All Counties":
#     st.subheader(f"📊 {metric_option.replace('_', ' ')} by County")
#     top_n = st.slider("Show Top N Counties", 1, len(gdf), 10)
#     top_data = filtered_gdf.sort_values(metric_option, ascending=False).head(top_n)
#     st.bar_chart(top_data.set_index("County")[metric_option])
# else:
#     st.subheader(f"📊 {metric_option.replace('_', ' ')} for {selected_county}")
#     st.bar_chart(filtered_gdf.set_index("County")[metric_option])

st.subheader("📊 Screening and Positive Cases by County")

# Sort and select top N counties
top_n = st.slider("Show Top N Counties", 1, len(filtered_gdf), 10)
top_data = filtered_gdf.sort_values("Women_Positive", ascending=False).head(top_n)

# Ensure required columns exist
if {"County", "Women_Screened", "Women_Positive", "Positivity_Rate"}.issubset(top_data.columns):

    # Prepare data for stacked bar
    melted = top_data.melt(
        id_vars=["County", "Positivity_Rate"],
        value_vars=["Women_Screened", "Women_Positive"],
        var_name="Category",
        value_name="Count"
    )

    # Bar chart
    bar = alt.Chart(melted).mark_bar().encode(
        x=alt.X('County:N', sort='-y'),
        y=alt.Y('Count:Q'),
        color=alt.Color('Category:N', scale=alt.Scale(scheme='set2')),
        tooltip=['County', 'Category', 'Count']
    ).properties(width=700, height=400)

    # Add positivity rate text
    text = alt.Chart(top_data).mark_text(
        align='center',
        baseline='bottom',
        dy=-5,
        fontSize=12,
        color='black'
    ).encode(
        x=alt.X('County:N', sort='-y'),
        y=alt.Y('Women_Screened:Q'),
        text=alt.Text('Positivity_Rate:Q', format=".1f")
    )

    st.altair_chart(bar + text, use_container_width=True)

else:
    st.warning("One or more required columns are missing from the dataset.")