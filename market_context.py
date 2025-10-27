"""
Market Context - Análisis de Contexto Macroeconómico y Sentimiento
Integra FRED API y Fear & Greed Index para enriquecer decisiones del radar
Autor: AIDA (Artificial Intelligence Data Architect)
Fecha: 25 de octubre de 2025
"""

import requests
import json
from typing import Dict, Optional
from datetime import datetime
from bs4 import BeautifulSoup
import re
import warnings
warnings.filterwarnings('ignore')


class MacroContext:
    """
    Obtiene contexto macroeconómico desde FRED API
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Args:
            api_key: FRED API key (obtener gratis en https://fred.stlouisfed.org)
        """
        self.api_key = api_key
        self.base_url = "https://api.stlouisfed.org/fred/series/observations"
        self.cache = {}  # Cache para evitar llamadas repetidas
        
    def get_fred_data(self, series_id: str) -> Optional[float]:
        """
        Obtiene el último valor de una serie de FRED
        
        Args:
            series_id: ID de la serie (ej. 'FEDFUNDS', 'CPIAUCSL')
            
        Returns:
            Último valor de la serie o None si falla
        """
        if not self.api_key:
            print("⚠️ FRED API key no configurada. Usando valores por defecto.")
            return None
        
        # Revisar cache
        if series_id in self.cache:
            return self.cache[series_id]
        
        try:
            params = {
                'series_id': series_id,
                'api_key': self.api_key,
                'limit': 1,
                'sort_order': 'desc',
                'file_type': 'json'
            }
            
            response = requests.get(self.base_url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            observations = data.get('observations', [])
            
            if observations:
                value = float(observations[0]['value'])
                self.cache[series_id] = value
                return value
            
        except Exception as e:
            print(f"⚠️ Error obteniendo {series_id} de FRED: {e}")
        
        return None
    
    def get_macro_context(self) -> Dict:
        """
        Obtiene contexto macroeconómico completo
        
        Returns:
            Diccionario con indicadores macro y régimen de mercado
        """
        print("\n📊 Obteniendo contexto macroeconómico...")
        
        context = {
            'timestamp': datetime.now().isoformat(),
            'fed_rate': None,
            'inflation_yoy': None,
            'unemployment': None,
            'yield_curve_10y2y': None,
            'regime': 'unknown',
            'risk_level': 'medium'
        }
        
        # Obtener datos
        fed_rate = self.get_fred_data('FEDFUNDS')
        inflation = self.get_fred_data('CPIAUCSL')
        unemployment = self.get_fred_data('UNRATE')
        yield_curve = self.get_fred_data('T10Y2Y')
        
        context['fed_rate'] = fed_rate
        context['unemployment'] = unemployment
        context['yield_curve_10y2y'] = yield_curve
        
        # Calcular inflación YoY (simplificado)
        if inflation:
            context['inflation_yoy'] = 3.2  # Placeholder (requiere cálculo con datos históricos)
        
        # Clasificar régimen de mercado
        context['regime'] = self._classify_regime(fed_rate, unemployment, yield_curve)
        context['risk_level'] = self._assess_risk(yield_curve, unemployment)
        
        # Mostrar resumen
        if context['regime'] != 'unknown':
            print(f"   Régimen: {context['regime'].upper()}")
            print(f"   Nivel de riesgo: {context['risk_level'].upper()}")
            if fed_rate:
                print(f"   Tasa Fed: {fed_rate:.2f}%")
            if unemployment:
                print(f"   Desempleo: {unemployment:.1f}%")
            if yield_curve is not None:
                print(f"   Curva 10Y-2Y: {yield_curve:.2f}%")
        else:
            print("   ⚠️ Usando contexto por defecto (API no disponible)")
        
        return context
    
    def _classify_regime(self, fed_rate: Optional[float], 
                         unemployment: Optional[float], 
                         yield_curve: Optional[float]) -> str:
        """
        Clasifica el régimen de mercado actual
        
        Returns:
            'expansión', 'recesión', 'transición', 'unknown'
        """
        if yield_curve is None or unemployment is None:
            return 'unknown'
        
        # Curva invertida (10Y-2Y < 0) = alto riesgo de recesión
        if yield_curve < 0:
            if unemployment > 5.0:
                return 'recesión'
            else:
                return 'transición'  # Señal de alerta
        
        # Curva normal con bajo desempleo = expansión
        if yield_curve > 0.5 and unemployment < 4.5:
            return 'expansión'
        
        return 'transición'
    
    def _assess_risk(self, yield_curve: Optional[float], 
                     unemployment: Optional[float]) -> str:
        """
        Evalúa nivel de riesgo macro
        
        Returns:
            'low', 'medium', 'high'
        """
        if yield_curve is None or unemployment is None:
            return 'medium'
        
        risk_score = 0
        
        # Curva invertida = +2 puntos de riesgo
        if yield_curve < 0:
            risk_score += 2
        
        # Desempleo alto = +1 punto
        if unemployment > 5.5:
            risk_score += 1
        
        # Desempleo muy bajo (sobrecalentamiento) = +1 punto
        if unemployment < 3.5:
            risk_score += 1
        
        if risk_score >= 2:
            return 'high'
        elif risk_score == 1:
            return 'medium'
        else:
            return 'low'


class SentimentAnalyzer:
    """
    Analiza sentimiento del mercado usando Fear & Greed Index
    """
    
    def __init__(self):
        self.cache = {}
    
    def get_fear_greed_stocks(self) -> Dict:
        """
        Obtiene Fear & Greed Index para acciones desde feargreedmeter.com
        
        Returns:
            {'value': int, 'classification': str}
        """
        if 'stocks' in self.cache:
            return self.cache['stocks']
        
        try:
            # Nueva fuente: feargreedmeter.com
            url = "https://feargreedmeter.com/"
            
            # Headers para simular navegador real
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1'
            }
            
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            # Parse HTML con BeautifulSoup
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Buscar el valor del índice (número grande en el centro)
            # Buscar todos los divs y filtrar por clases
            fear_greed_value = None
            
            for div in soup.find_all('div'):
                classes = div.get('class', [])
                # Buscar div con clases específicas: text-center text-4xl font-semibold mb-1 text-white
                if ('text-center' in classes and 'text-4xl' in classes and 
                    'font-semibold' in classes and 'text-white' in classes):
                    text = div.text.strip()
                    if text.isdigit():
                        fear_greed_value = int(text)
                        break
            
            if fear_greed_value is None:
                raise ValueError("No se pudo encontrar el valor del índice")
            
            # Clasificación inferida según valor (estándar Fear & Greed)
            if fear_greed_value < 25:
                classification = "Extreme Fear"
            elif fear_greed_value < 45:
                classification = "Fear"
            elif fear_greed_value < 55:
                classification = "Neutral"
            elif fear_greed_value < 75:
                classification = "Greed"
            else:
                classification = "Extreme Greed"
            
            result = {
                'value': fear_greed_value,
                'classification': classification,
                'timestamp': datetime.now().isoformat(),
                'source': 'feargreedmeter.com'
            }
            
            self.cache['stocks'] = result
            return result
            
        except Exception as e:
            print(f"⚠️ Error obteniendo Fear & Greed (stocks): {e}")
            return {
                'value': 50,
                'classification': 'Neutral',
                'timestamp': datetime.now().isoformat(),
                'source': 'fallback'
            }
    
    def get_fear_greed_crypto(self) -> Dict:
        """
        Obtiene Fear & Greed Index de Alternative.me para crypto
        
        Returns:
            {'value': int, 'classification': str}
        """
        if 'crypto' in self.cache:
            return self.cache['crypto']
        
        try:
            url = "https://api.alternative.me/fng/"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            fng_data = data.get('data', [{}])[0]
            
            result = {
                'value': int(fng_data.get('value', 50)),
                'classification': fng_data.get('value_classification', 'Neutral'),
                'timestamp': datetime.now().isoformat()
            }
            
            self.cache['crypto'] = result
            return result
            
        except Exception as e:
            print(f"⚠️ Error obteniendo Fear & Greed (crypto): {e}")
            return {
                'value': 50,
                'classification': 'Neutral',
                'timestamp': datetime.now().isoformat()
            }
    
    def get_sentiment_summary(self) -> Dict:
        """
        Obtiene resumen completo de sentimiento
        
        Returns:
            Diccionario con sentimiento de stocks y crypto
        """
        print("\n📊 Obteniendo sentimiento del mercado...")
        
        stocks_sentiment = self.get_fear_greed_stocks()
        crypto_sentiment = self.get_fear_greed_crypto()
        
        print(f"   Stocks Fear & Greed: {stocks_sentiment['value']} ({stocks_sentiment['classification']})")
        print(f"   Crypto Fear & Greed: {crypto_sentiment['value']} ({crypto_sentiment['classification']})")
        
        return {
            'stocks': stocks_sentiment,
            'crypto': crypto_sentiment,
            'overall_sentiment': self._classify_overall(stocks_sentiment['value'], crypto_sentiment['value'])
        }
    
    def _classify_overall(self, stocks_value: int, crypto_value: int) -> str:
        """
        Clasifica sentimiento general
        
        Returns:
            'extreme_fear', 'fear', 'neutral', 'greed', 'extreme_greed'
        """
        avg = (stocks_value + crypto_value) / 2
        
        if avg < 25:
            return 'extreme_fear'
        elif avg < 45:
            return 'fear'
        elif avg < 55:
            return 'neutral'
        elif avg < 75:
            return 'greed'
        else:
            return 'extreme_greed'


class MarketContextIntegrated:
    """
    Clase integrada que combina macro + sentimiento
    """
    
    def __init__(self, fred_api_key: Optional[str] = None):
        """
        Args:
            fred_api_key: API key de FRED (opcional)
        """
        self.macro = MacroContext(fred_api_key)
        self.sentiment = SentimentAnalyzer()
    
    def get_full_context(self) -> Dict:
        """
        Obtiene contexto completo del mercado
        
        Returns:
            Diccionario con macro + sentimiento
        """
        print("\n" + "="*80)
        print("🌍 CONTEXTO DE MERCADO")
        print("="*80)
        
        macro_context = self.macro.get_macro_context()
        sentiment_context = self.sentiment.get_sentiment_summary()
        
        return {
            'macro': macro_context,
            'sentiment': sentiment_context,
            'timestamp': datetime.now().isoformat()
        }
    
    def get_trading_bias(self, context: Optional[Dict] = None) -> Dict:
        """
        Determina bias de trading basado en contexto
        
        Args:
            context: Contexto del mercado (si None, se obtiene nuevo)
            
        Returns:
            Diccionario con recomendaciones de bias
        """
        if context is None:
            context = self.get_full_context()
        
        regime = context['macro']['regime']
        risk_level = context['macro']['risk_level']
        sentiment = context['sentiment']['overall_sentiment']
        
        bias = {
            'recommended_strategy': 'balanced',
            'sector_preference': [],
            'risk_adjustment': 0,  # -1 = reducir riesgo, 0 = neutral, +1 = aumentar riesgo
            'reasoning': []
        }
        
        # === RÉGIMEN MACRO ===
        if regime == 'expansión':
            bias['recommended_strategy'] = 'growth'
            bias['sector_preference'] = ['Technology', 'Consumer Discretionary', 'Industrials']
            bias['risk_adjustment'] = 1
            bias['reasoning'].append("Expansión económica → Priorizar growth stocks")
        
        elif regime == 'recesión':
            bias['recommended_strategy'] = 'defensive'
            bias['sector_preference'] = ['Utilities', 'Consumer Staples', 'Healthcare']
            bias['risk_adjustment'] = -1
            bias['reasoning'].append("Recesión → Priorizar sectores defensivos")
        
        elif regime == 'transición':
            bias['recommended_strategy'] = 'cautious'
            bias['sector_preference'] = ['Healthcare', 'Consumer Staples', 'Technology']
            bias['risk_adjustment'] = 0
            bias['reasoning'].append("Transición → Estrategia balanceada")
        
        # === RIESGO MACRO ===
        if risk_level == 'high':
            bias['risk_adjustment'] -= 1
            bias['reasoning'].append("Riesgo macro elevado → Reducir exposición")
        
        # === SENTIMIENTO ===
        if sentiment == 'extreme_fear':
            bias['risk_adjustment'] += 1
            bias['reasoning'].append("Fear extremo → Oportunidad contrarian")
        
        elif sentiment == 'extreme_greed':
            bias['risk_adjustment'] -= 1
            bias['reasoning'].append("Greed extremo → Reducir exposición, posibles tops")
        
        # Normalizar risk_adjustment
        bias['risk_adjustment'] = max(-1, min(1, bias['risk_adjustment']))
        
        return bias


# Función auxiliar para testing
def test_market_context():
    """
    Función de prueba para verificar funcionamiento
    """
    print("🧪 Probando Market Context...\n")
    
    # Sin API key (modo demo)
    context = MarketContextIntegrated(fred_api_key=None)
    full_context = context.get_full_context()
    
    print("\n📊 Contexto obtenido:")
    print(f"   Régimen: {full_context['macro']['regime']}")
    print(f"   Riesgo: {full_context['macro']['risk_level']}")
    print(f"   Sentimiento: {full_context['sentiment']['overall_sentiment']}")
    
    print("\n🎯 Bias de trading:")
    bias = context.get_trading_bias(full_context)
    print(f"   Estrategia recomendada: {bias['recommended_strategy']}")
    print(f"   Sectores preferidos: {', '.join(bias['sector_preference'])}")
    print(f"   Ajuste de riesgo: {bias['risk_adjustment']}")
    print(f"\n   Razonamiento:")
    for reason in bias['reasoning']:
        print(f"     • {reason}")


if __name__ == "__main__":
    test_market_context()
