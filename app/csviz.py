import pandas as pd
import streamlit as st
import plotly.express as px

st.set_page_config(layout="wide")

def load_data():
    uploaded_file = st.sidebar.file_uploader("Upload a CSV file", type=["csv"])
    if uploaded_file:
        df = pd.read_csv(uploaded_file)
        return df
    return None

def generate_visualizations(df):
    tab = st.selectbox("Select a tab", ["Summary", "Numeric Data", "Categorical Data", "Geographic Data"])
    
    if tab == "Summary":
        st.dataframe(df, use_container_width=True)
        
        with st.expander("Edit Mode", expanded=False):
            st.data_editor(key="edited_data", data=df, num_rows="dynamic")  # Editable dataframe with session state
        
            if "edited_data" in st.session_state:
                st.write("Here's the value in Session State:")
                st.write(st.session_state["edited_data"])

    if tab == "Numeric Data":
        numeric_cols = df.select_dtypes(include=['float64', 'int64']).columns.tolist()
        if numeric_cols:
            selected_num = st.multiselect("Choose numeric columns", numeric_cols, default=numeric_cols)
            for col in selected_num:
                st.write(f"## {col}")
                fig = px.histogram(df, x=col)
                st.plotly_chart(fig)
    
    if tab == "Categorical Data":
        categorical_cols = df.select_dtypes(include=['object']).columns.tolist()
        if categorical_cols:
            selected_cat = st.multiselect("Choose categorical columns", categorical_cols, default=categorical_cols)
            for col in selected_cat:
                st.write(f"## {col}")
                temp_df = pd.DataFrame(df[col].value_counts()).reset_index()
                temp_df.columns = ['value', 'count']
                fig = px.bar(temp_df, x='value', y='count')
                st.plotly_chart(fig)
    
    if tab == "Geographic Data":
        if 'Country' in df.columns:
            st.write("## Country-wise Data")
            fig = px.choropleth(df, locations='Country', color='Sales',
                                locationmode='country names',
                                color_continuous_scale="Viridis")
            st.plotly_chart(fig)

st.title('Dynamic Data Dashboard')


# Dark mode settings would go into .streamlit/config.toml, not in the Python script.
df = load_data()
if df is not None:
    generate_visualizations(df)
