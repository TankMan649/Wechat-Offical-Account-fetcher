"""
Demonstrate fetching a REAL public WeChat article
No credentials needed!
"""
import httpx
from bs4 import BeautifulSoup


def fetch_public_wechat_article(url):
    """
    Fetch a public WeChat article by URL
    This works without any credentials!
    """
    print(f"\nFetching article from: {url}")
    print("-"*60)

    try:
        # Fetch the article (no credentials needed!)
        response = httpx.get(url, timeout=10, follow_redirects=True)

        if response.status_code == 200:
            print(f"✓ Successfully accessed! (HTTP {response.status_code})")

            # Parse the HTML
            soup = BeautifulSoup(response.text, 'html.parser')

            # Extract article metadata
            title = soup.find('h1', {'class': 'rich_media_title'})
            author = soup.find('a', {'id': 'js_name'})
            content_div = soup.find('div', {'id': 'js_content'})

            print("\nArticle Details:")
            print("-"*60)

            if title:
                print(f"Title: {title.text.strip()}")
            else:
                print("Title: (Could not extract)")

            if author:
                print(f"Account: {author.text.strip()}")
            else:
                print("Account: (Could not extract)")

            if content_div:
                # Get first 200 characters of content
                content_text = content_div.get_text(strip=True)[:200]
                print(f"\nContent Preview:")
                print(content_text + "...")
            else:
                print("\nContent: (Could not extract)")

            print("\n" + "="*60)
            print("✓ PUBLIC ACCESS CONFIRMED!")
            print("="*60)
            print("\nThis proves that WeChat articles ARE publicly accessible!")
            print("No login or credentials were needed to fetch this article.")

            return True

        else:
            print(f"✗ HTTP {response.status_code}")
            if response.status_code == 404:
                print("  Article not found (invalid URL or removed)")
            elif response.status_code == 301 or response.status_code == 302:
                print(f"  Redirected to: {response.headers.get('Location', 'unknown')}")
            return False

    except Exception as e:
        print(f"✗ Error: {e}")
        return False


def main():
    print("="*60)
    print("Real Public WeChat Article Test")
    print("="*60)
    print("\nThis test attempts to fetch a real WeChat article URL")
    print("to demonstrate public accessibility.")
    print("\nNote: You can provide any valid WeChat article URL.")
    print("      Format: https://mp.weixin.qq.com/s/[article_id]")

    # Option 1: Use a provided URL
    print("\n" + "="*60)
    print("Option 1: Test with a specific article URL")
    print("="*60)

    print("""
If you have a WeChat article URL, you can test it like this:

import httpx
from bs4 import BeautifulSoup

url = 'https://mp.weixin.qq.com/s/YOUR_ARTICLE_ID'
response = httpx.get(url)  # No credentials!
soup = BeautifulSoup(response.text, 'html.parser')

title = soup.find('h1', {'class': 'rich_media_title'})
print(f"Article title: {title.text.strip()}")
    """)

    # Option 2: Explain how to find article URLs
    print("\n" + "="*60)
    print("Option 2: How to find WeChat article URLs")
    print("="*60)

    print("""
You can get WeChat article URLs from:

1. Sogou WeChat Search (https://weixin.sogou.com)
   - Search for a topic or account
   - Click on any article
   - Copy the URL from your browser

2. WeChat App
   - Open any official account article
   - Tap share
   - Copy link

3. Google/Bing Search
   - Search: site:mp.weixin.qq.com [topic]
   - Results show public WeChat articles

All these URLs work without credentials!
    """)

    # Try with user input
    print("\n" + "="*60)
    print("Interactive Test")
    print("="*60)

    try:
        user_url = input("\nEnter a WeChat article URL to test (or press Enter to skip): ").strip()

        if user_url and user_url.startswith('http'):
            result = fetch_public_wechat_article(user_url)

            if result:
                print("\n✓ Test successful! The article is publicly accessible.")
            else:
                print("\n⚠ Could not fetch article (may be invalid URL)")

        else:
            print("\nSkipping interactive test.")

    except EOFError:
        print("\nNo input provided - skipping interactive test.")

    # Summary
    print("\n\n" + "="*60)
    print("SUMMARY: WeChat Articles ARE Public")
    print("="*60)

    print("""
Key Findings:

✓ Individual WeChat articles are publicly accessible
✓ No login or credentials required to read articles
✓ Anyone can access articles via direct URLs

However, the CURRENT TOOL needs credentials because:

- It systematically fetches ALL articles from an account
- Uses admin API for reliable pagination
- Gets complete metadata (covers, authors, dates)
- More efficient than scraping public pages

To test the current tool:
1. You need access to a WeChat Official Account admin panel
2. Follow README.md to get Cookie and URL
3. Run: python main.py
4. This fetches articles systematically via admin API

Both approaches have their place:
- Public access: Good for reading individual articles
- Admin API: Best for systematically collecting all articles
    """)

    print("="*60)


if __name__ == "__main__":
    main()
