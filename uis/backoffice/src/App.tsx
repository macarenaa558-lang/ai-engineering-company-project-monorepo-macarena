import { useState, type ChangeEvent, type DragEvent } from 'react'
import './App.css'

type AnalysisResult = {
  total_records: number
  valid_records: number
  invalid_records: number
  error_counts: {
    missing_location: number
    invalid_category: number
    empty_description: number
    missing_reporter: number
    invalid_status: number
    closed_without_score: number
    score_out_of_range: number
  }
  category_counts: Record<string, number>
  status_counts: Record<string, number>
  scored_cases: number
  closed_cases: number
  average_score: number
  score_counts: Record<string, number>
}

function App() {
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [analysis, setAnalysis] = useState<AnalysisResult | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const chooseFile = (file: File | undefined) => {
    setError('')
    setAnalysis(null)

    if (!file) {
      return
    }

    if (!file.name.toLowerCase().endsWith('.csv')) {
      setSelectedFile(null)
      setError('Please select a CSV file.')
      return
    }

    setSelectedFile(file)
  }

  const handleFileChange = (event: ChangeEvent<HTMLInputElement>) => {
    chooseFile(event.target.files?.[0])
  }

  const handleDrop = (event: DragEvent<HTMLDivElement>) => {
    event.preventDefault()
    chooseFile(event.dataTransfer.files?.[0])
  }

  const handleAnalyze = async () => {
    if (!selectedFile) {
      setError('Select a CSV file before starting the analysis.')
      return
    }

    const formData = new FormData()
    formData.append('file', selectedFile)

    setLoading(true)
    setError('')

    try {
      const response = await fetch('/api/incidents/analyze', {
        method: 'POST',
        body: formData,
      })

      const data = await response.json()

      if (!response.ok) {
        throw new Error(data.detail || 'The file could not be analyzed.')
      }

      setAnalysis(data)
    } catch (err) {
      setAnalysis(null)

      if (err instanceof Error) {
        setError(err.message)
      } else {
        setError('An unexpected error occurred.')
      }
    } finally {
      setLoading(false)
    }
  }

  const handleDownload = async () => {
    try {
      const response = await fetch('/api/incidents/results/export')

      if (!response.ok) {
        throw new Error('The results could not be downloaded.')
      }

      const blob = await response.blob()
      const url = window.URL.createObjectURL(blob)
      const link = document.createElement('a')

      link.href = url
      link.download = 'incident-analysis-results.csv'
      document.body.appendChild(link)
      link.click()
      link.remove()

      window.URL.revokeObjectURL(url)
    } catch (err) {
      if (err instanceof Error) {
        setError(err.message)
      }
    }
  }

  const percentage = (value: number) => {
    if (!analysis || analysis.valid_records === 0) {
      return 0
    }

    return (value / analysis.valid_records) * 100
  }

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand">
          <div className="brand-mark">B</div>

          <div>
            <strong>Brasaland</strong>
            <span>Digital Backoffice</span>
          </div>
        </div>

        <nav className="nav-menu">
          <span className="nav-label">OPERATIONS</span>
          <button className="nav-item active">
            Incident Analysis
          </button>
        </nav>

        <div className="sidebar-footer">
          Brasaland Digital
          <span>Operations Intelligence</span>
        </div>
      </aside>

      <main className="main-content">
        <header className="page-header">
          <div>
            <span className="eyebrow">OPERATIONS</span>
            <h1>Incident Analysis</h1>
            <p>
              Upload the monthly incident report to validate records and
              generate operational metrics.
            </p>
          </div>

          {analysis && (
            <button
              type="button"
              className="download-button"
              onClick={handleDownload}
            >
              Download CSV
            </button>
          )}
        </header>

        <section className="upload-card">
          <div
            className="drop-zone"
            onDragOver={(event) => event.preventDefault()}
            onDrop={handleDrop}
          >
            <div className="upload-icon">↑</div>

            <h2>Upload incident report</h2>

            <p>
              Drag and drop your CSV file here or select it from your device.
            </p>

            <label className="file-button">
              Select CSV
              <input
                type="file"
                accept=".csv,text/csv"
                onChange={handleFileChange}
              />
            </label>

            {selectedFile && (
              <div className="selected-file">
                Selected file: <strong>{selectedFile.name}</strong>
              </div>
            )}
          </div>

          <button
            type="button"
            className="analyze-button"
            onClick={handleAnalyze}
            disabled={!selectedFile || loading}
          >
            {loading ? 'Analyzing...' : 'Analyze incidents'}
          </button>

          {error && <div className="error-message">{error}</div>}
        </section>

        {analysis && (
          <>
            <section className="metrics-grid">
              <article className="metric-card">
                <span>Total records</span>
                <strong>{analysis.total_records}</strong>
              </article>

              <article className="metric-card valid">
                <span>Valid records</span>
                <strong>{analysis.valid_records}</strong>
              </article>

              <article className="metric-card invalid">
                <span>Invalid records</span>
                <strong>{analysis.invalid_records}</strong>
              </article>

              <article className="metric-card score">
                <span>Average satisfaction</span>
                <strong>{analysis.average_score.toFixed(2)}</strong>
                <small>/ 5.00</small>
              </article>
            </section>

            <div className="analysis-grid">
              <section className="panel">
                <div className="panel-header">
                  <div>
                    <span className="eyebrow">VALID RECORDS</span>
                    <h2>Incidents by category</h2>
                  </div>
                </div>

                <div className="bar-list">
                  {Object.entries(analysis.category_counts).map(
                    ([category, count]) => (
                      <div className="bar-row" key={category}>
                        <div className="bar-info">
                          <span>{category.replaceAll('_', ' ')}</span>
                          <strong>
                            {count} ({percentage(count).toFixed(1)}%)
                          </strong>
                        </div>

                        <div className="bar-track">
                          <div
                            className="bar-fill"
                            style={{
                              width: `${percentage(count)}%`,
                            }}
                          />
                        </div>
                      </div>
                    ),
                  )}
                </div>
              </section>

              <section className="panel">
                <div className="panel-header">
                  <div>
                    <span className="eyebrow">VALID RECORDS</span>
                    <h2>Incidents by status</h2>
                  </div>
                </div>

                <div className="status-list">
                  {Object.entries(analysis.status_counts).map(
                    ([status, count]) => (
                      <div className="status-row" key={status}>
                        <div>
                          <span className={`status-dot ${status.toLowerCase()}`} />
                          {status}
                        </div>

                        <strong>
                          {count} ({percentage(count).toFixed(1)}%)
                        </strong>
                      </div>
                    ),
                  )}
                </div>
              </section>
            </div>

            <div className="analysis-grid">
              <section className="panel">
                <div className="panel-header">
                  <div>
                    <span className="eyebrow">DATA QUALITY</span>
                    <h2>Invalid records</h2>
                  </div>

                  <strong className="panel-total">
                    {analysis.invalid_records}
                  </strong>
                </div>

                <div className="issue-list">
                  <div>
                    <span>Missing location_id</span>
                    <strong>{analysis.error_counts.missing_location}</strong>
                  </div>

                  <div>
                    <span>Invalid or missing category</span>
                    <strong>{analysis.error_counts.invalid_category}</strong>
                  </div>

                  <div>
                    <span>Empty description</span>
                    <strong>{analysis.error_counts.empty_description}</strong>
                  </div>

                  <div>
                    <span>Missing reporter_id</span>
                    <strong>{analysis.error_counts.missing_reporter}</strong>
                  </div>

                  <div>
                    <span>Invalid or missing status</span>
                    <strong>{analysis.error_counts.invalid_status}</strong>
                  </div>

                  <div>
                    <span>Closed case, no score</span>
                    <strong>{analysis.error_counts.closed_without_score}</strong>
                  </div>

                  <div>
                    <span>Satisfaction score out of range</span>
                    <strong>{analysis.error_counts.score_out_of_range}</strong>
                  </div>
                </div>
              </section>

              <section className="panel">
                <div className="panel-header">
                  <div>
                    <span className="eyebrow">CUSTOMER EXPERIENCE</span>
                    <h2>Satisfaction index</h2>
                  </div>

                  <div className="average-badge">
                    {analysis.average_score.toFixed(2)}
                    <span>/5</span>
                  </div>
                </div>

                <p className="scored-summary">
                  {analysis.scored_cases} scored cases of{' '}
                  {analysis.closed_cases} closed cases
                </p>

                <div className="score-list">
                  {[5, 4, 3, 2, 1].map((score) => (
                    <div className="score-row" key={score}>
                      <span>{score} ★</span>

                      <div className="score-track">
                        <div
                          className="score-fill"
                          style={{
                            width: `${
                              analysis.scored_cases
                                ? ((analysis.score_counts[String(score)] || 0) /
                                    analysis.scored_cases) *
                                  100
                                : 0
                            }%`,
                          }}
                        />
                      </div>

                      <strong>
                        {analysis.score_counts[String(score)] || 0}
                      </strong>
                    </div>
                  ))}
                </div>
              </section>
            </div>
          </>
        )}
      </main>
    </div>
  )
}

export default App