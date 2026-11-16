import { lazy, Suspense, useCallback, useEffect, useState } from "react";
import { NavLink, Route, Routes } from "react-router-dom";
import { BarChart3, MessageSquareText } from "lucide-react";
import { api, fmt, Meta, ModelStatus } from "./api";
import ModelSelector from "./components/ModelSelector";
import AskPage from "./pages/Ask";

// gráficos (recharts) só carregam ao abrir o dashboard
const DashboardPage = lazy(() => import("./pages/Dashboard"));

function NavItem({ to, icon, label }: { to: string; icon: React.ReactNode; label: string }) {
  return (
    <NavLink
      to={to}
      end
      className={({ isActive }) =>
        `flex items-center gap-2 rounded-lg px-3 py-1.5 text-sm font-medium transition ${
          isActive
            ? "bg-brand-50 text-brand-700 dark:bg-white/10 dark:text-white"
            : "text-[var(--ink-2)] hover:bg-black/5 dark:hover:bg-white/5"
        }`
      }
    >
      {icon}
      <span>{label}</span>
    </NavLink>
  );
}

const MODEL_KEY = "voc.modelo";

function readSavedModel(): string | null {
  try { return localStorage.getItem(MODEL_KEY); } catch { return null; }
}

export default function App() {
  const [meta, setMeta] = useState<Meta | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [models, setModels] = useState<ModelStatus[]>([]);
  const [model, setModelState] = useState<string | null>(readSavedModel);

  useEffect(() => {
    api.meta().then((m) => { setMeta(m); setModels(m.modelos ?? []); }).catch((e: Error) => setError(e.message));
  }, []);

  // modelo salvo que deixou de existir na configuração volta para o padrão
  useEffect(() => {
    if (models.length && model && !models.some((m) => m.modelo === model)) setModelState(null);
  }, [models, model]);

  const setModel = useCallback((next: string) => {
    setModelState(next);
    try { localStorage.setItem(MODEL_KEY, next); } catch { /* armazenamento indisponível */ }
  }, []);

  const refreshModels = useCallback(() => {
    api.models().then(setModels).catch(() => { /* mantém o último estado conhecido */ });
  }, []);

  const selected = model ?? models[0]?.modelo ?? null;

  return (
    <div className="min-h-screen">
      <header className="sticky top-0 z-20 border-b border-black/5 bg-[var(--page)]/80 backdrop-blur dark:border-white/10">
        <div className="mx-auto flex h-14 max-w-7xl items-center gap-4 px-4 sm:px-6">
          <div className="flex items-center gap-2">
            <div className="grid h-7 w-7 place-items-center rounded-lg bg-brand-500 text-white">
              <MessageSquareText size={16} strokeWidth={2.25} />
            </div>
            <span className="font-semibold tracking-tight">Voz do Cliente</span>
            <span className="hidden text-sm text-[var(--muted)] sm:inline">· Olist</span>
          </div>
          <nav className="ml-2 flex items-center gap-1">
            <NavItem to="/" icon={<MessageSquareText size={16} />} label="Perguntar" />
            <NavItem to="/dashboard" icon={<BarChart3 size={16} />} label="Dashboard" />
          </nav>
          {meta && (
            <div className="ml-auto flex items-center gap-3 text-xs text-[var(--muted)]">
              <span className="hidden lg:inline">{fmt.int(meta.documentos)} avaliações</span>
              {models.length > 0 ? (
                <ModelSelector models={models} selected={selected} onSelect={setModel} />
              ) : (
                <span className="rounded-full border border-black/10 px-2 py-0.5 dark:border-white/10">modo extrativo</span>
              )}
            </div>
          )}
        </div>
      </header>

      <main className="mx-auto max-w-7xl px-4 py-6 sm:px-6 sm:py-8">
        {error ? (
          <div className="rounded-xl border border-red-200 bg-red-50 p-4 text-sm text-red-800 dark:border-red-900 dark:bg-red-950/40 dark:text-red-200">
            Não foi possível conectar à API: {error}. Confira se o servidor está rodando
            (<code>uvicorn voc_rag.api:app --port 8000</code>).
          </div>
        ) : (
          <Routes>
            <Route path="/" element={<AskPage meta={meta} models={models} model={selected} setModel={setModel} refreshModels={refreshModels} />} />
            <Route path="/dashboard" element={<Suspense fallback={null}><DashboardPage /></Suspense>} />
          </Routes>
        )}
      </main>
    </div>
  );
}
