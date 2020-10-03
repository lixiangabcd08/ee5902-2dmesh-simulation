import math


class BaseRouter:
    def __init__(self, id, coordinates):
        self.id = id
        self.coordinates = coordinates  # [y, x]
        self.neighbours_id = [id, None, None, None, None]
        self.in_buffer = []
        self.out_buffer = []  # single buffer for testing
        self.buffer_size = 16
        self.local_storage = []

    def set_neighbours(self, neighbours_coordinates, neighbours_id):
        # put the id in the respective port directions
        for index in range(len(neighbours_coordinates)):
            coordinates = neighbours_coordinates[index]
            id = neighbours_id[index]
            direction = self.arbiter(coordinates)
            self.neighbours_id[direction] = id

    def packet_in(self, packet):
        """ store to input buffer """
        if self.in_buffer_full():
            return False
        else:
            # update packet information before storing
            packet.update_packet(self.id, self.coordinates)
            self.in_buffer.append(packet)
            return True

    def packet_store(self, packet):
        """ store to local storage """
        self.local_storage.append(packet)

    def out_buffer_packet_peek(self):
        # see the output buffer data
        if not self.out_buffer_empty():
            packet = self.out_buffer[0]
            return packet
        else:
            return None

    def out_buffer_packet_remove(self):
        # remove the output buffer data
        if not self.out_buffer_empty():
            # remove the packet
            self.out_buffer.pop(0)

    def out_buffer_empty(self):
        if len(self.out_buffer) == 0:
            return True
        else:
            return False

    def in_buffer_empty(self):
        if len(self.in_buffer) == 0:
            return True
        else:
            return False

    def in_buffer_full(self):
        if len(self.in_buffer) == self.buffer_size:
            return True
        else:
            return False

    def sent_controller(self):
        packet = self.out_buffer_packet_peek()
        dest_id = None
        if packet is not None:
            # check where the packet is going
            direction = self.arbiter(packet.dest_coordinates)
            dest_id = self.neighbours_id[direction]

            # if packet has arrived
            if direction == 0:
                self.out_buffer_packet_remove()
                self.packet_store(packet)
                dest_id = None

        # uppper level check if neighour_buffer is free
        return dest_id, packet

    def prepare_next_cycle(self):
        # move the data to output buffer only if the previous data was sent
        if not self.in_buffer_empty() and self.out_buffer_empty():
            # move 1 packet to output buffer
            self.out_buffer.append(self.in_buffer[0])
            self.in_buffer.pop(0)

    def arbiter(self, dest_coordinates):
        """ X-Y algorithm """
        direction = None  # 0 self, 1 north, 2 east, 3 south, 4 west
        x_diff = dest_coordinates[1] - self.coordinates[1]
        y_diff = dest_coordinates[0] - self.coordinates[0]
        if x_diff > 0:  # go east
            direction = 2
        elif x_diff < 0:  # go west
            direction = 4
        elif y_diff > 0:  # go south
            direction = 3
        elif y_diff < 0:  # go north
            direction = 1
        else:  # arrived
            direction = 0
        return direction
