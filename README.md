# DeveloperGPT
[![License](https://img.shields.io/badge/license-MIT-green)](./LICENSE)
[![CI](https://github.com/luo-anthony/DeveloperGPT/actions/workflows/main.yml/badge.svg)](https://github.com/luo-anthony/DeveloperGPT/actions/workflows/main.yml)
[![LLMs](https://img.shields.io/badge/Supported%20LLMs-GPT3.5,%20BLOOM-blue)](https://img.shields.io/badge/Supported%20LLMs-GPT3.5,%20BLOOM-blue)
[![PyPI](https://img.shields.io/pypi/v/developergpt)](https://pypi.org/project/developergpt/)

<!-- [![codecov](https://codecov.io/gh/luo-anthony/DeveloperGPT/branch/main/graph/badge.svg?token=DeveloperGPT_token_here)](https://codecov.io/gh/luo-anthony/DeveloperGPT) -->

DeveloperGPT is a terminal application that uses the latest LLMs to help developers be more productive. It is one of the first developer productivity terminal applications that supports **open source LLMs** such as the [BLOOM](https://bigscience.huggingface.co/blog/bloom) model in addition to OpenAI GPT LLMs. 

By default, DeveloperGPT uses the [gpt-3.5-turbo](https://platform.openai.com/docs/models) model from OpenAI (requires an OpenAI API Key), but it also supports the open-source [BLOOM](https://bigscience.huggingface.co/blog/bloom) model and GPT-4 from OpenAI. Using BLOOM with DeveloperGPT is **completely free** and does **not require an API key** (rate-limited) thanks to the Hugging Face Inference API. 

From testing, OpenAI GPT models generally yield better results and are able to handle more complex requests compared to the BLOOM model. 

DeveloperGPT has two main features:
#### 1. Natural Language to Terminal Commands
**Supported Models:** GPT-3.5 (default), GPT-4, BLOOM

**Usage:** `developergpt cmd [your natural language command request]`
![Natural Language Example](https://github.com/luo-anthony/DeveloperGPT/raw/main/samples/cmddemo.gif)

From testing, the GPT-3.5 model is accurate for the majority of natural langauge to command requests and is significantly cheaper to use than GPT-4. The BLOOM model command output may not be accurate, especially for more complex commands. Using the BLOOM model may also result in unexpected or undefined behavior. With all models, it is always good practice to manually verify the command output before running it.

#### 2. Chat inside the Terminal
**Supported Models:** GPT-3.5 (default), GPT-4, BLOOM

**Usage:** `developergpt chat`
![Chat Example](https://github.com/luo-anthony/DeveloperGPT/raw/main/samples/chatdemo.gif)

**NOTE:** Chat moderation is **NOT** implemented - all your chat messages should follow the OpenAI and BLOOM terms of use. 

## Install DeveloperGPT from PyPI
```bash
pip install -U developergpt
```

### Setup


#### OpenAI GPT Models
By default, DeveloperGPT uses the GPT-3.5 model from OpenAI. To use GPT-3.5 or GPT-4, you will need an OpenAI API Key.

1. Get your own OpenAI API Key: https://platform.openai.com/account/api-keys
2. Set your OpenAI API Key as an environment variable. You only need to do this once. 
```bash
# set OpenAI API Key (using zsh for example)
$ echo 'export OPENAI_API_KEY=[your_key_here]' >> ~/.zshenv

# reload the environment (or just quit and open a new terminal)
$ source ~/.zshenv
```

#### BLOOM
To use the BLOOM model instead, you can optionally set up a [Hugging Face User Access](https://huggingface.co/settings/tokens) or [Inference API](https://huggingface.co/docs/api-inference/index) token as an environment variable using the steps below. Setting up a token is **not required (the BLOOM model will work without any token or key)**, but it will allow you to make more requests without being rate limited. 

```bash
# [OPTIONAL] set Hugging Face API token (using zsh for example)
# You only need to do this once
$ echo 'export HUGGING_FACE_API_KEY=[your_key_here]' >> ~/.zshenv

# reload the environment (or just quit and open a new terminal)
$ source ~/.zshenv
```

## Usage
```bash
# see available commands
$ developergpt 

# give feedback
$ developergpt feedback
```

#### Natural Language to Terminal Comands
DeveloperGPT allows you to get and execute terminal commands using natural language. 
```bash
# Natural Language to Terminal Commands using OpenAI GPT-3.5 (default)
$ developergpt cmd [your natural language command request]

# Natural Language to Terminal Commands using OpenAI GPT-3.5 (default) with prompt
$ developergpt cmd 

# Example Usage
$ developergpt cmd list all commits that contain the word "llm"
```

Use `developergpt --model bloom cmd` to use the BLOOM model instead of the GPT-3.5 model (used by default). 
```bash
# Natural Language to Terminal Commands using BLOOM model instead
$ developergpt --model bloom cmd [your natural language command request]
```

Use `developergpt --model bloom cmd` to use the GPT-4 model instead of the GPT-3.5 model (used by default). 
```bash
# Natural Language to Terminal Commands using GPT-4 model instead
$ developergpt --model gpt-4 cmd [your natural language command request]
```

Use `developergpt cmd --fast` to get commands faster without any explanations (may be less accurate). 
```bash
# Fast Mode (GPT-3.5): Commands are given without explanation (may be less accurate)
$ developergpt cmd --fast [your natural language command request]

# Fast Mode (BLOOM): Commands are given without explanation (may be less accurate)
$ developergpt --model bloom cmd --fast [your natural language command request]

# Fast Mode (GPT-4): Commands are given without explanation (may be less accurate)
$ developergpt --model gpt-4 cmd --fast [your natural language command request]
```

#### Chat inside the Terminal
DeveloperGPT allows you to chat with the GPT models or the BLOOM model in the terminal. 

```bash
# chat with DeveloperGPT using GPT-3.5 (default)
$ developergpt chat

# chat with DeveloperGPT using BLOOM model instead
$ developergpt --model bloom chat

# chat with DeveloperGPT using GPT-4
$ developergpt --model gpt-4 chat
```

**NOTE:** DeveloperGPT is **NOT** to be used for any purposes forbidden by the terms of use of the LLMs used. Additionally, DeveloperGPT itself (apart from the LLMs) is a proof of concept tool and is not intended to be used for any serious or commerical work. 

### OpenAI API Usage
You can monitor your OpenAI API usage here: https://platform.openai.com/account/usage

By default, DeveloperGPT uses the `gpt-3.5-turbo` model which is very cost efficient (1/10 the cost of models such as `text-davinci-003`). Based on preliminary testing, using DeveloperGPT with GPT-3.5 should cost no more than 10 cents per day.

### Hugging-Face Inference API Usage (BLOOM)
Currently, using the BLOOM model does not require a token and is free but rate limited. To avoid rate limit, you can set a token using the instructions above. 

## Contributing
Read the [CONTRIBUTING.md](CONTRIBUTING.md) file.

### Future Roadmap
- Add support for more open-source models (Alpaca, Vicuna, LLAMA, etc.)

## Credit
- Thanks to Hugging Face and the NLP community for open-source models and prompts! 
- This project uses the Python project template from https://github.com/rochacbruno/python-project-template
