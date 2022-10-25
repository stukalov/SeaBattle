import random


class QuitGame(Exception):
    pass


class ShipException(Exception):
    pass


class Cell:
    def __init__(self, x, y):
        self.__x = x
        self.__y = y

    @property
    def x(self):
        return self.__x

    @property
    def y(self):
        return self.__y

    def __eq__(self, other):
        return self.__x == other.x and self.__y == other.y

    def __add__(self, other):
        return self.__class__(self.x + other.x, self.y + other.y)


class Ship:
    TYPE_HORIZONTAL = 0
    TYPE_VERTICAL = 1

    def __init__(self, size, type):
        '''
        :param size: размер в клетках 1, 2 или 3
        :param type: 0 - горизонтальный, 1 - вертикальный
        '''
        self.__size = size
        if type in [0, 1]:
            self.__type = type
        else:
            raise ShipException('Указано неверный тип корабля')
        self.__pos = None
        self.__cells = [None] * size
        self.__hits = [False] * size

    @property
    def size(self):
        return self.__size

    @property
    def type(self):
        return self.__type

    @property
    def pos(self):
        return self.__pos

    @pos.setter
    def pos(self, value):
        self.__pos = value
        i = 0
        while i < self.size:
            self.__cells[i] = value
            value += Cell(0, 1) if self.type else Cell(1, 0)
            i += 1

    @property
    def killed(self):
        return all(self.__hits)

    @property
    def area(self):
        return self.__cells[0] + Cell(-1, -1), self.__cells[-1] + Cell(1, 1)

    @property
    def cells(self):
        return self.__cells

    def on_board(self):
        w, h = Board.width(), Board.height()
        for pos in self.__cells:
            if any([pos.x < 1, pos.y < 1, pos.x > w, pos.y > h]):
                raise ShipException('Корабль за пределами игрового поля')

    def in_area(self, area):
        # угловые точки исключаем. В них может находиться корабль. В задании на картинке корабли касаются углами
        c1, c2 = area[0], area[1]
        c3, c4 = Cell(c1.x, c2.y), Cell(c2.x, c1.y)
        for pos in self.__cells:
            in_area = c1.x <= pos.x <= c2.x and c1.y <= pos.y <= c2.y
            in_corner = any([pos == c1, pos == c2, pos == c3, pos == c4])
            if in_area and not in_corner:
                raise ShipException('С этим кораблем в соседних клетках есть другой корабль')

    def hit(self, cell):
        for i, item in enumerate(self.cells):
            if item == cell:
                self.__hits[i] = True
                return True
        return False


class ShipList(list):

    def hit(self, cell):
        for ship in self:
            if ship.hit(cell):
                return True
        return False

    @property
    def killed(self):
        return all([ship.killed for ship in self])


class Board:
    CELL_EMPTY = '0'
    CELL_SHIP = '■'
    CELL_HIT = 'X'
    CELL_NOT_HIT = 'T'

    def __init__(self, ships, show_ships=True):
        self.__field = [[self.CELL_EMPTY] * self.width() for _ in range(self.height())]
        self.__ships = ships
        if show_ships:
            self.__place_ships()

    def __place_ships(self):
        for ship in self.__ships:
            for cell in ship.cells:
                # self.__field[СТРОКА][СТОЛБЕЦ]
                self.__field[cell.y-1][cell.x-1] = self.CELL_SHIP

    @staticmethod
    def width():
        return 6

    @staticmethod
    def height():
        return 6

    @staticmethod
    def ship_sizes():
        return (3, 2, 2, 1, 1, 1, 1)

    def __str__(self):
        str = '   |'
        for x in range(self.width()):
            str += f' {x+1} |'
        out = [str]
        for y in range(self.height()):
            str = f' {y+1} |'
            for x in range(self.width()):
                # self.__field[СТРОКА][СТОЛБЕЦ]
                str += f' {self.__field[y][x]} |'
            out.append(str)
        return '\n'.join(out) + '\n'

    def hit(self, cell):
        # self.__field[СТРОКА][СТОЛБЕЦ]
        self.__field[cell.y-1][cell.x-1] = self.CELL_HIT if self.__ships.hit(cell) else self.CELL_NOT_HIT

    @property
    def killed(self):
        return self.__ships.killed


class Player:

    def __init__(self):
        self.__board = self.generate_board()
        self.__hit_map = [False] * Board.width() * Board.height()

    @property
    def board(self):
        return self.__board

    @property
    def hit_variants(self):
        return list(filter(lambda x: not self.__hit_map[x], (i for i, _ in enumerate(self.__hit_map))))

    def get_hit(self):
        hit = self.make_hit()
        cell = Cell(hit % self.__board.width() + 1, hit // self.__board.width() + 1)
        if self.__hit_map[hit]:
            raise ValueError(f'По координатам {cell.x}:{cell.y} вы уже стреляли.')
        self.__hit_map[hit] = True
        return cell

    # Переопределяется в дочернем классе, Запрос хода игрока
    def make_hit(self):
        pass

    # Поле очень маленькое, не всегда удается рзместить случаныйм образом все корабли у четом ограничений
    def generate_board(self):
        ships = ShipList()
        for size in Board.ship_sizes():
            while True:
                try:
                    x, y, t = self.get_ship_params(size)
                    ship = Ship(size, t)
                    ship.pos = Cell(x, y)
                    ship.on_board()
                    area = ship.area
                    for check in ships:
                        check.in_area(area)
                except (ShipException, ValueError) as e:
                    self.print_exception(e)
                    self.print_ships(ships)
                    continue
                ships.append(ship)
                self.print_ships(ships)
                break
        return self.create_board(ships)

    # Переопределяется в дочернем классе
    def get_ship_params(self, size):
        pass

    # Переопределяется в дочернем классе (Bot - не печатает ошибки, Human - печатает)
    def print_exception(self, e):
        pass

    # Переопределяется в дочернем классе (Bot - свое поле при расставлении кораблей, Human - печатает)
    def print_ships(self, ships):
        pass

    # Переопределяется в дочернем классе
    def create_board(self, ships):
        return Board(ships)

    def play(self, enemy):
        enemy.board.hit(self.get_hit())
        return enemy.board.killed



class BotPlayer(Player):

    def make_hit(self):
        hit = random.choice(self.hit_variants)
        return hit

    def get_ship_params(self, size):
        x, y = random.randrange(Board.width()) + 1, random.randrange(Board.height()) + 1
        t = random.choice([Ship.TYPE_HORIZONTAL, Ship.TYPE_VERTICAL])
        return x, y, t

    def create_board(self, ships):
        return Board(ships, False)


class HumanPlayer(Player):

    @staticmethod
    def input(text):
        inp = input(text)
        if inp == '0':
            raise QuitGame()
        return inp.split()

    def make_hit(self):
        xy = self.input('Введите координаты выстрела X и Y через пробел: ')
        if len(xy) != 2:
            raise ValueError('Указано неверное количество координат.')
        try:
            x, y = list(map(int, xy))
        except ValueError as e:
            raise ValueError('Одна из координат не число.')
        if not 1 <= x <= self.board.width():
            raise ValueError(f'Координата X за пределами поля. Для X укажите от 1 до {self.board.width()}.')
        if not 1 <= y <= self.board.height():
            raise ValueError(f'Координата Y за пределами поля. Для Y укажите от 1 до {self.board.height()}.')
        hit = (y - 1) * self.board.width() + (x - 1)
        return hit

    def get_ship_params(self, size):
        # чтобы было похоже на русский язык
        size_word = {1: 'клетку', 2: 'клетки', 3: 'клетки'}
        print(f'Расположите корабль размером в {size} {size_word[size]}')
        print(f"Допустимые значения: ")
        print(f"X: от 1 до {Board.width()}, ")
        print(f"Y: от 1 до {Board.height()}")
        if size > 1:
            print(f"Тип: 0 - горизонтальный, 1 - вертикальный")
        xyt = self.input("Укажите координаты 'X', 'Y' его первой клетки" +
                         (" и 'Тип' корабля через пробел" if size > 1 else "") + ": ")
        if size == 1:
            xyt.append(0)
        if len(xyt) != 3:
            raise ValueError('Указано неверное количество параметров.')
        try:
            return list(map(int, xyt))
        except ValueError as e:
            raise ValueError('Один из параметров не число.')

    def print_exception(self, e):
        print('\n', e, '\n')

    def print_ships(self, ships):
        print(Board(ships))


class GameLogic:

    def __init__(self):
        self.__score = {'user': 0, 'bot': 0}

    @staticmethod
    def print_fields(human, bot):
        w = (Board.width() + 1) * 4 + 5
        h_field, b_field = str(human.board).split('\n'), str(bot.board).split('\n')
        h_field.insert(0, 'Ваше поле:')
        b_field.insert(0, 'Поле компьютера:')
        for h, b in zip(h_field, b_field):
            print(f'{h:{w}}{b}')

    def play_game(self):
        player1, player2 = human, bot = HumanPlayer(), BotPlayer()
        self.print_fields(human, bot)
        while True:
            if player1 == human:
                print('Ваш ход:')
            else:
                print('Ход компьютера:')
            try:
                won = player1.play(player2)
                self.print_fields(human, bot)
                if won:
                    return player1
                player1, player2 = player2, player1
            except ValueError as e:
                print(e)

    def print_score(self):
        if self.__score['user'] > self.__score['bot']:
            print(f"Счет {self.__score['user']}:{self.__score['bot']} в Вашу пользу")
        elif self.__score['user'] < self.__score['bot']:
            print(f"Счет {self.__score['bot']}:{self.__score['user']} в пользу компьютера")
        else:
            print(f"Счет ничейный {self.__score['bot']}:{self.__score['user']}")

    def won_player(self, won):
        if isinstance(won, HumanPlayer):
            self.__score['user'] += 1
            print('Вы выиграли')
        elif isinstance(won, BotPlayer):
            self.__score['bot'] += 1
            print('Выиграл компьютер')
        else:
            print('Ничья')

    def run(self):
        print('Приветствую Вас в игре морской бой\n')
        print('Для выхода из игры в любой момент введите 0')
        while True:
            try:
                self.won_player(self.play_game())
                self.print_score()
                print('\nПоиграем еще раз?\n')
            except KeyboardInterrupt:
                break
            except QuitGame:
                break
            except BaseException as e:
                print('Произошла ошибка\n')
                break

        print('Игра закончена. Ждем Вас снова\n')


if __name__ == "__main__":
    GameLogic().run()
