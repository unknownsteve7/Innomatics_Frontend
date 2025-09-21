# AI Resume Analyzer - Backend Integration Setup

## 🔗 How to Connect Your Backend

Your Streamlit frontend is now ready to connect to your backend API running on another device!

### Quick Setup

1. **Start your Streamlit app:**
   ```bash
   streamlit run app.py
   ```

2. **In the sidebar, you'll see "🔗 Backend Settings":**
   - Enter your backend URL (e.g., `http://192.168.1.100:8000`)
   - Enable "🔌 Connect to Backend" checkbox
   - Click "🔍 Test Connection" to verify

3. **Backend URL Examples:**
   - Same network: `http://192.168.1.100:8000`
   - Different subnet: `http://10.0.0.50:8000`
   - Public domain: `https://your-api.domain.com`

### 🔧 Backend API Requirements

Your backend should implement these endpoints:

#### Core Endpoints
- `GET /api/health` - Health check
- `GET /api/jobs` - Get all jobs
- `POST /api/jobs` - Create new job
- `GET /api/candidates` - Get all candidates
- `POST /api/jobs/{job_id}/apply` - Submit application
- `POST /api/analyze-resume` - Analyze resume

#### Data Format Examples

**Job Creation (POST /api/jobs):**
```json
{
  "title": "Frontend Developer",
  "department": "Engineering",
  "description": "Job description here...",
  "requirements": ["React", "TypeScript", "CSS"],
  "applicants": 0,
  "avg_score": 0
}
```

**Job Application (POST /api/jobs/{job_id}/apply):**
- Form data with resume file
- Returns: `{"score": 85, "status": "success"}`

**Resume Analysis (POST /api/analyze-resume):**
- Form data with resume file
- Returns: `{"score": 85, "verdict": "High", "summary": "...", "gaps": [], "suggestions": "..."}`

### 🚀 Features

**✅ What Works:**
- ✅ Dual mode: Backend + Demo mode
- ✅ Real-time connection testing
- ✅ Job creation with backend sync
- ✅ upload and analysis
- ✅ Application tracking
- ✅ Automatic fallback to demo mode

**🔄 Backend Integration:**
- Jobs are synced between frontend and backend
- Resume analysis uses backend AI if available
- Application data is sent to backend for processing
- Connection status is displayed in sidebar

### 📊 Demo Mode vs Backend Mode

| Feature | Demo Mode | Backend Mode |
|---------|-----------|--------------|
| Job Management | ✅ Local only | ✅ Synced with backend |
| Resume Analysis | ✅ Mock scores | ✅ Real AI analysis |
| Data Persistence | ❌ Session only | ✅ Database stored |
| File Storage | ❌ Temporary | ✅ Persistent |
| User Authentication | ❌ Role simulation | ✅ Real auth |

### 🛠 Troubleshooting

1. **Connection Failed:**
   - Check if backend is running
   - Verify IP address and port
   - Check firewall settings
   - Ensure both devices are on same network

2. **API Errors:**
   - Check backend logs
   - Verify API endpoint paths
   - Ensure proper data format

3. **File Upload Issues:**
   - Check file size limits
   - Verify supported file types
   - Ensure backend accepts multipart/form-data

### 🔑 Environment Variables (Optional)

Create a `.env` file for default configuration:
```env
BACKEND_URL=http://192.168.1.100:8000
MAX_FILE_SIZE=10485760
API_TIMEOUT=30
```

### 📞 Support

If you need help with backend integration:
1. Check the sidebar connection status
2. Use "🔍 Test Connection" button
3. Monitor browser developer console for errors
4. Check backend server logs

**Your frontend is now ready to connect to any backend API! 🚀**