"""
DeveloperGPT by luo-anthony
"""

import os
import subprocess
import sys
from typing import Optional

import click
import google.generativeai as genai
import inquirer
from anthropic import Anthropic
from google.generativeai import GenerativeModel
from llama_cpp import Llama
from openai import OpenAI
from prompt_toolkit import PromptSession
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.shortcuts import CompleteStyle
from rich.console import Console

from developergpt import (
    anthropic_adapter,
    config,
    gemini_adapter,
    huggingface_adapter,
    openai_adapter,
    utils,
)

console: Console = Console()
session: PromptSession = PromptSession()


@click.group()
@click.option(
    "--temperature",
    default=0.2,
    help="The temperature of the model response for chat (higher means more creative, lower means more predictable)",
)
@click.option(
    "--model",
    default="gemini",
    help=f"The LLM to use. Options: {', '.join(config.SUPPORTED_MODELS)}",
)
@click.option(
    "--offline",
    is_flag=True,
    default=False,
    help=f"Use DeveloperGPT with a quantized LLM running on-device (offline). Options: {', '.join(config.OFFLINE_MODELS)}",
)
@click.pass_context
def main(ctx, temperature: float, model: str, offline: bool):
    model = model.lower().strip().replace(".", "")
    if offline and model not in config.OFFLINE_MODELS:
        model = config.MISTRAL_Q6  # default to mistral 6 bit quantization if offline

    if model not in config.SUPPORTED_MODELS:
        console.print(
            f"""[bold red]LLM {model} is not supported. """
            f"""Supported LLMs: {", ".join(config.SUPPORTED_MODELS)}[/bold red]"""
        )
        sys.exit(-1)
    internet_conn = utils.check_connectivity()
    if model not in config.OFFLINE_MODELS and not internet_conn:
        console.print(
            """[bold red]No internet connection. """
            """Please check your internet connection or use --offline mode.[/bold red]"""
        )
        sys.exit(-1)

    ctx.ensure_object(dict)
    client: Optional[OpenAI | Llama | Anthropic] = None
    if offline or model in config.OFFLINE_MODELS:
        console.print(
            f"""[bold yellow]Using quantized {' '.join(config.LLAMA_CPP_MODEL_MAP[model])} running on-device (offline)."""
        )
        repo, llm_file, chat_format = config.LLAMA_CPP_MODEL_MAP[model]
        common_llama_args = {
            "n_ctx": config.OFFLINE_MODEL_CTX,
            "verbose": False,
            "chat_format": chat_format,
        }
        if internet_conn:
            client = Llama.from_pretrained(
                repo_id=repo,
                filename=llm_file,
                local_dir=config.OFFLINE_MODEL_CACHE_DIR,
                local_dir_use_symlinks=True,
                n_threads=8,
                **common_llama_args,  # type: ignore
            )
        else:
            model_path = os.path.join(config.OFFLINE_MODEL_CACHE_DIR, llm_file)
            if not os.path.exists(model_path):
                console.print(
                    f"""[bold red]No internet connection and model not found locally at {model_path}. """
                    """Please download the model first when on internet using --offline.[/bold red]"""
                )
                sys.exit(-1)
            client = Llama(
                model_path=model_path,
                n_threads=8,
                **common_llama_args,  # type: ignore
            )
    elif model in config.OPENAI_MODEL_MAP:
        client = OpenAI(api_key=config.get_environ_key(config.OPEN_AI_API_KEY, console))
        openai_adapter.check_open_ai_key(console, client)
        console.print(f"[bold yellow]Using OpenAI {config.OPENAI_MODEL_MAP[model]}.")
    elif model in config.HF_MODEL_MAP:
        ctx.obj["api_key"] = config.get_environ_key_optional(
            config.HUGGING_FACE_API_KEY, console
        )
        console.print(
            f"[bold yellow]Using {config.HF_MODEL_MAP[model]} via Hugging Face Inference API."
        )
    elif model in config.GOOGLE_MODEL_MAP:
        api_key = config.get_environ_key(config.GOOGLE_API_KEY, console)
        genai.configure(api_key=api_key)
    elif model in config.ANTHROPIC_MODEL_MAP:
        api_key = config.get_environ_key(config.ANTHROPIC_API_KEY, console)
        client = Anthropic(api_key=api_key)

    ctx.obj["temperature"] = temperature
    ctx.obj["model"] = model
    ctx.obj["offline"] = offline
    ctx.obj["client"] = client


@main.command(help="Chat with DeveloperGPT")
@click.pass_context
@click.argument("user_input", nargs=-1)
def chat(ctx, user_input):
    """
    Chat with LLMs in Terminal
    """
    if user_input:
        user_input = str(" ".join(user_input))
        session.history.append_string(user_input)

    model = ctx.obj["model"]
    input_messages = []

    if model in config.OPENAI_MODEL_MAP or model in config.LLAMA_CPP_MODEL_MAP:
        input_messages = [openai_adapter.INITIAL_CHAT_SYSTEM_MSG]
    elif model in config.HF_MODEL_MAP:
        instruct_model = model in config.HF_INSTRUCT_MODELS
        if instruct_model:
            input_messages = []
        else:
            input_messages = huggingface_adapter.BASE_INPUT_CHAT_MSGS
    elif model in config.GOOGLE_MODEL_MAP:
        gemini_model = GenerativeModel(config.GOOGLE_MODEL_MAP[model])
        chat_session = gemini_model.start_chat()
    elif model in config.ANTHROPIC_MODEL_MAP:
        input_messages = []
    else:
        return

    console.print("[gray]Type 'quit' to exit the chat[/gray]")
    while True:
        if not user_input:
            user_input = utils.prompt_user_input(
                "Chat: ", session, console, auto_suggest=AutoSuggestFromHistory()
            )

        if not user_input:
            continue

        if model in config.OPENAI_MODEL_MAP or model in config.LLAMA_CPP_MODEL_MAP:
            # llama.cpp models are OpenAI API drop-in compatible
            client = ctx.obj["client"]
            input_messages = openai_adapter.get_model_chat_response(
                user_input=user_input,
                console=console,
                input_messages=input_messages,
                temperature=ctx.obj["temperature"],
                model=model,
                client=client,
            )
        elif model in config.HF_MODEL_MAP:
            api_token = ctx.obj.get("api_key", None)
            input_messages = huggingface_adapter.get_model_chat_response(
                user_input=user_input,
                console=console,
                input_messages=input_messages,
                api_token=api_token,
                temperature=ctx.obj["temperature"],
                model=model,
            )
        elif model in config.GOOGLE_MODEL_MAP:
            gemini_adapter.get_model_chat_response(
                user_input=user_input,
                console=console,
                chat_session=chat_session,
                temperature=ctx.obj["temperature"],
            )
        elif model in config.ANTHROPIC_MODEL_MAP:
            client = ctx.obj["client"]
            input_messages = anthropic_adapter.get_model_chat_response(
                user_input=user_input,
                console=console,
                input_messages=input_messages,
                temperature=ctx.obj["temperature"],
                model=model,
                client=client,
            )

        user_input = None


@main.command(help="Natural language to terminal commands")
@click.argument("user_input", nargs=-1)
@click.option(
    "--fast",
    is_flag=True,
    default=False,
    help="Get commands without explanations (may be less accurate)",
)
@click.pass_context
def cmd(ctx, user_input, fast):
    """
    Natural Language to Terminal Commands
    """
    input_request = "\nDesired Command Request: "

    if user_input:
        user_input = str(" ".join(user_input))
        session.history.append_string(user_input)

    model = ctx.obj["model"]

    if not user_input:
        console.print("[gray]Type 'quit' to exit[/gray]")

    while True:
        if not user_input:
            user_input = utils.prompt_user_input(
                input_request,
                session,
                console,
                completer=utils.PathCompleter(),
                complete_style=CompleteStyle.MULTI_COLUMN,
                key_bindings=config.kb,
            )

        if not user_input:
            continue

        model_output = None
        if model in config.OPENAI_MODEL_MAP or model in config.LLAMA_CPP_MODEL_MAP:
            # llama.cpp models are OpenAI API drop-in compatible
            client = ctx.obj["client"]
            model_output = openai_adapter.model_command(
                user_input=user_input,
                console=console,
                fast_mode=fast,
                model=model,
                client=client,
            )
        elif model in config.HF_MODEL_MAP:
            api_token = ctx.obj.get("api_key", None)
            model_output = huggingface_adapter.model_command(
                user_input=user_input,
                console=console,
                api_token=api_token,
                fast_mode=fast,
                model=model,
            )
        elif model in config.GOOGLE_MODEL_MAP:
            model_output = gemini_adapter.model_command(
                user_input=user_input,
                console=console,
                fast_mode=fast,
                model=model,
            )
        elif model in config.ANTHROPIC_MODEL_MAP:
            model_output = anthropic_adapter.model_command(
                user_input=user_input,
                console=console,
                fast_mode=fast,
                model=model,
                client=ctx.obj["client"],
            )

        user_input = None  # clear input for next iteration

        commands = utils.print_command_response(model_output, console, fast)
        if not commands:
            continue

        # Give user options to revise query, execute command(s), or quit
        options = [
            "Revise Query",
            "Execute Command(s)",
            "Copy Command(s) to Clipboard",
            "Quit",
        ]
        questions = [
            inquirer.List("Next", message="What would you like to do?", choices=options)
        ]
        selected_option = inquirer.prompt(questions)["Next"]  # type: ignore

        if selected_option == "Revise Query":
            input_request = "Revised Command Request: "
            continue
        elif selected_option == "Execute Command(s)":
            console.print("[bold blue]Executing command(s)...\n[/bold blue]")

            for idx, cmd in enumerate(commands):
                if cmd:
                    console.print(
                        f"""[bold blue]Executing Command [{idx+1}]: {cmd}[/bold blue]"""
                    )
                    subprocess.run(cmd, shell=True)

        elif selected_option == "Copy Command(s) to Clipboard":
            utils.copy_comands_to_cliboard(commands)
            console.print("[bold blue]Copied command(s) to clipboard[/bold blue]")
        else:
            console.print("[bold blue]Exiting...\n[/bold blue]")

        sys.exit(0)


"""
@main.command()
@click.pass_context
def test(ctx):
    pass
    while True:
        user_input = utils.prompt_user_input(
            "Chat: ", session, console, auto_suggest=AutoSuggestFromHistory()
        )
        if len(user_input) == 0:
            continue
"""

"""
@main.command(help="Used for manual testing of all models")
@click.pass_context
def manual_test_cases(ctx):
    for model in config.SUPPORTED_MODELS:
        console.print(
            f"developergpt --model {model} cmd find all files in ~/Documents larger than 50kB"
        )
        console.print(
            f"developergpt --model {model} cmd --fast find all files in ~/Documents larger than 50kB"
        )
        console.print(f"developergpt --model {model} chat")
"""

if __name__ == "__main__":
    main()
