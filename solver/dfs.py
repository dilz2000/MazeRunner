# maze_app/solver/dfs.py

def dfs_solver(maze, start, end):
    stack = [start]
    visited = set()
    parent = {}

    visited.add(start)

    while stack:
        current = stack.pop()
        if current == end:
            break
        for neighbor in maze.nodes[current].neighbors:
            if neighbor not in visited:
                visited.add(neighbor)
                parent[neighbor] = current
                stack.append(neighbor)

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
