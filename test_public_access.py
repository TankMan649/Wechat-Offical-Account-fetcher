"""
Test WeChat article collection using PUBLIC Sogou search API
No credentials needed!
"""
import wechatsogou

def test_public_article_access():
    """
    Test accessing WeChat Official Account articles via public Sogou search
    This doesn't require any WeChat credentials!
    """
    print("="*60)
    print("Testing Public WeChat Article Access")
    print("="*60)
    print("\nUsing Sogou WeChat public search API")
    print("No credentials needed!\n")

    # Initialize the wechatsogou client
    ws_api = wechatsogou.WechatSogouAPI()

    # Try to search for a popular WeChat official account
    # Using "腾讯" (Tencent) as an example - a well-known public account
    account_name = "腾讯"

    print(f"Searching for official account: {account_name}")
    print("-"*60)

    try:
        # Search for official accounts
        accounts = ws_api.search_gzh(account_name, page=1)

        if accounts:
            print(f"\n✓ Found {len(accounts)} account(s)")

            # Get the first account
            first_account = accounts[0]
            print(f"\nAccount Info:")
            print(f"  Name: {first_account.get('wechat_name', 'N/A')}")
            print(f"  ID: {first_account.get('wechat_id', 'N/A')}")
            print(f"  Description: {first_account.get('introduction', 'N/A')[:100]}...")

            # Try to get articles from this account
            print(f"\n{'-'*60}")
            print("Fetching recent articles...")
            print("-"*60)

            # Get article list
            article_info = ws_api.get_gzh_info(first_account['wechat_id'])

            if article_info and 'article' in article_info:
                articles = article_info['article']
                print(f"\n✓ Found {len(articles)} recent article(s)\n")

                for idx, article in enumerate(articles[:5], 1):  # Show first 5
                    print(f"{idx}. {article.get('title', 'N/A')}")
                    print(f"   URL: {article.get('url', 'N/A')[:80]}...")
                    print(f"   Date: {article.get('send_time', 'N/A')}")
                    print()

                print("="*60)
                print("✓ PUBLIC ACCESS TEST SUCCESSFUL!")
                print("="*60)
                print("\nProof of concept:")
                print("  ✓ Can access WeChat Official Accounts publicly")
                print("  ✓ Can retrieve article lists without credentials")
                print("  ✓ Can get article titles, URLs, and metadata")
                print("\nThis demonstrates that WeChat articles ARE publicly")
                print("accessible through Sogou's search API!")

                return True
            else:
                print("No articles found for this account")
                return False
        else:
            print(f"✗ No accounts found for '{account_name}'")
            return False

    except Exception as e:
        print(f"\n✗ Error occurred: {e}")
        print("\nNote: Sogou may have rate limiting or require captcha")
        print("verification for automated access. This is expected.")
        import traceback
        traceback.print_exc()
        return False


def test_article_search():
    """
    Test searching for articles by keyword
    """
    print("\n\n" + "="*60)
    print("Testing Article Search by Keyword")
    print("="*60)

    ws_api = wechatsogou.WechatSogouAPI()
    keyword = "人工智能"  # "Artificial Intelligence" in Chinese

    print(f"\nSearching for articles about: {keyword}")
    print("-"*60)

    try:
        articles = ws_api.search_article(keyword, page=1)

        if articles:
            print(f"\n✓ Found {len(articles)} article(s)\n")

            for idx, article in enumerate(articles[:3], 1):  # Show first 3
                print(f"{idx}. {article.get('title', 'N/A')}")
                print(f"   Account: {article.get('gzh', {}).get('wechat_name', 'N/A')}")
                print(f"   URL: {article.get('url', 'N/A')[:80]}...")
                print()

            print("="*60)
            print("✓ ARTICLE SEARCH TEST SUCCESSFUL!")
            print("="*60)
            return True
        else:
            print("No articles found")
            return False

    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("\n" + "="*60)
    print("WeChat Public Access Testing")
    print("="*60)
    print("\nThis test uses Sogou's PUBLIC API to access WeChat content")
    print("No WeChat credentials or login required!")
    print("="*60)

    # Test 1: Access account and articles
    result1 = test_public_article_access()

    # Test 2: Search articles by keyword
    result2 = test_article_search()

    print("\n\n" + "="*60)
    print("FINAL RESULTS")
    print("="*60)
    print(f"Account Access Test: {'✓ PASSED' if result1 else '✗ FAILED'}")
    print(f"Article Search Test: {'✓ PASSED' if result2 else '✗ FAILED'}")
    print("="*60)

    if result1 or result2:
        print("\n✓ At least one test passed!")
        print("\nThis proves WeChat Official Account articles are")
        print("publicly accessible without admin credentials!")
    else:
        print("\n⚠ Tests may have failed due to:")
        print("  - Network issues")
        print("  - Sogou rate limiting")
        print("  - CAPTCHA requirements")
        print("\nThis is expected for automated access.")
