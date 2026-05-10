import sys
from collections import deque 
import bisect

def main():
    directed, filename = parse_arguments() #Get the file and whether the graph is directed or not
    g, begin_a, begin_b, nodes, links = get_graph(filename, directed) #Transform the data from the file into a graph
    perform_initial_meeting_check(g, begin_a, begin_b, nodes, links, directed) #After getting the graph, we start checking for meetings

#---------------------------------
#Functions to get the initial data
#---------------------------------

def parse_arguments():
    arguments = sys.argv
    if len(arguments) == 2: #Not Directed
        directed, filename = False, sys.argv[1]
    elif len(arguments) == 3 and arguments[1] == "-d": #Directed
        directed, filename = True, sys.argv[2] 
    return directed, filename
    
def get_graph(filename, directed):
    g = {}
    f = open(filename)
    graph_input = list(f) #Put the contents into a list so that i know which line is the last
    f.close()
    
    i=0
    for line in graph_input:
        i+=1
        nodes = [int(x) for x in line.split()]
        if len(nodes) != 2:
            continue

        if i == 1: #It's the first line, sould be treated differently
            total_nodes, total_links = nodes[0], nodes[1]
            continue
        elif i == len(graph_input): #It's the last line, sould also be treated differently
            begin_a, begin_b = nodes[0], nodes[1]
            break
        #Ιnitialization
        if nodes[0] not in g:
            g[nodes[0]] = []
        if nodes[1] not in g:
            g[nodes[1]] = []
        bisect.insort(g[nodes[0]], nodes[1]) #Αdd the link (A->B)
        if not directed: #Then we add the other link too (B->A)
            bisect.insort(g[nodes[1]], nodes[0])
            
    return g, begin_a, begin_b, total_nodes, total_links

#-----------------------------------------------------------------------
#Functions for NOT DIRECTED graphs or DIRECTED graphs with meeting nodes
#-----------------------------------------------------------------------

def perform_initial_meeting_check(g, begin_a, begin_b, nodes, links, directed):
    #Case 1 - Breadth-first search with parity and checking whether we find a meeting without any adjustments
    visited_a, distance_a, pred_a, visited_b, distance_b, pred_b = perform_breadth_first_search_with_parity(g, begin_a, begin_b)
    min_steps, meeting_node, parity = find_meeting_node(g, visited_a, visited_b, distance_a, distance_b)
    
    #If the two distances match, it's either undirected or directed with matching distances - so no problem with the indexes
    if (not directed or (directed and meeting_node!=-1 and distance_a[meeting_node][min_steps%2] == distance_b[meeting_node][min_steps%2])):
        updated_links = output_check(g, begin_a, begin_b, pred_a, pred_b, meeting_node, min_steps, parity, distance_a, links, directed)
        #If there is an update on the graph, it means we failed to find a meeting node and hence adjusted the graph
        if updated_links != links:
            #Recursion, the process repeated again with the updated graph
            perform_initial_meeting_check(g, begin_a, begin_b, nodes, updated_links, directed) 
    else: #If it's directed with no meeting edges, new approach
        meeting_node = find_meeting_node_with_min_combined_steps(visited_a, visited_b, distance_a, distance_b) #Find the nearest meeting
        #Pass the ball to the other function
        failed, circles_2_links, circles_3_links = [], [], []
        perform_advanced_meeting_check_for_directed_graphs(g, begin_a, begin_b, meeting_node, circles_2_links, circles_3_links, failed) 

def perform_breadth_first_search_with_parity(g, begin_a, begin_b):
    visited_a, distance_a, pred_a = breadth_first_search_with_parity(g, begin_a) #Search for A
    visited_b, distance_b, pred_b = breadth_first_search_with_parity(g, begin_b) #Search for B
    return visited_a, distance_a, pred_a, visited_b, distance_b, pred_b

def breadth_first_search_with_parity(g, node):
    de = deque()
    visited, inqueue, distance, pred = [], [], [], []
    for i in range(len(g)): #Initialization
        visited.append([False, False]) #2D arrays (Aij), i is the node, j the parity
        inqueue.append([False, False])
        distance.append([-1,-1])
        pred.append([-1, -1])
        
    #Starting with the first node and parity 0
    de.append([node,0]) 
    inqueue[node][0]=True
    distance[node][0] = 0
    
    while not len(de) == 0:
        c = de.popleft()
        visited_node = c[0]
        parity = c[1]
        inqueue[visited_node][parity]=False
        visited[visited_node][parity]=True
        
        for u in AdjacencyList(g,visited_node):
            #The parity changes, if it was 0 it's now 1 and if it was 1 it's now 0
            if not visited[u][1-parity] and not inqueue[u][1-parity]: 
                de.append([u, 1-parity])
                distance[u][1-parity]=distance[visited_node][parity]+1 #We keep the distance from starting node
                pred[u][1-parity] = visited_node #We keep the node which we last visited so that we can track the path
                inqueue[u][1-parity] = True
                
    return visited, distance, pred

def AdjacencyList(g,c):
    return g.get(c)
          
def find_meeting_node(g, visited_a, visited_b, distance_a, distance_b):
    min_steps, meeting_node = -1, (-1,-1)
    current_data=[min_steps, meeting_node] #Keep them in a list in order for other functions to change their values
    for i in range(len(g)):
        if visited_a[i][0] and visited_b[i][0]: #If both visited node i with parity 0, it's a meeting
            check_min_steps(distance_a[i][0],distance_b[i][0], i, 0, current_data)
        if visited_a[i][1] and visited_b[i][1]: #If both visited node i with parity 1, it's a meeting
            check_min_steps(distance_a[i][1],distance_b[i][1], i, 1, current_data)
    
    min_steps, meeting_node, parity = current_data[0], current_data[1][0], current_data[1][1]
    return min_steps, meeting_node, parity

def check_min_steps(distance_a, distance_b, node, parity, current_data):
    #Initial Check
    if current_data[0]==-1: #There has been no meeting before 
        #We need the min max
        current_data[0] = max(distance_a,distance_b)
        current_data[1] = (node, parity)
        return
    
    max_steps_between_the_two = max(distance_a,distance_b)
    if max_steps_between_the_two <= current_data[0]: #If the distance is less than the one we have now
        current_data[0] = max_steps_between_the_two
        current_data[1] = (node, parity)

#One of my favorite functions - tracking back the path node by node
def get_path(meeting_node, begin_node, pred, parity):
    pred_node = meeting_node
    path = [meeting_node]
    while pred_node!=begin_node:
        pred_node = pred[pred_node][parity] #Get the previous node
        parity = 1 - parity #Change parity accordingly
        path.insert(0, pred_node) #Insert at the beginning
    return path

def output_check(g, begin_a, begin_b, pred_a, pred_b, meeting_node, min_steps, parity, distance_a, links, directed):
    if meeting_node!=-1:
        #There is a meeting node without any adjustments - SUCCESS
        path_a = get_path(meeting_node, begin_a, pred_a, parity)
        path_b = get_path(meeting_node, begin_b, pred_b, parity)   
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
                    non_neighbors_adjustment(g, begin_b, begin_a, pred_a, min_distance)
                links+=1
    return links

#---------------------------------------------------------
#Functions for the adjustment of NOT DIRECTED graphs ONLY
#---------------------------------------------------------

def neighbors_adjustment(g, begin_a, begin_b):
    neighbors = sorted(g[begin_a] + g[begin_b])
    for neighbor in neighbors:
        if neighbor!=begin_a and neighbor!=begin_b:
            new_neighbor = neighbor
            break
    p = bisect.bisect_left(g[begin_a], new_neighbor) #Search the neighbor
    
    if new_neighbor == g[begin_a][p]: #If it's connected with A
        node_for_connection = begin_b #Connect it with B
    else: #If it's connected with B, connect it with A
        node_for_connection = begin_a 
                    
    adjust_undirected_graph(g, node_for_connection, new_neighbor)

def non_neighbors_adjustment(g, begin_b, begin_a, pred_a, min_distance):
    path = get_path(begin_b, begin_a, pred_a, min_distance%2)
    middle_node = path[int(len(path)/2)]
    pred_by_two = path[middle_node - 2]
    adjust_undirected_graph(g, pred_by_two, middle_node)  

def adjust_undirected_graph(g, node_A, node_B):
    bisect.insort(g[node_A], node_B)
    bisect.insort(g[node_B], node_A)
    print_adjustment(node_A, node_B)

#------------------------------------------------------------------------------
#Functions ONLY for directed graphs with no meeting node (from the first search)
#------------------------------------------------------------------------------

def find_meeting_node_with_min_combined_steps(visited_a, visited_b, distance_a, distance_b):
    #At this stage, we don't care about parity - we just want nodes where the two can meet irrespective of steps count
    #Instead of performing a new breadth first search, will use results from the first one
    min_distance=-1
    meeting_node=-1
    
    for i in range(len(visited_a)):
        if (visited_a[i][0] or visited_a[i][1]) and (visited_b[i][0] or visited_b[i][1]): #If both visited the node
            dis_a = check_min_distance(distance_a[i][0], distance_a[i][1]) #Min distance for A
            dis_b = check_min_distance(distance_b[i][0], distance_b[i][1]) #Min distance for B
            new_min_distance = dis_a + dis_b #Min combined distance
    
            if min_distance == -1 or (new_min_distance < min_distance): #New min distance
                min_distance = new_min_distance
                meeting_node = i
    
    return meeting_node

def check_min_distance(dis_1, dis_2):
    dis = min(dis_1, dis_2) #Min distance between the two
    if dis == -1: #If the min is -1, it's not valid, so we just take the other one
        dis = max(dis_1, dis_2)
    return dis

def perform_advanced_meeting_check_for_directed_graphs(g, begin_a, begin_b, meeting_node, circles_2_links, circles_3_links, failed, og_node = None):
    #2-step circles
    if og_node is None:
        links = adjust_directed_graph(g, meeting_node, True)
        for link in links:
            p = bisect.bisect_left(circles_2_links, link)
            #Skip if we already have this 
            if p != len(circles_2_links) and circles_2_links[p] == link:
                continue
            bisect.insort(circles_2_links, link) #Add the links to the list for testing 2-step circles
    #3-step circles
    else:
        links = adjust_directed_graph(g, meeting_node, False, og_node)
        for link in links:
            p = bisect.bisect_left(circles_3_links, link)
            #Skip if we already have this
            if p != len(circles_3_links) and circles_3_links[p] == link:
                continue
            bisect.insort(circles_3_links, link) #Add the links to the list for testing 3-step circles
            
    #Test 2-step circles or 3-step cirles alone - NO COMBINATION YET
    path, l, failed = circles_check_for_possible_meetings(g, begin_a, begin_b, links, failed, False) 
    
    #Found a meeting
    if l!=-1:
        l = list([l])
        print_directed_g_results(l, path)
        
    #Failed to find a meeting
    else:
        if len(circles_3_links) == 0 and links == circles_2_links:
            for link in circles_2_links:
                #Recursion for 3-step cirles
                perform_advanced_meeting_check_for_directed_graphs(g, begin_a, begin_b, link[1], circles_2_links, circles_3_links, failed, meeting_node)
            #When the recursion stops, if we failed to create 3-step circles -> FAILED!
            if len(circles_3_links) == 0:
                print_failed_results()
            #We check the possible meetings
            else:
                #With combination this time
                path, l_1, l_2 = circles_check_for_possible_meetings(g, begin_a, begin_b, circles_2_links, failed, True, circles_3_links)
                if l_1!=-1 and l_2 !=-1: #Found a meeting
                    l = list([l_1] + [l_2])
                    print_directed_g_results(l, path)
                else: #Everything failed
                    print_failed_results()
                
def adjust_directed_graph(g, meeting_node, circles_2 , og_node = None):
    links = []
    for node in g:
        #For all nodes, besides the node itself
        if node!=meeting_node:
            #Search the node in its adjacency list
            p = bisect.bisect_left(g[node], meeting_node)
            #If it exists (B->A)
            if p != len(g[node]) and g[node][p] == meeting_node:
                if circles_2:
                    #Add (A->B) to the possible links (A->B->A)
                    links.append((meeting_node, node))
                else:
                    #Add (A->C) to the possible links (A->C->B->A)
                    links.append((og_node, node))
    return links

def circles_check_for_possible_meetings(g, begin_a, begin_b, links, failed, combination, sec_links = None):
    min_length, path, l = -1, [], -1
    if not combination:
        data = [min_length, path, l]
    else:
        l_2 = -1 #Extra links
        data = [min_length, path, l, l_2]
    for link in links:
        if not combination:
            #Check if we already tested this connection
            p = bisect.bisect_left(failed, (link[0], link[1]))
            if p != len(failed) and failed[p] == (link[0], link[1]):
                break
            #If not, test it
            bisect.insort(g[link[0]], link[1])  
            data = run_search(g, begin_a, begin_b, data, link, failed)
            path, l  = data[1], data[2]
        else:
            for sec_link in sec_links:
                bisect.insort(g[link[0]], link[1])
                bisect.insort(g[sec_link[0]], sec_link[1])
                data = run_search(g, begin_a, begin_b, data, link, failed, sec_link)
                path, l, l_2 = data[1], data[2], data[3]
    if not combination:
        return path, l, failed
    else:
        return path, l, l_2

def run_search(g, begin_a, begin_b, data, link, failed, link_2 = None):
    if link_2 is None: #No combination
        min_length, path, l = data[0], data[1], data[2]
    else: #Combination of 2-step circles & 3-step ones
        min_length, path, l, l_2 = data[0], data[1], data[2], data[3]
    pred, new_meeting = breadth_first_search_with_cartesian_product(g, begin_a, begin_b) #New search
    
    if new_meeting != (-1,-1): #MEETING FOUND!!!
        new_path = track_new_path(pred, new_meeting)
        #New meeting is the first we find, or it requires less steps
        if min_length == -1 or (min_length !=-1 and len(new_path) < min_length): 
            min_length = len(new_path)
            path = new_path
            l = link
            if link_2 is not None:
                l_2 = link_2
    else: #Meeting failed, so we re-adjust the graph and add it as a failure
        bisect.insort(failed, (link[0], link[1]))
        g[link[0]].remove(link[1])
        if link_2 is not None:
            bisect.insort(failed, (link_2[0], link_2[1]))
            g[link_2[0]].remove(link_2[1])
            
    if link_2 is None:
        data[0], data[1], data[2] = min_length, path, l
    else:
        data[0], data[1], data[2], data[3] = min_length, path, l, l_2
        
    return data

#New version of breadth-first search
def breadth_first_search_with_cartesian_product(g, begin_a, begin_b):
    de = deque()
    visited, inqueue, pred = {}, {}, {} #Use dictionaries because we do not know which nodes we will have

    de.append((begin_a, begin_b))
    visited[(begin_a, begin_b)], inqueue[(begin_a, begin_b)], pred[(begin_a, begin_b)] = False, True, -1
    found, meeting = False, (-1,-1)
    
    while not found and not len(de) == 0:
        a,b = de.popleft()
        visited[(a,b)] = True
        inqueue[(a,b)] = False
        for node_a in AdjacencyList(g, a):
            for node_b in AdjacencyList(g, b):
                if node_a == node_b: #MEETING FOUND!!!
                    meeting = (node_a, node_b)
                    found = True
                v = visited.get((node_a, node_b))
                i = inqueue.get((node_a, node_b))
                
                #If we have not visited yet and it's not in queue
                if (not v or v is None) and (not i or i is None): 
                    de.append((node_a, node_b))
                    inqueue[(node_a, node_b)] = True
                    #Keep the node which we came from, same logic used in breadth-first search with parity
                    pred[(node_a, node_b)] = (a, b)
                    
    return pred, meeting

def track_new_path(pred, new_meeting):
    c = new_meeting
    path = [c]
    #Track new path backwards, same logic used before with directed graphs
    while pred.get((c)) != -1: 
        c = pred.get((c))
        path.insert(0, c)
    return path

#--------------------------
#Printing the final results
#--------------------------

def print_directed_g_results(added_links, path):
    if len(added_links) == 1:
        print_adjustment(added_links[0][0], added_links[0][1])
    else:
        print_two_adjustments(added_links)
    path_a, path_b = [], []
    for p in path:
        path_a.append(p[0])
        path_b.append(p[1])
    print_successful_results(len(path) - 1, path_a, path_b)
 
def print_adjustment(node_A, node_B):
    print("No meeting is possible.")
    print("Adding 1 edge.")
    print("Adding " + str(node_A) + " " + str(node_B) + ".")

def print_two_adjustments(nodes):
    print("No meeting is possible.")
    print("Adding 2 edges.")
    print("Adding " + str(nodes[0][0]) + " " + str(nodes[0][1]) + ".")
    print("Adding " + str(nodes[1][0]) + " " + str(nodes[1][1]) + ".")

def print_successful_results(steps, path_a, path_b):
    for i in range(steps + 1):
        print(str(i) + ": Alice at " + str(path_a[i]) + ", Bob at " + str(path_b[i]))
    print("Meeting at node " + str(path_a[i]) + " at time step " + str(steps) + ".")

def print_failed_results():
    print("No meeting is possible.")
    print("Could not establish a rendezvous by adding edges.")
          
if __name__ == "__main__":
    main()