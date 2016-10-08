import time
from pgzero.actor import Actor


def toggle_status(item):
    if hasattr(item, '_next'):
        item._next = 1 - item.status
    else:
        item.status = 1 - item.status


class BaseCell():

    images = [
        'cell_dead'
    ]

    def __init__(self, x, y, cell_width, cell_height, parent):
        self.status = 0
        self._next = 0
        self.x = x
        self.y = y
        self.cell_width = cell_width
        self.cell_height = cell_height
        self.parent = parent

        self._actor = Actor(self.get_image(), self.get_pos(), anchor=('left', 'top'))

    def get_image(self):
        return self.images[self.status]

    def get_pos(self):
        return (
            self.x * self.cell_width,
            self.y * self.cell_height,
        )

    def draw(self):
        self.status = self._next
        self._actor.image = self.get_image()
        self._actor.draw()

    def update(self):
        pass

    def click(self):
        pass


class BaseBoard():

    cell_class = BaseCell
    interval = 0

    def __init__(self, width, height, cell_width, cell_height):
        self.cell_width = cell_width
        self.cell_height = cell_height
        self.width = width
        self.height = height
        self.status = 0

        self._last = 0
        self._board = [
            [
                self.get_new_cell(x, y) for y in range(height)
            ] for x in range(width)
        ]

    def get_new_cell(self, x, y):
        return self.cell_class(x, y, self.cell_width, self.cell_height, self)

    def each(self):
        for col in self._board:
            for cell in col:
                yield cell

    def draw(self):
        for cell in self.each():
            cell.draw()

    def do_update(self):
        if self.status == 1:
            for cell in self.each():
                cell.update()

    def update(self):
        if time.clock() - self.interval > self._last:
            self._last = time.clock()
            self.do_update()

    def get_xy_for_pos(self, pos):
        return (
            pos[0] // self.cell_width,
            pos[1] // self.cell_height,
        )

    def cell_at_xy(self, x, y):
        if x < 0 or y < 0:
            return None
        try:
            return self._board[x][y]
        except IndexError:
            return None

    def click(self, pos):
        (x, y) = self.get_xy_for_pos(pos)
        self.cell_at_xy(x, y).click()
