"""
DeveloperGPT by luo-anthony
"""
import platform
import sys
from datetime import datetime

import openai
from rich.console import Console
from rich.live import Live
from rich.markdown import Markdown
from rich.panel import Panel

from developergpt import config, utils

cmd_format = """
<command and arguments to execute>\n
<command and arguments to execute>\n
<command and arguments to execute>\n

\n**Explanation**\n
- <explanation of command 1>\n
\t- <explanation of argument 1>\n
\t- <explanation of argument 2>\n
- <explanation of command 2>\n
\t- <explanation of argument 1>\n
- <explanation of command 3>\n
\t- <explanation of argument 1>\n
"""

conda_output_example = """
curl -O https://repo.anaconda.com/miniconda/Miniconda3-latest-MacOSX-x86_64.sh\n
bash Miniconda3-latest-MacOSX-x86_64.sh\n

\n**Explanation**\n
- The `curl` command is used to issue web requests, e.g. download web pages.\n
\t- `-O` specifies that we want to save the response to a file.\n
\t- `https://repo.anaconda.com/miniconda/Miniconda3-latest-MacOSX-x86_64.sh` is the URL of the file we want to download.\n
- The `bash` command is used to execute shell scripts.\n
\t- `Miniconda3-latest-MacOSX-x86_64.sh` is the name of the file we want to execute.\n
"""

search_output_example = """
find ~/Documents/ -name 'test*.py'\n

\n**Explanation**\n
- `find` is used to list files.\n
\t- `~/Documents` specifies the folder to search in.\n
\t- `-name 'test.py'` specifies that we want to search for files starting with `test` and ending with `.py`.\n
"""

process_output_example = """
ps -axm -o %mem,rss,comm | awk '$1 > 0.5 { printf("%.0fMB\\t%s\n", $2/1024, $3); }'\n

\n**Explanation**\n
- The `ps` command is used to list processes.\n
\t- `axm` specifies that we want to list all processes.\n
\t- `-o %mem,rss,comm` specifies that we want to output the memory usage, resident set size, and command name for each process.\n
\t- `awk '$1 > 0.5 { printf("%.0fMB\t%s\n", $2/1024, $3); }'` is used to filter the output to only show processes using more than 50 MB of RAM.\n
"""


INITIAL_CHAT_SYSTEM_MSG = {
    "role": "system",
    "content": f"""
                You are DeveloperGPT, a helpful personal assistant for a programmer working on a {platform.platform()} machine. 
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
            As an assistant for a programmer on a {platform.platform()} machine, your task is to provide the appropriate command-line commands to execute a user request.
            """,
}

INITIAL_USER_CMD_MSG = {
    "role": "user",
    "content": f"""
            Provide the appropriate command-line commands that can be executed on a {platform.platform()} machine for a user request.
            Today's date/time is {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}.
            If the request is possible, please provide commands that can be executed in the command line and do not require a GUI.
            Do not include commands that require a yes/no response.
            For each command, explain the command and any arguments used.
            Try to find the simplest command(s) that can be used to execute the request.
            If the command(s) have any terminal output, try to format the output in a way that is easy to read.

            If the request is valid, format each command output in the following format: {cmd_format}

            If the request is invalid, please return the following format: {utils.ERROR_CODE}
            """,
}


def format_user_request(user_request: str) -> dict:
    return {
        "role": "user",
        "content": f"""Provide the appropriate command-line commands that can be executed on a {platform.platform()} machine for the user request: "{user_request}".""",
    }


def format_assistant_response(assistant_response: str) -> dict:
    return {"role": "assistant", "content": assistant_response}


EXAMPLE_ONE = (
    format_user_request("install conda"),
    format_assistant_response(conda_output_example),
)

EXAMPLE_TWO = (
    format_user_request(
        "search ~/Documents directory for any .py file that begins with 'test'"
    ),
    format_assistant_response(search_output_example),
)

EXAMPLE_THREE = (
    format_user_request("List all processes using more than 50 MB of RAM"),
    format_assistant_response(process_output_example),
)

NEGATIVE_EXAMPLE_ONE = (
    format_user_request("the quick brown fox jumped over"),
    format_assistant_response(utils.ERROR_CODE),
)

BASE_INPUT_CMD_MSGS = [
    INITIAL_CMD_SYSTEM_MSG,
    INITIAL_USER_CMD_MSG,
    *EXAMPLE_ONE,
    *EXAMPLE_TWO,
    *EXAMPLE_THREE,
    *NEGATIVE_EXAMPLE_ONE,
]


def get_model_chat_response(
    user_input: str, console: "Console", input_messages: list, temperature: float
) -> list:
    MODEL = "gpt-3.5-turbo"
    MAX_TOKENS = 4000
    RESERVED_OUTPUT_TOKENS = 1024
    MAX_INPUT_TOKENS = MAX_TOKENS - RESERVED_OUTPUT_TOKENS

    input_messages.append({"role": "user", "content": user_input})
    input_messages, n_input_tokens = utils.check_reduce_context(
        input_messages, MAX_INPUT_TOKENS, MODEL, ctx_removal_index=1
    )
    n_output_tokens = max(RESERVED_OUTPUT_TOKENS, MAX_TOKENS - n_input_tokens)

    """Get the response from the model."""
    response = openai.ChatCompletion.create(
        model=MODEL,
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
            msg = chunk["choices"][0]["delta"].get("content", "")
            collected_messages.append(msg)
            output_panel.renderable = Markdown(
                "".join(collected_messages), inline_code_theme="monokai"
            )

    full_response = "".join(collected_messages)
    input_messages.append({"role": "assistant", "content": full_response})
    return input_messages


def model_command(user_input: str, console: "Console", input_messages: list) -> list:
    MODEL = "gpt-3.5-turbo"
    MAX_TOKENS = 4000
    RESERVED_OUTPUT_TOKENS = 1024
    MAX_INPUT_TOKENS = MAX_TOKENS - RESERVED_OUTPUT_TOKENS
    TEMP = 0.05

    input_messages.append(format_user_request(user_input))

    n_input_tokens = utils.count_msg_tokens(input_messages, MODEL)

    if n_input_tokens > MAX_INPUT_TOKENS:
        input_messages, n_input_tokens = utils.remove_old_contexts(
            input_messages,
            MAX_INPUT_TOKENS,
            n_input_tokens,
            MODEL,
            ctx_removal_index=2,
        )

    n_output_tokens = max(RESERVED_OUTPUT_TOKENS, MAX_TOKENS - n_input_tokens)

    with console.status("[bold blue]Decoding request") as _:
        response = openai.ChatCompletion.create(
            model=MODEL,
            messages=input_messages,
            max_tokens=n_output_tokens,
            temperature=TEMP,
        )

    model_output = response["choices"][0]["message"]["content"].strip()

    return model_output


def check_open_ai_key(console: "Console") -> None:
    """Check if the OpenAI API key is valid."""
    try:
        _ = openai.Model.list()
    except openai.error.AuthenticationError:
        console.print(
            f"[bold red]Error: Invalid OpenAI API key. Check your {config.OPEN_AI_API_KEY} environment variable.[/bold red]"
        )
        sys.exit(-1)
