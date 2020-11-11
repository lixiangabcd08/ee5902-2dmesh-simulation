"""
functions to link the coordinates x,y and id
"""


def coordinates_2_id(coordinates, m, n):
    return coordinates[0] * n + coordinates[1]


def coordinates_2_id_list(coordinates_list, m, n):
    id_list = []
    for coordinates in coordinates_list:
        id_list.append(coordinates_2_id(coordinates, m, n))

    # id_list.sort()  # might not need it
    return id_list


def id_2_coordinates(id, m, n):
    """ m = rows, n = columns """
    return (int(id / n), int(id % n))
