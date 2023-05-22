"""Plugin to return Google Image Search images for queries using SerpAPI"""
from typing import Dict, Type, List

from serpapi import GoogleSearch
import requests
from steamship.invocable import Config, InvocableResponse, InvocationContext
from steamship.data.block import BlockUploadType
from steamship import Block, File, MimeTypes, SteamshipError, Tag
from steamship.invocable import Config, InvocableResponse
from steamship.plugin.inputs.raw_block_and_tag_plugin_input import RawBlockAndTagPluginInput
from steamship.plugin.outputs.raw_block_and_tag_plugin_output import RawBlockAndTagPluginOutput
from steamship.plugin.request import PluginRequest
from steamship.plugin.generator import Generator

# tag consts
TAG_KIND = "search-result"
TAG_NAME = "google-image-search"
SEARCH_ENGINE = "google"
NUM_IMAGES = 1

class GoogleImageSearchGeneratorConfig(Config):
    """Configures the Serp API."""

    serpapi_api_key: str = ""


class GoogleImageSearchGenerator(Generator):
    """Tags files based on search results of their content."""

    config: GoogleImageSearchGeneratorConfig

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        GoogleSearch.SERP_API_KEY = self.config.serpapi_api_key

    @classmethod
    def config_cls(cls) -> Type[Config]:
        """Return configuration template for the generator."""
        return GoogleImageSearchGeneratorConfig

    def run(
        self, request: PluginRequest[RawBlockAndTagPluginInput]
    ) -> InvocableResponse[RawBlockAndTagPluginOutput]:
        """For each block in the submitted file, submit a search query and retrieve the answer."""

        generated_blocks = []
        for block in request.data.blocks:
            if not block.text:
                continue

            params = {
                "engine": SEARCH_ENGINE,          # search engine. Google, Bing, Yahoo, Naver, Baidu...
                "q": block.text,                  # search query
                "tbm": "isch",                    # image results
                "num": f"{NUM_IMAGES * 3}",       # number of images per page, with a buffer in case of download failure
                "ijn": 0,                         # page number: 0 -> first page, 1 -> second...
            }

            search = GoogleSearch(params)

            try:
                for block in self._answer_from_search_results(search.get_dict()):
                    generated_blocks.append(block)
                    
            except ValueError as ve:
                raise SteamshipError(
                    str=f"Error executing search for {block.text}",
                    suggestion="Please try again if you feel this should have succeeded",
                    error=ve,
                )
        return InvocableResponse(data=RawBlockAndTagPluginOutput(blocks=generated_blocks))

    @staticmethod
    def _answer_from_search_results(search_result: Dict[str, str], k: int = 1) -> List[Block]:
        # borrows heavily from the implementation in:
        # https://github.com/hwchase17/langchain/blob/master/langchain/serpapi.py
        # which itself was borrowed from:
        # https://github.com/ofirpress/self-ask
        if "error" in search_result.keys():
            raise ValueError(f"Got error from SerpAPI: {search_result['error']}")

        ret = []
        already_seen = {}

        for image in search_result["images_results"]:
            image_url = image["original"]
            if image_url not in already_seen:
                already_seen[image_url] = True

                # We can't do the below method, though I'm preserving it, because
                # the engine doesn't include a User-Agent header, causing Wikipedia (a common google image
                # host) to reject the request.
                #  
                # ret.append(Block(
                #     url=image_url, 
                #     mime_type=MimeTypes.PNG, 
                #     upload_type=BlockUploadType.URL,
                #     tags=[
                #         Tag(
                #             kind=TAG_KIND,
                #             name=TAG_NAME
                #         )
                #     ]
                # ))
            
                headers = {'User-Agent': 'Steamship Browser v1'}
                response = requests.get(image_url, headers)
                if response.ok:
                    ret.append(Block(
                        upload_bytes=response.content, 
                        upload_type=BlockUploadType.FILE,
                        mime_type=MimeTypes.PNG, 
                        tags=[
                            Tag(
                                kind=TAG_KIND,
                                name=TAG_NAME
                            )
                        ]
                    ))

            # Exit if we've gathered the required number of images
            if len(ret) == k:
                return ret
        
        if len(ret):
            return ret
        
        raise ValueError(f"No image returned from SerpAPI.")