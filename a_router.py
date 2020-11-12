"""
Module: A Router
Desp: Adaptive Routing Strategy
version: 0.0.2

requirements: router.py

Changelog:  0.0.1 - router
            0.0.2 - fixed the CCD checking
"""
from router import BaseRouter


class ARouter(BaseRouter):
    def __init__(self, id, coordinates, rx_address):
        super().__init__(id, coordinates, rx_address)

    ### buffer status ###

    def buffer_half_full(self, port):
        half_full = int(self.buffer_size / 2)
        # Case when pkt sent, the actual buffer size becomes (Threshold_v-1)
        if (len(self.buffer[port]) == half_full - 1) and self.pkt_sent[port]:
            return True

        # For cases when buffer_size is more than threshold, even before/after sent
        elif len(self.buffer[port]) >= half_full:
            return True
        else:
            return False

    ### router functions ###

    def direction_transform_algo(self, direction):
        """
        Transform the direction used in the simulation to the direction system
        used in the paper.
        """
        algo_direction = None
        if direction == self.NORTH:
            algo_direction = 0
        elif direction == self.EAST:
            algo_direction = 1
        elif direction == self.SOUTH:
            algo_direction = 3
        else:  # WEST
            algo_direction = 2
        return algo_direction

    def direction_transform_original(self, direction):
        """
        Transform the direction used in the paper to the direction system
        used in the simulation.
        """
        algo_direction = None
        if direction == 0:
            algo_direction = self.NORTH
        elif direction == 1:
            algo_direction = self.EAST
        elif direction == 2:
            algo_direction = self.WEST
        else:  # 3
            algo_direction = self.SOUTH
        return algo_direction

    def opposite_port_original(self, direction):
        """
        retrive the opposite port id, orignal port encoding.
        Use to reflect the view of the incoming port in get_x_index
        """
        port = None
        if direction == 1:
            port = self.SOUTH
        elif direction == 2:
            port = self.WEST
        elif direction == 3:
            port = self.NORTH
        else:  # 4
            port = self.EAST
        return port

    def get_busy_loop(self, direction):
        """
        Get whether this direction is busy or not, OR operation for CCD in that
        direction
        Recursive function
        """
        is_busy = False

        if self.buffer_half_full(self.opposite_port_original(direction)):
            is_busy = True
            return is_busy  # can early terminate since OR operation
        else:
            # continue to next router
            neighbour_router = self.neighbour_routers[direction]
            if neighbour_router is not None:
                return neighbour_router.get_busy_loop(direction)
            else:  # the last module on the line
                return is_busy

    def get_busy_index(self, direction):
        """
        Get whether this direction is busy or not, OR operation for CCD in that
        direction
        Starting func that calls Recursive function, to skip the first router
        """
        neighbour_router = self.neighbour_routers[direction]
        if neighbour_router is not None:
            return neighbour_router.get_busy_loop(direction)
        else:  # should not be sending to unconnected port
            return True

    def get_congested_loop(self, direction):
        """
        Get whether this direction is congested or not, AND operation for CCD in
        that direction
        Recursive function
        """
        if self.buffer_full(self.opposite_port_original(direction)):
            is_congested = True
        else:
            is_congested = False
        neighbour_router = self.neighbour_routers[direction]
        if neighbour_router is not None:
            return is_congested & neighbour_router.get_congested_loop(direction)
        else:  # the last module on the line
            return is_congested

    def get_congested_index(self, direction):
        """
        Get whether this direction is congested or not, AND operation for CCD in
        that direction
        Starting func that calls Recursive function, to skip the first router
        """
        neighbour_router = self.neighbour_routers[direction]
        if neighbour_router is not None:
            return neighbour_router.get_congested_loop(direction)
        else:  # should not be sending to unconnected port
            return True

    def arbiter(self, dest_coordinates):
        """
        Algo: Adaptive Routing
        """
        direction = super().arbiter(dest_coordinates)
        direction_old = direction
        if direction != self.SELF:
            # change the old direction index to the direction in the paper
            algo_direction = self.direction_transform_algo(direction)
            # follow the logical diagram on figure 2 on the paper
            s1 = [1, 0, 0, 1][algo_direction]
            s2 = self.get_multiplexer(s1, "busy")
            s3 = self.get_multiplexer(self.inverse(s1), "busy")
            s4 = s2 | (not s3)
            s5 = not (s2 & s3)
            s6 = [s1, self.inverse(s1)][int(s4)]
            s7 = [self.inverse(algo_direction), s6][int(s5)]
            result = [algo_direction, s7][
                int(self.get_multiplexer(algo_direction, "congested"))
            ]
            # transfer back to the original direction system
            direction = self.direction_transform_original(result)

            # special check by us to prevent packet sending to unconnected port
            if self.neighbours_id[direction] is None:
                direction = direction_old

        return direction

    def inverse(self, a):
        # ~ in default invert to 4 bits, thus need to change to 2 bits operation
        return ~a & 0b0011

    def get_multiplexer(self, selector, line):
        if selector == 0:
            direction = self.NORTH
        elif selector == 1:
            direction = self.EAST
        elif selector == 2:
            direction = self.WEST
        elif selector == 3:
            direction = self.SOUTH

        if line == "busy":
            return self.get_busy_index(direction)
        else:
            # if(self.get_congested_index(direction)):
            #     print("yes")
            return self.get_congested_index(direction)

    def scheduler(self):
        """
        Func: determine which port to serve
        algo: Round Robin and First Come First Serve
        """
        serving_port = (self.current_serving_port + 1) % 5
        while (
            len(self.buffer[serving_port]) == 0
            and serving_port != self.current_serving_port
        ):
            # try the next port if buffer is empty
            # exit if all ports are empty
            serving_port = (serving_port + 1) % 5
        self.current_serving_port = serving_port
        return self.current_serving_port