"""
Dark Web Threat Intelligence API
Simulates dark web monitoring with ML-based threat classification
"""

from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from datetime import datetime, timedelta
import random
import json
import hashlib
import re
import os
import sqlite3
import csv
import io
import jwt
from functools import wraps
from collections import defaultdict

app = Flask(__name__)
CORS(app)

# Configuration
SECRET_KEY = os.environ.get('SECRET_KEY', 'darkweb-intel-secret-key-2026')
API_KEY = os.environ.get('API_KEY', 'threat-intel-api-key-test')
DB_PATH = os.environ.get('DB_PATH', 'threats.db')

# ==========================================
# DATABASE MANAGER
# ==========================================

class DatabaseManager:
    def __init__(self, db_path=DB_PATH):
        self.db_path = db_path
        self.init_db()
    
    def init_db(self):
        """Initialize database schema"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        # Threats table
        c.execute('''CREATE TABLE IF NOT EXISTS threats (
            id TEXT PRIMARY KEY,
            timestamp TEXT,
            type TEXT,
            source TEXT,
            severity TEXT,
            score REAL,
            description TEXT,
            country TEXT,
            status TEXT,
            iocs TEXT,
            mitre_tactics TEXT,
            affected_sectors TEXT,
            created_at TEXT
        )''')
        
        # Incidents table
        c.execute('''CREATE TABLE IF NOT EXISTS incidents (
            id TEXT PRIMARY KEY,
            name TEXT,
            severity TEXT,
            threat_ids TEXT,
            status TEXT,
            description TEXT,
            created_at TEXT,
            updated_at TEXT
        )''')
        
        # Alerts table
        c.execute('''CREATE TABLE IF NOT EXISTS alerts (
            id TEXT PRIMARY KEY,
            threat_id TEXT,
            alert_type TEXT,
            message TEXT,
            read INTEGER DEFAULT 0,
            created_at TEXT,
            FOREIGN KEY(threat_id) REFERENCES threats(id)
        )''')
        
        conn.commit()
        conn.close()
    
    def save_threat(self, threat):
        """Save threat to database"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        try:
            c.execute('''INSERT INTO threats VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)''', (
                threat['id'],
                threat['timestamp'],
                threat['type'],
                threat['source'],
                threat['severity'],
                threat['score'],
                threat['description'],
                threat['country'],
                threat['status'],
                json.dumps(threat['iocs']),
                json.dumps(threat['mitre_tactics']),
                json.dumps(threat['affected_sectors']),
                datetime.now().isoformat()
            ))
            conn.commit()
        except sqlite3.IntegrityError:
            pass
        finally:
            conn.close()
    
    def get_threats(self, limit=200):
        """Retrieve all threats from database"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        
        c.execute('SELECT * FROM threats ORDER BY timestamp DESC LIMIT ?', (limit,))
        rows = c.fetchall()
        conn.close()
        
        threats = []
        for row in rows:
            threat = dict(row)
            threat['iocs'] = json.loads(threat['iocs'])
            threat['mitre_tactics'] = json.loads(threat['mitre_tactics'])
            threat['affected_sectors'] = json.loads(threat['affected_sectors'])
            threats.append(threat)
        
        return threats

# ==========================================
# AUTHENTICATION & CACHE
# ==========================================

def require_api_key(f):
    """Decorator to require API key"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get('X-API-Key')
        if api_key != API_KEY:
            return jsonify({'error': 'Invalid or missing API key'}), 401
        return f(*args, **kwargs)
    return decorated_function

class SimpleCache:
    def __init__(self, ttl=300):
        self.cache = {}
        self.ttl = ttl
    
    def get(self, key):
        if key in self.cache:
            value, expire_time = self.cache[key]
            if datetime.now() < expire_time:
                return value
            del self.cache[key]
        return None
    
    def set(self, key, value):
        self.cache[key] = (value, datetime.now() + timedelta(seconds=self.ttl))
    
    def clear(self):
        self.cache.clear()

cache = SimpleCache(ttl=300)
db = DatabaseManager()

class ThreatIntelligenceEngine:
    def __init__(self):
        self.threats = []
        self.sources = [
            'Pastebin', 'Ghostbin', 'Telegram', 'IRC Channel',
            'Tor Forum', 'Dark Web Marketplace', 'Hacker Forum',
            'Data Breach Dump', 'Ransomware Group', 'Carding Forum'
        ]
        self.threat_types = [
            'Data Breach', 'Ransomware', 'Phishing Campaign',
            'Malware Distribution', 'Credential Stuffing',
            'Zero-Day Exploit', 'DDoS Attack', 'Insider Threat',
            'Supply Chain Attack', 'Social Engineering'
        ]
        self.countries = ['US', 'RU', 'CN', 'KP', 'IR', 'UA', 'BY', 'Unknown']
        self.severity_weights = {
            'Critical': 0.1,
            'High': 0.25,
            'Medium': 0.35,
            'Low': 0.3
        }
        self.generate_initial_data()
    
    def generate_threat_id(self, data):
        """Generate unique threat ID"""
        hash_input = f"{data['timestamp']}{data['source']}{data['type']}"
        return f"THREAT-{hashlib.md5(hash_input.encode()).hexdigest()[:8].upper()}"
    
    def extract_iocs(self, description):
        """Extract Indicators of Compromise"""
        iocs = {
            'ips': [],
            'domains': [],
            'emails': [],
            'hashes': []
        }
        
        # Extract IPs
        ip_pattern = r'\b(?:\d{1,3}\.){3}\d{1,3}\b'
        iocs['ips'] = list(set(re.findall(ip_pattern, description)))
        
        # Extract domains
        domain_pattern = r'\b(?:[a-zA-Z0-9-]+\.)+[a-zA-Z]{2,}\b'
        domains = re.findall(domain_pattern, description)
        iocs['domains'] = [d for d in domains if not d.endswith(('.com', '.org', '.net')) or random.random() > 0.5][:5]
        
        # Extract emails
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        iocs['emails'] = list(set(re.findall(email_pattern, description)))[:3]
        
        # Generate fake hashes
        hash_types = ['MD5', 'SHA256', 'SHA1']
        for _ in range(random.randint(0, 3)):
            htype = random.choice(hash_types)
            if htype == 'MD5':
                hash_val = hashlib.md5(str(random.random()).encode()).hexdigest()
            elif htype == 'SHA1':
                hash_val = hashlib.sha1(str(random.random()).encode()).hexdigest()
            else:
                hash_val = hashlib.sha256(str(random.random()).encode()).hexdigest()
            iocs['hashes'].append(f"{htype}:{hash_val}")
        
        return iocs
    
    def calculate_threat_score(self, threat_type, source, description):
        """ML-based threat scoring (0-100)"""
        base_score = 0
        
        # Type-based scoring
        type_scores = {
            'Ransomware': 95, 'Data Breach': 90, 'Zero-Day Exploit': 92,
            'Malware Distribution': 85, 'Credential Stuffing': 80,
            'Supply Chain Attack': 88, 'Phishing Campaign': 75,
            'DDoS Attack': 70, 'Insider Threat': 82, 'Social Engineering': 65
        }
        base_score += type_scores.get(threat_type, 50)
        
        # Source reliability
        source_scores = {
            'Ransomware Group': 95, 'Dark Web Marketplace': 90,
            'Data Breach Dump': 88, 'Tor Forum': 75,
            'Hacker Forum': 80, 'Telegram': 70,
            'IRC Channel': 65, 'Pastebin': 60, 'Ghostbin': 55
        }
        base_score += source_scores.get(source, 50) * 0.3
        
        # Keyword analysis
        critical_keywords = ['exploit', '0day', 'ransom', 'breach', 'leak', 'dump']
        high_keywords = ['attack', 'compromise', 'vulnerability', 'malware']
        
        desc_lower = description.lower()
        keyword_score = 0
        for kw in critical_keywords:
            if kw in desc_lower:
                keyword_score += 10
        for kw in high_keywords:
            if kw in desc_lower:
                keyword_score += 5
        
        base_score += min(keyword_score, 20)
        
        # Add randomness (simulating ML uncertainty)
        base_score += random.randint(-5, 5)
        
        return max(0, min(100, base_score))
    
    def determine_severity(self, score):
        """Convert score to severity level"""
        if score >= 85:
            return 'Critical'
        elif score >= 70:
            return 'High'
        elif score >= 50:
            return 'Medium'
        else:
            return 'Low'
    
    def generate_description(self, threat_type, source):
        """Generate realistic threat description"""
        templates = {
            'Data Breach': [
                f"Database dump from major {random.choice(['healthcare', 'finance', 'tech'])} company exposed on {source}",
                f"Leaked credentials: {random.randint(10000, 1000000)} user records",
                f"PII dump including SSN, DOB, addresses found on {source}"
            ],
            'Ransomware': [
                f"New ransomware strain targeting {random.choice(['Windows', 'Linux', 'macOS'])} systems",
                f"Ransomware group claims attack on {random.choice(['hospital', 'school', 'government'])}",
                f"Encryption keys and victim list leaked on {source}"
            ],
            'Phishing Campaign': [
                f"Mass phishing campaign targeting {random.choice(['banking', 'crypto', 'email'])} users",
                f"Clone of {random.choice(['PayPal', 'Netflix', 'Microsoft'])} login detected",
                f"Spear-phishing emails targeting C-level executives"
            ],
            'Malware Distribution': [
                f"Malware dropper hosted on compromised {random.choice(['WordPress', 'Joomla'])} sites",
                f"New trojan variant distributed via {random.choice(['email', 'torrent', 'fake software'])}",
                f"Command & Control server active at IP range"
            ],
            'Zero-Day Exploit': [
                f"Unpatched vulnerability in {random.choice(['Chrome', 'Windows', 'Adobe'])} being exploited",
                f"Proof-of-concept code released for CVE-2026-{random.randint(1000, 9999)}",
                f"Active exploitation detected in the wild"
            ]
        }
        
        if threat_type in templates:
            return random.choice(templates[threat_type])
        return f"Suspicious activity detected on {source}"
    
    def generate_initial_data(self, count=200):
        """Generate initial threat dataset"""
        print("🌑 Generating threat intelligence data...")
        
        for i in range(count):
            # Random timestamp within last 30 days
            hours_ago = random.randint(0, 720)
            timestamp = datetime.now() - timedelta(hours=hours_ago)
            
            threat_type = random.choice(self.threat_types)
            source = random.choice(self.sources)
            description = self.generate_description(threat_type, source)
            
            score = self.calculate_threat_score(threat_type, source, description)
            severity = self.determine_severity(score)
            
            threat = {
                'id': None,  # Will be generated
                'timestamp': timestamp.isoformat(),
                'type': threat_type,
                'source': source,
                'severity': severity,
                'score': score,
                'description': description,
                'country': random.choice(self.countries),
                'status': random.choice(['Active', 'Contained', 'Investigating', 'New']),
                'iocs': self.extract_iocs(description),
                'mitre_tactics': random.sample(['Initial Access', 'Execution', 'Persistence', 'Defense Evasion', 'Credential Access', 'Discovery', 'Lateral Movement', 'Collection', 'Exfiltration', 'Impact'], k=random.randint(1, 3)),
                'affected_sectors': random.sample(['Healthcare', 'Finance', 'Government', 'Technology', 'Education', 'Energy', 'Retail'], k=random.randint(1, 3))
            }
            
            threat['id'] = self.generate_threat_id(threat)
            self.threats.append(threat)
        
        # Sort by timestamp (newest first)
        self.threats.sort(key=lambda x: x['timestamp'], reverse=True)
        print(f"✅ Generated {count} threat records")
    
    def get_recent(self, hours=24, severity=None):
        """Get recent threats"""
        cutoff = datetime.now() - timedelta(hours=hours)
        filtered = [t for t in self.threats if datetime.fromisoformat(t['timestamp']) > cutoff]
        
        if severity:
            filtered = [t for t in filtered if t['severity'] == severity]
        
        return filtered
    
    def get_by_id(self, threat_id):
        """Get specific threat by ID"""
        for t in self.threats:
            if t['id'] == threat_id:
                return t
        return None
    
    def search(self, query):
        """Search threats"""
        query = query.lower()
        results = []
        
        for t in self.threats:
            searchable = f"{t['id']} {t['type']} {t['source']} {t['description']} {t['country']}".lower()
            if query in searchable:
                results.append(t)
        
        return results[:50]
    
    def get_stats(self):
        """Get intelligence statistics"""
        now = datetime.now()
        last_24h = [t for t in self.threats if datetime.fromisoformat(t['timestamp']) > now - timedelta(hours=24)]
        last_7d = [t for t in self.threats if datetime.fromisoformat(t['timestamp']) > now - timedelta(days=7)]
        
        # Severity distribution
        severity_dist = defaultdict(int)
        for t in self.threats:
            severity_dist[t['severity']] += 1
        
        # Type distribution
        type_dist = defaultdict(int)
        for t in self.threats:
            type_dist[t['type']] += 1
        
        # Source distribution
        source_dist = defaultdict(int)
        for t in self.threats:
            source_dist[t['source']] += 1
        
        # Country distribution
        country_dist = defaultdict(int)
        for t in self.threats:
            country_dist[t['country']] += 1
        
        # Trend (last 7 days vs previous 7 days)
        prev_7d = [t for t in self.threats 
                   if now - timedelta(days=14) < datetime.fromisoformat(t['timestamp']) <= now - timedelta(days=7)]
        
        trend = len(last_7d) - len(prev_7d)
        
        return {
            'total_threats': len(self.threats),
            'last_24h': len(last_24h),
            'last_7d': len(last_7d),
            'critical_count': severity_dist['Critical'],
            'high_count': severity_dist['High'],
            'trend': trend,
            'trend_percentage': round((trend / max(len(prev_7d), 1)) * 100, 1),
            'severity_distribution': dict(severity_dist),
            'top_threat_types': dict(sorted(type_dist.items(), key=lambda x: x[1], reverse=True)[:5]),
            'top_sources': dict(sorted(source_dist.items(), key=lambda x: x[1], reverse=True)[:5]),
            'country_distribution': dict(country_dist),
            'active_monitors': 12,
            'sources_tracked': len(self.sources),
            'last_updated': now.isoformat()
        }
    
    def get_geolocation_data(self):
        """Get data for world map"""
        country_data = defaultdict(lambda: {'count': 0, 'severity_score': 0, 'types': []})
        
        for t in self.threats:
            country = t['country']
            country_data[country]['count'] += 1
            country_data[country]['severity_score'] += t['score']
            country_data[country]['types'].append(t['type'])
        
        # Calculate average severity
        result = {}
        for country, data in country_data.items():
            result[country] = {
                'count': data['count'],
                'avg_severity': round(data['severity_score'] / data['count'], 1),
                'top_threat': max(set(data['types']), key=data['types'].count) if data['types'] else 'Unknown'
            }
        
        return result
    
    def get_threat_correlations(self, threat_id):
        """Find related/correlated threats"""
        threat = self.get_by_id(threat_id)
        if not threat:
            return []
        
        correlations = []
        for t in self.threats:
            if t['id'] == threat_id:
                continue
            
            # Score correlation
            score = 0
            
            # Same type = high correlation
            if t['type'] == threat['type']:
                score += 30
            
            # Same country = moderate correlation
            if t['country'] == threat['country']:
                score += 20
            
            # Same source = high correlation
            if t['source'] == threat['source']:
                score += 25
            
            # Overlapping IOCs
            for ioc_type in ['ips', 'domains', 'emails']:
                overlap = set(t['iocs'][ioc_type]) & set(threat['iocs'][ioc_type])
                if overlap:
                    score += 15 * len(overlap)
            
            # Overlapping sectors
            overlap_sectors = set(t['affected_sectors']) & set(threat['affected_sectors'])
            if overlap_sectors:
                score += 10 * len(overlap_sectors)
            
            # Timeline proximity (threats within 24 hours)
            t_time = datetime.fromisoformat(t['timestamp'])
            threat_time = datetime.fromisoformat(threat['timestamp'])
            hours_apart = abs((t_time - threat_time).total_seconds() / 3600)
            if hours_apart < 24:
                score += 15
            
            if score > 20:  # Only include if correlation score > 20
                correlations.append({
                    'threat_id': t['id'],
                    'correlation_score': score,
                    'type': t['type'],
                    'severity': t['severity'],
                    'timestamp': t['timestamp']
                })
        
        return sorted(correlations, key=lambda x: x['correlation_score'], reverse=True)[:10]
    
    def get_timeline_data(self, days=30):
        """Get threat timeline for chart"""
        cutoff = datetime.now() - timedelta(days=days)
        daily_data = defaultdict(lambda: {'total': 0, 'critical': 0, 'high': 0, 'medium': 0, 'low': 0})
        
        for threat in self.threats:
            threat_time = datetime.fromisoformat(threat['timestamp'])
            if threat_time > cutoff:
                day = threat_time.strftime('%Y-%m-%d')
                daily_data[day]['total'] += 1
                severity = threat['severity'].lower()
                daily_data[day][severity] += 1
        
        return dict(sorted(daily_data.items()))
    
    def get_predictive_insights(self):
        """Generate ML-based predictive insights"""
        now = datetime.now()
        
        # Analyze trends
        today = [t for t in self.threats if datetime.fromisoformat(t['timestamp']).date() == now.date()]
        this_week = [t for t in self.threats if now - timedelta(days=7) < datetime.fromisoformat(t['timestamp']) < now]
        this_month = [t for t in self.threats if now - timedelta(days=30) < datetime.fromisoformat(t['timestamp']) < now]
        
        # Calculate trend direction
        trend_direction = "increasing" if len(this_week) > len(this_month) / 4 else "decreasing"
        
        # Most likely next threats
        threat_type_counts = defaultdict(int)
        for t in this_month:
            threat_type_counts[t['type']] += 1
        
        top_types = sorted(threat_type_counts.items(), key=lambda x: x[1], reverse=True)[:3]
        
        # High-risk sectors
        sector_counts = defaultdict(int)
        for t in this_month:
            for sector in t['affected_sectors']:
                sector_counts[sector] += 1
        
        top_sectors = sorted(sector_counts.items(), key=lambda x: x[1], reverse=True)[:3]
        
        # Most active sources
        source_counts = defaultdict(int)
        for t in this_month:
            source_counts[t['source']] += 1
        
        top_sources = sorted(source_counts.items(), key=lambda x: x[1], reverse=True)[:3]
        
        return {
            'trend_direction': trend_direction,
            'threats_today': len(today),
            'threats_this_week': len(this_week),
            'predicted_top_threat_types': [t[0] for t in top_types],
            'at_risk_sectors': [s[0] for s in top_sectors],
            'most_active_sources': [s[0] for s in top_sources],
            'confidence_level': 'HIGH' if len(this_month) > 50 else 'MEDIUM'
        }
    
    def export_threats_csv(self, threat_ids=None):
        """Export threats to CSV format"""
        threats_to_export = self.threats
        if threat_ids:
            threats_to_export = [t for t in self.threats if t['id'] in threat_ids]
        
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Header
        writer.writerow(['Threat ID', 'Type', 'Severity', 'Score', 'Source', 'Country', 'Status', 'Timestamp', 'Description'])
        
        # Data rows
        for threat in threats_to_export:
            writer.writerow([
                threat['id'],
                threat['type'],
                threat['severity'],
                threat['score'],
                threat['source'],
                threat['country'],
                threat['status'],
                threat['timestamp'],
                threat['description']
            ])
        
        return output.getvalue()
    
    def export_threats_json(self, threat_ids=None):
        """Export threats to JSON format"""
        threats_to_export = self.threats
        if threat_ids:
            threats_to_export = [t for t in self.threats if t['id'] in threat_ids]
        
        return json.dumps(threats_to_export, indent=2)

# Initialize engine
engine = ThreatIntelligenceEngine()

# ==========================================
# API ROUTES
# ==========================================

@app.route('/')
def home():
    return jsonify({
        "service": "Dark Web Threat Intelligence API",
        "version": "1.0.0",
        "description": "Real-time threat monitoring and analysis",
        "endpoints": {
            "/threats": "Get all threats (paginated)",
            "/threats/recent": "Get last 24h threats",
            "/threats/critical": "Get critical threats only",
            "/threats/<id>": "Get specific threat details",
            "/search": "Search threats by keyword",
            "/stats": "Get intelligence statistics",
            "/geo": "Get geolocation data for map",
            "/feed": "Get real-time threat feed"
        }
    })

@app.route('/threats')
def get_threats():
    """Get all threats with pagination"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    severity = request.args.get('severity')
    
    threats = engine.threats
    if severity:
        threats = [t for t in threats if t['severity'] == severity]
    
    total = len(threats)
    start = (page - 1) * per_page
    end = start + per_page
    
    return jsonify({
        'threats': threats[start:end],
        'total': total,
        'page': page,
        'per_page': per_page,
        'pages': (total + per_page - 1) // per_page
    })

@app.route('/threats/recent')
def get_recent():
    """Get recent threats (last 24h)"""
    hours = request.args.get('hours', 24, type=int)
    return jsonify({
        'threats': engine.get_recent(hours),
        'count': len(engine.get_recent(hours)),
        'timeframe': f'Last {hours} hours'
    })

@app.route('/threats/critical')
def get_critical():
    """Get critical and high severity threats"""
    critical = [t for t in engine.threats if t['severity'] in ['Critical', 'High']]
    return jsonify({
        'threats': critical[:50],
        'count': len(critical),
        'critical_count': len([t for t in critical if t['severity'] == 'Critical']),
        'high_count': len([t for t in critical if t['severity'] == 'High'])
    })

@app.route('/threats/<threat_id>')
def get_threat(threat_id):
    """Get specific threat details"""
    threat = engine.get_by_id(threat_id)
    if threat:
        return jsonify(threat)
    return jsonify({'error': 'Threat not found'}), 404

@app.route('/search')
def search_threats():
    """Search threats"""
    query = request.args.get('q', '')
    if not query or len(query) < 2:
        return jsonify({'error': 'Query must be at least 2 characters'}), 400
    
    results = engine.search(query)
    return jsonify({
        'query': query,
        'results': results,
        'count': len(results)
    })

@app.route('/stats')
def get_stats():
    """Get intelligence statistics"""
    return jsonify(engine.get_stats())

@app.route('/geo')
def get_geo():
    """Get geolocation data"""
    return jsonify(engine.get_geolocation_data())

@app.route('/feed')
def get_feed():
    """Get real-time feed (last 10 threats)"""
    return jsonify({
        'feed': engine.threats[:10],
        'updated': datetime.now().isoformat()
    })

@app.route('/health')
def health():
    """Health check"""
    return jsonify({
        'status': 'healthy',
        'threats_loaded': len(engine.threats),
        'sources': len(engine.sources),
        'timestamp': datetime.now().isoformat()
    })

# ==========================================
# ADVANCED ANALYTICS ROUTES
# ==========================================

@app.route('/threats/<threat_id>/correlations')
def get_correlations(threat_id):
    """Get correlated threats"""
    correlations = engine.get_threat_correlations(threat_id)
    return jsonify({
        'threat_id': threat_id,
        'correlations': correlations,
        'count': len(correlations)
    })

@app.route('/analytics/timeline')
def analytics_timeline():
    """Get threat timeline data"""
    days = request.args.get('days', 30, type=int)
    timeline = engine.get_timeline_data(days)
    return jsonify({
        'timeline': timeline,
        'days': days
    })

@app.route('/analytics/predictive')
def analytics_predictive():
    """Get predictive insights"""
    return jsonify(engine.get_predictive_insights())

@app.route('/analytics/advanced')
def analytics_advanced():
    """Advanced analytics dashboard"""
    stats = engine.get_stats()
    predictive = engine.get_predictive_insights()
    timeline = engine.get_timeline_data(7)
    
    # Calculate additional metrics
    now = datetime.now()
    last_7d = [t for t in engine.threats if datetime.fromisoformat(t['timestamp']) > now - timedelta(days=7)]
    last_30d = [t for t in engine.threats if datetime.fromisoformat(t['timestamp']) > now - timedelta(days=30)]
    
    avg_score_7d = sum(t['score'] for t in last_7d) / len(last_7d) if last_7d else 0
    avg_score_30d = sum(t['score'] for t in last_30d) / len(last_30d) if last_30d else 0
    
    return jsonify({
        'stats': stats,
        'predictive': predictive,
        'timeline': timeline,
        'metrics': {
            'avg_threat_score_7d': round(avg_score_7d, 2),
            'avg_threat_score_30d': round(avg_score_30d, 2),
            'critical_trend': len([t for t in last_7d if t['severity'] == 'Critical']) / max(len(last_7d), 1),
            'data_completeness': '98.5%',
            'monitoring_coverage': '12 sources, 8 countries'
        }
    })

@app.route('/export/threats/csv')
def export_csv():
    """Export threats as CSV"""
    threat_ids = request.args.getlist('threat_ids')
    csv_data = engine.export_threats_csv(threat_ids if threat_ids else None)
    
    return send_file(
        io.BytesIO(csv_data.encode()),
        mimetype='text/csv',
        as_attachment=True,
        download_name=f'threats_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
    )

@app.route('/export/threats/json')
def export_json():
    """Export threats as JSON"""
    threat_ids = request.args.getlist('threat_ids')
    json_data = engine.export_threats_json(threat_ids if threat_ids else None)
    
    return send_file(
        io.BytesIO(json_data.encode()),
        mimetype='application/json',
        as_attachment=True,
        download_name=f'threats_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
    )

@app.route('/api/key')
def get_api_key():
    """Get API key for testing"""
    return jsonify({
        'api_key': API_KEY,
        'description': 'Use X-API-Key header for authenticated endpoints'
    })

@app.route('/threats/metrics/by-type')
def metrics_by_type():
    """Get threat metrics grouped by type"""
    type_metrics = defaultdict(lambda: {
        'count': 0,
        'avg_score': 0,
        'avg_severity': 0,
        'critical_count': 0
    })
    
    for threat in engine.threats:
        t_type = threat['type']
        type_metrics[t_type]['count'] += 1
        type_metrics[t_type]['avg_score'] += threat['score']
        if threat['severity'] == 'Critical':
            type_metrics[t_type]['critical_count'] += 1
    
    # Calculate averages
    for t_type in type_metrics:
        count = type_metrics[t_type]['count']
        type_metrics[t_type]['avg_score'] = round(type_metrics[t_type]['avg_score'] / count, 2)
    
    return jsonify({
        'metrics_by_type': dict(type_metrics),
        'total_types': len(type_metrics)
    })

@app.route('/threats/metrics/by-source')
def metrics_by_source():
    """Get threat metrics grouped by source"""
    source_metrics = defaultdict(lambda: {
        'count': 0,
        'reliability': 0,
        'avg_score': 0
    })
    
    for threat in engine.threats:
        source = threat['source']
        source_metrics[source]['count'] += 1
        source_metrics[source]['avg_score'] += threat['score']
    
    # Calculate averages and reliability
    for source in source_metrics:
        count = source_metrics[source]['count']
        source_metrics[source]['avg_score'] = round(source_metrics[source]['avg_score'] / count, 2)
        source_metrics[source]['reliability'] = round((75 + (count % 25)) / 100, 2)
    
    return jsonify({
        'metrics_by_source': dict(source_metrics),
        'total_sources': len(source_metrics)
    })

@app.route('/incidents', methods=['GET', 'POST'])
def manage_incidents():
    """Manage security incidents"""
    if request.method == 'POST':
        data = request.json
        incident_id = f"INC-{hashlib.md5(str(datetime.now()).encode()).hexdigest()[:8].upper()}"
        
        incident = {
            'id': incident_id,
            'name': data.get('name', 'Unnamed Incident'),
            'severity': data.get('severity', 'Medium'),
            'threat_ids': data.get('threat_ids', []),
            'status': 'Open',
            'description': data.get('description', ''),
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat()
        }
        
        return jsonify(incident), 201
    
    return jsonify({
        'message': 'POST to create incidents'
    })

@app.route('/alerts')
def get_alerts():
    """Get recent alerts"""
    limit = request.args.get('limit', 50, type=int)
    alerts = []
    
    for threat in engine.threats[:limit]:
        if threat['severity'] in ['Critical', 'High']:
            alert = {
                'id': f"ALERT-{threat['id']}",
                'threat_id': threat['id'],
                'alert_type': 'SEVERITY_ALERT',
                'message': f"{threat['severity']} severity {threat['type']} detected from {threat['source']}",
                'created_at': threat['timestamp']
            }
            alerts.append(alert)
    
    return jsonify({
        'alerts': alerts,
        'count': len(alerts)
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5002))
    print(f"🌑 Dark Web Intelligence API on port {port}")
    app.run(host='0.0.0.0', port=port)