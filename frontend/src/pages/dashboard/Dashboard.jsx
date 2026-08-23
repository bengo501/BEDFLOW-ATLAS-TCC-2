import React, { useState, useEffect, useCallback } from 'react';
import { createPortal } from 'react-dom';
import { useLanguage } from '../context/LanguageContext';
import ThemeIcon from './ThemeIcon';
import BackendConnectionError from './BackendConnectionError';
import PaginationControls from './PaginationControls';
import './Dashboard.css';
import '../styles/CasosCFD.css';
import '../styles/MeshViewer3DPage.css';
import { getDashboardSummary, listSimulations, getSimulation, deleteSimulation, parseApiError, getArtifactsStorage } from '../services/api';
import { getSimStatusBadgeClass, slugify } from './results/resultsShared';
import { useActiveUser } from '../context/UserContext';

function formatDurationSeconds(sec) {
  if (typeof sec !== 'number' || Number.isNaN(sec) || sec < 0) return '—';
  const total = Math.floor(sec);
  const h = Math.floor(total / 3600);
  const m = Math.floor((total % 3600) / 60);
  const s = total % 60;
  if (h > 0) return `${h}h ${m}m`;
  if (m > 0) return `${m}m`;
  return `${s}s`;
}

function formatDateShort(iso, language) {
  if (!iso) return '—';
  try {
    return new Date(iso).toLocaleString(language === 'pt' ? 'pt-BR' : 'en-US', {
      dateStyle: 'short',
      timeStyle: 'short',
    });
  } catch {
    return '—';
  }
}

/** anel svg 0–100 % (taxa de sucesso, progresso, etc.) */
function DonutChart({ percent, size = 52, stroke = 5, className = '', strokeColor }) {
  const p = Math.min(100, Math.max(0, Number(percent) || 0));
  const r = (size - stroke) / 2;
  const cx = size / 2;
  const cy = size / 2;
  const c = 2 * Math.PI * r;
  const dash = c * (p / 100);
  const gap = c - dash;
  const arcStroke = strokeColor || 'var(--primary, #5f1923)';
  return (
    <svg
      width={size}
      height={size}
      className={`dash-donut ${className}`}
      viewBox={`0 0 ${size} ${size}`}
      aria-hidden
    >
      <circle
        cx={cx}
        cy={cy}
        r={r}
        fill="none"
        stroke="var(--border, #444)"
        strokeWidth={stroke}
      />
      <circle
        cx={cx}
        cy={cy}
        r={r}
        fill="none"
        stroke={arcStroke}
        strokeWidth={stroke}
        strokeDasharray={`${dash} ${gap}`}
        strokeLinecap="round"
        transform={`rotate(-90 ${cx} ${cy})`}
      />
    </svg>
  );
}

/** barra horizontal proporcional aos estados (concluídas, em execução, …) */
function StatusDistributionBar({ completed, running, pending, failed, pt }) {
  const c = Number(completed) || 0;
  const r = Number(running) || 0;
  const p = Number(pending) || 0;
  const f = Number(failed) || 0;
  const total = c + r + p + f || 1;
  const seg = (n) => ({ width: `${(n / total) * 100}%` });
  return (
    <div className="dash-status-bar-wrap" role="img" aria-label={pt ? 'distribuição por estado' : 'status distribution'}>
      <div className="dash-status-bar">
        {c > 0 ? (
          <div className="dash-status-seg dash-status-seg--completed" style={seg(c)} title={`${pt ? 'concluídas' : 'completed'}: ${c}`} />
        ) : null}
        {r > 0 ? (
          <div className="dash-status-seg dash-status-seg--running" style={seg(r)} title={`${pt ? 'executando' : 'running'}: ${r}`} />
        ) : null}
        {p > 0 ? (
          <div className="dash-status-seg dash-status-seg--pending" style={seg(p)} title={`${pt ? 'pendentes' : 'pending'}: ${p}`} />
        ) : null}
        {f > 0 ? (
          <div className="dash-status-seg dash-status-seg--failed" style={seg(f)} title={`${pt ? 'falhas' : 'failed'}: ${f}`} />
        ) : null}
      </div>
      <ul className="dash-status-legend">
        <li><span className="dash-legend-dot dash-legend-dot--completed" />{pt ? 'concl.' : 'done'} {c}</li>
        <li><span className="dash-legend-dot dash-legend-dot--running" />{pt ? 'exec.' : 'run'} {r}</li>
        <li><span className="dash-legend-dot dash-legend-dot--pending" />{pt ? 'pend.' : 'pend'} {p}</li>
        <li><span className="dash-legend-dot dash-legend-dot--failed" />{pt ? 'falha' : 'fail'} {f}</li>
      </ul>
    </div>
  );
}

function formatGiB(bytes) {
  if (typeof bytes !== 'number' || Number.isNaN(bytes) || bytes < 0) return '0.00';
  return (bytes / 1024 ** 3).toFixed(2);
}

function normalizeSimulationStatus(status) {
  const s = String(status ?? '').trim().toLowerCase();
  if (['completed', 'running', 'pending', 'failed'].includes(s)) return s;
  return s || 'pending';
}

function mapSimulationFromApi(sim, language) {
  return {
    id: sim.id,
    name: sim.name,
    status: normalizeSimulationStatus(sim.status),
    progress: typeof sim.progress === 'number' ? sim.progress : 0,
    bedId: sim.bed_id,
    regime: sim.regime,
    solver: sim.solver,
    inletVelocity: sim.inlet_velocity,
    fluidDensity: sim.fluid_density,
    fluidViscosity: sim.fluid_viscosity,
    maxIterations: sim.max_iterations,
    convergenceCriteria: sim.convergence_criteria,
    description: sim.description,
    meshCellsCount: sim.mesh_cells_count,
    meshQuality: sim.mesh_quality,
    caseDirectory: sim.case_directory,
    logFilePath: sim.log_file_path,
    pressureDrop: sim.pressure_drop,
    averageVelocity: sim.average_velocity,
    reynoldsNumber: sim.reynolds_number,
    executionTime: sim.execution_time,
    parametersJson: sim.parameters_json,
    createdAt: sim.created_at,
    updatedAt: sim.updated_at,
    startedAt: sim.started_at,
    completedAt: sim.completed_at,
    createdBy: sim.created_by,
    date: sim.created_at
      ? new Date(sim.created_at).toLocaleString(language === 'pt' ? 'pt-BR' : 'en-US')
      : '—',
    duration: formatDurationSeconds(sim.execution_time),
  };
}

/** ícone svg atualizar (alinhado a database / templates salvos) */
function IconRefresh({ className }) {
  return (
    <svg
      className={className}
      width="16"
      height="16"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden
    >
      <path d="M23 4v6h-6" />
      <path d="M1 20v-6h6" />
      <path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15" />
    </svg>
  );
}

function Dashboard() {
  const { language, t } = useLanguage();
  const pt = language === 'pt';
  const { activeUserId } = useActiveUser();
  const [dashboardData, setDashboardData] = useState({
    totalSimulations: 0,
    totalModels3D: 0,
    completedSimulations: 0,
    runningSimulations: 0,
    failedSimulations: 0,
    pendingSimulations: 0,
    successRate: 0,
    averageExecutionTime: null,
    averagePressureDrop: null,
    averageReynoldsNumber: null,
  });
  const [searchTerm, setSearchTerm] = useState('');
  const [activeFilter, setActiveFilter] = useState('all');
  const [simulations, setSimulations] = useState([]);
  const [page, setPage] = useState(1);
  const [limit, setLimit] = useState(4);
  const [totalSimulationsList, setTotalSimulationsList] = useState(0);
  const [totalPages, setTotalPages] = useState(1);
  const [loading, setLoading] = useState(true);
  const [silentBusy, setSilentBusy] = useState(false);
  const [connectionError, setConnectionError] = useState(null);
  const [artifacts, setArtifacts] = useState({
    bytes_used: 0,
    bytes_cap: 60 * 1024 ** 3,
    cap_gb: 60,
    percent_of_cap: 0,
    breakdown: [],
  });

  const [modalOpen, setModalOpen] = useState(false);
  const [modalId, setModalId] = useState(null);
  const [modalSim, setModalSim] = useState(null);
  const [modalLoading, setModalLoading] = useState(false);
  const [modalError, setModalError] = useState(null);
  const [actionBusyId, setActionBusyId] = useState(null);

  const getStatusIcon = (status) => {
    const s = normalizeSimulationStatus(status);
    switch (s) {
      case 'completed':
        return <ThemeIcon light="correctLight.png" dark="correctDark.png" alt="" className="status-icon" />;
      case 'running':
        return <ThemeIcon light="runLight.png" dark="runDark.png" alt="" className="status-icon" />;
      case 'pending':
        return <ThemeIcon light="refreshLight.png" dark="refreshDark.png" alt="" className="status-icon" />;
      case 'failed':
        return <ThemeIcon light="cancelLight.png" dark="cancelDark.png" alt="" className="status-icon" />;
      default:
        return null;
    }
  };

  const getStatusText = (status) => {
    const s = normalizeSimulationStatus(status);
    const statusMap = {
      completed: pt ? 'Concluída' : 'Completed',
      running: pt ? 'Executando' : 'Running',
      pending: pt ? 'Pendente' : 'Pending',
      failed: pt ? 'Falhou' : 'Failed',
    };
    return statusMap[s] || s;
  };

  const getStatusClass = (status) => `simulation-status ${normalizeSimulationStatus(status)}`;

  const openSimulationModal = useCallback(
    async (simOrId) => {
      const id = typeof simOrId === 'object' ? simOrId?.id : simOrId;
      const cached =
        typeof simOrId === 'object'
          ? simOrId
          : simulations.find((s) => s.id === id);
      setModalId(id);
      setModalOpen(true);
      setModalLoading(true);
      setModalError(null);
      setModalSim(cached ?? null);
      try {
        const raw = await getSimulation(id);
        setModalSim(mapSimulationFromApi(raw, language));
        setModalError(null);
      } catch (e) {
        if (!cached) {
          setModalError(parseApiError(e) || (pt ? 'erro ao carregar' : 'load error'));
        }
      } finally {
        setModalLoading(false);
      }
    },
    [language, pt, simulations],
  );

  const closeModal = useCallback(() => {
    setModalOpen(false);
    setModalId(null);
    setModalSim(null);
    setModalError(null);
  }, []);

  const handleDownloadSimulation = async (id) => {
    setActionBusyId(id);
    try {
      const data = await getSimulation(id);
      const filename = `simulacao_${data.id}_${slugify(data.name)}.json`;
      const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = filename;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      window.setTimeout(() => URL.revokeObjectURL(url), 1000);
    } catch (e) {
      console.error(e);
    } finally {
      setActionBusyId(null);
    }
  };

  const handleDeleteSimulation = async (id) => {
    const ok = window.confirm(
      pt
        ? `eliminar a simulação #${id}? esta ação é irreversível.`
        : `delete simulation #${id}? this cannot be undone.`,
    );
    if (!ok) return;
    setActionBusyId(id);
    try {
      await deleteSimulation(id);
      await loadData({ silent: true });
    } catch (e) {
      console.error(e);
    } finally {
      setActionBusyId(null);
    }
  };

  useEffect(() => {
    if (!modalOpen) return;
    const onKey = (e) => {
      if (e.key === 'Escape') closeModal();
    };
    window.addEventListener('keydown', onKey);
    return () => window.removeEventListener('keydown', onKey);
  }, [modalOpen, closeModal]);

  const loadData = useCallback(
    async (opts = {}) => {
      const silent = opts.silent === true;
      if (silent) setSilentBusy(true);
      else setLoading(true);
      setConnectionError(null);
      try {
        const [summary, simData, storageRes] = await Promise.all([
          getDashboardSummary(8),
          listSimulations({
            page,
            limit,
            search: searchTerm || null,
            status: activeFilter === 'all' ? null : activeFilter,
          }),
          getArtifactsStorage().catch(() => null),
        ]);

        if (storageRes && typeof storageRes.bytes_used === 'number') {
          setArtifacts({
            bytes_used: storageRes.bytes_used,
            bytes_cap: storageRes.bytes_cap ?? 60 * 1024 ** 3,
            cap_gb: storageRes.cap_gb ?? 60,
            percent_of_cap: Number(storageRes.percent_of_cap) || 0,
            breakdown: Array.isArray(storageRes.breakdown) ? storageRes.breakdown : [],
          });
        }

        setDashboardData({
          totalSimulations: summary.total_simulations || 0,
          totalModels3D: summary.total_models_3d || 0,
          completedSimulations: summary.by_status?.completed || 0,
          runningSimulations: summary.by_status?.running || 0,
          failedSimulations: summary.by_status?.failed || 0,
          pendingSimulations: summary.by_status?.pending || 0,
          successRate: summary.success_rate || 0,
          averageExecutionTime: summary.average_execution_time,
          averagePressureDrop: summary.average_pressure_drop,
          averageReynoldsNumber: summary.average_reynolds_number,
        });

        const recentItems = Array.isArray(simData?.items) ? simData.items : [];
        setSimulations(recentItems.map((sim) => mapSimulationFromApi(sim, language)));
        setTotalSimulationsList(simData?.total || 0);
        setTotalPages(simData?.total_pages || simData?.pages || 1);
      } catch (error) {
        console.error('erro ao carregar dados do dashboard:', error);
        setConnectionError(t('backendConnectionError'));
        setSimulations([]);
        setTotalSimulationsList(0);
      } finally {
        setLoading(false);
        setSilentBusy(false);
      }
    },
    [activeFilter, language, limit, page, searchTerm, t],
  );

  useEffect(() => {
    void loadData({ silent: false });
    const timer = window.setInterval(() => void loadData({ silent: true }), 5000);
    return () => window.clearInterval(timer);
  }, [activeUserId, loadData]);

  return (
    <div className="dashboard">
      <div className="dashboard-header">
        <div className="dashboard-title-row">
          <ThemeIcon light="analiseLight.png" dark="analiseLight.png" alt="" className="dashboard-title-icon" location="sidebar" />
          <h1>{pt ? 'Dashboard' : 'Dashboard'}</h1>
        </div>
      </div>

      {connectionError && <BackendConnectionError message={connectionError} />}

      <div className="metrics-grid metrics-grid--compact">
        <div className="metric-card">
          <div className="metric-icon">
            <ThemeIcon light="triangle_white_outline.png" dark="triangle_black_outline.png" alt="" className="card-icon card-icon--sm" />
          </div>
          <div className="metric-content">
            <div className="metric-value metric-value--sm">{dashboardData.totalSimulations}</div>
            <div className="metric-label">{pt ? 'Total de simulações' : 'Total simulations'}</div>
            <div className="metric-subtitle">
              {dashboardData.completedSimulations} {pt ? 'concluídas' : 'completed'}
            </div>
          </div>
        </div>

        <div className="metric-card">
          <div className="metric-icon success">
            <ThemeIcon light="modelLight-removebg-preview.png" dark="modelDark-removebg-preview.png" alt="" className="card-icon card-icon--sm dash-metric-icon-themed" />
          </div>
          <div className="metric-content">
            <div className="metric-value metric-value--sm">{dashboardData.totalModels3D}</div>
            <div className="metric-label">{pt ? 'Modelos 3D' : '3D models'}</div>
            <div className="metric-subtitle">{pt ? 'Persistidos no SQLite' : 'Persisted in SQLite'}</div>
          </div>
        </div>

        <div className="metric-card metric-card--with-chart">
          <div className="metric-icon warning">
            <ThemeIcon light="correctLight.png" dark="correctDark.png" alt="" className="card-icon card-icon--sm" />
          </div>
          <div className="metric-content">
            <div className="metric-row-chart">
              <DonutChart percent={dashboardData.successRate} size={48} stroke={5} />
              <div>
                <div className="metric-value metric-value--sm">{dashboardData.successRate.toFixed(1)}%</div>
                <div className="metric-label">{pt ? 'Taxa de sucesso' : 'Success rate'}</div>
                <div className="metric-subtitle">
                  {dashboardData.completedSimulations}/{dashboardData.totalSimulations || 0}
                </div>
              </div>
            </div>
          </div>
        </div>

        <div className="metric-card">
          <div className="metric-icon error">
            <ThemeIcon light="runLight.png" dark="runDark.png" alt="" className="card-icon card-icon--sm" />
          </div>
          <div className="metric-content">
            <div className="metric-value metric-value--sm">{dashboardData.runningSimulations}</div>
            <div className="metric-label">{pt ? 'Em execução' : 'Running'}</div>
            <div className="metric-subtitle">
              {dashboardData.pendingSimulations} {pt ? 'pendentes' : 'pending'}
            </div>
          </div>
        </div>
      </div>

      <div className="dash-chart-panel">
        <h4 className="dash-chart-panel-title">{pt ? 'Simulações por estado' : 'Simulations by status'}</h4>
        <StatusDistributionBar
          completed={dashboardData.completedSimulations}
          running={dashboardData.runningSimulations}
          pending={dashboardData.pendingSimulations}
          failed={dashboardData.failedSimulations}
          pt={pt}
        />
      </div>

      <div className="resources-grid resources-grid--compact">
        <div className="resource-card">
          <div className="resource-icon">
            <ThemeIcon light="job_monitor_clock_white.png" dark="job_monitor_clock_white.png" alt="" className="card-icon card-icon--sm dash-metric-icon-themed" />
          </div>
          <div className="resource-content">
            <div className="resource-value resource-value--sm">{formatDurationSeconds(dashboardData.averageExecutionTime)}</div>
            <div className="resource-label">{pt ? 'Tempo médio' : 'Average time'}</div>
            <div className="resource-subtitle">{pt ? 'Simulações concluídas' : 'Completed simulations'}</div>
          </div>
        </div>

        <div className="resource-card">
          <div className="resource-icon">
            <ThemeIcon light="triangle_white_outline.png" dark="triangle_black_outline.png" alt="" className="card-icon card-icon--sm" />
          </div>
          <div className="resource-content">
            <div className="resource-value resource-value--sm">
              {dashboardData.averagePressureDrop != null ? dashboardData.averagePressureDrop.toFixed(2) : '—'}
            </div>
            <div className="resource-label">{pt ? 'Queda média de pressão' : 'Average pressure drop'}</div>
            <div className="resource-subtitle">Pa</div>
          </div>
        </div>

        <div className="resource-card">
          <div className="resource-icon success">
            <ThemeIcon light="database-01-svgrepo-com.svg" dark="database-01-svgrepo-com.svg" alt="" className="card-icon card-icon--sm db-memory-icon" />
          </div>
          <div className="resource-content">
            <div className="resource-value resource-value--sm">
              {dashboardData.averageReynoldsNumber != null ? dashboardData.averageReynoldsNumber.toFixed(2) : '—'}
            </div>
            <div className="resource-label">{pt ? 'Reynolds médio' : 'Average Reynolds'}</div>
            <div className="resource-subtitle">{pt ? 'Dados reais' : 'Real data'}</div>
          </div>
        </div>

        <div className="resource-card resource-card--with-mini-donut">
          <div className="resource-icon error">
            <ThemeIcon light="cancelLight.png" dark="cancelDark.png" alt="" className="card-icon card-icon--sm" />
          </div>
          <div className="resource-content resource-content--row">
            <div>
              <div className="resource-value resource-value--sm">{dashboardData.failedSimulations}</div>
              <div className="resource-label">{pt ? 'Falhas' : 'Failures'}</div>
              <div className="resource-subtitle">{pt ? 'Sincronizadas do backend' : 'Synced from backend'}</div>
            </div>
            {dashboardData.totalSimulations > 0 ? (
              <div className="resource-mini-donut" title={pt ? '% falhas sobre o total' : '% failed of total'}>
                <DonutChart
                  percent={(100 * dashboardData.failedSimulations) / dashboardData.totalSimulations}
                  size={40}
                  stroke={4}
                  strokeColor="var(--error, #c62828)"
                />
                <span className="resource-mini-donut-label">
                  {((100 * dashboardData.failedSimulations) / dashboardData.totalSimulations).toFixed(0)}%
                </span>
              </div>
            ) : null}
          </div>
        </div>
      </div>

      <div className="dash-artifacts-widget ui-raised-surface">
        <div className="dash-artifacts-row">
          <div className="dash-artifacts-text">
            <div className="dash-artifacts-title">
              {pt ? 'Disco — artefactos do projeto' : 'Disk — project artifacts'}
            </div>
            <div className="dash-artifacts-sub">
              {formatGiB(artifacts.bytes_used)} / {artifacts.cap_gb} GiB ·{' '}
              {Number(artifacts.percent_of_cap).toFixed(1)}% {pt ? 'do limite' : 'of cap'}
            </div>
          </div>
          <DonutChart percent={artifacts.percent_of_cap} size={44} stroke={5} />
        </div>
        <div className="dash-artifacts-track" title={pt ? 'Percentagem usada' : 'Percent used'}>
          <div
            className="dash-artifacts-fill"
            style={{ width: `${Math.min(100, Number(artifacts.percent_of_cap) || 0)}%` }}
          />
        </div>
        {artifacts.breakdown?.length > 0 && (
          <ul className="dash-artifacts-breakdown">
            {artifacts.breakdown.map((row) => (
              <li key={row.label}>
                <span>{row.label}</span>
                <span>
                  {formatGiB(row.size_bytes)} GiB
                </span>
              </li>
            ))}
          </ul>
        )}
      </div>

      <div className="dash-simulations-section">
        <div className="dash-simulations-title-row dash-simulations-title-row--section">
          <ThemeIcon light="jobLight.png" dark="jobDark.png" alt="" className="dash-simulations-title-icon" />
          <h3>{pt ? 'Simulações' : 'Simulations'}</h3>
        </div>

        <div className="dash-simulations-panel ui-raised-surface">
          <div className="dash-simulations-panel-toolbar">
            <div className="dash-sim-search-row">
              <input
                type="text"
                placeholder={pt ? 'Buscar simulações…' : 'Search simulations…'}
                value={searchTerm}
                onChange={(e) => {
                  setPage(1);
                  setSearchTerm(e.target.value);
                }}
                className="search-input search-input--compact"
                aria-label={pt ? 'Buscar simulações' : 'Search simulations'}
              />
              <button
                type="button"
                className="mesh-viewer-hub-btn mesh-viewer-hub-btn--compact"
                onClick={() => void loadData({ silent: true })}
                disabled={loading || silentBusy}
                aria-busy={silentBusy || undefined}
                title={pt ? 'atualizar lista' : 'refresh list'}
              >
                <IconRefresh className="mesh-viewer-hub-btn__icon" aria-hidden />
                {loading || silentBusy ? '…' : pt ? 'atualizar' : 'refresh'}
              </button>
            </div>

            <div className="filter-section filter-section--in-panel">
            <button
              type="button"
              className={`filter-btn filter-btn--sm ${activeFilter === 'all' ? 'active' : ''}`}
              onClick={() => {
                setPage(1);
                setActiveFilter('all');
              }}
            >
              {pt ? 'Todas' : 'All'} ({totalSimulationsList})
            </button>
            <button
              type="button"
              className={`filter-btn filter-btn--sm ${activeFilter === 'completed' ? 'active' : ''}`}
              onClick={() => {
                setPage(1);
                setActiveFilter('completed');
              }}
            >
              <ThemeIcon light="correctLight.png" dark="correctDark.png" alt="" className="filter-icon" />
              {pt ? 'Concluídas' : 'Completed'}
            </button>
            <button
              type="button"
              className={`filter-btn filter-btn--sm ${activeFilter === 'running' ? 'active' : ''}`}
              onClick={() => {
                setPage(1);
                setActiveFilter('running');
              }}
            >
              <ThemeIcon light="runLight.png" dark="runDark.png" alt="" className="filter-icon" />
              {pt ? 'Executando' : 'Running'}
            </button>
            <button
              type="button"
              className={`filter-btn filter-btn--sm ${activeFilter === 'pending' ? 'active' : ''}`}
              onClick={() => {
                setPage(1);
                setActiveFilter('pending');
              }}
            >
              <ThemeIcon light="refreshLight.png" dark="refreshDark.png" alt="" className="filter-icon" />
              {pt ? 'Pendentes' : 'Pending'}
            </button>
            <button
              type="button"
              className={`filter-btn filter-btn--sm ${activeFilter === 'failed' ? 'active' : ''}`}
              onClick={() => {
                setPage(1);
                setActiveFilter('failed');
              }}
            >
              <ThemeIcon light="cancelLight.png" dark="cancelDark.png" alt="" className="filter-icon" />
              {pt ? 'Falharam' : 'Failed'}
            </button>
            </div>
          </div>

          <div className="casos-grid">
          {loading && <p className="simulations-loading">{pt ? 'A carregar…' : 'Loading…'}</p>}
          {!loading && simulations.length === 0 && (
            <p className="simulations-empty">{pt ? 'Nenhuma simulação encontrada' : 'No simulations found'}</p>
          )}
          {simulations.map((simulation) => {
            const simStatus = normalizeSimulationStatus(simulation.status);
            return (
            <div key={simulation.id} className="caso-card">
              <div className="caso-header">
                <h3 title={simulation.name}>{simulation.name}</h3>
                <span className={`status-badge ${getSimStatusBadgeClass(simStatus)}`}>
                  {getStatusText(simStatus)}
                </span>
              </div>
              <div className="caso-info">
                <div className="info-row">
                  <span className="info-label">id:</span>
                  <span>{simulation.id}</span>
                </div>
                <div className="info-row">
                  <span className="info-label">{pt ? 'leito:' : 'bed:'}</span>
                  <span>#{simulation.bedId ?? '—'}</span>
                </div>
                <div className="info-row">
                  <span className="info-label">{pt ? 'criado:' : 'created:'}</span>
                  <span>{simulation.date}</span>
                </div>
                <div className="info-row">
                  <span className="info-label">{pt ? 'duração:' : 'duration:'}</span>
                  <span>{simulation.duration}</span>
                </div>
                {(simStatus === 'running' || simStatus === 'pending') && (
                  <div className="info-row">
                    <span className="info-label">{pt ? 'progresso:' : 'progress:'}</span>
                    <span>{simulation.progress}%</span>
                  </div>
                )}
                {simulation.regime ? (
                  <div className="info-row">
                    <span className="info-label">{pt ? 'regime:' : 'regime:'}</span>
                    <span>{simulation.regime}</span>
                  </div>
                ) : null}
              </div>
              <div className="caso-acoes">
                <button
                  type="button"
                  className="btn-mode-option"
                  onClick={() => void openSimulationModal(simulation)}
                  disabled={actionBusyId === simulation.id}
                >
                  <ThemeIcon light="docsLight.png" dark="docsLight.png" alt="" className="btn-icon" />
                  {pt ? 'detalhes' : 'details'}
                </button>
                <button
                  type="button"
                  className="btn-mode-option"
                  onClick={() => void handleDownloadSimulation(simulation.id)}
                  disabled={actionBusyId === simulation.id}
                >
                  <ThemeIcon light="downloadLight-removebg-preview.png" dark="donwloadDark-removebg-preview.png" alt="" className="btn-icon" />
                  json
                </button>
                <button
                  type="button"
                  className="btn-mode-option"
                  onClick={() => void handleDeleteSimulation(simulation.id)}
                  disabled={actionBusyId === simulation.id}
                >
                  <ThemeIcon light="cancelLight.png" dark="cancelDark.png" alt="" className="btn-icon" />
                  {pt ? 'deletar' : 'delete'}
                </button>
              </div>
            </div>
            );
          })}
          </div>

          <PaginationControls
            page={page}
            totalPages={totalPages}
            total={totalSimulationsList}
            limit={limit}
            loading={loading}
            onPageChange={setPage}
            onLimitChange={(value) => {
              setPage(1);
              setLimit(value);
            }}
            label={pt ? 'Lista do dashboard' : 'Dashboard list'}
            limitOptions={[4, 8, 12, 20, 50]}
            pt={pt}
          />
        </div>
      </div>

      {modalOpen &&
        createPortal(
          <div
            className="dash-modal-overlay"
            role="presentation"
            onClick={(e) => {
              if (e.target === e.currentTarget) closeModal();
            }}
          >
            <div
              className="dash-modal"
              role="dialog"
              aria-modal="true"
              aria-labelledby="dash-modal-title"
              onClick={(e) => e.stopPropagation()}
            >
              <div className="dash-modal-header">
                <h2 id="dash-modal-title">
                  {modalLoading ? (pt ? 'a carregar…' : 'loading…') : modalSim?.name || `id ${modalId}`}
                </h2>
                <button type="button" className="dash-modal-close" onClick={closeModal} aria-label={pt ? 'fechar' : 'close'}>
                  ×
                </button>
              </div>
              <div className="dash-modal-body">
                {modalError && <p className="dash-modal-err">{modalError}</p>}
                {modalLoading && !modalSim && (
                  <p className="dash-modal-muted">{pt ? 'a obter dados da base…' : 'fetching from database…'}</p>
                )}
                {modalSim && (
                  <>
                    <div className="dash-modal-hero">
                      <div className={getStatusClass(modalSim.status)}>
                        {getStatusIcon(modalSim.status)}
                        {getStatusText(modalSim.status)}
                      </div>
                      <DonutChart percent={modalSim.progress} size={72} stroke={7} />
                      <div className="dash-modal-progress-label">{modalSim.progress}%</div>
                    </div>
                    <dl className="dash-modal-dl">
                      <dt>id</dt>
                      <dd>{modalSim.id}</dd>
                      <dt>{pt ? 'leito' : 'bed'}</dt>
                      <dd>#{modalSim.bedId}</dd>
                      <dt>{pt ? 'regime' : 'regime'}</dt>
                      <dd>{modalSim.regime ?? '—'}</dd>
                      <dt>{pt ? 'solver' : 'solver'}</dt>
                      <dd>{modalSim.solver ?? '—'}</dd>
                      <dt>{pt ? 'velocidade entrada' : 'inlet velocity'}</dt>
                      <dd>{modalSim.inletVelocity != null ? `${modalSim.inletVelocity} m/s` : '—'}</dd>
                      <dt>{pt ? 'densidade' : 'density'}</dt>
                      <dd>{modalSim.fluidDensity != null ? `${modalSim.fluidDensity} kg/m³` : '—'}</dd>
                      <dt>{pt ? 'viscosidade' : 'viscosity'}</dt>
                      <dd>{modalSim.fluidViscosity != null ? `${modalSim.fluidViscosity} pa·s` : '—'}</dd>
                      <dt>{pt ? 'iterações máx.' : 'max iterations'}</dt>
                      <dd>{modalSim.maxIterations ?? '—'}</dd>
                      <dt>{pt ? 'convergência' : 'convergence'}</dt>
                      <dd>{modalSim.convergenceCriteria ?? '—'}</dd>
                      <dt>{pt ? 'células malha' : 'mesh cells'}</dt>
                      <dd>{modalSim.meshCellsCount ?? '—'}</dd>
                      <dt>{pt ? 'qualidade malha' : 'mesh quality'}</dt>
                      <dd>{modalSim.meshQuality ?? '—'}</dd>
                      <dt>Δp</dt>
                      <dd>{modalSim.pressureDrop != null ? `${Number(modalSim.pressureDrop).toFixed(4)} pa` : '—'}</dd>
                      <dt>{pt ? 'velocidade média' : 'avg velocity'}</dt>
                      <dd>{modalSim.averageVelocity != null ? `${Number(modalSim.averageVelocity).toFixed(4)} m/s` : '—'}</dd>
                      <dt>reynolds</dt>
                      <dd>{modalSim.reynoldsNumber != null ? Number(modalSim.reynoldsNumber).toFixed(2) : '—'}</dd>
                      <dt>{pt ? 'duração execução' : 'execution time'}</dt>
                      <dd>{formatDurationSeconds(modalSim.executionTime)}</dd>
                      <dt>{pt ? 'criado em' : 'created'}</dt>
                      <dd>{formatDateShort(modalSim.createdAt, language)}</dd>
                      <dt>{pt ? 'início' : 'started'}</dt>
                      <dd>{formatDateShort(modalSim.startedAt, language)}</dd>
                      <dt>{pt ? 'concluído' : 'completed'}</dt>
                      <dd>{formatDateShort(modalSim.completedAt, language)}</dd>
                      <dt>{pt ? 'atualizado' : 'updated'}</dt>
                      <dd>{formatDateShort(modalSim.updatedAt, language)}</dd>
                      <dt>{pt ? 'diretório caso' : 'case directory'}</dt>
                      <dd className="dash-modal-path">{modalSim.caseDirectory ?? '—'}</dd>
                      <dt>{pt ? 'log' : 'log'}</dt>
                      <dd className="dash-modal-path">{modalSim.logFilePath ?? '—'}</dd>
                      {modalSim.description ? (
                        <>
                          <dt>{pt ? 'descrição' : 'description'}</dt>
                          <dd>{modalSim.description}</dd>
                        </>
                      ) : null}
                    </dl>
                    {modalSim.parametersJson && Object.keys(modalSim.parametersJson).length > 0 ? (
                      <details className="dash-modal-json">
                        <summary>{pt ? 'parameters_json' : 'parameters_json'}</summary>
                        <pre>{JSON.stringify(modalSim.parametersJson, null, 2)}</pre>
                      </details>
                    ) : null}
                  </>
                )}
              </div>
            </div>
          </div>,
          document.body,
        )}
    </div>
  );
}

export default Dashboard;
