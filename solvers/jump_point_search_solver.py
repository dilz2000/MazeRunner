# solvers/jump_point_search_solver.py

from .base_solver import BaseSolver
from tkinter import messagebox


class JumpPointSearchSolver(BaseSolver):
    def solve(self, callback):
        """Placeholder for Jump Point Search algorithm implementation."""
        messagebox.showinfo("Algorithm Not Implemented", "Jump Point Search is not yet implemented.")
        self.canvas.after(100, lambda: callback(False))  # Indicate failure
