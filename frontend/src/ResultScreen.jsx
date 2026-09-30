function ResultScreen() {
  return (
    <main className="result">
      <div className="toolbar">
        <button type="button" aria-label="Zoom out">−</button>
        <span className="zoom-level">100%</span>
        <button type="button" aria-label="Zoom in">+</button>
        <div className="spacer" />
        <button type="button" className="primary">Download PDF</button>
        <button type="button">Start over</button>
      </div>

      <div className="pdf-frame">
        <div className="pdf-page">PDF preview will appear here</div>
      </div>
    </main>
  )
}

export default ResultScreen