"""
class to interact with BigQuery tables using google apis
"""
from google.cloud import bigquery
from app.utils.data_string_utils import pretty_print_df
import json

from app.gcp.base_client import BaseClient


class BigQueryClient(BaseClient):
    def __init__(self, project_id: str = None):
        super().__init__(project_id)
        self.bq_client = bigquery.Client()

    def get_dataset_tables_list(
        self, dataset_name: str, stdout_print: bool = True
    ) -> list:
        """
        get list of tables in the schema
        :param dataset_name: str|dataset-name
        :param stdout_print: bool|print the tables list on
        :return: list of dicts|each dict containing info of one table
        """
        dataset_id = f"{self.project_id}.{dataset_name}"

        tables = self.bq_client.list_tables(dataset_id)
        tables_list = [
            {
                "table_id": table.table_id,
                "dataset_id": table.dataset_id,
                "project": table.project,
            }
            for table in tables
        ]
        if stdout_print:
            print(json.dumps(tables_list, indent=4))
        return tables_list

    def get_select_query_results(
        self,
        select_query: str,
        limit: int = None,
        pretty_print: bool = False,
    ) -> dict:
        """
        get results from executing a select query on a BigQuery table
        optionally also pretty prints the result
        :param select_query: str|query to be executed on the table
        :param limit: int|number of records to fetch, if a value>100 is passed, limit=100 is used, default=10
        :param pretty_print: bool|should the result be pretty-printed, default=False
        :return: dict|query results
        """
        if limit is not None:
            select_query = f"{select_query} LIMIT {limit}"
            query_results = self.execute_query(sql_query=select_query)
            query_results = (
                query_results.get("results").to_dataframe()
                if query_results.get("errors") is None
                else {}
            )
            if pretty_print:
                pretty_print_df(dataframe=query_results)
            return json.loads(query_results.to_json(orient="records"))

    def execute_query(self, sql_query: str, as_json: bool = False) -> dict:
        """
        execute an SQL query on a GBQ table of project
        :param sql_query: str | SQL query as plaintext
        :param as_json: bool | (optional, default=False) return type
        :return: Union[dict, RowIterator], depending on as_json param
        """
        try:
            query_job = self.bq_client.query(sql_query)
            query_results = query_job.result()
            return {
                "errors": None,
                "results": query_results.to_dataframe().to_dict(orient="records")
                if as_json
                else query_results,
            }
        except Exception as e:
            print(f"Exception occurred: {e}")
            return {"error": e}


if __name__ == "__main__":
    _query = """
            SELECT * FROM `sandbox-381608.user_data.user_profiles`
    """
    result = BigQueryClient().execute_query(sql_query=_query, as_json=True)
    print(result)
