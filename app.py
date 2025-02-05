from flask import Flask, render_template, jsonify
from sqlalchemy import create_engine, func, desc, and_
from sqlalchemy.orm import sessionmaker
from models import Property, PropertyFeature
from config import DATABASE_URL
from datetime import datetime, timedelta

app = Flask(__name__)
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/market-trends')
def market_trends():
    session = Session()
    try:
        # Average price by region and property type
        regional_prices = session.query(
            Property.address.label('region'),
            Property.property_type,
            func.avg(Property.price).label('avg_price'),
            func.count(Property.id).label('count')
        ).group_by('region', Property.property_type).all()

        # Price trends over time (last 12 months)
        current_date = datetime.now()
        year_ago = current_date - timedelta(days=365)
        
        monthly_trends = session.query(
            func.date_trunc('month', Property.created_at).label('month'),
            func.avg(Property.price).label('avg_price')
        ).filter(Property.created_at >= year_ago)\
         .group_by('month')\
         .order_by('month').all()

        return jsonify({
            'regionalPrices': [
                {
                    'region': r,
                    'propertyType': pt,
                    'avgPrice': float(ap),
                    'count': c
                } for r, pt, ap, c in regional_prices
            ],
            'monthlyTrends': [
                {
                    'month': m.strftime('%Y-%m'),
                    'avgPrice': float(p)
                } for m, p in monthly_trends
            ]
        })
    finally:
        session.close()

@app.route('/api/property-types')
def property_types():
    session = Session()
    try:
        # Most common property types
        popular_types = session.query(
            Property.property_type,
            func.count(Property.id).label('count'),
            func.avg(Property.price).label('avg_price')
        ).group_by(Property.property_type)\
         .order_by(desc('count')).all()

        # Average time on market by property type
        time_on_market = session.query(
            Property.property_type,
            func.avg(
                func.extract('day', Property.updated_at - Property.created_at)
            ).label('avg_days')
        ).filter(Property.is_active == False)\
         .group_by(Property.property_type).all()

        return jsonify({
            'popularTypes': [
                {
                    'type': t,
                    'count': c,
                    'avgPrice': float(p)
                } for t, c, p in popular_types
            ],
            'timeOnMarket': [
                {
                    'type': t,
                    'avgDays': float(d) if d else 0
                } for t, d in time_on_market
            ]
        })
    finally:
        session.close()

@app.route('/api/hotspots')
def hotspots():
    session = Session()
    try:
        # Areas with most new listings (last 30 days)
        thirty_days_ago = datetime.now() - timedelta(days=30)
        new_listings = session.query(
            Property.address.label('area'),
            func.count(Property.id).label('new_listings'),
            func.avg(Property.price).label('avg_price')
        ).filter(Property.created_at >= thirty_days_ago)\
         .group_by('area')\
         .order_by(desc('new_listings')).limit(10).all()

        # Price appreciation by area
        six_months_ago = datetime.now() - timedelta(days=180)
        price_appreciation = session.query(
            Property.address.label('area'),
            func.avg(Property.price).label('current_price')
        ).filter(Property.created_at >= six_months_ago)\
         .group_by('area').all()

        return jsonify({
            'newListings': [
                {
                    'area': a,
                    'count': c,
                    'avgPrice': float(p)
                } for a, c, p in new_listings
            ],
            'priceAppreciation': [
                {
                    'area': a,
                    'currentPrice': float(p)
                } for a, p in price_appreciation
            ]
        })
    finally:
        session.close()

@app.route('/api/property-stats')
def property_stats():
    session = Session()
    try:
        # Basic property statistics
        price_by_type = session.query(
            Property.property_type,
            func.avg(Property.price).label('avg_price'),
            func.count(Property.id).label('count')
        ).group_by(Property.property_type).all()
        
        price_distribution = session.query(
            func.width_bucket(Property.price, 0, 2000000, 10).label('bucket'),
            func.count(Property.id).label('count')
        ).group_by('bucket').order_by('bucket').all()
        
        bedroom_distribution = session.query(
            Property.bedrooms,
            func.count(Property.id).label('count')
        ).group_by(Property.bedrooms).order_by(Property.bedrooms).all()

        # Commercial vs Residential comparison
        commercial_vs_residential = session.query(
            Property.property_type,
            func.avg(Property.price).label('avg_price'),
            func.count(Property.id).label('count')
        ).filter(
            Property.property_type.in_(['commercial', 'residential'])
        ).group_by(Property.property_type).all()
        
        return jsonify({
            'priceByType': [
                {'type': t, 'avgPrice': float(p), 'count': c} 
                for t, p, c in price_by_type
            ],
            'priceDistribution': [
                {'range': f"{b*200000}-{(b+1)*200000}", 'count': c} 
                for b, c in price_distribution
            ],
            'bedroomDistribution': [
                {'bedrooms': b, 'count': c} 
                for b, c in bedroom_distribution
            ],
            'commercialVsResidential': [
                {'type': t, 'avgPrice': float(p), 'count': c}
                for t, p, c in commercial_vs_residential
            ]
        })
    finally:
        session.close()

if __name__ == '__main__':
    app.run(debug=True) 