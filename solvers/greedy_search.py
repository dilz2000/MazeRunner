# solvers/greedy_best_first_solver.py
import time
from .base_solver import BaseSolver
import heapq

class GreedyBestFirstSolver(BaseSolver):
    def solve(self, callback):
        """Solves the maze using Greedy Best-First Search (GBFS)."""
        maze = self.maze
        priority_queue = []
        heapq.heappush(priority_queue, (self.heuristic(self.start), self.start))  # (priority, node)
        self.visited.add(self.start)

        start_time = time.time()

        def step():
            if not priority_queue:
                callback(False)  # No solution found
                return
            _, current = heapq.heappop(priority_queue)

            if current == self.end:
                end_time = time.time()
                solving_time = end_time - start_time
                path = self.reconstruct_path()
                if path:
                    self.animate_path(callback)
                else:
                    callback(False)  # No path found
                print(f"Greedy Solving Time: {solving_time:.6f} seconds")
                return

            row, col = divmod(current, maze.cols)
            neighbors = maze.get_neighbors(row, col)

            for neighbor in neighbors:
                neighbor_id = maze.get_cell_id(neighbor[0], neighbor[1])
                if neighbor_id not in self.visited:
                    self.visited.add(neighbor_id)
                    self.parent[neighbor_id] = current
                    heapq.heappush(priority_queue, (self.heuristic(neighbor_id), neighbor_id))
                    self.canvas.highlight_cell(neighbor_id, "yellow")

            self.canvas.after(self.animation_speed, step)

        step()

    def heuristic(self, node):
        """Compute heuristic (Manhattan Distance) between the node and the goal."""
        node_row, node_col = divmod(node, self.maze.cols)
        goal_row, goal_col = divmod(self.end, self.maze.cols)
        return abs(goal_row - node_row) + abs(goal_col - node_col)  # Manhattan Distance
