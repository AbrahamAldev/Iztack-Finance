"""Unit tests for classification service."""
from datetime import date, timedelta

from app.modules.clasificacion.service import ClassificationService


class TestClassificationService:
    def test_classify_product_alimentos(self):
        result = ClassificationService.classify_product("Leche Alpura 1L", price=25.0)
        assert result["category"] == "alimentos"
        assert result["is_consumable"] is True
        assert result["has_warranty"] is False

    def test_classify_product_electronicos(self):
        result = ClassificationService.classify_product("Televisor Samsung 50 pulgadas", price=8500.0)
        assert result["category"] == "electronicos"
        assert result["is_high_value"] is True
        assert result["has_warranty"] is True

    def test_check_expired_ticket(self):
        today = date.today()
        expired_date = today - timedelta(days=61)
        is_expired, days_remaining = ClassificationService.check_expired_ticket(expired_date)
        assert is_expired is True
        assert days_remaining < 0

    def test_detect_money_leak(self):
        result = ClassificationService.detect_money_leak(
            "Papel Higiénico", unit_price=25.0, bulk_price=85.0, bulk_quantity=12
        )
        assert result["has_leak"] is True
        assert result["savings_per_unit"] > 0

    def test_calculate_savings_goal(self):
        expenses = {"alimentos": 5000, "entretenimiento": 2000}
        result = ClassificationService.calculate_savings_goal(expenses, target_savings_percent=15)
        assert result["total_monthly_expenses"] == 7000
        assert result["target_monthly_savings"] == 1050
