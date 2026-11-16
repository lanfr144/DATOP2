"""Tests du lab 02c. Lancer : python manage.py test"""
from rest_framework.test import APITestCase


class HelloTests(APITestCase):
    def test_hello(self):
        self.assertEqual(self.client.get("/hello/").json(), {"message": "Hello, DRF!"})
        self.assertEqual(self.client.get("/hello/Ana/").json(), {"message": "Hello, Ana!"})
        self.assertEqual(self.client.post("/hello/").status_code, 405)   # GET seulement
        self.assertIn("time", self.client.get("/time/").json())


class BookTests(APITestCase):
    def setUp(self):
        for title, author, published in [("Django for Beginners", "William S. Vincent", "2020-01-01"),
                                          ("Python Tricks", "Dan Bader", "2017-10-01"),
                                          ("Two Scoops of Django", "Daniel Feldroy", "2022-03-01")]:
            r = self.client.post("/books/", {"title": title, "author": author, "published": published},
                                 format="json")
            self.assertEqual(r.status_code, 201)

    def test_search_ordering_pagination(self):
        r = self.client.get("/books/?search=vincent").json()
        self.assertEqual([b["title"] for b in r["results"]], ["Django for Beginners"])
        # pagination (PAGE_SIZE = 2) : count, next, previous, results
        page1 = self.client.get("/books/?ordering=-published").json()
        self.assertEqual(page1["count"], 3)
        self.assertEqual([b["title"] for b in page1["results"]], ["Two Scoops of Django", "Django for Beginners"])
        self.assertIsNotNone(page1["next"])
        combined = self.client.get("/books/?search=django&ordering=title&page=1").json()
        self.assertEqual([b["title"] for b in combined["results"]], ["Django for Beginners", "Two Scoops of Django"])

    def test_crud_and_validation(self):
        pk = self.client.get("/books/?search=tricks").json()["results"][0]["id"]
        self.assertEqual(self.client.patch(f"/books/{pk}/", {"title": "PT"}, format="json").json()["title"], "PT")
        self.assertEqual(self.client.post("/books/", {"title": "x"}, format="json").status_code, 400)
        r = self.client.post("/books/", {"title": "Future", "author": "X", "published": "2099-01-01"}, format="json")
        self.assertEqual(r.status_code, 400)
        self.assertEqual(r.json()["published"], ["The publication date cannot be in the future."])
        self.assertEqual(self.client.delete(f"/books/{pk}/").status_code, 204)
        self.assertEqual(self.client.get(f"/books/{pk}/").status_code, 404)

    def test_exercise3_function_views(self):
        r = self.client.post("/v1/books/", {"title": "A", "author": "B", "published": "2020-01-01"}, format="json")
        self.assertEqual(r.status_code, 201)
        pk = r.json()["id"]
        self.assertEqual(self.client.put(f"/v1/books/{pk}/", {"title": "A2", "author": "B", "published": "2020-01-01"},
                                         format="json").json()["title"], "A2")
        self.assertEqual(self.client.delete(f"/v1/books/{pk}/").status_code, 204)
        self.assertEqual(self.client.get(f"/v1/books/{pk}/").status_code, 404)   # get_object_or_404
