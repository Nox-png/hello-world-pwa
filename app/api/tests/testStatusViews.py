from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from django.contrib.auth.models import User
from unittest.mock import patch

class StatusViewsTests(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='apitest', password='apitest')
        self.client.force_authenticate(user=self.user)

    def test_showStatus(self):
        print("Test: Abruf Systemstatus")
        url = "/api/showStatus/"
        response = self.client.get(url)
        print("Response-Content:", response.content.decode())
        try:
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertIn('App Version', response.json())
            self.assertIn('App Build', response.json())
            self.assertIn('Python Version', response.json())
            self.assertIn('Django Version', response.json())
            self.assertIn('Datenbank Typ', response.json())
            self.assertIn('Datenbank Version', response.json())
            self.assertIn('Datenbank Name', response.json())
            self.assertIn('Installationstyp', response.json())
            print("✔️ Test: showStatus\n")
        except AssertionError as e:
            print(f"❌ Test fehlgeschlagen: {e}")
            print("Antwort:", response.content)
            print()
            raise

    def test_showStatus_requires_auth(self):
        print("Test: Auth-Pflicht für Systemstatus")
        unauth_client = APIClient()
        url = "/api/showStatus/"
        response = unauth_client.get(url)
        print("Response-Content:", response.content.decode())
        self.assertIn(response.status_code, [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN])
        print("✔️ Test: showStatus requires auth\n")

    @patch('api.modules.status.statusViews.getDBVersion', side_effect=Exception('db failed'))
    def test_showStatus_internal_error_payload(self, _mock_db_version):
        print("Test: showStatus interner Fehler")
        url = "/api/showStatus/"
        response = self.client.get(url)
        print("Response-Content:", response.content.decode())
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        self.assertEqual(response.json().get('error'), 'Interner Serverfehler.')
        print("✔️ Test: showStatus internal error payload\n")

    def test_health_check_public(self):
        print("Test: Öffentlicher Health-Check")
        unauth_client = APIClient()
        url = "/health/"
        response = unauth_client.get(url)
        print("Response-Content:", response.content.decode())
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json().get('status'), 'healthy')
        self.assertIn('timestamp', response.json())
        self.assertIn('app', response.json())
        self.assertIn('checks', response.json())
        self.assertEqual(response.json().get('checks', {}).get('database'), 'ok')
        print("✔️ Test: health check public\n")

    @patch('web.views.get_database_health', return_value=(False, 'db down'))
    def test_health_check_degraded(self, _mock_health):
        print("Test: Health-Check degraded bei DB-Fehler")
        url = "/health/"
        response = self.client.get(url)
        print("Response-Content:", response.content.decode())
        self.assertEqual(response.status_code, status.HTTP_503_SERVICE_UNAVAILABLE)
        self.assertEqual(response.json().get('status'), 'degraded')
        self.assertEqual(response.json().get('checks', {}).get('database'), 'error')
        self.assertIn('database_error', response.json().get('checks', {}))
        print("✔️ Test: health check degraded\n")