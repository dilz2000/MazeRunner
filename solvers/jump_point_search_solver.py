# solvers/jump_point_search_solver.py

from .base_solver import BaseSolver
import heapq

class JumpPointSearchSolver(BaseSolver):
    def solve(self, callback):
        maze = self.maze
        heap = []
        heapq.heappush(heap, (0, self.start))
        distances = {node: float('inf') for node in range(maze.rows * maze.cols)}
        distances[self.start] = 0

        def heuristic(a, b):
            """Manhattan distance heuristic."""
            a_row, a_col = divmod(a, maze.cols)
            b_row, b_col = divmod(b, maze.cols)
            return abs(a_row - b_row) + abs(a_col - b_col)

        def jump(current, direction):
            """Jump in the given direction until a jump point is found."""
            row, col = divmod(current, maze.cols)
            dx, dy = direction
            next_row, next_col = row + dx, col + dy

            if not maze.is_valid(next_row, next_col) or maze.is_wall(next_row, next_col):
                return None

            next_id = maze.get_cell_id(next_row, next_col)
            if next_id == self.end:
                return next_id

            # Check for forced neighbors
            if dx != 0 and dy != 0:
                # Diagonal move
                if (maze.is_valid(row + dx, col) and maze.is_wall(row + dx, col)) or \
                   (maze.is_valid(row, col + dy) and maze.is_wall(row, col + dy)):
                    return next_id

                # Check for jump points in the horizontal and vertical directions
                if jump(next_id, (dx, 0)) is not None or jump(next_id, (0, dy)) is not None:
                    return next_id
            else:
                # Horizontal or vertical move
                if dx != 0:
                    # Horizontal move
                    if (maze.is_valid(row + dx, col + 1) and not maze.is_wall(row + dx, col + 1)) or \
                       (maze.is_valid(row + dx, col - 1) and not maze.is_wall(row + dx, col - 1)):
                        return next_id
                else:
                    # Vertical move
                    if (maze.is_valid(row + 1, col + dy) and not maze.is_wall(row + 1, col + dy)) or \
                       (maze.is_valid(row - 1, col + dy) and not maze.is_wall(row - 1, col + dy)):
                        return next_id

            return jump(next_id, direction)

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
                path = self.reconstruct_path()
                if path:
                    self.animate_path(callback)
                else:
                    callback(False)
                return
            row, col = divmod(current, maze.cols)
            neighbors = self.maze.get_neighbors(row, col)
            for neighbor in neighbors:
                neighbor_id = maze.get_cell_id(neighbor[0], neighbor[1])
                if neighbor_id in self.visited:
                    continue
                direction = (neighbor[0] - row, neighbor[1] - col)
                jump_point = jump(current, direction)
                if jump_point is not None:
                    tentative_g = distances[current] + heuristic(current, jump_point)
                    if tentative_g < distances[jump_point]:
                        distances[jump_point] = tentative_g
                        f_score = tentative_g + heuristic(jump_point, self.end)
                        self.parent[jump_point] = current
                        heapq.heappush(heap, (f_score, jump_point))
                        self.canvas.highlight_cell(jump_point, "yellow")
            self.canvas.after(self.animation_speed, step)

        step()