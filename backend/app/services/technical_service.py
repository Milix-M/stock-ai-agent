"""
テクニカル分析サービス
"""
from typing import List, Optional, Dict, Any
from dataclasses import dataclass
from datetime import datetime
import numpy as np


@dataclass
class TechnicalIndicators:
    """テクニカル指標"""
    sma_5: Optional[float] = None  # 5日単純移動平均
    sma_20: Optional[float] = None  # 20日単純移動平均
    sma_60: Optional[float] = None  # 60日単純移動平均
    ema_12: Optional[float] = None  # 12日指数移動平均
    ema_26: Optional[float] = None  # 26日指数移動平均
    rsi: Optional[float] = None  # 相対力指数
    macd: Optional[float] = None  # MACD
    macd_signal: Optional[float] = None  # MACDシグナル
    bb_upper: Optional[float] = None  # ボリンジャーバンド上限
    bb_middle: Optional[float] = None  # ボリンジャーバンド中央
    bb_lower: Optional[float] = None  # ボリンジャーバンド下限


class TechnicalAnalysisService:
    """テクニカル分析サービス"""
    
    def calculate_sma(self, prices: List[float], window: int) -> Optional[float]:
        """単純移動平均を計算"""
        if len(prices) < window:
            return None
        return sum(prices[-window:]) / window
    
    def calculate_ema(self, prices: List[float], window: int) -> Optional[float]:
        """指数移動平均を計算"""
        if len(prices) < window:
            return None
        
        alpha = 2 / (window + 1)
        ema = prices[0]
        for price in prices[1:]:
            ema = alpha * price + (1 - alpha) * ema
        return ema
    
    def calculate_rsi(self, prices: List[float], window: int = 14) -> Optional[float]:
        """RSI（相対力指数）を計算"""
        if len(prices) < window + 1:
            return None
        
        deltas = [prices[i] - prices[i-1] for i in range(1, len(prices))]
        gains = [d if d > 0 else 0 for d in deltas[-window:]]
        losses = [-d if d < 0 else 0 for d in deltas[-window:]]
        
        avg_gain = sum(gains) / window
        avg_loss = sum(losses) / window
        
        if avg_loss == 0:
            return 100.0
        
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    def calculate_macd(
        self, 
        prices: List[float], 
        fast: int = 12, 
        slow: int = 26, 
        signal: int = 9
    ) -> tuple:
        """MACDを計算"""
        if len(prices) < slow + signal:
            return None, None
        
        # 高速・低速EMA
        ema_fast = self.calculate_ema(prices, fast)
        ema_slow = self.calculate_ema(prices, slow)
        
        if ema_fast is None or ema_slow is None:
            return None, None
        
        macd = ema_fast - ema_slow
        
        # MACDのシグナル線（EMA）
        # 簡易的に直近のMACD値から計算
        macd_values = []
        for i in range(signal, len(prices) + 1):
            if i >= slow:
                fast_ema = self.calculate_ema(prices[:i], fast)
                slow_ema = self.calculate_ema(prices[:i], slow)
                if fast_ema and slow_ema:
                    macd_values.append(fast_ema - slow_ema)
        
        macd_signal = self.calculate_ema(macd_values, signal) if len(macd_values) >= signal else macd
        
        return macd, macd_signal
    
    def calculate_bollinger_bands(
        self, 
        prices: List[float], 
        window: int = 20, 
        num_std: float = 2.0
    ) -> tuple:
        """ボリンジャーバンドを計算"""
        if len(prices) < window:
            return None, None, None
        
        sma = self.calculate_sma(prices, window)
        std = np.std(prices[-window:])
        
        upper = sma + (std * num_std)
        lower = sma - (std * num_std)
        
        return upper, sma, lower
    
    async def analyze_stock(self, stock_prices: List[Dict[str, Any]]) -> TechnicalIndicators:
        """銘柄のテクニカル分析を実行"""
        if not stock_prices:
            return TechnicalIndicators()
        
        closes = [float(p["close"]) for p in stock_prices]
        
        # MACD計算
        macd, macd_signal = self.calculate_macd(closes)
        
        # ボリンジャーバンド計算
        bb_upper, bb_middle, bb_lower = self.calculate_bollinger_bands(closes)
        
        return TechnicalIndicators(
            sma_5=self.calculate_sma(closes, 5),
            sma_20=self.calculate_sma(closes, 20),
            sma_60=self.calculate_sma(closes, 60),
            ema_12=self.calculate_ema(closes, 12),
            ema_26=self.calculate_ema(closes, 26),
            rsi=self.calculate_rsi(closes),
            macd=macd,
            macd_signal=macd_signal,
            bb_upper=bb_upper,
            bb_middle=bb_middle,
            bb_lower=bb_lower,
        )
    
    def generate_signals(self, indicators: TechnicalIndicators) -> List[str]:
        """テクニカルシグナルを生成"""
        signals = []
        
        # RSIシグナル
        if indicators.rsi is not None:
            if indicators.rsi > 70:
                signals.append("RSIが70を超えています（過買いの可能性）")
            elif indicators.rsi < 30:
                signals.append("RSIが30を下回っています（過売りの可能性）")
        
        # MACDシグナル
        if indicators.macd is not None and indicators.macd_signal is not None:
            if indicators.macd > indicators.macd_signal:
                signals.append("MACDがシグナル線を上抜け（買いシグナル）")
            else:
                signals.append("MACDがシグナル線を下回っています（売りシグナル）")
        
        # 移動平均シグナル
        if indicators.sma_5 and indicators.sma_20:
            if indicators.sma_5 > indicators.sma_20:
                signals.append("短期移動平均が中期移動平均を上回っています（上昇トレンド）")
            else:
                signals.append("短期移動平均が中期移動平均を下回っています（下降トレンド）")
        
        return signals
