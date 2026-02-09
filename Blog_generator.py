import time
import random
import requests
from bs4 import BeautifulSoup
import pandas as pd

# Base URL of the Amazon Kindle books page
base_url = "https://www.amazon.in/s?i=digital-text&bbn=10837929031&rh=n%3A10837929031%2Cp_36%3A-100&s=date-desc-rank&language=en_IN&linkCode=ll2&linkId=f7edd02bf11a81392e4cb3e1a90ece8a&tag=receiver06-21&ref=as_li_ss_tl"

# List of possible headers to avoid detection
headers_list = [
    {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"},
    {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Firefox/104.0.0.0 Safari/537.36"},
    {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/106.0.1370.47 Safari/537.36"}
]

# Select a random header from the list
headers = random.choice(headers_list)

# List to store filtered book details
all_books = []

# Function to fetch books from a single page
def fetch_books_from_page(url, delay=2, retries=3):
    """
    Fetches books from a given page URL and extracts relevant information.
    Retries in case of failure.
    """
    print(f"[DEBUG] Fetching URL: {url}")
    
    for attempt in range(retries):
        try:
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                print(f"[DEBUG] Page fetched successfully. Status Code: {response.status_code}")
                return BeautifulSoup(response.content, "html.parser")
            else:
                print(f"[WARNING] HTTP {response.status_code} - Retry {attempt + 1}/{retries}")
                time.sleep(delay)
        except Exception as e:
            print(f"[ERROR] An error occurred: {e}")
            time.sleep(delay)
    
    print("[ERROR] Failed to fetch the page after retries.")
    return None

# Function to extract the last page number from pagination
def get_last_page_number(soup):
    print("[DEBUG] Extracting last page number...")
    pagination = soup.find("span", {"class": "s-pagination-strip"})
    if pagination:
        page_numbers = pagination.find_all("span", {"class": "s-pagination-item"})
        last_page = 1  # Default if we can't find the last page
        for page in page_numbers:
            try:
                page_number = int(page.text.strip())
                last_page = max(last_page, page_number)
            except ValueError:
                continue  # Ignore non-numeric entries like "Next" or "..."
        print(f"[DEBUG] Last page number identified: {last_page}")
        return last_page
    print("[DEBUG] No pagination found. Assuming single page.")
    return 1  # Return 1 if no pagination found

# Function to handle pagination and fetch books from all pages
def fetch_books():
    run_once = True
    page_number = 1
    last_page = 1  # Default to 1 in case of errors

    while True:
        print(f"[INFO] Fetching page {page_number}...")
        url = f"{base_url}&page={page_number}"
        
        soup = fetch_books_from_page(url)
        if not soup:
            print("[ERROR] Failed to fetch the page. Exiting...")
            break  # Exit if the page cannot be fetched
        
        # Extract last page number
        if run_once:
            last_page = get_last_page_number(soup)
            run_once = False
        
        # Extract book details from the current page
        book_containers = soup.find_all("div", {"data-component-type": "s-search-result"})
        print(f"[DEBUG] Found {len(book_containers)} book containers on the page.")

        for container in book_containers:
            # Check if the book has the "Or ₹0 to buy" offer
            offer_tag = container.find("div", {"data-cy": "secondary-offer-recipe"})
            if offer_tag and "Or ₹0 to buy" in offer_tag.text:
                # Extract title
                title_tag = container.find("h2", {"class": "a-size-medium"})
                title = title_tag.text.strip() if title_tag else None

                # Extract price
                price_tag = container.find("span", {"class": "a-price-whole"})
                price = price_tag.text.strip() if price_tag else "Free"

                # Extract link
                link_tag = container.find("a", {"class": "a-link-normal"}, href=True)
                link = f"https://www.amazon.in{link_tag['href']}" if link_tag else None

                # Extract image URL
                image_tag = container.find("img", {"class": "s-image"})
                image_url = image_tag['src'] if image_tag else None

                if title:
                    all_books.append({
                        "Title": title,
                        "Price": price,
                        "Link": link + "&tag=receiver06-21",
                        "Image URL": image_url
                    })

        if page_number >= last_page:
            print("[INFO] Reached the last page.")
            break  # No more pages, exit the loop
        
        # Check for "Next" page link
        next_page_tag = soup.find("li", {"class": "s-pagination-item s-pagination-next"})
        if next_page_tag and 's-pagination-disabled' in next_page_tag.get("class", []):
            print("[INFO] Next button is disabled. Exiting...")
            break  # No next page, exit the loop
        else:
            page_number += 1  # Go to the next page

# Run the fetching process
fetch_books()

# Save the books to Excel if any are found
if all_books:
    print(f"[INFO] Total books found: {len(all_books)}")
    df = pd.DataFrame(all_books)
    df.to_excel("kindle_books_filtered_all_pages.xlsx", index=False)
    print("[INFO] Data successfully saved to kindle_books_filtered_all_pages.xlsx")
else:
    print("[WARNING] No books matching the filter found.")
# Check if any books were found and save to Excel
if all_books:
    df = pd.DataFrame(all_books)
    df.to_excel("kindle_books_filtered_all_pages.xlsx", index=False)
    print("Data successfully saved to kindle_books_filtered_all_pages.xlsx")
else:
    print("No books matching the filter found.")


def generate_html_from_excel(excel_file, output_html_file):
    # Read the Excel file
    try:
        df = pd.read_excel(excel_file)
    except FileNotFoundError:
        print(f"Error: The file {excel_file} was not found.")
        return
    except Exception as e:
        print(f"An error occurred: {e}")
        return

    # Tamil paragraph content
    paragraph_top = """
    <p class="paragraph">
    
        <strong>அன்பார்ந்த புத்தக வாசகர்களே!</strong><br><br>
        <strong>அமேசான் <span style='color:orange'>கிண்டிலில்</span></strong> நாள்தோறும் புத்தகங்கள் இலவசமாக வழங்கப்படுகிறது.<br>
        இந்த இலவச புத்தகமானது அந்தந்த ஆசிரியர்களே இலவசமாக வழங்குகின்றனர்.<br><br>
        இந்த இலவச புத்தகங்கள் இந்திய நேரப்படி அறிவித்த நாளில் மதியம் <strong>1:30pm</strong> முதல் 
        மறுநாள் மதியம் <strong>1:30pm</strong> வரை செல்லுபடியாகும்.<br>
        <strong style='color: red'>(சில புத்தகங்கள் தொடர்ச்சியாக இலவசமாக கிடைக்கும்)</strong><br>
        அந்த புத்தகங்களை பெற முந்தைய நாள் பதிவுகளையும் காணுங்கள் நன்றி.
<strong>அமேசான் <span style='color:orange'>கிண்டிலில்</span></strong> இருந்து இலவசமாக புத்தகத்தை வாங்குவது எப்படி என்று தெரிந்து கொள்ள 
       <strong> <a href="https://receiverindia.blogspot.com/2020/05/how-to-buy-free-books-in-amazon-kindle_7.html">இங்கே கிளிக் செய்யவும்.</strong></a><br><br>

    </p>
    """
    paragraph_bottom = """
    <p class="paragraph">
        <strong>அமேசான் <span style='color:orange'>கிண்டிலில்</span></strong> இருந்து இலவசமாக புத்தகத்தை வாங்குவது எப்படி என்று தெரிந்து கொள்ள 
        <a href="https://receiverindia.blogspot.com/2020/05/how-to-buy-free-books-in-amazon-kindle_7.html">இங்கே கிளிக் செய்யவும்.</a><br><br>
        For our regular updates follow us on social media platforms.<br><br>
        <strong><a href="https://fb.com/receiverindia">Facebook</a> <a href="https://x.com/receiverindia">X</a> <a href="https://instagram.com/receiverindia">Instagram</a> <a href="https://www.youtube.com/@receiverindia">Youtube</a> </strong><br>
        உங்கள் புத்தகத்தை பல வாசகர்களிடம் கொண்டு சேர்க்க இங்கே பதிவிடுங்கள்.<br><br>
        நீங்கள் உங்கள் புத்தகத்தின் லிங்க் மற்றும் இலவச விற்பனைக்கு கொடுத்துள்ள தேதியையும் 
        எங்கள் முகநூல் பக்கத்திற்கு அனுப்புங்கள்.<br>
நன்றி மீண்டும் வருக!!!<br>


    </p>
    """

    # Start the HTML content with a style block for better maintainability
    html_content = """
    <!DOCTYPE html>
    <html lang="ta">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">      
        <title>Kindle Books</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                margin: 20px;
            }
            .paragraph {
                text-align: center;
                font-size: 18px;
                line-height: 1.8;
                margin-bottom: 40px;
            }
            .book-container {
                display: flex;
                flex-wrap: wrap;
                justify-content: center;
                gap: 20px;
            }
            .book-item {
                text-align: center;
                width: 200px;
            }
            .book-item img {
                width: 150px;
                height: auto;
            }
            .book-item a {
                display: block;
                margin-top: 10px;
                font-size: 16px;
                color: #0066cc;
                text-decoration: none;
            }
            .book-item a:hover {
                text-decoration: underline;
            }
        </style>
    </head>
    <body>
    """

    # Add the top paragraph
    html_content += paragraph_top

    # Start the book container
    html_content += '<div class="book-container">\n'

    # Generate a div for each row in the dataframe
    for _, row in df.iterrows():
        title = row['Title']
        link = row['Link']
        image_url = row['Image URL']
        
        html_content += f'''
        <div class="book-item">
            <img src="{image_url}" alt="{title}">
            <a href="{link}" target="_blank">{title}</a>
        </div>
        '''

    # Close the book container
    html_content += '</div>\n'

    # Add the bottom paragraph
    html_content += paragraph_bottom

    # Close the HTML tags
    html_content += """
    </body>
    </html>
    """

    # Write the content to the output HTML file
    with open(output_html_file, 'w', encoding='utf-8') as file:
        file.write(html_content)

    print(f"HTML file generated: {output_html_file}")

# Usage example
excel_file = 'kindle_books_filtered_all_pages.xlsx'  # Replace with your Excel file name
output_html_file = 'output.html'  # Replace with your desired output HTML file name
generate_html_from_excel(excel_file, output_html_file)
import time
import random
import requests
from bs4 import BeautifulSoup
import pandas as pd

# Base URL of the Amazon Kindle books page
base_url = "https://www.amazon.in/s?i=digital-text&bbn=10837929031&rh=n%3A10837929031%2Cp_36%3A-100&s=date-desc-rank&linkCode=ll2&tag=receiver06-21&linkId=f7edd02bf11a81392e4cb3e1a90ece8a&language=en_IN&ref_=as_li_ss_tl"

# List of possible headers to avoid detection
headers_list = [
    {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"},
    {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Firefox/104.0.0.0 Safari/537.36"},
    {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/106.0.1370.47 Safari/537.36"}
]

# Select a random header from the list
headers = random.choice(headers_list)

# List to store filtered book details
all_books = []

# Function to fetch books from a single page
def fetch_books_from_page(url, delay=2, retries=3):
    """
    Fetches books from a given page URL and extracts relevant information.
    Retries in case of failure.
    """
    print(f"[DEBUG] Fetching URL: {url}")
    
    for attempt in range(retries):
        try:
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                print(f"[DEBUG] Page fetched successfully. Status Code: {response.status_code}")
                return BeautifulSoup(response.content, "html.parser")
            else:
                print(f"[WARNING] HTTP {response.status_code} - Retry {attempt + 1}/{retries}")
                time.sleep(delay)
        except Exception as e:
            print(f"[ERROR] An error occurred: {e}")
            time.sleep(delay)
    
    print("[ERROR] Failed to fetch the page after retries.")
    return None

# Function to extract the last page number from pagination
def get_last_page_number(soup):
    print("[DEBUG] Extracting last page number...")
    pagination = soup.find("span", {"class": "s-pagination-strip"})
    if pagination:
        page_numbers = pagination.find_all("span", {"class": "s-pagination-item"})
        last_page = 1  # Default if we can't find the last page
        for page in page_numbers:
            try:
                page_number = int(page.text.strip())
                last_page = max(last_page, page_number)
            except ValueError:
                continue  # Ignore non-numeric entries like "Next" or "..."
        print(f"[DEBUG] Last page number identified: {last_page}")
        return last_page
    print("[DEBUG] No pagination found. Assuming single page.")
    return 1  # Return 1 if no pagination found

# Function to handle pagination and fetch books from all pages
def fetch_books():
    run_once = True
    page_number = 1
    last_page = 1  # Default to 1 in case of errors

    while True:
        print(f"[INFO] Fetching page {page_number}...")
        url = f"{base_url}&page={page_number}"
        
        soup = fetch_books_from_page(url)
        if not soup:
            print("[ERROR] Failed to fetch the page. Exiting...")
            break  # Exit if the page cannot be fetched
        
        # Extract last page number
        if run_once:
            last_page = get_last_page_number(soup)
            run_once = False
        
        # Extract book details from the current page
        book_containers = soup.find_all("div", {"data-component-type": "s-search-result"})
        print(f"[DEBUG] Found {len(book_containers)} book containers on the page.")

        for container in book_containers:
            # Check if the book has the "Or ₹0 to buy" offer
            offer_tag = container.find("div", {"data-cy": "secondary-offer-recipe"})
            if offer_tag and "Or ₹0 to buy" in offer_tag.text:
                # Extract title
                title_tag = container.find("h2", {"class": "a-size-medium"})
                title = title_tag.text.strip() if title_tag else None

                # Extract price
                price_tag = container.find("span", {"class": "a-price-whole"})
                price = price_tag.text.strip() if price_tag else "Free"

                # Extract link
                link_tag = container.find("a", {"class": "a-link-normal"}, href=True)
                link = f"https://www.amazon.in{link_tag['href']}" if link_tag else None

                # Extract image URL
                image_tag = container.find("img", {"class": "s-image"})
                image_url = image_tag['src'] if image_tag else None

                if title:
                    all_books.append({
                        "Title": title,
                        "Price": price,
                        "Link": link + "&tag=receiver06-21",
                        "Image URL": image_url
                    })

        if page_number >= last_page:
            print("[INFO] Reached the last page.")
            break  # No more pages, exit the loop
        
        # Check for "Next" page link
        next_page_tag = soup.find("li", {"class": "s-pagination-item s-pagination-next"})
        if next_page_tag and 's-pagination-disabled' in next_page_tag.get("class", []):
            print("[INFO] Next button is disabled. Exiting...")
            break  # No next page, exit the loop
        else:
            page_number += 1  # Go to the next page

# Run the fetching process
fetch_books()

# Save the books to Excel if any are found
if all_books:
    print(f"[INFO] Total books found: {len(all_books)}")
    df = pd.DataFrame(all_books)
    df.to_excel("kindle_books_filtered_all_pages.xlsx", index=False)
    print("[INFO] Data successfully saved to kindle_books_filtered_all_pages.xlsx")
else:
    print("[WARNING] No books matching the filter found.")
# Check if any books were found and save to Excel
if all_books:
    df = pd.DataFrame(all_books)
    df.to_excel("kindle_books_filtered_all_pages.xlsx", index=False)
    print("Data successfully saved to kindle_books_filtered_all_pages.xlsx")
else:
    print("No books matching the filter found.")


def generate_html_from_excel(excel_file, output_html_file):
    # Read the Excel file
    try:
        df = pd.read_excel(excel_file)
    except FileNotFoundError:
        print(f"Error: The file {excel_file} was not found.")
        return
    except Exception as e:
        print(f"An error occurred: {e}")
        return

    # Tamil paragraph content
    paragraph_top = """
    <p class="paragraph">
    
        <strong>அன்பார்ந்த புத்தக வாசகர்களே!</strong><br><br>
        <strong>அமேசான் <span style='color:orange'>கிண்டிலில்</span></strong> நாள்தோறும் புத்தகங்கள் இலவசமாக வழங்கப்படுகிறது.<br>
        இந்த இலவச புத்தகமானது அந்தந்த ஆசிரியர்களே இலவசமாக வழங்குகின்றனர்.<br><br>
        இந்த இலவச புத்தகங்கள் இந்திய நேரப்படி அறிவித்த நாளில் மதியம் <strong>1:30pm</strong> முதல் 
        மறுநாள் மதியம் <strong>1:30pm</strong> வரை செல்லுபடியாகும்.<br>
        <strong style='color: red'>(சில புத்தகங்கள் தொடர்ச்சியாக இலவசமாக கிடைக்கும்)</strong><br>
        அந்த புத்தகங்களை பெற முந்தைய நாள் பதிவுகளையும் காணுங்கள் நன்றி.
<strong>அமேசான் <span style='color:orange'>கிண்டிலில்</span></strong> இருந்து இலவசமாக புத்தகத்தை வாங்குவது எப்படி என்று தெரிந்து கொள்ள 
       <strong> <a href="https://receiverindia.blogspot.com/2020/05/how-to-buy-free-books-in-amazon-kindle_7.html">இங்கே கிளிக் செய்யவும்.</strong></a><br><br>

    </p>
    """
    paragraph_bottom = """
    <p class="paragraph">
        <strong>அமேசான் <span style='color:orange'>கிண்டிலில்</span></strong> இருந்து இலவசமாக புத்தகத்தை வாங்குவது எப்படி என்று தெரிந்து கொள்ள 
        <a href="https://receiverindia.blogspot.com/2020/05/how-to-buy-free-books-in-amazon-kindle_7.html">இங்கே கிளிக் செய்யவும்.</a><br><br>
        For our regular updates follow us on social media platforms.<br><br>
        <strong><a href="https://fb.com/receiverindia">Facebook</a> <a href="https://x.com/receiverindia">X</a> <a href="https://instagram.com/receiverindia">Instagram</a> <a href="https://www.youtube.com/@receiverindia">Youtube</a> </strong><br>
        உங்கள் புத்தகத்தை பல வாசகர்களிடம் கொண்டு சேர்க்க இங்கே பதிவிடுங்கள்.<br><br>
        நீங்கள் உங்கள் புத்தகத்தின் லிங்க் மற்றும் இலவச விற்பனைக்கு கொடுத்துள்ள தேதியையும் 
        எங்கள் முகநூல் பக்கத்திற்கு அனுப்புங்கள்.<br>
நன்றி மீண்டும் வருக!!!<br>


    </p>
    """

    # Start the HTML content with a style block for better maintainability
    html_content = """
    <!DOCTYPE html>
    <html lang="ta">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">      
        <title>Kindle Books</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                margin: 20px;
            }
            .paragraph {
                text-align: center;
                font-size: 18px;
                line-height: 1.8;
                margin-bottom: 40px;
            }
            .book-container {
                display: flex;
                flex-wrap: wrap;
                justify-content: center;
                gap: 20px;
            }
            .book-item {
                text-align: center;
                width: 200px;
            }
            .book-item img {
                width: 150px;
                height: auto;
            }
            .book-item a {
                display: block;
                margin-top: 10px;
                font-size: 16px;
                color: #0066cc;
                text-decoration: none;
            }
            .book-item a:hover {
                text-decoration: underline;
            }
        </style>
    </head>
    <body>
    """

    # Add the top paragraph
    html_content += paragraph_top

    # Start the book container
    html_content += '<div class="book-container">\n'

    # Generate a div for each row in the dataframe
    for _, row in df.iterrows():
        title = row['Title']
        link = row['Link']
        image_url = row['Image URL']
        
        html_content += f'''
        <div class="book-item">
            <img src="{image_url}" alt="{title}">
            <a href="{link}" target="_blank">{title}</a>
        </div>
        '''

    # Close the book container
    html_content += '</div>\n'

    # Add the bottom paragraph
    html_content += paragraph_bottom

    # Close the HTML tags
    html_content += """
    </body>
    </html>
    """

    # Write the content to the output HTML file
    with open(output_html_file, 'w', encoding='utf-8') as file:
        file.write(html_content)

    print(f"HTML file generated: {output_html_file}")

# Usage example
excel_file = 'kindle_books_filtered_all_pages.xlsx'  # Replace with your Excel file name
output_html_file = 'output.html'  # Replace with your desired output HTML file name
generate_html_from_excel(excel_file, output_html_file)