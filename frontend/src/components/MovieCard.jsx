import React from 'react';

const MovieCard = ({ title, image, rating, year }) => {
  // Default placeholder ako nema slike
  const imageUrl = image || 'https://via.placeholder.com/300x450?text=No+Poster';

  return (
    <div className="w-full max-w-xs mx-auto bg-white rounded-xl shadow-md overflow-hidden hover:shadow-xl transition-shadow duration-300 cursor-pointer">
      {/* Poster */}
      <div className="relative h-80 overflow-hidden">
        <img 
          src={imageUrl} 
          alt={title} 
          className="w-full h-full object-cover transition-transform duration-300 hover:scale-105"
          onError={(e) => {
            e.target.onerror = null;
            e.target.src = 'https://via.placeholder.com/300x450?text=No+Image';
          }}
        />
        
        {/* Rating badge */}
        {rating && (
          <div className="absolute top-3 right-3 bg-black bg-opacity-75 text-white text-sm font-bold px-2 py-1 rounded-full flex items-center">
            <span className="text-yellow-400 mr-1">★</span>
            {rating.toFixed(1)}
          </div>
        )}
        
        {/* Year badge */}
        {year && (
          <div className="absolute top-3 left-3 bg-blue-600 text-white text-xs font-semibold px-3 py-1 rounded-full">
            {year}
          </div>
        )}
      </div>

      {/* Title and Info */}
      <div className="p-4">
        <h3 className="font-bold text-lg text-gray-900 truncate mb-2 hover:text-blue-600 transition-colors">
          {title}
        </h3>
        
        {/* Additional info row */}
        <div className="flex items-center justify-between text-sm text-gray-600">
          <div className="flex items-center">
            <svg className="w-4 h-4 text-gray-400 mr-1" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-12a1 1 0 10-2 0v4a1 1 0 00.293.707l2.828 2.829a1 1 0 101.415-1.415L11 9.586V6z" clipRule="evenodd" />
            </svg>
            <span>{year || 'N/A'}</span>
          </div>
          
          {rating && (
            <div className="flex items-center">
              <svg className="w-4 h-4 text-yellow-500 mr-1" fill="currentColor" viewBox="0 0 20 20">
                <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
              </svg>
              <span className="font-medium">{rating.toFixed(1)}</span>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

// Default props
MovieCard.defaultProps = {
  title: 'Unknown Movie',
  image: '',
  rating: null,
  year: null
};

export default MovieCard;