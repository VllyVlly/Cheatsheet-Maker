const STAGES = ['Parsing your files', 'Classifying content', 'Assembling LaTeX', 'Compiling PDF']

function LoadingScreen() {
  const currentStage = 1 // hardcoded for now; later the backend status drives this

  return (
    <main className="loading">
      <div className="spinner" />
      <h2>Building your cheatsheet…</h2>
      <p className="hint">This can take a few minutes for large files.</p>

      <ul className="stages">
        {STAGES.map((name, i) => {
          const state = i < currentStage ? 'done' : i === currentStage ? 'active' : 'pending'
          return (
            <li key={name} className={`stage ${state}`}>
              <span className="dot" />
              {name}
            </li>
          )
        })}
      </ul>
    </main>
  )
}

export default LoadingScreen