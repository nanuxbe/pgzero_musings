from cellboard import ScrollableCell, ScrollingBoard, CantScroll, SelectableCellMixin, denormalize


CELL_WIDTH = 70
CELL_HEIGHT = 70

CELL_CT_W = 5
CELL_CT_H = 5


class Cell(SelectableCellMixin, ScrollableCell):

    images = [
        'blank',
        'grass-left',
        'grass-mid',
        'grass-right',
        'grass-center',
        'liquid-water',
        'liquid-water-center',
    ]

    def click(self, selected=None):
        self._next = selected.status


class ControleCell(ScrollableCell):
    images = [
        'add_row',
        'add_col',
        'save',
    ]
    draw_status_zero = True

    def click(self):
        if hasattr(self, self.get_image()):
            getattr(self, self.get_image())()

    def save(self):
        print('save')
        value = str(denormalize(self.parent.parent.map)) \
            .replace('[[', '[\n[') \
            .replace('], ', '],\n') \
            .replace(']]', ']\n]')
        with open('exported.map', 'w') as f:
            f.write(value)


class Controles():

    def __init__(self, cell_class, cell_width, cell_height, parent, width=250, height=300, x=0, y=0):
        self.offset = (-x, -y)
        self.margin = (5, 0)
        self.cells = []
        self.controle_cells = []
        self.cell_width = cell_width
        self.cell_height = cell_height
        self.parent = parent

        for i in range(len(ControleCell.images)):
            cell = ControleCell(i % 2, i // 2, cell_width, cell_height, self)
            cell._next = i
            cell.status = i
            self.controle_cells.append(cell)

        iy = 1
        ix = 0
        for i, image in enumerate(cell_class.images):
            iy += 1
            if (iy + 1) * cell_height > height:
                iy = 2
                ix += 1
            if (ix + 1) * cell_width > width:
                raise Exception('No room left for controle')
            cell = cell_class(ix, iy, cell_width, cell_height, self)
            cell._next = i
            cell.status = i
            self.cells.append(cell)

    def draw(self, screen=None):
        for cell in self.controle_cells:
            cell.draw()
        for cell in self.cells:
            cell.draw(screen)

    def click(self, pos):

        for cell in self.controle_cells:
            if cell._actor.collidepoint(pos):
                cell.click()
                return

        col_index = -1

        for i, cell in enumerate(self.cells):
            collide = False
            cell_pos = cell.get_pos()
            if pos[0] < cell_pos[0] + self.cell_width and pos[1] < cell_pos[1] + self.cell_height and \
                    pos[0] >= cell_pos[0] and pos[1] >= cell_pos[1]:
                collide = True
            if collide:
                col_index = i
                cell.selected = True
            elif col_index != -1:
                cell.selected = False

        for i in range(col_index):
            self.cells[i].selected = False

    @property
    def selected_cell(self):
        for cell in self.cells:
            if cell.selected:
                return cell
        return None


class Board(ScrollingBoard):

    controles_width = 160
    controles_height = 500
    margin = (2, 2)
    border_color = (255, 255, 255)
    background_color = (30, 30, 30)

    #offset = (CELL_WIDTH, CELL_HEIGHT)
    cell_class = Cell

    def __init__(self, *args, **kwargs):
        with open('blank.map', 'r') as f:
            self.map = eval(f.read())
        super(Board, self).__init__(*args, **kwargs)
        self.controles = Controles(self.cell_class, self.cell_width, self.cell_height,
                                   x=WIDTH - self.controles_width, width=self.controles_width,
                                   height=self.controles_height, parent=self)

    def draw_background(self):
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

    def draw(self, screen):
        super(Board, self).draw(screen=screen)
        self.draw_background()
        self.controles.draw(screen=screen)

    def click(self, pos):
        inboard = True
        if pos[0] > self.width * self.cell_width + 2 * self.margin[0]:
            inboard = False
        if pos[1] > self.height * self.cell_height + 2 * self.margin[1]:
            inboard = False
        if not inboard:
            self.controles.click(pos)
        else:
            super(Board, self).click(pos, selected=self.controles.selected_cell)


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
