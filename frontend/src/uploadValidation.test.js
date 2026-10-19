import test from 'node:test'
import assert from 'node:assert/strict'
import { getUploadError, mergeFiles, maxFileSize, maxTotalFileSize } from './uploadValidation.js'

function makeFile(name, size = 1024, lastModified = 1) {
  return { name, size, lastModified }
}

test('accepts mixed file types and case-insensitive extensions', () => {
  const files = [makeFile('lecture.PDF'), makeFile('notes.docx'), makeFile('slides.pptx')]
  assert.equal(getUploadError(files), '')
})

test('accepts exact size and count limits', () => {
  const files = Array.from({ length: 10 }, (_, index) => makeFile(`${index}.pdf`, maxTotalFileSize / 10))
  assert.equal(getUploadError(files), '')
  assert.equal(getUploadError([makeFile('large.pdf', maxFileSize)]), '')
})

test('rejects too many files including files already selected', () => {
  const files = Array.from({ length: 10 }, (_, index) => makeFile(`${index}.pdf`))
  const combined = mergeFiles(files, [makeFile('extra.pdf')])
  assert.match(getUploadError(combined), /no more than 10/)
  assert.equal(files.length, 10)
})

test('rejects a batch over the combined size limit', () => {
  const files = Array.from({ length: 4 }, (_, index) => makeFile(`${index}.pdf`, maxFileSize))
  assert.match(getUploadError(mergeFiles(files, [makeFile('extra.docx', 1)])), /combined file size/)
})

test('identifies unsupported, empty, and oversized files', () => {
  assert.match(getUploadError([makeFile('wrong.txt')]), /wrong.txt.*PDF, DOCX, or PPTX/)
  assert.match(getUploadError([makeFile('empty.pdf', 0)]), /empty.pdf.*empty/)
  assert.match(getUploadError([makeFile('large.pdf', maxFileSize + 1)]), /large.pdf.*25 MB/)
  assert.match(getUploadError([]), /at least one/)
})

test('deduplicates existing files and duplicates within one selection', () => {
  const first = makeFile('first.pdf')
  const second = makeFile('second.pdf')
  assert.deepEqual(mergeFiles([first], [first, second, second]), [first, second])
})

test('preserves order and distinguishes files with different sizes or timestamps', () => {
  const first = makeFile('lecture.pdf')
  const updated = makeFile('lecture.pdf', 2048)
  const newer = makeFile('lecture.pdf', 1024, 2)
  assert.deepEqual(mergeFiles([first], [updated, newer]), [first, updated, newer])
})
