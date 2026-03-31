import argparse
import math
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM

def main():
    args = parse_arguments()
    model, tokenizer = create_model()
    f_in = open(args.input_file)
    text = f_in.read()
    tokens = find_tokens(tokenizer, text)
    windows = find_windows(tokens, args.stride, args.n_ctx)
    
    j = 0
    sums=[]
    total_length = 0
    for window in windows:
        logits = get_logits(model, window)
        indexes_for_evaluation = find_logits_indexes_for_evaluation(len(tokens), j, args.stride, args.n_ctx, args.begin_context_tokens)
        total_length += len(indexes_for_evaluation)
        sum = 0
        for i in indexes_for_evaluation:
            log_probs = softmax(logits, i - args.stride*j)
            token = tokens[i+1]
            token_log_prob = log_probs[token] 
            sum += round(token_log_prob, 4)
        print(-sum)
        sums.append(-sum)
        j += 1

    total_sum = 0
    for sum in sums:
        total_sum+=sum
    nll = total_sum / total_length
    print(math.exp(nll))
    
    write_file(args.out_file, f_in.name, tokens, len(windows))
    
    f_in.close()
    

def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("input_file", help = "name of input file")
    parser.add_argument("out_file", help = "name of output file")
    parser.add_argument("--stride", default = 512, help = "the stride")
    parser.add_argument("--n_ctx", default = 2048, help = "the size of the context window")
    parser.add_argument("--begin_context_tokens", default = 512, help = "the number of tokens that will be used as initial context")
    parser.add_argument
    return parser.parse_args()

def create_model():
    model_name = "facebook/opt-125m"
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForCausalLM.from_pretrained(
        model_name, tie_word_embeddings=False
    )
    model.eval()
    return model, tokenizer

def find_tokens(tokenizer, text):
    tokens = tokenizer(text).input_ids
    return tokens

def find_windows(tokens, stride, nctx):
    num_windows = 1
    size = nctx
    windows = []
    windows.append(get_window_tokens(0, nctx, tokens))
    while size < len(tokens):
        num_windows += 1
        size += stride
        windows.append(get_window_tokens(stride*(num_windows-1), nctx + stride*(num_windows-1), tokens))
    return windows

def get_window_tokens(begin_index, last_index, tokens):
    i = begin_index
    window = []
    while i < last_index:
        if (i < len(tokens)):
            window.append(tokens[i])
            i += 1
        else:
            break
    return window

def get_logits(model, window):
    window_tensor = torch.tensor([window])
    with torch.no_grad():
        logits = model(window_tensor).logits
    return logits

def find_logits_indexes_for_evaluation(tokens_length, window_num, stride, n_ctx, begin_context_tokens):
    indexes_for_evaluation = []
    if window_num == 0:
        for j in range(begin_context_tokens -1, n_ctx):
            indexes_for_evaluation.append(j)
    else:
        for j in range(n_ctx + stride*(window_num-1), n_ctx + stride*window_num):
            if j < tokens_length - 1:
                indexes_for_evaluation.append(j)
            else:
                break
    return indexes_for_evaluation
       
def softmax(logits, i):
    row = logits[0,i].tolist()
    max_val = max(row)
    shifted = [x- max_val for x in row]
    log_sum_exp = math.log(sum(math.exp(x) for x in shifted))
    log_probs = [x- log_sum_exp for x in shifted]
    return log_probs

def write_file(out_file, input_file_name, tokens, windows):
    f_out = open(out_file, 'w')
    f_out.write("Computing perplexity for " + str(input_file_name) + "...")
    f_out.write("\nTokenizing text...")
    f_out.write("\nFound " + str(len(tokens)) + " tokens") 
    f_out.write("\nProcessing " + str(len(tokens)) + " tokens in " + str(windows) + " window(s).")
    for i in range(windows):
        f_out.write("\nWindow " + str(i+1) + "/" + str(windows) + ": nll = " ) 
    f_out.write("\nPerplexity: " + 'x') 
    f_out.close()
    
if __name__ == "__main__":
    main()