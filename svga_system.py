"""
Sistema de Vigilancia y Generación de Alertas Algorítmicas (SVGA)
Implementación basada en los principios de John J. Murphy y pandas-ta
Autor: AIDA (Artificial Intelligence Data Architect)
Fecha: 25 de octubre de 2025
"""

import pandas as pd
import numpy as np
import pandas_ta as ta
import yfinance as yf
import plotly.graph_objects as go
import plotly.io as pio
from plotly.subplots import make_subplots
import json
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import json
from datetime import datetime, timedelta
from typing import Dict, List, Tuple
import warnings
warnings.filterwarnings('ignore')


class SVGASystem:
    """Sistema de Vigilancia y Generación de Alertas Algorítmicas"""
    
    def __init__(self, portfolio_tickers: List[str], market_tickers: List[str]):
        """
        Inicializa el sistema SVGA
        
        Args:
            portfolio_tickers: Lista de activos del portafolio (ej: ['PAXG-USD', 'BTC-USD', '^SPX'])
            market_tickers: Lista de activos para análisis de mercado general
        """
        self.portfolio_tickers = portfolio_tickers
        self.market_tickers = market_tickers
        self.data = {}
        self.signals = {}
        self.metrics = {}
        
    def download_data(self, ticker: str, period: str = "1y", interval: str = "1d") -> pd.DataFrame:
        """
        Descarga datos OHLCV de yfinance
        
        Args:
            ticker: Símbolo del activo
            period: Período de datos (1mo, 3mo, 6mo, 1y, 2y, 5y)
            interval: Intervalo de datos (1d, 1wk, 1mo)
        
        Returns:
            DataFrame con datos OHLCV estandarizados
        """
        print(f" Descargando datos para {ticker}...")
        df = yf.download(ticker, period=period, interval=interval, progress=False)
        
        # Estandarizar nombres de columnas para pandas-ta
        df.columns = [col[0].lower() if isinstance(col, tuple) else col.lower() for col in df.columns]
        
        # Asegurar que tenemos las columnas necesarias
        required_cols = ['open', 'high', 'low', 'close', 'volume']
        for col in required_cols:
            if col not in df.columns:
                raise ValueError(f"Columna '{col}' no encontrada en los datos de {ticker}")
        
        return df
    
    def calculate_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calcula indicadores técnicos usando pandas-ta (VERSIÓN MEJORADA)
        
        Aplica la extensión .ta de DataFrame para calcular las métricas clave del SVGA:
        - Tendencia: EMAs múltiples, Bandas de Bollinger, Ichimoku
        - Momentum: RSI, MACD, Estocástico, ROC
        - Volatilidad: ATR, Bandas de Bollinger, Keltner Channels
        - Volumen: OBV, Volume SMA, Chaikin Money Flow
        - Fuerza de Tendencia: ADX, Aroon
        - Patrones: Reconocimiento de velas japonesas
        - Fibonacci: Niveles de retroceso automáticos
        """
        print("🔬 Calculando indicadores técnicos (versión mejorada)...")
        
        # === TENDENCIA Y VOLATILIDAD ===
        df.ta.ema(length=12, append=True)       # EMA rápida
        df.ta.ema(length=26, append=True)       # EMA intermedia
        df.ta.ema(length=50, append=True)       # EMA lenta
        df.ta.ema(length=200, append=True)      # EMA largo plazo
        df.ta.sma(length=20, append=True)       # SMA para Bollinger
        df.ta.bbands(length=20, std=2, append=True)  # Bandas de Bollinger
        df.ta.donchian(length=20, append=True)  # Canal de Donchian
        df.ta.kc(length=20, append=True)        # Keltner Channels
        
        # === MOMENTUM Y OSCILADORES ===
        df.ta.rsi(length=14, append=True)       # RSI
        df.ta.macd(fast=12, slow=26, signal=9, append=True)  # MACD
        df.ta.stoch(k=14, d=3, append=True)     # Estocástico
        df.ta.roc(length=10, append=True)       # Rate of Change
        df.ta.cci(length=20, append=True)       # Commodity Channel Index
        
        # === FUERZA DE TENDENCIA ===
        df.ta.adx(length=14, append=True)       # ADX
        df.ta.aroon(length=25, append=True)     # Aroon (detecta inicio de tendencias)
        
        # === VOLUMEN Y CONFIRMACIÓN ===
        df.ta.obv(append=True)                  # On Balance Volume
        df.ta.atr(length=14, append=True)       # Average True Range
        df.ta.cmf(length=20, append=True)       # Chaikin Money Flow
        df.ta.vwap(append=True)                 # Volume Weighted Average Price
        
        # === PATRONES DE VELAS (si TA-Lib disponible) ===
        try:
            # Patrones clave de Murphy
            df.ta.cdl_pattern(name="doji", append=True)
            df.ta.cdl_pattern(name="engulfing", append=True)
            df.ta.cdl_pattern(name="hammer", append=True)
            df.ta.cdl_pattern(name="morningstar", append=True)
        except:
            pass  # TA-Lib no instalado
        
        # === NIVELES DE FIBONACCI ===
        df = self._calculate_fibonacci_levels(df)
        
        # === DETECCIÓN DE LÍNEAS DE TENDENCIA ===
        df = self._detect_trend_lines(df)
        
        return df
    
    def _calculate_fibonacci_levels(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calcula niveles de retroceso de Fibonacci basados en swing high/low reciente
        """
        if len(df) < 50:
            return df
        
        # Identificar swing high y low de los últimos 50 períodos
        lookback = min(50, len(df))
        recent_high = df['high'].iloc[-lookback:].max()
        recent_low = df['low'].iloc[-lookback:].min()
        
        diff = recent_high - recent_low
        
        # Niveles de Fibonacci (retrocesos)
        df['fib_0'] = recent_low
        df['fib_236'] = recent_low + 0.236 * diff
        df['fib_382'] = recent_low + 0.382 * diff
        df['fib_500'] = recent_low + 0.500 * diff
        df['fib_618'] = recent_low + 0.618 * diff
        df['fib_786'] = recent_low + 0.786 * diff
        df['fib_100'] = recent_high
        
        return df
    
    def _detect_trend_lines(self, df: pd.DataFrame, window: int = 20) -> pd.DataFrame:
        """
        Detecta líneas de tendencia usando regresión lineal en ventanas deslizantes
        """
        if len(df) < window:
            return df
        
        # Línea de tendencia alcista (basada en mínimos)
        lows = df['low'].values
        x = np.arange(len(lows))
        
        # Regresión lineal simple en los últimos 'window' períodos
        recent_x = x[-window:]
        recent_lows = lows[-window:]
        
        if len(recent_x) > 1:
            # Calcular pendiente e intercepto
            slope_support = np.polyfit(recent_x, recent_lows, 1)[0]
            intercept_support = np.polyfit(recent_x, recent_lows, 1)[1]
            
            # Línea de tendencia bajista (basada en máximos)
            recent_highs = df['high'].values[-window:]
            slope_resistance = np.polyfit(recent_x, recent_highs, 1)[0]
            intercept_resistance = np.polyfit(recent_x, recent_highs, 1)[1]
            
            # Proyectar líneas para todo el DataFrame
            df['trendline_support'] = slope_support * x + intercept_support
            df['trendline_resistance'] = slope_resistance * x + intercept_resistance
        
        return df
    
    def generate_signals(self, df: pd.DataFrame, ticker: str) -> Dict:
        """
        Genera señales y alertas basadas en la lógica del SVGA
        
        Implementa:
        - Filtro 1: Alineación con tendencia de largo plazo (EMA 50 vs EMA 200)
        - Filtro 2: Fuerza de tendencia (ADX)
        - Alertas de alta prioridad: Divergencias, rupturas, debilidad
        
        Returns:
            Diccionario con señales discretas y alertas
        """
        print(f" Generando señales para {ticker}...")
        
        # Obtener última fila de datos
        latest = df.iloc[-1]
        prev = df.iloc[-2]
        
        signals = {
            "ticker": ticker,
            "timestamp": str(df.index[-1]),
            "price_current": float(latest['close']),
            "filters": {},
            "alerts": [],
            "signal": 0,  # 1: Compra, -1: Venta, 0: Neutral
            "priority": "LOW"
        }
        
        # === FILTRO 1: TENDENCIA DE LARGO PLAZO ===
        ema_50 = latest.get('EMA_50', np.nan)
        ema_200 = latest.get('EMA_200', np.nan)
        
        if not np.isnan(ema_50) and not np.isnan(ema_200):
            long_term_trend = "ALCISTA" if ema_50 > ema_200 else "BAJISTA"
            signals["filters"]["long_term_trend"] = long_term_trend
        else:
            signals["filters"]["long_term_trend"] = "INDEFINIDO"
        
        # === FILTRO 2: FUERZA DE TENDENCIA (ADX) ===
        adx = latest.get('ADX_14', np.nan)
        if not np.isnan(adx):
            if adx > 40:
                market_regime = "TENDENCIA_FUERTE"
            elif adx > 25:
                market_regime = "TENDENCIA_MODERADA"
            elif adx > 20:
                market_regime = "TENDENCIA_DÉBIL"
            else:
                market_regime = "LATERAL"
            signals["filters"]["market_regime"] = market_regime
            signals["filters"]["adx_value"] = float(adx)
        else:
            signals["filters"]["market_regime"] = "INDEFINIDO"
        
        # === DETECCIÓN DE ALERTAS DE ALTA PRIORIDAD ===
        
        # 1. ALERTA DE ANOMALÍA (DIVERGENCIA RSI)
        rsi = latest.get('RSI_14', np.nan)
        if not np.isnan(rsi):
            signals["rsi_value"] = float(rsi)
            
            # Sobrecompra
            if rsi > 70:
                # Verificar divergencia bajista (precio sube, RSI baja)
                price_trend = latest['close'] > df['close'].iloc[-10:].mean()
                rsi_trend = rsi < df['RSI_14'].iloc[-10:].mean()
                
                if price_trend and rsi_trend:
                    signals["alerts"].append({
                        "type": "DIVERGENCIA_BAJISTA",
                        "description": "Anomalía detectada: Precio alcista pero RSI descendente en zona de sobrecompra",
                        "priority": "HIGH"
                    })
                    signals["signal"] = -1
                    signals["priority"] = "HIGH"
                else:
                    signals["alerts"].append({
                        "type": "SOBRECOMPRA",
                        "description": f"RSI en zona de sobrecompra ({rsi:.2f} > 70)",
                        "priority": "MEDIUM"
                    })
            
            # Sobreventa
            elif rsi < 30:
                # Verificar divergencia alcista (precio baja, RSI sube)
                price_trend = latest['close'] < df['close'].iloc[-10:].mean()
                rsi_trend = rsi > df['RSI_14'].iloc[-10:].mean()
                
                if price_trend and rsi_trend:
                    signals["alerts"].append({
                        "type": "DIVERGENCIA_ALCISTA",
                        "description": "Anomalía detectada: Precio bajista pero RSI ascendente en zona de sobreventa",
                        "priority": "HIGH"
                    })
                    signals["signal"] = 1
                    signals["priority"] = "HIGH"
                else:
                    signals["alerts"].append({
                        "type": "SOBREVENTA",
                        "description": f"RSI en zona de sobreventa ({rsi:.2f} < 30)",
                        "priority": "MEDIUM"
                    })
        
        # 2. ALERTA DE RUPTURA CONFIRMADA (Bandas de Bollinger + OBV)
        bbl = latest.get('BBL_20_2.0', np.nan)
        bbu = latest.get('BBU_20_2.0', np.nan)
        obv = latest.get('OBV', np.nan)
        
        if not np.isnan(bbl) and not np.isnan(bbu) and not np.isnan(obv):
            # Ruptura alcista de banda superior
            if latest['close'] > bbu and prev['close'] <= prev.get('BBU_20_2.0', bbu):
                obv_trend = obv > df['OBV'].iloc[-5:].mean()
                if obv_trend:
                    signals["alerts"].append({
                        "type": "RUPTURA_ALCISTA_CONFIRMADA",
                        "description": "Ruptura de banda superior de Bollinger confirmada por OBV ascendente",
                        "priority": "HIGH"
                    })
                    if signals["signal"] == 0:  # No sobrescribir señal de divergencia
                        signals["signal"] = 1
                        signals["priority"] = "HIGH"
            
            # Ruptura bajista de banda inferior
            elif latest['close'] < bbl and prev['close'] >= prev.get('BBL_20_2.0', bbl):
                obv_trend = obv < df['OBV'].iloc[-5:].mean()
                if obv_trend:
                    signals["alerts"].append({
                        "type": "RUPTURA_BAJISTA_CONFIRMADA",
                        "description": "Ruptura de banda inferior de Bollinger confirmada por OBV descendente",
                        "priority": "HIGH"
                    })
                    if signals["signal"] == 0:
                        signals["signal"] = -1
                        signals["priority"] = "HIGH"
        
        # 3. SEÑALES DE MACD
        macd = latest.get('MACD_12_26_9', np.nan)
        macd_signal = latest.get('MACDs_12_26_9', np.nan)
        macd_hist = latest.get('MACDh_12_26_9', np.nan)
        
        if not np.isnan(macd_hist):
            signals["macd_histogram"] = float(macd_hist)
            
            # Cruce alcista del histograma
            prev_hist = prev.get('MACDh_12_26_9', 0)
            if macd_hist > 0 and prev_hist <= 0:
                signals["alerts"].append({
                    "type": "MACD_CRUCE_ALCISTA",
                    "description": "Histograma MACD cruza línea cero al alza (señal temprana de momento positivo)",
                    "priority": "MEDIUM"
                })
                if signals["signal"] == 0 and signals["filters"]["market_regime"] != "LATERAL":
                    signals["signal"] = 1
            
            # Cruce bajista del histograma
            elif macd_hist < 0 and prev_hist >= 0:
                signals["alerts"].append({
                    "type": "MACD_CRUCE_BAJISTA",
                    "description": "Histograma MACD cruza línea cero a la baja (señal temprana de momento negativo)",
                    "priority": "MEDIUM"
                })
                if signals["signal"] == 0 and signals["filters"]["market_regime"] != "LATERAL":
                    signals["signal"] = -1
        
        # 4. APLICAR FILTROS DE VALIDACIÓN
        if signals["filters"]["market_regime"] == "LATERAL":
            signals["alerts"].append({
                "type": "MERCADO_LATERAL",
                "description": f"ADX bajo ({adx:.2f}) indica mercado sin tendencia clara. Señales de seguimiento de tendencia no recomendadas.",
                "priority": "LOW"
            })
            # En mercado lateral, reducir confianza en señales de tendencia
            if abs(signals["signal"]) == 1 and signals["priority"] != "HIGH":
                signals["signal"] = 0
        
        # Validar alineación con tendencia de largo plazo
        if signals["filters"]["long_term_trend"] == "BAJISTA" and signals["signal"] == 1:
            signals["alerts"].append({
                "type": "ALERTA_CONTRA_TENDENCIA",
                "description": "Señal de compra contra tendencia de largo plazo bajista. Precaución.",
                "priority": "MEDIUM"
            })
        elif signals["filters"]["long_term_trend"] == "ALCISTA" and signals["signal"] == -1:
            signals["alerts"].append({
                "type": "ALERTA_CONTRA_TENDENCIA",
                "description": "Señal de venta contra tendencia de largo plazo alcista. Precaución.",
                "priority": "MEDIUM"
            })
        
        # 5. SEÑAL FINAL
        if signals["signal"] == 1:
            signals["recommendation"] = "COMPRAR"
        elif signals["signal"] == -1:
            signals["recommendation"] = "VENDER"
        else:
            signals["recommendation"] = "MANTENER"
        
        # Si no hay alertas, agregar estado neutral
        if not signals["alerts"]:
            signals["alerts"].append({
                "type": "SIN_SEÑALES",
                "description": "No se detectaron condiciones de alerta en este momento",
                "priority": "LOW"
            })
        
        return signals
    
    def create_chart(self, df: pd.DataFrame, ticker: str, signals: Dict) -> go.Figure:
        """
        Crea gráfico interactivo multi-panel con Plotly
        
        Estructura:
        - Panel 1: Precio + EMAs + Bandas de Bollinger
        - Panel 2: RSI con zonas de 70/30
        - Panel 3: MACD + Histograma
        - Panel 4: Volumen + OBV
        """
        print(f" Generando gráfico para {ticker}...")
        
        # Crear subplots
        fig = make_subplots(
            rows=4, cols=1,
            shared_xaxes=True,
            vertical_spacing=0.03,
            subplot_titles=(
                f'{ticker} - Precio y Tendencia',
                'RSI (Índice de Fuerza Relativa)',
                'MACD (Convergencia/Divergencia de Medias Móviles)',
                'Volumen y OBV'
            ),
            row_heights=[0.4, 0.2, 0.2, 0.2]
        )
        
        # === PANEL 1: PRECIO Y TENDENCIA ===
        # Candlestick
        fig.add_trace(
            go.Candlestick(
                x=df.index,
                open=df['open'],
                high=df['high'],
                low=df['low'],
                close=df['close'],
                name='Precio',
                increasing_line_color='#26a69a',
                decreasing_line_color='#ef5350'
            ),
            row=1, col=1
        )
        
        # EMAs
        if 'EMA_12' in df.columns:
            fig.add_trace(go.Scatter(x=df.index, y=df['EMA_12'], name='EMA 12', 
                                     line=dict(color='#2196F3', width=1)), row=1, col=1)
        if 'EMA_26' in df.columns:
            fig.add_trace(go.Scatter(x=df.index, y=df['EMA_26'], name='EMA 26', 
                                     line=dict(color='#FF9800', width=1)), row=1, col=1)
        if 'EMA_50' in df.columns:
            fig.add_trace(go.Scatter(x=df.index, y=df['EMA_50'], name='EMA 50', 
                                     line=dict(color='#9C27B0', width=2)), row=1, col=1)
        if 'EMA_200' in df.columns:
            fig.add_trace(go.Scatter(x=df.index, y=df['EMA_200'], name='EMA 200', 
                                     line=dict(color='#F44336', width=2, dash='dash')), row=1, col=1)
        
        # Bandas de Bollinger
        if 'BBL_20_2.0' in df.columns and 'BBU_20_2.0' in df.columns:
            fig.add_trace(go.Scatter(
                x=df.index, y=df['BBU_20_2.0'], name='BB Superior',
                line=dict(color='rgba(128,128,128,0.3)', width=1, dash='dot'),
                showlegend=False
            ), row=1, col=1)
            
            fig.add_trace(go.Scatter(
                x=df.index, y=df['BBL_20_2.0'], name='BB Inferior',
                line=dict(color='rgba(128,128,128,0.3)', width=1, dash='dot'),
                fill='tonexty', fillcolor='rgba(128,128,128,0.1)',
                showlegend=False
            ), row=1, col=1)
        
        # === PANEL 2: RSI ===
        if 'RSI_14' in df.columns:
            fig.add_trace(go.Scatter(x=df.index, y=df['RSI_14'], name='RSI',
                                     line=dict(color='#673AB7', width=2)), row=2, col=1)
            
            # Líneas de referencia 70/30
            fig.add_hline(y=70, line_dash="dash", line_color="red", opacity=0.5, row=2, col=1)
            fig.add_hline(y=30, line_dash="dash", line_color="green", opacity=0.5, row=2, col=1)
            fig.add_hline(y=50, line_dash="dot", line_color="gray", opacity=0.3, row=2, col=1)
        
        # === PANEL 3: MACD ===
        if 'MACD_12_26_9' in df.columns:
            fig.add_trace(go.Scatter(x=df.index, y=df['MACD_12_26_9'], name='MACD',
                                     line=dict(color='#00BCD4', width=2)), row=3, col=1)
        
        if 'MACDs_12_26_9' in df.columns:
            fig.add_trace(go.Scatter(x=df.index, y=df['MACDs_12_26_9'], name='Señal',
                                     line=dict(color='#FF5722', width=1)), row=3, col=1)
        
        if 'MACDh_12_26_9' in df.columns:
            colors = ['#26a69a' if val >= 0 else '#ef5350' for val in df['MACDh_12_26_9']]
            fig.add_trace(go.Bar(x=df.index, y=df['MACDh_12_26_9'], name='Histograma',
                                 marker_color=colors, opacity=0.7), row=3, col=1)
        
        fig.add_hline(y=0, line_dash="dash", line_color="gray", opacity=0.5, row=3, col=1)
        
        # === PANEL 4: VOLUMEN Y OBV ===
        colors_vol = ['#26a69a' if df['close'].iloc[i] >= df['open'].iloc[i] else '#ef5350' 
                      for i in range(len(df))]
        fig.add_trace(go.Bar(x=df.index, y=df['volume'], name='Volumen',
                             marker_color=colors_vol, opacity=0.5), row=4, col=1)
        
        if 'OBV' in df.columns:
            fig.add_trace(go.Scatter(x=df.index, y=df['OBV'], name='OBV', yaxis='y2',
                                     line=dict(color='#FFC107', width=2)), row=4, col=1)
        
        # Layout
        fig.update_layout(
            title=f'{ticker} - Análisis Técnico Completo (SVGA)',
            xaxis_rangeslider_visible=False,
            height=1200,
            template='plotly_dark',
            hovermode='x unified',
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        
        # Actualizar ejes Y
        fig.update_yaxes(title_text="Precio", row=1, col=1)
        fig.update_yaxes(title_text="RSI", range=[0, 100], row=2, col=1)
        fig.update_yaxes(title_text="MACD", row=3, col=1)
        fig.update_yaxes(title_text="Volumen", row=4, col=1)
        
        return fig
    
    def analyze_portfolio(self) -> Dict:
        """Analiza el portafolio completo y genera alertas"""
        print("\n" + "="*80)
        print(" ANÁLISIS DEL PORTAFOLIO")
        print("="*80 + "\n")
        
        portfolio_results = {
            "analysis_timestamp": datetime.now().isoformat(),
            "portfolio_composition": self.portfolio_tickers,
            "assets": {}
        }
        
        for ticker in self.portfolio_tickers:
            try:
                # Descargar y procesar datos
                df = self.download_data(ticker, period="1y", interval="1d")
                df = self.calculate_indicators(df)
                
                # Generar señales
                signals = self.generate_signals(df, ticker)
                
                # === GENERACIÓN DE GRÁFICOS (DESACTIVADA) ===
                # Crear gráfico
                # fig = self.create_chart(df, ticker, signals)
                
                # # Guardar gráfico HTML
                # chart_filename = f"chart_{ticker.replace('^', '').replace('-', '_')}.html"
                # fig.write_html(f"c:/Users/mikia/analisis-tecnico/{chart_filename}")
                # print(f" Gráfico HTML guardado: {chart_filename}")
                
                # # Guardar gráfico PNG (v4.0)
                # try:
                #     png_filename = f"chart_{ticker.replace('^', '').replace('-', '_')}.png"
                #     pio.write_image(fig, f"c:/Users/mikia/analisis-tecnico/{png_filename}", 
                #                     width=1920, height=1200, scale=2)
                #     print(f" Gráfico PNG guardado: {png_filename}")
                # except Exception as e:
                #     print(f" ⚠️ Error al guardar PNG: {e}")
                
                # print("")
                chart_filename = f"chart_{ticker.replace('^', '').replace('-', '_')}.html"  # Mantener referencia
                
                # Almacenar resultados
                self.data[ticker] = df
                self.signals[ticker] = signals
                portfolio_results["assets"][ticker] = {
                    "signals": signals,
                    "chart_file": chart_filename,
                    "latest_metrics": self._extract_latest_metrics(df)
                }
                
            except Exception as e:
                print(f" Error procesando {ticker}: {str(e)}\n")
                portfolio_results["assets"][ticker] = {"error": str(e)}
        
        return portfolio_results
    
    def analyze_market(self) -> Dict:
        """Analiza el mercado general para contexto macro"""
        print("\n" + "="*80)
        print(" ANÁLISIS DEL MERCADO GENERAL")
        print("="*80 + "\n")
        
        market_results = {
            "analysis_timestamp": datetime.now().isoformat(),
            "market_indicators": self.market_tickers,
            "assets": {}
        }
        
        for ticker in self.market_tickers:
            try:
                # Descargar datos
                df = self.download_data(ticker, period="2y", interval="1wk")  # Semanal para perspectiva macro
                df = self.calculate_indicators(df)
                
                # Generar señales
                signals = self.generate_signals(df, ticker)
                
                # === GENERACIÓN DE GRÁFICOS (DESACTIVADA) ===
                # # Crear gráfico simplificado
                # fig = self.create_chart(df, ticker, signals)
                
                # # Guardar gráfico HTML
                # chart_filename = f"market_{ticker.replace('^', '').replace('-', '_')}.html"
                # fig.write_html(f"c:/Users/mikia/analisis-tecnico/{chart_filename}")
                # print(f" Gráfico de mercado HTML guardado: {chart_filename}")
                
                # # Guardar gráfico PNG (v4.0)
                # try:
                #     png_filename = f"market_{ticker.replace('^', '').replace('-', '_')}.png"
                #     pio.write_image(fig, f"c:/Users/mikia/analisis-tecnico/{png_filename}", 
                #                     width=1920, height=1200, scale=2)
                #     print(f" Gráfico de mercado PNG guardado: {png_filename}")
                # except Exception as e:
                #     print(f" ⚠️ Error al guardar PNG: {e}")
                
                # print("")
                chart_filename = f"market_{ticker.replace('^', '').replace('-', '_')}.html"  # Mantener referencia
                
                # Almacenar resultados
                market_results["assets"][ticker] = {
                    "signals": signals,
                    "chart_file": chart_filename,
                    "latest_metrics": self._extract_latest_metrics(df)
                }
                
            except Exception as e:
                print(f" Error procesando {ticker}: {str(e)}\n")
                market_results["assets"][ticker] = {"error": str(e)}
        
        return market_results
    
    def _extract_latest_metrics(self, df: pd.DataFrame) -> Dict:
        """Extrae las métricas más recientes del DataFrame"""
        latest = df.iloc[-1]
        metrics = {
            "price": float(latest['close']),
            "volume": float(latest['volume']),
        }
        
        # Agregar indicadores disponibles
        indicators = {
            'EMA_12': 'ema_12',
            'EMA_26': 'ema_26',
            'EMA_50': 'ema_50',
            'EMA_200': 'ema_200',
            'RSI_14': 'rsi',
            'MACD_12_26_9': 'macd',
            'MACDh_12_26_9': 'macd_histogram',
            'ADX_14': 'adx',
            'OBV': 'obv',
            'ATR_14': 'atr',
            'BBL_20_2.0': 'bollinger_lower',
            'BBU_20_2.0': 'bollinger_upper'
        }
        
        for col, name in indicators.items():
            if col in latest.index and not pd.isna(latest[col]):
                metrics[name] = float(latest[col])
        
        return metrics
    
    def generate_report(self, portfolio_results: Dict, market_results: Dict) -> str:
        """
        Genera informe ejecutivo en formato Markdown
        """
        print("\n Generando informe ejecutivo...\n")
        
        report = f"""#  INFORME EJECUTIVO - SISTEMA SVGA

**Fecha y Hora de Análisis:** {datetime.now().strftime('%d de %B de %Y, %H:%M:%S')}

---

##  RESUMEN EJECUTIVO DEL PORTAFOLIO

"""
        
        # Análisis del portafolio
        for ticker, data in portfolio_results["assets"].items():
            if "error" in data:
                report += f"###  {ticker}\n**Error:** {data['error']}\n\n"
                continue
            
            signals = data["signals"]
            recommendation = signals["recommendation"]
            priority = signals["priority"]
            
            # Emoji según recomendación
            emoji = "🟢" if recommendation == "COMPRAR" else "🔴" if recommendation == "VENDER" else "🟡"
            
            report += f"""### {emoji} {ticker}

**Recomendación:** **{recommendation}** (Prioridad: {priority})  
**Precio Actual:** ${signals['price_current']:.2f}  
**Régimen de Mercado:** {signals['filters']['market_regime']}  
**Tendencia Largo Plazo:** {signals['filters']['long_term_trend']}

#### 🚨 Alertas Detectadas:

"""
            
            for alert in signals["alerts"]:
                priority_emoji = "🔴" if alert["priority"] == "HIGH" else "🟡" if alert["priority"] == "MEDIUM" else "⚪"
                report += f"- {priority_emoji} **{alert['type']}:** {alert['description']}\n"
            
            report += f"\n📈 [Ver gráfico interactivo]({data['chart_file']})\n\n---\n\n"
        
        # Análisis de mercado general
        report += """##  CONTEXTO DE MERCADO GENERAL

"""
        
        for ticker, data in market_results["assets"].items():
            if "error" in data:
                continue
            
            signals = data["signals"]
            report += f"""### {ticker}

**Tendencia:** {signals['filters']['long_term_trend']}  
**Régimen:** {signals['filters']['market_regime']}  
**Precio:** ${signals['price_current']:.2f}

"""
        
        # Métricas clave
        report += """---

##  MÉTRICAS TÉCNICAS CLAVE

### Interpretación de Indicadores:

#### RSI (Índice de Fuerza Relativa)
- **> 70:** Zona de sobrecompra (posible corrección bajista)
- **< 30:** Zona de sobreventa (posible rebote alcista)
- **Divergencias:** Señal temprana de cambio de tendencia

#### MACD (Convergencia/Divergencia de Medias Móviles)
- **Histograma > 0:** Momento alcista
- **Histograma < 0:** Momento bajista
- **Cruce de línea cero:** Señal temprana de cambio de momento

#### ADX (Índice de Movimiento Direccional)
- **> 40:** Tendencia fuerte (favorecer estrategias de seguimiento)
- **20-40:** Tendencia moderada
- **< 20:** Mercado lateral (favorecer osciladores)

#### OBV (Volumen Total Acumulativo)
- **Confirmación:** OBV y precio en misma dirección = señal válida
- **Divergencia:** OBV y precio en direcciones opuestas = alerta de cambio

---

##  ADVERTENCIA LEGAL

Este análisis es generado automáticamente por el Sistema SVGA basado en principios de análisis técnico. **NO constituye asesoramiento de inversión.** Todas las inversiones conllevan riesgo. El rendimiento pasado no garantiza resultados futuros. Consulte con un asesor financiero profesional antes de tomar decisiones de inversión.

---

*Generado por AIDA (Artificial Intelligence Data Architect)*  
*Sistema SVGA v1.0*
"""
        
        return report
    
    def generate_portfolio_report(self, portfolio_results: Dict) -> str:
        """
        Genera informe ejecutivo SOLO del Portfolio en formato Markdown
        """
        report = f"""# 📊 INFORME DE PORTFOLIO - SISTEMA SVGA

**Fecha y Hora de Análisis:** {datetime.now().strftime('%d de %B de %Y, %H:%M:%S')}

---

## 💼 ANÁLISIS DEL PORTAFOLIO

"""
        
        # Análisis del portafolio
        for ticker, data in portfolio_results["assets"].items():
            if "error" in data:
                report += f"### ⚠️ {ticker}\n**Error:** {data['error']}\n\n"
                continue
            
            signals = data["signals"]
            recommendation = signals["recommendation"]
            priority = signals["priority"]
            
            # Emoji según recomendación
            emoji = "🟢" if recommendation == "COMPRAR" else "🔴" if recommendation == "VENDER" else "🟡"
            
            report += f"""### {emoji} {ticker}

**Recomendación:** **{recommendation}** (Prioridad: {priority})  
**Precio Actual:** ${signals['price_current']:.2f}  
**Régimen de Mercado:** {signals['filters']['market_regime']}  
**Tendencia Largo Plazo:** {signals['filters']['long_term_trend']}

#### 🚨 Alertas Detectadas:

"""
            
            for alert in signals["alerts"]:
                priority_emoji = "🔴" if alert["priority"] == "HIGH" else "🟡" if alert["priority"] == "MEDIUM" else "⚪"
                report += f"- {priority_emoji} **{alert['type']}:** {alert['description']}\n"
            
            report += f"\n📈 [Ver gráfico interactivo]({data['chart_file']})\n\n---\n\n"
        
        # Métricas clave
        report += """---

## 📊 MÉTRICAS TÉCNICAS CLAVE

### Interpretación de Indicadores:

#### RSI (Índice de Fuerza Relativa)
- **> 70:** Zona de sobrecompra (posible corrección bajista)
- **< 30:** Zona de sobreventa (posible rebote alcista)
- **Divergencias:** Señal temprana de cambio de tendencia

#### MACD (Convergencia/Divergencia de Medias Móviles)
- **Histograma > 0:** Momento alcista
- **Histograma < 0:** Momento bajista
- **Cruce de línea cero:** Señal temprana de cambio de momento

#### ADX (Índice de Movimiento Direccional)
- **> 40:** Tendencia fuerte (favorecer estrategias de seguimiento)
- **20-40:** Tendencia moderada
- **< 20:** Mercado lateral (favorecer osciladores)

#### OBV (Volumen Total Acumulativo)
- **Confirmación:** OBV y precio en misma dirección = señal válida
- **Divergencia:** OBV y precio en direcciones opuestas = alerta de cambio

---

## ⚠️ ADVERTENCIA LEGAL

Este análisis es generado automáticamente por el Sistema SVGA basado en principios de análisis técnico. **NO constituye asesoramiento de inversión.** Todas las inversiones conllevan riesgo. El rendimiento pasado no garantiza resultados futuros. Consulte con un asesor financiero profesional antes de tomar decisiones de inversión.

---

*Generado por AIDA (Artificial Intelligence Data Architect)*  
*Sistema SVGA v1.0*
"""
        
        return report
    
    def generate_market_report(self, market_results: Dict) -> str:
        """
        Genera informe ejecutivo SOLO del Mercado en formato Markdown
        """
        report = f"""# 🌍 INFORME DE MERCADO - SISTEMA SVGA

**Fecha y Hora de Análisis:** {datetime.now().strftime('%d de %B de %Y, %H:%M:%S')}

---

## 📈 CONTEXTO DE MERCADO GENERAL

"""
        
        # Análisis de mercado general
        for ticker, data in market_results["assets"].items():
            if "error" in data:
                report += f"### ⚠️ {ticker}\n**Error:** {data['error']}\n\n"
                continue
            
            signals = data["signals"]
            recommendation = signals["recommendation"]
            
            # Emoji según recomendación
            emoji = "🟢" if recommendation == "COMPRAR" else "🔴" if recommendation == "VENDER" else "🟡"
            
            report += f"""### {emoji} {ticker}

**Recomendación:** {recommendation}  
**Tendencia:** {signals['filters']['long_term_trend']}  
**Régimen:** {signals['filters']['market_regime']}  
**Precio:** ${signals['price_current']:.2f}

#### 🚨 Alertas:

"""
            
            for alert in signals["alerts"]:
                priority_emoji = "🔴" if alert["priority"] == "HIGH" else "🟡" if alert["priority"] == "MEDIUM" else "⚪"
                report += f"- {priority_emoji} **{alert['type']}:** {alert['description']}\n"
            
            report += f"\n📈 [Ver gráfico interactivo]({data['chart_file']})\n\n---\n\n"
        
        # Métricas clave
        report += """---

## 📊 MÉTRICAS TÉCNICAS CLAVE

### Interpretación de Indicadores:

#### RSI (Índice de Fuerza Relativa)
- **> 70:** Zona de sobrecompra (posible corrección bajista)
- **< 30:** Zona de sobreventa (posible rebote alcista)
- **Divergencias:** Señal temprana de cambio de tendencia

#### MACD (Convergencia/Divergencia de Medias Móviles)
- **Histograma > 0:** Momento alcista
- **Histograma < 0:** Momento bajista
- **Cruce de línea cero:** Señal temprana de cambio de momento

#### ADX (Índice de Movimiento Direccional)
- **> 40:** Tendencia fuerte (favorecer estrategias de seguimiento)
- **20-40:** Tendencia moderada
- **< 20:** Mercado lateral (favorecer osciladores)

---

## ⚠️ ADVERTENCIA LEGAL

Este análisis es generado automáticamente por el Sistema SVGA basado en principios de análisis técnico. **NO constituye asesoramiento de inversión.** Todas las inversiones conllevan riesgo. El rendimiento pasado no garantiza resultados futuros. Consulte con un asesor financiero profesional antes de tomar decisiones de inversión.

---

*Generado por AIDA (Artificial Intelligence Data Architect)*  
*Sistema SVGA v1.0*
"""
        
        return report
    
    def export_results(self, portfolio_results: Dict, market_results: Dict):
        """
        Exporta resultados en JSON y Markdown (modo local - deprecado para multi-usuario)
        """
        # Exportar JSON
        json_data = {
            "portfolio": portfolio_results,
            "market": market_results,
            "metadata": {
                "system": "SVGA v1.0",
                "author": "AIDA",
                "timestamp": datetime.now().isoformat()
            }
        }
        
        # ===================================================================
        # EXPORTAR JSON SEPARADOS: Portfolio y Mercado
        # ===================================================================
        
        # JSON de Portfolio
        portfolio_json = {
            "portfolio": json_data["portfolio"],
            "metadata": json_data["metadata"]
        }
        portfolio_json_filename = "portfolio_analisis.json"
        with open(f"c:/Users/mikia/analisis-tecnico/{portfolio_json_filename}", 'w', encoding='utf-8') as f:
            json.dump(portfolio_json, f, indent=2, ensure_ascii=False)
        print(f" ✅ JSON Portfolio: {portfolio_json_filename}")
        
        # JSON de Mercado
        market_json = {
            "market": json_data["market"],
            "metadata": json_data["metadata"]
        }
        market_json_filename = "mercado_analisis.json"
        with open(f"c:/Users/mikia/analisis-tecnico/{market_json_filename}", 'w', encoding='utf-8') as f:
            json.dump(market_json, f, indent=2, ensure_ascii=False)
        print(f" ✅ JSON Mercado: {market_json_filename}")
        
        # ===================================================================
        # EXPORTAR MARKDOWN SEPARADOS: Portfolio y Mercado
        # ===================================================================
        
        # Informe de Portfolio
        portfolio_report = self.generate_portfolio_report(portfolio_results)
        portfolio_md_filename = "portfolio_informe.md"
        with open(f"c:/Users/mikia/analisis-tecnico/{portfolio_md_filename}", 'w', encoding='utf-8') as f:
            f.write(portfolio_report)
        print(f" ✅ Informe Portfolio: {portfolio_md_filename}")
        
        # Informe de Mercado
        market_report = self.generate_market_report(market_results)
        market_md_filename = "mercado_informe.md"
        with open(f"c:/Users/mikia/analisis-tecnico/{market_md_filename}", 'w', encoding='utf-8') as f:
            f.write(market_report)
        print(f" ✅ Informe Mercado: {market_md_filename}")
    
    def generate_results_in_memory(self, portfolio_results: Dict, market_results: Dict) -> Dict:
        """
        Genera resultados en memoria sin guardar archivos locales
        (Nuevo método para sistema multi-usuario con Supabase)
        
        Args:
            portfolio_results: Resultados del análisis de portfolio
            market_results: Resultados del análisis de mercado
        
        Returns:
            Diccionario con:
            - portfolio_json: Dict con datos JSON del portfolio
            - portfolio_md: String con informe MD del portfolio
            - mercado_json: Dict con datos JSON del mercado
            - mercado_md: String con informe MD del mercado
        """
        # Preparar JSON
        metadata = {
            "system": "SVGA v1.0",
            "author": "AIDA",
            "timestamp": datetime.now().isoformat()
        }
        
        portfolio_json = {
            "portfolio": portfolio_results,
            "metadata": metadata
        }
        
        mercado_json = {
            "market": market_results,
            "metadata": metadata
        }
        
        # Generar informes MD
        portfolio_md = self.generate_portfolio_report(portfolio_results)
        mercado_md = self.generate_market_report(market_results)
        
        return {
            "portfolio_json": portfolio_json,
            "portfolio_md": portfolio_md,
            "mercado_json": mercado_json,
            "mercado_md": mercado_md
        }
    
    def run(self):
        """Ejecuta el análisis completo del sistema SVGA"""
        print("\n" + "="*80)
        print("🚀 SISTEMA SVGA - INICIO DE ANÁLISIS")
        print("="*80 + "\n")
        
        # Analizar portafolio
        portfolio_results = self.analyze_portfolio()
        
        # Analizar mercado
        market_results = self.analyze_market()
        
        # Exportar resultados (genera 4 archivos: 2 JSON + 2 MD)
        self.export_results(portfolio_results, market_results)
        
        print("\n" + "="*80)
        print("✅ ANÁLISIS COMPLETADO")
        print("="*80 + "\n")
        
        print("� Archivos generados:")
        print("   📊 PORTFOLIO:")
        print("      - portfolio_analisis.json (métricas del portfolio)")
        print("      - portfolio_informe.md (informe ejecutivo del portfolio)")
        print("   🌍 MERCADO:")
        print("      - mercado_analisis.json (métricas del mercado)")
        print("      - mercado_informe.md (informe ejecutivo del mercado)")
        # print("   📈 GRÁFICOS:")
        # print("      - chart_*.html (gráficos interactivos del portafolio)")
        # print("      - chart_*.png (gráficos exportados del portafolio)")
        # print("      - market_*.html (gráficos interactivos del mercado)")
        # print("      - market_*.png (gráficos exportados del mercado)")
        print("\n")
    
    def run_in_memory(self) -> Dict:
        """
        Ejecuta el análisis completo y retorna resultados en memoria
        (Sin guardado de archivos locales - para sistema multi-usuario)
        
        Returns:
            Diccionario con todos los resultados en memoria:
            - portfolio_json: Dict con análisis del portfolio
            - portfolio_md: String con informe MD del portfolio
            - mercado_json: Dict con análisis del mercado
            - mercado_md: String con informe MD del mercado
        """
        print("\n🚀 SISTEMA SVGA - ANÁLISIS EN MEMORIA")
        
        # Analizar portafolio
        portfolio_results = self.analyze_portfolio()
        
        # Analizar mercado
        market_results = self.analyze_market()
        
        # Generar resultados en memoria (sin archivos)
        memory_results = self.generate_results_in_memory(portfolio_results, market_results)
        
        print("✅ ANÁLISIS EN MEMORIA COMPLETADO\n")
        
        return memory_results


def main():
    """Función principal para ejecutar el sistema SVGA"""
    
    # Definir activos del portafolio
    portfolio = [
        'PAXG-USD',  # Oro digital
        'BTC-USD',   # Bitcoin
        '^GSPC'      # S&P 500
    ]
    
    # Definir indicadores de mercado general para contexto
    market_indicators = [
        '^DJI',      # Dow Jones
        '^IXIC',     # NASDAQ
        '^TNX',      # Treasury Yield 10 años
        'GC=F',      # Oro Futures
        'CL=F',      # Petróleo Futures
        'DX-Y.NYB'   # Índice del Dólar
    ]
    
    # Inicializar y ejecutar sistema
    svga = SVGASystem(portfolio_tickers=portfolio, market_tickers=market_indicators)
    svga.run()


if __name__ == "__main__":
    main()
