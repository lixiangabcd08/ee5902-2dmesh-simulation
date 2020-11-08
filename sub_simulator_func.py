"""
This contains some common functions used by sub simulators
"""
import numpy as np

from network_map import coordinates_2_id
from network_map import coordinates_2_id_list
from network_map import id_2_coordinates

from receiver import PacketReceiver as rx

from router import BaseRouter as Router
from elra_router import ELRARouter
from ca_router import CARouter
from a_router import ARouter
from modxy_router import modXYRouter


def create_router_list(args, noc_map, noc_map_nodes):
    m, n = args.m, args.n
    algo_type = args.algo_type
    number_of_routers = m * n

    router_list = []
    receiver_list = []
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
        elif algo_type == 3:
            router_list.append(ELRARouter(router_id, coordinates, rx_address))
        elif algo_type == 2:
            router_list.append(ARouter(router_id, coordinates, rx_address))
        elif algo_type == 1:
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

    return router_list, receiver_list
