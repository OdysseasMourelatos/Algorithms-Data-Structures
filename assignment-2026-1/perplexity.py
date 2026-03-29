import argparse
import math
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM

def main():
    args = parseArguments()
    model, tokenizer = createModel()
    f_in = open(args.input_file)
    text = f_in.read()
    tokens = find_tokens(tokenizer, text)
    windows = find_windows(tokens, args.stride, args.n_ctx)
    
    write_file(args.out_file, f_in.name, tokens, windows)
    
    f_in.close()
    

def parseArguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("input_file", help = "name of input file")
    parser.add_argument("out_file", help = "name of output file")
    parser.add_argument("--stride", default = 512, help = "the stride")
    parser.add_argument("--n_ctx", default = 2048, help = "the size of the context window")
    parser.add_argument("--begin_context_tokens", default = 512, help = "the number of tokens that will be used as initial context")
    parser.add_argument
    return parser.parse_args()

def createModel():
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
    while size < len(tokens):
        num_windows += 1
        size += stride
    return num_windows

def get_window_tokens(begin_index, window_size, tokens):
    i = begin_index
    window = []
    while i < window_size:
        window.append(tokens[i])
        i += 1
    return window
    
def write_file(out_file, input_file_name, tokens, windows):
    f_out = open(out_file, 'w')
    f_out.write("Computing perplexity for " + str(input_file_name) + "...")
    f_out.write("\nTokenizing text...")
    f_out.write("\nFound " + str(len(tokens)) + " tokens") 
    f_out.write("\nProcessing " + str(len(tokens)) + " tokens in " + str(windows) + " window(s).")
    for i in range(windows):
        f_out.write("\nWindow " + str(i+1) + "/" + str(windows) + ": nll = " ) 
    f_out.write("\nPerplexity: " + 'x') # function call
    f_out.close()
    
if __name__ == "__main__":
    main()