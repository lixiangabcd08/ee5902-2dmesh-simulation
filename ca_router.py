"""
Module: CA Router
Desp: Congestion-Aware Routing Algorithm
version: 0.0.2

requirements: router.py

Changelog:  0.0.1 - router
            0.0.2 - bug fix for arbiter
            0.1.0 - moved set_neighbour_routers to baseRouter
"""
from router import BaseRouter


class CARouter(BaseRouter):
    def __init__(self, id, coordinates, rx_address):
        super().__init__(id, coordinates, rx_address)

    def get_busy_index(self, channel):
        """
        Func: calculate the busy index using look up table
        """
        full = 0
        half_full = 0
        for buffer in self.buffer:
            if len(buffer) == self.buffer_size:
                full += 1
            if len(buffer) >= (self.buffer_size / 2):
                half_full += 1
        c_full = True if len(self.buffer[channel]) == self.buffer_size else False
        busy_index = None
        # look up table
        if not c_full and half_full <= 2:
            busy_index = 0
        if not c_full and half_full > 2:
            busy_index = 1
        if not c_full and full > 0 and full < 2:
            busy_index = 2
        if c_full and half_full < 3:
            busy_index = 3
        if c_full and half_full >= 3:
            busy_index = 4
        if not c_full and full > 2:
            busy_index = 5
        if c_full and full > 1:
            busy_index = 6
        if c_full and full > 2:
            busy_index = 7

        return busy_index

    def arbiter(self, dest_coordinates):
        """
        Algo: Congestion Aware router
        Details: Decide on whether to go X direction or Y direction based on
        which one is free
        """
        direction = None
        ex = dest_coordinates[1] - self.coordinates[1]
        ey = dest_coordinates[0] - self.coordinates[0]

        if ex > 0:
            if ey > 0:
                if self.neighbour_routers[self.SOUTH].get_busy_index(
                    self.SOUTH
                ) >= self.neighbour_routers[self.EAST].get_busy_index(self.EAST):
                    direction = self.EAST
                else:
                    direction = self.SOUTH
            elif ey < 0:
                if self.neighbour_routers[self.NORTH].get_busy_index(
                    self.NORTH
                ) >= self.neighbour_routers[self.EAST].get_busy_index(self.EAST):
                    direction = self.EAST
                else:
                    direction = self.NORTH
            else:
                direction = self.EAST
        elif ex < 0:
            if ey > 0:
                if self.neighbour_routers[self.SOUTH].get_busy_index(
                    self.SOUTH
                ) >= self.neighbour_routers[self.WEST].get_busy_index(self.WEST):
                    direction = self.WEST
                else:
                    direction = self.SOUTH
            elif ey < 0:
                if self.neighbour_routers[self.NORTH].get_busy_index(
                    self.NORTH
                ) >= self.neighbour_routers[self.WEST].get_busy_index(self.WEST):
                    direction = self.WEST
                else:
                    direction = self.NORTH
            else:
                direction = self.WEST
        else:  # ex==0
            if ey > 0:
                direction = self.SOUTH
            elif ey < 0:
                direction = self.NORTH
            else:  # reached destination
                direction = self.SELF
        return direction
