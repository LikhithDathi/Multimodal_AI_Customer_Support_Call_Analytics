import api from "./api";
import type {
  SummaryResponse,
  AnalyzeApiResponse,
  HistoryCall,  
} from "../types/analysis";

export const fetchSummary = async (): Promise<SummaryResponse> => {
  const res = await api.get<SummaryResponse>("/calls/summary");
  return res.data;
};

export const analyzeCall = async (file: File): Promise<AnalyzeApiResponse> => {
  const formData = new FormData();
  formData.append("file", file);

  const res = await api.post<AnalyzeApiResponse>(
    "/analyze-call",
    formData,
    {
      headers: { "Content-Type": "multipart/form-data" },
    }
  );

  if (!res.data || typeof res.data.status !== "string") {
    throw new Error("Invalid response from analyze-call API");
  }

  return res.data;
};

export const fetchCalls = async (params?: {
  sentiment?: string;
  urgency?: string;
  outcome?: string;
  start_date?: string;
  end_date?: string;
}): Promise<HistoryCall[]> => {
  const res = await api.get("/calls", { params });
  return res.data;
};

// =======================
// ANALYTICS - SINGLE ML ENDPOINT
// =======================

export interface OperationalRisk {
  risk_score: number;
  level: "Low" | "Medium" | "High";
  top_factor: {
    name: string;
    impact: string;
    coefficient: number;
  };
  total_calls_used: number;
}

export const getOperationalRisk = async (): Promise<OperationalRisk> => {
  const res = await api.get("/analytics/operational-risk");
  return res.data;
};