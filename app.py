from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import requests
import html2text
from llama_index import Document
from llama_index.node_parser import SimpleNodeParser
from llama_index.text_splitter import TokenTextSplitter

# 1. Scrape raw HTML

def scrape_website(url: str):
    print("Scraping website...")

    try:
        # Send a GET request to the URL
        response = requests.get(url)

        # Check if the request was successful (status code 200)
        if response.status_code == 200:
            # Parse the HTML content of the page using BeautifulSoup
            soup = BeautifulSoup(response.text, 'html.parser')

            # Extract the HTML content from the parsed page
            html_string = str(soup)

            return html_string
        else:
            print(f"HTTP request failed with status code {response.status_code}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {str(e)}")
        return None


# 2. Convert html to markdown

def convert_html_to_markdown(html):

    # Create an html2text converter
    converter = html2text.HTML2Text()

    # Configure the converter
    converter.ignore_links = False

    # Convert the HTML to Markdown
    markdown = converter.handle(html)

    return markdown


# Turn https://developers.webflow.com/docs/getting-started-with-apps to https://developers.webflow.com

def get_base_url(url):
    parsed_url = urlparse(url)

    base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
    return base_url


# Turn relative url to absolute url in html

def convert_to_absolute_url(html, base_url):
    soup = BeautifulSoup(html, 'html.parser')

    for img_tag in soup.find_all('img'):
        if img_tag.get('src'):
            src = img_tag.get('src')
            if src.startswith(('http://', 'https://')):
                continue
            absolute_url = urljoin(base_url, src)
            img_tag['src'] = absolute_url
        elif img_tag.get('data-src'):
            src = img_tag.get('data-src')
            if src.startswith(('http://', 'https://')):
                continue
            absolute_url = urljoin(base_url, src)
            img_tag['data-src'] = absolute_url

    for link_tag in soup.find_all('a'):
        href = link_tag.get('href')
        if href is not None and not href.startswith(('http://', 'https://')):
            absolute_url = urljoin(base_url, href)
            link_tag['href'] = absolute_url

    updated_html = str(soup)

    return updated_html


def get_markdown_from_url(url):
    base_url = get_base_url(url)
    html = scrape_website(url)
    updated_html = convert_to_absolute_url(html, base_url)
    markdown = convert_html_to_markdown(updated_html)

    return markdown


# 3. Create vector index from markdown

def create_nodes_from_text(markdown, url):
    text_splitter = TokenTextSplitter(
        separator="\n",
        chunk_size=1024,
        chunk_overlap=20,
        backup_separators=["\n\n", ".", ","]
    )
    docs = []
    for Mark in markdown:
        docs.append(Document(text=Mark, metadata={'url':url}))

    node_parser = SimpleNodeParser(text_splitter=text_splitter)
    nodes = node_parser.get_nodes_from_documents(docs, show_progress=True)
    
    return nodes

# url = "https://developers.webflow.com/docs"
# query = "How to create a Webflow app?"
# markdown = get_markdown_from_url(url)
# index = create_index_from_text(markdown)
# answer = generate_answer(query, index)
# print(answer)
