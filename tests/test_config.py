# ============================================================
# tests/test_config.py — Config Validation Testleri
# ============================================================

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import unittest
import config


class TestConfigTickers(unittest.TestCase):
    """BIST ticker format testleri"""

    def test_bist_tickers_have_is_suffix(self):
        """Tüm BIST ticker'ları .IS ile bitmeli"""
        for ticker in config.BIST_STOCKS:
            self.assertTrue(
                ticker.endswith(".IS"),
                f"{ticker} geçerli BIST formatında değil (.IS eksik)",
            )

    def test_no_turkish_chars_in_tickers(self):
        """Ticker'larda Türkçe karakter olmamalı"""
        turkish_chars = set("ÇçĞğİıÖöŞşÜü")
        for ticker in config.BIST_STOCKS:
            bad = [c for c in ticker if c in turkish_chars]
            self.assertFalse(
                bad,
                f"{ticker} Türkçe karakter içeriyor: {bad}",
            )

    def test_known_corrected_tickers_present(self):
        """Düzeltilmiş ticker'ların listede olması"""
        corrected = ["ISCTR.IS", "AKBNK.IS", "ARCLK.IS", "TUPRS.IS", "ENKAI.IS", "VESTL.IS"]
        for ticker in corrected:
            self.assertIn(ticker, config.BIST_STOCKS, f"{ticker} BIST_STOCKS içinde olmalı")

    def test_invalid_tickers_removed(self):
        """Geçersiz ticker'ların listede olmaması"""
        invalid = ["ISABANK.IS", "AKBANK.IS", "ARÇEL.IS", "TUPAS.IS", "ENKA.IS", "VESTEL.IS",
                   "PAGB.IS", "SEKB.IS", "AEFKS.IS", "NTTUR.IS", "GRNT.IS", "PSDTC.IS",
                   "PRIM.IS", "PARLX.IS", "ENTEL.IS", "GOLTS.IS", "GENIL.IS", "GEREL.IS",
                   "TRNFP.IS", "ORKA.IS", "ORKIM.IS", "YABNK.IS"]
        for ticker in invalid:
            self.assertNotIn(ticker, config.BIST_STOCKS, f"Geçersiz ticker {ticker} hâlâ listede")

    def test_all_stocks_not_empty(self):
        """ALL_STOCKS boş olmamalı"""
        self.assertGreater(len(config.ALL_STOCKS), 0)

    def test_all_stocks_is_union(self):
        """ALL_STOCKS = BIST_STOCKS + GLOBAL_STOCKS"""
        self.assertEqual(
            set(config.ALL_STOCKS),
            set(config.BIST_STOCKS) | set(config.GLOBAL_STOCKS),
        )


class TestConfigSectorMapping(unittest.TestCase):
    """STOCK_SECTORS mapping testleri"""

    def test_stock_sectors_exists(self):
        """STOCK_SECTORS config'de tanımlı olmalı"""
        self.assertTrue(hasattr(config, "STOCK_SECTORS"))
        self.assertIsInstance(config.STOCK_SECTORS, dict)
        self.assertGreater(len(config.STOCK_SECTORS), 0)

    def test_all_bist_stocks_have_sector(self):
        """Tüm BIST hisseleri STOCK_SECTORS içinde olmalı"""
        for ticker in config.BIST_STOCKS:
            self.assertIn(
                ticker,
                config.STOCK_SECTORS,
                f"{ticker} STOCK_SECTORS içinde tanımlanmamış",
            )

    def test_sector_values_are_known(self):
        """Tüm sektör değerleri ALL_SECTORS veya özel kategorilerde olmalı"""
        allowed = set(config.ALL_SECTORS) | {"savunma", "madencilik", "indeks", "ulaştırma"}
        for ticker, sector in config.STOCK_SECTORS.items():
            self.assertIn(
                sector,
                allowed,
                f"{ticker} sektörü '{sector}' tanınan sektörler içinde değil",
            )


class TestConfigValidation(unittest.TestCase):
    """validate_config() fonksiyon testleri"""

    def test_validate_config_returns_list(self):
        """validate_config() bir liste döndürmeli"""
        result = config.validate_config()
        self.assertIsInstance(result, list)

    def test_validate_config_catches_missing_keys(self):
        """Varsayılan (placeholder) değerlerle uyarı üretmeli"""
        errors = config.validate_config()
        self.assertIsInstance(errors, list)
        # Ortam değişkenleri ayarlanmamışsa en az bir uyarı beklenir
        self.assertGreater(len(errors), 0, "Placeholder değerler için uyarı üretilmeli")


if __name__ == "__main__":
    unittest.main()
