# controllers/maze_app.py

# maze_app.py (Application Controller):
# Manages user interface and maze generation flow
# Key responsibilities:
# Create UI elements
# Handle maze generation
# Manage start/end point randomization
# Control canvas sizing and updates
# Handle user interactions
import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox, filedialog
from PIL import Image, ImageTk
import numpy as np
import heapq
import random
from collections import deque

from image_processor import preprocess_image, extract_maze_structure, detect_grid_lines, build_grid_from_hough_lines, \
    group_nearby_lines, adjust_grid_lines_to_maze, find_openings_in_outer_walls, determine_cell_from_opening, \
    extract_clean_maze, find_start_end_nodes
from models.maze import Maze
from models.maze_image import assign_start_end_cells, MazeL
from solvers.greedy_search import GreedyBestFirstSolver
from solvers.iterative_deepening_DFS_solver import IterativeDeepeningDFSSolver
from solvers.jump_point_search_solver import JumpPointSearchSolver
from solvers.wilson_solver import WilsonSolver
from views.maze_canvas import MazeCanvas
from solvers.bfs_solver import BFSSolver
from solvers.dfs_solver import DFSSolver
from solvers.dijkstra_solver import DijkstraSolver
from solvers.a_star_solver import AStarSolver



class MazeApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Maze Runner")
        self.root.geometry("1200x900")
        self.root.resizable(True, True)

        ctk.set_appearance_mode("System")
        ctk.set_default_color_theme("dark-blue")

        control_frame = ctk.CTkFrame(root, width=400, corner_radius=10)
        control_frame.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)

        # -- SIZE LABEL AND ENTRY --
        size_frame = ctk.CTkFrame(control_frame, corner_radius=10)
        size_frame.pack(fill=tk.X, pady=5, padx=5)

        size_label = ctk.CTkLabel(size_frame, text="Maze Size (rows):", font=("Arial", 14))
        size_label.pack(side=tk.LEFT, padx=5, pady=5)

        self.size_entry = ctk.CTkEntry(size_frame, width=100, font=("Arial", 14))
        self.size_entry.pack(side=tk.RIGHT, padx=5, pady=5)
        self.size_entry.insert(0, "10")  # Default value

        # -- PATHFINDING ALGORITHM SELECTION --
        solver_frame = ctk.CTkFrame(control_frame, corner_radius=10)
        solver_frame.pack(fill=tk.X, pady=5, padx=5)

        solver_label = ctk.CTkLabel(solver_frame, text="Solver Algorithm:", font=("Arial", 14))
        solver_label.pack(side=tk.LEFT, padx=5, pady=5)

        self.solver_var = tk.StringVar(value="BFS")
        solver_options = ["BFS", "DFS", "Dijkstra's", "A*", "Jump Point Search", "Wilson", "Greedy Search", "Iterative Deepening DFS"]
        solver_menu = ctk.CTkOptionMenu(solver_frame, variable=self.solver_var, values=solver_options, font=("Arial", 14))
        solver_menu.pack(side=tk.RIGHT, padx=5, pady=5)

        # -- BUTTONS --
        button_frame = ctk.CTkFrame(control_frame, corner_radius=10, fg_color="#ADD8E6")
        button_frame.pack(fill=tk.X, pady=10, padx=5)

        self.generate_button = ctk.CTkButton(button_frame, text="Generate Maze", command=self.generate_maze, font=("Arial", 14))
        self.generate_button.pack(fill=tk.X, pady=5, padx=5)

        self.upload_button = ctk.CTkButton(button_frame, text="Upload Image", command=self.upload_image,font=("Arial", 14))
        self.upload_button.pack(fill=tk.X, pady=5, padx=5)

        self.solve_button = ctk.CTkButton(button_frame, text="Solve Maze", command=self.solve_maze, state="disabled", font=("Arial", 14))
        self.solve_button.pack(fill=tk.X, pady=5, padx=5)

        self.reset_button = ctk.CTkButton(button_frame, text="Reset Maze", command=self.reset_maze, state="disabled", font=("Arial", 14))
        self.reset_button.pack(fill=tk.X, pady=5, padx=5)

        self.clear_path_button = ctk.CTkButton(button_frame, text="Clear Path", command=self.clear_path, state="disabled", font=("Arial", 14))
        self.clear_path_button.pack(fill=tk.X, pady=5, padx=5)

        # -- CUSTOM MAZE TOOLS --
        tools_frame = ctk.CTkFrame(control_frame, corner_radius=10, fg_color="#ADD8E6")
        tools_frame.pack(fill=tk.X, pady=10, padx=5)

        self.draw_wall_button = ctk.CTkButton(tools_frame, text="Draw Walls", command=self.set_draw_mode, state="disabled", font=("Arial", 14))
        self.draw_wall_button.pack(side=tk.LEFT, padx=5, pady=5, expand=True)

        self.erase_wall_button = ctk.CTkButton(tools_frame, text="Erase Walls", command=self.set_erase_mode, state="disabled", font=("Arial", 14))
        self.erase_wall_button.pack(side=tk.RIGHT, padx=5, pady=5, expand=True)

        # -- STATUS BAR --
        self.status_var = tk.StringVar()

        # -- CANVAS FOR MAZE WITH SCROLLBARS --
        self.canvas_frame = ctk.CTkFrame(root)
        self.canvas_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Create a container frame for the canvas and scrollbars
        self.canvas_container = ctk.CTkFrame(self.canvas_frame)
        self.canvas_container.pack(fill=tk.BOTH, expand=True)

        # Add horizontal scrollbar at the bottom
        self.h_scrollbar = ctk.CTkScrollbar(self.canvas_container, orientation="horizontal")
        self.h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)

        # Add vertical scrollbar on the right
        self.v_scrollbar = ctk.CTkScrollbar(self.canvas_container, orientation="vertical")
        self.v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Add canvas
        self.canvas = tk.Canvas(self.canvas_container, bg="white",
                                xscrollcommand=self.h_scrollbar.set, yscrollcommand=self.v_scrollbar.set)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Configure scrollbars
        self.h_scrollbar.configure(command=self.canvas.xview)
        self.v_scrollbar.configure(command=self.canvas.yview)

        # Bind canvas configure event to update scroll region
        self.canvas.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))

        # Initialize maze-related variables
        self.maze = None
        self.path = []
        self.animation_speed = 0  # Milliseconds between steps
        self.draw_mode = False
        self.erase_mode = False
        self.maze_canvas = None
        self.solving_time = 0
        self.start = None
        self.end = None

        # Add a frame for status and timing information
        status_frame = ctk.CTkFrame(control_frame, corner_radius=10)
        status_frame.pack(fill=tk.X, pady=5, padx=5)

        # Status variable and label
        self.status_var = tk.StringVar()
        status_label = ctk.CTkLabel(status_frame, textvariable=self.status_var, font=("Arial", 14))
        status_label.pack(fill=tk.X, padx=5, pady=5)

        # Time display label
        self.time_var = tk.StringVar(value="Time: -")
        time_label = ctk.CTkLabel(status_frame, textvariable=self.time_var, font=("Arial", 14))
        time_label.pack(fill=tk.X, padx=5, pady=5)

    def upload_image(self):
        """Allow the user to upload an image, process it, and use it as a maze."""

        # Open file dialog to select an image
        file_path = filedialog.askopenfilename(
            title="Select Image",
            filetypes=[("Image files", "*.png;*.jpg;*.jpeg;*.bmp")]
        )

        if not file_path:  # User canceled
            return

        try:
            # Process the image to extract maze structure
            image, combined_edges = preprocess_image(file_path)
            processed_maze = extract_maze_structure(combined_edges, image)

            # Detect grid lines
            h_grid_lines, v_grid_lines = detect_grid_lines(processed_maze)
            h_grid_hough, v_grid_hough, h_line_img, v_line_img = build_grid_from_hough_lines(processed_maze)

            # Merge detected grid lines
            final_h_grid = sorted(list(set(h_grid_lines + h_grid_hough)))
            final_v_grid = sorted(list(set(v_grid_lines + v_grid_hough)))

            # Remove duplicate lines
            final_h_grid = group_nearby_lines(final_h_grid)
            final_v_grid = group_nearby_lines(final_v_grid)

            # Adjust grid lines for better alignment
            adjusted_h_grid_lines, adjusted_v_grid_lines = adjust_grid_lines_to_maze(final_h_grid, final_v_grid,
                                                                                     processed_maze)

            # Find openings in the outer walls
            openings = find_openings_in_outer_walls(image, processed_maze, adjusted_h_grid_lines, adjusted_v_grid_lines)

            # Determine nearest cells to openings
            nearest_cells = []
            for opening in openings:
                cell = determine_cell_from_opening(opening, adjusted_h_grid_lines, adjusted_v_grid_lines)
                nearest_cells.append(cell)

            # Extract a clean binary representation of the maze
            clean_maze = extract_clean_maze(image, processed_maze, adjusted_h_grid_lines, adjusted_v_grid_lines,
                                            openings, nearest_cells)

            # Find start and end nodes (red cells)
            start_coords, end_coords = find_start_end_nodes(clean_maze)

            if start_coords is None or end_coords is None:
                messagebox.showerror("Error", "Could not detect two distinct red nodes for start and end points.")
                return

            # Build the maze structure
            self.maze = MazeL(adjusted_h_grid_lines, adjusted_v_grid_lines, processed_maze)
            self.maze = assign_start_end_cells(self.maze, start_coords, end_coords, adjusted_h_grid_lines,
                                               adjusted_v_grid_lines)

            # Store start and end as indexed cells
            self.start = self.maze.start_cell
            self.end = self.maze.end_cell
            print("checkpoint 1")

            # Visualize the extracted maze on the canvas
            self.visualize_maze()
            print("checkpoint 3")

            # Enable solving and editing options
            self.solve_button.configure(state="normal")
            self.reset_button.configure(state="normal")
            self.draw_wall_button.configure(state="normal")
            self.erase_wall_button.configure(state="normal")
            self.clear_path_button.configure(state="disabled")

            self.status_var.set("Maze uploaded and processed successfully.")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to process image: {e}")
            self.status_var.set("Failed to load image.")

    # def upload_image(self):
    #     """Allow the user to upload an image to use as a maze template."""
    #
    #     # Open file dialog to select an image
    #     file_path = filedialog.askopenfilename(
    #         title="Select Image",
    #         filetypes=[("Image files", "*.png;*.jpg;*.jpeg;*.bmp")]
    #     )
    #
    #     if not file_path:  # User canceled
    #         return
    #
    #     try:
    #         image = Image.open(file_path)
    #         print("uploaded")
    #
    #     except Exception as e:
    #         messagebox.showerror("Error", f"Failed to process image: {e}")
    #         self.status_var.set("Failed to load image.")

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
            if not isinstance(btn, ctk.CTkButton):  # Ensure it's a button widget
                print(f"⚠ WARNING: {btn} is not a button! Skipping...")
                continue

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
        """
        Open the top wall of the start cell and the bottom wall of the end cell.
        This should only apply to generated mazes, NOT uploaded image-based mazes.
        """
        print("Checkpoint 2")
        if isinstance(self.maze, MazeL):
            print("⚠ Skipping wall opening for uploaded maze (MazeL).")
            return  # Do nothing for uploaded mazes, they already have proper walls

        if not self.maze or not self.start or not self.end:
            return  # Safety check

        # Open start cell's top wall
        start_row, start_col = divmod(self.start, self.maze.cols)
        self.maze.grid[start_row][start_col].walls['top'] = False

        # Open end cell's bottom wall
        end_row, end_col = divmod(self.end, self.maze.cols)
        self.maze.grid[end_row][end_col].walls['bottom'] = False

        print(f"✅ Opened start wall at ({start_row}, {start_col}) and end wall at ({end_row}, {end_col})")

    def visualize_maze(self):
        """Initialize and draw the maze on the canvas."""
        if self.maze_canvas:
            self.maze_canvas.destroy()
        print("checkpoint 4")
        # Determine cell size based on current window size
        canvas_width = self.root.winfo_width() - 40
        canvas_height = self.root.winfo_height() - 200  # Adjust based on control frame height
        cell_size = max(min(canvas_width, canvas_height) // self.maze.size, 20)

        # Create a frame inside the canvas to hold the maze
        self.maze_frame = tk.Frame(self.canvas)
        self.canvas.create_window((0, 0), window=self.maze_frame, anchor="nw")

        # Initialize the maze canvas
        self.maze_canvas = MazeCanvas(self.maze_frame, self.maze, cell_size, width=self.maze.size * cell_size + 20,
                                      height=self.maze.size * cell_size + 20)
        self.maze_canvas.pack()

        # Update scroll region
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        print("checkpoint 5")

        if self.start is None or self.end is None:
            print("⚠ Warning: Start or End node is missing!")
            return  # Exit early if no valid start/end

        print(f"Start Cell: {self.start}, End Cell: {self.end}")  # Debugging

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

        print(f"DEBUG: Raw Start = {start}, Raw End = {end}")  # Debugging

        # Ensure start and end are in integer format for divmod()
        if isinstance(start, tuple):
            start = start[0] * self.maze.cols + start[1]  # Convert to 1D index
        if isinstance(end, tuple):
            end = end[0] * self.maze.cols + end[1]  # Convert to 1D index

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
        elif algorithm == "Wilson":
            solver = WilsonSolver(self.maze, start, end, self.maze_canvas, self.animation_speed)

        elif algorithm == "Greedy Search":
            solver = GreedyBestFirstSolver(self.maze, start, end, self.maze_canvas, self.animation_speed)

        elif algorithm == "Iterative Deepening DFS":
            solver = IterativeDeepeningDFSSolver(self.maze, start, end, self.maze_canvas, self.animation_speed)
        else:
            messagebox.showerror("Unknown Algorithm", f"Solver '{algorithm}' is not implemented.")
            self.status_var.set("Failed to solve maze.")
            self.toggle_buttons(state="normal")
            self.clear_path_button.configure(state="normal")
            return

        if solver:
            solver.solve(self.on_solver_complete)

    def on_solver_complete(self, success, solving_time):
        """Callback when the solver completes."""
        if success:
            self.status_var.set("Pathfinding complete.")
        else:
            self.status_var.set("No solution found.")

            # Update the time display
            if solving_time > 0:
                self.time_var.set(f"Execution Time: {solving_time:.6f} seconds")
            else:
                self.time_var.set("Time: -")

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