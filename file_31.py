class SpatialHash:
    def __init__(self, cell_size=96):
        self.cell_size = cell_size
        self.table = {}

    def clear(self):
        self.table.clear()

    def _cells(self, rect):
        cs = self.cell_size
        x0 = int(rect[0] // cs)
        y0 = int(rect[1] // cs)
        x1 = int((rect[0]+rect[2]) // cs)
        y1 = int((rect[1]+rect[3]) // cs)
        for cx in range(x0, x1+1):
            for cy in range(y0, y1+1):
                yield (cx, cy)

    def insert(self, obj, rect):
        for cell in self._cells(rect):
            if cell not in self.table:
                self.table[cell] = []
            self.table[cell].append(obj)

    def query(self, rect):
        found = set()
        for cell in self._cells(rect):
            if cell in self.table:
                for obj in self.table[cell]:
                    found.add(obj)
        return found

    def query_point(self, x, y):
        cs = self.cell_size
        cell = (int(x//cs), int(y//cs))
        return self.table.get(cell, [])