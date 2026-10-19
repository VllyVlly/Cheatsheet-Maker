import { useRef, useState } from 'react'
import Icon from './Icon'
import { getUploadError, mergeFiles, maxFiles } from './uploadValidation'

function FileUpload({ files, setFiles }) {
  const inputRef = useRef(null)
  const [dragging, setDragging] = useState(false)
  const [error, setError] = useState('')
  const totalSize = files.reduce((total, file) => total + file.size, 0)

  function addFiles(selectedFiles) {
    if (!selectedFiles.length) return

    const combined = mergeFiles(files, selectedFiles)
    const uploadError = getUploadError(combined)

    if (uploadError) {
      setError(uploadError)
      return
    }

    setError('')
    setFiles(combined)
  }

  function removeFile(index) {
    setFiles(files.filter((_, fileIndex) => fileIndex !== index))
    setError('')
  }

  function handleDrop(event) {
    event.preventDefault()
    setDragging(false)
    addFiles(event.dataTransfer.files)
  }

  function handleFileChange(event) {
    addFiles(event.target.files)
    event.target.value = ''
  }

  return (
    <div>
      <input
        ref={inputRef}
        className="file-input"
        type="file"
        multiple
        accept=".pdf,.docx,.pptx"
        aria-label="Choose lecture files"
        tabIndex={-1}
        onChange={handleFileChange}
      />
      <button
        type="button"
        className={`upload-zone ${dragging ? 'dragging' : ''}`}
        onClick={() => inputRef.current.click()}
        onDragOver={(event) => { event.preventDefault(); setDragging(true) }}
        onDragLeave={() => setDragging(false)}
        onDrop={handleDrop}
      >
        <span className="upload-icon"><Icon name="upload" size={25} /></span>
        <strong>Drop your lecture materials here</strong>
        <span>or <span className="text-blue">browse files</span> from your computer</span>
        <small>PDF, DOCX, or PPTX · Up to 25 MB per file</small>
      </button>

      {error && <p className="field-error" role="alert">{error}</p>}
      {files.length > 0 && (
        <ul className="file-list">
          {files.map((file, index) => (
            <li key={`${file.name}-${file.size}-${file.lastModified}`}>
              <span className="file-icon"><Icon name="file" /></span>
              <div className="file-details">
                <strong>{file.name}</strong>
                <span>{(file.size / 1024 / 1024).toFixed(2)} MB · {file.name.split('.').pop().toUpperCase()}</span>
              </div>
              <button
                type="button"
                className="icon-button"
                aria-label={`Remove ${file.name}`}
                onClick={() => removeFile(index)}
              >
                <Icon name="close" size={17} />
              </button>
            </li>
          ))}
        </ul>
      )}
      <p className="upload-note" role="status">
        {files.length > 0 && `${files.length} of ${maxFiles} files · ${(totalSize / 1024 / 1024).toFixed(2)} of 100 MB selected. `}
        Combine up to 10 files into one cheatsheet. Maximum 25 MB per file and 100 MB total.
      </p>
    </div>
  )
}

export default FileUpload
