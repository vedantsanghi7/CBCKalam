export type Status = "QUALIFIES" | "ALMOST_QUALIFIES" | "DOES_NOT_QUALIFY" | "UNCERTAIN";

export interface RuleEvaluation {
  rule_id: string;
  result: boolean | "UNKNOWN";
  evidence: string;
}

export interface ConfidenceBreakdown {
  base: number;
  completeness: number;
  cleanliness: number;
  freshness: number;
}

export interface SchemeResult {
  scheme_id: string;
  name: string;
  status: Status;
  confidence: number;
  confidence_breakdown: ConfidenceBreakdown;
  rules_evaluated: RuleEvaluation[];
  missing_inputs: string[];
  gap_analysis: string[];
  ambiguity_notes: string[];
  benefit_if_qualified?: {
    amount: number;
    frequency: string;
    mode: string;
    type: string;
  };
  documents_checklist: string[];
  application_url: string;
  application_order: number;
}

export interface TurnResponse {
  reply: string;
  options: string[] | null;
  slots_known: Record<string, any>;
  slots_missing: string[];
  ready_to_match: boolean;
  total_slots_known: number;
  total_slots_possible: number;
  eligible_count?: number;
  qualifies_count?: number;
  almost_count?: number;
}

export interface SchemeSummary {
  id: string;
  name: string;
  ministry: string;
  launched: string;
  benefit: Record<string, any> | null;
  benefit_line: string;
  documents_checklist: string[];
  rules_count: number;
  description?: string;
  short_description?: string;
  category?: string;
  application_url?: string;
}

export interface Language {
  code: string;
  name: string;
  local_name: string;
}

export interface SchemeDetail {
  scheme_id: string;
  name: string;
  ministry: string;
  launched: string;
  category?: string;
  description?: string;
  short_description?: string;
  application_url?: string;
  benefit: Record<string, any>;
  sources: Array<{ url: string; section: string; fetched_on: string }>;
  inputs_required: string[];
  rules: Array<{
    id: string;
    type: string;
    predicate: string;
    description: string;
    source_text: string;
    confidence: string;
    ambiguity_flags: string[];
    ambiguity_notes?: string;
  }>;
  prerequisites: Array<{ scheme: string; soft: boolean }>;
  overlaps_with: Array<{ scheme: string; nature: string }>;
  documents_checklist: string[];
  verification?: Record<string, any>;
}

export interface ChatMessage {
  id: string;
  role: "user" | "assistant";
  text: string;
  timestamp: Date;
  options?: string[] | null;
  /** Language the message was originally generated in. Used to decide if translation is needed. */
  lang?: string;
}
