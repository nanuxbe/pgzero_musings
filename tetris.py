from random import choice
import time
import serial

from cellboard import BaseCell, BaseBoard, toggle_status, rotate, normalize


CELL_WIDTH = 20
CELL_HEIGHT = 20

CELL_CT_W = 10
CELL_CT_H = 25

WIDTH = CELL_CT_W * CELL_WIDTH
HEIGHT = CELL_CT_H * CELL_HEIGHT


def restore_game():
    global board
    board._matrix = board._hidden_matrix
    board.status = 1


class CantMoveThere(Exception):
    pass


class Cell(BaseCell):

    images = [
        'cell_empty',
        'cell_i',
        'cell_j',
        'cell_l',
        'cell_o',
        'cell_s',
        'cell_t',
        'cell_z',
    ]


class Piece():

    _value = []

    def __init__(self, matrix, x=0, y=0):
        self._value = normalize(self._value)
        self.check_can_be_there(matrix, x, y, self._value)
        self.x = x
        self.y = y

    def check_can_be_there(self, matrix, x, y, value):
        for i in range(len(value)):
            for j in range(len(value[0])):
                if x + i >= len(matrix) or x < 0:
                    raise CantMoveThere()
                if y + j >= len(matrix[0]) or y < 0:
                    raise CantMoveThere()
                if value[i][j] != 0 and matrix[x + i][y + j] != 0:
                    raise CantMoveThere()

    def move(self, matrix, x=0, y=0):
        self.check_can_be_there(matrix, self.x + x, self.y + y, self._value)
        self.x += x
        self.y += y

    def rotate(self, matrix, factor=1, check=True):
        ct = abs(factor - 1) + 1
        new_value = rotate(self._value, ct)
        if check:
            self.check_can_be_there(matrix, self.x, self.y, new_value)
        self._value = new_value

    def plot_on(self, board):
        for x in range(len(self._value)):
            for y in range(len(self._value[0])):
                if self._value[x][y] > 0:
                    board.cell_at_xy(self.x + x, self.y + y)._next = self._value[x][y]

    def merge_into(self, matrix):
        for x in range(len(self._value)):
            for y in range(len(self._value[0])):
                matrix[self.x + x][self.y + y] += self._value[x][y]


class LPiece(Piece):

    _value = [
        [3, 0],
        [3, 0],
        [3, 3],
    ]


class OPiece(Piece):

    _value = [
        [4, 4],
        [4, 4],
    ]


class IPiece(Piece):
    _value = [
        [1],
        [1],
        [1],
        [1],
    ]


class JPiece(Piece):
    _value = [
        [0, 2],
        [0, 2],
        [2, 2],
    ]


class SPiece(Piece):
    _value = [
        [0, 5, 5],
        [5, 5, 0],
    ]


class TPiece(Piece):
    _value = [
        [6, 6, 6],
        [0, 6, 0],
    ]


class ZPiece(Piece):
    _value = [
        [7, 7, 0],
        [0, 7, 7],
    ]


class Board(BaseBoard):

    cell_class = Cell
    interval = .05
    pieces = [
        LPiece,
        OPiece,
        IPiece,
        JPiece,
        SPiece,
        TPiece,
        ZPiece,
    ]

    def __init__(self, width, height, *args, **kwargs):
        super(Board, self).__init__(width, height, *args, **kwargs)
        self._matrix = [
            [0 for i in range(height)]
            for j in range(width)
        ]
        self._moving = None
        self.status = 1

    def do_update(self):
        if self.status == 1:
            if self._moving is None:
                try:
                    self._moving = choice(self.pieces)(self._matrix, 4, 0)
                except CantMoveThere:
                    raise Exception('Game Over')
            else:
                try:
                    self._moving.move(self._matrix, y=1)
                except CantMoveThere:
                    self.next_piece()

    def draw(self):
        self.clear_full_rows()
        self.plot()
        super(Board, self).draw()

    def clear_full_rows(self):
        matrix = rotate(self._matrix)
        new_matrix = []
        cleared = 0
        for line in matrix:
            if all(line):
                cleared += 1
                line = [0 for x in range(self.width)]
            new_matrix.append(line)

        if cleared > 0:
            self._matrix = rotate(new_matrix, 3)
            self.status = 2
            print('you cleared {} lines'.format(cleared))
            matrix = [
                [0 for x in range(self.width)]
                for y in range(cleared)
            ] + list(filter(
                lambda l: not all(l),
                matrix
            ))
            self._hidden_matrix = rotate(matrix, 3)
            clock.schedule_unique(restore_game, .25)

    def plot(self):
        for x in range(len(self._matrix)):
            for y in range(len(self._matrix[0])):
                self.cell_at_xy(x, y)._next = self._matrix[x][y]
        if self._moving is not None:
            self._moving.plot_on(self)

    def rotate_piece(self, direction=1):
        if self._moving is not None:
            try:
                self._moving.rotate(self._matrix, direction)
            except CantMoveThere:
                pass

    def move_piece(self, direction):
        if self._moving is not None:
            try:
                self._moving.move(self._matrix, direction)
            except CantMoveThere:
                pass

    def drop_piece(self, count=None):
        if count == None:
            count = self.height
        if self._moving is not None:
            try:
                for i in range(count):
                    self._moving.move(self._matrix, y=1)
            except CantMoveThere:
                self.next_piece()


    def next_piece(self):
        self._moving.merge_into(self._matrix)
        self._moving = None


board = Board(CELL_CT_W, CELL_CT_H, CELL_WIDTH, CELL_HEIGHT)
ser = None
try:
    ser = serial.Serial('/dev/ttyACM0', 115200, timeout=.0001)
except:
    ser = None


def draw():
    screen.clear()
    board.draw()


def update():
    global ser
    try:
        if ser is None:
            print('reconnecting')
            ser = serial.Serial('/dev/ttyACM0', 115200, timeout=.0001)
        rcv = ser.readline()
        cmd = rcv.decode('utf-8').rstrip()
        cmd = cmd.split(':')
        if cmd[0] == 'btn':
            direction = 1
            if cmd[1] == 'b':
                direction = -1
            board.rotate_piece(direction)
        elif cmd[0] == 'move':
            dx = 0
            dy = 0

            if cmd[1] == 'left':
                dx = -1
            elif cmd[1] == 'right':
                dx = 1
            elif cmd[1] == 'backwards':
                dy = 1

            if dx != 0:
                board.move_piece(dx)
            elif dy != 0:
                board.drop_piece(dy)
    except serial.SerialException:
        try:
            if ser is not None:
                ser.close()
                ser = None
                print('Disconencting')
            print('Lost or no connection')
        except UnboundLocalError:
            print('ser not assigned yet')
    except Exception as e:
        print(e)
    board.update()


def on_key_down(key):
    if key == keys.UP:
        board.rotate_piece()
    elif key == keys.LEFT:
        board.move_piece(-1)
    elif key == keys.RIGHT:
        board.move_piece(1)
    elif key == keys.DOWN:
        board.drop_piece(1)
    elif key == keys.SPACE:
        board.drop_piece()
