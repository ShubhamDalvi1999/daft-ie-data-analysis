from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# API Configuration
DAFT_API_KEY = os.getenv('DAFT_API_KEY')
DAFT_API_WSDL = 'https://api.daft.ie/v3/wsdl'  # Replace with actual WSDL URL

# Database Configuration
DATABASE_URL = 'sqlite:///daft_properties.db'

# Logging Configuration
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')

# API Request Configuration
REQUEST_TIMEOUT = 30  # seconds
MAX_RETRIES = 3
RETRY_DELAY = 5  # seconds 