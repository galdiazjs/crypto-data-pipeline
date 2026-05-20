import boto3
from botocore.exceptions import ClientError

BUCKET  = "de-learning-sgaldamez-2026"
DB      = "de_learning"

glue = boto3.client("glue", region_name="us-east-1")

# Crear tabla crypto_raw en Glue
try:
    glue.create_table(
        DatabaseName = DB,
        TableInput   = {
            "Name": "crypto_raw",
            "StorageDescriptor": {
                "Columns": [
                    {"Name": "coin_id",                  "Type": "string"},
                    {"Name": "simbolo",                  "Type": "string"},
                    {"Name": "nombre",                   "Type": "string"},
                    {"Name": "ranking_market_cap",       "Type": "int"},
                    {"Name": "precio_usd",               "Type": "double"},
                    {"Name": "market_cap_usd",           "Type": "double"},
                    {"Name": "volumen_24h_usd",          "Type": "double"},
                    {"Name": "variacion_24h_pct",        "Type": "double"},
                    {"Name": "variacion_7d_pct",         "Type": "double"},
                    {"Name": "categoria_precio",         "Type": "string"},
                    {"Name": "performance_24h",          "Type": "string"},
                    {"Name": "ratio_volumen_mcap",       "Type": "double"},
                    {"Name": "fecha_carga",              "Type": "string"},
                    {"Name": "timestamp_actualizacion",  "Type": "string"},
                ],
                "Location":     f"s3://{BUCKET}/crypto/",
                "InputFormat":  "org.apache.hadoop.mapred.TextInputFormat",
                "OutputFormat": "org.apache.hadoop.hive.ql.io.HiveIgnoreKeyTextOutputFormat",
                "SerdeInfo": {
                    "SerializationLibrary": "org.apache.hadoop.hive.ql.io.parquet.serde.ParquetHiveSerDe"
                }
            },
            "PartitionKeys": [
                {"Name": "year",  "Type": "string"},
                {"Name": "month", "Type": "string"},
                {"Name": "day",   "Type": "string"},
            ],
            "TableType": "EXTERNAL_TABLE"
        }
    )
    print("Tabla crypto_raw creada en Glue")
except ClientError as e:
    if e.response["Error"]["Code"] == "AlreadyExistsException":
        print("Tabla ya existe — OK")
    else:
        raise