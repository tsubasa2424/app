import streamlit as st
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

class WebScraperApp:
    def __init__(self, master):
        self.master = master
        master.title("Web Scraper")

        self.keyword_input = st.sidebar.text_input("Enter the keyword:")
        self.search_button = st.sidebar.button("Search")
        self.exit_button = st.sidebar.button("Exit")

        # 検索結果を表示するテキストウィンドウ
        self.result_text = st.empty()

    def search_on_website(self):
        keyword = self.keyword_input
        self.result_text.text("")  # 検索前にテキストをクリア
        self.scrape_website(keyword)

    def scrape_website(self, keyword):
        coindesk_url = "https://www.coindeskjapan.com"
        search_url = urljoin(coindesk_url, f"/?s={keyword}")

        self.scrape_search_results(search_url, keyword)

    def scrape_search_results(self, search_url, keyword):
        try:
            while True:
                response = requests.get(search_url)
                response.raise_for_status()
                soup = BeautifulSoup(response.text, 'html.parser')

                # 記事のタイトルとリンクを取得して表示
                article_links = [(a.text.strip(), urljoin(search_url, a['href'])) for a in soup.find_all('a', href=True)]
                if article_links:
                    for article_title, article_link in article_links:
                        self.result_text.text(f'{article_title}: {article_link}\n\n')
                else:
                    self.result_text.text('No articles found on the page.\n\n')

                # ページネーションのリンクがあれば次のページに移動
                next_page_link = soup.find('a', class_='next page-numbers')
                if next_page_link:
                    next_page_url = urljoin(search_url, next_page_link['href'])
                    search_url = next_page_url
                else:
                    break  # ページネーションのリンクがなければ終了

        except requests.exceptions.RequestException as e:
            self.result_text.text(f"Failed to retrieve the page. Error: {e}\n")

def main():
    root = st
    app = WebScraperApp(root)
    app.search_on_website()

if __name__ == "__main__":
    main()












