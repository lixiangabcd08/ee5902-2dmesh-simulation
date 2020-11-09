"""
Module: single_pkt_test
Desp:   single pkt test for functional check
version: 0.0.1

requirements:   sub_simulator_func.py
                network_map.py
                packet_generator.py
                heatmap.py

Changelog:  0.0.1 - initial release
"""
import argparse
import time
import numpy as np

import sub_simulator_func as sim_func

from network_map import coordinates_2_id
from network_map import coordinates_2_id_list
from network_map import id_2_coordinates

from packet_generator import Generator

from heatmap import heatmap_display
from heatmap import heatmap_multiple_display


def sub_simulator(args, noc_map, noc_map_nodes):
    m, n = args.m, args.n
    cycle_limit = args.cycle_limit
    algo_type = args.algo_type
    verbose = args.verbose
    sim_data_path = args.sim_data_path
    number_of_routers = m * n
    noc_heatmap_list = []

    fout = open(sim_data_path, "w")

    # init the packet generator
    generator = Generator(m, n)

    # set the algo types to run
    if algo_type == 5:  # loop all
        algo_type_list = [0, 1, 2, 3, 4]
    else:  # only run the selected one
        algo_type_list = [algo_type]

    # run the simulation
    for algo_type in algo_type_list:
        args.algo_type = algo_type  # edit the algo_type
        out_str = "*************** For algo %d ***************\n" % algo_type
        fout.write(out_str)
        print(out_str, end="")

        start_time = time.time()

        # create the routers and map them
        router_list, receiver_list = sim_func.create_router_list(args, noc_map,noc_map_nodes)

        # number of cycles to simulate for single packet testing
        for current_clock_cycle in range(cycle_limit):
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

            # if current_clock_cycle % 100 == 0:  # for debugging
            #     print("current_clock_cycle = ", current_clock_cycle)

            if empty_flag:  # all routers has cleared their buffer
                str1 = ("ending cycle = %d" % current_clock_cycle)
                print(str1, end="")
                fout.write(str1)
                break

        print("--- time taken: %s seconds ---" % (time.time() - start_time))  # time
        print("--- Total packets sent: %s ---" % (generator.get_packet_sent_sum()))
        # collect the statistics
        noc_heatmap = sim_func.stats_collection(receiver_list, fout, args)
        noc_heatmap_list.append(noc_heatmap)
    
    # final output for heatmap
    if verbose == 3:
        if len(noc_heatmap_list) == 1:
            heatmap_display(noc_heatmap_list[0], algo_type)
        else:
            heatmap_multiple_display(noc_heatmap_list)