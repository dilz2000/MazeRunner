# views/maze_canvas.py

# Handles drawing the maze on a tkinter canvas
# Key methods:
#
# draw_maze(): Renders maze walls
# highlight_start_end(): Marks start and end points
# highlight_cell(): Temporarily highlights cells
# highlight_path(): Marks final path
# add_wall() and remove_wall(): Allows wall modification

import tkinter as tk

class MazeCanvas(tk.Canvas):
    def __init__(self, parent, maze, cell_size, *args, **kwargs):
        super().__init__(parent, bg="white", *args, **kwargs)
        self.maze = maze
        self.cell_size = cell_size
        self.wall_ids = {}
        self.draw_maze()

    def draw_maze(self):
        """Draw the maze on the canvas."""
        self.delete("all")
        maze = self.maze
        for r in range(maze.rows):
            for c in range(maze.cols):
                x = c * self.cell_size + 10
                y = r * self.cell_size + 10
                cell = maze.grid[r][c]

                # Draw walls and assign tags for interaction
                if cell.walls['top']:
                    wall_tag = f"wall_{r}_{c}_top"
                    wall = self.create_line(x, y, x + self.cell_size, y, fill="black", width=3, tags=wall_tag)
                    self.wall_ids[wall_tag] = ((r, c), (r, c + 1))
                if cell.walls['left']:
                    wall_tag = f"wall_{r}_{c}_left"
                    wall = self.create_line(x, y, x, y + self.cell_size, fill="black", width=3, tags=wall_tag)
                    self.wall_ids[wall_tag] = ((r, c), (r + 1, c))
                if cell.walls['bottom']:
                    wall_tag = f"wall_{r}_{c}_bottom"
                    wall = self.create_line(x, y + self.cell_size, x + self.cell_size, y + self.cell_size, fill="black",
                                            width=3, tags=wall_tag)
                    self.wall_ids[wall_tag] = ((r, c), (r, c + 1))
                if cell.walls['right']:
                    wall_tag = f"wall_{r}_{c}_right"
                    wall = self.create_line(x + self.cell_size, y, x + self.cell_size, y + self.cell_size, fill="black",
                                            width=3, tags=wall_tag)
                    self.wall_ids[wall_tag] = ((r, c), (r + 1, c))

    def highlight_start_end(self, start, end):
        """Highlight the start and end points."""
        print("checkpoint 6")
        maze = self.maze
        print("checkpoint 7")
        if isinstance(start, tuple):  # MazeL (Uploaded Image)
            start_row, start_col = start
            end_row, end_col = end
        else:  # Maze (Generated Maze)
            start_row, start_col = divmod(start, maze.cols)
            end_row, end_col = divmod(end, maze.cols)

        print("checkpoint 8")

        # Draw start point
        x_start = start_col * self.cell_size + 10
        y_start = start_row * self.cell_size + 10
        self.create_rectangle(
            x_start + 4, y_start + 4,
            x_start + self.cell_size - 4, y_start + self.cell_size - 4,
            fill="green", outline="", tags="start"
        )

        # Draw end point
        x_end = end_col * self.cell_size + 10
        y_end = end_row * self.cell_size + 10
        self.create_rectangle(
            x_end + 4, y_end + 4,
            x_end + self.cell_size - 4, y_end + self.cell_size - 4,
            fill="red", outline="", tags="end"
        )

    def highlight_start_end(self, start, end):
        """Highlight the start and end points."""
        print("checkpoint 6")

        maze = self.maze
        print("checkpoint 7")

        # Ensure correct format for start/end based on maze type
        if isinstance(start, tuple):  # MazeL (Uploaded Image)
            print("Detected tuple-based start/end values!")
            start_row, start_col = start
            end_row, end_col = end
        else:  # Maze (Generated Maze)
            print("Detected integer-based start/end values!")
            start_row, start_col = divmod(start, maze.cols)
            end_row, end_col = divmod(end, maze.cols)

        print(f"Start Cell: ({start_row}, {start_col}), End Cell: ({end_row}, {end_col})")  # Debugging
        print("checkpoint 8")

        # Draw start point
        x_start = start_col * self.cell_size + 10
        y_start = start_row * self.cell_size + 10
        self.create_rectangle(
            x_start + 4, y_start + 4,
            x_start + self.cell_size - 4, y_start + self.cell_size - 4,
            fill="green", outline="", tags="start"
        )

        # Draw end point
        x_end = end_col * self.cell_size + 10
        y_end = end_row * self.cell_size + 10
        self.create_rectangle(
            x_end + 4, y_end + 4,
            x_end + self.cell_size - 4, y_end + self.cell_size - 4,
            fill="red", outline="", tags="end"
        )
        print("Checkpoint 9: Successfully drew start/end points.")

    def add_wall(self, wall_tag):
        """Add a wall by setting the corresponding cell's wall to True and redraw the wall."""
        if wall_tag not in self.wall_ids:
            return

        (r1, c1), (r2, c2) = self.wall_ids[wall_tag]
        cell1 = self.maze.grid[r1][c1]
        cell2 = self.maze.grid[r2][c2]

        # Determine which wall to add
        if r1 == r2:
            # Horizontal wall between (r, c) and (r, c+1)
            cell1.walls['right'] = True
            cell2.walls['left'] = True
        else:
            # Vertical wall between (r, c) and (r+1, c)
            cell1.walls['bottom'] = True
            cell2.walls['top'] = True

        # Redraw the wall
        self.itemconfigure(wall_tag, fill="black")

    def remove_wall(self, wall_tag):
        """Remove a wall by setting the corresponding cell's wall to False and redraw the wall."""
        if wall_tag not in self.wall_ids:
            return

        (r1, c1), (r2, c2) = self.wall_ids[wall_tag]
        cell1 = self.maze.grid[r1][c1]
        cell2 = self.maze.grid[r2][c2]

        # Determine which wall to remove
        if r1 == r2:
            # Horizontal wall between (r, c) and (r, c+1)
            cell1.walls['right'] = False
            cell2.walls['left'] = False
        else:
            # Vertical wall between (r, c) and (r+1, c)
            cell1.walls['bottom'] = False
            cell2.walls['top'] = False

        # Redraw the wall
        self.itemconfigure(wall_tag, fill="white")

    def highlight_cell(self, node_id, color):
        """Highlight a cell temporarily."""
        row, col = divmod(node_id, self.maze.cols)
        x = col * self.cell_size + 10
        y = row * self.cell_size + 10
        self.create_rectangle(
            x + 2, y + 2,
            x + self.cell_size - 2, y + self.cell_size - 2,
            fill=color, outline="", tags="path"
        )
        self.update_idletasks()

    def highlight_path(self, node_id):
        """Highlight the path permanently."""
        row, col = divmod(node_id, self.maze.cols)
        x = col * self.cell_size + 10
        y = row * self.cell_size + 10
        self.create_rectangle(
            x + 4, y + 4,
            x + self.cell_size - 4, y + self.cell_size - 4,
            fill="darkblue", outline="", tags="path"
        )
        self.update_idletasks()

    def clear_path(self):
        """Clear the current path visualization."""
        self.delete("path")
