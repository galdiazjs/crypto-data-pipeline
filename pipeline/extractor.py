import requests
import logging
import time
from datetime import datetime

logger = logging.getLogger(__name__)

class CoinGeckoExtractor:
    """
    Extrae datos de mercado desde la API de CoinGecko.
    Maneja paginacion, rate limiting y errores de red.
    """

    BASE_URL = "https://api.coingecko.com/api/v3"
    MAX_REINTENTOS = 3

    def __init__(self, moneda: str = "usd", por_pagina: int = 100):
        self.moneda     = moneda
        self.por_pagina = por_pagina
        self.session    = requests.Session()
        self.session.headers.update({
            "Accept": "application/json",
            "User-Agent": "crypto-pipeline-de-learning/1.0"
        })
    
    def _get_con_reintento(self, url: str, params: dict) -> dict:
        """
        Hace GET con retry exponencial.
        CoinGecko limita a 10-30 requests/minuto en el tier gratuito.
        """
        for intento in range(self.MAX_REINTENTOS):
            try:
                response = self.session.get(url, params = params, timeout=30)

                #Rate limit de CoinGecko - esperar y reintentar
                if response.status_code == 429:
                    espera = 60 * (intento + 1)
                    logger.warning(f"Rate limit alcanzado. Esperando {espera}s...")
                    time.sleep(espera)
                    continue

                response.raise_for_status()
                return response.json()
            except requests.exceptions.Timeout:
                logger.warning(f"Timeout en intento {intento + 1}/{self.MAX_REINTENTOS}")
                if intento == self.MAX_REINTENTOS - 1:
                    raise
                time.sleep(2 ** intento) #backoff exponencial
            
            except requests.exceptions.HTTPError as e:
                logger.error(f"HTTP Error: {e.response.status_code}")
                raise
        
        raise Exception(f"Fallo despues de {self.MAX_REINTENTOS} intentos.")
    
    def extraer_mercado(self, paginas: int = 3) -> list:
        """
        Extrae datos de mercado paginados.
        Por defecto extrae las top 100 (1 por pagina de 100)
        """
        todos = []

        for pagina in range (1, paginas + 1):
            logger.info(f"Extrayendo pagina {pagina}/{paginas}")

            params = {
                "vs_currency": self.moneda,
                "order": "market_cap_desc",
                "per_page": self.por_pagina,
                "page": pagina,
                "sparkline": "false",
                "locale": "en"                
            }

            datos = self._get_con_reintento(
                f"{self.BASE_URL}/coins/markets",
                params
            )

            if not datos:
                logger.info(f"Pagina {pagina} vacia - fin de datos")
                break

            todos.extend(datos)
            logger.info(f"Pagina {pagina}: {len(datos)} monedas | Total: {len(todos)}")

            #Pause entre paginas para respetar rate limits
            if pagina < paginas:
                time.sleep(2)
        logger.info(f"Extraccion completa: {len(todos)}")
        return todos