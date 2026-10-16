export type AnalysisResult = {
  total_records: number
  valid_records: number
  invalid_records: number
  error_counts: {
    missing_location: number
    invalid_category: number
    empty_description: number
    missing_reporter: number
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
