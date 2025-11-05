"""
Simple test to verify the article fetching logic
"""
import asyncio
import json
import os


async def test_fetch_logic():
    """
    Test the basic logic of parsing WeChat API response
    This simulates what happens when the API returns data
    """
    print("\n=== Testing Article Parsing Logic ===\n")

    # Simulate a typical WeChat API response
    mock_api_response = {
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
                                "author_name": "Author 1"
                            },
                            {
                                "title": "Test Article 2",
                                "cover": "https://example.com/cover2.jpg",
                                "link": "https://mp.weixin.qq.com/s/test2",
                                "author_name": "Author 2"
                            }
                        ]
                    })
                },
                {
                    "publish_info": json.dumps({
                        "appmsgex": [
                            {
                                "title": "Test Article 3",
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

    # Create test directory
    test_dir = "/tmp/wechat_simple_test"
    os.makedirs(test_dir, exist_ok=True)
    os.chdir(test_dir)

    # Create CSV with header
    with open("result.csv", "w", encoding="utf-8") as f:
        f.write("title,cover,link,author_name\n")

    # Simulate the parsing logic from fetch_article.py
    article_count = 0
    publish_list_count = 0
    resp = mock_api_response

    print("Parsing response...")
    for i in json.loads(resp["publish_page"])["publish_list"]:
        publish_list_count += 1
        print(f"\nProcessing publish_list item #{publish_list_count}")

        with open("result.csv", 'a', encoding='utf-8') as f:
            for j in json.loads(i["publish_info"])["appmsgex"]:
                article_count += 1
                print(f"  - Article #{article_count}: {j['title']}")
                f.write(f"{j['title']},{j['cover']},{j['link']},{j['author_name']}\n")

    # Read and display results
    with open("result.csv", "r", encoding="utf-8") as f:
        content = f.read()

    lines = content.strip().split("\n")
    article_lines = len(lines) - 1  # Subtract header

    print(f"\n{'='*60}")
    print(f"Results:")
    print(f"  - publish_list items: {publish_list_count}")
    print(f"  - Total articles: {article_count}")
    print(f"  - CSV lines (excluding header): {article_lines}")
    print(f"{'='*60}")

    print("\nCSV Content:")
    print(content)

    # Verify
    assert article_lines == article_count, f"CSV lines ({article_lines}) doesn't match article count ({article_count})"
    assert article_count == 3, f"Expected 3 articles, got {article_count}"

    print("\n✓ Test PASSED: Article parsing logic works correctly")
    return True


async def test_page_increment_logic():
    """
    Test to demonstrate the page increment bug in fetch_article.py
    """
    print("\n\n=== Testing Page Increment Logic ===\n")

    # Simulate multiple API responses
    print("Scenario: API returns 2 items in publish_list")
    print("Current code behavior:\n")

    active_page = 0
    target_page = -1  # Infinite, will break manually

    # Simulate first API call
    print(f"1. API call with begin={active_page * 5}")
    print(f"   Current active_page: {active_page}")

    # Simulate processing 2 items in publish_list
    for item_num in range(2):
        print(f"\n2.{item_num + 1}. Processing publish_list item #{item_num + 1}")
        # In current code, page increments here (BUG!)
        active_page += 1
        print(f"     Page incremented to: {active_page}")

    # Next API call
    print(f"\n3. Next API call with begin={active_page * 5}")
    print(f"   Current active_page: {active_page}")

    print("\n" + "="*60)
    print("BUG ANALYSIS:")
    print("="*60)
    print("Expected: Page should increment only once per API response")
    print(f"Expected begin parameter for 2nd API call: 5 (page 1)")
    print(f"Actual begin parameter for 2nd API call: {active_page * 5} (page {active_page})")
    print("\nThis causes the fetcher to skip pages!")
    print("If each API response has N items in publish_list,")
    print("the fetcher will skip N-1 pages with each request.")
    print("="*60)


if __name__ == "__main__":
    print("="*60)
    print("WeChat Fetcher - Simple Logic Tests")
    print("="*60)

    # Test article parsing
    try:
        asyncio.run(test_fetch_logic())
    except Exception as e:
        print(f"\n✗ Test FAILED: {e}")
        import traceback
        traceback.print_exc()

    # Test page increment logic
    asyncio.run(test_page_increment_logic())

    print("\n" + "="*60)
    print("Test suite completed")
    print("="*60)
