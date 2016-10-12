from cellboard import ScrollableCell, ScrollingBoard, CantScroll


CELL_WIDTH = 70
CELL_HEIGHT = 70

CELL_CT_W = 5
CELL_CT_H = 5

WIDTH = CELL_WIDTH * CELL_CT_W
HEIGHT = CELL_HEIGHT * CELL_CT_H


class Cell(ScrollableCell):

    images = [
        'blank',
        'grass-left',
        'grass-mid',
        'grass-right',
        'grass-center',
        'liquid-water',
        'liquid-water-center',
    ]


class Board(ScrollingBoard):

    map = [
        [0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0],
        [2, 3, 5, 5, 1, 2],
        [4, 4, 6, 6, 4, 4],
    ]
    #offset = (CELL_WIDTH, CELL_HEIGHT)
    cell_class = Cell


dx = 0
dy = 0

board = Board(CELL_CT_W, CELL_CT_H, CELL_WIDTH, CELL_HEIGHT)
board.status = 1


def draw():
    screen.clear()
    board.draw()

def update():
    global dx, dy
    if dx != 0 or dy!= 0:
        try:
            board.scroll(dx, dy)
        except CantScroll:
            print("Can't scroll")
    board.update()


def on_key_up(key):
    global dx, dy
    if key == keys.RIGHT or key == keys.LEFT:
        dx = 0
    elif key == keys.UP or key == keys.DOWN:
        dy = 0


def on_key_down(key):
    global dx, dy
    if key == keys.RIGHT:
        dx = 1
    elif key == keys.LEFT:
        dx = -1
    elif key == keys.UP:
        dy = -1
    elif key == keys.DOWN:
        dy = 1
