from django.contrib.auth import get_user_model
from django.test import Client
from django.test import TestCase
from django.urls import reverse

from notes.models import Note
from notes.forms import NoteForm


class NoteTests(TestCase):
    def setUp(self):
        self.client = Client()

        self.user1 = get_user_model().objects.create_user(username='user1')
        self.user2 = get_user_model().objects.create_user(username='user2')

        self.note_user1 = Note.objects.create(title='Заметка 1',
                                              text='Текст 1',
                                              author=self.user1)

        self.note_user2 = Note.objects.create(title='Заметка 2',
                                              text='Текст 2',
                                              author=self.user2)

        self.client.force_login(self.user1)

    def test_notes_list_view_context(self):
        response = self.client.get(reverse('notes:list'))
        self.assertContains(response, self.note_user1.title)
        self.assertNotContains(response, self.note_user2.title)

    def test_create_and_edit_note_forms_are_passed(self):
        response_add = self.client.get(reverse('notes:add'))
        response_edit = self.client.get(reverse('notes:edit',
                                                args=[self.note_user1.slug]))
        self.assertIsInstance(response_add.context['form'], NoteForm)
        self.assertIsInstance(response_edit.context['form'], NoteForm)

    def test_notes_of_another_user_not_in_context(self):
        response = self.client.get(reverse('notes:detail',
                                           args=[self.note_user2.slug]))
        self.assertNotIn('object', response.context)
