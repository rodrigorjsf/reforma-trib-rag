import { useState, type ReactNode } from "react";

const sections = [
  { id: "executive", label: "Executive Summary" },
  { id: "persona", label: "User Persona" },
  { id: "features", label: "Core Features" },
  { id: "mvp", label: "MVP Scope" },
  { id: "journey", label: "User Journey" },
  { id: "stack", label: "Tech Stack" },
  { id: "security", label: "Security & Ops" },
  { id: "monetization", label: "Monetization" },
];

type ColorType = "emerald" | "amber" | "sky" | "violet" | "rose" | "slate";

interface BadgeProps {
  children: ReactNode;
  color?: ColorType;
  className?: string; // Add className to props
}

const Badge = ({ children, color = "emerald", className = "" }: BadgeProps) => {
  const colors: Record<ColorType, string> = {
    emerald: "bg-emerald-900/40 text-emerald-300 border-emerald-700/50",
    amber: "bg-amber-900/40 text-amber-300 border-amber-700/50",
    sky: "bg-sky-900/40 text-sky-300 border-sky-700/50",
    violet: "bg-violet-900/40 text-violet-300 border-violet-700/50",
    rose: "bg-rose-900/40 text-rose-300 border-rose-700/50",
    slate: "bg-slate-800/60 text-slate-300 border-slate-600/50",
  };
  return (
    <span className={`inline-block text-xs font-mono px-2 py-0.5 rounded border ${colors[color]} tracking-wide ${className}`}>
      {children}
    </span>
  );
};

// Removed unused SectionDivider component

interface MetricCardProps {
  label: string;
  value: string;
  sub: string;
  color?: "emerald" | "sky" | "violet" | "amber" | "rose";
}

const MetricCard = ({ label, value, sub, color = "emerald" }: MetricCardProps) => {
  const colors: Record<string, string> = {
    emerald: "border-emerald-800/50 bg-emerald-950/30",
    sky: "border-sky-800/50 bg-sky-950/30",
    violet: "border-violet-800/50 bg-violet-950/30",
    amber: "border-amber-800/50 bg-amber-950/30",
    rose: "border-rose-800/50 bg-rose-950/30",
  };
  const textColors: Record<string, string> = {
    emerald: "text-emerald-400",
    sky: "text-sky-400",
    violet: "text-violet-400",
    amber: "text-amber-400",
    rose: "text-rose-400",
  };
  return (
    <div className={`border rounded-lg p-4 ${colors[color]}`}>
      <div className="text-xs text-slate-500 font-mono uppercase tracking-wide mb-1">{label}</div>
      <div className={`text-2xl font-bold ${textColors[color]}`}>{value}</div>
      {sub && <div className="text-xs text-slate-500 mt-1">{sub}</div>}
    </div>
  );
};

interface StackRowProps {
  layer: string;
  tech: string;
  rationale: string;
  cost: string;
}

const StackRow = ({ layer, tech, rationale, cost }: StackRowProps) => (
  <div className="border-b border-slate-800/50 last:border-0 grid grid-cols-12 gap-2 py-3 items-start">
    <div className="col-span-2">
      <span className="text-xs font-mono text-slate-500 uppercase tracking-wide">{layer}</span>
    </div>
    <div className="col-span-3">
      <span className="text-sm font-semibold text-slate-200">{tech}</span>
    </div>
    <div className="col-span-5">
      <span className="text-sm text-slate-400">{rationale}</span>
    </div>
    <div className="col-span-2 text-right">
      <Badge color="emerald">{cost}</Badge>
    </div>
  </div>
);

interface JourneyStepProps {
  step: string;
  title: string;
  actions: string;
  value: string;
  isHighlight?: boolean;
}

const JourneyStep = ({ step, title, actions, value, isHighlight = false }: JourneyStepProps) => (
  <div className={`relative flex gap-4 ${isHighlight ? "" : ""}`}>
    <div className="flex flex-col items-center">
      <div className={`w-8 h-8 rounded-full flex items-center justify-center text-xs font-bold border
        ${isHighlight
          ? "bg-emerald-600 border-emerald-500 text-white shadow-lg shadow-emerald-900/40"
          : "bg-slate-800 border-slate-700 text-slate-400"
        }`}>
        {step}
      </div>
      <div className="w-px flex-1 bg-gradient-to-b from-slate-700 to-transparent min-h-16" />
    </div>
    <div className={`pb-6 flex-1 ${isHighlight ? "border border-emerald-800/40 rounded-lg p-3 -mt-1 bg-emerald-950/20" : ""}`}>
      <div className="flex items-center gap-2 mb-1">
        <span className="text-sm font-semibold text-slate-200">{title}</span>
        {isHighlight && <Badge color="emerald">First Value</Badge>}
      </div>
      <div className="text-xs text-slate-500 mb-2">{actions}</div>
      {value && <div className="text-xs text-slate-400 italic">{value}</div>}
    </div>
  </div>
);

interface ThreatRowProps {
  threat: string;
  mitigation: string;
  priority: "critical" | "high" | "medium";
}

const ThreatRow = ({ threat, mitigation, priority }: ThreatRowProps) => {
  const pColors: Record<string, string> = {
    critical: "text-rose-400",
    high: "text-amber-400",
    medium: "text-sky-400",
  };
  return (
    <div className="border-b border-slate-800/50 last:border-0 py-3">
      <div className="flex items-center gap-2 mb-1">
        <span className={`text-xs font-mono uppercase ${pColors[priority]}`}>{priority}</span>
        <span className="text-sm text-slate-200">{threat}</span>
      </div>
      <div className="text-xs text-slate-500 ml-0">{mitigation}</div>
    </div>
  );
};

interface PriceCardProps {
  tier: string;
  price: string;
  features: string[];
  cta: string;
  highlight?: boolean;
}

const PriceCard = ({ tier, price, features, cta, highlight = false }: PriceCardProps) => (
  <div className={`rounded-xl border p-5 flex flex-col gap-3 relative
    ${highlight ? "border-emerald-700/60 bg-emerald-950/20" : "border-slate-700/40 bg-slate-800/20"}`}>
    {highlight && (
      <div className="absolute -top-3 left-1/2 -translate-x-1/2">
        <Badge color="emerald">Recommended</Badge>
      </div>
    )}
    <div className="text-center">
      <div className="text-xs text-slate-500 font-mono uppercase tracking-widest mb-1">{tier}</div>
      <div className="text-3xl font-bold text-slate-100">{price}</div>
      <div className="text-xs text-slate-600">/month</div>
    </div>
    <div className="border-t border-slate-800 pt-3 flex-1">
      {features.map((f, i) => (
        <div key={i} className="flex items-start gap-2 py-1">
          <span className="text-emerald-500 text-xs mt-0.5">✓</span>
          <span className="text-xs text-slate-400">{f}</span>
        </div>
      ))}
    </div>
    <button className={`w-full text-xs font-mono py-2 rounded border transition-colors
      ${highlight
        ? "bg-emerald-700/30 border-emerald-600/50 text-emerald-300 hover:bg-emerald-700/50"
        : "bg-slate-700/30 border-slate-600/50 text-slate-400 hover:bg-slate-700/50"
      }`}>
      {cta}
    </button>
  </div>
);

export default function PRD() {
  const [activeSection, setActiveSection] = useState("executive");

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100" style={{ fontFamily: "'SF Mono', 'Fira Code', monospace" }}>
      {/* Header */}
      <div className="border-b border-slate-800 bg-slate-950/95 sticky top-0 z-10">
        <div className="max-w-5xl mx-auto px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-7 h-7 rounded bg-emerald-600 flex items-center justify-center">
              <span className="text-xs font-bold text-white">RT</span>
            </div>
            <div>
              <span className="text-sm font-semibold text-slate-200">ReformaTax</span>
              <span className="text-slate-600 text-xs ml-2">PRD v1.0</span>
            </div>
          </div>
          <div className="flex gap-1">
            <Badge color="slate">MVP</Badge>
            <Badge color="emerald">2025</Badge>
          </div>
        </div>
        {/* Nav */}
        <div className="max-w-5xl mx-auto px-6 pb-3 flex gap-1 overflow-x-auto">
          {sections.map((s) => (
            <button
              key={s.id}
              onClick={() => setActiveSection(s.id)}
              className={`text-xs font-mono px-3 py-1 rounded whitespace-nowrap transition-colors
                ${activeSection === s.id
                  ? "bg-emerald-900/40 text-emerald-300 border border-emerald-700/50"
                  : "text-slate-500 hover:text-slate-300 border border-transparent hover:border-slate-700/40"
                }`}
            >
              {s.label}
            </button>
          ))}
        </div>
      </div>

      {/* Content */}
      <div className="max-w-5xl mx-auto px-6 py-8 space-y-10">

        {/* EXECUTIVE SUMMARY */}
        {activeSection === "executive" && (
          <div className="space-y-6">
            <div>
              <h1 className="text-2xl font-bold text-slate-100 mb-1">Product Requirements Document</h1>
              <p className="text-slate-500 text-sm">ReformaTax — AI-powered Q&A platform for Brazilian Tax Reform</p>
            </div>
            <div className="grid grid-cols-4 gap-3">
              <MetricCard label="Target Market" value="~5M" sub="Accountants + SME owners in BR" color="sky" />
              <MetricCard label="MVP Timeline" value="6 wks" sub="From zero to first deploy" color="violet" />
              <MetricCard label="Launch Cost" value="$0" sub="All free tiers" color="emerald" />
              <MetricCard label="Revenue Target" value="$3K" sub="MRR at 6 months" color="amber" />
            </div>
            <div className="border border-slate-800 rounded-lg p-5 bg-slate-900/40">
              <div className="text-xs text-slate-500 font-mono uppercase tracking-widest mb-3">Monorepo Structure</div>
              <p className="text-sm text-slate-300 leading-relaxed">
                Organized as a modular monorepo with clear service boundaries:
              </p>
              <div className="mt-3 font-mono text-xs text-slate-400 space-y-1">
                <div>📁 apps/frontend — Next.js React application</div>
                <div>📁 apps/backend — FastAPI Python services</div>
                <div>📁 packages/types — Shared TypeScript definitions</div>
                <div>📁 packages/shared — Common business logic</div>
                <div>📁 packages/utils — Utility functions and helpers</div>
              </div>
            </div>
            <div className="border border-slate-800 rounded-lg p-5 bg-slate-900/40">
              <div className="text-xs text-slate-500 font-mono uppercase tracking-widest mb-3">Problem Statement</div>
              <p className="text-sm text-slate-300 leading-relaxed">
                The Brazilian Tax Reform (LC 214/2024) fundamentally restructures consumption taxation.
                Accountants and business owners need to understand its impact quickly and accurately,
                but the legal text is dense, cross-referenced, and constantly being supplemented by new
                regulations. There is no reliable, accessible tool that answers specific questions
                grounded exclusively in official sources — without hallucination or ambiguity.
              </p>
            </div>
            <div className="border border-slate-800 rounded-lg p-5 bg-slate-900/40">
              <div className="text-xs text-slate-500 font-mono uppercase tracking-widest mb-3">Core Value Proposition</div>
              <p className="text-sm text-slate-300 leading-relaxed">
                ReformaTax is a <span className="text-emerald-400 font-semibold">citation-grounded Q&A engine</span> that answers
                questions about the tax reform using only official legal sources (Planalto, DOU), always citing
                the specific article that supports each statement. It does not interpret — it locates, explains,
                and references. Users get clarity without legal risk.
              </p>
            </div>
            <div className="border border-slate-800 rounded-lg p-5 bg-slate-900/40">
              <div className="text-xs text-slate-500 font-mono uppercase tracking-widest mb-3">Success Criteria (MVP)</div>
              <div className="grid grid-cols-3 gap-4 mt-2">
                {[
                  { metric: "Citation Rate", target: "100%", desc: "Every response cites source article" },
                  { metric: "Hallucination Rate", target: "< 2%", desc: "Responses unsupported by context" },
                  { metric: "User Satisfaction", target: "> 4/5", desc: "Post-interaction rating" },
                ].map((m, i) => (
                  <div key={i} className="border border-slate-700/40 rounded-lg p-3">
                    <div className="text-xs text-slate-600 mb-1">{m.metric}</div>
                    <div className="text-lg font-bold text-emerald-400">{m.target}</div>
                    <div className="text-xs text-slate-600">{m.desc}</div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* USER PERSONA */}
        {activeSection === "persona" && (
          <div className="space-y-6">
            <div>
              <h2 className="text-xl font-bold text-slate-100 mb-1">User Persona</h2>
              <p className="text-slate-500 text-sm">Primary and secondary user profiles</p>
            </div>
            {/* Primary */}
            <div className="border border-emerald-800/40 rounded-xl overflow-hidden">
              <div className="bg-emerald-950/40 px-5 py-3 flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-full bg-slate-800 border border-slate-700 flex items-center justify-center text-lg">👨‍💼</div>
                  <div>
                    <span className="text-sm font-semibold text-slate-200">Carlos — Contador (CPA)</span>
                    <Badge color="emerald" className="ml-2">Primary</Badge>
                  </div>
                </div>
                <Badge color="sky">Age 34 | São Paulo</Badge>
              </div>
              <div className="p-5 grid grid-cols-3 gap-6">
                <div>
                  <div className="text-xs text-slate-600 font-mono uppercase tracking-wide mb-2">Profile</div>
                  <div className="text-xs text-slate-400 space-y-2">
                    <p>Mid-career accountant at a regional firm. Handles 40+ SME clients. Technically comfortable but not a developer. Uses Excel daily, Google for research.</p>
                  </div>
                </div>
                <div>
                  <div className="text-xs text-slate-600 font-mono uppercase tracking-wide mb-2">Daily Frustrations</div>
                  <div className="text-xs text-slate-400 space-y-2">
                    <p>• Spends 2-3h/week reading conflicting blog posts about the reform</p>
                    <p>• Can't quickly find which specific article applies to a client's situation</p>
                    <p>• Fears giving wrong advice due to misinterpretation</p>
                    <p>• New regulations drop weekly with no centralized view</p>
                  </div>
                </div>
                <div>
                  <div className="text-xs text-slate-600 font-mono uppercase tracking-wide mb-2">Behavior & Needs</div>
                  <div className="text-xs text-slate-400 space-y-2">
                    <p>• Needs answers in under 30 seconds</p>
                    <p>• Wants to see the legal source, not just an opinion</p>
                    <p>• Will pay for reliability — trust is the product</p>
                    <p>• Mobile usage during client meetings</p>
                  </div>
                </div>
              </div>
            </div>
            {/* Secondary */}
            <div className="border border-slate-700/40 rounded-xl overflow-hidden">
              <div className="bg-slate-900/40 px-5 py-3 flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-full bg-slate-800 border border-slate-700 flex items-center justify-center text-lg">👩‍💼</div>
                  <span className="text-sm font-semibold text-slate-200">Ana — Proprietária de MEI</span>
                  <Badge color="slate">Secondary</Badge>
                </div>
                <Badge color="sky">Age 29 | Belo Horizonte</Badge>
              </div>
              <div className="p-5 grid grid-cols-3 gap-6">
                <div>
                  <div className="text-xs text-slate-600 font-mono uppercase tracking-wide mb-2">Profile</div>
                  <div className="text-xs text-slate-400">
                    <p>Small business owner (MEI → ME transition). No accounting background. Relies on her accountant but wants to understand her own situation independently.</p>
                  </div>
                </div>
                <div>
                  <div className="text-xs text-slate-600 font-mono uppercase tracking-wide mb-2">Daily Frustrations</div>
                  <div className="text-xs text-slate-400 space-y-1">
                    <p>• "Will this reform increase my taxes?"</p>
                    <p>• Can't parse legal language</p>
                    <p>• Overwhelmed by news contradictions</p>
                  </div>
                </div>
                <div>
                  <div className="text-xs text-slate-600 font-mono uppercase tracking-wide mb-2">Behavior & Needs</div>
                  <div className="text-xs text-slate-400 space-y-1">
                    <p>• Needs plain Portuguese explanations</p>
                    <p>• Low willingness to pay (freemium target)</p>
                    <p>• High shareability — word of mouth</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* CORE FEATURES */}
        {activeSection === "features" && (
          <div className="space-y-6">
            <div>
              <h2 className="text-xl font-bold text-slate-100 mb-1">Core Features</h2>
              <p className="text-slate-500 text-sm">Three features. Zero extras. Each one solves the primary pain point directly.</p>
            </div>
            {[
              {
                num: "01",
                title: "Citation-Grounded Q&A",
                color: "emerald",
                why: "This is the product. Everything else is secondary.",
                pain: "Carlos spends hours searching for which article applies. He needs an answer in 10 seconds with the source visible.",
                spec: [
                  "User submits a natural language question in Portuguese",
                  "System retrieves relevant chunks from official legal corpus via hybrid search (vector + BM25)",
                  "LLM generates response constrained to retrieved context only",
                  "Every claim in the response includes inline citation: [Art. X, §Y — LC 214/2024]",
                  "If no relevant context found, system responds with explicit 'not found' — never fabricates",
                  "Sources panel shows full text of cited articles for verification",
                ],
                outofsope: "The system does NOT provide personalized tax calculations or legal advice for specific business situations.",
              },
              {
                num: "02",
                title: "Live Source Freshness",
                color: "sky",
                why: "The reform is actively being regulated. Stale data = wrong answers = lost trust.",
                pain: "New Instruções Normativas drop weekly. Carlos needs to know the system reflects the latest official text, not last month's.",
                spec: [
                  "Automated weekly check against official PDF sources (Planalto, DOU)",
                  "Content hash comparison detects updates without re-downloading unchanged docs",
                  "Incremental re-indexing: only new/changed documents are re-processed",
                  "UI badge shows 'Sources updated: [date]' so users know data freshness",
                  "Admin dashboard (internal) shows ingestion status and any parsing errors",
                ],
                outofsope: "Real-time ingestion on publication. Weekly cadence is sufficient for this domain.",
              },
              {
                num: "03",
                title: "Plain-Language Summary Mode",
                color: "violet",
                why: "Secondary persona (Ana) can't parse legal text. This feature unlocks the freemium funnel.",
                pain: "Ana asks 'How does this affect my MEI?' She needs a 3-sentence explanation, not a legal paragraph.",
                spec: [
                  "Toggle on each response: 'Modo Técnico' vs 'Modo Simplificado'",
                  "Simplified mode uses the same retrieved context but prompts the LLM to use plain language",
                  "Citations are preserved in both modes (never sacrifice traceability for readability)",
                  "Disclaimer shown in simplified mode: 'Esta explicação é simplificada. Consulte um profissional para decisões específicas.'",
                ],
                outofsope: "Translation to other languages. Portuguese-only at MVP.",
              },
            ].map((f, i) => (
              <div key={i} className="border border-slate-800 rounded-xl overflow-hidden">
                <div className="px-5 py-3 bg-slate-900/60 flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <span className="text-xs font-mono text-slate-600">{f.num}</span>
                    <h3 className="text-sm font-semibold text-slate-200">{f.title}</h3>
                    <Badge color={f.color as ColorType}>Core</Badge>
                  </div>
                </div>
                <div className="p-5 grid grid-cols-5 gap-5">
                  <div className="col-span-2 space-y-3">
                    <div>
                      <div className="text-xs text-slate-600 font-mono uppercase tracking-wide mb-1">Why This Feature</div>
                      <p className="text-xs text-slate-300 italic">{f.why}</p>
                    </div>
                    <div>
                      <div className="text-xs text-slate-600 font-mono uppercase tracking-wide mb-1">Pain Addressed</div>
                      <p className="text-xs text-slate-400">{f.pain}</p>
                    </div>
                    <div className="border border-slate-700/40 rounded p-2 bg-slate-800/30">
                      <div className="text-xs text-slate-600 font-mono uppercase tracking-wide mb-1">Out of Scope</div>
                      <p className="text-xs text-slate-500">{f.outofsope}</p>
                    </div>
                  </div>
                  <div className="col-span-3">
                    <div className="text-xs text-slate-600 font-mono uppercase tracking-wide mb-2">Specifications</div>
                    <div className="space-y-1.5">
                      {f.spec.map((s, j) => (
                        <div key={j} className="flex items-start gap-2">
                          <span className="text-emerald-600 text-xs mt-0.5">▸</span>
                          <span className="text-xs text-slate-400">{s}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}

        {/* MVP SCOPE */}
        {activeSection === "mvp" && (
          <div className="space-y-6">
            <div>
              <h2 className="text-xl font-bold text-slate-100 mb-1">MVP Functionality</h2>
              <p className="text-slate-500 text-sm">What ships in v1.0. Everything else is post-launch.</p>
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div className="border border-emerald-800/40 rounded-xl p-5 bg-emerald-950/15">
                <div className="flex items-center gap-2 mb-3">
                  <span className="text-emerald-500 text-sm">✓</span>
                  <span className="text-xs font-mono text-emerald-400 uppercase tracking-widest">In Scope — MVP v1.0</span>
                </div>
                {[
                  "Single Q&A interface with streaming responses",
                  "Citation inline + sources panel",
                  "Modo Técnico / Modo Simplificado toggle",
                  "Auth0 login (email + Google OAuth)",
                  "Free tier: 10 questions/day",
                  "Paid tier: unlimited questions",
                  "Disclaimer on every response",
                  "Sources freshness badge",
                  "Responsive design (desktop + mobile)",
                  "Conversation history (last 30 days)",
                ].map((item, i) => (
                  <div key={i} className="flex items-start gap-2 py-1">
                    <span className="text-emerald-600 text-xs mt-0.5">✓</span>
                    <span className="text-xs text-slate-400">{item}</span>
                  </div>
                ))}
              </div>
              <div className="border border-slate-700/40 rounded-xl p-5 bg-slate-900/30">
                <div className="flex items-center gap-2 mb-3">
                  <span className="text-slate-600 text-sm">✕</span>
                  <span className="text-xs font-mono text-slate-500 uppercase tracking-widest">Post-MVP (v2.0+)</span>
                </div>
                {[
                  "Document upload (user's own docs)",
                  "Multi-topic support beyond reforma",
                  "Team/company plans with shared quotas",
                  "PDF export of Q&A sessions",
                  "Email digest of regulatory changes",
                  "Integrations (API for third-party tools)",
                  "Analytics dashboard for enterprise",
                  "Multi-language support",
                  "Custom branding / white-label",
                  "Webhook notifications on source updates",
                ].map((item, i) => (
                  <div key={i} className="flex items-start gap-2 py-1">
                    <span className="text-slate-600 text-xs mt-0.5">○</span>
                    <span className="text-xs text-slate-500">{item}</span>
                  </div>
                ))}
              </div>
            </div>
            {/* Architecture sketch */}
            <div className="border border-slate-800 rounded-xl p-5 bg-slate-900/40">
              <div className="text-xs text-slate-600 font-mono uppercase tracking-widest mb-4">MVP Architecture Overview</div>
              <div className="font-mono text-xs text-slate-400 whitespace-pre leading-relaxed">
{`  User (Browser)
       │
       ▼
  ┌──────────────┐     ┌──────────────────┐
  │  Next.js     │────▶│  FastAPI         │
  │  (Vercel)    │     │  (Railway)       │
  │  - Auth UI   │     │  - /query        │
  │  - Chat UI   │     │  - /sources      │
  │  - Citations │     │  - streaming SSE │
  └──────────────┘     └────────┬─────────┘
                                │
                    ┌───────────┼───────────┐
                    ▼           ▼           ▼
             ┌────────┐  ┌──────────┐  ┌─────────┐
             │ChromaDB│  │  Ollama  │  │  Groq   │
             │(vetores│  │(embedding│  │  API    │
             │ local) │  │  local)  │  │(geração)│
             └────────┘  └──────────┘  └─────────┘`}
              </div>
            </div>
          </div>
        )}

        {/* USER JOURNEY */}
        {activeSection === "journey" && (
          <div className="space-y-6">
            <div>
              <h2 className="text-xl font-bold text-slate-100 mb-1">User Journey</h2>
              <p className="text-slate-500 text-sm">From discovery to first value — optimized for the shortest path to trust.</p>
            </div>
            <div className="border border-slate-800 rounded-xl p-6 bg-slate-900/30">
              <JourneyStep step="1" title="Discovery" actions="User finds ReformaTax via Google (SEO on reform keywords) or LinkedIn/Twitter mention." value="Mental model: 'This might answer my question about CBS alíquotas.'" />
              <JourneyStep step="2" title="Landing Page" actions="Sees headline, one example Q&A with visible citation, trust signals (source badges). CTA: 'Try free'." value="Mental model: 'It shows the actual law text. Seems reliable.'" />
              <JourneyStep step="3" title="Sign Up" actions="Auth0 modal — Google OAuth (one click) or email. No credit card. No long forms." value="" />
              <JourneyStep step="4" title="First Question" actions="Pre-filled suggestion chips: 'Como o CBS afeta MEI?' / 'Quais são as alíquotas do IBS?' User taps one or types own question." value="" />
              <JourneyStep step="5" title="First Value ✓" actions="Response arrives with streaming text + citation panel opens automatically showing the source article. User clicks 'Ver texto completo' and confirms accuracy." value="This is the moment. User sees: answer + source + can verify. Trust is built." isHighlight={true} />
              <JourneyStep step="6" title="Retention Hook" actions="After 3rd question, soft paywall: 'Você usou 3 das 10 perguntas gratuitas hoje. Upgrade para ilimitado.' No block — just awareness." value="" />
            </div>
            <div className="border border-slate-800 rounded-xl p-5 bg-slate-900/40">
              <div className="text-xs text-slate-600 font-mono uppercase tracking-widest mb-3">Onboarding Design Principles</div>
              <div className="grid grid-cols-3 gap-4">
                {[
                  { principle: "Zero friction to first value", detail: "No tutorial, no onboarding wizard. User types a question within 15 seconds of landing." },
                  { principle: "Trust before monetization", detail: "The free tier must deliver genuine value. Paywall only appears after user has experienced quality." },
                  { principle: "Show, don't tell", detail: "Landing page shows a real Q&A example with real citations. No marketing copy about 'AI-powered'." },
                ].map((p, i) => (
                  <div key={i} className="border border-slate-700/40 rounded-lg p-3">
                    <div className="text-xs font-semibold text-slate-300 mb-1">{p.principle}</div>
                    <div className="text-xs text-slate-500">{p.detail}</div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* TECH STACK */}
        {activeSection === "stack" && (
          <div className="space-y-6">
            <div>
              <h2 className="text-xl font-bold text-slate-100 mb-1">Technical Stack</h2>
              <p className="text-slate-500 text-sm">Optimized for fast launch, low cost, and AI-agent-friendly code standards.</p>
            </div>
            <div className="border border-slate-800 rounded-xl overflow-hidden">
              <div className="bg-slate-900/60 px-5 py-3">
                <div className="grid grid-cols-12 gap-2 text-xs text-slate-600 font-mono uppercase tracking-wide">
                  <span className="col-span-2">Layer</span>
                  <span className="col-span-3">Technology</span>
                  <span className="col-span-5">Rationale</span>
                  <span className="col-span-2 text-right">Cost</span>
                </div>
              </div>
              <div className="px-5 py-2">
                <StackRow layer="Frontend" tech="Next.js 14+" rationale="SSR for SEO (critical for organic traffic on legal keywords). App Router + Server Components. TypeScript strict mode." cost="$0 Vercel" />
                <StackRow layer="Auth" tech="Auth0" rationale="Free tier: 25K MAU. MFA built-in. Google OAuth. SDK for Next.js is production-ready." cost="$0 Free" />
                <StackRow layer="Backend" tech="FastAPI" rationale="Async native for SSE streaming. Strong typing (Pydantic). OpenAPI docs auto-generated — AI agents can consume the spec directly." cost="$0 Railway" />
                <StackRow layer="Vector DB" tech="ChromaDB" rationale="Embedded in FastAPI process. Zero infra. Persists to Railway volume. Sufficient for < 500K vectors." cost="$0" />
                <StackRow layer="Embedding" tech="Ollama + nomic-embed" rationale="Runs in Railway container. No API cost per query. nomic-embed: 768 dims, fast, good multilingual." cost="$0" />
                <StackRow layer="LLM" tech="Groq (Mixtral)" rationale="Free tier: 14K TPM on Mixtral-8x7B. Sub-100ms latency. Best PT quality at this price point. Streaming native." cost="$0 Free" />
                <StackRow layer="Cache" tech="Upstash Redis" rationale="Serverless. Free: 10K cmds/day. Caches repeated questions (high hit rate on common reform topics)." cost="$0 Free" />
                <StackRow layer="Parsing" tech="Marker (offline)" rationale="Runs locally during ingestion. Best open-source PDF→Markdown for tables. No API dependency." cost="$0" />
                <StackRow layer="Monitoring" tech="Railway Logs + Sentry" rationale="Sentry free tier: 5K events/mo. Enough to catch hallucination spikes and errors in production." cost="$0 Free" />
              </div>
            </div>
            {/* AI Agent Friendliness */}
            <div className="border border-violet-800/40 rounded-xl p-5 bg-violet-950/15">
              <div className="flex items-center gap-2 mb-3">
                <Badge color="violet">AI-Agent Compatibility</Badge>
              </div>
              <div className="grid grid-cols-3 gap-4">
                {[
                  { title: "OpenAPI-First Backend", detail: "FastAPI auto-generates OpenAPI spec. Any AI agent (Claude, GPT, etc.) can discover and call endpoints without manual documentation." },
                  { title: "Strict TypeScript + Pydantic", detail: "All contracts are typed. Pydantic models serve as source of truth for both validation and documentation. Zero ambiguity for code generation." },
                  { title: "Modular Service Boundaries", detail: "Each service (parser, chunker, indexer, query engine) is isolated with clear interfaces. AI agents can modify one without breaking others." },
                ].map((item, i) => (
                  <div key={i} className="border border-slate-700/40 rounded-lg p-3">
                    <div className="text-xs font-semibold text-violet-300 mb-1">{item.title}</div>
                    <div className="text-xs text-slate-500">{item.detail}</div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* SECURITY & OPS */}
        {activeSection === "security" && (
          <div className="space-y-6">
            <div>
              <h2 className="text-xl font-bold text-slate-100 mb-1">Security & Operational Reliability</h2>
              <p className="text-slate-500 text-sm">Threat model, cost controls, and rate limiting for a solo-operated SaaS.</p>
            </div>
            {/* Threat Model */}
            <div className="border border-slate-800 rounded-xl overflow-hidden">
              <div className="bg-slate-900/60 px-5 py-3">
                <span className="text-xs font-mono text-slate-500 uppercase tracking-widest">Security Threat Model</span>
              </div>
              <div className="px-5 py-3">
                <ThreatRow threat="LLM Prompt Injection" mitigation="All user input is sanitized before passing to LLM. System prompt and user prompt are separated. Context is injected server-side only — user never controls what enters the prompt." priority="critical" />
                <ThreatRow threat="API Key Exposure" mitigation="All API keys (Groq, Auth0) stored as environment variables on Railway. Never exposed to frontend. Frontend only calls your own FastAPI endpoints." priority="critical" />
                <ThreatRow threat="Rate Limit Abuse / DDoS" mitigation="Rate limiting at two layers: (1) Auth0 brute-force protection on login, (2) FastAPI middleware rate limit per user_id: 10 req/min free, 30 req/min paid. Redis-backed counters." priority="high" />
                <ThreatRow threat="Data Scraping / Bulk Export" mitigation="Responses are generated per-question. No bulk export endpoint exists. Conversation history limited to 30 days and paginated." priority="high" />
                <ThreatRow threat="Unauthorized Access to Legal Corpus" mitigation="Legal corpus is internal-only (ChromaDB on Railway). Not exposed via any API. Users only see LLM-generated responses + cited article excerpts." priority="medium" />
                <ThreatRow threat="Hallucination in Production" mitigation="Bounded prompt (system prompt enforces citation). Post-generation check: if response contains no citation markers, it is flagged and returned as 'insufficient information.' Sentry alerts on flagged responses." priority="critical" />
              </div>
            </div>
            {/* Cost Controls */}
            <div className="border border-amber-800/40 rounded-xl overflow-hidden">
              <div className="bg-amber-950/30 px-5 py-3">
                <span className="text-xs font-mono text-amber-400 uppercase tracking-widest">Cost Management Strategy</span>
              </div>
              <div className="p-5 grid grid-cols-3 gap-4">
                {[
                  { title: "Cache-First Query", detail: "Redis caches responses by question hash. Common questions (MEI, alíquotas, CBS vs IBS) have very high cache hit rate. Reduces Groq API calls by est. 60-70% at scale." },
                  { title: "Free Tier Quotas", detail: "10 questions/day for free users. Enforced via Redis counter per user_id per day (UTC). Prevents free-tier abuse. Quota resets at midnight UTC." },
                  { title: "LLM Token Budget", detail: "max_tokens capped at 800 per response. Sufficient for cited answers. Prevents runaway generation costs. Monitor avg tokens/response via logs." },
                  { title: "Embedding Locally", detail: "Zero cost per embedding. All embedding happens on Railway container via Ollama. No per-query API cost regardless of volume." },
                  { title: "Alert on Cost Spike", detail: "Railway spend alerts at $10 and $25 thresholds. Groq usage dashboard monitored weekly. Any anomaly triggers immediate investigation." },
                  { title: "Graceful Degradation", detail: "If Groq API is down or rate-limited, return cached response if available. If no cache, return 'Service temporarily unavailable' — never silently fail." },
                ].map((item, i) => (
                  <div key={i} className="border border-slate-700/40 rounded-lg p-3">
                    <div className="text-xs font-semibold text-amber-300 mb-1">{item.title}</div>
                    <div className="text-xs text-slate-500">{item.detail}</div>
                  </div>
                ))}
              </div>
            </div>
            {/* Rate Limit Spec */}
            <div className="border border-slate-800 rounded-xl p-5 bg-slate-900/40">
              <div className="text-xs text-slate-600 font-mono uppercase tracking-widest mb-3">Rate Limit & Quota Matrix</div>
              <div className="overflow-x-auto">
                <table className="w-full text-xs">
                  <thead>
                    <tr className="border-b border-slate-800">
                      <th className="text-left text-slate-600 py-2 font-mono">Resource</th>
                      <th className="text-left text-slate-600 py-2 font-mono">Free Tier</th>
                      <th className="text-left text-slate-600 py-2 font-mono">Paid Tier</th>
                      <th className="text-left text-slate-600 py-2 font-mono">Enforcement</th>
                    </tr>
                  </thead>
                  <tbody>
                    {[
                      ["Questions / day", "10", "Unlimited", "Redis counter, resets UTC midnight"],
                      ["Requests / minute", "5", "30", "Redis sliding window per user_id"],
                      ["Response max tokens", "800", "800", "LLM param, same for all tiers"],
                      ["Conversation history", "7 days", "30 days", "DB TTL + scheduled cleanup"],
                      ["Concurrent sessions", "1", "3", "Auth0 session management"],
                    ].map((row, i) => (
                      <tr key={i} className="border-b border-slate-800/50">
                        <td className="py-2 text-slate-300">{row[0]}</td>
                        <td className="py-2 text-slate-500">{row[1]}</td>
                        <td className="py-2 text-emerald-400">{row[2]}</td>
                        <td className="py-2 text-slate-600">{row[3]}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        )}

        {/* MONETIZATION */}
        {activeSection === "monetization" && (
          <div className="space-y-6">
            <div>
              <h2 className="text-xl font-bold text-slate-100 mb-1">Monetization Strategy</h2>
              <p className="text-slate-500 text-sm">Realistic pricing for a niche B2B SaaS in the Brazilian legal-tech market.</p>
            </div>
            {/* Pricing */}
            <div className="grid grid-cols-3 gap-4">
              <PriceCard
                tier="Free"
                price="R$ 0"
                features={[
                  "10 questions per day",
                  "Citation-grounded responses",
                  "Modo Simplificado + Técnico",
                  "7-day conversation history",
                  "Community support (Discord)",
                ]}
                cta="Get Started"
              />
              <PriceCard
                tier="Pro"
                price="R$ 49"
                highlight={true}
                features={[
                  "Unlimited questions",
                  "30-day conversation history",
                  "Priority response (lower latency)",
                  "Email support",
                  "Early access to new features",
                  "PDF export of Q&A sessions",
                ]}
                cta="Start Free Trial (7 days)"
              />
              <PriceCard
                tier="Team"
                price="R$ 199"
                features={[
                  "Everything in Pro",
                  "Up to 5 team members",
                  "Shared conversation workspace",
                  "Monthly usage report",
                  "Dedicated Slack support",
                  "Custom onboarding session",
                ]}
                cta="Contact Sales"
              />
            </div>
            {/* Unit Economics */}
            <div className="border border-slate-800 rounded-xl p-5 bg-slate-900/40">
              <div className="text-xs text-slate-600 font-mono uppercase tracking-widest mb-4">Unit Economics — Per Paying User</div>
              <div className="grid grid-cols-4 gap-4">
                <MetricCard label="COGS (Pro)" value="~$2" sub="Groq API + infra share" color="rose" />
                <MetricCard label="Gross Margin" value="~96%" sub="At R$ 49/mo ($9 USD)" color="emerald" />
                <MetricCard label="CAC Target" value="< $15" sub="Organic SEO + content" color="sky" />
                <MetricCard label="Payback Period" value="< 2 mo" sub="At target CAC" color="violet" />
              </div>
            </div>
            {/* Revenue Projections */}
            <div className="border border-slate-800 rounded-xl p-5 bg-slate-900/40">
              <div className="text-xs text-slate-600 font-mono uppercase tracking-widest mb-4">Revenue Projection — Conservative Scenario</div>
              <div className="overflow-x-auto">
                <table className="w-full text-xs">
                  <thead>
                    <tr className="border-b border-slate-800">
                      {["Month", "Free Users", "Pro Subs", "Team Subs", "MRR (R$)", "Est. Infra Cost"].map(h => (
                        <th key={h} className="text-left text-slate-600 py-2 font-mono">{h}</th>
                      ))}
                    </tr>
                  </thead>
                  <tbody>
                    {[
                      ["1-2", "200", "5", "0", "245", "~$5"],
                      ["3-4", "500", "20", "2", "1,378", "~$10"],
                      ["5-6", "1,200", "50", "5", "3,445", "~$20"],
                      ["7-9", "3,000", "100", "12", "7,288", "~$40"],
                      ["10-12", "5,000", "180", "25", "13,870", "~$70"],
                    ].map((row, i) => (
                      <tr key={i} className="border-b border-slate-800/50">
                        {row.map((cell, j) => (
                          <td key={j} className={`py-2 ${j === 3 ? "text-emerald-400 font-semibold" : "text-slate-400"}`}>{cell}</td>
                        ))}
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
              <div className="mt-4 text-xs text-slate-600">
                Assumptions: 2% free→paid conversion (industry avg for niche B2B tools). Growth driven primarily by SEO on long-tail reform keywords. Team tier requires manual outreach to accounting firms starting month 4.
              </div>
            </div>
            {/* Acquisition Strategy */}
            <div className="border border-slate-800 rounded-xl p-5 bg-slate-900/40">
              <div className="text-xs text-slate-600 font-mono uppercase tracking-widest mb-3">Acquisition Strategy (Zero Ad Spend)</div>
              <div className="grid grid-cols-3 gap-4">
                {[
                  { channel: "SEO Content", priority: "P0", detail: "Blog posts answering specific reform questions. Target long-tail keywords: 'reforma tributária MEI', 'CBS alíquota serviços'. Next.js SSR makes this viable from day 1." },
                  { channel: "LinkedIn Organic", priority: "P0", detail: "Weekly posts about new regulations with the tool's answer as the content. Targets accountants and business owners directly." },
                  { channel: "Accountant Communities", priority: "P1", detail: "Slack/WhatsApp groups for CPAs. Offer free access in exchange for feedback. Word-of-mouth in professional networks is the highest-converting channel in BR." },
                ].map((item, i) => (
                  <div key={i} className="border border-slate-700/40 rounded-lg p-3">
                    <div className="flex items-center gap-2 mb-1">
                      <span className="text-xs font-semibold text-slate-300">{item.channel}</span>
                      <Badge color={item.priority === "P0" ? "emerald" : "sky"}>{item.priority as ColorType}</Badge>
                    </div>
                    <div className="text-xs text-slate-500">{item.detail}</div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* Footer */}
        <div className="border-t border-slate-800 pt-6 flex items-center justify-between">
          <div className="text-xs text-slate-600 font-mono">
            PRD v1.0 — ReformaTax MVP — Jan 2025
          </div>
          <div className="flex gap-2">
            <Badge color="slate">Confidential</Badge>
            <Badge color="emerald">Ready for Development</Badge>
          </div>
        </div>
      </div>
    </div>
  );
}