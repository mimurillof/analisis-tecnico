"""
Tactical Radars - Sistema de 5 Radares Tacticos con Flujo de 3 Fases
Implementa el framework: Regimen -> Radares Tacticos -> Analisis SVGA
Autor: AIDA (Artificial Intelligence Data Architect)
Fecha: 25 de octubre de 2025
Version: 1.0
"""

import sys
import pandas as pd
import numpy as np
import pandas_ta as ta
import yfinance as yf
from typing import List, Dict, Tuple, Optional
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# Configurar encoding UTF-8 para stdout (Windows compatibility)
if sys.platform == 'win32':
    import codecs
    # Solo reconfigurar si stdout tiene buffer (no es ya un TextIOWrapper)
    if hasattr(sys.stdout, 'buffer'):
        sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    if hasattr(sys.stderr, 'buffer'):
        sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')


class TacticalRadarSystem:
    """
    Sistema de radares tácticos que implementa el flujo de 3 fases:
    
    FASE 1: Determinar régimen de mercado (Benchmark)
    FASE 2: Ejecutar radares apropiados según régimen
    FASE 3: Análisis profundo con SVGA
    """
    
    def __init__(self, benchmark: str = "^GSPC"):
        """
        Args:
            benchmark: Ticker del benchmark (default: ^GSPC - S&P 500)
        """
        self.benchmark = benchmark
        self.market_regime = None
        self.regime_signal = None
        self.data = None
        self.tickers = []
        
    def determine_market_regime(self, period: str = "2y") -> Dict:
        """
        FASE 1: Determina el régimen del mercado basado en el benchmark
        
        Args:
            period: Período de análisis del benchmark
            
        Returns:
            Dict con régimen ('ALCISTA', 'BAJISTA', 'LATERAL') y señal
        """
        print("\n" + "="*80)
        print("🌍 FASE 1: DETERMINANDO RÉGIMEN DE MERCADO")
        print("="*80)
        print(f"📊 Analizando benchmark: {self.benchmark}...")
        
        try:
            # Descargar datos del benchmark
            bench_data = yf.download(self.benchmark, period=period, progress=False)
            
            if bench_data.empty:
                raise ValueError("No se pudieron obtener datos del benchmark")
            
            # Aplanar columnas MultiIndex si es necesario (cuando es un solo ticker)
            if isinstance(bench_data.columns, pd.MultiIndex):
                bench_data.columns = [col[0] for col in bench_data.columns]
            
            # Calcular indicadores técnicos con pandas_ta
            # Verificar que hay suficientes datos (mínimo 60 barras para EMA 50 + warm-up)
            if len(bench_data) < 60:
                raise ValueError(f"Datos insuficientes para el benchmark ({len(bench_data)} barras, se necesitan al menos 60)")
            
            # Agregar indicadores usando funciones de pandas_ta directamente
            # CRÍTICO: Extraer como Series (squeeze) para evitar DataFrame
            close = bench_data['Close'].squeeze()
            high = bench_data['High'].squeeze()
            low = bench_data['Low'].squeeze()
            
            # EMAs
            ema50 = ta.ema(close, length=50)
            ema200 = ta.ema(close, length=200)
            
            bench_data['EMA_50'] = ema50
            bench_data['EMA_100'] = ema200
            
            # MACD
            macd_df = ta.macd(close)
            if macd_df is not None and not macd_df.empty:
                bench_data['MACD_12_26_9'] = macd_df['MACD_12_26_9']
                bench_data['MACDs_12_26_9'] = macd_df['MACDs_12_26_9']
                bench_data['MACDh_12_26_9'] = macd_df['MACDh_12_26_9']
            
            # ADX
            adx_df = ta.adx(high, low, close, length=14)
            if adx_df is not None and not adx_df.empty:
                bench_data['ADX_14'] = adx_df['ADX_14']
            
            # RSI
            bench_data['RSI_14'] = ta.rsi(close, length=14)
            
            # Drop NaN (por indicadores que requieren warm-up)
            bench_data = bench_data.dropna()
            
            if bench_data.empty:
                raise ValueError("Todos los datos son NaN después de calcular indicadores")
            
            # Valores actuales
            latest = bench_data.iloc[-1]
            prev = bench_data.iloc[-2]
            
            close = bench_data['Close']
            price = latest['Close']
            ema_50 = latest['EMA_50']
            EMA_100 = latest['EMA_100']
            macd_hist = latest['MACDh_12_26_9']
            adx = latest['ADX_14']
            rsi = latest['RSI_14']
            
            # Determinar régimen con lógica mejorada
            regime = "LATERAL"
            signal = "MANTENER"
            confidence = 0
            reasons = []
            
            # === ANÁLISIS DE TENDENCIA ===
            if price > EMA_100:
                reasons.append(f"✅ Precio sobre EMA 100 (${price:.2f} > ${EMA_100:.2f})")
                confidence += 30
                
                if price > ema_50:
                    reasons.append(f"✅ Precio sobre EMA 50 (${price:.2f} > ${ema_50:.2f})")
                    confidence += 20
                    
                if ema_50 > EMA_100:
                    reasons.append(f"✅ Golden Cross activo (EMA 50 > EMA 100)")
                    confidence += 20
                    regime = "ALCISTA"
                    signal = "COMPRAR"
                    
            elif price < EMA_100:
                reasons.append(f"❌ Precio bajo EMA 100 (${price:.2f} < ${EMA_100:.2f})")
                confidence += 30
                
                if price < ema_50:
                    reasons.append(f"❌ Precio bajo EMA 50 (${price:.2f} < ${ema_50:.2f})")
                    confidence += 20
                    
                if ema_50 < EMA_100:
                    reasons.append(f"❌ Death Cross activo (EMA 50 < EMA 100)")
                    confidence += 20
                    regime = "BAJISTA"
                    signal = "VENDER"
            
            # === ANÁLISIS DE MOMENTUM ===
            if macd_hist > 0:
                reasons.append(f"✅ MACD histograma positivo ({macd_hist:.2f})")
                if regime == "ALCISTA":
                    confidence += 15
            elif macd_hist < 0:
                reasons.append(f"❌ MACD histograma negativo ({macd_hist:.2f})")
                if regime == "BAJISTA":
                    confidence += 15
            
            # === ANÁLISIS DE FUERZA DE TENDENCIA ===
            if adx < 20:
                reasons.append(f"⚠️ ADX débil ({adx:.1f} < 20) - Mercado lateral")
                regime = "LATERAL"
                signal = "MANTENER"
                confidence = max(confidence * 0.5, 40)  # Reducir confianza
            elif adx > 25:
                reasons.append(f"✅ ADX fuerte ({adx:.1f} > 25) - Tendencia confirmada")
                confidence += 15
            
            # Normalizar confianza
            confidence = min(confidence, 100)
            
            # Resultado
            result = {
                'regime': regime,
                'signal': signal,
                'confidence': confidence,
                'benchmark': self.benchmark,
                'price': price,
                'ema_50': ema_50,
                'EMA_100': EMA_100,
                'macd_hist': macd_hist,
                'adx': adx,
                'rsi': rsi,
                'reasons': reasons,
                'timestamp': datetime.now().isoformat()
            }
            
            # Guardar estado
            self.market_regime = regime
            self.regime_signal = signal
            
            # Mostrar resultado
            print(f"\n🎯 RÉGIMEN DE MERCADO: {regime}")
            print(f"📊 SEÑAL: {signal}")
            print(f"💪 CONFIANZA: {confidence:.0f}%")
            print(f"\n📋 ANÁLISIS:")
            for reason in reasons:
                print(f"   {reason}")
            
            print(f"\n📊 Métricas del benchmark:")
            print(f"   Precio actual: ${price:.2f}")
            print(f"   EMA 50: ${ema_50:.2f}")
            print(f"   EMA 100: ${EMA_100:.2f}")
            print(f"   MACD Histograma: {macd_hist:.2f}")
            print(f"   ADX: {adx:.1f}")
            print(f"   RSI: {rsi:.1f}")
            
            # Recomendación de radares
            print(f"\n🎯 RECOMENDACIÓN:")
            if regime == "ALCISTA":
                print(f"   ✅ Ejecutar RADARES ALCISTAS (2A):")
                print(f"      - Radar 1: Reversión a la Media")
                print(f"      - Radar 2: Ignición de Momentum")
            elif regime == "BAJISTA":
                print(f"   ❌ Ejecutar RADARES BAJISTAS (2B):")
                print(f"      - Radar 3: Reversión Bajista")
                print(f"      - Radar 4: Ruptura Bajista")
            else:
                print(f"   ⚠️ Ejecutar RADAR NEUTRAL (2C):")
                print(f"      - Radar 5: Mercado Lateral")
            
            return result
            
        except Exception as e:
            print(f"❌ Error determinando régimen: {e}")
            return {
                'regime': 'UNKNOWN',
                'signal': 'MANTENER',
                'confidence': 0,
                'error': str(e)
            }
    
    def download_universe(self, tickers: List[str], period: str = "6mo") -> bool:
        """
        Descarga datos para el universo de tickers
        
        Args:
            tickers: Lista de tickers a analizar
            period: Período de datos
            
        Returns:
            True si exitoso
        """
        print(f"\n🔽 Descargando {len(tickers)} activos...")
        
        try:
            self.tickers = tickers
            self.data = yf.download(
                tickers,
                period=period,
                group_by='ticker',
                auto_adjust=True,
                progress=False,
                threads=True
            )
            
            if self.data.empty:
                print("❌ No se obtuvieron datos")
                return False
            
            print(f"✅ Descarga completada: {len(self.data)} barras")
            return True
            
        except Exception as e:
            print(f"❌ Error en descarga: {e}")
            return False
    
    def radar_1_reversion_alcista(self, df_metrics: pd.DataFrame) -> pd.DataFrame:
        """
        RADAR 1: Reversión a la Media (Comprar la Caída)
        
        Criterios:
        - Precio > EMA 100 (tendencia alcista)
        - Precio < EMA 50 (retroceso)
        - RSI(14) < 40 (sobreventa)
        """
        print("\n📡 RADAR 1: Reversión a la Media (Comprar la Caída)")
        
        filtered = df_metrics[
            (df_metrics['precio'] > df_metrics['EMA_100']) &
            (df_metrics['precio'] < df_metrics['ema_50']) &
            (df_metrics['rsi'] < 40)
        ].copy()
        
        filtered['radar'] = 'Reversión Alcista'
        filtered['score'] = (
            50 +  # Base
            (40 - filtered['rsi']) * 1.0 +  # Más puntos si más sobrevendido
            ((filtered['EMA_100'] - filtered['precio']) / filtered['precio'] * 100) * 2  # Descuento vs tendencia
        )
        
        print(f"   ✅ {len(filtered)} candidatos encontrados")
        return filtered
    
    def radar_2_ignicion_momentum(self, df_metrics: pd.DataFrame) -> pd.DataFrame:
        """
        RADAR 2: Ignición de Momentum (Comprar la Ruptura)
        
        Criterios:
        - MACD histograma cruzando de negativo a positivo
        - ADX cruzando por encima de 20
        - RSI cruzando por encima de 50
        """
        print("\n📡 RADAR 2: Ignición de Momentum (Comprar la Ruptura)")
        
        filtered = df_metrics[
            (df_metrics['macd_hist'] > 0) &
            (df_metrics['macd_hist'] < 1) &  # Recién cruzó
            (df_metrics['macd_hist_prev'] <= 0) &  # Venía negativo
            (df_metrics['adx'] > 20) &
            (df_metrics['rsi'] > 50)
        ].copy()
        
        filtered['radar'] = 'Ignición Momentum'
        filtered['score'] = (
            60 +  # Base más alta (señal más fuerte)
            (filtered['adx'] - 20) * 1.5 +  # ADX fuerte
            (filtered['rsi'] - 50) * 0.5  # RSI alcista
        )
        
        print(f"   ✅ {len(filtered)} candidatos encontrados")
        return filtered
    
    def radar_3_reversion_bajista(self, df_metrics: pd.DataFrame) -> pd.DataFrame:
        """
        RADAR 3: Reversión Bajista (Vender en la Subida / Short)
        
        Criterios:
        - Precio < EMA 100 (tendencia bajista)
        - Precio > EMA 50 (rebote)
        - RSI(14) > 60 (sobrecompra)
        """
        print("\n📡 RADAR 3: Reversión Bajista (Vender en la Subida)")
        
        filtered = df_metrics[
            (df_metrics['precio'] < df_metrics['EMA_100']) &
            (df_metrics['precio'] > df_metrics['ema_50']) &
            (df_metrics['rsi'] > 60)
        ].copy()
        
        filtered['radar'] = 'Reversión Bajista'
        filtered['score'] = (
            50 +
            (filtered['rsi'] - 60) * 1.0 +
            ((filtered['precio'] - filtered['EMA_100']) / filtered['precio'] * 100) * 2
        )
        
        print(f"   ✅ {len(filtered)} candidatos encontrados")
        return filtered
    
    def radar_4_ruptura_bajista(self, df_metrics: pd.DataFrame) -> pd.DataFrame:
        """
        RADAR 4: Ruptura Bajista (Vender la Caída / Short)
        
        Criterios:
        - MACD histograma cruzando de positivo a negativo
        - ADX cruzando por encima de 20
        - RSI cruzando por debajo de 50
        """
        print("\n📡 RADAR 4: Ruptura Bajista (Vender la Caída)")
        
        filtered = df_metrics[
            (df_metrics['macd_hist'] < 0) &
            (df_metrics['macd_hist'] > -1) &  # Recién cruzó
            (df_metrics['macd_hist_prev'] >= 0) &  # Venía positivo
            (df_metrics['adx'] > 20) &
            (df_metrics['rsi'] < 50)
        ].copy()
        
        filtered['radar'] = 'Ruptura Bajista'
        filtered['score'] = (
            60 +
            (filtered['adx'] - 20) * 1.5 +
            (50 - filtered['rsi']) * 0.5
        )
        
        print(f"   ✅ {len(filtered)} candidatos encontrados")
        return filtered
    
    def radar_5_mercado_lateral(self, df_metrics: pd.DataFrame) -> pd.DataFrame:
        """
        RADAR 5: Mercado Lateral (Operar el Rango)
        
        Criterios:
        - ADX < 20 (sin tendencia)
        - RSI oscilando entre 35 y 65
        - Precio cruzando EMAs frecuentemente
        """
        print("\n📡 RADAR 5: Mercado Lateral (Operar el Rango)")
        
        filtered = df_metrics[
            (df_metrics['adx'] < 20) &
            (df_metrics['rsi'] > 35) &
            (df_metrics['rsi'] < 65)
        ].copy()
        
        # Detectar cruces de EMAs (indicador de rango)
        filtered['ema_crosses'] = (
            ((filtered['precio'] > filtered['ema_20']) & (filtered['precio_prev'] <= filtered['ema_20_prev'])) |
            ((filtered['precio'] < filtered['ema_20']) & (filtered['precio_prev'] >= filtered['ema_20_prev']))
        ).astype(int)
        
        filtered['radar'] = 'Mercado Lateral'
        filtered['score'] = (
            40 +  # Base más baja (oportunidad más limitada)
            (20 - filtered['adx']) * 2 +  # Más lateral = más puntos
            abs(50 - filtered['rsi']) * -0.5 +  # Cerca del medio = mejor
            filtered['ema_crosses'] * 10  # Cruces frecuentes
        )
        
        print(f"   ✅ {len(filtered)} candidatos encontrados")
        return filtered
    
    def calculate_tactical_metrics(self) -> pd.DataFrame:
        """
        Calcula todas las métricas necesarias para los 5 radares
        Usa pandas_ta para cálculos eficientes
        """
        print("\n🧮 Calculando métricas tácticas...")
        
        metrics = []
        
        for ticker in self.tickers:
            try:
                # Extraer datos del ticker
                if len(self.tickers) == 1:
                    ticker_data = self.data
                else:
                    ticker_data = self.data[ticker]
                
                if ticker_data.empty or len(ticker_data) < 80:
                    continue
                
                df = ticker_data.copy()
                data_len = len(df)
                # CRÍTICO: Extraer como Series (squeeze) para evitar DataFrame
                close = df['Close'].squeeze()
                high = df['High'].squeeze()
                low = df['Low'].squeeze()
                volume_series = df['Volume'].squeeze() if 'Volume' in df.columns else None

                # Ajustar dinámicamente las ventanas según la longitud disponible
                ema20_len = min(20, data_len) if data_len >= 5 else data_len
                ema50_len = min(50, data_len) if data_len >= 20 else max(10, data_len // 2)
                if data_len >= 120:
                    ema100_len = 100
                else:
                    ema100_len = max(ema50_len, int(data_len * 0.6))
                    ema100_len = max(ema100_len, 30)
                    ema100_len = min(ema100_len, data_len)
                
                # === CALCULAR INDICADORES CON PANDAS_TA ===
                
                # EMAs (usar longitudes adaptativas para evitar DataFrames vacíos en historiales cortos)
                df['EMA_20'] = ta.ema(close, length=ema20_len)
                df['EMA_50'] = ta.ema(close, length=ema50_len)
                df['EMA_100'] = ta.ema(close, length=ema100_len)
                
                # RSI
                df['RSI'] = ta.rsi(close, length=14)
                
                # MACD
                macd_df = ta.macd(close)
                if macd_df is not None and not macd_df.empty:
                    df['MACD'] = macd_df['MACD_12_26_9']
                    df['MACD_signal'] = macd_df['MACDs_12_26_9']
                    df['MACD_hist'] = macd_df['MACDh_12_26_9']
                else:
                    df['MACD'] = 0
                    df['MACD_signal'] = 0
                    df['MACD_hist'] = 0
                
                # ADX
                adx_df = ta.adx(high, low, close, length=14)
                if adx_df is not None and not adx_df.empty:
                    df['ADX'] = adx_df['ADX_14']
                else:
                    df['ADX'] = 20  # Valor neutral

                if volume_series is not None:
                    df['VOLUME_SMA_20'] = ta.sma(volume_series, length=min(20, data_len))
                
                # Drop NaN
                df = df.dropna()
                
                if df.empty or len(df) < 2:
                    continue
                
                # Valores actuales y anteriores
                latest = df.iloc[-1]
                prev = df.iloc[-2]
                
                metrics.append({
                    'ticker': ticker,
                    'precio': latest['Close'],
                    'precio_prev': prev['Close'],
                    'ema_20': latest['EMA_20'],
                    'ema_20_prev': prev['EMA_20'],
                    'ema_50': latest['EMA_50'],
                    'EMA_100': latest['EMA_100'],
                    'rsi': latest['RSI'],
                    'macd_hist': latest['MACD_hist'],
                    'macd_hist_prev': prev['MACD_hist'],
                    'adx': latest['ADX'],
                    'volume': latest['Volume'] if 'Volume' in latest else 0,
                    'volume_sma_20': latest.get('VOLUME_SMA_20', 0)
                })
                
            except Exception as e:
                continue
        
        df_metrics = pd.DataFrame(metrics)
        print(f"✅ Métricas calculadas para {len(df_metrics)} activos")
        
        return df_metrics
    
    def run_tactical_scan(self, tickers: List[str], period: str = "6mo", 
                          max_candidates: int = 15) -> Tuple[List[str], pd.DataFrame, str]:
        """
        Ejecuta el flujo completo de 3 fases
        
        FASE 1: Determinar régimen
        FASE 2: Ejecutar radares apropiados
        FASE 3: Retornar candidatos para SVGA
        
        Args:
            tickers: Lista de tickers a escanear
            period: Período de datos
            max_candidates: Máximo de candidatos a retornar
            
        Returns:
            Tupla (candidatos, métricas completas, radar_usado)
        """
        print("\n" + "="*80)
        print("🚀 SISTEMA DE RADARES TÁCTICOS - FLUJO DE 3 FASES")
        print("="*80)
        
        # === FASE 1: RÉGIMEN ===
        # Determinar régimen SIEMPRE con 2 años de datos (independiente del período de escaneo)
        regime_info = self.determine_market_regime(period="2y")
        regime = regime_info['regime']
        
        if regime == 'UNKNOWN':
            print("❌ No se pudo determinar el régimen. Abortando.")
            return [], pd.DataFrame(), 'NONE'
        
        # === FASE 2: DESCARGAR Y CALCULAR ===
        print("\n" + "="*80)
        print("📡 FASE 2: PROSPECCIÓN TÁCTICA")
        print("="*80)
        
        # Usar período más corto para escaneo (6 meses = ~126 días hábiles)
        # Suficiente para EMA 100 (no EMA 100)
        if not self.download_universe(tickers, period=period):
            return [], pd.DataFrame(), 'NONE'
        
        df_metrics = self.calculate_tactical_metrics()
        
        if df_metrics.empty:
            print("❌ No se pudieron calcular métricas")
            return [], df_metrics, 'NONE'
        
        # === EJECUTAR RADARES APROPIADOS SEGÚN RÉGIMEN ===
        all_candidates = pd.DataFrame()
        radars_used = []
        
        if regime == "ALCISTA":
            print(f"\n🟢 Régimen ALCISTA detectado - Ejecutando Radares 1 y 2...")
            
            # Radar 1: Reversión a la Media
            radar1_results = self.radar_1_reversion_alcista(df_metrics)
            if not radar1_results.empty:
                all_candidates = pd.concat([all_candidates, radar1_results])
                radars_used.append("Radar 1 (Reversión Alcista)")
            
            # Radar 2: Ignición de Momentum
            radar2_results = self.radar_2_ignicion_momentum(df_metrics)
            if not radar2_results.empty:
                all_candidates = pd.concat([all_candidates, radar2_results])
                radars_used.append("Radar 2 (Ignición Momentum)")
        
        elif regime == "BAJISTA":
            print(f"\n🔴 Régimen BAJISTA detectado - Ejecutando Radares 3 y 4...")
            
            # Radar 3: Reversión Bajista
            radar3_results = self.radar_3_reversion_bajista(df_metrics)
            if not radar3_results.empty:
                all_candidates = pd.concat([all_candidates, radar3_results])
                radars_used.append("Radar 3 (Reversión Bajista)")
            
            # Radar 4: Ruptura Bajista
            radar4_results = self.radar_4_ruptura_bajista(df_metrics)
            if not radar4_results.empty:
                all_candidates = pd.concat([all_candidates, radar4_results])
                radars_used.append("Radar 4 (Ruptura Bajista)")
        
        else:  # LATERAL
            print(f"\n🟡 Régimen LATERAL detectado - Ejecutando Radar 5...")
            
            # Radar 5: Mercado Lateral
            radar5_results = self.radar_5_mercado_lateral(df_metrics)
            if not radar5_results.empty:
                all_candidates = pd.concat([all_candidates, radar5_results])
                radars_used.append("Radar 5 (Mercado Lateral)")
        
        # === CONSOLIDAR Y ORDENAR ===
        if all_candidates.empty:
            print("\n⚠️ No se encontraron candidatos con los criterios actuales")
            return [], df_metrics, ', '.join(radars_used) if radars_used else 'NONE'
        
        # Ordenar por score y limitar
        all_candidates = all_candidates.sort_values('score', ascending=False).head(max_candidates)
        
        # Mostrar resultados
        print(f"\n" + "="*80)
        print(f"🎯 RESULTADOS DE RADARES TÁCTICOS")
        print("="*80)
        print(f"📊 Radares ejecutados: {', '.join(radars_used)}")
        print(f"🏆 Total de candidatos: {len(all_candidates)}")
        print(f"\n🏆 Top {min(15, len(all_candidates))} candidatos:")
        
        for i, (idx, row) in enumerate(all_candidates.head(15).iterrows(), 1):
            print(f"   {i:2}. {row['ticker']:8} | Radar: {row['radar']:20} | "
                  f"Score: {row['score']:5.1f} | Precio: ${row['precio']:8.2f} | "
                  f"RSI: {row['rsi']:5.1f} | ADX: {row['adx']:5.1f}")
        
        candidates_list = all_candidates['ticker'].tolist()
        
        print("\n" + "="*80)
        print(f"✅ FASE 2 COMPLETADA - {len(candidates_list)} candidatos listos para SVGA")
        print("="*80)
        
        return candidates_list, all_candidates, ', '.join(radars_used)


def test_tactical_system():
    """Prueba el sistema táctico con S&P 500"""
    
    print("TEST DEL SISTEMA DE RADARES TACTICOS\n")
    
    # Crear sistema
    tactical = TacticalRadarSystem(benchmark="^GSPC")
    
    # Lista de prueba (S&P 500 Top 50)
    test_tickers = [
        'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA', 'META', 'TSLA', 'BRK-B',
        'JPM', 'V', 'MA', 'UNH', 'JNJ', 'LLY', 'XOM', 'WMT',
        'PG', 'HD', 'COST', 'BAC', 'ABBV', 'CVX', 'MRK', 'KO',
        'PEP', 'AVGO', 'MCD', 'TMO', 'CSCO', 'ABT', 'ORCL', 'CRM',
        'NKE', 'ACN', 'DHR', 'INTC', 'AMD', 'TXN', 'CMCSA', 'NEE',
        'PM', 'DIS', 'VZ', 'ADBE', 'NFLX', 'COP', 'RTX', 'HON',
        'IBM', 'QCOM'
    ]
    
    # Ejecutar flujo completo
    candidates, metrics, radars = tactical.run_tactical_scan(
        tickers=test_tickers,
        period="6mo",
        max_candidates=15
    )
    
    print(f"\n📊 RESUMEN FINAL:")
    print(f"   Régimen: {tactical.market_regime}")
    print(f"   Señal: {tactical.regime_signal}")
    print(f"   Radares usados: {radars}")
    print(f"   Candidatos encontrados: {len(candidates)}")
    print(f"\n📋 Candidatos para SVGA:")
    for i, ticker in enumerate(candidates, 1):
        print(f"   {i}. {ticker}")


if __name__ == "__main__":
    test_tactical_system()

