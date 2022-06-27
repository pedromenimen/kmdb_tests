from datetime import date, datetime

from accounts.models import User
from genres.models import Genre
from movies.models import Movie
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase
from tests.mocks import (
    movie_info,
    required_fields_in_request_create_movie,
    required_fields_in_response_create_movie,
    user_info,
)


class T2RouteTests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.base_url = "http://localhost:8000/api/"
        cls.user_info = user_info()
        cls.movie_info = movie_info()

    def test_if_movie_can_be_created(self):
        self.client.force_authenticate(
            user=User.objects.create_superuser(**self.user_info)
        )
        response = self.client.post(
            f"{self.base_url}movies/", self.movie_info, format="json"
        )
        movie: Movie = Movie.objects.all().first()
        self.assertEqual(response.headers["Content-Type"], "application/json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        for field in required_fields_in_response_create_movie():
            self.assertIn(field, response.json())

        self.assertEqual(response.json()["id"], movie.id)
        self.assertEqual(response.json()["title"], movie.title)
        self.assertEqual(response.json()["duration"], movie.duration)
        self.assertEqual(response.json()["classification"], movie.classification)
        self.assertEqual(response.json()["synopsis"], movie.synopsis)
        self.assertTrue(
            type(movie.premiere) == datetime or type(movie.premiere) == date,
        )

    def test_if_movie_cant_be_created_if_is_missing_fields(self):
        self.client.force_authenticate(
            user=User.objects.create_superuser(**self.user_info)
        )
        response = self.client.post(f"{self.base_url}movies/", {}, format="json")

        self.assertEqual(response.headers["Content-Type"], "application/json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        for field in required_fields_in_request_create_movie():
            self.assertEqual(response.json()[field], ["This field is required."])

    def test_if_user_can_get_movie_list(self):
        genres = self.movie_info.pop("genres")
        movie: Movie = Movie.objects.create(**self.movie_info)
        for genre in genres:
            found_genre = Genre.objects.get_or_create(**genre)[0]
            found_genre.Movie.add(movie)
        response = self.client.get(f"{self.base_url}movies/", format="json")
        self.assertEqual(response.headers["Content-Type"], "application/json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.json()["results"], list)
        self.assertEqual(response.json()["results"][0]["id"], movie.id)
        self.assertEqual(response.json()["results"][0]["title"], movie.title)
        self.assertEqual(response.json()["results"][0]["duration"], movie.duration)
        self.assertEqual(
            response.json()["results"][0]["classification"], movie.classification
        )
        self.assertEqual(response.json()["results"][0]["synopsis"], movie.synopsis)

    def test_if_user_can_get_movie_by_id(self):
        genres = self.movie_info.pop("genres")
        movie: Movie = Movie.objects.create(**self.movie_info)
        for genre in genres:
            found_genre = Genre.objects.get_or_create(**genre)[0]
            found_genre.Movie.add(movie)
        response = self.client.get(f"{self.base_url}movies/{movie.id}/", format="json")

        self.assertEqual(response.headers["Content-Type"], "application/json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()["id"], movie.id)
        self.assertEqual(response.json()["title"], movie.title)
        self.assertEqual(response.json()["duration"], movie.duration)
        self.assertEqual(response.json()["classification"], movie.classification)
        self.assertEqual(response.json()["synopsis"], movie.synopsis)

    def test_if_user_can_login(self):
        user: User = User.objects.create_user(**self.user_info)
        response = self.client.post(
            f"{self.base_url}users/login/",
            {"email": self.user_info["email"], "password": self.user_info["password"]},
            format="json",
        )
        token = Token.objects.get(user=user).key
        self.assertEqual(response.headers["Content-Type"], "application/json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("token", response.json())
        self.assertEqual(response.json()["token"], token)

    def test_if_user_cant_login_with_wrong_email_or_password(self):
        response = self.client.post(
            f"{self.base_url}users/login/",
            {
                "email": self.user_info["email"] + "aa",
                "password": self.user_info["password"] + "aa",
            },
            format="json",
        )

        self.assertEqual(response.headers["Content-Type"], "application/json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn("detail", response.json())
        self.assertEqual(response.json()["detail"], "invalid email or password")

    def test_if_user_cant_login_if_is_missing_some_field(self):
        response = self.client.post(f"{self.base_url}users/login/", {}, format="json")

        self.assertEqual(response.headers["Content-Type"], "application/json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json()["email"], ["This field is required."])
        self.assertEqual(response.json()["password"], ["This field is required."])
