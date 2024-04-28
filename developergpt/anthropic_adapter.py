"""
DeveloperGPT by luo-anthony
"""

import sys
from typing import Optional

import anthropic._exceptions as anthropic_exceptions
from anthropic import Anthropic
from rich.console import Console
from rich.live import Live
from rich.markdown import Markdown
from rich.panel import Panel

from developergpt import config, utils
from developergpt.few_shot_prompts import (
    CHAT_SYS_MSG,
    CMD_SYS_MSG,
    INITIAL_USER_CMD_MSG,
    INITIAL_USER_CMD_MSG_FAST,
)
from developergpt.openai_adapter import (
    BASE_INPUT_CMD_MSGS,
    BASE_INPUT_CMD_MSGS_FAST,
    format_assistant_response,
    format_user_request,
)


def get_model_chat_response(
    *,
    user_input: str,
    console: Console,
    input_messages: list,
    temperature: float,
    model: str,
    client: Anthropic,
) -> list:
    """
    Get the chat response from the model.

    Args:
        user_input (str): The user's input message.
        console (Console): The console object for printing messages.
        input_messages (list): The list of input messages exchanged between the user and the model.
        temperature (float): The temperature parameter for controlling the randomness of the model's output.
        model (str): The name of the model to use for generating the response.
        client (Anthropic): The client object for making API requests to the model.

    Returns:
        list: The updated list of input messages, including the generated response.
    """
    MAX_TOKENS = 3800
    RESERVED_OUTPUT_TOKENS = 1024
    MAX_INPUT_TOKENS = MAX_TOKENS - RESERVED_OUTPUT_TOKENS
    # Note:  use OpenAI gpt-4-turbo token counts as rough estimate
    input_messages.append({"role": "user", "content": user_input})
    input_messages, n_input_tokens = utils.check_reduce_context(
        input_messages, MAX_INPUT_TOKENS, "gpt-4-turbo", ctx_removal_index=1
    )
    n_output_tokens = max(RESERVED_OUTPUT_TOKENS, MAX_TOKENS - n_input_tokens)
    model_name = config.ANTHROPIC_MODEL_MAP[model]
    try:
        """Get the response from the model."""
        stream = client.messages.create(
            model=model_name,
            messages=input_messages,
            max_tokens=n_output_tokens,
            temperature=temperature,
            system=CHAT_SYS_MSG,
            stream=True,
        )
        collected_messages = []
        panel_width = min(console.width, config.DEFAULT_COLUMN_WIDTH)
        output_panel = Panel(
            "",
            title="[bold blue]DeveloperGPT[/bold blue]",
            title_align="left",
            width=panel_width,
        )
        with Live(output_panel, refresh_per_second=4):
            for event in stream:
                if event.type == "content_block_delta":
                    collected_messages.append(event.delta.text)
                    output_panel.renderable = Markdown(
                        "".join(collected_messages), inline_code_theme="monokai"
                    )

        full_response = "".join(collected_messages)
        input_messages.append(format_assistant_response(full_response))
        return input_messages
    except anthropic_exceptions.AnthropicError as e:
        console.log(f"[bold red] Anthropic API Error: {e}[/bold red]")
        sys.exit(-1)


BASE_ANTHROPIC_MSGS = [
    {"role": "user", "content": INITIAL_USER_CMD_MSG},
    {"role": "assistant", "content": "Understood!"},
] + BASE_INPUT_CMD_MSGS[2:]

BASE_ANTHROPIC_MSGS_FAST = [
    {"role": "user", "content": INITIAL_USER_CMD_MSG_FAST},
    {"role": "assistant", "content": "Understood!"},
] + BASE_INPUT_CMD_MSGS_FAST[2:]


def model_command(
    *,
    user_input: str,
    console: Console,
    fast_mode: bool,
    model: str,
    client: Anthropic,
) -> Optional[str]:
    """
    Get command suggestion from model.

    Args:
        user_input (str): The user's natural language terminal command request.
        console (Console): The console object for displaying status messages.
        fast_mode (bool): Flag indicating whether to use fast mode.
        model (str): The model to use for generating the response.
        client (Anthropic): The client object for making API requests.

    Returns:
        Optional[str]: The model's response as a string, or None if there is no response.
    """
    n_output_tokens = 3800

    # skip the first system message in the base input messages
    if fast_mode:
        input_messages = list(BASE_ANTHROPIC_MSGS_FAST)
    else:
        input_messages = list(BASE_ANTHROPIC_MSGS)

    input_messages.append(format_user_request(user_input))

    # DO NOT prefill Claude response - for some reason this results in
    # more outputs with unparseable JSON
    # https://docs.anthropic.com/claude/docs/prefill-claudes-response
    # input_messages.append({"role": "assistant", "content": "{"})

    model_name = config.ANTHROPIC_MODEL_MAP[model]
    try:
        with console.status("[bold blue]Decoding request") as _:
            response = client.messages.create(
                model=model_name,
                messages=input_messages,  # type: ignore
                max_tokens=n_output_tokens,
                temperature=config.CMD_TEMP,
                system=CMD_SYS_MSG,
            )
    except anthropic_exceptions.AnthropicError as e:
        console.log(f"[bold red] Anthropic API Error: {e}[/bold red]")
        sys.exit(-1)

    raw_output = response.content[0].text
    return utils.clean_model_output(raw_output) if raw_output else None
