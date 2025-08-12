def determine_year(filename=None):
    """
    Extract year from filename using pattern matching.
    Looks for 4 consecutive numbers with spaces on either side.
    
    Args:
        filename: String filename to extract year from
        
    Returns:
        Year string (e.g., "2022", "2023") or "Unknown" if no match found
    """

    if filename is None or len(filename) == 0:
        print("ERROR: No filename passed to years function")
        return None

    import re
    pattern = r'\s(\d{4})\s'
    match = re.search(pattern, filename)
    year_found = match.group(1) if match else None
    
    if year_found == None:
        print(f"ERROR: No year found in {filename}, cannot process")
        return None

    from support.config import years
    if year_found not in years:
        years.append(year_found)
    
    return match.group(1) if match else None
