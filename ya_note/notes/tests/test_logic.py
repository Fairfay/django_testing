from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from notes.models import Note
from notes.forms import NoteForm


class NoteTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.User = get_user_model()
        cls.user1 = cls.User.objects.create_user(
            username='testuser')
        cls.user2 = cls.User.objects.create_user(
            username='otheruser')
        cls.user1_client = Client()
        cls.user2_client = Client()
        cls.user1_client.force_login(cls.user1)
        cls.user2_client.force_login(cls.user2)

    @classmethod
    def setUp(cls):
        cls.note = Note.objects.create(title='Test Note',
                                       text='Test Text',
                                       author=cls.user1)

    def tearDown(self):
        Note.objects.all().delete()

    def _create_note(self, title='Test Note', text='Test Text', author=None):
        if author is None:
            author = self.user1
        return Note.objects.create(title=title, text=text, author=author)

    def _get_url(self, view, kwargs=None):
        return reverse(f'notes:{view}', kwargs=kwargs)

    def test_note_creation_and_automatic_slug_generation(self):
        test_cases = [
            {'client': self.user1_client, 'title': 'Test Note 1',
             'text': 'Test Text 1', 'slug': 'test-note-1'},
            {'client': self.user1_client, 'title': 'Test Note 2',
             'text': 'Test Text 2', 'slug': 'test-note-2'},
            {'client': self.user1_client, 'title': 'Test Note 3',
             'text': 'Test Text 3', 'slug': None},
        ]

        for case in test_cases:
            with self.subTest(case=case):
                response = case['client'].post(self._get_url('add'),
                                               {'title': case['title'],
                                                'text': case['text']})
                self.assertEqual(response.status_code, 302)
                note = Note.objects.get(title=case['title'])
                self.assertEqual(note.slug, case['slug'] or 'test-note-3')

    def test_clean_slug_not_unique(self):
        duplicate_note = Note.objects.create(title='Test Note 2',
                                             text='Test Text 2',
                                             author=self.user1)
        form_data = {'title': 'Test Note 3', 'text': 'Test Text 3',
                     'slug': duplicate_note.slug}
        form = NoteForm(data=form_data, instance=self.note)
        self.assertFalse(form.is_valid())

    def test_user_permissions(self):
        views = {'edit': 'Test Note 1', 'delete': 'Test Note 2'}
        for view, title in views.items():
            with self.subTest(view=view):
                note = self._create_note(title=title, author=self.user1)
                response = self.user1_client.get(
                    self._get_url(view, kwargs={'slug': note.slug}))
                self.assertEqual(response.status_code, 200)
                response = self.user2_client.get(
                    self._get_url(view, kwargs={'slug': note.slug}))
                self.assertEqual(response.status_code, 404)
