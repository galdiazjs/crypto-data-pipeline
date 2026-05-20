-- Capa marts: enriquecimiento con logica de negocio adicional
-- Agrega banderas, scores y clasificaciones utiles para el dashboard
{{ config(materialized='table') }}

SELECT
    -- Identificadores
    coin_id,
    simbolo,
    nombre,
    ranking,
    fecha_carga,

    -- Precios y mercado
    precio_usd,
    market_cap_usd,
    volumen_24h_usd,
    variacion_24h_pct,
    variacion_7d_pct,
    ratio_volumen_mcap,

    -- Categorias heredadas del pipeline Python
    categoria_precio,
    performance_24h,

    -- Nuevas clasificaciones de negocio
    CASE
        WHEN ranking <= 10  THEN 'tier_1'
        WHEN ranking <= 50  THEN 'tier_2'
        WHEN ranking <= 100 THEN 'tier_3'
        ELSE                     'otros'
    END                                             AS tier_mercado,

    -- Banderas booleanas utiles para filtros en dashboards
    CASE WHEN variacion_24h_pct > 0
         THEN TRUE ELSE FALSE END                   AS subio_hoy,

    CASE WHEN variacion_24h_pct > 0
          AND variacion_7d_pct  > 0
         THEN TRUE ELSE FALSE END                   AS tendencia_alcista,

    CASE WHEN ratio_volumen_mcap > 0.10
         THEN TRUE ELSE FALSE END                   AS alta_liquidez,

    -- Market cap en billones para legibilidad en dashboards
    ROUND(market_cap_usd / 1000000000.0, 2)        AS market_cap_billions,

    -- Volumen en millones para legibilidad
    ROUND(volumen_24h_usd / 1000000.0, 2)          AS volumen_24h_millions

FROM {{ ref('stg_crypto') }}