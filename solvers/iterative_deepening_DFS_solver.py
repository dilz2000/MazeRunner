# solvers/iddfs_solver.py

from .base_solver import BaseSolver
import time


class IterativeDeepeningDFSSolver(BaseSolver):
    def solve(self, callback):
        maze = self.maze
        max_depth = 1  # Start with depth limit of 1
        found = False

        start_time = time.time()

        # Keep increasing depth until solution is found or entire maze is explored
        while not found:
            self.visited = set()  # Reset visited for each depth iteration
            self.parent = {}  # Reset parent dictionary

            # Perform DFS with current depth limit
            found = self.depth_limited_search(self.start, max_depth, callback)

            if found:
                end_time = time.time()
                solving_time = end_time - start_time
                print(f"IDDFS Solving Time: {solving_time:.6f} seconds")
                print(f"Solution found at depth: {max_depth}")
                path = self.reconstruct_path()
                if path:
                    self.animate_path(callback)
                else:
                    callback(False)  # No path found (shouldn't happen)
                return

            # If we've explored the entire maze without finding a solution at the current depth,
            # we need to stop increasing the depth
            if len(self.visited) == maze.rows * maze.cols or max_depth > maze.rows * maze.cols:
                callback(False)  # No solution exists
                return

            max_depth += 1  # Increase depth limit

    def depth_limited_search(self, current, depth_limit, callback):
        """Perform depth-limited search from current node up to depth_limit."""
        self.visited.add(current)
        self.canvas.highlight_cell(current, "yellow")

        # Check if we've reached the goal
        if current == self.end:
            return True

        # If we've reached depth limit, don't explore further in this path
        if depth_limit <= 0:
            return False

        # Get neighbors and explore recursively
        row, col = divmod(current, self.maze.cols)
        neighbors = self.maze.get_neighbors(row, col)

        for neighbor in neighbors:
            neighbor_id = self.maze.get_cell_id(neighbor[0], neighbor[1])
            if neighbor_id not in self.visited:
                self.parent[neighbor_id] = current

                # We need to use the canvas after method to animate the exploration
                # But we can't use recursion with after, so we'll do the recursion synchronously
                result = self.depth_limited_search(neighbor_id, depth_limit - 1, callback)
                if result:
                    return True

        return False