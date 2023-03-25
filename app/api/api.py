from app.gcp.big_query.big_query_client import (
    BigQueryClient,
)
from app import (
    __version__,
    __appname__,
    __email__,
    __author__,
)


class Api:
    @staticmethod
    def get_app_details() -> dict:
        return {
            "appname": __appname__,
            "version": __version__,
            "email": __email__,
            "author": __author__,
        }

    @staticmethod
    def get_bigquery_operation_results(
            _query: str, gbq_table_id: str = None
    ) -> dict:
        _bigquery_response = BigQueryClient().execute_query(
            sql_query=_query,
            as_json=True
        )
        return {"response": _bigquery_response}


if __name__ == "__main__":
    print(Api().get_bigquery_operation_results(
        _query="""
            SELECT * FROM `sandbox-381608.user_data.user_profiles`
        """,
        gbq_table_id="sandbox-381608.user_data.user_profiles",
    ))
