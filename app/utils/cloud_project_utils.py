"""
utils for working with GCP APIs
"""
import os

from dotenv import load_dotenv


class CloudProjectUtils:
    def __init__(self):
        load_dotenv()
        self.run_env = self.get_run_environment()
        self.secrets_env = "CLOUD"
        self.project_id = None

    @staticmethod
    def get_run_environment():
        return os.getenv("RUN_ENV") or "CLOUD"

    def get_project_id_and_secrets_env(
            self,
    ) -> dict:
        """
        return project-id and secrets_env for GCP using different sources
        :return: dict
        """
        if self.run_env == "LOCAL":
            self.project_id = self._get_project_id_locally()
        else:  # > python37
            self.project_id = self.get_project_id_from_gcp()

            if not self.project_id:
                raise ValueError("Could not get a value for PROJECT_ID")
        return {
            "project_id": self.project_id,
            "secrets_env": self.secrets_env,
        }

    @staticmethod
    def _get_project_id_locally():
        _project_id = os.getenv("GCP_PROJECT_NAME")

        # else if this is running locally then GOOGLE_APPLICATION_CREDENTIALS should be defined
        if not _project_id and "GOOGLE_APPLICATION_CREDENTIALS" in os.environ:
            import json

            with open(os.environ["GOOGLE_APPLICATION_CREDENTIALS"], "r") as fp:
                credentials = json.load(fp)
            _project_id = credentials["project_id"]
        return _project_id or None

    @staticmethod
    def get_project_id_from_gcp():
        # Only works on Cloud App Run
        import urllib.request

        url = "http://metadata.google.internal/computeMetadata/v1/project/project-id"
        req = urllib.request.Request(url)
        req.add_header("Metadata-Flavor", "Google")
        _project_id = urllib.request.urlopen(req).read().decode()

        if not _project_id:  # Running from Cloud Shell
            _project_id = os.environ["DEVSHELL_PROJECT_ID"]

        # If this is running in a cloud function, then GCP_PROJECT should be defined
        if not _project_id and "GCP_PROJECT" in os.environ:
            _project_id = os.environ["GCP_PROJECT"]
        return _project_id or None


if __name__ == "__main__":
    _pid = CloudProjectUtils().get_project_id_and_secrets_env()
    print(_pid)
