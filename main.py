import time
from random import randint


class Ship:
    def __init__(self, bow, ship_len, rotation):
        self.bow = bow
        self.hp = ship_len
        self.ship_len = ship_len
        self.rotation = rotation

    @property
    def coordinates(self):
        ship_coordinates = []
        for i in range(self.ship_len):
            coordinate_x = self.bow.x
            coordinate_y = self.bow.y
            if self.rotation == 0:
                coordinate_x += i
            elif self.rotation == 1:
                coordinate_y += i
            ship_coordinates.append(Dot(coordinate_x, coordinate_y))
        return ship_coordinates


class Dot:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __repr__(self):
        return f'({self.x}, {self.y})'


class BoardException(Exception):
    pass


class BoardOutException(BoardException):
    def __str__(self):
        return "Shooting out of range!"


class BoardUsedException(BoardException):
    def __str__(self):
        return "You already shot at this point"


class BoardWrongShipException(BoardException):
    pass


class Board:
    def __init__(self, hidden_field=False, size=6):
        self.hidden_field = hidden_field
        self.size = size
        self.ships = []
        self.busy_dots = []
        self.ship_quantity = 0
        self.field = []
        for i in range(size):
            self.field.append(['0'] * size)

    def add_ship(self, ship):
        for coordinate in ship.coordinates:
            if self.out(coordinate) or coordinate in self.busy_dots:
                raise BoardWrongShipException()
        for coordinate in ship.coordinates:
            self.field[coordinate.x][coordinate.y] = "■"
            self.busy_dots.append(coordinate)
        self.ships.append(ship)
        self.contour(ship)
        self.ship_quantity += 1

    def contour(self, ship, verb = False):
        around = [
            (-1, -1), (-1, 0), (-1, 1),
            ( 0, -1), ( 0, 0), ( 0, 1),
            ( 1, -1), ( 1, 0), ( 1, 1)
        ]
        for coordinate in ship.coordinates:
            for dx, dy in around:
                coordinates = Dot(coordinate.x + dx, coordinate.y + dy)
                if not(self.out(coordinates)) and coordinates not in self.busy_dots:
                    if verb:
                        self.field[coordinates.x][coordinates.y] = "."
                    self.busy_dots.append(coordinates)

    def __str__(self):
        board = "      | "
        for i in range(self.size):
            board += f"{i+1} | "
        board += "\n" + "      |" + "   |" * self.size + "\n" + "------" + " ---" * self.size + "\n"
        vert_num = 1
        for x in self.field:
            board += f"  {vert_num}   | " + " | ".join(x) + " |" + "\n" + "------" + " ---" * self.size + "\n"
            vert_num += 1
        if self.hidden_field:
            board = board.replace("■", "0")
        return board

    def out(self, coordinate):
        if (0 <= coordinate.x < self.size) and (0 <= coordinate.y < self.size):
            return False
        else:
            return True

    def shot(self, coordinate):
        if self.out(coordinate):
            raise BoardOutException()

        if coordinate in self.busy_dots:
            raise BoardUsedException()

        self.busy_dots.append(coordinate)

        for ship in self.ships:
            if coordinate in ship.coordinates:
                ship.hp -= 1
                self.field[coordinate.x][coordinate.y] = "X"
                if ship.hp == 0:
                    self.ship_quantity -= 1
                    self.contour(ship, verb = True)
                    print("Ship destroyed!")
                    time.sleep(2)
                    return True
                else:
                    print("Ship wounded!")
                    time.sleep(2)
                    return True

        self.field[coordinate.x][coordinate.y] = "."
        print("Miss!")
        time.sleep(2)
        return False


    def begin(self):
        self.busy_dots = []


class Player:
    def __init__(self, board, enemy):
        self.board = board
        self.enemy = enemy

    def ask(self):
        raise NotImplementedError()

    def move(self):
        while True:
            try:
                target = self.ask()
                repeat = self.enemy.shot(target)
                return repeat
            except BoardException as e:
                print(e)


class AI(Player):
    def ask(self):
        d = Dot(randint(0, 5), randint(0, 5))
        print(f"AI move: {d.x + 1} {d.y + 1}")
        return d


class User(Player):
    def ask(self):
        while True:
            cords = input("Your move: ").split()

            if len(cords) != 2:
                print(" Input 2 coordinates! ")
                continue

            x, y = cords

            if not (x.isdigit()) or not (y.isdigit()):
                print(" Input numbers! ")
                continue

            x, y = int(x), int(y)

            return Dot(x - 1, y - 1)


class Game:
    def __init__(self, size = 6):
        self.size = size
        pl = self.random_board()
        co = self.random_board()
        co.hidden_field = True

        self.ai = AI(co, pl)
        self.us = User(pl, co)

    def random_board(self):
        board = None
        while board is None:
            board = self.random_place()
        return board

    def random_place(self):
        lens = [3, 2, 2, 1, 1, 1, 1]
        board = Board(size = self.size)
        attempts = 0
        for l in lens:
            while True:
                attempts += 1
                if attempts > 2000:
                    return None
                ship = Ship(Dot(randint(0, self.size), randint(0, self.size)), l, randint(0, 1))
                try:
                    board.add_ship(ship)
                    break
                except BoardWrongShipException:
                    pass
        board.begin()
        return board

    def loop(self):
        print('''
-------------------
    Welcome to
the sea battle game
-------------------
input format: x y 
 x - row number 
y - column number
''')
        time.sleep(4)
        num = 0
        while True:
            separator = "--------" + "----" * self.size
            print(f"\n{separator}\nPlayer's board:\n{self.us.board}\n Player's ships quantity: {self.us.board.ship_quantity}")
            print(f"\n{separator}\nAI's board:\n{self.ai.board}\n AI's ships quantity: {self.ai.board.ship_quantity}")
            time.sleep(2)
            if num % 2 == 0:
                print("\n" + "-" * 20)
                print("Player's move!")
                repeat = self.us.move()
            else:
                print("\n" + "-" * 20)
                print("AI's move!")
                repeat = self.ai.move()
            if repeat:
                num -= 1

            if self.ai.board.ship_quantity == 0:
                print("-" * 20)
                print("Player win!")
                break

            if self.us.board.ship_quantity == 0:
                print("-" * 20)
                print("AI win!")
                break
            num += 1


g = Game()
g.loop()
