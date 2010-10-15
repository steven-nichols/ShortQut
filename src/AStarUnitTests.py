#!/usr/bin/env python

import unittest
from AStar import AStar

class TestSequenceFunctions(unittest.TestCase):

    def testset1_path2self(self):
        search = AStar(True, 'data/graph1.txt')
        path = search.shortestPath('A', 'A')
        self.assertEqual(path, ['A'], 'Incorrect path when start and goal are \
                                        the same')
    
    def testset1_pathAB(self):
        search = AStar(True, 'data/graph1.txt')
        path = search.shortestPath('A', 'B')
        self.assertEqual(path, ['A', 'C', 'B'], 'Incorrect path from A to B')
    
    def testset1_pathAE(self):
        search = AStar(True, 'data/graph1.txt')
        path = search.shortestPath('A', 'E')
        
        self.assertTrue(len(path) <= len(['A','B','C','D','E']), 'Path too long')
        for element in path:
            self.assertTrue(element in ['A','B','C','D','E'], 'Node not in list')
        
    def testset2_pathReversed(self):
        '''Symmetric graph'''
        search = AStar(True, 'data/graph2.txt')
        path1 = search.shortestPath('A', 'E')
        path2 = search.shortestPath('E', 'A')
        path2.reverse()
        self. assertEqual(path1, path2, 'Incorrect path when start/goal reversed\
                                         in symmetric graph')

    def testset3_pathAE(self):
        search = AStar(True, 'data/graph3.txt')
        path = search.shortestPath('A', 'E')
        self.assertEqual(path, ['A', 'C', 'F', 'E'], 'Incorrect path from A to E')
        
        
    def testset4_linear(self):
        f = open('data/graph4.txt', 'w')
        for i in range(0, 25):
            f.write("%s, %s, %d\n" % (chr(65 + i), chr(65 + i + 1), 1))
        f.close()
        
        search = AStar(True, 'data/graph4.txt')
        path = search.shortestPath('A', 'Z')
        
        self.assertTrue(len(path) == 26, 'Incorrect path on linear graph')
        cost = search.pathCost(path)
        self.assertTrue(cost == 25, 'Incorrect cost of shortest path')
        count = 0
        for element in path:
            self.assertEqual(element, chr(65 + count), 'Node not in list')
            count += 1
            
            
if __name__ == '__main__':
    unittest.main()

