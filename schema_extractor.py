import pandas as pd

def get_schema(conn, database):
    query = """
    SELECT
        TABLE_NAME,
        COLUMN_NAME,
        DATA_TYPE
    FROM information_schema.columns
    WHERE table_schema = %s
    ORDER BY TABLE_NAME, ORDINAL_POSITION;
    """

    df = pd.read_sql(query, conn, params=[database])

    schema = {}

    for table, group in df.groupby("TABLE_NAME"):
        schema[table] = [
            {
                "column": row.COLUMN_NAME,
                "type": row.DATA_TYPE
            }
            for row in group.itertuples()
        ]
    
    text=""
    tbl=""
    for table, columns in schema.items():
        text += f"Table: {table}\n"
        tbl+=f"{table}, "

        for col in columns:
            text += f"  - {col['column']} ({col['type']})\n"

        text += "\n"
    return text,tbl
