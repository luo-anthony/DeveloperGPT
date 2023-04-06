"""
DeveloperGPT by luo-anthony
"""


import os
import sys

import tiktoken
from prompt_toolkit.completion import Completer, Completion
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel

from developergpt import config


def pretty_print_commands(commands: list, console: "Console", panel_width: int):
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


def prompt_user_input(
    input_request,
    session,
    console,
    completer=None,
    complete_style=None,
    auto_suggest=None,
):
    user_input = session.prompt(
        input_request,
        style=config.INPUT_STYLE,
        completer=completer,
        complete_style=complete_style,
        auto_suggest=auto_suggest,
    ).strip()

    if len(user_input) == 0:
        return ""

    if user_input.lower() == "quit":
        console.print("[bold blue]Exiting... [/bold blue]")
        sys.exit(0)

    return user_input


def check_reduce_context(
    messages: list, token_limit: int, model: str, ctx_removal_index: int
) -> tuple[list, int]:
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
        # print("Warning: model not found. Using cl100k_base encoding.")
        encoding = tiktoken.get_encoding("cl100k_base")
    if model == "gpt-3.5-turbo":
        # print(
        #     "Warning: gpt-3.5-turbo may change over time. Returning num tokens assuming gpt-3.5-turbo-0301."
        # )
        return count_msg_tokens(messages, model="gpt-3.5-turbo-0301")
    elif model == "gpt-4":
        # print(
        #     "Warning: gpt-4 may change over time. Returning num tokens assuming gpt-4-0314."
        # )
        return count_msg_tokens(messages, model="gpt-4-0314")
    elif model == "gpt-3.5-turbo-0301":
        tokens_per_message = (
            4  # every message follows <|start|>{role/name}\n{content}<|end|>\n
        )
        tokens_per_name = -1  # if there's a name, the role is omitted
    elif model == "gpt-4-0314":
        tokens_per_message = 3
        tokens_per_name = 1
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
) -> tuple[list, int]:
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
                if cwd in completion:
                    completion = os.path.relpath(completion, cwd)
                elif text.startswith("~/"):
                    completion = completion.replace(os.path.expanduser("~/"), "~/")

                # substitute for the full path but only display the basename of the file
                yield Completion(
                    completion,
                    display=os.path.basename(completion),
                    start_position=-len(text),
                )
