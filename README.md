# DeveloperGPT
[![License](https://img.shields.io/badge/license-MIT-green)](./LICENSE)
[![LLMs](https://img.shields.io/badge/Supported%20LLMs-Gemini,%20Mistral7B,%20Gemma,%20GPT3.5,%20GPT4,%20Zephyr,%20Claude-blue)](https://img.shields.io/badge/Supported%20LLMs-Gemini,%20Mistral7B,%20Gemma,%20GPT3.5,%20GPT4,%20Zephyr,%20Claude-blue)
[![PyPI](https://img.shields.io/pypi/v/developergpt)](https://pypi.org/project/developergpt/)

DeveloperGPT is a LLM-powered command line tool that enables natural language to terminal commands and in-terminal chat. DeveloperGPT is powered by Google Gemini 1.5 Flash by default but also supports OpenAI GPT LLMs, Anthropic Claude 3 LLMs, open LLMs hosted on Hugging Face, and offline quantized on-device LLMs.

As of June 2024, DeveloperGPT is completely free to use when using Google Gemini 1.5 Pro (used by default) or Google Gemini 1.0 Pro at up to 15 requests per minute.

Additionally, DeveloperGPT supports [quantized Mistral-7B-Instruct](https://huggingface.co/TheBloke/Mistral-7B-Instruct-v0.2-GGUF) LLMs via llama.cpp for fully offline on-device use (these LLMs can run on machines without a dedicated GPU - see [llama.cpp](https://github.com/ggerganov/llama.cpp) for more details).

#### Supported LLMs
Switch between different LLMs using the `--model` flag: `developergpt --model [llm_name] [cmd, chat]`
| Model(s)                                   | Source                                                                                                                       | Details                                                  |
| ------------------------------------------ | ---------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------- |
| **Gemini Pro**, **Gemini Flash** (default) | [Google Gemini 1.0 Pro, Gemini 1.5 Flash](https://deepmind.google/technologies/gemini/)                                      | Free (up to 15 requests/min), Google AI API Key Required |
| **GPT35, GPT4**                            | [OpenAI](https://platform.openai.com/docs/models)                                                                            | Pay-Per-Usage, OpenAI API Key Required                   |
| **Haiku, Sonnet**                          | [Anthropic (Claude 3)](https://docs.anthropic.com/claude/docs/models-overview)                                               | Pay-Per-Usage, Anthropic API Key Required                |
| **Zephyr**                                 | [Zephyr7B-Beta](https://huggingface.co/HuggingFaceH4/zephyr-7b-beta)                                                         | Free, Open LLM, Hugging Face Inference API               |
| **Gemma, Gemma-Base**                      | [Gemma-1.1-7B-Instruct](https://huggingface.co/google/gemma-1.1-7b-it), [Gemma-Base](https://huggingface.co/google/gemma-7b) | Free, Open LLM, Hugging Face Inference API               |
| **Mistral-Q6, Mistral-Q4**                 | [Quantized GGUF Mistral-7B-Instruct](https://huggingface.co/TheBloke/Mistral-7B-Instruct-v0.2-GGUF)                          | Free, Open LLM, OFFLINE, ON-DEVICE                       |
| **Mistral**                                | [Mistral-7B-Instruct](https://huggingface.co/mistralai/Mistral-7B-Instruct-v0.2)                                             | Free, Open LLM, Hugging Face Inference API               |

- `mistral-q6` and `mistral-q4` are [Quantized GGUF Mistral-7B-Instruct](https://huggingface.co/TheBloke/Mistral-7B-Instruct-v0.2-GGUF) LLMs running locally on-device using llama.cpp (Q6_K quantized and Q4_K quantized models respectively)


### Features 
DeveloperGPT has 2 main features. 
#### 1. Natural Language to Terminal Commands
**Usage:** `developergpt cmd [your natural language command request]`
```bash
# Example
$ developergpt cmd list all git commits that contain the word llm
```

![Natural Language Example 1](https://github.com/luo-anthony/DeveloperGPT/raw/main/samples/cmd_demo.gif)

Use `developergpt cmd --fast` to get commands faster without any explanations (~1.6 seconds with `--fast` vs. ~3.2 seconds with regular on average). Commands given in `fast` mode may be less accurate - see [DeveloperGPT Natural Language to Terminal Command Accuracy](#developergpt-natural-language-to-terminal-command-accuracy) for more details.

```bash
# Fast Mode: Commands are given without explanation for faster response
$ developergpt cmd --fast [your natural language command request]
```

Use `developergpt --model [model_name] cmd` to use a different LLM instead of Gemini Flash (used by default).  
```bash
# Example: Natural Language to Terminal Commands using the GPT-3.5 instead of Gemini Flash
$ developergpt --model gpt35 cmd [your natural language command request]
```

#### 2. Chat inside the Terminal

**Usage:** `developergpt chat`
```bash
# Chat with DeveloperGPT using Gemini 1.5 Flash (default)
$ developergpt chat
```

![Chat Example](https://github.com/luo-anthony/DeveloperGPT/raw/main/samples/chat_demo.gif)

Use `developergpt --model [model_name] chat` to use a different LLM.  
```bash
# Example
$ developergpt --model mistral chat
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

### DeveloperGPT Natural Language to Terminal Command Accuracy
Accuracy of DeveloperGPT varies depending on the LLM used as well as the mode (`--fast` vs. regular). Shown below are Top@1 Accuracy of different LLMs on a set of [85 natural language command requests](https://github.com/luo-anthony/DeveloperGPT/blob/evaluation_v2/evaluation/85_command_requests.txt) (this isn't a rigorous evaluation, but it gives a rough sense of accuracy). Github CoPilot in the CLI v1.0.1 is also included for comparison. 

![DeveloperGPT LLM Accuracy](https://github.com/luo-anthony/DeveloperGPT/raw/main/samples/evaluation.png)

### Setup
#### Using Google Gemini (Default)
By default, DeveloperGPT uses Google Gemini 1.5 Flash. To use Gemini 1.0 Pro or Gemini 1.5 Flash, you will need an API key (free to use up to 15 queries per minute).

1. Get your own Google AI Studio API Key: https://makersuite.google.com/app/apikey
2. Set your Google API Key as an environment variable. You only need to do this once. 
```bash
# set Google API Key (using zsh for example)
$ echo 'export GOOGLE_API_KEY=[your_key_here]' >> ~/.zshenv

# reload the environment (or just quit and open a new terminal)
$ source ~/.zshenv
```

#### Using Hugging Face Inference API Open LLMs
To use open LLMs such as Gemma or Mistral hosted on Hugging Face, you can optionally set up a [Hugging Face Inference API](https://huggingface.co/settings/tokens) token as an environment variable using the steps below. 
See https://huggingface.co/docs/api-inference/index for more details. 

```bash
# [OPTIONAL] set Hugging Face token (using zsh for example)
$ echo 'export HUGGING_FACE_API_KEY=[your_key_here]' >> ~/.zshenv

# reload the environment (or just quit and open a new terminal)
$ source ~/.zshenv
```

#### Using Mistral-7B-Instruct (Offline)
To use Mistral-7B-Instruct, just run DeveloperGPT with the `--offline` flag. This will download the model on first run and use it locally in any future runs (no internet connection is required after the first use). No special setup is required. 
```bash
developergpt --offline chat
```

#### Using OpenAI GPT LLMs
To use GPT-3.5 or GPT-4, you will need an OpenAI API key.

1. Get your own OpenAI API Key and setup billing: https://platform.openai.com/account/api-keys
2. Set your OpenAI API Key as an environment variable. You only need to do this once. 
```bash
# set OpenAI API Key (using zsh for example)
$ echo 'export OPENAI_API_KEY=[your_key_here]' >> ~/.zshenv

# reload the environment (or just quit and open a new terminal)
$ source ~/.zshenv
```

#### Using Anthropic LLMs
To use Anthropic Claude 3 Sonnet or Haiku, you will need an Anthropic API key.

1. Get your own Anthropic API Key: https://www.anthropic.com/api
2. Set your Anthropic API Key as an environment variable. You only need to do this once. 
```bash
# set Anthropic API Key (using zsh for example)
$ echo 'export ANTHROPIC_API_KEY=[your_key_here]' >> ~/.zshenv

# reload the environment (or just quit and open a new terminal)
$ source ~/.zshenv
```


### LLM Cost
#### Google Gemini LLMs
As of June 2024, Google Gemini 1.0 Pro and Gemini 1.5 Flash are free to use up to 15 queries per minute. For more information, see: https://ai.google.dev/pricing

#### Hugging Face Hosted Open LLMs 
As of April 2024, using Hugging Face Inference API hosted LLMs is free but rate limited. See https://huggingface.co/docs/api-inference/index for more details.

#### Mistral-7B-Instruct (llama.cpp)
Mistral-7B-Instruct is free to use and runs locally on-device.

#### OpenAI GPT
You can monitor your OpenAI API usage here: https://platform.openai.com/account/usage. The average cost per query using GPT-3.5 is < 0.1 cents. Using GPT-4 is not recommended as GPT-3.5 is much more cost-effective and achieves a very high accuracy for most commands. 

#### Anthropic Claude LLMs
You can monitor your Anthropic API usage here: https://console.anthropic.com/settings/plans. The average cost per query using Claude 3 Haiku is < 0.1 cents. See https://www.anthropic.com/api for pricing details. 

## Contributing
Read the [CONTRIBUTING.md](CONTRIBUTING.md) file.

## Credit
- Thanks to Hugging Face and the NLP/LLM community for open LLMs, generous free hosted inference APIs, tools, quantization, and other resources! 
- Thanks to Google for the generous Gemini API free tier. 
- This project uses the Python project template from https://github.com/rochacbruno/python-project-template
