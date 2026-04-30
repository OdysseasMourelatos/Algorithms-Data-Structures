import sys
from collections import deque 
import bisect

def main():
    
    directed, filename = parse_arguments()
    
    g, begin_a, begin_b, nodes, links = get_graph(filename, directed)
    
    perform_initial_meeting_check(g, begin_a, begin_b, nodes, links, directed)

def parse_arguments():
    arguments = sys.argv
    if len(arguments) == 2:
        directed = False
        filename = sys.argv[1]
    elif len(arguments) == 3 and arguments[1] == "-d":
        directed = True
        filename = sys.argv[2]
    return directed, filename
    
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

def perform_initial_meeting_check(g, begin_a, begin_b, nodes, links, directed): 
    visited_a, distance_a, prev_a, visited_b, distance_b, prev_b = perform_breadth_first_search_with_parity(g, begin_a, begin_b)
    min_steps, meeting_node, parity = find_meeting_nodes(g, visited_a, visited_b, distance_a, distance_b)
    
    #If the two distances match, it's either undirected or directed with matching distances - so no problem with the indexes
    if not directed or (directed and distance_a[meeting_node][min_steps%2] == distance_b[meeting_node][min_steps%2]):
        updated_links = output_check(g, begin_a, begin_b, prev_a, prev_b, meeting_node, min_steps, parity, distance_a, links, directed)
        #If there is an update on the graph, it means we failed to find a meeting node and hence adjusted the graph
        if updated_links != links:
            perform_initial_meeting_check(g, begin_a, begin_b, nodes, updated_links, directed)
    else:
        meeting_node = find_meeting_node_with_min_combined_steps(visited_a, visited_b, distance_a, distance_b)
        failed = []
        circles_2_links = []
        circles_3_links = []
        perform_advanced_meeting_check_for_directed_graphs(g, begin_a, begin_b, meeting_node, circles_2_links, circles_3_links, failed)
        
def perform_advanced_meeting_check_for_directed_graphs(g, begin_a, begin_b, meeting_node, circles_2_links, circles_3_links, failed, og_node = None):
    #2-step circles
    if og_node is None:
        links = adjust_directed_graph(g, meeting_node, True)
        for link in links:
            p = bisect.bisect_left(circles_2_links, link)
            #Skip if we already have this 
            if p != len(circles_2_links) and circles_2_links[p] == link:
                continue
            bisect.insort(circles_2_links, link)
    #3-step circles
    else:
        links = adjust_directed_graph(g, meeting_node, False, og_node)
        for link in links:
            p = bisect.bisect_left(circles_3_links, link)
            #Skip if we already have this
            if p != len(circles_3_links) and circles_3_links[p] == link:
                continue
            bisect.insort(circles_3_links, link)
            
    path, l, failed = circles_check_for_possible_meetings(g, begin_a, begin_b, links, failed, False)
    #Found a meeting
    if l!=-1:
        print_directed_g_results(l, path)
    #Failed to find a meeting
    else:
        if len(circles_3_links) == 0:
            for link in links:
                perform_advanced_meeting_check_for_directed_graphs(g, begin_a, begin_b, link[1], circles_2_links, circles_3_links, failed, meeting_node)
            #When the recursion stops
            circles_check_for_possible_meetings(g, begin_a, begin_b, circles_2_links, failed, True, circles_3_links)
        
def adjust_directed_graph(g, meeting_node, circles_2 , og_node = None):
    links = []
    for node in g:
        #For all nodes, besides the node itself
        if node!=meeting_node:
            #Search the node in its adjacency list
            p = bisect.bisect_left(g[node], meeting_node)
            #If it exists (A->B)
            if p != len(g[node]) and g[node][p] == meeting_node:
                if circles_2:
                    #Add (B->A) to the possible links
                    links.append((meeting_node, node))
                else:
                    links.append((og_node, node))
    return links

def circles_check_for_possible_meetings(g, begin_a, begin_b, links, failed, combination, links_3 = None):
    min_length = -1
    path = []
    l = -1
    data = [min_length, path, l]
    for link in links:
        if not combination:
            #Check if we already tested this connection
            p = bisect.bisect_left(failed, (link[0], link[1]))
            if p != len(failed) and failed[p] == (link[0], link[1]):
                break
            #If not, test it
            bisect.insort(g[link[0]], link[1])  
        else:
            for link_3 in links_3:
                bisect.insort(g[link[0]], link[1])
                bisect.insort(g[link_3[0]], link_3[1])
        data = run_search(g, begin_a, begin_b, data, link, failed)
    
    path, l  = data[1], data[2]
    return path, l, failed

def run_search(g, begin_a, begin_b, data, link, failed):
    min_length, path, l = data[0], data[1], data[2]
    prev, new_meeting = breadth_first_search_with_cartesian_product(g, begin_a, begin_b)
    if new_meeting != (-1,-1):
        new_path = track_new_path(prev, new_meeting)
        if min_length == -1 or (min_length !=-1 and len(new_path) < min_length):
            min_length = len(new_path)
            path = new_path
            l = link
    else:
        bisect.insort(failed, (link[0], link[1]))
        g[link[0]].remove(link[1])
    data[0], data[1], data[2] = min_length, path, l
    return data
    
def perform_breadth_first_search_with_parity(g, begin_a, begin_b):
    visited_a, distance_a, prev_a = breadth_first_search_with_parity(g, begin_a)
    visited_b, distance_b, prev_b = breadth_first_search_with_parity(g, begin_b)
    return visited_a, distance_a, prev_a, visited_b, distance_b, prev_b

def breadth_first_search_with_parity(g, node):
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

def find_meeting_nodes(g, visited_a, visited_b, distance_a, distance_b):
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
    return min_steps, meeting_node, parity

def check_min_steps(distance_a, distance_b, node, parity, current_data):
    #Initial Check
    if current_data[0]==-1:
        #We need the min max 
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

def output_check(g, begin_a, begin_b, prev_a, prev_b, meeting_node, min_steps, parity, distance_a, links, directed):
    if meeting_node!=-1:
        #There is a meeting node without any adjustments
        path_a = get_path(meeting_node, begin_a, prev_a, parity)
        path_b = get_path(meeting_node, begin_b, prev_b, parity)   
        print_successful_results(min_steps, path_a, path_b)
    else:
        if not directed:
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
            
                #Neighbors
                if min_distance == 1:
                    neighbors_adjustment(g, begin_a, begin_b)
                #Not Neighbors
                else:
                    non_neighbors_adjustment(g, begin_b, begin_a, prev_a, min_distance)
                links+=1
    return links

def neighbors_adjustment(g, begin_a, begin_b):
    neighbors = sorted(g[begin_a] + g[begin_b])
    for neighbor in neighbors:
        if neighbor!=begin_a and neighbor!=begin_b:
            new_neighbor = neighbor
            break
    p = bisect.bisect_left(g[begin_a], new_neighbor)
    
    if new_neighbor == g[begin_a][p]:
        node_for_connection = begin_b
    else:
        node_for_connection = begin_a
                    
    adjust_undirected_graph(g, node_for_connection, new_neighbor)

def non_neighbors_adjustment(g, begin_b, begin_a, prev_a, min_distance):
    path = get_path(begin_b, begin_a, prev_a, min_distance%2)
    middle_node = path[int(len(path)/2)]
    prev_by_two = path[middle_node - 2]
    adjust_undirected_graph(g, prev_by_two, middle_node)  

def adjust_undirected_graph(g, node_A, node_B):
    bisect.insort(g[node_A], node_B)
    bisect.insort(g[node_B], node_A)
    print_adjustment(node_A, node_B)
   
def print_successful_results(steps, path_a, path_b):
    for i in range(steps + 1):
        print(str(i) + ": Alice at " + str(path_a[i]) + ", Bob at " + str(path_b[i]))
    print("Meeting at node " + str(path_a[i]) + " at time step " + str(steps) + ".")

def print_failed_results():
    print("No meeting is possible.")
    print("Could not establish a rendezvous by adding edges.")

def print_adjustment(node_A, node_B):
    print("No meeting is possible.")
    print("Adding 1 edge.")
    print("Adding " + str(node_A) + " " + str(node_B) + ".")

def find_meeting_node_with_min_combined_steps(visited_a, visited_b, distance_a, distance_b):
    #At this stage, we don't care about parity - we just want nodes where the two can meet irrespective of steps count
    #Instead of performing a new breadth first search, will try to use results from the first one
    min_distance=-1
    meeting_node=-1
    
    for i in range(len(visited_a)):
        if (visited_a[i][0] or visited_a[i][1]) and (visited_b[i][0] or visited_b[i][1]):
            dis_a = check_min_distance(distance_a[i][0], distance_a[i][1])
            dis_b = check_min_distance(distance_b[i][0], distance_b[i][1])
            new_min_distance = dis_a + dis_b
            
            #Check
            if min_distance == -1:
                min_distance = new_min_distance
                meeting_node = i
            else:
                if new_min_distance < min_distance:
                    min_distance = new_min_distance
                    meeting_node = i
                    
    return meeting_node

def check_min_distance(dis_1, dis_2):
    dis = min(dis_1, dis_2)
    if dis == -1:
        dis = max(dis_1, dis_2)
    return dis
     
def breadth_first_search_with_cartesian_product(g, begin_a, begin_b):
    de = deque()
    visited = {}
    inqueue = {}
    prev = {}
    
    de.append((begin_a, begin_b))
    visited[(begin_a, begin_b)] = False
    inqueue[(begin_a, begin_b)] = True
    prev[(begin_a, begin_b)] = -1
    found = False
    meeting=(-1,-1)
    
    while not found and not len(de) == 0:
        a,b = de.popleft()
        visited[(a,b)] = True
        inqueue[(a,b)] = False
        for node_a in AdjacencyList(g, a):
            for node_b in AdjacencyList(g, b):
                if node_a == node_b:
                    meeting = (node_a, node_b)
                    found = True
                v = visited.get((node_a, node_b))
                i = inqueue.get((node_a, node_b))
                if (not v or v is None) and (not i or i is None):
                    de.append((node_a, node_b))
                    inqueue[(node_a, node_b)] = True
                    prev[(node_a, node_b)] = (a, b)
    return prev, meeting

def track_new_path(prev, new_meeting):
    c = new_meeting
    path = [c]
    while prev.get((c)) != -1:
        c = prev.get((c))
        path.insert(0, c)
    return path

def print_directed_g_results(added_link, path):
    print_adjustment(added_link[0], added_link[1])

    path_a = []
    path_b = []
    for p in path:
        path_a.append(p[0])
        path_b.append(p[1])

    print_successful_results(len(path) -1, path_a, path_b)
           
if __name__ == "__main__":
    main()