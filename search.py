'''All the algorithms to calculate the shortest route

'''
from copy import deepcopy
from itertools import permutations

def nearest_neighbour(matrix):
    '''Calculate the shortest route using a greedy search

    Parameters:
    matrix             Distance matrix
    '''

    # Intialise varibles and fill them with dud values
    shortest = float("inf")
    best_route = None

    # Peform the nearest neighbour algorithm starting from every row
    for row_index in range(len(matrix)):
        current_row = row_index
        temp_matrix = deepcopy(matrix)

        # 0 distance routes aren't allowed
        for row in range(len(temp_matrix)):
            temp_matrix[row][row] = float("inf")

        # Values for the current run
        test_time = 0
        route = [current_row]

        # Nearest neighbour algorithm
        while len(route) != len(matrix):
            lowest = min(temp_matrix[current_row])
            index  = temp_matrix[current_row].index(lowest)
            test_time += lowest
            route.append(index)

            #Ensures that a node is never visited more than once
            for i in range(len(temp_matrix)):
                temp_matrix[i][current_row] = float("inf")
                temp_matrix[current_row][i] = float("inf")
            
            current_row = index

        # The best route is saved
        if shortest > test_time:
            shortest = test_time
            best_route = route
            
    return shortest, best_route

def brute_force(matrix):
    '''Iterate though all possible routes to find the best one

    Parameters:
    matrix             Distance matrix
    '''

    # Intialise varibles and fill them with dud values
    shortest = float("inf")
    best_route = None

    # Iterate though all permutations of route
    for order in permutations(range(0,len(matrix))):
        total_time = 0
        for index, node in enumerate(order):
            if index != len(order)-1:
                total_time += matrix[node][order[index+1]]

        # The best route is saved
        if total_time < shortest:
            shortest = total_time
            best_route = order

    return shortest, best_route
