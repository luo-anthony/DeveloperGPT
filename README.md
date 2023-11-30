# DeveloperGPT
[![License](https://img.shields.io/badge/license-MIT-green)](./LICENSE)
[![LLMs](https://img.shields.io/badge/Supported%20LLMs-GPT3.5,%20GPT4,%20OpenChat,%20Zephyr-blue)](https://img.shields.io/badge/Supported%20LLMs-GPT,%20BLOOM-blue)
[![PyPI](https://img.shields.io/pypi/v/developergpt)](https://pypi.org/project/developergpt/)
[![OpenAI GPTs](https://img.shields.io/badge/OpenAI%20GPTs-Try%20the%20online%20DeveloperGPT-8A2BE2)](https://chat.openai.com/g/g-mfPPe6MKC-developergpt)

DeveloperGPT is a LLM-powered command line tool that enables natural language to terminal commands and in-terminal chat.

DeveloperGPT is powered by [OpenAI's GPT3.5](https://platform.openai.com/docs/models) (by default) with additional support for GPT4 and open-source models hosted on Hugging Face including [Zephyr](https://huggingface.co/HuggingFaceH4/zephyr-7b-beta) and [OpenChat](https://huggingface.co/openchat/openchat_3.5).

DeveloperGPT has two main features:
#### 1. Natural Language to Terminal Commands
**Supported LLMs:** GPT3.5 (default), GPT4, Zephyr, OpenChat

**Usage:** `developergpt cmd [your natural language command request]`
```bash
# Example
$ developergpt cmd list all commits that contain the word "llm"
```

Use `developergpt cmd --fast` to get commands faster without any explanations (may be less accurate). 
```bash
# Fast Mode: Commands are given without explanation (may be less accurate)
$ developergpt cmd --fast [your natural language command request]
```

Use `developergpt --model [zephyr,openchat,gpt4] cmd` to use a different LLM instead of GPT3.5. 
```bash
# Example: Natural Language to Terminal Commands using the Zephyr LLM instead of GPT3.5
$ developergpt --model zephyr cmd [your natural language command request]
```
vGPT3.5 is generally accurate for the majority of natural langauge to command requests and is significantly cheaper to use than GPT4. Other models such as Zephyr or OpenChat are less accurate and may result in in unexpected or undefined behavior. With all models, it is always good practice to manually verify the command output before running it.

![Natural Language Example 1](https://github.com/luo-anthony/DeveloperGPT/raw/main/samples/cmd_demo.gif)

#### 2. Chat inside the Terminal
**Supported LLMs:** GPT3.5 (default), GPT4, Zephyr, OpenChat

**Usage:** `developergpt chat`
```bash
# chat with DeveloperGPT using GPT3.5 (default)
$ developergpt chat
```

Use `developergpt --model [zephyr,openchat,gpt4] chat` to use a different LLM instead of GPT3.5. 
```bash
# chat with DeveloperGPT using OpenChat
$ developergpt --model openchat chat

# chat with DeveloperGPT using Zephyr
$ developergpt --model zephyr chat

# chat with DeveloperGPT using GPT4
$ developergpt --model gpt4 chat
```

![Chat Example](https://github.com/luo-anthony/DeveloperGPT/raw/main/samples/chat_demo.gif)

Chat moderation is **NOT** implemented - all your chat messages should follow the terms of use of the LLM used. 

## Usage
DeveloperGPT is **NOT** to be used for any purposes forbidden by the terms of use of the LLMs used. Additionally, DeveloperGPT itself (apart from the LLMs) is a proof of concept tool and is not intended to be used for any serious or commerical work. 

### Install DeveloperGPT from PyPI
```bash
pip install -U developergpt
```

### Basic Usage
```bash
# see available commands
$ developergpt 
```

### Setup
#### Using OpenAI GPT (Default)
By default, DeveloperGPT uses GPT3.5 from OpenAI in addition to supporting GPT4. To use GPT3.5 or GPT4, you will need an OpenAI API Key.

1. Get your own OpenAI API Key: https://platform.openai.com/account/api-keys
2. Set your OpenAI API Key as an environment variable. You only need to do this once. 
```bash
# set OpenAI API Key (using zsh for example)
$ echo 'export OPENAI_API_KEY=[your_key_here]' >> ~/.zshenv

# reload the environment (or just quit and open a new terminal)
$ source ~/.zshenv
```

#### Using Open-Source Models (Optional)
To use open-source models such as Zephyr or OpenChat hosted on Hugging Face, you can optionally set up a [Hugging Face](https://huggingface.co/settings/tokens) or [Inference API](https://huggingface.co/docs/api-inference/index) token as an environment variable using the steps below. Setting up a token is **not required**, but it will allow you to make more requests without being rate limited. 

```bash
# [OPTIONAL] set Hugging Face token (using zsh for example)
# You only need to do this once
$ echo 'export HUGGING_FACE_API_KEY=[your_key_here]' >> ~/.zshenv

# reload the environment (or just quit and open a new terminal)
$ source ~/.zshenv
```

### OpenAI API Usage
You can monitor your OpenAI API usage here: https://platform.openai.com/account/usage. Based on preliminary testing, using DeveloperGPT with GPT3.5 should cost no more than 10 cents per day with regular usage. 

### Hugging-Face Usage 
Currently, using Hugging Face LLMs does not require a token and is free but rate limited. To avoid rate limit, you can set a token using the instructions above. 

## Contributing
Read the [CONTRIBUTING.md](CONTRIBUTING.md) file.

### Future Roadmap
- Add support for more open-source models such as LLAMA 2

## Credit
- Thanks to Hugging Face and the NLP community for open-source models and prompts! 
- This project uses the Python project template from https://github.com/rochacbruno/python-project-template
