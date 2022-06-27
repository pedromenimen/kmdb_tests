from accounts.models import User
from genres.models import Genre
from movies.models import Movie
from rest_framework import status
from rest_framework.test import APITestCase
from reviews.models import Review
from tests.mocks import movie_info, review_info, user_info


class T4RouteTests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.base_url = "http://localhost:8000/api/"
        cls.user_info = user_info()
        cls.movie_info = movie_info()
        cls.review_info = review_info()
        genres = cls.movie_info.pop("genres")
        movie: Movie = Movie.objects.create(**cls.movie_info)
        for genre in genres:
            found_genre = Genre.objects.get_or_create(**genre)[0]
            found_genre.Movie.add(movie)
        cls.movie = movie

    def test_if_user_can_create_a_review(self):
        user: User = User.objects.create_user(**self.user_info)
        self.client.force_authenticate(user=user)

        review_info = self.review_info
        review_info.pop("recomendation")
        response = self.client.post(
            f"{self.base_url}movies/{self.movie.id}/reviews/",
            review_info,
            format="json",
        )
        review: Review = Review.objects.all().first()
        self.assertEqual(response.headers["Content-Type"], "application/json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.json()["movie_id"], self.movie.id)
        self.assertEqual(response.json()["stars"], review.stars)
        self.assertEqual(response.json()["review"], review.review)
        self.assertEqual(response.json()["spoilers"], review.spoilers)
        self.assertEqual(response.json()["recomendation"], review.recomendation)
        self.assertEqual(response.json()["critic"]["id"], user.id)

    def test_if_user_cant_create_review_with_wrong_recomendation_string(self):
        self.client.force_authenticate(user=User.objects.create_user(**self.user_info))
        review_info = self.review_info
        review_info["recomendation"] = "invalid recomendation"
        response = self.client.post(
            f"{self.base_url}movies/{self.movie.id}/reviews/",
            review_info,
            format="json",
        )

        self.assertEqual(response.headers["Content-Type"], "application/json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("recomendation", response.json())
        self.assertTrue("invalid recomendation" in response.json()["recomendation"][0])
        self.assertTrue("is not a valid choice" in response.json()["recomendation"][0])

    def test_if_user_cant_create_review_if_star_field_is_out_of_range(self):
        self.client.force_authenticate(user=User.objects.create_user(**self.user_info))
        review_info = self.review_info
        review_info["stars"] = 100
        response = self.client.post(
            f"{self.base_url}movies/{self.movie.id}/reviews/",
            review_info,
            format="json",
        )

        self.assertEqual(response.headers["Content-Type"], "application/json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("stars", response.json())
        self.assertEqual(
            response.json()["stars"], ["Ensure this value is less than or equal to 10."]
        )

    def test_if_user_cant_create_review_if_star_field_is_less_than_min_value(self):
        self.client.force_authenticate(user=User.objects.create_user(**self.user_info))
        review_info = self.review_info
        review_info["stars"] = 0
        response = self.client.post(
            f"{self.base_url}movies/{self.movie.id}/reviews/",
            review_info,
            format="json",
        )

        self.assertEqual(response.headers["Content-Type"], "application/json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("stars", response.json())
        self.assertEqual(
            response.json()["stars"],
            ["Ensure this value is greater than or equal to 1."],
        )

    def test_if_user_can_get_review_without_being_logged(self):
        user: User = User.objects.create_user(**self.user_info)
        review: Review = Review.objects.create(
            **self.review_info, movie=self.movie, critic=user
        )
        response = self.client.get(
            f"{self.base_url}movies/{self.movie.id}/reviews/", format="json"
        )
        self.assertEqual(response.headers["Content-Type"], "application/json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("results", response.json())
        self.assertIsInstance(response.json()["results"], list)
        self.assertEqual(response.json()["results"][0]["id"], review.id)
        self.assertEqual(response.json()["results"][0]["stars"], review.stars)
        self.assertEqual(response.json()["results"][0]["review"], review.review)
        self.assertEqual(response.json()["results"][0]["spoilers"], review.spoilers)
        self.assertEqual(
            response.json()["results"][0]["recomendation"], review.recomendation
        )
        self.assertEqual(response.json()["results"][0]["critic"]["id"], user.id)

    def test_if_admin_can_delete_any_review(self):
        self.client.force_authenticate(
            user=User.objects.create_superuser(**self.user_info),
        )
        user: User = User.objects.create_user(**user_info())
        review: Review = Review.objects.create(
            **self.review_info, movie=self.movie, critic=user
        )
        response = self.client.delete(
            f"{self.base_url}reviews/{review.id}/", format="json"
        )
        review_exists = Review.objects.filter(id=review.id).exists()
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(review_exists)

    def test_if_normal_user_can_delete_its_review(self):
        user: User = User.objects.create_user(**self.user_info)
        self.client.force_authenticate(user=user)
        review: Review = Review.objects.create(
            **self.review_info, movie=self.movie, critic=user
        )
        response = self.client.delete(
            f"{self.base_url}reviews/{review.id}/", format="json"
        )
        review_exists = Review.objects.filter(id=review.id).exists()
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(review_exists)

    def test_if_normal_user_cant_delete_review_from_other_user(self):
        user: User = User.objects.create_user(**user_info())
        review: Review = Review.objects.create(
            **self.review_info,
            movie=self.movie,
            critic=user,
        )
        user_without_review: User = User.objects.create_user(**self.user_info)
        self.client.force_authenticate(user=user_without_review)
        response = self.client.delete(
            f"{self.base_url}reviews/{review.id}/", format="json"
        )
        review_exists = Review.objects.filter(id=review.id).exists()
        self.assertEqual(response.headers["Content-Type"], "application/json")
        self.assertTrue(review_exists)

    def test_if_review_list_can_be_listed_if_not_logged(self):
        response = self.client.get(f"{self.base_url}reviews/", format="json")

        self.assertEqual(response.headers["Content-Type"], "application/json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("results", response.json())
        self.assertIsInstance(response.json()["results"], list)
