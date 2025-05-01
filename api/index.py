from fastapi import FastAPI, Query, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import sys
import os

# Add project root to path to allow imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scrapers import TamilScraper, HindiScraper, EnglishScraper
from services import TMDBService
from models import Movie, MovieSearchResult

app = FastAPI(title="Movie API", 
              description="API for scraping movie information and streaming links",
              version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods
    allow_headers=["*"],  # Allow all headers
)

# Error handling middleware
@app.middleware("http")
async def errors_middleware(request: Request, call_next):
    try:
        return await call_next(request)
    except Exception as exc:
        return JSONResponse(
            status_code=500,
            content={"detail": str(exc)}
        )

@app.get("/")
def read_root():
    """Root endpoint with API information"""
    return {
        "api": "Movie Scraper API",
        "version": "1.0.0",
        "endpoints": {
            "search": "/api/search?q={query}&source={source}",
            "movie": "/api/movie?url={url}&source={source}",
            "tmdb": "/api/tmdb?title={title}"
        }
    }

@app.get("/api/search")
def search_movies(
    q: str = Query(..., description="Search query"),
    source: str = Query(None, description="Source to search (tamil, hindi, english, all)")
):
    """Search for movies across different sources"""
    if not q:
        raise HTTPException(status_code=400, detail="Search query cannot be empty")
    
    results = []
    
    # Determine which sources to search
    source = source.lower() if source else "all"
    
    try:
        # Search Tamil source
        if source in ["tamil", "all"]:
            tamil_results = TamilScraper.search_movies(q)
            results.extend(tamil_results)
        
        # Search Hindi source
        if source in ["hindi", "all"]:
            hindi_results = HindiScraper.search_movies(q)
            results.extend(hindi_results)
        
        # Search English source
        if source in ["english", "all"]:
            english_results = EnglishScraper.search_movies(q)
            results.extend(english_results)
        
        # Create response
        response = MovieSearchResult(
            query=q,
            source=source,
            total=len(results),
            movies=[Movie(**movie) for movie in results]
        )
        
        return response.dict()
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error searching movies: {str(e)}")


@app.get("/api/movie")
def get_movie_details(
    url: str = Query(..., description="Movie URL to fetch details for"),
    source: str = Query(..., description="Source of the movie (tamil, hindi, english)"),
    enrich: bool = Query(True, description="Enrich with TMDB data")
):
    """Get detailed information about a specific movie"""
    if not url:
        raise HTTPException(status_code=400, detail="Movie URL cannot be empty")
    
    if not source:
        raise HTTPException(status_code=400, detail="Source must be specified")
    
    source = source.lower()
    
    try:
        # Fetch movie details based on source
        movie_data = None
        
        if source == "tamil":
            movie_data = TamilScraper.get_movie_details(url)
        elif source == "hindi":
            movie_data = HindiScraper.get_movie_details(url)
        elif source == "english":
            movie_data = EnglishScraper.get_movie_details(url)
        else:
            raise HTTPException(status_code=400, detail=f"Invalid source: {source}")
        
        # Enrich with TMDB data if requested
        if enrich and movie_data:
            movie_data = TMDBService.enrich_movie_data(movie_data)
        
        return Movie(**movie_data).dict()
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching movie details: {str(e)}")


@app.get("/api/tmdb")
def get_tmdb_info(
    title: str = Query(..., description="Movie title to search on TMDB"),
    movie_id: int = Query(None, description="Optional TMDB ID if already known")
):
    """Get movie information from TMDB"""
    try:
        if movie_id:
            # If ID is provided, get details directly
            movie_details = TMDBService.get_movie_details(movie_id)
            if not movie_details:
                raise HTTPException(status_code=404, detail=f"Movie with ID {movie_id} not found on TMDB")
            return movie_details
        
        # Search by title
        if not title:
            raise HTTPException(status_code=400, detail="Movie title cannot be empty")
        
        movie_basic = TMDBService.search_movie(title)
        if not movie_basic:
            raise HTTPException(status_code=404, detail=f"Movie '{title}' not found on TMDB")
        
        # Get detailed information
        movie_id = movie_basic.get("id")
        movie_details = TMDBService.get_movie_details(movie_id)
        
        return movie_details or movie_basic
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching TMDB data: {str(e)}")


@app.get("/api/trending")
def get_trending_movies(
    source: str = Query("all", description="Source to get trending movies from (tamil, hindi, english, all)")
):
    """Get trending/recent movies from different sources"""
    source = source.lower()
    trending_movies = []
    
    try:
        # Tamil trending (homepage movies)
        if source in ["tamil", "all"]:
            tamil_soup = TamilScraper._get_soup(TamilScraper.BASE_URL)
            if tamil_soup:
                tamil_movies = TamilScraper.search_movies("")[:8]  # Get first 8 results
                trending_movies.extend(tamil_movies)
        
        # Hindi trending
        if source in ["hindi", "all"]:
            hindi_soup = HindiScraper._get_soup(HindiScraper.BASE_URL)
            if hindi_soup:
                hindi_movies = HindiScraper.search_movies("")[:8]  # Get first 8 results
                trending_movies.extend(hindi_movies)
        
        # English trending
        if source in ["english", "all"]:
            english_soup = EnglishScraper._get_soup(EnglishScraper.BASE_URL)
            if english_soup:
                english_movies = EnglishScraper.search_movies("")[:8]  # Get first 8 results
                trending_movies.extend(english_movies)
        
        # Create response
        response = {
            "source": source,
            "total": len(trending_movies),
            "movies": [Movie(**movie).dict() for movie in trending_movies]
        }
        
        return response
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching trending movies: {str(e)}")
