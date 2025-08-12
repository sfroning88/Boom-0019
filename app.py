import os, sys
from flask import Flask, render_template, request, jsonify
from ngrok import connect

# create a Flask app
app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'default_secret_key')

# get the Ngrok token
ngrok_token = os.environ.get('NGROK_API_TOKEN')

@app.route('/')
def home():
    # render base home template
    return render_template('chat.html')

# upload the xlsx payroll files
@app.route('/UPLOAD_XLSX_FILES', methods=['POST'])
def UPLOAD_XLSX_FILES():
    files = request.files.getlist('file')
    if not files:
        return jsonify({'success': False, 'message': 'No files detected.'}), 400

    from support.extension import ALLOWED_EXTENSIONS, retrieve_extension
    
    # Filter only xlsx files
    xlsx_files = []
    for file in files:
        if retrieve_extension(file.filename) in ALLOWED_EXTENSIONS:
            xlsx_files.append(file)
    
    if len(xlsx_files) == 0:
        return jsonify({'success': False, 'message': 'No valid xlsx files found in folder.'}), 400

    print(f"Processing {len(xlsx_files)} xlsx files from folder upload")
    
    # Process each file with progress bar
    from tqdm import tqdm
    
    for file in tqdm(xlsx_files, desc="Processing payroll files"):
        from functions.payroll import process_payroll_file
        support.config.employees = process_payroll_file(employees=support.config.employees, file=file)

        if support.config.employees is None:
            print(f"ERROR: File {file.filename} was not processed successfully")
            continue

    if len(support.config.employees.keys()) == 0:
        return jsonify({'success': False, 'message': 'No files were successfully processed.'}), 400

    return jsonify({'success': True, 'message': f'Successfully processed {len(xlsx_files)} payroll files.'}), 200

# download the data book xlsx file
@app.route('/DOWNLOAD_DATA_BOOK', methods=['POST'])
def DOWNLOAD_DATA_BOOK():
    import support.config
    import os
    
    if not support.config.employees:
        return jsonify({'success': False, 'message': 'No payroll data available for download.'}), 400
    
    # Get custom download directory from request
    data = request.get_json()
    if data and 'download_dir' in data:
        custom_dir = data['download_dir'].strip()
        if custom_dir:
            # Expand user path (e.g., ~/Desktop -> /Users/username/Desktop)
            downloads_dir = os.path.expanduser(custom_dir)
        else:
            downloads_dir = os.path.expanduser("~/Downloads")
    
    if not os.path.exists(downloads_dir):
        return jsonify({'success': False, 'message': 'Invalid directory path provided.'}), 400
       
    print(f"Starting data book generation and download to {downloads_dir}...")
    
    # Generate data book xlsx file
    from functions.databook import generate_data_book
    data_book_content = generate_data_book(employees=support.config.employees, years=support.config.years)
        
    if data_book_content is None:
        return jsonify({'success': False, 'message': 'Failed to generate data book.'}), 400
        
    # Save data book to file
    file_path = os.path.join(downloads_dir, 'payroll_data_book.xlsx')
        
    # Write the BytesIO content to file
    with open(file_path, 'wb') as f:
        f.write(data_book_content.getvalue())
        
    print(f"Data book downloaded: payroll_data_book.xlsx")
    return jsonify({'success': True, 'message': f'Data book downloaded to {downloads_dir}'}), 200
        
if __name__ == '__main__':
    if len(sys.argv) != 1:
        print("Usage: python3 app.py")
        sys.exit(1)

    # ngrok tunnel URL (will be set when tunnel is created)
    ngrok_url = None

    # Check if ngrok is available and create tunnel
    import importlib.util
    ngrok_spec = importlib.util.find_spec("ngrok")
    
    if ngrok_spec is None:
        print("ERROR: ngrok package not available")
        sys.exit(1)

    # Authenticate with ngrok using environment token
    if ngrok_token is None:
        print("ERROR: Please set your ngrok token")
        sys.exit(1)
    
    from ngrok import set_auth_token
    set_auth_token(ngrok_token)

    from ngrok import connect
    tunnel = connect(5000, domain="guiding-needlessly-mallard.ngrok-free.app")

    if tunnel is None:
        print("ERROR: Failed to connect to ngrok tunnel, check active instances")
        sys.exit(1)

    print("##############################_APP_BEGIN_##############################")

    # dictionary for employee payroll data
    import support.config
    support.config.employees = {}
    support.config.years = []

    print(f"CHECKPOINT: Employees dictionary initialized: {'Yes' if support.config.employees is not None else 'No'}")
    print(f"CHECKPOINT: Years list initialized: {'Yes' if support.config.years is not None else 'No'}")
    
    print(f"CHECKPOINT: Using static domain: https://guiding-needlessly-mallard.ngrok-free.app/oauth/callback")
    
    print("##############################_APP_END_##############################")

    # run the app
    app.run(port=5000)
