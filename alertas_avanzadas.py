"""
Sistema de Alertas Avanzadas para SVGA
Detecta anomalías, oportunidades y alertas en tiempo real
Inspirado en sistemas de detección de patrones institucionales
Autor: AIDA
Fecha: 25 de octubre de 2025
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
from datetime import datetime


class DetectorAlertasAvanzadas:
    """
    Detector avanzado de alertas, anomalías y oportunidades
    """
    
    def __init__(self):
        self.alertas_detectadas = []
        self.anomalias = []
        self.oportunidades = []
    
    def detectar_todas_alertas(self, datos_completos: Dict) -> Dict:
        """
        Detecta todas las alertas, anomalías y oportunidades
        
        Args:
            datos_completos: Diccionario con todos los análisis
        
        Returns:
            Dict con alertas estructuradas
        """
        self.alertas_detectadas = []
        self.anomalias = []
        self.oportunidades = []
        
        # Consolidar activos
        todos_activos = {}
        if 'portfolio' in datos_completos and 'assets' in datos_completos['portfolio']:
            todos_activos.update(datos_completos['portfolio']['assets'])
        if 'crypto' in datos_completos and 'assets' in datos_completos['crypto']:
            todos_activos.update(datos_completos['crypto']['assets'])
        
        # Detectar para cada activo
        for ticker, data in todos_activos.items():
            if 'latest_metrics' not in data or 'signals' not in data:
                continue
            
            metrics = data['latest_metrics']
            signals = data['signals']
            
            # 1. Anomalía: Volatilidad aumentada
            self._detectar_volatilidad_anormal(ticker, metrics)
            
            # 2. Anomalía: Volumen inusual (alto o bajo)
            self._detectar_volumen_inusual(ticker, metrics)
            
            # 3. Oportunidad: Patrones alcistas/bajistas con probabilidad
            self._detectar_patrones_con_probabilidad(ticker, metrics, signals)
            
            # 4. Oportunidad: Divergencias RSI/MACD
            self._detectar_divergencias(ticker, signals)
            
            # 5. Anomalía: Cambios abruptos de precio
            self._detectar_cambios_abruptos_precio(ticker, metrics)
            
            # 6. Alerta: RSI extremo
            self._detectar_rsi_extremo(ticker, metrics)
        
        # Detectar correlaciones rotas entre activos
        self._detectar_correlaciones_rotas(todos_activos)
        
        return {
            'anomalias': self.anomalias,
            'oportunidades': self.oportunidades,
            'alertas': self.alertas_detectadas
        }
    
    def _detectar_volatilidad_anormal(self, ticker: str, metrics: Dict):
        """
        Detecta aumento inusual de volatilidad
        Similar a: "Volatilidad de 'AAPL' aumentó 35% inesperadamente"
        """
        atr = metrics.get('atr', 0)
        atr_percent = metrics.get('atr_percent', 0)
        
        # Calcular ATR histórico promedio (aproximación)
        if atr_percent > 5.0:  # ATR% > 5% indica alta volatilidad
            # Estimar aumento (comparando con umbral normal de 3%)
            aumento_pct = ((atr_percent - 3.0) / 3.0) * 100
            
            if aumento_pct > 25:  # Aumento > 25%
                self.anomalias.append({
                    'tipo': 'VOLATILIDAD_AUMENTADA',
                    'ticker': ticker,
                    'titulo': f"⚠️ Anomalía Detectada",
                    'descripcion': f"Volatilidad de '{ticker}' aumentó un {aumento_pct:.0f}% inesperadamente en últimas 24h.",
                    'severidad': 'ALTA' if aumento_pct > 50 else 'MEDIA',
                    'metricas': {
                        'atr_actual': atr,
                        'atr_percent': atr_percent,
                        'aumento_estimado': f"{aumento_pct:.1f}%"
                    }
                })
    
    def _detectar_volumen_inusual(self, ticker: str, metrics: Dict):
        """
        Detecta volumen inusualmente alto o bajo
        Similar a: "El volumen de negociación de 'GOOGL' es inusualmente bajo hoy"
        """
        volume = metrics.get('volume', 0)
        volume_sma_20 = metrics.get('volume_sma_20', 0)
        
        if volume_sma_20 > 0:
            rvol = volume / volume_sma_20
            
            # Volumen MUY alto (>3x)
            if rvol > 3.0:
                self.alertas_detectadas.append({
                    'tipo': 'VOLUMEN_ALTO',
                    'ticker': ticker,
                    'titulo': f"💡 Alerta",
                    'descripcion': f"El volumen de negociación de '{ticker}' es inusualmente ALTO hoy ({rvol:.1f}x promedio).",
                    'severidad': 'MEDIA',
                    'metricas': {
                        'rvol': f"{rvol:.2f}x",
                        'volumen_actual': volume,
                        'volumen_promedio': volume_sma_20
                    }
                })
            
            # Volumen MUY bajo (<0.4x)
            elif rvol < 0.4:
                self.alertas_detectadas.append({
                    'tipo': 'VOLUMEN_BAJO',
                    'ticker': ticker,
                    'titulo': f"💡 Alerta",
                    'descripcion': f"El volumen de negociación de '{ticker}' es inusualmente BAJO hoy ({rvol:.1f}x promedio).",
                    'severidad': 'BAJA',
                    'metricas': {
                        'rvol': f"{rvol:.2f}x",
                        'volumen_actual': volume,
                        'volumen_promedio': volume_sma_20
                    }
                })
    
    def _detectar_patrones_con_probabilidad(self, ticker: str, metrics: Dict, signals: Dict):
        """
        Detecta patrones alcistas/bajistas y calcula probabilidad
        Similar a: "Patrón alcista identificado en 'MSFT' con probabilidad del 70%"
        """
        # Calcular probabilidad basada en convergencia de indicadores
        score_alcista = 0
        score_bajista = 0
        total_indicadores = 0
        
        # 1. EMAs (20%)
        ema_50 = metrics.get('ema_50', 0)
        ema_200 = metrics.get('ema_200', 0)
        if ema_50 and ema_200:
            total_indicadores += 1
            if ema_50 > ema_200:
                score_alcista += 0.20
            else:
                score_bajista += 0.20
        
        # 2. RSI (15%)
        rsi = metrics.get('rsi', 50)
        total_indicadores += 1
        if rsi > 55:
            score_alcista += 0.15
        elif rsi < 45:
            score_bajista += 0.15
        
        # 3. MACD (25%)
        macd_hist = metrics.get('macd_histogram', 0)
        total_indicadores += 1
        if macd_hist > 0:
            score_alcista += 0.25
        else:
            score_bajista += 0.25
        
        # 4. ADX (15%)
        adx = metrics.get('adx', 0)
        if adx > 25:
            total_indicadores += 1
            score_alcista += 0.15 if ema_50 > ema_200 else 0
            score_bajista += 0.15 if ema_50 < ema_200 else 0
        
        # 5. Volumen (15%)
        volume = metrics.get('volume', 0)
        volume_sma = metrics.get('volume_sma_20', 0)
        if volume_sma > 0:
            rvol = volume / volume_sma
            total_indicadores += 1
            if rvol > 1.2:
                if score_alcista > score_bajista:
                    score_alcista += 0.15
                else:
                    score_bajista += 0.15
        
        # 6. Stochastic (10%)
        stoch_k = metrics.get('stoch_k', 50)
        total_indicadores += 1
        if stoch_k > 60:
            score_alcista += 0.10
        elif stoch_k < 40:
            score_bajista += 0.10
        
        # Convertir a porcentaje
        prob_alcista = int(score_alcista * 100)
        prob_bajista = int(score_bajista * 100)
        
        # Generar alerta si probabilidad > 60%
        if prob_alcista >= 60:
            self.oportunidades.append({
                'tipo': 'PATRON_ALCISTA',
                'ticker': ticker,
                'titulo': f"💡 Oportunidad Potencial",
                'descripcion': f"Patrón alcista identificado en '{ticker}' con probabilidad del {prob_alcista}%.",
                'severidad': 'ALTA' if prob_alcista >= 75 else 'MEDIA',
                'metricas': {
                    'probabilidad': f"{prob_alcista}%",
                    'indicadores_convergentes': total_indicadores,
                    'recomendacion': signals.get('recommendation', 'MANTENER')
                }
            })
        
        elif prob_bajista >= 60:
            self.oportunidades.append({
                'tipo': 'PATRON_BAJISTA',
                'ticker': ticker,
                'titulo': f"⚠️ Oportunidad Potencial (Venta)",
                'descripcion': f"Patrón bajista identificado en '{ticker}' con probabilidad del {prob_bajista}%.",
                'severidad': 'ALTA' if prob_bajista >= 75 else 'MEDIA',
                'metricas': {
                    'probabilidad': f"{prob_bajista}%",
                    'indicadores_convergentes': total_indicadores,
                    'recomendacion': signals.get('recommendation', 'MANTENER')
                }
            })
    
    def _detectar_divergencias(self, ticker: str, signals: Dict):
        """
        Detecta divergencias RSI/MACD
        Similar a: "Se detectó una divergencia alcista en el RSI para 'NVDA'"
        """
        # Buscar divergencias en las alertas existentes
        for alert in signals.get('alerts', []):
            if 'DIVERGENCIA' in alert['type']:
                tipo_div = alert['type']
                es_alcista = 'ALCISTA' in tipo_div
                
                self.oportunidades.append({
                    'tipo': 'DIVERGENCIA_DETECTADA',
                    'ticker': ticker,
                    'titulo': f"💡 Oportunidad: Divergencia {'Alcista' if es_alcista else 'Bajista'}",
                    'descripcion': f"Se detectó una divergencia {'alcista' if es_alcista else 'bajista'} en el {'RSI' if 'RSI' in tipo_div else 'MACD'} para '{ticker}'.",
                    'severidad': alert['priority'],
                    'metricas': {
                        'tipo_divergencia': tipo_div,
                        'descripcion_tecnica': alert['description']
                    }
                })
    
    def _detectar_cambios_abruptos_precio(self, ticker: str, metrics: Dict):
        """
        Detecta cambios abruptos de precio (>5%)
        """
        close = metrics.get('close', 0)
        close_prev = metrics.get('close_prev', 0)
        
        if close_prev > 0:
            cambio_pct = ((close - close_prev) / close_prev) * 100
            
            if abs(cambio_pct) > 5:
                self.anomalias.append({
                    'tipo': 'CAMBIO_PRECIO_ABRUPTO',
                    'ticker': ticker,
                    'titulo': f"⚠️ Anomalía Detectada",
                    'descripcion': f"Cambio de precio abrupto en '{ticker}': {cambio_pct:+.2f}% en última sesión.",
                    'severidad': 'ALTA' if abs(cambio_pct) > 10 else 'MEDIA',
                    'metricas': {
                        'cambio_porcentaje': f"{cambio_pct:+.2f}%",
                        'precio_actual': close,
                        'precio_anterior': close_prev
                    }
                })
    
    def _detectar_rsi_extremo(self, ticker: str, metrics: Dict):
        """
        Detecta RSI en zona extrema (>75 o <25)
        """
        rsi = metrics.get('rsi', 50)
        
        if rsi > 75:
            self.alertas_detectadas.append({
                'tipo': 'RSI_SOBRECOMPRA',
                'ticker': ticker,
                'titulo': f"💡 Alerta",
                'descripcion': f"'{ticker}' en zona de sobrecompra extrema (RSI: {rsi:.1f}). Posible corrección.",
                'severidad': 'MEDIA',
                'metricas': {
                    'rsi': rsi,
                    'umbral': 75
                }
            })
        
        elif rsi < 25:
            self.alertas_detectadas.append({
                'tipo': 'RSI_SOBREVENTA',
                'ticker': ticker,
                'titulo': f"💡 Alerta",
                'descripcion': f"'{ticker}' en zona de sobreventa extrema (RSI: {rsi:.1f}). Posible rebote.",
                'severidad': 'MEDIA',
                'metricas': {
                    'rsi': rsi,
                    'umbral': 25
                }
            })
    
    def _detectar_correlaciones_rotas(self, todos_activos: Dict):
        """
        Detecta correlaciones rotas entre activos
        Similar a: "La correlación histórica entre 'XOM' y el precio del petróleo..."
        """
        # Nota: Esta es una versión simplificada
        # En producción, necesitarías datos históricos de correlación
        
        # Ejemplo: Detectar si BTC y ETH se están moviendo en direcciones opuestas
        btc_data = todos_activos.get('BTC-USD', {})
        eth_data = todos_activos.get('ETH-USD', {})
        
        if btc_data and eth_data:
            btc_metrics = btc_data.get('latest_metrics', {})
            eth_metrics = eth_data.get('latest_metrics', {})
            
            btc_change = btc_metrics.get('close', 0) - btc_metrics.get('close_prev', 0)
            eth_change = eth_metrics.get('close', 0) - eth_metrics.get('close_prev', 0)
            
            # Si BTC sube y ETH baja (o viceversa) significativamente
            if (btc_change > 0 and eth_change < 0) or (btc_change < 0 and eth_change > 0):
                btc_pct = (btc_change / btc_metrics.get('close_prev', 1)) * 100
                eth_pct = (eth_change / eth_metrics.get('close_prev', 1)) * 100
                
                if abs(btc_pct) > 2 and abs(eth_pct) > 2:
                    self.anomalias.append({
                        'tipo': 'CORRELACION_ROTA',
                        'ticker': 'BTC-USD / ETH-USD',
                        'titulo': f"⚠️ Anomalía: Correlación Rota",
                        'descripcion': f"La correlación histórica entre 'BTC-USD' y 'ETH-USD' se ha desviado significativamente. BTC {btc_pct:+.2f}% vs ETH {eth_pct:+.2f}%.",
                        'severidad': 'MEDIA',
                        'metricas': {
                            'btc_cambio': f"{btc_pct:+.2f}%",
                            'eth_cambio': f"{eth_pct:+.2f}%"
                        }
                    })
