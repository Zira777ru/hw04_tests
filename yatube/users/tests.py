from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from http import HTTPStatus
from django.urls import reverse

from users.forms import CreatingForm

User = get_user_model()


class UsersURLTests(TestCase):
    def setUp(self):
        self.user = User.objects.create(username='TestUser')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_available_pages_for_anonymous(self):
        """Проверка urls приложения users для анонимного юзера."""
        pages = {
            'signup': '/auth/signup/',
            'logout': '/auth/logout/',
            'login': '/auth/login/',
            'password_reset': '/auth/password_reset/',
            'password_reset_done': '/auth/password_reset/done/',
            'password_reset_complete': '/auth/reset/done/',
        }
        for field, page in pages.items():
            with self.subTest(field=field):
                response = self.client.get(page)
                self.assertEqual(response.status_code, HTTPStatus.OK.value)

    def test_available_pages_for_auth_user(self):
        """Проверка urls приложения users для авторизованного юзера."""
        pages = {
            'password_change/': '/auth/password_change/',
            'password_change/done/': '/auth/password_change/done/',
        }
        for field, page in pages.items():
            with self.subTest(field=field):
                response = self.authorized_client.get(page)
                self.assertEqual(response.status_code, HTTPStatus.OK.value)

    def test_redirect_anonymous(self):
        """Редирект анонимного пользователя"""
        pages = {
            '/auth/password_change/':
                '/auth/login/?next=/auth/password_change/',
            '/auth/password_change/done/':
                '/auth/login/?next=/auth/password_change/done/',
        }
        for url, result_page in pages.items():
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertRedirects(response, result_page)


class UsersCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.client = Client()
        cls.form = CreatingForm()

    def test_create_user(self):
        """Валидная форма создает запись в User."""
        user_count = User.objects.count()
        form_data = {
            'first_name': 'TestName',
            'last_name': 'TestLustName',
            'username': 'testuser',
            'email': 'emalfortest@yatube.com',
            'password1': 'TestPassword837101@1',
            'password2': 'TestPassword837101@1',
        }
        UsersCreateFormTests.client.post(
            reverse('users:signup'),
            data=form_data,
            follow=True
        )
        self.assertEqual(User.objects.count(), user_count + 1)
