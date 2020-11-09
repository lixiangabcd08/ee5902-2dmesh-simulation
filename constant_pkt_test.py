"""
Module: constant_pkt_test
Desp:   constant pkt test for NoC congestion
version: 0.0.1

requirements:   sub_simulator_func.py
                packet_generator.py
                heatmap.py

Changelog:  0.0.1 - initial release
"""
import argparse
import time
import numpy as np

import sub_simulator_func as sim_func

from packet_generator import ConstGenerator

from heatmap import heatmap_display
from heatmap import heatmap_multiple_display


def sub_simulator(args, noc_map, noc_map_nodes):
    m, n = args.m, args.n
    algo_type = args.algo_type
    cycle_limit = args.cycle_limit
    load_cycles = args.load_cycles
    algo_type = args.algo_type
    verbose = args.verbose
    print_output = args.print_output
    sim_data_path = args.sim_data_path
    number_of_routers = m * n
    noc_heatmap_list = []

    fout = open(sim_data_path, "w")

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

        # init the packet generator
        generator = ConstGenerator(m, n)

        # create the routers and map them
        router_list, receiver_list = sim_func.create_router_list(
            args, noc_map, noc_map_nodes
        )

        # number of cycles to simulate for single packet testing
        for current_clock_cycle in range(cycle_limit):

            empty_flag = True

            """ set up the testing packets in load_cycles """
            if current_clock_cycle < load_cycles:
                for router in router_list:
                    # each router have possibility to initiate packet
                    pk = generator.get_packet(
                        router.id, current_clock_cycle, router.buffer_empty_actual(0)
                    )
                    if pk is not None:  # no packet from this router
                        router.packet_in(pk, 0)

                empty_flag = False  # prevent early termination

            """ This is to run the routers for 1 cycle to send out pkt """
            for router_id in range(number_of_routers):
                # check if the router is empty for early cycle termination
                is_empty = router_list[router_id].empty_buffers()
                if not is_empty:
                    empty_flag = False

                # let router handles the background check
                router_list[router_id].send_controller(current_clock_cycle)

            # loop 2nd time to set the next output packet in the router's buffers
            for router_id in range(number_of_routers):
                router_list[router_id].prepare_next_cycle()

            # if current_clock_cycle % 100 == 0:  # for debugging
            #     print("current_clock_cycle = ", current_clock_cycle)

            if empty_flag:  # all routers has cleared their buffer
                str1 = ("ending cycle = %d\n" % current_clock_cycle)
                fout.write(str1)
                print(str1, end="")
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

    fout.close()