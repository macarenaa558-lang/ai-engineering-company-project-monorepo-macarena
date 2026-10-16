import type { AnalysisResult } from '../types/analysis'

type Props = { analysis: AnalysisResult }

export default function CategoryPanel({ analysis }: Props) {
  const percentage = (value: number) =>
    analysis.valid_records ? (value / analysis.valid_records) * 100 : 0

  return (
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
  )
}
