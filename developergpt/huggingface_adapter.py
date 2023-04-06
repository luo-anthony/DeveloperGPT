"""
DeveloperGPT by luo-anthony
"""

import platform
import re

from rich.console import Console

# using: https://pypi.org/project/text-generation/
from text_generation import InferenceAPIClient

from developergpt import config, utils

# TODO: add more hugging_face models: flan-ul2, Vicuna-13B?


def format_bloom_input(user_input: str) -> str:
    model_input = f"""To {user_input} on a {platform.platform()} machine, use the following command(s):"""
    return model_input


def model_command(user_input: str, console: "Console") -> list:
    model = "bigscience/bloom"
    client = InferenceAPIClient(model)
    MAX_RESPONSE_TOKENS = 128

    panel_width = min(console.width, config.DEFAULT_COLUMN_WIDTH)

    # TODO add context size + token reduction for hugging-face
    # TODO add prior context
    # TODO see if can get explanations working

    model_input = format_bloom_input(user_input)

    with console.status("[bold blue]Decoding request") as _:
        response = client.generate(
            model_input, max_new_tokens=MAX_RESPONSE_TOKENS
        ).generated_text

    # console.log(response)

    # only get first response - responses are delinated by "\n\n"
    cmds = response.split("\n\n")[0]

    # filter cmd output
    cmd_strings = []
    for c in cmds.split("\n"):
        if any(char.isalnum() for char in c):
            c = c.strip()
            c = re.sub(r"^(\$+)", "", c)  # remove leading $
            cmd_strings.append(c)

    utils.pretty_print_commands(cmd_strings, console, panel_width)

    return cmd_strings
