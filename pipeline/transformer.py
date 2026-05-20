import logging
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

class CryptoTransformer:
    """
    Transforma los datos crudos de CoinGecko en regisrtos limpios.
    """

    CATEGORIAS_PRECIO = [
        (50_000, float('inf'), "mega_cap"),
        (10_000,    50_000,     "large_cap"),
        (1_000,     10_000,     "mid_cap"),
        (100,       1_000,      "small_cap"),
        (0,         100,        "micro_cap")
    ]

    def _categorizar_precio(self, precio: float) -> str:
        """Asigna una categoria segun el precio actual."""
        if precio is None:
            return "Unknown"
        for minimo, maximo, categoria in self.CATEGORIAS_PRECIO:
            if minimo <= precio < maximo:
                return categoria
        return "Unknown"
    
    def _categorizar_variacion(self, variacion_24h: float) -> str:
        """Clasifica la performance de las ultinmas 24 horas"""
        if variacion_24h is None:
            return "Unknown"
        if variacion_24h >= 10:
            return "muy_positivo"
        if variacion_24h >= 3:
            return "positivo"
        if variacion_24h >= -3:
            return "neutro"
        if variacion_24h >= -10:
            return "negativo"
        else:
            return "muy_negativo"
    
    def transformar(self, monedas: list) -> list:
        """Transforma la lista de monedas crudas en registros limpoios.
        """
        logger.info(f"Transformando {len(monedas)} monedas")
        transformados = []
        omitidos = 0
        fecha_carga = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        
        for moneda in monedas:
            try:
                precio      = moneda.get("current_price")
                variacion   = moneda.get("price_change_percentage_24h")
                market_cap  = moneda.get("market_cap")
                volumen     = moneda.get("total_volume")

                registro = {
                    # Identificadores
                    "coin_id":               moneda["id"],
                    "simbolo":               moneda["symbol"].upper(),
                    "nombre":                moneda["name"],
                    "ranking_market_cap":    moneda.get("market_cap_rank"),

                    # Precios y mercado
                    "precio_usd":            precio,
                    "market_cap_usd":        market_cap,
                    "volumen_24h_usd":       volumen,

                    # Variaciones
                    "variacion_24h_pct":     variacion,
                    "variacion_7d_pct":      moneda.get("price_change_percentage_7d_in_currency"),

                    # Campos calculados
                    "categoria_precio":      self._categorizar_precio(precio),
                    "performance_24h":       self._categorizar_variacion(variacion),
                    "ratio_volumen_mcap":    round(volumen / market_cap, 4)
                                             if market_cap and volumen else None,

                    # Metadatos
                    "fecha_carga":           fecha_carga,
                    "timestamp_actualizacion": moneda.get("last_updated", "")
                }

                transformados.append(registro)
            
            except KeyError as e:
                omitidos += 1
                logger.warning(f"Campo faltante en {moneda.get('id','unknown')}: {e}")
                continue
        
        logger.info(f"Transformacion completa: {len(transformados)} OK | {omitidos} omitidos")
        return transformados