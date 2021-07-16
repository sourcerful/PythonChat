from tkinter import Tk, Frame, Scrollbar, Label, END, Entry, Text, VERTICAL, Button
import socket
import threading
from tkinter import messagebox


class GUI:
    """
    This class initializes the GUI for the client, and creates the socket between the client and the server.
    """
    client_socket = None
    last_received_message = None

    def __init__(self, master):
        """
        The constructor of the GUI class
        :param master: the root of the GUI
        """
        self.root = master
        self.chat_transcript_area = None
        self.name_widget = None
        self.enter_text_widget = None
        self.join_button = None
        self.play_button = None
        self.initialize_socket()
        self.initialize_gui()
        self.listen_for_incoming_messages_in_a_thread()

    def initialize_socket(self):
        """
        This function creates the socket and connects the client to the server.
        :return: None
        """
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        remote_ip = '127.0.0.1'
        remote_port = 10319
        try:
            self.client_socket.connect((remote_ip, remote_port))
        except Exception:
            print("Couldn't connect to server.")

    def initialize_gui(self):
        """
        This function starts initializing the Graphical User Interface of the program-
        creating the window the program is based on.
        :return: None
        """
        self.root.title("Socket Chat")
        self.root.resizable(0, 0)
        self.display_chat_box()
        self.display_name_section()
        self.display_chat_entry_box()

    def listen_for_incoming_messages_in_a_thread(self):
        """
        This function opens a thread that always listens to incoming messages
        and works all the time.
        :return: None
        """
        thread = threading.Thread(target=self.receive_message_from_server, args=(self.client_socket,))
        thread.start()

    def receive_message_from_server(self, so):
        """
        This function is always waiting for messages to receive in an infinite loop
        and once it receives a message it functions accordingly.
        :param so: the socket between the client and the server
        :return: None
        """
        while True:
            buffer = so.recv(1024)
            if not buffer:
                break
            message = buffer.decode('utf-8')
            if "joined" in message:
                self.user = message.split(":")[1]
                message = self.user + " has joined"
                self.chat_transcript_area.insert('end', message + '\n')
                self.chat_transcript_area.yview(END)
            else:
                self.chat_transcript_area.insert('end', message + '\n')
                self.chat_transcript_area.yview(END)

        so.close()

    def display_name_section(self):
        """
        This function displays on the window in a frame the label and the Entry to write
        the name of the client, and displays the JOIN and PLAY buttons to use.
        :return: None
        """
        frame = Frame()
        Label(frame, text='Enter your name :', font=("Helvetica", 16)).pack(side='left', padx=10)
        self.name_widget = Entry(frame, width=50, borderwidth=2)
        self.name_widget.pack(side='left', anchor='e')
        self.join_button = Button(frame, text="Join", width=10, command=self.on_join).pack(side='top')
        self.play_button = Button(frame, text="Play", width=10, command=self.start_game).pack(side='bottom') #display play button
        frame.pack(side='top', anchor='nw')

    def start_game(self):
        """
        This functions starts the game between the 2 clients who entered.
        :return: None
        """
        if len(self.name_widget.get()) == 0:
            messagebox.showerror("Enter your name", "Enter your name to play")
            return
        self.client_socket.send("{} is looking for a game!".format(self.name_widget.get()).encode('utf-8'))
        self.popupmsg()

    def popupmsg(self):
        """
        This function pops up a window that shows that the server is waiting for
        another player to press PLAY and play against the client.
         the client can wait, or it can cancel the search.
        :return: None
        """
        popup = Tk()
        popup.geometry('300x100')
        popup.wm_title("Waiting")
        label = Label(popup, text="Waiting for a player...", font=("Verdana", 10))
        label.pack(side="top", fill="x", pady=10)
        B1 = Button(popup, text="Cancel", command=popup.destroy)
        B1.pack()
        popup.mainloop()

    def display_chat_box(self):
        """
        This function displays the chat box - the chat box is where all the messages
        are written such as - who joined, what messages are displayed, who left and who
        is searching for a player to play with.
        :return: None
        """
        frame = Frame()
        Label(frame, text='Chat Box:', font=("Serif", 12)).pack(side='top', anchor='w')
        self.chat_transcript_area = Text(frame, width=60, height=10, font=("Serif", 12))
        scrollbar = Scrollbar(frame, command=self.chat_transcript_area.yview, orient=VERTICAL)
        self.chat_transcript_area.config(yscrollcommand=scrollbar.set)
        self.chat_transcript_area.bind('<KeyPress>', lambda e: 'break')
        self.chat_transcript_area.pack(side='left', padx=10)
        scrollbar.pack(side='right', fill='y')
        frame.pack(side='top')

    def display_chat_entry_box(self):
        """
        This function displays the chat entry box. The chat entry box is where
        the user can write what he wants and send his message to the other users
        connected to the server.
        :return: None
        """
        frame = Frame()
        Label(frame, text='Enter message:', font=("Serif", 12)).pack(side='top', anchor='w')
        self.enter_text_widget = Text(frame, width=60, height=3, font=("Serif", 12))
        self.enter_text_widget.pack(side='left', pady=15)
        self.enter_text_widget.bind('<Return>', self.on_enter_key_pressed)
        frame.pack(side='top')

    def on_join(self):
        """
        This function checks if the user has entered a name and acts accordingly, if the
        user entered a name the function sends it to the server to display it on the
        chat box.
        :return: None
        """
        if len(self.name_widget.get()) == 0:
            messagebox.showerror("Enter your name", "Enter your name to send a message")
            return
        self.name_widget.config(state='disabled')
        self.client_socket.send(("joined:" + self.name_widget.get()).encode('utf-8'))

    def on_enter_key_pressed(self, event):
        """
        This function checks if the user entered a name and sends the message
        the user has entered after pressing the ENTER key.
        :param event: ENTER key
        :return: None
        """
        if len(self.name_widget.get()) == 0:
            messagebox.showerror("Enter your name", "Enter your name to send a message")
            return
        self.send_chat()
        self.clear_text()

    def clear_text(self):
        """
        This function allows the option of deleting the message the user is
        writing during his writing.
        :return: None
        """
        self.enter_text_widget.delete(1.0, 'end')

    def send_chat(self):
        """
        This function is responsible for sending the user data to the
        server.
        :return: 'break' (str)
        """
        senders_name = self.name_widget.get().strip() + ": "
        data = self.enter_text_widget.get(1.0, 'end').strip()
        message = (senders_name + data).encode('utf-8')
        self.chat_transcript_area.insert('end', message.decode('utf-8') + '\n')
        self.chat_transcript_area.yview(END)
        self.client_socket.send(message)
        self.enter_text_widget.delete(1.0, 'end')
        return 'break'

    def on_close_window(self):
        """
        This function is responsible for the user quitting the chat and making sure he
        wants it. After the user quits the chat the function alerts the server by sending
        a message saying the user has left and later it gets displayed on the chat box.
        :return: None
        """
        if messagebox.askokcancel("Quit", "Do you want to quit?"):
            self.client_socket.send("{} has left".format(self.name_widget.get()).encode('utf-8'))
            self.root.destroy()
            self.client_socket.close()
            exit(0)

def main():
    root = Tk()
    gui = GUI(root)
    root.protocol("WM_DELETE_WINDOW", gui.on_close_window)
    root.mainloop()

if __name__ == '__main__':
    main()