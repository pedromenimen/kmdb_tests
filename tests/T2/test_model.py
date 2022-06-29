from django.test import TestCase
from genres.models import Genre
from movies.models import Movie
from account.models import User
from reviews.models import Review
from tests.mocks import genre_info, movie_info, review_info


class T2ModelTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.movie_info = movie_info()
        cls.genre_info = genre_info()
        cls.review_info = review_info()

    def test_if_movie_can_be_created(self):
        genres = self.movie_info.pop("genres")
        movie: Movie = Movie.objects.create(**self.movie_info)
        for genre in genres:
            found_genre = Genre.objects.get_or_create(**genre)[0]
            movie.genres.add(found_genre)
        self.assertEqual(movie.title, self.movie_info["title"])
        self.assertEqual(movie.duration, self.movie_info["duration"])
        self.assertEqual(movie.premiere, self.movie_info["premiere"])
        self.assertEqual(movie.classification, self.movie_info["classification"])
        self.assertEqual(movie.synopsis, self.movie_info["synopsis"])

    def test_if_genre_can_be_created(self):
        Genre.objects.create(**self.genre_info)
        genre: Genre = Genre.objects.all().first()
        self.assertEqual(genre.name, self.genre_info["name"])

    def test_if_review_can_be_created(self):
        genres = self.movie_info.pop("genres")
        movie: Movie = Movie.objects.create(**self.movie_info)
        for genre in genres:
            found_genre = Genre.objects.get_or_create(**genre)[0]
            movie.genres.add(found_genre)
        user: User = User.objects.create_user(**self.user_info)
        Review.objects.create(**self.review_info, critic=user, movie=movie)
        review: Review = Review.objects.all().first()
        self.assertEqual(review.stars, self.review_info["stars"])
        self.assertEqual(review.review, self.review_info["review"])
        self.assertEqual(review.spoilers, self.review_info["spoilers"])
        self.assertEqual(review.recomendation, self.review_info["recomendation"])
