import { useState } from 'react'
import SetupScreen from './SetupScreen'
import LoadingScreen from './LoadingScreen'
import ResultScreen from './ResultScreen'
import './App.css'

function App() {
  const [view, setView] = useState('setup') // 'setup' | 'loading' | 'result'

  return (
    <div className="App">
      {/* DEV ONLY: delete once real logic decides the view */}
      <div className="dev-bar">
        {['setup', 'loading', 'result'].map((v) => (
          <button
            key={v}
            type="button"
            className={view === v ? 'active' : ''}
            onClick={() => setView(v)}
          >
            {v}
          </button>
        ))}
      </div>

      {view === 'setup' && <SetupScreen />}
      {view === 'loading' && <LoadingScreen />}
      {view === 'result' && <ResultScreen />}
    </div>
  )
}

export default App