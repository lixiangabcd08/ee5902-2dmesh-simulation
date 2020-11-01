import argparse
import networkx as nx
import time

from network_map import coordinates_2_id
from network_map import coordinates_2_id_list

from receiver import PacketReceiver as rx

from router import BaseRouter as Router
from elra_router import ELRARouter
from ca_router import CARouter
from a_router import ARouter
from modxy_router import modXYRouter

from packet import BasePacket
from packet import StatPacket
from packet_generator import Generator
from packet_generator import RandomGenerator
from packet_generator import ConstGenerator


def main():
    args = parser.parse_args()
    m, n = args.m, args.n
    num_of_testing_pkts = args.num_of_testing_pkts
    algo_type = args.algo_type
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
        if algo_type == 4:
            router_list.append(CARouter(router_id, coordinates, rx_address))
        elif (algo_type == 3):  
            router_list.append(ELRARouter(router_id, coordinates, rx_address))
        elif (algo_type == 2): 
            router_list.append(ARouter(router_id, coordinates, rx_address))
        elif (algo_type == 1):
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

    # init the packet generator
    generator0 = Generator(m, n)
    generator1 = RandomGenerator(m, n, max_pkt=num_of_testing_pkts)
    generator2 = ConstGenerator(m, n, sir=10, max_pkt=50)

    ### debug to input packet data
    current_clock_cycle = 0
    source_id = 0
    des_point = [2,2]
    ini_point = [0,0]
    pk0 = StatPacket(source_id,des_point,ini_point, current_clock_cycle)
    pk1 = StatPacket(6,[0,2],[2,0], current_clock_cycle)  # 6-2

    # run the simulation

    # number of cycles to simulate for single packet testing
    for current_clock_cycle in range(number_of_routers * 5):
        """ set up the testing packets in first cycle """
        if current_clock_cycle == 0:
            # packets = generator1.generate_list(current_clock_cycle)
            # for packet in packets:
            #     router_list[packet.source_id].packet_in(packet, 0)
            packet = generator0.generate_single(current_clock_cycle) # for debugging
            router_list[pk0.source_id].packet_in(pk0, 0)  #for debugging
            router_list[pk1.source_id].packet_in(pk1, 0)

        # if (current_clock_cycle < 3):  # for stress testing, can remove
        #     pk2 = StatPacket(2,[2,2],[0,2], current_clock_cycle)  # 2-8
        #     pk3 = StatPacket(5,[2,2],[1,2], current_clock_cycle)  # 5-8
        #     pk4 = StatPacket(4,[2,2],[1,1], current_clock_cycle)  # 4-8
        #     router_list[pk2.source_id].packet_in(pk2, 0)
        #     router_list[pk3.source_id].packet_in(pk3, 0)
        #     router_list[pk4.source_id].packet_in(pk4, 0)
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

        if current_clock_cycle % 100 == 0:  # for debugging
            print("current_clock_cycle = ", current_clock_cycle)

        if empty_flag:  # all routers has cleared their buffer
            print("ending cycle = ", current_clock_cycle)
            break

    print("--- time taken: %s seconds ---" % (time.time() - start_time))  # time
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
        "--num_of_testing_pkts", type=int, default="5", help="num of pkts to send"
    )
    parser.add_argument(
        "--testing_mode",
        type=int,
        default="0",
        help="0->single pkt test, 1->multiple pkt test",
    )
    start_time = time.time()
    main()