# Google Image Search Plugin

This project implements a basic Steamship Generator that images to queries using Google Image Search (via the SerpAPI).

## First Time Setup (to develop, not use, this plugin)

We recommend using Python virtual environments for development.
To set one up, run the following command from this directory:

```bash
python3 -m venv .venv
```

Activate your virtual environment by running:

```bash
source .venv/bin/activate
```

Your first time, install the required dependencies with:

```bash
python -m pip install -r requirements.dev.txt
python -m pip install -r requirements.txt
```

## Developing

All the code for this plugin is located in the `src/api.py` file.

## Testing

Tests are located in the `test/test_integration.py` file. You can run them with:

```bash
pytest
```

## Deploying

Deploy by running:

```bash
ship deploy
```

That will deploy your plugin to Steamship and register it as a plugin for use.

## Using

Once deployed, your Plugin can be referenced by the handle in your `steamship.json` file.

```python
from steamship import Steamship, Block, File, MimeTypes, Tag

MY_PLUGIN_HANDLE = "... fill this out ..."

with Steamship.temporary_workspace() as client:
    search = client.use_plugin(MY_PLUGIN_HANDLE)
    task = search.tag(doc="How old was Abraham Lincoln when he died?")
    task.wait()
    for block in task.output.file.blocks:
        for tag in block.tags:
            print(tag)
```

## Feedback

Questions, comments, suggestions, etc. are all welcome, either via hello@steamship.com or our [Discord](https://discord.gg/5Vry5ANVwT).

We would love take a look, hear your suggestions, help where we can, and share what you've made with the community.# google-image-search-generator
