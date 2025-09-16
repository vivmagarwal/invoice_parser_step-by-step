import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App.jsx'
import * as serviceWorker from './utils/serviceWorker'

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <App />
  </StrictMode>,
)

// Temporarily disable service worker registration to fix loading issues
// TODO: Re-enable once service worker issues are resolved
// serviceWorker.register({
//   onSuccess: () => {
//     console.log('App is ready for offline use');
//   },
//   onUpdate: (registration) => {
//     console.log('New app version available');
//     // You could show a notification here
//   }
// });

// Unregister any existing service worker to clear the cache
serviceWorker.unregister();