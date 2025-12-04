import { useState } from 'react'
import './App.css'

function App() {
  const [loaded, setLoaded] = useState(false)

  return (
    <div style={{ position: 'fixed', inset: 0 }}>
      {!loaded && (
        <div style={{
          position: 'absolute', inset: 0, display: 'flex', alignItems: 'center', justifyContent: 'center',
          color: '#555'
        }}>
          Loading planner…
        </div>
      )}
      <iframe
        title="Streamlit App"
        src="/streamlit/"
        style={{ border: 'none', width: '100%', height: '100%' }}
        onLoad={() => setLoaded(true)}
      />
    </div>
  )
}

export default App
