CONDA_REQUEST = "install conda"

CONDA_OUTPUT_EXAMPLE = """
    {
        "input": conda_request,
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
                "arg_explanations": [
                                        "``~/Documents` specifies the folder to search in.",
                                        "`-name 'test.py'` specifies that we want to search for files starting with `test` and ending with `.py`."
                                    ]
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
