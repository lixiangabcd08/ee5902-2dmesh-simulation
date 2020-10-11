from packet import StatPacket
from network_map import coordinates_2_id
import random

### This generator generate random package
class Generator():
    def __init__(self, m, n):
        self.m = m
        self.n = n

    # generate a single packet
    def generate_single(self, current_clock_cycle):
        has_two_points = False
        while not has_two_points:
            ini_point = self.gen_random_point()
            des_point = self.gen_random_point()
            if ini_point != des_point: # make sure the two points are not identical
                has_two_points = True
        source_id = coordinates_2_id(ini_point,self.m,self.n)
        return StatPacket(source_id,des_point,ini_point, current_clock_cycle)

    def gen_random_point(self):
        coordinate_x = random.randint(0,self.m-1)
        coordinate_y = random.randint(0,self.n-1)
        return (coordinate_x, coordinate_y)


class RandomGenerator(Generator):
    def __init__(self, m, n, max_pkt=50):
        super().__init__(m,n)
        self.max_pkt = max_pkt

    def generate_list(self,current_clock_cycle):
        random_list = []
        no_pkt = random.randint(0,self.max_pkt)
        for _ in range(no_pkt):
            random_list.append(self.generate_single(current_clock_cycle))
        return random_list


class ConstGenerator(Generator):
    def __init__(self, m, n, sir=20, max_pkt=50):
        super().__init__(m,n)
        self.max_pkt = max_pkt
        self.sir = sir
    
    def generate_list(self, current_clock_cycle):
        # return single packet if not the peak
        # return max no of packets if the peak
        random_list = []
        if not current_clock_cycle%self.sir:
            return [self.generate_single(current_clock_cycle)]
        else:
            for _ in range(self.max_pkt):
                random_list.append(self.generate_single(current_clock_cycle))
            return random_list