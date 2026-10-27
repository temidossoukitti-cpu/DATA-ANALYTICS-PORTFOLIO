import { useMemo, useState } from "react";
import {
  ArrowDownRight,
  ArrowUpRight,
  BarChart3,
  ChevronRight,
  CircleHelp,
  FilterX,
  LayoutDashboard,
  RotateCcw,
  Search,
  Table2,
  WalletCards,
} from "lucide-react";
import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  Legend,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { dashboardData, type SummaryRow } from "@/data/dashboardData";

type View = "overview" | "departments" | "categories";

const TURQUOISE = "#53b7b5";
const ORANGE = "#f59a2f";
const PALE_BLUE = "#dff1f4";
const SLATE = "#263238";

const money = (value: number) => {
  const absolute = Math.abs(value);
  const sign = value < 0 ? "−" : "";
  if (absolute >= 1_000_000_000) return `${sign}$${(absolute / 1_000_000_000).toFixed(1)}B`;
  if (absolute >= 1_000_000) return `${sign}$${(absolute / 1_000_000).toFixed(1)}M`;
  if (absolute >= 1_000) return `${sign}$${(absolute / 1_000).toFixed(1)}K`;
  return `${sign}$${absolute.toFixed(0)}`;
};

const pct = (value: number | null) => (value === null ? "—" : `${value.toFixed(0)}%`);

function MetricCard({ label, value, detail, tone = "turquoise" }: { label: string; value: string; detail: string; tone?: "turquoise" | "orange" | "neutral" }) {
  return (
    <div className={`metric-card metric-${tone}`}>
      <span className="metric-label">{label}</span>
      <strong>{value}</strong>
      <span className="metric-detail">{detail}</span>
    </div>
  );
}

function InsightButton({ children, onClick, active = false, icon }: { children: React.ReactNode; onClick: () => void; active?: boolean; icon?: React.ReactNode }) {
  return (
    <button className={`insight-button ${active ? "active" : ""}`} onClick={onClick} type="button">
      {icon}
      <span>{children}</span>
      <ChevronRight size={15} />
    </button>
  );
}

function SummaryTable({ rows, kind, onSelect }: { rows: ReadonlyArray<SummaryRow>; kind: "department" | "category"; onSelect: (row: SummaryRow) => void }) {
  return (
    <div className="summary-table-wrap">
      <table className="summary-table">
        <thead>
          <tr>
            <th>{kind === "department" ? "Département" : "Catégorie de dépense"}</th>
            <th>Budget</th>
            <th>Réalisé</th>
            <th>Écart</th>
            <th>Utilisation</th>
          </tr>
        </thead>
        <tbody>
          {rows.slice(0, 8).map((row) => (
            <tr key={row.name} onClick={() => onSelect(row)} className="clickable-row">
              <td title={row.name}>{row.name}</td>
              <td>{money(row.budget)}</td>
              <td>{money(row.actual)}</td>
              <td className={row.variance > 0 ? "bad" : "good"}>{row.variance > 0 ? "+" : ""}{money(row.variance)}</td>
              <td><span className={`status-pill ${row.utilization !== null && row.utilization > 100 ? "status-bad" : "status-good"}`}>{pct(row.utilization)}</span></td>
            </tr>
          ))}
        </tbody>
      </table>
      <p className="table-hint"><Search size={14} /> Clique sur une ligne pour la sélectionner et filtrer la vue.</p>
    </div>
  );
}

export default function Home() {
  const [view, setView] = useState<View>("overview");
  const [year, setYear] = useState("2026");
  const [department, setDepartment] = useState("Toutes");
  const [category, setCategory] = useState("Toutes");
  const [selected, setSelected] = useState<SummaryRow | null>(null);

  const selectedDepartment = useMemo(() => dashboardData.departments.find((item) => item.name === department), [department]);
  const selectedCategory = useMemo(() => dashboardData.categories.find((item) => item.name === category), [category]);
  const current = selectedDepartment ?? selectedCategory;
  const utilization = dashboardData.totals.actual / dashboardData.totals.budget * 100;
  const favorable = dashboardData.totals.variance <= 0;

  const chartRows = useMemo(() => {
    if (department !== "Toutes") return dashboardData.departments.filter((item) => item.name === department);
    return dashboardData.departments.slice(0, 10);
  }, [department]);

  const resetFilters = () => {
    setYear("2026");
    setDepartment("Toutes");
    setCategory("Toutes");
    setSelected(null);
    setView("overview");
  };

  const chooseRow = (row: SummaryRow) => {
    setSelected(row);
    if (view === "departments") setDepartment(row.name);
    if (view === "categories") setCategory(row.name);
  };

  return (
    <main className="dashboard-shell">
      <header className="topbar">
        <div className="brand-block">
          <div className="brand-mark"><BarChart3 size={20} /></div>
          <div><div className="eyebrow">CIVIC SIGNAL</div><h1>Budget vs Réalisé</h1></div>
        </div>
        <div className="topbar-meta"><span>Ville d’Austin · FY2026 Q3</span><span className="live-dot">Données officielles</span></div>
      </header>

      <section className="intro-row">
        <div>
          <p className="eyebrow">TABLEAU DE BORD FINANCIER</p>
          <h2>Où les dépenses s’écartent-elles du budget ?</h2>
          <p className="intro-copy">Utilise les boutons et les filtres pour interroger les résultats. Les montants sont agrégés à partir de 57 267 lignes du budget opérationnel Austin.</p>
        </div>
        <div className="view-switcher" role="tablist" aria-label="Vues du dashboard">
          <button className={view === "overview" ? "view-tab active" : "view-tab"} onClick={() => setView("overview")}><LayoutDashboard size={16} /> Vue générale</button>
          <button className={view === "departments" ? "view-tab active" : "view-tab"} onClick={() => setView("departments")}><WalletCards size={16} /> Départements</button>
          <button className={view === "categories" ? "view-tab active" : "view-tab"} onClick={() => setView("categories")}><Table2 size={16} /> Catégories</button>
        </div>
      </section>

      <section className="filter-panel" aria-label="Filtres du dashboard">
        <div className="filter-title"><span className="filter-icon"><Search size={16} /></span><div><strong>Interroger les données</strong><small>Les boutons mettent à jour les vues</small></div></div>
        <label>Année fiscale<select value={year} onChange={(event) => setYear(event.target.value)}><option value="2026">FY2026</option></select></label>
        <label>Département<select value={department} onChange={(event) => { setDepartment(event.target.value); setSelected(null); }}>{["Toutes", ...dashboardData.departments.map((row) => row.name)].map((item) => <option key={item} value={item}>{item}</option>)}</select></label>
        <label>Catégorie<select value={category} onChange={(event) => { setCategory(event.target.value); setSelected(null); }}>{["Toutes", ...dashboardData.categories.map((row) => row.name)].map((item) => <option key={item} value={item}>{item}</option>)}</select></label>
        <button className="reset-button" onClick={resetFilters} type="button"><RotateCcw size={15} /> Réinitialiser</button>
      </section>

      <section className="kpi-grid">
        <MetricCard label="Budget total" value={money(dashboardData.totals.budget)} detail="Montant prévu" tone="turquoise" />
        <MetricCard label="Dépenses réelles" value={money(dashboardData.totals.actual)} detail="Montant consommé" tone="orange" />
        <MetricCard label="Écart favorable" value={money(Math.abs(dashboardData.totals.variance))} detail="Budget restant global" tone="turquoise" />
        <MetricCard label="Consommation" value={`${utilization.toFixed(1)}%`} detail={favorable ? "Sous le budget global" : "Au-dessus du budget"} tone={favorable ? "neutral" : "orange"} />
      </section>

      {current && <div className="selection-banner"><span><strong>Sélection :</strong> {current.name}</span><span>Budget {money(current.budget)} · Réalisé {money(current.actual)} · Écart <b className={current.variance > 0 ? "bad" : "good"}>{current.variance > 0 ? "+" : ""}{money(current.variance)}</b></span><button onClick={() => { setSelected(null); setDepartment("Toutes"); setCategory("Toutes"); }} type="button">Effacer la sélection</button></div>}

      {view === "overview" && (
        <>
          <section className="content-grid">
            <div className="panel chart-panel">
              <div className="panel-heading"><div><p className="eyebrow">COMPARAISON</p><h3>Budget et dépenses par département</h3></div><span className="legend-chip"><i className="legend-square turquoise" /> Budget <i className="legend-square orange" /> Réalisé</span></div>
              <div className="bar-chart" role="img" aria-label="Comparaison du budget et des dépenses par département">
                <div className="bar-axis"><span>$2B</span><span>$1.5B</span><span>$1B</span><span>$500M</span><span>$0</span></div>
                <div className="bar-plot">{chartRows.map((row) => { const max = Math.max(...chartRows.map((item) => item.budget)); return <button className="bar-column" key={row.name} onClick={() => chooseRow(row)} type="button" title={`${row.name} · Budget ${money(row.budget)} · Réalisé ${money(row.actual)}`}><div className="bar-pair"><span className="bar budget-bar" style={{ height: `${Math.max(4, row.budget / max * 100)}%` }} /><span className="bar actual-bar" style={{ height: `${Math.max(4, row.actual / max * 100)}%` }} /></div><span className="bar-label">{row.name}</span></button>; })}</div>
              </div>
            </div>
            <div className="panel side-panel"><div className="panel-heading"><div><p className="eyebrow">QUESTIONS RAPIDES</p><h3>Que veux-tu examiner ?</h3></div><CircleHelp size={20} color="#53b7b5" /></div><div className="insight-list"><InsightButton onClick={() => setView("departments")} icon={<ArrowUpRight size={16} />}>Départements au-dessus du budget</InsightButton><InsightButton onClick={() => setView("categories")} icon={<Table2 size={16} />}>Catégories qui expliquent l’écart</InsightButton><InsightButton onClick={() => { setDepartment("Toutes"); setCategory("Toutes"); setSelected(null); setView("overview"); }} icon={<FilterX size={16} />}>Revenir à la vue globale</InsightButton></div><div className="callout"><strong>Lecture simple</strong><span>Un écart positif signifie que le réalisé dépasse le budget. Un écart négatif signifie qu’il reste du budget.</span></div></div>
          </section>
          <section className="content-grid lower-grid"><div className="panel"><div className="panel-heading"><div><p className="eyebrow">DÉPARTEMENTS</p><h3>Principaux postes de dépenses</h3></div><button className="text-button" onClick={() => setView("departments")} type="button">Tout voir <ChevronRight size={15} /></button></div><SummaryTable rows={dashboardData.departments} kind="department" onSelect={(row) => { setView("departments"); chooseRow(row); }} /></div><div className="panel"><div className="panel-heading"><div><p className="eyebrow">CATÉGORIES</p><h3>Principaux écarts</h3></div><button className="text-button" onClick={() => setView("categories")} type="button">Tout voir <ChevronRight size={15} /></button></div><SummaryTable rows={dashboardData.categories} kind="category" onSelect={(row) => { setView("categories"); chooseRow(row); }} /></div></section>
        </>
      )}

      {view === "departments" && (
        <section className="detail-layout"><div className="panel wide-panel"><div className="panel-heading"><div><p className="eyebrow">ANALYSE PAR DÉPARTEMENT</p><h3>Classement des départements</h3><span className="panel-subtitle">Clique sur un département pour le garder à l’écran.</span></div><button className="reset-button" onClick={() => setDepartment("Toutes")} type="button"><RotateCcw size={15} /> Tout afficher</button></div><SummaryTable rows={department === "Toutes" ? dashboardData.departments : dashboardData.departments.filter((row) => row.name === department)} kind="department" onSelect={chooseRow} /></div><div className="panel detail-card"><p className="eyebrow">POINT DE CONTRÔLE</p><h3>{selectedDepartment?.name ?? "Sélectionne un département"}</h3>{selectedDepartment ? <><div className="big-number">{money(selectedDepartment.actual)}</div><p>Dépenses réelles</p><div className="mini-stat"><span>Budget</span><strong>{money(selectedDepartment.budget)}</strong></div><div className="mini-stat"><span>Écart</span><strong className={selectedDepartment.variance > 0 ? "bad" : "good"}>{selectedDepartment.variance > 0 ? "+" : ""}{money(selectedDepartment.variance)}</strong></div><button className="primary-button" onClick={() => setView("categories")} type="button">Voir les catégories <ChevronRight size={16} /></button></> : <p className="empty-copy">Utilise le tableau ou le filtre Département pour commencer l’analyse.</p>}</div></section>
      )}

      {view === "categories" && (
        <section className="detail-layout"><div className="panel wide-panel"><div className="panel-heading"><div><p className="eyebrow">ANALYSE PAR CATÉGORIE</p><h3>Catégories de dépenses</h3><span className="panel-subtitle">Les lignes orange signalent une dépense supérieure au budget.</span></div><button className="reset-button" onClick={() => setCategory("Toutes")} type="button"><RotateCcw size={15} /> Tout afficher</button></div><SummaryTable rows={category === "Toutes" ? dashboardData.categories : dashboardData.categories.filter((row) => row.name === category)} kind="category" onSelect={chooseRow} /></div><div className="panel detail-card"><p className="eyebrow">POINT DE CONTRÔLE</p><h3>{selectedCategory?.name ?? "Sélectionne une catégorie"}</h3>{selectedCategory ? <><div className="big-number">{pct(selectedCategory.utilization)}</div><p>Utilisation du budget</p><div className="mini-stat"><span>Budget</span><strong>{money(selectedCategory.budget)}</strong></div><div className="mini-stat"><span>Réalisé</span><strong>{money(selectedCategory.actual)}</strong></div><button className="primary-button" onClick={() => setView("overview")} type="button">Retour à la vue générale <ChevronRight size={16} /></button></> : <p className="empty-copy">Utilise le tableau ou le filtre Catégorie pour commencer l’analyse.</p>}</div></section>
      )}

      <footer className="footer-note"><span>Source : City of Austin · Program Budget Operating Budget Vs Expense · FY2026 Q3</span><span>Dashboard interactif · version portfolio</span></footer>
    </main>
  );
}
