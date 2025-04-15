import json
from bs4 import BeautifulSoup, Tag
import requests
from urllib.parse import urljoin
import time
import warnings
warnings.filterwarnings("ignore")


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
                
                # Check for adaptive/IRT support from catalog table
                adaptive_support = "❓"
                adaptive_cell = row.select_one("td.adaptive-support") or row.select_one("td:nth-child(3)")
                if adaptive_cell:
                    # Look for green dot or indicator
                    green_dot = adaptive_cell.select_one('svg.green, span.green-circle, .green-dot')
                    if green_dot or ("green" in str(adaptive_cell).lower()):
                        adaptive_support = "🟢"  # Green circle emoji
                    else:
                        adaptive_support = "🔴"  # Red circle emoji
    
                # Alternative check for text that might indicate support
                adaptive_text = row.find(string=lambda x: x and "Adaptive" in x or "IRT" in x)
                if adaptive_text and adaptive_support == "❓":
                    parent_element = adaptive_text.parent
                    if "supported" in str(parent_element).lower() or "yes" in str(parent_element).lower():
                        adaptive_support = "🟢"
                    elif "not supported" in str(parent_element).lower() or "no" in str(parent_element).lower():
                        adaptive_support = "🔴"
            
                # Clean URL
                assessment_url = urljoin(BASE_URL, link["href"].strip())
                if "solutions/products/product-catalog/solutions/products" in assessment_url:
                    assessment_url = assessment_url.replace(
                        "solutions/products/product-catalog/solutions/products",
                        "solutions/products"
                    )
                
                try:
                    print(f"📄 Tab {tab_num}: Fetching ({i}/{len(rows)}) {assessment_url}")
                    assessment_response = requests.get(
                        assessment_url, 
                        headers={'User-Agent': 'Mozilla/5.0'}, 
                        timeout=10
                    )
                    assessment_soup = BeautifulSoup(assessment_response.text, 'html.parser')
                    
                    # Initialize all fields with default values
                    assessment_data = {
                        "name": link.get_text(strip=True),
                        "url": assessment_url,
                        "adaptive/irt_support": adaptive_support,
                        "description": "Description unavailable",
                        "duration": "Duration not specified",
                        "languages": [],
                        "job_level": "Level not specified",
                        "remote_testing": "Remote testing not specified",
                        "test_type": "Type not specified",
                        "source_tab": tab_num
                    }
                    
                    # DESCRIPTION SCRAPING
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
                        assessment_data["description"] = description.strip()
                    
                    # NEW FIELDS SCRAPING
                    
                    # 1. Find all specification sections
                    spec_sections = assessment_soup.find_all(lambda tag: tag.name in ['div', 'section'] and 
                                                           'specification' in ' '.join(tag.get('class', [])).lower())
                    
                    # 2. Alternative: Look for headings that might contain these fields
                    for heading in assessment_soup.find_all(['h2', 'h3', 'h4']):
                        heading_text = heading.get_text(strip=True).lower()
                        next_sibling = heading.find_next_sibling()
                        
                        # Duration
                        if 'assessment length' in heading_text or 'duration' in heading_text:
                            duration_text = next_sibling.get_text(strip=True) if next_sibling else ""
                            if 'minutes' in duration_text.lower():
                                assessment_data["duration"] = duration_text
                        
                        # Languages
                        elif 'languages' in heading_text:
                            languages_text = next_sibling.get_text(strip=True) if next_sibling else ""
                            assessment_data["languages"] = [lang.strip() for lang in languages_text.split(',') if lang.strip()]
                        
                        # Job Level
                        elif 'job levels' in heading_text or 'job level' in heading_text:
                            job_level_text = next_sibling.get_text(strip=True) if next_sibling else ""
                            assessment_data["job_level"] = job_level_text
                        
                        # 3. For Remote Testing (green dot)
                        remote_testing_text = assessment_soup.find(string=lambda x: x and "Remote Testing:" in x)
                        if remote_testing_text:
                            parent_element = remote_testing_text.parent
                            green_dot = None
                            
                            # Try looking for a circle element after the text
                            green_dot = parent_element.find_next('svg') or parent_element.find_next('span', class_=lambda x: x and ('circle' in x or 'dot' in x))
                            
                            # If not found, try looking for any element with green color
                            if not green_dot:
                                green_dot = parent_element.find_next(attrs={'style': lambda x: x and 'green' in x.lower()})
                            
                            # If not found, try looking for elements with specific classes
                            if not green_dot:
                                green_dot = assessment_soup.select_one('span.green-circle, circle.green, .green-dot, .status-green')
                            
                            # Check if anything green was found
                            if green_dot:
                                assessment_data["remote_testing"] = "🟢"  # Green circle emoji
                            else:
                                assessment_data["remote_testing"] = "🔴"  # Red circle emoji
                        else:
                            assessment_data["remote_testing"] = "❓"  # Question mark if section not found

                        # 4. For Test Type (A B P format)
                        test_type_element = assessment_soup.find(string=lambda x: "Test Type:" in x if x else False)
                        if test_type_element:
                            # Look for the subsequent elements containing the test type letters
                            test_type_container = test_type_element.parent.find_next('span') or test_type_element.find_next_sibling()
                            if test_type_container:
                                test_type_text = test_type_container.get_text(strip=True)
                                assessment_data["test_type"] = test_type_text
                            else:
                                # Alternative approach - get all letters that follow the "Test Type:" text
                                next_element = test_type_element.next_sibling
                                test_type_letters = []
                                while next_element and not isinstance(next_element, Tag) and not "Remote Testing" in str(next_element):
                                    if next_element.strip():
                                        test_type_letters.append(next_element.strip())
                                    next_element = next_element.next_sibling
                                assessment_data["test_type"] = " ".join(test_type_letters) if test_type_letters else "Not found"
                    
                    assessments.append(assessment_data)
                    time.sleep(1.5)
                
                except Exception as e:
                    print(f"⚠️ Tab {tab_num}: Failed to scrape {assessment_url}: {str(e)}")
                    assessments.append({
                        "name": link.get_text(strip=True),
                        "url": assessment_url,
                        "description": f"Description unavailable (Error: {str(e)})",
                        "source_tab": tab_num
                    })
            
            print(f"✅ Tab {tab_num} completed")
            time.sleep(2)
            
        except Exception as e:
            print(f"❌ Tab {tab_num} failed: {str(e)}")
            continue
    
    with open("data/shl_assessments_complete.json", "w") as f:
        json.dump(assessments, f, indent=2)
        
    print(f"\n🚀 TOTAL SCRAPED: {len(assessments)} assessments across {len(CATALOG_URLS)} tabs")
    return assessments

if __name__ == "__main__":
    scrape_shl_catalog()