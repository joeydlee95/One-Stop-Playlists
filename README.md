# Hear Me Out!

## Introduction
This is an application that can persistently store your favorite songs or videos in playlists that you create. This application uses the flask framework and OAuth 2 authorization framework.

## Build/Installing
1. git clone https://github.com/joeydlee95/item-catalog
2. vagrant up
3. vagrant ssh
4. cd /vagrant
5. Set up the database: python database_setup.py

## Running
Use python application.py and go to localhost:5000/

## File Layout
application.py
 - Handles requests and uses that database to maintain a persistent storage.
 - Can create, delete, and edit playlists. You need to have a title and description for each playlist.
 - Within each playlist, you can add, delete, and edit songs. You need to have a title, genre, link.
 - To be able to use any of these functions, you must be logged on.

templates directory
 - Contains the html files that are viewed in the browser.

static directory
 - Contains the css and images files that should be referenced from the templates.

## Login
Using OAuth 2 authentication framework, you can log in using google or facebook logins.

## JSON Files
 Can access a JSON formatted file for a playlist or a song. Go to "/playlists/playlist_id/JSON", where playlist_id is the id of the playlist you want the json of, to get the json of a particular playlist. Go to "/playlists/playlist_id/song_id/JSON", where playlist_id is the id of the playlist you want and song_id is the id of the song you want, to get the json of a particular song.

