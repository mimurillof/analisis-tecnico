"""
User Manager - Gestión de usuarios desde Supabase
Autor: AIDA
Fecha: 27 de octubre de 2025

Consulta usuarios de la base de datos y sus configuraciones de portfolio
"""

import os
from typing import List, Dict, Optional
from supabase import create_client, Client
from supabase.lib.client_options import ClientOptions

# Cargar variables de entorno desde .env
from dotenv import load_dotenv
load_dotenv()


class UserManager:
    """Gestor de usuarios y sus configuraciones"""
    
    def __init__(self):
        """
        Inicializa el cliente de Supabase para consultas a la BD
        
        Variables requeridas:
        - SUPABASE_URL: URL del proyecto Supabase
        - SUPABASE_SERVICE_ROLE: Service role key (backend only)
        """
        self.supabase_url = os.environ.get("SUPABASE_URL")
        self.supabase_service_role = os.environ.get("SUPABASE_SERVICE_ROLE")
        
        if not self.supabase_url or not self.supabase_service_role:
            raise ValueError(
                "❌ Variables de entorno SUPABASE_URL y SUPABASE_SERVICE_ROLE son requeridas"
            )
        
        try:
            self.client: Client = create_client(
                self.supabase_url,
                self.supabase_service_role,
                options=ClientOptions(
                    auto_refresh_token=False,
                    persist_session=False
                )
            )
            print("✅ Cliente Supabase para usuarios inicializado")
        except Exception as e:
            raise ConnectionError(f"❌ Error conectando con Supabase: {e}")
    
    def get_all_active_users(self) -> List[Dict]:
        """
        Obtiene todos los usuarios de la base de datos
        
        Estructura de tu BD:
        - Tabla: users
        - Columnas: user_id (uuid), email, first_name, last_name, created_at, etc.
        
        Returns:
            Lista de diccionarios con información de usuarios
        """
        try:
            # Consultar tabla 'users' (estructura real de tu BD)
            response = (
                self.client
                .table("users")
                .select("*")
                .execute()
            )
            
            users = response.data
            
            if not users:
                print("⚠️ No se encontraron usuarios en la tabla 'users'")
                return []
            
            print(f"✅ {len(users)} usuarios encontrados")
            return users
            
        except Exception as e:
            print(f"❌ Error consultando usuarios: {e}")
            return []
    
    def get_user_by_id(self, user_id: str) -> Optional[Dict]:
        """
        Obtiene información de un usuario específico por su ID
        
        Args:
            user_id: ID del usuario (UUID o string)
        
        Returns:
            Diccionario con información del usuario o None si no existe
        """
        try:
            response = (
                self.client
                .table("users")
                .select("*")
                .eq("user_id", user_id)  # Columna correcta: user_id
                .single()
                .execute()
            )
            
            return response.data
            
        except Exception as e:
            print(f"⚠️ Usuario {user_id} no encontrado: {e}")
            return None
    
    def get_user_portfolio_config(self, user_id: str) -> Dict:
        """
        Obtiene la configuración del portfolio de un usuario desde tu BD real
        
        Estructura:
        - Tabla portfolios: portfolio_id, user_id, portfolio_name, description
        - Tabla assets: asset_id, portfolio_id, asset_symbol, quantity, acquisition_price
        
        Args:
            user_id: ID del usuario
        
        Returns:
            Diccionario con:
            - portfolio_tickers: Lista de tickers del portfolio del usuario
            - scan_sp500: Si debe escanear S&P 500
            - scan_crypto: Si debe escanear crypto
            - max_candidates: Máximo de candidatos del mercado
        """
        try:
            # 1. Obtener portfolios del usuario
            portfolios_response = (
                self.client
                .table("portfolios")
                .select("portfolio_id, portfolio_name")
                .eq("user_id", user_id)
                .execute()
            )
            
            if not portfolios_response.data:
                print(f"⚠️ No se encontraron portfolios para usuario {user_id}")
                return self._get_default_config()
            
            # 2. Obtener todos los assets de todos los portfolios del usuario
            portfolio_ids = [p['portfolio_id'] for p in portfolios_response.data]
            
            all_tickers = []
            for portfolio_id in portfolio_ids:
                assets_response = (
                    self.client
                    .table("assets")
                    .select("asset_symbol")
                    .eq("portfolio_id", portfolio_id)
                    .execute()
                )
                
                # Extraer símbolos y agregarlos
                tickers = [asset['asset_symbol'] for asset in assets_response.data]
                all_tickers.extend(tickers)
            
            # Eliminar duplicados
            unique_tickers = list(set(all_tickers))
            
            if not unique_tickers:
                print(f"⚠️ No se encontraron assets para usuario {user_id}")
                return self._get_default_config()
            
            print(f"✅ Portfolio de usuario {user_id[:8]}...: {unique_tickers}")
            
            return {
                "portfolio_tickers": unique_tickers,
                "scan_sp500": True,
                "scan_crypto": True,
                "max_candidates": 10
            }
            
        except Exception as e:
            print(f"⚠️ Error obteniendo portfolio para usuario {user_id}: {e}")
            return self._get_default_config()
    
    def _get_default_config(self) -> Dict:
        """Retorna configuración por defecto"""
        return {
            "portfolio_tickers": [
                'PAXG-USD',  # Oro digital
                '^GSPC',     # S&P 500
                'BTC-USD',   # Bitcoin
                'ETH-USD',   # Ethereum
                'BNB-USD',   # Binance Coin
                'SOL-USD'    # Solana
            ],
            "scan_sp500": True,
            "scan_crypto": True,
            "max_candidates": 10
        }
    
    def get_users_batch(self, batch_size: int = 10, offset: int = 0) -> List[Dict]:
        """
        Obtiene usuarios en batches para procesamiento optimizado
        Útil para sistemas con muchos usuarios
        
        Args:
            batch_size: Número de usuarios por batch
            offset: Offset para paginación
        
        Returns:
            Lista de usuarios
        """
        try:
            response = (
                self.client
                .table("users")
                .select("*")
                .range(offset, offset + batch_size - 1)
                .execute()
            )
            
            return response.data
            
        except Exception as e:
            print(f"❌ Error obteniendo batch de usuarios: {e}")
            return []
    
    def count_active_users(self) -> int:
        """
        Cuenta el número total de usuarios
        
        Returns:
            Número de usuarios
        """
        try:
            response = (
                self.client
                .table("users")
                .select("*", count="exact")
                .execute()
            )
            
            return response.count or 0
            
        except Exception as e:
            print(f"⚠️ Error contando usuarios: {e}")
            return 0


def test_user_queries():
    """Función de prueba para verificar consultas de usuarios"""
    try:
        print("\n" + "="*80)
        print("🔍 PRUEBA DE CONSULTAS DE USUARIOS")
        print("="*80 + "\n")
        
        # Inicializar manager
        manager = UserManager()
        
        # Contar usuarios
        print("📊 Contando usuarios activos...")
        count = manager.count_active_users()
        print(f"   Total: {count} usuarios activos\n")
        
        # Obtener usuarios
        print("👥 Obteniendo usuarios...")
        users = manager.get_all_active_users()
        
        if users:
            print(f"\n✅ Se encontraron {len(users)} usuarios:")
            for i, user in enumerate(users[:5], 1):  # Mostrar solo primeros 5
                user_id = user.get('id') or user.get('id_user') or user.get('user_id')
                email = user.get('email', 'N/A')
                print(f"   {i}. ID: {user_id[:8]}... | Email: {email}")
            
            if len(users) > 5:
                print(f"   ... y {len(users) - 5} usuarios más")
            
            # Probar configuración de primer usuario
            if users:
                first_user = users[0]
                user_id = first_user.get('id') or first_user.get('id_user')
                
                print(f"\n📋 Obteniendo configuración del primer usuario...")
                config = manager.get_user_portfolio_config(user_id)
                print(f"   Portfolio tickers: {config['portfolio_tickers']}")
                print(f"   Escanear S&P 500: {config['scan_sp500']}")
                print(f"   Escanear Crypto: {config['scan_crypto']}")
        else:
            print("⚠️ No se encontraron usuarios")
            print("\n💡 SUGERENCIA: Crea usuarios de prueba en tu base de datos:")
            print("   1. Ve a Supabase Dashboard > Table Editor")
            print("   2. Crea tabla 'profiles' si no existe")
            print("   3. Agrega columnas: id (uuid), email (text), active (boolean)")
            print("   4. Inserta algunos usuarios de prueba")
        
        print("\n" + "="*80 + "\n")
        
    except Exception as e:
        print(f"\n❌ ERROR EN PRUEBA: {e}\n")


if __name__ == "__main__":
    test_user_queries()

