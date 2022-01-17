def allowed_files(filename: str, allowed_extensions: list):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions
