def process_payroll_file(employees=None, file=None):
    """
    Process payroll xlsx files and extract employee data.
    Extracts Total Gross Pay and Total Employer Taxes and Contributions for each employee.
    
    Args:
        employees: Global employees dictionary to update
        file: Uploaded xlsx file
        
    Returns:
        Updated employees dictionary or None if processing fails
    """

    if file is None:
        print("ERROR: No file was passed to processing")
        return None

    import pandas as pd
    import re

    # Extract data for each employee
    from functions.year import determine_year
    year = determine_year(file.filename)

    if year is None:
        print("ERROR: Could not determine year from filename")
        return None
    
    # Read Excel file into dataframe
    df = pd.read_excel(file, header=None)
    
    # Find employee names - check headers first
    employee_cols = []
    employee_names = []
    
    # Find employee names in headers (row 0)
    for col_idx in range(len(df.columns)):
        if pd.notna(df.iloc[0, col_idx]):
            # Check if this looks like an employee name (not empty, not a number, not a date)
            cell_value = str(df.iloc[0, col_idx]).strip()
            if (cell_value and 
                not cell_value.replace('.', '').replace(',', '').isdigit() and
                not re.match(r'\d{1,2}/\d{1,2}/\d{2,4}', cell_value) and
                not re.match(r"TOTAL", cell_value) and
                len(cell_value) > 2):
                employee_cols.append(col_idx)
                employee_names.append(cell_value)
    
    if len(employee_cols) == 0:
        print(f"ERROR: Could not find any employees in headers in {year}")
        return None
    
    print(f"Found {len(employee_cols)} employee columns: {employee_cols}")
    if employee_cols:
        print(f"Sample employee names from headers:")
        for col_idx in employee_cols[:3]:  # Show first 3
            print(f"  Column {col_idx}: {df.iloc[0, col_idx]}")
    
    # Find row indexes for Total Gross Pay and Total Employer Taxes
    gross_pay_row = None
    employer_taxes_row = None
    
    # Check Column C for Total Gross Pay
    for idx, value in enumerate(df.iloc[:, 2]):  # Column C
        if pd.notna(value):
            if re.search(r'Total Gross Pay', str(value), re.IGNORECASE):
                gross_pay_row = idx
                break
    
    # Check Column A for Total Employer Taxes and Contributions
    for idx, value in enumerate(df.iloc[:, 0]):  # Column A
        if pd.notna(value):
            if re.search(r'Total Employer Taxes and Contributions', str(value), re.IGNORECASE):
                employer_taxes_row = idx
                break
    
    if gross_pay_row is None:
        print(f"ERROR: Could not find gross pay in {year}")
        return None

    if employer_taxes_row is None:
        print(f"ERROR: Could not find employer taxes and contributions in {year}")
        return None
    
    print(f"#########################################\nProcessing {year}:")
    print(f"Gross pay row: {gross_pay_row+1}, Employer taxes row: {employer_taxes_row+1}")

    number_cols = [x + 4 for x in employee_cols]
    
    employee_iter = 0
    for col_idx in number_cols:
        employee_name = employee_names[employee_iter]
        gross_pay = df.iloc[gross_pay_row, col_idx]
        employer_taxes = df.iloc[employer_taxes_row, col_idx]

        if pd.isna(gross_pay) or pd.isna(employer_taxes):
            print(f"WARNING: Did not process data for {employee_name}")
            continue

        if employee_name not in list(employees.keys()):
            employees[employee_name] = {}

        employees[employee_name][year] = [gross_pay, employer_taxes]
        employee_iter += 1

    return employees
