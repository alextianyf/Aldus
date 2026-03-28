import axios from 'axios'

async function openFile(pdfPath) {
  await axios.post('http://localhost:8000/open', { path: pdfPath })
}

async function openFolder(pdfPath) {
  await axios.post('http://localhost:8000/open-folder', { path: pdfPath })
}

export default function PreviewPanel({ pdfUrl, pdfPath, loading, loadingMsg }) {
  if (loading) {
    return (
      <div className="preview-empty">
        <div className="preview-placeholder">
          <div className="spinner" />
          <p>{loadingMsg || 'Converting...'}</p>
        </div>
      </div>
    )
  }

  if (!pdfUrl) {
    return (
      <div className="preview-empty">
        <div className="preview-placeholder">
          <span className="preview-icon">📄</span>
          <p>PDF preview will appear here after conversion</p>
        </div>
      </div>
    )
  }

  return (
    <div className="preview-panel">
      <div className="preview-toolbar">
        <span className="preview-label">Preview</span>
        <div className="toolbar-actions">
          {pdfPath && (
            <>
              <button className="btn-open" onClick={() => openFolder(pdfPath)}>
                Show in folder
              </button>
              <button className="btn-open primary" onClick={() => openFile(pdfPath)}>
                Open in viewer ↗
              </button>
            </>
          )}
        </div>
      </div>
      <iframe src={pdfUrl} title="PDF Preview" className="preview-iframe" />
    </div>
  )
}
