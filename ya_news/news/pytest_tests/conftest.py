from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import Client

import pytest

from news.models import Comment, News


User = get_user_model()


@pytest.fixture
def test_news():
    return News.objects.create(title='Заголовок', text='Текст')


@pytest.fixture
def test_user():
    return User.objects.create(username='Мимо Крокодил')


@pytest.fixture
def auth_client(test_user):
    client = Client()
    client.force_login(test_user)
    return client


@pytest.fixture
def form_data():
    return {'text': 'Текст комментария'}


@pytest.fixture
def author():
    return User.objects.create(username='Автор комментария')


@pytest.fixture
def author_client(author):
    client = Client()
    client.force_login(author)
    return client


@pytest.fixture
def reader():
    return User.objects.create(username='Читатель')


@pytest.fixture
def reader_client(reader):
    client = Client()
    client.force_login(reader)
    return client


@pytest.fixture
def comment(test_news, author):
    return Comment.objects.create(news=test_news,
                                  author=author, text='Текст комментария')


@pytest.fixture
def edit_url(comment):
    return reverse('news:edit', args=(comment.id,))


@pytest.fixture
def delete_url(comment):
    return reverse('news:delete', args=(comment.id,))


@pytest.fixture
def updated_form_data():
    return {'text': 'Обновлённый комментарий'}


@pytest.fixture
def url_to_comments(test_news):
    return reverse('news:detail', args=(test_news.id,)) + '#comments'
