# maze_app/generator/graph_generator.py

import random
from generator.union_find import UnionFind
from models.graph_maze import GraphMaze


def kruskal_generate(rows, cols):
    maze = GraphMaze(rows, cols)
    uf = UnionFind(rows * cols)
    edges = maze.edges.copy()
    random.shuffle(edges)

    for edge in edges:
        node1, node2 = edge
        if uf.union(node1, node2):
            # Connect the nodes in the maze graph
            maze.nodes[node1].connect(node2)
            maze.nodes[node2].connect(node1)

    return maze
