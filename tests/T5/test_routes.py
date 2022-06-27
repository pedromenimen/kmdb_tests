import pdb

from accounts.models import User
from genres.models import Genre
from movies.models import Movie
from rest_framework import status
from rest_framework.test import APITestCase
from reviews.models import Review
from tests.mocks import movie_info, required_fields_pagination, review_info, user_info


class T5RouteTests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.base_url = "http://localhost:8000/api/"
        cls.user = User.objects.create_superuser(**user_info())

    def test_if_pagination_works_as_expected_in_get_users_route(self):
        users = [User(**user_info()) for _ in range(3)]
        User.objects.bulk_create(users)
        self.client.force_authenticate(user=self.user)
        response = self.client.get(f"{self.base_url}users/", format="json")
        self.assertEqual(response.headers["Content-Type"], "application/json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for field in required_fields_pagination():
            self.assertIn(field, response.json())
        self.assertEqual(response.json()["count"], 4)
        self.assertEqual(len(response.json()["results"]), 3)
        self.assertTrue("/?page=2" in response.json()["next"])
        response2 = self.client.get(response.json()["next"], format="json")
        self.assertEqual(response2.headers["Content-Type"], "application/json")
        for field in required_fields_pagination():
            self.assertIn(field, response2.json())
        self.assertEqual(response2.json()["count"], 4)
        self.assertEqual(len(response2.json()["results"]), 1)

    def test_if_pagination_works_as_expected_in_get_movie_list_route(self):
        for _ in range(4):
            movie_inf = movie_info()
            genres = movie_inf.pop("genres")
            movie: Movie = Movie.objects.create(**movie_inf)
            for genre in genres:
                found_genre = Genre.objects.get_or_create(**genre)[0]
                found_genre.Movie.add(movie)
        self.client.force_authenticate(user=self.user)
        response = self.client.get(f"{self.base_url}movies/", format="json")
        self.assertEqual(response.headers["Content-Type"], "application/json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for field in required_fields_pagination():
            self.assertIn(field, response.json())
        self.assertEqual(response.json()["count"], 4)
        self.assertEqual(len(response.json()["results"]), 3)
        self.assertTrue("/?page=2" in response.json()["next"])
        response2 = self.client.get(response.json()["next"], format="json")
        self.assertEqual(response2.headers["Content-Type"], "application/json")
        for field in required_fields_pagination():
            self.assertIn(field, response2.json())
        self.assertEqual(response2.json()["count"], 4)
        self.assertEqual(len(response2.json()["results"]), 1)

    def test_if_paginator_works_as_expected_in_get_movie_reviews_route(self):
        movie_inf = movie_info()
        genres = movie_inf.pop("genres")
        movie: Movie = Movie.objects.create(**movie_inf)
        for genre in genres:
            found_genre = Genre.objects.get_or_create(**genre)[0]
            found_genre.Movie.add(movie)
        reviews = [
            Review(**review_info(), movie=movie, critic=self.user) for _ in range(4)
        ]
        Review.objects.bulk_create(reviews)
        self.client.force_authenticate(user=self.user)
        response = self.client.get(
            f"{self.base_url}movies/{movie.id}/reviews/", format="json"
        )

        self.assertEqual(response.headers["Content-Type"], "application/json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for field in required_fields_pagination():
            self.assertIn(field, response.json())
        self.assertEqual(response.json()["count"], 4)
        self.assertEqual(len(response.json()["results"]), 3)
        self.assertTrue("/?page=2" in response.json()["next"])
        response2 = self.client.get(response.json()["next"], format="json")
        self.assertEqual(response2.headers["Content-Type"], "application/json")
        for field in required_fields_pagination():
            self.assertIn(field, response2.json())
        self.assertEqual(response2.json()["count"], 4)
        self.assertEqual(len(response2.json()["results"]), 1)

    def test_if_paginator_works_as_expected_in_get_all_reviews_route(self):
        movie_inf = movie_info()
        genres = movie_inf.pop("genres")
        movie: Movie = Movie.objects.create(**movie_inf)
        for genre in genres:
            found_genre = Genre.objects.get_or_create(**genre)[0]
            found_genre.Movie.add(movie)
        reviews = [
            Review(**review_info(), movie=movie, critic=self.user) for _ in range(4)
        ]
        Review.objects.bulk_create(reviews)
        self.client.force_authenticate(user=self.user)
        response = self.client.get(f"{self.base_url}reviews/", format="json")

        self.assertEqual(response.headers["Content-Type"], "application/json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for field in required_fields_pagination():
            self.assertIn(field, response.json())
        self.assertEqual(response.json()["count"], 4)
        self.assertEqual(len(response.json()["results"]), 3)
        self.assertTrue("/?page=2" in response.json()["next"])
        response2 = self.client.get(response.json()["next"], format="json")
        self.assertEqual(response2.headers["Content-Type"], "application/json")
        for field in required_fields_pagination():
            self.assertIn(field, response2.json())
        self.assertEqual(response2.json()["count"], 4)
        self.assertEqual(len(response2.json()["results"]), 1)
