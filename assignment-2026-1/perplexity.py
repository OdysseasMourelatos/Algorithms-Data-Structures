import argparse
import math
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM

def main():
    #Parsing the arguments
    args = parse_arguments()
    
    #Creating the model & getting the BOS token
    model, tokenizer = create_model()
    bos_token = tokenizer.bos_token_id
    
    #Reading the file
    f_in = open(args.input_file)
    text = f_in.read()
    
    #Getting ALL the tokens
    tokens = find_tokens(tokenizer, text)
    
    #Getting the tokens of EACH window
    windows = find_windows(tokens, args.stride, args.n_ctx, bos_token)
    
    #Initialization
    j = 0
    sums=[]
    total_length = 0
   
    #Outer loop - for every window
    for window in windows:
        #Gives us the logits of each window
        logits = get_logits(model, window)
        
        #Finding the indexes of the window which we'll use to evaluate our model
        indexes_for_evaluation = find_window_indexes_for_evaluation(len(window), j, args.stride, args.n_ctx, args.begin_context_tokens)
        total_length += len(indexes_for_evaluation)
        sum = 0
        
        #Inner loop - for every index inside the window that we'll use for evaluation
        for i in indexes_for_evaluation:
            #Gives us the probabilities of EACH word in the dictionary of the model, using the function softmax
            log_probs = softmax(logits, i)
            #Finding ONLY the token that we care about, all the other words are not needed anymore
            token = window[i+1]
            token_log_prob = log_probs[token] 
            sum += token_log_prob
        sums.append(-sum)
        j += 1

    #Final Calculations
    total_sum = 0
    for sum in sums:
        total_sum+=sum
    nll = total_sum / total_length

    #Output as a file
    write_file(args.out_file, f_in.name, tokens, len(windows), sums, math.exp(nll))
    
    f_in.close()
    
#Parsing the arguments as described 
def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("input_file", help = "name of input file")
    parser.add_argument("out_file", help = "name of output file")
    parser.add_argument("--stride", default = 512, help = "the stride")
    parser.add_argument("--n_ctx", default = 2048, help = "the size of the context window")
    parser.add_argument("--begin_context_tokens", default = 512, help = "the number of tokens that will be used as initial context")
    parser.add_argument
    return parser.parse_args()

#Creating the model using the code given to us by our professor
def create_model():
    model_name = "facebook/opt-125m"
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForCausalLM.from_pretrained(
        model_name, tie_word_embeddings=False
    )
    model.eval()
    return model, tokenizer

#Transforming the words given in text into tokens
def find_tokens(tokenizer, text):
    tokens = tokenizer(text).input_ids
    return tokens

#Allows us to get the tokens of each window
def find_windows(tokens, stride, nctx, BOS):
    #For the first window
    num_windows = 1
    size = nctx
    windows = []
    windows.append(get_window_tokens(0, nctx, tokens, BOS))
    
    #For every other window until we reach the end, increasing by stride each time 
    while size < len(tokens):
        num_windows += 1
        size += stride
        begin_index = stride*(num_windows-1)
        last_index = nctx + stride*(num_windows-1)
        windows.append(get_window_tokens(begin_index, last_index, tokens, BOS))
    return windows

#Sends back the tokens of 1 window per time
def get_window_tokens(begin_index, last_index, tokens, BOS):
    i = begin_index
    window = []
    
    #If it's not the first window
    if begin_index!=0:
        #Add the BOS
        window.append(BOS)
        #Skip first index to make way for the BOS
        i+=1
        
    #Add the elements to the window
    while i < last_index:
        if (i < len(tokens)):
            window.append(tokens[i])
            i += 1
        else:
            break
    return window

#Gives us the logits of a certain row, using the code our professor gave us
def get_logits(model, window):
    window_tensor = torch.tensor([window])
    with torch.no_grad():
        logits = model(window_tensor).logits
    return logits

#Finds ONLY the indexes of each window that we'll use to evaluate the model
def find_window_indexes_for_evaluation(window_length, window_num, stride, n_ctx, begin_context_tokens):
    indexes_for_evaluation = []
    
    #For the first window - special treatment
    if window_num == 0:
        for j in range(begin_context_tokens, n_ctx):
            indexes_for_evaluation.append(j - 1)
            
    #For every other window we increase by stride
    else:
        for j in range(n_ctx - stride, n_ctx):
            if j < window_length:
                indexes_for_evaluation.append(j - 1)
            else:
                break
    return indexes_for_evaluation

#Softmax function using the code our professor gave us - converts logits into probabilities
def softmax(logits, i):
    row = logits[0,i].tolist()
    max_val = max(row)
    shifted = [x- max_val for x in row]
    log_sum_exp = math.log(sum(math.exp(x) for x in shifted))
    log_probs = [x- log_sum_exp for x in shifted]
    return log_probs

#Final output to the user as a file
def write_file(out_file, input_file_name, tokens, windows, sums, perplexity):
    f_out = open(out_file, 'w')
    f_out.write("Computing perplexity for " + str(input_file_name) + "...")
    f_out.write("\nTokenizing text...")
    f_out.write("\nFound " + str(len(tokens)) + " tokens") 
    f_out.write("\nProcessing " + str(len(tokens)) + " tokens in " + str(windows) + " window(s).")
    for i in range(windows):
        f_out.write("\nWindow " + str(i+1) + "/" + str(windows) + ": nll = " + str(round(sums[i],4)) ) 
    f_out.write("\nPerplexity: " + str(round(perplexity,2))) 
    f_out.close()
    
if __name__ == "__main__":
    main()