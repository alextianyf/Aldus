export default function PreviewPanel({ pdfUrl }) {
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
      <iframe
        src={pdfUrl}
        title="PDF Preview"
        className="preview-iframe"
      />
    </div>
  )
}
