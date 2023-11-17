from http import HTTPStatus
from django.urls import reverse
import pytest
from django.contrib.auth import get_user_model
# Импортируем класс комментария.
from news.models import Comment, News

# Получаем модель пользователя.
User = get_user_model()


@pytest.fixture
def setup_test_data():
    news = News.objects.create(title='Заголовок', text='Текст')
    author = User.objects.create(username='Лев Толстой')
    reader = User.objects.create(username='Читатель простой')
    comment = Comment.objects.create(
        news=news,
        author=author,
        text='Текст комментария'
    )
    return news, author, reader, comment


@pytest.mark.django_db
def test_pages_availability(client, setup_test_data):
    news, _, _, _ = setup_test_data
    urls = [
        ('news:home', None),
        ('news:detail', (news.id,)),
        ('users:login', None),
        ('users:logout', None),
        ('users:signup', None),
    ]
    for name, args in urls:
        url = reverse(name, args=args)
        response = client.get(url)
        assert response.status_code == HTTPStatus.OK


@pytest.mark.django_db
def test_redirect_for_anonymous_client(client, setup_test_data):
    _, _, _, comment = setup_test_data
    login_url = reverse('users:login')

    for name in ('news:edit', 'news:delete'):
        url = reverse(name, args=(comment.id,))
        redirect_url = f'{login_url}?next={url}'
        response = client.get(url)
        assert response.status_code == HTTPStatus.FOUND
        assert response.url == redirect_url