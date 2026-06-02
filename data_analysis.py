import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Set style for charts
sns.set_theme(style="whitegrid")

#== Load data ===
# CHANGE HERE depending on which dataset you want to analyze - comment/uncomment the appropriate lines

# all movies data
df = pd.read_csv('processed_data/movies_processed.csv')
OUTPUT_DIR = "analysis/charts/charts_all_movies"

# top 1000 movies data
#df = pd.read_csv('processed_data/top_1000_movies.csv')
#OUTPUT_DIR = "analysis/charts/charts_top_1000_movies"

# Remove any remaining missing values
df = df.dropna(subset=['averageRating', 'runtimeMinutes', 'startYear', 'numVotes', 'directors', 'genres'])

# Filter out movies with unrealistic runtimes (e.g., > 500 minutes)
df = df[df['runtimeMinutes'] < 500]

# === 1. Rating distribution ===
plt.figure(figsize=(10, 6))
sns.histplot(df['averageRating'], bins=20, kde=True, color='royalblue')
plt.title('Rating distribution')
plt.xlabel('Average Rating')
plt.ylabel('Number of Movies')
plt.savefig(f"{OUTPUT_DIR}/1_rating_distribution.png", bbox_inches='tight', dpi=300)
plt.close()

# === 2. Movie runtime distribution ===
plt.figure(figsize=(10, 6))
sns.histplot(df['runtimeMinutes'], bins=30, kde=True, color='darkorange')
plt.title('Movie Runtime Distribution')
plt.xlabel('Runtime (minutes)')
plt.ylabel('Number of Movies')
plt.savefig(f"{OUTPUT_DIR}/2_runtime_distribution.png", bbox_inches='tight', dpi=300)
plt.close()


print(f"Average runtime: {df['runtimeMinutes'].mean():.2f} minutes")
print(f"Median runtime: {df['runtimeMinutes'].median():.0f} minutes")
print(f"Longest movie in the list: {df['runtimeMinutes'].max():.0f} minutes")

# === 3. Genre analysis ===
# Since genres in the column are separated by commas (e.g., 'Action,Crime,Drama'), we use explode() to create a separate row for each genre.
df_genres = df.assign(single_genre=df['genres'].str.split(',')).explode('single_genre')
genre_counts = df_genres['single_genre'].value_counts()

plt.figure(figsize=(12, 6))
sns.barplot(x=genre_counts.values, y=genre_counts.index, hue=genre_counts.index, palette='viridis', legend=False)
plt.title('Most common genres')
plt.xlabel('Number of occurrences')
plt.ylabel('Genre')
plt.savefig(f"{OUTPUT_DIR}/3_genre_analysis.png", bbox_inches='tight', dpi=300)
plt.close()

# Genres with the most votes
top_voted_genres = df_genres.groupby('single_genre')['numVotes'].sum().sort_values(ascending=False).head(5)
print("Genres with the highest total votes:")
print(top_voted_genres)

plt.figure(figsize=(10, 6))
sns.barplot(x=top_voted_genres.values, y=top_voted_genres.index, hue=top_voted_genres.index, palette='magma', legend=False)
plt.title('Genres with the highest total votes')
plt.xlabel('Total Number of Votes')
plt.ylabel('Genre')
plt.ticklabel_format(style='plain', axis='x')
plt.savefig(f"{OUTPUT_DIR}/4_genres_by_votes.png", bbox_inches='tight', dpi=300)
plt.close()

# Average rating by genre (only for genres with at least 10 movies to avoid skewed results)
genre_stats = df_genres.groupby('single_genre').agg(
    mean_rating=('averageRating', 'mean'),
    count=('averageRating', 'count')
)
top_rated_genres = genre_stats[genre_stats['count'] >= 10].sort_values(by='mean_rating', ascending=False)
print("\nTop 5 highest rated genres (min. 10 movies):")
print(top_rated_genres[['mean_rating', 'count']].head(5))

plt.figure(figsize=(12, 6))
sns.barplot(x=top_rated_genres['mean_rating'], y=top_rated_genres.index, hue=top_rated_genres.index, palette='mako', legend=False)
plt.title('Genres with the highest average rating (min. 10 movies)')
plt.xlabel('Average Rating')
plt.ylabel('Genre')
plt.savefig(f"{OUTPUT_DIR}/5_top_rated_genres.png", bbox_inches='tight', dpi=300)
plt.close()

# === 4. Golden age of cinema ===
# Calculate decade (e.g., 1994 -> 1990)
df['decade'] = (df['startYear'] // 10) * 10
decade_ratings = df.groupby('decade').agg(
    mean_rating=('averageRating', 'mean'),
    count=('averageRating', 'count')
).reset_index()

plt.figure(figsize=(10, 6))
sns.lineplot(data=decade_ratings, x='decade', y='mean_rating', marker='o')
plt.title('Average rating by decade')
plt.xlabel('Decade')
plt.ylabel('Average Rating')
plt.savefig(f"{OUTPUT_DIR}/6_decade_ratings.png", bbox_inches='tight', dpi=300)
plt.close()

#=== 5. Popularity vs. rating ===
plt.figure(figsize=(10, 6))
sns.scatterplot(data=df, x='numVotes', y='averageRating', alpha=0.6)
plt.title('Popularity vs. Rating')
plt.xlabel('Number of Votes')
plt.ylabel('Average Rating')
plt.ticklabel_format(style='plain', axis='x')
plt.xscale('log')  # Log scale for better visibility
plt.savefig(f"{OUTPUT_DIR}/7_popularity_vs_rating.png", bbox_inches='tight', dpi=300)
plt.close()

correlation = df['numVotes'].corr(df['averageRating'])
print(f"Correlation between number of votes and average rating: {correlation:.2f}")

# === 6. Directors ranking ===
# Explode directors into separate rows
df_directors = df.assign(single_director=df['directors'].astype(str).str.split(', ')).explode('single_director')

# Find the most common genre for each director
# Explode genres for each director
df_dir_gen = df_directors.assign(single_genre=df_directors['genres'].astype(str).str.split(',')).explode('single_genre')
# Get the most common genre for each director
genre_counts = df_dir_gen.groupby(['single_director', 'single_genre']).size().reset_index(name='count')
# Find the maximum number of movies in a single genre for each director
genre_counts['max_count'] = genre_counts.groupby('single_director')['count'].transform('max')
# Filter only the genres that match that maximum count (this preserves ties)
top_genres = genre_counts[genre_counts['count'] == genre_counts['max_count']]
# Group by director again and join tying genres with a slash (e.g., "Comedy / Drama")
dominant_genre = top_genres.groupby('single_director')['single_genre'].apply(lambda x: ' / '.join(sorted(x))).reset_index(name='top_genre')

# Calculate director statistics
director_stats = df_directors.groupby('single_director').agg(
    mean_rating=('averageRating', 'mean'),
    movie_count=('averageRating', 'count'),
    mean_runtime=('runtimeMinutes', 'mean')
).reset_index()

# Merge dominant genre back into director stats
director_stats = director_stats.merge(dominant_genre, on='single_director', how='left')

# Filter directors with at least 10 movies for a more meaningful ranking
filtered_directors = director_stats[director_stats['movie_count'] >= 10]

# Ranking 1: Best rated directors
top_rated_directors = filtered_directors.sort_values(by='mean_rating', ascending=False).head(5)
print("--- TOP 5 HIGHEST RATED DIRECTORS (min. 10 movies) ---")
print(top_rated_directors[['single_director', 'mean_rating', 'movie_count', 'top_genre']])

# Ranking 2: Directors with the longest average runtime
longest_movies_directors = filtered_directors.sort_values(by='mean_runtime', ascending=False).head(5)
print("\n--- TOP 5 DIRECTORS WITH THE LONGEST AVERAGE RUNTIME (min. 10 movies) ---")
print(longest_movies_directors[['single_director', 'mean_runtime', 'movie_count', 'top_genre']])