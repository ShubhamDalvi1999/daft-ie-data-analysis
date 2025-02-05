# Daft.ie Property Data Pipeline

This project implements a data pipeline for ingesting, processing, and storing property data from the Daft.ie API.

## Features

- Data ingestion from Daft.ie API using SOAP protocol
- Robust error handling and retry mechanisms
- Data validation and quality checks
- PostgreSQL database storage with geographical data support
- Monitoring and logging capabilities

## Prerequisites

- Python 3.8+
- PostgreSQL database
- Daft.ie API credentials

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd daft-property-pipeline
```

2. Create a virtual environment and activate it:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file in the project root with the following variables:
```
DAFT_API_KEY=your_api_key_here
DB_HOST=localhost
DB_PORT=5432
DB_NAME=daft_properties
DB_USER=your_db_user
DB_PASSWORD=your_db_password
LOG_LEVEL=INFO
```

5. Create the PostgreSQL database:
```sql
CREATE DATABASE daft_properties;
```

## Usage

1. Run the pipeline:
```bash
python pipeline.py
```

The pipeline will:
- Fetch property data from Daft.ie API
- Transform and validate the data
- Store it in the PostgreSQL database
- Log any validation errors or issues

## Data Model

The database schema includes the following tables:

- `properties`: Main property information
- `property_features`: Additional property features
- `property_images`: Property image URLs
- `data_quality_logs`: Data validation and quality check logs

## Monitoring and Logging

- All pipeline operations are logged
- Data quality issues are tracked in the `data_quality_logs` table
- Critical errors trigger alerts (configure in config.py)

## Error Handling

The pipeline includes:
- Automatic retries for API failures
- Data validation checks
- Transaction management for database operations
- Comprehensive error logging

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details. 