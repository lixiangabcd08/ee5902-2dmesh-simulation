import argparse
import networkx as nx
import time

from network_map import coordinates_2_id
from network_map import coordinates_2_id_list

import single_pkt_test as SPT
import random_pkt_test as RPT
import constant_pkt_test as CPT


def main(args):

    m, n = args.m, args.n
    # num_of_testing_pkts = args.num_of_testing_pkts
    # algo_type = args.algo_type
    print(args)
    # create the network mapping
    noc_map = nx.grid_2d_graph(m, n)
    noc_map_nodes = list(noc_map.nodes)
    # print(list(noc_map.nodes))  # debug
    # print(list(noc_map.edges))  # debug

    if (args.test_mode == 0):
        SPT.sub_simulator(args, noc_map, noc_map_nodes)
    elif (args.test_mode == 1):
        RPT.sub_simulator(args, noc_map, noc_map_nodes)
    elif (args.test_mode == 2):
        CPT.sub_simulator(args, noc_map, noc_map_nodes)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="noc simulator")
    parser.add_argument("--m", type=int, default="4", help="m, number of columns ")
    parser.add_argument("--n", type=int, default="4", help="n, number of rows ")
    parser.add_argument(
        "--algo_type", type=int, default="0", help="type of routers to test"
    )
    parser.add_argument(
        "--num_of_testing_pkts", type=int, default="5", help="num of pkts to send"
    )
    parser.add_argument(
        "--test_mode",
        type=int,
        default="0",
        help="0->single pkt test, 1->multiple pkt test",
    )
    args = parser.parse_args()

    main(args)
