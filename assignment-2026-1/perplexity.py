import argparse
import math
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM

def main():
    args = parseArguments()
    f_in = open(args.input_file)
    f_out = open(args.out_file, 'w')
    f_out.write("Computing perplexity for " + str(f_in.name) + "...")
    f_out.write("\nTokenizing text...")
    f_in.close()
    f_out.close()
    model = createModel()
       
def createModel():
    model_name = "facebook/opt-125m"
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForCausalLM.from_pretrained(
        model_name, tie_word_embeddings=False
    )
    model.eval()
    return model

def parseArguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("input_file", help = "name of input file")
    parser.add_argument("out_file", help = "name of output file")
    parser.add_argument("--stride", default = 512, help = "the stride")
    parser.add_argument("--n-ctx", default = 2048, help = "the size of the window")
    parser.add_argument("--begin-context-tokens", default = 512, help = "the number of tokens that will be used as context window")
    parser.add_argument
    return parser.parse_args()
    
if __name__ == "__main__":
    main()