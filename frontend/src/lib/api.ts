import type { TurnResponse, SchemeResult, SchemeSummary, SchemeDetail, Language } from '@/types';

const BASE = import.meta.env.VITE_API_BASE ?? "http://localhost:8000";

class ApiError extends Error {
  status: number;
  constructor(status: number, message: string) { super(message); this.status = status; }
}

async function req<T>(path: string, init?: RequestInit): Promise<T> {
  const r = await fetch(`${BASE}${path}`, {
    ...init,
    headers: { "content-type": "application/json", ...init?.headers },
  });
  if (!r.ok) throw new ApiError(r.status, await r.text());
  return r.json();
}

export const api = {
  startSession: () =>
    req<{ session_id: string }>("/session", { method: "POST" }),

  turn: (sid: string, utterance: string, language?: string) =>
    req<TurnResponse>(`/session/${sid}/turn`, {
      method: "POST",
      body: JSON.stringify({ utterance, language }),
    }),

  patch: (sid: string, slot: string, value: unknown) =>
    req(`/session/${sid}/patch`, {
      method: "POST",
      body: JSON.stringify({ slot, value }),
    }),

  match: (sid: string) =>
    req<SchemeResult[]>(`/session/${sid}/match`, { method: "POST" }),

  listSchemes: () =>
    req<{ schemes: SchemeSummary[] }>("/schemes"),

  getScheme: (id: string) =>
    req<SchemeDetail>(`/schemes/${id}`),

  ambiguity: () =>
    req<{ markdown: string }>("/ambiguity-map"),

  languages: () =>
    req<{ languages: Language[] }>("/languages"),

  translate: (text: string, target: string, source: string = "auto") =>
    req<{ translated_text: string; target: string }>("/translate", {
      method: "POST",
      body: JSON.stringify({ text, target, source }),
    }),

  translateBatch: (items: Array<{ id: string; text: string }>, target: string) =>
    req<{ items: Array<{ id: string; translated_text: string }>; target: string }>(
      "/translate/batch",
      { method: "POST", body: JSON.stringify({ items, target }) }
    ),

  stt: async (audio: Blob, language: string = "hi-IN"): Promise<{ transcript: string; language: string }> => {
    const fd = new FormData();
    fd.append("file", audio, "audio.webm");
    fd.append("language", language);
    const r = await fetch(`${BASE}/stt`, { method: "POST", body: fd });
    if (!r.ok) throw new ApiError(r.status, await r.text());
    return r.json();
  },

  tts: async (text: string, language: string = "hi-IN"): Promise<Blob> => {
    const r = await fetch(`${BASE}/tts`, {
      method: "POST",
      headers: { "content-type": "application/json" },
      body: JSON.stringify({ text, language }),
    });
    if (!r.ok) throw new ApiError(r.status, await r.text());
    return r.blob();
  },

  resetSession: (sid: string) =>
    req(`/session/${sid}/reset`, { method: "POST" }),
};

export const API_BASE = BASE;
