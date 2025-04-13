from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from sqlalchemy.orm import relationship
from models import Base


class User(Base):
    __tablename__ = 'users'
    id = Column("pk_users", Integer, primary_key=True)
    username = Column(String(140), unique=True, nullable=False)
    created = Column(DateTime, default=datetime.now(), nullable=False)
    updated = Column(DateTime, default=datetime.now(), onupdate=datetime.now())

    # Update relationships
    movies = relationship("Movies", back_populates="user", lazy="select")  # Movies added by user
    user_movies = relationship("UserMovie", back_populates="user", lazy="select")  # User's watchlist/watched

    # Methods to get watchlist and watched movies
    def get_watchlist(self):
        return [um.movie for um in self.user_movies if um.in_watchlist and not um.watched]

    def get_watched(self):
        return [um.movie for um in self.user_movies if um.watched]

    def get_stats(self):
        watched_movies = [um for um in self.user_movies if um.watched]
        total_watched = len(watched_movies)

        # Count by genre
        genre_counts = {}
        for um in watched_movies:
            genres = um.movie.return_genres()
            for genre in genres:
                if genre in genre_counts:
                    genre_counts[genre] += 1
                else:
                    genre_counts[genre] = 1

        # Average rating if available
        ratings = [um.rating for um in watched_movies if um.rating]
        avg_rating = sum(ratings) / len(ratings) if ratings else 0

        return {
            "total_watched": total_watched,
            "genres": genre_counts,
            "average_rating": avg_rating,
            "watchlist_count": len([um for um in self.user_movies if um.in_watchlist and not um.watched])
        }