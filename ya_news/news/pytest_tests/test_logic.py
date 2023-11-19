from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import Client

import pytest
from http import HTTPStatus

from news.models import Comment, News
from news.forms import BAD_WORDS, WARNING


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


User = get_user_model()


@pytest.mark.django_db
def test_user_can_create_comment(test_news, test_user, auth_client, form_data):
    url = reverse('news:detail', args=(test_news.id,))
    response = auth_client.post(url, data=form_data)
    assert response.status_code == HTTPStatus.FOUND
    assert response.url.endswith('#comments')
    assert Comment.objects.count() == 1
    comment = Comment.objects.get()
    assert comment.text == form_data['text']
    assert comment.news == test_news
    assert comment.author == test_user


@pytest.mark.django_db
def test_user_cant_use_bad_words(test_news, test_user, auth_client):
    url = reverse('news:detail', args=(test_news.id,))
    bad_words_data = {'text': f'Какой-то текст, {BAD_WORDS[0]}, еще текст'}
    response = auth_client.post(url, data=bad_words_data)
    assert response.status_code == HTTPStatus.OK
    assert 'form' in response.context
    form_errors = response.context['form'].errors
    assert 'text' in form_errors
    assert form_errors['text'] == [WARNING]
    assert Comment.objects.count() == 0


@pytest.mark.django_db
def test_author_can_delete_comment(author, author_client,
                                   comment, delete_url, url_to_comments):
    assert Comment.objects.count() == 1
    response = author_client.delete(delete_url)
    assert response.status_code == HTTPStatus.FOUND
    assert response.url.endswith(url_to_comments)
    assert Comment.objects.count() == 0


@pytest.mark.django_db
def test_user_cant_delete_comment_of_another_user(reader_client,
                                                  comment,
                                                  delete_url):
    response = reader_client.delete(delete_url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.count() == 1
