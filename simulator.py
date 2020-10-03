import argparse
import networkx as nx
from network_map import coordinates_2_id
from network_map import coordinates_2_id_list
from router import BaseRouter as Router
from packet import BasePacket
from packet import StatPacket


def main():
    args = parser.parse_args()
    m, n = args.m, args.n
    print(args)
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
        # create the router based on algo
        router_list.append(Router(router_id, coordinates))
        router_list[router_id].set_neighbours(neighbours_coordinates, neighbours_id)

        # print(router_list[router_id].neighbours_id)  # debug
        # print(router_list[router_id].coordinates)  # debug
        # print(coordinates_2_id(coordinates, m, n))  # debug

    # debug to input packet data into [0,0] to [m-1,n-1] 
    source_id = 0
    dest_coordinates = [m-1, n-1]
    current_coordinates = [0, 0]
    pk0 = StatPacket(source_id, dest_coordinates, current_coordinates)

    router_list[0].packet_in(pk0)

    # run the simulation

    # number of cycles to simulate
    for cycle_count in range(10):
        for router_id in range(number_of_routers):
            print(cycle_count, router_id, router_list[router_id].in_buffer_empty())
            # get the output packet first
            dest_id, packet = router_list[router_id].sent_controller()
            if dest_id is not None:  # if there is packet
                status = router_list[dest_id].packet_in(packet)  # try sending
                if status is True:
                    # remove from sending router
                    router_list[router_id].out_buffer_packet_remove()
            # else do nothing, prepare for next cycle
            router_list[router_id].prepare_next_cycle()


    # collect the statistics

    # debug fixed data
    final_pkt = router_list[number_of_routers-1].local_storage[0]
    print(final_pkt.clock_cycle_taken, final_pkt.path_trace)






if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='noc simulator')
    parser.add_argument('-m', type=int, default='3',
                        help='m, number of columns ')
    parser.add_argument('-n', type=int, default='3',
                        help='n, number of rows ')
    parser.add_argument('-algo_type', type=int, default='0',
                        help='type of routers to test')
    main()