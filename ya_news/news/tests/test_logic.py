import pytest
from http import HTTPStatus
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.test import Client
from news.forms import BAD_WORDS, WARNING
from news.models import Comment, News

User = get_user_model()

@pytest.fixture
def setup_test_data():
    news = News.objects.create(title='Заголовок', text='Текст')
    user = User.objects.create(username='Мимо Крокодил')
    auth_client = Client()
    auth_client.force_login(user)
    form_data = {'text': 'Текст комментария'}
    return news, user, auth_client, form_data

@pytest.mark.django_db
def test_anonymous_user_cant_create_comment(client, setup_test_data):
    news, _, _, form_data = setup_test_data
    url = reverse('news:detail', args=(news.id,))
    client.post(url, data=form_data)
    comments_count = Comment.objects.count()
    assert comments_count == 0

@pytest.mark.django_db
def test_user_can_create_comment(setup_test_data):
    news, user, auth_client, form_data = setup_test_data
    url = reverse('news:detail', args=(news.id,))
    response = auth_client.post(url, data=form_data)
    assert response.status_code == HTTPStatus.FOUND
    assert response.url.endswith('#comments')
    comments_count = Comment.objects.count()
    assert comments_count == 1
    comment = Comment.objects.get()
    assert comment.text == form_data['text']
    assert comment.news == news
    assert comment.author == user

@pytest.mark.django_db
def test_user_cant_use_bad_words(setup_test_data):
    news, user, auth_client, _ = setup_test_data
    url = reverse('news:detail', args=(news.id,))
    bad_words_data = {'text': f'Какой-то текст, {BAD_WORDS[0]}, еще текст'}
    response = auth_client.post(url, data=bad_words_data)
    assert response.status_code == HTTPStatus.OK
    assert 'form' in response.context
    form_errors = response.context['form'].errors
    assert 'text' in form_errors
    assert form_errors['text'] == [WARNING]
    comments_count = Comment.objects.count()
    assert comments_count == 0


@pytest.fixture
def setup_comment_edit_delete_test_data():
    news = News.objects.create(title='Заголовок', text='Текст')
    author = User.objects.create(username='Автор комментария')
    author_client = Client()
    author_client.force_login(author)
    reader = User.objects.create(username='Читатель')
    reader_client = Client()
    reader_client.force_login(reader)
    comment = Comment.objects.create(news=news, author=author, text='Текст комментария')
    edit_url = reverse('news:edit', args=(comment.id,))
    delete_url = reverse('news:delete', args=(comment.id,))
    form_data = {'text': 'Обновлённый комментарий'}
    url_to_comments = reverse('news:detail', args=(news.id,)) + '#comments'
    return news, author, author_client, reader_client, comment, edit_url, delete_url, form_data, url_to_comments

@pytest.mark.django_db
def test_author_can_delete_comment(setup_comment_edit_delete_test_data):
    _, author, author_client, _, comment, _, delete_url, _, url_to_comments = setup_comment_edit_delete_test_data
    comments_count = Comment.objects.count()
    assert comments_count == 1
    response = author_client.delete(delete_url)
    assert response.status_code == HTTPStatus.FOUND
    assert response.url.endswith(url_to_comments)
    comments_count = Comment.objects.count()
    assert comments_count == 0

@pytest.mark.django_db
def test_user_cant_delete_comment_of_another_user(setup_comment_edit_delete_test_data):
    _, _, _, reader_client, comment, _, delete_url, _, _ = setup_comment_edit_delete_test_data
    response = reader_client.delete(delete_url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comments_count = Comment.objects.count()
    assert comments_count == 1