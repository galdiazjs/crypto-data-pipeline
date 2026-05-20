-- Capa staging: limpieza y estandarizacion de los datos crudos
-- Responsabilidad: un registro por moneda por dia, nombres claros, tipos correctos
-- Materialization: view — es solo limpieza, no ocupa espacio fisico

SELECT
    coin_id                                         AS coin_id,
    simbolo                                         AS simbolo,
    nombre                                          AS nombre,
    CAST(ranking_market_cap AS INTEGER)             AS ranking,
    CAST(precio_usd AS DOUBLE)                      AS precio_usd,
    CAST(market_cap_usd AS DOUBLE)                  AS market_cap_usd,
    CAST(volumen_24h_usd AS DOUBLE)                 AS volumen_24h_usd,
    CAST(variacion_24h_pct AS DOUBLE)               AS variacion_24h_pct,
    CAST(variacion_7d_pct AS DOUBLE)                AS variacion_7d_pct,
    LOWER(categoria_precio)                         AS categoria_precio,
    LOWER(performance_24h)                          AS performance_24h,
    CAST(ratio_volumen_mcap AS DOUBLE)              AS ratio_volumen_mcap,
    CAST(fecha_carga AS DATE)                       AS fecha_carga,
    timestamp_actualizacion

FROM {{ source('raw', 'crypto_raw') }}

WHERE coin_id IS NOT NULL
  AND precio_usd IS NOT NULL
  AND precio_usd > 0