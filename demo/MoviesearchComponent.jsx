import React, { useState } from 'react';

const MovieSearch = () => {
  const [query, setQuery] = useState('');
  const [source, setSource] = useState('all');
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState(null);
  const [selectedMovie, setSelectedMovie] = useState(null);
  const [movieDetails, setMovieDetails] = useState(null);

  const API_BASE_URL = 'https://your-vercel-deployment-url.vercel.app';

  const handleSearch = async (e) => {
    e.preventDefault();
    if (!query.trim()) return;
    
    setLoading(true);
    try {
      const response = await fetch(`${API_BASE_URL}/api/search?q=${encodeURIComponent(query)}&source=${source}`);
      const data = await response.json();
      setResults(data);
      setSelectedMovie(null);
      setMovieDetails(null);
    } catch (error) {
      console.error('Error searching movies:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleGetDetails = async (movie) => {
    setSelectedMovie(movie);
    setMovieDetails(null);
    
    try {
      const response = await fetch(`${API_BASE_URL}/api/movie?url=${encodeURIComponent(movie.source_url)}&source=${movie.source}`);
      const data = await response.json();
      setMovieDetails(data);
    } catch (error) {
      console.error('Error fetching movie details:', error);
    }
  };

  return (
    <div className="container mx-auto p-4">
      <h1 className="text-3xl font-bold mb-6">Movie Search</h1>
      
      <form onSubmit={handleSearch} className="mb-6">
        <div className="flex flex-col sm:flex-row gap-4">
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Search for movies..."
            className="border border-gray-300 rounded px-4 py-2 flex-grow"
          />
          
          <select
            value={source}
            onChange={(e) => setSource(e.target.value)}
            className="border border-gray-300 rounded px-4 py-2"
          >
            <option value="all">All Sources</option>
            <option value="tamil">Tamil</option>
            <option value="hindi">Hindi</option>
            <option value="english">English</option>
          </select>
          
          <button
            type="submit"
            className="bg-blue-600 text-white px-6 py-2 rounded"
            disabled={loading}
          >
            {loading ? 'Searching...' : 'Search'}
          </button>
        </div>
      </form>
      
      {results && (
        <div className="results mb-8">
          <h2 className="text-xl font-semibold mb-4">Search Results ({results.total})</h2>
          
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
            {results.movies.map((movie, index) => (
              <div key={index} className="movie-card border rounded-lg overflow-hidden shadow-md">
                <div className="aspect-w-2 aspect-h-3 bg-gray-200">
                  {movie.poster ? (
                    <img 
                      src={movie.poster} 
                      alt={movie.title}
                      className="w-full h-full object-cover"
                      onError={(e) => {e.target.onerror = null; e.target.src = 'https://via.placeholder.com/300x450?text=No+Image'}}
                    />
                  ) : (
                    <div className="w-full h-full flex items-center justify-center bg-gray-100">
                      No Image
                    </div>
                  )}
                </div>
                
                <div className="p-4">
                  <h3 className="font-semibold text-lg mb-2 line-clamp-2">{movie.title}</h3>
                  <p className="text-sm text-gray-600 mb-2">Source: {movie.source}</p>
                  <p className="text-sm text-gray-600 mb-4">Language: {movie.language}</p>
                  
                  <button
                    onClick={() => handleGetDetails(movie)}
                    className="bg-blue-600 text-white w-full py-2 rounded"
                  >
                    View Details
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
      
      {selectedMovie && movieDetails && (
        <div className="movie-details border rounded-lg p-6">
          <div className="flex flex-col md:flex-row gap-8">
            <div className="w-full md:w-1/3 lg:w-1/4">
              {movieDetails.poster ? (
                <img 
                  src={movieDetails.poster} 
                  alt={movieDetails.title}
                  className="w-full rounded-lg shadow-lg"
                  onError={(e) => {e.target.onerror = null; e.target.src = 'https://via.placeholder.com/300x450?text=No+Image'}}
                />
              ) : (
                <div className="w-full h-96 flex items-center justify-center bg-gray-100 rounded-lg">
                  No Image
                </div>
              )}
            </div>
            
            <div className="flex-1">
              <h2 className="text-2xl font-bold mb-4">{movieDetails.title}</h2>
              
              {movieDetails.overview && (
                <div className="mb-4">
                  <h3 className="text-lg font-semibold mb-2">Overview</h3>
                  <p>{movieDetails.overview}</p>
                </div>
              )}
              
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 mb-6">
                {movieDetails.release_date && (
                  <div>
                    <span className="font-semibold">Release Date:</span> {movieDetails.release_date}
                  </div>
                )}
                
                {movieDetails.runtime && (
                  <div>
                    <span className="font-semibold">Runtime:</span> {movieDetails.runtime} minutes
                  </div>
                )}
                
                {movieDetails.rating && (
                  <div>
                    <span className="font-semibold">Rating:</span> {movieDetails.rating}/10
                  </div>
                )}
                
                <div>
                  <span className="font-semibold">Language:</span> {movieDetails.language}
                </div>
              </div>
              
              {movieDetails.genres && movieDetails.genres.length > 0 && (
                <div className="mb-6">
                  <h3 className="text-lg font-semibold mb-2">Genres</h3>
                  <div className="flex flex-wrap gap-2">
                    {movieDetails.genres.map((genre, index) => (
                      <span key={index} className="px-3 py-1 bg-gray-200 rounded-full text-sm">
                        {genre}
                      </span>
                    ))}
                  </div>
                </div>
              )}
              
              {movieDetails.cast && movieDetails.cast.length > 0 && (
                <div className="mb-6">
                  <h3 className="text-lg font-semibold mb-2">Cast</h3>
                  <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-4">
                    {movieDetails.cast.map((actor, index) => (
                      <div key={index} className="text-center">
                        {actor.profile_image ? (
                          <img 
                            src={actor.profile_image} 
                            alt={actor.name}
                            className="w-20 h-20 object-cover rounded-full mx-auto mb-2"
                            onError={(e) => {e.target.onerror = null; e.target.src = 'https://via.placeholder.com/100x100?text=X'}}
                          />
                        ) : (
                          <div className="w-20 h-20 rounded-full bg-gray-200 flex items-center justify-center mx-auto mb-2">
                            {actor.name.charAt(0)}
                          </div>
                        )}
                        <p className="font-medium text-sm">{actor.name}</p>
                        {actor.character && (
                          <p className="text-xs text-gray-600">{actor.character}</p>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              )}
              
              {movieDetails.links && movieDetails.links.length > 0 && (
                <div>
                  <h3 className="text-lg font-semibold mb-2">Streaming Links</h3>
                  <div className="grid gap-2">
                    {movieDetails.links.map((link, index) => (
                      <a 
                        key={index}
                        href={link.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="flex justify-between items-center p-3 border rounded hover:bg-gray-50"
                      >
                        <div>
                          <span className="font-medium">{link.quality}</span>
                          {link.size && <span className="text-sm text-gray-600 ml-2">({link.size})</span>}
                        </div>
                        <span className="text-blue-600">Watch</span>
                      </a>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default MovieSearch;
