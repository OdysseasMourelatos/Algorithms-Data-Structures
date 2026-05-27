import sys, argparse, json, re

def main():
    digits = create_digits_table()
    transformation_table = get_transformation_table(digits)
    for digit in transformation_table[1]:
        print(digit)
        
def create_digits_table():
    digits = [
        {1,2,3,4,5,6}, #0
        {2,3}, #1
        {0,1,2,4,5}, #2
        {0,1,2,3,4}, #3
        {0,2,3,6}, #4
        {0,1,3,4,6}, #5
        {0,1,3,4,5,6}, #6
        {1,2,3,6}, #7
        {0,1,2,3,4,5,6}, #8
        {0,1,2,3,4,6} #9
    ]
    return digits     

def get_transformation_table(digits):
    transformation_table=[]
    #For every digit (0,1, .., 9)
    for digit1 in digits:
        digit_table = []
        #What it requires to be transformed into every digit
        for digit2 in digits:
            added = digit2 - digit1
            removed = digit1 - digit2
            (a, r) = len(added), len(removed)
            d = a - r
            if a > 2 or r > 2:
                continue
            digit_table.append([digit2, added, removed, (a,r), d])
        transformation_table.append(digit_table)
    return transformation_table

if __name__ == "__main__":
    main()