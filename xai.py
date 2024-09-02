import sys
import os
import json
from openai import OpenAI
import pyperclip
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

client = OpenAI(api_key=os.getenv('API_KEY'))

class Config:
    def __init__(self, file_path='xai.json'):
        self.file_path = file_path
        self.data = self.load()

    def load(self):
        """Load the configuration from the JSON file."""
        try:
            with open(self.file_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {}

    def save(self):
        """Save the current configuration to the JSON file."""
        with open(self.file_path, 'w') as f:
            json.dump(self.data, f, indent=4)

    def get(self, key, default=None):
        """Get a value from the configuration."""
        return self.data.get(key, default)

    def set(self, key, value):
        """Set a value in the configuration and save it."""
        self.data[key] = value
        self.save()

    def validate(self):
        """Validate the necessary fields in the configuration."""
        if not self.data or 'assistant_id' not in self.data or 'os' not in self.data or 'model' not in self.data:
            raise Exception("Please run xai --setup")

class Assistant:
    def __init__(self, config):
        self.config = config
        self.id = config.get('assistant_id')
        self.name = f"xai-{config.get('os')}-{config.get('model')}"
        self.model = config.get('model')
        self.instructions = self._get_instructions()

    def _get_instructions(self):
        """Set instructions based on the OS type from the config."""
        os_type = self.config.get('os')
        return f"you will receive instructions for performing a specific task. your job is to respond with a command that can be copy-pasted directly into a {os_type} shell to be executed. you should respond just with the command in plain text format without markdown."

    def create_assistant(self):
        """Creates an assistant and saves the assistant ID to the config."""
        xai = client.beta.assistants.create(
            instructions=self.instructions,
            name=self.name,
            model=self.model,
        )
        self.id = xai.id
        self.config.set('assistant_id', self.id)
        return self

    def get_assistant(self):
        """Returns the assistant ID if it exists, otherwise creates a new assistant and returns the ID."""
        if self.id is not None:
            return self

        existing_assistant = self.find_existing_assistant()
        if existing_assistant:
            self.id = existing_assistant.id
            self.config.set('assistant_id', self.id)
            return self
        
        return self.create_assistant()

    def find_existing_assistant(self):
        """Searches for an existing assistant by name."""
        existing = client.beta.assistants.list()
        for assistant in existing.data:
            if assistant.name == self.name:
                return assistant
        return None

def query_openai(prompt, config):
    try:
        thread = client.beta.threads.create()
        client.beta.threads.messages.create(
          thread.id,
          role="user",
          content=prompt,
        )
        assistant_id = Assistant(config).get_assistant().id
        run = client.beta.threads.runs.create_and_poll(
          thread_id=thread.id,
          assistant_id=assistant_id,
        )
        if run.status == 'completed': 
            messages = client.beta.threads.messages.list(
                thread_id=thread.id
            )
            return messages.data[0].content[0].text.value
        else:
            print(run.status)
    except Exception as e:
        return f"An error occurred: {e}"

def setup(config):
    print('===============================')
    print("Welcome to xai setup!")
    print('===============================')
    config.set('os', 'Linux' if sys.platform in ["linux", "linux2"] else 'macOS')

    model = input("Please choose a model (leave empty for gpt-4o): ")
    if not model:
        model = "gpt-4o"
    config.set('model', model)

    # Create assistant
    print('Getting assistant with model:', model)
    assistant = Assistant(config).get_assistant()
    print('Setup completed successfully!')
    print('')
    print(f'Current configuration:')
    print('-------------------------------')
    print(f'Operating System: {config.get("os")}')
    print(f'Assistant ID: {assistant.id}')
    print(f'Assistant Name: {assistant.name}')
    print(f'Assistant Model: {config.get("model")}')
    print('-------------------------------')
    print('')
    print('To get started, make any request to XAI.')
    print('Example: xai make post request')
    sys.exit(0)

if __name__ == "__main__":
    config = Config('xai.json')

    if len(sys.argv) == 2 and sys.argv[1] == "--setup":
        setup(config)

    try:
        config.validate()
    except Exception as e:
        print(e)
        sys.exit(1)

    query = " ".join(sys.argv[1:])
    if not query:
        print("Please provide a prompt.")
        sys.exit(1)
    
    response = query_openai(query, config)
    print(response)
    # Copy response to clipboard
    pyperclip.copy(response)
