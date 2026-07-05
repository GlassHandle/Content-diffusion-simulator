import {
  mockContentAnalysis,
  mockCreator,
  mockSimOutput,
  mockSuggestions,
  type ContentAnalysis,
  type SimOutput,
  type Suggestion,
} from '../config/site'
import type { SimInputs } from '../state/SimulationContext'

export type CreatorProfile = typeof mockCreator

const API_BASE: string | undefined = import.meta.env.VITE_API_BASE

// fallback if API not connected
async function withFallback<T>(label: string, real: () => Promise<T>, fallback: () => T,minMs = 900,): Promise<T> {
  const started = performance.now()
  try {
    if (!API_BASE) throw new Error('VITE_API_BASE not set')
    return await real()
  } catch (err) {
    console.warn(`[api] ${label}: falling back to mock —`, err)
    const elapsed = performance.now() - started
    if (elapsed < minMs) await new Promise((r) => setTimeout(r, minMs - elapsed))
    return fallback()
  }
}


export async function authorizeCreator(handle: string, platform: string): Promise<CreatorProfile> {
  return withFallback(
    'authorizeCreator',
    async () => {
      // to point this at L2 route and map the
      // response. Example against the FastAPI creator analyzer:
      const res = await fetch(
        `${API_BASE}/creator/analyze?username=${encodeURIComponent(handle)}&platform=${encodeURIComponent(platform)}`,
        { method: 'POST' },
      )
      if (!res.ok) throw new Error(`HTTP ${res.status}`)
      const data = await res.json()
      // map the *-creator.json "scores" block -> CreatorProfile
      return {
        handle,
        platform,
        trust: data.scores.creator_trust_score,
        momentum: data.scores.creator_momentum_score,
        niche_authority: data.scores.niche_authority_score,
        audience_quality: data.scores.audience_quality_score,
        volatility: data.scores.creator_volatility_score,
      }
    },
    () => ({ ...mockCreator, handle: handle || mockCreator.handle, platform }),
    700,
  )
}

export async function analyzeContent(inputs: SimInputs): Promise<ContentAnalysis> {
  return withFallback(
    'analyzeContent',
    async () => {
      // the real route is POST /context/analyze/{text|image|video}?username=...
      // For media you must upload the actual File — today the form only keeps
      // `fileName`; stash the File object in SimulationContext when you wire this.
      const username = encodeURIComponent(inputs.handle.replace(/^@/, ''))
      let res: Response
      if (inputs.modality === 'text') {
        res = await fetch(`${API_BASE}/context/analyze/text?username=${username}`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ text: inputs.description }),
        })
      } else {
        const form = new FormData()
        // form.append('file', theActualFileObject) 
        form.append('description', inputs.description)
        res = await fetch(`${API_BASE}/context/analyze/${inputs.modality}?username=${username}`, {
          method: 'POST',
          body: form,
        })
      }
      if (!res.ok) throw new Error(`HTTP ${res.status}`)
      const data = await res.json()
      // map the analyze response -> ContentAnalysis (dims/composites/topics/entities)
      return {
        modality: inputs.modality,
        dims: Object.fromEntries(
          Object.entries(data.engagement.scores as Record<string, { score: number }>).map(
            ([k, v]) => [k, v.score],
          ),
        ),
        composites: data.engagement.composite,
        topics: data.topics,
        entities: data.entities,
      }
    },
    () => ({ ...mockContentAnalysis, modality: inputs.modality }),
    2500, // this lets the scan animation breathe on the mock path
  )
}


export async function runSimulationApi(
  analysis: ContentAnalysis,
  creator: CreatorProfile,
): Promise<{ output: SimOutput; suggestions: Suggestion[] }> {
  return withFallback(
    'runSimulationApi',
    async () => {
      // wire this with the simulator API route, e.g.:
      const res = await fetch(`${API_BASE}/simulate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ analysis, creator }),
      })
      if (!res.ok) throw new Error(`HTTP ${res.status}`)
      const data = await res.json()
      // expected simulator stdout shape: expected_reach, reach_p10/50/90,
      // viral_probability, confidence, mean_wave[] (+ suggestions from L5)
      return { output: data.output as SimOutput, suggestions: data.suggestions as Suggestion[] }
    },
    () => ({ output: mockSimOutput, suggestions: mockSuggestions }),
    3000, // this lets the wave animation breathe on the mock path
  )
}
