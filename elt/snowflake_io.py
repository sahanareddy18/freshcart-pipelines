from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def write_landing(records: list[dict[str, Any]], directory: str | Path = "landing") -> Path:
    landing_dir = Path(directory)
    landing_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    path = landing_dir / f"orders_{stamp}.jsonl"
    with path.open("w", encoding="utf-8") as file:
        for record in records:
            file.write(json.dumps(record, separators=(",", ":")) + "\n")
    return path


def connect_from_env():
    import snowflake.connector

    required = {
        "account": "SNOWFLAKE_ACCOUNT",
        "user": "SNOWFLAKE_USER",
        "password": "SNOWFLAKE_PASSWORD",
        "warehouse": "SNOWFLAKE_WAREHOUSE",
        "database": "SNOWFLAKE_DATABASE",
        "schema": "SNOWFLAKE_SCHEMA",
    }
    missing = [env_name for env_name in required.values() if not os.getenv(env_name)]
    if missing:
        raise RuntimeError(f"Missing Snowflake environment variables: {', '.join(missing)}")
    return snowflake.connector.connect(
        **{argument: os.environ[env_name] for argument, env_name in required.items()}
    )


def load_file(connection, path: str | Path, table: str = "BRONZE.ORDERS_RAW") -> None:
    source = Path(path).resolve()
    if not source.is_file():
        raise FileNotFoundError(source)
    stage = "FRESHCART_LANDING_STAGE"
    file_uri = source.as_uri().replace("'", "''")
    with connection.cursor() as cursor:
        cursor.execute(f"CREATE STAGE IF NOT EXISTS {stage}")
        cursor.execute(
            f"PUT '{file_uri}' @{stage} AUTO_COMPRESS=FALSE OVERWRITE=TRUE"
        )
        cursor.execute(
            f"""COPY INTO {table} (raw_payload, source_file, record_hash)
FROM (
  SELECT $1, METADATA$FILENAME, SHA2(TO_JSON($1), 256)
  FROM @{stage}/{source.name}
)
FILE_FORMAT = (TYPE = JSON STRIP_OUTER_ARRAY = FALSE)
FORCE = TRUE"""
        )


def execute_transform_sql(connection, sql_path: str | Path) -> None:
    sql = Path(sql_path).read_text(encoding="utf-8")
    connection.execute_string(sql)