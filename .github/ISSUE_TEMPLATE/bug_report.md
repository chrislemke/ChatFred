---
name: Bug report
about: Create a report to help us improve
title: ''
labels: bug
assignees: ''

---

I had a look at the [troubleshooting section](https://github.com/chrislemke/ChatFred#troubleshooting-%EF%B8%8F)
- [ ] Yes
- [ ] No

**Describe the bug**
A clear and concise description of what the bug is.

**To Reproduce**
Steps to reproduce the behavior:
1. Go to '...'
2. Click on '....'
3. Scroll down to '....'
4. See error

**Expected behavior**
A clear and concise description of what you expected to happen.

**Screenshots**
If applicable, add screenshots to help explain your problem.

**Alfred's debug log**
```
 VARIABLES:{
  always_copy_to_clipboard = "1"
  always_speak = "0"
  api_key = "sk-************************************************" # Removed for privacy
  cf_aliases = "joke=tell me a joke;"
  chat_gpt_model = "gpt-3.5-turbo"
  frequency_penalty = "0.0"
  history_length = "3"
  history_type = "search"
  image_size = "512"
  instruct_gpt_model = "text-davinci-003"
  jailbreak_prompt = ""
  max_tokens = ""
  presence_penalty = "0.0"
  save_to_file = "0"
  save_to_file_dir = "/Users/***" # Removed for privacy
  show_loading_indicator = "1"
  show_notifications = "1"
  temperature = "0"
  top_p = "1"
  transformation_prompt = "Write the text so that each letter is replaced by its successor in the alphabet."
  user_prompt = "why are errors bad?"
}
RESPONSE:'Errors are often considered bad because they can lead to negative consequences in various aspects of life.'
```

**Relevant information from the `ChatFred_Error.log` file**
```
Date/Time: 2023-01-01 12:30:07.000000
model: gpt-3.5-turbo
workflow_version: 1.2.0
error_message: Incorrect API key provided: sk-44******************************************PEG2.   You can find your API key at https://platform.openai.com/account/api-keys.
user_prompt: Why do birds fly?
temperature: 0.0
max_tokens: None
top_p: 1
frequency_penalty: 0.0
presence_penalty: 0.0
```

**Additional context**
Add any other context about the problem here.
