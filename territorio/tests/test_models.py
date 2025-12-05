"""
Test suite for territorio models.
Tests model string representations (__str__) and model behavior.
"""

from decimal import Decimal

from django.test import TestCase

from territorio.models import AreaPrioritariaRadon, ComuneArpa, ComuneCompleto


class ComuneArpaModelTest(TestCase):
    """Test ComuneArpa model."""

    def test_str_representation(self):
        """Test __str__ method returns correct format."""
        comune = ComuneArpa(
            codice_istat="001001",
            nome="Torino",
            provincia="TO",
            media_radon=Decimal("150.5"),
        )
        expected = "Torino (TO)"
        assert str(comune) == expected

    def test_str_with_special_characters(self):
        """Test __str__ handles special characters."""
        comune = ComuneArpa(
            codice_istat="001002",
            nome="Saint-Vincent",
            provincia="AO",
        )
        expected = "Saint-Vincent (AO)"
        assert str(comune) == expected


class AreaPrioritariaRadonModelTest(TestCase):
    """Test AreaPrioritariaRadon model."""

    def test_str_representation_prioritaria(self):
        """Test __str__ method for prioritaria area."""
        area = AreaPrioritariaRadon(
            codice_istat="001001",
            nome="Torino",
            area_prioritaria="prioritaria",
        )
        expected = "Torino - AP: prioritaria"
        assert str(area) == expected

    def test_str_representation_non_prioritaria(self):
        """Test __str__ method for non prioritaria area."""
        area = AreaPrioritariaRadon(
            codice_istat="001002",
            nome="Milano",
            area_prioritaria="non prioritaria",
        )
        expected = "Milano - AP: non prioritaria"
        assert str(area) == expected

    def test_str_representation_attenzionata(self):
        """Test __str__ method for attenzionata area."""
        area = AreaPrioritariaRadon(
            codice_istat="001003",
            nome="Roma",
            area_prioritaria="attenzionata",
        )
        expected = "Roma - AP: attenzionata"
        assert str(area) == expected


class ComuneCompletoModelTest(TestCase):
    """Test ComuneCompleto model."""

    def test_str_representation(self):
        """Test __str__ method returns correct format."""
        comune = ComuneCompleto(
            codice_istat="001001",
            nome="Torino",
            provincia="TO",
        )
        expected = "Torino (TO)"
        assert str(comune) == expected

    def test_str_with_geometry(self):
        """Test __str__ with geometry field using WKT."""
        # ComuneCompleto uses POLYGON geometry, not Point
        polygon_wkt = "POLYGON((7.68 45.07, 7.69 45.07, 7.69 45.08, 7.68 45.08, 7.68 45.07))"
        comune = ComuneCompleto(
            codice_istat="001001",
            nome="Torino",
            provincia="TO",
            geom=polygon_wkt,
        )
        expected = "Torino (TO)"
        assert str(comune) == expected

    def test_str_with_all_fields(self):
        """Test __str__ includes only name and province."""
        comune = ComuneCompleto(
            codice_istat="001001",
            nome="Torino",
            provincia="TO",
            area_prioritaria="prioritaria",
            media_radon=Decimal("150.5"),
        )
        # __str__ should only show nome and provincia
        expected = "Torino (TO)"
        assert str(comune) == expected
