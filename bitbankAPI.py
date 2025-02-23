import tkinter as tk
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from urllib.parse import urljoin
import requests
from bs4 import BeautifulSoup


class WebScraperApp:
    def __init__(self, master):
        self.master = master
        master.title("Web Scraper")

        self.url_label = tk.Label(master, text="Enter the URL:")
        self.url_label.pack()

        self.url_entry = tk.Entry(master)
        self.url_entry.pack()

        self.keyword_label = tk.Label(master, text="Enter the keyword:")
        self.keyword_label.pack()

        self.keyword_entry = tk.Entry(master)
        self.keyword_entry.pack()

        self.search_button = tk.Button(master, text="Search", command=self.search_on_website)
        self.search_button.pack()

        self.exit_button = tk.Button(master, text="Exit", command=master.quit)
        self.exit_button.pack()

    def search_on_website(self):
        url = self.url_entry.get()
        keyword = self.keyword_entry.get()
        self.scrape_website(url, keyword)

    def scrape_website(self, url, keyword):
        chromedriver_path = "C:/Users/otatu/OneDrive/chrome-win32/chromedriver-win32/chromedriver.exe"
        driver = webdriver.Chrome(executable_path=chromedriver_path)
        driver.get(url)

        # サイト内検索ボックスにキーワードを入力
        search_box = driver.find_element_by_name("s")  # 検索ボックスのname属性を指定
        search_box.clear()
        search_box.send_keys(keyword)
        search_box.send_keys(Keys.RETURN)

        self.scrape_search_results(driver, keyword)

    def scrape_search_results(self, driver, keyword):
        # サイト内検索結果ページのスクレイピング
        try:
            response = requests.get(driver.current_url)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')

            # ページのタイトルとURLを取得
            title = soup.title.text
            print(f'Title: {title}')
            print(f'URL: {driver.current_url}')

            # ページのテキストを取得してキーワードが含まれる部分を表示
            page_text = ' '.join([p.get_text() for p in soup.find_all(['p', 'div'])])
            print(f'\nPage Text with "{keyword}":\n')
            keyword_text = [line.strip() for line in page_text.splitlines() if keyword in line]
            for line in keyword_text:
                print(line)

            # ページ内の記事へのリンクを取得して表示
            article_links = [a['href'] for a in soup.find_all('a', href=True) if keyword in a.get_text()]
            if article_links:
                print(f'\nArticle Links:')
                for article_link in article_links:
                    full_article_link = urljoin(driver.current_url, article_link)
                    print(full_article_link)

            else:
                print('\nNo article links found on the page.')

            # ページネーションのリンクを取得して次のページに移動
            next_page_link = soup.find('a', class_='next page-numbers')
            if next_page_link:
                next_page_url = urljoin(driver.current_url, next_page_link['href'])
                print(f'\nMoving to next page: {next_page_url}')
                self.scrape_website(next_page_url, keyword)  # 次のページをスクレイピング

        except requests.exceptions.RequestException as e:
            print(f"Failed to retrieve the page. Error: {e}")


def main():
    root = tk.Tk()
    app = WebScraperApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()



