"""Optional MySQL adapter: one JSON report per row, streamed to stdout."""
import argparse
import getpass
import json
import os
from analyzer.core import analyze


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--host", default="localhost")
    p.add_argument("--user", required=True)
    p.add_argument("--database", required=True)
    p.add_argument("--query", required=True, help="SELECT query; first column must contain text")
    a = p.parse_args()
    if not a.query.lstrip().upper().startswith("SELECT "):
        p.error("Use a SELECT query with a read-only database account.")
    try:
        import mysql.connector
    except ImportError:
        p.error("Install optional adapter: pip install mysql-connector-python")
    connection = mysql.connector.connect(host=a.host, user=a.user, database=a.database,
        password=os.environ.get("STRING_ANALYZER_MYSQL_PASSWORD") or getpass.getpass("MySQL password: "))
    try:
        cursor = connection.cursor()
        try:
            cursor.execute(a.query)
            for index, row in enumerate(cursor, 1):
                if row[0] is not None and not isinstance(row[0], str):
                    raise ValueError(f"Row {index}: first column must be text or NULL")
                print(json.dumps({"row": index, "analysis": analyze(row[0] or "")}, ensure_ascii=False))
        finally:
            cursor.close()
    finally:
        connection.close()


if __name__ == "__main__":
    main()
