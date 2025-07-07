library(dotenv)
library(ellmer)

chat <- chat_openai(
  model = "claude-sonnet-4-20250514",
  system_prompt = "You are a terse assistant.",
)
chat$chat("What is the capital of the moon?")

chat$chat("Are you sure about that?")
