config = {
    "verbose": true,
    "log": true,
    "assistant_name": "Ame",
    "memory": {
        "enabled": true,
        "path": null
    },
    "language": {
        "enabled": true,
        "model_path": null,
        "max_tokens": 128,
        "temperature": 0.85,
        "context_limit": 2048,
        "virtual_context_limit": 1024, 
        "personality_prompt": null,
        "model_file_ext": ".bin"
    },
    "vision": {
        "enabled": true,
        "model_path": null
    },
    "tts": {
        "enabled": false,
        "model_path": null,
        "temperature": 0.6
    },
    "stt": {
        "enabled": false,
        "model_path": null
    },
    "modules": {
        "enabled": true,
        "json_path": null,
        "model_path": null,
        "vectorizer_path": null
    },
    "weeb": false,
    "use_gpu": true,
    "debug": true
}

def input_validator(intxt):
    while True:
        userans = input(intxt).lower()

        if userans == 'y':
            return True
        elif userans == 'n':
            return False
        else:
            print('Invalid input. Please try again.')

def advanced_setup():
    print('---GENERAL---')
    verbose = input_validator('Would you like to enable verbose mode? (y/n): ')
    log = input_validator('Would you like to enable logging? (y/n): ')
    assistant_name = input('What is the name of the assistant (this is also used in the prompt): ')
    print('---MEMORY---')
    memory_enabled = input_validator('Would you like to enable memory? (y/n): ')
    if memory_enabled:
        memory_path = input('Please enter the path to the memory file (leave blank for autodetect): ')
        if memory_path == '':
            memory_path = None
    print('---LANGUAGE---')
    language_enabled = input_validator('Would you like to enable language? (y/n): ')
    if language_enabled:
        language_model_path = input('Please enter the path to the language model (leave blank for autodetect): ')
        if language_model_path == '':
            language_model_path = None
        language_max_tokens = input('Please enter the maximum number of tokens to generate (leave blank for default [128]): ')
        if language_max_tokens == '':
            language_max_tokens = 128
        else:
            language_max_tokens = int(language_max_tokens)
        language_temperature = input('Please enter the temperature (leave blank for default [0.85]): ')
        if language_temperature == '':
            language_temperature = 0.85
        else:
            language_temperature = float(language_temperature)
        language_context_limit = input('Please enter the context limit of your language model: ')
        language_virtual_context_limit = input('Please enter the virtual context limit (the point where the last message will be removed from history to prevent too many tokens error, recommended to be ~80% of actual context limit): ')
        language_personality_prompt = input('Please enter the personality prompt (leave blank for default): ')
        if language_personality_prompt == '':
            language_personality_prompt = None
        language_model_file_ext = input('Please enter the model file extension (leave blank for default, .gguf): ')
        if language_model_file_ext == '':
            language_model_file_ext = '.gguf'
    # vision is not implemented yet
    #print('---VISION---')
    #vision_enabled = input_validator('Would you like to enable vision? (y/n): ')
    #if vision_enabled:
        # vision_model_path = input('Please enter the path to the vision model (leave blank for default): ')
        # if vision_model_path == '':
        #    vision_model_path = None
    print('---TEXT TO SPEECH---')
    tts_enabled = input_validator('Would you like to enable text to speech? (y/n): ')
    if tts_enabled:
        tts_model_path = input('Please enter the path to the text to speech model (leave blank for default [base]): ')
        if tts_model_path == '':
            tts_model_path = None
        tts_temperature = input('Please enter the temperature (leave blank for default): ')
        if tts_temperature == '':
            tts_temperature = 0.6
        else:
            tts_temperature = float(tts_temperature)
    print('---SPEECH TO TEXT---')
    stt_enabled = input_validator('Would you like to enable speech to text? (y/n): ')
    if stt_enabled:
        stt_model = input('Please enter the name of the stt model (leave blank for default): ')
        if stt_model_path == '':
            stt_model_path = None
    print('---MODULES---')
    modules_enabled = input_validator('Would you like to enable modules? (y/n): ')
    if modules_enabled:
        modules_json_path = input('Please enter the path to the modules json file (leave blank for default): ')
        if modules_json_path == '':
            modules_json_path = None
        modules_model_path = input('Please enter the path to the modules model (leave blank for default): ')
        if modules_model_path == '':
            modules_model_path = None
        modules_vectorizer_path = input('Please enter the path to the modules vectorizer (leave blank for default): ')
        if modules_vectorizer_path == '':
            modules_vectorizer_path = None
    print('---MISC---')
    weeb = False # not implemented yet 
    use_gpu = input_validator('Would you like to use the GPU? (y/n): ')
    debug = input_validator('Would you like to enable debug mode? (y/n): ')

def express_setup():
    

def setup():
    print('Welcome to the Ame setup wizard. This will automatically configure Ame for you.')
    print('Please read and follow the instructions carefully.')
    type_of_setup = input('Would you like to do an express setup or an advanced setup? (e/a): ')
    if type_of_setup == 'a':
        advanced_setup()
    else:
        express_setup()