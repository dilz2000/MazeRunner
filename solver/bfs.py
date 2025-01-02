# maze_app/solver/bfs.py

from collections import deque


def bfs_solver(maze, start, end):
    queue = deque([start])
    visited = set()
    parent = {}

    visited.add(start)

    while queue:
        current = queue.popleft()
        if current == end:
            break
        for neighbor in maze.nodes[current].neighbors:
            if neighbor not in visited:
                visited.add(neighbor)
                parent[neighbor] = current
                queue.append(neighbor)

    # Reconstruct path
    path = []
    step = end
    while step != start:
        path.append(step)
        step = parent.get(step)
        if step is None:
            return []  # No path found
    path.append(start)
    path.reverse()
    return path
