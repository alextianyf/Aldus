import { useEffect, useState } from 'react'
import FilePicker from './components/FilePicker'
import ThemeSelector from './components/ThemeSelector'
import Settings from './components/Settings'
import PreviewPanel from './components/PreviewPanel'
import ProgressLog from './components/ProgressLog'
import { getConfig, saveConfig, getThemes, convertFile, convertFolder, previewUrl } from './api'
import './App.css'

export default function App() {
  const [path, setPath]       = useState('')
  const [author, setAuthor]   = useState('')
  const [theme, setTheme]     = useState('default')
  const [themes, setThemes]   = useState(['default'])
  const [pdfUrl, setPdfUrl]   = useState(null)
  const [loading, setLoading] = useState(false)
  const [status, setStatus]   = useState('')
  const [results, setResults] = useState([])

  useEffect(() => {
    getConfig().then(c => {
      setAuthor(c.author || '')
      setTheme(c.theme || 'default')
    }).catch(() => {})

    getThemes().then(d => {
      if (d.themes.length > 0) setThemes(d.themes)
    }).catch(() => {})
  }, [])

  const isFolder = path.trim() && !path.trim().endsWith('.md')

  async function handleConvert() {
    if (!path.trim()) {
      setStatus('Please enter a file or folder path.')
      return
    }

    setLoading(true)
    setStatus('')
    setResults([])
    setPdfUrl(null)

    try {
      if (isFolder) {
        const res = await convertFolder({ folder_path: path.trim(), theme, author })
        setResults(res.results)
        setStatus(`Done — ${res.success} converted, ${res.failed} failed.`)
        const first = res.results.find(r => r.status === 'ok')
        if (first) setPdfUrl(previewUrl(first.pdf))
      } else {
        const res = await convertFile({ file_path: path.trim(), theme, author })
        setPdfUrl(previewUrl(res.pdf_path))
        setStatus('Conversion complete.')
      }
    } catch (err) {
      setStatus(`Error: ${err.response?.data?.detail || err.message}`)
    } finally {
      setLoading(false)
    }
  }

  async function handleSaveConfig() {
    try {
      await saveConfig({ author, theme })
      setStatus('Settings saved.')
    } catch {
      setStatus('Failed to save settings.')
    }
  }

  return (
    <div className="app">
      <div className="sidebar">
        <div className="sidebar-header">
          <h1 className="logo">Aldus</h1>
          <p className="tagline">Markdown → PDF</p>
        </div>

        <FilePicker value={path} onChange={setPath} />
        <ThemeSelector themes={themes} value={theme} onChange={setTheme} />
        <Settings author={author} onAuthorChange={setAuthor} onSave={handleSaveConfig} />

        <div className="section">
          <button className="btn-convert" onClick={handleConvert} disabled={loading}>
            {loading ? 'Converting...' : isFolder ? '⚡ Convert Folder' : '⚡ Convert'}
          </button>
        </div>

        {status && (
          <div className={`status-msg ${status.startsWith('Error') ? 'error' : 'success'}`}>
            {status}
          </div>
        )}

        <ProgressLog results={results} />
      </div>

      <div className="preview">
        <PreviewPanel pdfUrl={pdfUrl} />
      </div>
    </div>
  )
}
