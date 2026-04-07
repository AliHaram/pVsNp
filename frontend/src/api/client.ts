// frontend/src/api/client.ts

const BASE = '/api';

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const resp = await fetch(`${BASE}${path}`, {
    headers: { 'Content-Type': 'application/json', ...options?.headers },
    ...options,
  });
  if (!resp.ok) {
    throw new Error(`API error: ${resp.status} ${resp.statusText}`);
  }
  if (resp.status === 204) return undefined as T;
  return resp.json();
}

export const api = {
  // Algorithms
  listAlgorithms: () => request<any[]>('/algorithms'),
  uploadAlgorithm: (file: File) => {
    const form = new FormData();
    form.append('file', file);
    return fetch(`${BASE}/algorithms`, { method: 'POST', body: form }).then(r => r.json());
  },
  getAlgorithm: (id: number) => request<any>(`/algorithms/${id}`),
  deleteAlgorithm: (id: number) => request<void>(`/algorithms/${id}`, { method: 'DELETE' }),

  // Instances
  generateInstances: (body: { instance_type: string; n: number; count: number }) =>
    request<any[]>('/instances/generate', { method: 'POST', body: JSON.stringify(body) }),
  listInstances: () => request<any[]>('/instances'),
  getInstance: (id: number) => request<any>(`/instances/${id}`),

  // Benchmarks
  runBenchmark: (body: { algorithm_ids: number[]; instance_ids: number[] }) =>
    request<any>('/benchmarks/run', { method: 'POST', body: JSON.stringify(body) }),
  getBenchmark: (id: number) => request<any>(`/benchmarks/${id}`),
  listBenchmarks: () => request<any[]>('/benchmarks'),

  // Counterexamples
  huntCounterexamples: (body: { algorithm_id: number; strategy: string; count: number; max_n: number }) =>
    request<any[]>('/counterexamples/hunt', { method: 'POST', body: JSON.stringify(body) }),
  listCounterexamples: () => request<any[]>('/counterexamples'),

  // Profiler
  runProfiler: (body: { algorithm_id: number; min_n: number; max_n: number; samples_per_size: number }) =>
    request<any>('/profiler/run', { method: 'POST', body: JSON.stringify(body) }),
  getProfilerRun: (id: number) => request<any>(`/profiler/${id}`),

  // Complexity Finder
  analyzeComplexity: (file: File, inputGenerator: string) => {
    const form = new FormData();
    form.append('file', file);
    form.append('input_generator', inputGenerator);
    return fetch(`${BASE}/complexity/analyze`, { method: 'POST', body: form }).then(r => r.json());
  },
  getComplexityAnalysis: (id: number) => request<any>(`/complexity/${id}`),

  // Status
  getStatus: () => request<any>('/status'),
};

// WebSocket
export function connectWS(onMessage: (data: any) => void): WebSocket {
  const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
  const ws = new WebSocket(`${protocol}//${window.location.host}/api/ws`);
  ws.onmessage = (e) => onMessage(JSON.parse(e.data));
  return ws;
}
