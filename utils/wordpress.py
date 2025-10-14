from wp_api import WPClient
from wp_api.auth import ApplicationPasswordAuth
import os

auth = ApplicationPasswordAuth( username=os.getenv("WP_USER"), password=os.getenv("WP_APP_PASSWORD"))
wp = WPClient(base_url=os.getenv("WP_BASE_URL"), auth=auth)

def util_get_post_by_id(post_id: int) -> dict:
    return wp.posts.get(post_id)

def util_get_recent_posts(count: int = 5) -> list[dict]:
    return wp.posts.list(per_page=count)