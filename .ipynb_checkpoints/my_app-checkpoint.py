# Standard libraries
import numpy as np  
import pandas as pd  
import matplotlib.pyplot as plt  
import seaborn as sns  
import streamlit as st
import plotly.express as px

# Config
pd.set_option('display.max_columns', None)  # Show all columns
sns.set_style('darkgrid')  # Set visualization style

# Streamlit Config
st.set_page_config(page_title="Used Cars Market", layout="wide")

# Title and Subtitle
st.markdown("""
    <h1 style='text-align: center;'>🚗 Used Cars Market 🚙</h1>
    <h3 style='text-align: center;'>🛠️ Filter cars and Explore Market trends 🏁</h3>
""", unsafe_allow_html=True)

# Load dataset
df_vehicles = pd.read_csv('vehicles_us.csv',low_memory= False)

# Convert data types
df_vehicles = df_vehicles.astype({
    'model_year': 'Int64', 
    'cylinders': 'Int64', 
    'odometer': 'Int64'})
df_vehicles['is_4wd'] = df_vehicles['is_4wd'].fillna(0).astype(bool)   
df_vehicles['date_posted'] = pd.to_datetime(df_vehicles['date_posted']) 

# Split 'model' column into 'make' and 'model'
df_vehicles[['make', 'model']] = df_vehicles['model'].str.split(' ', n=1, expand=True)

df_vehicles.rename(columns={
    'odometer': 'odometer_miles',
    'date_posted': 'listing_date',
}, inplace=True)

# New Columns 
df_vehicles['car_age'] = df_vehicles['model_year'].max() - df_vehicles['model_year']
df_vehicles['price_per_mile'] = df_vehicles['price'] / df_vehicles['odometer_miles']
df_vehicles['price_per_mile'].replace([np.inf, -np.inf], np.nan)
df_vehicles['high_mileage'] = df_vehicles['odometer_miles'].apply(lambda x: 1 if x > 150000 else 0)
df_vehicles['age_category'] = pd.cut(df_vehicles['car_age'], bins=[0, 5, 10, 20, float('inf')], labels=['<5', '5-10', '10-20', '>20'])
df_vehicles['listing_date'] = df_vehicles['listing_date'].dt.strftime('%Y-%m-%d')

#|###################################################|#
#|************ streamlit sidebar section ************|#
#|###################################################|#
## streamlit sidebar header
st.sidebar.header('Filter Options')

# Year Filter
min_year = int(df_vehicles['model_year'].min())
max_year = int(df_vehicles['model_year'].max())
selected_year = st.sidebar.slider('Select Model Year:', min_year, max_year, (min_year, max_year))

# # Make Filter
# unique_make = sorted(df_vehicles['make'].dropna().unique())
# selected_car = st.sidebar.multiselect(
#     'Select Car Make',  # More descriptive label
#     unique_make,  # Options
#     default=unique_make,  # Default selects all makes
#     placeholder="Choose car makes..."  # A hint inside the dropdown
# )

# Make Filter
unique_make = sorted(df_vehicles['make'].dropna().unique())
# selected_makes = st.sidebar.multiselect('Select Car Make:', unique_makes, unique_makes)
selected_car = st.sidebar.multiselect(
    'Select Car Make',  # More descriptive label
    unique_make,  # Options
    default=None,  # No preselected cars (user selects what they need)
    placeholder="Choose car makes..."  # A hint inside the dropdown
)

# Model Filter
if selected_car:
    # Get models related to the selected makes
    unique_model = sorted(df_vehicles[df_vehicles['make'].isin(selected_car)]['model'].dropna().unique())
else:
    unique_model = []  # If no make is selected, show no models

# Add model filter (optional, based on selected make)
selected_models = st.sidebar.multiselect(
    'Select Car Model',  # More descriptive label
    unique_model,  # Options based on selected make(s)
    default=None,  # No preselected cars (user selects what they need)
    placeholder="Choose car model..."  # A hint inside the dropdown
)

# Comparison Section (optional)
st.sidebar.header("Compare Cars")
compare_cars = st.sidebar.radio(
    "Do you want to compare cars?",
    ('No', 'Yes')  # Option to choose whether to compare or not
)

# # Apply Filters
# df_filtered = df_vehicles[
#     (df_vehicles['model_year'].between(selected_year[0], selected_year[1])) &  # Filter between selected years
#     (df_vehicles['make'].isin(selected_car))  # Filter based on selected makes
# ]

# Initially, display the full table (if no filters are selected)
if selected_car or selected_models:
    df_filtered = df_vehicles[
        (df_vehicles['make'].isin(selected_car) if selected_car else True) &
        (df_vehicles['model'].isin(selected_models) if selected_models else True)
    ]
else:
    df_filtered = df_vehicles  # No filters, show all cars

    


# If model is selected, further filter by model
if selected_models:
    df_filtered = df_filtered[df_filtered['model'].isin(selected_models)]


# Show Filtered Data
st.write(f"Showing {df_filtered.shape[0]} cars matching criteria")
st.dataframe(df_filtered)

# Handle Comparison Section
if compare_cars == 'Yes':
    # Comparison logic (same as the previous implementation for car comparison)
    st.sidebar.subheader("Select Cars for Comparison")
    car_1_index = st.sidebar.selectbox("Select the first car to compare", df_filtered.index)
    car_2_index = st.sidebar.selectbox("Select the second car to compare", df_filtered.index)

    # Get selected car rows
    car_1_row = df_filtered.loc[car_1_index]
    car_2_row = df_filtered.loc[car_2_index]

    # Create comparison data for all attributes
    all_attributes = ['price', 'model_year', 'make', 'model', 'condition', 'cylinders', 'fuel', 
                      'odometer_miles', 'transmission', 'type', 'paint_color', 'is_4wd', 'listing_date', 'days_listed']

    # Display Comparison Table
    comparison_df = pd.DataFrame({
        'Attribute': all_attributes,
        'Car 1': car_1_row[all_attributes].values,
        'Car 2': car_2_row[all_attributes].values
    })

    st.subheader(f"Comparison of {car_1_row['make']} {car_1_row['model']} and {car_2_row['make']} {car_2_row['model']}")
    st.dataframe(comparison_df)


# # Compare cars sold
# # Sidebar for Car Selection
# st.sidebar.header("Compare Cars")
# # Selecting cars from the filtered DataFrame based on make and model
# car_1 = st.sidebar.selectbox("Select the first car to compare", df_filtered[['make', 'model']].drop_duplicates().values.tolist(), format_func=lambda x: f"{x[0]} {x[1]}")
# car_2 = st.sidebar.selectbox("Select the second car to compare", df_filtered[['make', 'model']].drop_duplicates().values.tolist(), format_func=lambda x: f"{x[0]} {x[1]}")
# car_3 = st.sidebar.selectbox("Select the third car to compare", df_filtered[['make', 'model']].drop_duplicates().values.tolist(), format_func=lambda x: f"{x[0]} {x[1]}")

# # Check if valid selections are made
# if car_1 is None or car_2 is None or car_3 is None:
#     st.error("Please select all three cars to compare.")
# else:
#     # Fetch the selected rows for each car
#     car_1_row = df_filtered[(df_filtered['make'] == car_1[0]) & (df_filtered['model'] == car_1[1])]
#     car_2_row = df_filtered[(df_filtered['make'] == car_2[0]) & (df_filtered['model'] == car_2[1])]
#     car_3_row = df_filtered[(df_filtered['make'] == car_3[0]) & (df_filtered['model'] == car_3[1])]


# # If no car data is found (e.g., user selects invalid cars), show an error
#     if car_1_row.empty or car_2_row.empty or car_3_row.empty:
#         st.error("Invalid car selection. Please select valid cars from the list.")
#     else:
#         # Create comparison data for all attributes (without selection)
#         all_attributes = ['price', 'model_year', 'make', 'model', 'condition', 'cylinders', 'fuel', 
#                           'odometer_miles', 'transmission', 'type', 'paint_color', 'is_4wd', 'listing_date', 'days_listed']

#         comparison_data = {
#             'Attribute': all_attributes,
#             car_1_row['make'].values[0] + ' ' + car_1_row['model'].values[0]: [car_1_row[attr].values[0] for attr in all_attributes],
#             car_2_row['make'].values[0] + ' ' + car_2_row['model'].values[0]: [car_2_row[attr].values[0] for attr in all_attributes],
#             car_3_row['make'].values[0] + ' ' + car_3_row['model'].values[0]: [car_3_row[attr].values[0] for attr in all_attributes]
#         }

#         # Convert to DataFrame for better display
#         comparison_df = pd.DataFrame(comparison_data)

#         # Display the comparison table
#         st.header("Cars Comparison")
#         st.write(comparison_df)


#|###################################################|#
#|************ Visualization ************|#
#|###################################################|#

# Prices Histogram
st.subheader("Price Distribution")
fig_price = px.histogram(df_filtered, x='price', nbins=50, title="Distribution of Car Prices")
st.plotly_chart(fig_price, use_container_width=True)

# Comparisons
st.header("Comparisons' Plots")
# Price vs Condition
condition_selected = st.selectbox('Select condition to view price distribution', df_filtered['condition'].unique())
fig1 = px.histogram(df_filtered[df_filtered['condition'] == condition_selected], x='price', color='condition',
                    title=f"Price Distribution for {condition_selected} Condition")
st.plotly_chart(fig1)

# Price vs Age
# st.header("Price vs Age")
fig2 = px.scatter(df_filtered, x="car_age", y="price", color="make", title="Price vs Age")
st.plotly_chart(fig2)


# Price vs Odometer
#st.header("Price vs Odometer (per Miles)")
fig3 = px.scatter(df_filtered, x="odometer_miles", y="price", color="make", title="Price vs Odometer", hover_data=['model_year', 'model'])
st.plotly_chart(fig3, use_container_width=True)

# Visualization - Scatter Plot of Price vs Odometer




# Price vs Make 
#st.header("Price Distribution by Make")
fig4 = px.box(df_filtered, x="make", y="price", title="Price Distribution by Make")
st.plotly_chart(fig4)


# Correlation Matrix for Numerical Features (Heatmap)

# 5. Correlation Matrix for Numerical Features (Heatmap)
#st.header("Correlation Matrix for Numerical Features")
numeric_df = df_filtered.select_dtypes(include=['float64', 'int64'])
corr_matrix = numeric_df.corr()
plt.figure(figsize=(10, 8))
sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', fmt='.2f')
st.pyplot()
