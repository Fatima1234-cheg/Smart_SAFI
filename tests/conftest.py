"""
Pytest configuration for Smart City - SmartSafi
"""

import pytest
from app import create_app, mongo


@pytest.fixture
def app():
    """Create application for testing"""
    app = create_app('testing')
    
    with app.app_context():
        # Clear test database
        mongo.db.command('dropDatabase')
        yield app
        # Cleanup after tests
        mongo.db.command('dropDatabase')


@pytest.fixture
def client(app):
    """Create test client"""
    return app.test_client()


@pytest.fixture
def runner(app):
    """Create test CLI runner"""
    return app.test_cli_runner()


@pytest.fixture
def sample_user_data():
    """Sample user data for testing"""
    return {
        'username': 'testuser',
        'email': 'test@example.com',
        'password': 'TestPassword123!',
        'first_name': 'Test',
        'last_name': 'User',
        'role': 'viewer'
    }


@pytest.fixture
def sample_waste_data():
    """Sample waste data for testing"""
    return {
        'bin_id': 'BIN001',
        'region': 'nord',
        'fill_level': 75,
        'status': 'normal',
        'temperature': 25,
        'humidity': 60,
        'location': {'lat': 32.2994, 'lon': -9.2372}
    }


@pytest.fixture
def sample_water_data():
    """Sample water data for testing"""
    return {
        'sensor_id': 'WAT001',
        'source': 'source1',
        'ph': 7.2,
        'turbidity': 0.5,
        'conductivity': 450,
        'temperature': 18,
        'location': {'lat': 32.3000, 'lon': -9.2380}
    }


@pytest.fixture
def auth_headers(client, sample_user_data):
    """Generate authentication headers for testing"""
    # First, register a user
    client.post('/auth/register', json=sample_user_data)
    
    # Then login
    response = client.post('/auth/login', json={
        'username': sample_user_data['username'],
        'password': sample_user_data['password']
    })
    
    token = response.json.get('access_token')
    return {'Authorization': f'Bearer {token}'}
