import requests
from bs4 import BeautifulSoup
import re
from typing import List, Dict, Any, Optional
import urllib.parse

class TamilScraper:
    BASE_URL = "http://mv.tamiltech.live"
    
    @staticmethod
    def _get_soup(url: str) -> Optional[BeautifulSoup]:
        """Get BeautifulSoup object from URL"""
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
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
        search_url = f"{TamilScraper.BASE_URL}/?s={urllib.parse.quote(query)}"
        soup = TamilScraper._get_soup(search_url)
        
        if not soup:
            return results
        
        # Find movie entries
        movie_entries = soup.select("article.item")
        
        for movie in movie_entries:
            try:
                title_elem = movie.select_one("h3.title a")
                if not title_elem:
                    continue
                
                title = title_elem.text.strip()
                movie_url = title_elem["href"]
                
                # Get poster if available
                poster = None
                poster_elem = movie.select_one("img.poster")
                if poster_elem and "src" in poster_elem.attrs:
                    poster = poster_elem["src"]
                    # Fix relative URLs
                    if poster and not poster.startswith(("http://", "https://")):
                        poster = urllib.parse.urljoin(TamilScraper.BASE_URL, poster)
                
                movie_data = {
                    "title": title,
                    "source": "tamiltech",
                    "source_url": movie_url,
                    "poster": poster,
                    "language": "Tamil",
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
        soup = TamilScraper._get_soup(movie_url)
        
        movie_data = {
            "title": "",
            "source": "tamiltech",
            "source_url": movie_url,
            "language": "Tamil",
            "links": []
        }
        
        if not soup:
            return movie_data
        
        # Extract title
        title_elem = soup.select_one("h1.entry-title")
        if title_elem:
            movie_data["title"] = title_elem.text.strip()
        
        # Extract poster
        poster_elem = soup.select_one(".wp-post-image")
        if poster_elem and "src" in poster_elem.attrs:
            movie_data["poster"] = poster_elem["src"]
        
        # Extract stream links
        link_elements = soup.select("a[href*='?url=']")
        for link in link_elements:
            try:
                link_url = link["href"]
                
                # Try to extract quality information
                quality = "Unknown"
                quality_text = link.text.strip()
                
                # Look for quality patterns like "720p", "1080p", etc.
                quality_match = re.search(r'(\d+p|\d+\s*[kK])', quality_text)
                if quality_match:
                    quality = quality_match.group(1)
                
                movie_data["links"].append({
                    "quality": quality,
                    "url": link_url,
                    "language": "Tamil"
                })
            except Exception as e:
                print(f"Error extracting link: {str(e)}")
                continue
        
        # Try to extract additional download links from iframes
        iframe_elements = soup.select("iframe")
        for iframe in iframe_elements:
            if "src" in iframe.attrs:
                iframe_src = iframe["src"]
                if iframe_src.startswith("//"):
                    iframe_src = "https:" + iframe_src
                
                # Only add if it seems like a video source
                if any(domain in iframe_src for domain in ["drive.google", "youtube", "vimeo", "dailymotion"]):
                    movie_data["links"].append({
                        "quality": "Embed",
                        "url": iframe_src,
                        "language": "Tamil"
                    })
        
        return movie_data
