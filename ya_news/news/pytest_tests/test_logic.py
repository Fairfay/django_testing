from django.urls import reverse

import pytest
from http import HTTPStatus

from news.models import Comment
from news.forms import BAD_WORDS, WARNING


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
def test_user_cant_use_bad_words(test_news, auth_client):
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
def test_author_can_delete_comment(author_client,
                                   delete_url, url_to_comments):
    assert Comment.objects.count() == 1
    response = author_client.delete(delete_url)
    assert response.status_code == HTTPStatus.FOUND
    assert response.url.endswith(url_to_comments)
    assert Comment.objects.count() == 0


@pytest.mark.django_db
def test_user_cant_delete_comment_of_another_user(reader_client,
                                                  delete_url):
    response = reader_client.delete(delete_url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.count() == 1
