import os
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP
from xdk import Client as XClient

load_dotenv()

mcp = FastMCP('xcp', host='0.0.0.0', port=8000)
xclient = XClient(bearer_token=os.getenv('X_BEARER_TOKEN') or '')

@mcp.tool()
def get_post_by_url(url: str) -> dict:
    """Get post text and media by post URL (e.g. https://x.com/i/status/123 or https://x.com/user/status/123)"""
    post_id = url.rstrip('/').split('/')[-1]
    post = xclient.posts.get_by_id(
        post_id,
        tweet_fields=['attachments', 'author_id', 'created_at', 'text'],
        expansions=['attachments.media_keys'],
        media_fields=['url', 'preview_image_url', 'type', 'width', 'height'],
    )

    dumped = post.model_dump()
    data = dumped.get('data') or {}
    includes = dumped.get('includes') or {}
    media_list = includes.get('media') or []

    return {
        'id': data.get('id'),
        'text': data.get('text'),
        'author_id': data.get('author_id'),
        'created_at': data.get('created_at'),
        'media': [
            {
                'type': m.get('type'),
                'url': m.get('url') or m.get('preview_image_url'),
                'width': m.get('width'),
                'height': m.get('height'),
            }
            for m in media_list
        ],
    }


if __name__ == "__main__":
    try:
        mcp.run(transport='streamable-http')
    except KeyboardInterrupt:
        pass
