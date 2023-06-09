"""
DeveloperGPT by luo-anthony
"""

import subprocess
import sys
from functools import wraps

import click
import inquirer
import openai
from prompt_toolkit import PromptSession
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.shortcuts import CompleteStyle
from rich.console import Console

from developergpt import config, huggingface_adapter, openai_adapter, utils

console: Console = Console()
session: PromptSession = PromptSession()


def handle_api_error(f):
    """Handle API errors gracefully"""

    @wraps(f)
    def internal(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except openai.error.RateLimitError:
            console.print("[bold red] Rate limit exceeded. Try again later.[/bold red]")
            sys.exit(-1)
        except openai.error.ServiceUnavailableError:
            console.print("[bold red] Service Unavailable. Try again later.[/bold red]")
            sys.exit(-1)
        except openai.error.InvalidRequestError as e:
            console.log(f"[bold red] Invalid Request: {e}[/bold red]")
            sys.exit(-1)

    return internal


@click.group()
@click.option(
    "--temperature",
    default=0.1,
    help="The temperature of the model response (higher means more creative, lower means more predictable)",
)
@click.option(
    "--model",
    default="gpt-3.5-turbo",
    help="The language model to use. Options: gpt-3.5-turbo (default), gpt-4, bloom",
)
@click.pass_context
def main(ctx, temperature, model):
    model = model.lower().strip()
    if not utils.check_connectivity():
        console.print(
            "[bold red]No internet connection. Please check your internet connection and try again.[/bold red]"
        )
        sys.exit(-1)

    if model not in config.SUPPORTED_MODELS:
        console.print(
            f"""[bold red]Model {model} is not supported. 
            Supported models: {",".join(config.SUPPORTED_MODELS)}[/bold red]"""
        )
        sys.exit(-1)

    ctx.ensure_object(dict)
    if model == config.GPT35 or model == config.GPT4:
        openai.api_key = config.get_environ_key(config.OPEN_AI_API_KEY, console)
        openai_adapter.check_open_ai_key(console)
    elif model == config.BLOOM:
        ctx.obj["api_key"] = config.get_environ_key_optional(
            config.HUGGING_FACE_API_KEY, console
        )
        console.print(
            "[bold yellow]Using Bloom 176B model: some features may have unexpected behavior and results may not be as good as using GPT-3.5.[/bold yellow]"
        )

    ctx.obj["temperature"] = temperature
    ctx.obj["model"] = model


@main.command(help="Chat with DeveloperGPT")
@click.pass_context
@click.argument("user_input", nargs=-1)
@handle_api_error
def chat(ctx, user_input):
    if user_input:
        user_input = str(" ".join(user_input))
        session.history.append_string(user_input)

    model = ctx.obj["model"]

    if model == config.GPT35 or model == config.GPT4:
        input_messages = [openai_adapter.INITIAL_CHAT_SYSTEM_MSG]
    elif model == config.BLOOM:
        input_messages = huggingface_adapter.BASE_INPUT_CHAT_MSGS
        api_token = ctx.obj.get("api_key", None)
    console.print("[gray]Type 'quit' to exit the chat[/gray]")
    while True:
        if not user_input:
            user_input = utils.prompt_user_input(
                "Chat: ", session, console, auto_suggest=AutoSuggestFromHistory()
            )

        if not user_input:
            continue

        if model == config.GPT35 or model == config.GPT4:
            input_messages = openai_adapter.get_model_chat_response(
                user_input, console, input_messages, ctx.obj["temperature"], model
            )
        elif model == config.BLOOM:
            input_messages = huggingface_adapter.get_model_chat_response(
                user_input, console, input_messages, api_token
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
@handle_api_error
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

    if model == config.BLOOM:
        console.print(
            "[bold yellow]WARNING: Bloom 176B model command outputs are less accurate than GPT-3.5. Check all commands before running them.[/bold yellow]"
        )
        api_token = ctx.obj.get("api_key", None)

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

        if model == config.GPT35 or model == config.GPT4:
            model_output = openai_adapter.model_command(
                user_input, console, fast, model
            )
        elif model == config.BLOOM:
            model_output = huggingface_adapter.model_command(
                user_input, console, api_token, fast
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
        selected_option = inquirer.prompt(questions)["Next"]

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


@main.command(help="Give feedback")
def feedback():
    console.print(
        f"Thanks for using DeveloperGPT! You can [bold blue][link={config.FEEDBACK_LINK}]give feedback here[/link][/bold blue]!"
    )


if __name__ == "__main__":
    main()
