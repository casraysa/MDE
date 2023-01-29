from flask import Blueprint, request, make_response, jsonify
from . import controller

bp = Blueprint('images', __name__, url_prefix='/')

@bp.post("/image")
def process_pict():
    
    if not request.is_json or "data" not in request.json:
        return make_response({"description": "Debes incluir la foto en base64 en el campo data del body."}, 400)
    
    photo_path = request.json["path"]
    size = request.json["size"]
    imgstrb64 = request.json["data"]
        
    controller.models.add_photo(photo_path, size, imgstrb64)

    photo_info = controller.upload_photo(imgstrb64)
    tags = controller.find_tags(photo_info.url, 80)
    controller.delete_photo(photo_info)
    
    photo_dict = controller.models.get_photo_dict(photo_path)  
    controller.models.insert_tags(photo_dict, tags)
    
    d = controller.models.get_image(photo_dict['id'])  

    return jsonify(d)

@bp.get("/images")
def images():
    d = controller.models.get_images()
   
    return jsonify(d)
 
@bp.get("/image")
def image():
    id = request.args.get("id")
    
    if id is None:
        return make_response({"description": "Debes especificar un id de photo en la llamada."}, 400)
    
    d = controller.models.get_image(id)
    
    return jsonify(d)

@bp.get("/tags")
def tags():
    min_date = request.args.get("min_date")
    max_date = request.args.get("max_date")
    d = controller.models.get_tags(min_date, max_date)
    
    return jsonify(d)