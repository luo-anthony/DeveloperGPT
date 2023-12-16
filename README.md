# DeveloperGPT
[![License](https://img.shields.io/badge/license-MIT-green)](./LICENSE)
[![LLMs](https://img.shields.io/badge/Supported%20LLMs-GPT3.5,%20GPT4,%20Gemini,%20OpenChat,%20Zephyr-blue)](https://img.shields.io/badge/Supported%20LLMs-GPT,%20BLOOM-blue)
[![PyPI](https://img.shields.io/pypi/v/developergpt)](https://pypi.org/project/developergpt/)
[![OpenAI GPTs](https://img.shields.io/badge/OpenAI%20GPTs-Try%20the%20online%20DeveloperGPT-8A2BE2)](https://chat.openai.com/g/g-mfPPe6MKC-developergpt)

DeveloperGPT is a LLM-powered command line tool that enables natural language to terminal commands and in-terminal chat. DeveloperGPT is powered by [OpenAI's GPT3.5](https://platform.openai.com/docs/models) (by default) with additional support for open-source LLMs and Google's new Gemini model.

**Supported LLMs**
- OpenAI: GPT3.5 (default), GPT4
- Google: [Gemini](https://deepmind.google/technologies/gemini/)
- Open Source (Hugging Face): [Zephyr](https://huggingface.co/HuggingFaceH4/zephyr-7b-beta), [OpenChat](https://huggingface.co/openchat/openchat_3.5)

DeveloperGPT has two main features:
#### 1. Natural Language to Terminal Commands
**Supported LLMs:** GPT3.5 (default), GPT4, Gemini, Zephyr, OpenChat

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

Use `developergpt --model [gemini,zephyr,openchat,gpt4] cmd` to use a different LLM instead of GPT3.5. 
```bash
# Example: Natural Language to Terminal Commands using the Zephyr LLM instead of GPT3.5
$ developergpt --model zephyr cmd [your natural language command request]
```
GPT3.5 is generally accurate for the majority of natural langauge to command requests and is significantly cheaper to use than GPT4. Google's Gemini model is the fastest model with accuracy similar to OpenAI GPT models. Open-source models such as Zephyr or OpenChat are less accurate and may result in in unexpected or undefined behavior. With all models, it is always good practice to manually verify the command output before running it.

![Natural Language Example 1](https://github.com/luo-anthony/DeveloperGPT/raw/main/samples/cmd_demo.gif)

#### 2. Chat inside the Terminal
**Supported LLMs:** GPT3.5 (default), GPT4, Gemini, Zephyr, OpenChat

**Usage:** `developergpt chat`
```bash
# chat with DeveloperGPT using GPT3.5 (default)
$ developergpt chat
```

Use `developergpt --model [gemini,zephyr,openchat,gpt4] chat` to use a different LLM instead of GPT3.5. 
```bash
# chat with DeveloperGPT using Google's Gemini
$ developergpt --model gemini chat

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

#### Using Open-Source LLMs (Optional)
To use open-source LLMs such as Zephyr or OpenChat hosted on Hugging Face, you can optionally set up a [Hugging Face](https://huggingface.co/settings/tokens) or [Inference API](https://huggingface.co/docs/api-inference/index) token as an environment variable using the steps below. Setting up a token is **not required**, but it will allow you to make more requests without being rate limited. 

```bash
# [OPTIONAL] set Hugging Face token (using zsh for example)
# You only need to do this once
$ echo 'export HUGGING_FACE_API_KEY=[your_key_here]' >> ~/.zshenv

# reload the environment (or just quit and open a new terminal)
$ source ~/.zshenv
```

#### Using Google Gemini
Using Google's Gemini model requires some more setup than other LLMs. 
1. Follow the instructions to create a Google Cloud project and setup billing: https://developers.google.com/workspace/guides/create-project
2. Enable the Vertex AI API for your created project: https://console.cloud.google.com/apis/library/aiplatform.googleapis.com
3. Install the Google Cloud CLI on your machine: https://cloud.google.com/sdk/docs/install
4. Initialize Google Cloud CLI
```bash
$ gcloud init
```

5. Create local authentical credentials for your Google Account
```bash
$ gcloud auth application-default login
```

6. Set the `GCLOUD_PROJECT_ID` and `GCLOUD_LOCATION` environment variables. For a list of Vertex AI locations, see https://cloud.google.com/vertex-ai/docs/general/locations.
```bash
# set GCLOUD_PROJECT_ID, this should be the project ID of your Google Cloud project
$ echo 'export GCLOUD_PROJECT_ID=[your_project_id]' >> ~/.zshenv

# set GCLOUD_LOCATION, pick the location closest to you from the list of Vertex AI locations
$ echo 'export GCLOUD_LOCATION=[location]' >> ~/.zshenv

# reload the environment (or just quit and open a new terminal)
$ source ~/.zshenv
```

### Monitoring Usage

#### OpenAI API Usage
You can monitor your OpenAI API usage here: https://platform.openai.com/account/usage. Based on preliminary testing, using DeveloperGPT with GPT3.5 should cost no more than 10 cents per day with regular usage. 

#### Hugging-Face Usage 
Currently, using Hugging Face LLMs does not require a token and is free but rate limited. To avoid rate limit, you can set a token using the instructions above. 

#### Google Cloud Usage
TODO 

## Contributing
Read the [CONTRIBUTING.md](CONTRIBUTING.md) file.

### Future Roadmap
- Add support for more open-source models such as LLAMA 2

## Credit
- Thanks to Hugging Face and the NLP community for open-source models and prompts! 
- This project uses the Python project template from https://github.com/rochacbruno/python-project-template
