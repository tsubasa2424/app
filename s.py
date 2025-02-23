from flask import Flask, render_template, request
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from urllib.parse import urljoin

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def form():
    if request.method == 'POST':
        url = request.form.get('url')
        keyword = request.form.get('keyword')
        results = scrape_website(url, keyword)
        return render_template('results.html', results=results)
    return render_template('form.html')

def scrape_website(url, keyword):
    chromedriver_path = "C:/Users/otatu/OneDrive/chrome-win32/chromedriver-win32/chromedriver.exe"
    driver = webdriver.Chrome(executable_path=chromedriver_path)
    driver.get(url)

    search_box = driver.find_element(By.NAME, "s")
    search_box.clear()
    search_box.send_keys(keyword)
    search_box.send_keys(Keys.RETURN)

    return scrape_search_results(driver, keyword)

def scrape_search_results(driver, keyword):
    results = []
    try:
        while True:
            response = requests.get(driver.current_url)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')

            title = soup.title.text
            results.append({'title': title, 'url': driver.current_url})

            article_links = [(a.text.strip(), urljoin(driver.current_url, a['href'])) for a in soup.find_all('a', href=True)]
            for article_title, article_link in article_links:
                results.append({'title': article_title, 'url': article_link})

            next_page_link = soup.find('a', class_='next page-numbers')
            if next_page_link:
                next_page_url = urljoin(driver.current_url, next_page_link['href'])
                driver.get(next_page_url)
            else:
                break

    except requests.exceptions.RequestException as e:
        results.append({'error': f"Failed to retrieve the page. Error: {e}"})

    return results

if __name__ == "__main__":
    app.run(debug=True)
