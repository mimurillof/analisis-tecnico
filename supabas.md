Manual Técnico: Gestión de Archivos en Supabase Storage con Python

Introducción

La gestión programática del almacenamiento de archivos es una piedra angular en las arquitecturas de nube modernas. Habilita procesos de automatización críticos en pipelines de CI/CD, permite el aprovisionamiento dinámico de recursos y asegura la escalabilidad de las aplicaciones. Desde avatares de usuario hasta documentos compartidos, la capacidad de manipular archivos de manera eficiente y segura es fundamental. Este manual técnico está diseñado para guiar a los desarrolladores de Python a través del proceso de configuración, carga y actualización de archivos en Supabase Storage, utilizando la biblioteca oficial supabase-py.

A lo largo de este documento, abordaremos los siguientes puntos clave:

* Configuración inicial del cliente de Supabase: Establecer una conexión segura con su proyecto.
* Creación y gestión de buckets de almacenamiento: Organizar sus archivos en contenedores lógicos.
* Procesos para cargar y actualizar archivos: Implementar las operaciones fundamentales de escritura.
* Consideraciones de seguridad mediante RLS: Entender los permisos necesarios para cada operación.

Con estos conocimientos, estará preparado para integrar un sistema robusto de gestión de archivos en sus aplicaciones Python. Comencemos con el primer paso esencial: la configuración del entorno.


--------------------------------------------------------------------------------


1. Configuración del Entorno y Cliente de Supabase

Una correcta inicialización del cliente de Supabase es el fundamento para cualquier interacción con sus servicios, incluyendo Storage. Este paso garantiza que su aplicación pueda comunicarse de manera segura y autenticada con la infraestructura de su proyecto, utilizando las credenciales adecuadas para autorizar cada operación.

Prerrequisitos de Instalación

Para comenzar, debe instalar la biblioteca supabase-py en su entorno de Python. Puede hacerlo fácilmente utilizando pip:

pip install supabase


Inicialización del Cliente

La función create_client() es el punto de entrada para interactuar con la API de Supabase. Requiere dos parámetros obligatorios que se encuentran en el panel de control (dashboard) de su proyecto Supabase, en la sección de configuración de la API:

1. supabase_url: La URL única de su proyecto Supabase.
2. supabase_key: La clave de API de su proyecto. Puede ser su clave pública anon para operaciones del lado del cliente o, para operaciones de backend que requieren privilegios elevados, la clave service_role. La clave service_role omite todas las políticas de RLS y debe manejarse con extrema confidencialidad.

El siguiente código demuestra cómo instanciar el cliente de manera segura, utilizando variables de entorno para proteger sus credenciales.

import os
from supabase import create_client, Client

# Obtener la URL y la clave desde las variables de entorno
url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")

# Crear el cliente de Supabase
supabase: Client = create_client(url, key)


Advertencia de Seguridad Nunca exponga su supabase_key (especialmente la service_role_key) en el lado del cliente (navegador) o en repositorios de código públicos. La service_role_key tiene privilegios de administrador y debe ser utilizada exclusivamente en un entorno de servidor seguro.

Una vez que el cliente supabase ha sido configurado, está listo para interactuar con los servicios. El siguiente paso lógico es crear un contenedor (bucket) para almacenar los archivos.


--------------------------------------------------------------------------------


2. Gestión de Buckets en Supabase Storage

En el contexto de Supabase Storage, un "bucket" es un contenedor principal diseñado para organizar archivos. Cada bucket funciona como un sistema de archivos independiente, con sus propias reglas de seguridad y políticas de acceso. Antes de poder cargar cualquier archivo, es un prerrequisito indispensable crear al menos un bucket.

Creación de un Bucket

Para crear un nuevo bucket, se utiliza el método supabase.storage.create_bucket(). Este método requiere un id (el nombre único del bucket) y un diccionario de options para configurar su comportamiento.

Para ejecutar esta operación, la política de seguridad a nivel de fila (RLS) requiere que el rol tenga permiso de insert sobre la tabla buckets.

El siguiente ejemplo crea un bucket privado llamado "avatars" con reglas específicas para los tipos de archivo y el tamaño máximo permitido.

response = (
    supabase.storage
    .create_bucket(
        "avatars",
        options={
            "public": False,
            "allowed_mime_types": ["image/png"],
            "file_size_limit": 1024,
        }
    )
)


Las opciones de configuración disponibles se detallan a continuación:

Clave	Descripción
public	Si es True, cualquier persona con el enlace puede acceder a los archivos. Si se establece en False (valor por defecto), se requiere una URL firmada o autorización. Recomendación de arquitectura: Configure public en True únicamente para activos que son genuinamente públicos, como imágenes de marketing. Para cualquier dato sensible o específico del usuario, siempre utilice False y gestione el acceso controlado a través de URLs firmadas.
allowed_mime_types	Una lista de tipos MIME permitidos para la carga de archivos. Por ejemplo, ["image/png", "image/jpeg"].
file_size_limit	El tamaño máximo de archivo permitido en bytes. En el ejemplo, 1024 equivale a 1 KB.

Con el bucket "avatars" ya creado, el sistema está listo para el siguiente paso: poblarlo con archivos.


--------------------------------------------------------------------------------


3. Carga de Archivos: Métodos y Estrategias

La operación de carga es la acción central en la gestión de almacenamiento. La biblioteca supabase-py proporciona un método flexible y potente que permite manejar tanto archivos físicos almacenados en el disco local como datos volátiles que residen en la memoria de la aplicación, adaptándose a diversos casos de uso.

El Método upload()

La función principal para subir archivos es storage.from_("bucket_name").upload(). Para que una operación de carga estándar tenga éxito, la política de RLS activa debe conceder permiso de insert sobre la tabla objects.

Sus parámetros clave son:

Parámetro	Descripción
path	La ruta de destino del archivo dentro del bucket, incluyendo el nombre del archivo (ej. public/avatar1.png).
file	El cuerpo del archivo que se va a almacenar. Puede ser un objeto de archivo abierto desde el disco o un objeto de bytes en memoria.
file_options	Un diccionario con opciones adicionales, como la configuración de la caché o la habilitación del modo upsert.

3.1. Carga Estándar desde un Archivo Local

El escenario más común es cargar un archivo que ya existe en el sistema de archivos del servidor. El siguiente ejemplo muestra cómo abrir un archivo en modo de lectura binaria ("rb") y pasarlo al método upload().

# La ruta del archivo en el sistema local
local_file_path = "./public/avatar1.png"

# La ruta de destino dentro del bucket "avatars"
destination_path = "public/avatar1.png"

with open(local_file_path, "rb") as f:
    response = (
        supabase.storage
        .from_("avatars")
        .upload(
            file=f,
            path=destination_path,
            file_options={"cache-control": "3600", "upsert": "false"}
        )
    )


En este código, el archivo local se carga en la ruta de destino dentro del bucket. Es crucial notar el parámetro file_options={"upsert": "false"}. Este es el comportamiento por defecto y significa que la operación fallará con un error si ya existe un archivo en la ruta public/avatar1.png. Este comportamiento protege contra la sobreescritura accidental y es fundamental para entender el problema que la estrategia de "upsert" resuelve en la siguiente sección.

3.2. Carga Directa de Datos en Memoria

El parámetro file del método upload() acepta directamente el "cuerpo del archivo", lo que significa que puede recibir un objeto de bytes sin necesidad de guardarlo previamente en disco. Este enfoque es ideal para archivos generados dinámicamente (como reportes en PDF o imágenes procesadas) o para manejar archivos recibidos a través de una solicitud de red en un framework web como Flask o FastAPI.

A continuación, se presenta un ejemplo conceptual utilizando la clase BytesIO para simular un archivo en memoria:

import io

# Simula datos de un archivo en memoria (por ejemplo, recibidos de una API)
file_in_memory = io.BytesIO(b"Este es el contenido de un archivo de texto virtual.")

# La ruta de destino dentro del bucket
destination_path = "virtual/documento.txt"

response = (
    supabase.storage
    .from_("avatars")
    .upload(
        file=file_in_memory,
        path=destination_path,
        file_options={"content-type": "text/plain"}
    )
)


Una vez que los archivos están en el bucket, el siguiente desafío común es gestionarlos cuando ya existen.


--------------------------------------------------------------------------------


4. Creación y Actualización de Archivos (Upsert)

El concepto de "upsert" (una combinación de update e insert) ofrece un valor estratégico significativo, ya que simplifica la lógica de la aplicación. En lugar de verificar primero si un archivo existe para decidir si se debe crear o actualizar, una operación de upsert maneja ambos escenarios con un solo comando: crea el archivo si no existe, o lo sobrescribe si ya está presente.

Implementar "Upsert" con el Método upload()

El comportamiento predeterminado del método upload() es fallar si el archivo en la ruta especificada ya existe. Sin embargo, este comportamiento se puede modificar a través del parámetro file_options, configurando la clave upsert como "true".

Para realizar una operación de upsert, el rol necesita los permisos RLS de select, insert y update sobre la tabla objects.

with open("./public/avatar1.png", "rb") as f:
    response = (
        supabase.storage
        .from_("avatars")
        .upload(
            file=f,
            path="public/avatar1.png",
            # Habilita el modo upsert para sobrescribir si el archivo ya existe
            file_options={"cache-control": "3600", "upsert": "true"}
        )
    )


Este comando garantiza que el archivo avatar1.png siempre refleje la versión más reciente, sin generar errores si se intenta subir repetidamente.

Presentar el Método update() para Actualización Explícita

Como alternativa a la operación condicional de upsert, Supabase ofrece el método .update() para reemplazar explícitamente un archivo existente. Esta acción es más directa y su intención es inequívoca: actualizar un recurso conocido.

Para esta operación, se requieren los permisos RLS de update y select sobre la tabla objects.

with open("./public/avatar1.png", "rb") as f:
    response = (
        supabase.storage
        .from_("avatars")
        .update(
            file=f,
            path="public/avatar1.png",
            file_options={"cache-control": "3600", "upsert": "true"}
        )
    )


Nota para desarrolladores: Aunque la documentación oficial incluye upsert: "true" en este ejemplo, su presencia en el método .update() es probablemente redundante. La función principal del método es reemplazar explícitamente un archivo existente, haciendo que la lógica de upsert sea conceptualmente innecesaria. Para una mayor claridad e intención explícita en el código, confíe en el nombre del método como el principal indicador de su comportamiento.

La elección entre estos dos métodos depende de la intención explícita de su lógica de aplicación:

* Utilice .upload(..., upsert=True) cuando su lógica no distingue entre la creación inicial y las actualizaciones posteriores, como al sincronizar la foto de perfil de un usuario. Simplifica el código al no requerir una verificación previa de existencia.
* Prefiera .update() cuando la lógica de su aplicación maneja explícitamente el reemplazo de un archivo. Esto hace que la intención de su código sea más clara y garantiza que se genere un error si el archivo que se intenta reemplazar no existe.


--------------------------------------------------------------------------------


5. Conclusión y Próximos Pasos

A través de este manual, ha adquirido las habilidades clave para gestionar archivos en Supabase Storage con Python. Desde la configuración inicial y segura del cliente hasta la creación de buckets y la ejecución de operaciones de carga y actualización, ahora posee las herramientas necesarias para construir aplicaciones con capacidades de almacenamiento de archivos robustas y eficientes.

Para continuar expandiendo su dominio sobre Supabase Storage, le sugerimos explorar los siguientes temas en la documentación oficial:

* Descarga de archivos: Aprender a recuperar archivos de buckets privados utilizando el método download().
* Generación de URLs firmadas: Crear enlaces de acceso temporal y seguro a archivos privados con create_signed_url.
* Eliminación de archivos: Gestionar el ciclo de vida de sus archivos aprendiendo a eliminarlos de forma segura con el método remove().


El proceso central para consultar datos en Supabase implica usar el método `select()`.

### 1. Consultar Tablas para un `id_user` Específico

Si quieres que tu programa consulte una tabla (por ejemplo, `planets` o cualquier tabla de tu aplicación) y filtre los datos basándose en el ID de usuario almacenado allí, debes usar el método `table()` seguido de `select()` y luego aplicar un filtro como `eq()`:

*   **Seleccionar datos:** Para obtener datos de una tabla, utilizas `supabase.table("nombre_de_la_tabla").select("*")`.
*   **Aplicar un filtro de igualdad (`eq`):** Para encontrar filas donde una columna (por ejemplo, `user_id_column`) sea igual a un valor específico (el `id_user` que buscas), encadenas el método `eq()`.

**Ejemplo de Consulta y Filtro:**
Para obtener registros donde la columna `user_id` es igual a un ID específico:

```python
response = (
    supabase.table("mi_tabla")
    .select("*") # Selecciona todas las columnas
    .eq("user_id", "el_id_del_usuario_a_buscar") # Filtra donde la columna 'user_id' es igual al valor
    .execute()
)
```
Recuerda que los filtros son cruciales y deben usarse después de `select()` en las consultas. También puedes usar otros filtros como `match()` si necesitas aplicar varias condiciones de igualdad a la vez.

### 2. Obtener el ID del Usuario Autenticado

A menudo, quieres que el programa consulte datos asociados al usuario que ha iniciado sesión actualmente. Para obtener el ID del usuario activo, puedes usar los métodos de autenticación:

#### A. Obtener el Objeto de Usuario Verificado (`get_user()`)

Este método es el más recomendado para obtener datos de usuario confiables, ya que verifica el JWT del token de acceso en el servidor:

```python
# Obtener el usuario logueado con la sesión existente
response = supabase.auth.get_user()
# El ID del usuario estará dentro del objeto 'user' de la respuesta.
```

#### B. Obtener las Reclamaciones del JWT (`get_claims()`)

Si el ID del usuario está incluido en el *access token* JWT (lo cual es común), puedes extraer las reclamaciones (claims) del JWT después de verificarlo. Este método es a menudo más rápido que `get_user()` porque usa un endpoint de Web Key Set que generalmente está cacheado:

```python
# Obtener las reclamaciones (claims) del objeto de usuario
response = supabase.auth.get_claims()
```

### 3. Acceso de Administrador a Cualquier ID de Usuario

Si tu programa se ejecuta en un **servidor de confianza** (trusted server) y necesita acceder al ID de cualquier usuario registrado en el esquema `auth.users`, debes usar el cliente de administración de autenticación (`supabase.auth.admin`).

**¡Advertencia Importante!** Cualquier método bajo el *namespace* `supabase.auth.admin` requiere una clave `service_role`. **Nunca** debes exponer tu clave `service_role` en el navegador.

Puedes obtener el ID de usuario (`auth.users.id`) de esta manera:

1.  **Inicializar el cliente de Admin:** Necesitas tu `service_role_key` en lugar de la clave pública.

    ```python
    from supabase import create_client
    from supabase.lib.client_options import ClientOptions
    
    # ... inicialización con service_role_key ...
    supabase = create_client(
        supabase_url,
        service_role_key, # Se usa la service_role_key aquí
        options=ClientOptions(auto_refresh_token=False, persist_session=False,)
    )
    admin_auth_client = supabase.auth.admin # Accede a la API de auth admin
    ```

2.  **Buscar un usuario por ID:** El método `get_user_by_id()` requiere el ID del usuario que se mapea a la columna `auth.users.id`.

    ```python
    user_id_a_buscar = "715ed5db-f090-4b8c-a067-640ecee36aa0"
    response = supabase.auth.admin.get_user_by_id(user_id_a_buscar)
    ```

3.  **Listar todos los usuarios:** También puedes listar todos los usuarios (por defecto 50 por página) para ver sus IDs si es necesario.

    ```python
    response = supabase.auth.admin.list_users()
    ```

Espero que esta guía te ayude a estructurar las consultas de tu programa. ¡Mucha suerte!