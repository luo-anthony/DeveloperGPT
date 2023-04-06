"""
DeveloperGPT by luo-anthony
"""
import os
import sys

from prompt_toolkit.styles import Style

# appearance constants
DEFAULT_COLUMN_WIDTH = 100

INPUT_STYLE = Style.from_dict(
    {
        "prompt": "bold ansigreen",
    }
)

# supported models
GPT35 = "gpt-3.5"
BLOOM = "bloom"
SUPPORTED_MODELS = set([GPT35, BLOOM])

OPEN_AI_API_KEY = "OPENAI_API_KEY"
HUGGING_FACE_API_KEY = "HUGGING_FACE_API_KEY"


def get_environ_key(keyname, console) -> str:
    key = os.environ.get(keyname, None)
    if not key:
        console.print(
            f"""[bold red]No {keyname} environment variable found. Please set the {keyname} environment variable.[/bold red]
            \nexport {keyname}=<your_api_key>"""
        )
        sys.exit(-1)
    return key
