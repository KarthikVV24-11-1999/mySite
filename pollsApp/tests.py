from django.test import TestCase
from django.urls import reverse
from .models import Question, Choice


class PollsAppTests(TestCase):
    def setUp(self):
        self.question = Question.objects.create(
            question_text="This is a Sample Question text",
            pub_date="2024-01-01 00:00:00",
        )
        self.choice = Choice.objects.create(
            question=self.question, choice_text="Choice 1", votes=0
        )

    def test_index_view_status_code(self):
        response = self.client.get(reverse("pollsApp:index"))
        self.assertEqual(response.status_code, 200)

    def test_index_view_uses_correct_template(self):
        response = self.client.get(reverse("pollsApp:index"))
        self.assertTemplateUsed(response, "pollsApp/index.html")

    def test_index_view_displays_question(self):
        response = self.client.get(reverse("pollsApp:index"))
        self.assertContains(response, self.question.question_text)

    def test_vote_view_redirects_to_results(self):
        response = self.client.post(
            reverse("pollsApp:vote", args=[self.question.pk]),
            {"choice": self.choice.pk},
        )
        self.assertRedirects(
            response, reverse("pollsApp:results", args=[self.question.pk])
        )

    def test_vote_increases_choice_vote_count(self):
        initial_votes = self.choice.votes
        self.client.post(
            reverse("pollsApp:vote", args=[self.question.pk]),
            {"choice": self.choice.pk},
        )
        self.choice.refresh_from_db()
        self.assertEqual(self.choice.votes, initial_votes + 1)

    def test_results_view_displays_correct_question(self):
        response = self.client.get(reverse("pollsApp:results", args=[self.question.pk]))
        self.assertContains(response, self.question.question_text)

    def test_results_view_displays_correct_choice(self):
        response = self.client.get(reverse("pollsApp:results", args=[self.question.pk]))
        self.assertContains(response, self.choice.choice_text)

    def test_vote_view_does_not_increase_vote_count_for_invalid_choice(self):
        initial_votes = self.choice.votes
        self.client.post(
            reverse("pollsApp:vote", args=[self.question.pk]), {"choice": 999}
        )
        self.choice.refresh_from_db()
        self.assertEqual(self.choice.votes, initial_votes)

    def test_question_creation_updates_index_view(self):
        new_question = Question.objects.create(
            question_text="This is a New Sample Question Text",
            pub_date="2024-01-01 00:00:00",
        )
        response = self.client.get(reverse("pollsApp:index"))
        self.assertContains(response, new_question.question_text)
