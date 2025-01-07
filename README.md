![Banner](https://repository-images.githubusercontent.com/663230405/3d3fa7a7-d37c-41a8-9517-793b50ea616d)

## Setting a new standard for local virtual assistants 💧

Meet Ame, the most powerful virtual assistant framework, powered by cutting-edge technology. Ame is a feature-rich, multi-modal, open-source virtual assistant framework (**[API](#api)**) designed to run entirely locally. It leverages the power of LLaMA to provide personalized and intuitive interaction. Ame's server is designed to run on enterprise-grade or high-end consumer-grade hardware (3090, 24gb VRAM+), you can run Ame on lower-end consumer hardware by using a more aggressive quantization, smaller model and/or by disabling TTS, STT and/or vision. Split computing is planned for v2 which will allow for splitting the compute workload across multiple devices. See **[announcements](#announcements-)** for updates and more information. 

Join the **[discord](https://discord.gg/S6h8XYsuZt)** for frequent dev updates, discussion, community involvement and more.

## Disclaimer ⚠️
~~Ame is in an incomplete state and is being developed by me and only me, expect progress to be slow, refer to the **[progress](#progress-v1)** section of the readme for more information. The client and server are unable to communicate the audio files, this has not been implemented yet, audio generation is functional.~~

**The Ame Project has been discontinued, something new is coming soon... stay tuned.**

## Announcements 📢
- [2024-05-15] Development is going well, see the discord channel #dev-spam for more! (Including a todo list and timelines) 

## Overview 📖
- **[Key features 🚀](#key-features-)**
- **[Usage 💻](#usage-%EF%B8%8F)**
- **[Development progress 🚧](#progress-v1)**
- **[About Ame 💧](#the-meaning-behind-ame-)**
- **[Contributing 🤝](#contributing-)**
- **[Acknowledgements 🙏](#acknowledgements-)**
- **[License ⚖️](#license-%EF%B8%8F)**

## Key features 🚀
**Customizable Modules**: Ame's modular design allows for easy customization and extensibility. Each module serves a specific function, such as managing calendars, providing updates, or assisting with personal tasks—Ame adapts to you. Developers can create their own modules or modify existing ones to tailor Ame's capabilities to their specific requirements.

**Text-to-Speech (TTS) and Speech-to-Text (STT)**: Ame's TTS and STT capabilities enable natural and effortless communication. STT is powered by OpenAI's whisper and TTS is powered by Suno's bark.

**Discord Integration**: Ame seamlessly integrates with Discord, allowing you to interact with it through text-based messaging and voice notes. Discord provides a familiar and convenient way to interact with Ame, enabling efficient communication and access to its full range of functionalities.

**Open-Source**: Ame is entirely open-source. This allows for knowledge sharing and the continuous improvement of Ame while contributing to the open-source community, democratizing ML research in the process.

**Locally Run and Privacy-Focused**: Ame prioritizes user privacy and data control by operating entirely on the user's local machine or a user controlled server.

**Long-term Memory**: Ame utilizes a vector database that optimizes memory storage and retrieval, enabling Ame to access data that goes beyond the context limit of its model.

**Easy setup and configuration**: An automatic setup wizard allows for 3 click installation of dependencies and easy configuration setup.


### Full feature list
`*` means the feature is yet to be implemented, see **[progress](#progress-v1)**, this list does not include features that may be coming in **[v2](#plans-for-v2-)**.
- MIT Licensed
- Support for any LLaMA GGML/GGUF (via llama.cpp)
- Developer-friendly module platform
- Long-term memory
- Full customizability
- High-quality text-to-speech (via bark)
- Accurate speech-to-text (via whisper)
- Smart context limit management
- Pre-built server and client
- Remote server command
- Client UI`*`
- Discord integrations
- Fully open-source
- Easy-to-use API

## Usage ⚙️

### Install & Setup

```bash
git clone https://github.com/Expl0dingCat/Ame.git
``` 

Run `setup_wizard.py` in the root directory, this will automatically install the dependencies you do not have and setup your config. This supports Linux (including distributions) and Windows. 

- Ame was designed on Python 3.10.11 (should be compatible with lower versions but not officially supported)
- If llama-cpp-python is using your CPU when use_gpu is set to `true`, ensure you have nvidia-cuda-toolkit

### Server/client
Move `server.py` (interfaces/server-client/) to the root folder then run:
```bash
python server.py
```

To access the server locally make sure `Local = True` in `client.py` (interfaces/server-client/), to access it externally, modify the base URL and set `Local = False`, then run:
```bash
python client.py
```

### Discord bot
Move `discord-bot.py` (interfaces/discord/) to the root folder, enter in your bot's token and then run:
```bash
python discord-bot.py
```

### API
Ame's API allows for programmatic use of Ame's entire system. Here is an example:

```py
from controller import controller

# Initialize the controller, see documentation for more info
controller = controller()

# Generate text based on the input "Hello, World!"
response = controller.generate_response("Hello, World!")
```
For a more advanced example, see `server.py`.

## Progress (`v1`)
🔴 Planned
🟡 In progress
🟢 Finished

### Core

Component                     | Status 
----------------------------- | -----
Speech-to-text                |  🟢
Text-to-speech                |  🟢
Long-term memory              |  🟢
Primary controller            |  🟢
Module handler                |  🟢
Server/client interface       |  🟢

### Ext

Component                     | Status 
----------------------------- | -----
Client UI                     |  🔴
Discord interface             |  🔴
Documentation                 |  🟡

## Plans for `v2` 🔵
As `v1` is still in development, this section is subject to volatile change, it currently contains features I wanted to include in `v1` but don't have time as well as brand new _concepts_ that may or may not be implemented. If you would like to suggest features for `v2`, please feel free to contact me.
- Voice identification
- Web UI
- Multi-memory banks
- Passive listening
- Extreme redundancy
- Vision system
- Edge TPU support
- RVC (singing and possibly TTS)
- Vtuber integrations (weeb)
- Safetensor support -
- Home Assistant (this is already detectable out of the box by the module system but its a large task to integrate)

## The meaning behind "Ame" 💧
The name "Ame" originates from the Japanese word "雨" (pronounced ah-meh), which translates to "rain" in English. Like rain, Ame represents a refreshing and nourishing presence in your digital life. Just as raindrops bring life to the earth, Ame breathes life into your digital environment, providing support and efficiency.

## Contributing 🤝
If you would like to contribute to the Ame project, please contact me. Ame is being developed by me, and me only. Any help is greatly appreciated.

## Acknowledgements 🙏
Ame relies on 3rd party open source software to function, this project would not have been possible without:

- [llama-cpp-python](https://github.com/abetlen/llama-cpp-python) - LLaMA GGML inference
- [HyperDB](https://github.com/jdagdelen/hyperDB) - Long term memory vector DB
- [Whisper](https://github.com/openai/whisper) and [Bark](https://github.com/suno-ai/bark) - Speech-to-text and text-to-speech
- [LLaMA](https://github.com/facebookresearch/llama) - Base LLM

## License ⚖️
Ame is released under the MIT License, which allows you to use, modify, and distribute the software freely. Please refer to the [license file](https://github.com/Expl0dingCat/ame/blob/main/LICENSE) for more details.
