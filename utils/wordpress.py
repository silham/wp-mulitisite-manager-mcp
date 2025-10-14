from wp_api import WPClient
from wp_api.auth import ApplicationPasswordAuth
import os

auth = ApplicationPasswordAuth( username="goto@digifix.com.au", app_password="iUGn XOkL QPvs q6jv CCI1 xWAd")
wp = WPClient(base_url="https://googlerank.com.au", auth=auth)

def util_get_post_by_id(post_id: int) -> dict:
    return wp.posts.get(post_id)

def util_get_recent_posts(count: int = 5) -> list[dict]:
    return wp.posts.list(per_page=count)

if __name__ == "__main__":
    # Example usage
    print(util_get_recent_posts(3))