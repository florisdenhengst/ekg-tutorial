# Imports
from random import getrandbits
from openai import OpenAI
from openai.types.beta.threads import ThreadMessage
import time


def format_message(message: ThreadMessage) -> str:
    """
    Returns a formatted version of a message.
    """
    lines = [c.text.value.strip() for c in message.content]
    lines = [l.replace("\n\n", "\n") for l in lines if l != ""]
    text_content = "\n".join(lines)
    return f"{message.role}: {text_content}"

def multiline_input(prompt: str) -> str:
    """
    Reads input from stdin until an empty line is observed
    """
    user_input = ""
    print(prompt, end="")
    while True:
        line = input()
        if line == "":
            return user_input
        else:
            user_input += line + "\n"


# Create OpenAI client
client = OpenAI()

prompt_file = '../resources/dd_funnyxxx/prompt.txt'

with open(prompt_file) as f:
    impersonator_instructions = f.read()

# impersonator_instructions = f"For the duration of this conversation, assume the persona of a patient with type 2 diabetes. Your response should be consistent with the patients beliefs, values, experiences, the tone of voice, writing style of the following piece of text. {text}."

# First instantiate the assistant
assistant = client.beta.assistants.create(
    name="Patient simulator",
    instructions=impersonator_instructions,
    model="gpt-3.5-turbo"
)

# Then instantiate a longer running conversation -- called thread in openai
thread = client.beta.threads.create()

user_prompt = ""
while "bye" not in user_prompt.lower():
    # Input 1. Hi Floris! Since you enjoy gaming, why not consider trying out exergaming? It combines the fun of playing video games with physical activity. You can find various gaming consoles or fitness apps that offer interactive games specifically designed to get you moving and exercising. It's a great way to burn calories while having a good time!
    user_prompt = multiline_input("> ")
    message = client.beta.threads.messages.create(
        thread_id=thread.id,
        role="user",
        content=user_prompt,

    )

    # Create a single conversation -- called a run in openai.
    # We can inject preferences into the instructions here.
    run = client.beta.threads.runs.create(
        thread_id=thread.id,
        assistant_id=assistant.id,
    )

    # poll whether the run has completed 
    run = client.beta.threads.runs.retrieve(
        thread_id=thread.id,
        run_id=run.id
    )

    # ...wait until run.status == completed
    while(run.status != 'completed'):
        time.sleep(5)
        print(run.status)
        run = client.beta.threads.runs.retrieve(
            thread_id=thread.id,
            run_id=run.id
        )

    # retrieve all messages in the list
    messages = client.beta.threads.messages.list(
        thread_id=thread.id   
    )

    formatted_messages = [format_message(m) for m in messages]
    print(formatted_messages[0])