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
    de = deque()
    visited = []
    inqueue = []
    distance = []
    prev = []
    for i in range(len(g)):
        visited.append([False, False])
        inqueue.append([False, False])
        distance.append([-1,-1])
        prev.append(-1)
    
    print(visited)
    de.append([node,0])
    inqueue[node][0]=True
    distance[node][0] = 0
    parity = [[node, 0]]
    
    while not len(de) == 0:
        c = de.popleft()
        visited_node = c[0]
        parity = c[1]%2
        inqueue[visited_node][parity]=False
        visited[visited_node][parity]=True
        for u in AdjacencyList(g,visited_node):
            #parity.append([u, distance[u]%2])
            if not visited[u][1-parity] and not inqueue[u][1-parity]:
                de.append([u, 1-parity])
                #distance[u][0]=distance[c][0]+1
                prev[u] = c
                inqueue[u][1-parity] = True
        print(de)
    #print(distance)
    #print(prev)
    return visited

def AdjacencyList(g,c):
    return g.get(c)

if __name__ == "__main__":
    main()