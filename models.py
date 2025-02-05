from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class Property(Base):
    __tablename__ = 'properties'

    id = Column(Integer, primary_key=True)
    daft_id = Column(String, unique=True, nullable=False)
    property_type = Column(String)
    price = Column(Float)
    bedrooms = Column(Integer)
    bathrooms = Column(Integer)
    address = Column(String)
    ber_rating = Column(String)
    description = Column(String)
    latitude = Column(Float)
    longitude = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True)

    # Relationships
    features = relationship("PropertyFeature", back_populates="property")
    images = relationship("PropertyImage", back_populates="property")

class PropertyFeature(Base):
    __tablename__ = 'property_features'

    id = Column(Integer, primary_key=True)
    property_id = Column(Integer, ForeignKey('properties.id'))
    feature_name = Column(String)
    feature_value = Column(String)
    
    # Relationship
    property = relationship("Property", back_populates="features")

class PropertyImage(Base):
    __tablename__ = 'property_images'

    id = Column(Integer, primary_key=True)
    property_id = Column(Integer, ForeignKey('properties.id'))
    image_url = Column(String)
    image_type = Column(String)  # e.g., 'main', 'interior', 'exterior'
    
    # Relationship
    property = relationship("Property", back_populates="images")

class DataQualityLog(Base):
    __tablename__ = 'data_quality_logs'

    id = Column(Integer, primary_key=True)
    property_id = Column(Integer, ForeignKey('properties.id'))
    check_type = Column(String)  # e.g., 'missing_data', 'validation_error'
    check_result = Column(Boolean)
    message = Column(String)
    timestamp = Column(DateTime, default=datetime.utcnow) 