from packet import StatPacket
from network_map import coordinates_2_id, id_2_coordinates
import random
import math
import numpy as np
import copy

### This generator generate random package
class Generator:
    def __init__(self, m, n):
        self.m = m
        self.n = n
        self.packet_sum = 0
    
    def soft_reset(self):
        self.packet_sum = 0

    # generate a single StatPacket packet according to the user input
    def generate_single(
        self, source_id, dest_coordinates, current_coordinates, current_clock_cycle
    ):
        self.packet_sum += 1
        return StatPacket(
            source_id, dest_coordinates, current_coordinates, current_clock_cycle
        )

    # generate a random single StatPacket packet, ignore mapping
    def generate_random_single(self, current_clock_cycle):
        has_two_points = False
        while not has_two_points:
            ini_point = self.gen_random_point()
            des_point = self.gen_random_point()
            if ini_point != des_point:  # make sure the two points are not identical
                has_two_points = True
        source_id = coordinates_2_id(ini_point, self.m, self.n)
        self.packet_sum += 1
        return StatPacket(source_id, des_point, ini_point, current_clock_cycle)

    def gen_random_point(self):
        coordinate_x = random.randint(0, self.m - 1)
        coordinate_y = random.randint(0, self.n - 1)
        return (coordinate_x, coordinate_y)

    def get_packet_sent_sum(self):
        """
        return the number of packets sent out in total
        """
        return self.packet_sum


class RandomGenerator(Generator):
    # rate should be a value between 0 and 10
    def __init__(self, m, n, rate=5, load_cycles = 10):
        super().__init__(m, n)
        self.rate = rate
        # store packets for send for each node
        self.packets = [[] for j in range(m * n)]
        self.current_pkt_index = [0 for j in range(m * n)]

        # create the map
        # for example, 9 nodes will create a map of [0,1,2,3,4],[5,6,7],[8]
        # indicated by [(0,4),(5,7),(8,8)] in packets in the form of (start_node,end_node)
        self.nodes_map = []
        no_of_nodes = m * n
        start_node = 0
        layer_node_no = no_of_nodes
        while start_node < no_of_nodes:
            # insert tuple of (starting_node, ending_node)
            if (
                start_node + math.ceil(layer_node_no / 2) >= no_of_nodes
            ):  # the last layer
                end_node = no_of_nodes - 1
            else:
                end_node = start_node + math.ceil(layer_node_no / 2) - 1
            self.nodes_map.append((start_node, end_node))
            start_node = end_node + 1  # start node for the next layer
            layer_node_no = math.ceil(
                int(layer_node_no / 2)
            )  # number of nodes in the next layer should be half of the one in the current layer
        
        self.pre_generate_pkt(load_cycles)

    def soft_reset(self):
        self.packet_sum = 0
        self.current_pkt_index = [0 for j in range(self.m * self.n)]

    def get_layer_no(self, node_id):
        for index, layer in enumerate(self.nodes_map):
            if layer[1] >= node_id:
                return index

    def pre_generate_pkt(self, load_cycles):
        """
        generate the list of packets to be use for testing based on the 
        load cycles and rate
        """
        for router_id in range(self.m * self.n):
            for current_clock_cycle in range(load_cycles):
                if (np.random.uniform(0, 10) > self.rate):
                    # if the random number is greater than the rate
                    self.generate_packets(router_id, current_clock_cycle)
            
    # generate a list of packet which follows the mapping guideline
    def generate_packets(self, source_id, current_clock_cycle):
        ini_coordinates = id_2_coordinates(source_id, self.m, self.n)
        ini_layer = self.get_layer_no(source_id)
        if ini_layer + 1 < len(self.nodes_map):  # if not the last layer
            node_no = self.nodes_map[ini_layer + 1][0]
            last_node = self.nodes_map[ini_layer + 1][1]
            node_packets = []
            while node_no <= last_node:  # dest must from the next layer
                dest_coordinates = id_2_coordinates(node_no, self.m, self.n)
                node_packets.append(
                    StatPacket(
                        source_id,
                        dest_coordinates,
                        ini_coordinates,
                        current_clock_cycle,
                    )
                )
                node_no += 1
            self.packets[source_id] += node_packets

    def get_pkt_list(self, router_id, current_clock_cycle):
        pkt_list =[]
        pkt_index = self.current_pkt_index[router_id]
        # print((self.packets[router_id]))
        if pkt_index < (len(self.packets[router_id])):  # has packet
            # check if the pkt is for current cycle
            pkt = self.packets[router_id][pkt_index]
            while (pkt.start_clock_cycle == current_clock_cycle):
                pkt = copy.copy(self.packets[router_id][pkt_index])  # copy pkt
                pkt_list.append(pkt)
                self.packet_sum += 1
                pkt_index += 1
                # prepare for next loop
                try:  # next packet might be end of list
                    pkt = self.packets[router_id][pkt_index]
                except IndexError:
                    break

        self.current_pkt_index[router_id] = pkt_index  # save the index
        return pkt_list


# congestion generator
class ConstGenerator(Generator):
    def __init__(self, m, n):
        super().__init__(m, n)
        self.dest_coordinates = (m - 1, n - 1)  # send to the last node

    def get_packet(self, router_id, current_clock_cycle, is_empty):
        if (
            int(router_id / self.n) == router_id % self.n
            and router_id != self.m * self.n - 1
        ):  # node on diagonal and not the last node
            ini_coordinates = id_2_coordinates(router_id, self.m, self.n)
            pkt = StatPacket(
                router_id, self.dest_coordinates, ini_coordinates, current_clock_cycle
            )
            self.packet_sum += 1
        elif (int(router_id % self.n) == self.n - 1) and (
            router_id != self.m * self.n - 1
        ):
            ini_coordinates = id_2_coordinates(router_id, self.m, self.n)
            pkt = StatPacket(
                router_id, self.dest_coordinates, ini_coordinates, current_clock_cycle
            )
            self.packet_sum += 1
        else:
            pkt = None
        return pkt