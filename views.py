from flask import Blueprint, request, make_response, jsonify
from . import controller

bp = Blueprint('images', __name__, url_prefix='/')

@bp.post("/image")
def process_pict():
    min_confidence = request.args.get("min_confidence")
    
    min_confidence = 80 if min_confidence is None else int(min_confidence)
    
    if not request.is_json or "data" not in request.json:
        return make_response({"description": "Debes incluir la foto en base64 en el campo data del body."}, 400)
    
    imgb64str = request.json["data"]
        
    d = controller.get_tags(imgb64str, min_confidence)

    return jsonify(d)

@bp.get("/images")
def images():
    min_date = request.args.get("min_date")
    max_date = request.args.get("max_date")
    tags = request.args.get("tags")
    
    if min_date is not None:
        min_date.replace("%20", " ")
        
    if max_date is not None:
        max_date.replace("%20", " ")
        
    if tags is not None:
        tags = tags.replace("%20", " ")
        tags = "'" + tags.replace(",", "','") + "'"
    
    d = controller.models.get_images(min_date, max_date, tags)
   
    return d
 
@bp.get("/image/<id>")
def image(id):
    return controller.models.get_image(id)

@bp.get("/tags")
def tags():
    min_date = request.args.get("min_date")
    max_date = request.args.get("max_date")
    
    if min_date is not None:
        min_date.replace("%20", " ")
        
    if max_date is not None:
        max_date.replace("%20", " ")
    
    d = controller.models.get_tags(min_date, max_date)
    
    return d