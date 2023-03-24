"""
class to upload data to BigQuery
"""
from __future__ import annotations
from app.gcp.big_query.big_query_table import BigQueryTable
import pandas as pd
from app.utils.data_type_utils import (
    fix_special_characters_in_json_keys,
)


class BigQueryUploader(BigQueryTable):
    def __init__(
        self,
        project_id: str,
        dataset_name: str,
        table_name: str,
        data_to_upload: dict | list[dict] | pd.DataFrame,
        schema_id: str = None,
    ):
        super().__init__(
            project_id=project_id,
            dataset_name=dataset_name,
            table_name=table_name,
            schema_id=schema_id,
        )
        if not self.exists:
            self.create()
        self.data_to_upload = fix_special_characters_in_json_keys(
            data_to_update=data_to_upload
        )

    def do_upload(self) -> dict:
        """

        :return:
        """
        upload_results = {"table_id": self.table_id}
        try:
            if isinstance(self.data_to_upload, dict):
                _df_to_upload = pd.DataFrame(self.data_to_upload, index=[0])
            elif isinstance(self.data_to_upload, list):
                _df_to_upload = pd.DataFrame(self.data_to_upload)
            elif isinstance(self.data_to_upload, pd.DataFrame):
                _df_to_upload = self.data_to_upload
            else:
                upload_results["errors"] = Exception("No suitable data found for uploading.")
                return upload_results
            upload_results["jobs"] = self.update_from_dataframe(data_df=_df_to_upload).dict()
        except Exception as e:
            upload_results["errors"] = e
        return upload_results
