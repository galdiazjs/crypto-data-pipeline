-- Vista del mercado total por dia — una fila por fecha
-- Util para graficar tendencias del mercado en su conjunto
{{ config(materialized='table') }}

SELECT
    fecha_carga                                         AS fecha,

    -- Metricas del mercado total
    COUNT(*)                                            AS total_monedas,
    ROUND(SUM(market_cap_usd) / 1000000000000.0, 2)   AS market_cap_total_trillions,
    ROUND(SUM(volumen_24h_usd) / 1000000000.0, 2)      AS volumen_total_billions,

    -- Distribucion de performance
    SUM(CASE WHEN performance_24h IN ('positivo', 'muy_positivo')
             THEN 1 ELSE 0 END)                        AS monedas_en_verde,
    SUM(CASE WHEN performance_24h IN ('negativo', 'muy_negativo')
             THEN 1 ELSE 0 END)                        AS monedas_en_rojo,
    SUM(CASE WHEN performance_24h = 'neutro'
             THEN 1 ELSE 0 END)                        AS monedas_neutras,

    -- Variacion promedio ponderada por market cap
    ROUND(
        SUM(variacion_24h_pct * market_cap_usd) / NULLIF(SUM(market_cap_usd), 0)
    , 4)                                               AS variacion_ponderada_24h,

    -- Extremos del dia
    MAX(variacion_24h_pct)                             AS mayor_subida_pct,
    MIN(variacion_24h_pct)                             AS mayor_caida_pct,
    MAX(precio_usd)                                    AS precio_maximo_mercado,

    -- Dominancia de Bitcoin (si existe en el snapshot)
    ROUND(
        MAX(CASE WHEN coin_id = 'bitcoin' THEN market_cap_usd ELSE 0 END)
        / NULLIF(SUM(market_cap_usd), 0) * 100
    , 2)                                               AS dominancia_btc_pct

FROM {{ ref('stg_crypto') }}
GROUP BY fecha_carga
ORDER BY fecha_carga DESC