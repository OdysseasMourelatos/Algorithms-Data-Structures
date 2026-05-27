import sys, argparse, json, re

def main():
    digits = create_digits_dictionary()
    print(digits[0])
    print(digits[2])
    print(digits[0] - digits[2])
    print(digits[2] - digits[0])
    
def create_digits_table():
    digits = [
        {1,2,3,4,5,6}, 
        {2,3},
        {0,1,2,4,5},
        {0,1,2,3,4},
        {0,2,3,6},
        {0,1,3,4,6},
        {0,1,3,4,5,6},
        {1,2,3,6},
        {0,1,2,3,4,5,6},
        {0,1,2,3,4,6}
    ]
    return digits     
    
if __name__ == "__main__":
    main()