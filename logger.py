import logging
import sys
from google.oauth2 import service_account
import google.cloud.logging

SERVICE_NAME = "zendesk-oauth"


def get_logger():
    return logging.getLogger(SERVICE_NAME)


def _init_logger(isGCPLogging: bool):
    logger = get_logger()

    logger.setLevel(logging.INFO)

    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(name)s - %(message)s")
    if isGCPLogging:
        # Docs: https://google-auth.readthedocs.io/en/latest/user-guide.html
        credentials = service_account.Credentials.from_service_account_file('service_acc_credentials.json')
        # Create a handler for Google Cloud Logging.
        gcloud_logging_client = google.cloud.logging.Client(project="ask-ai-sandbox", credentials=credentials)
        gcloud_logging_client.setup_logging()
    else:
        # Create a stream handler to log messages to the console.
        stream_handler = logging.StreamHandler(sys.stdout)
        stream_handler.setFormatter(formatter)
        stream_handler.setLevel(logging.INFO)
        logger.addHandler(stream_handler)


_init_logger(isGCPLogging=True)


