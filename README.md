# 🚀 Crypto Market Data Pipeline

Pipeline de datos end-to-end que extrae, transforma y sirve datos del mercado
de criptomonedas usando el stack moderno de Data Engineering en AWS.

## 📊 Caso de Uso

El equipo de análisis de inversiones necesita un dashboard diario con las
métricas del mercado crypto — precios, capitalización, volumen y performance —
para las 100 criptomonedas más relevantes del mercado.

## 🏗️ Arquitectura

```
CoinGecko API (REST)
        │
        ▼
Python ETL Pipeline
(Extracción + Transformación + Carga)
        │
        ▼
AWS S3 (Data Lake)
s3://bucket/crypto/year=YYYY/month=MM/day=DD/data.parquet
        │
        ├──────────────────┐
        ▼                  ▼
AWS Glue              dbt (SQL Transforms)
Data Catalog    stg_crypto → crypto_enriquecido
                         → resumen_mercado_diario
                         → top_10_por_dia
                               │
                               ▼
                         AWS Athena
                    (SQL queries sobre S3)
```

## 🛠️ Stack Tecnológico

| Capa | Tecnología | Propósito |
|------|-----------|-----------|
| Extracción | Python + requests | Consume la CoinGecko API con paginación |
| Transformación Python | pandas + pyarrow | Limpieza y enriquecimiento de datos |
| Almacenamiento | AWS S3 + Parquet | Data Lake particionado por fecha |
| Catálogo | AWS Glue Data Catalog | Metadatos y esquema de tablas |
| Transformación SQL | dbt + DuckDB/Athena | Modelos analíticos por capas |
| Consulta | AWS Athena | SQL sobre S3 sin base de datos |

## 📁 Estructura del Proyecto

```
crypto-pipeline/
├── pipeline/
│   ├── extractor.py       # CoinGeckoExtractor: extracción con retry y rate limit
│   ├── transformer.py     # CryptoTransformer: categorías y métricas de negocio
│   ├── loader.py          # S3Loader: carga a S3 en Parquet + registro en Glue
│   └── main.py            # Orquestador del pipeline completo
├── dbt_crypto/
│   ├── models/
│   │   ├── staging/       # stg_crypto: limpieza y estandarización
│   │   └── marts/         # crypto_enriquecido, resumen_mercado_diario, top_10_por_dia
│   └── seeds/             # Datos de prueba para desarrollo local
├── .env.example           # Variables de entorno necesarias
├── requirements.txt       # Dependencias del proyecto
└── README.md
```

## 🚀 Cómo Ejecutar

### Prerrequisitos

- Python 3.8+
- AWS CLI configurado (`aws configure`)
- Cuenta AWS con permisos en S3, Glue y Athena

### Instalación

```bash
git clone https://github.com/galdiazjs/crypto-data-pipeline.git
cd crypto-data-pipeline

pip install -r requirements.txt
```

### Configuración

```bash
cp .env.example .env
# Editar .env con tus valores de AWS y bucket S3
```

### Ejecutar el pipeline

```bash
# 1. Registrar tabla en Glue (solo la primera vez)
python pipeline/setup_glue_crypto.py

# 2. Ejecutar el pipeline ETL
python pipeline/main.py
```

### Ejecutar las transformaciones dbt

```bash
cd dbt_crypto

# Verificar conexión
dbt debug

# Correr los modelos
dbt run

# Validar calidad de datos
dbt test

# Ver documentación y linaje
dbt docs generate && dbt docs serve
```

## 📐 Decisiones de Diseño

### Composición sobre Herencia
Las clases `CoinGeckoExtractor`, `CryptoTransformer` y `S3Loader` son
independientes y componibles. Esto permite cambiar la fuente (ej: Binance API)
o el destino (ej: Redshift) sin modificar los otros componentes.

### Normalización de Tipos Explícita
CoinGecko retorna `market_cap` como entero, pero Glue lo espera como `double`.
Se fuerza el casting explícito antes de escribir el Parquet para evitar
errores `HIVE_BAD_DATA` en Athena.

### Particionamiento por Fecha
Los datos se particionan como `year=/month=/day=/` para que Athena aplique
partition pruning y solo lea las particiones relevantes, reduciendo el costo
de cada query.

### Capas dbt
- **Staging**: limpieza básica como `VIEW` (siempre fresca, sin espacio físico)
- **Marts**: lógica de negocio como `TABLE` (pre-calculada, rápida para dashboards)

## 📊 Modelos dbt

| Modelo | Tipo | Descripción |
|--------|------|-------------|
| `stg_crypto` | View | Datos limpios y estandarizados por moneda por día |
| `crypto_enriquecido` | Table | Tier de mercado, banderas y métricas en escala legible |
| `resumen_mercado_diario` | Table | Una fila por día con métricas del mercado total |
| `top_10_por_dia` | Table | Top 10 ganadores y perdedores por día |

## 🔮 Próximos Pasos

- [ ] Agregar orquestación con Apache Airflow (schedule diario a las 6am)
- [ ] Implementar alertas por email cuando el pipeline falla
- [ ] Agregar dashboard en AWS QuickSight o Metabase
- [ ] Extender a las top 250 monedas del mercado

## 👤 Autor

Saul Galdamez — Data Engineer
- LinkedIn: [linkedin.com/in/galdiazjs](https://linkedin.com/in/galdiazjs)
- GitHub: [github.com/galdiazjs](https://github.com/galdiazjs)
