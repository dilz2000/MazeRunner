# maze_app/ui/visualization.py

import tkinter as tk


class MazeCanvas(tk.Canvas):
    def __init__(self, parent, maze, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.maze = maze
        self.solution = []
        self.cell_size = 20  # Default cell size
        self.margin = 20  # Margin around the maze
        self.draw_maze()

    def draw_maze(self):
        self.delete("all")
        rows = self.maze.rows
        cols = self.maze.cols
        self.cell_size = min((self.winfo_width() - 2 * self.margin) // cols,
                             (self.winfo_height() - 2 * self.margin) // rows)
        for node_id, node in self.maze.nodes.items():
            row, col = node.row, node.col
            x = self.margin + col * self.cell_size
            y = self.margin + row * self.cell_size
            # Draw lines to connected neighbors
            for neighbor in node.neighbors:
                n_row, n_col = self.get_row_col(neighbor, cols)
                nx = self.margin + n_col * self.cell_size
                ny = self.margin + n_row * self.cell_size
                self.create_line(x + self.cell_size, y + self.cell_size // 2,
                                 nx, ny + self.cell_size // 2, fill="black")
                self.create_line(x + self.cell_size // 2, y + self.cell_size,
                                 nx + self.cell_size // 2, ny, fill="black")
        # Draw start and end points
        self.draw_start_end()

    def get_row_col(self, node_id, cols):
        return node_id // cols, node_id % cols

    def draw_start_end(self):
        # Draw start (top-left) and end (bottom-right)
        start_x = self.margin + 0 * self.cell_size + self.cell_size // 2
        start_y = self.margin + 0 * self.cell_size + self.cell_size // 2
        end_x = self.margin + (self.maze.cols - 1) * self.cell_size + self.cell_size // 2
        end_y = self.margin + (self.maze.rows - 1) * self.cell_size + self.cell_size // 2
        radius = self.cell_size // 4
        self.create_oval(start_x - radius, start_y - radius,
                         start_x + radius, start_y + radius,
                         fill="green", outline="")
        self.create_oval(end_x - radius, end_y - radius,
                         end_x + radius, end_y + radius,
                         fill="red", outline="")

    def draw_solution(self, path):
        if not path:
            return
        self.solution = path
        for i in range(len(path) - 1):
            node1 = self.maze.nodes[path[i]]
            node2 = self.maze.nodes[path[i + 1]]
            x1 = self.margin + node1.col * self.cell_size + self.cell_size // 2
            y1 = self.margin + node1.row * self.cell_size + self.cell_size // 2
            x2 = self.margin + node2.col * self.cell_size + self.cell_size // 2
            y2 = self.margin + node2.row * self.cell_size + self.cell_size // 2
            self.create_line(x1, y1, x2, y2, fill="blue", width=2, tag="solution")

    def clear_solution(self):
        self.delete("solution")
        self.solution = []
