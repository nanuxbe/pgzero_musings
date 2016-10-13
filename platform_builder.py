from cellboard import ScrollableCell, ScrollingBoard, SelectableCellMixin
from cellboard import normalize, denormalize
from pgzero.rect import Rect


class BuilderCell(SelectableCellMixin, ScrollableCell):

    def click(self, selected=None):
        if selected:
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
            self.parent.parent.store_map()
            getattr(self, self.get_image())()

    def save(self):
        print('save')
        value = str(denormalize(self.parent.parent.map)) \
            .replace('[[', '[\n[') \
            .replace('], ', '],\n') \
            .replace(']]', ']\n]')
        print(value)
        with open('exported.map', 'w') as f:
            f.write(value)

    def add_col(self):
        map = denormalize(self.parent.parent.map)
        new_map = []
        for line in map:
            line.append(0)
            new_map.append(line)
        self.parent.parent.map = new_map
        self.parent.parent.build_board()

    def add_row(self):
        map = denormalize(self.parent.parent.map)
        map.append([0 for x in map[0]])
        self.parent.parent.map = map
        self.parent.parent.build_board()


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


class BuilderBoard(ScrollingBoard):

    controles_width = 220
    controles_height = 350
    margin = (2, 2)
    border_color = (255, 255, 255)
    background_color = (30, 30, 30)
    cell_class = BuilderCell

    def __init__(self, *args, **kwargs):
        with open('blank.map', 'r') as f:
            self.map = eval(f.read())
        super(BuilderBoard, self).__init__(*args, **kwargs)
        board_width = self.cell_width * self.width + self.margin[0] * 2
        self.controles = Controles(self.cell_class, self.cell_width, self.cell_height,
                                   x=board_width, width=self.controles_width,
                                   height=self.controles_height, parent=self)

    def store_map(self):
        self.map = [
            [
                self._board[x][y].status for y in range(len(self._board[x]))

            ] for x in range(len(self._board))
        ]

    def draw_background(self, screen=None):
        if screen is not None:
            px_width = self.width * self.cell_width
            px_height = self.height * self.cell_height
            height = max(self.controles_height, px_height + self.margin[1] * 2)
            screen.draw.filled_rect(Rect((0, 0), (px_width + 2 * self.margin[0], self.margin[1])), self.border_color)
            screen.draw.filled_rect(Rect((0, self.margin[1]), (self.margin[0], px_height)), self.border_color)
            screen.draw.filled_rect(Rect((0, px_height + self.margin[1]), (px_width + 2 * self.margin[0], self.margin[1])), self.border_color)
            screen.draw.filled_rect(Rect((px_width + self.margin[0], self.margin[1]), (self.margin[0], px_height)), self.border_color)
            screen.draw.filled_rect(Rect((px_width + 2 * self.margin[0], 0), (self.controles_width, height)), self.background_color)
            if height > px_height + 2 * self.margin[1]:
                diff = height - px_height + 2 * self.margin[1] - 1
                screen.draw.filled_rect(Rect((0, px_height + 2 * self.margin[1] + 1), (px_width + 2 * self.margin[0], diff)), self.background_color)

    def draw(self, screen):
        super(BuilderBoard, self).draw(screen=screen)
        self.draw_background(screen=screen)
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
            super(BuilderBoard, self).click(pos, selected=self.controles.selected_cell)

