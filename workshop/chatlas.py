from chatlas import ChatOpenAI
from dotenv import load_dotenv

chat = ChatOpenAI(model="gpt-4.1", system_prompt="You are a terse assistant.")

chat.chat("What is the capital of the moon?")

chat.chat("Are you sure?")
