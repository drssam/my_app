# Standard libraries
import numpy as np  
import pandas as pd  
import matplotlib.pyplot as plt  
import seaborn as sns  
import streamlit as st
import plotly.express as px
import warnings



warnings.filterwarnings(action='ignore')
  
# Config
pd.set_option('display.max_columns', None) 
sns.set_style('darkgrid') 

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

# Make Filter
unique_make = sorted(df_vehicles['make'].dropna().unique())

selected_car = st.sidebar.multiselect(
    'Select Car Make',  
    unique_make,  
    default=None,  
    placeholder="Choose car makes..."  
)

# Model Filter
if selected_car:
    unique_model = sorted(df_vehicles[df_vehicles['make'].isin(selected_car)]['model'].dropna().unique())
else:
    unique_model = []  

# Add model filter 
selected_models = st.sidebar.multiselect(
    'Select Car Model',  
    unique_model,  
    default=None,  
    placeholder="Choose car model..."  
)

# Comparison Section
st.sidebar.header("Compare Cars")
compare_cars = st.sidebar.radio(
    "Do you want to compare cars?",
    ('No', 'Yes')  
)

# display full table
if selected_car or selected_models:
    df_filtered = df_vehicles[
        (df_vehicles['make'].isin(selected_car) if selected_car else True) &
        (df_vehicles['model'].isin(selected_models) if selected_models else True)
    ]
else:
    df_filtered = df_vehicles 

# If model is selected
if selected_models:
    df_filtered = df_filtered[df_filtered['model'].isin(selected_models)]

# Filtered Data
st.write(f"Showing {df_filtered.shape[0]} cars matching criteria")
st.dataframe(df_filtered)

# Comparison Section
if compare_cars == 'Yes':
    # Comparison logic 
    st.sidebar.subheader("Select Cars for Comparison")
    car_1_index = st.sidebar.selectbox("Select the first car to compare", df_filtered.index)
    car_2_index = st.sidebar.selectbox("Select the second car to compare", df_filtered.index)

    # Get selected car rows
    car_1_row = df_filtered.loc[car_1_index]
    car_2_row = df_filtered.loc[car_2_index]

    all_attributes = ['price', 'model_year', 'make', 'model', 'condition', 'cylinders', 'fuel', 
                      'odometer_miles', 'transmission', 'type', 'paint_color', 'is_4wd', 'listing_date', 'days_listed']

    # Comparison Table
    comparison_df = pd.DataFrame({
        'Attribute': all_attributes,
        'Car 1': car_1_row[all_attributes].values,
        'Car 2': car_2_row[all_attributes].values
    })

    st.subheader(f"Comparison of {car_1_row['make']} {car_1_row['model']} and {car_2_row['make']} {car_2_row['model']}")
    st.dataframe(comparison_df)

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


# Price vs Make 
#st.header("Price Distribution by Make")
fig4 = px.box(df_filtered, x="make", y="price", title="Price Distribution by Make")
st.plotly_chart(fig4)


# Correlation Matrix

#st.header("Correlation Matrix for Numerical Features")
numeric_df = df_filtered.select_dtypes(include=['float64', 'int64'])
corr_matrix = numeric_df.corr()
plt.figure(figsize=(10, 8))
sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', fmt='.2f')
st.pyplot()
