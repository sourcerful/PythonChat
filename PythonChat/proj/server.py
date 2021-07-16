"""
Server for multithreaded chat application. for any new client that the server gets, he's asked
for his name, and shows everyone who joined.
(This is a prototype)
"""
import socket
import threading


class ChatServer:
    """
    This class activates the server and creates a listening socket so clients can connect.
    """
    clients_list = []
    last_received_message = ""

    def __init__(self):
        """
        The constructor of the server class.
        """
        self.server_socket = None
        self.create_listening_server()

    def create_listening_server(self):
        """
        This function creates the listening socket of the server, making the server
        wait for incoming connections.
        :return:
        """
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        local_ip = '127.0.0.1'
        local_port = 10319
        # this will allow you to immediately restart a TCP server
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # this makes the server listen to requests coming from other computers on the network
        self.server_socket.bind((local_ip, local_port))
        print("Listening for incoming messages..")
        self.server_socket.listen(5)
        self.receive_messages_in_a_new_thread()

    def receive_messages(self, so):
        """
        This function is always waiting for messages and receiving them, and after
        receiving the messages, calls a function that broadcasts the messages to all
        the clients.
        :param so: The socket between the server and the current client.
        :return: None
        """
        while True:
            incoming_buffer = so.recv(1024)
            if not incoming_buffer:
                break
            self.last_received_message = incoming_buffer.decode('utf-8')
            self.broadcast_to_all_clients(so)  # send to all clients
        so.close()

    def broadcast_to_all_clients(self, senders_socket):
        """
        This function broadcasts the message it was given to all the clients
        connected to the server.
        :param senders_socket: The socket of the client who sent the message.
        :return: None
        """
        for client in self.clients_list:
            socket, (ip, port) = client
            print("Message from ('{}', '{}')".format(ip, port))
            if socket is not senders_socket:
                socket.sendall(self.last_received_message.encode('utf-8'))

    def receive_messages_in_a_new_thread(self):
        """
        This function allows the server to always accept new connections from new
        clients and makes sure the server is always receiving messages, by calling a
        thread.
        :return: None
        """
        while True:
            client = so, (ip, port) = self.server_socket.accept()
            print(client)
            self.add_to_clients_list(client)
            print('Connected to ', ip, ':', str(port))
            t = threading.Thread(target=self.receive_messages, args=(so,))
            t.start()

    def add_to_clients_list(self, client):
        """
        This function adds the current client to the clients list, that includes all the clients
        connected to the server.
        :param client: The new client who connected to the server.
        :return: None
        """
        if client not in self.clients_list:
            self.clients_list.append(client)

def main():
    ChatServer()

if __name__ == "__main__":
    main()