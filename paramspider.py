import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse, parse_qs, urlunparse
import re

def get_all_forms(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    return soup.find_all('form')

def get_all_links(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    return [a['href'] for a in soup.find_all('a', href=True)]

def get_params_from_url(url):
    parsed_url = urlparse(url)
    return parse_qs(parsed_url.query)

def spider_params(base_url, output_file):
    visited_urls = set()
    urls_with_params = []

    def crawl(url):
        if url in visited_urls or not url.startswith(base_url):
            return
        visited_urls.add(url)
        
        try:
            links = get_all_links(url)
            forms = get_all_forms(url)
        except requests.RequestException as e:
            print(f"Request failed: {e}")
            return

        for link in links:
            absolute_url = urljoin(base_url, link)
            params = get_params_from_url(absolute_url)
            if params:
                urls_with_params.append(absolute_url)
                print(absolute_url)
            crawl(absolute_url)

        for form in forms:
            form_action = form.get('action')
            if form_action:
                form_url = urljoin(base_url, form_action)
                params = get_params_from_url(form_url)
                if params:
                    urls_with_params.append(form_url)
                    print(form_url)
            for input_tag in form.find_all('input'):
                input_name = input_tag.get('name')
                if input_name:
                    action_url = urljoin(base_url, form_action) if form_action else url
                    full_url = f"{action_url}?{input_name}=value"
                    urls_with_params.append(full_url)
                    print(full_url)

    crawl(base_url)

    with open(output_file, 'w') as f:
        for url in urls_with_params:
            f.write(f"{url}\n")

if __name__ == "__main__":
    base_url = input("Enter the base URL to crawl: ").strip()
    output_file = "params.txt"
    spider_params(base_url, output_file)
    print(f"Parameters have been written to {output_file}")
