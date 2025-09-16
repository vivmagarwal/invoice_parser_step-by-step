# Teacher Notes - STEP 009: Dashboard & Analytics

## Learning Objectives
By the end of this step, students will be able to:
1. ✅ Create interactive dashboards
2. ✅ Implement data analytics
3. ✅ Build charts and visualizations
4. ✅ Add real-time statistics
5. ✅ Create complete frontend UI

## Prerequisites
- Completed Step 008 (Complete Invoice Processing)
- Understanding of React components
- Basic knowledge of data visualization

## Time Estimate
- **Teaching**: 3-4 hours
- **Practice**: 2-3 hours
- **Total**: 5-7 hours

## Key Features Added in This Step

### 1. Analytics Service
- Data aggregation
- Statistical calculations
- Trend analysis
- Performance metrics

### 2. Complete Frontend
- Dashboard page
- Invoice list with filters
- Upload interface
- User profile management
- Settings page

### 3. Data Visualizations
- Charts (using Recharts)
- Statistics cards
- Progress indicators
- Activity timeline

## Setup Instructions

```bash
# Navigate to the step directory
cd invoice-parser-step009/ending-code

# Backend setup
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8009

# Frontend setup (new terminal)
cd frontend
npm install
npm run dev
```

## Frontend Components Structure

### Dashboard Component
```jsx
// pages/Dashboard.jsx
import { useState, useEffect } from 'react';
import { LineChart, BarChart } from 'recharts';
import StatsCard from '../components/StatsCard';

function Dashboard() {
  const [stats, setStats] = useState(null);
  const [chartData, setChartData] = useState([]);

  useEffect(() => {
    fetchAnalytics();
  }, []);

  const fetchAnalytics = async () => {
    const response = await fetch('/api/analytics/dashboard');
    const data = await response.json();
    setStats(data.stats);
    setChartData(data.chartData);
  };

  return (
    <div className="dashboard">
      <div className="stats-grid">
        <StatsCard title="Total Invoices" value={stats?.totalInvoices} />
        <StatsCard title="Total Amount" value={stats?.totalAmount} />
        <StatsCard title="This Month" value={stats?.thisMonth} />
      </div>

      <div className="charts">
        <LineChart data={chartData} />
        <BarChart data={chartData} />
      </div>
    </div>
  );
}
```

### Invoice List Component
```jsx
// components/InvoiceList.jsx
import { useState } from 'react';
import InvoiceCard from './InvoiceCard';
import FilterPanel from './FilterPanel';
import Pagination from './Pagination';

function InvoiceList() {
  const [invoices, setInvoices] = useState([]);
  const [filters, setFilters] = useState({});
  const [page, setPage] = useState(1);

  const handleFilter = (newFilters) => {
    setFilters(newFilters);
    fetchInvoices(newFilters, 1);
  };

  const fetchInvoices = async (filters, page) => {
    const query = new URLSearchParams({ ...filters, page });
    const response = await fetch(`/api/invoices?${query}`);
    const data = await response.json();
    setInvoices(data.invoices);
  };

  return (
    <div className="invoice-list-container">
      <FilterPanel onFilter={handleFilter} />
      <div className="invoice-grid">
        {invoices.map(invoice => (
          <InvoiceCard key={invoice.id} invoice={invoice} />
        ))}
      </div>
      <Pagination
        currentPage={page}
        onPageChange={setPage}
        totalPages={10}
      />
    </div>
  );
}
```

## Backend Analytics Implementation

### Analytics Service
```python
# app/services/analytics_service.py
class AnalyticsService:
    async def get_dashboard_stats(self, user_id: int):
        """Get dashboard statistics for user"""

        # Total invoices
        total_invoices = await self.db.query(Invoice).filter_by(
            user_id=user_id
        ).count()

        # Total amount
        total_amount = await self.db.query(
            func.sum(Invoice.total_amount)
        ).filter_by(user_id=user_id).scalar()

        # This month
        start_of_month = datetime.now().replace(day=1)
        this_month = await self.db.query(Invoice).filter(
            Invoice.user_id == user_id,
            Invoice.created_at >= start_of_month
        ).count()

        # Chart data
        chart_data = await self.get_monthly_trend(user_id)

        return {
            "stats": {
                "totalInvoices": total_invoices,
                "totalAmount": total_amount or 0,
                "thisMonth": this_month
            },
            "chartData": chart_data
        }

    async def get_monthly_trend(self, user_id: int):
        """Get monthly invoice trend"""
        # SQL query to group by month
        result = await self.db.query(
            func.date_trunc('month', Invoice.created_at).label('month'),
            func.count(Invoice.id).label('count'),
            func.sum(Invoice.total_amount).label('total')
        ).filter_by(user_id=user_id).group_by('month').all()

        return [
            {
                "month": row.month.strftime("%B"),
                "count": row.count,
                "total": float(row.total or 0)
            }
            for row in result
        ]
```

### Analytics API Endpoints
```python
# app/api/routes/analytics.py
@router.get("/dashboard")
async def get_dashboard_analytics(
    current_user: User = Depends(get_current_user),
    analytics: AnalyticsService = Depends(get_analytics_service)
):
    """Get dashboard analytics data"""
    return await analytics.get_dashboard_stats(current_user.id)

@router.get("/export")
async def export_analytics(
    format: str = "csv",
    current_user: User = Depends(get_current_user),
    analytics: AnalyticsService = Depends(get_analytics_service)
):
    """Export analytics data"""
    data = await analytics.get_export_data(current_user.id)

    if format == "csv":
        return StreamingResponse(
            generate_csv(data),
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=analytics.csv"}
        )
    elif format == "json":
        return data
```

## Testing the Implementation

### Test Dashboard
1. Navigate to http://localhost:5173/dashboard
2. Check statistics cards update
3. Verify charts render correctly
4. Test date range filters

### Test Invoice List
1. Navigate to http://localhost:5173/invoices
2. Test search functionality
3. Apply filters
4. Check pagination

### API Testing
```bash
# Get dashboard stats
curl http://localhost:8009/api/analytics/dashboard \
  -H "Authorization: Bearer $TOKEN"

# Export data
curl http://localhost:8009/api/analytics/export?format=csv \
  -H "Authorization: Bearer $TOKEN" \
  -o analytics.csv
```

## Common Issues and Solutions

### Issue 1: Chart Not Rendering
**Solution:** Ensure Recharts is installed and data format matches

### Issue 2: Stats Not Updating
**Solution:** Check WebSocket connection for real-time updates

### Issue 3: Slow Dashboard Load
**Solution:** Implement caching for analytics queries

## Assessment Points
1. Can create interactive dashboards
2. Understands data aggregation
3. Can implement charts and visualizations
4. Handles real-time updates

## Key Takeaways
- Analytics provide business value
- Dashboard UX is crucial
- Performance optimization matters
- Real-time updates enhance user experience

## Files Modified/Created
- `app/services/analytics_service.py` - NEW
- `frontend/src/pages/Dashboard.jsx` - NEW
- `frontend/src/components/` - Multiple new components
- Complete frontend UI implementation
- Analytics API endpoints

## Connection to Next Steps
Step 010 will add:
- Production optimizations
- Security enhancements
- Monitoring and logging
- Deployment configuration