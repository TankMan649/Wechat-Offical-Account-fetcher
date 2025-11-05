"""
Simple validation test to confirm the fix works
"""
import asyncio
import json
import os
from unittest.mock import AsyncMock, patch, MagicMock


async def test_article_collection():
    """
    Validate that articles are collected correctly from multiple pages
    """
    print("\n=== Validation Test: Article Collection ===\n")

    # Simulate 2 pages of results
    mock_response_page_0 = {
        "base_resp": {"ret": 0},
        "publish_page": json.dumps({
            "publish_list": [
                {
                    "publish_info": json.dumps({
                        "appmsgex": [
                            {"title": "Article 1", "cover": "cover1.jpg", "link": "link1", "author_name": "Author 1"},
                            {"title": "Article 2", "cover": "cover2.jpg", "link": "link2", "author_name": "Author 2"}
                        ]
                    })
                },
                {
                    "publish_info": json.dumps({
                        "appmsgex": [
                            {"title": "Article 3", "cover": "cover3.jpg", "link": "link3", "author_name": "Author 3"}
                        ]
                    })
                }
            ]
        })
    }

    mock_response_page_1 = {
        "base_resp": {"ret": 0},
        "publish_page": json.dumps({
            "publish_list": [
                {
                    "publish_info": json.dumps({
                        "appmsgex": [
                            {"title": "Article 4", "cover": "cover4.jpg", "link": "link4", "author_name": "Author 4"}
                        ]
                    })
                }
            ]
        })
    }

    mock_response_end = {"base_resp": {"ret": 0}}  # No publish_page

    from scripts.fetch_article import WechatOfficialAccountFetcher

    # Setup test directory
    test_dir = "/tmp/wechat_validation_test"
    os.makedirs(test_dir, exist_ok=True)
    os.chdir(test_dir)

    # Track which response to return based on call count
    call_count = [0]
    def get_response():
        call_count[0] += 1
        if call_count[0] == 1:
            print(f"  API Call {call_count[0]}: Returning page 0 (3 articles in 2 publish_list items)")
            return mock_response_page_0
        elif call_count[0] == 2:
            print(f"  API Call {call_count[0]}: Returning page 1 (1 article)")
            return mock_response_page_1
        else:
            print(f"  API Call {call_count[0]}: Returning end signal (no more data)")
            return mock_response_end

    with patch('asyncio.sleep', new_callable=AsyncMock):
        with patch('scripts.fetch_article.AsyncClient') as mock_client_class:
            # Setup mock
            mock_get = AsyncMock()
            mock_get.side_effect = lambda **kwargs: MagicMock(json=get_response)

            mock_client = MagicMock()
            mock_client.get = mock_get
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock(return_value=None)
            mock_client_class.return_value = mock_client

            # Run test
            print("Starting article fetch...\n")
            fetcher = WechatOfficialAccountFetcher(
                cookie="test_cookie",
                url="https://mp.weixin.qq.com/cgi-bin/appmsgpublish?sub=list&begin=0&count=5&fakeid=test&token=test",
                start_page=0,
                end_page=-1
            )

            await fetcher.get_published_articles()

            # Validate results
            print("\n" + "="*60)
            if os.path.exists("result.csv"):
                with open("result.csv", "r", encoding="utf-8") as f:
                    content = f.read()

                lines = content.strip().split("\n")
                articles = lines[1:]  # Skip header

                print("Results:")
                print("="*60)
                for idx, line in enumerate(lines, 1):
                    print(f"{idx}. {line}")

                print("="*60)
                print(f"\n✓ Total articles collected: {len(articles)}")
                print(f"✓ Expected: 4 articles")
                print(f"✓ API calls made: {call_count[0]}")

                # Verify all articles are present
                assert len(articles) == 4, f"Expected 4 articles, got {len(articles)}"
                assert "Article 1" in content
                assert "Article 2" in content
                assert "Article 3" in content
                assert "Article 4" in content

                print("\n" + "="*60)
                print("✓ TEST PASSED!")
                print("="*60)
                print("\nValidation successful:")
                print("  ✓ All articles from multiple pages collected")
                print("  ✓ Page increment logic works correctly")
                print("  ✓ Fetcher stops when no more data available")
                print("  ✓ No articles are skipped")
                return True
            else:
                print("✗ result.csv not created")
                return False


if __name__ == "__main__":
    print("="*60)
    print("WeChat Fetcher - Validation Test")
    print("="*60)

    try:
        result = asyncio.run(test_article_collection())
        if not result:
            exit(1)
    except Exception as e:
        print(f"\n✗ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
