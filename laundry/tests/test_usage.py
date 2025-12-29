from django.test import TestCase, Client
from laundry.models import Inquilino, Maquina, HistoricoUso
from django.utils import timezone

class UsagePermissionsTest(TestCase):
    def setUp(self):
        self.client = Client()
        # Create a machine
        self.maquina = Maquina.objects.create(nome='M1', ip_address='192.168.0.10', status=Maquina.StatusMaquina.DISPONIVEL, tempo_minutos=30, custo_creditos=2)

    def _login_as(self, inquilino):
        session = self.client.session
        session['inquilino_id'] = inquilino.id
        session.save()

    def test_home_hides_use_button_when_no_credits(self):
        inquilino = Inquilino.objects.create(apartamento='2', password=None, creditos=0)
        self._login_as(inquilino)
        # sanity checks
        self.assertEqual(Inquilino.objects.count(), 1)
        self.assertEqual(Maquina.objects.count(), 1)
        self.assertEqual(Inquilino.objects.get(apartamento='2').apartamento, '2')
        resp = self.client.get('/home/')
        # verify view context
        self.assertIn('creditos_disponiveis', resp.context)
        self.assertEqual(resp.context['creditos_disponiveis'], 0)
        self.assertEqual(resp.context['inquilino'].apartamento, '2')
        self.assertContains(resp, 'Você não tem créditos disponíveis')
        # should not show the 'Usar' link
        self.assertNotContains(resp, 'Usar')
        self.assertContains(resp, 'Créditos insuficientes', status_code=200)

    def test_cannot_use_when_insufficient_credits_backend(self):
        inquilino = Inquilino.objects.create(apartamento='3', password=None, creditos=1)
        self._login_as(inquilino)
        # sanity checks
        self.assertEqual(Inquilino.objects.count(), 1)
        self.assertEqual(Maquina.objects.count(), 1)
        self.assertEqual(Inquilino.objects.get(apartamento='3').apartamento, '3')
        # attempt to use machine that costs 2 credits
        resp = self.client.get(f'/usar/{self.maquina.id}/', follow=True)
        # should redirect to home and show error about insufficient credits
        self.assertContains(resp, 'Créditos insuficientes.')
        # machine still available and no history created
        m = Maquina.objects.get(pk=self.maquina.pk)
        self.assertEqual(m.status, Maquina.StatusMaquina.DISPONIVEL)
        self.assertEqual(HistoricoUso.objects.count(), 0)

    def test_can_use_when_enough_credits(self):
        inquilino = Inquilino.objects.create(apartamento='4', password=None, creditos=3)
        self._login_as(inquilino)
        # mock the network call to the Tasmota device so the test does not depend on external network
        from unittest.mock import patch
        with patch('laundry.services.TasmotaService.ligar_com_timer', return_value=True):
            resp = self.client.get(f'/usar/{self.maquina.id}/', follow=True)
        # should succeed and show success page with new balance
        self.assertContains(resp, 'Seu novo saldo')
        # verify history created and credit deducted
        i = Inquilino.objects.get(pk=inquilino.pk)
        self.assertEqual(i.creditos, 3 - self.maquina.custo_creditos)
        self.assertEqual(HistoricoUso.objects.count(), 1)