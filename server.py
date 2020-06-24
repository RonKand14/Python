import socket
import random
from _thread import *
import time


"""
I have created Dict obj and list obj to help generate a Card class
"""
values = {'Two': 2, 'Three': 3, 'Four': 4, 'Five': 5, 'Six': 6, 'Seven': 7, 'Eight': 8, 'Nine': 9, 'Ten': 10,
          'J': 11, 'Q': 12, 'K': 13, 'A': 14}
suits = ('H', 'C', 'D', 'S')     # H = Heart , C = Clubs, D = Diamond, S = Spade


# Classes: Card, Deck, War, Server.
class Card:
    """
    Card class: Need to insert a suit and a value to create object.
                Has a __str__ method to print a card as requested
    """
    def __init__(self, suit, value):
        self.value = value
        self.suit = suit

    def __str__(self):
        if self.value == 11:
            return f"J{self.suit}"
        elif self.value == 12:
            return f"Q{self.suit}"
        elif self.value == 13:
            return f"K{self.suit}"
        elif self.value == 14:
            return f"A{self.suit}"
        else:
            return f"{self.value}{self.suit}"


class Deck:
    """
    Deck class: In creating an object Generates a deck of 52 cards. Had
    Methods:
    shuffle - shuffles the deck || deal  - return the first card on the deck and deletes it from it ||
    __len__ - return's the the number of cad's in the deck. || deal_hands - split the deck to 2 equal half's and return them as a tuple.
    """
    def __init__(self):
        self.deck = []
        for suit in suits:
            for value in range(2, 15):
                self.deck.append(Card(suit, value))

    def deal(self):                             # Delete the card from the deck and return the card print style
        card = self.deck[0]
        del self.deck[0]
        return card.__str__()

    def shuffle(self):                          # shuffles the deck with random
        random.shuffle(self.deck)

    def __len__(self):
        count = 0
        for i in self.deck:
            count += 1
        return count

    def deal_hands(self):                     # Generate and return 2 decks from 1 - 26 cards each
        first_hand = []
        second_hand = []
        for i in range(0, 52):
            if i < 26:
                first_hand.append(self.deck[i])
            else:
                second_hand.append(self.deck[i])
        return first_hand, second_hand


class War:
    """
    War class.
    Supports one game session. Designed for 2 equal lists of cards to start a game session.
    Method description:
        game_check
        compare_cards
        deal
        update
        create_msg
        war
        getCard
        bad_input
    IMPORTANT:
    Each deal method activation will go to the next round.
    """
    def __init__(self, lst1, lst2):
        self.server_hand = lst1
        self.player_hand = lst2
        self.server_card = lst1[0]
        self.player_card = lst2[0]
        self.cards_left = len(lst1)
        self.balance = 0
        self.round = 0
        self.bet = 0
        self.round_result = 0
        self.player_request = 0
        self.win = 0                # used to generate the correct msg when ending the game

    def get_card(self):
        """Returns the player card field"""

        return self.player_card

    def bad_input(self):
        """Returns a string that displays the correct input expected from the player."""

        msg = "Invalid message! Please select your action according to the following:\nBet: integers only.\nLog request = log.\n" \
              "Quit = quit.\n Accepting War = war.\nSurrendering war = surrender.\nPlaying again(end game) = yes.\n Declining to play again = no."
        return msg

    def game_check(self):
        """
        Check's if the deck is empty. Return value: True if none empty || False empty. updated fields: player_request
        TODO: NEEDS MORE WORK FOR LOGIC!
        """
        if self.cards_left == 0:
            self.player_request = 7
            return False
        else:
            return True

    def compare_cards(self):
        """
        Compares between the player and server cards. Return value's: player wins = 2 || server wins = 1 || draw = 0
        """
        if self.player_card.value > self.server_card.value:
            return 2
        elif self.player_card.value < self.server_card.value:
            return 1
        else:
            return 0

    def deal(self):
        """
        Deals and discard a card from each deck a card and updates the player and server card field
        As well, updates cards left field(-1), round field(+1) and round result.
        """
        s_card = self.server_hand[0]
        p_card = self.player_hand[0]
        self.server_card = s_card
        self.player_card = p_card
        del self.server_hand[0]
        del self.player_hand[0]
        self.round_result = self.compare_cards()
        self.round += 1
        self.cards_left -= 1
        self.server_card = s_card
        self.player_card = p_card
        return p_card

    def war(self):
        """
        If player chooses WAR: discard 3 cards(or less) and updating card left field and activate deal method.
        Returns the player card and updates fields by using deal method.
        """
        if self.cards_left >= 4:
            del self.server_hand[0:2]
            del self.player_hand[0:2]
            self.cards_left -= 3
            return self.deal()
        elif self.cards_left == 3:
            del self.server_hand[0:1]
            del self.player_hand[0:1]
            self.cards_left -= 2
            return self.deal()
        elif self.cards_left == 2:
            del self.server_hand[0]
            del self.player_hand[0]
            self.cards_left -= 1
            return self.deal()
        else:
            return self.deal()

    def update(self, msg):
        """
        Pass this function the client msg to check the type of msg.
        Updates the field player_request according to player msg:
        0 = bet was placed
        1 = log request
        2 =  mid game quit
        3 = WAR
        4 = surrender
        5 = invalid msg
        6 = play again
        7 = game over
        """
        if self.balance > 0:
            self.win = 1
        else:
            self.balance = 0

        if msg.lower()[0] == 'b':
            self.bet = int(msg[1:])
            self.player_request = 0
            return True
        elif msg.lower() == 'log':
            self.player_request = 1
            return True
        elif msg.lower() == 'quit':
            self.player_request = 2
            return True
        elif msg.lower() == 'war':
            self.player_request = 3
            self.war()
            return True
        elif msg.lower() == 'surrender':
            self.player_request = 4
            return True
        elif msg.lower() == 'yes':     # TODO: Needs to handles this to create new War obj - in server?
            self.player_request = 6
            return True                 # Todo: change later

        elif msg.lower() == 'no':
            self.player_request = 7
            return True
        else:
            self.player_request = 5
            self.bad_input()
            return False

    def create_msg(self):
        """
        Generate a message according to the round_result field and player_request field
        Returns the message as it should be printed to the player console
        Each msg has a header from '0'-'5'.
        Updates the balance fields on th object.
        """
        if self.player_request == 0:         # REGULAR ROUND MSG
            if self.round_result == 2:                                                 # player wins
                self.balance += self.bet
                msg = f"1The result of round {self.round}:\nPlayer won: {self.bet}$\n" \
                      f"Dealer’s card: {self.server_card}\nPlayer’s card: {self.player_card}\n"
            elif self.round_result == 1:                                                # dealer win
                self.balance -= self.bet
                msg = f"2The result of round {self.round}:\nDealer won: {self.bet}$\n" \
                      f"Dealer’s card: {self.server_card}\nPlayer’s card: {self.player_card}\n"
            else:                                                                       # draw
                msg = f"3The result of round {self.round} is a tie!\nDealer’s card: {self.server_card}\n" \
                      f"Player’s card: {self.player_card}\nDo you wish to surrender or go to war? Type: war / surrender"

        elif self.player_request == 1:         # LOG REQUEST
            msg = f"4Current round: {self.round}\nPlayer balance: {self.balance}\n"
            pass

        elif self.player_request == 2:                                                  # quit mid game
            msg = f"5The game has ended on round {self.round}\nThe player choose to quit\n" \
                  f"Player's balance: {self.balance}\nThank you for playing "

        elif self.player_request == 3:           # WAR MSG
            if self.round_result == 2:                                                  # player wins war
                msg = f"Round 1 tie breaker:\nGoing to WAR!\n3 cards were discarded.\n" \
                      f"Original bet: {self.bet}$\nNew bet: {self.bet*2}$\n" \
                      f"Dealer card: {self.server_card}\nPlayer card: {self.player_card}\nPlayer won: {self.bet}$\n"
            elif self.round_result == 1:                                                # player loses war
                msg = f"Round 1 tie breaker:\nGoing to WAR!\n3 cards were discarded.\n" \
                      f"Original bet: {self.bet}$\nNew bet: {self.bet * 2}$\n" \
                      f"Dealer card: {self.server_card}\nPlayer card: {self.player_card}\nDealer won: {self.bet*2}$\n"
            else:                                                                        # another draw - player wins and doubles the bet
                msg = f"Round 1 tie breaker:\nGoing to WAR!\n3 cards were discarded.\n" \
                      f"Original bet: {self.bet}$\nNew bet: {self.bet * 2}$\n" \
                      f"Dealer card: {self.server_card}\nPlayer card: {self.player_card}\nPlayer won: {self.bet*2}$\n"

        elif self.player_request == 4:            # SURRENDER MSG
            msg = f"Round 1 tie breaker:\nPlayer surrendered!\nThe bet: {self.bet}\n" \
                    f"Dealer won: {self.bet / 2}$\nPlayer won: {self.bet / 2}$\n"

        else:                                        # GAME OVER
            if self.win == 1:                                                           # player balance > 0
                msg = f"0The game has ended!\nPlayer balance: {self.balance}$\nPlayer is the winner!\n" \
                      f"Would you like to play again? Type: yes/no"
            else:                                                                       # player balance < 0
                msg = f"0The game has ended!\nPlayer balance: {self.balance}$\nDealer is the winner!\n" \
                      f"Would you like to play again? Type: yes/no"

        return msg


class Server:
    """
    Server class:
    Need to pass host(IPv4 address like) and port number to create an object.
    Track's the number of players connected, socket,host and port.
    Methods:
        create_socket
        bind_socket
        accepting_connection
        threaded_client
    """
    def __init__(self, host, port):
        self.NUM_OF_PLAYERS = 0
        self.host = host
        self.port = port
        self.s = None
        self.all_connections = []
        self.all_addr = []

    def create_socket(self):
        """
        Create's a socket with AF_INET address family and type: SOCK_STREAM - updates the object socket field.
        """
        try:
            self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        except socket.error as msg:
            print("Socket creation error: " + str(msg))

    def bind_socket(self):
        """
        Bind's the object's socket to the host and port (fields)
        Use socket.listen to listen for connection's
        Using recursion to loop until bind it successful.
        """
        try:
            print("Binding the Port: " + str(self.port))
            self.s.bind((self.host, self.port))
            self.s.listen()
            return True

        except socket.error as msg:
            print("Socket Binding error" + str(msg))
            return False

    def accepting_connections(self):
        """
        Infinite loop to handle incoming connection request from clients - to close server just press any key whi;e in server console.
        Supports 2 parallel connection, if 2 clients is connected send's denied answer to the client.
        Send's the connected client to threaded_client method to start a game session and keeps looking for connection's.
        the time.sleep function is get the server  the time to update itself while a client disconnect's to support the next connection.
        """
        self.s.setblocking(True)

        while True:
            try:
                conn, addr = self.s.accept()
                conn.settimeout(30)                 # Prevent's idle client to take place without playing
                if self.NUM_OF_PLAYERS < 2:
                    self.NUM_OF_PLAYERS += 1
                    data = str(conn.recv(4096).decode('utf-8'))
                    print(f"Received from {addr}: {data}")
                    print("Connection has been established with: " + addr[0])
                    start_new_thread(self.threaded_client, (conn,))

                else:
                    data = conn.recv(4096).decode('utf-8')
                    print(f"Received from {addr}: {data}")
                    conn.sendall("request denied".encode())
                    print(f"No connection was made with: {addr}")
                    conn.close()

            except OSError:
                pass
            except KeyboardInterrupt:
                break
            except TimeoutError:
                print("Idle client - closing connection")

    def threaded_client(self, conn):
        """
        Handles the logic. each connected client triggers this function activation.
        Messaging from and to the client it dealt in this function.
        """
        playing = True
        with conn:
            try:
                while playing:
                    deck1 = Deck()
                    deck1.shuffle()
                    hand1, hand2 = deck1.deal_hands()
                    war = War(hand1, hand2)
                    open_msg = "Game accepted, " + "your card is:" + str(war.deal())
                    conn.sendall(open_msg.encode())

                    while war.game_check():
                        data = str(conn.recv(4096).decode('utf-8'))
                        war.update(data)

                        if war.player_request == 0:
                            conn.sendall(war.create_msg().encode())
                            if war.round_result == 0:
                                data = str(conn.recv(4096).decode('utf-8'))
                                war.update(data)
                                conn.sendall(war.create_msg().encode())
                                war.game_check()
                                if war.player_request == 7:                     # TODO: fix the logic here so look more elegant
                                    conn.sendall(war.create_msg().encode())
                                    break
                                msg = "6Your card is:" + str(war.deal())
                                conn.sendall(msg.encode())
                            else:
                                msg = "6Your card is:" + str(war.deal())
                                conn.sendall(msg.encode())

                        elif war.player_request == 1:
                            conn.sendall(war.create_msg().encode())

                        elif war.player_request == 2:
                            conn.sendall(war.create_msg().encode())
                            print("Closing connection")
                            playing = False
                            break

                    # Deck is empty
                    # TODO: fix the logic here so look more elegant
                    data = str(conn.recv(4096).decode('utf-8'))
                    if data:
                        if data != 'yes' and data != 'no':
                            war.update(data)
                            conn.sendall(war.create_msg().encode())
                            war.game_check()
                            conn.sendall(war.create_msg().encode())
                            ending_msg = str(conn.recv(4096).decode('utf-8'))
                            if ending_msg != 'yes':
                                conn.sendall("Closing connection".encode())
                                playing = False
                                break
                        else:
                            if data == 'no':
                                conn.sendall("Closing connection".encode())
                                playing = False
                                break

            except OSError:
                playing = False

        self.NUM_OF_PLAYERS -= 1
        print(f"Connection closed with: {conn}")


# MAIN FUNCTION TO START SET UP THE SERVER
def main():
    host = socket.gethostname()
    addr = socket.gethostbyname(host)
    port = 5555
    print(f"Host name: {host}. Host IPv4 is: {addr}. Port: 5555")
    server = Server(addr, port)
    server.create_socket()
    server.bind_socket()
    server.accepting_connections()


main()

