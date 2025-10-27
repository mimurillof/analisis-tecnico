"""
Supabase Manager - Gestión de archivos en Supabase Storage
Autor: AIDA
Fecha: 27 de octubre de 2025

Gestiona la conexión con Supabase y la subida de archivos
directamente desde memoria sin guardado local.
"""

import os
import io
import json
from typing import Dict, Optional, Tuple
from datetime import datetime
from supabase import create_client, Client
from supabase.lib.client_options import ClientOptions

# Cargar variables de entorno desde .env
from dotenv import load_dotenv
load_dotenv()


class SupabaseManager:
    """Gestor de archivos en Supabase Storage"""
    
    def __init__(self):
        """
        Inicializa el cliente de Supabase usando variables de entorno
        
        Variables requeridas:
        - SUPABASE_URL: URL del proyecto Supabase
        - SUPABASE_SERVICE_ROLE: Service role key (backend only)
        
        Variables opcionales:
        - SUPABASE_BUCKET_NAME: Nombre del bucket (default: portfolio-files)
        - ENABLE_SUPABASE_UPLOAD: Flag para activar/desactivar subida (default: true)
        """
        self.supabase_url = os.environ.get("SUPABASE_URL")
        self.supabase_service_role = os.environ.get("SUPABASE_SERVICE_ROLE")
        
        if not self.supabase_url or not self.supabase_service_role:
            raise ValueError(
                "❌ Variables de entorno SUPABASE_URL y SUPABASE_SERVICE_ROLE son requeridas. "
                "Asegúrate de configurarlas en Heroku o tu archivo .env"
            )
        
        # Configuración del bucket
        self.bucket_name = os.environ.get("SUPABASE_BUCKET_NAME", "portfolio-files")
        self.upload_enabled = os.environ.get("ENABLE_SUPABASE_UPLOAD", "true").lower() == "true"
        
        # Inicializar cliente con service_role_key
        # IMPORTANTE: Esto solo debe usarse en backend (nunca exponer en navegador)
        try:
            self.client: Client = create_client(
                self.supabase_url,
                self.supabase_service_role,
                options=ClientOptions(
                    auto_refresh_token=False,
                    persist_session=False
                )
            )
            print(f"✅ Cliente Supabase inicializado correctamente")
            print(f"   Bucket: {self.bucket_name}")
            print(f"   Upload enabled: {self.upload_enabled}")
        except Exception as e:
            raise ConnectionError(f"❌ Error conectando con Supabase: {e}")
    
    def upload_file_from_memory(
        self, 
        user_id: str, 
        filename: str, 
        content: bytes,
        content_type: str = "application/json"
    ) -> Tuple[bool, str]:
        """
        Sube un archivo desde memoria directamente a Supabase Storage
        
        Args:
            user_id: ID del usuario (se usa como carpeta)
            filename: Nombre del archivo (ej: portfolio_analisis.json)
            content: Contenido del archivo en bytes
            content_type: Tipo MIME del archivo
        
        Returns:
            Tupla (éxito: bool, mensaje: str)
        """
        # Verificar si la subida está habilitada
        if not self.upload_enabled:
            return True, f"⚠️ Upload deshabilitado - {filename} NO subido (ENABLE_SUPABASE_UPLOAD=false)"
        
        try:
            # Construir ruta: {user_id}/{filename}
            file_path = f"{user_id}/{filename}"
            
            # Subir con upsert=true (crear si no existe, actualizar si existe)
            # El método upload de Supabase acepta bytes directamente
            response = self.client.storage.from_(self.bucket_name).upload(
                path=file_path,
                file=content,  # Pasar bytes directamente
                file_options={
                    "content-type": content_type,
                    "cache-control": "3600",
                    "upsert": "true"  # Clave: permite crear o actualizar
                }
            )
            
            return True, f"✅ {filename} subido correctamente para usuario {user_id}"
            
        except Exception as e:
            error_msg = f"❌ Error subiendo {filename} para usuario {user_id}: {str(e)}"
            return False, error_msg
    
    def upload_analysis_files(
        self,
        user_id: str,
        portfolio_json: Dict,
        portfolio_md: str,
        mercado_json: Dict,
        mercado_md: str
    ) -> Dict[str, Tuple[bool, str]]:
        """
        Sube los 4 archivos de análisis para un usuario
        
        Args:
            user_id: ID del usuario
            portfolio_json: Diccionario con análisis del portfolio
            portfolio_md: Contenido markdown del informe de portfolio
            mercado_json: Diccionario con análisis del mercado
            mercado_md: Contenido markdown del informe de mercado
        
        Returns:
            Diccionario con resultados de cada archivo
        """
        results = {}
        
        # Convertir JSON a bytes
        portfolio_json_bytes = json.dumps(portfolio_json, indent=2, ensure_ascii=False).encode('utf-8')
        mercado_json_bytes = json.dumps(mercado_json, indent=2, ensure_ascii=False).encode('utf-8')
        
        # Convertir MD a bytes
        portfolio_md_bytes = portfolio_md.encode('utf-8')
        mercado_md_bytes = mercado_md.encode('utf-8')
        
        # Subir cada archivo
        results['portfolio_analisis.json'] = self.upload_file_from_memory(
            user_id, 
            'portfolio_analisis.json', 
            portfolio_json_bytes,
            'application/json'
        )
        
        results['portfolio_informe.md'] = self.upload_file_from_memory(
            user_id,
            'portfolio_informe.md',
            portfolio_md_bytes,
            'text/markdown'
        )
        
        results['mercado_analisis.json'] = self.upload_file_from_memory(
            user_id,
            'mercado_analisis.json',
            mercado_json_bytes,
            'application/json'
        )
        
        results['mercado_informe.md'] = self.upload_file_from_memory(
            user_id,
            'mercado_informe.md',
            mercado_md_bytes,
            'text/markdown'
        )
        
        return results
    
    def get_file_url(self, user_id: str, filename: str) -> Optional[str]:
        """
        Obtiene la URL pública de un archivo (si el bucket es público)
        o genera una URL firmada (si el bucket es privado)
        
        Args:
            user_id: ID del usuario
            filename: Nombre del archivo
        
        Returns:
            URL del archivo o None si hay error
        """
        try:
            file_path = f"{user_id}/{filename}"
            
            # Obtener URL pública (solo funciona si bucket es público)
            public_url = self.client.storage.from_(self.bucket_name).get_public_url(file_path)
            
            return public_url
            
        except Exception as e:
            print(f"⚠️ Error obteniendo URL para {filename}: {e}")
            return None
    
    def create_signed_url(
        self, 
        user_id: str, 
        filename: str, 
        expires_in: int = 3600
    ) -> Optional[str]:
        """
        Crea una URL firmada temporal para acceso privado
        
        Args:
            user_id: ID del usuario
            filename: Nombre del archivo
            expires_in: Tiempo de expiración en segundos (default: 1 hora)
        
        Returns:
            URL firmada o None si hay error
        """
        try:
            file_path = f"{user_id}/{filename}"
            
            # Crear URL firmada
            response = self.client.storage.from_(self.bucket_name).create_signed_url(
                file_path,
                expires_in
            )
            
            return response.get('signedURL')
            
        except Exception as e:
            print(f"⚠️ Error creando URL firmada para {filename}: {e}")
            return None
    
    def verify_bucket_exists(self) -> bool:
        """
        Verifica que el bucket 'portfolio-files' existe
        
        Returns:
            True si el bucket existe
        """
        try:
            buckets = self.client.storage.list_buckets()
            bucket_names = [b.name for b in buckets]
            
            if self.bucket_name in bucket_names:
                print(f"✅ Bucket '{self.bucket_name}' encontrado")
                return True
            else:
                print(f"⚠️ Bucket '{self.bucket_name}' NO encontrado. Créalo en Supabase Dashboard.")
                print(f"   Buckets disponibles: {bucket_names}")
                return False
                
        except Exception as e:
            print(f"❌ Error verificando buckets: {e}")
            return False
    
    def ensure_user_folder(self, user_id: str) -> Tuple[bool, str]:
        """
        Asegura que la carpeta del usuario existe en el bucket
        (Supabase crea carpetas automáticamente al subir archivos)
        
        Args:
            user_id: ID del usuario
        
        Returns:
            Tupla (éxito, mensaje)
        """
        # En Supabase Storage, las carpetas se crean automáticamente
        # al subir el primer archivo con ese prefijo
        return True, f"Carpeta para usuario {user_id} será creada al subir primer archivo"


def test_connection():
    """Función de prueba para verificar la conexión con Supabase"""
    try:
        print("\n" + "="*80)
        print("🔍 PRUEBA DE CONEXIÓN CON SUPABASE")
        print("="*80 + "\n")
        
        # Inicializar manager
        manager = SupabaseManager()
        
        # Verificar bucket
        manager.verify_bucket_exists()
        
        # Crear archivo de prueba
        print("\n📝 Creando archivo de prueba...")
        test_data = {
            "test": True,
            "timestamp": datetime.now().isoformat(),
            "message": "Conexión exitosa"
        }
        
        success, msg = manager.upload_file_from_memory(
            user_id="test_user",
            filename="test_connection.json",
            content=json.dumps(test_data).encode('utf-8'),
            content_type="application/json"
        )
        
        print(msg)
        
        if success:
            print("\n✅ ¡PRUEBA EXITOSA! Supabase está configurado correctamente.")
        else:
            print("\n❌ Prueba fallida. Revisa la configuración de Supabase.")
        
        print("\n" + "="*80 + "\n")
        
    except Exception as e:
        print(f"\n❌ ERROR EN PRUEBA: {e}\n")
        print("Asegúrate de tener configuradas las variables SUPABASE_URL y SUPABASE_KEY")


if __name__ == "__main__":
    test_connection()

