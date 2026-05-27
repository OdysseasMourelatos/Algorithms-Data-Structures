import sys, argparse, json, re

def main():
    digits = create_digits_dictionary()
    print(digits.get(0))
    print(digits.get(2))
    print(digits.get(0) - digits.get(2))
    print(digits.get(2) - digits.get(0))
    
def create_digits_dictionary():
    digits = {
        0 : {1,2,3,4,5,6}, 
        1 : {2,3},
        2 : {0,1,2,4,5},
        3 : {0,1,2,3,4},
        4 : {0,2,3,6},
        5 : {0,1,3,4,6},
        6 : {0,1,3,4,5,6},
        7 : {1,2,3,6},
        8 : {0,1,2,3,4,5,6},
        9 : {0,1,2,3,4,6}
    }
    return digits     
    
if __name__ == "__main__":
    main()