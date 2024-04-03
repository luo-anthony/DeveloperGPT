"""
DeveloperGPT by luo-anthony
"""

import sys
from datetime import datetime
from typing import Optional

import openai
from llama_cpp import Llama
from openai import OpenAI
from rich.console import Console
from rich.live import Live
from rich.markdown import Markdown
from rich.panel import Panel

from developergpt import config, few_shot_prompts, utils
from developergpt.few_shot_prompts import (
    INITIAL_USER_CMD_MSG,
    INITIAL_USER_CMD_MSG_FAST,
)

INITIAL_CHAT_SYSTEM_MSG = {
    "role": "system",
    "content": f"""
                You are DeveloperGPT, a helpful personal assistant for a programmer working on a {config.USER_PLATFORM} machine. 
                Your task is to assist the programmer with any programming-related tasks they may have. 
                This could include providing advice on how to approach a programming problem, suggesting tools or libraries to use for a particular task, 
                helping to troubleshoot errors or bugs in code, answering general programming questions, and providing code snippets or examples.

                Please keep your answers short and concise and use a suitable format for printing on the terminal. 
                If you provide code snippets, use ```<language> to specify the language. 
            """,
}

INITIAL_CMD_SYSTEM_MSG = {
    "role": "system",
    "content": f"""
            As an assistant for a programmer on a {config.USER_PLATFORM} machine, your task is to provide the appropriate command-line commands to execute a user request.
            """,
}


def format_user_request(
    user_request: str, platform: str = config.USER_PLATFORM
) -> dict:
    return {
        "role": "user",
        "content": f"""Provide the appropriate command-line commands that can be executed on a {platform} machine for the user request: "{user_request}".""",
    }


def format_assistant_response(assistant_response: str) -> dict:
    return {"role": "assistant", "content": assistant_response}


BASE_INPUT_CMD_MSGS = [
    INITIAL_CMD_SYSTEM_MSG,
    {"role": "user", "content": INITIAL_USER_CMD_MSG},
    format_user_request(
        few_shot_prompts.CONDA_REQUEST, platform=few_shot_prompts.EXAMPLE_PLATFORM
    ),
    format_assistant_response(few_shot_prompts.CONDA_OUTPUT_EXAMPLE),
    format_user_request(
        few_shot_prompts.SEARCH_REQUEST, platform=few_shot_prompts.EXAMPLE_PLATFORM
    ),
    format_assistant_response(
        few_shot_prompts.SEARCH_OUTPUT_EXAMPLE,
    ),
    format_user_request(
        few_shot_prompts.UNKNOWN_REQUEST, platform=few_shot_prompts.EXAMPLE_PLATFORM
    ),
    format_assistant_response(
        few_shot_prompts.UNKNOWN_QUERY_OUTPUT_EXAMPLE_ONE,
    ),
]

BASE_INPUT_CMD_MSGS_FAST = [
    INITIAL_CMD_SYSTEM_MSG,
    {"role": "user", "content": INITIAL_USER_CMD_MSG_FAST},
    format_user_request(
        few_shot_prompts.CONDA_REQUEST, platform=few_shot_prompts.EXAMPLE_PLATFORM
    ),
    format_assistant_response(
        few_shot_prompts.CONDA_OUTPUT_EXAMPLE_FAST,
    ),
    format_user_request(
        few_shot_prompts.SEARCH_REQUEST, platform=few_shot_prompts.EXAMPLE_PLATFORM
    ),
    format_assistant_response(
        few_shot_prompts.SEARCH_OUTPUT_EXAMPLE_FAST,
    ),
    format_user_request(
        few_shot_prompts.PROCESS_REQUEST, platform=few_shot_prompts.EXAMPLE_PLATFORM
    ),
    format_assistant_response(
        few_shot_prompts.PROCESS_OUTPUT_EXAMPLE_FAST,
    ),
    format_user_request(
        few_shot_prompts.UNKNOWN_REQUEST, platform=few_shot_prompts.EXAMPLE_PLATFORM
    ),
    format_assistant_response(
        few_shot_prompts.UNKNOWN_QUERY_OUTPUT_EXAMPLE_ONE_FAST,
    ),
]


def get_model_chat_response(
    *,
    user_input: str,
    console: Console,
    input_messages: list,
    temperature: float,
    model: str,
    client: OpenAI | Llama,
) -> list:
    MAX_TOKENS = 4000
    RESERVED_OUTPUT_TOKENS = 1024
    MAX_INPUT_TOKENS = MAX_TOKENS - RESERVED_OUTPUT_TOKENS
    # Note: llama.cpp models use OpenAI token counts as rough estimate
    if model in config.OFFLINE_MODELS:
        model_name = "gpt-3.5-turbo"
    else:
        model_name = config.OPENAI_MODEL_MAP[model]

    input_messages.append({"role": "user", "content": user_input})
    input_messages, n_input_tokens = utils.check_reduce_context(
        input_messages, MAX_INPUT_TOKENS, model_name, ctx_removal_index=1
    )
    n_output_tokens = max(RESERVED_OUTPUT_TOKENS, MAX_TOKENS - n_input_tokens)
    try:
        """Get the response from the model."""
        if model in config.OPENAI_MODEL_MAP:
            assert isinstance(client, OpenAI)
            response = client.chat.completions.create(
                model=model_name,
                messages=input_messages,
                max_tokens=n_output_tokens,
                temperature=temperature,
                stream=True,
            )
        else:
            assert isinstance(client, Llama)
            response = client.create_chat_completion_openai_v1(  # type: ignore
                messages=input_messages,
                max_tokens=n_output_tokens,
                temperature=temperature,
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
            for chunk in response:
                msg = chunk.choices[0].delta.content
                if msg:
                    collected_messages.append(msg)
                    output_panel.renderable = Markdown(
                        "".join(collected_messages), inline_code_theme="monokai"
                    )
    except openai.RateLimitError:
        console.print("[bold red] Rate limit exceeded. Try again later.[/bold red]")
        sys.exit(-1)
    except openai.BadRequestError as e:
        console.log(f"[bold red] Bad Request: {e}[/bold red]")
        sys.exit(-1)

    full_response = "".join(collected_messages)
    input_messages.append(format_assistant_response(full_response))
    return input_messages


def model_command(
    *,
    user_input: str,
    console: Console,
    fast_mode: bool,
    model: str,
    client: OpenAI | Llama,
) -> Optional[str]:
    n_output_tokens = 4000

    if fast_mode:
        input_messages = list(BASE_INPUT_CMD_MSGS_FAST)
    else:
        input_messages = list(BASE_INPUT_CMD_MSGS)

    input_messages.append(format_user_request(user_input))
    try:
        response_format = (
            None if fast_mode or model == config.GPT4 else {"type": "json_object"}
        )
        with console.status("[bold blue]Decoding request") as _:
            if model in config.OPENAI_MODEL_MAP:
                assert isinstance(client, OpenAI)
                model_name = config.OPENAI_MODEL_MAP[model]
                response = client.chat.completions.create(  # type: ignore
                    model=model_name,
                    messages=input_messages,
                    max_tokens=n_output_tokens,
                    temperature=config.CMD_TEMP,
                    response_format=response_format,
                )
            else:
                assert isinstance(client, Llama)
                response = client.create_chat_completion_openai_v1(
                    messages=input_messages,
                    max_tokens=n_output_tokens,
                    temperature=config.CMD_TEMP,
                    response_format=response_format,
                )
    except openai.RateLimitError:
        console.print("[bold red] Rate limit exceeded. Try again later.[/bold red]")
        sys.exit(-1)
    except openai.BadRequestError as e:
        console.log(f"[bold red] Bad Request: {e}[/bold red]")
        sys.exit(-1)
    except openai.APIError as e:
        console.log(f"[bold red] OpenAI API Error: {e}[/bold red]")
        sys.exit(-1)

    raw_output = response.choices[0].message.content
    return utils.clean_model_output(raw_output)


def check_open_ai_key(console: "Console", client: "OpenAI") -> None:
    """Check if the OpenAI API key is valid."""
    try:
        _ = client.models.list()
    except openai.AuthenticationError:
        console.print(
            f"[bold red]Error: Invalid OpenAI API key. Check your {config.OPEN_AI_API_KEY} environment variable.[/bold red]"
        )
        sys.exit(-1)
    except openai.PermissionDeniedError:
        console.print(
            "[bold red]Error: OpenAI API Permission Denied. Your location may not be supported by OpenAI.[/bold red]"
        )
        sys.exit(-1)
    except openai.APIError as e:
        console.print(f"[bold red]Error: OpenAI API error: {e}.[/bold red]")
        sys.exit(-1)
