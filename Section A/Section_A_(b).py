#Classes
class Person:
    def __init__(self, user_id, name):
        self.user_id = user_id
        self.name = name

    def get_details(self):
        return "User ID: " + str(self.user_id) + ", Name: " + self.name

#User inherits from Person
class User(Person):
    def __init__(self, user_id, name):
        super().__init__(user_id, name)

        self.viewing_history = []
        self.preferences = []

    def watch_movie(self, movie):
        self.viewing_history.append(movie)

        if movie.genre not in self.preferences:
            self.preferences.append(movie.genre)

    def rate_movie(self, movie, rating):
        movie.update_rating(rating)

class Movie:
    def __init__(self, movie_id, title, genre, rating=0.0):
        self.movie_id = movie_id
        self.title = title
        self.genre = genre
        self.ratings = []
        self.avg_rating = rating

    def update_rating(self, rating):
        self.ratings.append(rating)
        total = 0

        for r in self.ratings:
            total += r

        self.avg_rating = total / len(self.ratings)

    def get_details(self):
        return self.title + " (" + self.genre + ") - Avg Rating: " + str(round(self.avg_rating, 1))


class MovieRecommendationSystem:
    def __init__(self, movie_list):
        self.movies = movie_list

    def recommend_by_genre(self, user):
        recommended = []

        for movie in self.movies:
            if movie.genre in user.preferences:
                if movie not in user.viewing_history:
                    recommended.append(movie)

        return recommended

    def recommend_by_rating(self, user, top_n=5):
        unseen_movies = []

        for movie in self.movies:
            if movie not in user.viewing_history:
                unseen_movies.append(movie)

        for i in range(len(unseen_movies)):
            for j in range(i+1, len(unseen_movies)):
                if unseen_movies[i].avg_rating < unseen_movies[j].avg_rating:
                    temp = unseen_movies[i]
                    unseen_movies[i] = unseen_movies[j]
                    unseen_movies[j] = temp

        recommended = []
        count = 0

        for m in unseen_movies:
            recommended.append(m)
            count += 1

            if count >= top_n:
                break

        return recommended

    def display_recommendations(self, user):
        print("\nRecommended Movies for " + user.name + ":\n")

        genre_based = self.recommend_by_genre(user)
        print("Movie recommendations based on Genres")

        if len(genre_based) > 0:
            for movie in genre_based:
                print("- " + movie.get_details())
        else:
            print("No movie suggestion based on genres")

        rating_based = self.recommend_by_rating(user)
        print("\nMovie recommendation based on rating (Top-Rated)")

        for movie in rating_based:
            print("- " + movie.get_details())

#Initializing movies
movie1 = Movie(1, "Inception", "Sci-Fi")
movie2 = Movie(2, "Titanic", "Romance")
movie3 = Movie(3, "The Matrix", "Sci-Fi")
movie4 = Movie(4, "The Notebook", "Romance")
movie5 = Movie(5, "Avengers", "Action")
movie6 = Movie(6, "Interstellar", "Sci-Fi")
movie7 = Movie(7, "Joker", "Thriller")
movie8 = Movie(8, "Parasite", "Thriller")
movie9 = Movie(9, "La La Land", "Musical")
movie10 = Movie(10, "Frozen", "Animation")

all_movies = [movie1, movie2, movie3, movie4, movie5, movie6, movie7, movie8, movie9, movie10]

ratings_dict = {
    1: [5, 4, 5],
    2: [4, 3],
    3: [5, 5],
    4: [3, 4],
    5: [4, 5],
    6: [5, 4],
    7: [5],
    8: [4, 5],
    9: [4],
    10: [5, 5]
}

for m in all_movies:
    if m.movie_id in ratings_dict:
        for r in ratings_dict[m.movie_id]:
            m.update_rating(r)

user1 = User(101, "Alice")
user2 = User(102, "Bob")
user3 = User(103, "Charlie")
user4 = User(104, "Diana")

all_users = [user1, user2, user3, user4]

#simulating users watching movies
user1.watch_movie(movie1)
user1.rate_movie(movie1, 5)

user1.watch_movie(movie2)
user1.rate_movie(movie2, 4)

user2.watch_movie(movie3)
user2.rate_movie(movie3, 5)

user2.watch_movie(movie6)
user2.rate_movie(movie6, 4)

user3.watch_movie(movie4)
user3.rate_movie(movie4, 4)

user3.watch_movie(movie8)
user3.rate_movie(movie8, 5)

user4.watch_movie(movie5)
user4.rate_movie(movie5, 5)

user4.watch_movie(movie10)
user4.rate_movie(movie10, 5)

mrs = MovieRecommendationSystem(all_movies)

for u in all_users:
    mrs.display_recommendations(u)