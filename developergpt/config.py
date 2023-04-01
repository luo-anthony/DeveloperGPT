"""
DeveloperGPT by luo-anthony
"""
import platform
from datetime import datetime

json_cmd_format = """
    {
        "input": "<user input>",
        "error": 0,
        "commands": [
            {
                "seq": <Order of Command>,
                "cmd_to_execute": "<commands and arguments to execute>",
                "cmd_explanations": ["<explanation of command 1>", "<explantion of command 2>", ...],
                "arg_explanations": ["<explanation of argument 1>", "<explanation of argument 2>", ...]
            },
            {
                "seq": <Order of Command>,
                "cmd_to_execute": "<commands and arguments to execute>",
                "cmd_explanations": ["<explanation of command 1>", "<explantion of command 2>", ...],
                "arg_explanations": ["<explanation of argument 1>", "<explanation of argument 2>", ...]
            }
        ]
    }
    """

json_invalid_format = """{"input": "<user input>", "error": 1}"""

conda_output_example = """
    {
        "input": "install conda",
        "error": 0,
        "commands": [
            {
                "seq": 1,
                "cmd_to_execute": "curl -O https://repo.anaconda.com/miniconda/Miniconda3-latest-MacOSX-x86_64.sh",
                "cmd_explanations": ["The `curl` command is used to issue web requests, e.g. download web pages."],
                "arg_explanations": [
                                        "`-O` specifies that we want to save the response to a file.",
                                        "`https://repo.anaconda.com/miniconda/Miniconda3-latest-MacOSX-x86_64.sh` is the URL of the file we want to download."
                                    ]
            },
            {
                "seq": 2,
                "cmd_to_execute": "bash Miniconda3-latest-MacOSX-x86_64.sh",
                "cmd_explanations": ["The `bash` command is used to execute shell scripts."],
                "arg_explanations": ["`Miniconda3-latest-MacOSX-x86_64.sh` is the name of the file we want to execute."]
            }
        ]
    }
    """

search_output_example = """
    {
        "input": "search the ~/Documents/ directory for any .py file that begins with 'test'",
        "error" : 0,
        "commands": [
            {
                "seq": 1,
                "cmd_to_execute": "find ~/Documents/ -name "test*.py"",
                "cmd_explanations": ["`find` is used to list files."],
                "arg_explanations": [
                                        "``~/Documents` specifies the folder to search in.",
                                        "`-name "test.py"` specifies that we want to search for files starting with `test` and ending with `.py`."
                                    ]
            }
        ]
    }
    """

unknown_query_output_example_one = (
    """{"input": "the quick brown fox jumped over", "error": 1}"""
)

INITIAL_CHAT_SYSTEM_MSG = {
    "role": "system",
    "content": f"""
                You are DeveloperGPT, a helpful personal assistant for a programmer working on a {platform.platform()} machine. 
                Your task is to assist the programmer with any programming-related tasks they may have. 
                This could include providing advice on how to approach a programming problem, suggesting tools or libraries to use for a particular task, 
                helping to troubleshoot errors or bugs in code, answering general programming questions, and providing code snippets or examples.

                Please keep your answers short and concise and use a suitable format for printing on the terminal. 
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

            If the request is valid, format each command output in the following JSON format: {json_cmd_format}

            If the request is invalid, please return the following JSON format: {json_invalid_format}
            """,
}


def format_user_request(user_request: str) -> dict[str, str]:
    return {
        "role": "user",
        "content": f"""Provide the appropriate command-line commands that can be executed on a {platform.platform()} machine for the user request: "{user_request}".""",
    }


def format_assistant_response(assistant_response: str) -> dict[str, str]:
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

NEGATIVE_EXAMPLE_ONE = (
    format_user_request("the quick brown fox jumped over"),
    format_assistant_response(unknown_query_output_example_one),
)
