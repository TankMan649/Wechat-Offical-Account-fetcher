"""
Public WeChat Article Scraper - No Credentials Required!
Uses Sogou WeChat Search to find and collect articles from official accounts.
"""
import asyncio
import re
import csv
from urllib.parse import quote, urlencode
import httpx
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from loguru import logger


class PublicWechatScraper:
    """
    Scrape WeChat Official Account articles using public Sogou search
    No admin credentials needed!
    """

    def __init__(self, account_name: str, max_articles: int = 10, use_proxy: bool = False):
        self.account_name = account_name
        self.max_articles = max_articles
        self.use_proxy = use_proxy
        self.sogou_base = "https://weixin.sogou.com"
        self.articles = []

    async def search_account(self):
        """Search for the official account on Sogou"""
        logger.info(f"Searching for WeChat account: {self.account_name}")

        search_url = f"{self.sogou_base}/weixin?type=1&query={quote(self.account_name)}"

        headers = {
            'User-Agent': UserAgent().random,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        }

        proxies = None
        if self.use_proxy:
            proxies = "socks5://127.0.0.1:9050"  # Tor default

        async with httpx.AsyncClient(headers=headers, proxies=proxies, timeout=30, follow_redirects=True) as client:
            try:
                resp = await client.get(search_url)

                if resp.status_code == 200:
                    soup = BeautifulSoup(resp.text, 'html.parser')

                    # Find the first account result
                    account_link = soup.find('a', {'uigs': 'account_name_0'})

                    if account_link:
                        account_url = account_link.get('href')
                        logger.info(f"Found account URL: {account_url}")
                        return account_url
                    else:
                        logger.warning("Account not found in search results")
                        # Try to find any account link
                        links = soup.find_all('a', href=re.compile('gzh'))
                        if links:
                            account_url = links[0].get('href')
                            logger.info(f"Found account URL (fallback): {account_url}")
                            return account_url

                        logger.error("No account links found")
                        return None
                else:
                    logger.error(f"Search failed with status {resp.status_code}")
                    return None

            except Exception as e:
                logger.error(f"Error searching for account: {e}")
                return None

    async def get_articles_from_account(self, account_url: str):
        """Get articles from the account page"""
        logger.info("Fetching articles from account page...")

        headers = {
            'User-Agent': UserAgent().random,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Referer': self.sogou_base,
        }

        proxies = None
        if self.use_proxy:
            proxies = "socks5://127.0.0.1:9050"

        async with httpx.AsyncClient(headers=headers, proxies=proxies, timeout=30, follow_redirects=True) as client:
            try:
                resp = await client.get(account_url)

                if resp.status_code == 200:
                    soup = BeautifulSoup(resp.text, 'html.parser')

                    # Find article links
                    article_items = soup.find_all('li', class_=re.compile('wx-rb'))

                    if not article_items:
                        # Try alternative selectors
                        article_items = soup.find_all('div', class_=re.compile('txt-box'))

                    logger.info(f"Found {len(article_items)} article items")

                    for item in article_items[:self.max_articles]:
                        try:
                            # Extract article info
                            title_elem = item.find('h3') or item.find('h4') or item.find('a')
                            link_elem = item.find('a', href=re.compile('mp.weixin.qq.com'))

                            if title_elem and link_elem:
                                title = title_elem.text.strip()
                                link = link_elem.get('href')

                                # Try to get publish date
                                date_elem = item.find('span', class_='s2') or item.find('div', class_='s2')
                                date = date_elem.text.strip() if date_elem else 'Unknown'

                                article = {
                                    'title': title,
                                    'link': link,
                                    'date': date,
                                    'account': self.account_name
                                }

                                self.articles.append(article)
                                logger.info(f"Collected: {title}")

                        except Exception as e:
                            logger.warning(f"Error parsing article item: {e}")
                            continue

                    return len(self.articles)
                else:
                    logger.error(f"Failed to fetch account page: {resp.status_code}")
                    return 0

            except Exception as e:
                logger.error(f"Error fetching articles: {e}")
                return 0

    async def search_articles_directly(self):
        """
        Alternative method: Search for articles directly by keyword
        This can work even if we can't access the account page
        """
        logger.info(f"Searching for articles by keyword: {self.account_name}")

        search_url = f"{self.sogou_base}/weixin?type=2&query={quote(self.account_name)}"

        headers = {
            'User-Agent': UserAgent().random,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        }

        proxies = None
        if self.use_proxy:
            proxies = "socks5://127.0.0.1:9050"

        async with httpx.AsyncClient(headers=headers, proxies=proxies, timeout=30, follow_redirects=True) as client:
            try:
                resp = await client.get(search_url)

                if resp.status_code == 200:
                    soup = BeautifulSoup(resp.text, 'html.parser')

                    # Find article results
                    articles = soup.find_all('div', class_='txt-box')

                    logger.info(f"Found {len(articles)} articles in search")

                    for article in articles[:self.max_articles]:
                        try:
                            title_elem = article.find('h3') or article.find('a')
                            link_elem = article.find('a', href=re.compile('mp.weixin.qq.com'))
                            account_elem = article.find('a', class_='account')
                            date_elem = article.find('span', class_='s2')

                            if title_elem and link_elem:
                                article_data = {
                                    'title': title_elem.text.strip(),
                                    'link': link_elem.get('href'),
                                    'account': account_elem.text.strip() if account_elem else 'Unknown',
                                    'date': date_elem.text.strip() if date_elem else 'Unknown'
                                }

                                self.articles.append(article_data)
                                logger.info(f"Collected: {article_data['title']}")

                        except Exception as e:
                            logger.warning(f"Error parsing article: {e}")
                            continue

                    return len(self.articles)
                else:
                    logger.error(f"Search failed: {resp.status_code}")
                    return 0

            except Exception as e:
                logger.error(f"Error in article search: {e}")
                return 0

    async def run(self):
        """Main execution method"""
        logger.info("="*60)
        logger.info("Public WeChat Scraper - No Credentials Needed!")
        logger.info("="*60)

        # Method 1: Try to find account and get articles
        account_url = await self.search_account()

        if account_url:
            await self.get_articles_from_account(account_url)

        # Method 2: If Method 1 didn't get enough, search articles directly
        if len(self.articles) < self.max_articles:
            logger.info("Trying direct article search...")
            await self.search_articles_directly()

        # Save results
        if self.articles:
            await self.save_results()
            logger.info(f"✓ Successfully collected {len(self.articles)} articles!")
            return True
        else:
            logger.error("✗ No articles collected")
            return False

    async def save_results(self):
        """Save articles to CSV"""
        import os
        os.makedirs("workdir", exist_ok=True)

        filename = "workdir/public_scrape_results.csv"

        with open(filename, 'w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=['title', 'link', 'account', 'date'])
            writer.writeheader()
            writer.writerows(self.articles)

        logger.info(f"Results saved to: {filename}")

        # Also print to console
        logger.info("\n" + "="*60)
        logger.info("COLLECTED ARTICLES:")
        logger.info("="*60)
        for i, article in enumerate(self.articles, 1):
            logger.info(f"\n{i}. {article['title']}")
            logger.info(f"   Account: {article['account']}")
            logger.info(f"   Date: {article['date']}")
            logger.info(f"   Link: {article['link'][:80]}...")


async def main():
    """Main function"""
    print("="*60)
    print("Public WeChat Article Scraper")
    print("="*60)
    print("\nThis tool scrapes WeChat articles from public Sogou search")
    print("No WeChat admin credentials required!")
    print("\nNote: Sogou may have rate limiting or require CAPTCHA")
    print("="*60)

    account_name = input("\nEnter WeChat official account name (Chinese recommended): ").strip()

    if not account_name:
        account_name = "腾讯科技"  # Default: Tencent Tech
        print(f"Using default: {account_name}")

    max_articles = input("How many articles to collect (default: 10): ").strip()
    max_articles = int(max_articles) if max_articles else 10

    use_proxy = input("Use proxy/Tor? (y/n, default: n): ").strip().lower() == 'y'

    scraper = PublicWechatScraper(
        account_name=account_name,
        max_articles=max_articles,
        use_proxy=use_proxy
    )

    result = await scraper.run()

    if result:
        print("\n" + "="*60)
        print("✓ SUCCESS!")
        print("="*60)
        print("\nArticles saved to: workdir/public_scrape_results.csv")
        print("Check the file to see the collected articles!")
    else:
        print("\n" + "="*60)
        print("✗ FAILED")
        print("="*60)
        print("\nPossible reasons:")
        print("- Sogou rate limiting")
        print("- CAPTCHA required")
        print("- Account name not found")
        print("\nTry:")
        print("- Using a different account name")
        print("- Waiting a few minutes and trying again")
        print("- Using proxy/Tor (set up required)")


if __name__ == "__main__":
    asyncio.run(main())
