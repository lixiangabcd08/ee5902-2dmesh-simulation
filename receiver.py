"""
Module: Receiver
Desp:   Basic receiver with buffer for stats collection
version: 0.0.1

requirements: NIL

Changelog:  0.0.1 - inital release
"""

import numpy as np


class BaseReceiver:
    def __init__(self, id):
        self.id = id
        self.number_of_packet_received = 0

    def store(self, packet):
        self.number_of_packet_received += 1

    def print_stat(self):
        if self.number_of_packet_received > 0:
            print("--------------------Router %d--------------------" % self.id)
            print(
                "number_of_packet_received =",
                self.number_of_packet_received,
            )


class PacketReceiver(BaseReceiver):
    def __init__(self, id):
        super().__init__(id)
        self.local_storage = []
        self.average_clock_taken = None

    def store(self, packet):
        super().store(packet)
        self.local_storage.append(packet)

    def is_empty(self):
        return not self.local_storage

    def print_packet_stat(self):
        clocks_taken = []
        clock_taken_by_source = {}
        if self.local_storage:
            for pkt in self.local_storage:
                # for average calculations
                clocks_taken.append(pkt.clock_cycle_taken)
                try:
                    current_list = clock_taken_by_source[pkt.source_id]
                    current_list.append(pkt.clock_cycle_taken)
                    clock_taken_by_source.update({pkt.source_id: current_list})
                except KeyError:
                    clock_taken_by_source.update(
                        {pkt.source_id: [pkt.clock_cycle_taken]}
                    )
                print(
                    "Pkt source:",
                    pkt.source_id,
                    ", Dest:",
                    pkt.dest_coordinates,
                    ", clk:",
                    pkt.clock_cycle_taken,
                    "path:",
                    pkt.path_trace,
                )
            print("average clock cycles = %.2f" % np.average(clocks_taken))
            for source in clock_taken_by_source:
                print(
                    "average clock cycles from router %d = %.2f in %d packets"
                    % (
                        source,
                        np.average(clock_taken_by_source[source]),
                        len(clock_taken_by_source[source]),
                    )
                )

    def heatmap_collection(self):
        heatmap = {}
        if self.local_storage:
            for pkt in self.local_storage:  # for every pkt
                pkt.path_trace.pop(0)  # remove the source id
                for router in pkt.path_trace:  # for every place it been to
                    # increment heatmap
                    try:
                        current_val = heatmap[router]
                        heatmap.update({router: (current_val + 1)})
                    except KeyError:
                        heatmap.update({router: 1})
        return heatmap