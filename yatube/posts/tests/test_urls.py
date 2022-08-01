from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.core.cache import cache

from posts.models import Post, Group

from http import HTTPStatus

User = get_user_model()


class PostURLTest(TestCase):
    """Создание записей в БД для тестов URLS"""
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.author = User.objects.create_user(username='author')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            id=0,
            author=cls.author,
            text='Тестовый пост',
        )

    def setUp(self):
        """Создание авторизованных и не авторизованного клиентов."""
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(PostURLTest.user)
        self.authorized_author = Client()
        self.authorized_author.force_login(PostURLTest.author)
        cache.clear()

    def test_urls_exists_at_desired_location_for_anonymous(self):
        """Страницы: index, group_list, profile, post_detail
        доступны не авторизованному пользователю.
        """
        templates_url_names = {
            'posts/index.html': '/',
            'posts/group_list.html': f'/group/{ PostURLTest.group.slug }/',
            'posts/profile.html': (f'/profile/'
                                   f'{ PostURLTest.post.author.username }/'),
            'posts/post_detail.html': f'/posts/{ PostURLTest.post.id }/',
        }
        for url in templates_url_names.values():
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_urls_exists_at_desired_location_for_authorized(self):
        """Страницы: index, group_list, profile, post_detail,
        create_post доступны авторизованному пользователю.
        """
        templates_url_names = {
            'posts/index.html': '/',
            'posts/group_list.html': f'/group/{ PostURLTest.group.slug }/',
            'posts/profile.html': (f'/profile/'
                                   f'{ PostURLTest.post.author.username }/'),
            'posts/post_detail.html': f'/posts/{ PostURLTest.post.id }/',
            'posts/create_post.html': '/create/',
        }
        for url in templates_url_names.values():
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_unexisting_page_exists_at_desired_location_for_anonymous(self):
        """
        Страница unexisting_page недоступна не авторизованному пользователю.
        """
        response = self.guest_client.get('/unexisting_page/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_unexisting_page_exists_at_desired_location_for_authorized(self):
        """Страница unexisting_page недоступна любому пользователю."""
        response = self.authorized_client.get('/unexisting_page/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_post_edit_exists_at_author_post(self):
        """Страница post_edit доступна автору поста."""
        if self.authorized_client == self.author:
            response = self.client.get(f'/posts/{ PostURLTest.post.id }/edit/')
            self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_post_edit_url_redirect_not_author_on_post_detail(self):
        """Страница post_edit перенаправит не автора поста
        на страницу post_detail.
        """
        if self.authorized_client != self.author:
            response = self.authorized_client.get(
                f'/posts/{ PostURLTest.post.id }/edit/', follow=True)
            self.assertRedirects(
                response, (f'/posts/{ PostURLTest.post.id }/'))

    def test_create_url_redirect_anonymous_on_auth_login(self):
        """Страница create перенаправит анонимного пользователя
        на страницу логина.
        """
        response = self.guest_client.get('/create/', follow=True)
        self.assertRedirects(
            response, ('/auth/login/?next=/create/'))

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_url_names = {
            '/': 'posts/index.html',
            f'/group/{ PostURLTest.group.slug }/': 'posts/group_list.html',
            (f'/profile/'
             f'{ PostURLTest.post.author.username }/'): 'posts/profile.html',
            f'/posts/{ PostURLTest.post.id }/': 'posts/post_detail.html',
            f'/posts/{ PostURLTest.post.id }/edit/': 'posts/create_post.html',
            '/create/': 'posts/create_post.html',
            '/unexisting_page/': 'core/404.html'
        }
        for url, template in templates_url_names.items():
            with self.subTest(url=url):
                response = self.authorized_author.get(url)
                self.assertTemplateUsed(response, template)
