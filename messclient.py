import socket
import threading
from datetime import datetime
import tkinter as tk
from tkinter import *

HEADERSIZE = 10
chat_log = ["--Chat Begin--"]

def update_dis():
     log.config(state=NORMAL)
     log.insert(tk.END, chat_log[len(chat_log)-1])
     log.config(state=DISABLED)
     log.see("end")


def send_msg(msg):
     msgbox.delete(0, END)
     if msg:
          msg = USERNAME + ": " + msg  # Add username to message
     # Add time to message
     now = datetime.now()
     current_time = now.strftime("%H:%M")
     if msg:
          msg = "\n" + "["+current_time+"]"+" "+msg
     msg = f"{len(msg):<{HEADERSIZE}}"+msg # Prepend header
     s.sendall(bytes(msg,"ascii"))
     chat_log.append(msg[HEADERSIZE:])
     update_dis()


def status_msg(type):
     now = datetime.now()
     current_time = now.strftime("%H:%M")
     msg = "\n" + "["+current_time+"]"+" "
     
     # no switch statements why :(
     if type == "Disconnect":
          msg = msg + USERNAME+" disconnected"
     
     msg = f"{len(msg):<{HEADERSIZE}}"+msg # Prepend header
     s.sendall(bytes(msg,"ascii"))
     chat_log.append(msg[HEADERSIZE:])
     update_dis()


def receive_msg(csocket):
     full_msg = b''
     new_msg = True
     # Decode in 16 byte chunks
     while True:
          msg = csocket.recv(16)
          if new_msg:
          #    print(msg)
          #    print("New message length: ", msg[:HEADERSIZE])
               msg_len = int(msg[:HEADERSIZE])
               new_msg = False
          
          # print(f"Full message length: {msg_len}")
          full_msg += msg
          if len(full_msg) - HEADERSIZE == msg_len: # If we have decoded the full message
               # print("Full message recieved")
               chat_log.append(full_msg[HEADERSIZE:])
               update_dis()
               new_msg = True
               full_msg = b''
     return full_msg


def disconnect(csocket):
     try:
          # try because if it doesnt work that most likely means the other person already disconnected
          status_msg("Disconnect") # Send disconnect message
          csocket.close()
     finally:
          exit()


def thread_recv(csocket):
     while True:
          receive_msg(csocket)


USERNAME = input("Enter Client Username: ")
IPV4     = input("Enter Server IPv4 (Default, Localhost): ")
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
if IPV4:
     s.connect((IPV4, 1337))
else:
     s.connect((socket.gethostname(), 1337))

# Multithreading madness
recv_thread = threading.Thread(target=thread_recv, args=(s,))
recv_thread.start()

# GUI

# GUI loading
root = tk.Tk()
root.title("PesterChum")
root.geometry('620x500')

# GUI elements
title =    tk.Label(text = "PesterChum", font = ("Courier", 32))
subtitle = tk.Label(text = USERNAME, font = ("Courier", 16))
log =      tk.Text(wrap = WORD, width = 83, font= ("Courier", 8))
msgbox =   tk.Entry(width = 78, font= ("Courier", 8))
send =     tk.Button(text = "Send", width = 6, command=lambda: send_msg(msgbox.get()))
disc =     tk.Button(text="Disconnect", width = 12, command=lambda: disconnect(s))

log.insert(tk.END, chat_log[0])
log.config(state=DISABLED)

# GUI packing
title.grid(    row = 1, column = 1, columnspan = 2)
subtitle.grid( row = 2, column = 1, columnspan = 2)
log.grid(      row = 3, column = 1, columnspan = 2)
msgbox.grid(   row = 4, column = 1)
send.grid(     row = 4, column = 2)
disc.grid(     row = 5, column = 1, columnspan = 2)

# GUI shortcuts
root.bind("<Return>", lambda event: send_msg(msgbox.get()))

# GUI center
root.grid_rowconfigure(0, weight = 1)
root.grid_rowconfigure(400, weight = 1)
root.grid_columnconfigure(0, weight = 1)
root.grid_columnconfigure(400, weight = 1)

# GUI execution
root.mainloop()
    