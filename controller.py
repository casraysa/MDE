from . import models
from imagekitio import ImageKit
import json
import requests as r
from uuid import uuid4

with open("credentials.json") as f:
    creds = json.load(f)

imagekit = ImageKit(
    private_key = creds['imagekitcreds']['private_key'],
    public_key = creds['imagekitcreds']['public_key'],
    url_endpoint ='https://ik.imagekit.io/casraysa'
)

api_key = creds['imaggacreds']['api_key']
api_secret = creds['imaggacreds']['api_secret']

def get_tags(b64str, min_confidence):
    
    photo_name = str(uuid4())
    # Generamos la URL para luego llamar a la API de imagekitio
    upload_info = imagekit.upload(file = b64str, file_name = photo_name)
    
    link = f"https://api.imagga.com/v2/tags?image_url={upload_info.url}"
    response = r.get(link, auth = (api_key, api_secret))

    tags = [
        {'tag': t["tag"]["en"], 'conf': t["confidence"]}
        for t in response.json()["result"]["tags"]
        if t["confidence"] > min_confidence
    ]
    
    imagekit.delete_file(file_id = upload_info.file_id)
    
    # Guardamos la imagen en una carpeta determinada
    file_name = "images/" + photo_name
    with open(file_name, 'w') as f:
        f.write(b64str)
    
    # Guardamos en BBDD y devolvemos respuesta
    return models.tags(file_name, tags)