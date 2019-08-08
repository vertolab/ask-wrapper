# A Python wrapper for [ask-cli](https://developer.amazon.com/docs/smapi/quick-start-alexa-skills-kit-command-line-interface.html)

## Prerequisites
### [ASK CLI](https://developer.amazon.com/docs/smapi/quick-start-alexa-skills-kit-command-line-interface.html#install-initialize)
* `npm install -g ask-cli`
* `ask init`
### `ask-wrapper`
* `pip install "git+git://github.com/vertolab/ask-wrapper.git"`
## Examples
### List all skills
    from ask_wrapper import ASKApi
    print(ASKApi().list_skills())
