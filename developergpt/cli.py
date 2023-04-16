"""
DeveloperGPT by luo-anthony
"""

import copy
import subprocess
import sys
from functools import wraps

import click
import inquirer
import openai
from prompt_toolkit import PromptSession
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.key_binding.key_processor import KeyPressEvent
from prompt_toolkit.keys import Keys
from prompt_toolkit.shortcuts import CompleteStyle
from rich.console import Console

from developergpt import config, huggingface_adapter, openai_adapter, utils

console = Console()
session: "PromptSession" = PromptSession()


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
    default="gpt-3.5",
    help="The language model to use. Options: gpt-3.5 (default), bloom",
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
    if model == config.GPT35:
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


@click.command(help="Chat with DeveloperGPT")
@click.pass_context
@handle_api_error
def chat(ctx):
    model = ctx.obj["model"]

    if model == config.GPT35:
        input_messages = [openai_adapter.INITIAL_CHAT_SYSTEM_MSG]
    elif model == config.BLOOM:
        input_messages = huggingface_adapter.BASE_INPUT_CHAT_MSGS
    console.print("[gray]Type 'quit' to exit the chat[/gray]")
    while True:
        user_input = utils.prompt_user_input(
            "Chat: ", session, console, auto_suggest=AutoSuggestFromHistory()
        )

        if len(user_input) == 0:
            continue

        if model == config.GPT35:
            input_messages = openai_adapter.get_model_chat_response(
                user_input, console, input_messages, ctx.obj["temperature"]
            )
        elif model == config.BLOOM:
            api_token = ctx.obj.get("api_key", None)
            input_messages = huggingface_adapter.get_model_chat_response(
                user_input, console, input_messages, api_token
            )


kb = KeyBindings()


@kb.add(Keys.Enter, eager=True)
def _(event: KeyPressEvent):
    buff = event.app.current_buffer
    if buff.complete_state:
        # during completion, enter will select the current completion instead of submitting input
        if buff.complete_state.current_completion:
            buff.apply_completion(buff.complete_state.current_completion)
            return  # don't submit input
    buff.validate_and_handle()


@click.command(help="Execute commands using natural language")
@click.pass_context
@handle_api_error
def cmd(ctx):
    input_request = "\nDesired Command Request: "

    model = ctx.obj["model"]
    input_messages = copy.deepcopy(openai_adapter.BASE_INPUT_CMD_MSGS)

    console.print("[gray]Type 'quit' to exit[/gray]")

    if model == config.BLOOM:
        console.print(
            "[bold yellow]WARNING: Bloom 176B model command outputs are less accurate than GPT-3.5. Check all commands before running them.[/bold yellow]"
        )

    while True:
        user_input = utils.prompt_user_input(
            input_request,
            session,
            console,
            completer=utils.PathCompleter(),
            complete_style=CompleteStyle.MULTI_COLUMN,
            key_bindings=kb,
        )
        if len(user_input) == 0:
            continue

        if model == config.GPT35:
            model_output = openai_adapter.model_command(
                user_input, console, input_messages
            )
        elif model == config.BLOOM:
            model_output = huggingface_adapter.model_command(user_input, console)

        commands = utils.print_command_response(model_output, console)
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

            console.print(
                "[bold blue]Copied executed command(s) to clipboard[/bold blue]"
            )
            utils.copy_comands_to_cliboard(commands)
        elif selected_option == "Copy Command(s) to Clipboard":
            utils.copy_comands_to_cliboard(commands)
            console.print("[bold blue]Copied command(s) to clipboard[/bold blue]")
        else:
            console.print("[bold blue]Exiting...\n[/bold blue]")

        sys.exit(0)


@click.command()
@click.pass_context
def test(ctx):
    pass
    # while True:
    #     user_input = utils.prompt_user_input(
    #         "Chat: ", session, console, auto_suggest=AutoSuggestFromHistory()
    #     )

    #     if len(user_input) == 0:
    #         continue


@click.command(help="Give feedback")
def feedback():
    console.print(
        "Thanks for using DeveloperGPT! You can [bold blue][link=https://forms.gle/J36KbztsRAPHXnrKA]give feedback here[/link][/bold blue]!"
    )


main.add_command(cmd)
main.add_command(chat)
main.add_command(feedback)
# main.add_command(test)

if __name__ == "__main__":
    main()
