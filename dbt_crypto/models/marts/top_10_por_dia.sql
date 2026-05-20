-- Top 10 monedas con mejor y peor performance por dia
-- Util para el widget "Ganadores y Perdedores" del dashboard
{{ config(materialized='table') }}

WITH ranked_monedas AS (
    SELECT
        fecha_carga,
        coin_id,
        simbolo,
        nombre,
        precio_usd,
        variacion_24h_pct,
        variacion_7d_pct,
        market_cap_usd,
        performance_24h,
        tier_mercado,

        -- Rank de mejor performance del dia
        ROW_NUMBER() OVER (
            PARTITION BY fecha_carga
            ORDER BY variacion_24h_pct DESC
        )                                   AS rank_ganadores,

        -- Rank de peor performance del dia
        ROW_NUMBER() OVER (
            PARTITION BY fecha_carga
            ORDER BY variacion_24h_pct ASC
        )                                   AS rank_perdedores

    FROM {{ ref('crypto_enriquecido') }}
)

SELECT
    fecha_carga,
    coin_id,
    simbolo,
    nombre,
    precio_usd,
    variacion_24h_pct,
    variacion_7d_pct,
    market_cap_usd,
    performance_24h,
    tier_mercado,
    rank_ganadores,
    rank_perdedores,

    CASE
        WHEN rank_ganadores <= 10 THEN 'top_ganador'
        WHEN rank_perdedores <= 10 THEN 'top_perdedor'
    END                                     AS categoria_ranking

FROM ranked_monedas
WHERE rank_ganadores <= 10
   OR rank_perdedores <= 10

ORDER BY fecha_carga DESC, variacion_24h_pct DESC