import Icon from './Icon'

function LoadingScreen({ fileCount }) {
  return (
    <main className="loading-screen" aria-live="polite" aria-busy="true">
      <div className="processing-visual"><div className="processing-ring" /><span><Icon name="layers" size={36} /></span></div>
      <span className="eyebrow">GOOD NOTES TAKE SHAPE</span>
      <h1>A clearer view is on its way.</h1>
      <p>We’re turning {fileCount === 1 ? 'your file' : `your ${fileCount} files`} into one focused cheatsheet.<br />This can take a few minutes. Keep this page open.</p>
      <div className="processing-status"><span className="status-dot" /> Processing your materials <span className="status-label">In progress</span></div>
      <div className="pipeline-explanation"><span>Extract content</span><Icon name="arrow" size={14} /><span>Condense ideas</span><Icon name="arrow" size={14} /><span>Create PDF</span></div>
      <p className="loading-note">Your formatting and custom prompts are included in this request.</p>
    </main>
  )
}

export default LoadingScreen
