# ============================================================
# chart_generator.py — Grafik Üretim (v2 - KOMPLE)
# ============================================================

import os
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime
import pandas as pd
import config

try:
    import numpy as np
except:
    import subprocess
    subprocess.run(["pip", "install", "numpy"], check=True)
    import numpy as np


def ensure_chart_dir():
    """Grafik klasörünü oluştur"""
    if not os.path.exists(config.CHART_DIR):
        os.makedirs(config.CHART_DIR)


def generate_charts(ticker: str, df: pd.DataFrame) -> str:
    """
    Hisse için teknik analiz grafiği oluştur
    Döndürür: Grafik dosya yolu
    """
    try:
        if df.empty or len(df) < 20:
            return None
        
        ensure_chart_dir()
        
        # Sütunları kontrol et
        if "Close" not in df.columns:
            return None
        
        close = df["Close"].squeeze()
        
        # Grafik oluştur
        fig, axes = plt.subplots(3, 1, figsize=(config.CHART_WIDTH, config.CHART_HEIGHT), dpi=config.CHART_DPI)
        fig.suptitle(f'{ticker} - Teknik Analiz', fontsize=16, fontweight='bold')
        
        # 1. Fiyat ve Moving Averages
        ax1 = axes[0]
        ax1.plot(df.index, close, label='Fiyat', color='black', linewidth=2)
        
        # SMA hesapla
        sma_short = close.rolling(window=config.SMA_SHORT).mean()
        sma_long = close.rolling(window=config.SMA_LONG).mean()
        
        ax1.plot(df.index, sma_short, label=f'SMA {config.SMA_SHORT}', color='blue', alpha=0.7)
        ax1.plot(df.index, sma_long, label=f'SMA {config.SMA_LONG}', color='red', alpha=0.7)
        
        ax1.set_title('Fiyat ve Hareketli Ortalamalar')
        ax1.legend(loc='best')
        ax1.grid(True, alpha=0.3)
        ax1.set_ylabel('Fiyat')
        
        # 2. Volume
        ax2 = axes[1]
        if "Volume" in df.columns:
            volume = df["Volume"].squeeze()
            colors = ['green' if close.iloc[i] > close.iloc[i-1] else 'red' 
                     for i in range(1, len(close))]
            colors.insert(0, 'gray')
            ax2.bar(df.index, volume, color=colors, alpha=0.6)
        
        ax2.set_title('Volume')
        ax2.set_ylabel('Hacim')
        ax2.grid(True, alpha=0.3)
        
        # 3. RSI
        ax3 = axes[2]
        
        # RSI hesapla
        delta = close.diff()
        gain = delta.where(delta > 0, 0.0)
        loss = (-delta).where(delta < 0, 0.0)
        
        avg_gain = gain.rolling(window=config.RSI_PERIOD).mean()
        avg_loss = loss.rolling(window=config.RSI_PERIOD).mean()
        
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        
        ax3.plot(df.index, rsi, label='RSI(14)', color='purple', linewidth=2)
        ax3.axhline(y=70, color='r', linestyle='--', label='Overbought (70)', alpha=0.7)
        ax3.axhline(y=30, color='g', linestyle='--', label='Oversold (30)', alpha=0.7)
        ax3.fill_between(df.index, 30, 70, alpha=0.1, color='gray')
        
        ax3.set_title('RSI (14)')
        ax3.set_ylabel('RSI')
        ax3.set_ylim(0, 100)
        ax3.legend(loc='best')
        ax3.grid(True, alpha=0.3)
        
        # X-axis formatting
        for ax in axes:
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
            ax.xaxis.set_major_locator(mdates.MonthLocator())
            plt.setp(ax.xaxis.get_majorticklabels(), rotation=45)
        
        plt.tight_layout()
        
        # Dosyayı kaydet
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{config.CHART_DIR}/{ticker}_{timestamp}.png"
        
        plt.savefig(filename, dpi=config.CHART_DPI, bbox_inches='tight')
        plt.close()
        
        return filename
        
    except Exception as e:
        print(f"[ERROR] Grafik oluşturma hatası ({ticker}): {e}")
        return None


if __name__ == "__main__":
    print("✅ chart_generator.py yüklendi başarıyla")
