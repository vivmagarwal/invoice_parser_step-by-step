import { useState, useEffect } from 'react'
import axios from 'axios'
import { useTheme } from './contexts/ThemeContext'

function App() {
  const [apiData, setApiData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const { theme, toggleTheme } = useTheme()

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
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 transition-colors">
      {/* Header */}
      <header className="bg-gradient-to-r from-purple-600 to-indigo-600 dark:from-purple-800 dark:to-indigo-800 text-white">
        <div className="container mx-auto px-4 py-6">
          <div className="flex justify-between items-center">
            <div>
              <h1 className="text-3xl font-bold">Invoice Parser AI</h1>
              <p className="text-purple-100 mt-1">Upload invoices and extract data automatically</p>
            </div>
            <button
              onClick={toggleTheme}
              className="p-2 rounded-lg bg-white/20 hover:bg-white/30 transition-colors"
              aria-label="Toggle theme"
            >
              {theme === 'light' ? '🌙' : '☀️'}
            </button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-4 py-8">
        <div className="max-w-2xl mx-auto">
          {/* Status Card */}
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6 transition-colors">
            <h2 className="text-2xl font-semibold text-gray-900 dark:text-white mb-4">
              API Status
            </h2>

            {loading && (
              <div className="flex items-center space-x-2">
                <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-indigo-600"></div>
                <span className="text-gray-600 dark:text-gray-400">Loading...</span>
              </div>
            )}

            {error && (
              <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-4">
                <p className="text-red-600 dark:text-red-400 font-medium">{error}</p>
              </div>
            )}

            {apiData && (
              <div className="space-y-4">
                <div className="bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-lg p-4">
                  <p className="text-green-600 dark:text-green-400 font-medium">
                    ✓ Connected to API
                  </p>
                </div>

                <div className="text-gray-700 dark:text-gray-300">
                  <p className="text-lg">{apiData.message}</p>
                </div>

                <div className="border-t dark:border-gray-700 pt-4">
                  <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
                    Features
                  </h3>
                  <p className="text-gray-600 dark:text-gray-400">{apiData.data.feature}</p>
                  <div className="mt-2">
                    <span className="text-sm text-gray-500 dark:text-gray-500">Supported formats: </span>
                    <div className="flex gap-2 mt-1">
                      {apiData.data.supported_formats.map(format => (
                        <span
                          key={format}
                          className="px-2 py-1 bg-indigo-100 dark:bg-indigo-900/30 text-indigo-700 dark:text-indigo-400 rounded text-sm"
                        >
                          {format}
                        </span>
                      ))}
                    </div>
                  </div>
                </div>
              </div>
            )}

            <button
              onClick={fetchApiData}
              className="mt-6 w-full bg-indigo-600 hover:bg-indigo-700 dark:bg-indigo-500 dark:hover:bg-indigo-600 text-white font-medium py-2 px-4 rounded-lg transition-colors"
            >
              Refresh Status
            </button>
          </div>

          {/* Info Cards */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-6">
            <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-4 transition-colors">
              <h3 className="font-semibold text-gray-900 dark:text-white mb-2">Quick Start</h3>
              <p className="text-sm text-gray-600 dark:text-gray-400">
                Upload your invoice images and let AI extract the data automatically.
              </p>
            </div>
            <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-4 transition-colors">
              <h3 className="font-semibold text-gray-900 dark:text-white mb-2">Secure Processing</h3>
              <p className="text-sm text-gray-600 dark:text-gray-400">
                Your data is processed securely and stored with encryption.
              </p>
            </div>
          </div>
        </div>
      </main>
    </div>
  )
}

export default App