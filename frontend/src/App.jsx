import { useEffect, useState } from 'react'
import FilePicker from './components/FilePicker'
import ThemeSelector from './components/ThemeSelector'
import Settings from './components/Settings'
import PreviewPanel from './components/PreviewPanel'
import ProgressLog from './components/ProgressLog'
import { getConfig, saveConfig, getThemes, convertFile, convertFolder, previewUrl } from './api'
import './App.css'

export default function App() {
  const [path, setPath]         = useState('')
  const [author, setAuthor]     = useState('')
  const [theme, setTheme]       = useState('default')
  const [themes, setThemes]     = useState(['default'])
  const [footer, setFooter]     = useState(true)
  const [pdfUrl, setPdfUrl]     = useState(null)
  const [pdfPath, setPdfPath]   = useState(null)
  const [loading, setLoading]   = useState(false)
  const [loadingMsg, setLoadingMsg] = useState('')
  const [status, setStatus]     = useState('')
  const [results, setResults]   = useState([])

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

  function validate() {
    const p = path.trim()
    if (!p) return 'Please enter or browse a file or folder path.'
    if (p.endsWith('.md') === false && p.includes('.')) return 'Invalid input — select a .md file or a folder.'
    return null
  }

  async function handleConvert() {
    const err = validate()
    if (err) { setStatus(err); return }

    setLoading(true)
    setStatus('')
    setResults([])
    setPdfUrl(null)
    setPdfPath(null)

    try {
      if (isFolder) {
        setLoadingMsg('Converting folder...')
        const res = await convertFolder({
          folder_path: path.trim(), theme, author, include_footer: footer,
        })
        setResults(res.results)
        if (res.failed === 0) {
          setStatus(`Done — ${res.success} file${res.success !== 1 ? 's' : ''} converted.`)
        } else {
          setStatus(`Done — ${res.success} converted, ${res.failed} failed. Check the log below.`)
        }
        const first = res.results.find(r => r.status === 'ok')
        if (first) { setPdfUrl(previewUrl(first.pdf)); setPdfPath(first.pdf) }
      } else {
        setLoadingMsg('Converting...')
        const res = await convertFile({
          file_path: path.trim(), theme, author, include_footer: footer,
        })
        setPdfUrl(previewUrl(res.pdf_path))
        setPdfPath(res.pdf_path)
        setStatus('Conversion complete.')
      }
    } catch (err) {
      const detail = err.response?.data?.detail || err.message
      if (detail.includes('not found') || detail.includes('No such file')) {
        setStatus('File or folder not found. Check the path and try again.')
      } else if (detail.includes('No markdown files')) {
        setStatus('No .md files found in that folder.')
      } else {
        setStatus(`Error: ${detail}`)
      }
    } finally {
      setLoading(false)
      setLoadingMsg('')
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
        <Settings
          author={author}
          onAuthorChange={setAuthor}
          footer={footer}
          onFooterChange={setFooter}
          onSave={handleSaveConfig}
        />

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
        <PreviewPanel
          pdfUrl={pdfUrl}
          pdfPath={pdfPath}
          loading={loading}
          loadingMsg={loadingMsg}
        />
      </div>
    </div>
  )
}
