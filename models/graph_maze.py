# maze_app/models/graph_maze.py

class GraphMaze:
    def __init__(self, rows, cols):
        self.rows = rows
        self.cols = cols
        self.nodes = {}  # key: node_id, value: Node object
        self.edges = []  # list of tuples (node1, node2)
        self.build_graph()

    def build_graph(self):
        for row in range(self.rows):
            for col in range(self.cols):
                node_id = self.get_node_id(row, col)
                self.nodes[node_id] = Node(row, col)
                # Connect to right neighbor
                if col < self.cols - 1:
                    right_neighbor = self.get_node_id(row, col + 1)
                    self.edges.append((node_id, right_neighbor))
                # Connect to bottom neighbor
                if row < self.rows - 1:
                    bottom_neighbor = self.get_node_id(row + 1, col)
                    self.edges.append((node_id, bottom_neighbor))

    def get_node_id(self, row, col):
        return row * self.cols + col

    def get_neighbors(self, node_id):
        return self.nodes[node_id].neighbors

class Node:
    def __init__(self, row, col):
        self.row = row
        self.col = col
        self.neighbors = set()

    def connect(self, other):
        self.neighbors.add(other)
