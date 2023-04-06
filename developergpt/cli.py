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
    if model not in config.SUPPORTED_MODELS:
        console.print(
            f"""[bold red]Model {model} is not supported. 
            Supported models: {",".join(config.SUPPORTED_MODELS)}[/bold red]"""
        )
        sys.exit(-1)
    if model == config.GPT35:
        openai.api_key = config.get_environ_key(config.OPEN_AI_API_KEY, console)
    elif model == config.BLOOM:
        console.print(
            "[bold yellow]Using Bloom 176B model: some features may not be supported and results may not be as good as using GPT-3.5.[/bold yellow]"
        )
        # we don't need the api key for bloom yet

    ctx.ensure_object(dict)
    ctx.obj["temperature"] = temperature
    ctx.obj["model"] = model


@click.command(help="Chat with DeveloperGPT")
@click.pass_context
@handle_api_error
def chat(ctx):
    # TODO save previous conversations like the web interface does?
    if ctx.obj["model"] != config.GPT35:
        console.print(
            f"""[bold red]Model {ctx.obj["model"]} is not supported for chat. 
            Supported models: {config.GPT35}[/bold red]"""
        )
        sys.exit(-1)

    MODEL = "gpt-3.5-turbo"
    MAX_TOKENS = 4000
    RESERVED_OUTPUT_TOKENS = 1024
    MAX_INPUT_TOKENS = MAX_TOKENS - RESERVED_OUTPUT_TOKENS
    input_messages = [openai_adapter.INITIAL_CHAT_SYSTEM_MSG]
    console.print("[gray]Type 'quit' to exit the chat[/gray]")
    while True:
        user_input = utils.prompt_user_input(
            "Chat: ", session, console, auto_suggest=AutoSuggestFromHistory()
        )

        if len(user_input) == 0:
            continue

        input_messages.append({"role": "user", "content": user_input})
        input_messages, n_input_tokens = utils.check_reduce_context(
            input_messages, MAX_INPUT_TOKENS, MODEL, ctx_removal_index=1
        )
        n_output_tokens = max(RESERVED_OUTPUT_TOKENS, MAX_TOKENS - n_input_tokens)
        full_response = openai_adapter.get_model_chat_response(
            MODEL, console, input_messages, n_output_tokens, ctx.obj["temperature"]
        )
        input_messages.append({"role": "assistant", "content": full_response})


@click.command(help="Execute commands using natural language")
@click.pass_context
@handle_api_error
def cmd(ctx):
    input_request = "\nDesired Command Request: "

    model = ctx.obj["model"]
    input_messages = copy.deepcopy(openai_adapter.BASE_INPUT_CMD_MSGS)

    console.print("[gray]Type 'quit' to exit[/gray]")
    while True:
        user_input = utils.prompt_user_input(
            input_request,
            session,
            console,
            completer=utils.PathCompleter(),
            complete_style=CompleteStyle.MULTI_COLUMN,
        )
        if len(user_input) == 0:
            continue

        if model == config.GPT35:
            commands = openai_adapter.model_command(user_input, console, input_messages)
        elif model == config.BLOOM:
            commands = huggingface_adapter.model_command(user_input, console)

        if not commands:
            continue

        # TODO: make this look nicer
        # Give user options to revise query, execute command(s), or quit
        options = ["Revise Query", "Execute Command(s)", "Quit"]
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

        else:
            console.print("[bold blue]Exiting...\n[/bold blue]")

        sys.exit(0)


@click.command()
@click.pass_context
def api(ctx):
    # TODO: API command that exposes api to developer in terminal
    # NOTE: OpenAI has a command line tool already, this may not be nescessary
    pass


@click.command()
@click.pass_context
def test(ctx):
    pass


main.add_command(cmd)
main.add_command(chat)
# main.add_command(api)
# main.add_command(test)

if __name__ == "__main__":
    main()
