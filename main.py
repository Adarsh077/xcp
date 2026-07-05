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


@mcp.tool()
def get_user_details(url: str) -> dict:
    """Get user details by profile URL (e.g. https://x.com/username or https://twitter.com/username)"""
    username = url.rstrip('/').split('/')[-1]
    user = xclient.users.get_by_username(
        username,
        user_fields=[
            'created_at',
            'description',
            'location',
            'name',
            'profile_image_url',
            'protected',
            'public_metrics',
            'url',
            'username',
            'verified',
            'verified_type',
        ],
    )

    dumped = user.model_dump()
    data = dumped.get('data') or {}

    metrics = data.get('public_metrics') or {}

    return {
        'id': data.get('id'),
        'username': data.get('username'),
        'name': data.get('name'),
        'description': data.get('description'),
        'location': data.get('location'),
        'url': data.get('url'),
        'profile_image_url': data.get('profile_image_url'),
        'verified': data.get('verified'),
        'verified_type': data.get('verified_type'),
        'protected': data.get('protected'),
        'created_at': data.get('created_at'),
        'followers_count': metrics.get('followers_count'),
        'following_count': metrics.get('following_count'),
        'tweet_count': metrics.get('tweet_count'),
        'listed_count': metrics.get('listed_count'),
        'like_count': metrics.get('like_count'),
    }


if __name__ == "__main__":
    try:
        mcp.run(transport='streamable-http')
    except KeyboardInterrupt:
        pass
