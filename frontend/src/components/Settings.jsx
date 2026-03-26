export default function Settings({ author, onAuthorChange, onSave }) {
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
    </div>
  )
}
