''' class for packet '''


class Packet:
    def __init__(self, source_id, dest_coordinates, current_coordinates):
        self.source_id = source_id
        self.dest_coordinates = dest_coordinates
        self.current_coordinates = current_coordinates
        self.path_trace = [source_id]
        self.clock_cycle_taken = 0

    def increase_clock_cycle(self):
        self.clock_cycle_taken += 1

    def add_router(self, router_id):
        self.path_trace.append(router_id)

    def update_coordinates(self, current_coordinates):
        self.current_coordinates = current_coordinates