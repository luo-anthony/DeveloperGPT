"""
DeveloperGPT by luo-anthony
"""

import copy
import platform
import re
import sys

import requests
from rich.console import Console
from rich.live import Live
from rich.markdown import Markdown
from rich.panel import Panel

# using: https://pypi.org/project/text-generation/
from text_generation import InferenceAPIClient, errors

from developergpt import config, utils

# TODO: add more hugging_face models: flan-ul2, Vicuna-13B?


# TODO change the output format so that it doesn't use JSON and we don't need to deal with weird escaping issues with regex output
BLOOM_CMD_PROMPT = """The following is a software development command line system that allows a user to get the command(s) to execute their request in natural language. 
    The system gives the user a series of commands to be executed for the given platform in a set format with explanations.\n"""

conda_output_example = """\n
- `curl -O https://repo.anaconda.com/miniconda/Miniconda3-latest-MacOSX-x86_64.sh`\n
- `bash Miniconda3-latest-MacOSX-x86_64.sh`\n

\n**Explanation**\n
- The `curl` command is used to issue web requests, e.g. download web pages.\n
\t- `-O` specifies that we want to save the response to a file.\n
\t- `https://repo.anaconda.com/miniconda/Miniconda3-latest-MacOSX-x86_64.sh` is the URL of the file we want to download.\n
- The `bash` command is used to execute shell scripts.\n
\t- `Miniconda3-latest-MacOSX-x86_64.sh` is the name of the file we want to execute.\n
"""

search_output_example = """\n
- `find ~/Documents/ -name 'test*.py'`\n

\n**Explanation**\n
- `find` is used to list files.\n
\t- `~/Documents` specifies the folder to search in.\n
\t- `-name 'test.py'` specifies that we want to search for files starting with `test` and ending with `.py`.\n
"""


def format_user_cmd_request(user_input: str) -> str:
    user_input.replace('"', "'")
    return f"""User: Provide appropriate command-line commands that can be executed on a {platform.platform()} machine to: {user_input}."""


BLOOM_EXAMPLE_CMDS = [
    format_user_cmd_request("install conda"),
    f"""Assistant: {conda_output_example}""",
    format_user_cmd_request("the quick brown fox jumps"),
    f"""Assistant: {utils.ERROR_CODE}""",
    format_user_cmd_request(
        "search ~/Documents directory for any .py file that begins with 'test'"
    ),
    f"""Assistant: {search_output_example}""",
]


TIMEOUT = 25  # seconds


def model_command(user_input: str, console: "Console", api_token: str) -> str:
    model = "bigscience/bloom"
    client = InferenceAPIClient(model, token=api_token, timeout=TIMEOUT)
    MAX_RESPONSE_TOKENS = 256

    messages = copy.deepcopy(BLOOM_EXAMPLE_CMDS)
    messages.append(format_user_cmd_request(user_input))

    model_input = model_input = (
        BLOOM_CMD_PROMPT + "\n" + "\n".join(messages) + "\nAssistant:"
    )

    # console.log(model_input)
    with console.status("[bold blue]Decoding request") as _:
        try:
            exit = False
            output_text = ""
            for response in client.generate_stream(
                model_input, max_new_tokens=MAX_RESPONSE_TOKENS
            ):
                if not response.token.special:
                    output_text += response.token.text
                    # stop generation once we hit "User:"
                    idx = output_text.find("User:")
                    if idx > 0:
                        output_text = output_text[:idx].strip()
                        exit = True
                    if exit:
                        break

        except errors.RateLimitExceededError:
            console.print(
                "[bold red]Hugging Face Inference API rate limit exceeded. Please try again later or set a Hugging Face API key. [/bold red]"
            )
            sys.exit(-1)
        except errors.BadRequestError:
            console.print(
                "[bold red]Hugging Face Inference API returned a bad request. Check your Hugging Face API key.[/bold red]"
            )
            sys.exit(-1)
        except requests.exceptions.ReadTimeout:
            console.print(
                "[bold red]Hugging Face Inference API request timed out. Try again later.[/bold red]"
            )
            sys.exit(-1)

    # clean up
    output_text = output_text.strip()
    return output_text


BLOOM_CHAT_PROMPT = """The following is a conversation with a software development expert chatbot. 
    The chatbot should be able to understand and respond to questions and statements about a variety of topics related to Computer Science and Software Development. 
    The chatbot is conversational, flexible, and should be able to engage in casual, friendly conversation to assist the user.
    The chatbot should also be able to maintain context across multiple turns of conversation.\n"""

raw_chat_msgs = [
    "User: What is the difference between x86 and ARM architecture?",
    """Assistant: x86 and ARM are two different processor architectures used in modern computing devices. They have different instruction sets, 
    with x86 using a CISC instruction set and ARM using a RISC instruction set. x86 processors typically have higher clock speeds and can execute more instructions per clock cycle, while ARM processors are more power-efficient.
    x86 processors are compatible with a wide range of operating systems, while ARM processors are commonly used in mobile devices and are generally less expensive than x86 processors.""",
    "User: What are LDFLAGS in a Makefile?",
    """Assistant, LDFLAGS is a variable used in Makefiles that contains linker flags or options to pass to the linker program. 
    Linker flags control the behavior of the linker, which is responsible for linking together object files into an executable or library file. 
    LDFLAGS can be used to specify library paths, libraries to link against, and other linker options such as optimization flags or debug information. 
    By setting LDFLAGS in a Makefile, you can customize the linking process and provide additional options to the linker.""",
    "User: What are some other flags?",
    """Assistant: In addition to LDFLAGS, other commonly used flags in Makefiles include CFLAGS for C compiler options, CPPFLAGS for C preprocessor options, CC for specifying the C compiler, ARFLAGS for archive tool options, and LDLIBS for specifying libraries to link against. 
    These flags can be used to customize the build process and provide additional options to the compiler, linker, and other tools used in the build. Makefiles can be quite complex, and the use of flags and variables helps to manage the build process and ensure that it is repeatable and consistent.""",
    "User: Can you give me an example of a variadic template in C++?",
    """Assistant: A variadic template is a template that can accept a variable number of arguments. Here is an example\n
    ```cpp\n
    template <typename... Args>\n
    void print(Args... args) {\n
    \t(std::cout << ... << args) << std::endl;\n
    }\n
    ```""",
    "User: What is JIT?",
    """Assistant: A JIT (Just-In-Time) compiler is a type of compiler used in some programming languages that compiles code during runtime, rather than before the program is run. 
    JIT compilers can optimize the code based on the actual runtime behavior of the program, resulting in faster execution times. 
    JIT compilers are commonly used in languages such as Java, JavaScript, and .NET.""",
]

BASE_INPUT_CHAT_MSGS = [re.sub(" +", " ", msg) for msg in raw_chat_msgs]


def format_bloom_chat_input(messages: list) -> str:
    model_input = BLOOM_CHAT_PROMPT + "\n" + "\n".join(messages) + "\nAssistant:"
    return model_input


def format_user_input(user_input: str) -> str:
    return f"""User: {user_input}"""


def format_assistant_output(output: str) -> str:
    return f"""Assistant: {output}"""


def get_model_chat_response(
    user_input: str, console: "Console", input_messages: list, api_token: str
) -> list:
    model = "bigscience/bloom"
    client = InferenceAPIClient(model, token=api_token, timeout=TIMEOUT)
    MAX_RESPONSE_TOKENS = 384

    panel_width = min(console.width, config.DEFAULT_COLUMN_WIDTH)

    input_messages.append(format_user_input(user_input))

    model_input = format_bloom_chat_input(input_messages)
    # console.log(model_input)

    output_panel = Panel(
        "",
        title="[bold blue]DeveloperGPT[/bold blue]",
        title_align="left",
        width=panel_width,
    )

    output_text = ""
    try:
        with Live(output_panel, refresh_per_second=4):
            exit = False
            for response in client.generate_stream(
                model_input, max_new_tokens=MAX_RESPONSE_TOKENS
            ):
                if not response.token.special:
                    output_text += response.token.text
                    # stop generation once we hit "User:"
                    idx = output_text.find("User:")
                    if idx > 0:
                        output_text = output_text[:idx].strip()
                        exit = True

                    output_panel.renderable = Markdown(
                        output_text, inline_code_theme="monokai"
                    )

                    if exit:
                        break
                else:
                    console.log(response.token)
    except errors.RateLimitExceededError:
        console.print(
            "[bold red]Hugging Face Inference API rate limit exceeded. Please try again later or set a Hugging Face API key. [/bold red]"
        )
        sys.exit(-1)
    except errors.BadRequestError:
        console.print(
            "[bold red]Hugging Face Inference API returned a bad request. Check your Hugging Face API key.[/bold red]"
        )
        sys.exit(-1)

    input_messages.append(format_assistant_output(output_text))

    if len(input_messages) > 10:
        # remove oldest 1 user/assistant output pair
        input_messages.pop(0)
        input_messages.pop(0)

    return input_messages
