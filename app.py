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

# upload the txt file
@app.route('/UPLOAD_TXT_FILE', methods=['POST'])
def UPLOAD_TXT_FILE():
    files = request.files.getlist('file')
    if not files:
        return jsonify({'success': False, 'message': 'No files detected.'}), 400

    from support.extension import ALLOWED_EXTENSIONS, retrieve_extension
    
    # Filter only txt files
    txt_files = []
    for file in files:
        if retrieve_extension(file.filename) in ALLOWED_EXTENSIONS:
            txt_files.append(file)
    
    if not txt_files:
        return jsonify({'success': False, 'message': 'No valid txt files found in folder.'}), 400

    print(f"Processing {len(txt_files)} txt files from folder upload")
    
    # Process each file with progress bar
    from tqdm import tqdm
    processed_files = {}
    
    for file in tqdm(txt_files, desc="Converting txt files"):
        try:
            from functions.t2c import convert_t2c
            converted_file = convert_t2c(file=file)

            if converted_file is None:
                print(f"ERROR: File {file.filename} was not converted into csv successfully")
                continue

            from functions.c2x import convert_c2x
            converted_file = convert_c2x(converted_file=converted_file)

            if converted_file is None:
                print(f"ERROR: File {file.filename} was not converted into xlsx successfully")
                continue

            from support.generate import generate_code
            code = generate_code(file.filename)
            
            processed_files[code] = {'filename': file.filename, 'content': converted_file}
            
        except Exception as e:
            print(f"ERROR: Failed to process file {file.filename}: {e}")
            continue

    if not processed_files:
        return jsonify({'success': False, 'message': 'No files were successfully converted.'}), 400

    # Store all processed files in config
    import support.config
    support.config.files.update(processed_files)

    return jsonify({'success': True, 'message': f'Successfully processed {len(processed_files)} files from folder.'}), 200

# download the xlsx file
@app.route('/DOWNLOAD_XLSX_FILE', methods=['POST'])
def DOWNLOAD_XLSX_FILE():
    import support.config
    from tqdm import tqdm
    import os
    import json
    
    if not support.config.files:
        return jsonify({'success': False, 'message': 'No files available for download.'}), 400
    
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
    
    print(f"Starting download of {len(support.config.files)} files to {downloads_dir}...")
    
    # Download each file with progress bar
    successful_downloads = 0
    for code, file_info in tqdm(support.config.files.items(), desc="Downloading files"):
        filename = file_info['filename']
        content = file_info['content']
        
        # Generate Excel filename
        excel_filename = os.path.splitext(os.path.basename(filename))[0] + '.xlsx'
        
        # For folder uploads, maintain the subfolder structure but avoid duplication
        if '/' in filename:
            # Extract the subfolder path (everything after the base folder)
            path_parts = filename.split('/')
            if len(path_parts) > 1:
                # Skip the base folder name and join the rest
                subfolder_path = '/'.join(path_parts[1:-1])  # Exclude base folder and filename
                if subfolder_path:
                    full_download_path = os.path.join(downloads_dir, subfolder_path)
                    # Create subfolder if it doesn't exist
                    if not os.path.exists(full_download_path):
                        os.makedirs(full_download_path)
                    file_path = os.path.join(full_download_path, excel_filename)
                else:
                    # No subfolder, save directly in base folder
                    file_path = os.path.join(downloads_dir, excel_filename)
            else:
                # Fallback: save directly in base folder
                file_path = os.path.join(downloads_dir, excel_filename)
        else:
            file_path = os.path.join(downloads_dir, excel_filename)
        
        try:
            # Reset buffer position and write to file
            content.seek(0)
            with open(file_path, 'wb') as f:
                f.write(content.read())
            print(f"Downloaded: {excel_filename}")
            successful_downloads += 1
        except Exception as e:
            print(f"ERROR: Could not download {excel_filename}: {e}")
    
    print(f"Download complete! Successfully downloaded {successful_downloads} out of {len(support.config.files)} files")
    return jsonify({'success': True, 'message': f'Downloaded {successful_downloads} files to {downloads_dir}'}), 200
    
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
