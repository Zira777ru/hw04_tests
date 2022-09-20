from django.test import Client, TestCase
from django.urls import reverse
from django import forms

from posts.models import Post, Group, User
from posts.constants import POST_PER_PAGE, POSTS_PAG_TEST, POSTS_SECOND_PAGE


class PostPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.authorized_author = Client()
        cls.author = User.objects.create(username='TestAuthor')
        cls.authorized_author.force_login(cls.author)
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.author,
            text='Тестовый пост',
            group=cls.group,
        )
        cls.form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_pages_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse('posts:post_create'): 'posts/create_post.html',
            reverse('posts:post_edit', kwargs={
                'post_id': self.post.id}): 'posts/create_post.html',
            reverse('posts:post_detail', kwargs={
                'post_id': self.post.id}): 'posts/post_detail.html',
            reverse('posts:profile', kwargs={
                'username': self.post.author}): 'posts/profile.html',
            reverse('posts:group_list', kwargs={
                'slug': self.group.slug}): 'posts/group_list.html',
        }
        for reverse_name, template in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_author.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_index_page_show_correct_context(self):
        response = self.authorized_author.get(
            reverse('posts:index'))
        context_object = response.context['page_obj'].object_list
        query = Post.objects.all()
        self.assertQuerysetEqual(context_object, query, transform=lambda x: x)

    def test_group_list_page_show_correct_context(self):
        response = self.authorized_author.get(
            reverse('posts:group_list', kwargs={'slug': self.group.slug}))
        context_object = response.context['page_obj'].object_list
        query = Post.objects.filter(group=self.group)
        context_group = response.context['group']
        self.assertQuerysetEqual(context_object, query, transform=lambda x: x)
        self.assertEqual(context_group, self.group)

    def test_profile_page_show_correct_context(self):
        response = self.authorized_author.get(
            reverse('posts:profile', kwargs={'username': self.post.author}))
        context_object = response.context['page_obj'].object_list
        query = Post.objects.filter(author=self.author)
        context_profile = response.context['profile']
        self.assertQuerysetEqual(context_object, query, transform=lambda x: x)
        self.assertEqual(context_profile, self.author)

    def test_post_detail_page_show_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        response = self.authorized_author.get(
            reverse('posts:post_detail', kwargs={'post_id': self.post.id}))
        context_object = response.context['page_obj']
        post = Post.objects.get(pk=self.post.id)
        self.assertEqual(context_object, post)

    def test_create_post_show_correct_context(self):
        """Шаблон create_post сформирован с правильным контекстом."""
        response = self.authorized_author.get(reverse('posts:post_create'))
        for field, expected in self.form_fields.items():
            with self.subTest(field=field):
                form_field = response.context['form'].fields[field]
                self.assertIsInstance(form_field, expected)

    def test_post_edit_show_correct_context(self):
        """Шаблон post_edit сформирован с правильным контекстом."""
        response = self.authorized_author.get(
            reverse('posts:post_edit', kwargs={'post_id': self.post.id}))
        post = Post.objects.get(pk=self.post.id)
        context_form = response.context['form'].instance
        context_author = response.context.get('user')
        for field, expected in self.form_fields.items():
            with self.subTest(field=field):
                form_field = response.context['form'].fields[field]
                self.assertIsInstance(form_field, expected)
        self.assertTrue(response.context['is_edit'])
        self.assertEqual(context_form, post)
        self.assertEqual(context_author, post.author)

    def test_index_group_profile_post(self):
        """Новый пост появляется первым в шаблонах
        index, group_list, profile."""
        new_post = Post.objects.create(
            author=self.author,
            text='Первый пост',
            group=self.group,)
        templates = (
            reverse('posts:index'),
            reverse('posts:group_list',
                    kwargs={'slug': self.group.slug}),
            reverse('posts:profile', kwargs={
                'username': self.post.author}),
        )
        for template in templates:
            with self.subTest(template=template):
                response = self.authorized_author.get(template)
                context_object = response.context['page_obj'].object_list
                self.assertEqual(context_object[0], new_post)

    def test_post_instance_page(self):
        """Проверяем, что пост не попал в группу которой не предназначен"""
        other_group = Group.objects.create(
            title='Другая группа',
            slug='other-slug',
            description='Другое описание',
        )
        self.assertNotEqual(other_group.id, self.post.group.id)


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username='TestUser')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        generate_posts = [Post(
            author=cls.user,
            text='Тестовый пост',
            group=cls.group,) for x in range(POSTS_PAG_TEST)]
        cls.posts = Post.objects.bulk_create(generate_posts)
        cls.pages = [
            reverse('posts:index'),
            reverse('posts:group_list', kwargs={'slug': cls.group.slug}),
            reverse('posts:profile', kwargs={'username': cls.user.username}),
        ]

    def test_first_page_contains_ten_records(self):
        """Пагинатор выводит 10 постов на первую страницу."""
        for page in self.pages:
            with self.subTest(page=page):
                response = self.client.get(page)
                self.assertEqual(len(response.context['page_obj']),
                                 POST_PER_PAGE)

    def test_second_page_contains_three_records(self):
        """Пагинатор выводит 3 поста на вторую страницу."""
        for page in self.pages:
            with self.subTest(page=page):
                response = self.client.get(page + '?page=2')
                self.assertEqual(len(response.context['page_obj']),
                                 POSTS_SECOND_PAGE)
