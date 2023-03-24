"""
class to abstract interactions with BigQuery Tables
"""
from google.cloud import bigquery
from google.cloud.exceptions import NotFound
from app.gcp.big_query.big_query_client import BigQueryClient
from app.utils.data_string_utils import pretty_print_df
from app.utils.gbq_utils import get_gbq_schema_from_json
from app.models.models import GbqUploadResults
from dotenv import load_dotenv
from typing import Union
import pandas as pd
import json


class BigQueryTable(BigQueryClient):
    def __init__(
            self,
            project_id: str,
            dataset_name: str,
            table_name: str,
            p_key: str = None,
            schema_id: str = None,
    ):
        super().__init__(project_id=project_id)
        load_dotenv()
        self.dataset_name = dataset_name
        self.table_name = table_name
        self.table_id = f"{self.project_id}.{self.dataset_name}.{self.table_name}"
        self.p_key = p_key
        self.exists = self.check_exists()
        self.highest_pkey_value = self.get_highest_pkey_value() if self.exists else None
        self.schema = (
                get_gbq_schema_from_json(
                    table_name_key=self.table_name, schema_name_key=schema_id
                )
                or None
        )

    def create(self) -> None:
        """
        create table using schema provided
        :return:
        """
        if not self.schema:
            print(
                "Creating table with empty schema, as no schema mapping was found. Not recommended!"
            )
        table = bigquery.Table(
            self.table_id,
            schema=self.schema,
        )
        table = self.bq_client.create_table(table)
        self.exists = True
        print(f"Created table {table.project}.{table.dataset_id}.{table.table_id}")

    def check_exists(self) -> bool:
        try:
            self.bq_client.get_table(self.table_id)  # Make an API request.
            return True
        except NotFound:
            print(f"Table {self.table_id} is not found.")
            return False

    def delete(self):
        if self.check_exists():
            print(f"Deleting table and contents of {self.table_id}")
            try:
                self.bq_client.delete_table(self.table_id, not_found_ok=True)
                self.highest_pkey_value = None
                self.exists = False
            except Exception as e:
                print(
                    f"Error caught while deleting table: {e}. Proceeding without deletion."
                )
        else:
            print(f"{self.table_id} doesn't exist yet. Skipping deletion...")

    def get_num_rows(self):
        # FIXME this doesnt work well, keeps returning 0 frequently
        num_rows = None
        try:
            num_rows = self.bq_client.get_table(self.table_id).num_rows
        except Exception as e:
            print(f"Exception occurred: {e}")
        return num_rows

    def get_highest_pkey_value(self):
        """

        :return:
        """
        if self.p_key:
            p_key_dtype = self.get_col_name_types_mapping().get(self.p_key)
            if p_key_dtype and p_key_dtype == "STRING":
                select_query = f"""SELECT lower({self.p_key}) as {self.p_key} 
                FROM `{self.table_id}` 
                ORDER BY lower({self.p_key}) DESC 
                LIMIT 1"""
            else:
                select_query = f"""SELECT {self.p_key} 
                    FROM `{self.table_id}` 
                    ORDER BY {self.p_key} DESC 
                    LIMIT 1"""
            print(select_query)
            query_results = self.get_select_query_results(
                select_query=select_query, pretty_print=True
            )
            if query_results and isinstance(query_results, list):
                return query_results[0].get(self.p_key, None)
        return None

    def get_col_name_types_mapping(self) -> dict:
        """
        return a mapping dict with col-name and col-datatype for the GBQ table
        :return: dict | mapping {col_name: col-type}
        """
        return {
            _col.name: _col.field_type
            for _col in self.bq_client.get_table(self.table_id).schema
        }

    def get_table_properties(
            self,
            dataset_name: str = None,
            table_name: str = None,
            print_stdout: bool = False,
    ):
        """

        :param dataset_name:
        :param table_name:
        :param print_stdout:
        :return:
        """
        dataset_name = dataset_name or self.dataset_name
        table_name = table_name or self.table_name
        table_id = f"{self.project_id}.{dataset_name}.{table_name}"

        table = self.bq_client.get_table(table_id)
        if print_stdout:
            # View table properties
            print(
                f"""Got table '{table.project}.{table.dataset_id}.{table.table_id}'.
                    Table schema: {table.schema}
                    Table description: {table.description}
                    Table has {self.get_num_rows()} rows        
                """
            )
        return {
            "schema": table.schema,
            "description": table.description,
            "num_rows": self.get_num_rows(),
        }

    def get_records_in_table(
            self,
            dataset_name: str = None,
            table_name: str = None,
            limit: int = None,
            pretty_print: bool = False,
    ) -> dict:
        """
        get top records from a schema table
        optionally also pretty prints the result
        :param dataset_name: str|dataset-id
        :param table_name: str|table-id
        :param limit: int|number of records to fetch, if a value>100 is passed, limit=100 is used, default=10
        :param pretty_print: bool|should the result be pretty-printed, default=False
        :return: dict|query results
        """
        dataset_name = dataset_name or self.dataset_name
        table_name = table_name or self.table_name
        select_query = f"""
           SELECT *
            FROM `{dataset_name}.{table_name}`
            LIMIT {min(limit, 100)};
        """
        try:
            query_results = self.bq_client.query(select_query).to_dataframe()
            if pretty_print:
                pretty_print_df(dataframe=query_results)
            return json.loads(query_results.to_json(orient="records"))
        except Exception as e:
            print(f"Exception occurred: {e}")

    def update_from_json_data(self, data_json: Union[dict, list]) -> GbqUploadResults:
        """

        :param data_json:
        :return:
        """
        job_config = self.get_load_job_config(source="json")
        if isinstance(data_json, dict):
            df = pd.DataFrame([data_json])
        else:
            df = pd.DataFrame(data_json)
            print(f"created a Dataframe of {df.shape[0]} records for uploading..")
        try:
            json_object = json.loads(df.to_json(orient="records"))

            job = self.bq_client.load_table_from_json(
                json_object, self.table_id, job_config=job_config
            )
            if not job.errors:
                return self.get_job_success_dict(gbq_job=job, num_rows=df.shape[0])
            else:
                print(f"Errors occurred! {iter(job.errors)}")
        except Exception as ex:
            raise f"Exception caught while updating BigQuery: {ex}" from ex

    def update_from_dataframe(self, data_df: pd.DataFrame) -> GbqUploadResults:
        """

        :param data_df:
        :return:
        """
        print(
            f"INFO: Uploading a Dataframe of {data_df.shape[0]} records to {self.table_id}"
        )

        try:
            job = self.bq_client.load_table_from_dataframe(
                data_df,
                self.table_id,
                job_config=self.get_load_job_config(source="df"),
            )
            if not job.errors:
                return self.get_job_success_dict(gbq_job=job, num_rows=data_df.shape[0])
            else:
                print(f"Errors occurred! {job.errors}")
        except Exception as ex:
            raise f"Exception caught while updating BigQuery: {ex}" from ex

    def get_job_success_dict(
            self, gbq_job: bigquery.job, num_rows: int
    ) -> GbqUploadResults:
        return GbqUploadResults(
            **{
                "table_id": self.table_id,
                "job_id": gbq_job.result().job_id,
                "errors": None,
                "num_rows": num_rows,
            }
        )

    def get_load_job_config(self, source: str = None) -> bigquery.LoadJobConfig:
        """
        get GBQ load-job config for different types of sources
        :param source: str | json/csv/df
        :return:
        """
        if source == "json":
            source_format = bigquery.SourceFormat.NEWLINE_DELIMITED_JSON
        elif source in {"df", "csv"}:
            source_format = bigquery.SourceFormat.CSV
        else:
            source_format = None
        if self.schema:
            return bigquery.LoadJobConfig(
                autodetect=False,
                schema=self.schema,
                source_format=source_format,
                allow_quoted_newlines=True,
                allow_jagged_rows=True,
            )
        return bigquery.LoadJobConfig(
            autodetect=True,
            allow_quoted_newlines=True,
            allow_jagged_rows=True,
        )


if __name__ == "__main__":
    big_query_table = BigQueryTable(
        project_id="sandbox-381608",
        dataset_name="user_data",
        table_name="user_profiles",
    )
    big_query_table.create()
