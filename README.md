# 🚀 SVGA System v4.0 - Sistema Integrado de Análisis Técnico Profesional

**Sistema de Vigilancia y Generación de Alertas Algorítmicas**

**Versión:** 4.0 con Radares Tácticos + Alertas Avanzadas  
**Autor:** AIDA (Artificial Intelligence Data Architect)  
**Fecha:** Octubre 2025  
**Licencia:** MIT

---

## 📋 Tabla de Contenidos

1. [Descripción General](#-descripción-general)
2. [Características Principales](#-características-principales)
3. [Arquitectura del Sistema](#-arquitectura-del-sistema)
4. [Instalación](#-instalación)
5. [Guía de Uso](#-guía-de-uso)
6. [Componentes del Sistema](#-componentes-del-sistema)
7. [Interpretación de Resultados](#-interpretación-de-resultados)
8. [Archivos Generados](#-archivos-generados)
9. [Mejoras y Versiones](#-mejoras-y-versiones)
10. [Limitaciones y Advertencias](#-limitaciones-y-advertencias)
11. [FAQ](#-faq)
12. [Referencias](#-referencias)

---

## 🎯 Descripción General

El **SVGA System v4.0** es un sistema profesional de análisis técnico avanzado que combina:

- ✅ **Radares Tácticos** con detección de régimen de mercado (alcista/bajista/lateral)
- ✅ **Análisis Profundo** con 20+ indicadores técnicos basados en John J. Murphy
- ✅ **Alertas Avanzadas** con detección de anomalías y patrones probabilísticos
- ✅ **Visualizaciones Interactivas** multi-panel con Plotly
- ✅ **Exportación Completa** (JSON + Markdown + HTML + PNG + CSV)

### ¿Para quién es este sistema?

- 📊 **Traders cuantitativos** que necesitan análisis técnico automatizado
- 💹 **Analistas financieros** que buscan herramientas de screening eficientes
- 🔬 **Científicos de datos** interesados en finanzas algorítmicas
- 📈 **Inversores** que quieren análisis técnico profesional de sus portfolios

---

## ⚡ Características Principales

### 1. Sistema de Radares Tácticos de 3 Fases

```
FASE 1: Determinar Régimen de Mercado
   ↓
FASE 2: Ejecutar Radares Apropiados
   ↓
FASE 3: Análisis Profundo SVGA
```

**5 Radares Tácticos:**
- 🟢 **Radar 1:** Reversión a la Media (comprar la caída en tendencia alcista)
- 🟢 **Radar 2:** Ignición de Momentum (comprar la ruptura)
- 🔴 **Radar 3:** Reversión Bajista (vender en rebote)
- 🔴 **Radar 4:** Ruptura Bajista (vender la caída)
- 🟡 **Radar 5:** Mercado Lateral (operar el rango)

### 2. Análisis Técnico Exhaustivo

**Indicadores Implementados (20+):**

#### Tendencia
- EMAs (12, 26, 50, 200)
- SMAs (20, 50, 200)
- Bandas de Bollinger
- Canales de Donchian
- Keltner Channels
- Líneas de tendencia automáticas
- Niveles de Fibonacci (23.6%, 38.2%, 50%, 61.8%, 78.6%)

#### Momentum
- RSI (14)
- MACD (12, 26, 9) + Histograma
- Estocástico (%K, %D)
- ROC (Rate of Change)
- CCI (Commodity Channel Index)

#### Volumen
- OBV (On Balance Volume)
- CMF (Chaikin Money Flow)
- VWAP (Volume Weighted Average Price)

#### Fuerza de Tendencia
- ADX (Average Directional Index)
- Aroon (Up/Down)

#### Volatilidad
- ATR (Average True Range)
- Bandas de Bollinger
- Keltner Channels

### 3. Alertas Avanzadas

El sistema detecta automáticamente:

- ⚠️ **Anomalías:** Volatilidad extrema, volumen inusual, cambios abruptos
- 💡 **Oportunidades:** Patrones alcistas/bajistas con probabilidad calculada
- 🔔 **Divergencias:** RSI/MACD vs precio
- 📊 **Correlaciones rotas:** Entre activos correlacionados
- 🎯 **Patrones:** Con scoring de probabilidad 0-100%

### 4. Escalabilidad Extrema

| Métrica | Sistema v4.0 |
|---------|-------------|
| **Activos analizables** | 500+ simultáneamente |
| **Tiempo de ejecución** | ~30 seg para S&P 500 completo |
| **Llamadas API** | 1 llamada batch total |
| **Riesgo rate limiting** | Mínimo |

---

## 🏗️ Arquitectura del Sistema

### Flujo de Trabajo Completo

```
┌──────────────────────────────────────────────────────────┐
│  FASE 1: DETERMINACIÓN DE RÉGIMEN DE MERCADO            │
│  📊 Analiza benchmark (^GSPC, BTC-USD)                   │
│      └─ Calcula: EMA 50/100, MACD, ADX, RSI            │
│      └─ Determina: ALCISTA / BAJISTA / LATERAL         │
│      └─ Confianza: 0-100%                               │
└──────────────────────────────────────────────────────────┘
                            ↓
┌──────────────────────────────────────────────────────────┐
│  FASE 2: RADARES TÁCTICOS                               │
│  📡 Escaneo masivo según régimen                         │
│                                                          │
│  SI ALCISTA → Ejecuta Radares 1 y 2                     │
│  SI BAJISTA → Ejecuta Radares 3 y 4                     │
│  SI LATERAL → Ejecuta Radar 5                           │
│                                                          │
│      └─ Descarga: 500+ tickers (1 llamada batch)       │
│      └─ Calcula: Métricas tácticas vectorizadas        │
│      └─ Filtra: 5-15 candidatos top                    │
│      └─ Exporta: radar_sp500.csv, radar_crypto.csv     │
└──────────────────────────────────────────────────────────┘
                            ↓
┌──────────────────────────────────────────────────────────┐
│  FASE 3: ANÁLISIS PROFUNDO SVGA                         │
│  🔬 Portfolio + Candidatos del Radar                     │
│      └─ 20+ Indicadores técnicos (pandas-ta)           │
│      └─ Detección de señales (Murphy)                  │
│      └─ Alertas avanzadas (anomalías/oportunidades)    │
│      └─ Gráficos interactivos (Plotly)                 │
│      └─ Exportación: JSON + MD + HTML + PNG            │
└──────────────────────────────────────────────────────────┘
                            ↓
                [Resumen Ejecutivo Consolidado]
```

---

## 📦 Instalación

### Requisitos Previos

- **Python:** 3.8 o superior
- **Sistema Operativo:** Windows, macOS, Linux
- **RAM:** Mínimo 4GB (recomendado 8GB)
- **Conexión a Internet:** Para descargar datos de yfinance

### Instalación Paso a Paso

1. **Clonar o descargar el proyecto:**

```bash
cd analisis-tecnico
```

2. **Crear entorno virtual (recomendado):**

```bash
# Windows
python -m venv .venv
.\.venv\Scripts\activate

# macOS/Linux
python3 -m venv .venv
source .venv/bin/activate
```

3. **Instalar dependencias:**

```bash
pip install -r requirements.txt
```

**Dependencias principales:**
- `pandas` - Manipulación de datos
- `numpy` - Cálculos numéricos
- `pandas-ta` - Indicadores técnicos
- `yfinance` - Datos financieros
- `plotly` - Visualizaciones interactivas
- `kaleido` - Exportación de gráficos PNG
- `requests` - HTTP para sentimiento
- `beautifulsoup4` - Web scraping
- `lxml` - Parseo HTML/XML

4. **Verificar instalación:**

```bash
python -c "import pandas_ta as ta; print(f'✅ pandas-ta {ta.version}')"
python -c "import yfinance as yf; print('✅ yfinance OK')"
python -c "import plotly; print('✅ plotly OK')"
```

---

## 🚀 Guía de Uso

### Uso Básico: Análisis Completo Automático

```bash
python run_integrated_system.py
```

**Esto ejecutará:**
1. Radar S&P 500 (régimen alcista → Radares 1 y 2)
2. Radar Crypto Top 30 (régimen basado en BTC-USD)
3. Análisis profundo del portfolio configurado
4. Análisis de candidatos del radar
5. Generación de resumen ejecutivo con alertas

### Configuración del Portfolio

Edita `run_integrated_system.py` (líneas 833-843):

```python
mi_portafolio_completo = [
    # Stocks e índices
    'PAXG-USD',  # Oro digital
    '^GSPC',     # S&P 500
    # Crypto
    'BTC-USD',   # Bitcoin
    'ETH-USD',   # Ethereum
    'BNB-USD',   # Binance Coin
    'SOL-USD'    # Solana
]
```

### Uso Avanzado: Componentes Individuales

#### 1. Solo Radares Tácticos

```python
from tactical_radars import TacticalRadarSystem
from market_radar import MarketRadar

# Obtener universo S&P 500
radar_temp = MarketRadar(universe="sp500")
radar_temp.load_universe()

# Ejecutar sistema táctico
tactical = TacticalRadarSystem(benchmark="^GSPC")
candidates, metrics, radars_used = tactical.run_tactical_scan(
    tickers=radar_temp.tickers,
    period="6mo",
    max_candidates=15
)

print(f"Régimen: {tactical.market_regime}")
print(f"Candidatos: {candidates}")
```

#### 2. Solo SVGA (Análisis Profundo)

```python
from svga_system import SVGASystem

svga = SVGASystem(
    portfolio_tickers=['AAPL', 'MSFT', 'NVDA'],
    market_tickers=['GOOGL', 'AMZN', 'META']
)
svga.run()
```

#### 3. Solo Radar de Mercado (v5.0 con Scoring)

```python
from market_radar import MarketRadar

radar = MarketRadar(universe="crypto30")
candidates, metrics = radar.scan(
    period="3mo",
    strategy="momentum",  # o "breakout", "value", "mixed"
    max_candidates=20
)

# Ver scores
print(metrics[['ticker', 'price', 'score', 'confianza', 'roc_10d']].head(10))
```

### Estrategias de Radar Disponibles

| Estrategia | Descripción | Mejor para |
|------------|-------------|------------|
| `momentum` | Alto volumen + tendencia alcista + ROC > 3% | Mercados alcistas |
| `breakout` | Rupturas de rango con volumen | Consolidaciones |
| `golden_cross` | SMA 50 > SMA 200 con volumen | Cambios de tendencia |
| `value` | Activos infravalorados comenzando a subir | Reversiones |
| `mixed` | Combinación de múltiples señales | Uso general |

---

## 🧩 Componentes del Sistema

### 1. `run_integrated_system.py` - Orquestador Principal

**Función:** Ejecuta el flujo completo de 3 fases

**Características:**
- Configura portfolio y universos
- Ejecuta radares tácticos
- Lanza análisis SVGA
- Genera resumen ejecutivo
- Exporta todos los resultados

### 2. `tactical_radars.py` - Sistema de Radares Tácticos

**Función:** Implementa el flujo de 3 fases con 5 radares

**Características:**
- Determina régimen de mercado automáticamente
- Selecciona radares apropiados
- Calcula métricas adaptativas (EMA ajustadas a historia disponible)
- Genera scores para cada candidato
- Exporta CSV con resultados

**Radares Implementados:**

**RADAR 1: Reversión a la Media**
```python
# Criterios:
- Precio > EMA 100 (tendencia alcista de fondo)
- Precio < EMA 50 (retroceso temporal)
- RSI < 40 (sobreventa)
# Lógica: Comprar la caída en tendencia alcista
```

**RADAR 2: Ignición de Momentum**
```python
# Criterios:
- MACD histograma cruzando de negativo a positivo
- ADX > 20 (tendencia emergente)
- RSI > 50 (momentum alcista)
# Lógica: Comprar la ruptura temprana
```

**RADAR 3: Reversión Bajista**
```python
# Criterios:
- Precio < EMA 100 (tendencia bajista de fondo)
- Precio > EMA 50 (rebote temporal)
- RSI > 60 (sobrecompra)
# Lógica: Vender el rebote en tendencia bajista
```

**RADAR 4: Ruptura Bajista**
```python
# Criterios:
- MACD histograma cruzando de positivo a negativo
- ADX > 20 (tendencia emergente)
- RSI < 50 (momentum bajista)
# Lógica: Vender la caída temprana
```

**RADAR 5: Mercado Lateral**
```python
# Criterios:
- ADX < 20 (sin tendencia)
- RSI entre 35-65 (rango neutral)
- Cruces frecuentes de EMAs
# Lógica: Operar los extremos del rango
```

### 3. `market_radar.py` - Radar de Mercado v5.0

**Función:** Escaneo masivo con scoring 0-100

**Características:**
- Descarga batch eficiente (1 llamada API)
- Cálculo vectorizado de métricas
- Sistema de scoring multi-factor
- Integración con sentimiento (Fear & Greed)
- Clasificación por confianza (ALTA/MEDIA/BAJA)

**Universos Soportados:**
- `sp500` - S&P 500 (503 tickers)
- `nasdaq100` - NASDAQ 100
- `crypto30` - Top 30 Criptomonedas
- `crypto50` - Top 50 Criptomonedas
- `crypto100` - Top 100 Criptomonedas
- `custom` - Lista personalizada

**Scoring Multi-Factor:**
```
Score = Momentum (0-25) + Volumen (0-15) + Tendencia (0-20) 
        + Señales Especiales (0-30) + Ajuste Sentimiento (-10 a +10)

Clasificación:
- ALTA confianza: Score 70-100
- MEDIA confianza: Score 50-70
- BAJA confianza: Score 0-50
```

### 4. `svga_system.py` - Motor de Análisis Profundo

**Función:** Análisis técnico exhaustivo con 20+ indicadores

**Características:**
- Descarga de datos históricos (yfinance)
- Cálculo de 20+ indicadores (pandas-ta)
- Generación de señales (lógica Murphy)
- Detección de divergencias
- Identificación de rupturas
- Gráficos interactivos multi-panel
- Exportación HTML + PNG

**Señales Generadas:**
- `COMPRAR` - Alta probabilidad de movimiento alcista
- `VENDER` - Alta probabilidad de movimiento bajista
- `MANTENER` - Sin señales claras

**Prioridades:**
- `HIGH` - Señal respaldada por múltiples indicadores
- `MEDIUM` - Señal con confirmación moderada
- `LOW` - Señal sin confirmación fuerte

### 5. `alertas_avanzadas.py` - Detector de Alertas

**Función:** Detecta anomalías y oportunidades automáticamente

**Tipos de Alertas:**

**Anomalías:**
- Volatilidad aumentada (ATR% > umbral)
- Volumen inusual (RVOL > 3x o < 0.4x)
- Cambios abruptos de precio (> 5%)
- Correlaciones rotas entre activos

**Oportunidades:**
- Patrones alcistas/bajistas (con probabilidad)
- Divergencias RSI/MACD vs precio
- Confluencias de indicadores

**Probabilidad de Patrones:**
```python
# Factores considerados:
- EMAs (20% peso)
- RSI (15% peso)
- MACD (25% peso)
- ADX (15% peso)
- Volumen (15% peso)
- Estocástico (10% peso)

# Resultado: Probabilidad 0-100%
```

### 6. `market_context.py` - Análisis de Sentimiento

**Función:** Obtiene índices de sentimiento del mercado

**Fuentes:**
- Fear & Greed Index (Crypto) - CNN Business
- Fear & Greed Index (Stocks) - Alternative.me

**Ajuste de Scoring:**
```
Extreme Fear (< 25) → +10 puntos (oportunidad contrarian)
Fear (25-40)        → +5 puntos
Neutral (40-60)     → 0 puntos
Greed (60-75)       → -5 puntos (reducir riesgo)
Extreme Greed (>75) → -10 puntos
```

---

## 📊 Interpretación de Resultados

### 1. Informe de Portfolio (`portfolio_informe.md`)

```markdown
### 🟢 BTC-USD
**Recomendación:** **COMPRAR** (Prioridad: HIGH)
**Precio Actual:** $111,772.12
**Régimen de Mercado:** TENDENCIA_FUERTE
**Tendencia Largo Plazo:** ALCISTA

#### 🚨 Alertas Detectadas:
- 🔴 **RUPTURA_ALCISTA_CONFIRMADA:** Ruptura de banda superior de Bollinger
- 🟡 **MACD_CRUCE_ALCISTA:** Histograma cruza línea cero al alza
```

**Cómo interpretar:**

- **🟢 COMPRAR + HIGH** = Múltiples indicadores confirman oportunidad alcista
- **TENDENCIA_FUERTE** = ADX > 40, favorece seguimiento de tendencia
- **RUPTURA_ALCISTA_CONFIRMADA** = Precio + Volumen confirman ruptura

### 2. Informe de Mercado (`mercado_informe.md`)

Muestra candidatos del radar con sus señales y alertas.

### 3. Resumen Ejecutivo (`svga_informe_completo.md`)

**Secciones:**
- Distribución de señales (COMPRAR/VENDER/MANTENER)
- Anomalías detectadas
- Oportunidades identificadas
- Alertas de alta prioridad
- Cambios abruptos
- Recomendaciones estratégicas
- Métricas técnicas por activo
- Contexto de mercado

### 4. Gráficos Interactivos (HTML)

**5 Paneles:**

**Panel 1: Precio y Tendencia**
- Candlestick japonés
- EMAs (12, 26, 50, 200)
- Bandas de Bollinger
- Niveles de Fibonacci

**Panel 2: RSI**
- RSI (14)
- Zonas de sobrecompra (70) y sobreventa (30)
- Línea neutral (50)

**Panel 3: MACD**
- Línea MACD (12, 26)
- Línea de Señal (9)
- Histograma (diferencia)

**Panel 4: Volumen + OBV**
- Volumen (barras)
- OBV (línea, eje secundario)
- CMF integrado

**Consejos de lectura:**

- ✅ **Confluencias:** Precio tocando EMA 50 + Fibonacci 61.8% = nivel clave
- ✅ **Divergencias RSI:** RSI ascendente + Precio descendente = reversión inminente
- ✅ **MACD Histograma:** Cruce de línea cero = señal más temprana
- ✅ **OBV + Precio:** Ambos alcistas = tendencia confirmada
- ✅ **CMF > 0:** Presión compradora (dinero entrando)

### 5. CSV de Radares (`radar_sp500.csv`, `radar_crypto.csv`)

```csv
ticker,precio,score,confianza,roc_10d,rvol,rsi,adx,radar
MU,219.02,102.0,ALTA,12.5,2.8,72.2,40.6,Ignición Momentum
IBM,307.46,89.2,ALTA,9.3,2.1,72.0,32.1,Ignición Momentum
```

**Columnas clave:**
- `score`: Ranking 0-100 (mayor = mejor)
- `confianza`: ALTA/MEDIA/BAJA
- `roc_10d`: Momentum 10 días (%)
- `rvol`: Volumen relativo (múltiplo del promedio)
- `radar`: Radar que lo detectó

---

## 📁 Archivos Generados

### Después de ejecutar `run_integrated_system.py`

```
analisis-tecnico/
│
├── 📊 ARCHIVOS SEPARADOS (Portfolio y Mercado)
│   ├── portfolio_analisis.json      # Métricas del portfolio (JSON)
│   ├── portfolio_informe.md         # Informe ejecutivo portfolio (Markdown)
│   ├── mercado_analisis.json        # Métricas candidatos radar (JSON)
│   └── mercado_informe.md           # Informe ejecutivo candidatos (Markdown)
│
├── 📊 ARCHIVOS CONSOLIDADOS
│   ├── svga_completo.json           # Análisis completo (JSON)
│   └── svga_informe_completo.md     # Resumen ejecutivo consolidado (Markdown)
│
├── 📈 GRÁFICOS INTERACTIVOS (Portfolio)
│   ├── chart_PAXG_USD.html          # Gráfico interactivo PAXG
│   ├── chart_PAXG_USD.png           # Gráfico estático PAXG
│   ├── chart_GSPC.html              # Gráfico interactivo S&P 500
│   ├── chart_GSPC.png               # Gráfico estático S&P 500
│   ├── chart_BTC_USD.html           # Gráfico interactivo BTC
│   ├── chart_BTC_USD.png            # Gráfico estático BTC
│   └── ... (uno por cada activo del portfolio)
│
├── 📈 GRÁFICOS DE MERCADO (Candidatos del Radar)
│   ├── market_MU.html               # Gráfico interactivo MU
│   ├── market_MU.png                # Gráfico estático MU
│   ├── market_IBM.html              # Gráfico interactivo IBM
│   ├── market_IBM.png               # Gráfico estático IBM
│   └── ... (uno por cada candidato)
│
└── 📊 RESULTADOS DE RADARES
    ├── radar_sp500.csv              # Resultados radar S&P 500
    └── radar_crypto.csv             # Resultados radar Crypto
```

---

## 🆕 Mejoras y Versiones

### Versión 4.0 (Actual) - Octubre 2025

**Nuevas características:**
- ✅ Sistema de Radares Tácticos con 5 radares
- ✅ Detección automática de régimen de mercado
- ✅ Alertas avanzadas con anomalías y oportunidades
- ✅ Exportación de gráficos PNG (además de HTML)
- ✅ Informe consolidado completo
- ✅ Nombres de archivo fijos (sin timestamps)

### Versión 3.0 - Octubre 2025

**Mejoras:**
- Sistema integrado (Radar + SVGA)
- Portfolio único (stocks + crypto juntos)
- Resumen ejecutivo automatizado

### Versión 2.0 - Octubre 2025

**Mejoras:**
- Radar de mercado escalable (500+ activos)
- Descarga batch eficiente
- Análisis vectorizado
- Indicadores adicionales (Aroon, CMF, Keltner)

### Versión 1.0 - Octubre 2025

**Inicial:**
- Análisis SVGA básico
- 15 indicadores técnicos
- Gráficos interactivos
- Exportación JSON + Markdown

### Comparativa de Versiones

| Característica | v1.0 | v2.0 | v3.0 | v4.0 |
|----------------|------|------|------|------|
| Activos analizables | 10-20 | 500+ | 500+ | 500+ |
| Radares tácticos | ❌ | ❌ | ❌ | ✅ 5 radares |
| Detección régimen | ❌ | ❌ | ❌ | ✅ Automática |
| Alertas avanzadas | ❌ | ❌ | ❌ | ✅ Con probabilidad |
| Indicadores | 15 | 20+ | 20+ | 20+ |
| Exportación PNG | ❌ | ❌ | ❌ | ✅ |
| Resumen ejecutivo | ❌ | ❌ | ✅ | ✅ Mejorado |
| Scoring 0-100 | ❌ | ✅ | ✅ | ✅ |

---

## ⚠️ Limitaciones y Advertencias

### 1. Disclaimer Legal

**Este sistema NO constituye asesoramiento financiero.**

- Es una herramienta de **análisis técnico** para uso educativo e informativo
- Todas las inversiones conllevan **riesgo de pérdida**
- El rendimiento pasado **NO garantiza** resultados futuros
- **Consulte con un asesor financiero** profesional antes de invertir

### 2. Limitaciones de Datos (yfinance)

**Rate Limiting:**
- yfinance tiene límites no documentados
- El sistema minimiza riesgo con descarga batch
- Si escanea > 500 activos, dividir en sesiones

**Calidad de Datos:**
- Datos gratuitos, no profesionales
- Pueden tener retrasos o errores
- Para trading profesional, usar Bloomberg/Refinitiv

**Activos Delisted:**
- Algunos tickers pueden fallar
- El sistema los ignora automáticamente
- Se muestra advertencia en consola

### 3. Backtesting Requerido

**Ningún sistema es infalible:**
- Validar señales históricamente
- Probar con datos out-of-sample
- Ajustar parámetros con precaución
- Evitar sobreoptimización (overfitting)

### 4. Dependencia de Internet

**Requiere conexión:**
- Para descargar datos (yfinance)
- Para obtener sentimiento (Fear & Greed)
- Sin internet, el sistema no funciona

### 5. Recursos Computacionales

**Requisitos:**
- Análisis completo consume ~500MB RAM
- Generación de gráficos PNG requiere Kaleido
- En sistemas limitados, desactivar exportación PNG

---

## ❓ FAQ

### ¿Cuánto tiempo tarda un análisis completo?

**Típicamente:**
- Radar S&P 500 (503 tickers): ~30-45 segundos
- Radar Crypto (30 tickers): ~10-15 segundos
- Análisis SVGA portfolio (6 activos): ~20 segundos
- Análisis SVGA candidatos (10 activos): ~30 segundos
- Generación de gráficos: ~40 segundos
- **TOTAL: ~2-3 minutos**

### ¿Puedo analizar acciones fuera del S&P 500?

**Sí, de dos formas:**

1. **Añadir al portfolio:**
```python
mi_portafolio = ['AAPL', 'TSLA', 'NVDA']  # Cualquier ticker
```

2. **Crear universo personalizado:**
```python
radar = MarketRadar(universe="custom")
radar.load_universe(custom_tickers=['AAPL', 'MSFT', 'GOOGL'])
```

### ¿Funciona con criptomonedas?

**Sí, completamente:**
- Radar Crypto Top 30/50/100
- Análisis profundo de cualquier cripto en yfinance
- Usa sufijo `-USD` (ej: `BTC-USD`, `ETH-USD`)

### ¿Qué hacer si un ticker falla al descargar?

**El sistema lo maneja automáticamente:**
- Muestra advertencia en consola
- Continúa con los demás tickers
- No interrumpe el análisis

**Si quieres eliminar un ticker problemático:**
- Edita `market_radar.py` → `get_crypto_tickers()` o `get_sp500_tickers()`

### ¿Puedo cambiar los parámetros de los indicadores?

**Sí, pero con precaución:**

**En `svga_system.py`** - Método `calculate_indicators()`:
```python
df.ta.rsi(length=14, append=True)  # Cambiar 14 a otro valor
df.ta.ema(length=50, append=True)  # Cambiar 50 a otro valor
```

**⚠️ Advertencia:** Usar configuraciones estándar Murphy. No optimizar sin backtesting.

### ¿Los gráficos se actualizan automáticamente?

**No, son estáticos:**
- Se generan en el momento del análisis
- Para actualizar, ejecutar `run_integrated_system.py` nuevamente
- Los archivos se sobrescriben (nombres fijos)

### ¿Puedo exportar a Excel?

**Sí, los CSV se abren en Excel:**
- `radar_sp500.csv`
- `radar_crypto.csv`

**Los JSON también:**
- Importar en Excel → Datos → Desde JSON

### ¿Funciona en tiempo real?

**No, es análisis de fin de día:**
- Usa datos históricos de cierre
- Para tiempo real, necesitas API profesional
- yfinance tiene datos con retraso (~15 min)

### ¿Puedo ejecutarlo en un servidor/cron?

**Sí, es totalmente automatizable:**

```bash
# Linux/Mac - Cron diario a las 18:00
0 18 * * * cd /path/to/analisis-tecnico && .venv/bin/python run_integrated_system.py

# Windows - Task Scheduler
# Crear tarea que ejecute:
C:\Users\...\analisis-tecnico\.venv\Scripts\python.exe C:\Users\...\analisis-tecnico\run_integrated_system.py
```

### ¿Cómo interpreto un score de 45 (confianza BAJA)?

**Score 45 = Candidato especulativo:**
- Tiene algunas señales positivas
- No tiene confirmación fuerte
- Requiere mayor análisis manual
- Considerar solo si perfil de riesgo alto

**Recomendación:**
- ALTA confianza (70-100): Analizar primero
- MEDIA confianza (50-70): Revisar gráficos
- BAJA confianza (0-50): Opcional/especulativo

---

## 📚 Referencias

### Fundamentos Teóricos

1. **Murphy, John J.** - "Technical Analysis of the Financial Markets"
   - Biblia del análisis técnico
   - Principios implementados en SVGA

2. **Wilder, J. Welles** - "New Concepts in Technical Trading Systems"
   - RSI, ADX, ATR, Parabolic SAR

3. **Donchian, Richard** - "Donchian Channels y sistemas de ruptura"

4. **Bollinger, John** - "Bollinger on Bollinger Bands"

### Bibliotecas y Herramientas

5. **Pandas TA** - https://github.com/twopirllc/pandas-ta
   - Biblioteca de indicadores técnicos

6. **yfinance** - https://github.com/ranaroussi/yfinance
   - API Python para datos de Yahoo Finance

7. **Plotly** - https://plotly.com/python/
   - Visualizaciones interactivas

### Recursos Adicionales

8. **Investopedia** - https://www.investopedia.com/
   - Educación financiera

9. **TradingView** - https://www.tradingview.com/
   - Plataforma de gráficos

10. **Fear & Greed Index** - https://alternative.me/crypto/fear-and-greed-index/
    - Sentimiento del mercado crypto

---

## 🤝 Contribuciones y Soporte

**Desarrollado por:** AIDA (Artificial Intelligence Data Architect)  
**Versión:** 4.0  
**Última actualización:** Octubre 2025  
**Licencia:** MIT  

### Estructura del Proyecto

```
analisis-tecnico/
├── run_integrated_system.py    # Script principal (ejecutar este)
├── tactical_radars.py           # Sistema de radares tácticos
├── market_radar.py              # Radar de mercado v5.0
├── svga_system.py               # Motor de análisis profundo
├── alertas_avanzadas.py         # Detector de alertas
├── market_context.py            # Análisis de sentimiento
├── requirements.txt             # Dependencias Python
└── README.md                    # Este archivo
```

### Próximas Mejoras (Roadmap)

**Prioridad Alta:**
- [ ] Dashboard web interactivo (Streamlit/Dash)
- [ ] Alertas por email/Telegram
- [ ] Backtesting engine integrado

**Prioridad Media:**
- [ ] Reconocimiento de patrones avanzados (H&S, Copas)
- [ ] Ratio Put/Call para análisis de opciones
- [ ] Integración con más fuentes de datos

**Prioridad Baja:**
- [ ] Machine Learning para ajuste adaptativo
- [ ] Integración con brokers para ejecución
- [ ] Análisis de griegas de opciones

---

## 🎓 Casos de Uso

### Caso 1: Trader Diario

**Objetivo:** Encontrar oportunidades de trading en S&P 500

**Flujo:**
1. Ejecutar `python run_integrated_system.py` por la mañana
2. Revisar `radar_sp500.csv` → Filtrar por confianza ALTA
3. Abrir gráficos HTML de top 5 candidatos
4. Buscar confluencias (EMA 50 + Fibonacci + Volumen)
5. Operar solo señales con `COMPRAR` + `HIGH`

### Caso 2: Inversor de Largo Plazo

**Objetivo:** Monitorear portfolio mensualmente

**Flujo:**
1. Configurar portfolio en `run_integrated_system.py`
2. Ejecutar el primer día de cada mes
3. Revisar `portfolio_informe.md`
4. Actuar solo en alertas de alta prioridad
5. Revisar `svga_informe_completo.md` para contexto

### Caso 3: Analista Cuantitativo

**Objetivo:** Identificar activos para modelo cuantitativo

**Flujo:**
1. Ejecutar radares con `strategy="mixed"`
2. Exportar `radar_sp500.csv` a Python/R
3. Aplicar filtros adicionales (liquidez, beta, etc.)
4. Backtest en datos históricos
5. Integrar en estrategia cuantitativa

---

## 🏁 Conclusión

El **SVGA System v4.0** es una herramienta profesional de análisis técnico que combina:

- ✅ **Escalabilidad** (500+ activos)
- ✅ **Precisión** (20+ indicadores)
- ✅ **Automatización** (alertas avanzadas)
- ✅ **Visualización** (gráficos interactivos)
- ✅ **Exportación** (múltiples formatos)

**Ideal para:**
- Traders que necesitan screening eficiente
- Inversores que buscan análisis objetivo
- Analistas que quieren herramientas profesionales
- Científicos de datos interesados en finanzas

**Recuerda:**
- Úsalo como **herramienta de apoyo**, no como sistema infalible
- Combina con análisis fundamental
- Aplica gestión de riesgo adecuada
- Valida con backtesting antes de operar

---

**¡Feliz Trading! 📈**

*"The trend is your friend until the end when it bends."*  
— Ed Seykota

---


