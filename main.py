import tkinter as tk
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
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

        # サイト内検索ボックスにキーワードを自動入力
        search_box = driver.find_element(By.NAME, "s")  # 検索ボックスのname属性を指定
        search_box.clear()
        search_box.send_keys(keyword)
        search_box.send_keys(Keys.RETURN)

        self.scrape_search_results(driver, keyword)

    def scrape_search_results(self, driver, keyword):
        # サイト内のすべての記事を取得
        try:
            while True:
                response = requests.get(driver.current_url)
                response.raise_for_status()
                soup = BeautifulSoup(response.text, 'html.parser')

                # ページのタイトルとURLを取得
                title = soup.title.text
                print(f'Title: {title}')
                print(f'URL: {driver.current_url}')

                # 記事のタイトルとリンクを取得して表示
                article_links = [(a.text.strip(), urljoin(driver.current_url, a['href'])) for a in soup.find_all('a', href=True)]
                if article_links:
                    print(f'\nArticle Links:')
                    for article_title, article_link in article_links:
                        print(f'{article_title}: {article_link}')

                else:
                    print('\nNo articles found on the page.')

                # ページネーションのリンクがあれば次のページに移動
                next_page_link = soup.find('a', class_='next page-numbers')
                if next_page_link:
                    next_page_url = urljoin(driver.current_url, next_page_link['href'])
                    print(f'\nMoving to next page: {next_page_url}')
                    driver.get(next_page_url)
                else:
                    break  # ページネーションのリンクがなければ終了

        except requests.exceptions.RequestException as e:
            print(f"Failed to retrieve the page. Error: {e}")


def main():
    root = tk.Tk()
    app = WebScraperApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()