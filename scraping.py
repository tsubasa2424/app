import tkinter as tk
from urllib.parse import urljoin
import requests
from bs4 import BeautifulSoup


class WebScraperApp:
    def __init__(self, master):
        self.master = master
        master.title("Webスクレイピング")

        # URL入力欄
        self.url_label = tk.Label(master, text="URLを入力:")
        self.url_label.pack()
        self.url_entry = tk.Entry(master)
        self.url_entry.pack()

        # キーワード入力欄
        self.keyword_label = tk.Label(master, text="キーワードを入力:")
        self.keyword_label.pack()
        self.keyword_entry = tk.Entry(master)
        self.keyword_entry.pack()

        # ページ数入力欄
        self.pages_label = tk.Label(master, text="ページ数を入力 (デフォルト: 3):")
        self.pages_label.pack()
        self.pages_entry = tk.Entry(master)
        self.pages_entry.pack()

        # 検索ボタン
        self.search_button = tk.Button(master, text="検索", command=self.scrape_website)
        self.search_button.pack()

        # 終了ボタン
        self.exit_button = tk.Button(master, text="終了", command=master.quit)
        self.exit_button.pack()

        # 再検索ボタン
        self.search_again_button = tk.Button(master, text="再検索", command=self.reset_fields)
        self.search_again_button.pack()

        # 結果表示欄
        self.results_text = tk.Text(master)
        self.results_text.pack()

    def reset_fields(self):
        # 入力欄をクリア
        self.url_entry.delete(0, tk.END)
        self.keyword_entry.delete(0, tk.END)
        self.pages_entry.delete(0, tk.END)
        # 結果表示欄をクリア
        self.results_text.delete('1.0', tk.END)

    def scrape_website(self):
        # 入力されたURLとキーワードを取得
        url = self.url_entry.get()
        keyword = self.keyword_entry.get()
        max_pages = int(self.pages_entry.get() or 3)  # デフォルトは3ページ

        # URLとキーワードが空欄でないことを確認
        if not url or not keyword:
            print("URLとキーワードを入力してください")
            return

        # ページを順番に処理
        for page_number in range(1, max_pages + 1):
            # ページURLを作成
            page_url = urljoin(url, f"?page={page_number}")

            # ページをスクレイピング
            response = requests.get(page_url)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')

            # ページ情報を取り出す
            title = soup.title.text
            print(f"ページ{page_number}をスクレイピングしています")
            print(f"タイトル: {title}")
            print(f"URL: {page_url}")

            # ページ内のテキストからキーワードを含む部分を探す
            page_text = ' '.join([p.get_text() for p in soup.find_all(['p', 'div'])])
            keyword_text = [line.strip() for line in page_text.splitlines() if keyword in line]

            # 結果を表示
            self.results_text.insert(tk.END, f"\nページ{page_number}の検索結果:\n")
            for line in keyword_text:
                self.results_text.insert(tk.END, f"{line}\n")

            # 記事リンクを探す
            article_links = [a['href'] for a in soup.find_all('a', href=True) if keyword in a.get_text()]
            if article_links:
                self.results_text.insert(tk.END, f"\n記事リンク:\n")
                for article_link in article_links:
                    self.results_text.insert(tk.END, f"{article_link}\n")

        # スクロールバーを一番下まで移動
        self.results_text.see(tk.END)


def main():
    # ユーザーインターフェースを作成
    root = tk.Tk()
    root.title("Webスクレイピング")

    # URL入力欄
    url_label = tk.Label(root, text="URLを入力:")
    url_label.pack()
    url_entry = tk.Entry(root)
    url_entry.pack()

    # キーワード入力欄
    keyword_label = tk.Label(root, text="キーワードを入力:")
    keyword_label.pack()
    keyword_entry = tk.Entry(root)
    keyword_entry.pack()

    # ページ数入力欄
    pages_label = tk.Label(root, text="ページ数を入力 (デフォルト: 3):")
    pages_label.pack()
    pages_entry = tk.Entry(root)
    pages_entry.pack()

    # 検索ボタン
    search_button = tk.Button(root, text="検索", command=lambda: scrape_website(url_entry.get(), keyword_entry.get(), int(pages_entry.get() or 3)))
    search_button.pack()

    # 終了ボタン
    exit_button = tk.Button(root, text="終了", command=root.quit)
    exit_button.pack()

    # 結果表示欄
    results_text = tk.Text(root)
    results_text.pack()

    # 検索ボタンが押された時の処理
    def scrape_website(url, keyword, max_pages):
        """
        Webサイトをスクレイピングして、検索結果を表示する。

        Args:
            url: スクレイピング対象のURL
            keyword: 検索キーワード
            max_pages: 最大ページ数

        Returns:
            検索結果
        """

        # ページを順番に処理
        for page_number in range(1, max_pages + 1):
            # ページURLを作成
            page_url = urljoin(url, f"?page={page_number}")

            # ページをスクレイピング
            response = requests.get(page_url)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')

            # ページ情報を取り出す
            title = soup.title.text
            print(f"ページ{page_number}をスクレイピングしています")
            print(f"タイトル: {title}")
            print(f"URL: {page_url}")

            # ページ内のテキストからキーワードを含む部分を探す
            page_text = ' '.join([p.get_text() for p in soup.find_all(['p', 'div'])])
            keyword_text = [line.strip() for line in page_text.splitlines() if keyword in line]

            # 結果を表示
            results_text.insert(tk.END, f"\nページ{page_number}の検索結果:\n")
            for line in keyword_text:
                results_text.insert(tk.END, f"{line}\n")

            # 記事リンクを探す
            article_links = [a['href'] for a in soup.find_all('a', href=True) if keyword in a.get_text()]
            if article_links:
                results_text.insert(tk.END, f"\n記事リンク:\n")
                for article_link in article_links:
                    results_text.insert(tk.END, f"{article_link}\n")

        # スクロールバーを一番下まで移動
        results_text.see(tk.END)

    # メインループ
    root.mainloop()


if __name__ == "__main__":
    main()






