import tempfile
from pathlib import Path

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse


class DocumentSearchViewTests(TestCase):
    def test_search_view_returns_matching_documents(self):
        user_model = get_user_model()
        user = user_model.objects.create_user(username="tester", password="secret")
        self.client.force_login(user)

        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            docs_dir = root / "Documents"
            docs_dir.mkdir()
            sample_file = docs_dir / "math_workbook.pdf"
            sample_file.write_bytes(b"example")

            response = self.client.get(
                reverse("web:document_search"),
                {"q": "workbook", "root": str(root)},
            )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "math_workbook.pdf")

    def test_mentor_view_generates_problem_list_for_book_query(self):
        user_model = get_user_model()
        user = user_model.objects.create_user(username="mentor", password="secret")
        self.client.force_login(user)

        response = self.client.get(reverse("web:mentor"), {"q": "calculus"})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Practice Problems")
        self.assertContains(response, "Hint")
