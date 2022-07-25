import shutil
import tempfile

from django.contrib.auth import get_user_model
from posts.forms import PostForm
from posts.models import Post
from django.conf import settings
from django.test import Client, TestCase, override_settings
from django.urls import reverse

User = get_user_model()

# Создаем временную папку для медиа-файлов;
# на момент теста медиа папка будет переопределена
TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


# Для сохранения media-файлов в тестах будет использоваться
# временная папка TEMP_MEDIA_ROOT, а потом мы ее удалим
@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.post = Post.objects.create(
            author=cls.user,
            text='Текст'
        )
        # Создаем форму, если нужна проверка атрибутов
        cls.form = PostForm()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        # Создаем неавторизованный клиент
        self.guest_client = Client()
        # Создаем пользователя
        self.user = User.objects.create_user(username='HasNoName')
        # Создаем второй клиент
        self.authorized_client = Client()
        # Авторизуем пользователя
        self.authorized_client.force_login(self.user)
        self.author = self.authorized_client.force_login(self.post.author)

    def test_create_post(self):
        """Валидная форма создает запись в Post."""
        # Подсчитаем количество записей в Post
        post_count = Post.objects.count()
        form_data = {
            'text': 'Тестовый текст'
        }
        # Отправляем POST-запрос
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        # Проверяем, сработал ли редирект
        self.assertRedirects(
            response, reverse('posts:profile', kwargs={'username': 'auth'}))
        # Проверяем, увеличилось ли число постов
        self.assertEqual(Post.objects.count(), post_count + 1)
        # Проверяем, что создалась запись с заданным слагом
        self.assertTrue(
            Post.objects.filter(
                text='Тестовый текст'
            ).exists()
        )

    def test_edit_post(self):
        """При отправке валидной формы со страницы редактирования поста
        происходит изменение поста с post_id в базе данных."""
        form_data = {
            'text': 'Измененный тестовый текст'
        }

        response = self.authorized_client.post(
            reverse('posts:post_edit', kwargs={'post_id': '1'}),
            data=form_data
        )
        self.assertRedirects(
            response, reverse('posts:post_detail', kwargs={'post_id': 1}))
        self.assertTrue(
            Post.objects.filter(
                text='Измененный тестовый текст'
            ).exists()
        )

    def test_no_create_post_anonymous(self):
        """Незарегистрированный пользователь не может создать пост"""
        # Подсчитаем количество записей в Post
        post_count = Post.objects.count()
        form_data = {
            'text': 'Пост анонимного пользователя'
        }
        # Отправляем POST-запрос
        self.guest_client.post(reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertEqual(Post.objects.count(), post_count)
        # Проверяем, что запись не создалась
        self.assertFalse(
            Post.objects.filter(
                text='Пост анонимного пользователя'
            ).exists()
        )
