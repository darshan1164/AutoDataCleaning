import streamlit as st
import pandas as pd
import numpy as np
from io import BytesIO

st.title("Auto Data Cleaning Website")
st.write("Upload a CSV/Excel file or create your own dataset to automatically clean your data. No data is stored permanently.")

option = st.radio("Choose an option:", ("Upload File", "Create Dataset"))
df = None

if option == "Upload File":
    uploaded_file = st.file_uploader("Choose a CSV or Excel file", type=["csv", "xlsx", "xls"])
    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file) if uploaded_file.name.endswith('.csv') else pd.read_excel(uploaded_file)
elif option == "Create Dataset":
    st.write("Create your dataset by editing the table below:")
    initial_df = pd.DataFrame({'Column1': [None] * 5, 'Column2': [None] * 5, 'Column3': [None] * 5})
    edited_df = st.data_editor(initial_df, num_rows="dynamic")
    if st.button("Use This Dataset"):
        df = edited_df.dropna(how='all').reset_index(drop=True)

if df is not None and not df.empty:
    st.subheader("Original Data")
    st.write(f"Shape: {df.shape}")
    st.dataframe(df.head())

    def auto_clean_data(df):
        changes = {}
        before_dup = df.shape[0]
        df = df.drop_duplicates()
        changes['duplicates_removed'] = before_dup - df.shape[0]
        
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        categorical_cols = df.select_dtypes(include=['object']).columns
        
        missing_filled_numeric = 0
        for col in numeric_cols:
            missing_count = df[col].isnull().sum()
            df[col] = df[col].fillna(df[col].mean())
            missing_filled_numeric += missing_count
        
        missing_filled_categorical = 0
        for col in categorical_cols:
            missing_count = df[col].isnull().sum()
            df[col] = df[col].fillna(df[col].mode()[0] if not df[col].mode().empty else 'Unknown')
            missing_filled_categorical += missing_count
        
        changes['missing_filled_numeric'] = missing_filled_numeric
        changes['missing_filled_categorical'] = missing_filled_categorical
        
        before_outlier = df.shape[0]
        for col in numeric_cols:
            Q1 = df[col].quantile(0.25)
            Q3 = df[col].quantile(0.75)
            IQR = Q3 - Q1
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR
            df = df[(df[col] >= lower_bound) & (df[col] <= upper_bound)]
        changes['outliers_removed'] = before_outlier - df.shape[0]
        
        return df, changes

    cleaned_df, changes = auto_clean_data(df.copy())
    
    st.subheader("Cleaning Summary")
    st.write("**Data Cleaning Actions Performed:**")
    st.write(f"- **Duplicates Removed**: {changes['duplicates_removed']} rows were removed because they were exact duplicates of other rows.")
    st.write(f"- **Missing Values Filled**: {changes['missing_filled_numeric']} missing values in numeric columns were filled with the column mean. {changes['missing_filled_categorical']} missing values in categorical columns were filled with the most frequent value or 'Unknown'.")
    st.write(f"- **Outliers Removed**: {changes['outliers_removed']} rows were removed because they contained outlier values in numeric columns (values outside 1.5 * IQR from Q1/Q3).")
    
    st.subheader("Cleaned Data")
    st.write(f"Shape: {cleaned_df.shape}")
    st.dataframe(cleaned_df.head())
    
    def to_csv(df):
        output = BytesIO()
        df.to_csv(output, index=False)
        output.seek(0)
        return output

    csv_data = to_csv(cleaned_df)
    st.download_button(label="Download Cleaned Data as CSV", data=csv_data, file_name="cleaned_data.csv", mime="text/csv")

st.write("Note: Data is processed in memory and not stored.")