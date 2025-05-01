from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class MovieLink(BaseModel):
    quality: str = Field(default="Unknown")
    url: str
    language: Optional[str] = None
    size: Optional[str] = None


class CastMember(BaseModel):
    name: str
    character: Optional[str] = None
    profile_image: Optional[str] = None


class Movie(BaseModel):
    title: str
    source: str
    source_url: str
    links: List[MovieLink] = []
    poster: Optional[str] = None
    backdrop: Optional[str] = None
    tmdb_id: Optional[int] = None
    tmdb_title: Optional[str] = None
    overview: Optional[str] = None
    release_date: Optional[str] = None
    runtime: Optional[int] = None
    genres: List[str] = []
    rating: Optional[float] = None
    cast: List[CastMember] = []
    language: Optional[str] = None


class MovieSearchResult(BaseModel):
    query: str
    source: str
    total: int
    movies: List[Movie]
