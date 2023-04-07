from flask import Flask, jsonify, request, session
import os
import requests
from zenpy import Zenpy, ZenpyException

app = Flask(__name__)
app.secret_key = "super secret key"

ZENPY_CLIENTS = {

}


@app.route('/get_zendesk_token')
def get_zendesk_token():
    code = request.headers.get("code")
    token_endpoint = f'https://{os.environ.get("SUBDOMAIN")}.zendesk.com/oauth/tokens'
    data = {
            'grant_type': 'authorization_code',
            'client_id': os.environ.get('CLIENT_ID'),
            'code': code,
            'client_secret': os.environ.get('CLIENT_SECRET'),
            'scope': 'offline',
            'redirect_uri': os.environ.get('REDIRECT_URI')
    }
    response = requests.post(token_endpoint, data=data)
    tokens = response.json()
    if not response.ok:
        return jsonify({'message': tokens.get('error_description')}), response.status_code
    session[code] = tokens.get('access_token')
    return jsonify({"oauth_token": session[code]}), response.status_code


@app.route('/get_zendesk_tickets')
def get_zendesk_tickets():
    # Docs: ZenPy: http://docs.facetoe.com.au/api_objects.html
    code = request.headers.get("code")
    oauth_token = session.get(code) or request.headers.get('oauth_token')
    try:
        if oauth_token in ZENPY_CLIENTS:
            zenpy_client = ZENPY_CLIENTS.get(oauth_token)
        else:
            credentials = {
                'subdomain': os.environ.get("SUBDOMAIN"),
                'oauth_token': oauth_token
            }
            zenpy_client = Zenpy(**credentials)
            ZENPY_CLIENTS[oauth_token] = zenpy_client
        tickets = [ticket.to_dict() for ticket in zenpy_client.tickets()]
    except ZenpyException as exc:
        """
            "password, token or oauth_token are required! {'self': <zenpy.Zenpy object at 0x104c42370>, 'email': None,
            'token': None, 'oath_token': None, 'password': None, 
            'session': <requests.sessions.Session object at 0x104c42310>}"
        """
        return jsonify({'message': str(exc).split('{')[0]}), 404
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
    app.run(host="127.0.0.1", port=8115)
