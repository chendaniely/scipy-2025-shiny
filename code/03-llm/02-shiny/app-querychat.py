import querychat
from chatlas import ChatAnthropic
from seaborn import load_dataset
from shiny.express import render

# data -----
titanic = load_dataset("titanic")

# chatbot setup -----
def create_chat_callback(system_prompt):
    return ChatAnthropic(system_prompt=system_prompt)


querychat_config = querychat.init(
    titanic,
    "titanic",
    greeting="""Hello! I'm here to help you explore the Titanic dataset.""",
    create_chat_callback=create_chat_callback,
)

chat = querychat.server("chat", querychat_config)

# shiny application -----

# querychat UI
querychat.sidebar("chat")

# querychat filtered dataframe
@render.data_frame
def data_table():
    return chat["df"]()
