# models/user_movies.py
from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from models import Base


class UserMovie(Base):
    __tablename__ = 'user_movies'
    id = Column("pk_user_movies", Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.pk_users'), nullable=False)
    movie_id = Column(Integer, ForeignKey('movies.pk_movies'), nullable=False)
    in_watchlist = Column(Boolean, default=False)
    watched = Column(Boolean, default=False)
    date_added = Column(DateTime, default=datetime.now())
    date_watched = Column(DateTime, nullable=True)
    rating = Column(Integer, nullable=True)  # Optional personal rating (1-5)
    notes = Column(String(1000), nullable=True)  # Optional personal notes

    # Relationships
    user = relationship("User", back_populates="user_movies")
    movie = relationship("Movies", back_populates="user_movies")

    def __init__(self, user_id, movie_id, in_watchlist=False, watched=False,
                 rating=None, notes=None, date_watched=None):
        self.user_id = user_id
        self.movie_id = movie_id
        self.in_watchlist = in_watchlist
        self.watched = watched
        self.rating = rating
        self.notes = notes
        self.date_watched = date_watched