""" class for packet """


class BasePacket:
    def __init__(self, source_id, dest_coordinates, current_coordinates):
        self.source_id = source_id
        self.dest_coordinates = dest_coordinates
        self.current_coordinates = current_coordinates

    def update_packet(self, current_coordinates):
        self.update_coordinates(current_coordinates)

    def update_coordinates(self, current_coordinates):
        self.current_coordinates = current_coordinates


class StatPacket(BasePacket):
    """ with more variables for statics tracking """

    def __init__(
        self, source_id, dest_coordinates, current_coordinates, start_clock_cycle
    ):
        super().__init__(source_id, dest_coordinates, current_coordinates)
        self.path_trace = []
        self.clock_cycle_taken = 0
        self.start_clock_cycle = start_clock_cycle

    def update_packet(self, router_id, current_coordinates):
        """ overloading parent function """
        self.add_router_to_path_trace(router_id)
        self.update_coordinates(current_coordinates)

    def update_clock_cycle(self, current_clock_cycle):
        self.clock_cycle_taken = current_clock_cycle - self.start_clock_cycle

    def add_router_to_path_trace(self, router_id):
        self.path_trace.append(router_id)
