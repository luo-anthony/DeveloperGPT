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

# appearance constants
DEFAULT_COLUMN_WIDTH = 100

INPUT_STYLE = Style.from_dict(
    {
        "prompt": "bold ansigreen",
    }
)

# supported models
GPT35 = "gpt35"
GPT4 = "gpt4"
OPENCHAT = "openchat"
ZEPHYR = "zephyr"
SUPPORTED_MODELS = set([GPT35, GPT4, OPENCHAT, ZEPHYR])

OPENAI_MODEL_MAP = {"gpt35": "gpt-3.5-turbo", "gpt4": "gpt-4"}

HF_MODEL_MAP = {
    "openchat": "openchat/openchat_3.5",
    "zephyr": "HuggingFaceH4/zephyr-7b-beta",
}

OPEN_AI_API_KEY = "OPENAI_API_KEY"
HUGGING_FACE_API_KEY = "HUGGING_FACE_API_KEY"

USER_PLATFORM = platform.platform()


def get_environ_key(keyname: str, console: Console) -> str:
    key = os.environ.get(keyname, None)
    if not key:
        console.print(
            f"""[bold red]No {keyname} environment variable found. Please set the {keyname} environment variable.[/bold red]
            \nexport {keyname}=<your_api_key>"""
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
