"""
Test script for WeChat Official Account Fetcher
This includes both unit tests with mocking and a manual test function
"""
import asyncio
import json
import os
from unittest.mock import AsyncMock, patch, MagicMock
from scripts.fetch_article import WechatOfficialAccountFetcher


async def test_single_post_mock():
    """
    Test fetching a single post with mocked API response
    """
    print("\n=== Testing Single Post Collection (Mocked) ===\n")

    # Create a mock response that simulates WeChat API response
    mock_response = {
        "base_resp": {"ret": 0},
        "publish_page": json.dumps({
            "publish_list": [
                {
                    "publish_info": json.dumps({
                        "appmsgex": [
                            {
                                "title": "Test Article 1",
                                "cover": "https://example.com/cover1.jpg",
                                "link": "https://mp.weixin.qq.com/s/test1",
                                "author_name": "Test Author"
                            }
                        ]
                    })
                }
            ]
        })
    }

    # Mock the AsyncClient
    with patch('scripts.fetch_article.AsyncClient') as mock_client:
        # Setup mock client
        mock_get = AsyncMock()
        mock_get.return_value.json.return_value = mock_response

        mock_context = MagicMock()
        mock_context.__aenter__.return_value.get = mock_get
        mock_client.return_value.__aenter__ = AsyncMock(return_value=mock_context.__aenter__.return_value)
        mock_client.return_value.__aexit__ = AsyncMock()

        # Create test directory
        test_dir = "/tmp/wechat_test"
        os.makedirs(test_dir, exist_ok=True)
        os.chdir(test_dir)

        # Initialize fetcher with test data
        test_url = "https://mp.weixin.qq.com/cgi-bin/appmsgpublish?sub=list&begin=0&count=5&fakeid=test123&token=test_token"
        test_cookie = "test_cookie"

        fetcher = WechatOfficialAccountFetcher(
            cookie=test_cookie,
            url=test_url,
            start_page=0,
            end_page=1  # Only fetch 1 page
        )

        # Run the fetch
        await fetcher.get_published_articles()

        # Verify result.csv was created and contains data
        if os.path.exists("result.csv"):
            with open("result.csv", "r", encoding="utf-8") as f:
                content = f.read()
                print("✓ result.csv created successfully")
                print("\nCSV Content:")
                print(content)

                # Verify the content
                lines = content.strip().split("\n")
                assert len(lines) == 2, f"Expected 2 lines (header + 1 article), got {len(lines)}"
                assert "Test Article 1" in content, "Article title not found in CSV"
                assert "Test Author" in content, "Author name not found in CSV"
                print("\n✓ Article data correctly written to CSV")
                print(f"✓ Fetched {fetcher._fetched_pages} article(s)")
                return True
        else:
            print("✗ result.csv was not created")
            return False


async def manual_test_single_post():
    """
    Manual test function to test with real credentials
    This will fetch exactly 1 page (5 articles max) from a real WeChat account
    """
    print("\n=== Manual Test: Fetch Single Page ===\n")
    print("This test will fetch exactly 1 page (up to 5 articles) from a WeChat official account.")
    print("You need to provide:")
    print("1. URL from the appmsgpublish network request")
    print("2. Cookie from the same request")
    print("\nSee README.md for instructions on how to get these values.\n")

    url = input("Enter the URL (or 'skip' to skip manual test): ")
    if url.lower() == 'skip':
        print("Skipping manual test")
        return

    cookie = input("Enter the Cookie: ")

    # Create test directory
    test_dir = os.path.join(os.getcwd(), "test_workdir")
    os.makedirs(test_dir, exist_ok=True)
    os.chdir(test_dir)

    print(f"\nWorking directory: {os.getcwd()}")
    print("Fetching 1 page (start_page=0, end_page=1)...\n")

    try:
        fetcher = WechatOfficialAccountFetcher(
            cookie=cookie,
            url=url,
            start_page=0,
            end_page=1  # Only fetch 1 page for testing
        )

        await fetcher.get_published_articles()

        # Check results
        if os.path.exists("result.csv"):
            with open("result.csv", "r", encoding="utf-8") as f:
                content = f.read()
                lines = content.strip().split("\n")
                article_count = len(lines) - 1  # Subtract header

                print(f"\n✓ Success! Fetched {article_count} article(s)")
                print(f"✓ Results saved to: {os.path.join(test_dir, 'result.csv')}")
                print("\nFirst few lines of result.csv:")
                print("\n".join(lines[:6]))  # Show header + first 5 articles
                return True
        else:
            print("\n✗ result.csv was not created")
            return False

    except Exception as e:
        print(f"\n✗ Error occurred: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Run all tests"""
    print("=" * 60)
    print("WeChat Official Account Fetcher - Test Suite")
    print("=" * 60)

    # Run mocked test
    try:
        mock_result = await test_single_post_mock()
        print(f"\nMocked test: {'PASSED' if mock_result else 'FAILED'}")
    except Exception as e:
        print(f"\nMocked test: FAILED with error: {e}")
        import traceback
        traceback.print_exc()

    # Ask if user wants to run manual test
    print("\n" + "=" * 60)
    run_manual = input("\nDo you want to run manual test with real credentials? (y/n): ")
    if run_manual.lower() == 'y':
        try:
            manual_result = await manual_test_single_post()
            print(f"\nManual test: {'PASSED' if manual_result else 'FAILED'}")
        except Exception as e:
            print(f"\nManual test: FAILED with error: {e}")
            import traceback
            traceback.print_exc()

    print("\n" + "=" * 60)
    print("Test suite completed")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
