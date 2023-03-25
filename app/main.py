"""
main code for FastAPI setup
"""
import uvicorn
from fastapi import FastAPI, HTTPException
from app.api.api import Api
from app.models.models import AppDetails
from app.models.models import GetBigQueryRequest, GetBigQueryResponse

description = """
API for performing Google BigQuery results🚀

## 
* `get_bigquery_operation_results`: Get BigQuery Operation results
"""

tags_metadata = [
    {
        "name": "default",
        "description": "endpoints for details of app",
    },
    {
        "name": "bigquery-results",
        "description": "get bigquery operations results",
    },
]

app = FastAPI(
    title="Bigquery Cloudbuild app",
    description=description,
    version="0.1",
    docs_url="/docs",
)


@app.get(
    "/",
)
def root():
    return {
        "message": "bigqueryy-operations-result using Fast API in Python. Go to <IP>:8000/docs for API-explorer.",
        "errors": None,
    }


@app.get("/appinfo/", tags=["default"])
def get_app_info() -> AppDetails:
    return AppDetails(**Api().get_app_details())


@app.post(
    "/bigquery_operation_results",
    status_code=200,
    tags=["bigquery-results"],
)
def get_bigquery_operation_results(payload: GetBigQueryRequest) -> GetBigQueryResponse:
    if bigquery_response := Api().get_bigquery_operation_results(
            _query=payload.query,
            gbq_table_id=payload.gbq_table_id,
    ):
        return GetBigQueryResponse(
            request=payload,
            query_results=bigquery_response.get("response")
        )
    else:
        raise HTTPException(status_code=400, detail="Error")


if __name__ == "__main__":
    uvicorn.run("app.main:app", port=8080, reload=True, debug=True, workers=3)
