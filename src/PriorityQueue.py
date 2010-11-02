#!/usr/bin/env python
import itertools
from heapq import heappush, heappop, nsmallest
from Log import Log
log = Log('PriorityQueue', 'debug')


class hashablelist(list):
    '''This is kind of a hack to get around a Python restriction that lists 
    cannot be used as keys in dictionaries.'''
    
    def __init__(self, l):
        for x in l:
            self.append(x)
        
    def __hash__(self):
        return id(self)
        
    def toList(self):
        return self
        


class PriorityQueue:
    '''A generic priority queue based off the example implementation in the 
    Official heapq documentation. http://docs.python.org/library/heapq.html'''

    def __init__(self):
        self.pq = []                         # the priority queue list
        self.counter = itertools.count(1)    # unique sequence count
        self.item_finder = {}                # mapping of items to entries
        self.INVALID = 0                     # mark an entry as deleted
        self.valid_entries = 0               # count valid entries
        log.info('Initialize new priority queue')
        
    def push(self, priority, item, count=None):
        '''Add an item to the priority queue. The priority queue is implemented as
        a min heap such that the highest priority is 0, and the lowest priority is
        infinity.
        
        Args:
            priority (float) - priority of item to be added
            item (any) - the item to be added
            count (int) - unique id
            
        '''
        if(isinstance(item, list)):
            item = hashablelist(item)
        
        if count is None:
            count = next(self.counter)
        entry = [priority, count, item]
        self.item_finder[item] = entry
        heappush(self.pq, entry)
        self.valid_entries += 1
    
    def pop(self):
        '''Find and return the highest priority (0 = highest, infinity = 
        lowest). If more than one item has the same priority, the item that was 
        added first will be selected. 
        
        Returns:
            (tuple) - tuple of form: (priority, item)
        '''
        while True:
            try:
                priority, count, item = heappop(self.pq)
            except IndexError as e:
                log.error("Index Error: {!s}. [valid_entries = {!s}, pq = {!s}]"\
                        .format(e, self.valid_entries, self.pq))
                raise IndexError
            
            try:
                del self.item_finder[item]
            except KeyError:
                pass
            if count is not self.INVALID:
                if(isinstance(item, hashablelist)):
                    item = item.toList()
                self.valid_entries -= 1
                return (priority, item)

    def delete(self, item):
        '''Remove an item from the queue.
        
        Args:
            item (any) - the item to be removed
            
        '''
        if(isinstance(item, list)):
            item = hashablelist(item)
        entry = self.item_finder[item]
        entry[1] = self.INVALID
        self.valid_entries -= 1
        
    def __find(self, item):
        if(isinstance(item, list)):
            item = hashablelist(item)
            
        try:
            entry = self.item_finder[item]
        except KeyError:
            return None
        return entry
    
    def reprioritize(self, priority, item):
        '''Change the priority of an item already in the queue.
        
        Args:
            priority (float) - priority of item to be added
            item (any) - the item to be added
        '''
        
        if(isinstance(item, list)):
            item = hashablelist(item)
        
        entry = self.__find(item)
        if entry is not None:
            self.push(priority, item, entry[1])
            entry[1] = self.INVALID
            self.valid_entries -= 1
        else:
            self.push(priority, item)

    
    def tolist(self):
        '''Return a list representation of this object'''
        temp = nsmallest(len(self), self.pq)
        l = []
        for priority, count, item in temp:
            if count is not self.INVALID:
                if(isinstance(item, hashablelist)):
                    item = item.toList()
                l.append(item)
        return l
    
    def __len__(self):
        '''Return the number of valid entries currently in the queue'''
        return self.valid_entries;
    
    def __repr__(self):
        '''Return a string prepresentation of this object'''
        return str(self.tolist())
