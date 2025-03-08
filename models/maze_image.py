# models/maze_image.py
import numpy as np
from .cell import Cell

class MazeL:
    def __init__(self, h_grid_lines, v_grid_lines, processed_maze):
        """
        h_grid_lines, v_grid_lines: sorted lists of y-coordinates (horizontal lines) and x-coordinates (vertical lines).
        processed_maze: binary or skeletonized image where walls are white/255 and background is black/0 (or vice versa).
        """
        # Number of rows and columns
        self.rows = len(h_grid_lines) - 1
        self.cols = len(v_grid_lines) - 1
        self.size = self.rows

        # Create a 2D grid of Cell objects
        self.grid = [[Cell(r, c) for c in range(self.cols)] for r in range(self.rows)]

        self.start_cell = None  # (row, col) of the start node
        self.end_cell = None

        # Fill in walls for each cell by scanning the processed maze or using line positions
        self._assign_walls(h_grid_lines, v_grid_lines, processed_maze)

    def _assign_walls(self, h_grid_lines, v_grid_lines, processed_maze):
        """
        For each cell, determine if there's a wall on top, bottom, left, or right
        by checking the corresponding lines or scanning the processed_maze.
        """
        # Ensure lines are sorted
        h_grid_lines.sort()
        v_grid_lines.sort()

        # For each cell, we look at the bounding box defined by:
        # top_y = h_grid_lines[row]
        # bottom_y = h_grid_lines[row+1]
        # left_x = v_grid_lines[col]
        # right_x = v_grid_lines[col+1]
        # Then check if there's a "line" or "wall" at each boundary.
        for row in range(self.rows):
            for col in range(self.cols):
                cell = self.grid[row][col]

                # Coordinates in the image
                top_y = h_grid_lines[row]
                bottom_y = h_grid_lines[row + 1]
                left_x = v_grid_lines[col]
                right_x = v_grid_lines[col + 1]

                # 1. Check top wall
                # We look at the horizontal strip near top_y between left_x and right_x.
                # If that strip in processed_maze has white/wall pixels, top wall = True; otherwise False.
                if self._has_wall_horizontal(processed_maze, top_y, left_x, right_x):
                    cell.walls['top'] = True
                else:
                    cell.walls['top'] = False

                if self._has_wall_horizontal(processed_maze, bottom_y, left_x, right_x):
                    cell.walls['bottom'] = True
                else:
                    cell.walls['bottom'] = False

                if self._has_wall_vertical(processed_maze, left_x, top_y, bottom_y):
                    cell.walls['left'] = True
                else:
                    cell.walls['left'] = False

                if self._has_wall_vertical(processed_maze, right_x, top_y, bottom_y):
                    cell.walls['right'] = True
                else:
                    cell.walls['right'] = False

    def _has_wall_horizontal(self, img, y, x_start, x_end, thickness=4):
        """
        Check if there's a continuous white/wall pixel line around row 'y'
        between [x_start, x_end].
        We'll look in a small band of +/- thickness.
        """
        h, w = img.shape[:2]
        y_min = max(0, y - thickness)
        y_max = min(h, y + thickness + 1)

        # Slice the row region
        line_region = img[y_min:y_max, x_start:x_end]
        # If there's enough white pixels, we consider there's a wall
        # (Tune the ratio or threshold as needed)
        white_pixels = np.count_nonzero(line_region)
        total_pixels = line_region.size
        # If ratio of white pixels is large, there's a wall
        return (white_pixels / (total_pixels + 1e-5)) > 0.2

    def _has_wall_vertical(self, img, x, y_start, y_end, thickness=4):
        """
        Check if there's a continuous white/wall pixel line around column 'x'
        between [y_start, y_end].
        We'll look in a small band of +/- thickness.
        """
        h, w = img.shape[:2]
        x_min = max(0, x - thickness)
        x_max = min(w, x + thickness + 1)

        # Slice the column region
        line_region = img[y_start:y_end, x_min:x_max]
        white_pixels = np.count_nonzero(line_region)
        total_pixels = line_region.size
        # If ratio of white pixels is large, there's a wall
        return (white_pixels / (total_pixels + 1e-5)) > 0.2

    def get_cell_id(self, row, col):
        """
        Convert 2D cell coordinates to a 1D ID (for Union-Find or other indexing).
        """
        return row * self.cols + col

    def get_neighbors(self, row, col):
        """
        Return list of accessible neighbors (no wall in between).
        Each neighbor is a (row, col) tuple.
        """
        neighbors = []
        cell = self.grid[row][col]

        # Top neighbor
        if not cell.walls['top'] and row > 0:
            neighbors.append((row - 1, col))
        # Bottom neighbor
        if not cell.walls['bottom'] and row < self.rows - 1:
            neighbors.append((row + 1, col))
        # Left neighbor
        if not cell.walls['left'] and col > 0:
            neighbors.append((row, col - 1))
        # Right neighbor
        if not cell.walls['right'] and col < self.cols - 1:
            neighbors.append((row, col + 1))

        return neighbors

def map_pixel_to_cell(pixel_coords, h_grid_lines, v_grid_lines):
    """
    Maps pixel coordinates (x, y) to its respective indexed cell in the maze.
    """
    if not pixel_coords:
        return None  # If no valid pixel coordinate found

    x, y = pixel_coords

    # Find corresponding row index
    row = None
    for i in range(len(h_grid_lines) - 1):
        if h_grid_lines[i] <= y < h_grid_lines[i + 1]:
            row = i
            break

    # Find corresponding column index
    col = None
    for i in range(len(v_grid_lines) - 1):
        if v_grid_lines[i] <= x < v_grid_lines[i + 1]:
            col = i
            break

    if row is not None and col is not None:
        return (row, col)  # Return the indexed cell coordinates
    else:
        return None  # No matching cell found


def assign_start_end_cells(maze, start_pixel_coords, end_pixel_coords, h_grid_lines, v_grid_lines):
    """
    Assigns start and end nodes to the respective cells in the maze.
    """
    # Convert pixel positions to cell indexes
    start_cell = map_pixel_to_cell(start_pixel_coords, h_grid_lines, v_grid_lines)
    end_cell = map_pixel_to_cell(end_pixel_coords, h_grid_lines, v_grid_lines)

    if start_cell:
        row, col = start_cell
        maze.grid[row][col].is_start = True
        maze.start_cell = (row, col)
        maze.start = maze.get_cell_id(row, col)

    if end_cell:
        row, col = end_cell
        maze.grid[row][col].is_end = True
        maze.end_cell = (row, col)
        maze.end = maze.get_cell_id(row, col)

    return maze
