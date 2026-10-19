import FileUpload from './FileUpload'
import Icon from './Icon'

function SetupScreen({ files, setFiles, settings, setSettings, prompts, setPrompts, error, onGenerate }) {
  function updateSettings(event) {
    const { name, value } = event.target
    setSettings({ ...settings, [name]: name === 'columns' ? Number(value) : value })
  }

  function handleSubmit(event) {
    event.preventDefault()
    onGenerate()
  }

  return (
    <main>
      <div className="page-heading">
        <span className="eyebrow">YOUR NOTES, SIMPLIFIED</span>
        <h1>Make room for what matters.</h1>
        <p>Turn your lecture materials into a clear, concise cheatsheet.<br className="desktop-break" /> Keep the key ideas. Leave the information overload behind.</p>
      </div>

      <div className="setup-layout">
        <form onSubmit={handleSubmit}>
          <section className="card">
            <div className="card-heading"><span className="section-number">01</span><div><h2>Add your materials</h2><p>Start with your lecture notes, slides, or readings.</p></div></div>
            <FileUpload files={files} setFiles={setFiles} />
          </section>

          <section className="card">
            <div className="card-heading"><span className="section-number">02</span><div><h2>Make it your own</h2><p>Choose a layout that works for your exam.</p></div></div>
            <div className="settings-grid">
              <div className="field">
                <label htmlFor="font-size">Font size</label>
                <select id="font-size" name="font_size" value={settings.font_size} onChange={updateSettings}>
                  <option value="tiny">Tiny</option>
                  <option value="scriptsize">Extra small</option>
                  <option value="footnotesize">Small (recommended)</option>
                  <option value="small">Medium</option>
                  <option value="normalsize">Standard</option>
                </select>
              </div>
              <div className="field">
                <label htmlFor="columns">Columns</label>
                <select id="columns" name="columns" value={settings.columns} onChange={updateSettings}>
                  {[1, 2, 3, 4].map((number) => <option key={number} value={number}>{number} {number === 1 ? 'column' : 'columns'}</option>)}
                </select>
              </div>
              <div className="field">
                <label htmlFor="margin">Page margins</label>
                <input id="margin" name="margin" type="text" value={settings.margin} onChange={updateSettings} required pattern="[0-9]+([.][0-9]+)?(in|cm|mm|pt)" title="Use a positive measurement such as 1in, 1.5cm, or 10mm" />
                <span className="field-hint">For example: 1in, 1.5cm, or 10mm</span>
              </div>
              <fieldset className="field orientation-field">
                <legend>Orientation</legend>
                <div className="segmented">
                  {['portrait', 'landscape'].map((orientation) => (
                    <label key={orientation}>
                      <input type="radio" name="orientation" value={orientation} checked={settings.orientation === orientation} onChange={updateSettings} />
                      <span><span className={`paper-icon ${orientation}`} />{orientation === 'portrait' ? 'Portrait' : 'Landscape'}</span>
                    </label>
                  ))}
                </div>
              </fieldset>
            </div>

            <details className="advanced-options">
              <summary><Icon name="settings" size={17} /> Advanced options <span>Optional</span></summary>
              <div className="advanced-fields">
                <p>Give the AI extra guidance about what to extract and how to condense it.</p>
                <div className="field">
                  <label htmlFor="classifier-prompt">Classifier prompt</label>
                  <textarea id="classifier-prompt" rows="3" maxLength={10000} value={prompts.classifier} onChange={(event) => setPrompts({ ...prompts, classifier: event.target.value })} placeholder="e.g. Focus on definitions and proofs. Ignore administrative slides." />
                </div>
                <div className="field">
                  <label htmlFor="summarizer-prompt">Summarizer prompt</label>
                  <textarea id="summarizer-prompt" rows="3" maxLength={10000} value={prompts.summarizer} onChange={(event) => setPrompts({ ...prompts, summarizer: event.target.value })} placeholder="e.g. Keep definitions word-for-word and shorten worked examples." />
                </div>
              </div>
            </details>
          </section>

          {error && <div className="error-message" role="alert"><strong>We couldn’t generate your cheatsheet.</strong><p>{error}</p></div>}
          <div className="generate-row">
            <span>{files.length ? `${files.length} ${files.length === 1 ? 'file' : 'files'} → 1 cheatsheet` : 'Add your materials to get started'}</span>
            <button className="button button-primary" type="submit" disabled={!files.length}>Generate cheatsheet <Icon name="arrow" size={18} /></button>
          </div>
        </form>

        <aside className="info-sidebar">
          <div className="sheet-illustration" aria-hidden="true">
            <div className={`sample-sheet ${settings.orientation}`}>
              <div className="sample-title" />
              <div className="sample-columns" style={{ gridTemplateColumns: `repeat(${settings.columns}, 1fr)` }}>
                {Array.from({ length: settings.columns }, (_, index) => <div key={index}>{Array.from({ length: 3 }, (_, section) => <div className="sample-section" key={section}><i /><b /><b /><b /><em>E = mc²</em><b /><b /></div>)}</div>)}
              </div>
              <span>THE ESSENTIALS, AT A GLANCE</span>
            </div>
            <span className="illustration-badge"><Icon name="sparkles" size={14} /> A little less, a lot clearer</span>
          </div>
          <h3>Big ideas. Small footprint.</h3>
          <p>All the essentials, organized into one focused reference.</p>
          <ul className="benefit-list">
            <li><Icon name="check" size={16} /> Key definitions and theorems</li>
            <li><Icon name="check" size={16} /> Formulas with math preserved</li>
            <li><Icon name="check" size={16} /> Concise explanations and examples</li>
            <li><Icon name="check" size={16} /> PDF and editable LaTeX source</li>
          </ul>
          <div className="sidebar-tip"><strong>A quick tip</strong><p>Smaller fonts and more columns fit more content. Check the PDF before printing.</p></div>
        </aside>
      </div>
    </main>
  )
}

export default SetupScreen
