import { useState } from 'react'

function FileUpload() {
  const [file, setFile] = useState(null)

  function handleFileChange(e) {
    // TODO: get the selected File out of e.target.files (it's a FileList)
    // and store it with setFile
  }

  return (
    <div className="upload-section">
      <input type="file" onChange={handleFileChange} />
      {file && <p className="file-name">{file.name}</p>}
    </div>
  )
}

export default FileUpload