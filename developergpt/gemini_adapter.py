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
from vertexai.preview.generative_models import (
    ChatSession,
    Content,
    GenerativeModel,
    Part,
)

from developergpt import config, few_shot_prompts, utils

# Seems to cause very odd LLM output behavior when used with the chat system
# INITIAL_CHAT_SYSTEM_MSG = [
#     Content(
#         role="user",
#         parts=[
#             Part.from_text(
#                 f"""
#                 You are DeveloperGPT, a helpful personal assistant for a programmer working on a {config.USER_PLATFORM} machine.
#                 Your task is to assist the programmer with any programming-related tasks they may have.
#                 This could include providing advice on how to approach a programming problem, suggesting tools or libraries to use for a particular task,
#                 helping to troubleshoot errors or bugs in code, answering general programming questions, and providing code snippets or examples.
#                 Please keep your answers short and concise and use a suitable format for printing on the terminal.
#             """
#             )
#         ],
#     ),
#     Content(
#         role="model",
#         parts=[
#             Part.from_text(
#                 f"""
#                 I'm ready to be your trusty DeveloperGPT, your personal AI assistant for conquering the {config.USER_PLATFORM} programming world.
#             """
#             )
#         ],
#     ),
# ]

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


def format_initial_cmd_msg(cmd_format: str, invalid_format: str) -> str:
    return f"""
                Provide the appropriate command-line commands that can be executed on a {config.USER_PLATFORM} machine for a user request.
                Today's date/time is {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}.
                If the request is possible, please provide commands that can be executed in the command line and do not require a GUI.
                Do not include commands that require a yes/no response.
                For each command, explain the command and any arguments used.
                Try to find the simplest command(s) that can be used to execute the request.

                If the request is valid, format each command output in the following JSON format: {cmd_format}

                If the request is invalid, please return the following JSON format: {invalid_format}
                """


INITIAL_USER_CMD_MSG = format_initial_cmd_msg(JSON_CMD_FORMAT, JSON_INVALID_FORMAT)

INITIAL_USER_CMD_MSG_FAST = format_initial_cmd_msg(
    JSON_CMD_FORMAT_FAST, JSON_INVALID_FORMAT_FAST
)


def format_user_request(
    user_request: str, platform: str = config.USER_PLATFORM
) -> "Content":
    return Content(
        role="user",
        parts=[
            Part.from_text(
                f"""Provide the appropriate command-line commands that can be executed on a {platform} machine for the user request: "{user_request}"."""
            )
        ],
    )


def format_assistant_response(assistant_response: str) -> "Content":
    return Content(role="model", parts=[Part.from_text(assistant_response)])


BASE_INPUT_CMD_MSGS = [
    Content(role="user", parts=[Part.from_text(INITIAL_USER_CMD_MSG)]),
    Content(role="model", parts=[Part.from_text("Understood!")]),
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
    Content(role="user", parts=[Part.from_text(INITIAL_USER_CMD_MSG_FAST)]),
    Content(role="model", parts=[Part.from_text("Understood!")]),
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
    chat_session: "ChatSession",
) -> None:
    """Get the response from the model."""
    response = chat_session.send_message(user_input, stream=True)
    collected_messages = []
    panel_width = min(console.width, config.DEFAULT_COLUMN_WIDTH)
    output_panel = Panel(
        "",
        title="[bold blue]DeveloperGPT[/bold blue]",
        title_align="left",
        width=panel_width,
    )
    with Live(output_panel, refresh_per_second=4):
        for chunk in response:  # type: ignore
            msg = chunk.text
            if msg:
                collected_messages.append(msg)
                output_panel.renderable = Markdown(
                    "".join(collected_messages), inline_code_theme="monokai"
                )


def model_command(
    *, user_input: str, console: Console, fast_mode: bool, model: str
) -> Optional[str]:
    gemini_model = GenerativeModel(config.GOOGLE_MODEL_MAP[model])

    if fast_mode:
        input_messages = list(BASE_INPUT_CMD_MSGS_FAST)
    else:
        input_messages = list(BASE_INPUT_CMD_MSGS)

    input_messages.append(format_user_request(user_input))

    with console.status("[bold blue]Decoding request") as _:
        response = gemini_model.generate_content(contents=input_messages)

    # clean up the output - Gemini likes to put ``` around the output
    raw_output = response.text
    model_output = raw_output.replace("```", "").strip()
    return model_output
