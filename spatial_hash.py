class SpatialHash:
    def __init__(self, cell_size=96):
        self.cell_size = cell_size
        self.cells = {}

    def _key(self, x, y):
        return (int(x // self.cell_size), int(y // self.cell_size))

    def clear(self):
        self.cells.clear()

    def insert(self, obj, x, y, w=0, h=0):
        keys = set()
        for cx in range(int((x - w/2) // self.cell_size), int((x + w/2) // self.cell_size) + 1):
            for cy in range(int((y - h/2) // self.cell_size), int((y + h/2) // self.cell_size) + 1):
                keys.add((cx, cy))
        for key in keys:
            if key not in self.cells:
                self.cells[key] = []
            self.cells[key].append(obj)

    def query(self, x, y, w, h):
        results = set()
        for cx in range(int((x - w/2) // self.cell_size), int((x + w/2) // self.cell_size) + 1):
            for cy in range(int((y - h/2) // self.cell_size), int((y + h/2) // self.cell_size) + 1):
                key = (cx, cy)
                if key in self.cells:
                    for obj in self.cells[key]:
                        results.add(obj)
        return results

    def query_rect(self, rect):
        return self.query(rect.centerx, rect.centery, rect.width, rect.height)