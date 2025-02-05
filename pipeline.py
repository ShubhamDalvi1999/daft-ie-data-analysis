import logging
from datetime import datetime
from typing import Dict, List, Optional
from zeep import Client
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from config import (
    DAFT_API_KEY, DAFT_API_WSDL, DATABASE_URL,
    REQUEST_TIMEOUT, MAX_RETRIES, RETRY_DELAY
)
from models import Base, Property, PropertyFeature, PropertyImage, DataQualityLog
import time
import requests
from requests.exceptions import RequestException

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DaftPropertyPipeline:
    def __init__(self):
        self.engine = create_engine(DATABASE_URL)
        Base.metadata.create_all(self.engine)
        self.client = Client(DAFT_API_WSDL)
        self.session = requests.Session()
        self.session.headers.update({'Authorization': f'Bearer {DAFT_API_KEY}'})

    def fetch_properties(self, search_params: Dict) -> List[Dict]:
        """
        Fetch properties from Daft.ie API with retry mechanism
        """
        for attempt in range(MAX_RETRIES):
            try:
                response = self.session.post(
                    f"{DAFT_API_WSDL}/search_sale",
                    json=search_params,
                    timeout=REQUEST_TIMEOUT
                )
                response.raise_for_status()
                return response.json()
            except RequestException as e:
                if attempt == MAX_RETRIES - 1:
                    logger.error(f"Failed to fetch properties after {MAX_RETRIES} attempts: {str(e)}")
                    raise
                time.sleep(RETRY_DELAY)

    def transform_property_data(self, raw_property: Dict) -> Dict:
        """
        Transform raw property data into standardized format
        """
        try:
            transformed = {
                'daft_id': str(raw_property.get('id')),
                'property_type': raw_property.get('propertyType'),
                'price': float(raw_property.get('price', 0)),
                'bedrooms': int(raw_property.get('numBedrooms', 0)),
                'bathrooms': int(raw_property.get('numBathrooms', 0)),
                'address': raw_property.get('address'),
                'ber_rating': raw_property.get('berRating'),
                'description': raw_property.get('description'),
                'location': f"POINT({raw_property.get('longitude')} {raw_property.get('latitude')})"
                if raw_property.get('longitude') and raw_property.get('latitude')
                else None
            }
            return transformed
        except Exception as e:
            logger.error(f"Error transforming property data: {str(e)}")
            raise

    def validate_property_data(self, data: Dict) -> List[str]:
        """
        Validate property data and return list of validation errors
        """
        errors = []
        
        # Required fields validation
        required_fields = ['daft_id', 'price', 'address']
        for field in required_fields:
            if not data.get(field):
                errors.append(f"Missing required field: {field}")

        # Data type validation
        if data.get('price') and not isinstance(data['price'], (int, float)):
            errors.append("Price must be a number")

        # Value range validation
        if data.get('bedrooms') and (data['bedrooms'] < 0 or data['bedrooms'] > 20):
            errors.append("Invalid number of bedrooms")

        return errors

    def store_property_data(self, transformed_data: Dict) -> Optional[Property]:
        """
        Store transformed property data in the database
        """
        try:
            with Session(self.engine) as session:
                # Check if property already exists
                existing_property = session.query(Property).filter_by(
                    daft_id=transformed_data['daft_id']
                ).first()

                if existing_property:
                    # Update existing property
                    for key, value in transformed_data.items():
                        setattr(existing_property, key, value)
                    property_obj = existing_property
                else:
                    # Create new property
                    property_obj = Property(**transformed_data)
                    session.add(property_obj)

                # Log data quality check
                validation_errors = self.validate_property_data(transformed_data)
                for error in validation_errors:
                    quality_log = DataQualityLog(
                        property_id=property_obj.id,
                        check_type='validation_error',
                        check_result=False,
                        message=error
                    )
                    session.add(quality_log)

                session.commit()
                return property_obj
        except Exception as e:
            logger.error(f"Error storing property data: {str(e)}")
            session.rollback()
            raise

    def run_pipeline(self, search_params: Dict):
        """
        Run the complete pipeline
        """
        try:
            # Fetch data
            raw_properties = self.fetch_properties(search_params)
            
            for raw_property in raw_properties:
                # Transform
                transformed_data = self.transform_property_data(raw_property)
                
                # Validate
                validation_errors = self.validate_property_data(transformed_data)
                if validation_errors:
                    logger.warning(f"Validation errors for property {transformed_data.get('daft_id')}: {validation_errors}")
                
                # Store
                self.store_property_data(transformed_data)
                
            logger.info("Pipeline completed successfully")
        except Exception as e:
            logger.error(f"Pipeline failed: {str(e)}")
            raise

if __name__ == "__main__":
    # Example usage
    pipeline = DaftPropertyPipeline()
    search_params = {
        "location": "Dublin",
        "propertyType": ["house"],
        "maxPrice": 500000
    }
    pipeline.run_pipeline(search_params) 