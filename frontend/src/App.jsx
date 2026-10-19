import { useState } from 'react'
import SetupScreen from './SetupScreen'
import LoadingScreen from './LoadingScreen'
import ResultScreen from './ResultScreen'
import Icon from './Icon'
import { getUploadError } from './uploadValidation'
import './App.css'

function App() {
  const [view, setView] = useState('setup')
  const [files, setFiles] = useState([])
  const [settings, setSettings] = useState({
    font_size: 'footnotesize',
    columns: 2,
    margin: '1in',
    orientation: 'portrait',
  })
  const [prompts, setPrompts] = useState({ classifier: '', summarizer: '' })
  const [result, setResult] = useState(null)
  const [error, setError] = useState('')

  async function handleGenerate() {
    const uploadError = getUploadError(files)
    if (uploadError) {
      setError(uploadError)
      return
    }

    const form = new FormData()
    files.forEach((file) => form.append('files', file))
    form.append('settings', JSON.stringify(settings))
    form.append('classifier_prompt', prompts.classifier)
    form.append('summarizer_prompt', prompts.summarizer)

    setError('')
    setView('loading')

    try {
      const response = await fetch('/api/generate', { method: 'POST', body: form })
      if (response.status === 413) throw new Error('This upload is too large. Use up to 10 files, 25 MB per file, and 100 MB total.')
      const isJson = response.headers.get('content-type')?.includes('application/json')
      if (!isJson) throw new Error('The server returned an unexpected response. Check that Flask is running and try again.')

      const data = await response.json()
      if (!response.ok) throw new Error(data.error || 'Generation failed. Please try again.')
      if (!data.pdf_url || !data.tex_url) throw new Error('The server did not return download links.')

      setResult(data)
      setView('result')
    } catch (error) {
      setError(error.message === 'Failed to fetch'
        ? 'Could not reach the server. Check that Flask is running and try again.'
        : error.message)
      setView('setup')
    }
  }

  function handleStartOver() {
    setResult(null)
    setFiles([])
    setPrompts({ classifier: '', summarizer: '' })
    setView('setup')
  }

  function handleFilesChange(selectedFiles) {
    setFiles(selectedFiles)
    setError('')
  }

  return (
    <div className="app">
      <header className="site-header">
        <div className="header-inner">
          <a className="brand" href="/">
            <span className="brand-icon"><Icon name="layers" /></span>
            CheatSheet<span className="brand-light">Maker</span>
          </a>
          <span className="header-note">LESS MATERIAL. MORE CLARITY.</span>
        </div>
      </header>

      <div className="workspace">
        <nav className="workflow" aria-label="Generation progress">
          {['Configure', 'Generate', 'Your cheatsheet'].map((label, index) => {
            const current = ['setup', 'loading', 'result'].indexOf(view)
            return (
              <div
                key={label}
                className={`workflow-step ${index === current ? 'current' : ''} ${index < current ? 'complete' : ''}`}
                aria-current={index === current ? 'step' : undefined}
              >
                <span>{index < current ? <Icon name="check" size={14} /> : `0${index + 1}`}</span>
                {label}
              </div>
            )
          })}
        </nav>

        {view === 'setup' && (
          <SetupScreen
            files={files}
            setFiles={handleFilesChange}
            settings={settings}
            setSettings={setSettings}
            prompts={prompts}
            setPrompts={setPrompts}
            error={error}
            onGenerate={handleGenerate}
          />
        )}
        {view === 'loading' && <LoadingScreen fileCount={files.length} />}
        {view === 'result' && <ResultScreen result={result} onStartOver={handleStartOver} />}
      </div>

      <footer className="site-footer">
        <span>From lecture notes to the essentials.</span>
        <span>Built for focused learning <Icon name="sparkles" size={14} /></span>
      </footer>
    </div>
  )
}

export default App
