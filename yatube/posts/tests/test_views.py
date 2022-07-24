from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from django import forms

from posts.models import Post, Group

User = get_user_model()


class PostsPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Заголовок',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Текст'
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

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_pages_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse('posts:group_list',
                    kwargs={'slug': 'test-slug'}): 'posts/group_list.html',
            reverse('posts:profile',
                    kwargs={'username': 'HasNoName'}): 'posts/profile.html',
            reverse('posts:post_detail',
                    kwargs={'post_id': 1}): 'posts/post_detail.html',
            reverse('posts:post_create'): 'posts/create_post.html'}
        for reverse_name, template in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_urls_post_edit_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        self.authorized_client.force_login(self.post.author)
        templates_pages_names = {
                                reverse('posts:post_edit',
            kwargs={'post_id': 1}): 'posts/create_post.html'}
        for reverse_name, template in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_post_index_show_correct_context(self):
        """Шаблон index  сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:index'))
        # Взяли первый элемент из списка и проверили, что его содержание
        # совпадает с ожидаемым
        first_object = response.context['page_obj'][0]
        post_text_0 = first_object.text
        self.assertEqual(post_text_0, 'Текст')

    def test_group_list_show_correct_context(self):
        """Шаблон group_list  сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:group_list', kwargs={'slug': 'test-slug'}))
        # Взяли первый элемент из списка и проверили, что его содержание
        # совпадает с ожидаемым
        self.assertEqual(
            response.context.get('group').title, 'Заголовок')
        self.assertEqual(
            response.context.get('group').description, 'Тестовое описание')
        self.assertEqual(
            response.context.get('group').slug, 'test-slug')

    def test_profile_show_correct_context(self):
        """Шаблон profile  сформирован с правильным контекстом."""
        self.authorized_client.force_login(self.post.author)
        # Взяли первый элемент из списка и проверили, что его содержание
        # совпадает с ожидаемым
        response = self.authorized_client.get(
            reverse('posts:profile', kwargs={'username': 'HasNoName'}))
        post_detail_obj = response.context['author'].username
        self.assertEqual(post_detail_obj, 'HasNoName')

    def test_post_detail_show_correct_context(self):
        """Шаблон post_detail  сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:post_detail', kwargs={'post_id': 1}))
        post_detail_obj = response.context['posts'].pk
        self.assertEqual(post_detail_obj, 1)

    # Проверка словаря контекста создания поста (в нём передаётся форма)
    def test_create_post_show_correct_context(self):
        """Шаблон create_post сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:post_create'))
        # Словарь ожидаемых типов полей формы:
        # указываем, объектами какого класса должны быть поля формы
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                # Проверяет, что поле формы является экземпляром
                # указанного класса
                self.assertIsInstance(form_field, expected)

    # Проверка словаря контекста создания поста (в нём передаётся форма)
    def test_post_edit_show_correct_context(self):
        """Шаблон post_edit сформирован с правильным контекстом."""
        self.authorized_client.force_login(self.post.author)
        response = self.authorized_client.get(
            reverse('posts:post_edit', kwargs={'post_id': 1}))
        # post_edit = response.context['posts'].pk
        # self.assertEqual(post_edit, 1)
        # Словарь ожидаемых типов полей формы:
        # указываем, объектами какого класса должны быть поля формы
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }

        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                # Проверяет, что поле формы является экземпляром
                # указанного класса
                self.assertIsInstance(form_field, expected)


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth1')
        cls.group = Group.objects.create(
            title='Заголовок',
            slug='test-slug1',
            description='Тестовое описание'
        )
        cls.post_1 = Post.objects.create(
            author=cls.user,
            text='Текст',
            group=cls.group
        )
        cls.post_2 = Post.objects.create(
            author=cls.user,
            text='Текст',
            group=cls.group
        )
        cls.post_3 = Post.objects.create(
            author=cls.user,
            text='Текст',
            group=cls.group
        )
        cls.post_4 = Post.objects.create(
            author=cls.user,
            text='Текст',
            group=cls.group
        )
        cls.post_5 = Post.objects.create(
            author=cls.user,
            text='Текст',
            group=cls.group
        )
        cls.post_6 = Post.objects.create(
            author=cls.user,
            text='Текст',
            group=cls.group
        )
        cls.post_7 = Post.objects.create(
            author=cls.user,
            text='Текст',
            group=cls.group
        )
        cls.post_8 = Post.objects.create(
            author=cls.user,
            text='Текст',
            group=cls.group
        )
        cls.post_9 = Post.objects.create(
            author=cls.user,
            text='Текст',
            group=cls.group
        )
        cls.post_10 = Post.objects.create(
            author=cls.user,
            text='Текст',
            group=cls.group
        )
        cls.post_11 = Post.objects.create(
            author=cls.user,
            text='Текст',
            group=cls.group
        )
        cls.post_12 = Post.objects.create(
            author=cls.user,
            text='Текст',
            group=cls.group
        )
        cls.post_13 = Post.objects.create(
            author=cls.user,
            text='Текст',
            group=cls.group
        )

    def setUp(self):
        # Создаем неавторизованный клиент
        self.guest_client = Client()
        # Создаем пользователя
        self.user = User.objects.create_user(username='Vasya')
        # Создаем второй клиент
        self.authorized_client = Client()
        # Авторизуем пользователя
        self.authorized_client.force_login(self.user)

    def test_first_page_contains_ten_records_index(self):
        """Проверяем паджинатор первой страницы index
        Проверка: количество постов на первой странице равно 10"""
        response = self.client.get(reverse('posts:index'))
        self.assertEqual(len(response.context['page_obj']), 10)

    def test_second_page_contains_three_records_index(self):
        """Проверяем паджинатор второй страницы index
        Проверка: на второй странице должно быть 3 поста"""
        response = self.client.get(reverse('posts:index') + '?page=2')
        self.assertEqual(len(response.context['page_obj']), 3)

    def test_first_page_contains_ten_records_group_list(self):
        """Проверяем паджинатор первой страницы group_list
        Проверка: количество постов на первой странице равно 10"""
        response = self.client.get(
            reverse('posts:group_list', kwargs={'slug': 'test-slug1'}))
        self.assertEqual(len(response.context['page_obj']), 10)

    def test_second_page_contains_three_records_group_list(self):
        """Проверяем паджинатор второй страницы group_list
        Проверка: на второй странице должно быть 3 поста"""
        response = self.client.get(reverse('posts:group_list',
                                   kwargs={'slug': 'test-slug1'})
                                   + '?page=2')
        self.assertEqual(len(response.context['page_obj']), 3)

    def test_first_page_contains_ten_records_profile(self):
        """Проверяем паджинатор страницы profile
        Проверка: количество постов на первой странице равно 10"""
        response = self.authorized_client.get(
            reverse('posts:profile', kwargs={'username': 'auth1'}))
        self.assertEqual(len(response.context['page_obj']), 10)

    def test_second_page_contains_three_records_profile(self):
        """Проверяем паджинатор второй страницы profile
        Проверка: на второй странице должно быть 3 поста"""
        response = self.authorized_client.get(
            reverse('posts:profile', kwargs={'username': 'auth1'}) + '?page=2')
        self.assertEqual(len(response.context['page_obj']), 3)


class PostViewsTest_create_post_in(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth2')
        cls.group = Group.objects.create(
            title='Заголовок',
            slug='test-slug2',
            description='Тестовое описание',
        )
        cls.group_2 = Group.objects.create(
            title='Заголовок',
            slug='test-slug3',
            description='Тестовое описание',
        )
        cls.post_14 = Post.objects.create(
            author=cls.user,
            text='Текст',
            group=cls.group,
        )
        cls.post_54 = Post.objects.create(
            author=cls.user,
            text='Текст',
            group=cls.group_2,
        )

    def setUp(self):
        # Создаем неавторизованный клиент
        self.guest_client = Client()
        # Создаем пользователя
        self.user = User.objects.create_user(username='Vasya')
        # Создаем второй клиент
        self.authorized_client = Client()
        # Авторизуем пользователя
        self.authorized_client.force_login(self.user)

    def test_create_post_in_index(self):
        """Проверяем, что созаднный пост, есть на index"""
        response = self.authorized_client.get(reverse('posts:index'))
        # Взяли первый элемент из списка и проверили, что его содержание
        # совпадает с ожидаемым
        first_object = response.context['page_obj'][0]
        self.assertEqual(self.post_14, first_object)

    def test_create_post_in_group_list(self):
        """Проверяем, что созаднный пост, есть на group_list"""
        response = self.authorized_client.get(
            reverse('posts:group_list', kwargs={'slug': 'test-slug2'}))
        # Взяли первый элемент из списка и проверили, что его содержание
        # совпадает с ожидаемым
        first_object = response.context['page_obj'][0]
        self.assertEqual(self.post_14, first_object)

    def test_create_post_not_in_group_list(self):
        """Проверяем, что созаднный пост, отсутствует в группе"""
        response = self.authorized_client.get(
            reverse('posts:group_list', kwargs={'slug': 'test-slug3'}))
        # Взяли первый элемент из списка и проверили, что его содержание
        # совпадает с ожидаемым
        first_object = response.context['page_obj'][0]
        self.assertNotEqual(self.post_14, first_object)

    def test_create_post_in_profile(self):
        """Проверяем, что созаднный пост, есть на profile"""
        self.authorized_client.force_login(self.post_14.author)
        response = self.authorized_client.get(
            reverse('posts:profile', kwargs={'username': 'auth2'}))
        # Взяли первый элемент из списка и проверили, что его содержание
        # совпадает с ожидаемым
        post_detail_obj = response.context['page_obj'][0]
        self.assertEqual(self.post_14, post_detail_obj)
