from http import HTTPStatus

from django.test import TestCase, Client

from posts.models import Post, Group, User


class PostsURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create(username='TestAuthor')
        cls.user = User.objects.create(username='TestUser')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.author,
            text='Тестовый пост',
        )

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.authorized_author = Client()
        self.authorized_author.force_login(self.author)

    def test_available_pages_for_anonymous(self):
        """Страницы доступны любому пользователю."""
        pages = {
            'index': '/',
            'group': f'/group/{self.group.slug}/',
            'post_detail': f'/posts/{self.post.pk}/',
            'profile': f'/profile/{self.author.username}/',
        }
        for page, url in pages.items():
            with self.subTest(page=page):
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_redirect_anonymous(self):
        """Редирект анонимного пользователя"""
        pages = {
            f'/auth/login/?next=/posts/{self.post.pk}/edit/':
                f'/posts/{self.post.pk}/edit/',
            '/auth/login/?next=/create/': '/create/',
        }
        for page, url in pages.items():
            with self.subTest(page=page):
                response = self.client.get(url)
                self.assertRedirects(response, page)

    def test_url_create_post_available_auth_client(self):
        """Страница создания поста доступна авторизованному пользователю."""
        response = self.authorized_client.get('/create/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_url_edit_post_available_author(self):
        """Страница редактирования поста доступна автору (/posts/1/edit/)."""
        response = self.authorized_author.get(f'/posts/{self.post.pk}/edit/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_redirect_not_author(self):
        """Редирект со страницы edit_post не автора поста"""
        redirect_page = f'/posts/{self.post.pk}/'
        try_edit_page = f'/posts/{self.post.pk}/edit/'
        response = self.authorized_client.get(try_edit_page)
        self.assertRedirects(response, redirect_page)

    def test_unexisting_page(self):
        """Тест несуществующей страницы, должно вернуть 404."""
        response = self.authorized_author.get('/unexisting_page/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_url_names = {
            '/': 'posts/index.html',
            f'/group/{self.group.slug}/': 'posts/group_list.html',
            '/profile/TestAuthor/': 'posts/profile.html',
            f'/posts/{self.post.pk}/': 'posts/post_detail.html',
            f'/posts/{self.post.pk}/edit/': 'posts/create_post.html',
            '/create/': 'posts/create_post.html',
        }
        for address, template in templates_url_names.items():
            with self.subTest(address=address):
                response = self.authorized_author.get(address)
                self.assertTemplateUsed(response, template)
