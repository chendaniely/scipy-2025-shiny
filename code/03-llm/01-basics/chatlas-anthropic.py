from chatlas import ChatAnthropic
from dotenv import load_dotenv

load_dotenv()

chat = ChatAnthropic(model="claude-3-7-sonnet-latest", system_prompt="You are a terse assistant.")

chat.chat("What is the capital of the moon?")

chat.chat("Are you sure?")
