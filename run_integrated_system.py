"""
SVGA System + Market Radar - Sistema Integrado v4.1
Combina escaneo eficiente de mercados con análisis profundo
Mejoras v4.1:
- Eliminados archivos consolidados (_completo.json y .md) - solo archivos separados
- Alertas avanzadas (volatilidad, patrones con probabilidad, correlaciones)
- Nombres de archivo fijos (sin timestamps)
- Exportación de gráficos PNG
- Radares tácticos automáticos para S&P 500 y Crypto
Autor: AIDA
Fecha: 27 de octubre de 2025
"""

import sys
import os

# Configurar encoding UTF-8 para el stdout (Windows compatibility)
if sys.platform == 'win32':
    import codecs
    # Solo reconfigurar si stdout tiene buffer (no es ya un TextIOWrapper)
    if hasattr(sys.stdout, 'buffer'):
        sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    if hasattr(sys.stderr, 'buffer'):
        sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

from svga_system import SVGASystem
from market_radar import MarketRadar
from tactical_radars import TacticalRadarSystem
from alertas_avanzadas import DetectorAlertasAvanzadas
import json
import pandas as pd
import time
import traceback
from datetime import datetime
from typing import Dict, List


def generar_resumen_ejecutivo(datos_completos: Dict) -> Dict:
    """
    Genera resumen ejecutivo con análisis avanzado de alertas
    
    Args:
        datos_completos: Diccionario con todos los análisis realizados
    
    Returns:
        Dict con resumen ejecutivo estructurado
    """
    print("\n Generando resumen ejecutivo...", flush=True)
    
    resumen = {
        "timestamp": datetime.now().isoformat(),
        "distribucion_senales": {},
        "alertas_alta_prioridad": [],
        "alertas_media_prioridad": [],
        "anomalias": [],
        "oportunidades": [],
        "metricas_tecnicas": {},
        "cambios_abruptos": [],
        "recomendaciones": [],
        "contexto_mercado": {}
    }
    
    # === INTEGRAR DETECTOR DE ALERTAS AVANZADAS ===
    try:
        print("🔍 Ejecutando detector de alertas avanzadas...", flush=True)
        detector = DetectorAlertasAvanzadas()
        alertas_avanzadas = detector.detectar_todas_alertas(datos_completos)
        
        resumen['anomalias'] = alertas_avanzadas['anomalias']
        resumen['oportunidades'] = alertas_avanzadas['oportunidades']
        
        # Agregar alertas avanzadas a las alertas de alta prioridad
        for alerta in alertas_avanzadas['alertas']:
            resumen['alertas_alta_prioridad'].append({
                'ticker': alerta.get('ticker', 'N/A'),
                'tipo': alerta.get('tipo', 'GENERAL'),
                'descripcion': alerta.get('descripcion', ''),
                'prioridad': 'HIGH'
            })
        
        print(f" Detector: {len(alertas_avanzadas['anomalias'])} anomalías, "
              f"{len(alertas_avanzadas['oportunidades'])} oportunidades detectadas", flush=True)
              
    except Exception as e:
        print(f" Error en detector de alertas avanzadas: {e}", flush=True)
    
    # Consolidar todos los activos analizados
    todos_activos = {}
    
    # Portfolio contiene TODO (stocks + crypto)
    if 'portfolio' in datos_completos and 'assets' in datos_completos['portfolio']:
        todos_activos.update(datos_completos['portfolio']['assets'])
    
    # Ya no hay 'crypto' separado, todo está en 'portfolio'
    
    if not todos_activos:
        return resumen
    
    # === 1. DISTRIBUCIÓN DE SEÑALES ===
    senales = {'COMPRAR': 0, 'VENDER': 0, 'MANTENER': 0}
    for ticker, data in todos_activos.items():
        if 'signals' in data:
            signal = data['signals'].get('recommendation', 'MANTENER')
            senales[signal] = senales.get(signal, 0) + 1
    
    resumen['distribucion_senales'] = senales
    
    # === 2. ALERTAS DE ALTA Y MEDIA PRIORIDAD ===
    for ticker, data in todos_activos.items():
        if 'signals' in data:
            for alert in data['signals'].get('alerts', []):
                alerta_info = {
                    'ticker': ticker,
                    'tipo': alert['type'],
                    'descripcion': alert['description'],
                    'prioridad': alert['priority']
                }
                
                if alert['priority'] == 'HIGH':
                    resumen['alertas_alta_prioridad'].append(alerta_info)
                elif alert['priority'] == 'MEDIUM':
                    resumen['alertas_media_prioridad'].append(alerta_info)
    
    # === 3. MÉTRICAS TÉCNICAS CLAVE ===
    for ticker, data in todos_activos.items():
        if 'latest_metrics' in data and 'signals' in data:
            metrics = data['latest_metrics']
            signals = data['signals']
            
            # Tendencia
            tendencia = "ALCISTA" if metrics.get('ema_50', 0) > metrics.get('ema_200', 0) else "BAJISTA"
            
            # Momentum
            macd_hist = metrics.get('macd_histogram', 0)
            momentum = "POSITIVO" if macd_hist > 0 else "NEGATIVO"
            
            # Fuerza
            adx = metrics.get('adx', 0)
            fuerza = "FUERTE" if adx > 40 else "MODERADA" if adx > 25 else "DÉBIL"
            
            # Estado RSI
            rsi = metrics.get('rsi', 50)
            estado_rsi = "SOBRECOMPRA" if rsi > 70 else "SOBREVENTA" if rsi < 30 else "NEUTRAL"
            
            resumen['metricas_tecnicas'][ticker] = {
                'precio': signals.get('price_current', 0),
                'senal': signals.get('recommendation', 'MANTENER'),
                'tendencia': tendencia,
                'momentum': momentum,
                'fuerza_tendencia': fuerza,
                'adx': adx,
                'rsi': rsi,
                'estado_rsi': estado_rsi,
                'macd_histogram': macd_hist
            }
    
    # === 4. DETECCIÓN DE CAMBIOS ABRUPTOS ===
    for ticker, data in todos_activos.items():
        if 'latest_metrics' in data:
            metrics = data['latest_metrics']
            
            # Volumen extremo
            if 'volume' in metrics and 'volume_sma_20' in metrics:
                rvol = metrics['volume'] / metrics['volume_sma_20'] if metrics['volume_sma_20'] > 0 else 0
                if rvol > 5.0:
                    resumen['cambios_abruptos'].append({
                        'ticker': ticker,
                        'tipo': 'VOLUMEN_EXTREMO',
                        'descripcion': f"Volumen {rvol:.1f}x superior al promedio - Posible evento significativo",
                        'severidad': 'ALTA'
                    })
            
            # RSI extremo
            rsi = metrics.get('rsi', 50)
            if rsi > 80:
                resumen['cambios_abruptos'].append({
                    'ticker': ticker,
                    'tipo': 'RSI_SOBRECOMPRA_EXTREMA',
                    'descripcion': f"RSI en {rsi:.1f} - Sobreventa extrema, posible reversión inminente",
                    'severidad': 'MEDIA'
                })
            elif rsi < 20:
                resumen['cambios_abruptos'].append({
                    'ticker': ticker,
                    'tipo': 'RSI_SOBREVENTA_EXTREMA',
                    'descripcion': f"RSI en {rsi:.1f} - Sobrecompra extrema, posible reversión al alza",
                    'severidad': 'MEDIA'
                })
            
            # Cambio de precio abrupto
            if 'close' in metrics and 'close_prev' in metrics:
                cambio_pct = ((metrics['close'] - metrics['close_prev']) / metrics['close_prev'] * 100)
                if abs(cambio_pct) > 10:
                    resumen['cambios_abruptos'].append({
                        'ticker': ticker,
                        'tipo': 'CAMBIO_PRECIO_ABRUPTO',
                        'descripcion': f"Cambio de precio de {cambio_pct:+.2f}% en última sesión",
                        'severidad': 'ALTA' if abs(cambio_pct) > 15 else 'MEDIA'
                    })
    
    # === 5. RECOMENDACIONES ESTRATÉGICAS ===
    total_activos = len(todos_activos)
    
    # Recomendación según distribución de señales
    if senales['COMPRAR'] > total_activos * 0.5:
        resumen['recomendaciones'].append({
            'tipo': 'ESTRATEGIA_GENERAL',
            'mensaje': f"🟢 Mercado alcista detectado ({senales['COMPRAR']}/{total_activos} señales de compra). Considerar aumentar exposición.",
            'prioridad': 'ALTA'
        })
    elif senales['VENDER'] > total_activos * 0.5:
        resumen['recomendaciones'].append({
            'tipo': 'ESTRATEGIA_GENERAL',
            'mensaje': f"🔴 Mercado bajista detectado ({senales['VENDER']}/{total_activos} señales de venta). Considerar proteger capital.",
            'prioridad': 'ALTA'
        })
    else:
        resumen['recomendaciones'].append({
            'tipo': 'ESTRATEGIA_GENERAL',
            'mensaje': f"🟡 Mercado en consolidación ({senales['MANTENER']}/{total_activos} en espera). Esperar señales más claras.",
            'prioridad': 'MEDIA'
        })
    
    # Recomendaciones por alertas de alta prioridad
    if len(resumen['alertas_alta_prioridad']) > 0:
        resumen['recomendaciones'].append({
            'tipo': 'ACCION_INMEDIATA',
            'mensaje': f" {len(resumen['alertas_alta_prioridad'])} alertas de alta prioridad requieren atención inmediata. Revisar informes MD.",
            'prioridad': 'ALTA'
        })
    
    # Recomendación por cambios abruptos
    if len(resumen['cambios_abruptos']) > 0:
        cambios_alta = sum(1 for c in resumen['cambios_abruptos'] if c['severidad'] == 'ALTA')
        if cambios_alta > 0:
            resumen['recomendaciones'].append({
                'tipo': 'VIGILANCIA_VOLATILIDAD',
                'mensaje': f"📈 {cambios_alta} activos muestran cambios abruptos de alta severidad. Ajustar stops.",
                'prioridad': 'ALTA'
            })
    
    # === 6. CONTEXTO DE MERCADO ===
    radar_info = {}
    if 'radar_sp500' in datos_completos:
        radar_info['sp500'] = {
            'escaneados': datos_completos['radar_sp500'].get('total_escaneados', 0),
            'candidatos': len(datos_completos['radar_sp500'].get('candidatos', []))
        }
    
    if 'radar_crypto' in datos_completos:
        radar_info['crypto'] = {
            'escaneados': datos_completos['radar_crypto'].get('total_escaneados', 0),
            'candidatos': len(datos_completos['radar_crypto'].get('candidatos', []))
        }
    
    resumen['contexto_mercado'] = {
        'total_activos_analizados': total_activos,
        'radar_info': radar_info,
        'mercado_alcista': senales['COMPRAR'] > senales['VENDER'],
        'mercado_bajista': senales['VENDER'] > senales['COMPRAR'],
        'mercado_lateral': senales['MANTENER'] >= total_activos * 0.6
    }
    
    print(" Resumen ejecutivo generado", flush=True)
    
    return resumen


def run_integrated_analysis(
    portfolio_tickers: list,
    crypto_tickers: list,
    scan_sp500: bool = True,
    scan_crypto: bool = True,
    sp500_strategy: str = "momentum",
    crypto_strategy: str = "breakout",
    max_candidates: int = 10
) -> Dict:
    """
    Ejecuta análisis integrado completo: Radar + SVGA (Portfolio + Crypto)
    
    Args:
        portfolio_tickers: Portafolio base (stocks/indices)
        crypto_tickers: Portafolio crypto
        scan_sp500: Ejecutar radar del S&P 500
        scan_crypto: Ejecutar radar de criptomonedas
        sp500_strategy: Estrategia para S&P 500
        crypto_strategy: Estrategia para crypto
        max_candidates: Número máximo de candidatos por radar
    
    Returns:
        Dict con análisis completo y resumen ejecutivo
    """
    
    print("\n" + "="*80, flush=True)
    print("🚀 SISTEMA INTEGRADO SVGA 3.0 - ANÁLISIS COMPLETO AUTOMATIZADO", flush=True)
    print("="*80 + "\n", flush=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    datos_completos = {
        "timestamp": timestamp,
        "portfolio": {},  # Portfolio único (stocks + crypto)
        "market": {},     # Candidatos del mercado (S&P 500 + Crypto)
        "radar_sp500": {},
        "radar_crypto": {},
        "executive_summary": {}
    }
    
    # ==================================================================
    # FASE 1: SISTEMA DE RADARES TÁCTICOS (NUEVO)
    # ==================================================================
    
    # OPCIÓN A: Usar nuevo sistema táctico (ACTIVADO POR DEFECTO)
    use_tactical_system = True
    
    sp500_candidates = []
    crypto_candidates = []
    tactical_info = {}
    
    if use_tactical_system:
        print("🎯 USANDO SISTEMA DE RADARES TÁCTICOS CON FLUJO DE 3 FASES\n", flush=True)
        
        # === FASE 1A: RADARES TÁCTICOS PARA S&P 500 ===
        if scan_sp500:
            print(f"📡 FASE 1A: Radares Tácticos S&P 500...\n", flush=True)
            
            # Obtener universo S&P 500
            radar_temp = MarketRadar(universe="sp500")
            radar_temp.load_universe()
            sp500_universe = radar_temp.tickers
            
            # Ejecutar sistema táctico
            tactical_sp500 = TacticalRadarSystem(benchmark="^GSPC")
            sp500_candidates, sp500_full_metrics, sp500_radars_used = tactical_sp500.run_tactical_scan(
                tickers=sp500_universe,
                period="6mo",
                max_candidates=max_candidates
            )
            
            datos_completos['radar_sp500'] = {
                'total_escaneados': len(sp500_universe),
                'candidatos': sp500_candidates,
                'estrategia': 'TACTICAL',
                'regime': tactical_sp500.market_regime,
                'regime_signal': tactical_sp500.regime_signal,
                'radars_used': sp500_radars_used
            }
            
            tactical_info['sp500'] = {
                'regime': tactical_sp500.market_regime,
                'signal': tactical_sp500.regime_signal,
                'radars': sp500_radars_used
            }
            
            # Exportar resultados
            if not sp500_full_metrics.empty:
                sp500_full_metrics.to_csv('radar_sp500.csv', index=False)
                print(f"📁 Resultados exportados: radar_sp500.csv", flush=True)
        
        # === FASE 1B: RADARES TÁCTICOS PARA CRYPTO ===
        if scan_crypto:
            print(f"\n📡 FASE 1B: Radares Tácticos Crypto Top 30...\n", flush=True)
            
            # Obtener universo crypto
            radar_temp_crypto = MarketRadar(universe="crypto30")
            radar_temp_crypto.load_universe()
            crypto_universe = radar_temp_crypto.tickers
            
            # Ejecutar sistema táctico (usando BTC-USD como benchmark crypto)
            tactical_crypto = TacticalRadarSystem(benchmark="BTC-USD")
            crypto_candidates, crypto_full_metrics, crypto_radars_used = tactical_crypto.run_tactical_scan(
                tickers=crypto_universe,
                period="3mo",
                max_candidates=max_candidates
            )
            
            datos_completos['radar_crypto'] = {
                'total_escaneados': len(crypto_universe),
                'candidatos': crypto_candidates,
                'estrategia': 'TACTICAL',
                'regime': tactical_crypto.market_regime,
                'regime_signal': tactical_crypto.regime_signal,
                'radars_used': crypto_radars_used
            }
            
            tactical_info['crypto'] = {
                'regime': tactical_crypto.market_regime,
                'signal': tactical_crypto.regime_signal,
                'radars': crypto_radars_used
            }
            
            # Exportar resultados
            if not crypto_full_metrics.empty:
                crypto_full_metrics.to_csv('radar_crypto.csv', index=False)
                print(f"📁 Resultados exportados: radar_crypto.csv", flush=True)
    
    else:
        # OPCIÓN B: Usar sistema antiguo de radares
        print("📡 Usando sistema de radares tradicional\n")
        
        if scan_sp500:
            print(f"📡 FASE 1A: Radar S&P 500 con estrategia '{sp500_strategy}'...\n")
            
            radar_sp500 = MarketRadar(universe="sp500")
            sp500_candidates, sp500_metrics = radar_sp500.scan(
                period="6mo",
                strategy=sp500_strategy,
                max_candidates=max_candidates
            )
            
            datos_completos['radar_sp500'] = {
                'total_escaneados': len(radar_sp500.tickers),
                'candidatos': sp500_candidates,
                'estrategia': sp500_strategy
            }
            
            radar_sp500.export_radar_results(sp500_metrics, universe="sp500")
        
        if scan_crypto:
            print(f"\n📡 FASE 1B: Radar Crypto Top 30 con estrategia '{crypto_strategy}'...\n")
            
            radar_crypto = MarketRadar(universe="crypto30")
            crypto_candidates, crypto_metrics = radar_crypto.scan(
                period="3mo",
                strategy=crypto_strategy,
                max_candidates=max_candidates
            )
            
            datos_completos['radar_crypto'] = {
                'total_escaneados': len(radar_crypto.tickers),
                'candidatos': crypto_candidates,
                'estrategia': crypto_strategy
            }
            
            radar_crypto.export_radar_results(crypto_metrics, universe="crypto")
    
    # ==================================================================
    # FASE 2A: ANÁLISIS PROFUNDO PORTFOLIO ÚNICO
    # ==================================================================
    
    print("\n" + "="*80, flush=True)
    print("🔬 FASE 2: Análisis Profundo del Portfolio Único", flush=True)
    print("="*80 + "\n", flush=True)
    
    print(f" Portfolio Completo: {portfolio_tickers}", flush=True)
    
    # Combinar todos los candidatos del mercado (S&P 500 + Crypto)
    all_market_candidates = sp500_candidates + crypto_candidates
    print(f" Candidatos del Mercado (S&P 500 + Crypto): {all_market_candidates if all_market_candidates else 'Ninguno'}\n", flush=True)
    
    # Análisis ÚNICO: portfolio completo + todos los candidatos del mercado
    svga_system = SVGASystem(
        portfolio_tickers=portfolio_tickers,
        market_tickers=all_market_candidates
    )
    
    # Ejecutar análisis (genera 4 archivos: portfolio_*.json, portfolio_*.md, mercado_*.json, mercado_*.md)
    svga_system.run()
    
    # Cargar resultados de los JSON generados
    try:
        with open('portfolio_analisis.json', 'r', encoding='utf-8') as f:
            portfolio_data = json.load(f)
            datos_completos['portfolio'] = portfolio_data.get('portfolio', {})
    except Exception as e:
        print(f" Error cargando portfolio_analisis.json: {e}", flush=True)
    
    try:
        with open('mercado_analisis.json', 'r', encoding='utf-8') as f:
            market_data = json.load(f)
            datos_completos['market'] = market_data.get('market', {})
    except Exception as e:
        print(f" Error cargando mercado_analisis.json: {e}", flush=True)
    
    # Nota: Ya NO hay FASE 2B, todo se analiza en una sola pasada
    
    # ==================================================================
    # FASE 3: RESUMEN EJECUTIVO
    # ==================================================================
    
    print("\n" + "="*80, flush=True)
    print(" FASE 3: Generando Resumen Ejecutivo", flush=True)
    print("="*80, flush=True)
    
    datos_completos['executive_summary'] = generar_resumen_ejecutivo(datos_completos)
    
    # ==================================================================
    # FASE 4: EXPORTAR JSON Y MD CONSOLIDADOS (ELIMINADO - NO NECESARIO)
    # ==================================================================
    
    # Los archivos separados (portfolio_analisis.json/md y mercado_analisis.json/md) 
    # son suficientes. Ya no se generan archivos _completo
    
    # ==================================================================
    # NOTA: Ya NO eliminamos archivos separados (portfolio_*.json/md, mercado_*.json/md)
    # Estos archivos se mantienen como salidas independientes del análisis
    # ==================================================================
    
    # ==================================================================
    # RESUMEN FINAL
    # ==================================================================
    
    print("\n" + "="*80, flush=True)
    print(" ANÁLISIS INTEGRADO COMPLETADO", flush=True)
    print("="*80 + "\n", flush=True)
    
    # Mostrar resumen en consola
    resumen = datos_completos['executive_summary']
    
    print(" RESUMEN RÁPIDO:", flush=True)
    print(f"\n🎯 Distribución de señales:", flush=True)
    for signal, count in resumen['distribucion_senales'].items():
        emoji = "🟢" if signal == "COMPRAR" else "🔴" if signal == "VENDER" else "🟡"
        print(f"   {emoji} {signal}: {count}", flush=True)
    
    print(f"\n🚨 Alertas:", flush=True)
    print(f"   Alta prioridad: {len(resumen['alertas_alta_prioridad'])}", flush=True)
    print(f"   Media prioridad: {len(resumen['alertas_media_prioridad'])}", flush=True)
    print(f"   Cambios abruptos: {len(resumen['cambios_abruptos'])}", flush=True)
    
    print(f"\n💡 Recomendaciones principales:", flush=True)
    for rec in resumen['recomendaciones'][:3]:
        print(f"   {rec['mensaje']}", flush=True)
    
    print("\n📁 Archivos generados:", flush=True)
    print("      1. 📄 portfolio_analisis.json (métricas del portfolio)", flush=True)
    print("      2. 📝 portfolio_informe.md (informe del portfolio)", flush=True)
    print("      3. 📄 mercado_analisis.json (métricas del mercado)", flush=True)
    print("      4. 📝 mercado_informe.md (informe del mercado)", flush=True)
    # print("\n   📈 ARCHIVOS ADICIONALES:", flush=True)
    # print("      - chart_*.html (gráficos interactivos)", flush=True)
    # print("      - chart_*.png (gráficos exportados)", flush=True)
    # print("      - radar_*.csv (resultados de escaneos)", flush=True)
    
    return datos_completos


def generar_informe_markdown_completo(datos: Dict):
    """
    FUNCIÓN DEPRECADA - Ya no se utiliza
    
    Esta función generaba el archivo svga_informe_completo.md que fue eliminado
    según los nuevos requerimientos. Se mantiene el código por si se necesita en el futuro.
    
    Los informes ahora se generan separados:
    - portfolio_informe.md (generado por SVGASystem)
    - mercado_informe.md (generado por SVGASystem, incluye top 20 crypto)
    """
    return  # Función deshabilitada
    
    # CÓDIGO ORIGINAL COMENTADO (no se ejecuta)
    """
    
    filename = "svga_informe_completo.md"
    
    with open(filename, 'w', encoding='utf-8') as f:
        f.write("#  Informe SVGA v4.0 - Análisis Técnico Completo\n\n")
        f.write(f"**Generado:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write("---\n\n")
        
        # ====================================================================
        # RESUMEN EJECUTIVO
        # ====================================================================
        resumen = datos.get('executive_summary', {})
        
        f.write("## 📈 RESUMEN EJECUTIVO\n\n")
        
        # Distribución de señales
        f.write("### Distribución de Señales\n\n")
        senales = resumen.get('distribucion_senales', {})
        for signal, count in senales.items():
            emoji = "🟢" if signal == "COMPRAR" else "🔴" if signal == "VENDER" else "🟡"
            f.write(f"- {emoji} **{signal}**: {count}\n")
        
        # ====================================================================
        # ANOMALÍAS DETECTADAS (NUEVO V4.0)
        # ====================================================================
        f.write("\n### 🔍 ANOMALÍAS DETECTADAS\n\n")
        anomalias = resumen.get('anomalias', [])
        if anomalias:
            for anomalia in anomalias:
                f.write(f"-  **{anomalia.get('ticker', 'N/A')}**: {anomalia.get('descripcion', '')}\n")
        else:
            f.write(" No se detectaron anomalías\n")
        
        # ====================================================================
        # OPORTUNIDADES (NUEVO V4.0)
        # ====================================================================
        f.write("\n### � OPORTUNIDADES IDENTIFICADAS\n\n")
        oportunidades = resumen.get('oportunidades', [])
        if oportunidades:
            for oportunidad in oportunidades:
                ticker = oportunidad.get('ticker', 'N/A')
                tipo = oportunidad.get('tipo', '')
                desc = oportunidad.get('descripcion', '')
                prob = oportunidad.get('probabilidad', '')
                
                f.write(f"- 🎯 **{ticker}** ({tipo}): {desc}")
                if prob:
                    f.write(f" - {prob}")
                f.write("\n")
        else:
            f.write(" No hay oportunidades de alta probabilidad en este momento\n")
        
        # Alertas
        f.write("\n### �🚨 Alertas de Alta Prioridad\n\n")
        alertas_high = resumen.get('alertas_alta_prioridad', [])
        if alertas_high:
            for alerta in alertas_high:
                f.write(f"- **{alerta['ticker']}** ({alerta['tipo']}): {alerta['descripcion']}\n")
        else:
            f.write(" No hay alertas de alta prioridad\n")
        
        # Cambios abruptos
        f.write("\n### ⚡ Cambios Abruptos Detectados\n\n")
        cambios = resumen.get('cambios_abruptos', [])
        if cambios:
            for cambio in cambios:
                severidad_emoji = "🔴" if cambio['severidad'] == 'ALTA' else "🟡"
                f.write(f"- {severidad_emoji} **{cambio['ticker']}** ({cambio['tipo']}): {cambio['descripcion']}\n")
        else:
            f.write(" No se detectaron cambios abruptos\n")
        
        # Recomendaciones
        f.write("\n### 💡 Recomendaciones\n\n")
        recomendaciones = resumen.get('recomendaciones', [])
        if recomendaciones:
            for rec in recomendaciones:
                f.write(f"- {rec['mensaje']}\n")
        else:
            f.write("- Mantener seguimiento de las posiciones actuales\n")
        
        # ====================================================================
        # MÉTRICAS TÉCNICAS DETALLADAS POR ACTIVO (MEJORADO V4.0)
        # ====================================================================
        f.write("\n##  MÉTRICAS TÉCNICAS DETALLADAS\n\n")
        
        # Tabla resumen compacta
        f.write("### Tabla Resumen\n\n")
        metricas = resumen.get('metricas_tecnicas', {})
        
        if metricas:
            f.write("| Activo | Precio | Señal | Tendencia | Momentum | ADX | RSI |\n")
            f.write("|--------|--------|-------|-----------|----------|-----|-----|\n")
            
            for ticker, m in metricas.items():
                f.write(f"| {ticker} | ${m['precio']:,.2f} | {m['senal']} | {m['tendencia']} | {m['momentum']} | {m['adx']:.1f} | {m['rsi']:.1f} |\n")
        
        # ====================================================================
        # ANÁLISIS DETALLADO POR ACTIVO CON TODAS LAS MÉTRICAS (NUEVO V4.0)
        # ====================================================================
        f.write("\n### Análisis Detallado por Activo\n\n")
        
        # Portfolio contiene TODO (stocks + crypto)
        portfolio_assets = datos.get('portfolio', {}).get('assets', {})
        
        # Mercado contiene los candidatos del radar
        market_assets = datos.get('market', {}).get('assets', {})
        
        # Primero mostrar portfolio
        if portfolio_assets:
            f.write("#### 💼 PORTFOLIO\n\n")
            for ticker, asset_data in portfolio_assets.items():
                f.write(f"\n##### {ticker}\n\n")
                
                # Señal y precio
                signals = asset_data.get('signals', {})
                recommendation = signals.get('recommendation', 'N/A')
                price = signals.get('price_current', 0)
                
                emoji_signal = "🟢" if recommendation == "COMPRAR" else "🔴" if recommendation == "VENDER" else "🟡"
                f.write(f"**Señal:** {emoji_signal} {recommendation} | **Precio:** ${price:,.2f}\n\n")
            
            # Todas las métricas
            latest_metrics = asset_data.get('latest_metrics', {})
            
            if latest_metrics:
                f.write("**Indicadores Principales:**\n\n")
                f.write("| Indicador | Valor |\n")
                f.write("|-----------|-------|\n")
                
                # Lista completa de indicadores
                indicators_map = {
                    'ema_12': 'EMA 12',
                    'ema_26': 'EMA 26',
                    'ema_50': 'EMA 50',
                    'ema_200': 'EMA 200',
                    'rsi': 'RSI (14)',
                    'macd': 'MACD',
                    'macd_signal': 'MACD Signal',
                    'macd_histogram': 'MACD Histogram',
                    'stoch_k': 'Stochastic %K',
                    'stoch_d': 'Stochastic %D',
                    'adx': 'ADX',
                    'aroon_up': 'Aroon Up',
                    'aroon_down': 'Aroon Down',
                    'obv': 'OBV',
                    'cmf': 'CMF',
                    'vwap': 'VWAP',
                    'atr': 'ATR',
                    'atr_percent': 'ATR %',
                    'bb_upper': 'Bollinger Upper',
                    'bb_middle': 'Bollinger Middle',
                    'bb_lower': 'Bollinger Lower',
                    'bb_width': 'Bollinger Width %',
                    'keltner_upper': 'Keltner Upper',
                    'keltner_lower': 'Keltner Lower',
                    'volume': 'Volume',
                    'volume_sma_20': 'Volume SMA 20',
                    'rvol': 'Relative Volume'
                }
                
                for key, label in indicators_map.items():
                    if key in latest_metrics:
                        value = latest_metrics[key]
                        
                        # Formatear según tipo de valor
                        if isinstance(value, (int, float)):
                            if key in ['volume', 'obv', 'volume_sma_20']:
                                formatted = f"{value:,.0f}"
                            elif key in ['rsi', 'stoch_k', 'stoch_d', 'aroon_up', 'aroon_down', 
                                        'adx', 'atr_percent', 'bb_width', 'cmf']:
                                formatted = f"{value:.2f}"
                            else:
                                formatted = f"{value:,.2f}"
                        else:
                            formatted = str(value)
                        
                        f.write(f"| {label} | {formatted} |\n")
                
                # Fibonacci y soporte/resistencia
                fib_levels = asset_data.get('fibonacci_levels', {})
                if fib_levels:
                    f.write("\n**Niveles de Fibonacci:**\n\n")
                    f.write("| Nivel | Precio |\n")
                    f.write("|-------|--------|\n")
                    for nivel, precio in fib_levels.items():
                        f.write(f"| {nivel} | ${precio:,.2f} |\n")
                
                # Alertas del activo
                alerts = signals.get('alerts', [])
                if alerts:
                    f.write("\n**Alertas:**\n\n")
                    for alert in alerts:
                        priority_emoji = "🔴" if alert['priority'] == 'HIGH' else "🟡" if alert['priority'] == 'MEDIUM' else "🔵"
                        f.write(f"- {priority_emoji} [{alert['type']}] {alert['description']}\n")
                
                f.write("\n---\n")
        
        # Luego mostrar candidatos del mercado
        if market_assets:
            f.write("\n#### 🌍 CANDIDATOS DEL MERCADO (RADAR)\n\n")
            for ticker, asset_data in market_assets.items():
                f.write(f"\n##### {ticker}\n\n")
                
                # Señal y precio
                signals = asset_data.get('signals', {})
                recommendation = signals.get('recommendation', 'N/A')
                price = signals.get('price_current', 0)
                
                emoji_signal = "🟢" if recommendation == "COMPRAR" else "🔴" if recommendation == "VENDER" else "🟡"
                f.write(f"**Señal:** {emoji_signal} {recommendation} | **Precio:** ${price:,.2f}\n\n")
                
                # Métricas principales (versión simplificada para mercado)
                latest_metrics = asset_data.get('latest_metrics', {})
                
                if latest_metrics:
                    f.write("**Indicadores Clave:**\n\n")
                    f.write("| Indicador | Valor |\n")
                    f.write("|-----------|-------|\n")
                    
                    # Solo indicadores clave para candidatos del mercado
                    key_indicators = {
                        'ema_50': 'EMA 50',
                        'ema_200': 'EMA 200',
                        'rsi': 'RSI (14)',
                        'macd_histogram': 'MACD Histogram',
                        'adx': 'ADX',
                        'atr_percent': 'ATR %',
                        'rvol': 'Relative Volume'
                    }
                    
                    for key, label in key_indicators.items():
                        if key in latest_metrics:
                            value = latest_metrics[key]
                            if isinstance(value, (int, float)):
                                formatted = f"{value:.2f}"
                            else:
                                formatted = str(value)
                            f.write(f"| {label} | {formatted} |\n")
                    
                    # Alertas del activo
                    alerts = signals.get('alerts', [])
                    if alerts:
                        f.write("\n**Alertas:**\n\n")
                        for alert in alerts:
                            priority_emoji = "🔴" if alert['priority'] == 'HIGH' else "🟡" if alert['priority'] == 'MEDIUM' else "🔵"
                            f.write(f"- {priority_emoji} [{alert['type']}] {alert['description']}\n")
                
                f.write("\n---\n")
        
        # ====================================================================
        # CONTEXTO DE MERCADO
        # ====================================================================
        f.write("\n## 🌍 CONTEXTO DE MERCADO\n\n")
        contexto = resumen.get('contexto_mercado', {})
        
        f.write(f"- **Total de activos analizados:** {contexto.get('total_activos_analizados', 0)}\n")
        f.write(f"- **Mercado alcista:** {' Sí' if contexto.get('mercado_alcista') else '❌ No'}\n")
        f.write(f"- **Mercado bajista:** {' Sí' if contexto.get('mercado_bajista') else '❌ No'}\n")
        f.write(f"- **Mercado lateral:** {' Sí' if contexto.get('mercado_lateral') else '❌ No'}\n")
        
        radar_info = contexto.get('radar_info', {})
        if 'sp500' in radar_info:
            f.write(f"\n**Radar S&P 500:**\n")
            f.write(f"- Escaneados: {radar_info['sp500']['escaneados']}\n")
            f.write(f"- Candidatos: {radar_info['sp500']['candidatos']}\n")
        
        if 'crypto' in radar_info:
            f.write(f"\n**Radar Crypto:**\n")
            f.write(f"- Escaneados: {radar_info['crypto']['escaneados']}\n")
            f.write(f"- Candidatos: {radar_info['crypto']['candidatos']}\n")
        
        f.write("\n---\n\n")
        f.write("*Generado por SVGA System v4.0 con Alertas Avanzadas*\n")
    
    print(f" Informe MD completo: {filename}", flush=True)
    """


def limpiar_archivos_csv():
    """
    Limpia (elimina) todos los archivos CSV generados por los radares
    al final de cada ciclo de análisis
    """
    import glob
    
    csv_files = glob.glob('c:/Users/mikia/analisis-tecnico/radar_*.csv')
    
    if csv_files:
        print("\n🧹 Limpiando archivos CSV...", flush=True)
        for csv_file in csv_files:
            try:
                os.remove(csv_file)
                filename = os.path.basename(csv_file)
                print(f"   ✅ Eliminado: {filename}", flush=True)
            except Exception as e:
                print(f"   ⚠️ Error eliminando {csv_file}: {e}", flush=True)
    else:
        print("\n🧹 No se encontraron archivos CSV para limpiar", flush=True)


def main():
    """
    Función principal - Ejecución automática completa
    """
    
    # ===== CONFIGURACIÓN DE PORTAFOLIOS =====
    # PORTAFOLIO ÚNICO: Combina stocks, índices y crypto
    mi_portafolio_completo = [
        # Stocks e índices
        'PAXG-USD',  # Oro digital
        '^GSPC',     # S&P 500 (benchmark)
        # Crypto
        'BTC-USD',   # Bitcoin
        'ETH-USD',   # Ethereum
        'BNB-USD',   # Binance Coin
        'SOL-USD'    # Solana
    ]

    intervalo_minutos = os.environ.get('SVGA_INTERVAL_MINUTES', '15')
    try:
        intervalo_minutos = int(intervalo_minutos)
    except ValueError:
        print(f" Valor inválido para SVGA_INTERVAL_MINUTES='{intervalo_minutos}'. Se usará 15 minutos por defecto.")
        intervalo_minutos = 15

    if intervalo_minutos <= 0:
        print(f" Intervalo {intervalo_minutos} minutos no válido. Se usará 15 minutos por defecto.")
        intervalo_minutos = 15

    intervalo_segundos = intervalo_minutos * 60

    print("🚀 Iniciando modo de análisis continuo...", flush=True)
    print("   - Portfolio único (stocks + crypto) + Radar S&P 500", flush=True)
    print("   - Análisis de mercado (candidatos S&P 500 + candidatos crypto)", flush=True)
    print("   - Resumen ejecutivo con alertas avanzadas", flush=True)
    print(f"   - Intervalo entre ejecuciones: {intervalo_minutos} minutos\n", flush=True)

    ciclo = 1

    try:
        while True:
            inicio_ciclo = datetime.now()
            print("=" * 80, flush=True)
            print(f"🔁 Ciclo #{ciclo} - Inicio: {inicio_ciclo.strftime('%Y-%m-%d %H:%M:%S')}", flush=True)
            print("=" * 80, flush=True)

            try:
                run_integrated_analysis(
                    portfolio_tickers=mi_portafolio_completo,  # Portafolio único
                    crypto_tickers=[],  # Ya no se usa, todo está en portfolio_tickers
                    scan_sp500=True,
                    scan_crypto=True,
                    sp500_strategy="mixed",      # Estrategia mixta para S&P 500
                    crypto_strategy="breakout",  # Estrategia de rupturas para crypto
                    max_candidates=10
                )
                
                # Limpiar archivos CSV al final del ciclo
                limpiar_archivos_csv()
                
                fin_ciclo = datetime.now()
                duracion = (fin_ciclo - inicio_ciclo).total_seconds() / 60
                print(f"\n Ciclo #{ciclo} completado en {duracion:.2f} minutos", flush=True)
            except Exception as e:
                print(f"\n❌ Error durante el ciclo #{ciclo}: {e}", flush=True)
                traceback.print_exc()

            ciclo += 1

            print(f"\n⏱️ Esperando {intervalo_minutos} minutos para la próxima ejecución. Presiona Ctrl+C para detener.", flush=True)
            time.sleep(intervalo_segundos)

    except KeyboardInterrupt:
        print("\n🛑 Ejecución continua detenida por el usuario. Hasta la próxima!", flush=True)


if __name__ == "__main__":
    main()
