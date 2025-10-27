# 🚀 Guía de Configuración - Sistema Multi-Usuario con Supabase

Esta guía te llevará paso a paso para configurar el sistema de análisis técnico multi-usuario con Supabase.

---

## 📋 **Tabla de Contenidos**

1. [Requisitos Previos](#requisitos-previos)
2. [Configuración de Supabase](#configuración-de-supabase)
3. [Configuración Local](#configuración-local)
4. [Configuración en Heroku](#configuración-en-heroku)
5. [Pruebas del Sistema](#pruebas-del-sistema)
6. [Troubleshooting](#troubleshooting)

---

## 1. Requisitos Previos

### Cuentas Necesarias
- ✅ Cuenta en [Supabase](https://supabase.com) (gratis)
- ✅ Cuenta en [Heroku](https://heroku.com) (plan Eco recomendado)

### Dependencias
```bash
pip install -r requirements.txt
```

---

## 2. Configuración de Supabase

### 2.1. Crear Proyecto

1. Ve a [Supabase Dashboard](https://app.supabase.com)
2. Click en **"New Project"**
3. Completa:
   - **Name**: `analisis-tecnico` (o el nombre que prefieras)
   - **Database Password**: Genera una contraseña segura
   - **Region**: Selecciona la más cercana a tus usuarios
4. Click en **"Create new project"** (tarda ~2 minutos)

### 2.2. Crear Bucket de Storage

1. En el Dashboard, ve a **Storage** (menú lateral)
2. Click en **"Create a new bucket"**
3. Configura:
   - **Name**: `portfolio-files`
   - **Public bucket**: ❌ **NO** (mantener privado)
   - **File size limit**: 50 MB (suficiente para archivos JSON/MD)
   - **Allowed MIME types**: 
     - `application/json`
     - `text/markdown`
4. Click en **"Create bucket"**

### 2.3. Configurar Políticas de Seguridad (RLS)

#### Opción A: Acceso desde Backend (Recomendado)
Si usas `service_role_key` en el backend, las políticas RLS se omiten automáticamente. **No necesitas configurar políticas manualmente**.

#### Opción B: Acceso Controlado por Usuario (Opcional)
Si quieres que los usuarios solo accedan a sus propios archivos:

1. Ve a **Storage** > `portfolio-files` > **Policies**
2. Click en **"New Policy"**
3. Crea política de INSERT:
```sql
-- Nombre: Users can upload their own files
-- Operation: INSERT

-- Policy definition:
(bucket_id = 'portfolio-files') 
AND (auth.uid()::text = (storage.foldername(name))[1])
```

4. Crea política de SELECT:
```sql
-- Nombre: Users can view their own files
-- Operation: SELECT

-- Policy definition:
(bucket_id = 'portfolio-files') 
AND (auth.uid()::text = (storage.foldername(name))[1])
```

5. Crea política de UPDATE:
```sql
-- Nombre: Users can update their own files
-- Operation: UPDATE

-- Policy definition:
(bucket_id = 'portfolio-files') 
AND (auth.uid()::text = (storage.foldername(name))[1])
```

### 2.4. Crear Tabla de Usuarios

1. Ve a **Table Editor**
2. Click en **"Create a new table"**
3. Configura:
   - **Name**: `profiles`
   - Columns:
     | Name | Type | Default | Primary | Not Null |
     |------|------|---------|---------|----------|
     | id | uuid | uuid_generate_v4() | ✅ | ✅ |
     | email | text | - | ❌ | ✅ |
     | active | bool | true | ❌ | ✅ |
     | created_at | timestamp | now() | ❌ | ✅ |

4. Click en **"Save"**

### 2.5. (Opcional) Crear Tabla de Configuración de Portfolios

Si quieres configuraciones personalizadas por usuario:

1. Crear tabla `portfolio_config`:
```sql
CREATE TABLE portfolio_config (
  id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id uuid REFERENCES profiles(id) ON DELETE CASCADE,
  portfolio_tickers jsonb DEFAULT '[]'::jsonb,
  scan_sp500 boolean DEFAULT true,
  scan_crypto boolean DEFAULT true,
  max_candidates integer DEFAULT 10,
  created_at timestamp DEFAULT now(),
  updated_at timestamp DEFAULT now()
);
```

### 2.6. Obtener Credenciales

1. Ve a **Settings** > **API**
2. Copia:
   - **Project URL**: `https://xxxxx.supabase.co`
   - **Project API keys** > `service_role` (⚠️ NUNCA exponer en frontend)

---

## 3. Configuración Local

### 3.1. Crear Archivo de Variables de Entorno

```bash
# Copiar template
cp .env.example .env

# Editar con tus credenciales
nano .env  # o usa tu editor favorito
```

### 3.2. Configurar Variables

Edita `.env` con tus valores reales:

```bash
# Supabase
SUPABASE_URL=https://tu-proyecto-real.supabase.co
SUPABASE_KEY=tu_service_role_key_real_aqui

# Sistema
SVGA_INTERVAL_MINUTES=15
MAX_WORKERS=1
RUN_ONCE=false
```

### 3.3. Instalar Dependencias

```bash
pip install -r requirements.txt
```

---

## 4. Configuración en Heroku

### 4.1. Crear Aplicación en Heroku

```bash
# Login en Heroku
heroku login

# Crear app
heroku create tu-app-analisis-tecnico

# Agregar buildpack de Python
heroku buildpacks:add heroku/python
```

### 4.2. Configurar Variables de Entorno en Heroku

```bash
# Supabase
heroku config:set SUPABASE_URL="https://tu-proyecto.supabase.co"
heroku config:set SUPABASE_KEY="tu_service_role_key_aqui"

# Sistema
heroku config:set SVGA_INTERVAL_MINUTES=15
heroku config:set MAX_WORKERS=1
heroku config:set RUN_ONCE=false
```

### 4.3. Crear Procfile

Crea un archivo `Procfile` en la raíz del proyecto:

```
worker: python run_multiuser_system.py
```

### 4.4. Desplegar

```bash
# Inicializar git (si no está inicializado)
git init
git add .
git commit -m "Setup multi-user system with Supabase"

# Agregar remoto de Heroku
heroku git:remote -a tu-app-analisis-tecnico

# Desplegar
git push heroku main
```

### 4.5. Activar Worker

```bash
# Escalar worker (Heroku Eco)
heroku ps:scale worker=1

# Ver logs
heroku logs --tail
```

---

## 5. Pruebas del Sistema

### 5.1. Prueba de Conexión con Supabase

```bash
# Probar conexión y subida
python supabase_manager.py

# Deberías ver:
# ✅ Cliente Supabase inicializado correctamente
# ✅ Bucket 'portfolio-files' encontrado
# ✅ test_connection.json subido correctamente
```

### 5.2. Prueba de Consulta de Usuarios

```bash
# Probar consulta a la BD
python user_manager.py

# Deberías ver:
# ✅ Cliente Supabase para usuarios inicializado
# 📊 Total: X usuarios activos
```

### 5.3. Ejecución Única de Prueba

```bash
# Ejecutar una sola vez (sin loop infinito)
RUN_ONCE=true python run_multiuser_system.py
```

### 5.4. Verificar Archivos en Supabase

1. Ve a **Supabase Dashboard** > **Storage** > `portfolio-files`
2. Deberías ver carpetas con IDs de usuarios
3. Dentro de cada carpeta: 4 archivos
   - `portfolio_analisis.json`
   - `portfolio_informe.md`
   - `mercado_analisis.json`
   - `mercado_informe.md`

---

## 6. Troubleshooting

### Error: "Variables de entorno no encontradas"
```
❌ Variables de entorno SUPABASE_URL y SUPABASE_KEY son requeridas
```

**Solución**: 
- Verifica que el archivo `.env` existe
- Asegúrate de que las variables están bien escritas
- En Heroku: `heroku config` para verificar variables

### Error: "Bucket 'portfolio-files' NO encontrado"
```
⚠️ Bucket 'portfolio-files' NO encontrado
```

**Solución**:
- Ve a Supabase Dashboard > Storage
- Crea el bucket manualmente con el nombre exacto `portfolio-files`

### Error: "No se encontraron usuarios activos"
```
⚠️ No se encontraron usuarios activos en 'profiles'
```

**Solución**:
- Ve a Supabase Dashboard > Table Editor > `profiles`
- Inserta usuarios de prueba manualmente:
```sql
INSERT INTO profiles (email, active)
VALUES ('test@example.com', true);
```

### Error de Memoria en Heroku Eco
```
Error R14 (Memory quota exceeded)
```

**Solución**:
- Reduce `MAX_WORKERS` a 1
- Aumenta `SVGA_INTERVAL_MINUTES` a 30-60
- Considera plan Heroku Basic ($7/mes con 512MB RAM)

### Error: "Rate limit exceeded" de yfinance
```
429 Too Many Requests
```

**Solución**:
- Aumenta el intervalo entre ejecuciones
- Reduce el número de tickers en portfolios
- Implementa cache de datos de radar (ya incluido)

---

## 📊 Monitoreo

### Ver Logs en Heroku
```bash
# Tiempo real
heroku logs --tail

# Últimas 500 líneas
heroku logs -n 500

# Filtrar por worker
heroku logs --tail --dyno=worker
```

### Métricas de Rendimiento
```bash
# Ver uso de recursos
heroku ps

# Ver estado del worker
heroku ps:type
```

---

## 🎯 Próximos Pasos

1. ✅ Sistema configurado y funcionando
2. 🔄 Crear usuarios en la tabla `profiles`
3. 📊 Opcional: Crear dashboard web para visualizar informes
4. 📧 Opcional: Agregar notificaciones por email
5. 🔐 Opcional: Implementar autenticación de usuarios

---

## 📞 Soporte

Si tienes problemas:
1. Revisa los logs: `heroku logs --tail`
2. Verifica las variables de entorno
3. Comprueba la configuración de Supabase
4. Ejecuta pruebas locales primero

---

**¡Sistema listo para producción! 🚀**

