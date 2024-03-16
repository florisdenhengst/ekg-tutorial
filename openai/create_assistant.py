from openai import OpenAI
client = OpenAI()

def get_user_preferences(user_id: int):
    """
    A mock function that returns the preferences of the user.
    """
    return None

user = {
    "id": 42,
    "name": "Floris",

}
function = {
    "name": "get_user_preferences",
    "description": "A function that returns the users' preferences",
    "parameters": {
        "type": "object",
        "properties": {
            "user_id": {"type": "integer", "description": "the identifier of the current user"},
        },
        "required": ["user_id"],
    }
}

assistant = client.beta.assistants.create(
    name="Diabetes coach",
    instructions="You are a personal diabetes coach. Give healthy and diabetes-proof suggestions to patients and incorporate their preferences.",
    tools=[{"type": "function", "function": function,}],
    model="gpt-3.5-turbo"
)

thread = client.beta.threads.create()


message = client.beta.threads.messages.create(
    thread_id=thread.id,
    role="user",
    content="I like baking cakes. Can you give me a recipe?"
)

# create a new dialog. We can inject preferences into the instructions here.
run = client.beta.threads.runs.create(
  thread_id=thread.id,
  assistant_id=assistant.id,
  instructions=f"Address the user as {user['name']} and incorporate the users' preferences."
)

run = client.beta.threads.runs.retrieve(
  thread_id=thread.id,
  run_id=run.id
)

messages = client.beta.threads.messages.list(
  thread_id=thread.id
)

[m.content for m in messages]

run = client.beta.threads.runs.retrieve(
  thread_id=thread.id,
  run_id=run.id
)

client.beta.threads.messages.create(
    thread_id=thread.id,
    role="user",
    content="The kind does not matter, as long as it is very very sweet."
)

[m.content for m in messages]
