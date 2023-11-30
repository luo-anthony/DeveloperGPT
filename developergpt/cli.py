"""
DeveloperGPT by luo-anthony
"""

import subprocess
import sys
from functools import wraps

import click
import inquirer
from openai import OpenAI
from prompt_toolkit import PromptSession
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.shortcuts import CompleteStyle
from rich.console import Console

from developergpt import config, huggingface_adapter, openai_adapter, utils

console: Console = Console()
session: PromptSession = PromptSession()


@click.group()
@click.option(
    "--temperature",
    default=0.1,
    help="The temperature of the model response (higher means more creative, lower means more predictable)",
)
@click.option(
    "--model",
    default="gpt35",
    help=f"The LLM to use. Options: f{', '.join(config.SUPPORTED_MODELS)}",
)
@click.pass_context
def main(ctx, temperature, model):
    model = model.lower().strip().replace(".", "")
    if not utils.check_connectivity():
        console.print(
            "[bold red]No internet connection. Please check your internet connection and try again.[/bold red]"
        )
        sys.exit(-1)

    if model not in config.SUPPORTED_MODELS:
        console.print(
            f"""[bold red]LLM {model} is not supported. 
            Supported LLMs: {", ".join(config.SUPPORTED_MODELS)}[/bold red]"""
        )
        sys.exit(-1)

    ctx.ensure_object(dict)
    if model in config.OPENAI_MODEL_MAP:
        client = OpenAI(api_key=config.get_environ_key(config.OPEN_AI_API_KEY, console))
        openai_adapter.check_open_ai_key(console, client)
        ctx.obj["client"] = client
    elif model in config.HF_MODEL_MAP:
        ctx.obj["api_key"] = config.get_environ_key_optional(
            config.HUGGING_FACE_API_KEY, console
        )

        console.print(
            f"[bold yellow]Using {config.HF_MODEL_MAP[model]} via HF: some features may have unexpected behavior and results may not be as accurate as OpenAI GPT LLMs."
        )

    ctx.obj["temperature"] = temperature
    ctx.obj["model"] = model


@main.command(help="Chat with DeveloperGPT")
@click.pass_context
@click.argument("user_input", nargs=-1)
def chat(ctx, user_input):
    if user_input:
        user_input = str(" ".join(user_input))
        session.history.append_string(user_input)

    model = ctx.obj["model"]

    if model in config.OPENAI_MODEL_MAP:
        input_messages = [openai_adapter.INITIAL_CHAT_SYSTEM_MSG]
    elif model in config.HF_MODEL_MAP:
        input_messages = huggingface_adapter.BASE_INPUT_CHAT_MSGS
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

        if model in config.OPENAI_MODEL_MAP:
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
                model=model,
            )

        user_input = None


@main.command(help="Execute commands using natural language")
@click.argument("user_input", nargs=-1)
@click.option(
    "--fast",
    is_flag=True,
    default=False,
    help="Get commands without command or argument explanations (less accurate)",
)
@click.pass_context
def cmd(ctx, user_input, fast):
    input_request = "\nDesired Command Request: "

    if fast:
        console.print(
            "[bold yellow]Using Fast Mode: Commands are given without explanation and may be less accurate[/bold yellow]"
        )

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
        if model in config.OPENAI_MODEL_MAP:
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
        user_input = None  # clear input for next iteration

        commands = utils.print_command_response(model_output, console, fast, model)
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


# @main.command()
@click.pass_context
def test(ctx):
    pass
    # while True:
    #     user_input = utils.prompt_user_input(
    #         "Chat: ", session, console, auto_suggest=AutoSuggestFromHistory()
    #     )

    #     if len(user_input) == 0:
    #         continue

    #     print(user_input)


if __name__ == "__main__":
    main()
