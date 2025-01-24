# controllers/maze_app.py

import tkinter as tk
from tkinter import ttk, messagebox
import heapq
import random
from collections import deque

from models.maze import Maze
from views.maze_canvas import MazeCanvas
from solvers.bfs_solver import BFSSolver
from solvers.dfs_solver import DFSSolver
from solvers.dijkstra_solver import DijkstraSolver
from solvers.a_star_solver import AStarSolver
from solvers.jump_point_search_solver import JumpPointSearchSolver


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
        self.maze_canvas = None  # Will be initialized after maze generation

        # Bind mouse events for custom maze creation
        root.bind("<Configure>", self.on_resize)

        # Initialize maze-related variables
        self.maze = None
        self.path = []
        self.animation_speed = 50  # Milliseconds between steps
        self.draw_mode = False
        self.erase_mode = False

    def on_resize(self, event):
        """Handle window resizing to adjust the maze canvas."""
        if self.maze and self.maze_canvas:
            self.update_maze_canvas()

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
        """Initialize and draw the maze on the canvas."""
        if self.maze_canvas:
            self.maze_canvas.destroy()

        # Determine cell size based on current window size
        canvas_width = self.root.winfo_width() - 40
        canvas_height = self.root.winfo_height() - 200  # Adjust based on control frame height
        cell_size = max(min(canvas_width, canvas_height) // self.maze.size, 20)

        self.maze_canvas = MazeCanvas(self.root, self.maze, cell_size, width=self.maze.size * cell_size + 20,
                                      height=self.maze.size * cell_size + 20)
        self.maze_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Highlight start and end points
        self.maze_canvas.highlight_start_end(self.start, self.end)

    def update_maze_canvas(self):
        """Update the maze canvas when the window is resized."""
        if self.maze and self.maze_canvas:
            # Recalculate cell size
            canvas_width = self.root.winfo_width() - 40
            canvas_height = self.root.winfo_height() - 200  # Adjust based on control frame height
            cell_size = max(min(canvas_width, canvas_height) // self.maze.size, 20)

            self.maze_canvas.cell_size = cell_size
            self.maze_canvas.config(width=self.maze.size * cell_size + 20, height=self.maze.size * cell_size + 20)
            self.maze_canvas.draw_maze()
            self.maze_canvas.highlight_start_end(self.start, self.end)
            self.maze_canvas.clear_path()

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

        # Select the appropriate solver
        solver = None
        if algorithm == "BFS":
            solver = BFSSolver(self.maze, start, end, self.maze_canvas, self.animation_speed)
        elif algorithm == "DFS":
            solver = DFSSolver(self.maze, start, end, self.maze_canvas, self.animation_speed)
        elif algorithm == "Dijkstra's":
            solver = DijkstraSolver(self.maze, start, end, self.maze_canvas, self.animation_speed)
        elif algorithm == "A*":
            solver = AStarSolver(self.maze, start, end, self.maze_canvas, self.animation_speed)
        elif algorithm == "Jump Point Search":
            solver = JumpPointSearchSolver(self.maze, start, end, self.maze_canvas, self.animation_speed)
        else:
            messagebox.showerror("Unknown Algorithm", f"Solver '{algorithm}' is not implemented.")
            self.status_var.set("Failed to solve maze.")
            self.toggle_buttons(state="normal")
            self.clear_path_button.configure(state="normal")
            return

        if solver:
            solver.solve(self.on_solver_complete)

    def on_solver_complete(self, success):
        """Callback when the solver completes."""
        if success:
            self.status_var.set("Pathfinding complete.")
        else:
            self.status_var.set("No solution found.")
        self.toggle_buttons(state="normal")
        self.clear_path_button.configure(state="normal")

    def reset_maze(self):
        """Clear the current maze and path."""
        if self.maze_canvas:
            self.maze_canvas.destroy()
            self.maze_canvas = None
        self.maze = None
        self.path = []
        self.start = None
        self.end = None
        self.status_var.set("Maze reset. Generate a new maze.")

        # Disable all buttons except Generate
        self.toggle_buttons(state="disabled")
        self.generate_button.configure(state="normal")  # Re-enable Generate Maze button
        self.clear_path_button.configure(state="disabled")

    def clear_path(self):
        """Clear the current path visualization."""
        if self.maze_canvas:
            self.maze_canvas.clear_path()
        self.status_var.set("Path cleared.")

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
