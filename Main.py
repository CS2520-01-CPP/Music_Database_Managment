"""
Module: Main.py
Author: Jacob       : Backend
        Marlenne    : Frontend

Description:
This module creates a graphical user interface (GUI) for user sign-in and registration. It allows users to sign up for a new account or log into an existing one. 
The module interacts with a database to handle user authentication, ensuring that only registered users can access the system. 
The sign-in page includes fields for entering a username and password, and buttons for performing sign-up or login actions.

Usage:
1. Run the Main.py to launch the sign-in window.
2. Users can either sign up by providing a username and password or log in if they already have an account.
3. The script calls appropriate functions from the `Database` module to handle user registration and authentication.


Dependencies:
- Tkinter (for GUI)
- Database module (for database operations like fetching songs, creating playlists, etc.)

"""

import tkinter as tk
from tkinter import PhotoImage
import Database
import os

# Creates the Sign in Page
root = tk.Tk()
root.title("Python Final Sign-In Page")
root.geometry("400x400")

# Basic UI for now
tk.Label(root, text="Username:").pack()
entry_username = tk.Entry(root)
entry_username.pack()

tk.Label(root, text="Password:").pack()
entry_password = tk.Entry(root, show="*")
entry_password.pack()

# Functions to sign in with database
tk.Button(root, text="Signup", command=lambda: Database.do_signup(entry_username, entry_password)).pack(pady=5)
tk.Button(root, text="Login", command=lambda: Database.do_login(entry_username, entry_password, root)).pack(pady=5)
absolute_path = os.path.dirname(os.path.abspath(__file__))
filename = os.path.join(absolute_path, "logo.png")
og_image = PhotoImage(file = filename)
image = og_image.subsample(6,6)
image_label = tk.Label(root, image = image)
image_label.pack()

# Runs the sign in page
root.mainloop()