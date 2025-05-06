"""
Module: Database.py
Author: Jacob       : Backend

Date Created: 2025-04-02
Last Modified: 2025-05-06
Version: 1.0

Description:
This Module handles the backend logic for user authentication, playlist management, and song storage in a music database. 
It integrates with an SQLite database to manage users, playlists, and songs. The Module includes functions for user sign-up and login, loading songs into the database, 
adding songs to playlists, and retrieving playlists and song details. It also includes methods for hashing passwords, 
checking for duplicate entries, and interacting with the database to maintain a user's playlist and song list.


Usage:
- Users can sign up, log in, and manage their playlists.
- Songs can be loaded from a directory and added to playlists, which are then stored in the database.
- Functions like `signup()`, `login()`, and `add_songs_to_playlist()` handle the core interactions with the database.


Dependencies:
- SQLite3 (for database management)
- hashlib (for password hashing)
- tkinter (for GUI interactions with message boxes)
- mutagen (for MP3 file metadata extraction)

"""

import sqlite3, hashlib, os, json
from tkinter import messagebox
from mutagen.mp3 import MP3
import Activity

# Global variable and functions to store the current user
_current_user = None

def set_current_user(username):
    global _current_user
    _current_user = username

def get_current_user():
    return _current_user

def connect():
    conn = sqlite3.connect('song_database.db')
    return conn

# Database Creation

def create_tables():
    """Function to set up database incase it does not already exists"""
    conn = connect()
    cursor = conn.cursor()

    # Create User_Table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS User_Table (
        Username VARCHAR(45) PRIMARY KEY,
        Password VARCHAR(45),
        Playlist_Table_Name VARCHAR(45),
        FOREIGN KEY (Playlist_Table_Name) REFERENCES Playlist_Table(Name)
    )
    ''')

    # Create Playlist_Table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Playlist_Table (
        PlaylistID INTEGER PRIMARY KEY AUTOINCREMENT,
        Name VARCHAR(45),
        User_Username VARCHAR(45),
        List JSON,
        FOREIGN KEY (User_Username) REFERENCES User_Table(Username)
    )
    ''')

    # Create Song_Table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Song_Table (
        "Index" INTEGER PRIMARY KEY AUTOINCREMENT,
        Song TEXT
    )
    ''')

    conn.commit()
    conn.close()

# Login and Signup methods

def hash_password(password):
    """ Helper Function that deals with hashing passwords"""
    return hashlib.sha256(password.encode()).hexdigest()

def signup(username, password):
    """Function to handles the database interaction with singup"""
    conn = connect()
    cursor = conn.cursor()

    # Check if user already exists
    cursor.execute('SELECT * FROM User_Table WHERE Username = ?', (username,))
    if cursor.fetchone():
        conn.close()
        return False, "Username already exists."

    # Create empty playlist (optional: you can customize this later)
    playlist_name = f"{username}_playlist"
    cursor.execute('INSERT INTO Playlist_Table (Name, List) VALUES (?, ?)', (playlist_name, '[]'))

    # Insert the new user
    hashed = hash_password(password)
    cursor.execute('INSERT INTO User_Table (Username, Password, Playlist_Table_Name) VALUES (?, ?, ?)', (username, hashed, playlist_name))

    conn.commit()
    conn.close()
    return True, "User created successfully."

def login(username, password):
    """Function to handles the database interaction with login"""
    global _current_user
    
    if not username or not password:
        return False, "Username and password cannot be empty."

    conn = connect()
    cursor = conn.cursor()

    cursor.execute('SELECT Password FROM User_Table WHERE Username = ?', (username,))
    row = cursor.fetchone()

    conn.close()

    if row:
        stored_hashed_password = row[0]
        if stored_hashed_password == hash_password(password):
            _current_user = username
            return True, "Login successful."
        else:
            return False, "Incorrect username or password."
    else:
        return False, "Incorrect username or password."
    
# Database Manipulation Methods

def load_songs_to_database():
    """Function that periodically will sync the Songs dir with the database"""
    conn = connect()
    cursor = conn.cursor()

    songs_folder = "Songs"

    # Make sure Songs/ folder exists
    if not os.path.exists(songs_folder):
        os.makedirs(songs_folder)

    # List all files in Songs/
    for filename in os.listdir(songs_folder):
        filepath = os.path.join(songs_folder, filename)

        if os.path.isfile(filepath):
            # Check if the song is already in the database
            cursor.execute('SELECT * FROM Song_Table WHERE Song = ?', (filename,))
            if cursor.fetchone() is None:
                # Insert the song into the database
                cursor.execute('INSERT INTO Song_Table (Song) VALUES (?)', (filename,))
                print(f"Added {filename} to database.")  # Debugging line

    conn.commit()
    conn.close()

def add_songs_to_playlist(username, playlist_name, song_list):
    """Function to add a song to a users playlist"""
    conn = connect()
    cursor = conn.cursor()

    # Check if the playlist exists for the given user
    cursor.execute('SELECT * FROM Playlist_Table WHERE Name = ? AND User_Username = ?', (playlist_name, username))
    row = cursor.fetchone()

    if not row:
        # If the playlist doesn't exist, create it with an empty song list
        cursor.execute('INSERT INTO Playlist_Table (Name, User_Username, List) VALUES (?, ?, ?)', 
                       (playlist_name, username, '[]'))
        print(f"Playlist '{playlist_name}' created for user {username}.")
        conn.commit()
    else:
        print(f"Playlist '{playlist_name}' already exists for user {username}.")

    # Retrieve the existing song list (if any) for the playlist
    cursor.execute('SELECT List FROM Playlist_Table WHERE Name = ? AND User_Username = ?', (playlist_name, username))
    playlist_row = cursor.fetchone()

    if playlist_row:
        current_list = json.loads(playlist_row[0])  # Load the existing list from JSON

        # Add new songs to the current list
        new_songs = [song for song in song_list if song not in current_list]  # Avoid duplicates
        current_list.extend(new_songs)  # Add new songs

        # Update the playlist with the new list of songs
        cursor.execute('UPDATE Playlist_Table SET List = ? WHERE Name = ? AND User_Username = ?', 
                       (json.dumps(current_list), playlist_name, username))
        print(f"Added songs to playlist {playlist_name} for user {username}: {new_songs}")
    else:
        print(f"Error: Playlist {playlist_name} not found for user {username}.")
    
    conn.commit()
    conn.close()

# GUI Methods

def do_signup(entry_username, entry_password):
    """Function to handles Main.py signup Request"""
    username = entry_username.get()
    password = entry_password.get()

    success, message = signup(username, password)
    if success:
        messagebox.showinfo("Success", message)
    else:
        messagebox.showerror("Error", message)

def do_login(entry_username, entry_password, root):
    """Function to handles Main.py login Request"""
    username = entry_username.get()
    password = entry_password.get()

    success, message = login(username, password)
    if success:
        root.destroy()  # Close the old login window
        load_songs_to_database()  # Load songs for any user
        Activity.launch_activity()  # Launch the Activity window
    else:
        messagebox.showerror("Login Error", message)

def get_playlist(playlist_name):
    """Function to create a list of songs from the database Playlist_Table"""
    conn = connect()
    cursor = conn.cursor()

    # Retrieve the playlist for the given name
    cursor.execute('SELECT List FROM Playlist_Table WHERE Name = ?', (playlist_name,))
    row = cursor.fetchone()

    if row:
        song_list = json.loads(row[0])  # Parse the JSON list of songs
        conn.close()
        return song_list, None  # Return the playlist songs or an empty list if no songs
    else:
        conn.close()
        return None, f"Playlist '{playlist_name}' not found."
    
def get_all_playlists_for_user(username):
    """Function to create a list of playlist names from the database Playlist_Table"""
    conn = connect()
    cursor = conn.cursor()

    # Query to fetch all playlists for the given user
    cursor.execute('SELECT Name FROM Playlist_Table WHERE User_Username = ?', (username,))
    rows = cursor.fetchall()  # Fetch all rows

    # Ensure that playlists are being returned
    playlists = [row[0] for row in rows if row[0]]  # Extract playlist names
    conn.close()

    if playlists:
        return playlists, None  # Return the list of playlists
    else:
        return None, f"No playlists found for user '{username}'."
    
def get_song_details(song_name):
    """Function to split the stored database info into usefull information."""

    # Step 1: Split the song name into TITLE and AUTHOR
    if ',' in song_name:
        title, author = song_name.split(',', 1)  # Split only on the first comma
    else:
        title = song_name
        author = "Unknown"  # Default to "Unknown" if no comma is found

    # Step 2: Remove the ".mp3" from the author if it exists
    author = author.replace('.mp3', '').strip()

    # Step 3: Get the song duration from the Songs directory
    song_path = os.path.join("Songs", song_name)
    
    # Initialize duration to None in case the file isn't found or can't be processed
    duration = None

    if os.path.exists(song_path):
        try:
            # Load the MP3 file and get the duration
            audio = MP3(song_path)
            duration = audio.info.length  # Duration in seconds

            # Convert seconds to minutes and seconds
            minutes = int(duration // 60)  # Get the full minutes
            seconds = int(duration % 60)  # Get the remaining seconds

            # Format the duration as "X minutes Y seconds"
            duration = f"{minutes} minutes {seconds} seconds"

        except Exception as e:
            print(f"Error reading duration from {song_name}: {e}")
    
    # Return a tuple with TITLE, AUTHOR, and DURATION (formatted as minutes and seconds)
    return title.strip(), author.strip(), duration

# Debug Methods

def get_all_songs():
    """ Debug Function to see if the database works XD """
    conn = connect()
    cursor = conn.cursor()

    # Query to fetch all songs from the Song_Table
    cursor.execute('SELECT Song FROM Song_Table')
    rows = cursor.fetchall()  # Fetch all rows

    # Ensure that songs are being returned
    songs = [row[0] for row in rows if row[0]]
    conn.close()
    
    return songs

create_tables()