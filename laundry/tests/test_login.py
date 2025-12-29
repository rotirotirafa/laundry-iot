from django.test import TestCase, Client
from laundry.models import Inquilino
from django.contrib.auth.hashers import identify_hasher


class LoginMigrationTest(TestCase):
    def setUp(self):
        # create an inquilino with plaintext password (simulating admin manual set)
        self.inquilino = Inquilino.objects.create(apartamento='1', password='123456', creditos=10)
        self.client = Client()

    def test_plaintext_password_is_accepted_and_hashed_on_login(self):
        resp = self.client.post('/login/', {'apartamento': '1', 'password': '123456'}, follow=True)
        self.assertEqual(resp.status_code, 200)
        # reload object
        i = Inquilino.objects.get(pk=self.inquilino.pk)
        # password should no longer be the raw '123456'
        self.assertNotEqual(i.password, '123456')
        # it should be recognized by identify_hasher
        identify_hasher(i.password)