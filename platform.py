from cellboard import ScrollableCell, ScrollingBoard, CantScroll


CELL_WIDTH = 70
CELL_HEIGHT = 70

CELL_CT_W = 5
CELL_CT_H = 5


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

    controles_width = 160
    controles_height = 500
    margin = (2, 2)
    border_color = (255, 255, 255)
    background_color = (30, 30, 30)

    map = [
        [0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0],
        [2, 3, 5, 5, 1, 2],
        [4, 4, 6, 6, 4, 4],
    ]
    #offset = (CELL_WIDTH, CELL_HEIGHT)
    cell_class = Cell

    def draw(self):
        super(Board, self).draw()
        px_width = self.width * self.cell_width
        px_height = self.height * self.cell_height
        screen.draw.filled_rect(Rect((0, 0), (px_width + 2 * self.margin[0], self.margin[1])), self.border_color)
        screen.draw.filled_rect(Rect((0, self.margin[1]), (self.margin[0], px_height)), self.border_color)
        screen.draw.filled_rect(Rect((0, px_height + self.margin[1]), (px_width + 2 * self.margin[0], self.margin[1])), self.border_color)
        screen.draw.filled_rect(Rect((px_width + self.margin[0], self.margin[1]), (self.margin[0], px_height)), self.border_color)
        screen.draw.filled_rect(Rect((px_width + 2 * self.margin[0], 0), (self.controles_width, HEIGHT)), self.background_color)
        if HEIGHT > px_height + 2 * self.margin[1]:
            diff = HEIGHT - px_height + 2 * self.margin[1] - 1
            screen.draw.filled_rect(Rect((0, px_height + 2 * self.margin[1] + 1), (px_width + 2 * self.margin[0], diff)), self.background_color)



WIDTH = CELL_WIDTH * CELL_CT_W + 2 * Board.margin[0] + Board.controles_width
HEIGHT = max(CELL_HEIGHT * CELL_CT_H + 2 * Board.margin[1], Board.controles_height)

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
