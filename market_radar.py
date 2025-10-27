"""
Market Radar - Sistema de Escaneo Eficiente de Mercados v5.0
Implementa descarga en lote, scoring multi-factor y contexto de sentimiento
Autor: AIDA (Artificial Intelligence Data Architect)
Fecha: 25 de octubre de 2025
Versión 5.0 - Mejoras:
- Sistema de scoring 0-100 para priorizar candidatos
- Integración con sentimiento crypto (Fear & Greed)
- Clasificación por niveles de confianza
"""

import pandas as pd
import numpy as np
import yfinance as yf
from typing import List, Dict, Tuple, Optional
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# Importar contexto de mercado (Opción B: solo sentimiento)
try:
    from market_context import SentimentAnalyzer
    SENTIMENT_AVAILABLE = True
except ImportError:
    SENTIMENT_AVAILABLE = False
    print("⚠️ market_context.py no disponible. Ejecutando sin sentimiento.")


class MarketRadar:
    """
    Sistema de escaneo de mercado en dos fases para identificar oportunidades
    v5.0: Añade scoring multi-factor y contexto de sentimiento
    """
    
    def __init__(self, universe: str = "sp500"):
        """
        Inicializa el radar de mercado
        
        Args:
            universe: Universo de activos ('sp500', 'nasdaq100', 'crypto100', 'custom')
        """
        self.universe = universe
        self.tickers = []
        self.data = None
        self.candidates = []
        self.sentiment_context = None  # Nuevo: contexto de sentimiento
        
        # Inicializar analizador de sentimiento si disponible
        if SENTIMENT_AVAILABLE:
            try:
                self.sentiment_analyzer = SentimentAnalyzer()
            except Exception as e:
                print(f"⚠️ Error inicializando SentimentAnalyzer: {e}")
                self.sentiment_analyzer = None
        else:
            self.sentiment_analyzer = None
        
    def get_sp500_tickers(self) -> List[str]:
        """
        Obtiene lista de tickers del S&P 500 desde múltiples fuentes
        """
        print("📡 Obteniendo lista de S&P 500...")
        
        # Intento 1: Wikipedia con headers personalizados
        try:
            import requests
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            url = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'
            response = requests.get(url, headers=headers)
            tables = pd.read_html(response.text)
            sp500_table = tables[0]
            tickers = sp500_table['Symbol'].str.replace('.', '-', regex=False).tolist()
            print(f"✅ {len(tickers)} tickers obtenidos del S&P 500 (Wikipedia)")
            return tickers
        except Exception as e:
            print(f"⚠️ Wikipedia falló: {e}")
        
        # Intento 2: Lista curada completa (Top 100 del S&P 500 por capitalización)
        print("📡 Usando lista curada del S&P 500 Top 100...")
        sp500_top100 = [
            # Mega Cap Tech
            'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA', 'META', 'TSLA', 'BRK-B',
            # Tech & Software
            'AVGO', 'ORCL', 'ADBE', 'CRM', 'CSCO', 'INTC', 'AMD', 'QCOM', 'TXN',
            'IBM', 'INTU', 'NOW', 'PANW', 'AMAT', 'MU', 'ADI', 'LRCX', 'KLAC',
            # Finance
            'JPM', 'V', 'MA', 'BAC', 'WFC', 'GS', 'MS', 'BX', 'SPGI', 'AXP',
            'C', 'SCHW', 'BLK', 'CB', 'MMC', 'PGR', 'AIG', 'MET', 'TRV',
            # Healthcare
            'UNH', 'JNJ', 'LLY', 'ABBV', 'MRK', 'PFE', 'TMO', 'ABT', 'DHR',
            'CVS', 'AMGN', 'BMY', 'GILD', 'CI', 'ELV', 'MDT', 'REGN', 'ISRG',
            # Consumer
            'WMT', 'HD', 'COST', 'PG', 'KO', 'PEP', 'MCD', 'NKE', 'SBUX',
            'TGT', 'LOW', 'TJX', 'DIS', 'CMCSA', 'NFLX', 'PM', 'MO',
            # Energy
            'XOM', 'CVX', 'COP', 'SLB', 'EOG', 'PXD', 'MPC', 'PSX', 'VLO',
            # Industrial
            'BA', 'CAT', 'HON', 'UPS', 'RTX', 'GE', 'LMT', 'DE', 'MMM',
            # Other
            'TSLA', 'NEE', 'DUK', 'SO', 'AEP', 'EXC'
        ]
        print(f"✅ {len(sp500_top100)} tickers del S&P 500 Top 100 cargados")
        return sp500_top100
    
    def get_nasdaq100_tickers(self) -> List[str]:
        """
        Obtiene lista de tickers del NASDAQ 100
        """
        print("📡 Obteniendo lista de NASDAQ 100...")
        try:
            url = 'https://en.wikipedia.org/wiki/Nasdaq-100'
            tables = pd.read_html(url)
            nasdaq_table = tables[4]  # La tabla de componentes suele ser la 4ta
            tickers = nasdaq_table['Ticker'].str.replace('.', '-', regex=False).tolist()
            print(f"✅ {len(tickers)} tickers obtenidos del NASDAQ 100")
            return tickers
        except Exception as e:
            print(f"⚠️ Error obteniendo NASDAQ 100: {e}")
            return ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA', 'META', 'TSLA']
    
    def get_crypto_tickers(self, top_n: int = 50) -> List[str]:
        """
        Genera lista de tickers de criptomonedas principales
        
        Args:
            top_n: Número de criptos principales a incluir
        """
        print(f"📡 Generando lista de Top {top_n} Crypto...")
        # Lista curada de las principales criptomonedas en yfinance (ordenadas por liquidez)
        # NOTA: APT-USD, MATIC-USD, UNI-USD eliminados (delisted o sin datos)
        crypto_list = [
            'BTC-USD', 'ETH-USD', 'BNB-USD', 'XRP-USD', 'ADA-USD',
            'DOGE-USD', 'SOL-USD', 'TRX-USD', 'DOT-USD', 'LTC-USD',
            'SHIB-USD', 'AVAX-USD', 'LINK-USD', 'XLM-USD', 'ATOM-USD',
            'ETC-USD', 'BCH-USD', 'ALGO-USD', 'NEAR-USD', 'FIL-USD',
            'VET-USD', 'ICP-USD', 'HBAR-USD', 'QNT-USD', 'OP-USD',
            'ARB-USD', 'MKR-USD', 'AAVE-USD', 'SAND-USD', 'MANA-USD',
            'AXS-USD', 'FTM-USD', 'RUNE-USD', 'EGLD-USD', 'XTZ-USD',
            'THETA-USD', 'EOS-USD', 'KLAY-USD', 'ZEC-USD', 'NEO-USD',
            'BAT-USD', 'DASH-USD', 'COMP-USD', 'YFI-USD', 'SNX-USD',
            'CRV-USD', 'SUSHI-USD', 'CAKE-USD', '1INCH-USD', 'INJ-USD',
            'STX-USD', 'GMX-USD', 'TIA-USD', 'PYTH-USD', 'WND-USD'
        ]
        tickers = crypto_list[:top_n]
        print(f"✅ {len(tickers)} criptomonedas seleccionadas")
        return tickers
    
    def get_crypto30_tickers(self) -> List[str]:
        """
        Obtiene Top 30 criptos más líquidas (optimizado para escaneo rápido)
        """
        return self.get_crypto_tickers(top_n=30)
    
    def _get_fallback_tickers(self) -> List[str]:
        """Lista de respaldo de tickers de alta liquidez"""
        return [
            # Tech Giants
            'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA', 'META', 'TSLA',
            # Finance
            'JPM', 'BAC', 'WFC', 'GS', 'MS',
            # Healthcare
            'JNJ', 'UNH', 'PFE', 'ABBV', 'LLY',
            # Energy
            'XOM', 'CVX', 'COP', 'SLB',
            # Consumer
            'WMT', 'HD', 'MCD', 'NKE', 'SBUX',
            # Industrial
            'CAT', 'BA', 'GE', 'HON',
            # Communication
            'DIS', 'NFLX', 'CMCSA', 'VZ'
        ]
    
    def load_universe(self, custom_tickers: Optional[List[str]] = None):
        """
        Carga el universo de tickers a escanear
        
        Args:
            custom_tickers: Lista personalizada de tickers (si universe='custom')
        """
        if self.universe == "sp500":
            self.tickers = self.get_sp500_tickers()
        elif self.universe == "nasdaq100":
            self.tickers = self.get_nasdaq100_tickers()
        elif self.universe == "crypto100":
            self.tickers = self.get_crypto_tickers(top_n=100)
        elif self.universe == "crypto50":
            self.tickers = self.get_crypto_tickers(top_n=50)
        elif self.universe == "crypto30":
            self.tickers = self.get_crypto30_tickers()
        elif self.universe == "custom" and custom_tickers:
            self.tickers = custom_tickers
            print(f"✅ {len(self.tickers)} tickers personalizados cargados")
        else:
            print("⚠️ Universo no reconocido. Usando lista de respaldo.")
            self.tickers = self._get_fallback_tickers()
    
    def download_batch_optimized(self, period: str = "6mo", interval: str = "1d", batch_size: int = 100) -> bool:
        """
        Descarga datos en batches más pequeños para evitar sobrecarga
        OPTIMIZACIÓN: Reduce la carga en la API descargando en lotes
        
        Args:
            period: Período de datos (3mo, 6mo, 1y, 2y)
            interval: Intervalo (1d, 1wk)
            batch_size: Tamaño de cada batch (default: 100 tickers por batch)
        
        Returns:
            True si descarga exitosa
        """
        print(f"\n🔽 Descargando {len(self.tickers)} activos en batches de {batch_size}...")
        print(f"   Período: {period} | Intervalo: {interval}")
        
        try:
            # Dividir tickers en batches
            total_tickers = len(self.tickers)
            num_batches = (total_tickers + batch_size - 1) // batch_size
            
            all_data = []
            successful_tickers = []
            
            for batch_idx in range(num_batches):
                start_idx = batch_idx * batch_size
                end_idx = min((batch_idx + 1) * batch_size, total_tickers)
                batch_tickers = self.tickers[start_idx:end_idx]
                
                print(f"   📦 Batch {batch_idx + 1}/{num_batches}: {len(batch_tickers)} tickers...")
                
                # Descargar batch
                batch_data = yf.download(
                    batch_tickers, 
                    period=period, 
                    interval=interval,
                    group_by='ticker',
                    auto_adjust=True,
                    progress=False,
                    threads=True
                )
                
                if not batch_data.empty:
                    all_data.append(batch_data)
                    successful_tickers.extend(batch_tickers)
            
            # Combinar todos los batches
            if all_data:
                if len(all_data) == 1:
                    self.data = all_data[0]
                else:
                    self.data = pd.concat(all_data, axis=1)
                
                # Actualizar lista de tickers a solo los exitosos
                self.tickers = successful_tickers
                
                print(f"✅ Descarga completada: {len(self.data)} barras × {len(self.tickers)} activos")
                return True
            else:
                print("❌ No se obtuvieron datos en ningún batch")
                return False
            
        except Exception as e:
            print(f"❌ Error en descarga optimizada: {e}")
            return False
    
    def download_batch(self, period: str = "6mo", interval: str = "1d") -> bool:
        """
        Descarga datos de todos los tickers en UNA SOLA llamada (eficiencia crítica)
        
        Args:
            period: Período de datos (3mo, 6mo, 1y, 2y)
            interval: Intervalo (1d, 1wk)
        
        Returns:
            True si descarga exitosa
        """
        print(f"\n🔽 Descargando {len(self.tickers)} activos en lote...")
        print(f"   Período: {period} | Intervalo: {interval}")
        
        try:
            # CLAVE: Una sola llamada a yf.download para TODOS los tickers
            self.data = yf.download(
                self.tickers, 
                period=period, 
                interval=interval,
                group_by='ticker',
                auto_adjust=True,
                progress=False,
                threads=True  # Descarga paralela interna
            )
            
            if self.data.empty:
                print("❌ No se obtuvieron datos")
                return False
            
            print(f"✅ Descarga completada: {len(self.data)} barras × {len(self.tickers)} activos")
            return True
            
        except Exception as e:
            print(f"❌ Error en descarga batch: {e}")
            return False
    
    def calculate_radar_metrics(self) -> pd.DataFrame:
        """
        Calcula métricas de escaneo vectorizadas (sin bucles)
        
        Returns:
            DataFrame con métricas por ticker
        """
        print("\n🧮 Calculando métricas del radar...")
        
        metrics = []
        
        for ticker in self.tickers:
            try:
                # Extraer datos del ticker
                if len(self.tickers) == 1:
                    ticker_data = self.data
                else:
                    ticker_data = self.data[ticker]
                
                if ticker_data.empty or len(ticker_data) < 50:
                    continue
                
                # Datos básicos
                close = ticker_data['Close']
                volume = ticker_data['Volume']
                high = ticker_data['High']
                low = ticker_data['Low']
                
                # Último precio
                latest_close = close.iloc[-1]
                prev_close = close.iloc[-2]
                
                # === FILTRO 1: VOLUMEN RELATIVO (RVOL) ===
                avg_volume_20 = volume.rolling(20).mean().iloc[-1]
                latest_volume = volume.iloc[-1]
                rvol = latest_volume / avg_volume_20 if avg_volume_20 > 0 else 0
                
                # === FILTRO 2: MEDIAS MÓVILES ===
                sma_20 = close.rolling(20).mean().iloc[-1]
                sma_50 = close.rolling(50).mean().iloc[-1]
                sma_200 = close.rolling(200).mean().iloc[-1] if len(close) >= 200 else np.nan
                
                # Cruce de medias (Golden Cross / Death Cross)
                cross_signal = 0
                if not np.isnan(sma_200):
                    if sma_50 > sma_200 and close.rolling(50).mean().iloc[-2] <= close.rolling(200).mean().iloc[-2]:
                        cross_signal = 1  # Golden Cross
                    elif sma_50 < sma_200 and close.rolling(50).mean().iloc[-2] >= close.rolling(200).mean().iloc[-2]:
                        cross_signal = -1  # Death Cross
                
                # === FILTRO 3: RUPTURA DE RANGO (BREAKOUT) ===
                high_20 = high.rolling(20).max().iloc[-2]  # Máximo previo de 20 días
                low_20 = low.rolling(20).min().iloc[-2]
                
                breakout_up = latest_close > high_20
                breakout_down = latest_close < low_20
                
                # === FILTRO 4: MOMENTUM (RATE OF CHANGE) ===
                roc_10 = ((latest_close - close.iloc[-11]) / close.iloc[-11] * 100) if len(close) > 10 else 0
                
                # === FILTRO 5: VOLATILIDAD (ATR RELATIVO) ===
                tr = pd.DataFrame({
                    'hl': high - low,
                    'hc': abs(high - close.shift()),
                    'lc': abs(low - close.shift())
                }).max(axis=1)
                atr_14 = tr.rolling(14).mean().iloc[-1]
                atr_percent = (atr_14 / latest_close * 100) if latest_close > 0 else 0
                
                # Construir registro de métricas
                metrics.append({
                    'ticker': ticker,
                    'price': latest_close,
                    'price_change_pct': ((latest_close - prev_close) / prev_close * 100),
                    'volume': latest_volume,
                    'rvol': rvol,
                    'sma_20': sma_20,
                    'sma_50': sma_50,
                    'sma_200': sma_200,
                    'above_sma50': latest_close > sma_50,
                    'above_sma200': latest_close > sma_200 if not np.isnan(sma_200) else False,
                    'golden_cross': cross_signal == 1,
                    'death_cross': cross_signal == -1,
                    'breakout_up': breakout_up,
                    'breakout_down': breakout_down,
                    'roc_10d': roc_10,
                    'atr_percent': atr_percent,
                    'high_volume': rvol > 2.0,
                    'strong_momentum': roc_10 > 5.0
                })
                
            except Exception as e:
                # Silenciar errores individuales para no interrumpir el escaneo
                continue
        
        df_metrics = pd.DataFrame(metrics)
        print(f"✅ Métricas calculadas para {len(df_metrics)} activos")
        
        return df_metrics
    
    def apply_filters(self, df_metrics: pd.DataFrame, strategy: str = "momentum") -> List[str]:
        """
        Aplica filtros estratégicos para identificar candidatos
        MEJORADO: Filtros más sensibles para detectar más oportunidades
        
        Args:
            df_metrics: DataFrame con métricas calculadas
            strategy: Estrategia de filtrado ('momentum', 'breakout', 'value', 'mixed')
        
        Returns:
            Lista de tickers candidatos
        """
        print(f"\n🎯 Aplicando estrategia de filtrado: '{strategy.upper()}'")
        
        if strategy == "momentum":
            # Estrategia de Momentum MEJORADA: Más sensible
            filtered = df_metrics[
                (df_metrics['above_sma50'] == True) &  # Sobre media 50
                (
                    (df_metrics['roc_10d'] > 3.0) |  # Momentum moderado O
                    (df_metrics['rvol'] > 1.5)       # Alto volumen relativo
                )
            ]
            
        elif strategy == "breakout":
            # Estrategia de Ruptura MEJORADA: Menos restrictiva
            filtered = df_metrics[
                (
                    (df_metrics['breakout_up'] == True) |  # Ruptura O
                    (df_metrics['price_change_pct'] > 3.0)  # Cambio fuerte de precio
                ) &
                (df_metrics['rvol'] > 1.2)  # Volumen mínimo
            ]
            
        elif strategy == "golden_cross":
            # Estrategia de Cruce Dorado
            filtered = df_metrics[
                (df_metrics['golden_cross'] == True) &
                (df_metrics['rvol'] > 1.0)
            ]
            
        elif strategy == "value":
            # Estrategia de Valor MEJORADA: Busca reversiones
            filtered = df_metrics[
                (
                    (df_metrics['above_sma50'] == False) &  # Debajo de media
                    (df_metrics['roc_10d'] > -5.0) &         # No caída fuerte
                    (df_metrics['roc_10d'] < 3.0)            # Comenzando a subir
                ) |
                (
                    (df_metrics['above_sma50'] == True) &   # O sobre media
                    (df_metrics['roc_10d'] > 0) &            # Momentum positivo
                    (df_metrics['rvol'] > 1.3)               # Volumen
                )
            ]
            
        elif strategy == "mixed":
            # Estrategia Mixta MEJORADA: Combina múltiples señales con menos restricciones
            filtered = df_metrics[
                (
                    # Opción 1: Tendencia alcista con volumen
                    ((df_metrics['above_sma50'] == True) & (df_metrics['rvol'] > 1.2)) |
                    
                    # Opción 2: Ruptura
                    (df_metrics['breakout_up'] == True) |
                    
                    # Opción 3: Golden cross
                    (df_metrics['golden_cross'] == True) |
                    
                    # Opción 4: Momentum fuerte
                    ((df_metrics['roc_10d'] > 5.0) & (df_metrics['rvol'] > 1.0)) |
                    
                    # Opción 5: Cambio de precio significativo
                    (df_metrics['price_change_pct'] > 3.0)
                )
            ]
            
        else:
            print(f"⚠️ Estrategia '{strategy}' no reconocida. Usando 'mixed'.")
            return self.apply_filters(df_metrics, strategy="mixed")
        
        candidates = filtered['ticker'].tolist()
        print(f"✅ {len(candidates)} candidatos identificados")
        
        # Ordenar por fuerza (combinación de métricas)
        if len(filtered) > 0:
            # Sistema de scoring mejorado
            filtered['score'] = (
                filtered['rvol'] * 0.25 +                              # Volumen relativo
                filtered['roc_10d'].clip(-10, 20) * 0.35 +             # ROC (limitado)
                (filtered['above_sma50'].astype(int) * 8) +            # Sobre SMA 50
                (filtered['above_sma200'].astype(int) * 12) +          # Sobre SMA 200
                (filtered['breakout_up'].astype(int) * 15) +           # Ruptura
                (filtered['golden_cross'].astype(int) * 20) +          # Golden Cross
                (filtered['price_change_pct'].clip(-5, 10) * 0.5)      # Cambio de precio
            )
            filtered_sorted = filtered.sort_values('score', ascending=False)
            candidates = filtered_sorted['ticker'].tolist()
            
            # Mostrar top candidatos
            top_to_show = min(15, len(filtered_sorted))
            print(f"\n🏆 Top {top_to_show} candidatos por score:")
            for i, (idx, row) in enumerate(filtered_sorted.head(top_to_show).iterrows(), 1):
                print(f"   {i:2}. {row['ticker']:8} | Score: {row['score']:6.2f} | "
                      f"Precio: ${row['price']:8.2f} | RVOL: {row['rvol']:4.2f}x | "
                      f"ROC: {row['roc_10d']:+6.2f}% | Cambio: {row['price_change_pct']:+5.2f}%")
        
        return candidates
    
    def calculate_candidate_score(self, df_metrics: pd.DataFrame) -> pd.DataFrame:
        """
        Calcula score 0-100 para cada candidato (Opción B: scoring simplificado)
        Combina factores técnicos + sentimiento crypto
        
        Args:
            df_metrics: DataFrame con métricas calculadas
            
        Returns:
            DataFrame con columna 'score' añadida
        """
        print("\n📊 Calculando scores de candidatos...")
        
        # Obtener sentimiento si está disponible
        sentiment_boost = 0
        sentiment_info = "N/A"
        
        if self.sentiment_analyzer:
            try:
                # Para crypto, usar sentimiento crypto
                if 'crypto' in self.universe.lower():
                    sentiment = self.sentiment_analyzer.get_fear_greed_crypto()
                else:
                    # Para stocks, intentar sentimiento stocks (puede fallar por anti-bot)
                    try:
                        sentiment = self.sentiment_analyzer.get_fear_greed_stocks()
                    except:
                        # Fallback a crypto como proxy general
                        sentiment = self.sentiment_analyzer.get_fear_greed_crypto()
                
                sentiment_value = sentiment['value']
                sentiment_class = sentiment['classification']
                sentiment_info = f"{sentiment_value} ({sentiment_class})"
                
                # Ajustar score basado en sentimiento
                if sentiment_value < 25:  # Extreme Fear
                    sentiment_boost = 10  # Oportunidad contrarian
                elif sentiment_value < 40:  # Fear
                    sentiment_boost = 5
                elif sentiment_value > 75:  # Extreme Greed
                    sentiment_boost = -10  # Ser más conservador
                elif sentiment_value > 60:  # Greed
                    sentiment_boost = -5
                
                print(f"   Sentimiento del mercado: {sentiment_info}")
                print(f"   Ajuste de score: {sentiment_boost:+d} puntos")
                
                # Guardar contexto
                self.sentiment_context = sentiment
                
            except Exception as e:
                print(f"   ⚠️ No se pudo obtener sentimiento: {e}")
        
        # === CÁLCULO DE SCORE BASE (0-90 puntos) ===
        df_metrics['score_base'] = 0.0
        
        # MOMENTUM (0-25 puntos)
        df_metrics['score_momentum'] = df_metrics['roc_10d'].clip(-10, 25) * 0.7
        
        # VOLUMEN (0-15 puntos)
        df_metrics['score_volume'] = (df_metrics['rvol'] - 1).clip(0, 5) * 3
        
        # TENDENCIA (0-20 puntos)
        df_metrics['score_trend'] = (
            df_metrics['above_sma50'].astype(int) * 10 +
            df_metrics['above_sma200'].astype(int) * 10
        )
        
        # SEÑALES ESPECIALES (0-30 puntos)
        df_metrics['score_signals'] = (
            df_metrics['breakout_up'].astype(int) * 15 +
            df_metrics['golden_cross'].astype(int) * 15
        )
        
        # Score base
        df_metrics['score_base'] = (
            df_metrics['score_momentum'] +
            df_metrics['score_volume'] +
            df_metrics['score_trend'] +
            df_metrics['score_signals']
        ).clip(0, 90)
        
        # === APLICAR AJUSTE DE SENTIMIENTO ===
        df_metrics['score'] = (df_metrics['score_base'] + sentiment_boost).clip(0, 100)
        
        # === CLASIFICAR POR CONFIANZA ===
        df_metrics['confianza'] = pd.cut(
            df_metrics['score'],
            bins=[0, 50, 70, 100],
            labels=['BAJA', 'MEDIA', 'ALTA']
        )
        
        # Mostrar distribución
        print(f"\n   Distribución de confianza:")
        confianza_counts = df_metrics['confianza'].value_counts().sort_index()
        for nivel, count in confianza_counts.items():
            print(f"     {nivel}: {count} candidatos")
        
        return df_metrics
    
    def scan(self, period: str = "6mo", strategy: str = "momentum", 
             max_candidates: int = 20, use_optimized_download: bool = True) -> Tuple[List[str], pd.DataFrame]:
        """
        Ejecuta el escaneo completo del mercado
        MEJORADO: Usa descarga optimizada por default
        
        Args:
            period: Período de datos históricos
            strategy: Estrategia de filtrado
            max_candidates: Número máximo de candidatos a retornar
            use_optimized_download: Si True, usa descarga en batches (recomendado para >100 tickers)
        
        Returns:
            Tupla (lista de candidatos, DataFrame de métricas)
        """
        print("\n" + "="*80)
        print("📡 RADAR DE MERCADO - ESCANEO INICIADO")
        print("="*80)
        
        # Paso 1: Cargar universo
        if not self.tickers:
            self.load_universe()
        
        # Paso 2: Descarga (optimizada o normal según universo)
        if use_optimized_download and len(self.tickers) > 100:
            # Para universos grandes (S&P 500), usar descarga en batches
            if not self.download_batch_optimized(period=period, batch_size=100):
                return [], pd.DataFrame()
        else:
            # Para universos pequeños (crypto30), descarga normal
            if not self.download_batch(period=period):
                return [], pd.DataFrame()
        
        # Paso 3: Calcular métricas
        df_metrics = self.calculate_radar_metrics()
        
        if df_metrics.empty:
            print("❌ No se pudieron calcular métricas")
            return [], df_metrics
        
        # Paso 4: Aplicar filtros
        candidates_list = self.apply_filters(df_metrics, strategy=strategy)
        
        # === PASO 5: CALCULAR SCORES (NUEVO v5.0) ===
        # Filtrar solo candidatos que pasaron los filtros
        df_candidates = df_metrics[df_metrics['ticker'].isin(candidates_list)].copy()
        
        if not df_candidates.empty:
            df_candidates = self.calculate_candidate_score(df_candidates)
            
            # Ordenar por score y limitar
            df_candidates = df_candidates.sort_values('score', ascending=False)
            candidates = df_candidates.head(max_candidates)['ticker'].tolist()
            
            # Mostrar top candidatos con score
            print(f"\n🏆 Top {min(10, len(df_candidates))} candidatos con mejor score:")
            for i, (idx, row) in enumerate(df_candidates.head(10).iterrows(), 1):
                print(f"   {i:2}. {row['ticker']:8} | Score: {row['score']:5.1f} | "
                      f"Confianza: {row['confianza']:5} | "
                      f"Precio: ${row['price']:8.2f} | ROC: {row['roc_10d']:+6.2f}%")
            
            # Actualizar df_metrics con scores (para export)
            df_metrics = df_metrics.merge(
                df_candidates[['ticker', 'score', 'confianza']], 
                on='ticker', 
                how='left'
            )
        else:
            candidates = []
        
        print("\n" + "="*80)
        print(f"✅ RADAR COMPLETADO - {len(candidates)} candidatos listos para análisis profundo")
        print("="*80 + "\n")
        
        self.candidates = candidates
        
        return candidates, df_metrics
    
    def export_radar_results(self, df_metrics: pd.DataFrame, universe: str):
        """
        Exporta resultados del radar a CSV con nombre fijo (sin timestamp)
        
        Args:
            df_metrics: DataFrame con métricas
            universe: Universo escaneado (sp500, crypto, etc)
        """
        filename = f"radar_{universe}.csv"  # Nombre fijo
        filepath = f"c:/Users/mikia/analisis-tecnico/{filename}"
        df_metrics.to_csv(filepath, index=False)
        print(f"📁 Resultados del radar exportados a: {filename}")


def main():
    """Función de ejemplo para ejecutar el radar"""
    
    # Ejemplo 1: Escanear S&P 500
    print("🔍 EJEMPLO 1: Escaneando S&P 500...")
    radar_sp500 = MarketRadar(universe="sp500")
    candidates_momentum, metrics = radar_sp500.scan(
        period="6mo",
        strategy="momentum",
        max_candidates=15
    )
    radar_sp500.export_radar_results(metrics, "radar_sp500_momentum.csv")
    
    print(f"\n📊 Candidatos de momentum del S&P 500:")
    for i, ticker in enumerate(candidates_momentum, 1):
        print(f"   {i}. {ticker}")
    
    # Ejemplo 2: Escanear Crypto
    print("\n\n🔍 EJEMPLO 2: Escaneando Top 50 Crypto...")
    radar_crypto = MarketRadar(universe="crypto50")
    candidates_breakout, metrics_crypto = radar_crypto.scan(
        period="3mo",
        strategy="breakout",
        max_candidates=10
    )
    radar_crypto.export_radar_results(metrics_crypto, "radar_crypto_breakout.csv")
    
    print(f"\n📊 Candidatos de breakout en Crypto:")
    for i, ticker in enumerate(candidates_breakout, 1):
        print(f"   {i}. {ticker}")


if __name__ == "__main__":
    main()
