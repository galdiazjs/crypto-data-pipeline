import logging
import sys
from datetime import datetime, timezone
from extractor import CoinGeckoExtractor
from transformer import CryptoTransformer
from loader import S3Loader

logging.basicConfig(
    level = logging.INFO,
    format = "%(asctime)s - %(name)s - %(message)s",
    handlers = [
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(f"pipeline_{datetime.now().strftime('%Y%m%d')}.log")
    ]
)
logger = logging.getLogger("main")

#-- Configuracion
BUCKET      = "de-learning-sgaldamez-2026"
GLUE_DB     = "de_learning"
GLUE_TABLE  = "crypto_raw"
PAGINAS     = 1 #1 pagina = top 100 monedas

def main():
    inicio = datetime.now()
    logger.info("=" * 60)
    logger.info("CRYPTO MARKET DATA PIPELINE - INICIO")
    logger.info("=" * 60)
    
    try:
        #-- EXTRACT
        logger.info("[EXTRACT] Iniciando extraccion desde CoinGecko API")
        extractor   = CoinGeckoExtractor(moneda = "usd", por_pagina=100)
        datos_crudos = extractor.extraer_mercado(paginas=PAGINAS)
        logger.info(f"[EXTRACT] {len(datos_crudos)} monedas extraidas")

        #-- TRANSFORM
        logger.info(f"[TRANSFORM] Iniciando transformacion")
        transformer = CryptoTransformer()
        datos_limpios = transformer.transformar(datos_crudos)
        logger.info(f"[TRANSFORM] {len(datos_limpios)} registros transformados")

        #-- LOAD
        logger.info("[LOAD] Cargando a S3")
        loader = S3Loader(bucket=BUCKET, prefijo="crypto")
        s3_path = loader.cargar(datos_limpios)
        logger.info(f"[LOAD] Datos en; {s3_path}")

        #-- CATALOG
        logger.info(f"[CATALOG] Registrando particion en GLUE")
        loader.registrar_partitcion_glue(
            fecha= datetime.now(),
            database= GLUE_DB,
            tabla= GLUE_TABLE
        )

        #-- REPORTE FINAL
        duracion = (datetime.now() - inicio).seconds
        logger.info("=" * 60)
        logger.info("PIPELINE COMPLETADO")
        logger.info(f"  Monedas procesadas: {len(datos_limpios)}")
        logger.info(f"  Destino:            {s3_path}")
        logger.info(f"  Duracion:           {duracion} segundos")
        logger.info("=" * 60)
    except Exception as e:
        duracion = (datetime.now() - inicio).seconds
        logger.critical(f"PIPELINE FALLIDO despues de {duracion}s: {e}")
        raise

if __name__ == "__main__":
    main()