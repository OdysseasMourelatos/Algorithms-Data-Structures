import sys
from collections import deque 
import bisect

def main():
    n = len(sys.argv)
    if n == 2:
        filename = sys.argv[1]
    elif n == 3:
        filename = sys.argv[2]
    num_nodes, num_links, connections, begin_a, begin_b = get_txt_data(filename)
    
    g = {}
    
    for connenction in connections:
        node_a = connenction[0]
        node_b = connenction[1]
        value_a = g.get(node_a)
        value_b = g.get(node_b)
        
        if  value_a is None:
            g.update({node_a: [node_b]})
        else:
            value_a.append(node_b)
            g.update({node_a: value_a})
            
        if value_b is None:
            g.update({node_b: [node_a]})
        else:
            value_b.append(node_a)
            g.update({node_b: value_b})
        print(g)
        
    
def get_txt_data(filename):
    f = open(filename)
    contents = list(f)
    f.close()
    
    num_nodes = int(contents[0][0])
    num_links = int(contents[0][2])
    
    connections = []
    for i in range(1, len(contents) - 1):
        node_1 = int(contents[i][0])
        node_2 = int(contents[i][2])
        connections.append([node_1, node_2])
        
    begin_a = int(contents[i+1][0])
    begin_b = int(contents[i+1][2])   
    
    return num_nodes, num_links, connections, begin_a, begin_b

if __name__ == "__main__":
    main()