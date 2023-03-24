"""
Base-client for GCP APIs
"""
from dotenv import load_dotenv

from app.utils.cloud_project_utils import CloudProjectUtils


class BaseClient:

    def __init__(self, project_id: str = None):
        load_dotenv()
        _pid_senv = CloudProjectUtils().get_project_id_and_secrets_env()
        self.project_id = project_id or _pid_senv.get("project_id")
        self.secrets_env = _pid_senv.get("secrets_env") or None
