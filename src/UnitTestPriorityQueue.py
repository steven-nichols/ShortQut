#!/usr/bin/env python

import unittest
from PriorityQueue import PriorityQueue

class TestSequenceFunctions(unittest.TestCase):

    def test_pushpop(self):
        '''Push items onto queue and then remove them'''
        pq = PriorityQueue()
        for i in range(0, 10):
            pq.push(0,i)
            
        for i in range(0, 10):
            self.assertEqual(pq.pop()[1], i)
    
    def test_priority(self):
        '''Test the priority portion of the priority queue'''
        pq = PriorityQueue()
        for i in range(0, 10):
            pq.push(i,i)
            
        for i in range(0, 10):
            pri, item = pq.pop()
            # Priorities match
            self.assertEqual(pri, i)
            # Values match
            self.assertEqual(item, i)

    def test_neg_priority(self):
        '''Negative priorities'''
        pq = PriorityQueue()
        for i in range(-5, 5):
            pq.push(i,i)
            
        for i in range(-5, 5):
            pri, item = pq.pop()
            # Priorities match
            self.assertEqual(pri, i)
            # Values match
            self.assertEqual(item, i)
            
    def test_uselist(self):
        '''Push a list onto queue and them remove it'''
        pq = PriorityQueue()
        l = []

        pq.push(0,range(0, 10))
        self.assertEqual(pq.pop()[1], range(0, 10))
    
    def test_reprioritize(self):
        pq = PriorityQueue()
        for letter in range(ord('A'), ord('Z')+1):
            letter = chr(letter)
            pq.push(0, letter)
            pq.reprioritize(1, letter)
        
        for letter in range(ord('A'), ord('Z')+1):
            letter = chr(letter)
            pri, val = pq.pop()
            self.assertEqual(letter, val)
            self.assertEqual(pri, 1)

    def test_multiple(self):
        '''Test that two different priority queues do not interfere with
        each other'''
        pq = PriorityQueue()
        pq.push(0, 'A')
        
        pq = PriorityQueue()
        self.assertEqual(len(pq), 0)
        with self.assertRaises(IndexError):
            pq.pop()
        
#if __name__ == '__main__':
    #unittest.main()
suite = unittest.TestLoader().loadTestsFromTestCase(TestSequenceFunctions)
unittest.TextTestRunner(verbosity=2).run(suite)
