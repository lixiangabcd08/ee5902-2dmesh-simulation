"""
Module: BaseRouter
Desp:   Basic XY 2d mesh router for baseline testing
version: 0.2.4

requirements: receiver.py

Changelog:  0.0.1 - single buffer router (software)
            0.0.2 - 1 buffer per port and more functions
            0.1.0 - combined the buffer together for easy calculation
                    use a flag (pkt_available_to_send_now) to mark output data
                    Making buffer signals more hardware like
            0.2.0 - using 1 wrapper function to setup the router
                  - bug fix on buffer_empty, might return !empty buffer when
                    HW should be empty
            0.2.1 - bug fix on buffer_full, not enough status to indicate when
                    pkt sent but buffer has 1 empty space. Added pkt_sent
            0.2.2 - integrate the send_controller to simply top operation
            0.2.3 - bug fix, scheduler serving unconnected ports 
            0.2.4 - unlimited buffer for input local port
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
        self.neighbour_routers = [None, None, None, None, None]  # ignore local
        self.buffer = [[], [], [], [], []]  # 5 buffers, 1 for each port
        self.pkt_available_to_send_now = [False, False, False, False, False]
        self.pkt_sent = [False, False, False, False, False]  # for buffer_full
        self.buffer_size = 4
        self.local_storage = rx_address
        self.current_serving_port = 0  # so first cycle will server port 0

    ### setup the router ###

    def setup_router(self, neighbour_routers):
        """ use/overload this function to setup the router """
        self.set_neighbour_routers(neighbour_routers)
        self.set_neighbours()

    def set_neighbour_routers(self, neighbour_routers):
        """ set the neighbour router in the respective port directions """
        for router in neighbour_routers:
            coordinates = router.coordinates
            # use the old arbiter to decide the direction of the neighbour
            direction = self.get_neighbour_direction(coordinates)
            self.neighbour_routers[direction] = router

    def set_neighbours(self):
        """
        set the id in the respective port directions
        a bit redundant if we can get the neighbour address to access directly
        """
        for port, router in enumerate(self.neighbour_routers):
            if router:
                self.neighbours_id[port] = router.id

    ### buffer operations ###

    def packet_in(self, packet, port):
        """ store to input buffer """
        if port == 0:  # unlimited buffer for local port
            packet.update_packet(self.id, self.coordinates)
            self.buffer[port].append(packet)
            return True
        elif self.buffer_full(port):  # for other ports
            return False
        else:  # not full
            # update packet information before storing
            packet.update_packet(self.id, self.coordinates)
            self.buffer[port].append(packet)
            return True

    def packet_in_all(self, pkt_list):
        """ for packet generator to store all the input packets """
        for pk in pkt_list:
            self.packet_in(pk, 0)

    def packet_store(self, packet, current_clock_cycle):
        """ store to local storage """
        packet.update_clock_cycle(current_clock_cycle)  # update cycle
        self.local_storage.store(packet)

    def buffer_packet_peek(self, port):
        """ retrive the output buffer data """
        if self.pkt_available_to_send_now[port]:
            packet = self.buffer[port][0]  # always the first pkt
            return packet
        else:
            return None

    def buffer_packet_remove(self, port):
        """ remove the output buffer data """
        if not self.buffer_empty(port):
            # remove the packet
            self.buffer[port].pop(0)
        else:
            raise BufferError("Trying to remove packet from empty buffer")

    ### buffer status ###

    def buffer_empty(self, port):
        """ for current cycle, like hardware FIFO status """
        # when no packet available to output, the buffer is empty in this cycle
        if not self.pkt_available_to_send_now[port]:
            return True
        else:
            return False  # assume that the flag is set correctly

    def buffer_full(self, port):
        """ for current cycle, like hardware FIFO status """
        # no packet sent, but FIFO still full
        if len(self.buffer[port]) >= self.buffer_size:
            return True
        # packet was sent, but hardware wise buffer still considered full
        elif len(self.buffer[port]) == self.buffer_size - 1 and self.pkt_sent[port]:
            return True
        else:
            return False

    def buffer_empty_actual(self, port):
        """ for next cycle, to determine the next state """
        return not self.buffer[port]

    ### router functions ###

    def send_controller(self, current_clock_cycle):
        """
        Top warpper to run the send packet
        General steps:
        Get the packet, check if the receiving router free, the remove pkt
        """
        direction, packet = self.send_controller_pre(current_clock_cycle)
        if direction is not None:  # if there is packet
            # print("router",self.id, direction)  # debugging
            status = self.neighbour_routers[direction].receive_check(
                packet, self.id
            )  # try sending
            if status is True:
                # remove from sending router
                self.send_controller_post()

    def send_controller_pre(self, current_clock_cycle):
        """ serve the current port and check if dest router free """
        port = self.scheduler()
        packet = self.buffer_packet_peek(port)
        direction = None
        if packet is not None:
            # check where the packet is going
            direction = self.arbiter(packet.dest_coordinates)

            # if packet has arrived
            if direction == 0:
                self.buffer_packet_remove(port)
                self.packet_store(packet, current_clock_cycle)
                direction = None

        # upper level check if neighour_buffer is free
        return direction, packet

    def send_controller_post(self):
        """ remove the buffer data from the serving port """
        self.buffer_packet_remove(self.current_serving_port)
        self.pkt_sent[self.current_serving_port] = True  # to indicate the pkt sent

    def receive_check(self, packet, sender_id):
        """ check the correct port buffer for incoming pkt """
        port = self.neighbours_id.index(sender_id)
        return self.packet_in(packet, port)

    def prepare_next_cycle(self):
        for port in range(len(self.buffer)):
            # reset the sent flag
            self.pkt_sent[port] = False

            # mark data available to send for next cycle
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
        current_port = self.current_serving_port

        # loop through the list to check next present port
        for next_port in range(current_port + 1, len(self.neighbours_id)):
            neighbour_router = self.neighbours_id[next_port]
            if neighbour_router is not None:
                self.current_serving_port = next_port
                return next_port

        # reached the end of the list, has to be back to 0
        next_port = 0
        self.current_serving_port = next_port
        return next_port

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
