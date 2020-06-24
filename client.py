import socket
import time


class Client:
    """
    Client class:
    Fields: client's socket as s, host - server's Ip, port - server's port
    """
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.s = None

    def read_input(self):
        """
        read_input - read's and handles the input from the client to fit the game session
        If input is invalid - ask's again
        """
        while True:
            try:
                bet = input("What is your'e next move:")

                if bet.lower() == 'log' or bet.lower() == 'war' or bet.lower() == 'log' or bet.lower() == 'yes' or bet.lower() == 'no' or bet.lower() == 'surrender' or bet.lower() == 'quit':
                    return bet.lower()
                elif int(bet):
                    return 'b' + str(bet)
                elif bet.lower() == 'info':
                    self.print_info()
                else:
                    print("Error: invalid input. read the following input rules:")
                    self.print_info()
            except TypeError or ValueError:
                self.print_info()

    def print_info(self):
        """
        When invalid input is given - print this msg
        """
        return "Input info:\nBet: numbers only || Log request = log || Quit = quit || Accept war = war || Surrender war = surrender ||"

    def utf8_len(self, string):
        """
        Made it but didnt used it - checks the length of the string given
        """
        return len(string.encode('utf-8'))

    def making_connection(self):
        """
        Create a socket for the client and connect's to the server's socket if accepted
        If game session is valid - send to handling_connection method to handle game session.
        """

        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        message = "I want to play WAR"
        while True:
            try:
                self.s.connect((self.host, self.port))
                self.s.sendall(message.encode())
                data = str(self.s.recv(4096).decode('utf-8'))
                if data.lower() == "request denied":
                    print("Game request denied")
                    break

                else:
                    print("Hello! While playing Please select your action according to the following:\nBet: integers only.\nLog request = log.\nQuit = quit.\n"
                          "Accepting War = war.\nSurrendering war = surrender.\nPlaying again(end game) = yes.\nDeclining to play again = no.\n")
                    print(f"Your card is:{data[28:]}")
                    self.handling_connection()
                    break

            except OSError:
                print("OSError: connection lost")
                break

        # close the connection and process
        self.s.close()
        self.s = None
        time.sleep(5)
        exit("Client closed")

    def check_end(self, data):
        """
        Check's if  this msg given from server is an game_over msg - according to the header of it as 0.
        """
        if data[0] == '0':
            return False
        else:
            return True

    def handling_connection(self):
        """
        Handle a full game session including if the player want's to play again.
        """
        playing = True

        while playing:
            msg = self.read_input()
            self.s.sendall(msg.encode('utf-8'))

            while True:
                data = str(self.s.recv(4096 * 2).decode('utf-8'))
                header = data[0]

                if header == '1' or header == '2':
                    print(data[1:])

                elif header == '6':
                    print(data[1:])
                    msg = self.read_input()
                    self.s.sendall(msg.encode())

                elif header == '3':
                    print(data[1:])
                    msg = input()                  # war or surrender
                    while msg != "war" and msg != "surrender":
                        print("Input Error: Type war or surrender")
                        msg = input()
                    self.s.sendall(msg.encode())
                    data = str(self.s.recv(4096).decode('utf-8'))
                    print(data)

                elif header == '4':
                    print(data[1:])
                    msg = self.read_input()
                    self.s.sendall(msg.encode())

                elif header == '5':
                    print(data[1:])
                    playing = False
                    break

                elif header == '0':
                    print(data[1:])
                    msg = input()                    # yes or no only
                    while msg != 'yes' and msg != 'no':
                        print("Input Error: Type yes or no")
                        msg = input()
                    self.s.sendall(msg.encode())
                    if msg == 'yes':
                        data = str(self.s.recv(4096 * 2).decode('utf-8'))
                        print(f"Your card is:{data[28:]}")
                        self.handling_connection()
                        playing = False
                        break
                    else:
                        data = str(self.s.recv(4096 * 2).decode('utf-8'))
                        print(data)
                        playing = False
                        break


def main():
    my_name = socket.gethostname()
    my_host = socket.gethostbyname(my_name)
    server_port = 5555
    client1 = Client(my_host, server_port)
    client1.making_connection()


main()
