# maze_app/ui/main_window.py

import tkinter as tk
from tkinter import ttk, messagebox
from generator.graph_generator import kruskal_generate
from solver.bfs import bfs_solver
from solver.dfs import dfs_solver
from solver.a_star import a_star_solver
from solver.dijkstra import dijkstra_solver
from ui.visualization import MazeCanvas


class MainWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("Maze Runner")
        self.root.geometry("900x800")
        self.root.resizable(True, True)

        # Apply a modern theme
        style = ttk.Style(root)
        style.theme_use('clam')

        # Create main frames
        control_frame = ttk.Frame(root, padding="10 10 10 10")
        control_frame.pack(side=tk.TOP, fill=tk.X)

        canvas_frame = ttk.Frame(root, padding="10 10 10 10")
        canvas_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        # Shape selection
        shape_label = ttk.Label(control_frame, text="Select Shape:", font=("Arial", 12))
        shape_label.grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)

        shape_var = tk.StringVar(value="Rectangular")
        shape_options = ["Rectangular", "Square"]
        shape_menu = ttk.OptionMenu(control_frame, shape_var, shape_var.get(), *shape_options)
        shape_menu.grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)

        # Size input
        size_label = ttk.Label(control_frame, text="Enter Size (rows x cols):", font=("Arial", 12))
        size_label.grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)

        size_frame = ttk.Frame(control_frame)
        size_frame.grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)

        rows_entry = ttk.Entry(size_frame, width=5)
        rows_entry.grid(row=0, column=0, padx=(0, 2))
        rows_entry.insert(0, "10")  # Default value

        x_label = ttk.Label(size_frame, text="x", font=("Arial", 12))
        x_label.grid(row=0, column=1)

        cols_entry = ttk.Entry(size_frame, width=5)
        cols_entry.grid(row=0, column=2, padx=(2, 0))
        cols_entry.insert(0, "10")  # Default value

        # Solver selection
        solver_label = ttk.Label(control_frame, text="Select Solver Algorithm:", font=("Arial", 12))
        solver_label.grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)

        solver_var = tk.StringVar(value="BFS")
        solver_options = ["DFS", "BFS", "A*", "Dijkstra"]
        solver_menu = ttk.OptionMenu(control_frame, solver_var, solver_var.get(), *solver_options)
        solver_menu.grid(row=2, column=1, sticky=tk.W, padx=5, pady=5)

        # Generate and Solve buttons
        generate_button = ttk.Button(control_frame, text="Generate Maze",
                                     command=lambda: self.generate_maze(shape_var, rows_entry, cols_entry, canvas))
        generate_button.grid(row=3, column=0, padx=5, pady=15, sticky=tk.EW)

        solve_button = ttk.Button(control_frame, text="Solve Maze", command=lambda: self.solve_maze(solver_var, canvas))
        solve_button.grid(row=3, column=1, padx=5, pady=15, sticky=tk.EW)

        # Status bar
        status_var = tk.StringVar()
        status_bar = ttk.Label(root, textvariable=status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)

        # Canvas for maze with scrollbars
        canvas = MazeCanvas(canvas_frame, maze=None, bg="white")
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar_y = ttk.Scrollbar(canvas_frame, orient=tk.VERTICAL, command=canvas.yview)
        scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)
        scrollbar_x = ttk.Scrollbar(root, orient=tk.HORIZONTAL, command=canvas.xview)
        scrollbar_x.pack(side=tk.BOTTOM, fill=tk.X)

        canvas.configure(yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)

        # Update the status bar
        def update_status(message):
            status_var.set(message)
            root.update_idletasks()

        # Assign the update_status function to the canvas for access in other functions
        canvas.update_status = update_status

    def generate_maze(self, shape_var, rows_entry, cols_entry, canvas):
        try:
            shape = shape_var.get()
            rows = int(rows_entry.get())
            cols = int(cols_entry.get())

            if rows <= 0 or cols <= 0:
                raise ValueError("Rows and columns must be positive integers.")

            # Adjust rows and cols based on shape
            if shape == "Square":
                size = max(rows, cols)
                rows = cols = size

            canvas.update_status(f"Generating a {shape} maze of size {rows}x{cols}...")
            self.root.update_idletasks()

            # Generate the maze using Kruskal's Algorithm
            maze = kruskal_generate(rows, cols)
            canvas.maze = maze
            canvas.draw_maze()

            canvas.update_status("Maze generated successfully.")
        except ValueError as ve:
            messagebox.showerror("Invalid Input", str(ve))
            canvas.update_status("Failed to generate maze.")
        except Exception as e:
            messagebox.showerror("Error", f"An unexpected error occurred: {e}")
            canvas.update_status("Failed to generate maze.")

    def solve_maze(self, solver_var, canvas):
        try:
            if not canvas.maze:
                messagebox.showwarning("No Maze", "Please generate a maze first.")
                return

            algorithm = solver_var.get()
            canvas.update_status(f"Solving maze using {algorithm} algorithm...")
            self.root.update_idletasks()

            start = 0  # Top-left corner
            end = canvas.maze.get_node_id(canvas.maze.rows - 1, canvas.maze.cols - 1)  # Bottom-right corner

            # Select the solver based on user choice
            if algorithm == "BFS":
                path = bfs_solver(canvas.maze, start, end)
            elif algorithm == "DFS":
                path = dfs_solver(canvas.maze, start, end)
            elif algorithm == "A*":
                path = a_star_solver(canvas.maze, start, end)
            elif algorithm == "Dijkstra":
                path = dijkstra_solver(canvas.maze, start, end)
            else:
                messagebox.showerror("Unknown Algorithm", f"Solver '{algorithm}' is not implemented.")
                canvas.update_status("Failed to solve maze.")
                return

            if path:
                canvas.clear_solution()
                canvas.draw_solution(path)
                canvas.update_status(f"Maze solved successfully using {algorithm}.")
            else:
                messagebox.showinfo("No Solution", "No path could be found in the maze.")
                canvas.update_status("No solution found.")
        except ImportError as ie:
            messagebox.showerror("Solver Error", f"Solver module not found: {ie}")
            canvas.update_status("Failed to solve maze.")
        except Exception as e:
            messagebox.showerror("Error", f"An unexpected error occurred: {e}")
            canvas.update_status("Failed to solve maze.")
