"""
Module: Receiver
Desp:   Basic receiver with buffer for stats collection
version: 0.0.2

requirements: NIL

Changelog:  0.0.1 - inital release
            0.0.2 - added more print stat functions
"""

import numpy as np


class BaseReceiver:
    def __init__(self, id):
        self.id = id
        self.number_of_packet_received = 0

    def store(self, packet):
        self.number_of_packet_received += 1

    def print_stat(self, verbose, fout, print_output):
        if self.number_of_packet_received > 0:
            string = "--------------------Router %d--------------------\n" % self.id
            string += "number_of_packet_received =%d\n" % self.number_of_packet_received
            if print_output:
                print(string, end="")
            fout.write(string)


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

    def print_stat(self, verbose, fout, print_output):
        super().print_stat(verbose, fout, print_output)
        self.print_packet_stat(verbose, fout, print_output)

    def print_packet_stat(self, verbose, fout, print_output):
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
                if verbose >= 2:
                    pkt_string = "Pkt source: %2d, Dest: %s, clk:%4d, path:%s\n" % (
                        pkt.source_id,
                        str(pkt.dest_coordinates),
                        pkt.clock_cycle_taken,
                        str(pkt.path_trace),
                    )
                    fout.write(pkt_string)
                    if print_output:
                        print(pkt_string, end="")

            if verbose >= 1:
                avg_string = "average clk cycles = %.2f\n" % np.average(clocks_taken)
                for source in clock_taken_by_source:
                    avg_string += (
                        "average clk cycles from router %d = %.2f in %d packets\n"
                        % (
                            source,
                            np.average(clock_taken_by_source[source]),
                            len(clock_taken_by_source[source]),
                        )
                    )
                if print_output:
                    print(avg_string, end="")
                fout.write(avg_string)

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