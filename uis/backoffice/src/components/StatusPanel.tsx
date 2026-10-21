import { useMemo } from 'react'
import type { AnalysisResult } from '../types/analysis'

type Props = { analysis: AnalysisResult }

export default function StatusPanel({ analysis }: Props) {
  const statuses = useMemo(() => {
    return Object.entries(analysis.status_counts).map(([name, count]) => ({
      name,
      count,
      percentage: analysis.valid_records
        ? (count / analysis.valid_records) * 100
        : 0,
    }))
  }, [analysis.status_counts, analysis.valid_records])

  return (
              <section className="panel">
                <div className="panel-header">
                  <div>
                    <span className="eyebrow">VALID RECORDS</span>
                    <h2>Incidents by status</h2>
                  </div>
                </div>

                <div className="status-list">
                  {statuses.map(
                    ({ name: status, count, percentage }) => (
                      <div className="status-row" key={status}>
                        <div>
                          <span className={`status-dot ${status.toLowerCase()}`} />
                          {status}
                        </div>

                        <strong>
                          {count} ({percentage.toFixed(1)}%)
                        </strong>
                      </div>
                    ),
                  )}
                </div>
              </section>
  )
}
