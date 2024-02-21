from random import randint


class Dot:
    """ Класс координат"""
    def __init__(self, x ,y):
        self.x = x
        self.y = y

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __repr__(self):
        return f"Dot({self.x}, {self.y})"


"""Классы исключения"""
class BoardException(Exception):
    pass


class BoardOutException(BoardException):
    def __str__(self):
        return  "Выстрел по суше"


class BoardUsedException(BoardException):

    def __str__(self):
        return  "Выстрел в эту точку уже был"


class BoardWrongShipException(BoardException):

    pass


class Ship:
    """Класс корадль"""
    def __init__(self, bow, l, o,live):
        self.bow = bow
        self.l = l
        self.o = o
        self.live = live

    @property
    def dots(self):
        ship_dots = []
        for i in range(self.l):
            cur_x = self.bow.x
            cur_y = self.bow.y

            if self.o == 0:
                cur_x += i
            elif self.o == 1:
                cur_y += i
            ship_dots.append(Dot(cur_x, cur_y))
        return ship_dots

    def shooten(self, shot):
        return shot in self.dots


class Mapa:
    """Класс карты и взаимодействие с игровой картой"""
    def __init__(self, hid=False, size=6):
        self.hid = hid
        self.size = size


        self.count = 0

        self.field = [["O"]*size for _ in range(size)]

        self.busy = []
        self.ships = []


    def __str__(self):
        res = ""
        res += "  | 1 | 2 | 3 | 4 | 5 | 6 |"
        for i, row in enumerate(self.field):
            res += f"\n{i + 1} | " + " | ".join(row) + " |"

        if self.hid:
            res = res.replace("■", "O")
        return res

    def out(self, d):
        return not ((0 <= d.x < self.size) and (0 <= d.y < self.size))


    def countur(self, ship, verb=False):
        near = [
            (-1, -1), (-1, 0), (-1, 1),
            (0, -1), (0, 0), (0, 1),
            (1, -1), (1, 0), (1, 1)
        ]
        for d in ship.dots:
            for dx, dy in near:
                cur = Dot(d.x + dx, d.y + dy)
                if not (self.out(cur)) and cur not in self.busy:
                    if verb:
                        self.field[cur.x][cur.y] = "."
                    self.busy.append(cur)

    def add_ship(self, ship):
        for d in ship.dots:
            if self.out(d) or d in self.busy:
                raise BoardWrongShipException()
        for d in ship.dots:
            self.field[d.x][d.y] = "■"
            self.busy.append(d)

        self.ships.append(ship)
        self.countur(ship)

    def shot(self, d):
        if self.out(d):
            raise BoardOutException()

        if d in self.busy:
            raise BoardUsedException()

        self.busy.append(d)

        for ship in self.ships:
            if d in ship.dots:
                ship.live -= 1
                self.field[d.x][d.y] = "X"
                if ship.live == 0:
                    self.count += 1
                    self.countur(ship, verb=True)
                    print("Корабль уничтожен!")
                    return False
                else:
                    print("Корабль ранен!")
                    return True

        self.field[d.x][d.y] = "*"
        print("Мимо!")
        return False

    def begin(self):
        self.busy = []

    def win(self):
        """ метод выявляющий победителя"""
        return self.count == len(self.ships)


class Player:
    def __init__(self, mapa,  enemy):
        self.mapa = mapa
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
        d = Dot(randint(0,5), randint(0,5))
        print(f"Ход компьютера: {d.x + 1} {d.y +1}")
        return d


class User(Player):
    def ask(self):
        while True:
            cords = input("Ваш ход: ").split()

            if len(cords) != 2:
                print(" Введите 2 координаты! ")
                continue

            x, y = cords

            if not (x.isdigit()) or not (y.isdigit()):
                print(" Введите числа! ")
                continue

            x, y = int(x), int(y)
            return Dot(x - 1, y - 1)


class Game:

    def __init__(self, size=6):

        self.size = size
        self.lens = [3, 2, 1, 1, 1, 1]
        pl = self.random_mapa()
        co = self.random_mapa()
        co.hid = True

        self.ai = AI(co, pl)
        self.us = User(pl, co)



    @staticmethod
    def mapa_print(mapa_1, mapa_2):
        mapa_1 = mapa_1.split("\n")
        mapa_2 = mapa_2.split("\n")
        max_width = max(map(len, mapa_1))
        max_len = max(len(mapa_1), len(mapa_2))
        mapa_1 += [""] * (max_len - len(mapa_1))
        mapa_2 += [""] * (max_len - len(mapa_2))
        text = []
        for f, s in zip(mapa_1, mapa_2):
            text.append(f"{f: <{max_width}}   |:|   {s: <{max_width}}")

        return "\n".join(text)

    def greet(self):
        print("-------------------")
        print("  Приветсвуем вас  ")
        print("      в игре       ")
        print("    морской бой    ")
        print("-------------------")
        print(" формат ввода: x y ")
        print(" x - номер строки  ")
        print(" y - номер столбца ")

    def loop(self):
        num = 0
        while True:
            print("_ "*32)
            us_mapa = "Доска пользователя: \n\n" + str(self.us.mapa)
            ai_mapa = "Доска компьютера: \n\n" + str(self.ai.mapa)

            print(self.mapa_print(us_mapa, ai_mapa))

            if num % 2 == 0:
                print("Ходит пользователь!")
                repeat = self.us.move()
            else:
                print("Ходит компьютер!")
                repeat = self.ai.move()
            if repeat:
                num -= 1

            if self.ai.mapa.win():
                    print("-" * 20)
                    print("Пользователь выиграл!")
                    print(f"Осталось кораблей у Вас: {len(self.us.mapa.ships)}")
                    break

            if self.us.mapa.win():
                print("-" * 20)
                print("Компьютер выиграл!")
                print(f"Осталось кораблей у противника: {len(self.us.mapa.ships)}")
                break

            num += 1


    def try_mapa(self):

        mapa = Mapa(size=self.size)
        attempts = 0
        for p in self.lens:
            while True:
                attempts += 1
                if attempts > 3000:
                    return None
                ship = Ship(Dot(randint(0, self.size), randint(0, self.size)), p, randint(0, 1), p)
                try:
                    mapa.add_ship(ship)
                    break
                except BoardWrongShipException:
                    pass
        mapa.begin()
        return mapa

    def random_mapa(self):
        mapa = None
        while mapa is None:
            mapa = self.try_mapa()
            return mapa

    def start(self):
        self.greet()
        self.loop()


g = Game()
g.start()