#Classes
class Person:
    def __init__(self, user_id, name):
        self.user_id = user_id
        self.name = name

    def get_info(self):
        return "User ID: " + str(self.user_id) + ", Name: " + self.name
    
#User inherits from person
class User(Person):
    def __init__(self, user_id, name):
        super().__init__(user_id, name)
        self.watched_movies = [] 
        self.genres_liked = []   

    def watch(self, movie):
        self.watched_movies.append(movie)

        if movie.genre not in self.genres_liked:
            self.genres_liked.append(movie.genre)

    def rate(self, movie, score):
        movie.add_rating(score)

class Movie:
    def __init__(self, movie_id, title, genre, rating=0.0):
        self.movie_id = movie_id
        self.title = title
        self.genre = genre
        self.ratings = []
        self.avg_score = rating

    def add_rating(self, score):
        self.ratings.append(score)
        self.avg_score = sum(self.ratings) / len(self.ratings)

    def show_info(self):
        return self.title + " (" + self.genre + ") - Avg Score: " + str(round(self.avg_score, 1))


class MovieRecommendationSystem:
    def __init__(self, all_movies):
        self.all_movies = all_movies

    # Recommendation based on user's preferred genres
    def recommend_genre(self, user):
        result = []

        for m in self.all_movies:
            if m.genre in user.genres_liked and m not in user.watched_movies:
                result.append(m)
        return result

    # Recommend top-rated movies not watched by user
    def recommend_top(self, user, top_n=5):
        unseen = [m for m in self.all_movies if m not in user.watched_movies]

        for i in range(len(unseen)):
            for j in range(i + 1, len(unseen)):

                if (unseen[i].avg_score < unseen[j].avg_score) or \
                   (unseen[i].avg_score == unseen[j].avg_score and len(unseen[i].ratings) < len(unseen[j].ratings)):
                    unseen[i], unseen[j] = unseen[j], unseen[i]
        return unseen[:top_n]

    # Show recommendations for user
    def show_recommendations(self, user):
        print("\nRecommended Movies for " + user.name + ":\n")

        genre_list = self.recommend_genre(user)
        print("Movie recommendations based on Genres")
        if genre_list:
            for m in genre_list:
                print("* " + m.show_info())
        else:
            print("No movie suggestion based on genres")

        top_list = self.recommend_top(user)
        print("\nMovie recommendation based on rating (Top-Rated)")
        for m in top_list:
            print("* " + m.show_info())

    # Most watched genre for all users
    def most_watched_genre(self, users):
        genre_count = {}

        for u in users:
            for m in u.watched_movies:
                genre_count[m.genre] = genre_count.get(m.genre, 0) + 1
        
        if not genre_count:
            return None
        
        max_count = 0
        popular = ""

        for g in genre_count:
            if genre_count[g] > max_count:
                max_count = genre_count[g]
                popular = g

        return popular

    # Top trending movies
    def top_trending(self, top_n=3):

        movies_copy = self.all_movies[:]
        for i in range(len(movies_copy)):
            for j in range(i + 1, len(movies_copy)):

                if (movies_copy[i].avg_score < movies_copy[j].avg_score) or \
                   (movies_copy[i].avg_score == movies_copy[j].avg_score and len(movies_copy[i].ratings) < len(movies_copy[j].ratings)):
                    movies_copy[i], movies_copy[j] = movies_copy[j], movies_copy[i]
        return movies_copy[:top_n]

    # Total movies watched by a user
    def total_watched(self, user):
        return len(user.watched_movies)

# Initializing some movies
movies = [
    Movie(1, "Inception", "Sci-Fi"),
    Movie(2, "Titanic", "Romance"),
    Movie(3, "The Matrix", "Sci-Fi"),
    Movie(4, "The Notebook", "Romance"),
    Movie(5, "Avengers", "Action"),
    Movie(6, "Interstellar", "Sci-Fi"),
    Movie(7, "Joker", "Thriller"),
    Movie(8, "Parasite", "Thriller"),
    Movie(9, "La La Land", "Musical"),
    Movie(10, "Frozen", "Animation"),
    Movie(11, "Moana", "Animation"),
    Movie(12, "Black Panther", "Action")
]

#Initial Ratings
ratings_data = {
    1: [5, 4, 5], 2: [4, 3], 3: [5, 5], 4: [3, 4], 5: [4, 5],
    6: [5, 4], 7: [5], 8: [4, 5], 9: [4], 10: [5, 5], 11: [5, 4], 12: [4, 5, 5]
}

for m in movies:
    if m.movie_id in ratings_data:
        for r in ratings_data[m.movie_id]:
            m.add_rating(r)

#Initializing some users
users = [
    User(101, "Alice"),
    User(102, "Bob"),
    User(103, "Charlie"),
    User(104, "Diana")
]

# Users watch and rate some movies
users[0].watch(movies[0])
users[0].rate(movies[0], 5)

users[0].watch(movies[1])
users[0].rate(movies[1], 4)

users[1].watch(movies[2])
users[1].rate(movies[2], 5)

users[1].watch(movies[5])
users[1].rate(movies[5], 4)

users[2].watch(movies[3])
users[2].rate(movies[3], 4)

users[2].watch(movies[7])
users[2].rate(movies[7], 5)

users[3].watch(movies[4])
users[3].rate(movies[4], 5)

users[3].watch(movies[10])
users[3].rate(movies[10], 5) 

# Initialize the recommendation system
mrs = MovieRecommendationSystem(movies)

# Show initial recommendations
for u in users:
    mrs.show_recommendations(u)

# Show initial stats
print("\nSystem Stats")
print("Most watched genre:", mrs.most_watched_genre(users))

print("\nTop 3 trending movies:")
for m in mrs.top_trending():
    print("* " + m.show_info())

print("\nTotal movies watched per user:")
for u in users:
    print(u.name + ": " + str(mrs.total_watched(u)))

#New Watch events
print("\nNew watch and rating events")

# Users watch other movies and rate them
users[0].watch(movies[9])
users[0].rate(movies[9], 5) 

users[0].watch(movies[10])
users[0].rate(movies[10], 5) 

users[2].watch(movies[9])
users[2].rate(movies[9], 4)

users[1].rate(movies[1], 5) 

# Show updated recommendations
print("\nUpdated recommendations for Alice:")
mrs.show_recommendations(users[0])

print("\nUpdated recommendations for Bob:")
mrs.show_recommendations(users[1])

# Show updated stats
print("\nUpdated System Stats")
print("Most watched genre now:", mrs.most_watched_genre(users))

print("\nTop 3 trending movies now:")
for m in mrs.top_trending():
    print("* " + m.show_info())

print("\nTotal movies watched per user:")
for u in users:
    print(u.name + ": " + str(mrs.total_watched(u)))