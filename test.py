from app import (Venue, Artist, Genre, Show, db)
# data1 = {
#     # Venue
#     # "id": 1,
#     "name": "The Musical Hop",
#     "city": "San Francisco",
#     "state": "CA",
#     "address": "1015 Folsom Street",
#     "phone": "123-123-1234",
#     # "genres": ["Jazz", "Reggae", "Swing", "Classical", "Folk"],
#     "image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60",
#     "facebook_link": "https://www.facebook.com/TheMusicalHop",

#     "website": "https://www.themusicalhop.com",
#     "seeking_talent": True,
#     "seeking_description": "We are on the lookout for a local artist to play every two weeks. Please call us.",
#     # "past_shows": [{
#     #     "artist_id": 4,
#     #     "artist_name": "Guns N Petals",
#     #     "artist_image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
#     #     "start_time": "2019-05-21T21:30:00.000Z"
#     # }],
#     # "upcoming_shows": [],
#     # "past_shows_count": 1,
#     # "upcoming_shows_count": 0,
# }
genres = [
    'Alternative',
    'Blues',
    'Classical',
    'Country',
    'Electronic',
    'Folk',
    'Funk',
    'Hip-Hop',
    'Heavy Metal',
    'Instrumental',
    'Jazz',
    'Musical Theatre',
    'Pop',
    'Punk',
    'R&B',
    'Reggae',
    'Rock n Roll',
    'Soul',
    'Other']
# adding genres in our db
for g in genres:
    genre = Genre(name=g)
    db.session.add(genre)

db.session.commit()
db.session.close()


# for k in data1.keys():
#     print(k)
#     print(data1[k])

#     venue = Venue()
#     # setattr(venue, k, data1[k])
#     print(venue)
# import enum


# class Genres(enum.Enum):
#     Alternative = 'Alternative'
#     Blues = 'Blues'
#     Classical = 'Classical'
#     Country = 'Country'
#     Electronic = 'Electronic'
#     Folk = 'Folk'
#     Funk = 'Funk'
#     Hip_Hop = 'Hip-Hop'
#     Heavy_Metal = 'Heavy Metal'
#     Instrumental = 'Instrumental'
#     Jazz = 'Jazz'
#     Musical_Theatre = 'Musical Theatre'
#     Pop = 'Pop'
#     Punk = 'Punk'
#     R_AND_B = 'R&B'
#     Reggae = 'Reggae'
#     Rock_n_Roll = 'Rock n Roll'
#     Soul = 'Soul'
#     Other = 'Other'
