from django.contrib.auth import get_user_model

from django.test import TestCase, Client
from ..models import Post, Group

User = get_user_model()


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Заголовок',
            slug='test',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Текст',
            group=cls.group
        )

    def setUp(self):
        # Создаем неавторизованный клиент
        self.guest_client = Client()
        # Создаем пользователя
        self.user = User.objects.create_user(username='HasNoName')
        # Создаем второй клиент
        self.authorized_client = Client()
        # Авторизуем пользователя
        self.authorized_client.force_login(self.user)
        self.author_client = Client()
        self.author_client.force_login(self.user)
        self.author_client.force_login(self.post.author)

    def test_url_available_for_everyone(self):
        """Адреса доступные всем пользователям"""
        templates_url_names = {
            '': 200,
            '/group/test/': 200,
            '/profile/HasNoName/': 200,
            '/posts/1/': 200,
            '/unexisting_page/': 404}
        for address, code in templates_url_names.items():
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertEqual(response.status_code, code)

    def test_url_available_and_redirect(self):
        """Проверка доступности адресов и перенаправления"""
        # Натан, я попробую реализовать твои рекомендации
        templates_url_guest_client = {
            '/create/': 302,
            '/posts/1/edit/': 302}
        for address, code in templates_url_guest_client.items():
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertEqual(response.status_code, code)

        templates_url_authorized_client = {
            '/create/': 200,
            '/posts/1/edit/': 302}
        for address, code in templates_url_authorized_client.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertEqual(response.status_code, code)

        templates_url_author = {
            '/posts/1/edit/': 200}
        for address, code in templates_url_author.items():
            with self.subTest(address=address):
                response = self.author_client.get(address)
                self.assertEqual(response.status_code, code)
