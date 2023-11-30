"""
DeveloperGPT by luo-anthony
"""
import sys
from datetime import datetime
from typing import Optional

import openai
from openai import OpenAI
from rich.console import Console
from rich.live import Live
from rich.markdown import Markdown
from rich.panel import Panel

from developergpt import config, few_shot_prompts, utils

JSON_CMD_FORMAT = """
    {
        "input": "<user input>",
        "error": 0,
        "commands": [
            {
                "seq": <Order of Command>,
                "cmd_to_execute": "<commands and arguments to execute>",
                "cmd_explanations": ["<explanation of command 1>", "<explantion of command 2>", ...],
                "arg_explanations": ["<explanation of argument 1>", "<explanation of argument 2>", ...]
            },
            {
                "seq": <Order of Command>,
                "cmd_to_execute": "<commands and arguments to execute>",
                "cmd_explanations": ["<explanation of command 1>", "<explantion of command 2>", ...],
                "arg_explanations": ["<explanation of argument 1>", "<explanation of argument 2>", ...]
            }
        ]
    }
    """

JSON_CMD_FORMAT_FAST = """
    {
        "commands": ["<commands and arguments to execute>", "<commands and arguments to execute>", ...]
    }
    """

JSON_INVALID_FORMAT = """{"input": "<user input>", "error": 1}"""

JSON_INVALID_FORMAT_FAST = """{"error": 1}"""

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


def format_initial_cmd_msg(cmd_format: str, invalid_format: str) -> dict:
    return {
        "role": "user",
        "content": f"""
                Provide the appropriate command-line commands that can be executed on a {config.USER_PLATFORM} machine for a user request.
                Today's date/time is {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}.
                If the request is possible, please provide commands that can be executed in the command line and do not require a GUI.
                Do not include commands that require a yes/no response.
                For each command, explain the command and any arguments used.
                Try to find the simplest command(s) that can be used to execute the request.

                If the request is valid, format each command output in the following JSON format: {cmd_format}

                If the request is invalid, please return the following JSON format: {invalid_format}
                """,
    }


INITIAL_USER_CMD_MSG = format_initial_cmd_msg(JSON_CMD_FORMAT, JSON_INVALID_FORMAT)

INITIAL_USER_CMD_MSG_FAST = format_initial_cmd_msg(
    JSON_CMD_FORMAT_FAST, JSON_INVALID_FORMAT_FAST
)


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
    INITIAL_USER_CMD_MSG,
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
    INITIAL_USER_CMD_MSG_FAST,
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
    client: "OpenAI",
) -> list:
    MAX_TOKENS = 4000
    RESERVED_OUTPUT_TOKENS = 1024
    MAX_INPUT_TOKENS = MAX_TOKENS - RESERVED_OUTPUT_TOKENS
    model_name = config.OPENAI_MODEL_MAP[model]

    input_messages.append({"role": "user", "content": user_input})
    input_messages, n_input_tokens = utils.check_reduce_context(
        input_messages, MAX_INPUT_TOKENS, model_name, ctx_removal_index=1
    )
    n_output_tokens = max(RESERVED_OUTPUT_TOKENS, MAX_TOKENS - n_input_tokens)

    """Get the response from the model."""
    response = client.chat.completions.create(
        model=model_name,
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
    try:
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
    *, user_input: str, console: Console, fast_mode: bool, model: str, client: "OpenAI"
) -> Optional[str]:
    MAX_TOKENS = 4000
    RESERVED_OUTPUT_TOKENS = 1024
    MAX_INPUT_TOKENS = MAX_TOKENS - RESERVED_OUTPUT_TOKENS
    TEMP = 0.05
    model_name = config.OPENAI_MODEL_MAP[model]

    if fast_mode:
        input_messages = list(BASE_INPUT_CMD_MSGS_FAST)
    else:
        input_messages = list(BASE_INPUT_CMD_MSGS)

    input_messages.append(format_user_request(user_input))

    n_input_tokens = utils.count_msg_tokens(input_messages, model_name)

    if n_input_tokens > MAX_INPUT_TOKENS:
        input_messages, n_input_tokens = utils.remove_old_contexts(
            input_messages,
            MAX_INPUT_TOKENS,
            n_input_tokens,
            model_name,
            ctx_removal_index=2,
        )

    n_output_tokens = max(RESERVED_OUTPUT_TOKENS, MAX_TOKENS - n_input_tokens)
    try:
        with console.status("[bold blue]Decoding request") as _:
            response = client.chat.completions.create(
                model=model_name,
                messages=input_messages,
                max_tokens=n_output_tokens,
                temperature=TEMP,
            )
    except openai.RateLimitError:
        console.print("[bold red] Rate limit exceeded. Try again later.[/bold red]")
        sys.exit(-1)
    except openai.BadRequestError as e:
        console.log(f"[bold red] Bad Request: {e}[/bold red]")
        sys.exit(-1)

    model_output = response.choices[0].message.content
    return model_output


def check_open_ai_key(console: "Console", client: "OpenAI") -> None:
    """Check if the OpenAI API key is valid."""
    try:
        _ = client.models.list()
    except openai.AuthenticationError:
        console.print(
            f"[bold red]Error: Invalid OpenAI API key. Check your {config.OPEN_AI_API_KEY} environment variable.[/bold red]"
        )
        sys.exit(-1)
