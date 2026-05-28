import sys, argparse, json, re

def main():
    #Parsing the arguments
    args = parse_arguments()
    problem, mk = args.problem, args.max_k
    
    #Checking the validity of the problem and getting the digits & the operator
    digit1, digit2, digit3, operator = check_valid_problem(problem)
    
    standard_digits = create_digits_table()
    d1, d2, d3 = get_computer_digits(digit1, digit2, digit3, standard_digits)
    transformation_table = get_transformation_table(standard_digits, mk)
    
    print(d1, d2, d3)
    for digit in transformation_table[1]:
        print(digit)

def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("--problem", help = "PROBLEM", required=True)
    parser.add_argument("--max-k", default = 2, help = "MAX_K")
    return parser.parse_args()
     
def check_valid_problem(problem):
    x = re.split(" ", problem)
    digits = x[0], x[2], x[4]
    operator = x[1]
    equal_sign = x[3]
    if len(x) != 5:
        sys.exit("Invalid problem format")
    elif operator != "+" and operator != "-":
        sys.exit("Invalid operator: " + operator)
    elif equal_sign != "=":
        sys.exit("Problem must contain an equal sign")
    else:
        for digit in digits:
            if not digit.isdigit():
                sys.exit("Invalid digit: " + digit)
    return int(digits[0]), int(digits[1]), int(digits[2]), operator

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

def get_computer_digits(digit1, digit2, digit3, standard_digits):
    d1, d2, d3 = standard_digits[digit1], standard_digits[digit2], standard_digits[digit3]
    return d1, d2, d3

def get_transformation_table(digits, mk):
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
            if a > mk or r > mk:
                continue
            digit_table.append([digit2, added, removed, (a,r), d])
        transformation_table.append(digit_table)
    return transformation_table

def do_slot(i, ns):
    if i == ns:
        if check_solution():
            print("Solution found")
            return True
    for td in current_slot():
        if not impossible_to_find_solution():
            do_slot(i+1, ns)

def check_solution():
    print("Checking solution")
    
def current_slot():
    print("Getting current slot")

def impossible_to_find_solution():
    print("Checking if impossible to find solution")

if __name__ == "__main__":
    main()