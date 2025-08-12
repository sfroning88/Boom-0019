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
    
    if not xlsx_files:
        return jsonify({'success': False, 'message': 'No valid xlsx files found in folder.'}), 400

    print(f"Processing {len(xlsx_files)} xlsx files from folder upload")
    
    # Process each file with progress bar
    from tqdm import tqdm
    processed_files = {}
    
    for file in tqdm(xlsx_files, desc="Processing payroll files"):
        try:
            # Dummy function for now - will be implemented later
            from functions.payroll import process_payroll_file
            payroll_data = process_payroll_file(file=file)

            if payroll_data is None:
                print(f"ERROR: File {file.filename} was not processed successfully")
                continue

            from support.generate import generate_code
            code = generate_code(file.filename)
            
            processed_files[code] = {'filename': file.filename, 'payroll_data': payroll_data}
            
        except Exception as e:
            print(f"ERROR: Failed to process file {file.filename}: {e}")
            continue

    if not processed_files:
        return jsonify({'success': False, 'message': 'No files were successfully processed.'}), 400

    # Store all processed files in config
    import support.config
    support.config.files.update(processed_files)

    return jsonify({'success': True, 'message': f'Successfully processed {len(processed_files)} payroll files.'}), 200

# download the data book xlsx file
@app.route('/DOWNLOAD_DATA_BOOK', methods=['POST'])
def DOWNLOAD_DATA_BOOK():
    import support.config
    from tqdm import tqdm
    import os
    import json
    
    if not support.config.files:
        return jsonify({'success': False, 'message': 'No payroll data available for download.'}), 400
    
    # Get custom download directory from request
    try:
        data = request.get_json()
        if data and 'download_dir' in data:
            custom_dir = data['download_dir'].strip()
            if custom_dir:
                # Expand user path (e.g., ~/Desktop -> /Users/username/Desktop)
                downloads_dir = os.path.expanduser(custom_dir)
            else:
                downloads_dir = os.path.expanduser("~/Downloads")
        else:
            downloads_dir = os.path.expanduser("~/Downloads")
    except:
        downloads_dir = os.path.expanduser("~/Downloads")
    
    # Create downloads directory if it doesn't exist
    if not os.path.exists(downloads_dir):
        try:
            os.makedirs(downloads_dir)
        except Exception as e:
            return jsonify({'success': False, 'message': f'Could not create directory {downloads_dir}: {str(e)}'}), 400
    
    print(f"Starting data book generation and download to {downloads_dir}...")
    
    # Generate data book xlsx file
    try:
        from functions.payroll import generate_data_book
        data_book_content = generate_data_book(support.config.files)
        
        if data_book_content is None:
            return jsonify({'success': False, 'message': 'Failed to generate data book.'}), 400
        
        # Save data book to file
        file_path = os.path.join(downloads_dir, 'payroll_data_book.xlsx')
        
        # Reset buffer position and write to file
        data_book_content.seek(0)
        with open(file_path, 'wb') as f:
            f.write(data_book_content.read())
        
        print(f"Data book downloaded: payroll_data_book.xlsx")
        return jsonify({'success': True, 'message': f'Data book downloaded to {downloads_dir}'}), 200
        
    except Exception as e:
        print(f"ERROR: Could not generate/download data book: {e}")
        return jsonify({'success': False, 'message': f'Failed to generate data book: {str(e)}'}), 400
    
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

    # dictionary for uploaded files
    import support.config
    support.config.files = {}
    print(f"CHECKPOINT: Files dictionary initialized: {'Yes' if support.config.files is not None else 'No'}")

    print(f"CHECKPOINT: Using static domain: https://guiding-needlessly-mallard.ngrok-free.app/oauth/callback")
    
    print("##############################_APP_END_##############################")

    # run the app
    app.run(port=5000)
