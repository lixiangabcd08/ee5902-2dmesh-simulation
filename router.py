"""
Module: BaseRouter
Desp:   Basic XY 2d mesh router for baseline testing
version: 0.1.0

requirements: receiver.py

Changelog:  0.0.1 - single buffer router (software)
            0.0.2 - 1 buffer per port and more functions
            0.1.0 - combined the buffer together for easy calculation
                    use a flag (pkt_available_to_send_now) to mark output data
                    Making buffer signals more hardware like
"""


class BaseRouter:
    SELF = 0  # careful of the case
    EAST = 2
    WEST = 4
    SOUTH = 3
    NORTH = 1

    def __init__(self, id, coordinates, rx_address):
        self.id = id
        self.coordinates = coordinates  # [y, x]
        self.neighbours_id = [id, None, None, None, None]
        self.buffer = [[], [], [], [], []]  # 5 buffers, 1 for each port
        self.pkt_available_to_send_now = [False, False, False, False, False]
        self.buffer_size = 4
        self.local_storage = rx_address
        self.current_serving_port = 4  # so first cycle will server port 0

    def set_neighbours(self, neighbours_coordinates, neighbours_id):
        """ set the id in the respective port directions """
        for index in range(len(neighbours_coordinates)):
            coordinates = neighbours_coordinates[index]
            id = neighbours_id[index]
            direction = self.get_neighbour_direction(coordinates)
            self.neighbours_id[direction] = id

    ### buffer operations ###

    def packet_in(self, packet, port):
        """ store to input buffer """
        if self.buffer_full(port):
            return False
        else:
            # update packet information before storing
            packet.update_packet(self.id, self.coordinates)
            self.buffer[port].append(packet)
            return True

    def packet_store(self, packet, current_clock_cycle):
        """ store to local storage """
        packet.update_clock_cycle(current_clock_cycle)  # update cycle
        self.local_storage.store(packet)

    def buffer_packet_peek(self, port):
        """ retrive the output buffer data """
        if (self.pkt_available_to_send_now[port]):
            packet = self.buffer[port][0]  # always the first pkt
            return packet
        else:
            return None

    def buffer_packet_remove(self, port):
        """ remove the output buffer data """
        if (not self.buffer_empty(port)):
            # remove the packet
            self.buffer[port].pop(0)
        else:
            raise BufferError("Trying to remove packet from empty buffer")

    ### buffer status ###

    def buffer_empty(self, port):
        """ for current cycle, like hardware FIFO status """
        # if there is a packet available to output, the buffer is not empty
        if self.pkt_available_to_send_now[port]:
            return False
        else:
            return not self.buffer[port]  # empty list == false

    def buffer_full(self, port):
        """ for current cycle, like hardware FIFO status """
        if len(self.buffer[port]) == self.buffer_size:
            return True
        # packet was sent, hardware wise buffer still full
        elif (
            len(self.buffer[port]) == self.buffer_size-1
            and self.pkt_available_to_send_now[port]
        ):
            return True
        else:
            return False

    def buffer_empty_actual(self, port):
        """ for next cycle, to determine the next state """
        return not self.buffer[port]

    ### router functions ###

    def sent_controller_pre(self, current_clock_cycle):
        """ serve the current port and check if dest router free """
        port = self.scheduler()
        packet = self.buffer_packet_peek(port)
        dest_id = None
        if packet is not None:
            # check where the packet is going
            direction = self.arbiter(packet.dest_coordinates)
            dest_id = self.neighbours_id[direction]

            # if packet has arrived
            if direction == 0:
                self.buffer_packet_remove(port)
                self.packet_store(packet, current_clock_cycle)
                dest_id = None

        # upper level check if neighour_buffer is free
        return dest_id, packet

    def sent_controller_post(self):
        """ remove the output buffer data from the serving port """
        self.buffer_packet_remove(self.current_serving_port)

    def receive_check(self, packet, sender_id):
        """ check the correct port buffer for incoming pkt """
        port = self.neighbours_id.index(sender_id)
        return self.packet_in(packet, port)

    def prepare_next_cycle(self):
        # mark data available to send for next cycle
        for port in range(len(self.buffer)):
            if self.buffer_empty_actual(port):  # empty buffer
                self.pkt_available_to_send_now[port] = False
            else:
                # set for next cycle
                self.pkt_available_to_send_now[port] = True

    def scheduler(self):
        """
        Func: determine which port to serve
        algo: Round Robin
        """
        self.current_serving_port = (self.current_serving_port + 1) % 5
        return self.current_serving_port

    def arbiter(self, dest_coordinates):
        """
        Func: To determine which direction to send the packet
        Algo: X-Y algorithm
        """
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

    def get_neighbour_direction(self, dest_coordinates):
        """
        Func: To determine which direction is the neighbour
        """
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

    ### external functions for simulator performance ###

    def debug_empty_buffer(self):
        """ for debugging """
        for port in range(len(self.buffer)):
            status = self.buffer_empty_actual(port)
            if status is False:
                print(port, status)

    def empty_buffers(self):
        """
        For: early program termination
        Func: check if all buffer empty.  Return False for any filled buffer
        """
        for port in range(len(self.buffer)):
            status = self.buffer_empty_actual(port)
            if status is False:
                return False
        return True
