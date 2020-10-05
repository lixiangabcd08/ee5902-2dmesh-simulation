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
