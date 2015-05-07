# coding: utf-8
import json
from django.core import urlresolvers
from django.test import TestCase
from django.contrib.auth.models import User

class RestAuthLoginTestCase(TestCase):
    def setUp(self):
        self.url = urlresolvers.reverse('djutils.views.rest_auth.login')

    def test_require_post(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 405)

        response = self.client.post(self.url)
        self.assertNotEqual(response.status_code, 405)

    def test_require_params(self):
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 403)

        response_data = json.loads(str(response.content, encoding='utf-8'))
        self.assertIn("errors", response_data)
        self.assertIn("Username: This field is required.", response_data['errors'])
        self.assertIn("Password: This field is required.", response_data['errors'])

    def test_login_without_user_in_db(self):
        p = {'username': 'tester', 'password': '123'}

        response = self.client.post(self.url, p)
        self.assertEqual(response.status_code, 403)

        response_data = json.loads(str(response.content, encoding='utf-8'))
        self.assertIn("errors", response_data)
        self.assertEqual(
            len(response_data['errors']),
            1
        )
        self.assertTrue(
            response_data['errors'][0].startswith('Please enter a correct username and password')
        )

    def test_login_with_user_in_db(self):
        p = {'username': 'tester', 'password': '123'}
        User.objects.create_user(p['username'], password=p['password'])
        response = self.client.post(self.url, p)
        self.assertEqual(response.status_code, 200)



class RestAuthLogoutTestCase(TestCase):
    def setUp(self):
        self.url = urlresolvers.reverse('djutils.views.rest_auth.logout')

    def test_require_post(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 405)

    def test_logout(self):
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 200)


class RestAuthCurrentUserTestCase(TestCase):
    def setUp(self):
        self.url = urlresolvers.reverse('djutils.views.rest_auth.get_current_user')

    def test_not_authenticated(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

        response_data = json.loads(str(response.content, encoding='utf-8'))
        self.assertFalse(response_data['is_authenticated'])

    def test_authenticated(self):
        # login
        p = {'username': 'tester', 'password': '123'}
        User.objects.create_user(p['username'], password=p['password'])
        login_url = urlresolvers.reverse('djutils.views.rest_auth.login')
        self.client.post(login_url, p)

        # get info
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

        response_data = json.loads(str(response.content, encoding='utf-8'))
        self.assertTrue(response_data['is_authenticated'])
        self.assertEqual(response_data['username'], p['username'])