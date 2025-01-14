import os
import platform
import sys
import subprocess
import pkg_resources

def input_y_n(msg: str):
    while True:
        y_or_n = input(msg + ' (y/n): ').lower().strip()
        if y_or_n == 'y':
            return True
        elif y_or_n == 'n':
            return False
        else:
            print("Invalid input! Please input 'y' or 'n'.")

def input_with_options(msg: str, options: list):
    while True:
        options_str = ', '.join(str(x) for x in options)
        response = input(f'{msg} ({options_str}): ').lower().strip()
        if any(option in response for option in options):
            return response
        else:
            print(f'Invalid input! Please input one of the following: {options_str}')

def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

def detect_os():
    return platform.system()

def get_cuda_version():
    try:
        result = subprocess.run(['nvcc', '--version'], capture_output=True, text=True, check=True)
        version_info = result.stdout
        for line in version_info.split('\n'):
            if 'release' in line:
                parts = line.split()
                for i, part in enumerate(parts):
                    if part == 'release':
                        return True, parts[i + 1].rstrip(',')
    except subprocess.CalledProcessError:
        return False, 'CUDA is not installed or nvcc is not found in PATH.'
    except FileNotFoundError:
        return False, 'nvcc command not found. Make sure CUDA is installed and nvcc is in PATH.'

def check_bld_tools():
    import winreg
    try:
        registry_key_path = r'SOFTWARE\Microsoft\VisualStudio\SxS\VS7'
        registry_value_name = '17.0'

        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, registry_key_path, 0, winreg.KEY_READ) as key:
            try:
                install_path, regtype = winreg.QueryValueEx(key, registry_value_name)
                if install_path:
                    return True, f'Visual Studio Build Tools 2022 is installed at: {install_path}'
            except FileNotFoundError:
                return False, 'Visual Studio Build Tools 2022 is not installed.'
    except FileNotFoundError:
        return False, 'Visual Studio registry key not found.'
    
def prereq_check():
    cuda = False
    bld_tools = False

    cuda, info = get_cuda_version()
    if not cuda:
        print(info)
        print('WARNING: Could not detect CUDA version, CUDA is required for NVIDIA GPU based acceleration. If you do not have it and need it, you can install it here: https://developer.nvidia.com/cuda-toolkit')
    else:
        print(f'Detected CUDA version: {info}')

    if detect_os() == 'Windows':
        bld_tools, info = check_bld_tools()
        if not bld_tools:
            print(info)
            print('WARNING: Visual Studio Build Tools not found, it is required for llama-cpp-python (if you opted for gguf/ggml). You can download it here: https://visualstudio.microsoft.com/visual-cpp-build-tools')
    elif detect_os() == 'Linux':
        bld_tools = True

    return cuda, bld_tools

def install_base_dependencies(os, backend):
    dependancies = {'sentence-transformers', 'openai-whisper', 'aiohttp_cors', 'aiohttp', 'transformers'}
    already_installed = {pkg.key for pkg in pkg_resources.working_set}

    print(f'Attempting to install torch/torchvision/torchaudio for {backend}...')
    if backend == 'cuda':
        cuda, info = get_cuda_version()
        if cuda:
            if float(info) >= 12.1:
                for i in ('torch', 'torchvision', 'torchaudio'):
                    dependancies.add(i)
                print('CUDA version is 12.1 (or higher), torch/torchvision/torchaudio will be installed normally.')
            elif float(info) == 11.8:
                torch_pkgs = {'torch', 'torchvision', 'torchaudio'} - already_installed
                if torch_pkgs:
                    print('CUDA version is 11.8, installing torch/torchvision/torchaudio for CUDA 11.8...')
                    subprocess.check_call([sys.executable, '-m', 'pip', 'install', *torch_pkgs, '--index-url', 'https://download.pytorch.org/whl/cu118'])
            elif float(info) < 11.8:
                print('CUDA version is below 11.8, please upgrade to at least 11.8. Unable to install torch/torchvision/torchaudio.')
                exit(1)
        else:
            print('CUDA not found (or it could not be detected), please install CUDA Toolkit from https://developer.nvidia.com/cuda-toolkit to use this backend or use a different backend.')
            exit(1)
    elif backend == 'openblas':
        print('Using CPU backend, installing torch/torchvision/torchaudio for CPU...')
        torch_pkgs = {'torch', 'torchvision', 'torchaudio'} - already_installed
        if torch_pkgs:
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', *torch_pkgs, '--index-url', 'https://download.pytorch.org/whl/cpu'])
        else:
            print('Torch/torchvision/torchaudio already installed.')

    print('Checking and installing other dependencies...')
    
    missing = dependancies - already_installed
    for package in (dependancies - missing):    
        print(f'Already installed: {package}')
    print(f'Installing base dependencies for {os}...')
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', *missing])

def install_llm_backend(type, hardware):
    if type in ['all', 'gguf']:
        if hardware == 'openblas':
            cmake_args = '-DLLAMA_BLAS=ON -DLLAMA_BLAS_VENDOR=OpenBLAS'
        elif hardware == 'cuda':
            cmake_args = '-DLLAMA_CUDA=on'

        os_name = detect_os()
        if os_name == 'Windows':
            os.environ['CMAKE_ARGS'] = cmake_args
            print(f'Detected Windows, installing llama-cpp-python for Windows with cmake args: {cmake_args}...')
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'llama-cpp-python'])
        elif os_name in ['Linux', 'Darwin']:
            print(f'Detected {os_name}, installing llama-cpp-python for {os_name} with cmake args: {cmake_args}...')
            subprocess.check_call(['pip', 'install', 'llama-cpp-python'], env={'CMAKE_ARGS': cmake_args})

    if type in ['all', 'safetensors']:
        print('Installing safetensors to load .safetensors...')
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'safetensors'])

    if type in ['all', 'pkl']:
        print('Pickle selected, no additional installation required (.pkl models are not recommended, use .safetensors).')
    
    print('LLM backend installed.')

def install_vision_backend(type, hardware):
    print('Installing vision backend...')
    
    if type in ['all', 'llava']:
        print('Installing LLaVA requirements...')
        if input_y_n('LLaVA support is provided by llama-cpp-python, do you want to proceed?'):
            install_llm_backend('gguf', hardware)
        else:
            print('llama-cpp-python will not be installed, LLaVA will not be supported.')
    
    if type in ['all', 'clip']:
        print('Instlling CLIP and its requirements...')
        reqs = {'git+https://github.com/openai/CLIP.git', 'ftfy', 'regex', 'tqdm'}
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', *reqs])
    
    print('Vision backend installed.')

def config_builder():
    print('----- Building config -----')
    print('For default values, leave input blank and press enter, ensure input value types are right, config is not protected .')
    lora_path = None
    clip_path = None
    llava_clip_path = None
    tts_temp = 0.6
    tts_model_path = None
    verbose = input_y_n("Do you want Ame's controller to be verbose? (default: y)") or True
    log = input_y_n('Do you want Ame to log to a file? (default: y)') or True 
    assistant_name = str(input("What do you want your assistant's name to be? (default: Ame): ")) or 'Ame'
    memory_enabled = input_y_n('Do you want to enable long term memory via hyperdb? (default: y)') or True
    memory_path = str(input('Where do you want to store your memory? (default: auto): ')) or None
    language_model_path = str(input('Where do you want to store your language model? (default: auto): ')) or None
    max_tokens = int(input('What is the maximum number of tokens you want to generate each run? (default: 512): ')) or 512
    temperature = float(input('What temperature do you want to use for generation? (default: 0.85): ')) or 0.85
    context_size = int(input('What is the context length of the model? (default: auto): ')) or 0
    top_p = float(input('What top_p value do you want to use for generation? (default: 0.95): ')) or 0.95
    top_k = int(input('What top_k value do you want to use for generation? (default: 40): ')) or 40
    gpu = input_y_n('Do you want to use a GPU for generation? (only if you have CUDA)')
    gpu_layers = int(input('How many layers do you want to use on the GPU? (default: auto): ')) or -1
    threads = int(input('How many threads do you want to use for generation? (default: auto): ')) or None
    virtual_context_limit = int(input('What is the virtual context limit? [to prevent out of vram errors] (default: 2048): ')) or 2048
    personality_prompt = str(input('What is the personality prompt? (default: None): ')) or None
    model_file_ext = str(input('What is the model file extension? [this is important, it determines what backend is used] (default: .gguf): ')) or '.gguf'
    model_format = str(input('What is the model format? (default: chatml): ')) or 'chatml'
    lora = input_y_n('Do you want to use a LoRA? (default: n)') or False
    if lora:
        lora_path = str(input('Where is your LoRA located?: ')) or None
    vision_enabled = input_y_n('Do you want to enable vision? (default: y)') or True
    if vision_enabled:
        vision_backend = str(input_with_options('What vision backend do you want to use? [note: llava is a seperate LLM that still requires CLIP, entering clip here enables standalone clip that works with any LLM] (default: clip)', ['clip', 'llava'])) or 'clip'
        if vision_backend == 'clip':
            clip_path = str(input('Where is your CLIP model located?: ')) or None
        elif vision_backend == 'llava':
            llava_clip_path = str(input('Where is your CLIP model located?: ')) or None
    tts_enabled = input_y_n('Do you want to enable TTS? [powered by bark] (default: y)') or True
    if tts_enabled:
        tts_temp = float(input('What temperature do you want to use for TTS? (default: 0.6): ')) or 0.6
        tts_model_path = str(input('Where is your TTS model located? (default: auto): ')) or None
    

def dependancies_install():
    print('----- Installing dependancies -----')
    print(f'Detected operating system: {detect_os()}')
    print('Checking potential prerequisites... (Based on your specific requirements, not all prerequisites may be required.)')
    cuda, bld_tools = prereq_check()

    backend_hardware = input_with_options('What backend do you want to use (cuda for NVIDIA GPUs, openblas for CPU)?', ['cuda', 'openblas'])
    install_base_dependencies(detect_os(), backend_hardware)
    model_file_ext = input_with_options(f'What large language model backend do you want to install?', ['gguf', 'safetensors', 'pkl', 'all'])
    install_llm_backend(model_file_ext, backend_hardware)
    vision_backend = input_y_n('Do you want to install a vision backend?')
    if vision_backend:
        vision_backend_type = input_with_options('What vision backend do you want to install?', ['clip', 'llava', 'all'])
        install_vision_backend(vision_backend_type, backend_hardware)
    print('All dependancies installed.')

def menu():
    print('----- Ame configuration tool -----')
    print('1. Install dependancies and setup configuration')
    print('2. Install dependancies only')
    print('3. Setup configuration only')
    options = input_with_options('What would you like to do?', ['1', '2', '3'])
    if options == '1':
        dependancies_install()
        config_builder()
    elif options == '2':
        dependancies_install()
    elif options == '3':
        config_builder()

if __name__ == '__main__':
    menu()

