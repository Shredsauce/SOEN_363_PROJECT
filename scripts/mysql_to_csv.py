import mysql.connector
import pandas as pd
import os


# Function to execute a query and return a DataFrame
def execute_query(query):
    cursor = mydb.cursor()
    cursor.execute(query)
    column_names = [i[0] for i in cursor.description]
    rows = cursor.fetchall()
    df = pd.DataFrame(rows, columns=column_names)
    cursor.close()
    return df


# Connect to MySQL database
mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    password="YOUR_PASSWORD",  # Replace YOUR_PASSWORD with your actual password
    database="movies"
)

# Define output directory and ensure it exists
output_directory = r'C:\Users\your_username\Desktop\movie_data'  # Replace your_username with your actual username
os.makedirs(output_directory, exist_ok=True)

# Execute queries and save to CSV
content_rating_df = execute_query("SELECT * FROM Content_Rating")
# country_df = execute_query("SELECT * FROM Country")
# movie_df = execute_query("SELECT * FROM Movie")
# genre_df = execute_query("SELECT * FROM Genre")
# language_df = execute_query("SELECT * FROM Language")
# keywords_df = execute_query("SELECT * FROM Keyword")
# akas_df = execute_query("SELECT * FROM Akas")
# movie_genre_df = execute_query("SELECT * FROM MovieGenre")
# movie_language_df = execute_query("SELECT * FROM MovieLanguage")
# movie_keyword_df = execute_query("SELECT * FROM MovieKeyword")
# person_df = execute_query("SELECT * FROM Person")
# actor_df = execute_query("SELECT * FROM Actor")
# director_df = execute_query("SELECT * FROM Director")
# creator_df = execute_query("SELECT * FROM Creator")
# movie_actor_df = execute_query("SELECT * FROM MovieActor")
# movie_director_df = execute_query("SELECT * FROM MovieDirector")
# movie_creator_df = execute_query("SELECT * FROM MovieCreator")

# Save DataFrames to CSV
content_rating_df.to_csv(os.path.join(output_directory, 'content_rating.csv'), index=False)
country_df.to_csv(os.path.join(output_directory, 'country.csv'), index=False)
movie_df.to_csv(os.path.join(output_directory, 'movie.csv'), index=False)
genre_df.to_csv(os.path.join(output_directory, 'genre.csv'), index=False)
language_df.to_csv(os.path.join(output_directory, 'language.csv'), index=False)
keywords_df.to_csv(os.path.join(output_directory, 'keywords.csv'), index=False)
akas_df.to_csv(os.path.join(output_directory, 'akas.csv'), index=False)
movie_genre_df.to_csv(os.path.join(output_directory, 'movie_genre.csv'), index=False)
movie_language_df.to_csv(os.path.join(output_directory, 'movie_language.csv'), index=False)
movie_keyword_df.to_csv(os.path.join(output_directory, 'movie_keyword.csv'), index=False)
person_df.to_csv(os.path.join(output_directory, 'person.csv'), index=False)
actor_df.to_csv(os.path.join(output_directory, 'actor.csv'), index=False)
director_df.to_csv(os.path.join(output_directory, 'director.csv'), index=False)
creator_df.to_csv(os.path.join(output_directory, 'creator.csv'), index=False)
movie_actor_df.to_csv(os.path.join(output_directory, 'movie_actor.csv'), index=False)
movie_director_df.to_csv(os.path.join(output_directory, 'movie_director.csv'), index=False)
movie_creator_df.to_csv(os.path.join(output_directory, 'movie_creator.csv'), index=False)

# Inform the user that CSV files have been created
print("CSV files have been created successfully in the folder 'movie_data' on your desktop.")
