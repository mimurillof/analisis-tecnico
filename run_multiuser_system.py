"""
Sistema Multi-Usuario con Supabase v1.0
Ejecuta análisis técnico para múltiples usuarios y sube resultados a Supabase
Optimizado para Heroku Eco con procesamiento paralelo limitado

Autor: AIDA
Fecha: 27 de octubre de 2025
"""

import os
import sys
import time
import json
import traceback
from functools import lru_cache
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed

import schedule
import pytz
import pandas_market_calendars as mcal
from dotenv import load_dotenv


load_dotenv()

# Configurar encoding UTF-8 para el stdout (Windows compatibility)
NY_TZ = pytz.timezone('America/New_York')


@lru_cache(maxsize=1)
def _get_market_calendar():
    """Return cached NYSE calendar instance."""
    return mcal.get_calendar('XNYS')


def get_market_day_status(now: Optional[datetime] = None) -> Dict[str, object]:
    """Return structured information about today's NYSE trading session."""
    if now is None:
        now = datetime.now(NY_TZ)
    else:
        now = now.astimezone(NY_TZ)

    cal = _get_market_calendar()
    schedule = cal.schedule(start_date=now.date(), end_date=now.date())

    status: Dict[str, object] = {
        'date': now.date(),
        'weekday': now.strftime('%A'),
        'now': now,
        'is_trading_day': False,
        'in_session': False,
        'has_closed': False,
        'market_open': None,
        'market_close': None,
        'reason': 'Mercado cerrado (sin sesión programada)'
    }

    if schedule.empty:
        return status

    session = schedule.iloc[0]
    market_open = session['market_open'].tz_convert(NY_TZ)
    market_close = session['market_close'].tz_convert(NY_TZ)

    status.update({
        'is_trading_day': True,
        'market_open': market_open,
        'market_close': market_close,
        'in_session': market_open <= now <= market_close,
        'has_closed': now >= market_close,
    })

    if now < market_open:
        status['reason'] = (
            f"Mercado aún no abre (abre a las {market_open.strftime('%H:%M %Z')})"
        )
    elif now > market_close:
        status['reason'] = (
            f"Mercado ya cerró (cerró a las {market_close.strftime('%H:%M %Z')})"
        )
    else:
        status['reason'] = "Mercado en sesión"

    return status


def is_market_day(
    now: Optional[datetime] = None,
    *,
    require_session: bool = False,
    require_close: bool = False
) -> bool:
    """Determine if NYSE is considered open for processing given the constraints."""
    status = get_market_day_status(now)

    if not status['is_trading_day']:
        return False

    if require_session and not status['in_session']:
        return False

    if require_close and not status['has_closed']:
        return False

    return True
if sys.platform == 'win32':
    import codecs
    if hasattr(sys.stdout, 'buffer'):
        sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    if hasattr(sys.stderr, 'buffer'):
        sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

# Importar módulos del sistema
from svga_system import SVGASystem
from market_radar import MarketRadar
from tactical_radars import TacticalRadarSystem
from user_manager import UserManager
from supabase_manager import SupabaseManager


class MultiUserAnalysisSystem:
    """Sistema de análisis técnico multi-usuario con Supabase"""
    
    def __init__(self, max_workers: int = 2):
        """
        Inicializa el sistema multi-usuario
        
        Args:
            max_workers: Número máximo de workers en paralelo
                        - Para Heroku Eco: 1-2 workers recomendados
                        - Para plan superior: 3-5 workers
        """
        self.max_workers = max_workers
        self.user_manager = UserManager()
        self.supabase_manager = SupabaseManager()
        
        # Cache para resultados de radar (evitar escanear múltiples veces)
        self.radar_cache = {
            'sp500': {'candidates': [], 'timestamp': None},
            'crypto': {'candidates': [], 'timestamp': None}
        }
        
        print(f"✅ Sistema Multi-Usuario inicializado (max_workers={max_workers})")
    
    def run_radar_scan(
        self, 
        scan_sp500: bool = True, 
        scan_crypto: bool = True,
        max_candidates: int = 10
    ) -> Dict:
        """
        Ejecuta escaneo de radar UNA SOLA VEZ para todos los usuarios
        (Optimización: evita escanear el mercado múltiples veces)
        
        Args:
            scan_sp500: Si debe escanear S&P 500
            scan_crypto: Si debe escanear crypto
            max_candidates: Máximo de candidatos por radar
        
        Returns:
            Diccionario con candidatos de ambos radares
        """
        print("\n" + "="*80)
        print("📡 ESCANEO DE RADARES (COMPARTIDO PARA TODOS LOS USUARIOS)")
        print("="*80 + "\n")
        
        sp500_candidates = []
        crypto_candidates = []
        
        # === RADAR S&P 500 ===
        if scan_sp500:
            print("📡 RADAR S&P 500...")
            
            radar_temp = MarketRadar(universe="sp500")
            radar_temp.load_universe()
            sp500_universe = radar_temp.tickers
            
            tactical_sp500 = TacticalRadarSystem(benchmark="^GSPC")
            sp500_candidates, sp500_full_metrics, sp500_radars_used = tactical_sp500.run_tactical_scan(
                tickers=sp500_universe,
                period="6mo",
                max_candidates=max_candidates
            )
            
            print(f"✅ S&P 500: {len(sp500_candidates)} candidatos identificados\n")
            
            # Guardar en cache
            self.radar_cache['sp500'] = {
                'candidates': sp500_candidates,
                'timestamp': datetime.now().isoformat()
            }
        
        # === RADAR CRYPTO ===
        if scan_crypto:
            print("📡 RADAR CRYPTO...")
            
            radar_temp_crypto = MarketRadar(universe="crypto30")
            radar_temp_crypto.load_universe()
            crypto_universe = radar_temp_crypto.tickers
            
            tactical_crypto = TacticalRadarSystem(benchmark="BTC-USD")
            crypto_candidates, crypto_full_metrics, crypto_radars_used = tactical_crypto.run_tactical_scan(
                tickers=crypto_universe,
                period="3mo",
                max_candidates=max_candidates
            )
            
            print(f"✅ Crypto: {len(crypto_candidates)} candidatos identificados\n")
            
            # Guardar en cache
            self.radar_cache['crypto'] = {
                'candidates': crypto_candidates,
                'timestamp': datetime.now().isoformat()
            }
        
        print("="*80)
        print(f"✅ RADARES COMPLETADOS - {len(sp500_candidates) + len(crypto_candidates)} candidatos totales")
        print("="*80 + "\n")
        
        return {
            'sp500_candidates': sp500_candidates,
            'crypto_candidates': crypto_candidates,
            'all_market_candidates': sp500_candidates + crypto_candidates
        }
    
    def analyze_user(self, user: Dict, market_candidates: List[str]) -> Dict:
        """
        Analiza el portfolio de un usuario individual
        
        Args:
            user: Diccionario con datos del usuario
            market_candidates: Lista de candidatos del mercado (pre-escaneados)
        
        Returns:
            Diccionario con resultados del análisis
        """
        # Obtener user_id de tu estructura real (columna: user_id)
        user_id = user.get('user_id')
        email = user.get('email', f'user_{user_id[:8] if user_id else "unknown"}')
        first_name = user.get('first_name', '')
        last_name = user.get('last_name', '')
        
        full_name = f"{first_name} {last_name}".strip() if first_name or last_name else email
        
        print(f"\n{'='*80}")
        print(f"👤 ANALIZANDO USUARIO: {full_name} ({email})")
        print(f"   ID: {user_id[:8]}...")
        print(f"{'='*80}\n")
        
        try:
            # Obtener configuración del portfolio del usuario
            config = self.user_manager.get_user_portfolio_config(user_id)
            portfolio_tickers = config['portfolio_tickers']
            
            print(f"📊 Portfolio: {portfolio_tickers}")
            print(f"🌍 Mercado: {len(market_candidates)} candidatos\n")
            
            # Crear sistema SVGA para este usuario
            svga_system = SVGASystem(
                portfolio_tickers=portfolio_tickers,
                market_tickers=market_candidates
            )
            
            # Ejecutar análisis EN MEMORIA (sin archivos locales)
            results = svga_system.run_in_memory()
            
            # Subir a Supabase
            print(f"\n📤 SUBIENDO RESULTADOS A SUPABASE...")
            
            upload_results = self.supabase_manager.upload_analysis_files(
                user_id=user_id,
                portfolio_json=results['portfolio_json'],
                portfolio_md=results['portfolio_md'],
                mercado_json=results['mercado_json'],
                mercado_md=results['mercado_md']
            )
            
            # Mostrar resultados de subida
            success_count = sum(1 for success, _ in upload_results.values() if success)
            print(f"\n✅ {success_count}/4 archivos subidos correctamente para {email}")
            
            for filename, (success, msg) in upload_results.items():
                status = "✅" if success else "❌"
                print(f"   {status} {filename}")
            
            return {
                'user_id': user_id,
                'email': email,
                'success': success_count == 4,
                'upload_results': upload_results,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            error_msg = f"❌ Error analizando usuario {email}: {str(e)}"
            print(error_msg)
            traceback.print_exc()
            
            return {
                'user_id': user_id,
                'email': email,
                'success': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def run_sequential(self, users: List[Dict], market_candidates: List[str]) -> List[Dict]:
        """
        Procesa usuarios SECUENCIALMENTE (modo seguro para recursos limitados)
        
        Args:
            users: Lista de usuarios a procesar
            market_candidates: Candidatos del mercado (pre-escaneados)
        
        Returns:
            Lista con resultados de cada usuario
        """
        print(f"\n🔄 MODO SECUENCIAL - Procesando {len(users)} usuarios uno por uno...")
        
        results = []
        
        for i, user in enumerate(users, 1):
            print(f"\n{'='*80}")
            print(f"USUARIO {i}/{len(users)}")
            print(f"{'='*80}")
            
            result = self.analyze_user(user, market_candidates)
            results.append(result)
            
            # Pequeña pausa entre usuarios para no sobrecargar APIs
            if i < len(users):
                time.sleep(2)
        
        return results
    
    def run_parallel(self, users: List[Dict], market_candidates: List[str]) -> List[Dict]:
        """
        Procesa usuarios EN PARALELO con ThreadPoolExecutor
        (Usar solo si tienes recursos suficientes - no recomendado para Heroku Eco)
        
        Args:
            users: Lista de usuarios a procesar
            market_candidates: Candidatos del mercado (pre-escaneados)
        
        Returns:
            Lista con resultados de cada usuario
        """
        print(f"\n⚡ MODO PARALELO - Procesando {len(users)} usuarios con {self.max_workers} workers...")
        
        results = []
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Enviar tareas
            future_to_user = {
                executor.submit(self.analyze_user, user, market_candidates): user
                for user in users
            }
            
            # Procesar resultados conforme se completan
            for future in as_completed(future_to_user):
                user = future_to_user[future]
                try:
                    result = future.result()
                    results.append(result)
                except Exception as e:
                    user_id = user.get('id', 'unknown')
                    print(f"❌ Error procesando usuario {user_id}: {e}")
                    results.append({
                        'user_id': user_id,
                        'success': False,
                        'error': str(e)
                    })
        
        return results
    
    def run_full_cycle(self, parallel: bool = False) -> Dict:
        """
        Ejecuta ciclo completo: radar + análisis de todos los usuarios
        
        Args:
            parallel: Si True, procesa usuarios en paralelo
                     Si False, procesa secuencialmente (recomendado para Heroku Eco)
        
        Returns:
            Diccionario con resumen de ejecución
        """
        cycle_start = datetime.now()
        
        print("\n" + "="*80)
        print("🚀 SISTEMA MULTI-USUARIO - CICLO COMPLETO")
        print("="*80)
        print(f"Inicio: {cycle_start.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Modo: {'PARALELO' if parallel else 'SECUENCIAL'}")
        print("="*80 + "\n")
        
        try:
            # PASO 1: Obtener usuarios activos
            print("👥 PASO 1: Obteniendo usuarios activos...\n")
            users = self.user_manager.get_all_active_users()
            
            if not users:
                print("⚠️ No se encontraron usuarios activos. Ciclo abortado.")
                return {
                    'success': False,
                    'message': 'No hay usuarios activos',
                    'users_processed': 0
                }
            
            print(f"✅ {len(users)} usuarios encontrados\n")
            
            # PASO 2: Escanear mercado (UNA SOLA VEZ)
            print("📡 PASO 2: Escaneando mercado...\n")
            radar_results = self.run_radar_scan(
                scan_sp500=True,
                scan_crypto=True,
                max_candidates=10
            )
            
            market_candidates = radar_results['all_market_candidates']
            
            # PASO 3: Analizar usuarios (secuencial o paralelo)
            print(f"\n🔬 PASO 3: Analizando portfolios de usuarios...\n")
            
            if parallel and self.max_workers > 1:
                analysis_results = self.run_parallel(users, market_candidates)
            else:
                analysis_results = self.run_sequential(users, market_candidates)
            
            # RESUMEN FINAL
            cycle_end = datetime.now()
            duration = (cycle_end - cycle_start).total_seconds() / 60
            
            successful = sum(1 for r in analysis_results if r.get('success', False))
            failed = len(analysis_results) - successful
            
            print("\n" + "="*80)
            print("✅ CICLO COMPLETADO")
            print("="*80)
            print(f"Duración: {duration:.2f} minutos")
            print(f"Usuarios procesados: {len(analysis_results)}")
            print(f"  ✅ Exitosos: {successful}")
            print(f"  ❌ Fallidos: {failed}")
            print("="*80 + "\n")
            
            return {
                'success': True,
                'users_processed': len(analysis_results),
                'successful': successful,
                'failed': failed,
                'duration_minutes': duration,
                'market_candidates': len(market_candidates),
                'results': analysis_results,
                'timestamp': cycle_end.isoformat()
            }
            
        except Exception as e:
            print(f"\n❌ ERROR EN CICLO: {e}")
            traceback.print_exc()
            
            return {
                'success': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
def main():
    """Función principal - Ejecución continua con detección de horario de mercado"""
    
    # ===== CONFIGURACIÓN =====
    # Para Heroku Eco: usar modo secuencial (max_workers=1)
    # Para plan superior: usar max_workers=2-3
    MAX_WORKERS = int(os.environ.get('MAX_WORKERS', '1'))
    PARALLEL_MODE = MAX_WORKERS > 1
    
    # Intervalo entre ejecuciones (en minutos) - DURANTE HORARIO DE MERCADO
    INTERVAL_MINUTES = int(os.environ.get('SVGA_INTERVAL_MINUTES', '15'))
    
    # Intervalo cuando el mercado está cerrado (verificar cada hora)
    CLOSED_CHECK_MINUTES = int(os.environ.get('CLOSED_CHECK_MINUTES', '60'))
    
    # Intervalo cuando el mercado está cerrado (verificar cada hora)
    CLOSED_CHECK_MINUTES = int(os.environ.get('CLOSED_CHECK_MINUTES', '60'))
    
    # ===== INICIALIZAR SISTEMA =====
    print("🚀 Iniciando Sistema Multi-Usuario con Supabase...")
    print(f"   - Max Workers: {MAX_WORKERS}")
    print(f"   - Modo: {'PARALELO' if PARALLEL_MODE else 'SECUENCIAL'}")
    print(f"   - Intervalo durante horario de mercado: {INTERVAL_MINUTES} minutos")
    print(f"   - Intervalo fuera de horario: {CLOSED_CHECK_MINUTES} minutos")
    print()
    
    try:
        system = MultiUserAnalysisSystem(max_workers=MAX_WORKERS)
    except Exception as e:
        print(f"❌ Error inicializando sistema: {e}")
        print("   Verifica que las variables SUPABASE_URL y SUPABASE_KEY estén configuradas")
        return
    
    # ===== MODO DE EJECUCIÓN =====
    RUN_ONCE = os.environ.get('RUN_ONCE', 'false').lower() == 'true'
    
    if RUN_ONCE:
        # MODO: Ejecutar una sola vez (ignora horarios)
        print("🔄 MODO: Ejecución única\n")
        system.run_full_cycle(parallel=PARALLEL_MODE)
        print("\n✅ Ejecución única completada. Finalizando...")
        return
    
    # MODO: Ejecución continua adaptativa (cada 15 min en horario, cada hora fuera)
    print("🔄 MODO: Ejecución continua adaptativa")
    print("   📊 Durante sesión: ciclo cada 15 minutos")
    print("   🌙 Fuera de sesión: verificación cada hora\n")
    
    ciclo = 1
    
    try:
        while True:
            now = datetime.now(NY_TZ)
            status = get_market_day_status(now)
            
            print("\n" + "="*80)
            print(f"🔁 CICLO #{ciclo} - {now.strftime('%Y-%m-%d %H:%M:%S %Z')}")
            print("="*80)
            print(f"📅 {status['weekday']}, {status['date']}")
            print(f"📊 Estado: {status['reason']}")
            
            if status['is_trading_day']:
                market_open = status.get('market_open')
                market_close = status.get('market_close')
                market_open_str = market_open.strftime('%H:%M') if isinstance(market_open, datetime) else 'N/A'
                market_close_str = market_close.strftime('%H:%M') if isinstance(market_close, datetime) else 'N/A'
                print(f"⏰ Sesión: {market_open_str} - {market_close_str} ET")
            
            print("="*80 + "\n")
            
            # Decidir si ejecutar según el estado del mercado
            should_run = False
            wait_minutes = CLOSED_CHECK_MINUTES
            
            if not status['is_trading_day']:
                # Fin de semana o feriado
                print("⚠️ Mercado cerrado (fin de semana/feriado)")
                print(f"   ⏱️ Próxima verificación en {CLOSED_CHECK_MINUTES} minutos\n")
                wait_minutes = CLOSED_CHECK_MINUTES
                
            elif status['in_session']:
                # Mercado ABIERTO - ejecutar cada 15 minutos
                print("� MERCADO ABIERTO - Ejecutando análisis...\n")
                should_run = True
                wait_minutes = INTERVAL_MINUTES
                
            elif status['has_closed']:
                # Mercado ya cerró hoy - ejecutar una vez después del cierre
                print("🔵 Mercado cerrado - Ejecutando análisis post-cierre...\n")
                should_run = True
                wait_minutes = CLOSED_CHECK_MINUTES  # Luego esperar hasta mañana
                
            else:
                # Mercado aún no abre
                next_open = status['market_open']
                if isinstance(next_open, datetime):
                    print(f"⏰ Mercado abre a las {next_open.strftime('%H:%M %Z')}")
                print(f"   ⏱️ Próxima verificación en {CLOSED_CHECK_MINUTES} minutos\n")
                wait_minutes = CLOSED_CHECK_MINUTES
            
            # Ejecutar ciclo si corresponde
            if should_run:
                try:
                    cycle_result = system.run_full_cycle(parallel=PARALLEL_MODE)
                    
                    if cycle_result['success']:
                        print(f"\n✅ Ciclo #{ciclo} completado exitosamente")
                        print(f"   📊 Usuarios procesados: {cycle_result.get('users_processed', 0)}")
                        print(f"   ⏱️ Duración: {cycle_result.get('duration_minutes', 0):.2f} minutos")
                    else:
                        print(f"\n⚠️ Ciclo #{ciclo} completado con errores")
                    
                except Exception as e:
                    print(f"\n❌ Error en ciclo #{ciclo}: {e}")
                    traceback.print_exc()
            
            ciclo += 1
            
            # Esperar según el estado del mercado
            wait_seconds = wait_minutes * 60
            print(f"\n⏱️ Esperando {wait_minutes} minutos hasta próximo ciclo...")
            print(f"   (Presiona Ctrl+C para detener)\n")
            
            time.sleep(wait_seconds)
            
    except KeyboardInterrupt:
        print("\n🛑 Ejecución detenida por el usuario. ¡Hasta pronto!")


if __name__ == "__main__":
    main()

