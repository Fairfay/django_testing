from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from notes.models import Note
from notes.forms import NoteForm
from django.core.exceptions import ValidationError


class NoteTestCase(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='testuser',
            password='testpassword'
        )

    def _create_note(self, title='Test Note', text='Test Text', author=None):
        if author is None:
            author = self.user
        return Note.objects.create(title=title, text=text, author=author)

    def _get_url(self, view, kwargs=None):
        return reverse(f'notes:{view}', kwargs=kwargs)

    def _login(self, username='testuser', password='testpassword'):
        self.client.login(username=username, password=password)

    def test_note_creation_and_automatic_slug_generation(self):
        test_cases = [
            {'login': True, 'title': 'Test Note 1', 'text': 'Test Text 1', 'slug': 'test-note-1'},
            {'login': False, 'title': 'Test Note 2', 'text': 'Test Text 2', 'slug': 'test-note-2'},
            {'login': True, 'title': 'Test Note 3', 'text': 'Test Text 3', 'slug': None},
        ]

        for case in test_cases:
            with self.subTest(case=case):
                if case['login']:
                    self._login()
                response = self.client.post(self._get_url('add'), {'title': case['title'], 'text': case['text']})
                self.assertEqual(response.status_code, 302)
                note = Note.objects.get(title=case['title'])
                self.assertEqual(note.slug, case['slug'] or 'test-note-3')

    def test_clean_slug_not_unique(self):
        self.note = Note.objects.create(title='Test Note', text='Test Text', author=self.user)
        # Создаем еще одну заметку с таким же slug
        duplicate_note = Note.objects.create(title='Test Note 2', text='Test Text 2', author=self.user)

        # Создаем форму с тем же самым slug, что и у duplicate_note
        form_data = {'title': 'Test Note 3', 'text': 'Test Text 3', 'slug': duplicate_note.slug}
        form = NoteForm(data=form_data, instance=self.note)
        self.assertFalse(form.is_valid())



    def test_user_permissions(self):
        other_user = get_user_model().objects.create_user(
            username='otheruser',
            password='otherpassword'
        )
        views = {'edit': 'Test Note 1', 'delete': 'Test Note 2'}

        for view, title in views.items():
            with self.subTest(view=view):
                note = self._create_note(title=title, author=self.user)
                self._login()
                response = self.client.get(self._get_url(view, kwargs={'slug': note.slug}))
                self.assertEqual(response.status_code, 200)

                self._login(username='otheruser', password='otherpassword')
                response = self.client.get(self._get_url(view, kwargs={'slug': note.slug}))
                self.assertEqual(response.status_code, 404)
