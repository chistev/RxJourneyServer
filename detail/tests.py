import time
import requests
from django.test import SimpleTestCase

class RandomPostsLiveTest(SimpleTestCase):
    def fetch_posts(self):
        url = 'https://rxjourneyserver.pythonanywhere.com/detail/random-posts/the-mountain-of-life/'
        response = requests.get(url)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIsInstance(data, list)
        return data

    def test_random_posts_exclude_current(self):
        current_slug = 'the-mountain-of-life'
        posts = self.fetch_posts()
        slugs = [post['slug'] for post in posts]

        print("Returned slugs:", slugs)

        self.assertNotIn(
            current_slug, slugs,
            f"The current post '{current_slug}' should be excluded from random posts"
        )

    def test_random_posts_are_random(self):
        titles_1 = [post['title'] for post in self.fetch_posts()]
        time.sleep(1)
        titles_2 = [post['title'] for post in self.fetch_posts()]

        print("\nFirst response titles:", titles_1)
        print("Second response titles:", titles_2)

        self.assertNotEqual(
            titles_1, titles_2,
            "Expected different random posts, but the same set was returned."
        )
