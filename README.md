# DeveloperGPT
[![License](https://img.shields.io/badge/license-MIT-green)](./LICENSE)
[![LLMs](https://img.shields.io/badge/Supported%20LLMs-Gemini,%20Mistral7B,%20Gemma,%20GPT3.5,%20GPT4,%20Zephyr-blue)](https://img.shields.io/badge/Supported%20LLMs-Gemini,%20Mistral7B,%20Gemma,%20GPT3.5,%20GPT4,%20Zephyr-blue)
[![PyPI](https://img.shields.io/pypi/v/developergpt)](https://pypi.org/project/developergpt/)

DeveloperGPT is a LLM-powered command line tool that enables natural language to terminal commands and in-terminal chat. DeveloperGPT is powered by Google Gemini Pro by default but also supports OpenAI GPT LLMs, open-source LLMs hosted on Hugging Face, and offline quantized on-device LLMs.

As of April 2024, DeveloperGPT is completely free to use when using Google Gemini Pro 1.0 at up to 15 requests per minute - this is the default model used by DeveloperGPT in the latest version. 

Additionally, DeveloperGPT supports [quantized Mistral-7B-Instruct](https://huggingface.co/TheBloke/Mistral-7B-Instruct-v0.2-GGUF) LLMs via llama.cpp for fully offline on-device use (these LLMs can run on machines without a dedicated GPU - see [llama.cpp](https://github.com/ggerganov/llama.cpp) for more details).

#### Supported LLMs
Switch between different LLMs using the `--model` flag: `developergpt --model [model_name] [cmd, chat]`
| Model(s)                          | Source                                                                                                                       | Details                                                  |
| --------------------------------- | ---------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------- |
| **Gemini** (default)              | [Google AI (Gemini Pro 1.0)](https://deepmind.google/technologies/gemini/)                                                   | Free (up to 15 requests/min), Google AI API Key Required |
| **GPT35, GPT4**                   | [OpenAI](https://platform.openai.com/docs/models)                                                                            | Pay-Per-Usage, OpenAI API Key Required                   |
| **Zephyr**                        | [Zephyr7B-Beta](https://huggingface.co/HuggingFaceH4/zephyr-7b-beta)                                                         | Free, Open-Source, Hugging Face Inference API            |
| **Gemma, Gemma-Base**             | [Gemma-1.1-7B-Instruct](https://huggingface.co/google/gemma-1.1-7b-it), [Gemma-Base](https://huggingface.co/google/gemma-7b) | Free, Open-Source, Hugging Face Inference API            |
| **Mistral-Q6, Mistral-Q4**        | [Quantized GGUF Mistral-7B-Instruct](https://huggingface.co/TheBloke/Mistral-7B-Instruct-v0.2-GGUF)                          | Free, Open-Source, OFFLINE, ON-DEVICE                    |
| **Mistral**                       | [Mistral-7B-Instruct](https://huggingface.co/mistralai/Mistral-7B-Instruct-v0.2)                                             | Free, Open-Source, Hugging Face Inference API            |

- `mistral-q6` and `mistral-q4` are [Quantized GGUF Mistral-7B-Instruct](https://huggingface.co/TheBloke/Mistral-7B-Instruct-v0.2-GGUF) LLMs running locally on-device using llama.cpp (Q6_K quantized and Q4_K quantized models respectively)


### Features 
DeveloperGPT has 2 main features. 
#### 1. Natural Language to Terminal Commands
**Usage:** `developergpt cmd [your natural language command request]`
```bash
# Example
$ developergpt cmd list all commits that contain the word llm in the last 3 days
```

![Natural Language Example 1](https://github.com/luo-anthony/DeveloperGPT/raw/main/samples/cmd_demo.gif)

Use `developergpt cmd --fast` to get commands faster without any explanations (may be less accurate). 
```bash
# Fast Mode: Commands are given without explanation (may be less accurate)
$ developergpt cmd --fast [your natural language command request]
```

Use `developergpt --offline cmd` to use quantized Mistral-7B-Instruct running locally on-device. 
```bash
# Offline Mode: Using quantized Mistral-7B-Instruct running locally on-device (offline)
$ developergpt --offline cmd [your natural language command request]
```

Use `developergpt --model [model_name] cmd` to use a different LLM instead of Gemini Pro (used by default).  
```bash
# Example: Natural Language to Terminal Commands using the GPT3.5 instead of Gemini
$ developergpt --model gpt35 cmd [your natural language command request]
```

#### 2. Chat inside the Terminal

**Usage:** `developergpt chat`
```bash
# Chat with DeveloperGPT using Gemini Pro (default)
$ developergpt chat
```

![Chat Example](https://github.com/luo-anthony/DeveloperGPT/raw/main/samples/chat_demo.gif)

Use `developergpt --offline chat` to use quantized Mistral-7B-Instruct running locally on-device instead of Gemini via API. 

Use `developergpt --model [model_name] chat` to use a different LLM instead of Gemini. 
```bash
# Example
$ developergpt --model gemma chat
```

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
By default, DeveloperGPT uses Google Gemini Pro. To use Gemini Pro, you will need an API key (free to use up to 15 queries per minute).

1. Get your own Google AI Studio API Key: https://makersuite.google.com/app/apikey
2. Set your Google API Key as an environment variable. You only need to do this once. 
```bash
# set Google API Key (using zsh for example)
$ echo 'export GOOGLE_API_KEY=[your_key_here]' >> ~/.zshenv

# reload the environment (or just quit and open a new terminal)
$ source ~/.zshenv
```

#### Using Mistral-7B-Instruct (Offline)
To use Mistral-7B-Instruct, just run DeveloperGPT with the `--offline` flag. This will download the model on first run and use it locally in any future runs (no internet connection is required after the first use). No special setup is required. 
```bash
developergpt --offline chat
```

#### Using OpenAI GPT LLMs
To use GPT3.5 or GPT4, you will need an OpenAI API key.

1. Get your own OpenAI API Key and setup billing: https://platform.openai.com/account/api-keys
2. Set your OpenAI API Key as an environment variable. You only need to do this once. 
```bash
# set OpenAI API Key (using zsh for example)
$ echo 'export OPENAI_API_KEY=[your_key_here]' >> ~/.zshenv

# reload the environment (or just quit and open a new terminal)
$ source ~/.zshenv
```

#### Using Open-Source Hugging Face Inference API LLMs
To use open-source LLMs such as Gemma or Mistral hosted on Hugging Face, you can optionally set up a [Hugging Face Inference API](https://huggingface.co/settings/tokens) token as an environment variable using the steps below. 
See https://huggingface.co/docs/api-inference/index for more details. 

```bash
# [OPTIONAL] set Hugging Face token (using zsh for example)
# You only need to do this once
$ echo 'export HUGGING_FACE_API_KEY=[your_key_here]' >> ~/.zshenv

# reload the environment (or just quit and open a new terminal)
$ source ~/.zshenv
```

### Usage and Cost 
#### Mistral-7B-Instruct (llama.cpp)
Mistral-7B-Instruct is free to use and runs locally on-device.

#### Google Gemini
As of April 2024, Google Gemini is free to use up to 15 queries per minute. For more information, see: https://ai.google.dev/pricing

#### OpenAI GPT
You can monitor your OpenAI API usage here: https://platform.openai.com/account/usage. Based on preliminary testing, using DeveloperGPT with GPT3.5 should cost less than 10 cents per day with regular usage. Using GPT4 is not recommended as GPT3.5 is much more cost-effective and achieves a very high accuracy for most commands. 

#### Hugging Face Hosted Open LLMs 
As of April 2024, using Hugging Face Inference API hosted LLMs is free but rate limited. See https://huggingface.co/docs/api-inference/index for more details. 

## Contributing
Read the [CONTRIBUTING.md](CONTRIBUTING.md) file.

## Credit
- Thanks to Hugging Face and the NLP/LLM community for open-source LLMs, generous free hosted inference API, tools, quantization, and other resources! 
- Thanks to Google for the generous Gemini Pro API free tier. 
- This project uses the Python project template from https://github.com/rochacbruno/python-project-template
