from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_swagger_ui import get_swaggerui_blueprint
from sqlalchemy.exc import IntegrityError
from datetime import datetime
from models.__init__ import Session
from models.user import User
from models.movies import Movies
from models.user_movies import UserMovie

app = Flask(__name__)
CORS(app)  # Habilita CORS para todas as rotas

# Swagger configuration
SWAGGER_URL = '/api/docs'
API_URL = 'http://localhost:5000/static/swagger.json'
swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={
        'app_name': "Movie Dashboard API"
    }
)
app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)


# Rota Home
@app.route('/')
def home():
    """Home route showing API information"""
    return jsonify({
        "api": "Movie Dashboard API",
        "version": "1.0.0",
        "description": "A Personal Movie Tracking Dashboard API",
        "documentation": f"{request.url_root.rstrip('/')}{SWAGGER_URL}"
    }), 200


# Rotas User
@app.route('/api/users', methods=['GET'])
def get_all_users():
    """Get all users from the database"""
    session = Session()
    users = session.query(User).all()
    users_list = [{"id": user.id, "username": user.username} for user in users]
    session.close()
    return jsonify(users_list), 200


@app.route('/api/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    """Get a specific user by ID"""
    session = Session()
    user = session.query(User).filter(User.id == user_id).first()

    if user:
        # Get user stats
        stats = user.get_stats()

        user_data = {
            "id": user.id,
            "username": user.username,
            "created": user.created.isoformat() if user.created else None,
            "updated": user.updated.isoformat() if user.updated else None,
            "watchlist_count": stats["watchlist_count"],
            "watched_count": stats["total_watched"],
            "stats": stats
        }
        session.close()
        return jsonify(user_data), 200

    session.close()
    return jsonify({"message": "User not found"}), 404


@app.route('/api/users', methods=['POST'])
def create_user():
    """Create a new user"""
    data = request.get_json()

    if not data or not data.get('username'):
        return jsonify({"message": "Username is required"}), 400

    session = Session()

    try:
        new_user = User(username=data['username'])
        session.add(new_user)
        session.commit()

        user_data = {
            "id": new_user.id,
            "username": new_user.username,
            "created": new_user.created.isoformat() if new_user.created else None
        }

        session.close()
        return jsonify(user_data), 201

    except IntegrityError:
        session.rollback()
        session.close()
        return jsonify({"message": "Username already exists"}), 409

    except Exception as e:
        session.rollback()
        session.close()
        return jsonify({"message": f"Error creating user: {str(e)}"}), 500


@app.route('/api/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    """Delete a user by ID"""
    session = Session()
    user = session.query(User).filter(User.id == user_id).first()

    if not user:
        session.close()
        return jsonify({"message": "User not found"}), 404

    try:
        session.delete(user)
        session.commit()
        session.close()
        return jsonify({"message": f"User {user_id} deleted successfully"}), 200

    except Exception as e:
        session.rollback()
        session.close()
        return jsonify({"message": f"Error deleting user: {str(e)}"}), 500


# Rotas Movie
@app.route('/api/movies', methods=['GET'])
def get_all_movies():
    """Get all movies added by the requesting user"""
    # Get the user_id from query parameter
    user_id = request.args.get('user_id')

    if not user_id:
        return jsonify({"message": "user_id parameter is required"}), 400

    session = Session()
    # Only return movies added by this user
    movies = session.query(Movies).filter(Movies.user_id == user_id).all()

    movies_list = []
    for movie in movies:
        movies_list.append({
            "id": movie.id,
            "title": movie.title,
            "genre": movie.genre,
            "director": movie.director,
            "year": movie.year,
            "description": movie.description,
            "cover": movie.cover
        })

    session.close()
    return jsonify(movies_list), 200


@app.route('/api/movies/<int:movie_id>', methods=['GET'])
def get_movie(movie_id):
    """Get a specific movie by ID"""
    # Get the user_id from query parameter to verify ownership
    user_id = request.args.get('user_id')

    if not user_id:
        return jsonify({"message": "user_id parameter is required"}), 400

    session = Session()
    movie = session.query(Movies).filter(Movies.id == movie_id).first()

    if not movie:
        session.close()
        return jsonify({"message": "Movie not found"}), 404

    # Check if the movie belongs to the user
    if str(movie.user_id) != user_id:
        session.close()
        return jsonify({"message": "Unauthorized access to this movie"}), 403

    movie_data = {
        "id": movie.id,
        "title": movie.title,
        "genre": movie.genre,
        "director": movie.director,
        "year": movie.year,
        "description": movie.description,
        "cover": movie.cover,
        "genres": movie.return_genres()
    }
    session.close()
    return jsonify(movie_data), 200


@app.route('/api/movies', methods=['POST'])
def create_movie():
    """Create a new movie and add to watchlist"""
    data = request.get_json()

    # Validate required fields
    required_fields = ['title', 'genre', 'director', 'year', 'description', 'user_id']
    for field in required_fields:
        if field not in data:
            return jsonify({"message": f"Missing required field: {field}"}), 400

    session = Session()

    # Check if user exists
    user = session.query(User).filter(User.id == data['user_id']).first()
    if not user:
        session.close()
        return jsonify({"message": "User not found"}), 404

    try:
        # Create the movie
        new_movie = Movies(
            title=data['title'],
            genre=data['genre'],
            director=data['director'],
            year=data['year'],
            description=data['description'],
            cover=data.get('cover'),  # Optional field
            user_id=data['user_id']
        )

        session.add(new_movie)
        session.flush()  # This assigns an ID to new_movie

        # Automatically add to watchlist
        user_movie = UserMovie(
            user_id=data['user_id'],
            movie_id=new_movie.id,
            in_watchlist=True,
            watched=False
        )

        session.add(user_movie)
        session.commit()

        movie_data = {
            "id": new_movie.id,
            "title": new_movie.title,
            "genre": new_movie.genre,
            "director": new_movie.director,
            "year": new_movie.year,
            "description": new_movie.description,
            "cover": new_movie.cover,
            "watchlist_item_id": user_movie.id
        }

        session.close()
        return jsonify(movie_data), 201

    except Exception as e:
        session.rollback()
        session.close()
        return jsonify({"message": f"Error creating movie: {str(e)}"}), 500


@app.route('/api/movies/<int:movie_id>', methods=['DELETE'])
def delete_movie(movie_id):
    user_id = request.args.get('user_id')
    if not user_id:
        return jsonify({'message': 'user_id is required'}), 400
    session = Session()
    movie = session.query(Movies).filter(Movies.id == movie_id).first()
    if not movie:
        session.close()
        return jsonify({'message': 'Movie not found'}), 404
    if str(movie.user_id) != user_id:
        session.close()
        return jsonify({'message': 'Unauthorized to delete this movie'}), 403
    try:
        session.delete(movie)
        session.commit()
        session.close()
        return jsonify({'message': f'Movie {movie_id} deleted successfully'}), 200
    except Exception as e:
        session.rollback()
        session.close()
        return jsonify({'message': f'Error deleting movie: {str(e)}'}), 500
    """Delete a movie by ID"""
    session = Session()
    movie = session.query(Movies).filter(Movies.id == movie_id).first()

    if not movie:
        session.close()
        return jsonify({"message": "Movie not found"}), 404

    try:
        session.delete(movie)
        session.commit()
        session.close()
        return jsonify({"message": f"Movie {movie_id} deleted successfully"}), 200

    except Exception as e:
        session.rollback()
        session.close()
        return jsonify({"message": f"Error deleting movie: {str(e)}"}), 500


# Watchlist routes
@app.route('/api/users/<int:user_id>/watchlist', methods=['GET'])
def get_user_watchlist(user_id):
    """Get a user's watchlist"""
    session = Session()
    user = session.query(User).filter(User.id == user_id).first()

    if not user:
        session.close()
        return jsonify({"message": "User not found"}), 404

    # Get user's watchlist items
    watchlist_items = session.query(UserMovie).filter(
        UserMovie.user_id == user_id,
        UserMovie.in_watchlist == True,
        UserMovie.watched == False
    ).all()

    watchlist = []
    for item in watchlist_items:
        movie = session.query(Movies).filter(Movies.id == item.movie_id).first()

        watchlist.append({
            "id": item.id,
            "movie_id": movie.id,
            "title": movie.title,
            "director": movie.director,
            "year": movie.year,
            "genre": movie.genre,
            "cover": movie.cover,
            "date_added": item.date_added.isoformat() if item.date_added else None
        })

    session.close()
    return jsonify(watchlist), 200


@app.route('/api/users/<int:user_id>/watchlist', methods=['POST'])
def add_to_watchlist(user_id):
    """Add a movie to user's watchlist"""
    data = request.get_json()

    if not data or not data.get('movie_id'):
        return jsonify({"message": "Movie ID is required"}), 400

    movie_id = data.get('movie_id')

    session = Session()

    # Check if user exists
    user = session.query(User).filter(User.id == user_id).first()
    if not user:
        session.close()
        return jsonify({"message": "User not found"}), 404

    # Check if movie exists
    movie = session.query(Movies).filter(Movies.id == movie_id).first()
    if not movie:
        session.close()
        return jsonify({"message": "Movie not found"}), 404

    # Check if movie is already in watchlist
    existing = session.query(UserMovie).filter(
        UserMovie.user_id == user_id,
        UserMovie.movie_id == movie_id
    ).first()

    try:
        if existing:
            # Update existing entry
            existing.in_watchlist = True
            existing.date_added = datetime.now()
        else:
            # Create new entry
            user_movie = UserMovie(
                user_id=user_id,
                movie_id=movie_id,
                in_watchlist=True
            )
            session.add(user_movie)

        session.commit()
        session.close()
        return jsonify({"message": "Movie added to watchlist"}), 201

    except Exception as e:
        session.rollback()
        session.close()
        return jsonify({"message": f"Error adding to watchlist: {str(e)}"}), 500


@app.route('/api/users/<int:user_id>/watchlist/<int:item_id>', methods=['DELETE'])
def remove_from_watchlist(user_id, item_id):
    """Remove a movie from user's watchlist"""
    session = Session()

    # Find the watchlist item
    watchlist_item = session.query(UserMovie).filter(
        UserMovie.id == item_id,
        UserMovie.user_id == user_id,
        UserMovie.in_watchlist == True
    ).first()

    if not watchlist_item:
        session.close()
        return jsonify({"message": "Watchlist item not found"}), 404

    try:
        watchlist_item.in_watchlist = False
        session.commit()
        session.close()
        return jsonify({"message": "Movie removed from watchlist"}), 200

    except Exception as e:
        session.rollback()
        session.close()
        return jsonify({"message": f"Error removing from watchlist: {str(e)}"}), 500


# Watched movies routes
@app.route('/api/users/<int:user_id>/watched', methods=['GET'])
def get_user_watched(user_id):
    """Get a user's watched movies"""
    session = Session()
    user = session.query(User).filter(User.id == user_id).first()

    if not user:
        session.close()
        return jsonify({"message": "User not found"}), 404

    # Get user's watched items
    watched_items = session.query(UserMovie).filter(
        UserMovie.user_id == user_id,
        UserMovie.watched == True
    ).all()

    watched = []
    for item in watched_items:
        movie = session.query(Movies).filter(Movies.id == item.movie_id).first()

        watched.append({
            "id": item.id,
            "movie_id": movie.id,
            "title": movie.title,
            "director": movie.director,
            "year": movie.year,
            "genre": movie.genre,
            "cover": movie.cover,
            "date_watched": item.date_watched.isoformat() if item.date_watched else None,
            "rating": item.rating,
            "notes": item.notes
        })

    session.close()
    return jsonify(watched), 200


@app.route('/api/users/<int:user_id>/watched', methods=['POST'])
def mark_as_watched(user_id):
    """Mark a movie as watched"""
    data = request.get_json()

    if not data or not data.get('movie_id'):
        return jsonify({"message": "Movie ID is required"}), 400

    movie_id = data.get('movie_id')
    rating = data.get('rating')
    notes = data.get('notes')
    date_watched = data.get('date_watched', datetime.now().isoformat())

    # Convert date_watched to datetime object if it's a string
    if isinstance(date_watched, str):
        try:
            date_watched = datetime.fromisoformat(date_watched)
        except ValueError:
            date_watched = datetime.now()

    session = Session()

    # Check if user exists
    user = session.query(User).filter(User.id == user_id).first()
    if not user:
        session.close()
        return jsonify({"message": "User not found"}), 404

    # Check if movie exists
    movie = session.query(Movies).filter(Movies.id == movie_id).first()
    if not movie:
        session.close()
        return jsonify({"message": "Movie not found"}), 404

    # Check if movie is already in user's movies
    existing = session.query(UserMovie).filter(
        UserMovie.user_id == user_id,
        UserMovie.movie_id == movie_id
    ).first()

    try:
        if existing:
            # Update existing entry
            existing.watched = True
            existing.date_watched = date_watched
            existing.rating = rating
            existing.notes = notes
        else:
            # Create new entry
            user_movie = UserMovie(
                user_id=user_id,
                movie_id=movie_id,
                watched=True,
                date_watched=date_watched,
                rating=rating,
                notes=notes
            )
            session.add(user_movie)

        session.commit()
        session.close()
        return jsonify({"message": "Movie marked as watched"}), 201

    except Exception as e:
        session.rollback()
        session.close()
        return jsonify({"message": f"Error marking as watched: {str(e)}"}), 500


@app.route('/api/users/<int:user_id>/watched/<int:item_id>', methods=['DELETE'])
def remove_from_watched(user_id, item_id):
    """Remove a movie from user's watched list"""
    session = Session()

    # Find the watched item
    watched_item = session.query(UserMovie).filter(
        UserMovie.id == item_id,
        UserMovie.user_id == user_id,
        UserMovie.watched == True
    ).first()

    if not watched_item:
        session.close()
        return jsonify({"message": "Watched item not found"}), 404

    try:
        watched_item.watched = False
        watched_item.date_watched = None
        watched_item.rating = None
        watched_item.notes = None
        session.commit()
        session.close()
        return jsonify({"message": "Movie removed from watched list"}), 200

    except Exception as e:
        session.rollback()
        session.close()
        return jsonify({"message": f"Error removing from watched list: {str(e)}"}), 500


# Stats route
@app.route('/api/users/<int:user_id>/stats', methods=['GET'])
def get_user_stats(user_id):
    """Get user's movie statistics"""
    session = Session()
    user = session.query(User).filter(User.id == user_id).first()

    if not user:
        session.close()
        return jsonify({"message": "User not found"}), 404

    stats = user.get_stats()

    # Get recently watched movies (last 5)
    recently_watched = session.query(UserMovie).filter(
        UserMovie.user_id == user_id,
        UserMovie.watched == True
    ).order_by(UserMovie.date_watched.desc()).limit(5).all()

    recent_movies = []
    for item in recently_watched:
        movie = session.query(Movies).filter(Movies.id == item.movie_id).first()
        recent_movies.append({
            "id": movie.id,
            "title": movie.title,
            "date_watched": item.date_watched.isoformat() if item.date_watched else None,
            "rating": item.rating
        })

    # Add to stats
    stats["recently_watched"] = recent_movies

    session.close()
    return jsonify(stats), 200


if __name__ == '__main__':
    # Run the Flask application
    app.run(debug=True, port=5000)