# DeveloperGPT
[![License](https://img.shields.io/badge/license-MIT-green)](./LICENSE)
[![CI](https://github.com/luo-anthony/DeveloperGPT/actions/workflows/main.yml/badge.svg)](https://github.com/luo-anthony/DeveloperGPT/actions/workflows/main.yml)
[![PyPI](https://img.shields.io/pypi/v/developergpt)](https://pypi.org/project/developergpt/)
[![LLMs](https://img.shields.io/badge/Supported%20LLMs-GPT3.5,%20BLOOM-blue)](https://img.shields.io/badge/Supported%20LLMs-GPT3.5,%20BLOOM-blue)


<!-- [![codecov](https://codecov.io/gh/luo-anthony/DeveloperGPT/branch/main/graph/badge.svg?token=DeveloperGPT_token_here)](https://codecov.io/gh/luo-anthony/DeveloperGPT) -->

DeveloperGPT is a terminal application that uses the latest LLMs to help developers be more productive. 

By default, DeveloperGPT uses the [gpt-3.5-turbo](https://platform.openai.com/docs/models) model from OpenAI, but you can also use the open-source [BLOOM](https://bigscience.huggingface.co/blog/bloom) model. Support for more models and features is coming soon! 

In our testing, we recommend GPT-3.5 (default) as it generally yields better results and is able to handle more complex requests. 

DeveloperGPT has two main features:
#### 1. Natural Language to Terminal Commands
**Supported Models:** GPT3.5 (default), BLOOM
![Natural Language Example](https://github.com/luo-anthony/DeveloperGPT/raw/main/samples/cmddemo.gif)

**NOTE:** The BLOOM model command output may not be accurate, especially for more complex commands. Using the BLOOM model may also result in unexpected or undefined behavior. 

With both models, it is always good practice to manually verify the command output before running it.

#### 2. Chat inside the Terminal
**Supported Models:** GPT3.5 (default), BLOOM
![Chat Example](https://github.com/luo-anthony/DeveloperGPT/raw/main/samples/chatdemo.gif)

**NOTE:** Chat moderation is **NOT** implemented - all your chat messages should follow the OpenAI and BLOOM terms of use. 


## Install DeveloperGPT from PyPI
```bash
pip install -U developergpt
```

### Setup

By default, DeveloperGPT uses the GPT-3.5 model from OpenAI. From limited testing, the GPT-3.5 model has the best results. 

Get your own OpenAI API Key: https://platform.openai.com/account/api-keys

```bash
# Do this once 
# set OpenAI API Key (using zsh for example)
$ echo 'export OPENAI_API_KEY=[your_key_here]' >> ~/.zshenv

# reload the environment (or just quit and open a new terminal)
$ source ~/.zshenv
```

If you want to use the BLOOM model instead, you can optionally set up a [Hugging Face User Access](https://huggingface.co/settings/tokens) or [Inference API](https://huggingface.co/docs/api-inference/index) token. Setting up a token is not required (BLOOM model will work without any token or key), but it will allow you to make more requests without being rate limited. 

```bash
# Do this once 
# set Hugging Face API token (using zsh for example)
$ echo 'export HUGGING_FACE_API_KEY=[your_key_here]' >> ~/.zshenv

# reload the environment (or just quit and open a new terminal)
$ source ~/.zshenv
```

## Usage
```bash
# see available commands
$ developergpt 

# chat with DeveloperGPT using GPT-3.5 (default)
$ developergpt chat

# natural language to terminal commands using GPT-3.5 (default)
$ developergpt cmd

# chat with DeveloperGPT using BLOOM model instead
$ developergpt --model bloom chat

# natural langauge to terminal commands using BLOOM model instead
$ developergpt --model bloom cmd

# give feedback
$ developergpt feedback
```

### OpenAI API Usage (GPT-3.5)
You can monitor your OpenAI API usage here: https://platform.openai.com/account/usage

DeveloperGPT uses the `gpt-3.5-turbo` model which is very cost efficient (1/10 the cost of models such as `text-davinci-003`). Based on preliminary testing, using DeveloperGPT should cost no more than 10 cents per day (assuming ~100 requests/day). 

### Hugging-Face Usage (BLOOM)
Currently, using the BLOOM model does not require a token and is free but rate limited. To avoid rate limit, you can set a token using the instructions above. 

## Contributing
Read the [CONTRIBUTING.md](CONTRIBUTING.md) file.

### Future Roadmap
- Add support for open-source models (Alpaca, Vicuna, Dolly, etc.)

## Credit
- Thanks to Hugging Face and the NLP community for open-source models and prompts! 
- This project uses the Python project template from https://github.com/rochacbruno/python-project-template
- This project was written with assistance from ChatGPT and Github CoPilot. 
