#!/usr/bin/env python
import cProfile
import sys
import os
from PriorityQueue import PriorityQueue
from Database import Database, name2cord
#import Colorer
from Log import Log
log = Log('Pathfinding', 'debug', fileout=True)


#time_periods = 
def writeResultsToFile(L):
    '''A debug function'''
    log.info("Writing partial results to file")
    f = open("results.kml", "w")
    f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
    f.write('<kml xmlns="http://www.opengis.net/kml/2.2">\n')
    f.write('<Document>\n')
    for node in L:
        f.write(' <Placemark>\n')
        f.write(' <name>%s</name>\n' % node)
        f.write(' <Point>\n')
        f.write(' <coordinates>%s,%s,0</coordinates>\n' % (name2cord(node)[1],name2cord(node)[0]))
        f.write(' </Point>\n')
        f.write(' </Placemark>\n')

    f.write('</Document>\n')
    f.write('</kml>\n')

def weightedAvg2(mylist, current_time_period):
    '''Mylist is a list of tuples of form: (number, time period). The list
    entries are sorted by time period with the entires in the current time
    period receiving the most weight. Newer entries receive higher weights than
    older entries.'''

    # Separate out all entries in the current time period
    curr = []
    for entry in mylist:
        number, period = entry[0], entry[1]
        if(period == current_time_period):
            curr.append(entry)
    # Sort set by datel
    curr.sort()
    # Sort remaining entries by date
    mylist.sort()

    # Append remaining entries after current time period entries
    curr.append(mylist)

    return weightedAvg(mylist)


def weightedAvg(mylist):
    '''Returns the weighted moving average of the numbers in the list.'''
    n = len(mylist)
    wma = 0

    for i in range(0, n):
        wma += (n - i) * mylist[i]
    wma /= (n * (n + 1))/2.0

    return wma


class Pathfinding:
    '''The Pathfinding class contains functions related to finding routes in
    a network graph.
    '''
    
    def __init__(self, debug=False, graphfile=None):
        '''When ``debug`` is ``True``, the program uses the graph stored in 
        ``graphfile`` instead of pulling from the mysql database.
        '''
        self.debug = debug
        if graphfile is not None:
            log.info("AStart initiated on %s" % graphfile)
            
        if debug:
            if not os.path.exists(graphfile):
                print "Could not find '%s'" % graphfile
                
            self.graph = {}
            f = open(graphfile, 'r')
            for line in f:
                start, end, weight = line.split(',')
                if not self.graph.has_key(start):
                    self.graph[start] = []
                self.graph[start].append((end.strip(), int(weight.strip())))
        else:
            self.db = Database()

    def shortestPath(self, start, goal, exceptions=None):
        '''Returns the shortest path from the ``start`` vertex to the ``goal``
        vertex as a list of nodes. The path will avoid using any vertex from 
        the ``exceptions`` list, which could be used to find alternate routes
        or avoid certain roads such as highways. :func:`shortestPath` uses the
        best available pathfinding algorithm and should always be used instead
        of directly invoking such functions as :func:`aStarPath`, 
        :func:`dijkstra`, or :func:`dijkstraBi`.
        
        Use :func:`pathCost()` to find the cost of traversing the path.
            
        Some examples::
        
            search = Pathfinding()
            path = search.shortestPath("28.241378,-81.206989", "28.700301,-81.529274")
            # returns ['28.6118857,-81.196140', '28.5798874,-81.1783859', '28.5799816,-81.175521']
        '''
        log.info("Start: {}, Goal: {}".format(start, goal))
        #path = self.aStarPath(start, goal, exceptions)
        path = self.dijkstraBi(start, goal, exceptions)
        #path = self.dijkstra(start, goal, exceptions)
        
        log.info("Path: %s" % path)
        return path
        
        
    def aStarPath(self, start, goal, exceptions=None):
        '''A* is an algorithm that is used in pathfinding and graph traversal. 
        Noted for its performance and accuracy, it enjoys widespread use. It
        is an extension of Edger Dijkstra's 1959 algorithm and achieves better 
        performance (with respect to time) by using heuristics.
    
        Takes in the ``start`` node and a ``goal`` node and returns the
        shortest path between them as a list of nodes. Use pathCost() to find
        the cost of traversing the path.
        
        .. note::
            Does not currently use the heuristic function, making it less
            efficient than the bi-directional Dijkstra's algorithm used in 
            :func:`dijkstraBi`.
            
        .. deprecated:: 0.5
            Use :func:`shortestPath` instead.
            
        .. seealso::
            :func:`dijkstra`, :func:`dijkstraBi`
        '''
        
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
                #log.info("Path found of weight: %g" % self.pathCost(path))
                #log.info("Path: %s" % path)
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
                    #log.debug("Update node %s's weight to %g" % (y,
															#tentative_g_score))
                    came_from[y] = x
                    g_score[y] = tentative_g_score
                    h_score[y] = self.heuristicEstimateOfDistance(y, goal)
                    f_score.reprioritize(g_score[y] + h_score[y], y)
        return None # Failure


    def heuristicEstimateOfDistance(self, start, goal):
        '''Guide the A* search. Equivalent to Dijkstra's if it returns only 0.
        The heuristic function MUST use the same scale as the weight function 
        and MUST NOT over estimate the distance. 
        
        .. warning:: This function is not completed. It always returns 0.
        '''
        return 0
        
        
    def dijkstra(self, start, goal, exceptions=None):
        '''Dijkstra's algorithm, conceived by Dutch computer scientist Edsger 
        Dijkstra in 1956 and published in 1959, is a graph search algorithm 
        that solves the single-source shortest path problem for a graph with
        nonnegative edge path costs, producing a shortest path tree.
        
        .. note::
            Unmodified, Dijkstra's algorithm searches outward in a circle from
            the start node until it reaches the goal. It is therefore slower
            than other methods like A* or Bi-directional Dijkstra's. The
            algorithm is included here for performance comparision against
            other algorithms only.
        
        .. seealso::
            :func:`aStarPath`, :func:`dijkstraBi`
        '''
        dist = {}       # dictionary of final distances
        
        came_from = {} # dictionary of predecessors
        
        # nodes not yet found
        queue = PriorityQueue()

        # The set of nodes already evaluated
        closedset = []
        
        queue.push(0, start)
        
        while len(queue) > 0:
            #log.debug("queue: " + str(queue))
            weight, x = queue.pop()
            dist[x] = weight
            if x == goal:
                #log.debug("came_from: " + str(came_from))
                path = self.reconstructPath(came_from, goal)
                #log.info("Path: %s" % path)
                return path
                        
            closedset.append(x)
            
            for y in self.neighborNodes(x):
                if y in closedset:
                    continue                
                if(exceptions is not None and y in exceptions):
                    continue

                costxy = self.timeBetween(x,y)
                
                if not dist.has_key(y) or dist[x] + costxy < dist[y]:
                    dist[y] = dist[x] + costxy
                    queue.reprioritize(dist[y], y)
                    came_from[y] = x
                    #log.debug("Update node %s's weight to %g" % (y, dist[y]))

        return None
                


    def dijkstraBi(self, start, goal, exceptions=None):
        '''Bi-Directional Dijkstra's algorithm. The search begins at the
        ``start`` node and at the ``goal`` node simultaneously. The search area
        expands radially outward from both ends until the two meet in the
        middle. In most cases this reduces the number of vertices which must
        be checked by half.
        
        .. image:: dijkstra.png
        .. image:: dijkstra-bidirectional.png
        
        Search area of Dijkstra's algorithm (left) vs search area of 
        bi-directional Dijkstra's algorithm (right).
            
        .. seealso::
            :func:`aStarPath`, :func:`dijkstra`
        '''
        dist_f = {}       # dictionary of final distances
        dist_b = {}       # dictionary of final distances
        
        came_from_f = {} # dictionary of predecessors
        came_from_b = {} # dictionary of predecessors
        
        # nodes not yet found
        forward = PriorityQueue()
        backward = PriorityQueue()

        # The set of nodes already evaluated
        closedset_forward = []
        closedset_backward = []
        
        forward.push(0, start)
        backward.push(0, goal)
        
        while len(forward) + len(backward) > 0:
            if len(forward) > 0:
                done, stop = self.__dijkstraBiIter(start, goal, exceptions, 
                                        dist_f, came_from_f, forward, 
                                        closedset_forward, closedset_backward)

            if not done and len(backward) > 0:
                done, stop = self.__dijkstraBiIter(goal, start, exceptions,
                                        dist_b, came_from_b, backward, 
                                        closedset_backward, closedset_forward)
        
            if done:
                #log.debug("came_from_f: " + str(came_from_f))
                #log.debug("came_from_b: " + str(came_from_b))
                
                pathf = self.reconstructPath(came_from_f, stop)
                #log.info("PathF: %s" % pathf)
                
                pathb = self.reconstructPath(came_from_b, stop)
                pathb.reverse()
                #log.info("PathB: %s" % pathb)
                
                return pathf + pathb[1:]
        return None
        
    def __dijkstraBiIter(self, start, goal, exceptions, dist, came_from, queue,
                            closedset, revclosedset):
        ''' Run a single iteration of dijkstra's algorithm. 
        returns:
            (bool, string) - tuple of form: (is search over?, vertex stopped on)
        '''
        try:
            log.debug("queue: " + str(queue))
            weight, x = queue.pop()
            dist[x] = weight
            if x == goal:
                log.info("Found the goal")
                return True, x
            elif x in revclosedset:
                log.info("Meet in the middle: Node " + str(x))
                return True, x
                
            closedset.append(x)
            
            for y in self.neighborNodes(x):
                if y in closedset:
                    continue                
                if(exceptions is not None and y in exceptions):
                    continue
                    

                costxy = self.timeBetween(x,y)
                
                if not dist.has_key(y) or dist[x] + costxy < dist[y]:
                    dist[y] = dist[x] + costxy
                    queue.reprioritize(dist[y], y)
                    came_from[y] = x
                    log.debug("Update node %s's weight to %g" % (y, dist[y]))
                    
            return False, None
        except KeyboardInterrupt:
            writeResultsToFile(closedset)


    def alternateRoute(self, num, optimal_path):
        '''To obtain a ranked list of less-than-optimal solutions, the optimal 
        solution must first calculated. This optimal solution is passed in as
        ``optimal_path``. A single edge appearing in the optimal solution is 
        removed from the graph, and the optimum solution to this new graph is 
        calculated. Each edge of the original solution is suppressed in turn
        and a new shortest-path calculated. The secondary solutions are then
        ranked and the ``num`` best sub-optimal solutions are returned. If 
        less than ``num`` solutions exist for the given graph, less than
        ``num`` solutions will be returned. The results are a list of tuples
        of form: 
        ``((cost, path), (cost2, path2), ...)``
        
        An example of finding alternate routes::
        
            search = Pathfinding()
            # find optimal route
            optimal_path = search.shortestPath("A", "E")
            # returns ["A", "C", "E"]
            cost = search.pathCost(optimal_path)
            # returns 3
            alt_paths = search.alternateRoute(2, optimal_path)
            # returns ((4, ["A", "B", "D", "E"]), (4, ["A", "B", "F", "E"]))
        '''
        
        # Store the paths by their weights in a priority queue. The paths with
        # the lowest cost will move to the top. At the end, pop() the queue
        # once for each desired alternative.
        minheap = PriorityQueue()
        
        start, goal = optimal_path[0], optimal_path[-1]
        
        # Don't remove the start or goal nodes
        for i in range(1, len(optimal_path) - 1):
            y = optimal_path[i]
            
            log.info("Look for sub-optimal solution with vertex {} removed".\
                    format(y))
            path = self.shortestPath(start, goal, [y])
            #path = self.shortestPath(start, goal)
            cost = self.pathCost(path)
            
            log.debug("Cost of path with vertex %s removed is %g" \
                                    % (y, cost))
            minheap.push(cost, path)

        alternatives = []
        for i in range(0, min(num, len(minheap))):
            cost, path = minheap.pop()
            alternatives.append((cost,path))
            log.debug("Cost of #%d sub-optimal path is %g" % (i+1, cost))
            
        return alternatives


    def neighborNodes(self, vertex):
        '''Retrieve the neighbors of the vertex from the database and returns
        them as a list of vertices. If ``Pathfinding`` was started in debug
        mode the neighbors will be pulled from a file instead.
        '''
        neighbors = []

        if not self.debug:
            # Get the neighbors via an SQL query
            #neighbors = self.db.getNeighborsFromCoord(name2cord(vertex)[0], name2cord(vertex)[1])
            neighbors = self.db.getNeighbors(vertex)
            log.debug("Neighbors of %s are %s" % (vertex, neighbors))
            return neighbors
        else:
            try:
                for edge in self.graph[vertex]:
                    neighbors.append(edge[0])
            except KeyError:
                pass
                
            log.debug("Neighbors of %s are %s" % (vertex, neighbors))
            return neighbors


    def timeBetween(self, x, y):
        '''Returns the estimated travel time between ``x`` and ``y``. This is
        exactly equivalent to the weight of the edge ``(x,y)``.

        The weight of travelled road segments is determined by a weighted
        moving average. Travel time for road segments for which we have no data
        is calculated by assuming the travel speed will be 30 mph (which is the
        speed limit for business and residential streets in Florida).
        '''
        if not self.debug:
            # average travel time between x and y for this time period
            return self.db.getTravelTime(x, y)
        else:
            try:
                for edge in self.graph[x]:
                    if edge[0] == y:
                        return edge[1]
            except KeyError:
                pass
                
            try:
                for edge in self.graph[y]:
                    if edge[0] == y:
                        return edge[1]
            except KeyError:
                pass
                
            return float('infinity')
        
        
    def reconstructPath(self, came_from, goal):
        '''Returns a list of the vertices along the shortest path in order from
        the start vertex to the goal vertex. ``came_from`` is a dict of the
        form ``{'vertex': 'node before vertex in the shortest path'}``. The
        algorith starts at the goal vertex, specified by ``goal``, and works
        backward until the entire path has been reconstructed.
        '''
        current_node = goal
        trail = []
        while True:
            trail.insert(0,current_node)
            try:
                if current_node == came_from[current_node] or \
                        len(came_from[current_node]) == 0:
                    break
                else:
                    current_node = came_from[current_node]
            except KeyError:
                # break out of loop when we reach the root node
                break
        return trail
        
        
    def pathCost(self, path):
        '''Returns the cost of taking a ``path`` from start to finish. The
        ``path`` is a list of vertices such as the one returned by
        :func:`shortestPath()`.
        '''
        cost = 0
        i = iter(path)
        prev = i.next()
        for element in i:
            cost += self.timeBetween(prev, element)
            prev = element
        return cost
        
        
if __name__ == "__main__":
    if len(sys.argv) == 3:
        start = sys.argv[1]
        end = sys.argv[2]
        graphfile = 'data/hugegraph.csv'
    elif len(sys.argv) == 4:
        graphfile = sys.argv[1]
        start = sys.argv[2]
        end = sys.argv[3]
    else:
        start = 'A'
        end = 'E'
        graphfile = 'data/graph2.txt'
        
    #search = Pathfinding(True, graphfile)
    search = Pathfinding()
    cProfile.run("search.shortestPath('28.241378,-81.206989', '28.700301,-81.529274')")
    #path = search.shortestPath("28.2496933,-81.2789873", "28.624119,-81.207763")
    #alts = search.alternateRoute(3, path)
    #print path
    #print search.pathCost(path)
