import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly import tools
import plotly.offline as py
import plotly.express as px
import statsmodels.api as sm
import folium
import streamlit as st
import json
from streamlit_folium import folium_static

# Set page structure
header = st.container()
sidebar = st.container()

# Title
with header:
    st.title('World Fertility Dataset')
    st.write("The fertility rate is defined as the number of children that would be born to each woman if she were to live to the end of her child-bearing years.")
    st.text('Source: World Bank')
    st.write

# Navigation sidebar
with sidebar:
    page_names = ["Line Graph", "Bubble Map"]
    page = st.sidebar.radio('Graph Type:', page_names)

    st.sidebar.write("Created by Feliza Anindita")

# Load Database
fertility = sm.datasets.fertility.load_pandas()['data']

# Load coordinates database for map
# coordinatesdf = pd.read_csv("coordinates.csv")
# coordinatesdf = coordinatesdf.iloc[:, :-4]

# Transforming dataset for line graph
df = fertility.drop(['Indicator Name', 'Indicator Code'], axis=1)
linedf = df.astype(bytes)
linedf = linedf['Country Name'].astype(str)

# Specify line graph
if page == "Line Graph":
    chosen_country = st.multiselect('Choose the countries to be graphed',
                                    df['Country Name'])
    year_range = st.slider(
        "Year Range",
        1960, 2013, value=[1960, 2014])

    st.subheader("Show Dataframe")
    st.dataframe(df)

# Download button (need to be fixed still)
    def convert_df(df):
        return df.to_csv().encode('utf-8')

        csv = convert_df(df)
        st.download_button(
                label="Download data as CSV",
                data=csv,
                file_name='fertility.csv',
                mime='text/csv',
                )

    st.write("This is a line graph")
    st.line_chart(linedf)


def return_color(value):
    if value <= 2:
        return 'red'
    else:
        return 'green'


# Create folium map
if page == "Bubble Map":
    st.write("Bubble Map")
    map = folium.Map(location=[10, 80], zoom_start=3)
    choose_year = str(st.slider("Choose Year", min_value=1960,
                                max_value=2013, value=2008))


# Load json file with coordinates
    f = open('country.json',)
    data = json.load(f)
    f.close()

# Create bubbles
# To add fertility rate in popup and add colour coding for bubbles
    for ind in df.index:
        if not pd.isna(df[choose_year][ind]):
            if df['Country Code'][ind] in data[0]:
                folium.Circle(
                    location=[data[0][df['Country Code'][ind]]['latitude'],
                              data[0][df['Country Code'][ind]]['longitude']],
                    popup=df['Country Name'][ind],
                    radius=float(df[choose_year][ind])*100000,
                    color='red',
                    fill=True,
                    fill_color='red'
                ).add_to(map)

    folium_static(map)
    st.write(df[choose_year])
