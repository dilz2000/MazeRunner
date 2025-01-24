# models/cell.py

class Cell:
    def __init__(self, row, col):
        self.row = row
        self.col = col
        # Walls: top, bottom, left, right
        self.walls = {'top': True, 'bottom': True, 'left': True, 'right': True}
