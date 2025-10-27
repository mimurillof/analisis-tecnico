# 🔄 Sistema de Ejecución Continua - SVGA

## 📋 Descripción

El sistema SVGA ahora incluye **ejecución continua automática**, ejecutando análisis completos en intervalos configurables.

## 🚀 Uso Básico

### Ejecutar con intervalo por defecto (15 minutos)

```bash
python run_integrated_system.py
```

El sistema ejecutará el análisis completo cada 15 minutos indefinidamente hasta que lo detengas con `Ctrl+C`.

## ⚙️ Configuración del Intervalo

### Opción 1: Variable de Entorno (Windows PowerShell)

```powershell
$env:SVGA_INTERVAL_MINUTES="30"
python run_integrated_system.py
```

### Opción 2: Variable de Entorno (Windows CMD)

```cmd
set SVGA_INTERVAL_MINUTES=30
python run_integrated_system.py
```

### Opción 3: Variable de Entorno (Linux/Mac)

```bash
export SVGA_INTERVAL_MINUTES=30
python run_integrated_system.py
```

## 🎯 Características

### ✅ Lo que hace el sistema en cada ciclo:

1. **Fase 1: Radares Tácticos**
   - Escanea S&P 500 (503 tickers)
   - Escanea Top 30 Crypto
   - Identifica candidatos según régimen de mercado

2. **Fase 2: Análisis Profundo**
   - Analiza tu portfolio completo
   - Analiza candidatos detectados por los radares
   - Genera gráficos HTML y PNG

3. **Fase 3: Resumen Ejecutivo**
   - Detecta alertas avanzadas
   - Identifica anomalías y oportunidades
   - Genera recomendaciones

4. **Fase 4: Exportación**
   - JSON completo con todas las métricas
   - Informes Markdown detallados
   - Gráficos interactivos

### 📊 Archivos Generados (se actualizan en cada ciclo):

**Archivos Separados:**
- `portfolio_analisis.json` - Métricas del portfolio
- `portfolio_informe.md` - Informe del portfolio
- `mercado_analisis.json` - Métricas del mercado
- `mercado_informe.md` - Informe del mercado

**Archivos Consolidados:**
- `svga_completo.json` - Análisis completo consolidado
- `svga_informe_completo.md` - Informe ejecutivo completo

**Archivos Adicionales:**
- `chart_*.html` - Gráficos interactivos
- `chart_*.png` - Gráficos exportados
- `radar_*.csv` - Resultados de escaneos

## 🛑 Detener la Ejecución

Presiona `Ctrl+C` en cualquier momento para detener el bucle de forma segura.

## 📝 Ejemplo de Salida

```
🚀 Iniciando modo de análisis continuo...
   - Portfolio único (stocks + crypto) + Radar S&P 500
   - Análisis de mercado (candidatos S&P 500 + candidatos crypto)
   - Resumen ejecutivo con alertas avanzadas
   - Intervalo entre ejecuciones: 15 minutos

================================================================================
🔁 Ciclo #1 - Inicio: 2025-10-26 13:23:54
================================================================================

[... análisis completo ...]

✅ Ciclo #1 completado en 3.45 minutos

⏱️ Esperando 15 minutos para la próxima ejecución. Presiona Ctrl+C para detener.

================================================================================
🔁 Ciclo #2 - Inicio: 2025-10-26 13:38:54
================================================================================

[... análisis completo ...]
```

## ⚠️ Consideraciones

### Recomendaciones de Intervalo:

- **5-15 minutos**: Para trading activo o mercados volátiles
- **30-60 minutos**: Para seguimiento regular
- **120+ minutos**: Para análisis de largo plazo

### Importante:

- Cada ciclo toma entre 2-5 minutos dependiendo de:
  - Cantidad de activos en portfolio
  - Velocidad de tu conexión
  - Carga del sistema

- Los archivos se **sobrescriben** en cada ciclo con los datos más recientes

- El sistema maneja errores automáticamente y continúa con el siguiente ciclo

## 🔧 Solución de Problemas

### El output no se muestra en tiempo real

El código ya incluye `flush=True` en todos los prints para Windows. Si aún no ves el output:

1. Intenta ejecutar desde una terminal diferente
2. Verifica que Python no esté en modo de buffer completo

### Error de conexión a Internet

El sistema registrará el error y continuará con el siguiente ciclo.

### Consumo de API

Ten en cuenta que yfinance es gratuito, pero ejecutar el análisis muy frecuentemente podría causar límites de rate. Se recomienda no usar intervalos menores a 5 minutos.

## 💡 Tips

1. **Monitoreo en segundo plano**: Puedes minimizar la ventana y el sistema seguirá ejecutándose
2. **Logs**: Considera redirigir la salida a un archivo para registro histórico:
   ```bash
   python run_integrated_system.py > logs_svga.txt 2>&1
   ```
3. **Horarios de mercado**: Considera ejecutar solo durante horarios de mercado activos

---

**Sistema SVGA v4.0** - Análisis Técnico Continuo con Alertas Avanzadas

