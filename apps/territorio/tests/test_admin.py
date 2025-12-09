from unittest.mock import MagicMock, Mock, patch

from django.contrib.admin.sites import AdminSite
from django.test import SimpleTestCase

from apps.territorio.admin import ComuneArpaAdmin
from apps.territorio.models import ComuneArpa, ComuneCompleto


class ComuneArpaAdminPermissionsTest(SimpleTestCase):
    """Test per verificare che l'admin sia readonly (senza DB)"""

    def setUp(self):
        self.site = AdminSite()
        self.admin = ComuneArpaAdmin(ComuneArpa, self.site)
        self.request = Mock()

    def test_has_add_permission_false(self):
        """Verifica che add non sia permesso"""
        self.assertFalse(self.admin.has_add_permission(self.request))

    def test_has_change_permission_false(self):
        """Verifica che change non sia permesso"""
        self.assertFalse(self.admin.has_change_permission(self.request))

    def test_has_delete_permission_false(self):
        """Verifica che delete non sia permesso"""
        self.assertFalse(self.admin.has_delete_permission(self.request))

    def test_readonly_fields_configured(self):
        """Verifica che i campi readonly siano configurati"""
        expected_readonly = {
            "codice_istat",
            "nome",
            "provincia",
            "media_radon",
            "area_prioritaria_display",
            "dati_geologici_display",
            "mappa_confini",
        }
        self.assertEqual(set(self.admin.readonly_fields), expected_readonly)

    def test_list_display_configured(self):
        """Verifica che list_display sia configurato correttamente"""
        self.assertIn("codice_istat", self.admin.list_display)
        self.assertIn("nome", self.admin.list_display)

    def test_list_filter_configured(self):
        """Verifica che list_filter sia configurato"""
        self.assertIsNotNone(self.admin.list_filter)

    def test_search_fields_configured(self):
        """Verifica che search_fields sia configurato"""
        self.assertIsNotNone(self.admin.search_fields)


class ComuneArpaAdminDisplayMethodsTest(SimpleTestCase):
    """Test per i metodi display (con mock, senza DB)"""

    def setUp(self):
        self.site = AdminSite()
        self.admin = ComuneArpaAdmin(ComuneArpa, self.site)

    # ===== Test area_prioritaria_display =====
    @patch("apps.territorio.admin.ComuneCompleto.objects.get")
    def test_area_prioritaria_display_no_data(self, mock_get):
        """Testa area_prioritaria_display quando ComuneCompleto non esiste"""
        mock_get.side_effect = ComuneCompleto.DoesNotExist()
        comune = Mock(spec=ComuneArpa)
        comune.codice_istat = "999999"
        result = self.admin.area_prioritaria_display(comune)
        self.assertIsNotNone(result)
        self.assertGreater(len(result), 0)

    @patch("apps.territorio.admin.ComuneCompleto.objects.get")
    def test_area_prioritaria_display_with_area_prioritaria(self, mock_get):
        """Testa area_prioritaria_display con area prioritaria presente"""
        mock_comune_completo = Mock(spec=ComuneCompleto)
        mock_comune_completo.area_prioritaria = "Prioritaria"
        mock_get.return_value = mock_comune_completo

        comune = Mock(spec=ComuneArpa)
        comune.codice_istat = "001001"
        result = self.admin.area_prioritaria_display(comune)

        self.assertIsNotNone(result)
        self.assertGreater(len(result), 0)
        # Verifica che il badge sia renderizzato
        self.assertIn("bg-", result)

    @patch("apps.territorio.admin.ComuneCompleto.objects.get")
    def test_area_prioritaria_display_without_area_prioritaria(self, mock_get):
        """Testa area_prioritaria_display senza area prioritaria"""
        mock_comune_completo = Mock(spec=ComuneCompleto)
        mock_comune_completo.area_prioritaria = None
        mock_get.return_value = mock_comune_completo

        comune = Mock(spec=ComuneArpa)
        comune.codice_istat = "001002"
        result = self.admin.area_prioritaria_display(comune)

        self.assertIsNotNone(result)

    @patch("apps.territorio.admin.ComuneCompleto.objects.get")
    def test_area_prioritaria_display_null_ap(self, mock_get):
        """Testa area_prioritaria_display quando area_prioritaria è None"""
        mock_comune_completo = Mock(spec=ComuneCompleto)
        mock_comune_completo.area_prioritaria = None
        mock_get.return_value = mock_comune_completo

        comune = Mock(spec=ComuneArpa)
        comune.codice_istat = "001003"
        result = self.admin.area_prioritaria_display(comune)

        self.assertIsNotNone(result)

    @patch("apps.territorio.admin.ComuneCompleto.objects.get")
    def test_area_prioritaria_display_with_cache(self, mock_get):
        """Testa area_prioritaria_display quando la cache è già presente"""
        mock_comune_completo = Mock(spec=ComuneCompleto)
        mock_comune_completo.area_prioritaria = "Prioritaria"

        comune = Mock(spec=ComuneArpa)
        comune.codice_istat = "001021"
        # Simula che la cache sia già presente
        comune._cached_comune_completo = mock_comune_completo

        result = self.admin.area_prioritaria_display(comune)

        self.assertIsNotNone(result)
        # Verifica che non abbia fatto una query al DB perché la cache era presente
        mock_get.assert_not_called()
        """Testa area_prioritaria_display con testo 'Prioritaria'"""
        mock_comune_completo = Mock(spec=ComuneCompleto)
        mock_comune_completo.area_prioritaria = "Prioritaria"
        mock_get.return_value = mock_comune_completo

        comune = Mock(spec=ComuneArpa)
        comune.codice_istat = "001018"
        result = self.admin.area_prioritaria_display(comune)

        self.assertIsNotNone(result)
        # Deve avere il badge rosso per "prioritaria"
        self.assertIn("bg-red-600", result)

    @patch("apps.territorio.admin.ComuneCompleto.objects.get")
    def test_area_prioritaria_display_attenzione(self, mock_get):
        """Testa area_prioritaria_display con testo 'Attenzione'"""
        mock_comune_completo = Mock(spec=ComuneCompleto)
        mock_comune_completo.area_prioritaria = "Attenzione"
        mock_get.return_value = mock_comune_completo

        comune = Mock(spec=ComuneArpa)
        comune.codice_istat = "001019"
        result = self.admin.area_prioritaria_display(comune)

        self.assertIsNotNone(result)
        # Deve avere il badge arancione per "attenzione"
        self.assertIn("bg-amber-500", result)

    @patch("apps.territorio.admin.ComuneCompleto.objects.get")
    def test_area_prioritaria_display_prioritaria_text(self, mock_get):
        """Testa area_prioritaria_display con testo 'Prioritaria'"""
        mock_comune_completo = Mock(spec=ComuneCompleto)
        mock_comune_completo.area_prioritaria = "Prioritaria"
        mock_get.return_value = mock_comune_completo

        comune = Mock(spec=ComuneArpa)
        comune.codice_istat = "001018"
        result = self.admin.area_prioritaria_display(comune)

        self.assertIsNotNone(result)
        # Deve avere il badge rosso per "prioritaria"
        self.assertIn("bg-red-600", result)

    @patch("apps.territorio.admin.ComuneCompleto.objects.get")
    def test_area_prioritaria_display_prioritari_keyword(self, mock_get):
        """Testa area_prioritaria_display con keyword 'prioritari' (senza 'non')"""
        mock_comune_completo = Mock(spec=ComuneCompleto)
        # Test specifico per la branch: "prioritari" in ap_lower AND "non" not in ap_lower
        mock_comune_completo.area_prioritaria = "Zone Prioritarie"
        mock_get.return_value = mock_comune_completo

        comune = Mock(spec=ComuneArpa)
        comune.codice_istat = "001023"
        result = self.admin.area_prioritaria_display(comune)

        self.assertIsNotNone(result)
        # Deve avere il badge rosso perché contiene "prioritari" ma non "non"
        self.assertIn("bg-red-600", result)
        self.assertIn("Zone Prioritarie", result)

    # ===== Test dati_geologici_display =====
    @patch("apps.territorio.admin.ComuneCompleto.objects.get")
    def test_dati_geologici_display_no_data(self, mock_get):
        """Testa dati_geologici_display quando ComuneCompleto non esiste"""
        mock_get.side_effect = ComuneCompleto.DoesNotExist()
        comune = Mock(spec=ComuneArpa)
        comune.codice_istat = "999999"
        result = self.admin.dati_geologici_display(comune)
        self.assertIsNotNone(result)
        self.assertGreater(len(result), 0)

    @patch("apps.territorio.admin.ComuneCompleto.objects.get")
    def test_dati_geologici_display_with_full_data(self, mock_get):
        """Testa dati_geologici_display con tutti i dati geologici presenti"""
        mock_comune_completo = Mock(spec=ComuneCompleto)
        mock_comune_completo.unita_litologica = "Granito"
        mock_comune_completo.litologia = "Granito rosa"
        mock_comune_completo.formazione = "Formazione XYZ"
        mock_comune_completo.fascia_eta = "Paleozoico"
        mock_get.return_value = mock_comune_completo

        comune = Mock(spec=ComuneArpa)
        comune.codice_istat = "001004"
        result = self.admin.dati_geologici_display(comune)

        self.assertIsNotNone(result)
        self.assertGreater(len(result), 0)

    @patch("apps.territorio.admin.ComuneCompleto.objects.get")
    def test_dati_geologici_display_partial_data(self, mock_get):
        """Testa dati_geologici_display con alcuni dati mancanti"""
        mock_comune_completo = Mock(spec=ComuneCompleto)
        mock_comune_completo.unita_litologica = "Granito"
        mock_comune_completo.litologia = None
        mock_comune_completo.formazione = "Formazione XYZ"
        mock_comune_completo.fascia_eta = None
        mock_get.return_value = mock_comune_completo

        comune = Mock(spec=ComuneArpa)
        comune.codice_istat = "001005"
        result = self.admin.dati_geologici_display(comune)

        self.assertIsNotNone(result)
        # Verifica che il template sia renderizzato
        self.assertGreater(len(result), 0)

    @patch("apps.territorio.admin.ComuneCompleto.objects.get")
    def test_dati_geologici_display_all_empty(self, mock_get):
        """Testa dati_geologici_display quando tutti i dati sono None"""
        mock_comune_completo = Mock(spec=ComuneCompleto)
        mock_comune_completo.unita_litologica = None
        mock_comune_completo.litologia = None
        mock_comune_completo.formazione = None
        mock_comune_completo.fascia_eta = None
        mock_comune_completo.classe_permeabilita = None
        mock_comune_completo.distanza_faglia_m = None
        mock_get.return_value = mock_comune_completo

        comune = Mock(spec=ComuneArpa)
        comune.codice_istat = "001016"
        result = self.admin.dati_geologici_display(comune)

        self.assertIsNotNone(result)
        self.assertGreater(len(result), 0)

    @patch("apps.territorio.admin.ComuneCompleto.objects.get")
    def test_dati_geologici_display_with_permeability(self, mock_get):
        """Testa dati_geologici_display con dati di permeabilità"""
        mock_comune_completo = Mock(spec=ComuneCompleto)
        mock_comune_completo.unita_litologica = None
        mock_comune_completo.litologia = None
        mock_comune_completo.classe_permeabilita = 2  # Media
        mock_comune_completo.distanza_faglia_m = 500
        mock_get.return_value = mock_comune_completo

        comune = Mock(spec=ComuneArpa)
        comune.codice_istat = "001017"
        result = self.admin.dati_geologici_display(comune)

        self.assertIsNotNone(result)
        self.assertGreater(len(result), 0)

    @patch("apps.territorio.admin.ComuneCompleto.objects.get")
    def test_dati_geologici_display_with_cache(self, mock_get):
        """Testa dati_geologici_display quando la cache è già presente"""
        mock_comune_completo = Mock(spec=ComuneCompleto)
        mock_comune_completo.unita_litologica = "Granito"
        mock_comune_completo.litologia = "Granito rosa"

        comune = Mock(spec=ComuneArpa)
        comune.codice_istat = "001022"
        # Simula che la cache sia già presente
        comune._cached_comune_completo = mock_comune_completo

        result = self.admin.dati_geologici_display(comune)

        self.assertIsNotNone(result)
        # Verifica che non abbia fatto una query al DB
        mock_get.assert_not_called()

    # ===== Test mappa_confini =====
    def test_mappa_confini_no_geom(self):
        """Testa mappa_confini quando geometria è assente"""
        comune = Mock(spec=ComuneArpa)
        comune.codice_istat = "999999"
        comune.geom = None
        result = self.admin.mappa_confini(comune)
        self.assertIn("Nessuna geometria", result)

    def test_mappa_confini_with_geom(self):
        """Testa mappa_confini con geometria valida"""
        comune = Mock(spec=ComuneArpa)
        comune.codice_istat = "001006"
        # Mock della geometria con metodo wkt
        mock_geom = MagicMock()
        mock_geom.wkt = "POLYGON ((0 0, 1 0, 1 1, 0 1, 0 0))"
        comune.geom = mock_geom

        result = self.admin.mappa_confini(comune)
        self.assertIsNotNone(result)
        self.assertGreater(len(result), 0)
        # Verifica che contenga tag Leaflet
        self.assertIn("leaflet", result.lower())

    def test_mappa_confini_with_none_geom(self):
        """Testa mappa_confini con geom=None in modo esplicito"""
        comune = Mock(spec=ComuneArpa)
        comune.codice_istat = "001007"
        comune.geom = None
        result = self.admin.mappa_confini(comune)
        # Deve contenere fallback message
        self.assertIn("Nessuna geometria", result)

    def test_mappa_confini_object_attributes(self):
        """Testa che mappa_confini contenga i dati del comune"""
        comune = Mock(spec=ComuneArpa)
        comune.codice_istat = "001008"
        comune.nome = "Test Comune"
        comune.provincia = "TO"
        mock_geom = MagicMock()
        mock_geom.wkt = "POLYGON ((0 0, 1 0, 1 1, 0 1, 0 0))"
        mock_geom.geojson = '{"type": "Polygon", "coordinates": [[[0, 0], [1, 0], [1, 1], [0, 1], [0, 0]]]}'
        comune.geom = mock_geom

        result = self.admin.mappa_confini(comune)
        self.assertIn("001008", result)
        self.assertIn("Test Comune", result)
        self.assertIn("TO", result)

    # ===== Test media_radon_display =====
    def test_media_radon_display_no_data(self):
        """Testa media_radon_display quando media_radon è None"""
        comune = Mock(spec=ComuneArpa)
        comune.codice_istat = "999999"
        comune.media_radon = None
        result = self.admin.media_radon_display(comune)
        self.assertIn("N/D", result)

    def test_media_radon_display_with_value(self):
        """Testa media_radon_display con valore presente"""
        comune = Mock(spec=ComuneArpa)
        comune.codice_istat = "001008"
        comune.media_radon = 150.5
        result = self.admin.media_radon_display(comune)
        self.assertIn("150.5", result)

    def test_media_radon_display_with_zero_value(self):
        """Testa media_radon_display con valore 0"""
        comune = Mock(spec=ComuneArpa)
        comune.codice_istat = "001009"
        comune.media_radon = 0
        result = self.admin.media_radon_display(comune)
        self.assertIn("0", result)

    def test_media_radon_display_with_high_value(self):
        """Testa media_radon_display con valore alto (>300 Bq/m³)"""
        comune = Mock(spec=ComuneArpa)
        comune.codice_istat = "001010"
        comune.media_radon = 450.75
        result = self.admin.media_radon_display(comune)
        # Il valore è arrotondato a 1 decimale: 450.8
        self.assertIn("450.8", result)
        # Verifica che sia rosso (colore > 300)
        self.assertIn("#dc2626", result)

    def test_media_radon_display_with_low_value(self):
        """Testa media_radon_display con valore basso"""
        comune = Mock(spec=ComuneArpa)
        comune.codice_istat = "001011"
        comune.media_radon = 25.3
        result = self.admin.media_radon_display(comune)
        self.assertIn("25.3", result)

    def test_media_radon_display_boundary_200(self):
        """Testa media_radon_display al confine 200 Bq/m³ (verde->arancione)"""
        comune = Mock(spec=ComuneArpa)
        comune.codice_istat = "001012"
        comune.media_radon = 200.0
        result = self.admin.media_radon_display(comune)
        self.assertIn("200.0", result)
        # 200 non è > 300 e non è > 200, quindi verde
        self.assertIn("#10b981", result)

    def test_media_radon_display_boundary_200_1(self):
        """Testa media_radon_display appena sopra 200 Bq/m³ (arancione)"""
        comune = Mock(spec=ComuneArpa)
        comune.codice_istat = "001013"
        comune.media_radon = 200.1
        result = self.admin.media_radon_display(comune)
        # 200.1 è > 200 ma < 300, quindi arancione
        self.assertIn("#f59e0b", result)

    def test_media_radon_display_boundary_300(self):
        """Testa media_radon_display al confine 300 Bq/m³ (arancione->rosso)"""
        comune = Mock(spec=ComuneArpa)
        comune.codice_istat = "001014"
        comune.media_radon = 300.0
        result = self.admin.media_radon_display(comune)
        # 300 non è > 300, quindi arancione
        self.assertIn("#f59e0b", result)

    def test_media_radon_display_boundary_300_1(self):
        """Testa media_radon_display appena sopra 300 Bq/m³ (rosso)"""
        comune = Mock(spec=ComuneArpa)
        comune.codice_istat = "001015"
        comune.media_radon = 300.1
        result = self.admin.media_radon_display(comune)
        # 300.1 è > 300, quindi rosso
        self.assertIn("#dc2626", result)

    # ===== Test admin configuration =====
    def test_admin_list_display(self):
        """Verifica che list_display sia configurato"""
        self.assertIsNotNone(self.admin.list_display)
        self.assertIn("nome", self.admin.list_display)

    def test_admin_has_view_permission(self):
        """Verifica che view permission sia configurato"""
        request = Mock()
        result = self.admin.has_view_permission(request)
        # La view permission non dovrebbe essere disabilitata
        self.assertTrue(result is not False)

    # ===== Test get_object() e caching =====
    def test_has_delete_permission_is_false(self):
        """Verifica che delete permission sia false"""
        request = Mock()
        self.assertFalse(self.admin.has_delete_permission(request))

    def test_has_delete_permission_with_obj_is_false(self):
        """Verifica che delete permission sia false anche con obj"""
        request = Mock()
        obj = Mock()
        self.assertFalse(self.admin.has_delete_permission(request, obj))

    # ===== Test classe_permeabilita_display =====
    def test_classe_permeabilita_display_alta(self):
        """Testa classe_permeabilita_display con classe Alta (1)"""
        comune = Mock(spec=ComuneArpa)
        comune.classe_permeabilita = 1
        result = self.admin.classe_permeabilita_display(comune)
        self.assertIn("Alta", result)
        self.assertIn("#10b981", result)

    def test_classe_permeabilita_display_media(self):
        """Testa classe_permeabilita_display con classe Media (2)"""
        comune = Mock(spec=ComuneArpa)
        comune.classe_permeabilita = 2
        result = self.admin.classe_permeabilita_display(comune)
        self.assertIn("Media", result)
        self.assertIn("#fcd34d", result)

    def test_classe_permeabilita_display_bassa(self):
        """Testa classe_permeabilita_display con classe Bassa (3)"""
        comune = Mock(spec=ComuneArpa)
        comune.classe_permeabilita = 3
        result = self.admin.classe_permeabilita_display(comune)
        self.assertIn("Bassa", result)
        self.assertIn("#f59e0b", result)

    def test_classe_permeabilita_display_molto_bassa(self):
        """Testa classe_permeabilita_display con classe Molto Bassa (4)"""
        comune = Mock(spec=ComuneArpa)
        comune.classe_permeabilita = 4
        result = self.admin.classe_permeabilita_display(comune)
        self.assertIn("Molto Bassa", result)
        self.assertIn("#dc2626", result)

    def test_classe_permeabilita_display_unknown(self):
        """Testa classe_permeabilita_display con classe sconosciuta"""
        comune = Mock(spec=ComuneArpa)
        comune.classe_permeabilita = 99  # valore non mappato
        result = self.admin.classe_permeabilita_display(comune)
        self.assertIn("Sconosciuta", result)
        self.assertIn("#6b7280", result)

    def test_classe_permeabilita_display_none(self):
        """Testa classe_permeabilita_display quando è None"""
        comune = Mock(spec=ComuneArpa)
        comune.classe_permeabilita = None
        result = self.admin.classe_permeabilita_display(comune)
        self.assertIn("N/D", result)
        self.assertIn("#9ca3af", result)


class DatiMissingFilterTest(SimpleTestCase):
    """Test per DatiMissingFilter"""

    def setUp(self):
        from django.test import RequestFactory

        from apps.territorio.admin import DatiMissingFilter

        self.factory = RequestFactory()
        self.request = self.factory.get("/admin/")
        self.filter_class = DatiMissingFilter

    def test_lookups_returns_correct_tuples(self):
        """Test che lookups() restituisce le opzioni corrette - covers line 18"""
        filter_instance = self.filter_class(self.request, {}, Mock(), Mock())
        lookups = filter_instance.lookups(self.request, Mock())

        # Verifica il formato e i valori
        self.assertIsInstance(lookups, tuple)
        self.assertEqual(len(lookups), 2)
        self.assertEqual(lookups[0], ("radon_missing", "Senza media radon"))
        self.assertEqual(lookups[1], ("completi", "Dati completi"))

    def test_filter_title(self):
        """Test che il titolo del filter sia corretto"""
        self.assertEqual(self.filter_class.title, "Completezza Dati")

    def test_filter_parameter_name(self):
        """Test che parameter_name sia corretto"""
        self.assertEqual(self.filter_class.parameter_name, "dati_missing")


class AreaPrioritariaRadonAdminTest(SimpleTestCase):
    """Test per l'admin AreaPrioritariaRadon"""

    def setUp(self):
        from apps.territorio.admin import AreaPrioritariaRadonAdmin

        self.site = AdminSite()
        self.admin = AreaPrioritariaRadonAdmin(Mock(), self.site)

    def test_list_display_configured(self):
        """Verifica che list_display sia configurato"""
        self.assertIsNotNone(self.admin.list_display)

    def test_search_fields_configured(self):
        """Verifica che search_fields sia configurato"""
        self.assertIsNotNone(self.admin.search_fields)

    def test_list_filter_configured(self):
        """Verifica che list_filter sia configurato"""
        self.assertIsNotNone(self.admin.list_filter)

    def test_readonly_fields_configured(self):
        """Verifica che readonly_fields sia configurato"""
        self.assertIsNotNone(self.admin.readonly_fields)

    def test_area_prioritaria_display_no_data(self):
        """Testa area_prioritaria_display di AreaPrioritariaRadon quando N/D"""
        area = Mock()
        area.area_prioritaria = "N/D"
        result = self.admin.area_prioritaria_display(area)
        self.assertIn("Non disponibile", result)
        self.assertIn("text-gray-400", result)  # Tailwind class per grigio

    def test_area_prioritaria_display_none(self):
        """Testa area_prioritaria_display di AreaPrioritariaRadon quando None"""
        area = Mock()
        area.area_prioritaria = None
        result = self.admin.area_prioritaria_display(area)
        self.assertIn("Non disponibile", result)

    def test_area_prioritaria_display_prioritaria(self):
        """Testa area_prioritaria_display di AreaPrioritariaRadon con 'Prioritaria'"""
        area = Mock()
        area.area_prioritaria = "Prioritaria"
        result = self.admin.area_prioritaria_display(area)
        self.assertIn("Prioritaria", result)
        self.assertIn("bg-red-600", result)  # Tailwind: rosso

    def test_area_prioritaria_display_attenzione(self):
        """Testa area_prioritaria_display di AreaPrioritariaRadon con 'Attenzione'"""
        area = Mock()
        area.area_prioritaria = "Attenzione"
        result = self.admin.area_prioritaria_display(area)
        self.assertIn("Attenzione", result)
        self.assertIn("bg-amber-500", result)  # Tailwind: arancione

    def test_area_prioritaria_display_non_prioritaria(self):
        """Testa area_prioritaria_display di AreaPrioritariaRadon con 'Non Prioritaria'"""
        area = Mock()
        area.area_prioritaria = "Non Prioritaria"
        result = self.admin.area_prioritaria_display(area)
        self.assertIn("Non Prioritaria", result)
        self.assertIn("bg-emerald-600", result)  # Tailwind: verde

    def test_area_prioritaria_display_default(self):
        """Testa area_prioritaria_display di AreaPrioritariaRadon con valore sconosciuto"""
        area = Mock()
        area.area_prioritaria = "Categoria Sconosciuta"
        result = self.admin.area_prioritaria_display(area)
        self.assertIn("Categoria Sconosciuta", result)
        self.assertIn("bg-gray-500", result)  # Tailwind: grigio default

    def test_mappa_confini_no_geom(self):
        """Testa mappa_confini di AreaPrioritariaRadon senza geometria"""
        area = Mock()
        area.geom = None
        result = self.admin.mappa_confini(area)
        self.assertIn("Nessuna geometria", result)

    def test_mappa_confini_with_geom(self):
        """Testa mappa_confini di AreaPrioritariaRadon con geometria"""
        area = Mock()
        area.codice_istat = "001001"
        area.nome = "Area Prioritaria Test"
        area.provincia = "TO"
        mock_geom = MagicMock()
        mock_geom.geojson = '{"type": "Polygon"}'
        area.geom = mock_geom

        result = self.admin.mappa_confini(area)
        self.assertIsNotNone(result)
        self.assertIn("001001", result)
        self.assertIn("Area Prioritaria Test", result)

    def test_fields_configured(self):
        """Testa che fields sia configurato correttamente"""
        expected_fields = ("codice_istat", "nome", "provincia", "area_prioritaria", "mappa_confini")
        self.assertEqual(self.admin.fields, expected_fields)

    def test_short_description_set(self):
        """Testa che short_description sia impostato per area_prioritaria_display"""
        self.assertEqual(self.admin.area_prioritaria_display.short_description, "Piano Radon")

    def test_mappa_confini_short_description_set(self):
        """Testa che short_description sia impostato per mappa_confini"""
        self.assertEqual(self.admin.mappa_confini.short_description, "Mappa Confini Comunali")

    def test_has_add_permission_explicit(self):
        """Test esplicito che has_add_permission ritorna False"""
        result = self.admin.has_add_permission(Mock())
        self.assertIs(result, False)

    def test_has_change_permission_explicit(self):
        """Test esplicito che has_change_permission ritorna False"""
        result = self.admin.has_change_permission(Mock())
        self.assertIs(result, False)

    def test_has_change_permission_with_obj_explicit(self):
        """Test esplicito che has_change_permission ritorna False con obj"""
        result = self.admin.has_change_permission(Mock(), obj=Mock())
        self.assertIs(result, False)

    def test_has_delete_permission_explicit(self):
        """Test esplicito che has_delete_permission ritorna False"""
        result = self.admin.has_delete_permission(Mock())
        self.assertIs(result, False)

    def test_has_delete_permission_with_obj_explicit(self):
        """Test esplicito che has_delete_permission ritorna False con obj"""
        result = self.admin.has_delete_permission(Mock(), obj=Mock())
        self.assertIs(result, False)
