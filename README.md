# DeveloperGPT
[![License](https://img.shields.io/badge/license-MIT-green)](./LICENSE)
[![CI](https://github.com/luo-anthony/DeveloperGPT/actions/workflows/main.yml/badge.svg)](https://github.com/luo-anthony/DeveloperGPT/actions/workflows/main.yml)
[![PyPI](https://img.shields.io/pypi/v/developergpt)](https://pypi.org/project/developergpt/)

<!-- [![codecov](https://codecov.io/gh/luo-anthony/DeveloperGPT/branch/main/graph/badge.svg?token=DeveloperGPT_token_here)](https://codecov.io/gh/luo-anthony/DeveloperGPT) -->

DeveloperGPT is a terminal application that uses the latest LLMs to help developers be more productive. 

By default, DeveloperGPT uses the [gpt-3.5-turbo](https://platform.openai.com/docs/models) model from OpenAI, but you can also use the open-source [BLOOM](https://bigscience.huggingface.co/blog/bloom) model (some features are currently not supported when using BLOOM). Support for more models and features is coming soon! 

DeveloperGPT has two main features:
#### 1. Natural Language to Terminal Commands
**Supported Models:** **GPT3.5 (default)**, BLOOM
![Natural Language Example](https://github.com/luo-anthony/DeveloperGPT/raw/main/samples/cmddemo.gif)

**NOTE:** Currently, command explanations are **not** supported when using BLOOM. Commands using BLOOM may also require more revision to get the desired output. 

#### 2. Chat with GPT-3.5 Inside the Terminal
**Supported Models:** **GPT3.5 (only)**
![Chat Example](https://github.com/luo-anthony/DeveloperGPT/raw/main/samples/chatdemo.gif)

**NOTE:** Chat moderation is **NOT** implemented - all your chat messages should follow the OpenAI terms of use. 


## Install DeveloperGPT from PyPI
```bash
pip install -U developergpt
```

### Setup

DeveloperGPT uses the GPT-3.5 model from OpenAI by default (with full feature support). 

Get your own OpenAI API Key: https://platform.openai.com/account/api-keys

```bash
# Do this once 
# set OpenAI API Key (using zsh for example)
$ echo 'export OPENAI_API_KEY=[your_key_here]' >> ~/.zshenv

# reload the environment (or just quit and open a new terminal)
$ source ~/.zshenv
```

If you just want to use the BLOOM model with **Feature 1 (Natural Language to Terminal Commands)** only, you don't need to setup an OpenAI key.

## Usage
```bash
# see available commands
$ developergpt 

# chat with GPT-3.5 inside the terminal 
$ developergpt chat

# natural language to terminal commands using GPT-3.5 (default)
$ developergpt cmd

# natural langauge to terminal commands using BLOOM
$ developergpt --model bloom cmd
```

### OpenAI API Usage (GPT-3.5)
You can monitor your OpenAI API usage here: https://platform.openai.com/account/usage

DeveloperGPT uses the `gpt-3.5-turbo` model which is very cost efficient (1/10 the cost of models such as `text-davinci-003`). Based on preliminary testing, using DeveloperGPT should cost no more than 10 cents per day (assuming ~100 requests/day). 

### Hugging-Face API Usage (BLOOM)
Currently, using the BLOOM model does not require a [Hugging Face Inference API](https://huggingface.co/docs/api-inference/index) token and is free (but rate limited). 

## Contributing

Read the [CONTRIBUTING.md](CONTRIBUTING.md) file.

### Future Roadmap
- Add support for more open-source models (Vicuna-13B?)

## Credit
- Thanks to Hugging Face and the NLP community for open-source models! 
- This project uses the Python project template from https://github.com/rochacbruno/python-project-template
- This project was written with assistance from ChatGPT and Github CoPilot. 
