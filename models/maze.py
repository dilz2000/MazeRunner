# models/maze.py

import random
from .union_find import UnionFind
from .cell import Cell


class Maze:
    def __init__(self, size):
        self.size = size
        self.rows = size
        self.cols = size
        # Initialize grid
        self.grid = [[Cell(r, c) for c in range(self.cols)] for r in range(self.rows)]
        self.uf = UnionFind(self.rows * self.cols)
        self.walls = []
        self.build_walls()

    def build_walls(self):
        """Initialize all possible walls between cells."""
        for r in range(self.rows):
            for c in range(self.cols):
                if r < self.rows - 1:
                    self.walls.append(((r, c), (r + 1, c)))
                if c < self.cols - 1:
                    self.walls.append(((r, c), (r, c + 1)))

    def get_cell_id(self, row, col):
        """Convert 2D cell coordinates to 1D Union-Find ID."""
        return row * self.cols + col

    def generate_maze(self):
        """Generate maze using Kruskal's algorithm."""
        # Shuffle the walls randomly
        random.shuffle(self.walls)
        for wall in self.walls:
            (r1, c1), (r2, c2) = wall
            id1 = self.get_cell_id(r1, c1)
            id2 = self.get_cell_id(r2, c2)
            if self.uf.union(id1, id2):
                # Remove the wall between the two cells
                if r1 == r2:
                    # Cells are side by side horizontally
                    self.grid[r1][c1].walls['right'] = False
                    self.grid[r2][c2].walls['left'] = False
                else:
                    # Cells are on top of each other vertically
                    self.grid[r1][c1].walls['bottom'] = False
                    self.grid[r2][c2].walls['top'] = False


    def get_neighbors(self, row, col):
        """Return list of accessible neighbors for a cell."""
        neighbors = []
        cell = self.grid[row][col]
        if not cell.walls['top'] and row > 0:
            neighbors.append((row - 1, col))
        if not cell.walls['bottom'] and row < self.rows - 1:
            neighbors.append((row + 1, col))
        if not cell.walls['left'] and col > 0:
            neighbors.append((row, col - 1))
        if not cell.walls['right'] and col < self.cols - 1:
            neighbors.append((row, col + 1))
        return neighbors