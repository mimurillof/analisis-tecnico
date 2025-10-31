"""
Sistema Multi-Usuario con Supabase v1.0
Ejecuta análisis técnico para múltiples usuarios y sube resultados a Supabase
Optimizado para Heroku Eco con procesamiento paralelo limitado

Autor: AIDA
Fecha: 27 de octubre de 2025
"""

import sys
import os
import time
import traceback
from datetime import datetime, timedelta
from typing import Dict, List
from concurrent.futures import ThreadPoolExecutor, as_completed
import json
import schedule
import pytz

# Cargar variables de entorno desde .env (debe ser lo primero)
from dotenv import load_dotenv
load_dotenv()

# Configurar encoding UTF-8 para el stdout (Windows compatibility)
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


def is_market_day() -> bool:
    """
    Verifica si hoy es un día hábil del mercado (NYSE/NASDAQ)
    
    Returns:
        True si es día hábil, False en caso contrario
    """
    now_ny = datetime.now(pytz.timezone('America/New_York'))
    weekday = now_ny.weekday()  # 0=Lunes, 6=Domingo
    
    # El mercado está cerrado los sábados (5) y domingos (6)
    if weekday >= 5:
        return False
    
    # Verificar si es después del cierre del mercado (4:00 PM ET)
    # Si es antes de las 4 PM, aún no tenemos datos del día completo
    if now_ny.hour < 16:
        return False
    
    # Por ahora, asumimos que si es día de semana y después de las 4 PM, es día hábil
    # Nota: No verifica feriados, pero el sistema puede fallar graciosamente si no hay datos
    return True


def main():
    """Función principal - Ejecución programada con schedule o continua"""
    
    # ===== CONFIGURACIÓN =====
    # Para Heroku Eco: usar modo secuencial (max_workers=1)
    # Para plan superior: usar max_workers=2-3
    MAX_WORKERS = int(os.environ.get('MAX_WORKERS', '1'))
    PARALLEL_MODE = MAX_WORKERS > 1
    
    # Intervalo entre ejecuciones (en minutos) - para modo continuo
    INTERVAL_MINUTES = int(os.environ.get('SVGA_INTERVAL_MINUTES', '15'))
    
    # Configuración de schedule
    USE_SCHEDULE = os.environ.get('USE_SCHEDULE', 'true').lower() == 'true'
    SCHEDULE_TIME = os.environ.get('SCHEDULE_TIME', '16:30')  # 4:30 PM ET por defecto (después del cierre)
    SCHEDULE_DAYS = os.environ.get('SCHEDULE_DAYS', 'monday,tuesday,wednesday,thursday,friday').lower()
    
    # ===== INICIALIZAR SISTEMA =====
    print("🚀 Iniciando Sistema Multi-Usuario con Supabase...")
    print(f"   - Max Workers: {MAX_WORKERS}")
    print(f"   - Modo: {'PARALELO' if PARALLEL_MODE else 'SECUENCIAL'}")
    
    if USE_SCHEDULE:
        print(f"   - Modo: PROGRAMADO (Schedule)")
        print(f"   - Horario: {SCHEDULE_TIME} ET en días: {SCHEDULE_DAYS}")
    else:
        print(f"   - Modo: CONTINUO")
        print(f"   - Intervalo: {INTERVAL_MINUTES} minutos")
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
        # MODO: Ejecutar una sola vez
        print("🔄 MODO: Ejecución única\n")
        system.run_full_cycle(parallel=PARALLEL_MODE)
        print("\n✅ Ejecución única completada. Finalizando...")
        
    elif USE_SCHEDULE:
        # MODO: Ejecución programada con schedule
        print("🔄 MODO: Ejecución programada (Schedule)\n")
        print(f"⏰ El sistema se ejecutará automáticamente a las {SCHEDULE_TIME} ET")
        print(f"   en los siguientes días: {SCHEDULE_DAYS}\n")
        
        def scheduled_job():
            """Función que se ejecuta en el horario programado"""
            print("\n" + "="*80)
            print(f"⏰ EJECUCIÓN PROGRAMADA - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print("="*80 + "\n")
            
            # Verificar si es día hábil
            if not is_market_day():
                print("⚠️ Hoy no es un día hábil del mercado. Ejecución omitida.")
                print("   (El mercado está cerrado los fines de semana)\n")
                return
            
            try:
                cycle_result = system.run_full_cycle(parallel=PARALLEL_MODE)
                
                if cycle_result['success']:
                    print(f"✅ Ejecución programada completada exitosamente")
                else:
                    print(f"⚠️ Ejecución programada completada con errores")
                    
            except Exception as e:
                print(f"❌ Error en ejecución programada: {e}")
                traceback.print_exc()
        
        # Configurar schedule según los días especificados
        days_map = {
            'monday': schedule.every().monday,
            'tuesday': schedule.every().tuesday,
            'wednesday': schedule.every().wednesday,
            'thursday': schedule.every().thursday,
            'friday': schedule.every().friday,
            'saturday': schedule.every().saturday,
            'sunday': schedule.every().sunday
        }
        
        # Parsear días y configurar schedule
        schedule_days_list = [d.strip() for d in SCHEDULE_DAYS.split(',')]
        for day in schedule_days_list:
            if day in days_map:
                days_map[day].at(SCHEDULE_TIME).do(scheduled_job)
                print(f"✅ Programado para {day.capitalize()} a las {SCHEDULE_TIME}")
        
        print("\n🔄 Ejecutando scheduler... (Presiona Ctrl+C para detener)\n")
        
        # Ejecutar inmediatamente si es día hábil y ya pasó la hora programada
        try:
            # Verificar si debemos ejecutar ahora
            now_ny = datetime.now(pytz.timezone('America/New_York'))
            schedule_time_parts = SCHEDULE_TIME.split(':')
            schedule_hour = int(schedule_time_parts[0])
            schedule_minute = int(schedule_time_parts[1]) if len(schedule_time_parts) > 1 else 0
            
            # Si ya pasó la hora programada y es día hábil, ejecutar una vez
            if is_market_day() and now_ny.hour >= schedule_hour:
                print("📊 Ejecutando análisis inicial (ya pasó la hora programada)...\n")
                scheduled_job()
            
            # Mantener el scheduler corriendo
            while True:
                schedule.run_pending()
                time.sleep(60)  # Verificar cada minuto
                
        except KeyboardInterrupt:
            print("\n🛑 Ejecución detenida por el usuario. ¡Hasta pronto!")
    
    else:
        # MODO: Ejecución continua (sin schedule)
        print("🔄 MODO: Ejecución continua\n")
        
        ciclo = 1
        interval_seconds = INTERVAL_MINUTES * 60
        
        try:
            while True:
                print("\n" + "="*80)
                print(f"🔁 CICLO #{ciclo} - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                print("="*80 + "\n")
                
                # Verificar si es día hábil antes de ejecutar
                if not is_market_day():
                    print("⚠️ No es día hábil del mercado. Esperando...\n")
                    time.sleep(interval_seconds)
                    continue
                
                try:
                    cycle_result = system.run_full_cycle(parallel=PARALLEL_MODE)
                    
                    if cycle_result['success']:
                        print(f"✅ Ciclo #{ciclo} completado exitosamente")
                    else:
                        print(f"⚠️ Ciclo #{ciclo} completado con errores")
                    
                except Exception as e:
                    print(f"❌ Error en ciclo #{ciclo}: {e}")
                    traceback.print_exc()
                
                ciclo += 1
                
                print(f"\n⏱️ Esperando {INTERVAL_MINUTES} minutos para próximo ciclo...")
                print("   (Presiona Ctrl+C para detener)\n")
                
                time.sleep(interval_seconds)
                
        except KeyboardInterrupt:
            print("\n🛑 Ejecución detenida por el usuario. ¡Hasta pronto!")


if __name__ == "__main__":
    main()

