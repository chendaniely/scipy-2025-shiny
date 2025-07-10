# https://gist.github.com/wch/7a020ffa6c899e5d8143efcf82f47a92

library(shiny)
library(shinychat)
library(ellmer)
library(bslib)
library(dotenv)
library(promises)

# Define UI
ui <- page_fluid(
  tags$head(
    tags$style(HTML("

      shiny-chat-message[role='assistant']{
        padding: 0.5rem 1rem;
        border-radius: 1rem;
      }

      shiny-chat-message[role='assistant'][data-model='gpt-4o'].colored {
        background-color:rgb(204, 231, 224) !important;
      }
      shiny-chat-message[role='assistant'][data-model='gpt-4o'].colored shiny-markdown-stream p:first-child::before {
        content: 'gpt-4o: ';
      }
      shiny-chat-message[role='assistant'][data-model='gpt-4o-mini'].colored {
        background-color:rgb(241, 199, 202) !important;
      }
      shiny-chat-message[role='assistant'][data-model='gpt-4o-mini'].colored shiny-markdown-stream p:first-child::before {
        content: 'gpt-4o-mini: ';
      }
      shiny-chat-message[role='assistant'][data-model='claude-3-5-sonnet-latest'].colored {
        background-color:rgb(228, 216, 246) !important;
      }
      shiny-chat-message[role='assistant'][data-model='claude-3-5-sonnet-latest'].colored shiny-markdown-stream p:first-child::before {
        content: 'claude-3-5-sonnet-latest: ';
      }
      shiny-chat-message[role='assistant'][data-model='claude-3-5-haiku-latest'].colored {
        background-color:rgb(218, 230, 250) !important;
      }
      shiny-chat-message[role='assistant'][data-model='claude-3-5-haiku-latest'].colored shiny-markdown-stream p:first-child::before {
        content: 'claude-3-5-haiku-latest: ';
      }
    "))
  ),

  card(
    card_header(
      h2("20 Questions AI Game", class = "text-center"),
    ),

    # Add JavaScript for handling message coloring
    tags$script(HTML("
      // Handle setting model for latest message
      Shiny.addCustomMessageHandler('set_last_message_model', function(data) {
        const lastMessage = document.querySelector('shiny-chat-message[role=\"assistant\"]:last-child');
        if (lastMessage) {
          lastMessage.setAttribute('data-model', data.model);
          if (document.getElementById('show_details').checked) {
            updateMessageColors(true);
          }
        }
      });

      // Function to update message colors
      function updateMessageColors(enabled) {
        document.querySelectorAll('shiny-chat-message[role=\"assistant\"]').forEach(msg => {
          if (enabled) {
            msg.classList.add('colored');
          } else {
            msg.classList.remove('colored');
          }
        });
      }

      // Listen for checkbox changes
      $(document).on('change', '#show_details', function() {
        updateMessageColors(this.checked);
      });
    ")),

    # Chat interface
    chat_ui("chat"),
    div(
      style = "font-size: 0.8rem; width:min(680px, 100%); margin: 0 auto; display: flex; gap: 1rem; justify-content: flex-end;",
      fill = NA,
      checkboxInput("show_details", "Show conversation details", width = "auto")
    )
  ),

  conditionalPanel(
    "input.show_details === true",
    card(
      card_header(
        h2("Details", class = "text-center"),
      ),
      verbatimTextOutput("messages")
    )
  )
)

# Define server logic
server <- function(input, output, session) {
  # System prompt that instructs the AI how to play 20 questions
  system_prompt <- "You are playing the classic 20 Questions game with the user, but with reversed roles.
  In this game, YOU will think of something and the USER will ask yes/no questions to guess what it is.

  Rules:
  1. At the start, secretly choose a common object, animal, person, or place. Don't reveal what it is.
  2. Keep track of how many questions the user has asked (maximum 20).
  3. Start by explaining the game and telling the user you've thought of something.
  4. Answer the user's questions honestly with 'Yes', 'No', or a very brief clarification if needed.
  5. If the user guesses correctly before 20 questions, congratulate them and offer to play again.
  6. If they reach 20 questions without guessing correctly, reveal your answer and offer to play again.
  7. Be friendly, enthusiastic, and make the game fun!
  8. If the user asks to play again or start over, think of a new object.
  9. IMPORTANT: You are part of a team of AIs taking turns answering. Maintain continuity with previous answers.
  10. Read the conversation history carefully to understand what object was chosen and what questions were already asked.

  Begin by inviting the user to play the game."

  # Initialize both chat models
  chat_models <- list(
    chatlas::chat_openai(
      system_prompt = system_prompt,
      model = "gpt-4o"
    ),
    ellmer::chat_anthropic(
      system_prompt = system_prompt,
      model = "claude-3-5-sonnet-latest"
    ),
    ellmer::chat_openai(
      system_prompt = system_prompt,
      model = "gpt-4o-mini"
    ),
    ellmer::chat_anthropic(
      system_prompt = system_prompt,
      model = "claude-3-5-haiku-latest"
    )
  )

  chat_idx <- 1

  # Send initial message when the app starts
  chat_models[[chat_idx]]$set_turns(
    list(
      Turn(
        "assistant",
        contents = list(ContentText(
          "Let's play 20 questions! I will think of an object and you ask the questions."
        ))
      )
    )
  )

  # Append that same initial message to the chat UI
  chat_append(
    "chat",
    "Let's play 20 questions! I will think of an object and you ask the questions.",
    role = "assistant"
  )

  # All the messages
  all_messages <- reactiveVal(chat_models[[chat_idx]]$get_turns())

  # Handle user input
  observeEvent(input$chat_user_input, {
    current_chat <- chat_models[[chat_idx]]

    # Grab the chat history from the previously-used LLM chat object
    current_chat$set_turns(all_messages())

    stream <- current_chat$stream_async(input$chat_user_input)

    chat_append("chat", stream)$then(function() {
      all_messages(current_chat$get_turns())

      # Send message to client to set the model for the latest message
      session$sendCustomMessage(
        "set_last_message_model",
        list(model = current_chat$get_model())
      )

      # Increment the index and wrap around
      chat_idx <<- chat_idx %% length(chat_models) + 1
    })
  })

  output$messages <- renderText({
    msgs_simplified <- lapply(all_messages(), function(msg) {
      res <- list(
        role = msg@role,
        content = msg@contents[[1]]@text,
        model = msg@json$model
      )
      if (is.null(res$model)) {
        # Remove model if not present (will be the case for user messages)
        res$model <- NULL
      }
      res
    })

    jsonlite::toJSON(msgs_simplified, auto_unbox = TRUE, pretty = TRUE)
  })
}

# Run the application
shinyApp(ui = ui, server = server)
