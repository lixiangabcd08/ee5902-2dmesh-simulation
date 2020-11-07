"""
Module: modifiedXY Router
Desp: Modified X–Y routing for mesh topology based NoC router
version: 0.0.2

requirements: router.py

Changelog:  0.0.1 - router
            0.0.2 - updated external functions to check for side buffer also
"""
from router import BaseRouter


class modXYRouter(BaseRouter):
    def __init__(self, id, coordinates, rx_address):
        self.buffer_size = 1
        self.side_buffer_size = 3
        self.side_buffer = [[], [], [], [], []]  # 5 buffers, 1 for each port
        self.input_port_priority = [None, None, None, None, None]
        self.output_port_priority = [None, None, None, None, None]
        self.pkt_waiting_in_side_buffer = [False, False, False, False, False]
        self.num_ports_connected = 0
        self.current_serving_output_port = 0
        super().__init__(id, coordinates, rx_address)

    def setup_router(self, neighbour_routers):
        """ use/overload this function to setup the router """
        self.set_neighbour_routers(neighbour_routers)
        self.set_neighbours()
        self.set_priority()

    def set_priority(self):
        """ set the inital priority of the routers """
        priority = 0
        for port, router in enumerate(self.neighbours_id):
            if router is not None:
                self.input_port_priority[port] = priority
                self.output_port_priority[port] = priority
                priority += 1
        self.num_ports_connected = priority

    ### buffer operations ###

    def side_buffer_packet_in(self, packet, port):
        """ store to side buffer """
        if self.side_buffer_full(port):
            return False
        else:  # not full
            # no need to update hte packet
            self.side_buffer[port].append(packet)
            return True

    def side_buffer_packet_peek(self, port):
        """ retrive the side buffer data """
        if not self.side_buffer_empty(port):
            packet = self.side_buffer[port][0]  # always the first pkt
            return packet
        else:
            return None

    def side_buffer_packet_remove(self, port):
        """ remove the side buffer data """
        if not self.side_buffer_empty(port):
            # remove the packet
            self.side_buffer[port].pop(0)
        else:
            raise BufferError("Trying to remove packet from empty buffer")

    ### buffer status ###

    def side_buffer_empty(self, port):
        """ for current cycle, like hardware FIFO status """
        # when no packet available to output, the buffer is empty in this cycle
        if not self.pkt_waiting_in_side_buffer[port]:
            return True
        else:
            return False  # assume that the flag is set correctly

    def side_buffer_full(self, port):
        """ for current cycle, like hardware FIFO status """
        # no packet sent, but FIFO still full
        if len(self.side_buffer[port]) >= self.side_buffer_size:
            return True
        # packet was sent, but hardware wise buffer still considered full
        elif (
            len(self.side_buffer[port]) == self.buffer_size - 1 and self.pkt_sent[port]
        ):
            return True
        else:
            return False

    def side_buffer_empty_actual(self, port):
        """ for next cycle, to determine the next state """
        return not self.side_buffer[port]

    ### router functions ###

    def send_controller(self, current_clock_cycle):
        """
        Top warpper to run the send packet
        General steps:
        Get the packet, check if the receiving router free, the remove pkt
        """
        direction, packet = self.send_controller_pre(current_clock_cycle)
        if direction is not None:  # if there is packet
            status = self.neighbour_routers[direction].receive_check(
                packet, self.id
            )  # try sending
            if status is True:
                # remove from sending router
                self.send_controller_post()
            else:  # send fail
                # try to store at side buffer first
                self.send_controller_side_buffer_store(packet)

    def send_controller_side_buffer_store(self, packet):
        status = self.side_buffer_packet_in(packet, self.current_serving_port)
        if status:  # packet stored
            self.send_controller_post()
        # side buffer full, packet stuck, do nothing to stall the route

    def update_all_priority(self):
        """ for all the port priorities """
        self.input_port_priority = self.update_priority(
            self.input_port_priority, self.current_serving_port
        )
        self.output_port_priority = self.update_priority(
            self.output_port_priority, self.current_serving_output_port
        )

    def update_priority(self, port_priority, current_serving_port):
        """
        reduce the priority for the serving port
        update before next cycle starts
        """
        max_priority = self.num_ports_connected - 1
        serving_port_old_priority = port_priority[current_serving_port]

        if serving_port_old_priority < max_priority:  # not the lowest
            # increase the priority for other lower priority ports
            for priority in range(serving_port_old_priority + 1, max_priority + 1):
                try:
                    port = port_priority.index(priority)
                    port_priority[port] = priority - 1
                except ValueError:
                    pass
        # else for port already have lowest priority, no change

        # give the served port lowest priority
        port_priority[current_serving_port] = max_priority

        return port_priority

    def prepare_next_cycle_side(self):
        for port in range(len(self.side_buffer)):
            # mark data available to send for next cycle
            if self.side_buffer_empty_actual(port):  # empty buffer
                self.pkt_waiting_in_side_buffer[port] = False
            else:
                # set for next cycle
                self.pkt_waiting_in_side_buffer[port] = True

    def inject_pkt_from_side_buffer(self):
        """
        when injecting the packet, the paper seems to allow the packet to send
        out in next cycle.
        """
        # check if there is data in the side buffer first
        for port in range(len(self.side_buffer)):
            if self.side_buffer[port]:
                # check if the input buffer is available
                if not self.pkt_available_to_send_now[port]:  # not available = empty
                    packet = self.side_buffer_packet_peek(port)
                    self.buffer[port].append(packet)
                    self.side_buffer_packet_remove(port)

    def prepare_next_cycle(self):
        self.update_all_priority()
        self.prepare_next_cycle_side()
        self.inject_pkt_from_side_buffer()
        super().prepare_next_cycle()

    def send_pkt_queue(self):
        """ check which port need to send pkt, return a list """
        send_list = []
        for port, status in enumerate(self.pkt_available_to_send_now):
            if status:  # there is a pkt
                send_list.append(port)
        return send_list

    def group_output_port(self, send_list):
        """ group the input ports based on their direction/output """
        output_port_dict = {}
        # the input list should have more than 2 ports
        for port in send_list:
            packet = self.buffer_packet_peek(port)
            output_port = self.arbiter(packet.dest_coordinates)
            # retrive and update dict
            try:
                current_list = output_port_dict[output_port]
                current_list.append(port)
                output_port_dict.update({output_port: current_list})
            except KeyError:
                output_port_dict.update({output_port: [port]})

        return output_port_dict

    def check_highest_priority(self, port_list, priority_list):
        """
        return the port with the highest priority
        port_list is the filtered list of requesting ports
        """
        highest_priority_port = 0
        highest_priority = self.num_ports_connected
        for port in port_list:
            port_priority = priority_list[port]
            if port_priority < highest_priority:
                highest_priority = port_priority
                highest_priority_port = port
        return highest_priority_port

    def scheduler(self):
        """
        Func: determine which port to serve based on priority
        algo: iSLIP scheduler
        """
        send_list = self.send_pkt_queue()
        if send_list:
            if len(send_list) == 1:
                self.current_serving_port = send_list[0]
                return self.current_serving_port
            else:  # more than 1 port has pkt waiting
                # check which output port has the highest priority
                output_port_dict = self.group_output_port(send_list)
                self.current_serving_output_port = self.check_highest_priority(
                    output_port_dict, self.output_port_priority
                )

                # select which input port based on their priority
                input_list = output_port_dict[self.current_serving_output_port]
                self.current_serving_port = self.check_highest_priority(
                    input_list, self.input_port_priority
                )
                return self.current_serving_port

        else:  # no data in all ports, stay the same
            return self.current_serving_port

    ### external functions for simulator performance ###

    def debug_empty_buffer(self):
        """ for debugging """
        super().debug_empty_buffer()
        for port in range(len(self.side_buffer)):
            status = self.side_buffer_empty_actual(port)
            if status is False:
                print("side_buffer", port, status)

    def empty_buffers(self):
        """
        For: early program termination
        Func: check if all buffer empty.  Return False for any filled buffer
        """
        for port in range(len(self.side_buffer)):
            status = self.side_buffer_empty_actual(port)
            if status is False:
                return False
        return super().empty_buffers()

    def empty_side_buffers(self):
        """
        For: early program termination
        Func: check if all buffer empty.  Return False for any filled buffer
        """
        for port in range(len(self.side_buffer)):
            status = self.side_buffer_empty_actual(port)
            if status is False:
                return False
        return True