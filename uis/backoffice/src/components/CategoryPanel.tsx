import { useMemo } from 'react'
import type { AnalysisResult } from '../types/analysis'

type Props = { analysis: AnalysisResult }

export default function CategoryPanel({ analysis }: Props) {
  const categories = useMemo(() => {
    return Object.entries(analysis.category_counts).map(([name, count]) => ({
      name,
      count,
      percentage: analysis.valid_records
        ? (count / analysis.valid_records) * 100
        : 0,
    }))
  }, [analysis.category_counts, analysis.valid_records])

  return (
              <section className="panel">
                <div className="panel-header">
                  <div>
                    <span className="eyebrow">VALID RECORDS</span>
                    <h2>Incidents by category</h2>
                  </div>
                </div>

                <div className="bar-list">
                  {categories.map(
                    ({ name: category, count, percentage }) => (
                      <div className="bar-row" key={category}>
                        <div className="bar-info">
                          <span>{category.replaceAll('_', ' ')}</span>
                          <strong>
                            {count} ({percentage.toFixed(1)}%)
                          </strong>
                        </div>

                        <div className="bar-track">
                          <div
                            className="bar-fill"
                            style={{
                              width: `${percentage}%`,
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
