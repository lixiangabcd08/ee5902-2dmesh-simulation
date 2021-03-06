"""
Module: random_pkt_test
Desp:   random pkt test for NoC loading
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

from packet_generator import RandomGenerator

from heatmap import heatmap_display
from heatmap import heatmap_multiple_display


def sub_simulator(args, noc_map, noc_map_nodes):
    m, n = args.m, args.n
    algo_type = args.algo_type
    cycle_limit = args.cycle_limit
    load_cycles = args.load_cycles
    target_rate = args.target_rate  # special for random generator
    number_of_runs = args.runs
    algo_type = args.algo_type
    verbose = args.verbose
    print_output = args.print_output
    sim_data_path = args.sim_data_path
    sim_summary_path = args.sim_summary_path
    number_of_routers = m * n
    noc_heatmap_list = []
    cycle_taken = [[] for j in range(number_of_runs)]  # order by runs
    packet_sent = [[] for j in range(number_of_runs)]
    throughput = [[] for j in range(number_of_runs)]

    fout = open(sim_data_path, "w")
    fsum = open(sim_summary_path, "w")

    if number_of_runs > 1 and verbose == 3:
        print("Warning: verbose 3 not supported in multiple runs")

    # set the algo types to run
    if algo_type == 5:  # loop all
        algo_type_list = [0, 1, 2, 3, 4]
    else:  # only run the selected one
        algo_type_list = [algo_type]


    # run the simulation
    for run in range(number_of_runs):
        out_str = "-------- Algo %d - Run %d --------\n" % (algo_type, run)
        fout.write(out_str)
        print(out_str, end="")

        # init the packet generator to be used for the run
        generator = RandomGenerator(
            m, n, rate=target_rate, load_cycles=load_cycles,
        )  # greater the rate, less likely packets are generated


        for algo_type in algo_type_list:
            args.algo_type = algo_type  # edit the algo_type
            out_str = "*************** For algo %d ***************\n" % algo_type
            fout.write(out_str)
            print(out_str, end="")

            start_time = time.time()
            # create the routers and map them
            router_list, receiver_list = sim_func.create_router_list(
                args, noc_map, noc_map_nodes,
            )

            # soft reset the stats in generator
            generator.soft_reset()

            # number of cycles to simulate for single packet testing
            for current_clock_cycle in range(cycle_limit):

                if current_clock_cycle < load_cycles:
                    empty_flag = False  # prevent early termination
                else:
                    empty_flag = True

                """ set up the testing packets in each cycle """
                for router in router_list:
                    # each router have possibility to initiate packet
                    pk_list = generator.get_pkt_list(
                        router.id,
                        current_clock_cycle,
                    )
                    if pk_list is not None:  # no packet from this router
                        router.packet_in_all(pk_list)

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
                    cycle_taken[run].append(current_clock_cycle)
                    str1 = "ending cycle = %d\n" % current_clock_cycle
                    fout.write(str1)
                    print(str1, end="")
                    break

            print("--- time taken: %s seconds ---" % (time.time() - start_time))  # time
            print("--- Total packets sent: %s ---" % (generator.get_packet_sent_sum()))
            # collect the statistics
            noc_heatmap = sim_func.stats_collection(receiver_list, fout, args)
            noc_heatmap_list.append(noc_heatmap)
            packet_sent[run].append(generator.get_packet_sent_sum())

    # summary for the runs
    sim_func.summary(packet_sent, cycle_taken, fsum)

    # final output for heat map, only for 1 run
    if verbose == 3 and number_of_runs == 1:
        if len(noc_heatmap_list) == 1:
            heatmap_display(noc_heatmap_list[0], algo_type)
        else:
            heatmap_multiple_display(noc_heatmap_list)

    fout.close()
    fsum.close()
