#importing libraries
import streamlit as st
import pandas as pd
import plotly.express as px
import os

# Disable pyarrow timezone integration and pandas options
os.environ["PYARROW_IGNORE_TIMEZONE"] = "1"
pd.options.mode.use_inf_as_na = True  # Treat infinity values as NaN
pd.options.display.large_repr = "truncate"  # Avoid using pyarrow

# Load dataset without caching
def load_data():
    df = pd.read_csv('vehicles_us.csv')
    df['manufacturer'] = df['model'].apply(lambda x: x.split()[0])  # Extract manufacturer from model
    return df

df = load_data()

#Trouble shooting personal code
st.title("Car Listings Analysis")

# # Streamlit header
st.header("Explore the Dataset")

# Title for the histogram
st.subheader("🚗 Vehicle Count by Manufacturer and Model Type")

# Histogram to display vehicle count by manufacturer with color-coded model types
fig_manufacturer_model = px.histogram(
    df,
    x="manufacturer",
    color="type",  # Color segments by model type (e.g., SUV, pickup)
    title="Vehicle Count by Manufacturer and Model Type",
    category_orders={"manufacturer": df['manufacturer'].value_counts().index.tolist()},  # Sort manufacturers by count
)

# Customizing the layout
fig_manufacturer_model.update_layout(
    xaxis_title="Manufacturer",
    yaxis_title="Vehicle Count",
    yaxis=dict(
        tickmode='linear',
        tick0=0,
        dtick=2000,  # Setting y-axis tick intervals to 2,000
        range=[0, 14000]  # Setting y-axis range from 0 to 14,000
    ),
    bargap=0.1, # Adds a small space between bars
    width=1200, # Increase width for better visualization
    height=600, # Increase height for clearer differentiation
    template="plotly_white"  # Set the template style
)

# Display the plot in Streamlit
st.plotly_chart(fig_manufacturer_model)

# Title for the stacked bar chart
st.subheader("🚗 Distribution of Vehicle Condition by Model Year")

# Stacked bar chart to display the distribution of condition across model years
fig_condition_year = px.histogram(
    df,
    x="model_year",
    color="condition",  # Color segments by condition (e.g., good, excellent, fair)
    title="Distribution of Vehicle Condition by Model Year",
    category_orders={"condition": ["new", "like new", "excellent", "good", "fair", "salvage"]},  # Order conditions logically
)

# Customizing the layout
fig_condition_year.update_layout(
    xaxis_title="Model Year",
    yaxis_title="Vehicle Count",
    width=1200,  # Consistent width
    height=600,  # Consistent height
    bargap=0.1,  # Adds a small space between bars for clarity
    template="plotly_white"  # Set the template style
)

# Display the plot in Streamlit
st.plotly_chart(fig_condition_year)

# Bubble chart for average price by manufacturer and model year
st.subheader("💸 Average Price by Manufacturer and Model Year")

# Calculate average price by manufacturer and model year
avg_price_data = df.groupby(['manufacturer', 'model_year'])['price'].mean().reset_index()

# Create bubble chart
fig_avg_price = px.scatter(
    avg_price_data, x="manufacturer", y="model_year", size="price", color="manufacturer",
    title="Average Price by Manufacturer and Model Year",
    labels={"model_year": "Model Year", "price": "Average Price ($)"},
    hover_data={'price': ':.0f'},  # Display price as an integer in hover
    height=600, width=1200
)
fig_avg_price.update_layout(template="plotly_white")
st.plotly_chart(fig_avg_price)


# Overlayed bar chart for price vs. odometer by condition
st.subheader("💵 Price vs. Odometer by Condition")

# Bin the odometer values for clearer grouping
df['odometer_bin'] = pd.cut(df['odometer'], bins=[0, 50000, 100000, 150000, 200000, 250000, 300000, 350000, 400000], labels=[
    "0-50k", "50-100k", "100-150k", "150-200k", "200-250k", "250-300k", "300-350k", "350-400k"
])

# Aggregate average price by odometer bin and condition
avg_price_by_odometer = df.groupby(['odometer_bin', 'condition'])['price'].mean().reset_index()

# Create a bar chart with overlayed conditions
fig_price_odometer = px.bar(
    avg_price_by_odometer, x='odometer_bin', y='price', color='condition', barmode='overlay',
    title="Average Price by Odometer Range and Condition",
    labels={'odometer_bin': 'Odometer (miles)', 'price': 'Average Price ($)'},
    height=600, width=1200
)
fig_price_odometer.update_layout(template="plotly_white")
st.plotly_chart(fig_price_odometer)


# Convert 'date_posted' to datetime format
df['date_posted'] = pd.to_datetime(df['date_posted'], errors='coerce')

# Drop rows with NaT (null) in 'date_posted' if conversion failed
df = df.dropna(subset=['date_posted'])

# Create the Listings over Time plot
st.subheader("📅 Listings Over Time")

# Extract month and year from the 'date_posted' column for grouping
df['month_year'] = df['date_posted'].dt.to_period('M').astype(str)  # Monthly grouping
listings_over_time = df.groupby('month_year').size().reset_index(name='listings')

# Plot using Plotly Express
fig_listings_time = px.line(
    listings_over_time, x="month_year", y="listings",
    title="Number of Listings Over Time", markers=True, width=1200, height=600
)
fig_listings_time.update_layout(xaxis_title="Month-Year", yaxis_title="Number of Listings")
st.plotly_chart(fig_listings_time)

# Bar chart for top 10 most popular models
st.subheader("🚘 Top 10 Most Popular Car Models")
top_models = df['model'].value_counts().nlargest(10).reset_index()
top_models.columns = ['model', 'count']
fig_top_models = px.bar(
    top_models, x="model", y="count", title="Top 10 Most Popular Car Models",
    color="count", color_continuous_scale="Blues", width=1200, height=600
)
fig_top_models.update_layout(xaxis_title="Car Model", yaxis_title="Number of Listings")
st.plotly_chart(fig_top_models)

# Pie chart for fuel type distribution
st.subheader("⛽ Fuel Type Distribution")
fig_fuel_type = px.pie(
    df, names="fuel", title="Fuel Type Distribution", hole=0.3,
    color_discrete_sequence=px.colors.sequential.RdBu
)
fig_fuel_type.update_layout(width=800, height=500)
st.plotly_chart(fig_fuel_type)

# Title for the search engine
st.subheader("🔍 Vehicle Search Engine (Pie Chart by Manufacturer)")

# Filter options in the sidebar
st.sidebar.header("Filter Options")

# Price Range Filter with narrowed default range
price_min = int(df['price'].min())
price_max = int(df['price'].max())
price_range = st.sidebar.slider("Price Range", min_value=price_min, max_value=price_max, value=(price_min, price_min + (price_max - price_min) // 2))

# Model Year Range Filter with narrowed default range
year_min = int(df['model_year'].min())
year_max = int(df['model_year'].max())
year_range = st.sidebar.slider("Model Year Range", min_value=year_min, max_value=year_max, value=(year_min, year_min + (year_max - year_min) // 2))

# Condition Filter (multi-select)
condition_options = df['condition'].unique()
selected_conditions = st.sidebar.multiselect("Select Condition(s)", condition_options, default=condition_options)

# Fuel Type Filter (multi-select)
fuel_options = df['fuel'].unique()
selected_fuel_types = st.sidebar.multiselect("Select Fuel Type(s)", fuel_options, default=fuel_options)

# Transmission Filter (radio button)
transmission_options = df['transmission'].unique()
selected_transmission = st.sidebar.radio("Select Transmission", transmission_options)

# Apply Filters to DataFrame
filtered_df = df[
    (df['price'] >= price_range[0]) & (df['price'] <= price_range[1]) &
    (df['model_year'] >= year_range[0]) & (df['model_year'] <= year_range[1]) &
    (df['condition'].isin(selected_conditions)) &
    (df['fuel'].isin(selected_fuel_types)) &
    (df['transmission'] == selected_transmission)
]

# Count distribution by manufacturer
manufacturer_distribution = filtered_df['manufacturer'].value_counts().reset_index()
manufacturer_distribution.columns = ['manufacturer', 'count']

# Create pie chart
st.subheader("🖼️ Manufacturer Distribution Based on Search Criteria")
fig_pie = px.pie(
    manufacturer_distribution, names='manufacturer', values='count',
    title="Distribution of Manufacturers Matching Search Criteria",
    color_discrete_sequence=px.colors.sequential.RdBu
)
fig_pie.update_traces(textinfo='percent+label')
st.plotly_chart(fig_pie)
