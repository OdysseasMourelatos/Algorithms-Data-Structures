import sys
from collections import deque 
import bisect

def main():
    n = len(sys.argv)
    if n == 2:
        directed = False
        filename = sys.argv[1]
    elif n == 3:
        directed = True
        filename = sys.argv[2]

    g, begin_a, begin_b, nodes, links = get_graph(filename, directed)
    print(g)
    #parity_a = breadth_first_search(g, begin_a)
    #parity_b = breadth_first_search(g, begin_b)
    
    #print(parity_a)
    #print(parity_b)

def get_graph(filename, directed):
    g = {}
    first_line = True
    with open(filename) as graph_input:
        for line in graph_input:
            nodes = [int(x) for x in line.split()]
            if len(nodes) != 2:
                continue
            
            if first_line:
                begin_a = nodes[0]
                begin_b = nodes[1]
                first_line = False
                continue
            
            if nodes[0] not in g:
                g[nodes[0]] = []
            if nodes[1] not in g:
                g[nodes[1]] = []
            g[nodes[0]].append(nodes[1])
            if not directed:
                g[nodes[1]].append(nodes[0])
                
            last_a = nodes[0]
            last_b = nodes[1]
    
    nodes = last_a
    links = last_b
    
    remove_data(g, last_a, last_b)
    if not directed:
        remove_data(g, last_b, last_a)
    
    return g, begin_a, begin_b, nodes, links

def remove_data(g, a, b):
    for node in g.get(a):
        if node == b:
            g.get(a).remove(b)
    
def breadth_first_search(g, node):
    de = deque([])
    visited = []
    inqueue = []
    for i in range(len(g)):
        visited.append(False)
        inqueue.append(False)
    de.append(node)
    inqueue[node]=True
    
    i = 0
    parity = [[node, i]]
    
    while not len(de) == 0:
        c = de.popleft()
        inqueue[c]=False
        visited[c]=True
        i+=1
        for u in AdjacencyList(g,c):
            parity.append([u, i%2])
            if not visited[u] and not inqueue[u]:
                de.append(u)
                inqueue[u] = True
    return parity

def AdjacencyList(g,c):
    return g.get(c)

if __name__ == "__main__":
    main()