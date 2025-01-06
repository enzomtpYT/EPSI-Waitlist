from flask import Flask
import os
from routes.index import index

app = Flask(__name__)

custom_route_names = {
    "/": "Acceuil",
}

def get_routes():
    routes = []
    for rule in app.url_map.iter_rules():
        if rule.endpoint != 'static':
            routes.append(rule.rule)
    return routes

@app.context_processor
def inject_routes():
    return dict(routes=get_routes(), custom_route_names=custom_route_names)

app.add_url_rule("/", "index", index)

if __name__ == "__main__":
    debug_mode = os.getenv('FLASK_ENV') == 'development'
    app.run(host="127.0.0.1", port=8080, debug=debug_mode)