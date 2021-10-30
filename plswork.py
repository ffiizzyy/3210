pip install -r requirements.txt

import pandas as pd
import plotly.graph_objects as go
import statsmodels.api as sm
import folium
import streamlit as st
import json
from streamlit_folium import folium_static
from PIL import Image

# Load data into dataframe
fertility = sm.datasets.fertility.load_pandas()['data']

# Transforming dataset to drop unneccessary variables
df = fertility.drop(['Indicator Name', 'Indicator Code'], axis=1)
# Creating a dataframe with the country name as the index
linedf = df.set_index('Country Name')

# Set header page structure
header = st.container()
sidebar = st.container()

# Create header section
with header:
    st.title('World Fertility Dataset 1960-2013')
    st.write("""
    The fertility rate is defined as the number of children that would be
    born to each woman if she were to live to the end of her child-bearing
    years. It is measured in total births per woman. This dataset can be used
    to measure past performance of policies, as well as to develop new policies.
    """)
    st.text('Data Source: World Bank')
    st.markdown("""---""")


# Navigation sidebar for users to specify page view
worldbanklogo = Image.open('resizelogo.png')
pagenames = ["Line Graph", "Bubble Map", "View and Download Dataframe"]

with sidebar:
    st.sidebar.image(worldbanklogo)
    page = st.sidebar.selectbox('Choose page:', pagenames)
    st.sidebar.markdown("""---""")


# Specify line graph main page
if page == "Line Graph":
    st.subheader("Line Graph:")
    st.write("""This line graph visualises the changes with the fertility rate
            since 1960. Don't forget to choose the countries/regions and
            the year range that you want to view from the sidebar on the left.
            """)
    # Create input widgets for the line graph
    st.sidebar.write("User Inputs:")

    # Create select box for the list of countries
    chosen_country = st.sidebar.multiselect(
        'Select countries:',
        list(linedf.index),
        ['Australia', 'New Zealand'])

    # Create slider for user to select year range
    year_range = st.sidebar.slider(
        "Choose year range:",
        1960, 2013, value=[1960, 2013])

    # Create a list with every year contained in the slider and convert into a string
    years = list(range(year_range[0], year_range[1] + 1))

    # Create the line graph using plotly
    linegraph = go.Figure()

    # Create for loop which goes through each country in the dataframe
    for ind in df.index:
        # Initialises an empty list that stores the fertility rate for each country
        yearDATA = []
        # Loops through the year range selected
        for i in years:
            singleyearDATA = df[str(i)][ind]

            # If data is missing (NaN), the graph will display it as 0
            if pd.isna(singleyearDATA):
                yearDATA.append(0)
            #
            else:
                yearDATA.append(singleyearDATA)

    # Graphs the countries that is chosen on the line graph
        if df['Country Name'][ind] in chosen_country:
            linegraph.add_trace(go.Scatter(x=years, y=yearDATA,
                                name=df['Country Name'][ind], opacity=0.8
            ))

# Add title and labels to the line graph
    linegraph.update_layout(
        title_text="Global Fertility Rate",
        title_font_size=25,
        autosize=True,
        xaxis=dict(
            title_text="Year",
            titlefont=dict(size=18)),
        yaxis=dict(
            title_text="Fertility Rate (births/woman)",
            titlefont=dict(size=18))
    )

    st.plotly_chart(linegraph)

    # Create expander to explain missing data procedures
    with st.expander("TO NOTE: Missing Data"):
        st.write("""
            The dataset contains some missing values.
            If there are no fertility rates recorded for a country for
            that specific year, the point is shown as ZERO on the graph.
            There are no datapoints recorded for any countries for the years
            2012 and 2013.
            """)

    # Create dataframe which contains only the selected countries
    linegraphdf = linedf.loc[chosen_country]

    # Converts year value from integer to a string as column names are strings
    yearlist = list(map(str, years))

    # Show dataframe on the page with only selected country and year range
    st.markdown("---")
    st.subheader("Show Dataframe")
    st.write(linegraphdf.filter(yearlist))

# Create the download button for the CSV
    def convert_df(line_df):
        return df.to_csv().encode('utf-8')

    csv = convert_df(linegraphdf)
    st.download_button(
        label="Export country dataset as CSV",
        data=csv,
        file_name='FertilityDataSubset.csv',
        mime='text/csv'
    )

# Create interactive bubble map

if page == "Bubble Map":
    st.subheader("Interactive Bubble Map")
    st.write(""" The bubble map is a visual representation of the fertility rate
             of the country. Don't forget to change the year on the sidebar and
             choose the colour of the bubbles to be displayed.
             """)
    map = folium.Map()
    # Create input widgets for the interactive map
    chooseyear = str(st.sidebar.slider("Choose the year to be displayed:",
                                       min_value=1960,
                                       max_value=2013,
                                       value=2008))
    bubblecolour = st.sidebar.color_picker("Pick a bubble colour:", "#002244")

# Load json file with coordinates for the bubbles
    f = open('country.json',)
    data = json.load(f)
    f.close()

# Create interactive bubbles
    for ind in df.index:
        # For loop to specify that bubbles will only appear if the data is available
        if not pd.isna(df[chooseyear][ind]):
            if df['Country Code'][ind] in data[0]:
                # Create popup for the countries to include countries and fertility rate
                folium.CircleMarker(
                    location=[data[0][df['Country Code'][ind]]['latitude'],
                              data[0][df['Country Code'][ind]]['longitude']],
                    popup=folium.Popup(folium.IFrame(
                        '<h5>' + df['Country Name'][ind] +
                        '</h5>' +
                        str(round(df[chooseyear][ind], 4)),
                        height=75, width=75)),
                    radius=float(df[chooseyear][ind]) * 2,
                    color=bubblecolour,
                    fill=True,
                    fill_color=bubblecolour
                ).add_to(map)
    folium_static(map)
    with st.expander("TO NOTE: Bubble Sizes and Missing Data"):
        st.write("""
            The size of the bubble signifies the fertility rate.
            The bigger the bubble, the higher the fertility rate.
            If there are no data recorded for a country for a specific year,
            then the bubble will not appear.
            Data points of regions (eg. Other Small States, OECD Members) is
            not taken into account, and only the data from individual countries
            is considered.
            """)

st.sidebar.write("Created by Feliza Anindita")
# Create show and view dataframe main page
# Dataframe used is different - linedf has the countries as the index
if page == "View and Download Dataframe":
    st.write("Show Dataframe")
    st.dataframe(linedf)

# Create download button to be able to export dataframe to CSV
    def convert_df(linedf):
        return df.to_csv().encode('utf-8')

    csv = convert_df(linedf)
    st.download_button(
        label="Export full dataset as CSV",
        data=csv,
        file_name='WorldBankFertility.csv',
        mime='text/csv'
    )
