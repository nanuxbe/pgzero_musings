from random import choice
import time

from cellboard import BaseCell, BaseBoard, toggle_status


CELL_WIDTH = 20
CELL_HEIGHT = 20

CELL_CT_W = 10
CELL_CT_H = 25

WIDTH = CELL_CT_W * CELL_WIDTH
HEIGHT = CELL_CT_H * CELL_HEIGHT


class CantMoveThere(Exception):
    pass


class Cell(BaseCell):

    images = [
        'cell_dead',
        'cell_alive',
    ]


class Piece():

    _value = []

    def __init__(self, matrix, x=0, y=0):
        self.normalize()
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

    def normalize(self):
        self._value = list([
            list(reversed(line)) for line in self._value
        ])
        self.rotate([], -1, check=False)

    def move(self, matrix, x=0, y=0):
        self.check_can_be_there(matrix, self.x + x, self.y + y, self._value)
        self.x += x
        self.y += y

    def rotate(self, matrix, factor=1, check=True):
        ct = abs(factor - 1)
        for x in range(ct + 1):
            new_value = list([list(item) for item in zip(*self._value[::-1])])
        if check:
            self.check_can_be_there(matrix, self.x, self.y, new_value)
        self._value = new_value

    def plot_on(self, board):
        for x in range(len(self._value)):
            for y in range(len(self._value[0])):
                board.cell_at_xy(self.x + x, self.y + y)._next = self._value[x][y]

    def merge_into(self, matrix):
        for x in range(len(self._value)):
            for y in range(len(self._value[0])):
                matrix[self.x + x][self.y + y] += self._value[x][y]


class LPiece(Piece):

    _value = [
        [1, 0],
        [1, 0],
        [1, 1],
    ]


class OPiece(Piece):

    _value = [
        [1, 1],
        [1, 1],
    ]


class Board(BaseBoard):

    cell_class = Cell
    interval = .5
    pieces = [
        LPiece,
        OPiece
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
        self.plot()
        super(Board, self).draw()

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


def draw():
    screen.clear()
    board.draw()


def update():
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
