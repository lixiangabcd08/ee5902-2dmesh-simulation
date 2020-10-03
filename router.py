
class Router:
    def __init__(self, id, coordinates, neighbours_id):
        self.id = id
        self.coordinates = coordinates
        self.neighbours_id = neighbours_id

    def set_neighbours(self, neighbours_id):
        self.neighbours_id = neighbours_id
