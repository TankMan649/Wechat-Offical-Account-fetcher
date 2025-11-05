"""
Test the fixed article fetching logic
"""
import asyncio
import json
import os
from unittest.mock import AsyncMock, patch, MagicMock, call


async def test_fixed_pagination():
    """
    Test that pagination works correctly after the fix
    """
    print("\n=== Testing Fixed Pagination Logic ===\n")

    # Mock responses for 2 API calls
    mock_response_1 = {
        "base_resp": {"ret": 0},
        "publish_page": json.dumps({
            "publish_list": [
                {
                    "publish_info": json.dumps({
                        "appmsgex": [
                            {
                                "title": "Article 1 Page 0",
                                "cover": "https://example.com/cover1.jpg",
                                "link": "https://mp.weixin.qq.com/s/test1",
                                "author_name": "Author 1"
                            }
                        ]
                    })
                },
                {
                    "publish_info": json.dumps({
                        "appmsgex": [
                            {
                                "title": "Article 2 Page 0",
                                "cover": "https://example.com/cover2.jpg",
                                "link": "https://mp.weixin.qq.com/s/test2",
                                "author_name": "Author 2"
                            }
                        ]
                    })
                }
            ]
        })
    }

    mock_response_2 = {
        "base_resp": {"ret": 0},
        "publish_page": json.dumps({
            "publish_list": [
                {
                    "publish_info": json.dumps({
                        "appmsgex": [
                            {
                                "title": "Article 1 Page 1",
                                "cover": "https://example.com/cover3.jpg",
                                "link": "https://mp.weixin.qq.com/s/test3",
                                "author_name": "Author 3"
                            }
                        ]
                    })
                }
            ]
        })
    }

    # End response (no publish_page)
    mock_response_end = {
        "base_resp": {"ret": 0}
    }

    from scripts.fetch_article import WechatOfficialAccountFetcher

    # Create test directory
    test_dir = "/tmp/wechat_pagination_test"
    os.makedirs(test_dir, exist_ok=True)
    os.chdir(test_dir)

    # Mock the sleep to speed up testing
    with patch('asyncio.sleep', new_callable=AsyncMock):
        with patch('scripts.fetch_article.AsyncClient') as mock_client_class:
            # Setup mock responses
            mock_get = AsyncMock()
            responses = [mock_response_1, mock_response_2, mock_response_end]
            mock_get.side_effect = [
                MagicMock(json=lambda: responses[0]),
                MagicMock(json=lambda: responses[1]),
                MagicMock(json=lambda: responses[2])
            ]

            # Setup mock client context manager
            mock_client = MagicMock()
            mock_client.get = mock_get
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock(return_value=None)
            mock_client_class.return_value = mock_client

            # Run the test
            test_url = "https://mp.weixin.qq.com/cgi-bin/appmsgpublish?sub=list&begin=0&count=5&fakeid=test123&token=test_token"
            test_cookie = "test_cookie"

            fetcher = WechatOfficialAccountFetcher(
                cookie=test_cookie,
                url=test_url,
                start_page=0,
                end_page=-1  # Fetch until no more data
            )

            await fetcher.get_published_articles()

            # Verify the API calls were made with correct parameters
            print("Checking API calls...")
            calls = mock_get.call_args_list

            print(f"Total API calls made: {len(calls)}")

            for idx, call_obj in enumerate(calls):
                params = call_obj[1]['params']
                begin_value = params.get('begin', ['unknown'])[0]
                print(f"  Call {idx + 1}: begin={begin_value} (expected: {idx * 5})")

            # Verify the CSV results
            if os.path.exists("result.csv"):
                with open("result.csv", "r", encoding="utf-8") as f:
                    content = f.read()

                print("\n" + "="*60)
                print("CSV Content:")
                print("="*60)
                print(content)

                lines = content.strip().split("\n")
                article_count = len(lines) - 1  # Subtract header

                print("="*60)
                print(f"Summary:")
                print(f"  - Total articles fetched: {article_count}")
                print(f"  - Expected: 3 articles (2 from page 0, 1 from page 1)")
                print("="*60)

                # Verify
                assert article_count == 3, f"Expected 3 articles, got {article_count}"
                assert "Article 1 Page 0" in content
                assert "Article 2 Page 0" in content
                assert "Article 1 Page 1" in content

                # Verify pagination worked correctly
                assert len(calls) == 3, f"Expected 3 API calls, got {len(calls)}"
                assert calls[0][1]['params']['begin'][0] == '0', "First call should have begin=0"
                assert calls[1][1]['params']['begin'][0] == '5', "Second call should have begin=5"
                assert calls[2][1]['params']['begin'][0] == '10', "Third call should have begin=10"

                print("\n✓ Test PASSED: Pagination works correctly after fix!")
                print("  - Page increment happens once per API response")
                print("  - begin parameter increments by 5 each time")
                print("  - All articles are collected correctly")
                return True
            else:
                print("\n✗ result.csv was not created")
                return False


async def main():
    print("="*60)
    print("Testing Fixed WeChat Article Fetcher")
    print("="*60)

    try:
        result = await test_fixed_pagination()
        if result:
            print("\n" + "="*60)
            print("ALL TESTS PASSED!")
            print("="*60)
            print("\nThe fix successfully resolves the pagination bug.")
            print("The fetcher now correctly:")
            print("  1. Increments page only once per API response")
            print("  2. Uses correct begin parameter for each call")
            print("  3. Collects all articles without skipping pages")
        else:
            print("\nTEST FAILED")
    except Exception as e:
        print(f"\nTEST FAILED with error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
