#!/usr/bin/env python
import sys
from PriorityQueue import PriorityQueue
#import Colorer
from Log import Log
log = Log('AStar', 'debug')


class AStar:
    '''A* is an algorithm that is used in pathfinding and graph traversal. 
    Noted for its performance and accuracy, it enjoys widespread use. It is an 
    extension of Edger Dijkstra's 1959 algorithm and achieves better 
    performance (with respect to time) by using heuristics.
    '''
    def __init__(self, debug=False, graphfile=None):
        '''When *debug* is True, the program uses the graph stored in 
        *graphfile* instead of pulling from the mysql database.
        
        Args:
            debug (bool) - is in debug mode?
            graphfile (str) - filename of debug input file
        '''
        self.debug = debug
        self.graphfile = graphfile
        log.info("AStart initiated on %s" % graphfile)
        
    def neighborNodes(self, vertex):
        '''Retrieve the neighbors of the vertex from the database and add them
        to the shortest path search.
        
        Args:
            vertex (str) - name or ID of a vertex
            
        Returns:
            (list) - a list of neighbor vertices
        '''
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
        '''Returns the estimated travel time between x and y.
        
        Args:
            x (str) - name or ID of start vertex
            y (str) - name or ID of destination vertex
            
        Returns:
            (float) - travel time between vertices x and y
        '''
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
        The heuristic function MUST use the same scale as the weight function 
        and MUST NOT over estimate the distance.
        
        Args:
            start (str) - name or ID of start vertex
            goal (str) - name or ID of destination vertex
            
        Returns:
            (float) - an estimate of the travel time between vertices x and y
        '''
        return 0
        
        
    def reconstructPath(self, came_from, current_node):
        '''Returns a list of the vertices along the shortest path.
        
        Args:
            came_from (dict) - a dict of the form {'vertex': 'node before 
								vertex in the shortest path'}
            current_node (str) - name or ID of vertex
            
        Returns:
            (list) - vertices as they appear in the shortest path
        '''
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
        Returns the cost of taking that path from start to finish.

        Args:
            path (list) - a shortest path
            
        Returns:
            (float) - the cost of traversing the shortest path
        '''
        cost = 0
        i = iter(path)
        prev = i.next()
        for element in i:
            cost += self.timeBetween(prev, element)
            prev = element
        return cost


    def shortestPath(self, start, goal, exceptions=None):
        '''Takes in the *start* node and a *goal* node and returns the shortest
        path between them as a list of nodes. Use pathCost() to find the cost
        of traversing the path.
        
        Args:
            start (str) - name or ID of start vertex
            goal (str) - name or ID of destination vertex
            exceptions (list) - list of edges, (x,y), that should be ignored
            
        Returns:
            (list) - vertices as they appear in the shortest path
        '''
        
        log.info("Start: %s, Goal: %s" % (start, goal))
        
        # The set of nodes already evaluated
        closedset = []
        # The set of tentative nodes to be evaluated.
        openset = [start]
        # The map of navigated nodes.
        came_from = {}
        # Distance from start along optimal path.
        g_score = {start: 0}
        h_score = {start: self.heuristicEstimateOfDistance(start, goal)}
        # The estimated total distance from start to goal through y.
        f_score = PriorityQueue()
        f_score.push(h_score[start], start) 
        
        while len(openset) != 0:
            # the node in openset having the lowest f_score[] value
            heur, x = f_score.pop()
            if x == goal:
                path = self.reconstructPath(came_from, goal)
                log.info("Path found of weight: %g" % self.pathCost(path))
                log.info("Path: %s" % path)
                return path
            
            try:
                openset.remove(x)
            except ValueError as e:
                log.critical("Remove %s from the openset: %s" % (str(x), e))
                raise
            
            closedset.append(x)
            for y in self.neighborNodes(x):
                if y in closedset:
                    continue
                
                if(exceptions is not None and (x,y) in exceptions):
                    costxy = float('infinity')
                else:
                    costxy = self.timeBetween(x,y)
                tentative_g_score = g_score[x] + costxy
                
                if y not in openset:
                    openset.append(y)
                    tentative_is_better = True
                elif tentative_g_score < g_score[y]:
                    tentative_is_better = True
                else:
                    tentative_is_better = False

                if tentative_is_better == True:
                    log.debug("Update node %s's weight to %g" % (y,
															tentative_g_score))
                    came_from[y] = x
                    g_score[y] = tentative_g_score
                    h_score[y] = self.heuristicEstimateOfDistance(y, goal)
                    f_score.reprioritize(g_score[y] + h_score[y], y)
        return None # Failure


    def alternateRoute(self, num, optimal_path):
        '''Find the best sub-optimal solutions. Iterate over the optimal path
        and remove one segment at time. The removed segment is not allowed
        to be used in the new path. Store the cost of the new path and return 
        the removed segment.
        
        Args:
            num (int) - number of alternative routes to find
            optimal_path (list) - optimal path
        
        Returns:
            (list) - list of tuples of form: ((cost, path), (cost2, path2), ..)
        '''
        
        # Store the paths by their weights in a priority queue. The paths with
        # the lowest cost will move to the top. At the end, pop() the queue
        # once for each desired alternative.
        minheap = PriorityQueue()
        
        start, goal = optimal_path[0], optimal_path[-1]
        
        # Don't remove the start or goal nodes
        for i in range(1, len(optimal_path) - 1):
            x = optimal_path[i-1]
            y = optimal_path[i]
            
            log.info("Look for sub-optimal solution with edge (%s, %s) removed" % (x, y))
            path = self.shortestPath(start, goal, [(x,y)])
#            path = self.shortestPath(start, goal)
            cost = self.pathCost(path)
            
            log.debug("Cost of path with edge (%s, %s) removed is %g" \
                                    % (x, y, cost))
            minheap.push(cost, path)

        alternatives = []
        for i in range(0, min(num, len(minheap))):
            cost, path = minheap.pop()
            alternatives.append((cost,path))
            log.debug("Cost of #%d sub-optimal path is %g" % (i+1, cost))
            
        return alternatives

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
    
    print "Cost: %g" % search.pathCost(path)
