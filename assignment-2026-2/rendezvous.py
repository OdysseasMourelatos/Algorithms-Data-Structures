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
    
    visited_a, distance_a, prev_a = breadth_first_search(g, begin_a)
    visited_b, distance_b, prev_b = breadth_first_search(g, begin_b)
    
    min_steps=-1
    meeting_node=(-1,-1)
    current_data=[min_steps, meeting_node]

    for i in range(len(g)):
        if visited_a[i][0] and visited_b[i][0]:
            check_min_steps(distance_a[i][0],distance_b[i][0], i, 0, current_data)
        if visited_a[i][1] and visited_b[i][1]:
            check_min_steps(distance_a[i][1],distance_b[i][1], i, 1, current_data)
    
    min_steps = current_data[0]
    meeting_node = current_data[1][0]
    parity = current_data[1][1]
    
    if meeting_node!=-1:
        #There is a meeting node without any adjustments
        path_a = get_path(meeting_node, begin_a, prev_a, parity)
        path_b = get_path(meeting_node, begin_b, prev_b, parity)   
        print_successful_results(min_steps, path_a, path_b, meeting_node)
    else:
        #There is no way in which Alice & Bob will meet
        if distance_a[begin_b][0] ==-1 and distance_a[begin_b][1] ==-1:
            print_failed_results()
        #There is not a way for Alice & Bob to meet as of now, but could be adjusted
        else:
            #Initially searching for the min between the two possible distances
            min_distance = min(distance_a[begin_b][0], distance_a[begin_b][1])
            #If it's not possible (-1), we pick the other one
            if min_distance == -1:
                min_distance = max(distance_a[begin_b][0], distance_a[begin_b][1])
            
            if min_distance == 1:
                print(min_distance)
            else:
                path = get_path(begin_b, begin_a, prev_a, min_distance%2)
                middle_node = path[int(len(path)/2)]
                prev_by_two = path[middle_node - 2]
                adjust_graph(g, prev_by_two, middle_node)
                print(g)
                
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
        prev.append([-1, -1])
    
    de.append([node,0])
    inqueue[node][0]=True
    distance[node][0] = 0
    
    while not len(de) == 0:
        c = de.popleft()
        visited_node = c[0]
        parity = c[1]%2
        inqueue[visited_node][parity]=False
        visited[visited_node][parity]=True
        
        for u in AdjacencyList(g,visited_node):
            if not visited[u][1-parity] and not inqueue[u][1-parity]:
                de.append([u, 1-parity])
                distance[u][1-parity]=distance[visited_node][parity]+1
                prev[u][1-parity] = visited_node
                inqueue[u][1-parity] = True
                
    return visited, distance, prev

def AdjacencyList(g,c):
    return g.get(c)

def check_min_steps(distance_a, distance_b, node, parity, current_data):
    #Initial Check
    if current_data[0]==-1:
        current_data[0] = max(distance_a,distance_b)
        current_data[1] = (node, parity)
        return
    
    max_steps_between_the_two = max(distance_a,distance_b)
    if max_steps_between_the_two <= current_data[0]:
        current_data[0] = max_steps_between_the_two
        current_data[1] = (node, parity)

def get_path(meeting_node, begin_node, prev, parity):
    prev_node = meeting_node
    path = [meeting_node]
    while prev_node!=begin_node:
        prev_node = prev[prev_node][parity]
        parity = 1 - parity
        path.insert(0, prev_node)
    return path

def adjust_graph(g, node_A, node_B):
    bisect.insort(g[node_A], node_B)
    bisect.insort(g[node_B], node_A)
    
def print_successful_results(min_steps, path_a, path_b, meeting_node):
    for i in range(min_steps + 1):
        print(str(i) + ": Alice at " + str(path_a[i]) + ", Bob at " + str(path_b[i]))
    print("Meeting at node " + str(meeting_node) + " at time step " + str(min_steps))

def print_failed_results():
    print("No meeting is possible.")
    print("Could not establish a rendezvous by adding edges.")
if __name__ == "__main__":
    main()