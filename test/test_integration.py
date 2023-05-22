"""Integration test for google-image-search plugin."""
from steamship import Steamship
import api

PLUGIN_HANDLE = "google-image-search"


def test_run():

    test_cases = [
        ("Abraham Lincoln"),
        ("moon landing"),
        ("the first president of the United States"),
    ]

    with Steamship.temporary_workspace() as client:
        search = client.use_plugin(PLUGIN_HANDLE)

        for test_case in test_cases:
            task = search.tag(doc=test_case[0])
            task.wait()
            file = task.output.file
            assert file is not None
            assert file.blocks is not None
            assert len(file.blocks) == 1
            assert len(file.blocks[0].tags) == 1
            tag = file.blocks[0].tags[0]
            assert tag.kind == api.TAG_KIND
            assert tag.name == api.TAG_NAME
            
            data = file.blocks[0].raw()
            assert data
