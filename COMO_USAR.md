# 🚀 Cómo Usar el Sistema Multi-Usuario - Guía Práctica

## 📋 Resumen Rápido

Has implementado exitosamente un sistema de análisis técnico multi-usuario que:
- ✅ Lee usuarios desde Supabase
- ✅ Analiza portfolio individual de cada usuario
- ✅ Sube informes a Supabase Storage organizados por usuario
- ✅ Optimizado para Heroku Eco con procesamiento eficiente

---

## 🎯 Paso a Paso para Empezar

### 1️⃣ Configurar Supabase (Primera Vez)

#### a) Crear Bucket de Storage
```
1. Ve a https://app.supabase.com
2. Selecciona tu proyecto
3. Storage > "Create bucket"
4. Nombre: portfolio-files
5. Tipo: Privado (no público)
6. Click "Create"
```

#### b) Crear Tabla de Usuarios
```sql
-- En SQL Editor de Supabase, ejecuta:

CREATE TABLE profiles (
  id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
  email text NOT NULL,
  active boolean DEFAULT true,
  created_at timestamp DEFAULT now()
);

-- Insertar tu primer usuario de prueba:
INSERT INTO profiles (email, active)
VALUES ('tu_email@example.com', true);
```

#### c) Obtener Credenciales
```
1. Settings > API
2. Copiar:
   - Project URL
   - Service role key (secret key)
```

---

### 2️⃣ Configurar Localmente

#### a) Crear Archivo de Variables
```bash
# En la raíz del proyecto
cp env.example .env

# Editar con tus datos reales
nano .env
```

Completa:
```bash
SUPABASE_URL=https://tu-proyecto-real.supabase.co
SUPABASE_KEY=tu_service_role_key_aqui
SVGA_INTERVAL_MINUTES=15
MAX_WORKERS=1
```

#### b) Instalar Dependencias
```bash
pip install -r requirements.txt
```

---

### 3️⃣ Probar en Local

#### Test 1: Verificar Conexión
```bash
python supabase_manager.py
```
✅ Espera ver: "✅ Conexión exitosa"

#### Test 2: Ver Usuarios
```bash
python user_manager.py
```
✅ Espera ver: "✅ 1 usuarios activos encontrados"

#### Test 3: Ejecutar Una Vez
```bash
RUN_ONCE=true python run_multiuser_system.py
```

✅ Espera ver:
```
📡 RADAR S&P 500... ✅ 10 candidatos
📡 RADAR CRYPTO... ✅ 10 candidatos
👤 ANALIZANDO USUARIO: tu_email@example.com
📤 SUBIENDO RESULTADOS A SUPABASE...
✅ 4/4 archivos subidos correctamente
```

#### Test 4: Verificar en Supabase
```
1. Ve a Storage > portfolio-files
2. Deberías ver una carpeta con el ID de tu usuario
3. Dentro hay 4 archivos:
   ✅ portfolio_analisis.json
   ✅ portfolio_informe.md
   ✅ mercado_analisis.json
   ✅ mercado_informe.md
```

---

### 4️⃣ Desplegar en Heroku

#### a) Inicializar Git (si no lo has hecho)
```bash
git init
git add .
git commit -m "Multi-user system ready"
```

#### b) Crear App en Heroku
```bash
# Instalar Heroku CLI primero: https://devcenter.heroku.com/articles/heroku-cli

heroku login
heroku create tu-app-analisis-tecnico
```

#### c) Configurar Variables en Heroku
```bash
heroku config:set SUPABASE_URL="https://tu-proyecto.supabase.co"
heroku config:set SUPABASE_KEY="tu_service_role_key"
heroku config:set SVGA_INTERVAL_MINUTES=15
heroku config:set MAX_WORKERS=1
```

#### d) Desplegar
```bash
git push heroku main

# O si usas branch diferente:
git push heroku tu-branch:main
```

#### e) Activar el Worker
```bash
heroku ps:scale worker=1
```

#### f) Ver Logs en Tiempo Real
```bash
heroku logs --tail
```

---

## 📊 Entender los Archivos Generados

### Para Cada Usuario se Crean 4 Archivos:

#### 1. `portfolio_analisis.json`
- Contiene datos técnicos en formato JSON
- Métricas: RSI, MACD, EMAs, ADX, etc.
- Niveles de Fibonacci
- Señales de compra/venta
- **Uso**: APIs, dashboards, aplicaciones

#### 2. `portfolio_informe.md`
- Informe ejecutivo en Markdown
- Recomendaciones claras (COMPRAR/VENDER/MANTENER)
- Alertas de alta prioridad
- Fácil de leer para humanos
- **Uso**: Emails, reportes, documentación

#### 3. `mercado_analisis.json`
- Candidatos identificados por los radares
- Top oportunidades del S&P 500
- Top oportunidades crypto
- **Uso**: Descubrir nuevos activos para invertir

#### 4. `mercado_informe.md`
- Informe de candidatos del mercado
- Contexto de cada oportunidad
- Señales y métricas clave
- **Uso**: Análisis de nuevas oportunidades

---

## ⚙️ Personalizar el Sistema

### Cambiar Intervalo de Ejecución

**Local:**
```bash
# En .env
SVGA_INTERVAL_MINUTES=30
```

**Heroku:**
```bash
heroku config:set SVGA_INTERVAL_MINUTES=30
heroku restart
```

### Agregar Más Usuarios

**Opción 1: Manualmente en Supabase**
```sql
INSERT INTO profiles (email, active)
VALUES 
  ('usuario1@example.com', true),
  ('usuario2@example.com', true),
  ('usuario3@example.com', true);
```

**Opción 2: Desde tu Aplicación**
```python
from user_manager import UserManager

manager = UserManager()
# Tu lógica para crear usuarios
```

### Personalizar Portfolio por Usuario

1. Crear tabla de configuración:
```sql
CREATE TABLE portfolio_config (
  id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id uuid REFERENCES profiles(id) ON DELETE CASCADE,
  portfolio_tickers jsonb DEFAULT '["BTC-USD", "ETH-USD", "BNB-USD"]'::jsonb,
  scan_sp500 boolean DEFAULT true,
  scan_crypto boolean DEFAULT true,
  max_candidates integer DEFAULT 10,
  created_at timestamp DEFAULT now(),
  updated_at timestamp DEFAULT now()
);
```

2. Insertar configuración para un usuario:
```sql
INSERT INTO portfolio_config (user_id, portfolio_tickers)
VALUES (
  'user-uuid-aqui', 
  '["AAPL", "MSFT", "GOOGL", "BTC-USD", "ETH-USD"]'::jsonb
);
```

3. El sistema automáticamente usará esta configuración

---

## 🔍 Monitorear el Sistema

### Ver Estado del Worker
```bash
heroku ps
```

### Ver Últimos Logs
```bash
heroku logs -n 500
```

### Guardar Logs a Archivo
```bash
heroku logs -n 1000 > logs_analisis.txt
```

### Ver Uso de Recursos
```bash
heroku ps:type
```

### Reiniciar si Necesario
```bash
heroku restart
```

---

## 🛠️ Troubleshooting

### ❌ "No se encontraron usuarios activos"

**Causa**: La tabla `profiles` está vacía

**Solución**:
```sql
-- Verificar usuarios
SELECT * FROM profiles WHERE active = true;

-- Si está vacía, insertar:
INSERT INTO profiles (email, active)
VALUES ('test@example.com', true);
```

---

### ❌ "Bucket 'portfolio-files' NO encontrado"

**Causa**: El bucket no existe en Storage

**Solución**:
1. Supabase Dashboard > Storage
2. Create bucket
3. Nombre: `portfolio-files`
4. Tipo: Privado

---

### ❌ Error R14 en Heroku (Memory exceeded)

**Causa**: Demasiados workers o procesamiento paralelo

**Solución**:
```bash
heroku config:set MAX_WORKERS=1
heroku config:set SVGA_INTERVAL_MINUTES=30
heroku restart
```

---

### ❌ Error 429 "Too Many Requests"

**Causa**: Demasiadas requests a yfinance API

**Solución**:
- Aumentar intervalo entre ejecuciones
- Reducir número de tickers en portfolios
- El sistema ya optimiza compartiendo el radar

---

## 📈 Optimizaciones Implementadas

✅ **Radar Compartido**: El mercado se escanea UNA VEZ para todos los usuarios  
✅ **Procesamiento Secuencial**: Por defecto, para Heroku Eco  
✅ **Sin Archivos Locales**: Todo en memoria, directo a Supabase  
✅ **Upsert Automático**: Siempre la última versión sin errores  
✅ **Cache Inteligente**: Evita escaneos duplicados  

---

## 🎯 Flujo Típico de Ejecución

```
[15:00] Ciclo #1 inicia
├─ [15:01] Consultando usuarios → 5 usuarios encontrados
├─ [15:02] Radar S&P 500 → 10 candidatos
├─ [15:04] Radar Crypto → 10 candidatos
├─ [15:05] Analizando usuario 1 → ✅ Archivos subidos
├─ [15:07] Analizando usuario 2 → ✅ Archivos subidos
├─ [15:09] Analizando usuario 3 → ✅ Archivos subidos
├─ [15:11] Analizando usuario 4 → ✅ Archivos subidos
├─ [15:13] Analizando usuario 5 → ✅ Archivos subidos
└─ [15:14] Ciclo completado en 14 minutos

⏱️ Esperando 15 minutos...

[15:29] Ciclo #2 inicia...
```

---

## 📞 Siguiente Nivel

### Crear Dashboard Web (Opcional)
Para visualizar los informes en una interfaz web:

1. Framework recomendado: Streamlit o Flask
2. Leer archivos desde Supabase Storage
3. Mostrar gráficos interactivos
4. Permitir filtros por usuario/fecha

### Implementar Notificaciones (Opcional)
```python
# Ejemplo: enviar email si hay alertas HIGH
if alert['priority'] == 'HIGH':
    send_email_alert(user_email, alert_details)
```

### Análisis Histórico (Opcional)
- Guardar snapshots diarios
- Crear tabla de historial
- Comparar tendencias a lo largo del tiempo

---

## ✅ Checklist de Configuración

Marca cuando completes cada paso:

- [ ] Bucket `portfolio-files` creado en Supabase
- [ ] Tabla `profiles` creada con usuarios
- [ ] Variables de entorno configuradas (`.env`)
- [ ] Prueba local ejecutada con éxito
- [ ] Archivos visibles en Supabase Storage
- [ ] App creada en Heroku
- [ ] Variables configuradas en Heroku
- [ ] Código desplegado en Heroku
- [ ] Worker activado (`heroku ps:scale worker=1`)
- [ ] Logs verificados sin errores

---

## 🎓 Recursos Adicionales

- **SUPABASE_SETUP.md**: Guía completa paso a paso
- **QUICKSTART.md**: Guía rápida de 10 minutos
- **INTEGRATION_SUMMARY.md**: Resumen técnico de la arquitectura

---

**¡Tu sistema está listo para analizar portfolios automáticamente! 🚀📈**

Si tienes dudas, revisa los logs y la documentación detallada.

