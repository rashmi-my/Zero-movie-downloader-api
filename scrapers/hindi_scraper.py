import requests
from bs4 import BeautifulSoup
import re
from typing import List, Dict, Any, Optional
import urllib.parse

class HindiScraper:
    BASE_URL = "https://hdhub4u.graphics"
    
    @staticmethod
    def _get_soup(url: str) -> Optional[BeautifulSoup]:
        """Get BeautifulSoup object from URL"""
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Accept-Language": "en-US,en;q=0.9",
            "Referer": "https://hdhub4u.graphics/"
        }
        try:
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                return BeautifulSoup(response.text, "html.parser")
            return None
        except Exception as e:
            print(f"Error fetching {url}: {str(e)}")
            return None
    
    @staticmethod
    def search_movies(query: str) -> List[Dict[str, Any]]:
        """Search for movies based on query"""
        results = []
        
        # Search URL construction
        search_url = f"{HindiScraper.BASE_URL}/?s={urllib.parse.quote(query)}"
        soup = HindiScraper._get_soup(search_url)
        
        if not soup:
            return results
        
        # Find movie entries - adapt selectors based on actual site structure
        movie_entries = soup.select("article.post")
        
        for movie in movie_entries:
            try:
                title_elem = movie.select_one("h2.entry-title a") or movie.select_one("h2 a")
                if not title_elem:
                    continue
                
                title = title_elem.text.strip()
                movie_url = title_elem["href"]
                
                # Determine language (Hindi/English)
                language = "Hindi"  # Default
                if "english" in title.lower() or "dual audio" in title.lower():
                    language = "Hindi/English"
                
                # Get poster if available
                poster = None
                poster_elem = movie.select_one("img")
                if poster_elem and "src" in poster_elem.attrs:
                    poster = poster_elem["src"]
                    # Fix relative URLs
                    if poster and not poster.startswith(("http://", "https://")):
                        poster = urllib.parse.urljoin(HindiScraper.BASE_URL, poster)
                
                movie_data = {
                    "title": title,
                    "source": "hdhub4u",
                    "source_url": movie_url,
                    "poster": poster,
                    "language": language,
                    "links": []
                }
                
                results.append(movie_data)
            except Exception as e:
                print(f"Error parsing movie entry: {str(e)}")
                continue
        
        return results
    
    @staticmethod
    def get_movie_details(movie_url: str) -> Dict[str, Any]:
        """Get detailed information and links for a specific movie"""
        soup = HindiScraper._get_soup(movie_url)
        
        movie_data = {
            "title": "",
            "source": "hdhub4u",
            "source_url": movie_url,
            "language": "Hindi",
            "links": []
        }
        
        if not soup:
            return movie_data
        
        # Extract title
        title_elem = soup.select_one("h1.entry-title")
        if title_elem:
            movie_data["title"] = title_elem.text.strip()
            
            # Try to determine language from title
            if "english" in movie_data["title"].lower() or "dual audio" in movie_data["title"].lower():
                movie_data["language"] = "Hindi/English"
        
        # Extract poster
        poster_elem = soup.select_one(".entry-content img")
        if poster_elem and "src" in poster_elem.attrs:
            movie_data["poster"] = poster_elem["src"]
        
        # Extract download links
        # Look for download links with quality information
        link_patterns = [
            (r'(\d+p)', soup.select("a[href*='download']")),
            (r'(\d+p)', soup.select("a.dwnlink")),
            (r'(\d+p)', soup.select("a[href*='.mkv']")),
            (r'(\d+p)', soup.select("a[href*='.mp4']")),
            (r'(\d+\s*MB)', soup.select("a[href*='download']"))
        ]
        
        for pattern, elements in link_patterns:
            for link in elements:
                try:
                    link_text = link.text.strip()
                    link_url = link["href"]
                    
                    # Skip if it's not a real download link
                    if not link_url or link_url == "#" or link_url.startswith("javascript:"):
                        continue
                    
                    # Try to extract quality information
                    quality = "Unknown"
                    size = None
                    
                    # Look for quality in the link text
                    quality_match = re.search(pattern, link_text)
                    if quality_match:
                        quality = quality_match.group(1)
                    
                    # Look for size information
                    size_match = re.search(r'(\d+\s*(?:GB|MB|KB))', link_text)
                    if size_match:
                        size = size_match.group(1)
                    
                    movie_data["links"].append({
                        "quality": quality,
                        "url": link_url,
                        "language": movie_data["language"],
                        "size": size
                    })
                except Exception as e:
                    print(f"Error extracting link: {str(e)}")
                    continue
        
        return movie_data
