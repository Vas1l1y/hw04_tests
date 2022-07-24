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

    def test_create_url_available_for_authorized(self):
        """Адрес create доступен авторизованным пользователям"""
        response = self.authorized_client.get('/create/')
        self.assertEqual(response.status_code, 200)

    def test_create_url_redirect_anonymous(self):
        """Страница create перенаправляет анонимного пользователя"""
        response = self.guest_client.get('/create/')
        self.assertEqual(response.status_code, 302)

    def test_edit_url_redirect_anonymous(self):
        """Страница edit перенаправляет анонимного пользователя"""
        response = self.guest_client.get('/posts/1/edit/')
        self.assertEqual(response.status_code, 302)

    def test_edit_url_redirect_authorized_non_author(self):
        """Страница edit перенаправляет авторизованного
        пользователя, не является автором"""
        response = self.authorized_client.get('/posts/1/edit/')
        self.assertEqual(response.status_code, 302)

    def test_edit_url_available_for_author(self):
        """Адрес edit доступен автору"""
        # Делаем авторизованного пользователя автором поста
        self.authorized_client.force_login(self.post.author)
        response = self.authorized_client.get('/posts/1/edit/')
        self.assertEqual(response.status_code, 200)
