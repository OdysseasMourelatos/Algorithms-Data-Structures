import sys, argparse, json, re

def main():
    #Parsing the arguments
    args = parse_arguments()
    problem, mk = args.problem, args.max_k
    
    #Checking the validity of the problem and getting the numbers & the operator
    global operator
    numbers, operator = check_valid_problem(problem)
    
    #Find number of slots and check if it is greater than 6
    num_slots = 0
    for number in numbers:
        num_slots += len(number)
    if num_slots > 6:
        sys.exit("Too many digits: " + str(num_slots) + ". Maximum is 6.")
        
    global digits
    digits = [int(numbers[0]), int(numbers[1]), int(numbers[2])]
    
    standard_digits = create_digits_table()
    #Will make it work for numbers greater than 10 soon, for now it only works for single digit numbers
    global transformation_table
    computer_digits = get_computer_digits(digits[0], digits[1], digits[2], standard_digits)
    transformation_table = get_transformation_table(standard_digits, mk)

    #Begin the recurssion
    do_slot(0, num_slots)
    
    #Will change the operator once I have found all the solutions with the initial operator
    change_operator()
    o_d = o_r - o_a
    
    

def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("--problem", help = "PROBLEM", required=True)
    parser.add_argument("--max-k", default = 2, help = "MAX_K")
    return parser.parse_args()
     
def check_valid_problem(problem):
    x = re.split(" ", problem)
    numbers = x[0], x[2], x[4]
    operator = x[1]
    equal_sign = x[3]
    if len(x) != 5:
        sys.exit("Invalid problem format")
    elif operator != "+" and operator != "-":
        sys.exit("Invalid operator: " + operator)
    elif equal_sign != "=":
        sys.exit("Problem must contain an equal sign")
    else:
        for number in numbers:
            if not number.isdigit():
                sys.exit("Invalid number: " + number)
    return numbers, operator

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
        digit_dictionary= {}
        #What it requires to be transformed into every digit
        j = 0
        for digit2 in digits:
            j+=1
            added = digit2 - digit1
            removed = digit1 - digit2
            (a, r) = len(added), len(removed)
            d = a - r
            if a > mk or r > mk:
                continue
            digit_dictionary[j-1] = [digit2, added, removed, (a,r), d]
        transformation_table.append(digit_dictionary)
    return transformation_table

o_a, o_r = 0, 0

def change_operator():
    global operator, o_a, o_r
    if operator == "+":
        o_r, operator = 1, "-"
    else:
        o_a, operator = 1, "+"

solution = [-1, -1, -1]

def do_slot(i, ns):
    global solution
    print(solution)
    if i == ns:
        if check_solution():
            print("Solution found")
            return
    for td in current_slot(i):
        if not impossible_to_find_solution(td, i):
            solution[i] = td
            do_slot(i+1, ns)

def check_solution():
    return True
    
def current_slot(i):
    digit = digits[i]
    tds = transformation_table[digit].keys()
    return tds

def impossible_to_find_solution(td, i):
    print("Checking if impossible to find solution")

if __name__ == "__main__":
    main()