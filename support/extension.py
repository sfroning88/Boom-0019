ALLOWED_EXTENSIONS = ['txt']

def retrieve_extension(filename):
    exte = '.' in filename and filename.rsplit('.', 1)[1].lower()
    return exte.strip().lower()
