import { useState } from 'react'
import './FileUpload.css'

function FileUpload() {
  const [file, setFile] = useState(null)

  function handleFileChange(e) {
    // TODO: get the selected File out of e.target.files (it's a FileList)
    // and store it with setFile
  }

  function handleGenerateClick() {
    // TODO: no backend yet — do something that lets you *verify*
    // `file` was captured correctly
  }

  return (
    <div className="upload-section">
      <input type="file" onChange={handleFileChange} />
      <button
        type="button"
        className="generate-btn"
        onClick={handleGenerateClick}
        // disabled={/* TODO: expression using `file` */}
      >
        Generate
      </button>
    </div>
  )
}

export default FileUpload