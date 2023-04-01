"""
Anthony Luo
UNDER DEVELOPMENT
"""

import json
import os
import sys
from functools import wraps

import click
import inquirer
import openai
from rich.console import Console
from rich.live import Live
from rich.markdown import Markdown
from rich.panel import Panel

from developergpt import config, utils

console = Console()

DEFAULT_COLUMN_WIDTH = 100


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
@click.pass_context
@click.option(
    "--temperature",
    default=0.1,
    help="The temperature of the response (higher means more creative, lower means more predictable)",
)
def main(ctx, temperature):
    if not os.environ.get("OPENAI_API_KEY"):
        console.print(
            "No OPENAI_API_KEY environment variable found. Please set the OPENAI_API_KEY environment variable. \n EXPORT OPENAI_API_KEY=<your_api_key>"
        )
        sys.exit(-1)
    openai.api_key = os.environ["OPENAI_API_KEY"]
    ctx.ensure_object(dict)
    ctx.obj["temperature"] = temperature


@click.command(help="Chat with DeveloperGPT")
@click.pass_context
def chat(ctx):
    # TODO save previous conversations like the web interface does?
    MODEL = "gpt-3.5-turbo"
    MAX_TOKENS = 4000
    RESERVED_OUTPUT_TOKENS = 1024
    MAX_INPUT_TOKENS = MAX_TOKENS - RESERVED_OUTPUT_TOKENS
    input_messages = [config.INITIAL_CHAT_SYSTEM_MSG]
    console.print("[gray] Type 'quit' to exit the chat[/gray]")
    while True:
        user_input = console.input("\n[bold green]Chat: [/bold green]").strip()
        if len(user_input) == 0:
            continue

        if user_input.lower() == "quit":
            console.print("[bold blue]Bye! [/bold blue]")
            break

        input_messages.append({"role": "user", "content": user_input})
        input_messages, n_input_tokens = utils.check_reduce_context(
            input_messages, MAX_INPUT_TOKENS, MODEL, ctx_removal_index=1
        )
        n_output_tokens = max(RESERVED_OUTPUT_TOKENS, MAX_TOKENS - n_input_tokens)
        full_response = get_model_chat_response(
            MODEL, input_messages, n_output_tokens, ctx.obj["temperature"]
        )
        input_messages.append({"role": "assistant", "content": full_response})


@handle_api_error
def get_model_chat_response(
    model: str, messages: list, max_tokens: int, temperature: float
) -> str:
    """Get the response from the model."""
    response = openai.ChatCompletion.create(
        model=model,
        messages=messages,
        max_tokens=max_tokens,
        temperature=temperature,
        stream=True,
    )

    collected_messages = []
    panel_width = min(console.width, DEFAULT_COLUMN_WIDTH)
    output_panel = Panel(
        "",
        title="[bold blue]DeveloperGPT[/bold blue]",
        title_align="left",
        width=panel_width,
    )

    # TODO prettify the output
    with Live(output_panel, refresh_per_second=4):
        for chunk in response:
            msg = chunk["choices"][0]["delta"].get("content", "")
            collected_messages.append(msg)
            output_panel.renderable = Markdown(
                "".join(collected_messages), inline_code_theme="monokai"
            )

    full_response = "".join(collected_messages)
    return full_response


# def format_model_output(text: str) -> str:
#     """Format the model output to be more readable."""
#     text = re.sub(
#         r"```(.+?)```", "[syntax]" + r"\1" + "[/syntax]", text, flags=re.DOTALL
#     )
#     text = re.sub(r"`(.+?)`", "[syntax]" + r"\1" +
#                   "[/syntax]", text, flags=re.DOTALL)
#     text.replace("```", "[syntax]")
#     return text


@click.command(help="Execute commands using natural language")
@handle_api_error
def cmd():
    input_request = "\n[bold green]Desired Command Request: [/bold green]"

    MODEL = "gpt-3.5-turbo"
    MAX_TOKENS = 4000
    RESERVED_OUTPUT_TOKENS = 1024
    MAX_INPUT_TOKENS = MAX_TOKENS - RESERVED_OUTPUT_TOKENS
    TEMP = 0.05
    panel_width = min(console.width, DEFAULT_COLUMN_WIDTH)

    input_messages = [
        config.INITIAL_CMD_SYSTEM_MSG,
        config.INITIAL_USER_CMD_MSG,
        *config.EXAMPLE_ONE,
        *config.EXAMPLE_TWO,
        *config.NEGATIVE_EXAMPLE_ONE,
    ]
    console.print("[gray] Type 'quit' to exit[/gray]")

    while True:
        user_input = console.input(input_request).strip()
        if len(user_input) == 0:
            continue

        if user_input.lower() == "quit":
            console.print("[bold blue]Bye! [/bold blue]")
            break

        input_messages.append(config.format_user_request(user_input))

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
        # console.log(model_output)
        try:
            output_data = json.loads(model_output)
        except json.decoder.JSONDecodeError:
            console.print(
                "[bold red]Error: Could not parse model response properly[/bold red]"
            )
            continue

        if output_data.get("error", 0) or "commands" not in output_data:
            console.print(
                "[bold red]Error: Could not find commands for this request[/bold red]"
            )
            continue

        commands = output_data.get("commands", {})

        # print all the commands in a panel
        commands_format = "\n\n".join(
            [f"""- `{c.get("cmd_to_execute", "")}`""" for c in commands]
        )

        cmd_out = Markdown(
            commands_format,
            inline_code_lexer="bash",
        )

        console.print(
            Panel(
                cmd_out,
                title="[bold blue]Command(s)[/bold blue]",
                title_align="left",
                width=panel_width,
            )
        )

        # print all the explanations in a panel
        explanation_items = []
        for cmd in commands:
            explanation_items.extend(
                [f"- {c}" for c in cmd.get("cmd_explanations", [])]
            )
            explanation_items.extend(
                [f"\t- {c}" for c in cmd.get("arg_explanations", [])]
            )

        arg_out = Markdown("\n".join(explanation_items))

        console.print(
            Panel(
                arg_out,
                title="[bold blue]Explanation[/bold blue]",
                title_align="left",
                width=panel_width,
            )
        )

        # TODO: make this look nicer
        # Give user options to revise query, execute command(s), or quit
        options = ["Revise Query", "Execute Command(s)", "Quit"]
        questions = [
            inquirer.List("Next", message="What would you like to do?", choices=options)
        ]

        selected_option = inquirer.prompt(questions)["Next"]

        if selected_option == "Revise Query":
            input_request = "[bold green] Revised Command Request: [/bold green]"
            continue
        elif selected_option == "Execute Command(s)":
            console.print("[bold blue]Executing command(s)...\n[/bold blue]")
            for idx, cmd in enumerate(commands):
                console.print(
                    f"""[bold blue]Executing Command [{idx+1}]: {cmd.get('cmd_to_execute', '')}[/bold blue]"""
                )
                os.system(cmd.get("cmd_to_execute", ""))
        else:
            console.print("[bold blue]Exiting...\n[/bold blue]")

        sys.exit(0)


@click.command()
def test():
    # used for testing functions
    pass


@click.command()
@click.pass_context
def api(ctx):
    # TODO: API command that exposes api to developer in terminal
    # NOTE: OpenAI has a command line tool already, this may not be nescessary
    pass


main.add_command(cmd)
main.add_command(chat)
# main.add_command(api)
# main.add_command(test)

if __name__ == "__main__":
    main()
