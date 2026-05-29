import sys, argparse, json, re

def main():
    #Parsing the arguments
    args = parse_arguments()
    global m_k
    problem, m_k = args.problem, args.max_k
    
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
    transformation_table = get_transformation_table(standard_digits, m_k)
    
    sort_by_cost(digits)
    global range_d_table, suffix_min_max_table
    range_d_table = get_d_range(digits)
    suffix_min_max_table = get_suffix_min_max_table()
    
    #Begin the recurssion
    global t_a, t_r, solutions, o_d
    t_a, t_r, o_d = 0, 0, 0
    do_slot(0, num_slots)
    print(solutions)
    
    #Will change the operator once I have found all the solutions with the initial operator
    change_operator()
    o_d = o_r - o_a
    
    
    #Run again with the new operator
    do_slot(0, num_slots)
    print(solutions)
    
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

def get_transformation_table(digits, m_k):
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
            if a > m_k or r > m_k:
                continue
            digit_dictionary[j-1] = [digit2, added, removed, (a,r), d]
        transformation_table.append(digit_dictionary)
    return transformation_table

def sort_by_cost(digits):
    global transformation_table
    for digit in digits:
        transformation_table[digit] = dict(sorted(transformation_table[digit].items(), key=lambda item: item[1][3]))
o_a, o_r = 0, 0

def get_d_range(digits):
    range_d_table = []
    for digit in digits:
        min_d, max_d = min(transformation_table[digit].items(), key=lambda x: x[1][4]), max(transformation_table[digit].items(), key=lambda x: x[1][4])
        min_d, max_d = min_d[1][4], max_d[1][4]
        range_d = (min_d, max_d)
        range_d_table.append(range_d)
    return range_d_table     
 
def change_operator():
    global operator, o_a, o_r
    if operator == "+":
        o_r, operator = 1, "-"
    else:
        o_a, operator = 1, "+"

proposed_solution = [-1, -1, -1]
solutions = []
nodes_visited = 0
nodes_pruned = 0

def do_slot(i, ns):
    global proposed_solution, solutions, nodes_visited, nodes_pruned
    nodes_visited += 1
    if i == ns:
        if check_solution(proposed_solution):
            solutions.append(proposed_solution.copy())
            proposed_solution[i-1] = -1
        return
    for t_d in current_slot(i):
        if not impossible_to_find_solution(t_d, i, ns):
            proposed_solution[i] = t_d
            do_slot(i+1, ns)
            update_total_additions_and_removals(transformation_table[digits[i]].get(t_d)[3][0], transformation_table[digits[i]].get(t_d)[3][1], add = False)
        else:
            nodes_pruned += 1

def check_solution(solution):
    global t_a, t_r, o_a, o_r
    if t_a + o_a == t_r + o_r:
        if operator == "+":
            return solution[0] + solution[1] == solution[2]
        else:
            return solution[0] - solution[1] == solution[2]
    return False

def current_slot(i):
    digit = digits[i]
    t_ds = transformation_table[digit].keys()
    return t_ds

def impossible_to_find_solution(t_d, i, ns):
    impossible = m_k_check(t_d, i)
    if i < ns - 1:
        impossible = impossible and suffix_check(t_d, i)
    return impossible

def m_k_check(t_d, i):
    global t_a, t_r, m_k
    data = transformation_table[digits[i]].get(t_d)
    update_total_additions_and_removals(data[3][0], data[3][1], add = True)
    if t_a + o_a > m_k or t_r + o_r > m_k:
        update_total_additions_and_removals(data[3][0], data[3][1], add = False)
        return True
    return False

def suffix_check(t_d, i):
    global t_a, t_r, m_k, o_d
    n = o_d - (t_a - t_r) 
    if n < suffix_min_max_table[i][0] or n > suffix_min_max_table[i][1]:
        return True
    return False
    

def get_suffix_min_max_table():
    suffix_min_max_table = []
    for i in range(len(range_d_table) - 1):
        suf_min = min(range_d_table[i+1:], key=lambda x: x[0])[0]
        suf_max = max(range_d_table[i+1:], key=lambda x: x[1])[1]
        table_entry = (suf_min, suf_max)
        suffix_min_max_table.append(table_entry)
    return suffix_min_max_table

def update_total_additions_and_removals(new_a, new_r, add):
    global t_a, t_r
    if add:
        t_a += new_a
        t_r += new_r
    else:
        t_a -= new_a
        t_r -= new_r

if __name__ == "__main__":
    main()