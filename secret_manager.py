import json
from google.cloud import secretmanager
from google.api_core.exceptions import NotFound


# handle gcp credentials
class SecretsManagerWrapper:
    def __init__(self, project_name, client_path):
        self._secret_manager_client = secretmanager.SecretManagerServiceClient.from_service_account_file(client_path)
        self._gcp_project = project_name

    def get_secret(self, name):
        version = self._secret_manager_client.get_secret_version(
            request={"name": f"projects/{self._gcp_project}/secrets/{name}/versions/latest"}
        )

        response = self._secret_manager_client.access_secret_version(request={"name": version.name})
        payload = json.loads(response.payload.data.decode("UTF-8"))
        return payload

    def create_secret(self, name: str, value: str):
        # Create the parent secret.

        parent = f"projects/{self._gcp_project}"
        secret_path = self._secret_manager_client.secret_path(self._gcp_project, name)

        try:
            secret = self._secret_manager_client.get_secret(request={"name": secret_path})
        except NotFound:
            secret = self._secret_manager_client.create_secret(
                request={
                    "parent": parent,
                    "secret_id": name,
                    "secret": {"replication": {"automatic": {}}},
                }
            )

        # Add the secret version.
        self._secret_manager_client.add_secret_version(
            request={"parent": secret.name, "payload": {"data": value.encode()}}
        )
