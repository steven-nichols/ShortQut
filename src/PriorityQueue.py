#!/usr/bin/env python
import itertools
from heapq import heappush, heappop

class PriorityQueue:
    '''A generic priority queue based off the example implementation in the 
    Official heapq documentation. http://docs.python.org/library/heapq.html'''
    
    pq = []                         # the priority queue list
    counter = itertools.count(1)    # unique sequence count
    item_finder = {}                # mapping of items to entries
    INVALID = 0                     # mark an entry as deleted

    def push(self, priority, item, count=None):
        if count is None:
            count = next(self.counter)
        entry = [priority, count, item]
        self.item_finder[item] = entry
        heappush(self.pq, entry)
    
    def pop(self):
        while True:
            priority, count, item = heappop(self.pq)
            try:
                del self.item_finder[item]
            except KeyError:
                pass
            if count is not self.INVALID:
                return (priority, item)

    def delete(self, item):
        entry = self.item_finder[item]
        entry[1] = self.INVALID
        
    def find(self, item):
        try:
            entry = self.item_finder[item]
        except KeyError:
            return None
        return entry
    
    def reprioritize(self, priority, item):
        entry = self.find(item)
        if entry is not None:
            self.push(priority, item, entry[1])
            entry[1] = self.INVALID
        else:
            self.push(priority, item)
