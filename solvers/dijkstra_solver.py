# solvers/dijkstra_solver.py

from .base_solver import BaseSolver
import heapq
import time


class DijkstraSolver(BaseSolver):
    def solve(self, callback):
        maze = self.maze
        heap = []
        heapq.heappush(heap, (0, self.start))
        distances = {node: float('inf') for node in range(maze.rows * maze.cols)}
        distances[self.start] = 0

        start_time = time.time()

        def step():
            if not heap:
                callback(False)  # No solution found
                return
            current_distance, current = heapq.heappop(heap)
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
                print(f"Dijkstra Solving Time: {solving_time:.6f} seconds")
                return
            row, col = divmod(current, maze.cols)
            neighbors = self.maze.get_neighbors(row, col)
            for neighbor in neighbors:
                neighbor_id = maze.get_cell_id(neighbor[0], neighbor[1])
                if neighbor_id in self.visited:
                    continue
                new_dist = current_distance + 1  # Assuming uniform cost
                if new_dist < distances[neighbor_id]:
                    distances[neighbor_id] = new_dist
                    self.parent[neighbor_id] = current
                    heapq.heappush(heap, (new_dist, neighbor_id))
                    self.canvas.highlight_cell(neighbor_id, "yellow")
            self.canvas.after(self.animation_speed, step)

        step()
