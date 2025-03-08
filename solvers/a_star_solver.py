# solvers/a_star_solver.py
import time
from .base_solver import BaseSolver
import heapq


class AStarSolver(BaseSolver):
    def solve(self, callback):
        maze = self.maze
        heap = []
        heapq.heappush(heap, (0, self.start))
        distances = {node: float('inf') for node in range(maze.rows * maze.cols)}
        distances[self.start] = 0

        start_time = time.time()

        def heuristic(a, b):
            """Manhattan distance heuristic."""
            a_row, a_col = divmod(a, maze.cols)
            b_row, b_col = divmod(b, maze.cols)
            return abs(a_row - b_row) + abs(a_col - b_col)

        def step():
            if not heap:
                callback(False)  # No solution found
                return
            current_f, current = heapq.heappop(heap)
            if current in self.visited:
                self.canvas.after(self.animation_speed, step)
                return
            self.visited.add(current)
            if current == self.end:
                end_time = time.time()
                solving_time = end_time - start_time
                path = self.reconstruct_path()
                if path:
                    self.animate_path(callback)
                else:
                    callback(False)
                print(f"A* Solving Time: {solving_time:.6f} seconds")
                return
            row, col = divmod(current, maze.cols)
            neighbors = self.maze.get_neighbors(row, col)
            for neighbor in neighbors:
                neighbor_id = maze.get_cell_id(neighbor[0], neighbor[1])
                if neighbor_id in self.visited:
                    continue
                tentative_g = distances[current] + 1  # Assuming uniform cost
                if tentative_g < distances[neighbor_id]:
                    distances[neighbor_id] = tentative_g
                    f_score = tentative_g + heuristic(neighbor_id, self.end)
                    self.parent[neighbor_id] = current
                    heapq.heappush(heap, (f_score, neighbor_id))
                    self.canvas.highlight_cell(neighbor_id, "yellow")
            self.canvas.after(self.animation_speed, step)

        step()
