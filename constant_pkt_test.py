import argparse
import time
import numpy as np

from network_map import coordinates_2_id
from network_map import coordinates_2_id_list

from receiver import PacketReceiver as rx

from router import BaseRouter as Router
from elra_router import ELRARouter
from ca_router import CARouter
from a_router import ARouter
from modxy_router import modXYRouter

from packet import BasePacket
from packet import StatPacket
from packet_generator import Generator
from packet_generator import RandomGenerator
from packet_generator import ConstGenerator

from heatmap import heatmap_display

def sub_simulator(args, noc_map, noc_map_nodes):
    m, n = args.m, args.n
    algo_type = args.algo_type
    cycle_limit = args.cycle_limit
    load_cycles = args.load_cycles
    algo_type = args.algo_type
    number_of_routers = m * n
    router_list = []
    receiver_list = []

    start_time = time.time()

    # create the routers and map them
    for router_id in range(number_of_routers):
        # receiver to store the packets from routers
        rx_address = rx(router_id)
        receiver_list.append(rx_address)

        # get the parameters
        coordinates = noc_map_nodes[router_id]
        neighbours_coordinates = list(noc_map.adj[coordinates])
        neighbours_id = coordinates_2_id_list(neighbours_coordinates, m, n)
        # create the router based on algo
        if algo_type == 4:
            router_list.append(CARouter(router_id, coordinates, rx_address))
        elif (algo_type == 3):  
            router_list.append(ELRARouter(router_id, coordinates, rx_address))
        elif (algo_type == 2): 
            router_list.append(ARouter(router_id, coordinates, rx_address))
        elif (algo_type == 1):
            router_list.append(modXYRouter(router_id, coordinates, rx_address))
        else:
            router_list.append(Router(router_id, coordinates, rx_address))

    # This can only be done after all the routers are initiated
    for router_id in range(number_of_routers):
        # get the parameters
        coordinates = noc_map_nodes[router_id]
        neighbours_coordinates = list(noc_map.adj[coordinates])
        neighbours_id = coordinates_2_id_list(neighbours_coordinates, m, n)
        neighbour_routers = [
            router_list[neighbour_id] for neighbour_id in neighbours_id
        ]
        router_list[router_id].setup_router(neighbour_routers)

    # init the packet generator
    generator= ConstGenerator(m, n) # greate the sir, less likely packets are generated

    # run the simulation

    # number of cycles to simulate for single packet testing
    for current_clock_cycle in range(cycle_limit):
        """ set up the testing packets in load_cycles """
        if current_clock_cycle < load_cycles:
            for router in router_list:
                # each router have possibility to initiate packet
                pk = generator.get_packet(router.id,current_clock_cycle,router.buffer_empty_actual(0))
                if pk is not None: # no packet from this router
                    router.packet_in(pk, 0)

        empty_flag = True

        """ This is to run the routers for 1 cycle to send out pkt """
        for router_id in range(number_of_routers):
            # check if the router is empty for early cycle termination
            is_empty = router_list[router_id].empty_buffers()
            if not is_empty:
                empty_flag = False

            # print("current ", current_clock_cycle, router_id)  # debug
            # router_list[router_id].debug_empty_in_buffer()  # debug
            # let router handles the background check
            router_list[router_id].send_controller(current_clock_cycle)

        # loop 2nd time to set the next output packet in the router's buffers
        for router_id in range(number_of_routers):
            router_list[router_id].prepare_next_cycle()

        if current_clock_cycle % 100 == 0:  # for debugging
            print("current_clock_cycle = ", current_clock_cycle)

        if empty_flag:  # all routers has cleared their buffer
            print("ending cycle = ", current_clock_cycle)
            break

    print("--- time taken: %s seconds ---" % (time.time() - start_time))  # time
    # collect the statistics
    for router_id in range(number_of_routers):
        receiver_list[router_id].print_stat()
        receiver_list[router_id].print_packet_stat()

    # heatmap
    noc_heatmap = np.zeros(number_of_routers, dtype=int)
    for router_id in range(number_of_routers):
        router_heatmap = (receiver_list[router_id].heatmap_collection())
        # add the counts to the overall heatmap
        # if router_heatmap is not None:
        for router in router_heatmap:
            noc_heatmap[router] += router_heatmap[router]

    noc_heatmap = np.reshape(noc_heatmap, (m,n))
    heatmap_display(noc_heatmap)