from cellboard import BaseBoard, BaseCell, toggle_status


CELL_WIDTH = 20
CELL_HEIGHT = 20

CELL_CT_W = 32
CELL_CT_H = 24

WIDTH = CELL_WIDTH * CELL_CT_W
HEIGHT = CELL_HEIGHT * CELL_CT_H


class Cell(BaseCell):

    images = [
        'cell_dead',
        'cell_alive',
    ]

    def update(self):
        ct = 0
        for i in range(self.x - 1, self.x + 2):
            for j in range(self.y - 1, self.y + 2):
                if i != self.x or j != self.y:
                    neighbour = self.parent.cell_at_xy(i, j)
                    if neighbour is not None:
                        ct += neighbour.status

        self._next = self.status
        if self.status == 1:
            if ct < 2 or ct > 3:
                self._next = 0
        else:
            if ct == 3:
                self._next = 1

    def click(self):
        toggle_status(self)


class Board(BaseBoard):

    cell_class = Cell
    interval = .5


board = Board(CELL_CT_W, CELL_CT_H, CELL_WIDTH, CELL_HEIGHT)


def draw():
    screen.clear()
    board.draw()

def update():
    board.update()


def on_mouse_down(pos):
    board.click(pos)


def on_key_down(key):
    if key == keys.SPACE:
        toggle_status(board)
