import requests
from bs4 import BeautifulSoup
import re
from typing import List, Dict, Any, Optional
import urllib.parse

class EnglishScraper:
    BASE_URL = "https://sflix.to"
    
    @staticmethod
    def _get_soup(url: str) -> Optional[BeautifulSoup]:
        """Get BeautifulSoup object from URL"""
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Accept-Language": "en-US,en;q=0.9",
            "Referer": "https://sflix.to/"
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
        search_url = f"{EnglishScraper.BASE_URL}/search/{urllib.parse.quote(query)}"
        soup = EnglishScraper._get_soup(search_url)
        
        if not soup:
            return results
        
        # Find movie entries - adapt selectors based on actual site structure
        movie_entries = soup.select(".film-poster")
        
        for movie in movie_entries:
            try:
                link_elem = movie.select_one("a")
                if not link_elem or not link_elem.has_attr("href"):
                    continue
                
                movie_url = link_elem["href"]
                # Make sure URL is absolute
                if not movie_url.startswith(("http://", "https://")):
                    movie_url = urllib.parse.urljoin(EnglishScraper.BASE_URL, movie_url)
                
                # Get title
                title = ""
                title_elem = movie.select_one("a[title]")
                if title_elem and title_elem.has_attr("title"):
                    title = title_elem["title"].strip()
                
                # Get poster if available
                poster = None
                poster_elem = movie.select_one("img")
                if poster_elem and poster_elem.has_attr("data-src"):
                    poster = poster_elem["data-src"]
                elif poster_elem and poster_elem.has_attr("src"):
                    poster = poster_elem["src"]
                
                # Fix relative URLs for poster
                if poster and not poster.startswith(("http://", "https://")):
                    poster = urllib.parse.urljoin(EnglishScraper.BASE_URL, poster)
                
                movie_data = {
                    "title": title,
                    "source": "sflix",
                    "source_url": movie_url,
                    "poster": poster,
                    "language": "English",
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
        soup = EnglishScraper._get_soup(movie_url)
        
        movie_data = {
            "title": "",
            "source": "sflix",
            "source_url": movie_url,
            "language": "English",
            "links": []
        }
        
        if not soup:
            return movie_data
        
        # Extract title
        title_elem = soup.select_one("h2.heading-name")
        if title_elem:
            movie_data["title"] = title_elem.text.strip()
        
        # Extract poster
        poster_elem = soup.select_one(".film-poster img")
        if poster_elem:
            if poster_elem.has_attr("data-src"):
                movie_data["poster"] = poster_elem["data-src"]
            elif poster_elem.has_attr("src"):
                movie_data["poster"] = poster_elem["src"]
        
        # Extract streaming servers/links
        server_elements = soup.select(".server-item")
        for server in server_elements:
            try:
                server_name = "Unknown"
                server_label = server.select_one(".name")
                if server_label:
                    server_name = server_label.text.strip()
                
                # Extract link (might be data attribute or javascript)
                link_elem = server.select_one("a")
                if not link_elem:
                    continue
                
                # Try to extract link from data attributes or href
                link_url = None
                if link_elem.has_attr("data-id"):
                    # This is likely a dynamic link loaded via JS
                    server_id = link_elem["data-id"]
                    # Generate watch URL
                    if movie_url.endswith("/"):
                        link_url = f"{movie_url}watch?server={server_id}"
                    else:
                        link_url = f"{movie_url}/watch?server={server_id}"
                elif link_elem.has_attr("href"):
                    link_url = link_elem["href"]
                    # Make absolute URL if needed
                    if not link_url.startswith(("http://", "https://")):
                        link_url = urllib.parse.urljoin(EnglishScraper.BASE_URL, link_url)
                
                if link_url:
                    movie_data["links"].append({
                        "quality": server_name,
                        "url": link_url,
                        "language": "English"
                    })
            except Exception as e:
                print(f"Error extracting server: {str(e)}")
                continue
                
        # If no servers found directly, try to find the watch button
        if not movie_data["links"]:
            watch_btn = soup.select_one(".btn-play")
            if watch_btn and watch_btn.has_attr("href"):
                watch_url = watch_btn["href"]
                if not watch_url.startswith(("http://", "https://")):
                    watch_url = urllib.parse.urljoin(EnglishScraper.BASE_URL, watch_url)
                
                movie_data["links"].append({
                    "quality": "Default",
                    "url": watch_url,
                    "language": "English"
                })
        
        return movie_data
