# Boom-0019
# Payroll Data Conversion Tool

A Flask-based web application that processes payroll XLSX files and converts them into a standardized data book format for financial analysis and reporting.

## Project Overview

This tool is designed to process multiple payroll files organized by year (2022, 2023, 2024, YTD 2025) for two entities: **BC Stone** and **BC Stone Salem**. The application extracts specific payroll data from each file and consolidates it into a single data book Excel file that can be copy-pasted into larger financial models.

## Core Functionality

### What the Tool Does
1. **Uploads and processes** multiple XLSX payroll files from a selected folder
2. **Extracts key data** from each file:
   - Total Gross Pay (by employee)
   - Total Employer Taxes and Contributions (by employee)
3. **Separates employees** by entity (BC Stone vs. BC Stone Salem)
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
- Data is organized by employee and entity
- Results are stored in memory for the session

### Step 3: Data Book Generation
- User clicks "Generate Data Book" button
- User specifies download directory
- System creates a single Excel file with the template format
- File is saved as `payroll_data_book.xlsx`

## Input/Output Specifications

### Input Files
- **Format**: XLSX (Excel) files
- **Content**: Payroll data with employee information
- **Required Rows**:
  - Row 25: "Total Gross Pay" (annual totals)
  - Row 34: "Total Deductions from Gross Pay" (annual totals)
- **Structure**: Employee names in columns, annual data in "Jan - Dec 24" columns

### Output File
- **Filename**: `payroll_data_book.xlsx`
- **Format**: Data Book template with annual columns populated
- **Structure**:
  - Column B: Employee names
  - Columns D-G: Annual data (2022, 2023, 2024, YTD25) in $ thousands
  - Columns H-K: Percentage of total calculations
  - Monthly columns (N-S): Left blank as per requirements

## Data Storage Format

### Employee Data Structure
```python
{
    "employee_name": [gross_pay, employer_taxes],
    "Akers, Malex": [47650.91, 503.16],
    "Akers, Tracie L.": [45725.70, 5724.31],
    "Bair, Mackenzie": [58796.87, 4265.77]
}
```

### Entity Separation
- **BC Stone**: Primary entity employees
- **BC Stone Salem**: Secondary entity employees
- Employees are categorized based on their source file or metadata

### Annual Data Aggregation
- **2022**: Data from 2022 payroll files
- **2023**: Data from 2023 payroll files  
- **2024**: Data from 2024 payroll files
- **YTD25**: Data from YTD 2025 payroll files

## Technical Architecture

### Backend (Flask)
- **File Upload Endpoint**: `/UPLOAD_XLSX_FILES`
- **Data Book Generation**: `/DOWNLOAD_DATA_BOOK`
- **File Processing**: `functions/payroll.py`
- **Configuration**: `support/config.py`

### Frontend (HTML/JavaScript)
- **Chat Interface**: Modern chat-style UI with BOOM branding
- **File Selection**: Directory picker for XLSX files
- **Progress Tracking**: Real-time status updates
- **Responsive Design**: Bootstrap-based layout

### Dependencies
- **Flask**: Web framework
- **ngrok**: Tunnel service for external access
- **tqdm**: Progress bar functionality
- **openpyxl**: Excel file processing (to be implemented)

## Development Status

### ✅ Completed
- Project structure and Flask setup
- Frontend interface and user experience
- File upload and download endpoints
- Basic routing and error handling
- Dummy function placeholders

### 🔄 To Be Implemented
- **`process_payroll_file()`**: XLSX parsing and data extraction
- **`generate_data_book()`**: Data book Excel generation
- Entity identification logic
- Data validation and error handling
- Excel template formatting

## File Structure
```
Boom-0019/
├── app.py                 # Main Flask application
├── functions/
│   └── payroll.py        # Payroll processing functions
├── support/
│   ├── config.py         # Configuration and file storage
│   ├── extension.py      # File type validation
│   └── generate.py       # Code generation utilities
├── templates/
│   └── chat.html         # Frontend interface
├── static/
│   └── style.css         # Custom styling
└── requirements.txt       # Python dependencies
```

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

## Notes for Developers

- The application uses dummy functions in `functions/payroll.py` as placeholders
- File processing logic needs to be implemented based on the specific payroll file structure
- Entity separation logic should be developed based on file naming conventions or metadata
- Excel generation should follow the exact template format shown in the reference images
- Error handling should be robust for various file formats and data inconsistencies
