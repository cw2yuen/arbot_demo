import requests
from bs4 import BeautifulSoup
import json
import time
import os
from urllib.parse import urljoin, urlparse, urlunparse
import re
from collections import deque
import hashlib

class EnhancedArboDentalCrawler:
    def __init__(self, base_url="https://arbodentalcare.com/", delay=1, max_pages=100):
        self.base_url = base_url
        self.delay = delay
        self.max_pages = max_pages
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        self.scraped_data = []
        self.visited_urls = set()
        self.url_queue = deque([base_url])
        self.sitemap_urls = []
        
    def discover_sitemap(self):
        """Try to discover sitemap from robots.txt and common locations"""
        print("🔍 Discovering sitemap...")
        
        # Check robots.txt
        try:
            robots_url = urljoin(self.base_url, '/robots.txt')
            response = self.session.get(robots_url, timeout=10)
            if response.status_code == 200:
                for line in response.text.split('\n'):
                    if 'sitemap:' in line.lower():
                        sitemap_url = line.split(':', 1)[1].strip()
                        self.sitemap_urls.append(sitemap_url)
                        print(f"✅ Found sitemap in robots.txt: {sitemap_url}")
        except Exception as e:
            print(f"⚠️ Could not check robots.txt: {e}")
        
        # Check common sitemap locations
        common_sitemaps = [
            '/sitemap.xml',
            '/sitemap_index.xml',
            '/sitemap1.xml',
            '/sitemap.php'
        ]
        
        for sitemap_path in common_sitemaps:
            try:
                sitemap_url = urljoin(self.base_url, sitemap_path)
                response = self.session.get(sitemap_url, timeout=10)
                if response.status_code == 200:
                    self.sitemap_urls.append(sitemap_url)
                    print(f"✅ Found sitemap at: {sitemap_url}")
            except Exception as e:
                continue
        
        return self.sitemap_urls
    
    def parse_sitemap(self, sitemap_url):
        """Parse XML sitemap to extract URLs"""
        try:
            response = self.session.get(sitemap_url, timeout=10)
            if response.status_code != 200:
                return []
            
            soup = BeautifulSoup(response.content, 'xml')
            urls = []
            
            # Look for URL tags
            for url_tag in soup.find_all(['url', 'loc']):
                if url_tag.name == 'url':
                    loc_tag = url_tag.find('loc')
                    if loc_tag:
                        urls.append(loc_tag.text.strip())
                elif url_tag.name == 'loc':
                    urls.append(url_tag.text.strip())
            
            # Filter URLs to only include Arbo Dental Care pages
            filtered_urls = []
            for url in urls:
                if 'arbodentalcare.com' in url and url not in self.visited_urls:
                    filtered_urls.append(url)
            
            print(f"📋 Found {len(filtered_urls)} URLs in sitemap")
            return filtered_urls
            
        except Exception as e:
            print(f"❌ Error parsing sitemap {sitemap_url}: {e}")
            return []
    
    def discover_links(self, html_content, current_url):
        """Discover all links from a page"""
        soup = BeautifulSoup(html_content, 'html.parser')
        links = []
        
        # Find all anchor tags
        for anchor in soup.find_all('a', href=True):
            href = anchor['href']
            
            # Convert relative URLs to absolute
            absolute_url = urljoin(current_url, href)
            
            # Only include Arbo Dental Care URLs
            if 'arbodentalcare.com' in absolute_url:
                # Clean the URL (remove fragments, query params)
                parsed = urlparse(absolute_url)
                clean_url = urlunparse((parsed.scheme, parsed.netloc, parsed.path, '', '', ''))
                
                if clean_url not in self.visited_urls and clean_url not in links:
                    links.append(clean_url)
        
        return links
    
    def should_crawl_url(self, url):
        """Determine if a URL should be crawled"""
        # Skip if already visited
        if url in self.visited_urls:
            return False
        
        # Skip if we've reached max pages
        if len(self.scraped_data) >= self.max_pages:
            return False
        
        # Skip non-HTML files
        skip_extensions = ['.pdf', '.jpg', '.jpeg', '.png', '.gif', '.css', '.js', '.xml']
        if any(url.lower().endswith(ext) for ext in skip_extensions):
            return False
        
        # Skip external domains
        if not url.startswith(self.base_url):
            return False
        
        return True
    
    def scrape_page(self, url):
        """Scrape a single page and extract relevant information"""
        if not self.should_crawl_url(url):
            return None
        
        try:
            print(f"🔄 Scraping: {url}")
            response = self.session.get(url, timeout=15)
            response.raise_for_status()
            
            # Mark as visited
            self.visited_urls.add(url)
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract page data
            page_data = {
                'url': url,
                'title': self._extract_title(soup),
                'content': self._extract_content(soup),
                'metadata': self._extract_metadata(soup),
                'links_found': self.discover_links(response.content, url)
            }
            
            self.scraped_data.append(page_data)
            
            # Add discovered links to queue
            for link in page_data['links_found']:
                if link not in self.visited_urls and link not in [item for item in self.url_queue]:
                    self.url_queue.append(link)
            
            print(f"✅ Scraped successfully. Found {len(page_data['links_found'])} links")
            time.sleep(self.delay)
            
            return page_data
            
        except Exception as e:
            print(f"❌ Error scraping {url}: {str(e)}")
            self.visited_urls.add(url)  # Mark as visited to avoid retrying
            return None
    
    def _extract_title(self, soup):
        """Extract page title"""
        title_tag = soup.find('title')
        if title_tag:
            return title_tag.get_text(strip=True)
        
        # Fallback to h1
        h1_tag = soup.find('h1')
        if h1_tag:
            return h1_tag.get_text(strip=True)
        
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
    
    def crawl_site(self):
        """Crawl the entire Arbo Dental Care website"""
        print("🚀 Starting comprehensive website crawl...")
        
        # First, try to discover sitemap
        sitemap_urls = self.discover_sitemap()
        
        # Parse sitemaps and add URLs to queue
        for sitemap_url in sitemap_urls:
            sitemap_urls_found = self.parse_sitemap(sitemap_url)
            for url in sitemap_urls_found:
                if url not in [item for item in self.url_queue]:
                    self.url_queue.append(url)
        
        # Start crawling from queue
        while self.url_queue and len(self.scraped_data) < self.max_pages:
            url = self.url_queue.popleft()
            if self.should_crawl_url(url):
                self.scrape_page(url)
        
        print(f"🎉 Crawling completed! Scraped {len(self.scraped_data)} pages.")
        return self.scraped_data
    
    def save_data(self, filename="arbo_dental_data_comprehensive.json"):
        """Save scraped data to JSON file"""
        os.makedirs('data', exist_ok=True)
        filepath = os.path.join('data', filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.scraped_data, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Data saved to {filepath}")
        return filepath
    
    def get_crawl_summary(self):
        """Get summary of the crawl"""
        return {
            'total_pages_scraped': len(self.scraped_data),
            'total_urls_discovered': len(self.visited_urls),
            'sitemaps_found': len(self.sitemap_urls),
            'pages_by_type': self._categorize_pages()
        }
    
    def _categorize_pages(self):
        """Categorize pages by content type"""
        categories = {}
        for page in self.scraped_data:
            page_type = 'general'
            
            # Determine page type based on URL and content
            url_lower = page['url'].lower()
            if 'team' in url_lower or 'staff' in url_lower:
                page_type = 'team'
            elif 'services' in url_lower or 'treatments' in url_lower:
                page_type = 'services'
            elif 'about' in url_lower:
                page_type = 'about'
            elif 'contact' in url_lower:
                page_type = 'contact'
            elif 'blog' in url_lower or 'news' in url_lower:
                page_type = 'blog'
            
            categories[page_type] = categories.get(page_type, 0) + 1
        
        return categories

def main():
    """Main function to run the enhanced crawler"""
    print("🦷 Enhanced Arbo Dental Care Website Crawler")
    print("=" * 60)
    
    # Create and run crawler
    crawler = EnhancedArboDentalCrawler(max_pages=50)  # Limit to 50 pages for reasonable crawl time
    
    # Crawl the site
    data = crawler.crawl_site()
    
    # Save data
    crawler.save_data()
    
    # Print summary
    summary = crawler.get_crawl_summary()
    print("\n" + "=" * 60)
    print("📊 CRAWL SUMMARY")
    print("=" * 60)
    print(f"Total pages scraped: {summary['total_pages_scraped']}")
    print(f"Total URLs discovered: {summary['total_urls_discovered']}")
    print(f"Sitemaps found: {summary['sitemaps_found']}")
    print("\nPages by category:")
    for category, count in summary['pages_by_type'].items():
        print(f"  {category.capitalize()}: {count}")
    
    print("\n🎯 Next steps:")
    print("1. Review the comprehensive data file")
    print("2. Run: python data_preparation/knowledge_base.py")
    print("3. Test the enhanced AI agent with more comprehensive knowledge")

if __name__ == "__main__":
    main()


