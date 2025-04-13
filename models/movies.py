from sqlalchemy import Column, Integer, String, ForeignKey
from typing import List, Optional
from sqlalchemy.orm import relationship
from models import Base

class Movies(Base):
    __tablename__ = 'movies'
    id = Column("pk_movies", Integer, primary_key=True)
    title = Column(String(200), unique=False, nullable=False)
    genre = Column(String(200), unique=False, nullable=False)
    director = Column(String(200), unique=False, nullable=False)
    description = Column(String(200), unique=False, nullable=False)
    year = Column(Integer, nullable=False)
    cover = Column(String(500), unique=False, nullable=True)  # URL to movie poster image
    user_id = Column(Integer, ForeignKey('users.pk_users'), nullable=False)  # Added user_id for who added the movie

    # Relationships
    user = relationship("User", back_populates="movies")  # User who added the movie
    user_movies = relationship(
        "UserMovie",
        back_populates="movie",
        lazy="select",
        cascade="all, delete-orphan"
    )

    # Users who have this in watchlist/watched

    def __init__(self, title: str, genre: str, director: str, year: int, description: str,
                 cover: Optional[str] = None, user_id: Optional[int] = None,
                 reviews: Optional[List["Review"]] = None):
        """
        Initializes a Movies instance.

        Arguments:
            title: Title of the movie.
            genre: Genre(s) of the movie (comma separated if multiple).
            director: Director of the movie.
            year: Release year of the movie.
            description: Brief description of the movie.
            cover: URL to the movie poster image.
            user_id: ID of the user who added this movie.
            reviews: An optional list of Review objects.
        """
        self.title = title
        self.genre = genre
        self.director = director
        self.year = year
        self.description = description
        self.cover = cover
        self.user_id = user_id
        self.reviews = reviews if reviews is not None else []

    def add_review(self, review: "Review") -> None:
        """
        Adds a new review to this movie.

        Arguments:
            review: An instance of Review to be added.
        """
        self.reviews.append(review)

    def average_rating(self) -> float:
        """
        Calculate and return the average rating of the movie based on its reviews.
        If there are no reviews, this method returns 0.0.
        """
        if not self.reviews:
            return 0.0

        total = sum(review.rating for review in self.reviews)
        return total / len(self.reviews)

    def return_genres(self) -> List[str]:
        """
        Returns a list of genres by splitting the comma-separated genre string.
        """
        return [genre.strip() for genre in self.genre.split(',')] if self.genre else []

    # Method to get watch count
    def watch_count(self):
        return len([um for um in self.user_movies if um.watched])

    def __repr__(self):
        """String representation of Movie object"""
        return f'<Movie {self.id}>, {self.title}, {self.genre}, {self.director}, {self.year}, {self.reviews}'