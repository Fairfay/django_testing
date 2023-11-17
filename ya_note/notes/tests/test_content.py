# tests.py
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from notes.models import Note
from notes.forms import NoteForm

class NoteTests(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='user1', password='password1')
        self.user2 = User.objects.create_user(username='user2', password='password2')
        self.note_user1 = Note.objects.create(title='Заметка 1', text='Текст 1', author=self.user1)
        self.note_user2 = Note.objects.create(title='Заметка 2', text='Текст 2', author=self.user2)

        # Логинимся под пользователем user1
        self.client.login(username='user1', password='password1')

    def test_notes_list_view_context(self):
        response = self.client.get(reverse('notes:list'))
        self.assertContains(response, self.note_user1.title)
        self.assertNotContains(response, self.note_user2.title)

    def test_create_and_edit_note_forms_are_passed(self):
        response_add = self.client.get(reverse('notes:add'))
        response_edit = self.client.get(reverse('notes:edit', args=[self.note_user1.slug]))

        self.assertIsInstance(response_add.context['form'], NoteForm)
        self.assertIsInstance(response_edit.context['form'], NoteForm)

    def test_notes_of_another_user_not_in_context(self):
        response = self.client.get(reverse('notes:detail', args=[self.note_user2.slug]))
        self.assertNotIn('object', response.context)
