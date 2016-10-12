from cellboard import ScrollableCell, ScrollingBoard, CantScroll


CELL_WIDTH = 20
CELL_HEIGHT = 20

CELL_CT_W = 2
CELL_CT_H = 2

WIDTH = CELL_WIDTH * CELL_CT_W
HEIGHT = CELL_HEIGHT * CELL_CT_H


class Cell(ScrollableCell):

    images = [
        'cell_dead',
        'cell_alive',
    ]


class Board(ScrollingBoard):

    map = [
        [0, 1, 0, 1, 0],
        [1, 0, 1, 0, 1],
        [0, 1, 0, 1, 0],
        [1, 0, 1, 0, 1],
        [0, 1, 0, 1, 0],
    ]
    offset = (CELL_WIDTH, CELL_HEIGHT)
    cell_class = Cell


board = Board(CELL_CT_W, CELL_CT_H, CELL_WIDTH, CELL_HEIGHT)
board.status = 1


def draw():
    screen.clear()
    board.draw()

def update():
    board.update()


def on_key_down(key):
    x = 0
    y = 0
    if key == keys.RIGHT:
        x = 1
    elif key == keys.LEFT:
        x = -1
    elif key == keys.UP:
        y = -1
    elif key == keys.DOWN:
        y = 1
    try:
        board.scroll(x, y)
    except CantScroll:
        print("Can't scroll")
