from pydantic import BaseModel
from typing import Union


class GbqTableDetails:
    def __init__(self, table_id: str):
        table_id = table_id.replace("`", "")
        self.table_id = table_id
        self.project_id = table_id.split(".")[0] if "." in table_id else None
        self.dataset_name = table_id.split(".")[1] if "." in table_id else None
        self.table_name = table_id.split(".")[2] if "." in table_id else table_id


class GbqUploadResults(BaseModel):
    table_id: str
    job_id: str = None
    errors: Union[str, list, int] = None
    num_rows: int = 0