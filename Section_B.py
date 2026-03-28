import streamlit as st
import pandas as pd
import numpy as np
import json
import os
from sklearn.metrics.pairwise import cosine_similarity
from PIL import Image

MOVIES_FILE = "movies.txt"
RATINGS_FILE = "ratings.txt"
USERS_FILE = "users.txt"
IMAGES_DIR = "images"

def load_movies():
    movies = []

    # Opening the movie file to read the movies available in the system
    with open(MOVIES_FILE, "r") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                movie = json.loads(line)
                if 'genre' not in movie:
                    movie['genre'] = "Unknown"
                movies.append(movie)
            except json.JSONDecodeError:
                continue
    return pd.DataFrame(movies)

# This function is used to display the movie in a flexbox like way.
def display_movie_grid(movies, columns=3, show_slider=False, user_id=None):

    if isinstance(movies, pd.DataFrame):
        movies = movies.to_dict('records')
    
    for i in range(0, len(movies), columns):
        row_movies = movies[i:i+columns]
        cols = st.columns(len(row_movies))
        
        for col, movie in zip(cols, row_movies):
            with col:

                # Making all images in a fixed size to fix alignment issues when displaying movie cards
                img_file = movie['title'].replace(" ", "_").replace(":", "") + ".png"
                img_path = os.path.join(IMAGES_DIR, img_file)
                if os.path.exists(img_path):
                    img = Image.open(img_path)
                    img = img.resize((150, 225))
                    st.image(img)
                
                # Movie info
                st.markdown(f"**{movie.get('title','Unknown')} ({movie.get('year','-')})**")
                st.markdown(f"Genre: {movie.get('genre','Unknown')}")
                st.markdown(f"Avg Rating: {movie.get('avg_rating','-')}")
                
                # Slider to provide rating to movies
                if show_slider and user_id is not None:
                    rating = st.slider("Rate", 1, 5, 3, key=f"rate_{movie['movie_id']}")
                    if st.button("Submit", key=f"btn_{movie['movie_id']}"):
                        rate_movie(user_id, movie['movie_id'], movie['title'], rating)

                st.divider()

# Saves the movies to the file
def save_movies(movies_list):
    with open(MOVIES_FILE, "w") as f:
        for movie in movies_list:
            f.write(json.dumps(movie) + "\n")

# Fetching the ratings of the movies
def load_ratings():
    if not os.path.exists(RATINGS_FILE):
        return {}  
    if os.stat(RATINGS_FILE).st_size == 0:
        return {}  
    with open(RATINGS_FILE, "r") as f:
        return json.load(f)

# Saving a rating submitted by a user
def save_ratings(ratings):
    with open(RATINGS_FILE, "w") as f:
        json.dump(ratings, f, indent=2)

# This function is called when user is rating a movie
def rate_movie(user_id, movie_id, movieName, rating):
    ratings = load_ratings()
    if user_id not in ratings:
        ratings[user_id] = {}
    ratings[user_id][str(movie_id)] = rating
    save_ratings(ratings)
    st.success(f"Rated movie {movieName}: {rating}/5")

# Fetched recommended movie based on user
def recommend_movies(user_id, movies_df, top_n=5):

    ratings = load_ratings()
    if user_id not in ratings or len(ratings[user_id]) == 0:
        st.warning("You need to rate some movies first!")
        return pd.DataFrame()
    
    rated_ids = [int(mid) for mid in ratings[user_id].keys()]
    unrated_movies = movies_df[~movies_df['movie_id'].isin(rated_ids)].copy()
    
    if unrated_movies.empty:
        st.info("All movies were rated.")
        return pd.DataFrame()
    
    user_vector = np.zeros(len(movies_df))
    for mid_str, r in ratings[user_id].items():
        idx = movies_df.index[movies_df['movie_id']==int(mid_str)][0]
        user_vector[idx] = r
    
    genre_matrix = pd.get_dummies(movies_df['genre'])
    similarity = cosine_similarity(genre_matrix)
    
    scores = similarity.dot(user_vector)
    unrated_movies['score'] = [scores[idx] for idx in unrated_movies.index]
    
    recommendations = unrated_movies.sort_values('score', ascending=False).head(top_n)
    return recommendations

# Function to searcg for movies based on title, genre and year
def search_movies(movies_df, keyword=None, genre=None, year=None):
    results = movies_df.copy()
    
    if keyword and keyword.strip() != "":
        results = results[results['title'].str.contains(keyword, case=False, na=False)]
    
    if genre and genre.strip() != "":
        results = results[results['genre'].str.contains(genre, case=False, na=False)]
    
    if year:
        results = results[results['year'] == year]
    
    return results

# Display trending movie s
def trending_movies(movies_df):
    ratings = load_ratings()
    movie_counts = {}

    for user_ratings in ratings.values():
        for mid in user_ratings.keys():
            movie_counts[mid] = movie_counts.get(mid, 0) + 1

    trending = movies_df.copy()
    trending['views'] = trending['movie_id'].apply(lambda x: movie_counts.get(str(x), 0))

    trending = trending[trending['views'] > 0]

    return trending.sort_values(by='views', ascending=False).head(5)

# Function to find the most popular genres
def popular_genres():
    ratings = load_ratings()
    genre_count = {}
    movies_df = load_movies()
    for user_ratings in ratings.values():
        for mid in user_ratings.keys():
            genre = movies_df[movies_df['movie_id']==int(mid)]['genre'].values[0]
            genre_count[genre] = genre_count.get(genre, 0) + 1
    return genre_count

# The code for the streamlit app starts here
st.title("🎬 Movie Recommendation System")

mode = st.sidebar.selectbox("Select User Type", ["User", "Admin"])

if mode == "User":
    user_id = st.sidebar.text_input("Enter User ID", "user1")
    movies_df = load_movies()
    ratings = load_ratings()
    
    tabs = st.tabs(["Watch & Rate Movies", "Recommendations", "Search Movies", "User Dashboard"])
    
    # This tab is the Watch & Rate Movies Tab
    with tabs[0]:
        st.subheader("Watch & Rate Movies")
        display_movie_grid(movies_df, columns=3, show_slider=True, user_id=user_id)
    
    # Recommendations Tab
    with tabs[1]:
        st.subheader("Top Recommendations")
        
        all_recs = recommend_movies(user_id, movies_df, top_n=len(movies_df))
        
        if all_recs.empty:
            st.info("Rate some movies first.")
        else:
            max_rec = len(all_recs)
            top_n = st.number_input(
                "Number of Recommendations",
                min_value=1,
                max_value=max_rec,
                value=min(5, max_rec)
            )
            recs = all_recs.head(top_n)
            display_movie_grid(recs, columns=3)
    
    # Search Movie Tab
    with tabs[2]:
        st.subheader("Search Movies")
        
        keyword = st.text_input("Search by Title")
        genre_list = [""] + sorted(movies_df['genre'].unique().tolist())
        genre = st.selectbox("Search by Genre", genre_list)
        
        year_input = st.text_input("Search by Year")
        year = int(year_input) if year_input.isdigit() else None

        if st.button("Search"):
            results = search_movies(movies_df, keyword=keyword, genre=genre, year=year)
            if results.empty:
                st.info("No movies found.")
            else:
                display_movie_grid(results, columns=3)
    
    # User Dashboard Tab
    with tabs[3]:
        st.subheader("User Dashboard")

        # Displaying recommended movies to user
        st.markdown("### Recommended For You")
        recs = recommend_movies(user_id, movies_df, top_n=5)

        if recs.empty:
            st.info("Rate some movies to get personalized recommendations.")
        else:
            display_movie_grid(recs, columns=3)

        # Displays Watch history and ratings user gave to movies
        st.markdown("### Watch History & Ratings")


        ratings = load_ratings()

        if user_id in ratings and ratings[user_id]:
            user_movies = []

            for mid, r in ratings[user_id].items():
                movie_row = movies_df[movies_df['movie_id']==int(mid)]
                if not movie_row.empty:
                    movie = movie_row.iloc[0]
                    user_movies.append({
                        "title": movie['title'],
                        "genre": movie['genre'],
                        "year": movie['year'],
                        "rating": r
                    })

            st.table(pd.DataFrame(user_movies))
        else:
            st.info("No movies watched yet.")

        st.divider()

        # Shows trending movies
        st.markdown("### Trending Movies")

        trending = trending_movies(movies_df)

        if not trending.empty:
            st.bar_chart(trending.set_index('title')['views'])
            display_movie_grid(trending, columns=3)
        else:
            st.info("No trending data yet.")

        # Shows popular genres
        st.markdown("### Popular Genres")

        genres = popular_genres()

        if genres:
            st.bar_chart(pd.Series(genres))
        else:
            st.info("No genre data yet.")

        # Shows Rating distribution
        st.markdown("### Your Rating Distribution")

        if user_id in ratings and len(ratings[user_id]) > 0:
            rating_values = list(ratings[user_id].values())
            rating_series = pd.Series(rating_values).value_counts().sort_index()
            st.bar_chart(rating_series)
        else:
            st.info("No ratings yet.")

        # Shows top rated movies
        st.markdown("### Top Rated Movies")

        top_rated = movies_df.sort_values(by='avg_rating', ascending=False).head(5)
        st.bar_chart(top_rated.set_index('title')['avg_rating'])

# The part below is for the admin panel
elif mode == "Admin":
    key = st.sidebar.text_input("Enter Admin Password", type="password")

    if key == "admin123":
        st.subheader("🛠 Admin Console")

        movies_df = load_movies()
        ratings = load_ratings()

        admin_tabs = st.tabs([
            "Movie Management",
            "Engagement Analytics"
        ])

        # This first tab allows admin to Add / Update / Delete movies
        with admin_tabs[0]:

            # add movie section
            st.markdown("#### Add Movie")
            new_title = st.text_input("Movie Title")
            new_genre = st.text_input("Genre")
            new_year = st.number_input("Year", 1900, 2025, 2020)
            new_rating = st.number_input("Avg Rating", 0.0, 5.0, 4.0)

            if st.button("Add Movie"):
                new_id = int(movies_df['movie_id'].max()) + 1
                new_movie = {
                    "movie_id": new_id,
                    "title": new_title,
                    "genre": new_genre,
                    "year": new_year,
                    "avg_rating": new_rating
                }
                movies_df = pd.concat([movies_df, pd.DataFrame([new_movie])], ignore_index=True)
                save_movies(movies_df.to_dict('records'))
                st.success("Movie added successfully!")

            st.divider()

            # update movie section
            st.markdown("#### Edit Movie")

            movie_titles = movies_df['title'].tolist()

            selected_title = st.selectbox(
                "Select Movie to Edit",
                movie_titles,
                key="edit_movie_select"
            )

            movie_row = movies_df[movies_df['title'] == selected_title].iloc[0]

            if "prev_selected_movie" not in st.session_state:
                st.session_state.prev_selected_movie = selected_title

            if st.session_state.prev_selected_movie != selected_title:
                st.session_state.edit_genre = movie_row['genre']
                st.session_state.edit_year = int(movie_row['year'])
                st.session_state.edit_rating = float(movie_row['avg_rating'])
                st.session_state.prev_selected_movie = selected_title

            if "edit_genre" not in st.session_state:
                st.session_state.edit_genre = movie_row['genre']
            if "edit_year" not in st.session_state:
                st.session_state.edit_year = int(movie_row['year'])
            if "edit_rating" not in st.session_state:
                st.session_state.edit_rating = float(movie_row['avg_rating'])

            edit_genre = st.text_input("Genre", key="edit_genre")
            edit_year = st.number_input("Year", 1900, 2025, key="edit_year")
            edit_rating = st.number_input("Avg Rating", 0.0, 5.0, key="edit_rating")

            if st.button("Update Movie"):
                movies_df.loc[movies_df['title'] == selected_title, ['genre', 'year', 'avg_rating']] = [
                    edit_genre, edit_year, edit_rating
                ]
                save_movies(movies_df.to_dict('records'))

                st.session_state.update_success = True

                st.rerun()

            if st.session_state.get("update_success"):
                st.success(" Movie updated successfully!")
                st.session_state.update_success = False  # reset

            # Delete Movie Section
            st.markdown("#### 🗑 Delete Movie")
            delete_title = st.selectbox("Select Movie to Delete", movie_titles, key="delete")

            if st.button("Delete Movie"):
                movies_df = movies_df[movies_df['title'] != delete_title]
                save_movies(movies_df.to_dict('records'))
                st.warning("Movie deleted!")

        # Engagement Analytics Tab
        with admin_tabs[1]:

            # Most Watched Movies Part
            st.markdown("#### Most Watched Movies")
            movie_counts = {}

            for user_ratings in ratings.values():
                for mid in user_ratings.keys():
                    movie_counts[mid] = movie_counts.get(mid, 0) + 1

            views_df = movies_df.copy()
            views_df['views'] = views_df['movie_id'].apply(lambda x: movie_counts.get(str(x), 0))

            views_df = views_df[views_df['views'] > 0]

            if not views_df.empty:
                st.bar_chart(views_df.set_index('title')['views'])
            else:
                st.info("No viewing data yet.")

            # Top Active Users Part
            st.markdown("#### Top Active Users")

            user_activity = {}
            for user, user_ratings in ratings.items():
                user_activity[user] = len(user_ratings)

            if user_activity:
                st.bar_chart(pd.Series(user_activity))
            else:
                st.info("No user activity yet.")

            # Trending Movies part
            st.markdown("#### Trending Movies")

            trending_df = movies_df.copy()
            trending_df['views'] = trending_df['movie_id'].apply(lambda x: movie_counts.get(str(x), 0))

            trending_df = trending_df[trending_df['views'] > 0]

            if not trending_df.empty:

                trending_df['score'] = trending_df['views'] * trending_df['avg_rating']

                top_trending = trending_df.sort_values(by='score', ascending=False).head(5)

                st.bar_chart(top_trending.set_index('title')['score'])
            else:
                st.info("No trending data yet.")
    else:
        st.warning("Invalid Admin Key")