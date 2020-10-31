from tkinter import *
import tkinter as tk
from tkinter import ttk
from pprint import pprint
from functools import partial
from cfg import Config
import tweepy
import psycopg2

root = Tk()
nameVariable = StringVar()
passwordVariable = StringVar()


# root.geometry('200x450')

class Window(Frame):
    def __init__(self, master=None):
        Frame.__init__(self, master)
        self.master = master


userNameLabel = Label(root, text="Naam", font=('Comic Sans MS', 12))
userNameLabel.pack()
userName = Entry(root, textvariable=nameVariable, relief=RAISED, font=('Comic Sans MS', 12))  # Creates name Input
userName.pack()

passwordLabel = Label(root, text="Wachtwoord", font=('Comic Sans MS', 12))
passwordLabel.pack()
password = Entry(root, textvariable=passwordVariable, relief=RAISED,
                 font=('Comic Sans MS', 12))  # Creates password Input

frame_container = Frame(root)
frame_container.pack()

canvas_container = Canvas(frame_container, height=100)
frame2 = Frame(canvas_container)
canvas_container.create_window((0, 0), window=frame2, anchor='nw')

frame2.pack()

scrollbar = Scrollbar(frame_container, orient="vertical", command=canvas_container.yview)

canvas_container.pack(side=LEFT)

frame_container.pack()
password.pack()  # Loads input into window


def submit():
    connection = False
    try:
        connection = psycopg2.connect(user="postgres",
                                      password="root",
                                      host="localhost",
                                      port="5432",
                                      database="ns")

        cursor = connection.cursor()

    except (Exception, psycopg2.Error) as error:
        print("Error while connecting to PostgreSQL", error)

    cursor.execute("SELECT * FROM users WHERE email = %s AND password = %s",
                   (nameVariable.get(), passwordVariable.get()))
    items = cursor.fetchall()
    if (len(items)):
        passwordLabel.pack_forget()
        password.pack_forget()
        userNameLabel.pack_forget()
        userName.pack_forget()
        loginButton.pack_forget()
        cursor.execute(
            "SELECT * FROM messages WHERE status IS NULL AND messages.id NOT IN(SELECT messagesId FROM moderation_status)",
            (nameVariable.get(), passwordVariable.get()))
        for item in cursor.fetchall():
            print(item)
            submit.button = Button(frame2, text=item[1], command=partial(popUp, item))
            submit.button.pack()
        scrollbar.pack(side=RIGHT, fill=Y)


def popUp(item):
    print(item)
    popUp.topLevel = tk.Toplevel()
    popUp.topLevel.wm_title("Window")

    l = ttk.Label(popUp.topLevel, text="Inhoud")
    l.grid(row=1, column=0)
    T = tk.Label(popUp.topLevel, text=item[1])
    T.grid(row=1, column=1)

    naam = ttk.Label(popUp.topLevel, text="Naam")
    naam.grid(row=2, column=0)
    naamText = tk.Label(popUp.topLevel, text=item[3])
    naamText.grid(row=2, column=1)

    datum = ttk.Label(popUp.topLevel, text="Datum")
    datum.grid(row=3, column=0)
    datumContent = tk.Label(popUp.topLevel, text=f"{item[2]:%a, %b %d %Y}")
    datumContent.grid(row=3, column=1)

    approve = tk.Button(popUp.topLevel, text="Approve", background="green",
                        command=partial(checkMessage, item, "Approve"))
    approve.grid(row=4, column=0)

    reject = tk.Button(popUp.topLevel, text="Reject", background="red", command=partial(checkMessage, item, "Reject"))
    reject.grid(row=4, column=1)


def checkMessage(item, status):
    print(item)

    checkMessage.statusPopup = tk.Toplevel()
    checkMessage.statusPopup.wm_title(status + " Message")
    mystring = StringVar()
    messageLabel = ttk.Label(checkMessage.statusPopup, text="bericht")
    messageLabel.grid(row=1, column=0)
    checkMessage.messageItem = Text(checkMessage.statusPopup, relief=RAISED, font=('Comic Sans MS', 12), width=33,
                                    height=4)
    checkMessage.messageItem.grid(row=1, column=1)
    print(checkMessage.messageItem.get("1.0", "end-1c"))
    submit = tk.Button(checkMessage.statusPopup, text="Submit", background="blue",
                       command=partial(submitMessage, item, status, checkMessage.messageItem))
    submit.grid(row=4)


def submitMessage(item, status, message):
    try:
        connection = psycopg2.connect(user="postgres",
                                      password="root",
                                      host="localhost",
                                      port="5432",
                                      database="ns")

        cursor = connection.cursor()
        # Print PostgreSQL Connection properties
        # print(connection.get_dsn_parameters(), "\n")

        # Print PostgreSQL version
        cursor.execute("SELECT version();")
        record = cursor.fetchone()
        # print("You are connected to - ", record, "\n")

    except (Exception, psycopg2.Error) as error:
        print("Error while connecting to PostgreSQL", error)

    cursor.execute("INSERT INTO moderation_status (messagesId, userEmail, status, message) VALUES (%s, %s, %s, %s)",
                   (item[0], nameVariable.get(), status, message.get("1.0", "end-1c")))
    auth = tweepy.OAuthHandler(Config.consumer_key, Config.consumer_secret)
    auth.set_access_token(Config.access_token, Config.access_token_secret)
    api = tweepy.API(auth)
    print("test")
    print(message.get("1.0", "end-1c"))
    api.update_status(item[1])

    frame2.destroy()

    newFrame = Frame(canvas_container)
    canvas_container.create_window((0, 0), window=newFrame, anchor='nw')

    newFrame.pack()

    cursor.execute(
        "SELECT * FROM messages WHERE status IS NULL AND messages.id NOT IN(SELECT messagesId FROM moderation_status)",
        (nameVariable.get(), passwordVariable.get()))

    for item in cursor.fetchall():
        print(item)
        button = Button(newFrame, text=item[1], command=partial(popUp, item))
        button.pack()
        # messages.insert(item[0], item[1])
    scrollbar.pack(side=RIGHT, fill=Y)

    connection.commit()
    popUp.topLevel.destroy()
    checkMessage.statusPopup.destroy()


loginButton = Button(root, text="submit", command=submit, font=('Comic Sans MS', 12), fg="green", background="pink")
loginButton.pack()
app = Window(root)
root.mainloop()
