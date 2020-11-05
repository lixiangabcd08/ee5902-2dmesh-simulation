from packet import StatPacket
from network_map import coordinates_2_id, id_2_coordinates
import random
import math
import numpy as np

### This generator generate random package
class Generator():
    def __init__(self, m, n):
        self.m = m
        self.n = n
    
        # store packets for send for each node
        self.packets = [[]] * m * n

        # create the map
        # for example, 9 nodes will create a map of [0,1,2,3,4],[5,6,7],[8]
        # indicated by [(0,4),(5,7),(8,8)] in packets in the form of (start_node,end_node)
        self.nodes_map = []
        no_of_nodes = m*n
        start_node = 0
        layer_node_no = no_of_nodes
        while start_node < no_of_nodes:
            # insert tuple of (starting_node, ending_node)
            if start_node + math.ceil(layer_node_no/2) >= no_of_nodes: # the last layer
                end_node = no_of_nodes - 1
            else:
                end_node = start_node + math.ceil(layer_node_no/2) - 1
            self.nodes_map.append((start_node, end_node))
            start_node = end_node + 1 # start node for the next layer
            layer_node_no = math.ceil(int(layer_node_no/2)) # number of nodes in the next layer should be half of the one in the current layer

    # generate a single StatPacket packet according to the user input
    def generate_single(self, source_id, dest_coordinates, current_coordinates, current_clock_cycle):
        return StatPacket(source_id,dest_coordinates,current_coordinates,current_clock_cycle)

    # generate a random single StatPacket packet, ignore mapping
    def generate_random_single(self, current_clock_cycle):
        has_two_points = False
        while not has_two_points:
            ini_point = self.gen_random_point()
            des_point = self.gen_random_point()
            if ini_point != des_point: # make sure the two points are not identical
                has_two_points = True
        source_id = coordinates_2_id(ini_point,self.m,self.n)
        return StatPacket(source_id,des_point,ini_point, current_clock_cycle)

    def get_packet(self,router_id,current_clock_cycle,is_empty):
        if not self.packets:
            self.generate_packets(router_id, current_clock_cycle)
        pkt = self.packets.pop(0)
        return pkt

    # generate a list of packet which follows the mapping guideline
    def generate_packets(self, source_id, current_clock_cycle):
        ini_coordinates = id_2_coordinates(source_id,self.m,self.n)
        ini_layer = self.get_layer_no(source_id)
        if ini_layer+1 < len(self.nodes_map): # if not the last layer
            node_no = self.nodes_map[ini_layer+1][0]
            last_node = self.nodes_map[ini_layer+1][1]
            node_packets = []
            while node_no <= last_node: # dest must from the next layer
                dest_coordinates = id_2_coordinates(node_no,self.m,self.n)
                node_packets.append(StatPacket(source_id,dest_coordinates,ini_coordinates,current_clock_cycle))
                node_no += 1
            self.packets[source_id] += node_packets

    def get_layer_no(self,node_id):
        for index,layer in enumerate(self.nodes_map):
            if layer[1] >= node_id:
                return index

    def gen_random_point(self):
        coordinate_x = random.randint(0,self.m-1)
        coordinate_y = random.randint(0,self.n-1)
        return (coordinate_x, coordinate_y)


class RandomGenerator(Generator):
    # rate should be a value between -10 and 10
    def __init__(self, m, n, rate=5):
        super().__init__(m,n)
        self.rate = rate

    def get_packet(self,router_id,current_clock_cycle, is_empty):
        # Gaussian random values of average 0 and standard deviation of 1
        if np.random.uniform(0,10) > self.rate: # if the random number is greater than the rate
            self.generate_packets(router_id,current_clock_cycle)
        if len(self.packets[router_id]) > 0 and is_empty: # has packet
            pkt = self.packets[router_id].pop(0)
        else:
            pkt = None
        return pkt

    def generate_list(self,current_clock_cycle):
        random_list = []
        random_list.append(self.generate_random_single(current_clock_cycle))
        return random_list


class ConstGenerator(Generator):
    def __init__(self, m, n, sir=20):
        super().__init__(m,n)
        self.sir = sir

    # return BasePacket
    def get_packet(self, router_id, current_clock_cycle, is_empty):
        # if current_clock_cycle is divisible of sir
        if not current_clock_cycle%self.sir:
            self.generate_packets(router_id,current_clock_cycle)
        if len(self.packets[router_id]) > 0 and is_empty: # has packet
            pkt = self.packets[router_id].pop(0)
        else:
            pkt = None
        return pkt