# models/union_find.py

class UnionFind:
    def __init__(self, size):
        self.parent = list(range(size))
        self.rank = [0] * size

    def find(self, x):
        """Find the root of x with path compression."""
        if self.parent[x] != x:
            self.parent[x] = self.find(self.parent[x])
        return self.parent[x]

    def union(self, x, y):
        """Union by rank. Returns True if union was successful, False if already connected."""
        fx = self.find(x)
        fy = self.find(y)
        if fx == fy:
            return False  # Already in the same set
        if self.rank[fx] < self.rank[fy]:
            self.parent[fx] = fy
        else:
            self.parent[fy] = fx
            if self.rank[fx] == self.rank[fy]:
                self.rank[fx] += 1
        return True
