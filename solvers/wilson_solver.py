# solvers/wilson_solver.py

from .base_solver import BaseSolver
import random
import time


class WilsonSolver(BaseSolver):
    def solve(self, callback):
        maze = self.maze
        start_time = time.time()

        # Add the end (goal) to visited set first
        self.visited.add(self.end)

        def step():
            # If start is already in visited, we have a path
            if self.start in self.visited:
                end_time = time.time()
                solving_time = end_time - start_time
                print(f"Wilson Solving Time: {solving_time:.6f} seconds")
                path = self.reconstruct_path()
                if path:
                    self.animate_path(callback)
                else:
                    callback(False)  # No path found (shouldn't happen)
                return

            # Choose an unvisited cell to start a random walk from
            # Prioritize the start position if it's not visited yet
            if len(self.visited) == 1:  # Only end is visited
                current = self.start
            else:
                # Get all unvisited cells
                unvisited = []
                for r in range(maze.rows):
                    for c in range(maze.cols):
                        cell_id = maze.get_cell_id(r, c)
                        if cell_id not in self.visited and maze.is_valid_cell(r, c):
                            unvisited.append(cell_id)

                if not unvisited:
                    callback(False)  # No solution possible
                    return

                current = random.choice(unvisited)

            # Perform a loop-erased random walk until hitting a visited cell
            path = [current]
            current_path = {current: None}  # Keep track of the current path

            while current not in self.visited:
                row, col = divmod(current, maze.cols)
                neighbors = maze.get_neighbors(row, col)

                if not neighbors:
                    # No neighbors, dead end - restart step
                    self.canvas.after(self.animation_speed, step)
                    return

                # Choose a random neighbor
                next_cell = random.choice(neighbors)
                next_id = maze.get_cell_id(next_cell[0], next_cell[1])

                # If we've seen this cell in our current path, we have a loop
                if next_id in current_path:
                    # Erase the loop - fixed to avoid IndexError
                    loop_start = next_id
                    # Find the position of loop_start in the path
                    try:
                        loop_index = path.index(loop_start)
                        # Truncate the path to remove the loop
                        path = path[:loop_index + 1]
                        # Update the current position
                        current = path[-1]
                    except ValueError:
                        # If loop_start not in path, just continue with next cell
                        path.append(next_id)
                        current_path[next_id] = current
                        current = next_id
                else:
                    # Add to our path
                    path.append(next_id)
                    current_path[next_id] = current
                    current = next_id

                self.canvas.highlight_cell(current, "yellow")

            # Once we've hit a visited cell, add all cells in the path to visited and update parent
            for i in range(len(path) - 1):
                self.visited.add(path[i])
                self.parent[path[i]] = path[i + 1]  # Parent is the next cell in path towards visited
                self.canvas.highlight_cell(path[i], "darkblue")

            # Continue with next step
            self.canvas.after(self.animation_speed, step)

        step()

# # solvers/wilson_solver.py
#
# import random
# import time
#
# from .base_solver import BaseSolver
#
# class WilsonSolver(BaseSolver):
#     def solve(self, callback):
#         maze = self.maze
#         current = self.start
#         path = []
#         visited = set()
#
#         start_time = time.time()
#
#         def step():
#             nonlocal current, path
#
#             # If we reached the end node, reconstruct and animate the path
#             if current == self.end:
#                 end_time = time.time()
#                 solving_time = end_time - start_time
#                 self.path = path
#                 self.animate_path(callback)
#                 print(f"Wilson Solving Time: {solving_time:.6f} seconds")
#                 return
#
#             row, col = divmod(current, maze.cols)
#             neighbors = self.maze.get_neighbors(row, col)
#             random.shuffle(neighbors)  # Choose a random direction for the walk
#
#             if neighbors:
#                 next_row, next_col = neighbors[0]
#                 next_cell_id = maze.get_cell_id(next_row, next_col)
#
#                 if next_cell_id in path:
#                     # Loop detected, remove the loop by truncating path
#                     loop_index = path.index(next_cell_id)
#                     path = path[:loop_index + 1]
#                 else:
#                     path.append(next_cell_id)
#
#                 self.canvas.highlight_cell(next_cell_id, "yellow")
#                 current = next_cell_id  # Move to the next cell
#
#                 self.canvas.after(self.animation_speed, step)  # Recursive call
#
#         path.append(current)  # Start from the first node
#         step()  # Begin the random walk
