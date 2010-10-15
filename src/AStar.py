#!/usr/bin/env python
import sys
from PriorityQueue import PriorityQueue

from Log import Log
log = Log('AStar', 'info')

class AStar:
    '''A* is an algorithm that is used in pathfinding and graph traversal. Noted
    for its performance and accuracy, it enjoys widespread use. It is an 
    extension of Edsger Dijkstra's 1959 algorithm and achieves better 
    performance (with respect to time) by using heuristics.'''
    
    def __init__(self, debug=False, graphfile=None):
        '''When *debug* is True, the program uses the graph stored in *graphfile*
        instead of pulling from the mysql database'''
        self.debug = debug
        self.graphfile = graphfile
        log.info("AStart initiated on %s" % graphfile)
        
    def neighborNodes(self, vertex):
        '''Retrieve the neighbors of the vertex from the database and add them
        to the shortest path search'''
        neighbors = []

        if not self.debug:
            # Get the neighbors via an SQL query
            return
        else:
            f = open(self.graphfile, 'r')
            for line in f:
                start, end, weight = line.split(',')
                if start == vertex:
                    neighbors.append(end.strip())
            log.debug("Neighbors of %s are %s" % (vertex, neighbors))
            return neighbors


    def timeBetween(self, x, y):
        '''Returns the estimated travel time between x and y'''
        if not self.debug:
            # average travel time between x and y for this time period
            return
        else:
            f = open(self.graphfile, 'r')
            for line in f:
                start, end, weight = line.split(',')
                if start.strip() == x and end.strip() == y:
                    return int(weight)
            return float('infinity')
        
        
    def heuristicEstimateOfDistance(self, start, goal):
        '''Guide the A* search. Equivalent to Dijkstra's if it returns only 0.
        The heuristic function MUST NOT over estimate the distance.'''
        return 0
        
        
    def reconstructPath(self, came_from, current_node):
        '''Returns a list of the vertices along the shortest path'''
        trail = []
        while True:
            trail.insert(0,current_node)
            try:
                current_node = came_from[current_node]
            except KeyError:
                # break out of loop when we reach the root node
                break
        return trail
    
    
    def pathCost(self, path):
        '''Takes in the path as a list such as that returned by shortestPath(). 
        Returns the cost of taking that path from start to finish.'''
        cost = 0
        i = iter(path)
        prev = i.next()
        for element in i:
            cost += self.timeBetween(prev, element)
            prev = element
        return cost
        
        
    def shortestPath(self, start, goal):
        '''Takes in the *start* node and a *goal* node and returns the shortest
        path between them as a list of nodes. Use pathCost() to find the cost
        of traversing the path.'''
        
        log.info("Start: %s, Goal: %s" % (start, goal))
        
        # The set of nodes already evaluated
        closedset = []
        # The set of tentative nodes to be evaluated.
        openset = [start]
        came_from = {}                      # The map of navigated nodes.
        g_score = {start: 0}             # Distance from start along optimal path.
        h_score = {start: self.heuristicEstimateOfDistance(start, goal)}
        #f_score = []   # Estimated total distance from start to goal through y.
        #heapq.heappush(f_score, (h_score[start], start))
        f_score = PriorityQueue()
        f_score.push(h_score[start], start)
        
        while len(openset) != 0:
            heur, x = f_score.pop()   # the node in openset having the lowest f_score[] value
            if x == goal:
                path = self.reconstructPath(came_from, goal)
                log.info("Path found of weight: %d" % self.pathCost(path))
                log.info("Path: %s" % path)
                return path
            
            openset.remove(x)
            closedset.append(x)
            for y in self.neighborNodes(x):
                if y in closedset:
                    continue
                tentative_g_score = g_score[x] + self.timeBetween(x,y)
                
                if y not in openset:
                    openset.append(y) # add y to openset
                    tentative_is_better = True
                elif tentative_g_score < g_score[y]:
                    tentative_is_better = True
                else:
                    tentative_is_better = False

                if tentative_is_better == True:
                    log.debug("Update node %s's weight to %d" % (y, tentative_g_score))
                    came_from[y] = x
                    g_score[y] = tentative_g_score
                    h_score[y] = self.heuristicEstimateOfDistance(y, goal)
                    f_score.reprioritize(g_score[y] + h_score[y], y)
        return None # Failure

if __name__ == "__main__":
    if len(sys.argv) == 3:
        start = sys.argv[1]
        end = sys.argv[2]
        graphfile = 'data/graph1.txt'
    elif len(sys.argv) == 4:
        graphfile = sys.argv[1]
        start = sys.argv[2]
        end = sys.argv[3]
    else:
        start = 'A'
        end = 'D'
        graphfile = 'data/graph1.txt'
        
    search = AStar(True, graphfile)
    print "The shortest Path from " + start + " to " + end + " is:"
    path = search.shortestPath(start, end)
    for node in path[:-1]:
        print str(node) + " ->",
    print end
    
    print "Cost: %d" % search.pathCost(path)
