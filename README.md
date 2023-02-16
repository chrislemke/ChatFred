![chatfred](assets/images/chatfred.png)

# ChatFred
**[Alfred](https://www.alfredapp.com/) workflow using [OpenAI's](https://openai.com/) GPT model for chatting, text completion and much more 🤖**

## Setup 🛠️
Just install the workflow and add your OpenAI API key. If you have used ChatGPT, you already have an OpenAI account. Otherwise, you can [sign up here](https://beta.openai.com/signup) - You will receive $18 in free credit, no payment data is required. Then you can [create an API key](https://beta.openai.com/account/api-keys).

## Usage 🧑‍💻
To start the ChatFred workflow, just type ***cf*** or configure your own hotkey.

Ask questions:
![Screenshot](assets/images/screenshot1.png)

Translate text:
![Screenshot](assets/images/screenshot2.png)

If the reply is a bit longer just hit <kbd>CMD ⌘</kbd> + <kbd>RETURN ⏎</kbd>:
![Screenshot](assets/images/screenshot3.png)
![Screenshot](assets/images/screenshot4.png)

### Options 🤗
To handle the reply of ChatFred you have the following options.
- <kbd>CMD ⌘</kbd>: Show the reply in large text (can be combined with <kbd>CTRL ⌃</kbd>)
- <kbd>OPTION ⌥</kbd>: Let ChatFred speak 🗣️
- <kbd>CTRL ⌃</kbd>: Copy the reply to the clipboard
- <kbd>SHIFT ⇧</kbd>: Write the conversation to file: `ChatFred.txt`. The default location is the user's home directory (`~/`). You can change the location in the workflow configuration.

### Save conversations to file 📝
If you want to save all requests and ChatFred's replies to a file, you can enable this option in the workflow configuration (*Always save conversation to file*). The default location is the user's home directory (`~/`) but can be changed (*File directory*).

You can also hit <kbd>SHIFT ⇧</kbd> + <kbd>RETURN ⏎</kbd> for saving the reply manually.

Here is an example of the saved reply:
```
- 16. Feb 2023, 07:12:00 -
Request:
 What is Star Wars?

Reply:
 Star Wars is a science fiction media franchise created by George Lucas.
 It includes films, television series, books, comics, video games, and other merchandise.
 The franchise began with the eponymous 1977 film and quickly became a worldwide pop-culture phenomenon.
---
```
### Examples 📚
GTP-3 is a very powerful model. It can answer questions, write stories, and even write code. You can find more examples [here](https://platform.openai.com/examples).

## Tweaking the workflow (optional) 🦾
You can tweak the workflow to your liking. The following parameters are available. Simply adjust them in the workflow configuration.
- **OpenAI model**: Following models are available: `Ada`, `Babbage`, `Curie`, `Davinci` (ascending quality). Default: `Davinci`.
- **Temperature**: The temperature determines how greedy the generative model is. If the temperature is high, the model can output words other than the highest probability with a fairly high probability. The generated text will be more diverse, but there is a higher probability of grammar errors and the generation of nonsense. Default: `0`.
- **Maximum tokens**: The maximum number of tokens to generate in the completion. Default: `50`.
- **Top-p**: Top-p sampling selects from the smallest possible set of words whose cumulative probability exceeds probability p. In this way, the number of words in the set can be dynamically increased and decreased according to the nearest word probability distribution. Default: `1`.
- **Frequency penalty**: A value between `-2.0` and `2.0`. The frequency penalty parameter controls the model’s tendency to repeat predictions. Default: `0`.
- **Presence penalty**: A Value between `-2.0` and `2.0`. The presence penalty parameter encourages the model to make novel predictions. Default: `0`.
- **Always read out reply**: If enabled, ChatFred will read out all replies automatically. Default: `off`.
- **Always save conversation to file**: If enabled, all your request and ChatFred's replies will automatically be saved to a file (`{File directory}/ChatFred.txt`). Default: `off`.
- **File directory**: Custom directory where the 'ChatFred.txt' should be stored. Default to the user's home directory (`~/`).
- **Always copy to clipboard**: If enabled, all of ChatFred's replies will be copied to the clipboard automatically. Default: `off`.

 You can find more information about the model's parameters [here](https://platform.openai.com/docs/api-reference/completions/create).

## What's next? 🚧
As soon as OpenAI releases a ChatGPT API, I will integrate it into this workflow. Soon we will also implement the [Microsoft Azure OpenAI Service](https://learn.microsoft.com/en-us/azure/cognitive-services/openai/) to provide a broader choice of available services.
