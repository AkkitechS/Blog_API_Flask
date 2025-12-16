import cloudinary.uploader

def upload_to_cloudinary(file, directory):
    result = cloudinary.uploader.upload(file, folder=directory, resource_type="image")
    print(f'RESULT : {result}')
    return result.get('secure_url')