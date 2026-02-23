# Auto Data Cleaning Website

This is a simple web application built with Streamlit and Python for automatic data cleaning.

## Features

- Upload CSV or Excel files (.xlsx, .xls)
- Create your own dataset manually using an interactive table
- Automatic data cleaning:
  - Remove duplicate rows
  - Fill missing values (mean for numeric, mode for categorical)
  - Remove outliers using IQR method
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
4. View the original data summary
5. The app will automatically clean the data and show a **Cleaning Summary** explaining what was changed and why
6. View the cleaned data summary
7. Download the cleaned CSV file

## Note

This app runs locally and does not store any data permanently. All processing is done in memory.