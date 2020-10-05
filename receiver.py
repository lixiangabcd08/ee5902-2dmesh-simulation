"""
Module: Receiver
Desp:   Basic receiver with buffer for stats collection
version: 0.0.1

requirements: NIL

Changelog:  0.0.1 - inital release
"""


class BaseReceiver:
    def __init__(self, id):
        self.id = id
        self.number_of_packet_received = 0

    def store(self, packet):
        self.number_of_packet_received += 1

    def print_stat(self):
        print(self.id, ": number_of_packet_received =", self.number_of_packet_received)


class PacketReceiver(BaseReceiver):
    def __init__(self, id):
        super().__init__(id)
        self.local_storage = []

    def store(self, packet):
        super().store(packet)
        self.local_storage.append(packet)

    def is_empty(self):
        return not self.local_storage

    def print_packet_stat(self):
        if self.local_storage:
            for pkt in self.local_storage:
                print(
                    "Source: ", pkt.source_id, "; Destination: ",
                    pkt.dest_coordinates
                )
                print(pkt.clock_cycle_taken, pkt.path_trace)