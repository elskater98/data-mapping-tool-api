from database import mongo


def allowed_files(filename: str, allowed_extensions: list):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions


def getUser(username: str, projection={"_id": 0}):
    return mongo.db.users.find_one({"username": username}, projection)
