from accounts.models import User
from genres.models import Genre
from movies.models import Movie
from rest_framework import status
from rest_framework.test import APITestCase
from tests.mocks import movie_info, user_info


class T3RouteTests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.base_url = "http://localhost:8000/api/"
        cls.user_info = user_info()
        cls.movie_info = movie_info()
        genres = cls.movie_info.pop("genres")
        movie: Movie = Movie.objects.create(**cls.movie_info)
        for genre in genres:
            found_genre = Genre.objects.get_or_create(**genre)[0]
            movie.genres.add(found_genre)
        cls.movie = movie

    def test_if_cant_create_movie_if_not_logged(self):
        response = self.client.post(
            f"{self.base_url}movies/", self.movie_info, format="json"
        )
        self.assertEqual(response.headers["Content-Type"], "application/json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn("detail", response.json())
        self.assertEqual(
            response.json()["detail"], "Authentication credentials were not provided."
        )

    def test_if_normal_user_cant_create_movie(self):
        self.client.force_authenticate(user=User.objects.create_user(**self.user_info))
        response = self.client.post(
            f"{self.base_url}movies/", self.movie_info, format="json"
        )
        self.assertEqual(response.headers["Content-Type"], "application/json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertIn("detail", response.json())
        self.assertEqual(
            response.json()["detail"],
            "You do not have permission to perform this action.",
        )

    def test_if_movie_cant_be_created_with_invalid_token(self):
        response = self.client.post(
            f"{self.base_url}movies/",
            self.movie_info,
            HTTP_AUTHORIZATION="Token comcertezaissonaoehumtokenvalido",
            format="json",
        )
        self.assertEqual(response.headers["Content-Type"], "application/json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn("detail", response.json())
        self.assertEqual(response.json()["detail"], "Invalid token.")

    def test_if_movie_can_be_updated(self):
        self.client.force_authenticate(
            user=User.objects.create_superuser(**self.user_info)
        )
        new_movie_info = movie_info()
        response = self.client.patch(
            f"{self.base_url}movies/{self.movie.id}/", new_movie_info, format="json"
        )
        updated_movie: Movie = Movie.objects.all().first()
        self.assertEqual(response.headers["Content-Type"], "application/json")
        self.assertEqual(new_movie_info["title"], updated_movie.title)
        self.assertEqual(new_movie_info["duration"], updated_movie.duration)
        self.assertEqual(new_movie_info["classification"], updated_movie.classification)
        self.assertEqual(new_movie_info["synopsis"], updated_movie.synopsis)

    def test_if_cant_update_movie_if_not_logged(self):
        response = self.client.patch(
            f"{self.base_url}movies/{self.movie.id}/", movie_info(), format="json"
        )
        self.assertEqual(response.headers["Content-Type"], "application/json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn("detail", response.json())
        self.assertEqual(
            response.json()["detail"], "Authentication credentials were not provided."
        )

    def test_if_normal_user_cant_update_movie(self):
        self.client.force_authenticate(user=User.objects.create_user(**self.user_info))
        response = self.client.patch(
            f"{self.base_url}movies/{self.movie.id}/", movie_info(), format="json"
        )
        self.assertEqual(response.headers["Content-Type"], "application/json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertIn("detail", response.json())
        self.assertEqual(
            response.json()["detail"],
            "You do not have permission to perform this action.",
        )

    def test_if_movie_cant_be_updated_with_invalid_token(self):
        response = self.client.patch(
            f"{self.base_url}movies/",
            movie_info(),
            HTTP_AUTHORIZATION="Token comcertezaissonaoehumtokenvalido",
            format="json",
        )
        self.assertEqual(response.headers["Content-Type"], "application/json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn("detail", response.json())
        self.assertEqual(response.json()["detail"], "Invalid token.")

    def test_if_can_delete_movie(self):
        self.client.force_authenticate(
            user=User.objects.create_superuser(**self.user_info)
        )
        response = self.client.delete(
            f"{self.base_url}movies/{self.movie.id}/", format="json"
        )
        movie_exists = Movie.objects.filter(id=self.movie.id).exists()
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(movie_exists)

    def test_if_cant_delete_movie_if_not_logged(self):
        response = self.client.delete(
            f"{self.base_url}movies/{self.movie.id}/", format="json"
        )
        self.assertEqual(response.headers["Content-Type"], "application/json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn("detail", response.json())
        self.assertEqual(
            response.json()["detail"], "Authentication credentials were not provided."
        )

    def test_if_normal_user_cant_delete_movie(self):
        self.client.force_authenticate(user=User.objects.create_user(**self.user_info))
        response = self.client.delete(
            f"{self.base_url}movies/{self.movie.id}/", format="json"
        )
        self.assertEqual(response.headers["Content-Type"], "application/json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertIn("detail", response.json())
        self.assertEqual(
            response.json()["detail"],
            "You do not have permission to perform this action.",
        )

    def test_if_movie_cant_be_deleted_with_invalid_token(self):
        response = self.client.delete(
            f"{self.base_url}movies/",
            HTTP_AUTHORIZATION="Token comcertezaissonaoehumtokenvalido",
            format="json",
        )
        self.assertEqual(response.headers["Content-Type"], "application/json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn("detail", response.json())
        self.assertEqual(response.json()["detail"], "Invalid token.")

    def test_if_admin_can_get_all_users(self):
        user = User.objects.create_user(**user_info())
        self.client.force_authenticate(
            user=User.objects.create_superuser(**self.user_info)
        )
        response = self.client.get(f"{self.base_url}users/", format="json")
        self.assertEqual(response.headers["Content-Type"], "application/json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("results", response.json())
        self.assertIsInstance(response.json()["results"], list)
        self.assertEqual(len(response.json()["results"]), 2)
        self.assertEqual(response.json()["results"][0]["id"], user.id)
        self.assertEqual(response.json()["results"][0]["email"], user.email)
        self.assertEqual(response.json()["results"][0]["first_name"], user.first_name)
        self.assertEqual(response.json()["results"][0]["last_name"], user.last_name)

    def test_if_cant_get_all_users_if_not_logged(self):
        response = self.client.get(f"{self.base_url}users/", format="json")
        self.assertEqual(response.headers["Content-Type"], "application/json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn("detail", response.json())
        self.assertEqual(
            response.json()["detail"], "Authentication credentials were not provided."
        )

    def test_if_normal_user_cant_get_all_users(self):
        self.client.force_authenticate(user=User.objects.create_user(**self.user_info))
        response = self.client.get(f"{self.base_url}users/", format="json")
        self.assertEqual(response.headers["Content-Type"], "application/json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertIn("detail", response.json())
        self.assertEqual(
            response.json()["detail"],
            "You do not have permission to perform this action.",
        )

    def test_if_cant_get_all_users_with_invalid_token(self):
        response = self.client.get(
            f"{self.base_url}users/",
            HTTP_AUTHORIZATION="Token comcertezaissonaoehumtokenvalido",
            format="json",
        )
        self.assertEqual(response.headers["Content-Type"], "application/json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn("detail", response.json())
        self.assertEqual(response.json()["detail"], "Invalid token.")

    def test_if_admin_can_get_user_by_id(self):
        user: User = User.objects.create_user(**self.user_info)
        self.client.force_authenticate(
            user=User.objects.create_superuser(**user_info())
        )
        response = self.client.get(f"{self.base_url}users/{user.id}/", format="json")
        self.assertEqual(response.headers["Content-Type"], "application/json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()["id"], user.id)
        self.assertEqual(response.json()["email"], user.email)
        self.assertEqual(response.json()["first_name"], user.first_name)
        self.assertEqual(response.json()["last_name"], user.last_name)

    def test_if_cant_get_specific_user_if_not_logged(self):
        user: User = User.objects.create_user(**self.user_info)
        response = self.client.get(f"{self.base_url}users/{user.id}/", format="json")
        self.assertEqual(response.headers["Content-Type"], "application/json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn("detail", response.json())
        self.assertEqual(
            response.json()["detail"], "Authentication credentials were not provided."
        )

    def test_if_normal_user_cant_get_specific_user(self):
        user: User = User.objects.create_user(**user_info())
        self.client.force_authenticate(user=User.objects.create_user(**self.user_info))
        response = self.client.get(f"{self.base_url}users/{user.id}/", format="json")
        self.assertEqual(response.headers["Content-Type"], "application/json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertIn("detail", response.json())
        self.assertEqual(
            response.json()["detail"],
            "You do not have permission to perform this action.",
        )

    def test_if_cant_get_specific_user_with_invalid_token(self):
        user: User = User.objects.create_user(**self.user_info)
        response = self.client.get(
            f"{self.base_url}users/{user.id}/",
            HTTP_AUTHORIZATION="Token comcertezaissonaoehumtokenvalido",
            format="json",
        )

        self.assertEqual(response.headers["Content-Type"], "application/json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn("detail", response.json())
        self.assertEqual(response.json()["detail"], "Invalid token.")
