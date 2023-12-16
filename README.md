# DeveloperGPT
[![License](https://img.shields.io/badge/license-MIT-green)](./LICENSE)
[![LLMs](https://img.shields.io/badge/Supported%20LLMs-Gemini,%20GPT3.5,%20GPT4,%20OpenChat,%20Zephyr-blue)](https://img.shields.io/badge/Supported%20LLMs-Gemini,%20GPT3.5,%20GPT4,%20OpenChat,%20Zephyr-blue)
[![PyPI](https://img.shields.io/pypi/v/developergpt)](https://pypi.org/project/developergpt/)
[![OpenAI GPTs](https://img.shields.io/badge/OpenAI%20GPTs-Try%20the%20online%20DeveloperGPT-8A2BE2)](https://chat.openai.com/g/g-mfPPe6MKC-developergpt)

DeveloperGPT is a LLM-powered command line tool that enables natural language to terminal commands and in-terminal chat. DeveloperGPT is powered by Google Gemini Pro by default but also supports OpenAI GPT LLMs and open-source LLMs from Hugging Face such as Zephyr and OpenChat.

**NEW**: As of December 2023, DeveloperGPT is completely free to use when using Google Gemini Pro (up to 60 requests per minute) - this is the default model used by DeveloperGPT in the latest version. 

**Supported LLMs**
- Google AI (Free): [Gemini](https://deepmind.google/technologies/gemini/) (default)
- OpenAI (Paid): [GPT3.5, GPT4](https://platform.openai.com/docs/models)
- Open Source (Free): [Zephyr](https://huggingface.co/HuggingFaceH4/zephyr-7b-beta), [OpenChat](https://huggingface.co/openchat/openchat_3.5)

DeveloperGPT has two main features:
#### 1. Natural Language to Terminal Commands
**Supported LLMs:** Gemini (default), GPT3.5, GPT4, Zephyr, OpenChat

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

Use `developergpt --model [gpt35,gpt4,zephyr,openchat] cmd` to use a different LLM instead of Google Gemini.  
```bash
# Example: Natural Language to Terminal Commands using the GPT3.5 instead of Gemini
$ developergpt --model gpt35 cmd [your natural language command request]
```

Google's Gemini model is the fastest model with accuracy similar to OpenAI GPT models while being completely free. OpenAI GPT3.5 is generally accurate for the majority of natural langauge to command requests and is significantly cheaper to use than GPT4. Open-source models Zephyr and OpenChat are less accurate and may result in in unexpected or undefined behavior. With all models, it is always good practice to manually verify the command output before running it.

![Natural Language Example 1](https://github.com/luo-anthony/DeveloperGPT/raw/main/samples/cmd_demo.gif)

#### 2. Chat inside the Terminal
**Supported LLMs:** Gemini (default), GPT3.5, GPT4, Zephyr, OpenChat

**Usage:** `developergpt chat`
```bash
# chat with DeveloperGPT using Gemini Pro (default)
$ developergpt chat
```

Use `developergpt --model [gpt35,gpt4,zephyr,openchat] chat` to use a different LLM instead of Gemini. 
```bash
# chat with DeveloperGPT using GPT3.5
$ developergpt --model gpt35 chat

# chat with DeveloperGPT using GPT4
$ developergpt --model gpt4 chat

# chat with DeveloperGPT using OpenChat
$ developergpt --model openchat chat

# chat with DeveloperGPT using Zephyr
$ developergpt --model zephyr chat
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
#### Using Google Gemini (Default)
By default, DeveloperGPT uses Google Gemini Pro. To use Gemini Pro, you will need an API key (free to use up to 60 queries per minute).

1. Get your own Google AI Studio API Key: https://makersuite.google.com/app/apikey
2. Set your Google API Key as an environment variable. You only need to do this once. 
```bash
# set Google API Key (using zsh for example)
$ echo 'export GOOGLE_API_KEY=[your_key_here]' >> ~/.zshenv

# reload the environment (or just quit and open a new terminal)
$ source ~/.zshenv
```

#### Using OpenAI GPT LLMs
To use GPT3.5 or GPT4, you will need an OpenAI API key.

1. Get your own OpenAI API Key: https://platform.openai.com/account/api-keys
2. Set your OpenAI API Key as an environment variable. You only need to do this once. 
```bash
# set OpenAI API Key (using zsh for example)
$ echo 'export OPENAI_API_KEY=[your_key_here]' >> ~/.zshenv

# reload the environment (or just quit and open a new terminal)
$ source ~/.zshenv
```

#### Using Open-Source LLMs (Optional)
To use open-source LLMs such as Zephyr or OpenChat hosted on Hugging Face, you can optionally set up a [Hugging Face](https://huggingface.co/settings/tokens) or [Inference API](https://huggingface.co/docs/api-inference/index) token as an environment variable using the steps below. Setting up a token is **not required**, but it will allow you to make more requests without being rate limited. 

```bash
# [OPTIONAL] set Hugging Face token (using zsh for example)
# You only need to do this once
$ echo 'export HUGGING_FACE_API_KEY=[your_key_here]' >> ~/.zshenv

# reload the environment (or just quit and open a new terminal)
$ source ~/.zshenv
```

### Usage and Cost 
#### Google Gemini
As of December 2023, Google Gemini is free to use up to 60 queries per minute. For more information, see: https://ai.google.dev/pricing

#### OpenAI GPT
You can monitor your OpenAI API usage here: https://platform.openai.com/account/usage. Based on preliminary testing, using DeveloperGPT with GPT3.5 should cost no more than 10 cents per day with regular usage. 

#### Hugging-Face Open-Source LLMs 
As of December 2023, using Hugging Face LLMs does not require a token and is free but rate limited. To avoid rate limit, you can set a token using the instructions above. 

## Contributing
Read the [CONTRIBUTING.md](CONTRIBUTING.md) file.

### Future Roadmap
- Add support for more open-source models

## Credit
- Thanks to Hugging Face and the NLP community for open-source models and prompts! 
- This project uses the Python project template from https://github.com/rochacbruno/python-project-template
