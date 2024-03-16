# Imports
import json
from datetime import date, datetime
from pathlib import Path
from random import getrandbits

import requests
from cltl.brain.long_term_memory import LongTermMemory
from cltl.brain.utils.helper_functions import brain_response_to_json
from cltl.entity_linking.label_linker import LabelBasedLinker
from cltl.triple_extraction.api import Chat
from cltl.triple_extraction.cfg_analyzer import CFGAnalyzer
# from cltl.triple_extraction.spacy_analyzer import spacyAnalyzer
from cltl.triple_extraction.utils.helper_functions import utterance_to_capsules
from tqdm import tqdm

import logging

from cltl.brain import logger as brain_logger

from cltl.triple_extraction import logger as chat_logger

from openai import OpenAI
from openai.types.beta.threads import ThreadMessage
from typing import List
import time

class User(object):
    def __init__(
        self,
        idx: str,
        name: str,
        likes = List[str],
        dislikes = List[str],
    ):
        self.idx = idx
        self.name = name
        self.likes = likes
        self.dislikes = dislikes

    def get_likes(self) -> List[str]:
        # query to brain as knowledge graph
        return ', '.join(self.likes)
    
    def get_dislikes(self) -> List[str]:
        #query to brain as knowledge graph
        return ', '.join(self.dislikes)

def format_message(message: ThreadMessage) -> str:
    """
    Returns a formatted version of a message.
    """
    lines = [c.text.value.strip() for c in message.content]
    lines = [l.replace("\n\n", "\n") for l in lines if l != ""]
    text_content = "\n".join(lines)
    return f"{message.role}: {text_content}"


# Create OpenAI client
client = OpenAI()

coach_instructions = "You are a personal diabetes coach. Give healthy and diabetes-proof suggestions to patients and incorporate their preferences. Be brief and limit the advice given."

# First instantiate the assistant
assistant = client.beta.assistants.create(
    name="Diabetes coach",
    instructions=coach_instructions,
    model="gpt-3.5-turbo"
)

# Then instantiate a longer running conversation -- called thread in openai
thread = client.beta.threads.create()

# Instantiate the user
larry = User(
    idx="42",
    name="Larry",
    # should be query from brain/knowledge graph
    likes=['smoking', 'eating',],
    dislikes=['excercise', 'monitoring blood sugar', 'sleeping normal hours']
)
funnyxxx = User(
    idx="42",
    name="Funnyxxx",
    # should be query from brain/knowledge graph
    likes=['',],
    dislikes=['']
)

user_prompt = ""
while "bye" not in user_prompt.lower():
    # Input 1. I'd like to bake something. Can you give me a recipe?
    # Input 2. Looks like too much of a hassle. How about some other nice activity to do while its raining?
    # Input 3. Sounds like a great plan. Bye now!
    user_prompt = input("> ")
    message = client.beta.threads.messages.create(
        thread_id=thread.id,
        role="user",
        content=user_prompt,

    )

    # Create a single conversation -- called a run in openai.
    # We can inject preferences into the instructions here.
    user = funnyxxx
    likes = ''.join(user.get_likes())
    coach_instructions += f"Address the user as {user.name} and incorporate the users' preferences. If these are not known, ask for them."
    if len(user.get_likes()) == 0:
        coach_instructions += "It is not known what the user likes."
    else:
        coach_instructions += f"The user likes :{''.join(user.get_likes())}"
    if len(user.get_dislikes()) == 0:
        coach_instructions += "It is not known what the user dislikes."
    else:
        coach_instructions += f"The user dislikes :{''.join(user.get_dislikes())}"

    run = client.beta.threads.runs.create(
        thread_id=thread.id,
        assistant_id=assistant.id,
        instructions=coach_instructions
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
