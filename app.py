import datetime
from flask import Flask, jsonify, request, session
from flask_cors import CORS
from os import environ
import requests
from zenpy import Zenpy, ZenpyException
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = environ.get('SECRET_KEY')
app.permanent_session_lifetime = datetime.timedelta(days=365)
cors = CORS(app, resources={r"*": {"origins": "*"}})

SUBDOMAIN = environ.get('SUBDOMAIN')
CLIENT_ID = environ.get('CLIENT_ID')
CLIENT_SECRET = environ.get('CLIENT_SECRET')

REDIRECT_URI = environ.get('REDIRECT_URI')

def get_zenpy_client(access_token):
    try:
        credentials = {
            'subdomain': SUBDOMAIN,
            'oauth_token': access_token
        }
        zenpy_client = Zenpy(**credentials)
    except ZenpyException as exc:
        """
            "password, token or oauth_token are required! {'self': <zenpy.Zenpy object at 0x104c42370>, 'email': None,
            'token': None, 'oath_token': None, 'password': None, 
            'session': <requests.sessions.Session object at 0x104c42310>}"
        """
        return jsonify({'message': str(exc).split('{')[0]}), 404
    return zenpy_client


@app.route('/get_zendesk_token', methods=['GET'])
def get_zendesk_token():
    code = request.headers.get("code")
    token_endpoint = f'https://{SUBDOMAIN}.zendesk.com/oauth/tokens'
    data = {
            'grant_type': 'authorization_code',
            'client_id': CLIENT_ID,
            'code': code,
            'client_secret': CLIENT_SECRET,
            'scope': 'offline',
            'redirect_uri': REDIRECT_URI
    }
    response = requests.post(token_endpoint, data=data)
    tokens = response.json()
    if not response.ok:
        return jsonify({'message': tokens.get('error_description')}), response.status_code
    return jsonify({"access_token": tokens.get('access_token')}), response.status_code


@app.route('/get_zendesk_tickets', methods=['GET'])
def get_zendesk_tickets():
    # Docs: ZenPy: http://docs.facetoe.com.au/api_objects.html
    access_token = request.headers.get('access_token')
    zenpy_client = get_zenpy_client(access_token)
    try:
        tickets = [ticket.to_dict() for ticket in zenpy_client.tickets()]
    except Exception as exc:
        """
            {
                'error': 'invalid_token', 'error_description': 
                'The access token provided is expired, revoked, malformed or invalid for other reasons.'
            }
        """
        return jsonify({'message': exc.response.json().get('error_description')}), exc.response.status_code
    return jsonify(tickets), 200


if __name__ == '__main__':
    # app.debug = True
    app.run()
