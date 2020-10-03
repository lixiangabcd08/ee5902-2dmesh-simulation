'''
aim is to link the x,y to the id
'''


def coordinates_2_id(coordinates, m, n):
    return coordinates[0]*m + coordinates[1]


def coordinates_2_id_list(coordinates_list, m, n):
    id_list = []
    for coordinates in coordinates_list:
        id_list.append(coordinates_2_id(coordinates, m, n))

    id_list.sort()  # might not need it
    return id_list