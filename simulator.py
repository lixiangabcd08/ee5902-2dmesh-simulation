import argparse
import networkx as nx
from network_map import coordinates_2_id
from network_map import coordinates_2_id_list

from receiver import PacketReceiver as rx

from router import BaseRouter as Router
from packet import BasePacket
from packet import StatPacket
from packet_generator import Generator
from packet_generator import RandomGenerator
from packet_generator import ConstGenerator


def main():
    args = parser.parse_args()
    m, n = args.m, args.n
    num_of_testing_pkts = args.num_of_testing_pkts
    print(args)
    # create the network mapping
    noc_map = nx.grid_2d_graph(m, n)
    noc_map_nodes = list(noc_map.nodes)
    # print(list(noc_map.nodes))  # debug
    # print(list(noc_map.edges))  # debug

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
        router_list.append(Router(router_id, coordinates, rx_address))
        router_list[router_id].set_neighbours(neighbours_coordinates, neighbours_id)

        # print(router_list[router_id].neighbours_id)  # debug
        # print(router_list[router_id].coordinates)  # debug
        # print(coordinates_2_id(coordinates, m, n))  # debug

    # init the packet generator
    generator1 = RandomGenerator(m, n, max_pkt=50)
    generator2 = ConstGenerator(m, n, sir=10, max_pkt=50)

    ### debug to input packet data
    # current_clock_cycle = 0
    # source_id = 0
    # des_point = [1,1]
    # ini_point = [0,0]
    # pk0 = StatPacket(source_id,des_point,ini_point, current_clock_cycle)

    # run the simulation

    # number of cycles to simulate
    for current_clock_cycle in range(number_of_routers * 10):
        """ set up the testing packets in first cycle """
        if current_clock_cycle == 0:
            packets = generator1.generate_list(current_clock_cycle)
            for pk0 in packets:
                router_list[pk0.source_id].packet_in(pk0, 0)

        empty_flag = True

        """ This is to run the routers for 1 cycle to send out pkt """
        for router_id in range(number_of_routers):
            # check if the router is empty
            is_empty = router_list[router_id].empty_buffers()
            if not is_empty:
                empty_flag = False

            # print("current ", current_clock_cycle, router_id)  # debug
            # router_list[router_id].debug_empty_in_buffer()  # debug
            # get the output packet first
            dest_id, packet = router_list[router_id].sent_controller_pre(
                current_clock_cycle
            )
            if dest_id is not None:  # if there is packet
                status = router_list[dest_id].receive_check(
                    packet, router_id
                )  # try sending
                if status is True:
                    # remove from sending router
                    router_list[router_id].sent_controller_post()

        """
        Why only move the packet after all routers send their packets?
        Ans: during the same cycle, it is not possible to write in and pop out 
        the same FIFO. E.g. When the FIFO (includes buffer in/out) is full, if
        buffer out has move the data in that cycle, software wise it is not full
        anymore, but hardware wise it is impossible to write into that buffer in
        that clock cycle, so it is still full until the next cycle. By doing
        the internal buffer moving after all routers are done, it is to ensure
        the software follows how hardware moves.
        """
        # loop 2nd time to move the buffers in the router
        for router_id in range(number_of_routers):
            router_list[router_id].prepare_next_cycle()

        if current_clock_cycle % 100 == 0:  # for debugging
            print("current_clock_cycle = ", current_clock_cycle)

        if empty_flag:  # all routers has cleared their buffer
            print("ending cycle = ", current_clock_cycle)
            break

    # collect the statistics
    for router_id in range(number_of_routers):
        receiver_list[router_id].print_stat()
        receiver_list[router_id].print_packet_stat()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="noc simulator")
    parser.add_argument("--m", type=int, default="3", help="m, number of columns ")
    parser.add_argument("--n", type=int, default="3", help="n, number of rows ")
    parser.add_argument(
        "--algo_type", type=int, default="0", help="type of routers to test"
    )
    parser.add_argument(
        "--num_of_testing_pkts", type=int, default="5", help="type of pkts to send"
    )
    parser.add_argument(
        "--testing_mode",
        type=int,
        default="0",
        help="0->single pkt test, 1->multiple pkt test",
    )
    main()