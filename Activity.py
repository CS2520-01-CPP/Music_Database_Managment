"""
Module: Activity.py
Author: Jacob       : Backend
        Marlenne    : Frontend

Date Created: 2025-04-02
Last Modified: 2025-04-26
Version: 1.0

Description:
This module creates a graphical user interface (GUI) for managing songs and playlists in a music database system. It allows users to view all songs, manage playlists, 
and view song details. The module uses the Tkinter library for the GUI and interacts with a database for retrieving songs and playlists, 
allowing users to create new playlists, add songs to them, and view playlist contents.

Usage:
1. The user will be presented with two sections: one for Viewing all songs and one for managing playlists.
2. The "Create Playlist" button allows users to select multiple songs and create a new playlist.
3. The user can select songs and view details like title, author, and duration in the right-side area of the window.
4. The "Logout" will return to the login page.

Dependencies:
- Tkinter (for GUI)
- Database module (for database operations like fetching songs, creating playlists, etc.)

"""

import subprocess, tkinter as tk
from tkinter import BOTH, END, LEFT, RIGHT, Y, ttk
import Database

# The modification the GUI is split between left side and right side for simplicity.

def create_left_area(root, current_user, update_song_info_callback):
    """Function to create the left area (3/4 of the screen) with tabs for 'All Songs' and 'Playlist'"""
    # Create the left frame
    left_frame = tk.Frame(root, bg="lightblue")
    left_frame.grid(row=0, column=0, sticky="nsew")  # Left side will take up 3/4 of the screen


    # Create the logout button
    def logout():
        # Destroy the current activity window (activity_root)
        root.destroy()

        # Run Main.py using subprocess
        subprocess.run(["python", "Main.py"])

    

    s = ttk.Style()
    s.configure('TNotebook', tabposition='sw')
    customed_style = ttk.Style()
    customed_style.configure('Custom.TNotebook.Tab', padding=[100, 20], font=('Arial', 10))
    # Create a Notebook widget (tabs)
    notebook = ttk.Notebook(left_frame, style='Custom.TNotebook')
    notebook.pack(fill="both", expand=True, padx=20, pady=20)

    # Create the "All Songs" tab
    all_songs_frame = tk.Frame(notebook, bg="blue")
    notebook.add(all_songs_frame, text="All Songs")
    #all_songs_frame.place(x=-50, y=-50)

    # Create the "Playlist" tab
    playlist_frame = tk.Frame(notebook, bg="lightblue")
    notebook.add(playlist_frame, text="Playlist")

    # Create the "Account" tab
    account_frame = tk.Frame(notebook, bg="lightblue")
    notebook.add(account_frame, text="Account")

    # Logout button (positioned at the bottom-right corner)
    logout_button = tk.Button(left_frame, text="Logout", font=("Arial", 14), command=logout)
    #logout_button.pack(side="bottom")
    logout_button.place(x=830, y=655)

    # Add content to the "All Songs" tab
    #all_songs_label = tk.Label(all_songs_frame, text=f"All Songs", font=("Arial", 20))
    #all_songs_label.pack(pady=20)

    # Get and display all songs from the database
    songs = Database.get_all_songs()

    if songs:
        for song in songs:
            song_button = tk.Button(all_songs_frame, text=song, font=("Arial", 16), 
                                    command=lambda s=song: update_song_info_callback(s))
            song_button.pack(anchor="w", padx=20, pady=5)
    else:
        no_songs_label = tk.Label(all_songs_frame, text="No songs found in the database.", font=("Arial", 16))
        no_songs_label.place(x=10, y=200)
    
    song_sections_label = tk.Label(all_songs_frame, text=" Name\t\t   Artist\t\tLength\t", font=("Arial", 25))
    song_sections_label.place(x=10, y=100)

    search_var = tk.StringVar()
    search_entry = tk.Entry(all_songs_frame, textvariable=search_var, width = 30, font=("Arial", 20))
    search_entry.place(x=50, y=10)
    
    '''
    def update_suggestions(*args):
    search_term = search_var.get()
    suggestions = ["New York", "Los Angeles", "Chicago", "Houston", "Phoenix"]

    matching_suggestions = [suggestion for suggestion in suggestions if suggestion.lower().startswith(search_term.lower())]

    suggestion_list.delete(0, tk.END)
    for suggestion in matching_suggestions:
        suggestion_list.insert(tk.END, suggestion)

search_var.trace("w", update_suggestions)
    '''

    #suggestion_list = tk.Listbox(all_songs_frame, font=("Arial", 12))
    #suggestion_list.pack()

    def show():
        lbl.config(text=cb.get())

    # Dropdown options  
    a = ["A-Z Song Title", "A-Z Artist", "Song Length"]

    # Combobox
    cb = ttk.Combobox(all_songs_frame, values=a,width = 10, font=("Arial", 20))
    cb.set("Select Filter")
    cb.place(x=700, y=10)

    # Button to display selection  
    search_button = tk.Button(all_songs_frame, text="Search", command=show, font=("Arial", 10))
    search_button.place(x=520, y=15)
    
    # Label to show selected value  
    lbl = tk.Label(all_songs_frame, text=" ")
    lbl.place(x=10, y=50)
        
    #scroll bar for all songs
    all_songs_scroll_bar = tk.Scrollbar(all_songs_frame) 
    all_songs_scroll_bar.pack( side = RIGHT, fill = Y) 
    
    
    # Add content to the "Playlist" tab
    
    playlist_label = tk.Label(playlist_frame, text="Your Playlists", font=("Arial", 20))
    playlist_label.pack(pady=20)
    
   

    # Fetch and display the user's playlists
    def show_playlist_songs(playlist_name):
        """Function to show songs of the selected playlist."""
        # Remove all widgets from the current playlist frame
        for widget in playlist_frame.winfo_children():
            widget.destroy()

        # Add the back button to go back to the list of playlists
        back_button = tk.Button(playlist_frame, text="Back to Playlists", font=("Arial", 14),command=lambda: show_playlists())
        back_button.pack(pady=10)

        

        # Display playlist name and songs
        playlist_name_label = tk.Label(playlist_frame, text=f"Songs in {playlist_name}", font=("Arial", 20))
        playlist_name_label.pack(pady=10)

        

        # Get the songs for the selected playlist
        songs, error = Database.get_playlist(playlist_name)
        if error:
            playlist_error_label = tk.Label(playlist_frame, text=f"Error: {error}", font=("Arial", 16))
            playlist_error_label.pack(pady=20)
        else:
            if songs:
                for song in songs:
                    song_button = tk.Button(playlist_frame, text=song, font=("Arial", 16),
                                            command=lambda s=song: update_song_info_callback(s))
                    song_button.pack(anchor="w", padx=20, pady=5)
            else:
                no_playlist_label = tk.Label(playlist_frame, text="No songs in this playlist.", font=("Arial", 16))
                no_playlist_label.pack(pady=20)

    def show_playlists():
        """Function to show the list of playlists."""
        # Clear all widgets in the playlist frame
        for widget in playlist_frame.winfo_children():
            widget.destroy()

        # Display playlists list
        playlist_label = tk.Label(playlist_frame, text="Your Playlists", font=("Arial", 20))
        playlist_label.pack(pady=20)

        new_playlist_button = tk.Button(playlist_frame, text="New Playlist", font=("Arial", 14),command=lambda: show_playlists())
        new_playlist_button.place(x=10, y=10)

        playlists, error = Database.get_all_playlists_for_user(current_user)
        if error:
            playlist_error_label = tk.Label(playlist_frame, text=f"Error: {error}", font=("Arial", 16))
            playlist_error_label.pack(pady=20)
        else:
            if playlists:
                for playlist in playlists:
                    # Each playlist is clickable, display songs when clicked
                    playlist_button = tk.Button(playlist_frame, text=playlist, font=("Arial", 16),
                                                command=lambda p=playlist: show_playlist_songs(p))
                    playlist_button.pack(anchor="w", padx=20, pady=5)
            else:
                no_playlist_label = tk.Label(playlist_frame, text="No playlists found.", font=("Arial", 16))
                no_playlist_label.pack(pady=20)

    # Initially show the list of playlists
    show_playlists()
    #scroll bar for playlists
    playlist_scroll_bar = tk.Scrollbar(playlist_frame) 
    playlist_scroll_bar.pack( side = RIGHT, fill = Y) 

    # Add content to the "Account" tab
    account_label = tk.Label(account_frame, text=f"Account", font=("Arial", 20))
    account_label.pack(pady=20)

def create_right_area(root):
    """Function to create the right area (1/4 of the screen) to show selected song info"""
    # Create the right frame
    right_frame = tk.Frame(root, bg="lightgreen")
    right_frame.grid(row=0, column=1, sticky="nsew")  # Right side will take up 1/4 of the screen

    # Song information label (will update dynamically)
    song_info_label = tk.Label(right_frame, text="Select a song to view details", font=("Arial", 16), bg="lightgreen")
    song_info_label.pack(pady=20)

    # Song details labels (these will be updated dynamically when a song is selected)
    song_title_label = tk.Label(right_frame, text="Song Title: ", font=("Arial", 14), bg="lightgreen")
    song_title_label.pack(anchor="w", padx=20, pady=5)

    artist_label = tk.Label(right_frame, text="Artist: ", font=("Arial", 14), bg="lightgreen")
    artist_label.pack(anchor="w", padx=20, pady=5)

    duration_label = tk.Label(right_frame, text="Duration: ", font=("Arial", 14), bg="lightgreen")
    duration_label.pack(anchor="w", padx=20, pady=5)

    # Function to update the song info labels when a song is selected
    def update_song_info(song_name):
        # Get the details for the song
        title, author, duration = Database.get_song_details(song_name)
        
        # Update the UI labels with song information
        song_title_label.config(text=f"Song Title: {title}")
        artist_label.config(text=f"Author: {author}")
        
        # If duration is a string (e.g., "3 minutes 45 seconds"), just display it as is
        if isinstance(duration, str):
            duration_label.config(text=f"Duration: {duration}")
        else:
            # Otherwise, it's a float (duration in seconds), format it to minutes and seconds
            minutes = int(duration // 60)
            seconds = int(duration % 60)
            duration_label.config(text=f"Duration: {minutes} minutes {seconds} seconds")



    



    
    # Return the update function so it can be used elsewhere
    return update_song_info

def launch_activity():
    """Function to launch a new window after successfull login"""
    activity_root = tk.Tk()
    activity_root.title("Python Final")
    activity_root.geometry("1920x1080")  # Full screen size

    # Get the current user from the database
    current_user = Database.get_current_user()

    # Configure the grid to have two columns: 3/4 for the left side and 1/4 for the right side
    activity_root.grid_columnconfigure(0, weight=3)  # Left side (3/4 of the screen)
    activity_root.grid_columnconfigure(1, weight=1)  # Right side (1/4 of the screen)

    # Configure the row to make both frames expand to fill the height
    activity_root.grid_rowconfigure(0, weight=1)  # Make sure the row stretches vertically

    # Create the right area (this returns the update_song_info function)
    update_song_info = create_right_area(activity_root)

    # Pass the update_song_info function to the left area
    create_left_area(activity_root, current_user, update_song_info)

    
######################################################## debug info: delete later ########################################################
    
    # print all songs from the database
    songs = Database.get_all_songs()

    print("Songs in Database")
    if songs:
        for song in songs:
            print(song)
    else:
        print("No songs found in the database.")
    
    print("\n\n")

    # This is how to add a playlists for the current user
    Database.add_songs_to_playlist(current_user, 'temp_playlist', ['BIRDS OF A FEATHER, Billie Eilish.mp3', 'LUNCH, Billie Eilish.mp3'])

    # This is how to get a playlists contents
    songs, error = Database.get_playlist("temp_playlist")
    if error:
        print(f"Error: {error}")
    else:
        print("User's Selected Playlist: ")
        for song in songs:
            print(song)


    ######################################################## debug end ########################################################

    activity_root.mainloop()

