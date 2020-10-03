import argparse
import networkx as nx
from network_map import coordinates_2_id
from network_map import coordinates_2_id_list
from router import Router


def main():
    args = parser.parse_args()
    m, n = args.m, args.n
    print(m, n)
    # create the network mapping
    noc_map = nx.grid_2d_graph(m, n)
    noc_map_nodes = list(noc_map.nodes)
    # print(list(noc_map.nodes))  # debug
    # print(list(noc_map.edges))  # debug

    number_of_routers = m * n
    router_list = []

    # create the routers and map them
    for router_id in range(number_of_routers):
        print(router_id)
        # get the parameters
        coordinates = noc_map_nodes[router_id]
        neighbours_coordinates = list(noc_map.adj[coordinates])
        neighbours_id = coordinates_2_id_list(neighbours_coordinates, m, n)
        router_list.append(Router(router_id, coordinates, neighbours_id))

        # print(router_list[router_id].neighbours_id)  # debug
        # print(router_list[router_id].coordinates)  # debug
        # print(coordinates_2_id(coordinates, m, n))  # debug


    # run the simulation

    # collect the statistics 





if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='noc simulator')
    parser.add_argument('-m', type=int, default='2',
                        help='m, number of columns ')
    parser.add_argument('-n', type=int, default='2',
                        help='n, number of rows ')
    parser.add_argument('-algo_type', type=int, default='0',
                        help='type of routers to test')
    main()