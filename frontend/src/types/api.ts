export type OutputType = "email" | "linkedin" | "letter";

export interface GenerateRequest {
  job_offer: string;
  output_type: OutputType;
}

export interface SourceDocument {
  id: string;
  text: string;
  score: number;
  source: string;
}

export interface GenerateResponse {
  output: string;
  output_type: OutputType;
  sources: SourceDocument[];
  trace_id: string | null;
}
