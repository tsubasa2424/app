import tkinter as tk
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from urllib.parse import urljoin
import requests
from bs4 import BeautifulSoup

class WebScraperApp:
    def __init__(self, master):
        self.master = master
        master.title("Web Scraper")

        self.keyword_label = tk.Label(master, text="Enter the keyword:")
        self.keyword_label.pack()

        self.keyword_entry = tk.Entry(master)
        self.keyword_entry.pack()

        self.search_button = tk.Button(master, text="Search", command=self.search_on_website)
        self.search_button.pack()

        self.exit_button = tk.Button(master, text="Exit", command=master.quit)
        self.exit_button.pack()

        # 検索結果を表示するテキストウィンドウ
        self.result_text = tk.Text(master, wrap=tk.WORD)
        self.result_text.pack()

    def search_on_website(self):
        keyword = self.keyword_entry.get()
        self.result_text.delete(1.0, tk.END)  # 検索前にテキストをクリア
        self.scrape_website(keyword)

    def scrape_website(self, keyword):
        coindesk_url = "https://www.coindeskjapan.com"
        chromedriver_path = "C:/Users/otatu/OneDrive/chrome-win32/chromedriver-win32/chromedriver.exe"
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument("--headless")  # ブラウザを非表示にする
        driver = webdriver.Chrome(executable_path=chromedriver_path, chrome_options=chrome_options)
        driver.get(coindesk_url)

        # 検索ボックスが見つかるまで待機
        search_box = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.NAME, "s"))
        )

        # サイト内検索ボックスにキーワードを自動入力
        search_box.clear()
        search_box.send_keys(keyword)
        search_box.send_keys(Keys.RETURN)

        # サイトを非表示にする
        driver.execute_script("document.body.style.display = 'none';")

        # ページネーションを含む記事をスクレイピング
        self.scrape_articles(driver)

    def scrape_articles(self, driver):
        try:
            while True:
                # ページのHTMLを取得
                soup = BeautifulSoup(driver.page_source, 'html.parser')

                # 記事のタイトルとリンクを取得して表示
                article_links = [(a.text.strip(), urljoin(driver.current_url, a['href'])) for a in soup.find_all('a', href=True)]
                if article_links:
                    for article_title, article_link in article_links:
                        self.result_text.insert(tk.END, f'{article_title}: {article_link}\n')
                else:
                    self.result_text.insert(tk.END, 'No articles found on the page.\n')

                # ページネーションのリンクがあれば次のページに移動
                next_page_link = soup.find('a', class_='next page-numbers')
                if next_page_link:
                    next_page_url = urljoin(driver.current_url, next_page_link['href'])
                    driver.get(next_page_url)
                else:
                    break  # ページネーションのリンクがなければ終了

        except Exception as e:
            print(f"An error occurred: {e}")

def main():
    root = tk.Tk()
    app = WebScraperApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
