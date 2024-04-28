"""
DeveloperGPT by luo-anthony
"""

import json
import re
import sys
from typing import Optional

import requests
from huggingface_hub import InferenceClient
from huggingface_hub import errors as hf_errors
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
from developergpt.openai_adapter import (
    BASE_INPUT_CMD_MSGS,
    BASE_INPUT_CMD_MSGS_FAST,
    format_user_request,
)

TIMEOUT: int = 30  # seconds
MAX_RESPONSE_TOKENS = 784
MAX_HISTORY = 8  # number of user/assistant output pairs to keep in chat history

### Helper Functions and Prompts for Foundation Models and Non-Chat Completion Models ###

HF_CMD_PROMPT_COMPLETION_MODEL = """The following is a software development command line system that allows a user to get the command(s) to execute their request in natural language. 
    The system gives the user a series of commands to be executed for the given platform in Markdown format (escaping any special Markdown characters with \) along with explanations.\n"""


def format_user_cmd_request(
    user_input: str, platform: str = config.USER_PLATFORM
) -> str:
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
    format_assistant_output(few_shot_prompts.CONDA_OUTPUT_EXAMPLE_FAST),
    format_user_cmd_request(
        few_shot_prompts.SEARCH_REQUEST, platform=few_shot_prompts.EXAMPLE_PLATFORM
    ),
    format_assistant_output(few_shot_prompts.SEARCH_OUTPUT_EXAMPLE_FAST),
    format_user_cmd_request(
        few_shot_prompts.PROCESS_REQUEST, platform=few_shot_prompts.EXAMPLE_PLATFORM
    ),
    format_assistant_output(few_shot_prompts.PROCESS_OUTPUT_EXAMPLE_FAST),
]

# NOTE: this prompt coerces foundation models to work like chat models with code formatting examples and example response types (e.g. BLOOM, Gemma-7b)
# This is not needed for instruction-tuned models.

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
    """Assistant: LDFLAGS is a variable used in Makefiles that contains linker flags or options to pass to the linker program. 
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


### Hugging Face Adapter Functions ###


def model_command(
    *,
    user_input: str,
    console: Console,
    api_token: Optional[str],
    fast_mode: bool,
    model: str,
) -> str:
    """
    Get command suggestion from model.

    Args:
        user_input (str): The user natural language command request
        console (Console): The console object for printing output.
        api_token (Optional[str]): The API token for accessing the Hugging Face Inference API.
        fast_mode (bool): Flag indicating whether to use fast mode for the command execution.
        model (str): The name of the LLM to use.

    Returns:
        str: The output of the command execution.
    """
    model_name = config.HF_MODEL_MAP[model]
    instruct_model = model in config.HF_INSTRUCT_MODELS

    try:
        if instruct_model:
            cmd_output = _instruct_model_command(
                user_input=user_input,
                console=console,
                api_token=api_token,
                fast_mode=fast_mode,
                model=model,
            )
        else:
            cmd_output = _foundation_model_command(
                user_input=user_input,
                console=console,
                api_token=api_token,
                fast_mode=fast_mode,
                model_name=model_name,
            )
        return utils.clean_model_output(cmd_output)
    except (hf_errors.InferenceTimeoutError, errors.RateLimitExceededError) as e:
        console.print(
            "[bold red]Hugging Face Inference API request timed out or is unavailable. Try again later.[/bold red]"
        )
    except errors.BadRequestError as e:
        console.print(
            f"[bold red]Hugging Face Inference API returned a bad request. {e}[/bold red]"
        )
    except requests.exceptions.ReadTimeout:
        console.print(
            "[bold red]Hugging Face Inference API request timed out. Try again later.[/bold red]"
        )
    except Exception as e:
        console.print(f"[bold red]Error: {e}[/bold red]")
    sys.exit(-1)


def _instruct_model_command(
    *,
    user_input: str,
    console: Console,
    api_token: Optional[str],
    fast_mode: bool,
    model: str,
) -> str:
    """
    Instruction-Tuned Model Command using huggingface inference API

    Args:
        user_input (str): The user input to be processed by the model.
        console (Console): The console object for displaying status messages.
        api_token (Optional[str]): The API token for authentication (optional).
        fast_mode (bool): Flag indicating whether to use fast mode or not.
        model (str): The name of the model to be used.

    Returns:
        str: The generated response from the model.
    """
    model_name = config.HF_MODEL_MAP[model]
    chat_completion_model = model in config.HF_CHAT_COMPLETION_MODELS
    client = InferenceClient(model_name, token=api_token, timeout=TIMEOUT)

    with console.status("[bold blue]Decoding request") as _:
        if chat_completion_model:
            if fast_mode:
                input_messages = list(BASE_INPUT_CMD_MSGS_FAST[1:])
            else:
                input_messages = list(BASE_INPUT_CMD_MSGS[1:])
            input_messages.append(format_user_request(user_input))
            response = client.chat_completion(
                input_messages,
                max_tokens=MAX_RESPONSE_TOKENS,
                temperature=config.CMD_TEMP,
            )
            raw_output = response.choices[0].message.content
        else:
            if fast_mode:
                model_input = (
                    INITIAL_USER_CMD_MSG_FAST
                    + "\n"
                    + "\n".join(
                        HF_EXAMPLE_CMDS_FAST + [format_user_cmd_request(user_input)]
                    )
                    + "\nAssistant:"
                )
            else:
                model_input = (
                    INITIAL_USER_CMD_MSG
                    + "\n"
                    + "\n".join(HF_EXAMPLE_CMDS + [format_user_cmd_request(user_input)])
                    + "\nAssistant:"
                )
            raw_output = client.text_generation(
                model_input,
                max_new_tokens=MAX_RESPONSE_TOKENS,
                temperature=config.CMD_TEMP,
                stop_sequences=["User:"],
            )
        raw_output = utils.clean_model_output(raw_output)
        try:
            _ = json.loads(raw_output)
            # valid JSON -> return the cleaned output
            return raw_output
        except json.decoder.JSONDecodeError as e:
            # invalid JSON -> ask model to extract and fix the JSON
            extract_json_request = f"""
The following JSON cannot be parsed ({e}).
Please fix any errors in the JSON and return it (only return the fixed JSON itself).
The output should only be a single valid JSON block:\n
{raw_output}
            """
            second_attempt = client.text_generation(
                extract_json_request,
                max_new_tokens=MAX_RESPONSE_TOKENS,
                temperature=config.CMD_TEMP,
                stop_sequences=["User:"],
            )
            return second_attempt


def _foundation_model_command(
    *,
    user_input: str,
    console: Console,
    api_token: Optional[str],
    fast_mode: bool,
    model_name: str,
) -> str:
    """
    Foundation Model Command using different prompts and text_generation api

    Args:
        user_input (str): The user input for the command.
        console (Console): The console object for displaying status messages.
        api_token (Optional[str]): The API token for authentication (optional).
        fast_mode (bool): Flag indicating whether to use fast mode or not.
        model_name (str): The name of the model to use for generating responses.

    Returns:
        str: The generated text response from the model.
    """
    client = InferenceAPIClient(model_name, token=api_token, timeout=TIMEOUT)

    if fast_mode:
        messages = list(HF_EXAMPLE_CMDS_FAST)
    else:
        messages = list(HF_EXAMPLE_CMDS)
    messages.append(format_user_cmd_request(user_input))

    model_input = (
        HF_CMD_PROMPT_COMPLETION_MODEL + "\n" + "\n".join(messages) + "\nAssistant:"
    )

    with console.status("[bold blue]Decoding request") as _:
        return client.generate(
            model_input,
            max_new_tokens=MAX_RESPONSE_TOKENS,
            stop_sequences=["User:"],
            temperature=config.CMD_TEMP,
        ).generated_text


def get_model_chat_response(
    *,
    user_input: str,
    console: Console,
    input_messages: list,
    api_token: Optional[str],
    temperature: float,
    model: str,
) -> list:
    """
    Get the chat response from the model.

    Args:
        user_input (str): The user's input message.
        console (Console): The console object for printing messages.
        input_messages (list): The list of input messages exchanged in the chat.
        api_token (Optional[str]): The API token for accessing the Hugging Face Inference API.
        temperature (float): The temperature value for controlling the randomness of the model's output.
        model (str): The name of the model to use.

    Returns:
        list: The list of chat messages exchanged between the user and the model.
    """
    model_name = config.HF_MODEL_MAP[model]
    instruct_model = model in config.HF_INSTRUCT_MODELS

    output_panel = Panel(
        "",
        title="[bold blue]DeveloperGPT[/bold blue]",
        title_align="left",
        width=min(console.width, config.DEFAULT_COLUMN_WIDTH),
    )

    input_messages.append(format_user_input(user_input))
    try:
        if instruct_model:
            messages = _instruct_mode_chat(
                output_panel=output_panel,
                input_messages=input_messages,
                api_token=api_token,
                temperature=temperature,
                model_name=model_name,
            )
        else:
            messages = _foundation_model_chat(
                output_panel=output_panel,
                input_messages=input_messages,
                api_token=api_token,
                temperature=temperature,
                model_name=model_name,
            )
        if len(messages) > MAX_HISTORY:
            # remove oldest 1 user/assistant output pair
            messages = messages[2:]
        return messages

    except (hf_errors.InferenceTimeoutError, errors.RateLimitExceededError) as e:
        console.print(
            "[bold red]Hugging Face Inference API request timed out or is unavailable. Try again later.[/bold red]"
        )
    except errors.BadRequestError as e:
        console.print(
            f"[bold red]Hugging Face Inference API returned a bad request. {e}[/bold red]"
        )
    except requests.exceptions.ReadTimeout:
        console.print(
            "[bold red]Hugging Face Inference API request timed out. Try again later.[/bold red]"
        )
    except Exception as e:
        console.print(f"[bold red]Error: {e}[/bold red]")
    sys.exit(-1)


def _instruct_mode_chat(
    *,
    output_panel: Panel,
    input_messages: list,
    api_token: Optional[str],
    temperature: float,
    model_name: str,
) -> list:
    """
    Perform chat conversation with instruction-tuned model.

    Args:
        output_panel (Panel): The output panel to display the chat messages.
        input_messages (list): The list of input messages from the user.
        api_token (Optional[str]): The API token for authentication (optional).
        temperature (float): The temperature parameter for text generation.
        model_name (str): The name of the model to use for text generation.

    Returns:
        list: The updated list of input messages, including the assistant's response.
    """
    client = InferenceClient(model_name, token=api_token, timeout=TIMEOUT)
    model_input = "\n".join(input_messages) + "\nAssistant: "

    output_text = ""
    with Live(output_panel, refresh_per_second=4):
        for response in client.text_generation(
            model_input,
            max_new_tokens=MAX_RESPONSE_TOKENS,
            temperature=temperature,
            stop_sequences=["\nUser:"],
            stream=True,
            details=True,
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

    input_messages.append(format_assistant_output(output_text))
    return input_messages


def _foundation_model_chat(
    *,
    output_panel: Panel,
    input_messages: list,
    api_token: Optional[str],
    temperature: float,
    model_name: str,
) -> list:
    """
    Perform a chat conversation with the foundation model.

    Args:
        output_panel (Panel): The output panel to display the chat conversation.
        input_messages (list): The list of input messages in the conversation.
        api_token (Optional[str]): The API token for authentication (optional).
        temperature (float): The temperature value for controlling the randomness of the model's output.
        model_name (str): The name of the foundation model to use.

    Returns:
        list: The updated list of input messages, including the assistant's response.
    """
    client = InferenceAPIClient(model_name, token=api_token, timeout=TIMEOUT)
    model_input = HF_CHAT_PROMPT + "\n" + "\n".join(input_messages) + "\nAssistant: "

    output_text = ""
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

    input_messages.append(format_assistant_output(output_text))
    return input_messages
