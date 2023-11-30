"""
DeveloperGPT by luo-anthony
"""


import json
import os
import sys
from typing import Optional

import pyperclip
import requests
import tiktoken
from prompt_toolkit import PromptSession
from prompt_toolkit.completion import Completer, Completion
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel

from developergpt import config


def pretty_print_commands(commands: list, console: Console, panel_width: int) -> None:
    # print all the commands in a panel
    commands_format = "\n\n".join([f"""- `{c}`""" for c in commands])

    cmd_out = Markdown(
        commands_format,
        inline_code_lexer="bash",
    )

    console.print(
        Panel(
            cmd_out,
            title="[bold blue]Command(s)[/bold blue]",
            title_align="left",
            width=panel_width,
        )
    )


def print_command_response(
    model_output: Optional[str], console: Console, fast_mode: bool, model: str
) -> list:
    if not model_output:
        return []

    panel_width = min(console.width, config.DEFAULT_COLUMN_WIDTH)

    if fast_mode and model in config.HF_MODEL_MAP:
        cmd_strings = model_output.split("`\n")
        cmd_strings = [c.replace("`", "") for c in cmd_strings]
    else:
        try:
            output_data = json.loads(model_output)
        except json.decoder.JSONDecodeError:
            console.print(
                "[bold red]Error: Could not parse model response properly[/bold red]"
            )
            console.log(model_output)
            return []

        if output_data.get("error", 0) or "commands" not in output_data:
            console.print(
                "[bold red]Error: Could not find commands for this request[/bold red]"
            )
            return []
        commands = output_data.get("commands", {})
        if fast_mode:
            cmd_strings = commands
        else:
            cmd_strings = [cmd.get("cmd_to_execute", "") for cmd in commands]

    # print all the commands in a panel
    pretty_print_commands(cmd_strings, console, panel_width)

    if not fast_mode:
        # print all the explanations in a panel
        explanation_items = []
        for cmd in commands:
            explanation_items.extend(
                [f"- {c}" for c in cmd.get("cmd_explanations", [])]
            )
            explanation_items.extend(
                [f"\t- {c}" for c in cmd.get("arg_explanations", [])]
            )

        arg_out = Markdown("\n".join(explanation_items))

        console.print(
            Panel(
                arg_out,
                title="[bold blue]Explanation[/bold blue]",
                title_align="left",
                width=panel_width,
            )
        )
    return cmd_strings


def copy_comands_to_cliboard(commands: list):
    pyperclip.copy("\n".join(commands))


def prompt_user_input(
    input_request: str,
    session: PromptSession,
    console: Console,
    completer=None,
    complete_style=None,
    auto_suggest=None,
    key_bindings=None,
) -> str:
    user_input = session.prompt(
        input_request,
        style=config.INPUT_STYLE,
        completer=completer,
        complete_style=complete_style,
        auto_suggest=auto_suggest,
        key_bindings=key_bindings,
    ).strip()

    if len(user_input) == 0:
        return ""

    if user_input.lower() == "quit" or user_input.lower() == "exit":
        console.print("[bold blue]Exiting... [/bold blue]")
        sys.exit(0)

    return user_input


def check_reduce_context(
    messages: list, token_limit: int, model: str, ctx_removal_index: int
) -> tuple:
    """Check if token limit is exceeded and remove old context starting at ctx_removal_index if so."""
    n_tokens = count_msg_tokens(messages, model)
    if n_tokens > token_limit:
        messages, n_tokens = remove_old_contexts(
            messages, token_limit, n_tokens, model, ctx_removal_index
        )
    return messages, n_tokens


def count_msg_tokens(messages: list, model: str) -> int:
    """
    Returns the approximate number of tokens used by a list of messages
    function adapted from: https://github.com/openai/openai-cookbook/blob/main/examples/How_to_count_tokens_with_tiktoken.ipynb
    """
    try:
        encoding = tiktoken.encoding_for_model(model)
    except KeyError:
        print("Warning: model not found. Using cl100k_base encoding.")
        encoding = tiktoken.get_encoding("cl100k_base")
    if model in {
        "gpt-3.5-turbo-0613",
        "gpt-3.5-turbo-16k-0613",
        "gpt-4-0314",
        "gpt-4-32k-0314",
        "gpt-4-0613",
        "gpt-4-32k-0613",
    }:
        tokens_per_message = 3
        tokens_per_name = 1
    elif model == "gpt-3.5-turbo-0301":
        tokens_per_message = (
            4  # every message follows <|start|>{role/name}\n{content}<|end|>\n
        )
        tokens_per_name = -1  # if there's a name, the role is omitted
    elif "gpt-3.5-turbo" in model:
        # print("Warning: gpt-3.5-turbo may update over time. Returning num tokens assuming gpt-3.5-turbo-0613.")
        return count_msg_tokens(messages, model="gpt-3.5-turbo-0613")
    elif "gpt-4" in model:
        # print("Warning: gpt-4 may update over time. Returning num tokens assuming gpt-4-0613.")
        return count_msg_tokens(messages, model="gpt-4-0613")
    else:
        raise NotImplementedError(
            f"""num_tokens_from_messages() is not implemented for model {model}. See https://github.com/openai/openai-python/blob/main/chatml.md for information on how messages are converted to tokens."""
        )
    num_tokens = 0
    for message in messages:
        num_tokens += tokens_per_message
        for key, value in message.items():
            num_tokens += len(encoding.encode(value))
            if key == "name":
                num_tokens += tokens_per_name
    num_tokens += 3  # every reply is primed with <|start|>assistant<|message|>
    return num_tokens


def remove_old_contexts(
    messages: list, token_limit: int, n_tokens: int, model: str, ctx_removal_index: int
) -> tuple:
    """Remove old contexts until token limit is not exceeded."""
    while n_tokens > token_limit:
        removed_ctx = messages.pop(ctx_removal_index)
        n_removed = count_msg_tokens([removed_ctx], model)
        n_tokens -= n_removed

    return messages, n_tokens


class PathCompleter(Completer):
    """A completer for file paths."""

    def get_completions(self, document, complete_event):
        if complete_event.completion_requested:
            # only display completions when the user presses tab
            cwd = os.getcwd()

            text = document.text_before_cursor.lstrip().lower().split(" ")[-1]
            # print(f"text={text}")

            auto_completion = []

            if text.startswith("~/"):
                f_path = os.path.expanduser(text)
            elif text.startswith("/"):
                f_path = text
            else:
                f_path = os.path.join(cwd, text)

            curr_dir = os.path.dirname(f_path)
            fname = os.path.basename(f_path) if len(text) > 0 else ""

            # print(f"f_path={f_path}, fname={fname}, curr_dir={dir}")

            if os.path.isdir(curr_dir):
                # Generate a list of matching file names in the current directory
                # TODO: possibly change to glob + re to handle regular expressions
                auto_completion = [
                    os.path.join(curr_dir, f)
                    for f in os.listdir(curr_dir)
                    if fname in f.lower()
                ]

            # Yield the completions
            for completion in auto_completion:
                # simplify the completion substitution if possible
                if text.startswith("~/"):
                    completion = completion.replace(os.path.expanduser("~/"), "~/")
                elif cwd in completion:
                    completion = os.path.relpath(completion, cwd)

                # substitute for the full path but only display the basename of the file
                yield Completion(
                    completion,
                    display=os.path.basename(completion),
                    start_position=-len(text),
                )


def check_connectivity(url: str = "http://www.google.com", timeout: int = 8) -> bool:
    try:
        _ = requests.get(url, timeout=timeout)
        return True
    except requests.ConnectionError:
        return False
