import random

from faker import Faker
from faker.providers.person import Provider

fake: Provider = Faker()

fake.add_provider(Provider)

movie_genres = [
    "Action",
    "Comedy",
    "Drama",
    "Fantasy",
    "Horror",
    "Mystery",
    "Romance",
    "Thriller",
    "Western",
]

review_recomendations = ["Must Watch", "Should Watch", "Avoid Watch", "No Opinion"]


def user_info():
    return {
        "email": fake.unique.email(),
        "password": fake.password(),
        "first_name": fake.first_name(),
        "last_name": fake.last_name(),
    }


def movie_info():
    return {
        "title": fake.text()[:20].strip(),
        "duration": f"{random.randint(1, 200)}m",
        "genres": [
            {"name": genre} for genre in random.sample(movie_genres, len(movie_genres))
        ],
        "premiere": fake.date(),
        "classification": random.randint(1, 100),
        "synopsis": fake.text()[:140].strip(),
    }


def genre_info():
    return {"name": random.choice(movie_genres)}


def review_info():
    return {
        "stars": random.randint(1, 10),
        "review": fake.text()[:100].strip(),
        "spoilers": random.choice([True, False]),
        "recomendation": random.choice(review_recomendations),
    }


def required_fields_in_request_register_critic():
    return ["first_name", "last_name", "email", "password"]


def required_fields_in_response_register_critic():
    return ["id", "first_name", "last_name", "email", "date_joined", "updated_at"]


def required_fields_in_request_create_movie():
    return ["title", "premiere", "duration", "classification", "synopsis", "genres"]


def required_fields_in_response_create_movie():
    return [
        "id",
        "title",
        "premiere",
        "duration",
        "classification",
        "synopsis",
        "genres",
    ]


def required_fields_pagination():
    return ["count", "next", "previous", "results"]
