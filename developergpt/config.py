"""
DeveloperGPT by luo-anthony
"""

import os
import platform
import sys
from typing import Optional

from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.key_binding.key_processor import KeyPressEvent
from prompt_toolkit.keys import Keys
from prompt_toolkit.styles import Style
from rich.console import Console

### Appearance Constants ###
DEFAULT_COLUMN_WIDTH = 100

INPUT_STYLE = Style.from_dict(
    {
        "prompt": "bold ansigreen",
    }
)

### Supported LLMs and Configuration ###
GPT35 = "gpt35"
GPT4 = "gpt4"
ZEPHYR = "zephyr"
GEMMA = "gemma"
GEMMA_BASE = "gemma-base"
GEMINI = "gemini"
MISTRAL_Q6 = "mistral-q6"
MISTRAL_Q4 = "mistral-q4"
MISTRAL_HF = "mistral"
SONNET = "sonnet"
HAIKU = "haiku"
BLOOM = "bloom"  # not supported due to poor performance
SUPPORTED_MODELS = set(
    [
        GPT35,
        GPT4,
        GEMINI,
        ZEPHYR,
        MISTRAL_Q6,
        MISTRAL_Q4,
        MISTRAL_HF,
        GEMMA,
        GEMMA_BASE,
        SONNET,
        HAIKU,
    ]
)
OFFLINE_MODEL_CTX = 4000
OFFLINE_MODELS = set([MISTRAL_Q6, MISTRAL_Q4])
OFFLINE_MODEL_CACHE_DIR = os.path.expanduser("~/.cache/developergpt")

LLAMA_CPP_MODEL_MAP = {
    MISTRAL_Q6: (
        "TheBloke/Mistral-7B-Instruct-v0.2-GGUF",
        "mistral-7b-instruct-v0.2.Q6_K.gguf",
        "mistral-instruct",
    ),
    MISTRAL_Q4: (
        "TheBloke/Mistral-7B-Instruct-v0.2-GGUF",
        "mistral-7b-instruct-v0.2.Q4_K_M.gguf",
        "mistral-instruct",
    ),
}

OPENAI_MODEL_MAP = {
    GPT35: "gpt-3.5-turbo",
    GPT4: "gpt-4-turbo",
}

ANTHROPIC_MODEL_MAP = {
    SONNET: "claude-3-sonnet-20240229",
    HAIKU: "claude-3-haiku-20240307",
}

HF_MODEL_MAP = {
    ZEPHYR: "HuggingFaceH4/zephyr-7b-beta",
    GEMMA: "google/gemma-1.1-7b-it",
    GEMMA_BASE: "google/gemma-7b",
    MISTRAL_HF: "mistralai/Mistral-7B-Instruct-v0.2",
    BLOOM: "bigscience/bloom",
}

HF_INSTRUCT_MODELS = set([GEMMA, ZEPHYR, MISTRAL_HF])

# set of models that support the new chat completion endpoint
HF_CHAT_COMPLETION_MODELS = set([ZEPHYR])

GOOGLE_MODEL_MAP = {
    GEMINI: "gemini-1.0-pro",
}

### API Key Constants ###

GOOGLE_API_KEY = "GOOGLE_API_KEY"
OPEN_AI_API_KEY = "OPENAI_API_KEY"
HUGGING_FACE_API_KEY = "HUGGING_FACE_API_KEY"
ANTHROPIC_API_KEY = "ANTHROPIC_API_KEY"

### General Configuration ###

USER_PLATFORM = platform.platform()
CMD_TEMP = 0.01


def get_environ_key(keyname: str, console: Console) -> str:
    key = os.environ.get(keyname, None)
    if not key:
        console.print(
            f"""[bold red]No {keyname} environment variable found. Please set the {keyname} environment variable.[/bold red]
            export {keyname}=<your_api_key>"""
        )
        sys.exit(-1)
    return key


def get_environ_key_optional(keyname: str, console: Console) -> Optional[str]:
    key = os.environ.get(keyname, None)
    if not key:
        console.print(
            f"""[bold yellow]No {keyname} environment variable found. DeveloperGPT will still work but you may be rate-limited. 
For full access, set the {keyname} environment variable.[/bold yellow]"""
        )
    return key


kb = KeyBindings()


@kb.add(Keys.Enter, eager=True)
def _(event: KeyPressEvent):
    buff = event.app.current_buffer
    if buff.complete_state:
        # during completion, enter will select the current completion instead of submitting input
        if buff.complete_state.current_completion:
            buff.apply_completion(buff.complete_state.current_completion)
            return  # don't submit input
    buff.validate_and_handle()
