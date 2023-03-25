from pydantic import BaseModel
from typing import Union, List


class AppDetails(BaseModel):
    appname: str
    version: str
    email: str
    author: str


class GetBigQueryRequest(BaseModel):
    query: str
    gbq_table_id: Union[str, None] = None


class GetBigQueryResponse(BaseModel):
    request: GetBigQueryRequest
    query_results: Union[dict, None] = None


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


class GcpResponse(BaseModel):
    status: str = None
    message: str = None


class GcsUploadResults(BaseModel):
    project_id: str
    bucket_id: Union[str, List[str]]
    response: Union[GcpResponse, str, dict] = None
    errors: str = None


class GcsBucketPathDetails:
    """
    model for Gcs Bucket and subdir-path object based on bucket-id passed
    """

    def __init__(self, bucket_id: str):
        self.bucket_id = bucket_id
        _split = bucket_id.split(".") if "." in bucket_id else [bucket_id]
        self.project_id = _split[0] if "." in bucket_id else None
        self.bucket_name = _split[1] if "." in bucket_id else bucket_id
        self.sub_dir = _split[2] if "." in bucket_id and len(_split) > 2 else None
