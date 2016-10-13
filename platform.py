from platform_builder import BuilderCell, BuilderBoard
from cellboard import CantScroll


CELL_WIDTH = 70
CELL_HEIGHT = 70

CELL_CT_W = 5
CELL_CT_H = 5


class Cell(BuilderCell):

    images = [
        'blank',
        'grass-left',
        'grass-mid',
        'grass-right',
        'grass-center',
        'liquid-water',
        'liquid-water-center',
    ]


class Board(BuilderBoard):

    #offset = (CELL_WIDTH, CELL_HEIGHT)
    cell_class = Cell


WIDTH = CELL_WIDTH * CELL_CT_W + 2 * Board.margin[0] + Board.controles_width
HEIGHT = max(CELL_HEIGHT * CELL_CT_H + 2 * Board.margin[1], Board.controles_height)

dx = 0
dy = 0

board = Board(CELL_CT_W, CELL_CT_H, CELL_WIDTH, CELL_HEIGHT)
board.status = 1


def draw():
    screen.clear()
    board.draw(screen)


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


def on_mouse_down(pos):
    board.click(pos)
