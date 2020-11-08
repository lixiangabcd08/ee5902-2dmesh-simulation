"""
Module: simulator
Desp:   top wrapper for 2D mesh NoC simulator
version: 0.0.1

requirements:   network_map.py,
                single_pkt_test.py,
                random_pkt_test.py
                constant_pkt_test.py
                networkx

Changelog:  0.0.1 - initial release
"""
import argparse
import networkx as nx
import time

from network_map import coordinates_2_id
from network_map import coordinates_2_id_list
from network_map import id_2_coordinates

import single_pkt_test as SPT
import random_pkt_test as RPT
import constant_pkt_test as CPT


def str2bool(v):
    if isinstance(v, bool):
        return v
    if v.lower() in ("yes", "true", "t", "y", "1"):
        return True
    elif v.lower() in ("no", "false", "f", "n", "0"):
        return False
    else:
        return v


def main(args):

    m, n = args.m, args.n
    print(args)
    # create the network mapping
    noc_map = nx.grid_2d_graph(m, n)  # (rows, columns)
    noc_map_nodes = list(noc_map.nodes)

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
    parser.add_argument("--cycle_limit", type=int, default="300", help="cycles limit")
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
    parser.add_argument(
        "--verbose",
        type=int,
        default="0",
        help="""
        0->only num of pkt received per router
        1-> L0 + average clk cycles
        2-> L1 + all packet information
        3-> L2 + heatmap""",
    )
    parser.add_argument(
        "--print_output",
        type=str2bool,
        default=True,
        help="Whether to print simulator output in terminal",
    )
    parser.add_argument(
        "--sim_data_path",
        type=str,
        default="./sim_data.txt",
        help="path to save the simulation data",
    )
    args = parser.parse_args()

    main(args)
