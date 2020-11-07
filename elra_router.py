"""
module: elra_router
Desp: router based on Low-Cost Routing Architecture (NPL, 2018)

requirements: router.py

Changelog:  0.0.1 - router
"""
from router import BaseRouter


class ELRARouter(BaseRouter):
    def __init__(self, id, coordinates, rx_address):
        super().__init__(id, coordinates, rx_address)
        self.num_of_neighbour_routers = 0
        self.port_groups = []
        self.port_status = [[], [], [], [], []]
        self.Threshold_v = int(self.buffer_size / 2)
        self.current_serving_group = 1

    ### setup router ###

    def setup_router(self, neighbour_routers):
        """ overloading this function to setup the router """
        self.set_neighbour_routers(neighbour_routers)
        self.set_neighbours()
        self.set_num_of_neighbour_routers(neighbour_routers)
        self.set_group()
        self.set_port_status(0)  # speical set for loacl port

    def set_num_of_neighbour_routers(self, neighbour_routers):
        self.num_of_neighbour_routers = len(neighbour_routers)

    def set_group(self):
        """
        group the routers in groups as per paper, with some mod for 2d mesh.
        The local port is in its group.
        Other routers in their own group.

        hardcoded for 2d mesh
        """
        temp_port_groups = [[0], []]

        for port, router in enumerate(self.neighbour_routers):
            if router:  # there is address
                temp_port_groups[1].append(port)
                self.set_port_status(port)

        self.port_groups = temp_port_groups
        # print(self.id, self.port_groups)  # debug

    def set_port_status(self, port):
        """ inital the status """
        self.port_status[port] = [0, 0, 0, 0, 0, 0]  # 0 w_sum and the rest

    ### buffer status ###
    def buffer_over_threshold_v(self, port):
        # Case when pkt sent, the actual buffer size becomes (Threshold_v-1)
        if (len(self.buffer[port]) == self.Threshold_v - 1) and self.pkt_sent[port]:
            return True

        # For cases when buffer_size is more than threshold, even before/after sent
        elif len(self.buffer[port]) >= self.Threshold_v:
            return True
        else:
            return False

    ### router functions ###

    def prepare_next_cycle(self):
        """ overload BaseRouter's function """
        # update grant and wait status, special for ELRA router
        # as long the port is served, it need to update
        self.update_port_status_after_serving()
        super().prepare_next_cycle()

    def scheduler(self):
        """
        Func: determine which port to serve
        algo: Round Robin(on group) + Priority (weight per port)
        """
        # select the group by RR
        self.current_serving_group = (self.current_serving_group + 1) % 2

        self.update_group_port_status(self.current_serving_group)  # new for ELRA router

        # determine which port to serve within the group
        if self.current_serving_group == 0:  # local port
            self.current_serving_port = 0
        else:  # other ports
            # check which port has the highest weights
            max_w_sum = -1
            temp_serving_port = 0
            for port in self.port_groups[self.current_serving_group]:
                curr_w_sum = self.port_status[port][0]  # always at position 0
                if curr_w_sum > max_w_sum:
                    # print(port,max_w_sum)
                    max_w_sum = curr_w_sum
                    temp_serving_port = port
            self.current_serving_port = temp_serving_port
        return self.current_serving_port

    ### special ELRA functions ###

    def update_group_port_status(self, current_serving_group):
        for port in self.port_groups[current_serving_group]:
            self.update_port_status_weight(port)

    def update_port_status_weight(self, port):
        """ do this before the start of the cycle """
        status = self.port_status[port]
        w_p = int(bool(not self.buffer_empty(port)))  # status_present
        w_b = int(bool(self.buffer_over_threshold_v(port)))  # status_busy
        w_c = int(bool(self.buffer_full(port)))  # status_congested
        w_g = status[4]  # not updated here
        w_w = status[5]  # not updated here

        w_sum = self.weight_sum(w_p, w_b, w_c, w_g, w_w)
        self.port_status[port] = [w_sum, w_p, w_b, w_c, w_g, w_w]  # fixed order

    def update_port_status_after_serving(self):
        """ do this after current serving port is confirmed """
        for port in self.port_groups[self.current_serving_group]:
            if port == self.current_serving_port and self.pkt_sent[port] == True:
                self.update_status_for_granted(port)
            else:
                self.update_status_for_waiting(port)

    def update_status_for_granted(self, port):
        self.port_status[port][4] = 1
        self.port_status[port][5] = 0

    def update_status_for_waiting(self, port):
        # check if buffer empty, then it is not waiting
        if self.buffer_empty(port):
            self.port_status[port][4] = 0
            self.port_status[port][5] = 0
        else:
            self.port_status[port][4] = 0
            self.port_status[port][5] = 1

    def weight_sum(self, w_p, w_b, w_c, w_g, w_w):
        """ calculate the total traffic status weight """
        return w_p * 3 + w_b * 1 + w_c * 2 + w_g * (-1) + w_w * 1
