from queue import PriorityQueue
import time
import pygame

WIDTH = 750
WINDOW = pygame.display.set_mode((WIDTH, WIDTH))
pygame.display.set_caption("Path finding")

WHITE = (255, 255, 255)
INIT = (204, 0, 102)
SKY = (0, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
MUD = (255, 255, 102)
GREEN = (0, 255, 0)

class Node:

    def __init__(self, row, col, width, total_rows):
        self.row = row
        self.col = col
        self.x = row * width
        self.y = col * width
        self.color = WHITE
        self.total_rows = total_rows
        self.side_neighbors = []
        self.diagonal_neighbors = []
        self.width = width

    def get_pos(self):
        return self.col, self.row

    def is_closed(self):
        return self.color == MUD

    def is_open(self):
        return self.color == RED

    def is_obstacle(self):
        return self.color == BLACK

    def is_start(self):
        return self.color == INIT

    def is_end(self):
        return self.color == SKY

    def reset(self):
        self.color = WHITE

    def make_closed(self):
        self.color = MUD

    def make_open(self):
        self.color = RED

    def make_obstacle(self):
        self.color = BLACK

    def make_start(self):
        self.color = INIT

    def make_end(self):
        self.color = SKY

    def make_path(self):
        self.color = GREEN

    def draw(self, win):
        pygame.draw.rect(win, self.color, (self.x, self.y, self.width, self.width))
    
    def update_neighbors(self, grid):
        self.side_neighbors = []
        if self.row < self.total_rows - 1 and not grid[self.row + 1][self.col].is_obstacle():
            self.side_neighbors.append(grid[self.row + 1][self.col])

        if self.row > 0 and not grid[self.row - 1][self.col].is_obstacle():
            self.side_neighbors.append(grid[self.row - 1][self.col])

        if self.col < self.total_rows - 1 and not grid[self.row][self.col + 1].is_obstacle():
            self.side_neighbors.append(grid[self.row][self.col + 1])

        if self.col > 0 and not grid[self.row][self.col - 1].is_obstacle():
            self.side_neighbors.append(grid[self.row][self.col - 1])

        if self.col > 0 and self.row > 0 and not grid[self.row - 1][self.col - 1].is_obstacle():
            self.diagonal_neighbors.append(grid[self.row - 1][self.col - 1])

        if self.col < self.total_rows - 1 and self.row < self.total_rows - 1 and not grid[self.row + 1][self.col + 1].is_obstacle():
            self.diagonal_neighbors.append(grid[self.row + 1][self.col + 1])

        if self.col > 0 and self.row < self.total_rows - 1 and not grid[self.row + 1][self.col - 1].is_obstacle():
            self.diagonal_neighbors.append(grid[self.row + 1][self.col - 1])

        if self.col < self.total_rows - 1 and self.row > 0 and not grid[self.row - 1][self.col + 1].is_obstacle():
            self.diagonal_neighbors.append(grid[self.row - 1][self.col + 1])

def distance(point1, point2):
    return abs(point1.x - point2.x) ** 2 + abs(point1.y - point2.y) ** 2

def make_grid(row, width):
    grid = []
    gap = width // row
    for i in range(row):
        g = []
        for j in range(row):
            node = Node(i, j, gap, row)
            g.append(node)
        grid.append(g)
    return grid

def draw_grid(win, rows, width):
    gap = width // rows
    for i in range(rows):
        pygame.draw.line(win, BLACK, (0, i * gap), (width, i * gap))
    for i in range(rows):
        pygame.draw.line(win, BLACK, (i * gap, 0), (i * gap, width))

def draw(win, grid, rows, width):
    win.fill(WHITE)
    for row in grid:
        for nodes in row:
            nodes.draw(win)
    draw_grid(win, rows, width)
    pygame.display.update()

def get_clicked_pos(pos, rows, width):
    gap = width // rows
    y, x = pos
    row = y // gap
    col = x // gap

    return row, col

def A_Star_Algorithm(Draw, grid, start, end):
    count = 0
    open_set = PriorityQueue()
    open_set.put((0, count, start))
    parent = {}
    g_score = {node: float('inf') for row in grid for node in row}
    g_score[start] = 0
    f_score = {node: float('inf') for row in grid for node in row}
    f_score[start] = distance(start, end)
    open_set_hash = {start}

    while not open_set.empty():
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()

        current = open_set.get()[2]
        open_set_hash.remove(current)

        if current == end:
            p = parent[current]
            while p != start:
                p.make_path()
                p = parent[p]
                Draw()
            end.make_end()
            return True

        for neighbor in current.diagonal_neighbors:
            temp_g_score = g_score[current] + 14
            if temp_g_score < g_score[neighbor]:
                parent[neighbor] = current
                g_score[neighbor] = temp_g_score
                f_score[neighbor] = temp_g_score + distance(neighbor, end)
                if neighbor not in open_set_hash:
                    count += 1
                    open_set.put((f_score[neighbor], count, neighbor))
                    open_set_hash.add(neighbor)
                    neighbor.make_open()

        for neighbor in current.side_neighbors:
            temp_g_score = g_score[current] + 10

            if temp_g_score < g_score[neighbor]:
                parent[neighbor] = current
                g_score[neighbor] = temp_g_score
                f_score[neighbor] = temp_g_score + distance(neighbor, end)
                if neighbor not in open_set_hash:
                    count += 1
                    open_set.put((f_score[neighbor], count, neighbor))
                    open_set_hash.add(neighbor)
                    neighbor.make_open()

        Draw()
        if current != start:
            current.make_closed()

    return False

def main(win, width):
    ROWS = 50
    grid = make_grid(ROWS, width)

    start = None
    end = None

    run = True
    started = False

    while run:
        draw(win, grid, ROWS, width)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

            if started:
                continue

            if pygame.mouse.get_pressed()[0]:
                pos = pygame.mouse.get_pos()
                row, col = get_clicked_pos(pos, ROWS, width)
                node = grid[row][col]
                if not start and node != end:
                    start = node
                    start.make_start()
                elif not end and node != start:
                    end = node
                    end.make_end()
                elif node != start and node != end:
                    node.make_obstacle()
            elif pygame.mouse.get_pressed()[2]:
                pos = pygame.mouse.get_pos()
                row, col = get_clicked_pos(pos, ROWS, width)
                node = grid[row][col]
                node.reset()
                if node == start:
                    start = None
                if node == end:
                    end = None

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and not started:
                    for row in grid:
                        for node in row:
                            node.update_neighbors(grid)
                    Begin = time.time()
                    A_Star_Algorithm(lambda: draw(win, grid, ROWS, width), grid, start, end)
                    End = time.time()
                    print("Time: ",End - Begin)
                if event.key == pygame.K_c:
                    start = None
                    end = None
                    grid = make_grid(ROWS, WIDTH)
                    started = False
    pygame.quit()


main(WINDOW, WIDTH)
