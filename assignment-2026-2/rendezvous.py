import sys

def main():
    n = len(sys.argv)
    if n == 2:
        filename = sys.argv[1]
    elif n == 3:
        filename = sys.argv[2]
    i = 0
    with open(filename) as f:
        for line in f:
            if i == 0:
                num_nodes = int(line[0])
                num_links = int(line[2])
            i+=1
if __name__ == "__main__":
    main()