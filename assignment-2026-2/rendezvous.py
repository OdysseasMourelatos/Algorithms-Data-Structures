import sys
from collections import deque 
import bisect

def main():
    arguments = sys.argv
    if len(arguments) == 2:
        directed = False
        filename = sys.argv[1]
    elif len(arguments) == 3 and arguments[1] == "-d":
        directed = True
        filename = sys.argv[2]

    g, begin_a, begin_b, nodes, links = get_graph(filename, directed)
    print(g)
    
    parity_a = breadth_first_search(g, begin_a)
    parity_b = breadth_first_search(g, begin_b)
    
    print(parity_a)
    print(parity_b)

def get_graph(filename, directed):
    g = {}
    f = open(filename)
    graph_input = list(f)
    f.close()
    
    i=0
    for line in graph_input:
        i+=1
        nodes = [int(x) for x in line.split()]
        if len(nodes) != 2:
            continue
            
        if i == 1:
            total_nodes = nodes[0]
            total_links = nodes[1]
            continue
        elif i == len(graph_input): 
            begin_a = nodes[0]
            begin_b = nodes[1]
            break
        
        if nodes[0] not in g:
            g[nodes[0]] = []
        if nodes[1] not in g:
            g[nodes[1]] = []
        bisect.insort(g[nodes[0]], nodes[1])
        if not directed:
            bisect.insort(g[nodes[1]], nodes[0])
                
    return g, begin_a, begin_b, total_nodes, total_links

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