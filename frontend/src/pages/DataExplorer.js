import React, { useState, useEffect } from 'react';
import {
  Container, Row, Col, Card, Table, Form,
  InputGroup, Button, Badge, Alert, Spinner
} from 'react-bootstrap';
import api from '../services/api';
import './DataExplorer.css';

const DataExplorer = () => {
  const [movies, setMovies] = useState([]);
  const [places, setPlaces] = useState([]);
  const [correlations, setCorrelations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [activeTab, setActiveTab] = useState('movies');

  const fetchData = async () => {
    setLoading(true);
    try {
      // Ovdje ćete dodati prave API pozive
      // Za sada koristimo dummy podatke
      setMovies([
        { id: 1, title: 'Inception', year: 2010, rating: 8.8, genres: ['Action', 'Sci-Fi'] },
        { id: 2, title: 'The Shawshank Redemption', year: 1994, rating: 9.3, genres: ['Drama'] },
        { id: 3, title: 'The Dark Knight', year: 2008, rating: 9.0, genres: ['Action', 'Crime', 'Drama'] }
      ]);

      setPlaces([
        { id: 1, name: 'Los Angeles', country: 'USA', type: 'City', population: 3980000 },
        { id: 2, name: 'London', country: 'UK', type: 'City', population: 8982000 },
        { id: 3, name: 'Paris', country: 'France', type: 'City', population: 2148000 }
      ]);

      setCorrelations([
        { movie: 'Inception', place: 'Los Angeles', score: 0.85, reason: 'Sci-Fi theme matches tech hubs' },
        { movie: 'The Dark Knight', place: 'London', score: 0.72, reason: 'Gothic architecture matches film mood' }
      ]);

    } catch (err) {
      console.error('Error fetching data:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const filteredMovies = movies.filter(movie =>
    movie.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
    movie.genres.some(genre => genre.toLowerCase().includes(searchTerm.toLowerCase()))
  );

  const filteredPlaces = places.filter(place =>
    place.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    place.country.toLowerCase().includes(searchTerm.toLowerCase())
  );

  if (loading) {
    return (
      <Container className="text-center mt-5">
        <Spinner animation="border" />
        <p>Loading data...</p>
      </Container>
    );
  }

  return (
    <Container fluid className="data-explorer">
      {/* Header */}
      <Row className="mb-4">
        <Col>
          <h1 className="display-4">🔍 Data Explorer</h1>
          <p className="lead">Explore and analyze film and location data</p>
        </Col>
      </Row>

      {/* Search and Filter */}
      <Row className="mb-4">
        <Col md={8}>
          <InputGroup>
            <Form.Control
              placeholder="Search movies, places, genres..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
            <Button variant="primary">🔍 Search</Button>
          </InputGroup>
        </Col>
        <Col md={4}>
          <div className="d-flex justify-content-end">
            <Button
              variant={activeTab === 'movies' ? 'primary' : 'outline-primary'}
              className="me-2"
              onClick={() => setActiveTab('movies')}
            >
              🎬 Movies ({movies.length})
            </Button>
            <Button
              variant={activeTab === 'places' ? 'success' : 'outline-success'}
              className="me-2"
              onClick={() => setActiveTab('places')}
            >
              📍 Places ({places.length})
            </Button>
            <Button
              variant={activeTab === 'correlations' ? 'warning' : 'outline-warning'}
              onClick={() => setActiveTab('correlations')}
            >
              🔗 Correlations ({correlations.length})
            </Button>
          </div>
        </Col>
      </Row>

      {/* Data Display */}
      {activeTab === 'movies' && (
        <Card>
          <Card.Header>
            <h5>🎬 Movies from TMDB</h5>
          </Card.Header>
          <Card.Body>
            <Table striped hover responsive>
              <thead>
                <tr>
                  <th>Title</th>
                  <th>Year</th>
                  <th>Rating</th>
                  <th>Genres</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {filteredMovies.map(movie => (
                  <tr key={movie.id}>
                    <td>
                      <strong>{movie.title}</strong>
                      <br />
                      <small className="text-muted">ID: {movie.id}</small>
                    </td>
                    <td>{movie.year}</td>
                    <td>
                      <Badge bg="warning">
                        ⭐ {movie.rating}
                      </Badge>
                    </td>
                    <td>
                      {movie.genres.map(genre => (
                        <Badge key={genre} bg="info" className="me-1">
                          {genre}
                        </Badge>
                      ))}
                    </td>
                    <td>
                      <Button size="sm" variant="outline-primary">
                        View Details
                      </Button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </Table>
          </Card.Body>
        </Card>
      )}

      {activeTab === 'places' && (
        <Card>
          <Card.Header>
            <h5>📍 Places from Geoapify</h5>
          </Card.Header>
          <Card.Body>
            <Row>
              {filteredPlaces.map(place => (
                <Col md={4} key={place.id} className="mb-3">
                  <Card className="h-100">
                    <Card.Body>
                      <Card.Title>📍 {place.name}</Card.Title>
                      <Card.Subtitle className="mb-2 text-muted">
                        {place.country}
                      </Card.Subtitle>
                      <Card.Text>
                        <strong>Type:</strong> {place.type}<br />
                        <strong>Population:</strong> {place.population?.toLocaleString() || 'N/A'}
                      </Card.Text>
                      <Button variant="outline-success" size="sm">
                        View on Map
                      </Button>
                    </Card.Body>
                  </Card>
                </Col>
              ))}
            </Row>
          </Card.Body>
        </Card>
      )}

      {activeTab === 'correlations' && (
        <Card>
          <Card.Header>
            <h5>🔗 Film-Location Correlations</h5>
          </Card.Header>
          <Card.Body>
            {correlations.map((corr, index) => (
              <Card key={index} className="mb-3">
                <Card.Body>
                  <Row>
                    <Col md={4}>
                      <Card className="bg-light">
                        <Card.Body>
                          <Card.Title>🎬 {corr.movie}</Card.Title>
                        </Card.Body>
                      </Card>
                    </Col>
                    <Col md={1} className="text-center my-auto">
                      <h3>→</h3>
                      <Badge bg={
                        corr.score > 0.8 ? 'success' :
                        corr.score > 0.6 ? 'warning' : 'danger'
                      }>
                        {Math.round(corr.score * 100)}%
                      </Badge>
                    </Col>
                    <Col md={4}>
                      <Card className="bg-light">
                        <Card.Body>
                          <Card.Title>📍 {corr.place}</Card.Title>
                        </Card.Body>
                      </Card>
                    </Col>
                    <Col md={3}>
                      <Card>
                        <Card.Body>
                          <Card.Text>
                            <small>{corr.reason}</small>
                          </Card.Text>
                        </Card.Body>
                      </Card>
                    </Col>
                  </Row>
                </Card.Body>
              </Card>
            ))}
          </Card.Body>
        </Card>
      )}

      {/* Statistics */}
      <Row className="mt-4">
        <Col md={4}>
          <Card className="text-center">
            <Card.Body>
              <Card.Title>Total Movies</Card.Title>
              <Card.Text className="display-4">{movies.length}</Card.Text>
            </Card.Body>
          </Card>
        </Col>
        <Col md={4}>
          <Card className="text-center">
            <Card.Body>
              <Card.Title>Total Places</Card.Title>
              <Card.Text className="display-4">{places.length}</Card.Text>
            </Card.Body>
          </Card>
        </Col>
        <Col md={4}>
          <Card className="text-center">
            <Card.Body>
              <Card.Title>Correlations</Card.Title>
              <Card.Text className="display-4">{correlations.length}</Card.Text>
            </Card.Body>
          </Card>
        </Col>
      </Row>
    </Container>
  );
};

export default DataExplorer;