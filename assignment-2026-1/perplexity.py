import argparse
import math
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM

def main():
    args = parseArguments()
    model, tokenizer = createModel()
    f_in = open(args.input_file)
    text = f_in.read()
    
    tokens = tokenizer(text).input_ids
    print(len(tokens))
    
    
    write_file(args.out_file, f_in.name)
    
    f_in.close()
    
    
def parseArguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("input_file", help = "name of input file")
    parser.add_argument("out_file", help = "name of output file")
    parser.add_argument("--stride", default = 512, help = "the stride")
    parser.add_argument("--n-ctx", default = 2048, help = "the size of the context window")
    parser.add_argument("--begin-context-tokens", default = 512, help = "the number of tokens that will be used as initial context")
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

def write_file(out_file, input_file_name):
    f_out = open(out_file, 'w')
    f_out.write("Computing perplexity for " + str(input_file_name) + "...")
    f_out.write("\nTokenizing text...")
    f_out.write("\nFound " + 'x' + " tokens") # will soon be a function call
    f_out.write("\nProcessing " + 'x' + " tokens in " + 'y' " window(s).") # will also use function 
    for i in range(4): # 4 is temporary - just for testing purposes
        f_out.write("\nWindow " + str(i+1) + "/4: nll = " ) 
    f_out.write("\nPerplexity: " + 'x') # function call
    f_out.close()
    
if __name__ == "__main__":
    main()