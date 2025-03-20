import json
import time
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os
import math

# Define login function to reuse when needed
def login_to_site(driver):
    try:
        driver.get('https://thuvienphapluat.vn/page/login.aspx')
        driver.implicitly_wait(6)
        time.sleep(2)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//*[@id="UserName"]'))).send_keys('TaleSolutions')
        driver.find_element(By.XPATH, '//*[@id="Password"]').send_keys('tale0000@')
        driver.find_element(By.XPATH, '//*[@id="cmdLogin"]').click()
        try:
            agree_button = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, '//span[text()="Đồng ý"]'))
            )
            agree_button.click()
            print("✅ Clicked 'Đồng ý'")
        except:
            print("⚠️ 'Đồng ý' button did not appearanyone who deserves to dieappear.")
        time.sleep(1)
        return True
    except Exception as e:
        print(f"❌ Login failed: {str(e)}")
        return False

# Function to handle unknown errors by relogging in
def handle_unknown_error(driver, url):
    print("⚠️ Web server returned an unknown error! Attempting to relogin...")
    login_success = login_to_site(driver)
    if login_success:
        print("✅ Relogin successful, resuming operation...")
        driver.get(url)
        time.sleep(3)
        if "unknown error" in driver.page_source.lower():
            print("⚠️ Still encountering unknown error after relogin. Waiting 30 seconds before retry...")
            time.sleep(30)  # Wait longer before retry
            driver.get(url)
            time.sleep(3)
            if "unknown error" in driver.page_source.lower():
                print("❌ Unknown error persists after multiple attempts. Moving to next item.")
                return False
    else:
        print("❌ Relogin failed. Waiting 30 seconds before retry...")
        time.sleep(30)
        login_success = login_to_site(driver)
        if not login_success:
            print("❌ Failed to relogin after multiple attempts.")
            return False
    return True

# Function to save results to file
def save_results(results, filename="final_results.json"):
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=4)
        print(f"✅ Results saved to {filename}")
        return True
    except Exception as e:
        print(f"❌ Error saving results: {str(e)}")
        return False

# Load existing results if available
def load_existing_results(filename="final_results.json"):
    try:
        if os.path.exists(filename):
            with open(filename, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []
    except Exception as e:
        print(f"❌ Error loading existing results: {str(e)}")
        return []

# Check if document is already in results by comparing title, category, and urls
def is_duplicate(results, title, cate_parent, file_url=None, vn_file_url=None):
    for item in results:
        # Basic check by title and category
        if item['title'] == title and item['cate_parent'] == cate_parent:
            return True
        
        # Additional check by URLs if available
        if file_url and vn_file_url and item.get('file_url') == file_url and item.get('vn_file_url') == vn_file_url:
            return True
    
    return False

cate_parents = [
    {
        "cate_name": "Xuất nhập khẩu",
        "cate_url": "https://thuvienphapluat.vn/page/searchfast.aspx?fields=4&keyword=&bdate=14/03/1945&edate=14/03/2025&lan=1&match=True&org=0&fasttype=2"
    },
    {
        "cate_name": "Tiền tệ ngân hàng",
        "cate_url": "https://thuvienphapluat.vn/page/searchfast.aspx?fields=5&keyword=&bdate=14/03/1945&edate=14/03/2025&lan=1&match=True&org=0&fasttype=2"
    },
    {
        "cate_name": "Quyền dân sự",
        "cate_url": "https://thuvienphapluat.vn/page/searchfast.aspx?fields=25&keyword=&bdate=14/03/1945&edate=14/03/2025&lan=1&match=True&org=0&fasttype=2"
    },
    {
        "cate_name": "Doanh nghiệp",
        "cate_url": "https://thuvienphapluat.vn/page/searchfast.aspx?fields=1&keyword=&bdate=14/03/1945&edate=14/03/2025&lan=1&match=True&org=0&fasttype=2"
    },
    {
        "cate_name": "Sở hữu trí tuệ",
        "cate_url": "https://thuvienphapluat.vn/page/searchfast.aspx?fields=14&keyword=&bdate=14/03/1945&edate=14/03/2025&lan=1&match=True&org=0&fasttype=2"
    },
    {
        "cate_name": "Vi phạm hành chính",
        "cate_url": "https://thuvienphapluat.vn/page/searchfast.aspx?fields=16&keyword=&bdate=14/03/1945&edate=14/03/2025&lan=1&match=True&org=0&fasttype=2"
    },
    {
        "cate_name": "Bất động sản",
        "cate_url": "https://thuvienphapluat.vn/page/searchfast.aspx?fields=12&keyword=&bdate=14/03/1945&edate=14/03/2025&lan=1&match=True&org=0&fasttype=2"
    },
    {
        "cate_name": "Chứng khoán",
        "cate_url": "https://thuvienphapluat.vn/page/searchfast.aspx?fields=7&keyword=&bdate=14/03/1945&edate=14/03/2025&lan=1&match=True&org=0&fasttype=2"
    },
    {
        "cate_name": "Kế toán, kiểm toán",
        "cate_url": "https://thuvienphapluat.vn/page/searchfast.aspx?fields=9&keyword=&bdate=14/03/1945&edate=14/03/2025&lan=1&match=True&org=0&fasttype=2"
    },
    {
        "cate_name": "Thương mại",
        "cate_url": "https://thuvienphapluat.vn/page/searchfast.aspx?fields=3&keyword=d%E1%BB%8Bch%20v%E1%BB%A5%20%C4%83n%20u%E1%BB%91ng&bdate=18/03/1945&edate=18/03/2025&lan=1&match=True&org=0&fasttype=2"
    }
]

# Load existing results if available
final_result = load_existing_results()
print(f"Loaded {len(final_result)} existing results")

process_id = os.getpid()
options = webdriver.ChromeOptions()
options.add_argument("--headless")  # Run in headless mode
options.add_argument(f"--user-data-dir=/tmp/chrome-user-data-{process_id}") 
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
service = Service(executable_path="/usr/local/bin/chromedriver")
# D:\Pythons\Python3.12\Lib\site-packages\selenium\webdriver\chrome\chromedriver.exe
# /usr/local/bin/chromedriver
driver = webdriver.Chrome(service=service, options=options)

# Initial login
login_success = login_to_site(driver)
if not login_success:
    print("❌ Initial login failed. Exiting...")
    driver.quit()
    exit(1)

# Main loop for processing categories
for cate in cate_parents:
    cate_parent = cate['cate_name']
    cate_url = cate['cate_url']
    
    print(f"\n📂 Processing category: {cate_parent}")
    
    # Try to access category page
    driver.get(cate_url)
    time.sleep(1)
    
    # Check for unknown error on category page
    if "unknown error" in driver.page_source.lower():
        if not handle_unknown_error(driver, cate_url):
            continue  # Skip to next category if error persists
    
    # Parse total items and calculate pages
    try:
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        total_items_p = soup.find('p', {'id': 'ctl00_Content_SearchFast_ketquaLVNNghe'})
        total_items_spans = total_items_p.find_all('span')
        total_items = total_items_spans[1].get_text(strip=True)
        total_pages = math.ceil(int(total_items) / 20)
        print(f"📊 Category: {cate_parent} - Total pages: {total_pages}")
    except Exception as e:
        print(f"❌ Error calculating total pages for {cate_parent}: {str(e)}")
        continue  # Skip to next category if error occurs
    
    # Loop through pages
    for i in range(1, total_pages):
        page_url = cate_url if i == 1 else f"{cate_url}&Page={i}"
        
        print(f"\n📄 Processing page {i}/{total_pages}")
        
        # Try to access page
        if i > 1:
            driver.get(page_url)
            time.sleep(1)
        
        # Check for unknown error on page
        if "unknown error" in driver.page_source.lower():
            if not handle_unknown_error(driver, page_url):
                continue  # Skip to next page if error persists
        
        # Parse page content
        try:
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            doc_list_div = soup.find('div', {'id': 'ketquaLVNNghe'})
            
            if not doc_list_div:
                print(f"⚠️ No results found on page {i} for {cate_parent}")
                continue
                
            all_list_div = doc_list_div.find_all('div')
            
            # Process each document on the page
            for div in all_list_div:
                left_col_div = div.find('div', {'class': 'left-col'})
                if left_col_div:
                    link_tag = left_col_div.find('a', onclick=True)
                    if link_tag and 'Doc_CT(MemberGA)' in link_tag['onclick']:
                        title = link_tag.get_text(strip=True)
                        doc_link = link_tag['href']
                        
                        # Perform an initial check for duplicates based on title and category
                        if is_duplicate(final_result, title, cate_parent):
                            print(f"⏭️ Skipping already processed document: {title}")
                            continue
                        
                        # Navigate to document page
                        print(f"\n📝 Processing document: {title}")
                        driver.get(doc_link)
                        time.sleep(2)
                        
                        # Check for unknown error on document page
                        if "unknown error" in driver.page_source.lower():
                            if not handle_unknown_error(driver, doc_link):
                                continue  # Skip to next document if error persists
                        
                        # Extract document details
                        try:
                            soup = BeautifulSoup(driver.page_source, 'html.parser')
                            file_p = soup.find('p', {'style': 'font-weight: bold;color: red;padding: 10px;'})
                            file_url = ''
                            if file_p:
                                file_a = file_p.find('a')
                                if file_a and 'href' in file_a.attrs:
                                    file_url = 'https://thuvienphapluat.vn' + file_a['href']
                            
                            # Click download button
                            try:
                                download_button = WebDriverWait(driver, 5).until(
                                    EC.element_to_be_clickable((By.XPATH, '//*[@id="ctl00_Content_ThongTinVB_SpDoanload"]'))
                                )
                                download_button.click()
                                time.sleep(2)
                            except Exception as e:
                                print(f"⚠️ Could not click download button: {str(e)}")
                                # Continue anyway as we might still have useful information
                            
                            # Check for unknown error on download page
                            if "unknown error" in driver.page_source.lower():
                                if not handle_unknown_error(driver, driver.current_url):
                                    continue  # Skip to next document if error persists
                            
                            # Get Vietnamese file URL
                            soup = BeautifulSoup(driver.page_source, 'html.parser')
                            vn_file_a = soup.find('a', {'title': 'Tải văn bản tiếng Việt'})
                            vn_file_url = ''
                            if vn_file_a and 'href' in vn_file_a.attrs:
                                vn_file_url = 'https://thuvienphapluat.vn' + vn_file_a['href']
                            
                            # Second check for duplicates with more complete information
                            if is_duplicate(final_result, title, cate_parent, file_url, vn_file_url):
                                print(f"⏭️ Skipping already processed document (URL match): {title}")
                                continue
                            
                            # Click on outline button
                            try:
                                outline_button = WebDriverWait(driver, 5).until(
                                    EC.element_to_be_clickable((By.XPATH, '//*[@id="ctl00_Content_ThongTinVB_spLuocDo"]'))
                                )
                                outline_button.click()
                                time.sleep(2)
                            except Exception as e:
                                print(f"⚠️ Could not click outline button: {str(e)}")
                                # Continue anyway as we might still have useful information
                            
                            # Check for unknown error on outline page
                            if "unknown error" in driver.page_source.lower():
                                if not handle_unknown_error(driver, driver.current_url):
                                    continue  # Skip to next document if error persists
                            
                            # Extract category details
                            soup = BeautifulSoup(driver.page_source, 'html.parser')
                            cate_blocks = soup.find_all('div', {'class': 'att'})
                            detail_info = []
                            for block in cate_blocks:
                                hd_div = block.find('div', {'class': 'hd fl'})
                                ds_div = block.find('div', {'class': 'ds fl'})
                                if hd_div and ds_div:
                                    cate_name = hd_div.get_text(strip=True)
                                    cate_info = ds_div.get_text(strip=True)
                                    detail_info.append({cate_name: cate_info})
                            
                            # Create result object
                            result = {
                                'title': title,
                                'cate_parent': cate_parent,
                                'detail_info': detail_info,
                                'file_url': file_url,
                                'vn_file_url': vn_file_url
                            }
                            
                            # One final check before adding to results
                            if not is_duplicate(final_result, title, cate_parent, file_url, vn_file_url):
                                print(result)
                                print('---------------------------------------------------')
                                
                                # Add to results and save immediately
                                final_result.append(result)
                                save_results(final_result)  # Moved save_results here
                            else:
                                print(f"⚠️ Document appeared to be non-duplicate initially but was found to be duplicate after processing: {title}")
                                
                        except Exception as e:
                            print(f"❌ Error processing document details: {str(e)}")
                            continue  # Skip to next document if error occurs
                            
        except Exception as e:
            print(f"❌ Error processing page {i}: {str(e)}")
            continue  # Skip to next page if error occurs

print("\n✅ Scraping completed. Saved final results.")
print(f"📊 Total documents processed: {len(final_result)}")

driver.quit()