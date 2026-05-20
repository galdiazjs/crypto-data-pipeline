import boto3
import pyarrow as pa
import pyarrow.parquet as pq
import pandas as pd
import logging
import io
import os
from datetime import datetime, timezone
from botocore.exceptions import ClientError, NoCredentialsError

logger = logging.getLogger(__name__)

class S3Loader:
    """
    Cargar datos transformados a S3 en formato Parquet con particionamiento.
    """
    def __init__(self, bucket: str, prefijo: str = "crypto"):
        self.bucket     = bucket
        self.prefijo    = prefijo
        self.s3         = boto3.client("s3")
    
    def _construir_key(self, fecha: datetime) -> str:
        return (
            f"{self.prefijo}/"
            f"year={fecha.strftime('%Y')}/"
            f"month={fecha.strftime('%m')}/"
            f"day={fecha.strftime('%d')}/"
            f"data.parquet"
        )
    
    def _normalizar_tipos(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Fuerza los tipos correctos antes de escribir el Parquet.
        Evita conflictos de esquema entre pandas y Glue.
        """
        columnas_float = [
            "precio_usd",
            "market_cap_usd",
            "volumen_24h_usd",
            "variacion_24h_pct",
            "variacion_7d_pct",
            "ratio_volumen_mcap"
        ]
        columnas_int = [
            "ranking_market_cap"
        ]
        columnas_str = [
            "coin_id", "simbolo", "nombre",
            "categoria_precio", "performance_24h",
            "fecha_carga", "timestamp_actualizacion"
        ]

        for col in columnas_float:
            if col in df.columns:
                df[col] = df[col].astype("float64")

        for col in columnas_int:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce").astype("Int64")

        for col in columnas_str:
            if col in df.columns:
                df[col] = df[col].astype("str")

        return df
    
    def cargar(self, datos: list) -> str:
        """
        Convierte a Parquet en memoria y sube a S3
        """
        if not datos:
            raise ValueError("No hay datos para cargar")
        
        fecha   = datetime.now()
        s3_key  = self._construir_key(fecha)

        logger.info(f"Preparando {len(datos)} registros en Parquet")

        try:
            df      = pd.DataFrame(datos)
            df      = self._normalizar_tipos(df)
            tabla   = pa.Table.from_pandas(df, preserve_index=False)
            buffer  = io.BytesIO()
            pq.write_table(tabla, buffer, compression="snappy")
            buffer.seek(0)

            logger.info(f"Subiendo a s3://{self.bucket}/{s3_key}")
            self.s3.put_object(
                Bucket      = self.bucket,
                Key         = s3_key,
                Body        = buffer.getvalue(),
                ContentType = "application/octet-stream"
            )

            tamano= len(buffer.getvalue())
            logger.info(f"Carga exitosa: {tamano:,} bytes en s3://{self.bucket}/{s3_key}")
            return f"s3://{self.bucket}/{s3_key}"
        except NoCredentialsError:
            logger.error("Credenciales AWS no encontradas. Ejecuta 'aws configure'")
            raise
        except ClientError as e:
            logger.error(f"Error AWS: {e.response['Error']['Message']}")
            raise
    
    def registrar_partitcion_glue(self, fecha: datetime, database: str, tabla: str) -> None:
        """
        Registra la particion del dia en el Glue Data Catalog
        """
        glue = boto3.client("glue", region_name="us-east-1")
        s3_location = (
            f"s3://{self.bucket}/{self.prefijo}/"
            f"year={fecha.strftime('%Y')}/"
            f"month={fecha.strftime('%m')}/"
            f"day={fecha.strftime('%d')}/"
        )

        try:
            glue.create_partition(
                DatabaseName    = database,
                TableName       = tabla,
                PartitionInput  = {
                    "Values": [
                        fecha.strftime("%Y"),
                        fecha.strftime("%m"),
                        fecha.strftime("%d")
                    ],
                    "StorageDescriptor": {
                        "Location": s3_location,
                        "InputFormat": "org.apache.hadoop.mapred.TextInputFormat",
                        "OutputFormat": "org.apache.hadoop.hive.ql.io.HiveIgnoreKeyTextOutputFormat",
                        "SerdeInfo": {
                            "SerializationLibrary": "org.apache.hadoop.hive.ql.io.parquet.serde.ParquetHiveSerDe"
                        }
                    }
                }
            )
            logger.info(f"Particion registrada en Glue: {s3_location}")
        except ClientError as e:
            if e.response["Error"]["Code"] == "AlreadyExistsException":
                logger.info("Particion ya existe en Glue - OK")
            else:
                raise