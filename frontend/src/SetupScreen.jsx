import FileUpload from './FileUpload'

function SetupScreen() {
  function handleGenerateClick() {
    // TODO: later, this should switch the view to 'loading'
    // and send the file + settings to the backend
  }

  return (
    <main className="setup">
      <header className="header">
        <h1>CheatSheet Maker</h1>
      </header>
      <p className="description">
        Upload lecture notes or slides. The app extracts key definitions,
        theorems, formulas and examples, shortens the wording while keeping
        the math intact, and compiles a print-ready PDF based on your
        format settings.
      </p>

      <section className="step-card">
        <h2><span className="step-num">1</span> Upload your files</h2>
        <FileUpload />
      </section>

      <section className="step-card">
        <h2>
          <span className="step-num">2</span> Custom prompts
          <span className="optional">optional</span>
        </h2>
        <div className="field">
          <label htmlFor="classifier-prompt">Classifier prompt</label>
          <textarea
            id="classifier-prompt"
            rows="3"
            placeholder="e.g. Ignore administrative slides and focus on proofs"
          />
        </div>
        <div className="field">
          <label htmlFor="summarizer-prompt">Summarizer prompt</label>
          <textarea
            id="summarizer-prompt"
            rows="3"
            placeholder="e.g. Keep definitions word-for-word, shorten examples"
          />
        </div>
      </section>

      <section className="step-card">
        <h2><span className="step-num">3</span> Format settings</h2>
        <div className="settings-grid">
          <div className="field">
            <label htmlFor="font-size">Font size</label>
            <select id="font-size" defaultValue="footnotesize">
              <option value="tiny">tiny</option>
              <option value="scriptsize">scriptsize</option>
              <option value="footnotesize">footnotesize</option>
              <option value="small">small</option>
              <option value="normalsize">normalsize</option>
            </select>
          </div>

          <div className="field">
            <label htmlFor="columns">Columns</label>
            <select id="columns" defaultValue="2">
              <option value="1">1</option>
              <option value="2">2</option>
              <option value="3">3</option>
              <option value="4">4</option>
            </select>
          </div>

          <div className="field">
            <label htmlFor="margin">Margin</label>
            <input id="margin" type="text" defaultValue="1in" />
          </div>

          <div className="field">
            <span className="label">Orientation</span>
            <div className="segmented">
              <input type="radio" name="orientation" id="portrait" value="portrait" defaultChecked />
              <label htmlFor="portrait">Portrait</label>
              <input type="radio" name="orientation" id="landscape" value="landscape" />
              <label htmlFor="landscape">Landscape</label>
            </div>
          </div>
        </div>
      </section>

      <section className="generate-section">
        <button type="button" className="generate-btn" onClick={handleGenerateClick}>
          Generate cheatsheet
        </button>
      </section>
    </main>
  )
}

export default SetupScreen