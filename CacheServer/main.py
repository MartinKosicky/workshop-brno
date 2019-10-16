from flask import Flask
from flask import request, jsonify
from flask_cors import CORS
import jsonschema
app = Flask(__name__)
cors = CORS(app)

max_applications = {}

@app.errorhandler(jsonschema.exceptions.ValidationError)
def handle_validation_error(error):
    response = jsonify(error.to_dict())
    response.status_code = 400
    return response



@app.route('/top_applications/<episode>', methods=["GET"])
def get_top_applications(episode):
    global app

    if episode not in max_applications:
        return app.make_response(("Episode not found", 404))

    apps = max_applications[episode][:]

    def key_getter(val):
        return val["count"]
    apps.sort(key=key_getter, reverse = True)

    apps = apps[:10]
    return jsonify(apps)

@app.route('/set_top_applications', methods=["POST"])
def set_top_applications():
    schema = {
        "type":"object",
        "required":["partition","episode","applications"],
        "properties":{
            "partition":{"type":"string"},
            "episode":{"type":"integer", "minimum":0},
            "applications": {
                "type":"array",
                "maxItems": 10,
                "items": {
                    "type":"object",
                    "properties":{
                        "name":{"type":"string"},
                        "count":{"type":"integer","minimum": 0, }
                     },
                    "required":["name","count"]
                }
             }
        }
    }

    data = request.get_json()
    jsonschema.validate(data, schema=schema)
    v = max_applications.setdefault(str(data["episode"]), []).extend(data["applications"])
    return jsonify(True)


least_applications = {}

@app.route('/least_applications/<episode>', methods=["GET"])
def get_least_applications(episode):
    global app

    if episode not in least_applications:
        return app.make_response(("Episode not found", 404))

    apps = least_applications[episode][:]

    def key_getter(val):
        return val["count"]
    apps.sort(key=key_getter, reverse = False)

    apps = apps[:10]
    return jsonify(apps)

@app.route('/set_least_applications', methods=["POST"])
def set_least_applications():
    schema = {
        "type":"object",
        "required": ["partition", "episode","applications" ],
        "properties":{
            "partition":{"type":"string"},
            "episode":{"type":"integer", "minimum":0},
            "applications": {
                "type":"array",
                "maxItems": 10,
                "items": {
                    "type":"object",
                    "properties":{
                        "name":{"type":"string"},
                        "count":{"type":"integer","minimum": 0, }
                     },
                    "required": ["name", "count"]
                }
             }
        }
    }

    data = request.get_json()
    jsonschema.validate(data, schema=schema)
    v = least_applications.setdefault(str(data["episode"]), []).extend(data["applications"])
    return jsonify(True)


if __name__=="__main__":
    app.run(host="0.0.0.0",port=9999)
