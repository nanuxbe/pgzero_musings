import time
from pgzero.actor import Actor


def rotate(original, ct=1):
    rv = original
    for i in range(ct):
        rv = list([list(item) for item in zip(*rv[::-1])])
    return rv


def normalize(value):
    rv = list([
        list(reversed(line)) for line in value
    ])
    return rotate(rv, 3)


def toggle_status(item):
    if hasattr(item, '_next'):
        item._next = 1 - item.status
    else:
        item.status = 1 - item.status


class CantScroll(Exception):
    pass


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
        self.build_board()

    def build_board(self):
        self._board = [
            [
                self.get_new_cell(x, y) for y in range(self.height)
            ] for x in range(self.width)
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


class ScrollableCell(BaseCell):

    def get_pos(self, offset=None, margin=None):
        if offset is None:
            offset = self.parent.offset
        if margin is None:
            margin = self.parent.margin
        x, y = super(ScrollableCell, self).get_pos()
        return (x - offset[0] + margin[0], y - offset[1] + margin[1])

    def draw(self):
        x, y = self.get_pos()
        self._actor.left = x
        self._actor.top = y
        if self._next != 0:
            super(ScrollableCell, self).draw()


class ScrollingBoard(BaseBoard):

    map = []
    offset = (0, 0)
    margin = (0, 0)
    cell_class = ScrollableCell

    def build_board(self):
        self.map = normalize(self.map)
        self._board = [
            [
                self.get_new_cell(x, y) for y in range(len(self.map[x]))
            ] for x in range(len(self.map))
        ]

    def get_new_cell(self, x, y):
        cell = super(ScrollingBoard, self).get_new_cell(x, y)
        cell.status = self.map[x][y]
        cell._next = self.map[x][y]
        return cell

    def in_view(self, cell):
        x, y = cell.get_pos()
        if x + self.cell_width - 1 < 0:
            return False
        if y + self.cell_height - 1 < 0:
            return False
        if x >= self.width * self.cell_width:
            return False
        if y >= self.height * self.cell_height:
            return False
        return True

    def draw(self):
        for cell in self.each():
            if self.in_view(cell):
                cell.draw()

    def scroll(self, x=0, y=0):
        if self.offset[0] + x < 0:
            raise CantScroll()
        if self.offset[1] + y < 0:
            raise CantScroll
        if self.offset[0] + x + self.width * self.cell_width > len(self._board) * self.cell_width:
            raise CantScroll()
        if self.offset[1] + y + self.height * self.cell_height > len(self._board[0]) * self.cell_height:
            raise CantScroll
        self.offset = (self.offset[0] + x, self.offset[1] + y)
