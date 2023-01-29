from . import models
from imagekitio import ImageKit
import json
import requests as r


with open("credentials.json") as f:
    creds = json.load(f)

api_key = creds['imaggacreds']['api_key']
api_secret = creds['imaggacreds']['api_secret']

imagekit = ImageKit(
    private_key = creds['imagekitcreds']['private_key'],
    public_key = creds['imagekitcreds']['public_key'],
    url_endpoint ='https://ik.imagekit.io/casraysa'
)


def upload_photo(imgstr, photo_path):
    photo_name = photo_path.replace('./images/', '')
    upload_info = imagekit.upload(file = imgstr, file_name = photo_name)

    return upload_info


def find_tags(image_url, min_confidence):
    link = f"https://api.imagga.com/v2/tags?image_url={image_url}"
    response = r.get(link, auth = (api_key, api_secret))

    tags = [
        {'tag': t["tag"]["en"], 'conf': t["confidence"]}
        for t in response.json()["result"]["tags"]
        if t["confidence"] > min_confidence
    ]
    
    return tags


def delete_photo(upload_info):
    imagekit.delete_file(file_id = upload_info.file_id)