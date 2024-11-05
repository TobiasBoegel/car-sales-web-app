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

# Average price by manufacturer and model year heatmap
st.subheader("💸 Average Price by Manufacturer and Model Year")
avg_price_data = df.groupby(['manufacturer', 'model_year'])['price'].mean().reset_index()
fig_avg_price = px.density_heatmap(
    avg_price_data, x="model_year", y="manufacturer", z="price",
    color_continuous_scale="Viridis", title="Average Price by Manufacturer and Model Year"
)
fig_avg_price.update_layout(width=1200, height=600, xaxis_title="Model Year", yaxis_title="Manufacturer")
st.plotly_chart(fig_avg_price)

# Scatter plot for price vs. odometer by condition
st.subheader("📈 Price vs. Odometer by Condition")
fig_price_odometer_condition = px.scatter(
    df, x="odometer", y="price", color="condition",
    title="Price vs. Odometer by Condition", hover_data=['manufacturer', 'model'],
    width=1200, height=600
)
fig_price_odometer_condition.update_layout(xaxis_title="Odometer (miles)", yaxis_title="Price")
st.plotly_chart(fig_price_odometer_condition)

# Listings over time line chart
st.subheader("📅 Listings Over Time")
df['month_year'] = df['date_posted'].dt.to_period('M').astype(str)  # Monthly grouping
listings_over_time = df.groupby('month_year').size().reset_index(name='listings')
fig_listings_time = px.line(listings_over_time, x="month_year", y="listings",
                            title="Number of Listings Over Time", markers=True, width=1200, height=600)
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
st.subheader("🔍 Vehicle Search Engine")

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

# Manufacturer Filter (multi-select)
manufacturer_options = df['manufacturer'].unique()
selected_manufacturers = st.sidebar.multiselect("Select Manufacturer(s)", manufacturer_options, default=manufacturer_options)

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
    (df['manufacturer'].isin(selected_manufacturers)) &
    (df['fuel'].isin(selected_fuel_types)) &
    (df['transmission'] == selected_transmission)
]

# Ensure data types are consistent
filtered_df['price'] = pd.to_numeric(filtered_df['price'], errors='coerce').fillna(0).astype(int)
filtered_df['model_year'] = pd.to_numeric(filtered_df['model_year'], errors='coerce').fillna(0).astype(int)
filtered_df['odometer'] = pd.to_numeric(filtered_df['odometer'], errors='coerce').fillna(0).astype(int)
filtered_df['manufacturer'] = filtered_df['manufacturer'].astype(str)
filtered_df['condition'] = filtered_df['condition'].astype(str)
filtered_df['fuel'] = filtered_df['fuel'].astype(str)
filtered_df['transmission'] = filtered_df['transmission'].astype(str)

# Sorting Options
st.sidebar.header("Sorting Options")

# Sorting selection via radio buttons
sorting_criteria = st.sidebar.radio(
    "Choose Sorting Order",
    ("Price: High to Low", "Price: Low to High", "Year: New to Old", "Year: Old to New", "Condition: Best to Worst", "Condition: Worst to Best")
)

# Define sorting logic based on user selection
if sorting_criteria == "Price: High to Low":
    filtered_df = filtered_df.sort_values(by="price", ascending=False)
elif sorting_criteria == "Price: Low to High":
    filtered_df = filtered_df.sort_values(by="price", ascending=True)
elif sorting_criteria == "Year: New to Old":
    filtered_df = filtered_df.sort_values(by="model_year", ascending=False)
elif sorting_criteria == "Year: Old to New":
    filtered_df = filtered_df.sort_values(by="model_year", ascending=True)
elif sorting_criteria == "Condition: Best to Worst":
    condition_order = ["new", "like new", "excellent", "good", "fair", "salvage"]
    filtered_df['condition'] = pd.Categorical(filtered_df['condition'], categories=condition_order, ordered=True)
    filtered_df = filtered_df.sort_values(by="condition", ascending=True)
elif sorting_criteria == "Condition: Worst to Best":
    condition_order = ["salvage", "fair", "good", "excellent", "like new", "new"]
    filtered_df['condition'] = pd.Categorical(filtered_df['condition'], categories=condition_order, ordered=True)
    filtered_df = filtered_df.sort_values(by="condition", ascending=True)

# Display limited number of rows, converted to strings
display_df = filtered_df[['price', 'model_year', 'manufacturer', 'condition', 'odometer', 'fuel', 'transmission']].head(15).astype(str)
st.write("### Search Results")
st.write(f"Displaying the top 15 results based on selected criteria:")
st.write(display_df)
