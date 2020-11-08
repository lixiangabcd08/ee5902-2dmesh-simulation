import argparse
import time
import numpy as np

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
    number_of_routers = m * n

    start_time = time.time()

    # create the routers and map them
    router_list, receiver_list = create_router_list(args, noc_map,noc_map_nodes)

    # init the packet generator
    generator = Generator(m, n)

    # run the simulation

    # number of cycles to simulate for single packet testing
    for current_clock_cycle in range(number_of_routers * 5):
        """ set up the testing packets in first cycle """
        if current_clock_cycle == 0:
            dest_coordinates = id_2_coordinates(number_of_routers-1, m, n)
            src_coordinates = id_2_coordinates(0, m, n)
            pk0 = generator.generate_single(0, dest_coordinates, src_coordinates, current_clock_cycle)
            router_list[pk0.source_id].packet_in(pk0, 0)

            dest_coordinates = id_2_coordinates((m*(n-1)), m, n)
            src_coordinates = id_2_coordinates(m-1, m, n)
            pk1 = generator.generate_single(m-1, dest_coordinates, src_coordinates, current_clock_cycle)
            router_list[pk1.source_id].packet_in(pk1, 0)

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

        """
        Why only set the next output pkt after all routers sent their pkt?
        Ans: In hardware, it is not possible to write in and pop out the same
        pkt in 1 cycle. To prevent the software thinking that the new pkt is
        available immediately for sending, we set the flag to prevent new pkt
        being read. 
        
        E.g. When the FIFO is full, if a pkt was sent in that cycle, software 
        wise it is not full anymore, but hardware wise it is will display as 
        full, impossible to write into that FIFO in that clock cycle. It will
        only available in the next cycle.
        """
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