import argparse
import networkx as nx
import time

from network_map import coordinates_2_id
from network_map import coordinates_2_id_list
from network_map import id_2_coordinates

import single_pkt_test as SPT
import random_pkt_test as RPT
import constant_pkt_test as CPT


def main(args):

    m, n = args.m, args.n
    # num_of_testing_pkts = args.num_of_testing_pkts
    # algo_type = args.algo_type
    print(args)
    # create the network mapping
    noc_map = nx.grid_2d_graph(m, n)  # (rows, columns)
    noc_map_nodes = list(noc_map.nodes)
    # print(list(noc_map.nodes))  # debug
    # print(list(noc_map.edges))  # debug

    if args.test_mode == 0:
        SPT.sub_simulator(args, noc_map, noc_map_nodes)
    elif args.test_mode == 1:
        RPT.sub_simulator(args, noc_map, noc_map_nodes)
    elif args.test_mode == 2:
        CPT.sub_simulator(args, noc_map, noc_map_nodes)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="noc simulator", formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument("--m", type=int, default="4", help="m, number of rows")
    parser.add_argument("--n", type=int, default="4", help="n, number of column")
    parser.add_argument(
        "--algo_type",
        type=int,
        default="0",
        help="""type of routers to test.
        0:basic XY,
        1:modified XY,
        2:Adaptive Routing,
        3:ELRA,
        4:CA router
        5:all routers""",
    )
    parser.add_argument("--cycle_limit", type=int, default="200", help="cycles limit")
    parser.add_argument(
        "--load_cycles",
        type=int,
        default="20",
        help="cycles to inject packets in test mode 2",
    )
    parser.add_argument(
        "--target_rate",
        type=float,
        default="5",
        help="rate to send spikes in test mode 1",
    )
    parser.add_argument(
        "--test_mode",
        type=int,
        default="0",
        help="0->single pkt test, 1->random pkt test, 2->congestion pkt test",
    )
    args = parser.parse_args()

    main(args)
