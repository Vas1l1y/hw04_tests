from django.contrib.auth import get_user_model

from django.test import TestCase, Client
from ..models import Post, Group

User = get_user_model


class StaticURLTests(TestCase):
    def test_homepage(self):
        # Создаем экземпляр клиента
        guest_client = Client()
        # Делаем запрос к главной странице и проверяем статус
        response = guest_client.get('/')
        # Утверждаем, что для прохождения теста код должен быть равен 200
        self.assertEqual(response.status_code, 200)


class PostsURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тестовый слаг',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост в котором больше 15 символов',
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
        # Создадим третий клиент
        self.author_client = Client()
        # Авторизуем третий клиент
        self.author_client.force_login(self.user)
        # Сделаем автором поста
        self.author_client(self.author)


def test_urls_uses_correct_template(self):
    """URL-адрес использует соответствующий шаблон."""
    templates_url_names = {
        '': 'posts/index.html',
        'group/<slug>/': 'posts/group_list.html',
        'profile/<str:username>/': 'posts/profile.html',
        'posts/<int:post_id>/edit/': 'posts/create_post.html',
        'posts/<int:post_id>/': 'posts/post_detail.html',
        'create/': 'posts/create_post.html',
        'crush/': 'posts/crush.html'
    }
    for address, template in templates_url_names.items():
        with self.subTest(address=address):
            response = self.authorized_client.get(address)
            self.assertTemplateUsed(response, template)

    for address, template in templates_url_names.items():
        with self.subTest(address=address):
            response = self.author_client.get(address)
            self.assertTemplateUsed(response, template)
