export const maxFiles = 10
export const maxFileSize = 25 * 1024 * 1024
export const maxTotalFileSize = 100 * 1024 * 1024

const fileTypes = ['pdf', 'docx', 'pptx']

export function getUploadError(files) {
  if (!files.length) return 'Add at least one lecture file before generating.'
  if (files.length > maxFiles) return 'Choose no more than 10 files per cheatsheet.'

  for (const file of files) {
    const extension = file.name.split('.').pop().toLowerCase()
    if (!fileTypes.includes(extension)) return `${file.name}: choose a PDF, DOCX, or PPTX file.`
    if (file.size === 0) return `${file.name}: this file is empty.`
    if (file.size > maxFileSize) return `${file.name}: choose a file no larger than 25 MB.`
  }

  const totalSize = files.reduce((total, file) => total + file.size, 0)
  if (totalSize > maxTotalFileSize) return 'Keep the combined file size at or below 100 MB.'

  return ''
}

export function mergeFiles(files, selectedFiles) {
  const combined = [...files]

  for (const file of selectedFiles) {
    const duplicate = combined.some((existing) => (
      existing.name === file.name && existing.size === file.size && existing.lastModified === file.lastModified
    ))
    if (!duplicate) combined.push(file)
  }

  return combined
}
