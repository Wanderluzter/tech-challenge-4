import { lazy, Suspense, useEffect, useState } from "react";
import { NavLink, Route, Routes } from "react-router-dom";
import { BarChart3, MessageSquareText } from "lucide-react";
import { api, fmt, Meta } from "./api";
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

export default function App() {
  const [meta, setMeta] = useState<Meta | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api.meta().then(setMeta).catch((e: Error) => setError(e.message));
  }, []);

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
            <div className="ml-auto hidden items-center gap-2 text-xs text-[var(--muted)] md:flex">
              <span>{fmt.int(meta.documentos)} avaliações</span>
              <span>·</span>
              <span className="rounded-full border border-black/10 px-2 py-0.5 dark:border-white/10">
                {meta.modelo ?? "modo extrativo"}
              </span>
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
            <Route path="/" element={<AskPage meta={meta} />} />
            <Route path="/dashboard" element={<Suspense fallback={null}><DashboardPage /></Suspense>} />
          </Routes>
        )}
      </main>
    </div>
  );
}
