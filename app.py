#importing libraries
import streamlit as st
import pandas as pd
import plotly.express as px
#loading dataset
df = pd.read_csv('vehicles_us.csv')
df['manufacturer'] = df['model'].apply(lambda x: x.split()[0])
#Trouble shooting Render errors
import numpy as np
import pyarrow as pa
df['price'] = df['price'].astype(float)
df['date_posted'] = pd.to_datetime(df['date_posted'])
df['days_listed'] = df['days_listed'].astype(float)
#Displaying DataFrame with Streamlit
st.header('Data Viewer')
st.dataframe(df)
#Visualizing distribution of vehicle types by the manufacturer
st.header('Vehicle Types by Manufacturer')
fig = px.hisogram(df, x='Manufacturer', color='Type')
st.write(fig)
#Histogram of condition vs. model_year
st.header("Histogram of `Condition` vs `Model Year`")
fig = px.hisogram(df, x='Model Year', color='Condition')
st.write(fig)
#Comparing price distribution between manufacturers
st.header('Comparing Price Distribution between Manufacturers')
manufac_list = sorted(df['manufacturer'].unique())
manufacturer_1 = st.selectbox(
                              label = 'Select Manufacturer 1',
                              options = manufac_list,
                              index = manufac_list.index('chevrolet')
                              )
manufacturer_2 = st.selectbox(
                              label = 'Select Manufacturer 2',
                              options = manufac_list,
                              index = manufac_list.index('hyundai')
                              )
mask_filter = (df['manufacturer'] == manufacturer_1) | (df['manufacturer'] == manufacturer_2)
df_filtered = df[mask_filter]
normalize = st.checkbox('Normalize Histogram', value=True)
if normalize:
  histnorm = 'percent'
else:
  histnorm = None
fig = px.histogram(df_filtered,
                   x='Price',
                   nbins = 30,
                   color = 'Manufacturer',
                   histnorm = histnorm,
                   barmode = 'Overlay')
st.write(fig)
