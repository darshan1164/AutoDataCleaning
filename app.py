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

    with st.expander("Cleaning Options"):
        duplicate_option = st.selectbox(
            "Duplicate removal",
            ["Remove exact duplicates", "Keep duplicates"],
            index=0,
        )
        numeric_missing_strategy = st.selectbox(
            "Numeric missing value strategy",
            ["Mean", "Median", "Zero"],
            index=1,
        )
        categorical_missing_strategy = st.selectbox(
            "Categorical missing value strategy",
            ["Mode", "Unknown", "Missing"],
            index=0,
        )
        normalize_text = st.checkbox("Normalize text values (trim whitespace and lowercase)", value=True)
        outlier_action = st.selectbox(
            "Outlier handling",
            ["Flag only", "Remove rows", "Do nothing"],
            index=0,
        )

    def convert_numeric_like_columns(df):
        for col in df.columns:
            if df[col].dtype == object:
                cleaned = df[col].astype(str).str.strip().replace({'': np.nan})
                cleaned = cleaned.str.replace(',', '', regex=False)
                converted = pd.to_numeric(cleaned, errors='coerce')
                if converted.notna().sum() >= len(df) * 0.6:
                    df[col] = converted
        return df

    def normalize_text_columns(df):
        text_cols = df.select_dtypes(include=['object']).columns
        for col in text_cols:
            df[col] = df[col].astype(str).str.strip()
            df[col] = df[col].replace({'': np.nan})
            df[col] = df[col].where(df[col].isnull(), df[col].str.lower())
        return df

    def auto_clean_data(df):
        changes = {
            'duplicates_removed': 0,
            'missing_filled_numeric': 0,
            'missing_filled_categorical': 0,
            'outliers_removed': 0,
            'outliers_flagged': 0,
        }

        if duplicate_option == "Remove exact duplicates":
            before_dup = df.shape[0]
            df = df.drop_duplicates().reset_index(drop=True)
            changes['duplicates_removed'] = before_dup - df.shape[0]

        if normalize_text:
            df = normalize_text_columns(df)

        df = convert_numeric_like_columns(df)

        numeric_cols = df.select_dtypes(include=[np.number]).columns
        categorical_cols = df.select_dtypes(include=['object', 'category']).columns

        for col in numeric_cols:
            missing_count = df[col].isnull().sum()
            if missing_count > 0:
                if numeric_missing_strategy == "Median":
                    fill_value = df[col].median()
                elif numeric_missing_strategy == "Zero":
                    fill_value = 0
                else:
                    fill_value = df[col].mean()
                df[col] = df[col].fillna(fill_value)
                changes['missing_filled_numeric'] += missing_count

        for col in categorical_cols:
            missing_count = df[col].isnull().sum()
            if missing_count > 0:
                if categorical_missing_strategy == "Unknown":
                    fill_value = 'unknown'
                elif categorical_missing_strategy == "Missing":
                    fill_value = 'missing'
                else:
                    fill_value = df[col].mode()[0] if not df[col].mode().empty else 'unknown'
                df[col] = df[col].fillna(fill_value)
                changes['missing_filled_categorical'] += missing_count

        outlier_mask = pd.Series(False, index=df.index)
        if outlier_action != "Do nothing" and len(numeric_cols) > 0:
            for col in numeric_cols:
                Q1 = df[col].quantile(0.25)
                Q3 = df[col].quantile(0.75)
                IQR = Q3 - Q1
                lower_bound = Q1 - 1.5 * IQR
                upper_bound = Q3 + 1.5 * IQR
                outlier_mask |= df[col].lt(lower_bound) | df[col].gt(upper_bound)
            changes['outliers_flagged'] = int(outlier_mask.sum())
            if outlier_action == "Remove rows":
                before_outlier = df.shape[0]
                df = df.loc[~outlier_mask].reset_index(drop=True)
                changes['outliers_removed'] = before_outlier - df.shape[0]

        return df, changes, outlier_mask

    cleaned_df, changes, outlier_mask = auto_clean_data(df.copy())

    st.subheader("Cleaning Summary")
    st.write("**Data Cleaning Actions Performed:**")
    st.write(f"- **Duplicates Removed**: {changes['duplicates_removed']} exact duplicate rows removed.")
    st.write(f"- **Missing Values Filled**: {changes['missing_filled_numeric']} numeric values filled using {numeric_missing_strategy.lower()}. {changes['missing_filled_categorical']} categorical values filled using {categorical_missing_strategy.lower()}." )
    if outlier_action == "Flag only":
        st.write(f"- **Outliers Flagged**: {changes['outliers_flagged']} rows were marked as outliers and kept for review.")
    elif outlier_action == "Remove rows":
        st.write(f"- **Outliers Removed**: {changes['outliers_removed']} rows removed based on numeric outlier detection.")
    else:
        st.write("- **Outlier handling**: no outlier removal or flagging was applied.")

    st.subheader("Cleaned Data")
    st.write(f"Shape: {cleaned_df.shape}")
    st.dataframe(cleaned_df.head())

    with st.expander("Advanced Cleanup Review"):
        st.write("Review what was changed and optionally confirm advanced cleanup before downloading.")
        if duplicate_option == "Remove exact duplicates":
            st.write(f"- {changes['duplicates_removed']} exact duplicate rows were removed.")
        else:
            st.write("- Exact duplicate rows were left unchanged.")

        st.write(f"- Numeric missing values filled: {changes['missing_filled_numeric']} using {numeric_missing_strategy.lower()}.")
        st.write(f"- Categorical missing values filled: {changes['missing_filled_categorical']} using {categorical_missing_strategy.lower()}.")

        if outlier_action == "Flag only":
            st.write(f"- {changes['outliers_flagged']} outlier rows were flagged for review.")
            if changes['outliers_flagged'] > 0:
                st.dataframe(cleaned_df.loc[outlier_mask])
                if "remove_flagged_outliers" not in st.session_state:
                    st.session_state.remove_flagged_outliers = False
                if st.button("Remove flagged outlier rows"):
                    st.session_state.remove_flagged_outliers = True
                if st.session_state.remove_flagged_outliers:
                    cleaned_df = cleaned_df.loc[~outlier_mask].reset_index(drop=True)
                    st.write(f"After removing flagged outliers, cleaned shape is: {cleaned_df.shape}")
        elif outlier_action == "Remove rows":
            st.write(f"- {changes['outliers_removed']} outlier rows were already removed.")
        else:
            st.write("- Outlier handling was skipped.")

        if normalize_text:
            st.write("- Text normalization was applied to string columns.")
        else:
            st.write("- Text normalization was skipped.")

    def to_csv(df):
        output = BytesIO()
        df.to_csv(output, index=False)
        output.seek(0)
        return output

    csv_data = to_csv(cleaned_df)
    st.download_button(label="Download Cleaned Data as CSV", data=csv_data, file_name="cleaned_data.csv", mime="text/csv")

st.write("Note: Data is processed in memory and not stored.")
