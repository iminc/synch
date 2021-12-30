from synch.common import cluster_sql
from synch.enums import ClickHouseEngine
from synch.reader import Reader
from synch.writer.collapsing_merge_tree import ClickHouseCollapsingMergeTree


class ClickHouseVersionedCollapsingMergeTree(ClickHouseCollapsingMergeTree):
    engine = ClickHouseEngine.versioned_collapsing_merge_tree

    def get_table_create_sql(
        self,
        reader: Reader,
        schema: str,
        table: str,
        pk,
        partition_by: str = None,
        engine_settings: str = None,
        ttl: str = None,
        sign_column: str = None,
        version_column: str = None,
    ):
        super(ClickHouseVersionedCollapsingMergeTree, self).get_table_create_sql(
            reader, schema, table, pk, partition_by, engine_settings, ttl, sign_column=sign_column
        )
        select_sql = reader.get_source_select_sql(schema, table, sign_column)
        partition_by_str = ""
        engine_settings_str = ""
        ttl_str = ""
        if partition_by:
            partition_by_str = f" PARTITION BY {partition_by} "
        if engine_settings:
            engine_settings_str = f" SETTINGS {engine_settings} "
        if ttl:
            ttl_str = f" TTL {ttl} "
        return f"CREATE TABLE {schema}.{table}{cluster_sql(self.cluster_name)} ENGINE = {self.engine}({sign_column},{version_column}) {partition_by_str} ORDER BY {pk} {ttl_str} {engine_settings_str} AS {select_sql} limit 0"

    def get_full_insert_sql(self, reader: Reader, schema: str, targetTable: str, sourceTable: str, sign_column: str = None):
        return f"insert into {schema}.{targetTable} {reader.get_source_select_sql(schema, sourceTable, sign_column)}"
