#!/usr/bin/env python3

import anthropic
from src.model.chatbots import AnthropicChatbot, OpenAIChatbot
from src.model.conversation_manager import Conversation, ConversationManager
from src.utils.prompt_helpers import (
    clear_and_direct,
    use_examples,
    give_claude_role,
    use_xml_tags,
    chain_prompts,
    let_claude_think,
    prefill_response,
    control_output_format,
    rewrite_with_rubric,
    optimize_long_context,
)

anthropic = anthropic.Client()


def display_conversations(conversations, start_index):
    for i, conversation in enumerate(
        conversations[start_index : start_index + 10], start=start_index + 1
    ):
        print(f"{i}. {conversation.title}")


def select_conversation(conversations) -> Conversation | None:
    total_conversations = len(conversations)
    start_index = 0

    while True:
        print("Select a conversation:")
        display_conversations(conversations, start_index)

        if total_conversations > 10:
            print("p. Previous")
            print("n. Next")

        print("b. Back")
        choice = input("Enter your choice: ")

        if choice == "p" and start_index > 0:
            start_index -= 10
        elif choice == "n" and start_index + 10 < total_conversations:
            start_index += 10
        elif choice == "b":
            return None
        else:
            try:
                index = int(choice) - 1
                if 0 <= index < total_conversations:
                    return conversations[index]
                else:
                    print("Invalid choice. Please try again.")
            except ValueError:
                print("Invalid choice. Please try again.")


def display_conversation_history(conversation: Conversation):
    for i, branch in enumerate(conversation.branches, start=1):
        print(f"Branch {i}:")
        for j, message in enumerate(branch.messages, start=1):
            print(f"{j}. User: {message.text}")
            if message.response:
                print(f"   Assistant: {message.response}")
        print()


def select_message_to_edit(conversation: Conversation):
    display_conversation_history(conversation)
    branch_index = int(input("Enter the branch number: ")) - 1
    message_index = int(input("Enter the message number to edit: ")) - 1
    return conversation.branches[branch_index].messages[message_index]


def select_branch(conversation: Conversation):
    total_branches = len(conversation.branches)
    print(f"Total branches: {total_branches}")
    if total_branches == 1:
        return conversation.branches[0]

    while True:
        print("Select a branch:")
        for i, branch in enumerate(conversation.branches, start=1):
            print(f"{i}. Branch {branch.id}")

        print("b. Back")
        choice = input("Enter your choice: ")

        if choice.lower() == "b":
            return None
        else:
            try:
                index = int(choice) - 1
                if 0 <= index < total_branches:
                    return conversation.branches[index]
                else:
                    print("Invalid choice. Please try again.")
            except ValueError:
                print("Invalid choice. Please try again.")


def main():
    # Initialize chatbot and conversation manager
    chatbot = AnthropicChatbot(client=anthropic)  # Replace with your chatbot instance
    conversation_manager = ConversationManager(chatbot, data_dir="data/conversations")

    while True:
        # Display main menu
        print("LLM Playground")
        print("1. Send a message")
        print("2. Create a new branch")
        print("3. Create a new conversation")
        print("4. List conversations")
        print("5. Use prompt helpers")
        print("6. Exit")

        choice = input("Enter your choice: ")

        if choice == "1":
            # Send a message
            conversation_manager.load_conversations()
            conversation = select_conversation(conversation_manager.conversations)
            if conversation:
                branch = select_branch(conversation)
                if branch:
                    message = input("Enter your message: ")
                    response = conversation_manager.add_message(
                        conversation.id, branch.id, "user", message
                    )
                    if response.response:
                        print("Assistant:", response.response.text)
                    else:
                        print(
                            f"Error getting response from assistant. full response: {response}"
                        )

        elif choice == "2":
            # Create a new branch
            conversation = select_conversation(conversation_manager.conversations)
            if conversation:
                parent_branch_id = input("Enter parent branch ID (optional): ")
                branch = conversation_manager.create_branch(
                    conversation.id, parent_branch_id
                )
                print(f"New branch created with ID: {branch.id}")

        elif choice == "3":
            # Create a new conversation
            conversation_title = input("Enter conversation title: ")
            conversation = conversation_manager.create_conversation(
                conversation_title, conversation_title
            )
            print(f"New conversation created with ID: {conversation.id}")

        elif choice == "4":
            # List conversations
            conversation_manager.load_conversations()
            print("Conversations:")
            for conversation in conversation_manager.conversations:
                print(f"- {conversation.id}: {conversation.title}")

        elif choice == "5":
            # Use prompt helpers
            print("Prompt Helpers")
            print("1. Clear and direct")
            print("2. Use examples")
            print("3. Give Claude a role")
            print("4. Use XML tags")
            print("5. Chain prompts")
            print("6. Let Claude think")
            print("7. Prefill response")
            print("8. Control output format")
            print("9. Rewrite with rubric")
            print("10. Optimize long context")

            helper_choice = input("Enter your choice: ")

            if helper_choice == "1":
                prompt = input("Enter prompt: ")
                context = input("Enter context: ")
                modified_prompt = clear_and_direct(prompt, context)
                print("Modified prompt:", modified_prompt)

            elif helper_choice == "2":
                prompt = input("Enter prompt: ")
                examples = []
                while True:
                    example = input("Enter an example (or press Enter to finish): ")
                    if example:
                        examples.append(example)
                    else:
                        break
                modified_prompt = use_examples(prompt, examples)
                print("Modified prompt:", modified_prompt)

            elif helper_choice == "3":
                prompt = input("Enter prompt: ")
                role = input("Enter role: ")
                modified_prompt = give_claude_role(prompt, role)
                print("Modified prompt:", modified_prompt)

            elif helper_choice == "4":
                prompt = input("Enter prompt: ")
                input_tag = input("Enter input tag: ")
                output_tag = input("Enter output tag: ")
                modified_prompt = use_xml_tags(prompt, input_tag, output_tag)
                print("Modified prompt:", modified_prompt)

            elif helper_choice == "5":
                prompts = []
                while True:
                    prompt = input("Enter a prompt (or press Enter to finish): ")
                    if prompt:
                        prompts.append(prompt)
                    else:
                        break
                modified_prompt = chain_prompts(prompts)
                print("Modified prompt:", modified_prompt)

            elif helper_choice == "6":
                prompt = input("Enter prompt: ")
                modified_prompt = let_claude_think(prompt)
                print("Modified prompt:", modified_prompt)

            elif helper_choice == "7":
                prompt = input("Enter prompt: ")
                prefill_text = input("Enter prefill text: ")
                modified_prompt = prefill_response(prompt, prefill_text)
                print("Modified prompt:", modified_prompt)

            elif helper_choice == "8":
                prompt = input("Enter prompt: ")
                output_format = input("Enter output format: ")
                modified_prompt = control_output_format(prompt, output_format)
                print("Modified prompt:", modified_prompt)

            elif helper_choice == "9":
                prompt = input("Enter prompt: ")
                rubric = {}
                while True:
                    criterion = input(
                        "Enter a rubric criterion (or press Enter to finish): "
                    )
                    if criterion:
                        description = input("Enter criterion description: ")
                        rubric[criterion] = description
                    else:
                        break
                modified_prompt = rewrite_with_rubric(prompt, rubric)
                print("Modified prompt:", modified_prompt)

            elif helper_choice == "10":
                prompt = input("Enter prompt: ")
                context = input("Enter long context: ")
                modified_prompt = optimize_long_context(prompt, context)
                print("Modified prompt:", modified_prompt)

        elif choice == "6":
            # Exit the application
            print("Exiting...")
            break

        else:
            print("Invalid choice. Please try again.")


if __name__ == "__main__":
    main()
