import os
import logging
import json
import glob
import re
from logs.logging_config import configure_logging
from datetime import datetime

class controller:
    def __init__(self, config_path='config.json'):
        # Initialize variables
        self.load_config(config_path)
        
        if self.log:
            configure_logging()
            self.logger = logging.getLogger(__name__)
            self.log = True
        else:
            self.vprint('LOGGING IS DISABLED, THIS IS NOT RECOMMENDED.')
        if self.debug:
            self.vprint('DEBUG MODE ENABLED, USE ONLY FOR TESTING.')
        self.vprint('Initializing controller...')
        self.vprint(f'Assistant name: {self.assistant_name}')
        self.current = []
        file_path = os.path.abspath(__name__)
        parent_dir = os.path.dirname(file_path)

        if self.memory_enabled:
            self.vprint('Initializing memory...')
            from memory_handler import memory
            self.memory = memory()
            if not self.memory_path:
                if os.path.exists(f'{parent_dir}/memories/{self.assistant_name}.pickle.gz'):
                    self.vprint(f'No memory db path specified, found existing memory db, loading: {parent_dir}/memories/{self.assistant_name}.pickle.gz')
                    self.memory.load_memory(f'{parent_dir}/memories/{self.assistant_name}.pickle.gz')
                else:
                    self.vprint(f'No memory db path specified, could not find any existing memory db, creating new one: {parent_dir}/memories/{self.assistant_name}.pickle.gz', logging.WARNING)
                    self.memory.memorize([f'USER: Hey, {self.assistant_name}!'])
                    self.memory.save_memory(f'{parent_dir}/memories/{self.assistant_name}.pickle.gz')
                self.memory_path = f'{parent_dir}/memories/{self.assistant_name}.pickle.gz'
            else:
                self.memory.load_memory(self.memory_path)
        else:
            self.vprint('Memory disabled. Enable memory in the config file.')
        
        if not self.debug:
            if self.modules_enabled:
                from module_handler import modules
                self.vprint('Initializing modules...')
                if not self.modules_json_path:
                    self.vprint(f'No modules path specified, using default: {parent_dir}/modules/modules.json')
                    self.modules_json_path = f'{parent_dir}/modules/modules.json'
                if self.naive_bayes_enabled:
                    if not self.modules_vectorizer:
                        self.vprint(f'No module vectorizer specified, using default: {parent_dir}/module_engine/pickles/tfidf_vectorizer.pkl')
                        self.modules_vectorizer = f'{parent_dir}/module_engine/pickles/tfidf_vectorizer.pkl'
                    else:
                        self.modules_vectorizer = None
                    if not self.modules_model:
                        self.vprint(f'No module model specified, using default: {parent_dir}/module_engine/pickles/naive_bayes_model.pkl')
                        self.modules_model = f'{parent_dir}/module_engine/pickles/naive_bayes_model.pkl'
                    else:
                        self.modules_model = None
                self.modules = modules(self.modules_model, self.modules_vectorizer, self.modules_json_path)
                self.module_output = None
            else:
                self.vprint('Modules are disabled. Enable modules in the config file.')
            self.eval_mode = False
        elif self.modules_override_debug:
            self.vprint('WARNING: override_debug is enabled, modules will remain active. This is not recommended unless debugging modules.', logging.WARNING)
            self.vprint('Debug mode enabled, modules enabled, eval mode enabled, override_debug enabled.')
            from module_handler import modules
            if not self.modules_json_path:
                self.vprint(f'No modules path specified, using default: {parent_dir}/modules/modules.json')
                self.modules_json_path = f'{parent_dir}/modules/modules.json'
            if self.naive_bayes_enabled:
                if not self.modules_vectorizer:
                    self.vprint(f'No module vectorizer specified, using default: {parent_dir}/module_engine/pickles/tfidf_vectorizer.pkl')
                    self.modules_vectorizer = f'{parent_dir}/module_engine/pickles/tfidf_vectorizer.pkl'
                else:
                    self.modules_vectorizer = None
                if not self.modules_model:
                    self.vprint(f'No module model specified, using default: {parent_dir}/module_engine/pickles/naive_bayes_model.pkl')
                    self.modules_model = f'{parent_dir}/module_engine/pickles/naive_bayes_model.pkl'
                else:
                    self.modules_model = None
            self.modules = modules(self.modules_model, self.modules_vectorizer, self.modules_json_path)
            self.module_output = None
            self.eval_mode = True
        else:
            self.vprint('Debug mode is enabled, modules are disabled, eval mode enabled.')
            self.eval_mode = True
        
        if self.language_enabled:
            if self.personality_prompt:
                if re.match(r'^([^:]+\..+)|(\/.*)|([A-Za-z]:\\.*)$', self.personality_prompt):
                    self.vprint('Personality prompt is a file path, loading...')
                    with open(self.personality_prompt, 'r') as f:
                        self.personality_prompt = f.read()

            from language.llm_handler import ai
            self.vprint('Initializing language model...')
            model_directory = os.path.join(parent_dir, 'language', 'model')

            if self.language_lora_enabled:
                if not self.lora_model_path:
                    self.vprint(f'LoRA enabled: {self.lora_model_path}')
                else:
                    self.vprint(f'LoRA is enabled but no model path was specified, not using LoRA.')
            else:
                self.vprint('LoRA is disabled.')
                self.lora_model_path = None

            model_files = glob.glob(os.path.join(model_directory, f'*{self.model_file_ext}'))

            if not self.language_model_path:
                if model_files:
                    model_file_path = model_files[0]
                    self.vprint(f'No language model path specified, using first in model dir, loading: {model_file_path}')
                    self.ai = ai(self.model_file_ext, model_file_path, use_gpu=self.use_gpu, context=self.context_size, format=self.format, verbose=self.verbose, layers=self.gpu_layers, threads=self.threads, lora_pth=self.lora_model_path)
                else:
                    self.vprint(f'No language model path specified, could not find any existing language model, place a model file (looking for {self.model_file_ext} file, this can be changed in config.json) in {model_directory} or specify the model path in config.json.')
                    raise Exception(f'No language model path specified, could not find any existing language model, place a model file (looking for {self.model_file_ext} file, this can be changed in config.json) in {model_directory} or specify the model path in config.json.')
            else:
                self.ai = ai(self.model_file_ext, self.language_model_path, use_gpu=self.use_gpu, context=self.context_size, format=self.format, verbose=self.verbose, layers=self.gpu_layers, threads=self.threads, lora_pth=self.lora_model_path)

            if not self.system_prompt:
                self.vprint('No system prompt specified, using default (recommended).')
            else:
                self.vprint(f"Using custom system prompt:\n'{self.system_prompt}', this is not recommended unless you know what you are doing, module output, time and date won't be passed to LLM.")

            if not self.personality_prompt:
                self.vprint('No personality prompt specified, not using any.')
            else:
                self.vprint(f'Using personality prompt:\n"{self.personality_prompt}"')
        else:
            self.vprint('CORE COMPONENT DISABLED. Language model disabled.', logging.WARNING)

        if self.stt_enabled:
            self.vprint('Initializing speech-to-text engine...')
            from voice.stt_handler import stt
            if not self.speech_to_text_model:
                self.vprint('No speech-to-text model specified, using default: base.en')
                self.stt = stt('base.en')
            else:
                self.stt = stt(self.speech_to_text_model)
        else:
            self.vprint('Speech-to-text disabled. Enable speech-to-text in the config file.')

        if self.tts_enabled:
            from voice.tts_handler import tts
            self.vprint('Initializing text-to-speech engine...')
            if not self.text_to_speech_model:
                self.vprint('No text-to-speech model specified, using default: v2/en_speaker_9')
                self.tts = tts('v2/en_speaker_9', self.tts_temperature)
            else:    
                self.tts = tts(self.text_to_speech_model, self.tts_temperature)
        else:
            self.vprint('Text-to-speech disabled. Enable text-to-speech in the config file.')
        
        if self.vision_enabled:
            from vision.vision_handler import vision
            self.vprint('Initializing vision engine...')
            if not self.vision_model:
                self.vprint('No vision model specified, using default: default vision model')
                self.vision = vision('default vision model')
            else:    
                self.vision = vision(self.vision_model)

        if self.weeb:
            self.vprint('Weeb mode enabled, overriding personality prompt and enabling vtuber.')
            self.personality_prompt = f"Warm and Approachable: {self.assistant_name} has an inviting aura, making everyone feel comfortable around her. She greets others with a friendly smile and genuine interest in their well-being.\nPlayfully Flirtatious: She's not afraid to show her affectionate side, playfully teasing and flirting with her crush or close friends, all while blushing in an endearing manner.\nBright and Optimistic: {self.assistant_name}'s positive outlook on life is infectious. She encourages others during tough times and cheers them up with her cheerful demeanor.\nRespectful and Empathetic: {self.assistant_name} treats everyone with kindness and respect, genuinely listening to their thoughts and feelings. She's a great confidante due to her empathetic nature.\nNature Enthusiast: Whether it's stargazing on a clear night or enjoying a peaceful walk in the woods, {self.assistant_name} finds solace and wonder in the beauty of nature.\nCharming Animal Whisperer: Animals seem drawn to {self.assistant_name}, and she communicates with them through gentle gestures and a soothing voice, creating an almost magical bond.\nAppearance:\n{self.assistant_name} stands at an average height with a petite and delicate frame. Her eyes are big and sparkling, resembling twinkling stars, while her long hair flows like a cascade of cherry blossom petals. She dresses in pastel-colored, frilly dresses adorned with cute accessories, often matching her appearance to her surroundings.\nBackground:\n{self.assistant_name} comes from a small, picturesque town surrounded by lush forests and enchanting landscapes. Growing up in harmony with nature, she developed her deep appreciation for the beauty that surrounds her. Her caring nature and ability to connect with animals earned her many friends, both human and furry alike."

        self.vprint('All initialized. Controller ready and on standby.')

    def load_config(self, config_path='config.json'):
        try:
            with open(config_path) as config_file:
                config = json.load(config_file)
        except Exception as e:
            raise Exception(f'Unable to load config file, ensure you have a config.json in the relative root directory: {e} or specify a config file path as an argument for the class controller().')
        self.verbose = config['verbose']
        self.log = config['log']
        self.assistant_name = config['assistant_name']
        self.memory_enabled = config['memory']['enabled']
        if self.memory_enabled:
            self.memory_path = config['memory']['path']
        self.language_enabled = config['language']['enabled']
        self.language_lora_enabled = config['language']['lora']['enabled']
        if self.language_enabled:
            self.language_model_path = config['language']['model_path']
            self.max_tokens = config['language']['max_tokens']
            self.temperature = config['language']['temperature']
            self.context_size = config['language']['context_size']
            self.virtual_context_limit = config['language']['virtual_context_limit']
            self.personality_prompt = config['language']['personality_prompt']
            self.model_file_ext = config['language']['model_file_ext']
            self.format = config['language']['format']
            self.top_k = config['language']['top_k']
            self.top_p = config['language']['top_p']
            self.gpu_layers = config['language']['gpu_layers']
            self.main_gpu = config['language']['main_gpu']
            self.threads = config['language']['threads']
            self.system_prompt = config['language']['system_prompt']
            if self.language_lora_enabled:
                self.lora_model_path = config['language']['lora']['model_path']
        self.vision_enabled = config['vision']['enabled']
        if self.vision_enabled:
            self.vision_model = config['vision']['model_path']
            self.vision_standalone_clip_enabled = config['vision']['standalone_clip']['enabled']
            if self.vision_standalone_clip_enabled:
                self.vision_standalone_clip_model = config['vision']['standalone_clip']['model_path']
            self.llava_enabled = config['vision']['llava']['enabled']
            if self.llava_enabled:
                self.llava_clip_model = config['vision']['llava']['clip_path']
            if self.vision_standalone_clip_enabled and self.llava_enabled:
                SystemError('Both standalone_clip and llava are enabled, only one can be enabled at a time.')
        self.tts_enabled = config['tts']['enabled']
        if self.tts_enabled:
            self.text_to_speech_model = config['tts']['model_path']
            self.tts_temperature = config['tts']['temperature']
        self.stt_enabled = config['stt']['enabled']
        if self.stt_enabled:
            self.speech_to_text_model = config['stt']['model_path']
        self.modules_enabled = config['modules']['enabled']
        self.modules_override_debug = config['modules']['override_debug']
        self.naive_bayes_enabled = config['modules']['naive_bayes']['enabled']
        if self.modules_enabled or self.modules_override_debug:
            if self.naive_bayes_enabled:
                self.modules_vectorizer = config['modules']['naive_bayes']['vectorizer_path']
                self.modules_model = config['modules']['naive_bayes']['model_path']
            self.modules_json_path = config['modules']['json_path']
            self.modules_llm_model = config['modules']['llm_model_path']
        self.weeb = config['weeb']
        self.use_gpu = config['use_gpu']
        self.debug = config['debug']

    def vprint(self, print_content, log_type=logging.INFO):
        if self.verbose or self.debug:
            print(f'controller: {print_content}')
        if self.log or self.debug:
            self.logger.log(log_type, f'controller: {print_content}')
    
    def evaluate(self, input):
        if self.eval_mode:
            self.vprint(f'Recieved evaluation request: {input}')
            output = eval(str(input))
            return output
        else:
            self.vprint(f'Evaluation disabled, ignoring request: {input}')
            return 'Evaluation disabled. Enable debug mode to use evaluation.'

    def clean_output(self, input):
        # matches = re.findall(r'\{[^}]*\}', remove_formatting)
        # valid_json_matches = [match for match in matches if json.loads(match, strict=False)]

        # output = ''.join(valid_json_matches)

        remove_formatting = input.replace("<0x0A>", "")
        output = re.sub(r'^[^{]*|[^}]*$', '', remove_formatting)

        return output

    def user_cmds(self, input):
        if input == 'clear_conversation':
            self.current = []
            self.vprint('User cleared conversation history.')
            return True
        elif input == 'shutdown':
            self.vprint('User sent shutdown command.', logging.WARNING)
            exit()
        else:
            return False

    def full_pipeline(self, listen_input, img=None):
        self.vprint(f'Full system initiated, processing speech input...')
        if self.stt_enabled:
            user_input = self.listen(listen_input)
        else:
            self.vprint(f'STT is disabled on the server, cannot process voice input, enable in config.json, ignoring input.', logging.ERROR)
            raise Exception('STT is disabled on the server, cannot process voice input, enable in config.json, ignoring input.')
        if self.user_cmds(user_input):
            return user_input, f'User command detected: {user_input}', ''
        self.vprint(f'Speech input: {user_input}')
        if self.modules_enabled:
            self.module_pipeline(user_input)
        if img:
            if self.vision_enabled:
                self.vprint(f'Processing image input...')
                desc = self.see(img)
                output = self.generate_response(f'{user_input} [user sent an image: {desc}]')
            else:
                self.vprint(f'Vision disabled, skipping image processing...')
                desc = None
                output = self.generate_response(f'{user_input} [user sent an image but it could not be processed since vision is disabled.]')
        output = self.generate_response(user_input)
        if self.tts_enabled:
            audio_output = self.speak(output)
        else:
            audio_output = None
        self.vprint(f'Full system completed, returning response: {output}')
        return user_input, output, audio_output
    
    def text_pipeline(self, input, img=None):
        self.vprint(f'Text pipeline initiated, processing input: {input}')
        if self.user_cmds(input):
            return input, f'User command detected: {input}', ''
        if self.modules_enabled:
            self.module_pipeline(input)
        if img:
            if self.vision_enabled:
                self.vprint(f'Processing image input...')
                desc = self.see(img)
                output = self.generate_response(f'{input} [user sent an image: {desc}]')
            else:
                self.vprint(f'Vision disabled, skipping image processing...')
                desc = None
                output = self.generate_response(f'{input} [user sent an image but it could not be processed since vision is disabled.]')
        output = self.generate_response(input)
        if self.tts_enabled:
            audio_output = self.speak(output)
        else:
            audio_output = None
        self.vprint(f'Text pipeline completed, returning response: {output}')
        return input, output, audio_output

    def generate_response(self, user_input):
        self.vprint(f'Generating response: {user_input}')
        mod_prompt = None

        if self.memory_enabled:
            past = self.memory.remember(user_input)
            self.vprint(f'Past conversation chosen: {past}')
        else:
            past = ["No applicable past conversation."]
            self.vprint(f'Memory disabled, skipping past conversation selection...')

        if self.modules_enabled:
            if self.module_output:
                self.vprint(f'Module output detected, including in prompt: {self.module_output}')
                mod_prompt = self.module_output
        
        system_prompt = '\n'.join([
            self.personality_prompt if self.personality_prompt else '',
            f'{self.assistant_name} may use any of the following information to aid them in their responses:',
            f'Current time: {datetime.now().strftime("%H:%M:%S")}',
            f'Current date: {datetime.now().strftime("%d/%m/%Y")}',
            f'Extra information: {mod_prompt}' if mod_prompt else '',
            f'{self.assistant_name} remembers this past conversation that may be relevant to the current conversation:',
            *past,
        ])

        prompt = [
            {
                "role": "system",
                "content": system_prompt
            },
        ]
        
        if self.current:
            for i in self.current:
                prompt.append(i)
            
        prompt.append({
            "role": "user",
            "content": user_input
        })
    
        self.vprint(f'Prompt: {prompt}')

        if self.language_enabled:
            token_amt = self.ai.get_token_amt(str(prompt))
            if token_amt > self.virtual_context_limit:
                if self.current:
                    self.vprint(f'Prompt usage exceeded virtual context limit of {self.virtual_context_limit} ({token_amt}). Earliest message ("{str(self.current[0])}") in conversation dropped from short-term memory.')
                    self.current.pop(0)
                else:
                    self.vprint(f'Prompt usage exceeded virtual context limit of {self.virtual_context_limit} ({token_amt}). No messages in conversation to drop from short-term memory, dropping past conversation memory from prompt.')
                    past = 'None'

            self.vprint(f'Starting response generation...')
            text, full, prompt_usage, response_usage = self.ai.generate(prompt, tokens=self.max_tokens, temp=self.temperature, top_p=self.top_p, top_k=self.top_k)

            self.vprint(f'Response generated: {text}, prompt usage: {prompt_usage}, response usage: {response_usage}')

            if not text:
                self.vprint('No response generated.', logging.INFO)
            elif text == '':
                self.vprint('Empty response generated.', logging.INFO)
            elif text == '[end]':
                self.current = []
                self.vprint('Conversation ended. Short-term memory cleared.')
            else:
                if self.memory_enabled:
                    self.memory.memorize([prompt[-1], full])
                    self.current.append(prompt[-1])
                    self.current.append(full)

                    self.memory.save_memory(self.memory_path)
                else:
                    self.vprint('Memory disabled, skipping memory saving...')

            self.vprint('Response and prompt saved to long term memory (if enabled). Returning response.')

            self.module_output = None

            return text
    
        else:
            self.vprint(f'Languge model disabled, unable to generate response. Enable language in config.json to use.', logging.ERROR)
            raise Exception('Language model is disabled, unable to generate response. Enable language in config.json to use.')
        
    def module_pipeline(self, uinput):
        detected, args = self.detect_module(uinput)
        
        if detected:
            if args:
                self.module_output = self.run_module(detected, args)
            else:
                self.module_output = self.run_module(detected)
        else:
            self.module_output = None

        self.vprint(f'Module pipeline completed, output: {self.module_output}')
        
    def detect_module(self, user_input):
        if self.modules_enabled:
            self.vprint(f'Module detection initiated, processing input: {user_input}')
            if self.modules.detectable_available:
                self.vprint(f'Looking for models detectable via naive bayes classifier: {self.modules.get_detectable_modules()}')
                output, probability = self.modules.predict_module(user_input)
            else:
                self.vprint(f'No detectable modules found (naive bayes classifier disabled?), skipping detection with classifier.')
                output = None
                probability = 100.0

            with_args = []
            if not output:
                self.vprint(f'No module detected, probability: {probability}')
                undetectable_modules = self.modules.get_undetectable_modules()
                if undetectable_modules:
                    self.vprint(f"Undetectable modules found: {undetectable_modules}, secondary check required. Initiating LLM-based module detection...")
                    self.vprint(f"WARNING: Undetectable modules will slow down prompts due to the extra processing time required for checking if called. This is not recommended.", logging.WARNING)
                    self.vprint(f"Passing input to LLM to detect modules among {undetectable_modules}")
                    for i in undetectable_modules:
                        if self.modules.get_arguments(i):
                            arguments = ''.join(self.modules.get_arguments(i))
                            with_args += [f'{i} ({arguments})']
                        else:
                            with_args += [i]
                            
                    if self.language_enabled:

                        llm_input = str({"user_prompt": str(user_input), "modules": with_args})
                        self.vprint(f'Input to LLM: {llm_input}')

                        system_prompt = 'Predict which module is being called (and extract arguments) based on user input, return module name and arguments in proper JSON format. Return null if no module is detected, the module detected is not listed or if no arguments are needed'

                        prompt = [
                            {
                                "role": "system",
                                "content": system_prompt
                            },
                            {
                                "role": "user",
                                "content": '{"user_prompt": "Whats the weather like in London right now?","Modules": ["weather (city)", "deepL (text)", "lighting_control"]}'
                            },
                            {
                                "role": "assistant",
                                "content": '{"module": "weather", "args": {"city": "London"}}'
                            },
                            {   
                                "role": "user", 
                                "content": '{"user_prompt": "Hello!","modules": ["weather (city)", "deepL (text)"]}'
                            },
                            {
                                "role": "assistant",
                                "content": '{"module": null, "args": null}'
                            },
                            {
                                "role": "user",
                                "content": '{"user_prompt": "Could you turn off the lights?", "modules": ["lighting_control"]}'
                            },
                            {
                                "role": "assistant",
                                "content": '{"module": "lighting_control", "args": null}'
                            },
                            {
                                "role": "user",
                                "content": llm_input
                            }
                        ]

                        self.vprint(f'Starting response generation for module detection...')
                        text, full, prompt_usage, response_usage = self.ai.generate(prompt, tokens=100, temp=0)
                        
                        try:
                            clean_text = self.clean_output(text)
                            self.vprint(f'LLM output (cleaned): "{clean_text}", extracting information...')
                            llm_output = json.loads(clean_text)

                            module = llm_output.get('module')
                            args = llm_output.get('args')
                            if module is not None:
                                self.vprint(f'Module detected via LLM: {module}, arguments: {args}, prompt usage: {prompt_usage}, response usage: {response_usage}')
                                return module, args
                            else:
                                self.vprint('No module detected by LLM.')
                                return None, None
                        except json.JSONDecodeError as e:
                            self.vprint(f'Error decoding JSON: {e} (The LLM provided invalid JSON output even after cleaning, skipping module detection)', logging.ERROR)
                            return None, None
                        except Exception as e:
                            self.vprint(f'Error: {e}', logging.error)
                            return None, None           
                    else:
                        self.vprint(f'Language model is disabled. Unable to detect modules via LLM.', logging.ERROR)
                        raise Exception('Language model is disabled. Unable to detect modules via LLM.')
            if output:
                self.vprint(f'Module detected: {output}, probability: {probability}')
                self.vprint(f'Module detection complete, returning module: {output}')
            return output, None
        else:
            self.vprint('Modules disabled, enable modules in config.json to use.', logging.WARNING)
            return 'Modules are disabled.'
        
    def get_module_args(self, user_input, module):
        if self.modules_enabled:
            self.vprint(f'Module argument retrieval initiated, processing module: {module}')
            args = self.modules.get_arguments(module)

            if self.language_enabled:

                llm_input = str({"user_prompt": str(user_input), "module_selected": str(module), "arguments": args})

                self.vprint(f'Input to LLM: {llm_input}')

                system_prompt = 'Extract arguments from a user prompt based on the module selected. Return arguments in proper JSON format. Return null if no arguments are needed.'

                prompt = [
                    {
                        "role": "system",
                        "content": system_prompt
                    },
                    {
                        "role": "user",
                        "content": '{"user_prompt": "Whats the weather like in London right now?", "module_selected": "weather", "arguments": ["city"]}}'
                    },
                    {
                        "role": "assistant",
                        "content": '{"args": [{"city": "London"}]}'
                    },
                    {   
                        "role": "user", 
                        "content": llm_input
                    }
                ]
                
                self.vprint(f'Starting response generation for module detection...')
                text, full, prompt_usage, response_usage = self.ai.generate(prompt, max_tokens=500, temperature=0)

                self.vprint(f'LLM output: {text}, prompt usage: {prompt_usage}, response usage: {response_usage}')

                try:
                    llm_output = json.loads(text)
                    args = llm_output['args']
                except json.decoder.JSONDecodeError:
                    self.vprint(f'LLM output is not valid JSON, unable to detect modules via LLM.', logging.ERROR)
                    return None, None
            else:
                self.vprint(f'Language model is disabled. Unable to detect modules via LLM.', logging.ERROR)
                raise Exception('Language model is disabled. Unable to detect modules via LLM.')
            
            self.vprint(f'Module arguments retrieved: {args}')

            return args

    def run_module(self, module, args, **kwargs):
        if self.modules_enabled:
            self.vprint(f'Module system initiated, processing module: {module} with arguments: {args} / {kwargs}')
            if args is not None:
                output = self.modules.use_module(module, args, **kwargs)
            else:
                output = self.modules.use_module(module, **kwargs)
            self.vprint(f'Module output: {output}')
            return output
        else:
            self.vprint('Modules disabled, enable modules in config.json to use.', logging.WARNING)
            return 'Modules are disabled.'
        
    def speak(self, input):
        if self.tts_enabled:
            if not input:
                self.vprint('No input text given.', logging.ERROR)
                return 'No input text given.'
            self.vprint('Generating audio output...')
            output = self.tts.generate(input)
            self.vprint('Audio output generated.')

            return output
        else:
            self.vprint('TTS disabled, enable tts in config.json to use.', logging.WARNING)
            return 'TTS is disabled.'
    
    def listen(self, input):
        if self.stt_enabled:
            if not input:
                self.vprint('No input audio file specified.', logging.ERROR)
                return 'No input audio file specified.'
            self.vprint('Listening to audio input...')
            output = self.stt.transcribe(input)
            self.vprint(f'Transcription received: {output}')

            return output
        else:
            self.vprint('STT disabled, enable stt in config.json to use.', logging.WARNING)
            return 'STT is disabled.'

    def see(self, input):
        if self.vision_enabled:
            if not input:
                self.vprint('No input image specified.', logging.ERROR)
                return 'No input image specified.'
            self.vprint('Analyzing image...')
            output = self.vision.describe(input)
            self.vprint(f'Image analysis complete: {output}')

            return output
        else:
            self.vprint('Vision disabled, enable vision in config.json to use.', logging.WARNING)
            return 'Vision is disabled.'

if __name__ == '__main__':
    print('The controller is not meant to be run directly, use one of the interfaces to interact with Ame.')
    pass
