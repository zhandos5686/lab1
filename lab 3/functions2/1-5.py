# Dictionary of movies

movies = [
{
"name": "Usual Suspects", 
"imdb": 7.0,
"category": "Thriller"
},
{
"name": "Hitman",
"imdb": 6.3,
"category": "Action"
},
{
"name": "Dark Knight",
"imdb": 9.0,
"category": "Adventure"
},
{
"name": "The Help",
"imdb": 8.0,
"category": "Drama"
},
{
"name": "The Choice",
"imdb": 6.2,
"category": "Romance"
},
{
"name": "Colonia",
"imdb": 7.4,
"category": "Romance"
},
{
"name": "Love",
"imdb": 6.0,
"category": "Romance"
},
{
"name": "Bride Wars",
"imdb": 5.4,
"category": "Romance"
},
{
"name": "AlphaJet",
"imdb": 3.2,
"category": "War"
},
{
"name": "Ringing Crime",
"imdb": 4.0,
"category": "Crime"
},
{
"name": "Joking muck",
"imdb": 7.2,
"category": "Comedy"
},
{
"name": "What is the name",
"imdb": 9.2,
"category": "Suspense"
},
{
"name": "Detective",
"imdb": 7.0,
"category": "Suspense"
},
{
"name": "Exam",
"imdb": 4.2,
"category": "Thriller"
},
{
"name": "We Two",
"imdb": 7.2,
"category": "Romance"
}
]
def high_rating(movie):
    return movie["imdb"] > 5.5

i = int(input("which film rating do you wanna check? "))
print(high_rating(movies[i]))  

def top_films(movies):
    return [movie for movie in movies if movie["imdb"] > 5.5]

top_f = top_films(movies)
for movie in top_f:
    print(f"{movie['name']} ({movie['imdb']})")

def average_imdb_score(movies):
    total_imdb = sum(movie["imdb"] for movie in movies)
    return total_imdb / len(movies) if movies else 0

avg_score = average_imdb_score(movies)
print(f"Average IMDB score: {avg_score}")

def average_imdb_by_category(movies, category_name):

    filtered_movies = [movie for movie in movies if movie["category"].lower() == category_name.lower()]
    
    if filtered_movies:
        total_imdb = sum(movie["imdb"] for movie in filtered_movies)
        return total_imdb / len(filtered_movies)
    return 0

category = "Romance"
avg_score = average_imdb_by_category(movies, category)
print(f"Average IMDB score for {category} category: {avg_score}")



