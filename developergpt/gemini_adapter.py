"""
DeveloperGPT by luo-anthony
"""

from typing import Optional

import google.generativeai as genai
from google.generativeai import ChatSession, GenerativeModel
from rich.console import Console
from rich.live import Live
from rich.markdown import Markdown
from rich.panel import Panel

from developergpt import config, few_shot_prompts, utils
from developergpt.few_shot_prompts import (
    INITIAL_USER_CMD_MSG,
    INITIAL_USER_CMD_MSG_FAST,
)

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


def format_user_request(
    user_request: str, platform: str = config.USER_PLATFORM
) -> dict:
    return {
        "role": "user",
        "parts": [
            f"""Provide the appropriate command-line commands that can be executed on a {platform} machine for the user request: "{user_request}"."""
        ],
    }


def format_assistant_response(assistant_response: str) -> dict:
    return {"role": "model", "parts": [assistant_response]}


BASE_INPUT_CMD_MSGS = [
    {"role": "user", "parts": [INITIAL_USER_CMD_MSG]},
    {"role": "model", "parts": ["Understood!"]},
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
    {"role": "user", "parts": [INITIAL_USER_CMD_MSG_FAST]},
    {"role": "model", "parts": ["Understood!"]},
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
    temperature: float,
) -> None:
    """Get the response from the model."""
    response = chat_session.send_message(
        user_input,
        stream=True,
        generation_config=genai.types.GenerationConfig(temperature=temperature),
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
        response = gemini_model.generate_content(
            contents=input_messages,
            generation_config=genai.types.GenerationConfig(temperature=config.CMD_TEMP),
        )
    return utils.clean_model_output(response.text)
