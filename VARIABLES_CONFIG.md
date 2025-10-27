# 📝 Guía Completa de Variables de Entorno

## ✅ Variables que Tienes Configuradas

Basado en tu archivo `.env`, aquí está la explicación de cada variable:

---

## 🔐 Variables de Supabase (OBLIGATORIAS)

### `SUPABASE_URL`
```bash
SUPABASE_URL=https://tlmdrkthueicqnvbjmie.supabase.co
```
- **Qué es**: URL única de tu proyecto Supabase
- **Dónde obtenerla**: Dashboard > Settings > API > Project URL
- **Uso**: Todas las conexiones a Supabase la necesitan

---

### `SUPABASE_ANON_KEY`
```bash
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```
- **Qué es**: Clave pública para frontend (respeta RLS)
- **Dónde obtenerla**: Dashboard > Settings > API > anon key
- **Uso**: Para apps frontend/cliente (NO se usa en este backend)
- **Seguridad**: ✅ Segura para exponer públicamente (respeta Row Level Security)

---

### `SUPABASE_SERVICE_ROLE` ⚠️ (LA MÁS IMPORTANTE PARA BACKEND)
```bash
SUPABASE_SERVICE_ROLE=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```
- **Qué es**: Clave de administrador con privilegios totales
- **Dónde obtenerla**: Dashboard > Settings > API > service_role key
- **Uso**: **Backend exclusivamente** - omite todas las políticas RLS
- **Seguridad**: ❌ **NUNCA exponer en frontend/cliente**
- **Por qué la usamos**: Permite crear/actualizar archivos sin configurar políticas RLS complejas

---

## 📦 Variables de Storage

### `SUPABASE_BUCKET_NAME`
```bash
SUPABASE_BUCKET_NAME=portfolio-files
```
- **Qué es**: Nombre del bucket donde se guardan los archivos
- **Default**: `portfolio-files`
- **Uso**: Puedes cambiarlo si quieres usar otro bucket

---

### `SUPABASE_BASE_PREFIX`
```bash
SUPABASE_BASE_PREFIX=048adfcc-fe6e-4608-9b74-fc5608eed985
```
- **Qué es**: Prefijo opcional para organización
- **Uso actual**: Puede ser:
  - ID de una organización madre
  - ID de un proyecto específico
  - Prefijo para agrupar usuarios
- **En el código**: Actualmente NO se usa, pero podrías usarlo así:
  ```
  Ruta sin prefijo: {user_id}/archivo.json
  Ruta con prefijo: {base_prefix}/{user_id}/archivo.json
  ```

---

### `ENABLE_SUPABASE_UPLOAD`
```bash
ENABLE_SUPABASE_UPLOAD=true
```
- **Qué es**: Interruptor para activar/desactivar subida
- **Valores**:
  - `true` → Sube archivos a Supabase ✅
  - `false` → Solo genera archivos (útil para testing) ⚠️
- **Uso**: Ponlo en `false` para testing local sin gastar cuota de Storage

---

### `SUPABASE_CLEANUP_AFTER_TESTS`
```bash
SUPABASE_CLEANUP_AFTER_TESTS=false
```
- **Qué es**: Eliminar archivos de prueba automáticamente
- **Valores**:
  - `true` → Borra archivos después de tests
  - `false` → Mantiene archivos (recomendado para producción)
- **Uso**: Útil para CI/CD o tests automatizados

---

## ⚙️ Variables del Sistema de Análisis

### `SVGA_INTERVAL_MINUTES`
```bash
SVGA_INTERVAL_MINUTES=15
```
- **Qué es**: Minutos entre cada ciclo de análisis
- **Valores recomendados**:
  - `15` → Análisis cada 15 minutos (estándar)
  - `30` → Cada media hora (más conservador)
  - `60` → Cada hora (para muchos usuarios)
- **Consideración**: Más frecuente = más requests a yfinance

---

### `MAX_WORKERS`
```bash
MAX_WORKERS=1
```
- **Qué es**: Número de usuarios procesados en paralelo
- **Valores según plan**:
  - `1` → Secuencial (Heroku Eco) ✅
  - `2-3` → Paralelo (Heroku Basic)
  - `4-5` → Paralelo (Heroku Standard+)
- **Consideración**: Más workers = más RAM consumida

---

### `RUN_ONCE`
```bash
RUN_ONCE=false
```
- **Qué es**: Ejecutar solo una vez vs loop infinito
- **Valores**:
  - `false` → Loop infinito (producción) ✅
  - `true` → Ejecuta 1 vez y sale (testing)
- **Uso**: Ponlo en `true` para pruebas rápidas

---

## 🌐 Variables Opcionales

### `PORT`
```bash
PORT=8080
```
- **Qué es**: Puerto para servidor web (futuro)
- **Uso actual**: No se usa (el sistema es un worker, no servidor web)
- **Futuro**: Si implementas dashboard web

---

### `LOG_LEVEL`
```bash
LOG_LEVEL=INFO
```
- **Qué es**: Nivel de detalle en logs
- **Valores**:
  - `DEBUG` → Muestra TODO (verbose)
  - `INFO` → Información estándar ✅
  - `WARNING` → Solo advertencias
  - `ERROR` → Solo errores

---

## 🚀 Configuración para Heroku

### Variables Mínimas Requeridas
```bash
heroku config:set SUPABASE_URL="https://tlmdrkthueicqnvbjmie.supabase.co"
heroku config:set SUPABASE_SERVICE_ROLE="tu_service_role_key_real"
```

### Configuración Completa Recomendada
```bash
# Supabase
heroku config:set SUPABASE_URL="https://tlmdrkthueicqnvbjmie.supabase.co"
heroku config:set SUPABASE_SERVICE_ROLE="eyJhbGciOiJIUzI1..."
heroku config:set SUPABASE_BUCKET_NAME="portfolio-files"
heroku config:set ENABLE_SUPABASE_UPLOAD="true"

# Sistema
heroku config:set SVGA_INTERVAL_MINUTES="15"
heroku config:set MAX_WORKERS="1"
heroku config:set RUN_ONCE="false"
```

### Ver Variables Configuradas
```bash
heroku config
```

### Eliminar una Variable
```bash
heroku config:unset VARIABLE_NAME
```

---

## 🔍 Debugging de Variables

### Verificar que se Cargan Correctamente
Agrega esto al inicio de tu script:
```python
import os
print("=== VARIABLES DE ENTORNO ===")
print(f"SUPABASE_URL: {os.environ.get('SUPABASE_URL', 'NO CONFIGURADA')}")
print(f"SERVICE_ROLE: {'✅ Configurada' if os.environ.get('SUPABASE_SERVICE_ROLE') else '❌ NO configurada'}")
print(f"BUCKET: {os.environ.get('SUPABASE_BUCKET_NAME', 'portfolio-files (default)')}")
print(f"UPLOAD ENABLED: {os.environ.get('ENABLE_SUPABASE_UPLOAD', 'true')}")
```

---

## 📊 Resumen de Prioridades

### 🔴 CRÍTICAS (Sistema no funciona sin ellas)
- `SUPABASE_URL`
- `SUPABASE_SERVICE_ROLE`

### 🟡 IMPORTANTES (Tienen defaults razonables)
- `SUPABASE_BUCKET_NAME` (default: `portfolio-files`)
- `ENABLE_SUPABASE_UPLOAD` (default: `true`)
- `SVGA_INTERVAL_MINUTES` (default: `15`)
- `MAX_WORKERS` (default: `1`)

### 🟢 OPCIONALES (No afectan funcionalidad core)
- `SUPABASE_ANON_KEY` (no se usa en backend)
- `SUPABASE_BASE_PREFIX` (no implementado aún)
- `SUPABASE_CLEANUP_AFTER_TESTS`
- `RUN_ONCE` (default: `false`)
- `PORT` (no se usa)
- `LOG_LEVEL` (default: `INFO`)

---

## ✅ Tu Configuración Está Lista

Con las variables que tienes, el sistema debería funcionar perfectamente. Solo asegúrate de:

1. ✅ Tener el bucket `portfolio-files` creado en Supabase
2. ✅ Tener usuarios en la tabla `profiles`
3. ✅ Variables configuradas en Heroku (si despliegas ahí)

---

## 🆘 Si Algo No Funciona

### Error: "Variables de entorno no encontradas"
```bash
# Local: verifica que .env existe y tiene las variables
cat .env

# Heroku: verifica variables
heroku config
```

### Error: "Connection refused" o timeout
```bash
# Verifica que SUPABASE_URL es correcta
curl https://tlmdrkthueicqnvbjmie.supabase.co
```

### Error: "403 Forbidden" o "Unauthorized"
```bash
# Verifica que SUPABASE_SERVICE_ROLE es la correcta
# Dashboard > Settings > API > service_role key
```

---

**¡Configuración verificada y lista! ✅**

