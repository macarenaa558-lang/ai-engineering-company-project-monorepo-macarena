import type { AnalysisResult } from '../types/analysis'

type Props = { analysis: AnalysisResult }

export default function StatusPanel({ analysis }: Props) {
  const percentage = (value: number) =>
    analysis.valid_records ? (value / analysis.valid_records) * 100 : 0

  return (
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
  )
}
