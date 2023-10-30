import pandas as pd
import streamlit as st
import plotly.express as px
from geopy.geocoders import Nominatim

# Configuration and Sidebar
st.set_page_config(layout="wide")
st.experimental_set_query_params(_sidebar="open")
DEFAULT_URL = "https://public-one.s3.us-west-2.amazonaws.com/fake_customer_data.csv"

# Data Loading
def load_data():
    uploaded_file = st.sidebar.file_uploader("Upload a CSV file", type=["csv"])
    if uploaded_file:
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_csv(DEFAULT_URL)
    return df

# Geocoding function
def geocode(zip_code, country):
    geolocator = Nominatim(user_agent="geoapiExercises")
    location = geolocator.geocode({"postalcode": zip_code, "country": country})
    if location:
        return location.latitude, location.longitude
    else:
        return None, None

# Load offline geocoding data
geocoding_data = pd.read_csv('https://public-one.s3.us-west-2.amazonaws.com/geo-data.csv')

def generate_visualizations(df, tab=None):
    if tab is None:
        tab = st.selectbox("Select a tab", ["Summary", "Numeric Data", "Categorical Data", "Geographic Data", "KPI"])

    if tab == "Summary":
        generate_visualizations(df, 'Editor')
        generate_visualizations(df, 'Numeric Data')
        generate_visualizations(df, 'Categorical Data')
        generate_visualizations(df, 'Geographic Data')
        generate_visualizations(df, 'KPI')

    elif tab == "Editor":
        st.dataframe(df)
        with st.expander("Edit Mode"):
            edited_df = st.data_editor(data=df)
            if edited_df is not None:
                st.write("Here's the edited data:", edited_df)

    elif tab == "Numeric Data":
        numeric_cols = df.select_dtypes(include=['float64', 'int64']).columns.tolist()
        for col in numeric_cols:
            st.write(f"## {col}")
            fig = px.histogram(df, x=col)
            st.plotly_chart(fig)

    elif tab == "Categorical Data":
        categorical_cols = df.select_dtypes(include=['object']).columns.tolist()
        for col in categorical_cols:
            st.write(f"## {col}")
            temp_df = df[col].value_counts().reset_index()
            temp_df.columns = ['value', 'count']
            fig = px.bar(temp_df, x='value', y='count')
            st.plotly_chart(fig)

    if tab == "Geographic Data":
        zip_columns = [col for col in df.columns if col.lower().replace(" ", "") in ['zip', 'zipcode', 'postalcode']]
        if zip_columns:
            zip_column = zip_columns[0]
            st.write(f"## {zip_column} Data")

            # Merge with geocoding data
            df[zip_column] = df[zip_column].astype(str)
            geo_df = pd.merge(df, geocoding_data, left_on=zip_column, right_on='Zip Code', how='left')

            # Data filtering
            filter_col = st.selectbox("Filter by:", filterable_cols, index=default_filter_index, key="geo_filter_col")
            default_filter_index = filterable_cols.index('Customer Segment') if 'Customer Segment' in filterable_cols else 0
            filter_col = st.selectbox("Filter by:", filterable_cols, index=default_filter_index, key="geo_filter_col_GEO")
            filter_value = st.selectbox("Select value:", geo_df[filter_col].unique(), key="geo_filter_value")

            filtered_geo_df = geo_df[geo_df[filter_col] == filter_value]

            size_col = st.sidebar.selectbox("Size by:", df.select_dtypes(include=['float64', 'int64']).columns.tolist())
            color_col = st.selectbox("Color by:", df.select_dtypes(include=['float64', 'int64']).columns.tolist(), key="geo_color_col_GEO")
            
            fig = px.scatter_geo(filtered_geo_df, lat='Latitude', lon='Longitude', text=zip_column, scope='usa',
                                size=size_col, color=color_col)
            st.plotly_chart(fig, use_container_width=True)
    if tab == "KPI":
        filterable_cols = df.select_dtypes(include=['object']).columns.tolist()
        filter_col = st.selectbox("Filter KPIs by:", filterable_cols, index=filterable_cols.index('Customer Segment'))
        filter_val = st.selectbox("Select value:", df[filter_col].unique())
        
        filtered_kpi_df = df[df[filter_col] == filter_val]
        
        if not filtered_kpi_df.empty:
            avg_order_value = filtered_kpi_df['Average Order Value'].mean()
            total_purchase = filtered_kpi_df['Total Purchase Amount'].sum()
            
            col1, col2 = st.columns(2)
            col1.metric("Average Order Value", f"${avg_order_value:.2f}")
            col2.metric("Total Purchase Amount", f"${total_purchase:.2f}")
        else:
            st.write("No data available for the selected filter.")
# Main Execution
st.title('Dynamic Data Dashboard')
# Explanation and Disclaimer
st.write("""
CSViz is a CSV data visualizer built for speed. Try your own CSV or use the sample data below to save various data visualizations.
""")
# Explanation and Disclaimer inside an expandable section
with st.expander("Disclaimer and Info", expanded=False):
    st.markdown("""
    **Note**: All sample data is generated by AI and any similarities to real humans are coincidental.
    """)
# Main Execution
st.title('Dynamic Data Dashboard')
df = load_data()
if df is not None:
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(["Summary", "Editor", "Numeric Data", "Categorical Data", "Geographic Data", "KPI"])
    with tab1:
        generate_visualizations(df, tab='Summary')
    with tab2:
        generate_visualizations(df, tab='Editor')
    with tab3:
        generate_visualizations(df, tab='Numeric Data')
    with tab4:
        generate_visualizations(df, tab='Categorical Data')
    with tab5:
        generate_visualizations(df, tab='Geographic Data')
    with tab6:
        generate_visualizations(df, tab='KPI')


