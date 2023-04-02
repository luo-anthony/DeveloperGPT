# DeveloperGPT
[![License](https://img.shields.io/badge/license-MIT-green)](./LICENSE)
[![CI](https://github.com/luo-anthony/DeveloperGPT/actions/workflows/main.yml/badge.svg)](https://github.com/luo-anthony/DeveloperGPT/actions/workflows/main.yml)
[![PyPI](https://img.shields.io/pypi/v/developergpt)](https://pypi.org/project/developergpt/)

<!-- [![codecov](https://codecov.io/gh/luo-anthony/DeveloperGPT/branch/main/graph/badge.svg?token=DeveloperGPT_token_here)](https://codecov.io/gh/luo-anthony/DeveloperGPT) -->

DeveloperGPT is a terminal application that uses the [OpenAI API](https://openai.com/blog/openai-api) with the **gpt-3.5-turbo** model to help developers be more productive. Currently DeveloperGPT provides two main functionalities:
#### 1. Natural Language to Terminal Commands
![Natural Language Example](https://github.com/luo-anthony/DeveloperGPT/raw/main/samples/commandrequest.png)

#### 2. Chat with OpenAI GPT-3.5 Inside the Terminal
![Chat Example](https://github.com/luo-anthony/DeveloperGPT/raw/main/samples/chat.png)

NOTE: Chat moderation is **NOT** implemented - all your chat messages should follow the OpenAI terms of use. 


## Install it from PyPI
```bash
pip install developergpt
```

### Setup
Get your own OpenAI API Key: https://platform.openai.com/account/api-keys

```bash
# Do this once 
# set OpenAI API Key (using zsh for example)
$ echo 'export OPENAI_API_KEY=[your_key_here]' >> ~/.zshenv

# reload the environment (or just quit and open a new terminal)
$ source ~/.zshenv
```

## Usage
```bash
# see available commands
$ developergpt 

# chat with GPT-3.5 inside the terminal 
$ developergpt chat

# natural language to terminal commands
$ developergpt cmd
```

## Development

DeveloperGPT is currently under active development.

Read the [CONTRIBUTING.md](CONTRIBUTING.md) file.

### Future Work
- Add tests + update CI pipeline
- Switch to poetry package manager 
- Prettify model output 
- Support other models (hugging-face)
- Add docs 

## Credit
- This project uses the Python project template from https://github.com/rochacbruno/python-project-template
- This project was written with assistance from ChatGPT and Github CoPilot. 
