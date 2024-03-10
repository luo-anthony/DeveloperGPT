"""
DeveloperGPT by luo-anthony
"""

import json
import re
import sys
from typing import Optional

import requests
from rich.console import Console
from rich.live import Live
from rich.markdown import Markdown
from rich.panel import Panel

# using: https://pypi.org/project/text-generation/
from text_generation import InferenceAPIClient, errors

from developergpt import config, few_shot_prompts, utils
from developergpt.few_shot_prompts import (
    INITIAL_USER_CMD_MSG,
    INITIAL_USER_CMD_MSG_FAST,
)

# NOTE: this is used to coerce completion models into providing a chat-like response to command requests
HF_CMD_PROMPT_COMPLETION_MODEL = """The following is a software development command line system that allows a user to get the command(s) to execute their request in natural language. 
    The system gives the user a series of commands to be executed for the given platform in Markdown format (escaping any special Markdown characters with \) along with explanations.\n"""

TIMEOUT: int = 45  # seconds


def format_user_cmd_request(
    user_input: str, platform: str = config.USER_PLATFORM
) -> str:
    user_input.replace('"', "'")
    return f"""User: Provide appropriate command-line commands that can be executed on a {platform} machine to: {user_input}."""


def format_user_input(user_input: str) -> str:
    return f"""User: {user_input}"""


def format_assistant_output(output: str) -> str:
    return f"""Assistant: {output}"""


HF_EXAMPLE_CMDS = [
    format_user_cmd_request(
        few_shot_prompts.CONDA_REQUEST, platform=few_shot_prompts.EXAMPLE_PLATFORM
    ),
    format_assistant_output(few_shot_prompts.CONDA_OUTPUT_EXAMPLE),
    format_user_cmd_request(
        few_shot_prompts.SEARCH_REQUEST, platform=few_shot_prompts.EXAMPLE_PLATFORM
    ),
    format_assistant_output(few_shot_prompts.SEARCH_OUTPUT_EXAMPLE),
]

HF_EXAMPLE_CMDS_FAST = [
    format_user_cmd_request(
        few_shot_prompts.CONDA_REQUEST, platform=few_shot_prompts.EXAMPLE_PLATFORM
    ),
    format_assistant_output(few_shot_prompts.CONDA_OUTPUT_EXAMPLE_MARKDOWN),
    format_user_cmd_request(
        few_shot_prompts.SEARCH_REQUEST, platform=few_shot_prompts.EXAMPLE_PLATFORM
    ),
    format_assistant_output(few_shot_prompts.SEARCH_OUTPUT_EXAMPLE_MARKDOWN),
    format_user_cmd_request(
        few_shot_prompts.PROCESS_REQUEST, platform=few_shot_prompts.EXAMPLE_PLATFORM
    ),
    format_assistant_output(few_shot_prompts.PROCESS_OUTPUT_EXAMPLE_MARKDOWN),
]


def model_command(
    *,
    user_input: str,
    console: Console,
    api_token: Optional[str],
    fast_mode: bool,
    model: str,
) -> str:
    model_name = config.HF_MODEL_MAP[model]
    instruct_model = model in config.HF_INSTRUCT_MODELS
    client = InferenceAPIClient(model_name, token=api_token, timeout=TIMEOUT)
    MAX_RESPONSE_TOKENS = 784
    if fast_mode:
        messages = list(HF_EXAMPLE_CMDS_FAST)
    else:
        messages = list(HF_EXAMPLE_CMDS)
    messages.append(format_user_cmd_request(user_input))

    if instruct_model:
        if fast_mode:
            model_input = model_input = (
                INITIAL_USER_CMD_MSG_FAST + "\n" + "\n".join(messages) + "\nAssistant:"
            )
        else:
            model_input = model_input = (
                INITIAL_USER_CMD_MSG + "\n" + "\n".join(messages) + "\nAssistant:"
            )
    else:
        model_input = model_input = (
            HF_CMD_PROMPT_COMPLETION_MODEL + "\n" + "\n".join(messages) + "\nAssistant:"
        )

    with console.status("[bold blue]Decoding request") as _:
        try:
            output_text = client.generate(
                model_input,
                max_new_tokens=MAX_RESPONSE_TOKENS,
                stop_sequences=["User:"],
                temperature=config.CMD_TEMP,
            ).generated_text
            output_text = output_text.strip()
            json_str_attempt = utils.clean_model_output(output_text)

            # smaller instruction tuned models tend to exhibit more erratic behavior - we need a two-step JSON parse
            if not instruct_model:
                return json_str_attempt
            else:
                try:
                    _ = json.loads(json_str_attempt)
                    # valid JSON -> return the cleaned output
                    return json_str_attempt
                except json.decoder.JSONDecodeError:
                    # invalid JSON -> ask model to extract the JSON
                    extract_json_request = f"""Extract and return only the first JSON block from the following text. 
                    The output should be only valid JSON:\n
                    {json_str_attempt}
                    """
                    second_attempt = client.generate(
                        extract_json_request,
                        max_new_tokens=MAX_RESPONSE_TOKENS,
                        temperature=config.CMD_TEMP,
                    ).generated_text
                    return utils.clean_model_output(second_attempt)

        except errors.RateLimitExceededError as e:
            console.print(
                f"[bold red]Hugging Face Inference API rate limit exceeded. Please try again later or set a Hugging Face token. {e}[/bold red]"
            )
            sys.exit(-1)
        except errors.BadRequestError as e:
            console.print(
                f"[bold red]Hugging Face Inference API returned a bad request. {e}[/bold red]"
            )
            sys.exit(-1)
        except requests.exceptions.ReadTimeout:
            console.print(
                "[bold red]Hugging Face Inference API request timed out. Try again later.[/bold red]"
            )
            sys.exit(-1)


"""
NOTE: this prompt coerces completion models to work like chat models with code formatting examples and example response types (e.g. BLOOM, Gemma-7b)
This is not needed for instruction-tuned models. 
"""
HF_CHAT_PROMPT = """The following is a conversation with a software development expert chatbot. 
    The chatbot should be able to understand and respond to questions and statements about a variety of topics related to Computer Science and Software Development. 
    The chatbot is conversational, flexible, and should be able to engage in casual, friendly conversation to assist the user.
    The chatbot should also be able to maintain context across multiple turns of conversation.\n"""

RAW_CHAT_MSGS = [
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

BASE_INPUT_CHAT_MSGS = [re.sub(" +", " ", msg) for msg in RAW_CHAT_MSGS]


def get_model_chat_response(
    *,
    user_input: str,
    console: Console,
    input_messages: list,
    api_token: Optional[str],
    temperature: float,
    model: str,
) -> list:
    model_name = config.HF_MODEL_MAP[model]
    instruct_model = model in config.HF_INSTRUCT_MODELS
    client = InferenceAPIClient(model_name, token=api_token, timeout=TIMEOUT)
    MAX_RESPONSE_TOKENS = 1024

    panel_width = min(console.width, config.DEFAULT_COLUMN_WIDTH)
    input_messages.append(format_user_input(user_input))

    if instruct_model:
        model_input = "\n".join(input_messages) + "\nAssistant: "
    else:
        model_input = (
            HF_CHAT_PROMPT + "\n" + "\n".join(input_messages) + "\nAssistant: "
        )

    output_panel = Panel(
        "",
        title="[bold blue]DeveloperGPT[/bold blue]",
        title_align="left",
        width=panel_width,
    )

    output_text = ""
    try:
        with Live(output_panel, refresh_per_second=4):
            for response in client.generate_stream(
                model_input,
                max_new_tokens=MAX_RESPONSE_TOKENS,
                temperature=temperature,
                stop_sequences=["\nUser:"],
            ):
                if not response.token.special:
                    output_text += response.token.text
                    # don't show "User:" in the live output
                    idx = output_text.find("User:")
                    if idx > 0:
                        output_text = output_text[:idx].strip()
                    output_panel.renderable = Markdown(
                        output_text, inline_code_theme="monokai"
                    )
    except errors.RateLimitExceededError as e:
        console.print(
            f"[bold red]Hugging Face Inference API rate limit exceeded. Please try again later or set a Hugging Face token. {e}[/bold red]"
        )
        sys.exit(-1)
    except errors.BadRequestError as e:
        console.print(
            f"[bold red]Hugging Face Inference API returned a bad request. {e}[/bold red]"
        )
        sys.exit(-1)

    input_messages.append(format_assistant_output(output_text))

    if len(input_messages) > 8:
        # remove oldest 1 user/assistant output pair
        input_messages = input_messages[2:]

    return input_messages
