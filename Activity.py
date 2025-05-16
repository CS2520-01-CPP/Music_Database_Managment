"""
Module: Activity.py
Author: Jacob       : Backend
        Marlenne    : Frontend

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
- Pygame
"""

import os
import subprocess, tkinter as tk
import pygame
from tkinter import BOTH, BOTTOM, END, LEFT, RIGHT, TOP, VERTICAL, Y, PhotoImage, ttk
from tkinter import messagebox
import Database


#The modification the GUI is split between left side and right side for simplicity.
def create_left_area(root, current_user, update_song_info_callback):
    """Function to create the left area (3/4 of the screen) with tabs for 'All Songs' and 'Playlist'"""
    #Create the left frame
    left_frame = tk.Frame(root, bg="lightblue")
    left_frame.grid(row=0, column=0, sticky="nsew")  #Left side will take up 3/4 of the screen


    #Create the logout button
    def logout():
        #Destroy the current activity window (activity_root)
        root.destroy()

        #Run Main.py using subprocess
        subprocess.run(["python", "Main.py"])

    s = ttk.Style()
    s.configure('TNotebook', tabposition='sw')
    customed_style = ttk.Style()
    customed_style.configure('Custom.TNotebook.Tab', padding=[100, 20], font=('Arial', 10))
    #Create a Notebook widget (tabs)
    notebook = ttk.Notebook(left_frame, style='Custom.TNotebook')
    notebook.pack(fill="both", expand=True, padx=20, pady=20)

    #Create the "All Songs" tab
    all_songs_frame = tk.Frame(notebook, bg="blue")
    notebook.add(all_songs_frame, text="All Songs")

    #Create the "Playlist" tab
    playlist_frame = tk.Frame(notebook, bg="lightblue")
    notebook.add(playlist_frame, text="Playlist")

    #Create the "Account" tab
    account_frame = tk.Frame(notebook, bg="lightblue")
    notebook.add(account_frame, text="Account")


    #Add content to the "All Songs" tab
    all_songs_aesthetic_header = tk.Frame(all_songs_frame,width=900, height=80, highlightbackground="black", highlightthickness=10)
    song_sections_label = tk.Label(all_songs_frame, text=" All Songs in Database", font=("Arial", 25))
    song_sections_label.place(x=10, y=100)
    all_songs_aesthetic_header.place(y=80)
   
    #Adds scrollbar
    all_songs_canvas = tk.Canvas(all_songs_frame,width=900, height=800)
    all_songs_canvas.place(x=0,y=160)
    all_songs_scroll_bar = tk.Scrollbar(all_songs_frame, orient=VERTICAL, command=all_songs_canvas.yview) 
    all_songs_scroll_bar.pack(side=RIGHT, fill=Y) 
    all_songs_canvas.configure(yscrollcommand=all_songs_scroll_bar.set)
    all_songs_canvas.bind('<Configure>', lambda e: all_songs_canvas.configure(scrollregion=all_songs_canvas.bbox("all")))

    all_songs_scroll_frame = tk.Frame(all_songs_canvas)
    all_songs_canvas.create_window((0, 0), window=all_songs_scroll_frame, anchor="nw")


    #Get and display all songs from the database
    songs = Database.get_all_songs()
    
    if songs:
        for song in songs:
            song_button = tk.Button(all_songs_scroll_frame, text=song, font=("Arial", 16), 
                                    command=lambda s=song: update_song_info_callback(s)).pack()
    else:
        no_songs_label = tk.Label(all_songs_canvas, text="No songs found in the database.", font=("Arial", 16))
        no_songs_label.place(x=10, y=50)
    
    #Search bar with label to the left
    search_label = tk.Label(all_songs_frame, text="Search:", font=("Arial", 20))
    search_label.place(x=10, y=10)

    search_var = tk.StringVar()
    search_entry = tk.Entry(all_songs_frame, textvariable=search_var, width=30, font=("Arial", 20))
    search_entry.place(x=130, y=10)

    def update_song_list():
        search_term = search_var.get().lower()

        #Debugging: Check if the search term is being retrieved correctly
        print(f"Search term: {search_term}")

        #Clear existing song buttons
        for widget in all_songs_scroll_frame.winfo_children():
            widget.destroy()

        #Get all songs and filter by search term
        all_songs = Database.get_all_songs()

        #Debugging: Check if songs are being retrieved from the database
        print(f"All songs retrieved: {all_songs}")

        filtered_songs = [song for song in all_songs if search_term in song.lower()]

        #Debugging: Check the filtered songs
        print(f"Filtered songs: {filtered_songs}")

        #Helper to parse song into components (title, artist)
        def parse_song(song_str):
            print(f"Parsing song: {song_str}")  #Debugging print
            parts = song_str.split(", ")
            if len(parts) == 2:
                name = parts[0].strip()  #The song name
                artist_with_extension = parts[1].strip()  #The artist and file extension
                artist = artist_with_extension.replace(".mp3", "")  #Remove the .mp3 extension
                print(f"Parsed name: {name}, artist: {artist}")  #Debugging print
                return name, artist
            return song_str, ""  #If it's not in the expected format

        #Display the filtered songs
        if filtered_songs:
            for song in filtered_songs:
                tk.Button(
                    all_songs_scroll_frame,
                    text=song,
                    font=("Arial", 16),
                    command=lambda s=song: update_song_info_callback(s)
                ).pack()
        else:
            tk.Label(all_songs_scroll_frame, text="No songs found.", font=("Arial", 16)).pack()

    #Adding the trace for search_var to call update_song_list when the search text is changed
    search_var.trace_add("write", lambda *args: update_song_list())

    #Fetch and display the user's playlists
    def show_playlist_songs(playlist_name):
        """Function to show songs of the selected playlist."""
        for widget in playlist_frame.winfo_children():
            widget.destroy()

        #Add the back button to go back to the list of playlists
        back_button = tk.Button(playlist_frame, text="Back to Playlists", font=("Arial", 14),command=lambda: show_playlists())
        back_button.pack(pady=10)
        tk.Button(playlist_frame, text="Edit Playlist", font=("Arial", 14),
          command=lambda: edit_playlist_ui(playlist_name)).pack(pady=10)
        
        def edit_playlist_ui(playlist_name):
            for widget in playlist_frame.winfo_children():
                widget.destroy()

            tk.Label(playlist_frame, text=f"Edit Playlist: {playlist_name}", font=("Arial", 20)).pack(pady=10)

            #Search bar
            search_frame = tk.Frame(playlist_frame)
            search_frame.pack(pady=10)

            search_label = tk.Label(search_frame, text="Search:", font=("Arial", 14))
            search_label.pack(side=tk.LEFT)

            search_var = tk.StringVar()
            search_entry = tk.Entry(search_frame, textvariable=search_var, font=("Arial", 14), width=30)
            search_entry.pack(side=tk.LEFT)

            #Scrollable song checkbox list
            canvas = tk.Canvas(playlist_frame, width=500, height=400)
            scroll_frame = tk.Frame(canvas)
            scrollbar = tk.Scrollbar(playlist_frame, orient="vertical", command=canvas.yview)
            canvas.configure(yscrollcommand=scrollbar.set)

            canvas.create_window((0, 0), window=scroll_frame, anchor='nw')
            canvas.pack(side="left", fill="both", expand=True, padx=10)
            scrollbar.pack(side="right", fill="y")

            check_vars = {}

            def populate_checkboxes(filter_text=""):
                for widget in scroll_frame.winfo_children():
                    widget.destroy()
                check_vars.clear()

                all_songs = Database.get_all_songs()
                current_songs, _ = Database.get_playlist(playlist_name)
                filtered_songs = [song for song in all_songs if filter_text.lower() in song.lower()]

                for song in filtered_songs:
                    var = tk.BooleanVar(value=(song in current_songs))
                    check = tk.Checkbutton(scroll_frame, text=song, variable=var, font=("Arial", 12),
                                        anchor="w", justify="left", wraplength=450)
                    check.pack(anchor="w")
                    check_vars[song] = var

                scroll_frame.update_idletasks()
                canvas.config(scrollregion=canvas.bbox("all"))

            populate_checkboxes()
            search_var.trace_add("write", lambda *args: populate_checkboxes(search_var.get()))

            def save_edited_playlist():
                selected_songs = [song for song, var in check_vars.items() if var.get()]
                if not selected_songs:
                    messagebox.showerror("Error", "Select at least one song to keep in the playlist.")
                    return

                #Overwrite the playlist content
                Database.replace_playlist_songs(current_user, playlist_name, selected_songs)
                messagebox.showinfo("Success", f"Playlist '{playlist_name}' updated!")
                show_playlist_songs(playlist_name)

            tk.Button(playlist_frame, text="Save Changes", font=("Arial", 14), command=save_edited_playlist).pack(pady=10)
            tk.Button(playlist_frame, text="Cancel", font=("Arial", 12), command=lambda: show_playlist_songs(playlist_name)).pack(pady=5)


        playlist_name_aesthetic_header = tk.Frame(playlist_frame,width=1000, height=100, highlightbackground="black", highlightthickness=10)
        playlist_name_label = tk.Label(playlist_name_aesthetic_header, text=f"Songs in {playlist_name}", font=("Arial", 20))
        playlist_name_aesthetic_header.pack(pady=10)
        playlist_name_label.place(x=500, y=25,anchor = "n")

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
        for widget in playlist_frame.winfo_children():
            widget.destroy()

        playlist_aesthetic_header = tk.Frame(playlist_frame,width=900, height=90, highlightbackground="black", highlightthickness=10)
        playlist_label = tk.Label(playlist_frame, text=" Your Playlists", font=("Arial", 25))
        playlist_aesthetic_header.place(y=0)
        playlist_label.place(x=320, y=20)
        #adds scrollbar

        
        
        def new_playlist_ui():
            for widget in playlist_frame.winfo_children():
                widget.destroy()

            tk.Label(playlist_frame, text="Create New Playlist", font=("Arial", 20)).pack(pady=10)

            #Playlist name entry
            tk.Label(playlist_frame, text="Playlist Name:", font=("Arial", 14)).pack(pady=(0, 0))
            playlist_name_var = tk.StringVar()
            tk.Entry(playlist_frame, textvariable=playlist_name_var, font=("Arial", 14), width=30).pack()

            #Search bar
            search_frame = tk.Frame(playlist_frame)
            search_frame.pack(pady=10)

            search_label = tk.Label(search_frame, text="Search:", font=("Arial", 14))
            search_label.pack(side=tk.LEFT)

            search_var = tk.StringVar()
            search_entry = tk.Entry(search_frame, textvariable=search_var, font=("Arial", 14), width=30)
            search_entry.pack(side=tk.LEFT)


            #Frame + canvas for checkbox song list
            #scrollbar
            canvas = tk.Canvas(playlist_frame, width=500, height=400)
            scroll_frame = tk.Frame(canvas)
            scrollbar = tk.Scrollbar(playlist_frame, orient="vertical", command=canvas.yview)
            canvas.configure(yscrollcommand=scrollbar.set)

            canvas.create_window((0, 0), window=scroll_frame, anchor='nw')
            canvas.pack(side="left", fill="both", expand=True, padx=10)
            scrollbar.pack(side="right", fill="y")

            check_vars = {}  #Dictionary to store checkbox vars

            def populate_checkboxes(filter_text=""):
                #Clear previous
                for widget in scroll_frame.winfo_children():
                    widget.destroy()
                check_vars.clear()

                all_songs = Database.get_all_songs()
                filtered_songs = [song for song in all_songs if filter_text.lower() in song.lower()]

                for song in filtered_songs:
                    var = tk.BooleanVar()
                    check = tk.Checkbutton(scroll_frame, text=song, variable=var, font=("Arial", 12), anchor="w", justify="left", wraplength=450)
                    check.pack(anchor="w")
                    check_vars[song] = var

                scroll_frame.update_idletasks()
                canvas.config(scrollregion=canvas.bbox("all"))

            #Initially populate all songs
            populate_checkboxes()

            #Update on search change
            search_var.trace_add("write", lambda *args: populate_checkboxes(search_var.get()))

            #Create Playlist button
            def create_playlist():
                name = playlist_name_var.get().strip()
                if not name:
                    messagebox.showerror("Error", "Playlist name cannot be empty.")
                    return

                selected_songs = [song for song, var in check_vars.items() if var.get()]
                if not selected_songs:
                    messagebox.showerror("Error", "Select at least one song to create a playlist.")
                    return

                Database.add_songs_to_playlist(current_user, name, selected_songs)
                messagebox.showinfo("Success", f"Playlist '{name}' created!")
                show_playlists()

            tk.Button(playlist_frame, text="Create Playlist", font=("Arial", 14), command=create_playlist).pack(pady=10)

            #Cancel/back button
            tk.Button(playlist_frame, text="Cancel", font=("Arial", 12), command=show_playlists).pack(pady=5)

        #Now use the above in the button
        new_playlist_button = tk.Button(playlist_frame, text="New Playlist", font=("Arial", 14), command=new_playlist_ui)
        new_playlist_button.place(x=20, y=20)

        playlists, error = Database.get_all_playlists_for_user(current_user)
        if error:
            playlist_error_label = tk.Label(playlist_frame, text=f"Error: {error}", font=("Arial", 16))
            playlist_error_label.pack(pady=20)
            playlist_error_label.place(x=40, y=100)
        else:
            playlists_canvas = tk.Canvas(playlist_frame,width=900, height=800)
            playlists_canvas.place(x=0,y=90)
            playlists_scroll_bar = tk.Scrollbar(playlist_frame, orient=VERTICAL, command=playlists_canvas.yview) 
            playlists_scroll_bar.pack(side=RIGHT, fill=Y) 
            playlists_canvas.configure(yscrollcommand=playlists_scroll_bar.set)
            playlists_canvas.bind('<Configure>', lambda e: playlists_canvas.configure(scrollregion=playlists_canvas.bbox("all")))

            playlist_canvas_scroll_frame = tk.Frame(playlists_canvas)
            playlists_canvas.create_window((0, 0), window=playlist_canvas_scroll_frame, anchor="nw")
            
            if playlists:
                for playlist in playlists:

                    playlist_row = tk.Frame(playlist_canvas_scroll_frame)
            
                    playlist_row.pack(pady=5, fill="x")

                    playlist_button = tk.Button(playlist_row, text=playlist, font=("Arial", 14),
                                                command=lambda name=playlist: show_playlist_songs(name))
                    playlist_button.pack(side="left", padx=5)

                    remove_button = tk.Button(playlist_row, text="Remove", font=("Arial", 12), fg="red",
                                            command=lambda name=playlist: confirm_remove_playlist(name))
                    remove_button.pack(side="right", padx=5)
            else:
                no_playlist_label = tk.Label(playlist_frame, text="No playlists found.", font=("Arial", 16))
                no_playlist_label.place(x = 450,y=100)

    show_playlists()

    #Add content to the "Account" tab
    account_aesthetic_header = tk.Frame(account_frame,width=900, height=100, highlightbackground="black", highlightthickness=10)
    account_label = tk.Label(account_frame, text=" Your Account", font=("Arial", 25))
    account_aesthetic_header.place(y=0)
    account_label.place(x=450, y=25,anchor = "n")

#Logout button (positioned at the bottom-right corner)
    logout_button = tk.Button(left_frame, text="Logout", font=("Arial", 14), command=logout)

    def confirm_remove_playlist(name):
        confirm = messagebox.askyesno("Remove Playlist", f"Are you sure you want to delete '{name}'?")
        if confirm:
            Database.remove_playlist(current_user, name)
            messagebox.showinfo("Deleted", f"'{name}' has been deleted.")
            show_playlists()

    def on_tab_changed(event):
        selected_tab = notebook.tab(notebook.select(), "text")
        if selected_tab == "Account":
            logout_button.place(x=830, y=655)
        else:
            logout_button.place_forget()

    notebook.bind("<<NotebookTabChanged>>", on_tab_changed)



def create_right_area(root):
    """Function to create the right area (1/4 of the screen) to show selected song info"""
    #Initialize pygame mixer for audio playback
    pygame.mixer.init()

    #Create the right frame
    right_frame = tk.Frame(root, bg="white")
    right_frame.grid(row=0, column=1, sticky="nsew")  #Right side will take up 1/4 of the screen

    #Song information label (will update dynamically)
    song_info_label = tk.Label(right_frame, text="Select a song to view details", font=("Arial", 16), bg="lightgreen")
    song_info_label.pack(pady=20)

    #Song details labels (these will be updated dynamically when a song is selected)
    song_title_label = tk.Label(right_frame, text="Song Title: ", font=("Arial", 14), bg="lightgreen")
    song_title_label.pack(anchor="w", padx=20, pady=5)

    artist_label = tk.Label(right_frame, text="Artist: ", font=("Arial", 14), bg="lightgreen")
    artist_label.pack(anchor="w", padx=20, pady=5)

    duration_label = tk.Label(right_frame, text="Duration: ", font=("Arial", 14), bg="lightgreen")
    duration_label.pack(anchor="w", padx=20, pady=5)

    current_song_name = None
    is_playing = False  #Track if the song is currently playing

    #Function to play or stop the song
    def toggle_play_stop():
        nonlocal is_playing, current_song_name
        
        if is_playing:
            print(f"Stopping: {current_song_name}")
            pygame.mixer.music.stop()  #Stop the music
            play_button.config(text="Play")  #Change button text to "Play"
            is_playing = False
        else:
            print(f"Playing: {current_song_name}")
            current_song_dir = os.path.join(os.getcwd(), 'Songs', current_song_name)
            pygame.mixer.music.load(current_song_dir)  #Load the song
            pygame.mixer.music.play()  #Play the song
            play_button.config(text="Stop")  #Change button text to "Stop"
            is_playing = True

    #Function to update the song info labels when a song is selected
    def update_song_info(song_name):
        nonlocal current_song_name  #Use the outer variable
        
        #Get the details for the song
        title, author, duration = Database.get_song_details(song_name)
        
        #Update the UI labels with song information
        song_title_label.config(text=f"Song Title: {title}")
        song_title_label.place(x=30,y=350)
        artist_label.config(text=f"Author: {author}")
        artist_label.place(x=30,y=400)
        
        #If duration is a string (e.g., "3 minutes 45 seconds"), just display it as is
        if isinstance(duration, str):
            duration_label.config(text=f"Duration: {duration}")
            duration_label.place(x=30,y=450)
        else:
            #Otherwise, it's a float (duration in seconds), format it to minutes and seconds
            minutes = int(duration // 60)
            seconds = int(duration % 60)
            duration_label.config(text=f"Duration: {minutes} minutes {seconds} seconds")
            duration_label.place(x=30,y=450)
        #image to display when playing song
        absolute_path = os.path.dirname(os.path.abspath(__file__))
        filename = os.path.join(absolute_path, "pauseplay.png")
        og_image = PhotoImage(file = filename)
        image = og_image.subsample(6,6)
        play_image_label = tk.Label(right_frame, image = image)
        play_image_label.photo = image
        play_image_label.place(x=50,y=75)
        
        #Update the current song name
        current_song_name = song_name
        current_song_dir = os.path.join(os.getcwd(), 'Songs', current_song_name)
        print(f"Song directory: {current_song_dir}")
        
        
 

    #Add the Play/Stop button
    play_button = tk.Button(right_frame, text="Play", font=("Arial", 14), bg="lightgreen", command=toggle_play_stop)
    play_button.place(x=125,y=300)

    #Return the update function so it can be used elsewhere
    return update_song_info

def launch_activity():
    """Function to launch a new window after successfull login"""
    activity_root = tk.Tk()
    activity_root.title("Python Final")
    activity_root.geometry("1920x1080")  #Full screen size

    #Get the current user from the database
    current_user = Database.get_current_user()

    #Configure the grid to have two columns: 3/4 for the left side and 1/4 for the right side
    activity_root.grid_columnconfigure(0, weight=3)  #Left side (3/4 of the screen)
    activity_root.grid_columnconfigure(1, weight=1)  #Right side (1/4 of the screen)

    #Configure the row to make both frames expand to fill the height
    activity_root.grid_rowconfigure(0, weight=1)  #Make sure the row stretches vertically

    #Create the right area (this returns the update_song_info function)
    update_song_info = create_right_area(activity_root)

    #Pass the update_song_info function to the left area
    create_left_area(activity_root, current_user, update_song_info)

    activity_root.mainloop()

