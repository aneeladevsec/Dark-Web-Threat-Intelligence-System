# Quick Reference Guide - Dark Web Intelligence API

## 🚀 Getting Started (30 seconds)

1. **Navigate to project**
   ```bash
   cd c:\Users\PMLS\Downloads\darkweb-intel
   ```

2. **Install dependencies** (first time only)
   ```bash
   pip install -r backend/requirements.txt
   ```

3. **Start the server**
   ```bash
   python backend/app.py
   ```
   → Server runs on `http://localhost:5002`

4. **Open frontend**
   → Open `frontend/index.html` in browser

---

## 📊 Dashboard Overview

### Main Tabs

| Tab | Features |
|-----|----------|
| **Dashboard** | Real-time feed, stats cards, filtering, search |
| **Threats** | Full threat list, export CSV/JSON, metrics |
| **Analytics** | Timeline chart, type chart, advanced metrics |
| **Incidents** | Create/manage security incidents |
| **Alerts** | Real-time alerts from critical threats |

---

## 🔑 Top Features

### 1. Threat Intelligence Dashboard
- View 200+ simulated threats
- Real-time auto-refresh (30 seconds)
- Filter by severity (Critical/High/Medium/Low)
- Search threats by keyword, ID, or type

### 2. Advanced Analytics
- **Timeline Chart**: 7-day threat trend visualization
- **Type Distribution**: Doughnut chart of threat categories
- **Predictive Insights**: Trend direction and recommended focus areas
- **Advanced Metrics**: 30+ calculated metrics

### 3. Threat Correlation
- Find related threats automatically
- Correlation score (0-100+)
- Related by: Type, Geography, Source, IOCs, Sectors, Timeline
- Click "Show Related Threats" in threat details

### 4. Data Export
- **Export CSV**: Spreadsheet-ready format
- **Export JSON**: Full data with all fields
- Filter before export for specific threats

### 5. Real-Time Alerts
- Automatic alerts for Critical/High threats
- Alert type categorization
- Timestamp tracking
- Message details

---

## 📡 API Quick Reference

### Start with These Endpoints

```bash
# Get overall statistics
GET http://localhost:5002/stats

# Get first 20 threats
GET http://localhost:5002/threats

# Get threats from last 24 hours
GET http://localhost:5002/threats/recent=24

# Get only critical threats
GET http://localhost:5002/threats/critical

# Search for specific threat
GET http://localhost:5002/search?q=ransomware

# Get predictive insights
GET http://localhost:5002/analytics/predictive

# Get alerts
GET http://localhost:5002/alerts

# Export data
GET http://localhost:5002/export/threats/csv
GET http://localhost:5002/export/threats/json
```

### Full Endpoint List

**Threat Management**
- `/threats` - All threats
- `/threats/recent?hours=24` - Recent threats
- `/threats/critical` - Critical only
- `/threats/<id>` - Specific threat

**Analytics**
- `/analytics/timeline?days=7` - Timeline data
- `/analytics/predictive` - Predictions
- `/analytics/advanced` - Full dashboard
- `/threats/metrics/by-type` - Type metrics
- `/threats/metrics/by-source` - Source metrics

**Search & Query**
- `/search?q=keyword` - Search threats

**System**
- `/health` - Server status
- `/stats` - Statistics
- `/geo` - Geolocation data
- `/feed` - Latest 10 threats
- `/alerts` - Active alerts
- `/incidents` - Manage incidents

---

## 🎯 Common Tasks

### View All Critical Threats
1. Go to Dashboard tab
2. Click "Critical" filter button
3. See threats ranked by score

### Find Related Threats
1. Click any threat in the list
2. Click "Show Related Threats" button
3. View correlation scores
4. Click related threat to view details

### Export Threats Data
1. Go to Threats tab
2. Click "Export CSV" or "Export JSON"
3. File downloads automatically
4. Open in Excel/spreadsheet or text editor

### Check System Health
1. Go to Threats tab
2. Click "Export CSV" - if successful, system is healthy
3. Or visit: `http://localhost:5002/health`

### View Analytics
1. Go to Analytics tab
2. See 7-day timeline chart
3. See threat type distribution
4. Review trend analysis and metrics

### Create Incident
1. Go to Incidents tab
2. Click "Create Incident" button
3. Enter incident name
4. Track related threats

---

## 🔧 Configuration

Edit `.env` file to customize:

```env
PORT=5002                          # Change API port
API_KEY=threat-intel-api-key-test  # Change auth key
DB_PATH=threats.db                 # Database location
CACHE_TTL=300                      # Cache timeout (seconds)
```

---

## ❓ Troubleshooting

| Issue | Solution |
|-------|----------|
| Frontend not loading | Ensure backend running on port 5002 |
| No threats showing | Check console (F12) for errors |
| Export not working | Verify backend is responding |
| Charts not displaying | Clear browser cache, reload page |
| Database error | Delete threats.db, restart server |
| API timeout | Check backend terminal for errors |

---

## 📊 What's Included

### Backend (app.py - 742 lines)
- Flask REST API with 25+ endpoints
- SQLite database with persistence
- Advanced threat analytics engine
- Threat correlation system
- Predictive analysis module
- CSV/JSON export functionality
- Alert generation system
- API key authentication

### Frontend (index.html - 900+ lines)
- Multi-tab dashboard interface
- Interactive Chart.js visualizations
- Real-time threat feed
- Advanced filtering system
- Modal detail views
- Export functionality buttons
- Predictive insights widget
- Responsive dark theme UI

### Database (SQLite)
- threats table (200+ records)
- incidents table
- alerts table
- Optimized indexes
- Auto-persistence

### Documentation
- README.md (2000+ words)
- PROJECT_COMPLETION_REPORT.md
- This quick reference guide
- .env configuration file
- Test suite (test_api.py)
- Start script (start.bat)

---

## 🎓 Learning Resources

### Understanding Threats
Each threat includes:
- **ID**: Unique identifier (THREAT-XXXXX)
- **Type**: Category (Ransomware, Data Breach, etc.)
- **Severity**: Critical/High/Medium/Low
- **Score**: 0-100 ML-based threat score
- **Source**: Origin (Darkweb forum, Marketplace, etc.)
- **Country**: Geographic source
- **Status**: Active/Contained/Investigating
- **IOCs**: Indicators of Compromise
- **MITRE Tactics**: Attack framework mapping

### Understanding Correlations
Threats are correlated by:
- Same threat type (30 points)
- Same country (20 points)
- Same source (25 points)
- Overlapping IOCs (15 points each)
- Overlapping sectors (10 points each)
- Timeline proximity <24hrs (15 points)

---

## 💡 Pro Tips

1. **Quick Search**: Use Ctrl+F in the dashboard to search your browser view
2. **Export Everything**: Use JSON export to get complete data with IOCs
3. **Monitor Trends**: Check Analytics tab daily for emerging threats
4. **Set Alerts**: Check Alerts tab regularly for critical threats
5. **Create Incidents**: Link related threats to incidents for tracking
6. **API Integration**: Use API key to integrate with other systems
7. **Bookmark**: Save frequently used API endpoints
8. **Backups**: Regularly backup threats.db for data retention

---

## 🚀 Next Steps

1. ✅ Start the server
2. ✅ Open the dashboard
3. ✅ Explore the threat data
4. ✅ Check the analytics
5. ✅ Create an incident
6. ✅ Export some data
7. ✅ Test API endpoints

---

## 📞 Support

All features are documented in README.md  
API documentation in PROJECT_COMPLETION_REPORT.md  
Troubleshooting guide in both files above  

---

**Happy Threat Hunting! 🌑**
