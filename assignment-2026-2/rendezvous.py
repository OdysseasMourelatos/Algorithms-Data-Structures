import sys

def main():
    n = len(sys.argv)
    if n == 2:
        filename = sys.argv[1]
    elif n == 3:
        filename = sys.argv[2]
        
    f = open(filename)
    contents = list(f)
    len(contents)
    num_nodes = int(contents[0][0])
    num_links = int(contents[0][2])
    connections = []
    for i in range(1, len(contents) - 1):
        node_1 = int(contents[i][0])
        node_2 = int(contents[i][2])
        connections.append([node_1, node_2])
    print(connections)
    begin_a = int(contents[i+1][0])
    begin_b = int(contents[i+1][2])
    print(begin_a)
    print(begin_b)
if __name__ == "__main__":
    main()