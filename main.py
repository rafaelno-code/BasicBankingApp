import tkinter as tk
from tkinter import *
from tkinter import ttk
from tkinter.ttk import *

root = tk.Tk(screenName=None, baseName=None, className="bankingApp", useTk=1)
root.title("Rafa's Epic Banking App")

win_w, win_h = 600, 400

screen_w = root.winfo_screenwidth()
screen_h = root.winfo_screenheight()

x = (screen_w - win_w) // 2
y = (screen_h - win_h) // 2

root.geometry(f"{win_w}x{win_h}+{x}+{y}")

content = ttk.Frame()
content.pack(expand=True)
#title = ttk.Label(packFrame, text="Rafa's Tuff Banking App")
#title.pack()

signIn = ttk.Label(content, text="Sign in", font=30)
signIn.grid(row=0, column=0, columnspan=2, pady=(0,20))

userNameLabel = ttk.Label(content, text="Username")
userName = ttk.Entry(content)
userNameLabel.grid(row=1, column=0)
userName.grid(row=1, column=1)

passwordLabel = ttk.Label(content, text="Password")
password = ttk.Entry(content)
passwordLabel.grid(row=2, column=0)
password.grid(row=2, column=1)

signInButton = ttk.Button(content, text="Login", cursor="hand2")
signInButton.grid(row=3, column=0, columnspan=2)
Label(content, text="or if you aren't already:").grid(row=4, column=0)
enrollButton = ttk.Button(content, text="Enroll", cursor="hand2")
enrollButton.grid(row=4, column=1)

root.mainloop()

