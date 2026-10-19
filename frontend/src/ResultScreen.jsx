import Icon from './Icon'

function ResultScreen({ result, onStartOver }) {
  return (
    <main className="result-screen">
      <div className="result-heading">
        <div>
          <span className="success-label"><Icon name="check" size={15} /> READY TO REVIEW</span>
          <h1>Your essentials, all together.</h1>
          <p>Review your cheatsheet, then save a copy for your next study session.</p>
        </div>
        <button type="button" className="button button-secondary" onClick={onStartOver}>
          Create another <Icon name="arrow" size={17} />
        </button>
      </div>

      <section className="preview-card">
        <div className="preview-toolbar">
          <span><Icon name="file" size={18} /> cheatsheet.pdf</span>
          <div>
            <a className="button button-secondary" href={result.tex_url} download>
              LaTeX source <Icon name="download" size={16} />
            </a>
            <a className="button button-primary" href={result.pdf_url} download>
              Download PDF <Icon name="download" size={16} />
            </a>
          </div>
        </div>
        <iframe className="pdf-preview" title="Generated cheatsheet PDF" src={`${result.pdf_url}#view=FitH`} />
        <div className="preview-footer">
          <span>Check formulas and page count before printing.</span>
          <a href={result.pdf_url} target="_blank" rel="noreferrer">Open PDF in a new tab ↗</a>
        </div>
      </section>
    </main>
  )
}

export default ResultScreen
