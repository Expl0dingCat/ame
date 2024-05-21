import torch
from transformers import LlamaForCausalLM, LlamaTokenizer
from llama_cpp import Llama

class ai:
    def __init__(self, model_file_ext, model_pth, use_gpu=True, context=0, format="chatml", verbose=False, layers=-1, threads=None, lora_pth=None):
        self.model_file_ext = model_file_ext
        self.model_pth = model_pth
        self.use_gpu = use_gpu
        self.context = context
        self.format = format
        self.verbose = verbose
        self.layers = layers
        self.threads = threads
        self.lora_pth = lora_pth
        self.llm = None

        self.load_llm("cuda" if use_gpu else "cpu")
       
    def load_llm(self, device):
        if self.model_file_ext == '.gguf' or self.model_file_ext == '.ggml':
            if device == "cuda":
                self.llm = Llama(model_path=self.model_pth, verbose=self.verbose, n_gpu_layers=self.layers, n_threads=self.threads, n_ctx=self.context, chat_format=self.format, lora_pth=self.lora_pth)
            else:
                self.llm = Llama(model_path=self.model_pth, verbose=self.verbose, n_threads=self.threads, n_ctx=self.context, chat_format=self.format, lora_path=self.lora_pth)
        elif self.model_file_ext == '.safetensors':
            pass

    def generate(self, prompt, tokens=512, temp=0.85, top_p=0.95, top_k=0):
        if self.model_file_ext == '.gguf' or self.model_file_ext == '.ggml':
            response = self.llm.create_chat_completion(messages=prompt, max_tokens=tokens, temperature=temp, top_k=top_k, top_p=top_p)
            
            full_msg = response['choices'][0]['message']
            prompt_tokens = response['usage']['prompt_tokens']
            completion_tokens = response['usage']['completion_tokens']
            text = response['choices'][0]['message']['content']
        elif self.model_file_ext == '.safetensors':
            pass
            return text.strip(), full_msg, prompt_tokens, completion_tokens
    
    def format_prompt(self, messages, format="chatml", with_assistant_prompt=True):
        result = ""
        current_role = None

        if format == "chatml":
            for message in messages:
                role = message["role"]
                content = message["content"]

                if role != current_role:
                    current_role = role
                    result += f'<|im_start|>{role}\n'

                result += f'{content}<|im_end|>\n'

            if with_assistant_prompt:
                result += '<|im_start|>assistant\n'
        else:
            raise ValueError(f"Invalid or unsupported format: {format}")
    
    def get_token_amt(self, text):
        return len(self.llm.tokenize(text.encode('utf-8')))
