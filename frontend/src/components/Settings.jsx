export default function Settings({ author, onAuthorChange, footer, onFooterChange, pageNumbers, onPageNumbersChange, onSave }) {
  return (
    <div className="section">
      <label className="label">Author Name</label>
      <div className="input-row">
        <input
          className="input"
          type="text"
          placeholder="Your name..."
          value={author}
          onChange={e => onAuthorChange(e.target.value)}
        />
        <button className="btn-secondary" onClick={onSave}>Save</button>
      </div>
      <div className="toggle-row">
        <label className="toggle-label">
          <input
            type="checkbox"
            checked={footer}
            onChange={e => onFooterChange(e.target.checked)}
          />
          <span>Show footer</span>
        </label>
      </div>
      <div className="toggle-row">
        <label className="toggle-label">
          <input
            type="checkbox"
            checked={pageNumbers}
            onChange={e => onPageNumbersChange(e.target.checked)}
          />
          <span>Page numbers</span>
        </label>
      </div>
    </div>
  )
}
