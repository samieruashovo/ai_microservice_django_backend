from transformers import AutoTokenizer, AutoModelForCausalLM, TextStreamer
import torch
import os

MODEL_DIR = "/home/samier/Documents/llm-models/gemma-3-270m"

print("Loading tokenizer...")
tokenizer = AutoTokenizer.from_pretrained(
    MODEL_DIR,
    local_files_only=True
)

print("Loading model...")
model = AutoModelForCausalLM.from_pretrained(
    MODEL_DIR,
    torch_dtype=torch.float32,    # use float32 for CPU
    local_files_only=True
)

model.eval()

def generate_response(prompt: str, max_tokens=200):
    inputs = tokenizer(prompt, return_tensors="pt")
    outputs = model.generate(
        **inputs,
        max_new_tokens=max_tokens,
        do_sample=True,
        temperature=0.7,
        top_p=0.9
    )
    return tokenizer.decode(outputs[0], skip_special_tokens=True)
