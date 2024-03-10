from datetime import datetime

from developergpt import config

JSON_CMD_FORMAT = """
    {
        "input": "<user input>",
        "error": 0,
        "commands": [
            {
                "seq": <Order of Command>,
                "cmd_to_execute": "<commands and arguments to execute>",
                "cmd_explanations": ["<explanation of command 1>", "<explantion of command 2>", ...],
                "arg_explanations": {"<arg1>": "<explanation of arg1>", "<arg2>": "<explanation of argument 2>", ...}
            },
            {
                "seq": <Order of Command>,
                "cmd_to_execute": "<commands and arguments to execute>",
                "cmd_explanations": ["<explanation of command 1>", "<explantion of command 2>", ...],
                "arg_explanations": {"<arg1>": "<explanation of arg1>", "<arg2>": "<explanation of argument 2>", ...}
            }
        ]
    }
    """

JSON_CMD_FORMAT_FAST = """
    {
        "commands": ["<commands and arguments to execute>", "<commands and arguments to execute>", ...]
    }
    """

JSON_INVALID_FORMAT = """{"input": "<user input>", "error": 1}"""

JSON_INVALID_FORMAT_FAST = """{"error": 1}"""


def format_initial_cmd_msg(cmd_format: str, invalid_format: str) -> str:
    return f"""
                Provide the appropriate command-line commands that can be executed for a user request (keep in mind the platform of the user).
                Today's date/time is {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}.
                If the request is possible, please provide commands that can be executed in the command line and do not require a GUI.
                Do not include commands that require a yes/no response.
                For each command, explain the command and any arguments used.
                Try to find the simplest command(s) that can be used to execute the request.

                If the request is valid, format each command output in the following JSON format: {cmd_format}

                If the request is invalid, please return the following JSON format: {invalid_format}
                """


INITIAL_USER_CMD_MSG = format_initial_cmd_msg(JSON_CMD_FORMAT, JSON_INVALID_FORMAT)

INITIAL_USER_CMD_MSG_FAST = format_initial_cmd_msg(
    JSON_CMD_FORMAT_FAST, JSON_INVALID_FORMAT_FAST
)

CONDA_REQUEST = "install conda"

CONDA_OUTPUT_EXAMPLE = """
    {
        "input": "install conda",
        "error": 0,
        "commands": [
            {
                "seq": 1,
                "cmd_to_execute": "curl -O https://repo.anaconda.com/miniconda/Miniconda3-latest-MacOSX-x86_64.sh",
                "cmd_explanations": ["The `curl` command is used to issue web requests, e.g. download web pages."],
                "arg_explanations": {
                                        "-O": "specifies that we want to save the response to a file.",
                                        "https://repo.anaconda.com/miniconda/Miniconda3-latest-MacOSX-x86_64.sh": "is the URL of the file we want to download."
                                    }
            },
            {
                "seq": 2,
                "cmd_to_execute": "bash Miniconda3-latest-MacOSX-x86_64.sh",
                "cmd_explanations": ["The `bash` command is used to execute shell scripts."],
                "arg_explanations": {"Miniconda3-latest-MacOSX-x86_64.sh": "is the name of the file we want to execute."}
            }
        ]
    }
    """

CONDA_OUTPUT_EXAMPLE_FAST = """
    {
        "commands": ["curl -O https://repo.anaconda.com/miniconda/Miniconda3-latest-MacOSX-x86_64.sh", "bash Miniconda3-latest-MacOSX-x86_64.sh"]
    }
    """

CONDA_OUTPUT_EXAMPLE_MARKDOWN = """
`curl -O https://repo.anaconda.com/miniconda/Miniconda3-latest-MacOSX-x86_64.sh`\n
`bash Miniconda3-latest-MacOSX-x86_64.sh`\n
"""

SEARCH_REQUEST = "search ~/Documents directory for any .py file that begins with 'test'"

SEARCH_OUTPUT_EXAMPLE = """
    {
        "input": "search the ~/Documents/ directory for any .py file that begins with 'test'",
        "error" : 0,
        "commands": [
            {
                "seq": 1,
                "cmd_to_execute": "find ~/Documents/ -name 'test*.py'",
                "cmd_explanations": ["`find` is used to list files."],
                "arg_explanations": {
                                        "~/Documents": "specifies the folder to search in.",
                                        "-name 'test*.py'": "specifies that we want to search for files starting with `test` and ending with `.py`."
                                    }
            }
        ]
    }
    """

SEARCH_OUTPUT_EXAMPLE_FAST = """
    {
        "commands": ["find ~/Documents/ -name 'test*.py'"]
    }
    """

SEARCH_OUTPUT_EXAMPLE_MARKDOWN = """
`find ~/Documents/ -name 'test*.py'`\n
"""

PROCESS_REQUEST = "list all processes using more than 50 MB of memory"

PROCESS_OUTPUT_EXAMPLE_FAST = """
{
"commands": ["ps -axm -o %mem,rss,comm | awk '$1 > 0.5 { printf(\\"%.0fMB\\\\t%s\\\\n\\", $2/1024, $3); }'"]
}
"""

PROCESS_OUTPUT_EXAMPLE_MARKDOWN = """
`ps -axm -o %mem,rss,comm | awk '$1 > 0.5 { printf(\\"%.0fMB\\\\t%s\\\\n\\", $2/1024, $3); }'`\n
"""

UNKNOWN_REQUEST = "the quick brown fox jumped over"

UNKNOWN_QUERY_OUTPUT_EXAMPLE_ONE = (
    """{"input": "the quick brown fox jumped over", "error": 1}"""
)

UNKNOWN_QUERY_OUTPUT_EXAMPLE_ONE_FAST = """{"error": 1}"""

EXAMPLE_PLATFORM = "macOS-13.3.1-x86-64bit"
