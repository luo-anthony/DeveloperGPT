"""
DeveloperGPT by luo-anthony
"""


import tiktoken


def check_reduce_context(
    messages: list, token_limit: int, model: str, ctx_removal_index: int
) -> tuple[list, int]:
    """Check if token limit is exceeded and remove old context starting at ctx_removal_index if so."""
    n_tokens = count_msg_tokens(messages, model)
    if n_tokens > token_limit:
        messages, n_tokens = remove_old_contexts(
            messages, token_limit, n_tokens, model, ctx_removal_index
        )
    return messages, n_tokens


"""
count_msg_tokens function adapted from: https://github.com/openai/openai-cookbook/blob/main/examples/How_to_count_tokens_with_tiktoken.ipynb
"""


def count_msg_tokens(messages: list, model: str) -> int:
    """Returns the approximate number of tokens used by a list of messages"""
    try:
        encoding = tiktoken.encoding_for_model(model)
    except KeyError:
        # print("Warning: model not found. Using cl100k_base encoding.")
        encoding = tiktoken.get_encoding("cl100k_base")
    if model == "gpt-3.5-turbo":
        # print(
        #     "Warning: gpt-3.5-turbo may change over time. Returning num tokens assuming gpt-3.5-turbo-0301."
        # )
        return count_msg_tokens(messages, model="gpt-3.5-turbo-0301")
    elif model == "gpt-4":
        # print(
        #     "Warning: gpt-4 may change over time. Returning num tokens assuming gpt-4-0314."
        # )
        return count_msg_tokens(messages, model="gpt-4-0314")
    elif model == "gpt-3.5-turbo-0301":
        tokens_per_message = (
            4  # every message follows <|start|>{role/name}\n{content}<|end|>\n
        )
        tokens_per_name = -1  # if there's a name, the role is omitted
    elif model == "gpt-4-0314":
        tokens_per_message = 3
        tokens_per_name = 1
    else:
        raise NotImplementedError(
            f"""num_tokens_from_messages() is not implemented for model {model}. See https://github.com/openai/openai-python/blob/main/chatml.md for information on how messages are converted to tokens."""
        )
    num_tokens = 0
    for message in messages:
        num_tokens += tokens_per_message
        for key, value in message.items():
            num_tokens += len(encoding.encode(value))
            if key == "name":
                num_tokens += tokens_per_name
    num_tokens += 3  # every reply is primed with <|start|>assistant<|message|>
    return num_tokens


def remove_old_contexts(
    messages: list, token_limit: int, n_tokens: int, model: str, ctx_removal_index: int
) -> tuple[list, int]:
    """Remove old contexts until token limit is not exceeded."""
    while n_tokens > token_limit:
        removed_ctx = messages.pop(ctx_removal_index)
        n_removed = count_msg_tokens([removed_ctx], model)
        n_tokens -= n_removed

    return messages, n_tokens
