# Boom-0019
# Payroll Data Conversion Tool

A Flask-based web application that processes payroll XLSX files and converts them into a standardized data book format for financial analysis and reporting.

## Project Overview

This tool is designed to process multiple payroll files organized by year (2022, 2023, 2024, YTD 2025) for a given entity, and produce a simple excel file that can be copy and pasted into an existing payroll workbook.

## Core Functionality

### What the Tool Does
1. **Uploads and processes** multiple XLSX payroll files from a selected folder
2. **Extracts key data** from each file:
   - Total Gross Pay (by employee)
   - Total Employer Taxes and Contributions (by employee)
4. **Generates a data book** in the specified template format
5. **Downloads the result** as a single Excel file

### What Gets Excluded
- All other payroll data (hours, rates, individual pay types, deductions, etc.)
- Non-essential payroll information
- Raw file data

## Workflow

### Step 1: File Upload
- User clicks "Upload Payroll Files" button
- User selects a folder containing XLSX payroll files
- System processes each XLSX file in the folder
- Files are validated (must be .xlsx format)

### Step 2: Data Processing
- Each XLSX file is parsed to extract:
  - Employee names
  - Total Gross Pay values
  - Total Employer Taxes and Contributions values
- Data is organized by employee and year
- Results are stored in memory for the session

### Step 3: Data Book Generation
- User clicks "Generate Data Book" button
- User specifies download directory
- System creates a single Excel file with the template format
- File is saved as `payroll_data_book.xlsx`

## Input/Output Specifications

### Input Files
- **Format**: XLSX (Excel) files
- **Content**: Payroll data with employee information from QBD
- **Structure**: Employee names in columns with data 4 columns over

### Output File
- **Filename**: `payroll_data_book.xlsx`
- **Format**: Data Book template with annual columns populated
- **Structure**:
    Sheet 1: Gross Total Pay
    - Headers: Years (lowest to highest)
    - Column A: (Employee Name)
    - Column B: (Gross Total Pay)

    Sheet 2: Employer Taxes and Contributions
    - Headers: Years (lowest to highest)
    - Column A: (Employee Name)
    - Column B: (Employer Taxes and Contributions)

## Data Storage Format

### Employee Data Structure
The application now uses a global `employees` dictionary that stores payroll data organized by employee and year:

```python
{
    "employee_name": {
        "year": [gross_pay, employer_taxes],
        "2022": [47650.91, 503.16],
        "2023": [48500.00, 520.00],
        "2024": [49200.00, 540.00],
        "2025": [12500.00, 150.00]
    }
}
```

### Annual Data Aggregation
- **2022**: Data from 2022 payroll files
- **2023**: Data from 2023 payroll files  
- **2024**: Data from 2024 payroll files
- **2025**: Data from YTD 2025 payroll files

## Technical Architecture

### Backend (Flask)
- **File Upload Endpoint**: `/UPLOAD_XLSX_FILES`
- **Data Book Generation**: `/DOWNLOAD_DATA_BOOK`
- **File Processing**: `functions/payroll.py`, `functions/databook.py`
- **Configuration**: `support/config.py` (global `employees` dictionary)

### Frontend (HTML/JavaScript)
- **Chat Interface**: Modern chat-style UI with BOOM branding
- **File Selection**: Directory picker for XLSX files
- **Progress Tracking**: Real-time status updates
- **Responsive Design**: Bootstrap-based layout

### Dependencies
- **Flask**: Web framework
- **ngrok**: Tunnel service for external access
- **tqdm**: Progress bar functionality
- **openpyxl**: Excel file processing

## Usage Instructions

1. **Start the application**: `python3 app.py`
2. **Access the interface**: Navigate to the provided ngrok URL
3. **Upload files**: Click "Upload Payroll Files" and select folder
4. **Generate output**: Click "Generate Data Book" and specify download location
5. **Download result**: Retrieve `payroll_data_book.xlsx` from specified directory

## Future Enhancements

- Batch processing for large file sets
- Data validation and error reporting
- Custom entity mapping configuration
- Historical data comparison features
- Export to additional formats (CSV, PDF)
- User authentication and file management
