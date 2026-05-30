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
    
    #Seperate digits and numbers
    global digits, standard_digits, numbers_length
    digits, numbers_length = [], []
    for number in numbers:
        length = len(number)
        digits.append(int(number[0]))
        if length == 2: #If we have a number with 2 digits
            digits.append(int(number[1]))
        numbers_length.append(length) #Keep the length of each number
    
    #Create standard digits
    standard_digits = create_digits_table()
    
    #Get the transformation table
    global transformation_table
    transformation_table = get_transformation_table(standard_digits, m_k)
    
    #Sort so that we visit the nodes with the least amount of moves first
    sort_by_cost(digits)
    
    #Get the 2 tables needed for our second check (Check(2))
    global range_d_table, suffix_min_max_table
    range_d_table = get_d_range(digits)
    suffix_min_max_table = get_suffix_min_max_table()
    
    #Track each proposed solution, starting from [-1, ..., -1] to indicate absence of digits
    global proposed_solution
    proposed_solution = [-1 for i in range(num_slots)]
    
    #Begin the recurssion
    global t_a, t_r, solutions, o_d
    t_a, t_r, o_d = 0, 0, 0
    if operator != '+': #Change it to + first
        change_operator()
        o_d = o_r - o_a
    do_slot(0, num_slots)
    
    #Change the operator once I have found all the solutions with the initial operator
    change_operator()
    o_d = o_r - o_a
    #Run again with the new operator
    do_slot(0, num_slots)
    
    print(solutions)
    print(nodes_visited, nodes_pruned)
    print(moves)

def build_results(problem, m_k, counts, nodes_visited, nodes_pruned, solutions, moves):
    print()

#Parse the arguments  
def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("--problem", help = "PROBLEM", required=True)
    parser.add_argument("--max-k", default = 2, help = "MAX_K")
    return parser.parse_args()
    
#Check the validation of the problem given by the user
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

#Standard digits table
def create_digits_table():
    standard_digits = [
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
    return standard_digits     

#Build the transformation table for each digit
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
            if a > m_k or r > m_k: #Then it can't be transformed with limited amount of moves
                continue #Skip it
            #Add to the table: the digit for transformation, what was added, what was removed, (cost of addition & cost of removal), d = a - r
            digit_dictionary[j-1] = [digit2, added, removed, (a,r), d]
        #Add it to a huge table for all digits
        transformation_table.append(digit_dictionary)
    return transformation_table

#Sorting the transformation by cost so that we visit the ones with less moves first
def sort_by_cost(digits):
    global transformation_table, numbers_length
    for digit in digits:
        transformation_table[digit] = dict(sorted(transformation_table[digit].items(), key=lambda item: item[1][3][0] + item[1][3][1]))
        
o_a, o_r = 0, 0
#Change the operator from + to - and from - to +
def change_operator():
    global operator, o_a, o_r
    if operator == "+":
        o_r, operator = 1, "-"
    else:
        o_a, operator = 1, "+"

#The range of d = a - c for each digit, to use it in order to cut early impossible solutions
def get_d_range(digits):
    range_d_table = []
    for digit in digits:
        min_d, max_d = min(transformation_table[digit].items(), key=lambda x: x[1][4]), max(transformation_table[digit].items(), key=lambda x: x[1][4])
        min_d, max_d = min_d[1][4], max_d[1][4] #D is located in the last position of the table
        range_d = (min_d, max_d)
        range_d_table.append(range_d)
    return range_d_table     

#Based on the d_range, find the suffix table
def get_suffix_min_max_table():
    suffix_min_max_table = []
    for i in range(len(range_d_table) - 1):
        suf_min, suf_max = 0,0 
        for j in range(i+1, len(range_d_table)): 
            suf_min += range_d_table[j][0]
            suf_max += range_d_table[j][1]
        table_entry = (suf_min, suf_max)
        suffix_min_max_table.append(table_entry)
    return suffix_min_max_table

solutions = []
nodes_visited = 0
nodes_pruned = 0

#The most important function - the recurssion which finds the solution in the perfect order
def do_slot(i, ns):
    global proposed_solution, solutions, nodes_visited, nodes_pruned, t_a, t_r
    nodes_visited += 1 #Increase it by one every time we call the algorithm
    if i == ns:
        if check_solution(proposed_solution): #Check the validity of the equation
            solutions.append([proposed_solution.copy(), nodes_visited, nodes_pruned]) #Add it as a solution
            find_moves(proposed_solution) #Get its moves
            proposed_solution[i-1] = -1 #Change the proposed solution back to -1 (indicates empty spot)
        return
    for t_d in current_slot(i):
        if not impossible_to_find_solution(t_d, i, ns): #If it passes all tests
            proposed_solution[i] = t_d #Track the digit
            do_slot(i+1, ns) #Recurssive call
            #When the recurssion is finished, we decrease t_a & t_r since we're finished with this particular t_d
            update_total_additions_and_removals(transformation_table[digits[i]].get(t_d)[3][0], transformation_table[digits[i]].get(t_d)[3][1], add = False)
        else:
            nodes_pruned += 1 #Track the nodes we rejected

moves = []
#Find the moves for each solution
def find_moves(solution):
    global digits, transformation_table, moves, standard_digits
    additions, removals = [], []
    for i in range(len(solution)): #eg in 2 + 4 = 6, i = 1, 2, 3
        addition = list(transformation_table[digits[i]].get(solution[i])[1]) #In the first position it's what we added
        removal = list(transformation_table[digits[i]].get(solution[i])[2]) #In the second it's what we removed
        letter = chr(ord('A')+i) #1=A, 2=B, 3=C, if there's 4, 4=D ...
        for j in range(len(addition)): #We could've added more than 1 to get to this letter
            additions.append(letter + str(addition[j]))
        for j in range(len(removal)): #We could've removed more than 1 to get to this letter
            removals.append(letter + str(removal[j])) 
    moves.append((removals, additions))

#Check the validity of the equation
def check_solution(solution):
    numbers = []
    i = 0
    for n in numbers_length: 
        if n == 2: #If the number is composed by 2 digits
            number = str(solution[i]) + str(solution[i+1])
        else: #Then it's only 1 digit
            number = solution[i]
        i+=n
        numbers.append(int(number))
    if operator == "+":
        return numbers[0] + numbers[1] == numbers[2]
    else:
        return numbers[0] - numbers[1] == numbers[2]

#Find the digits in which digit[i] can be transformed to
def current_slot(i):
    digit = digits[i]
    t_ds = transformation_table[digit].keys()
    return t_ds

#This function rejects solution early
def impossible_to_find_solution(t_d, i, ns):
    global t_a, t_r, o_a, o_r
    impossible = m_k_check(t_d, i, ns) #Check(1)
    if i < ns - 1 and not impossible: #If we're not in the last slot and it's not impossible to find a solution
        impossible = suffix_check(t_d, i) #Check(2)
    return impossible

#Check(1)
def m_k_check(t_d, i, ns):
    global t_a, t_r, m_k
    data = transformation_table[digits[i]].get(t_d)
    update_total_additions_and_removals(data[3][0], data[3][1], add = True) #Try to increase t_a & t_r accordingly
    if t_a + o_a > m_k or t_r + o_r > m_k: #if what we're trying to add or remove is greater than our limit, we stop immediately 
        update_total_additions_and_removals(data[3][0], data[3][1], add = False) #Failed, so remove them
        return True

    if i == ns - 1 and t_a + o_a != t_r + o_r: #If we're in the last slot and there's no way in which we can balance additions & removals
        update_total_additions_and_removals(data[3][0], data[3][1], add = False) #Failed, so remove them
        return True
        
    return False

#Check(2)
def suffix_check(t_d, i):
    global t_a, t_r, m_k, o_d
    n = o_d - (t_a - t_r) #Find what we're missing 
    if n < suffix_min_max_table[i][0] or n > suffix_min_max_table[i][1]: #If it's impossible to cover in the next positions, cut it early
        #Remove them since m_k check had added them
        update_total_additions_and_removals(transformation_table[digits[i]].get(t_d)[3][0], transformation_table[digits[i]].get(t_d)[3][1], add = False)
        return True
    return False
    
#Update t_a and t_r accordingly
def update_total_additions_and_removals(new_a, new_r, add):
    global t_a, t_r
    if add:
        t_a += new_a
        t_r += new_r
    else:
        t_a -= new_a
        t_r -= new_r

#Print the output in json form
def print_json_output(results):
    json_output = json.dumps(results, indent=2)
    print(json_output)

if __name__ == "__main__":
    main()