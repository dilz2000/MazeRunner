# maze_app/solver/a_star.py

import heapq


def heuristic(node1, node2, cols):
    # Manhattan distance
    row1, col1 = node1 // cols, node1 % cols
    row2, col2 = node2 // cols, node2 % cols
    return abs(row1 - row2) + abs(col1 - col2)


def a_star_solver(maze, start, end):
    cols = maze.cols
    open_set = []
    heapq.heappush(open_set, (0, start))
    came_from = {}
    g_score = {node: float('inf') for node in maze.nodes}
    g_score[start] = 0
    f_score = {node: float('inf') for node in maze.nodes}
    f_score[start] = heuristic(start, end, cols)

    while open_set:
        current = heapq.heappop(open_set)[1]
        if current == end:
            break
        for neighbor in maze.nodes[current].neighbors:
            tentative_g_score = g_score[current] + 1  # Assuming uniform cost
            if tentative_g_score < g_score[neighbor]:
                came_from[neighbor] = current
                g_score[neighbor] = tentative_g_score
                f_score[neighbor] = tentative_g_score + heuristic(neighbor, end, cols)
                if not any(neighbor == item[1] for item in open_set):
                    heapq.heappush(open_set, (f_score[neighbor], neighbor))

    # Reconstruct path
    path = []
    step = end
    while step != start:
        path.append(step)
        step = came_from.get(step)
        if step is None:
            return []  # No path found
    path.append(start)
    path.reverse()
    return path
