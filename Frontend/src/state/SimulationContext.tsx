import { createContext, useContext, useState, useCallback, useRef, type ReactNode } from 'react'
import { authorizeCreator, analyzeContent, runSimulationApi, type CreatorProfile } from '../lib/api'
import { mockCreator, type ContentAnalysis, type SimOutput, type Suggestion } from '../config/site'

export type Modality = 'video' | 'image' | 'text'

export interface SimInputs {
  handle: string
  platform: string
  authorized: boolean
  modality: Modality
  fileName: string
  description: string
  tags: string[]
}

export interface SimResult {
  analysis: ContentAnalysis
  output: SimOutput
  creator: CreatorProfile
  suggestions: Suggestion[]
}

export type PipelineStatus = 'idle' | 'analyzing' | 'simulating' | 'done'

interface SimulationContextValue {
  inputs: SimInputs
  setInputs: (patch: Partial<SimInputs>) => void
  creator: CreatorProfile | null
  result: SimResult | null
  status: PipelineStatus
  connect: (handle: string, platform: string) => Promise<void>
  startPipeline: () => Promise<void>
  reset: () => void
}

const DEFAULT_INPUTS: SimInputs = {
  handle: '',
  platform: 'instagram',
  authorized: false,
  modality: 'video',
  fileName: '',
  description: '',
  tags: [],
}

const SimulationContext = createContext<SimulationContextValue | null>(null)

export function SimulationProvider({ children }: { children: ReactNode }) {
  const [inputs, setInputsState] = useState<SimInputs>(DEFAULT_INPUTS)
  const [creator, setCreator] = useState<CreatorProfile | null>(null)
  const [result, setResult] = useState<SimResult | null>(null)
  const [status, setStatus] = useState<PipelineStatus>('idle')

  const inputsRef = useRef(inputs)
  const creatorRef = useRef<CreatorProfile | null>(null)
  const runningRef = useRef(false)

  const setInputs = useCallback((patch: Partial<SimInputs>) => {
    setInputsState((prev) => {
      const next = { ...prev, ...patch }
      inputsRef.current = next
      return next
    })
  }, [])

  const connect = useCallback(async (handle: string, platform: string) => {
    const profile = await authorizeCreator(handle, platform)
    creatorRef.current = profile
    setCreator(profile)
    setInputsState((prev) => {
      const next = { ...prev, authorized: true }
      inputsRef.current = next
      return next
    })
  }, [])

  const startPipeline = useCallback(async () => {
    if (runningRef.current) return
    runningRef.current = true

    setStatus('analyzing')
    const analysis = await analyzeContent(inputsRef.current)

    setStatus('simulating')
    const usedCreator = creatorRef.current ?? mockCreator
    const { output, suggestions } = await runSimulationApi(analysis, usedCreator)

    setResult({ analysis, output, creator: usedCreator, suggestions })
    setStatus('done')
  }, [])

  const reset = useCallback(() => {
    setInputsState(DEFAULT_INPUTS)
    inputsRef.current = DEFAULT_INPUTS
    creatorRef.current = null
    runningRef.current = false
    setCreator(null)
    setResult(null)
    setStatus('idle')
  }, [])

  return (
    <SimulationContext.Provider
      value={{ inputs, setInputs, creator, result, status, connect, startPipeline, reset }}
    >
      {children}
    </SimulationContext.Provider>
  )
}

// eslint-disable-next-line react-refresh/only-export-components
export function useSimulation() {
  const ctx = useContext(SimulationContext)
  if (!ctx) throw new Error('useSimulation must be used within a SimulationProvider')
  return ctx
}
