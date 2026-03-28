import axios from 'axios'

async function pickFile() {
  const res = await axios.get('http://localhost:8000/pick-file')
  return res.data.path
}

async function pickFolder() {
  const res = await axios.get('http://localhost:8000/pick-folder')
  return res.data.path
}

export default function FilePicker({ value, onChange }) {
  async function handleBrowseFile() {
    const path = await pickFile()
    if (path) onChange(path)
  }

  async function handleBrowseFolder() {
    const path = await pickFolder()
    if (path) onChange(path)
  }

  return (
    <div className="section">
      <label className="label">Input</label>
      <div className="input-row">
        <input
          className="input"
          type="text"
          placeholder="Paste a file or folder path..."
          value={value}
          onChange={e => onChange(e.target.value)}
        />
      </div>
      <div className="browse-row">
        <button className="btn-browse" onClick={handleBrowseFile}>Browse File</button>
        <button className="btn-browse" onClick={handleBrowseFolder}>Browse Folder</button>
      </div>
      <p className="hint">
        Single <code>.md</code> file → one PDF &nbsp;|&nbsp; Folder → converts all recursively
      </p>
    </div>
  )
}
