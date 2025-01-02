import tkinter as tk
from tkinter import ttk, messagebox
import random
import heapq


class UnionFind:
    def __init__(self, size):
        self.parent = list(range(size))
        self.rank = [0] * size

    def find(self, x):
        """Find the root of x with path compression."""
        if self.parent[x] != x:
            self.parent[x] = self.find(self.parent[x])
        return self.parent[x]

    def union(self, x, y):
        """Union by rank. Returns True if union was successful, False if already connected."""
        fx = self.find(x)
        fy = self.find(y)
        if fx == fy:
            return False  # Already in the same set
        if self.rank[fx] < self.rank[fy]:
            self.parent[fx] = fy
        else:
            self.parent[fy] = fx
            if self.rank[fx] == self.rank[fy]:
                self.rank[fx] += 1
        return True


class Cell:
    def __init__(self, row, col):
        self.row = row
        self.col = col
        # Walls: top, bottom, left, right
        self.walls = {'top': True, 'bottom': True, 'left': True, 'right': True}


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


class MazeApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Maze Generator and Pathfinding Visualizer")
        self.root.geometry("1200x900")
        self.root.resizable(True, True)

        # Apply a modern theme
        style = ttk.Style(root)
        style.theme_use('clam')  # Options: 'clam', 'alt', 'default', 'classic'

        # Create main frames
        control_frame = ttk.Frame(root, padding="10 10 10 10")
        control_frame.pack(side=tk.TOP, fill=tk.X)

        canvas_frame = ttk.Frame(root, padding="10 10 10 10")
        canvas_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        # -- SIZE LABEL --
        size_label = ttk.Label(control_frame, text="Enter Size (rows):", font=("Arial", 12))
        size_label.grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)

        # -- SIZE ENTRY --
        self.size_entry = ttk.Entry(control_frame, width=10)
        self.size_entry.grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
        self.size_entry.insert(0, "10")  # Default value

        # -- PATHFINDING ALGORITHM SELECTION --
        solver_label = ttk.Label(control_frame, text="Select Solver Algorithm:", font=("Arial", 12))
        solver_label.grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)

        self.solver_var = tk.StringVar(value="BFS")
        solver_options = ["BFS", "DFS", "Dijkstra's", "A*", "Jump Point Search"]
        solver_menu = ttk.OptionMenu(control_frame, self.solver_var, self.solver_var.get(), *solver_options)
        solver_menu.grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)

        # -- BUTTONS --
        button_frame = ttk.Frame(control_frame)
        button_frame.grid(row=2, column=0, columnspan=2, pady=15)

        self.generate_button = ttk.Button(button_frame, text="Generate Maze", command=self.generate_maze)
        self.generate_button.grid(row=0, column=0, padx=5)

        self.solve_button = ttk.Button(button_frame, text="Solve Maze", command=self.solve_maze, state="disabled")
        self.solve_button.grid(row=0, column=1, padx=5)

        self.reset_button = ttk.Button(button_frame, text="Reset Maze", command=self.reset_maze, state="disabled")
        self.reset_button.grid(row=0, column=2, padx=5)

        self.clear_path_button = ttk.Button(button_frame, text="Clear Path", command=self.clear_path, state="disabled")
        self.clear_path_button.grid(row=0, column=3, padx=5)

        # -- CUSTOM MAZE TOOLS --
        tools_frame = ttk.Frame(control_frame)
        tools_frame.grid(row=3, column=0, columnspan=2, pady=10)

        self.draw_wall_button = ttk.Button(tools_frame, text="Draw Walls", command=self.set_draw_mode, state="disabled")
        self.draw_wall_button.grid(row=0, column=0, padx=5)

        self.erase_wall_button = ttk.Button(tools_frame, text="Erase Walls", command=self.set_erase_mode,
                                            state="disabled")
        self.erase_wall_button.grid(row=0, column=1, padx=5)

        # -- STATUS BAR --
        self.status_var = tk.StringVar()
        status_bar = ttk.Label(root, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)

        # -- CANVAS FOR MAZE --
        self.canvas = tk.Canvas(canvas_frame, bg="white")
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar_y = ttk.Scrollbar(canvas_frame, orient=tk.VERTICAL, command=self.canvas.yview)
        scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)
        scrollbar_x = ttk.Scrollbar(root, orient=tk.HORIZONTAL, command=self.canvas.xview)
        scrollbar_x.pack(side=tk.BOTTOM, fill=tk.X)

        self.canvas.configure(yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)

        # Bind mouse events for custom maze creation
        self.canvas.bind("<Button-1>", self.on_canvas_click)

        # Initialize maze-related variables
        self.maze = None
        self.path = []
        self.animation_speed = 50  # Milliseconds between steps
        self.draw_mode = False
        self.erase_mode = False

    def generate_maze(self):
        """Generate the maze and visualize it."""
        try:
            size = int(self.size_entry.get())
            if size <= 0:
                raise ValueError("Size must be a positive integer.")
            if size == 1:
                raise ValueError("Size must be greater than 1 to create a meaningful maze.")

            # Disable buttons during generation
            self.toggle_buttons(state="disabled")
            self.status_var.set(f"Generating a square maze of size {size}x{size}...")
            self.root.update_idletasks()

            # Generate the maze
            self.maze = Maze(size)
            self.maze.generate_maze()

            # Randomize start and end points
            self.start, self.end = self.randomize_start_end()

            # Open walls for start and end points
            self.open_start_end_walls()

            # Visualize the maze
            self.visualize_maze()

            self.status_var.set("Maze generated successfully.")
            self.toggle_buttons(state="normal", exclude=["generate_button"])
            self.solve_button.configure(state="normal")
            self.reset_button.configure(state="normal")
            self.draw_wall_button.configure(state="normal")
            self.erase_wall_button.configure(state="normal")
            self.clear_path_button.configure(state="disabled")

        except ValueError as ve:
            messagebox.showerror("Invalid Input", str(ve))
            self.status_var.set("Failed to generate maze.")
            self.toggle_buttons(state="normal")
        except Exception as e:
            messagebox.showerror("Error", f"An unexpected error occurred: {e}")
            self.status_var.set("Failed to generate maze.")
            self.toggle_buttons(state="normal")

    def toggle_buttons(self, state="normal", exclude=[]):
        """Enable or disable all buttons except those in the exclude list."""
        buttons = [
            self.generate_button,
            self.solve_button,
            self.reset_button,
            self.clear_path_button,
            self.draw_wall_button,
            self.erase_wall_button
        ]
        for btn in buttons:
            if btn not in exclude:
                btn.configure(state=state)

    def randomize_start_end(self):
        """Randomly select start and end points ensuring they are on top and bottom rows respectively."""
        size = self.maze.size
        # Select start from top row
        start_col = random.randint(0, size - 1)
        start_id = self.maze.get_cell_id(0, start_col)

        # Select end from bottom row
        end_col = random.randint(0, size - 1)
        end_id = self.maze.get_cell_id(size - 1, end_col)

        return start_id, end_id

    def open_start_end_walls(self):
        """Open the top wall of the start cell and the bottom wall of the end cell."""
        maze = self.maze

        # Open start cell's top wall
        start_row, start_col = divmod(self.start, maze.cols)
        self.maze.grid[start_row][start_col].walls['top'] = False

        # Open end cell's bottom wall
        end_row, end_col = divmod(self.end, maze.cols)
        self.maze.grid[end_row][end_col].walls['bottom'] = False

    def visualize_maze(self):
        """Draw the maze on the canvas."""
        self.canvas.delete("all")
        maze = self.maze
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()

        if canvas_width < 100 or canvas_height < 100:
            # Default size if the window is not fully rendered yet
            canvas_width = 800
            canvas_height = 600

        self.cell_size = max(min(canvas_width, canvas_height) // maze.size, 20)

        self.canvas.configure(scrollregion=(0, 0, maze.cols * self.cell_size + 20, maze.rows * self.cell_size + 20))

        # Store wall IDs for interaction
        self.wall_ids = {}

        for r in range(maze.rows):
            for c in range(maze.cols):
                x = c * self.cell_size + 10
                y = r * self.cell_size + 10
                cell = maze.grid[r][c]

                # Draw walls and assign tags for interaction
                if cell.walls['top']:
                    wall_tag = f"wall_{r}_{c}_top"
                    wall = self.canvas.create_line(x, y, x + self.cell_size, y, fill="black", width=3, tags=wall_tag)
                    self.wall_ids[wall_tag] = ((r, c), (r, c + 1))
                if cell.walls['left']:
                    wall_tag = f"wall_{r}_{c}_left"
                    wall = self.canvas.create_line(x, y, x, y + self.cell_size, fill="black", width=3, tags=wall_tag)
                    self.wall_ids[wall_tag] = ((r, c), (r + 1, c))
                if cell.walls['bottom']:
                    wall_tag = f"wall_{r}_{c}_bottom"
                    wall = self.canvas.create_line(x, y + self.cell_size, x + self.cell_size, y + self.cell_size,
                                                   fill="black", width=3, tags=wall_tag)
                    self.wall_ids[wall_tag] = ((r, c), (r, c + 1))
                if cell.walls['right']:
                    wall_tag = f"wall_{r}_{c}_right"
                    wall = self.canvas.create_line(x + self.cell_size, y, x + self.cell_size, y + self.cell_size,
                                                   fill="black", width=3, tags=wall_tag)
                    self.wall_ids[wall_tag] = ((r, c), (r + 1, c))

        # Highlight start and end points
        self.highlight_start_end()

    def highlight_start_end(self):
        """Highlight the start and end points with fixed positions on top and bottom rows."""
        maze = self.maze
        start_id = self.start
        end_id = self.end

        start_row, start_col = divmod(start_id, maze.cols)
        end_row, end_col = divmod(end_id, maze.cols)

        # Draw start point
        x_start = start_col * self.cell_size + 10
        y_start = start_row * self.cell_size + 10
        self.canvas.create_rectangle(
            x_start + 4, y_start + 4,
            x_start + self.cell_size - 4, y_start + self.cell_size - 4,
            fill="green", outline="", tags="start"
        )

        # Draw end point
        x_end = end_col * self.cell_size + 10
        y_end = end_row * self.cell_size + 10
        self.canvas.create_rectangle(
            x_end + 4, y_end + 4,
            x_end + self.cell_size - 4, y_end + self.cell_size - 4,
            fill="red", outline="", tags="end"
        )

    def solve_maze(self):
        """Initiate the selected pathfinding algorithm."""
        if not self.maze:
            messagebox.showwarning("No Maze", "Please generate a maze first.")
            return

        self.path = []
        algorithm = self.solver_var.get()
        self.status_var.set(f"Solving maze using {algorithm} algorithm...")
        self.root.update_idletasks()

        start = self.start
        end = self.end

        # Disable buttons during solving
        self.toggle_buttons(state="disabled", exclude=["reset_button", "clear_path_button"])
        self.clear_path_button.configure(state="disabled")

        if algorithm == "BFS":
            self.bfs(start, end)
        elif algorithm == "DFS":
            self.dfs(start, end)
        elif algorithm == "Dijkstra's":
            self.dijkstra(start, end)
        elif algorithm == "A*":
            self.a_star(start, end)
        elif algorithm == "Jump Point Search":
            self.jump_point_search(start, end)
        else:
            messagebox.showerror("Unknown Algorithm", f"Solver '{algorithm}' is not implemented.")
            self.status_var.set("Failed to solve maze.")
            self.toggle_buttons(state="normal")
            self.clear_path_button.configure(state="normal")

    def reset_maze(self):
        """Clear the current maze and path."""
        self.canvas.delete("all")
        self.maze = None
        self.path = []
        self.start = None
        self.end = None
        self.status_var.set("Maze reset. Generate a new maze.")

        # Disable all buttons except Generate
        self.toggle_buttons(state="disabled")
        self.generate_button.configure(state="normal")
        self.clear_path_button.configure(state="disabled")

    def clear_path(self):
        """Clear the current path visualization."""
        # Remove all path-related tags
        self.canvas.delete("path")
        self.status_var.set("Path cleared.")

    # ---------------- Pathfinding Algorithms ---------------- #

    def bfs(self, start, end):
        from collections import deque

        maze = self.maze
        queue = deque([start])
        visited = set([start])
        parent = {}

        def step():
            if not queue:
                self.status_var.set("No solution found using BFS.")
                self.toggle_buttons(state="normal")
                return
            current = queue.popleft()
            if current == end:
                self.reconstruct_path(parent, start, end)
                self.status_var.set("Maze solved successfully using BFS.")
                self.toggle_buttons(state="normal")
                return
            row, col = divmod(current, maze.cols)
            neighbors = self.get_neighbors(row, col)
            for neighbor in neighbors:
                neighbor_id = maze.get_cell_id(neighbor[0], neighbor[1])
                if neighbor_id not in visited:
                    visited.add(neighbor_id)
                    parent[neighbor_id] = current
                    queue.append(neighbor_id)
                    self.highlight_cell(neighbor_id, "yellow")
            self.root.after(self.animation_speed, step)

        step()

    def dfs(self, start, end):
        maze = self.maze
        stack = [start]
        visited = set([start])
        parent = {}

        def step():
            if not stack:
                self.status_var.set("No solution found using DFS.")
                self.toggle_buttons(state="normal")
                return
            current = stack.pop()
            if current == end:
                self.reconstruct_path(parent, start, end)
                self.status_var.set("Maze solved successfully using DFS.")
                self.toggle_buttons(state="normal")
                return
            row, col = divmod(current, maze.cols)
            neighbors = self.get_neighbors(row, col)
            for neighbor in neighbors:
                neighbor_id = maze.get_cell_id(neighbor[0], neighbor[1])
                if neighbor_id not in visited:
                    visited.add(neighbor_id)
                    parent[neighbor_id] = current
                    stack.append(neighbor_id)
                    self.highlight_cell(neighbor_id, "yellow")
            self.root.after(self.animation_speed, step)

        step()

    def dijkstra(self, start, end):
        maze = self.maze
        heap = []
        heapq.heappush(heap, (0, start))
        distances = {node: float('inf') for node in range(maze.rows * maze.cols)}
        distances[start] = 0
        parent = {}
        visited = set()

        def step():
            if not heap:
                self.status_var.set("No solution found using Dijkstra's Algorithm.")
                self.toggle_buttons(state="normal")
                return
            current_distance, current = heapq.heappop(heap)
            if current in visited:
                self.root.after(self.animation_speed, step)
                return
            visited.add(current)
            if current == end:
                self.reconstruct_path(parent, start, end)
                self.status_var.set("Maze solved successfully using Dijkstra's Algorithm.")
                self.toggle_buttons(state="normal")
                return
            row, col = divmod(current, maze.cols)
            neighbors = self.get_neighbors(row, col)
            for neighbor in neighbors:
                neighbor_id = maze.get_cell_id(neighbor[0], neighbor[1])
                if neighbor_id in visited:
                    continue
                new_dist = current_distance + 1  # Assuming uniform cost
                if new_dist < distances[neighbor_id]:
                    distances[neighbor_id] = new_dist
                    parent[neighbor_id] = current
                    heapq.heappush(heap, (new_dist, neighbor_id))
                    self.highlight_cell(neighbor_id, "yellow")
            self.root.after(self.animation_speed, step)

        step()

    def a_star(self, start, end):
        maze = self.maze
        heap = []
        heapq.heappush(heap, (0, start))
        distances = {node: float('inf') for node in range(maze.rows * maze.cols)}
        distances[start] = 0
        parent = {}
        visited = set()

        def heuristic(a, b):
            """Manhattan distance heuristic."""
            a_row, a_col = divmod(a, maze.cols)
            b_row, b_col = divmod(b, maze.cols)
            return abs(a_row - b_row) + abs(a_col - b_col)

        def step():
            if not heap:
                self.status_var.set("No solution found using A* Algorithm.")
                self.toggle_buttons(state="normal")
                return
            current_f, current = heapq.heappop(heap)
            if current in visited:
                self.root.after(self.animation_speed, step)
                return
            visited.add(current)
            if current == end:
                self.reconstruct_path(parent, start, end)
                self.status_var.set("Maze solved successfully using A* Algorithm.")
                self.toggle_buttons(state="normal")
                return
            row, col = divmod(current, maze.cols)
            neighbors = self.get_neighbors(row, col)
            for neighbor in neighbors:
                neighbor_id = maze.get_cell_id(neighbor[0], neighbor[1])
                if neighbor_id in visited:
                    continue
                tentative_g = distances[current] + 1  # Assuming uniform cost
                if tentative_g < distances[neighbor_id]:
                    distances[neighbor_id] = tentative_g
                    f_score = tentative_g + heuristic(neighbor_id, end)
                    parent[neighbor_id] = current
                    heapq.heappush(heap, (f_score, neighbor_id))
                    self.highlight_cell(neighbor_id, "yellow")
            self.root.after(self.animation_speed, step)

        step()

    def jump_point_search(self, start, end):
        """Placeholder for Jump Point Search algorithm implementation."""
        messagebox.showinfo("Algorithm Not Implemented", "Jump Point Search is not yet implemented.")
        self.status_var.set("Jump Point Search algorithm is under development.")
        self.toggle_buttons(state="normal")

    # ---------------- Pathfinding Helpers ---------------- #

    def get_neighbors(self, row, col):
        """Return list of accessible neighbors for a cell."""
        neighbors = []
        maze = self.maze
        cell = maze.grid[row][col]
        if not cell.walls['top'] and row > 0:
            neighbors.append((row - 1, col))
        if not cell.walls['bottom'] and row < maze.rows - 1:
            neighbors.append((row + 1, col))
        if not cell.walls['left'] and col > 0:
            neighbors.append((row, col - 1))
        if not cell.walls['right'] and col < maze.cols - 1:
            neighbors.append((row, col + 1))
        return neighbors

    def reconstruct_path(self, parent, start, end):
        """Reconstruct the path from start to end using the parent dictionary."""
        path = []
        current = end
        while current != start:
            path.append(current)
            current = parent.get(current)
            if current is None:
                messagebox.showinfo("No Solution", "No path could be found in the maze.")
                self.status_var.set("No solution found.")
                self.toggle_buttons(state="normal")
                return
        path.append(start)
        path.reverse()
        self.path = path
        self.animate_path()

    def animate_path(self):
        """Animate the final path."""
        for idx, node in enumerate(self.path):
            self.root.after(idx * self.animation_speed, lambda n=node: self.highlight_path(n))
        self.status_var.set("Pathfinding complete.")
        self.toggle_buttons(state="normal")
        self.clear_path_button.configure(state="normal")

    def highlight_cell(self, node_id, color):
        """Highlight a cell temporarily."""
        row, col = divmod(node_id, self.maze.cols)
        x = col * self.cell_size + 10
        y = row * self.cell_size + 10
        self.canvas.create_rectangle(
            x + 2, y + 2,
            x + self.cell_size - 2, y + self.cell_size - 2,
            fill=color, outline="", tags="path"
        )
        self.canvas.update_idletasks()

    def highlight_path(self, node_id):
        """Highlight the path permanently."""
        row, col = divmod(node_id, self.maze.cols)
        x = col * self.cell_size + 10
        y = row * self.cell_size + 10
        self.canvas.create_rectangle(
            x + 4, y + 4,
            x + self.cell_size - 4, y + self.cell_size - 4,
            fill="blue", outline="", tags="path"
        )
        self.canvas.update_idletasks()

    # ---------------- Custom Maze Creation ---------------- #

    def set_draw_mode(self):
        """Set the mode to draw walls."""
        self.draw_mode = True
        self.erase_mode = False
        self.status_var.set("Draw mode activated. Click on walls to add.")

    def set_erase_mode(self):
        """Set the mode to erase walls."""
        self.erase_mode = True
        self.draw_mode = False
        self.status_var.set("Erase mode activated. Click on walls to remove.")

    def on_canvas_click(self, event):
        """Handle canvas click events to draw or erase walls."""
        if not self.maze:
            return  # Do nothing if maze is not generated

        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)
        col = int((x - 10) // self.cell_size)
        row = int((y - 10) // self.cell_size)

        # Determine if the click is near a wall
        tolerance = 10  # Increased tolerance for easier clicking
        clicked_wall = None

        # Check top wall
        wall_top = f"wall_{row}_{col}_top"
        wall_bottom = f"wall_{row}_{col}_bottom"
        wall_left = f"wall_{row}_{col}_left"
        wall_right = f"wall_{row}_{col}_right"

        walls_to_check = {
            'top': wall_top,
            'bottom': wall_bottom,
            'left': wall_left,
            'right': wall_right
        }

        for direction, wall_tag in walls_to_check.items():
            if wall_tag not in self.wall_ids:
                continue  # Wall does not exist
            coords = self.canvas.coords(wall_tag)
            if not coords:
                continue  # Wall not present
            if direction in ['top', 'bottom']:
                # Horizontal walls
                wx1, wy1, wx2, wy2 = coords
                if abs(y - wy1) <= tolerance and wx1 <= x <= wx2:
                    clicked_wall = wall_tag
                    break
            else:
                # Vertical walls
                wx1, wy1, wx2, wy2 = coords
                if abs(x - wx1) <= tolerance and wy1 <= y <= wy2:
                    clicked_wall = wall_tag
                    break

        if clicked_wall:
            if self.draw_mode:
                self.add_wall(clicked_wall)
            elif self.erase_mode:
                self.remove_wall(clicked_wall)

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
        self.canvas.itemconfigure(wall_tag, fill="black")
        self.status_var.set("Wall added.")

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
        self.canvas.itemconfigure(wall_tag, fill="white")
        self.status_var.set("Wall removed.")


# ---------------- Main Function ---------------- #

def main():
    root = tk.Tk()
    app = MazeApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
