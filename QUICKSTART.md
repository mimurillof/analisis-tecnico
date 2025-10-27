# ⚡ Quick Start - Sistema Multi-Usuario

Guía rápida para poner en marcha el sistema en 10 minutos.

---

## 📦 Instalación Rápida

### 1. Instalar Dependencias
```bash
pip install -r requirements.txt
```

### 2. Configurar Variables de Entorno
```bash
# Copiar template
cp env.example .env

# Editar con tus credenciales de Supabase
nano .env
```

Completa con tus credenciales reales:
```bash
# Obligatorias
SUPABASE_URL=https://tu-proyecto.supabase.co
SUPABASE_SERVICE_ROLE=tu_service_role_key_aqui

# Opcionales (ya tienen defaults)
SUPABASE_BUCKET_NAME=portfolio-files
ENABLE_SUPABASE_UPLOAD=true
```

### 3. Crear Bucket en Supabase
1. Ve a [Supabase Dashboard](https://app.supabase.com)
2. Storage > Create bucket
3. Nombre: `portfolio-files`
4. Tipo: **Privado** (no público)

### 4. Crear Tabla de Usuarios
En SQL Editor de Supabase:
```sql
CREATE TABLE profiles (
  id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
  email text NOT NULL,
  active boolean DEFAULT true,
  created_at timestamp DEFAULT now()
);

-- Insertar usuario de prueba
INSERT INTO profiles (email, active)
VALUES ('test@example.com', true);
```

---

## 🧪 Probar el Sistema

### Prueba 1: Conexión con Supabase
```bash
python supabase_manager.py
```
✅ Deberías ver: "Conexión exitosa"

### Prueba 2: Consultar Usuarios
```bash
python user_manager.py
```
✅ Deberías ver: "1 usuarios activos encontrados"

### Prueba 3: Ejecución Completa (Una vez)
```bash
RUN_ONCE=true python run_multiuser_system.py
```
✅ Deberías ver:
- 📡 Radar escaneando mercado
- 👤 Analizando usuario test@example.com
- 📤 Subiendo archivos a Supabase
- ✅ Ciclo completado

### Prueba 4: Verificar en Supabase
1. Ve a Storage > `portfolio-files`
2. Busca carpeta con el ID del usuario
3. Deberías ver 4 archivos:
   - `portfolio_analisis.json`
   - `portfolio_informe.md`
   - `mercado_analisis.json`
   - `mercado_informe.md`

---

## 🚀 Desplegar en Heroku

### 1. Crear App
```bash
heroku create tu-app-analisis
```

### 2. Configurar Variables
```bash
# Obligatorias
heroku config:set SUPABASE_URL="https://tu-proyecto.supabase.co"
heroku config:set SUPABASE_SERVICE_ROLE="tu_service_role_key_aqui"

# Sistema
heroku config:set SVGA_INTERVAL_MINUTES=15
heroku config:set MAX_WORKERS=1
heroku config:set ENABLE_SUPABASE_UPLOAD=true

# Opcional
heroku config:set SUPABASE_BUCKET_NAME=portfolio-files
```

### 3. Desplegar
```bash
git add .
git commit -m "Deploy multi-user system"
git push heroku main
```

### 4. Activar Worker
```bash
heroku ps:scale worker=1
heroku logs --tail
```

---

## 📊 Estructura de Archivos Generados

Por cada usuario se generan 4 archivos en Supabase:

```
portfolio-files/
  └── {user_id}/
      ├── portfolio_analisis.json   ← Datos técnicos del portfolio
      ├── portfolio_informe.md       ← Informe ejecutivo del portfolio
      ├── mercado_analisis.json      ← Datos de candidatos del mercado
      └── mercado_informe.md         ← Informe de oportunidades del mercado
```

---

## ⚙️ Configuración Avanzada

### Cambiar Intervalo de Ejecución
```bash
# Local (en .env)
SVGA_INTERVAL_MINUTES=30

# Heroku
heroku config:set SVGA_INTERVAL_MINUTES=30
```

### Activar Procesamiento Paralelo
```bash
# Solo para plan Heroku Basic o superior
heroku config:set MAX_WORKERS=2
```

### Modo Debug (Una Ejecución)
```bash
# Local
RUN_ONCE=true python run_multiuser_system.py

# Heroku
heroku config:set RUN_ONCE=true
heroku restart
```

---

## 🔧 Troubleshooting Común

### ❌ "Variables de entorno no encontradas"
**Solución**: Verifica que `.env` existe y tiene las variables correctas

### ❌ "Bucket 'portfolio-files' NO encontrado"
**Solución**: Crea el bucket manualmente en Supabase Dashboard

### ❌ "No se encontraron usuarios activos"
**Solución**: Inserta usuarios en la tabla `profiles`

### ❌ Error de memoria en Heroku
**Solución**: 
- Usa `MAX_WORKERS=1`
- Aumenta `SVGA_INTERVAL_MINUTES`
- Considera plan Heroku Basic

---

## 📖 Documentación Completa

Para configuración detallada, ver: **[SUPABASE_SETUP.md](./SUPABASE_SETUP.md)**

---

## 🎯 Próximos Pasos

1. ✅ Sistema funcionando
2. 🔄 Agrega más usuarios en `profiles`
3. 📊 Personaliza portfolios por usuario (tabla `portfolio_config`)
4. 📧 Implementa notificaciones (opcional)
5. 🌐 Crea dashboard web (opcional)

---

**¡Listo para analizar! 📈**

