# maze_app/solver/dijkstra.py

import heapq

def dijkstra_solver(maze, start, end):
    cols = maze.cols
    heap = []
    heapq.heappush(heap, (0, start))
    distances = {node: float('inf') for node in maze.nodes}
    distances[start] = 0
    parent = {}

    while heap:
        current_distance, current = heapq.heappop(heap)
        if current == end:
            break
        for neighbor in maze.nodes[current].neighbors:
            distance = current_distance + 1  # Assuming uniform cost
            if distance < distances[neighbor]:
                distances[neighbor] = distance
                parent[neighbor] = current
                heapq.heappush(heap, (distance, neighbor))

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
