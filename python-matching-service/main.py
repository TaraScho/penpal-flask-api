from flask import Flask, request, jsonify, render_template, Blueprint
from ddtrace.contrib.trace_utils import set_user
from flask_login import login_required, current_user
from ddtrace.appsec.trace_utils import track_custom_event
from ddtrace import tracer
import requests

main = Blueprint('main', __name__)

penpals = [
    {"id": 1, "name": "Alice", "interests": ["books", "travel"]},
    {"id": 2, "name": "Bob", "interests": ["music", "art"]},
    {"id": 3, "name": "Charlie", "interests": ["coding", "gaming"]}
]

@main.route('/hello', methods=['GET'])
def hello():
    return "Hello, World!"

@main.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@main.route('/match_penpal', methods=['GET'])
@login_required
def match_penpal():
    return render_template('match_form.html', name=current_user.name)

@main.route('/match_penpal', methods=['POST'])
@login_required
def match_penpal_post():
    user_id = request.json.get('user_id')
    details_url = request.json.get('details_url')
    
    # Find a matching penpal for the user (logic can be expanded)
    matched_penpal = penpals[user_id % len(penpals)]

    # SSRF Vulnerability: Make a request to the user-supplied URL
    if details_url:
        try:
            response = requests.get(details_url)
            # Assume the response is JSON and add it to the penpal data
            matched_penpal['details'] = response.json()
        except requests.RequestException as e:
            return jsonify({"error": "Failed to fetch penpal details"}), 400

    return jsonify(matched_penpal)

if __name__ == '__main__':
    main.run(host="0.0.0.0", port=5000)