import { useState, useEffect } from 'react'
import axios from 'axios'
import './App.css'

function App() {
  const [apiData, setApiData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    fetchApiData()
  }, [])

  const fetchApiData = async () => {
    try {
      setLoading(true)
      const response = await axios.get('http://localhost:8000/api/test')
      setApiData(response.data)
      setError(null)
    } catch (err) {
      setError('Failed to connect to API')
      console.error('API Error:', err)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="app">
      <header className="app-header">
        <h1>Invoice Parser AI</h1>
        <p>Upload invoices and extract data automatically</p>
      </header>

      <main className="app-main">
        <div className="status-card">
          <h2>API Status</h2>
          {loading && <p>Loading...</p>}
          {error && <p className="error">{error}</p>}
          {apiData && (
            <div className="api-info">
              <p className="success">✓ Connected to API</p>
              <p>{apiData.message}</p>
              <div className="features">
                <h3>Features:</h3>
                <p>{apiData.data.feature}</p>
                <p>Supported formats: {apiData.data.supported_formats.join(', ')}</p>
              </div>
            </div>
          )}
          <button onClick={fetchApiData}>Refresh</button>
        </div>
      </main>
    </div>
  )
}

export default App