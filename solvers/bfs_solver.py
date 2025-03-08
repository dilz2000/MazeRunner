# solvers/bfs_solver.py

from .base_solver import BaseSolver
from collections import deque
import time

class BFSSolver(BaseSolver):
    def solve(self, callback):
        maze = self.maze
        queue = deque([self.start])
        self.visited.add(self.start)

        start_time = time.time()

        def step():
            if not queue:
                callback(False)  # No solution found
                return
            current = queue.popleft()
            if current == self.end:
                end_time = time.time()
                self.solving_time = end_time - start_time

                path = self.reconstruct_path()
                if path:
                    self.animate_path(callback)
                else:
                    callback(False, self.solving_time)  # No path found
                print(f"BFS Solving Time: {self.solving_time:.6f} seconds")
                return

            row, col = divmod(current, maze.cols)
            neighbors = self.maze.get_neighbors(row, col)
            for neighbor in neighbors:
                neighbor_id = maze.get_cell_id(neighbor[0], neighbor[1])
                if neighbor_id not in self.visited:
                    self.visited.add(neighbor_id)
                    self.parent[neighbor_id] = current
                    queue.append(neighbor_id)
                    self.canvas.highlight_cell(neighbor_id, "yellow")
            self.canvas.after(self.animation_speed, step)

        step()
