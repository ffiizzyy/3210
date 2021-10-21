import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly import tools
import plotly.offline as py
import plotly.express as px
import statsmodels.api as sm
import folium
import streamlit as st
import streamlit_folium
from streamlit_folium import folium_static

# Load Database
fertility = sm.datasets.fertility.load_pandas()['data']

# Load coordinates database for map
coordinatesdf = pd.read_csv("coordinates.csv")
coordinatesdf = coordinatesdf.iloc[:, :-4]

# Transforming dataset for line graph
df = fertility.drop(['Indicator Name', 'Indicator Code'], axis=1)

# Title
st.title('World Fertility Dataset')
st.write('Source: World Bank')

# Show dataframe
st.dataframe(df.head())

# Create country multiselect
chosen_country = st.multiselect('Choose the countries to be graphed',
                                df['Country Name'])
