#!/usr/bin/env python
# encoding: utf-8
"""
Byzantine.py

Created by Joshua Olson on 2011-04-02.
Copyright (c) 2011 solarmist. All rights reserved.
"""

import random
import copy
import sys
import getopt
from collections import defaultdict

ONE = 1
ZERO = 0
UNKNOWN = '?'
FAULTY = 'X'

verbose = False
help_message = ''' 
Byzantine Generals problem
'''

class Usage(Exception):
	def __init__(self, msg):
		self.msg = msg
		
class node:
    def __init__(self, input = 0, output = 0):
        self.input = input
        self.output = output

def h(i):
    if i < 10:
        return i
    else:
        return hex(copy.copy(i))[-1:]

class Process:
    '''A process class for the Byzantine Generals Problem'''
    #Static data items
    #PID of commander
    commander = 0
    #number of processes
    n = 7
    #number of traitors
    m = 2
    #traitors
    traitor = list()
    
    def __init__(self, p = 0):
        self.pid = p
        self.nodes = dict()
        if len(Process.children) == 0:
            self.generate_children(Process.m, Process.n, [True] * Process.n, Process.commander)
        if self.pid == Process.commander:
            self.value = random.randint(0,1)
            self.nodes[""] = node(self.value,UNKNOWN)
    
    def is_commander(self):
        return Process.commander == self.pid
        
    @staticmethod
    def get_default():
        print 'uses the default action and',
        return 1
        
    def get_value(self, value, destination):
        if Process.traitor[self.pid]:
            return random.randint(0,1)
        if self.pid == Process.commander:
            return self.value
        else:
            return value
    
    def is_faulty(self):
        return Process.traitor[self.pid]
        
    def receive_message(self, path, node):
        self.nodes[path] = node
        
    def send_messages(self, round, processes):
        for i in range( len(Process.pathsByRank[round][self.pid]) ):
            sourceNodePath = Process.pathsByRank[round][self.pid][i][:-1]
            sourceNode = self.nodes[sourceNodePath]
            for j in range(Process.n):
                if j != Process.commander:
                    value = self.get_value(sourceNode.input, j)
                    
                    if verbose:
                        print 'Sending from process ' + str(self.pid) + ' to ' + str(j) + ':', 
                        print '{' + str(value) + ', ' + Process.pathsByRank[round][self.pid][i] + ', ' + str(UNKNOWN) + '},', 
                        print 'getting value from sourceNode ' + sourceNodePath + ' value ' + str(value)
                        
                    processes[j].receive_message(Process.pathsByRank[round][self.pid][i], node(value, UNKNOWN))
    
    def decide(self):
        if self.pid == Process.commander:
            return self.nodes[""].input
            
        #Set the leave values
        for i in range(Process.n):
            for j in range( len(Process.pathsByRank[Process.m][i]) ):
                path = Process.pathsByRank[Process.m][i][j]
                node = self.nodes[path]
                node.output = node.input
                
        #Work up the tree
        for round in range(Process.m - 1, -1, -1):
            for i in range(Process.n):
                for j in range( len(Process.pathsByRank[round][i]) ):
                    path = Process.pathsByRank[round][i][j]
                    node = self.nodes[path]
                    node.output = self.get_majority(path)
                    
        topPath = Process.pathsByRank[0][Process.commander][0]
        return self.nodes[topPath].output
    
    def get_majority(self, path):
        counts = {ONE:0, ZERO:0, UNKNOWN:0}
        
        for child in Process.children[path]:
            node = self.nodes[child]
            counts[node.output] += 1

        if counts[ONE] > Process.n / 2:
            return ONE
        if counts[ZERO] > Process.n / 2:
            return ZERO
        if counts[ONE] == counts[ZERO] and counts[ONE] == Process.n / 2:
            return Process.get_default()
        else:
            #print 'Cannot decide'
            return UNKNOWN
        
    def generate_children(self, m, n, ids, source, currentPath = '', rank = 0):
        '''Build the communitation tree'''
        ids[source] = False
        currentPath += str(h(source))
        Process.pathsByRank[rank][source].append(currentPath)
        if rank < m:
            for i in range(len(ids)):
                if ids[i]:
                    self.generate_children(m, n, copy.copy(ids), i, currentPath, rank + 1)
                    Process.children[currentPath].append(currentPath + str(h(i)) )
        if verbose:
            print currentPath + ", children =",
            for i in Process.children[currentPath]:
                print i,
            print

def Byzantine(n = 7, m = 2, commandTraitor = True):
    #Set up static class variables
	Process.n = n
	Process.m = m #Traitors
	Process.commander = random.randint(0, Process.n -1)
	Process.pathsByRank = defaultdict(lambda : defaultdict(list))
	Process.children = defaultdict(list)
	
	Process.traitor = []
	processes = []
	
	#Create the processes and mark the traitors
	#PID > 9 need to be in hex.
	for i in range(Process.n):
	    Process.traitor.append(False)
	    processes.append( Process( h(i)) )
	    
	if commandTraitor:
	    Process.traitor[Process.commander] = True
	
	while Process.traitor.count(True) < Process.m:
	    Process.traitor[random.randint(0, Process.n - 1)] = True
	    
	if verbose:
	    print Process.traitor
	    
	for i in range(Process.m + 1):
	    for j in range( Process.n ):
	        processes[j].send_messages(i, processes)
	    
	for j in range( len(processes) ):
	    if processes[j].is_commander():
	        print 'Commander',  
	    print 'Process ' + str(j),
	    if processes[j].is_faulty():
	        print 'is faulty'
	    else:
	        print 'decides on value ' + str(processes[j].decide())
#Need a concensus value here? Did they converge?


def main(argv=None):
	if argv is None:
		argv = sys.argv
	try:
		try:
			opts, args = getopt.getopt(argv[1:], "vhs:", ["help", "set="])
		except getopt.error, msg:
			raise Usage(msg)
	
		# option processing
		for option, value in opts:
			if option == "-v":
			    global verbose
			    verbose = True
			if option in ("-h", "--help"):
				raise Usage(help_message)
			if option in ("-s", "--set"):
				n = value
		
		n = 9
		m = 4
		GenTraitor = True
			
		#for i in range(n):
		#    for j in range(i):
		#        if j > 0:
		#            print 'Byzantine Generals (General is a traitor) n = ' + str(i) + ' m = ' + str(j)
		#            Byzantine(i,j, True)
		#            print
		print 'Byzantine Generals n = ' + str(n) + ' m = ' + str(m)
		Byzantine(n,m, True)
		print
	
	except Usage, err:
		print >> sys.stderr, sys.argv[0].split("/")[-1] + ": " + str(err.msg)
		print >> sys.stderr, "\t for help use --help"
		return 2
		

	

if __name__ == "__main__":
	sys.exit(main())
