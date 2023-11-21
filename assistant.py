from datetime import datetime
import os
import time
from dotenv import load_dotenv
from openai import OpenAI

from config import PROCESSED_DATA_DIRECTORY

load_dotenv()
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

openai = OpenAI(api_key=OPENAI_API_KEY)


class Assistant:
    def __init__(self, personality: str):
        self.assistant_with_files = self.create_assistant(personality)
        self.thread = self.create_thread()

    def create_assistant(self, personality: str):
        file_ids = []
        for filename in os.listdir(PROCESSED_DATA_DIRECTORY):
            file_path = os.path.join(PROCESSED_DATA_DIRECTORY, filename)
            if os.path.isfile(file_path):
                file = openai.files.create(
                    file=open(file_path, "rb"),
                    purpose='assistants'
                )
                file_ids.append(file.id)

        print("Creating assistant with file_ids: ", file_ids)
        assistant = openai.beta.assistants.create(
            instructions=f"""Have a conversation with a human, answering the 
                following as best you can and try to use a tool to help. 
                You have access to the following tools: 
                Focused Labs QA-useful for when you need to answer
                questions about Focused Labs. If you don't know the 
                answer don't make one up, just say "Hmm, I'm not sure 
                please contact work@focusedlabs.io for further assistance."
                Answer questions from the perspective of a {personality}""",
            model="gpt-4-1106-preview",
            tools=[{"type": "retrieval"}],
            file_ids=file_ids
        )
        return assistant

    def create_thread(self):
        print("Creating thread")
        return openai.beta.threads.create()

    def add_user_question(self, user_question):
        print("Adding user question")
        openai.beta.threads.messages.create(thread_id=self.thread.id, role="user", content=user_question)

    def do_run(self):
        print("Doing run")
        return openai.beta.threads.runs.create(
            thread_id=self.thread.id,
            assistant_id=self.assistant_with_files.id
        )

    def get_run_status(self, run):
        print("Getting run status")
        return openai.beta.threads.runs.retrieve(thread_id=self.thread.id, run_id=run.id)

    def get_message(self, run):
        print("Getting message")
        messages = openai.beta.threads.messages.list(self.thread.id)
        print("All messages: ", messages)
        filtered_messages = [message for message in messages.data if
                             message.role == 'assistant' and message.run_id == run.id]
        print("Filtered messages: ", filtered_messages)
        last_message = filtered_messages[-1] if filtered_messages else None
        print("Last message: ", last_message)
        return last_message.content[0].text.value

    def process_question(self, question: str, in_new_thread: bool):
        # Timestamp in UTC
        timestamp = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
        error_message = ""

        try:
            if in_new_thread:
                self.thread = self.create_thread()

            self.add_user_question(question)
            run = self.do_run()
            run_status = self.get_run_status(run)

            while run_status.status not in ["completed", "failed"]:
                print(f"Current status: {run_status.status}")
                time.sleep(2)
                run_status = self.get_run_status(run)

            if run_status.status == "failed":
                timestamp = run_status.failed_at
                error_message = run_status.last_error.message

            if run_status.status == "completed":
                message = self.get_message(run)
            else:
                message = ""

            return timestamp, question, message, error_message

        except Exception as e:
            error_message = str(e)
            return timestamp, question, "", error_message
