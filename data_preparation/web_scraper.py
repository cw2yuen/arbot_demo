import requests
from bs4 import BeautifulSoup
import json
import time
import os
from urllib.parse import urljoin, urlparse
import re

class ArboDentalScraper:
    def __init__(self, base_url="https://arbodentalcare.com/", delay=2):
        self.base_url = base_url
        self.delay = delay
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        self.scraped_data = []
        
    def scrape_page(self, url):
        """Scrape a single page and extract relevant information"""
        try:
            print(f"Scraping: {url}")
            response = self.session.get(url)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract page data
            page_data = {
                'url': url,
                'title': self._extract_title(soup),
                'content': self._extract_content(soup),
                'metadata': self._extract_metadata(soup)
            }
            
            self.scraped_data.append(page_data)
            time.sleep(self.delay)
            
        except Exception as e:
            print(f"Error scraping {url}: {str(e)}")
    
    def _extract_title(self, soup):
        """Extract page title"""
        title_tag = soup.find('title')
        if title_tag:
            return title_tag.get_text(strip=True)
        return ""
    
    def _extract_content(self, soup):
        """Extract main content from the page"""
        content = []
        
        # Extract main headings and text
        for tag in soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'li']):
            text = tag.get_text(strip=True)
            if text and len(text) > 10:  # Filter out very short text
                content.append({
                    'type': tag.name,
                    'text': text
                })
        
        # Extract specific sections like team info, services, contact info
        team_section = self._extract_team_info(soup)
        if team_section:
            content.append(team_section)
            
        contact_section = self._extract_contact_info(soup)
        if contact_section:
            content.append(contact_section)
            
        services_section = self._extract_services_info(soup)
        if services_section:
            content.append(services_section)
        
        return content
    
    def _extract_team_info(self, soup):
        """Extract team member information"""
        team_info = []
        
        # Look for team member sections
        team_sections = soup.find_all('div', class_=re.compile(r'team|staff', re.I))
        
        for section in team_sections:
            # Look for individual team member info
            members = section.find_all(['h3', 'h4', 'h5', 'h6'])
            for member in members:
                member_text = member.get_text(strip=True)
                if member_text and any(keyword in member_text.lower() for keyword in ['dr.', 'doctor', 'christina', 'carol', 'guadalupe', 'gem']):
                    # Get the next paragraph or list item for bio
                    bio = ""
                    next_elem = member.find_next_sibling()
                    if next_elem and next_elem.name in ['p', 'li']:
                        bio = next_elem.get_text(strip=True)
                    
                    team_info.append({
                        'name': member_text,
                        'bio': bio,
                        'type': 'team_member'
                    })
        
        if team_info:
            return {
                'type': 'team_section',
                'data': team_info
            }
        return None
    
    def _extract_contact_info(self, soup):
        """Extract contact information"""
        contact_info = {}
        
        # Look for phone numbers
        phone_pattern = r'\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}'
        phone_matches = re.findall(phone_pattern, soup.get_text())
        if phone_matches:
            contact_info['phone'] = phone_matches[0]
        
        # Look for email addresses
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        email_matches = re.findall(email_pattern, soup.get_text())
        if email_matches:
            contact_info['email'] = email_matches[0]
        
        # Look for address
        address_keywords = ['holland st', 'bradford', 'on', 'l3z']
        address_text = ""
        for tag in soup.find_all(['p', 'div', 'span']):
            text = tag.get_text(strip=True)
            if any(keyword in text.lower() for keyword in address_keywords):
                address_text = text
                break
        
        if address_text:
            contact_info['address'] = address_text
        
        if contact_info:
            return {
                'type': 'contact_info',
                'data': contact_info
            }
        return None
    
    def _extract_services_info(self, soup):
        """Extract services information"""
        services = []
        
        # Look for services-related text
        service_keywords = ['dental', 'cleaning', 'implant', 'crown', 'filling', 'whitening', 'orthodontics']
        
        for tag in soup.find_all(['p', 'li', 'div']):
            text = tag.get_text(strip=True)
            if any(keyword in text.lower() for keyword in service_keywords):
                if len(text) > 20 and len(text) < 500:  # Reasonable length for service description
                    services.append(text)
        
        if services:
            return {
                'type': 'services',
                'data': services
            }
        return None
    
    def _extract_metadata(self, soup):
        """Extract additional metadata"""
        metadata = {}
        
        # Extract meta description
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        if meta_desc:
            metadata['description'] = meta_desc.get('content', '')
        
        # Extract language
        html_tag = soup.find('html')
        if html_tag:
            metadata['language'] = html_tag.get('lang', 'en')
        
        return metadata
    
    def scrape_site(self):
        """Scrape the main pages of the Arbo Dental Care website"""
        print("Starting to scrape Arbo Dental Care website...")
        
        # Main pages to scrape
        main_pages = [
            self.base_url,
            f"{self.base_url}#about",
            f"{self.base_url}#team",
            f"{self.base_url}#services",
            f"{self.base_url}#contact"
        ]
        
        for page in main_pages:
            self.scrape_page(page)
        
        print(f"Scraping completed. Scraped {len(self.scraped_data)} pages.")
        return self.scraped_data
    
    def save_data(self, filename="arbo_dental_data.json"):
        """Save scraped data to JSON file"""
        os.makedirs('data', exist_ok=True)
        filepath = os.path.join('data', filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.scraped_data, f, indent=2, ensure_ascii=False)
        
        print(f"Data saved to {filepath}")
        return filepath

def main():
    """Main function to run the scraper"""
    scraper = ArboDentalScraper()
    data = scraper.scrape_site()
    scraper.save_data()
    
    # Print summary
    print("\n=== SCRAPING SUMMARY ===")
    print(f"Total pages scraped: {len(data)}")
    
    for page in data:
        print(f"\nPage: {page['url']}")
        print(f"Title: {page['title']}")
        print(f"Content sections: {len(page['content'])}")

if __name__ == "__main__":
    main()


