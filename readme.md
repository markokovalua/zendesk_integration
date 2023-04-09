**zendesk integration implementation**

use GET `/get_zendesk_token` with zendesk oauth `code` passed in headers to obtain `oauth_token`

use GET `/get_zendesk_tickets` with zendesk oauth `code` or `oauth_token` for auth passed in headers to obtain 
zendesk related tickets

on `code` using - `oauth_token` is taken from session on `oauth_token` it will be used `oauth_token` directly

to run flask app:

1. navigate to project directory `/zendesk__integration`
2. python3 -m venv env
3. source venv/bin/activate 
4. pip install -r requirements.txt
5. set .env file variables
6. run python3 main.py to start flask app

or

install docker to your machine and run using it with a command:

`docker build --tag zendesk-integration . && docker run -d -p 5000:5000 --name zendesk-integration zendesk-integration`

