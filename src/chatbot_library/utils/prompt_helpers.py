def clear_and_direct(instruction: str, context: str) -> str:
    """
    Provide clear instructions and context to guide Claude's responses.

    Args:
        instruction (str): The clear instruction for Claude.
        context (str): The context to guide Claude's response.

    Returns:
        str: The formatted prompt with clear instructions and context.
    """
    return f"{instruction}\n\nContext: {context}"


def use_examples(prompt: str, examples: list) -> str:
    """
    Include examples in the prompt to illustrate the desired output format or style.

    Args:
        prompt (str): The main prompt or question.
        examples (list): A list of examples to include in the prompt.

    Returns:
        str: The formatted prompt with examples.
    """
    examples_str = "\n".join(examples)
    return f"{prompt}\n\nExamples:\n{examples_str}"


def give_claude_role(prompt: str, role: str) -> str:
    """
    Prime Claude to inhabit a specific role in order to increase performance for the use case.

    Args:
        prompt (str): The main prompt or question.
        role (str): The role for Claude to inhabit (e.g., expert, advisor, etc.).

    Returns:
        str: The formatted prompt with the specified role.
    """
    return f"You are an {role}.\n\n{prompt}"


def use_xml_tags(prompt: str, input_tag: str, output_tag: str) -> str:
    """
    Incorporate XML tags to structure prompts and responses for greater clarity.

    Args:
        prompt (str): The main prompt or question.
        input_tag (str): The XML tag for the input or prompt.
        output_tag (str): The XML tag for the desired output or response.

    Returns:
        str: The formatted prompt with XML tags.
    """
    return f"<{input_tag}>{prompt}</{input_tag}>\n<{output_tag}>"


def chain_prompts(prompts: list) -> str:
    """
    Divide complex tasks into smaller, manageable steps for better results.

    Args:
        prompts (list): A list of prompts representing the steps in the task.

    Returns:
        str: The chained prompts as a single string.
    """
    chained_prompt = "\n\n".join(prompts)
    return chained_prompt


def let_claude_think(prompt: str) -> str:
    """
    Encourage step-by-step thinking to improve the quality of Claude's output.

    Args:
        prompt (str): The main prompt or question.

    Returns:
        str: The formatted prompt encouraging step-by-step thinking.
    """
    return f"{prompt}\n\nThink through this step-by-step:"


def prefill_response(prompt: str, prefill_text: str) -> str:
    """
    Start Claude's response with a few words to guide its output in the desired direction.

    Args:
        prompt (str): The main prompt or question.
        prefill_text (str): The initial text to prefill Claude's response.

    Returns:
        str: The formatted prompt with the prefilled response.
    """
    return f"{prompt}\n\nResponse: {prefill_text}"


def control_output_format(prompt: str, output_format: str) -> str:
    """
    Specify the desired output format to ensure consistency and readability.

    Args:
        prompt (str): The main prompt or question.
        output_format (str): The desired output format (e.g., bullet points, numbered list, etc.).

    Returns:
        str: The formatted prompt specifying the output format.
    """
    return f"{prompt}\n\nOutput format: {output_format}"


def rewrite_with_rubric(prompt: str, rubric: dict) -> str:
    """
    Request revisions based on a rubric to get Claude to iterate and improve its output.

    Args:
        prompt (str): The main prompt or question.
        rubric (dict): A dictionary representing the rubric for rewriting. The keys are the criteria,
                       and the values are the descriptions or requirements for each criterion.

    Returns:
        str: The formatted prompt with the rewriting rubric.
    """
    rubric_str = "\n".join(
        f"- {criterion}: {description}" for criterion, description in rubric.items()
    )
    return f"{prompt}\n\nPlease rewrite the response based on the following rubric:\n{rubric_str}"


def optimize_long_context(prompt: str, context: str) -> str:
    """
    Optimize prompts that take advantage of Claude's longer context windows.

    Args:
        prompt (str): The main prompt or question.
        context (str): The longer context to provide additional information.

    Returns:
        str: The formatted prompt optimized for longer context windows.
    """
    return f"Context: {context}\n\n{prompt}"
