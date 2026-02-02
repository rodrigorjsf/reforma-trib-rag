import SystemPrompts from './SystemPrompts'
import PRDReformaTributariaSaaS from './PRDReformaTributariaSaaS'
import { useState } from 'react'

function App() {
  const [view, setView] = useState<'system-prompts' | 'prd'>('system-prompts')

  return (
    <div className="relative">
      <div className="fixed top-4 right-4 z-50 flex gap-2">
         <button
          onClick={() => setView('prd')}
          className={`px-3 py-1 text-xs rounded border ${view === 'prd' ? 'bg-emerald-600 text-white border-emerald-500' : 'bg-slate-800 text-slate-300 border-slate-700'}`}
        >
          PRD
        </button>
        <button
          onClick={() => setView('system-prompts')}
          className={`px-3 py-1 text-xs rounded border ${view === 'system-prompts' ? 'bg-emerald-600 text-white border-emerald-500' : 'bg-slate-800 text-slate-300 border-slate-700'}`}
        >
          System Prompts
        </button>
      </div>

      {view === 'system-prompts' ? <SystemPrompts /> : <PRDReformaTributariaSaaS />}
    </div>
  )
}

export default App
