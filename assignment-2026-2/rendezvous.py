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

    g = get_graph(filename, directed)
    print(g)
    parity_a = breadth_first_search(g, begin_a)
    parity_b = breadth_first_search(g, begin_b)
    
    print(parity_a)
    print(parity_b)

def get_graph(filename, directed):
    g = {}
    with open(filename) as graph_input:
        for line in graph_input:
            nodes = [int(x) for x in line.split()]
            if len(nodes) != 2:
                continue
            if nodes[0] not in g:
                g[nodes[0]] = []
            if nodes[1] not in g:
                g[nodes[1]] = []
            g[nodes[0]].append(nodes[1])
            if not directed:
                g[nodes[1]].append(nodes[0])
    return g

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