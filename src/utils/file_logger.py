# src/utils/file_logger.py

import os
from datetime import datetime

from hvac.api.secrets_engines.aws import json

LOG_FILE_PATH = "data/logs/send_message_logic_flow.log"
UI_LOG_FILE_PATH = "data/logs/ui_logic_flow.log"
CHATBOT_LOG_FILE_PATH = "data/logs/chatbots.log"


def log_to_file(
    log_file_path: str, message: str | None = None, variables: dict | None = None
):
    """
    Logs a message and/or variable values to a file.

    Args:
        log_file_path (str): The path to the log file.
        message (str, optional): The message to log. Defaults to None.
        variables (dict, optional): A dictionary of variables and their values to log. Defaults to None.
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}]\n"

    if message:
        log_entry += f"Message: {message}\n"

    if variables:
        for variable_name, variable_value in variables.items():
            log_entry += f"{variable_name}: {variable_value}\n"

    log_entry += "\n"

    with open(log_file_path, "a") as log_file:
        log_file.write(log_entry)


def log_function_call(log_file_path: str, function_name: str, **kwargs):
    """
    Logs a function call with its arguments.

    Args:
        log_file_path (str): The path to the log file.
        function_name (str): The name of the function being called.
        **kwargs: Keyword arguments representing the function's arguments.
    """
    log_entry = f"Function Call: {function_name}()\n"
    for arg_name, arg_value in kwargs.items():
        log_entry += f"  {arg_name}: {arg_value}\n"
    log_to_file(log_file_path, log_entry)


def log_variable(log_file_path: str, variable_name: str, variable_value):
    """
    Logs a variable and its value.

    Args:
        log_file_path (str): The path to the log file.
        variable_name (str): The name of the variable.
        variable_value: The value of the variable.
    """
    log_to_file(log_file_path, variables={variable_name: variable_value})


def initialize_log_file(log_file_path: str):
    """
    Initializes the log file by creating it if it doesn't exist and adding a header.

    Args:
        log_file_path (str): The path to the log file.
    """
    if not os.path.exists(log_file_path):
        with open(log_file_path, "w") as log_file:
            log_file.write("Log File Initialized\n\n")


def log_json_content(log_file_path: str, json_content: dict | list[dict]):
    """
    Logs the content of a JSON object or a list of JSON objects in a pretty-printed format.

    Args:
        log_file_path (str): The path to the log file.
        json_content (dict | list[dict]): The JSON object or list of JSON objects to log.
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}]\n"
    log_entry += "JSON Content:\n"

    if isinstance(json_content, dict):
        log_entry += json.dumps(json_content, indent=2)
    elif isinstance(json_content, list):
        for item in json_content:
            if isinstance(item, dict):
                log_entry += json.dumps(item, indent=2)
                log_entry += "\n"
            else:
                log_entry += f"{item}\n"
    else:
        log_entry += f"{json_content}\n"

    log_entry += "\n"

    with open(log_file_path, "a") as log_file:
        log_file.write(log_entry)
