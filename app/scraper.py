import json
from bs4 import BeautifulSoup
import requests
from urllib.parse import urljoin
import time

def scrape_shl_catalog():
    BASE_URL = "https://www.shl.com"
    
    # All 32 tab URLs exactly as provided
    CATALOG_URLS = [
        "https://www.shl.com/solutions/products/product-catalog/",
        "https://www.shl.com/solutions/products/product-catalog/?start=12&type=1",
        "https://www.shl.com/solutions/products/product-catalog/?start=24&type=1&type=1",
        "https://www.shl.com/solutions/products/product-catalog/?start=36&type=1&type=1",
        "https://www.shl.com/solutions/products/product-catalog/?start=48&type=1&type=1",
        "https://www.shl.com/solutions/products/product-catalog/?start=60&type=1&type=1",
        "https://www.shl.com/solutions/products/product-catalog/?start=72&type=1&type=1",
        "https://www.shl.com/solutions/products/product-catalog/?start=84&type=1&type=1",
        "https://www.shl.com/solutions/products/product-catalog/?start=96&type=1&type=1",
        "https://www.shl.com/solutions/products/product-catalog/?start=108&type=1&type=1",
        "https://www.shl.com/solutions/products/product-catalog/?start=120&type=1&type=1",
        "https://www.shl.com/solutions/products/product-catalog/?start=132&type=1&type=1",
        "https://www.shl.com/solutions/products/product-catalog/?start=144&type=1&type=1",
        "https://www.shl.com/solutions/products/product-catalog/?start=156&type=1&type=1",
        "https://www.shl.com/solutions/products/product-catalog/?start=168&type=1&type=1",
        "https://www.shl.com/solutions/products/product-catalog/?start=180&type=1&type=1",
        "https://www.shl.com/solutions/products/product-catalog/?start=192&type=1&type=1",
        "https://www.shl.com/solutions/products/product-catalog/?start=204&type=1&type=1",
        "https://www.shl.com/solutions/products/product-catalog/?start=216&type=1&type=1",
        "https://www.shl.com/solutions/products/product-catalog/?start=228&type=1&type=1",
        "https://www.shl.com/solutions/products/product-catalog/?start=240&type=1&type=1",
        "https://www.shl.com/solutions/products/product-catalog/?start=252&type=1&type=1",
        "https://www.shl.com/solutions/products/product-catalog/?start=264&type=1&type=1",
        "https://www.shl.com/solutions/products/product-catalog/?start=276&type=1&type=1",
        "https://www.shl.com/solutions/products/product-catalog/?start=288&type=1&type=1",
        "https://www.shl.com/solutions/products/product-catalog/?start=300&type=1&type=1",
        "https://www.shl.com/solutions/products/product-catalog/?start=312&type=1&type=1",
        "https://www.shl.com/solutions/products/product-catalog/?start=324&type=1&type=1",
        "https://www.shl.com/solutions/products/product-catalog/?start=336&type=1&type=1",
        "https://www.shl.com/solutions/products/product-catalog/?start=348&type=1&type=1",
        "https://www.shl.com/solutions/products/product-catalog/?start=360&type=1&type=1",
        "https://www.shl.com/solutions/products/product-catalog/?start=372&type=1&type=1"
    ]
    
    assessments = []
    
    for tab_num, CATALOG_URL in enumerate(CATALOG_URLS, 1):
        try:
            print(f"\n🔄 Fetching Tab {tab_num}... ({CATALOG_URL})")
            catalog_response = requests.get(CATALOG_URL, headers={'User-Agent': 'Mozilla/5.0'}, timeout=15)
            catalog_response.raise_for_status()
            catalog_soup = BeautifulSoup(catalog_response.text, 'html.parser')
            
            rows = catalog_soup.select("table tr")[1:]  # Skip header row
            print(f"🔍 Found {len(rows)} assessments in Tab {tab_num}")
            
            for i, row in enumerate(rows, 1):
                cols = row.select("td")
                if not cols:
                    continue
                    
                link = cols[0].find("a")
                if not link:
                    continue
                    
                # Clean URL (your existing logic)
                assessment_url = urljoin(BASE_URL, link["href"].strip())
                if "solutions/products/product-catalog/solutions/products" in assessment_url:
                    assessment_url = assessment_url.replace(
                        "solutions/products/product-catalog/solutions/products",
                        "solutions/products"
                    )
                
                # Your existing description scraping logic ▼
                try:
                    print(f"📄 Tab {tab_num}: Fetching ({i}/{len(rows)}) {assessment_url}")
                    assessment_response = requests.get(
                        assessment_url, 
                        headers={'User-Agent': 'Mozilla/5.0'}, 
                        timeout=10
                    )
                    assessment_soup = BeautifulSoup(assessment_response.text, 'html.parser')
                    
                    description = ""
                    
                    # Method 1: Try finding the description under a heading element
                    description_heading = assessment_soup.find(lambda tag: tag.name in ['h1', 'h2', 'h3', 'h4'] 
                                                   and tag.text.strip() == "Description")
                    if description_heading:
                        next_element = description_heading.find_next()
                        while next_element and next_element.name == 'p':
                            description += next_element.get_text(" ", strip=True) + " "
                            next_element = next_element.find_next()
                    
                    # Method 2: Look for a specific container with Description class or id
                    if not description:
                        description_div = assessment_soup.find(id="Description") or assessment_soup.find(class_="Description")
                        if description_div:
                            paragraphs = description_div.find_all('p')
                            description = " ".join([p.get_text(" ", strip=True) for p in paragraphs])
                    
                    # Method 3: Try direct CSS classes that might contain the description
                    if not description:
                        possible_containers = [
                            assessment_soup.select_one("div.product-details p"),
                            assessment_soup.select_one("div.product-description p"),
                            assessment_soup.select_one("div.description-content p"),
                            assessment_soup.select_one("section.description p"),
                            assessment_soup.select_one(".product-info .description")
                        ]
                        
                        for container in possible_containers:
                            if container:
                                description = container.get_text(" ", strip=True)
                                break
                    
                    # Method 4: Look for any paragraph that contains characteristic keywords
                    if not description or description == "We recommend upgrading to a modern browser.":
                        keywords = ["entry-level", "position", "candidate", "assessment", "measure", "skill", "solution is for"]
                        paragraphs = assessment_soup.find_all("p")
                        for p in paragraphs:
                            text = p.get_text(" ", strip=True)
                            if any(keyword in text.lower() for keyword in keywords) and len(text) > 50:
                                description = text
                                break
                    
                    # Final cleanup
                    if description and description != "We recommend upgrading to a modern browser.":
                        unwanted_keywords = ["Contact", "Practice Tests", "Support", "Login", "Buy Online", "Book a Demo"]
                        for keyword in unwanted_keywords:
                            description = description.replace(keyword, "")
                        
                        assessments.append({
                            "name": link.get_text(strip=True),
                            "url": assessment_url,
                            "description": description.strip() or "Description unavailable",
                            "source_tab": tab_num  # Track which tab it came from
                        })
                    else:
                        assessments.append({
                            "name": link.get_text(strip=True),
                            "url": assessment_url,
                            "description": "Description unavailable",
                            "source_tab": tab_num
                        })
                    
                    time.sleep(1.5)  # Slightly reduced delay for bulk scraping
                
                except Exception as e:
                    print(f"⚠️ Tab {tab_num}: Failed to scrape {assessment_url}: {str(e)}")
                    assessments.append({
                        "name": link.get_text(strip=True),
                        "url": assessment_url,
                        "description": f"Description unavailable (Error: {str(e)})",
                        "source_tab": tab_num
                    })
            
            print(f"✅ Tab {tab_num} completed")
            time.sleep(2)  # Delay between tabs
            
        except Exception as e:
            print(f"❌ Tab {tab_num} failed: {str(e)}")
            continue
    
    # Save final data
    with open("data/shl_assessments_complete.json", "w") as f:
        json.dump(assessments, f, indent=2)
        
    print(f"\n🚀 TOTAL SCRAPED: {len(assessments)} assessments across {len(CATALOG_URLS)} tabs")
    return assessments

if __name__ == "__main__":
    scrape_shl_catalog()