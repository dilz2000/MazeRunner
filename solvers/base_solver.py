# solvers/base_solver.py

from abc import ABC, abstractmethod

class BaseSolver(ABC):
    def __init__(self, maze, start, end, canvas, animation_speed=50):
        self.maze = maze
        self.start = start
        self.end = end
        self.canvas = canvas
        self.animation_speed = animation_speed
        self.path = []
        self.parent = {}
        self.visited = set()

    @abstractmethod
    def solve(self, callback):
        """Abstract method to solve the maze. Must be implemented by subclasses."""
        pass

    def reconstruct_path(self):
        """Reconstruct the path from start to end using the parent dictionary."""
        path = []
        current = self.end
        while current != self.start:
            path.append(current)
            current = self.parent.get(current)
            if current is None:
                return []  # No path found
        path.append(self.start)
        path.reverse()
        self.path = path
        return path

    def animate_path(self, callback):
        """Animate the final path."""
        for idx, node in enumerate(self.path):
            self.canvas.after(idx * self.animation_speed, lambda n=node: self.canvas.highlight_path(n))
        callback(True)  # Indicate completion
