from datetime import datetime, timedelta

import pytest
from django.conf import settings
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from news.models import Comment, News

User = get_user_model()


@pytest.fixture
def create_test_news():
    def _create_test_news():
        today = datetime.today()
        all_news = [
            News(
                title=f'Новость {index}',
                text='Просто текст.',
                date=today - timedelta(days=index)
            )
            for index in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1)
        ]
        News.objects.bulk_create(all_news)

    return _create_test_news


@pytest.fixture
def create_test_detail_page():
    news = News.objects.create(
        title='Тестовая новость', text='Просто текст.'
    )
    detail_url = reverse('news:detail', args=(news.id,))
    author = User.objects.create(username='Комментатор')
    now = timezone.now()
    for index in range(2):
        comment = Comment.objects.create(
            news=news, author=author, text=f'Tекст {index}',
        )
        comment.created = now + timedelta(days=index)
        comment.save()
    return detail_url, author


@pytest.mark.django_db
def test_news_count(client, create_test_news):
    create_test_news()
    home_url = reverse('news:home')
    response = client.get(home_url)
    object_list = response.context['object_list']
    news_count = len(object_list)
    assert news_count == settings.NEWS_COUNT_ON_HOME_PAGE


@pytest.mark.django_db
def test_news_order(client, create_test_news):
    create_test_news()
    home_url = reverse('news:home')
    response = client.get(home_url)
    object_list = response.context['object_list']
    all_dates = [news.date for news in object_list]
    sorted_dates = sorted(all_dates, reverse=True)
    assert all_dates == sorted_dates


@pytest.mark.django_db
def test_comments_order(client, create_test_detail_page):
    detail_url, _ = create_test_detail_page
    response = client.get(detail_url)
    assert 'news' in response.context
    news = response.context['news']
    all_comments = news.comment_set.all()
    assert all_comments[0].created < all_comments[1].created


@pytest.mark.django_db
def test_anonymous_client_has_no_form(client, create_test_detail_page):
    detail_url, _ = create_test_detail_page
    response = client.get(detail_url)
    assert 'form' not in response.context


@pytest.mark.django_db
def test_authorized_client_has_form(client, create_test_detail_page):
    detail_url, author = create_test_detail_page
    client.force_login(author)
    response = client.get(detail_url)
    assert 'form' in response.context
