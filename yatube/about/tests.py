from django.test import TestCase
from http import HTTPStatus
from django.urls import reverse


class StaticPagesURLTests(TestCase):
    def test_available_pages_for_anonymous(self):
        """Проверка доступности urls приложения about."""
        pages = {
            'author': '/about/author/',
            'tech': '/about/tech/'
        }
        for field, page in pages.items():
            with self.subTest(field=field):
                response = self.client.get(page)
                self.assertEqual(response.status_code, HTTPStatus.OK.value)

    def test_about_url_uses_correct_template(self):
        """Проверка доступности шаблонов приложения about."""
        pages = {
            '/about/author/': 'about/author.html',
            '/about/tech/': 'about/tech.html'
        }
        for address, page in pages.items():
            with self.subTest(address=address):
                response = self.client.get(address)
                self.assertTemplateUsed(response, page)

    def test_about_page_accessible_by_name(self):
        """URL, генерируемый при помощи именам, доступен."""
        names = ['about:author', 'about:tech']
        for name in names:
            with self.subTest(name=name):
                response = self.client.get(reverse(name))
                self.assertEqual(response.status_code, HTTPStatus.OK.value)

    def test_about_page_uses_correct_template(self):
        """При запросе к about:author и about:tech
        применяется шаблон about/author.html и about/tech.html."""
        names = {
            'about:author': 'about/author.html',
            'about:tech': 'about/tech.html',
        }
        for name, template in names.items():
            with self.subTest(name=name):
                response = self.client.get(reverse(name))
                self.assertTemplateUsed(response, template)
