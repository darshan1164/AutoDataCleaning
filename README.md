# Auto Data Cleaning Website

This is a simple web application built with Streamlit and Python for automatic data cleaning.

## Features

- Upload CSV or Excel files (.xlsx, .xls)
- Create your own dataset manually using an interactive table
- Configurable automatic data cleaning:
  - Optional exact duplicate removal
  - Numeric missing values can be filled with mean, median, or zero
  - Categorical missing values can be filled with mode, `unknown`, or `missing`
  - Normalize text values by trimming whitespace and converting to lowercase
  - Detect numeric outliers using the IQR method
  - Choose to flag outliers, remove rows, or skip outlier handling
- Advanced cleanup review section:
  - review which changes were made
  - inspect flagged outlier rows
  - optionally remove flagged outliers before downloading
- Download cleaned data as CSV
- No data storage - everything is processed in memory

## Requirements

- Python 3.7+
- Streamlit
- Pandas
- NumPy
- OpenPyXL (for Excel support)

## Installation

1. Clone or download this repository
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

## Running the App

Run the following command in the terminal:

```
streamlit run app.py
```

Then open the URL shown in the terminal (usually http://localhost:8501) in your browser.

## Usage

1. Choose between "Upload File" or "Create Dataset"
2. **For Upload File**: Select a CSV or Excel file
3. **For Create Dataset**: Edit the table to add your data, then click "Use This Dataset"
4. Set cleaning options in the "Cleaning Options" expander:
   - duplicate removal
   - numeric missing value strategy
   - categorical missing value strategy
   - text normalization
   - outlier handling
5. Review the original data summary
6. Review the cleaning summary and advanced cleanup section
7. If outliers were flagged, inspect the flagged rows and optionally remove them
8. Download the cleaned CSV file

## Note

This app runs locally and does not store any data permanently. All processing is done in memory.
