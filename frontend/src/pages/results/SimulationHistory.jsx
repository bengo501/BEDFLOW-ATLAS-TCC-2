import React, { useState, useEffect, useCallback } from 'react';
import { useLanguage } from '../context/LanguageContext';
import ThemeIcon from './ThemeIcon';
import BackendConnectionError from './BackendConnectionError';
import {
  listSimulations,
  listModels3D,
  getSimulation,
  deleteSimulation,
  createSimulationRecord,
  buildGeneratedFileUrl,
  buildMeshStreamUrl,
  listViewerMeshes,
  mergeDbModelsWithProjectMeshes,
} from '../services/api';
import { useActiveUser } from '../context/UserContext';
import PaginationControls from './PaginationControls';
import '../styles/CasosCFD.css';
import '../styles/MeshViewer3DPage.css';
import './SimulationHistory.css';

function isConnectionError(err) {
  if (!err) return false;
  const noResponse = !err.response && !!err.request;
  const network =
    err.code === 'ERR_NETWORK' ||
    err.code === 'ECONNABORTED' ||
    (typeof err.message === 'string' && err.message.toLowerCase().includes('network'));
  return noResponse || network;
}

function formatDurationSeconds(sec, language) {
  if (typeof sec !== 'number' || sec < 0 || Number.isNaN(sec)) return '—';
  const s = Math.floor(sec);
  const h = Math.floor(s / 3600);
  const m = Math.floor((s % 3600) / 60);
  if (h > 0) return language === 'pt' ? `${h}h ${m}m` : `${h}h ${m}m`;
  if (m > 0) return language === 'pt' ? `${m}m` : `${m}m`;
  return language === 'pt' ? `${s}s` : `${s}s`;
}

function mapApiSimulation(item, language) {
  const created = item.created_at ? new Date(item.created_at) : null;
  const createdDate = created
    ? created.toLocaleString(language === 'pt' ? 'pt-BR' : 'en-US')
    : '—';
  return {
    id: item.id,
    name: item.name,
    description: item.description || '',
    status: item.status,
    createdDate,
    duration: formatDurationSeconds(item.execution_time, language),
    bedId: item.bed_id,
    progress: typeof item.progress === 'number' ? item.progress : 0
  };
}

/** ícone svg atualizar (contraste no botão primário) */
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

function slugify(s) {
  return String(s || 'simulacao')
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '')
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/^-+|-+$/g, '')
    .slice(0, 60) || 'simulacao';
}

function getSimStatusBadgeClass(status) {
  switch (status) {
    case 'completed':
      return 'status-completed';
    case 'running':
      return 'status-running';
    case 'pending':
      return 'status-configured';
    case 'failed':
      return 'status-unknown';
    default:
      return 'status-unknown';
  }
}

function formatBytes(bytes) {
  if (typeof bytes !== 'number' || bytes < 0) return '—';
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

function SimulationHistory() {
  const { language, t } = useLanguage();
  const { activeUserId } = useActiveUser();
  const pt = language === 'pt';
  const [simulations, setSimulations] = useState([]);
  const [models3d, setModels3d] = useState([]);
  const [simPage, setSimPage] = useState(1);
  const [simLimit, setSimLimit] = useState(8);
  const [simTotal, setSimTotal] = useState(0);
  const [simTotalPages, setSimTotalPages] = useState(1);
  const [simFilters, setSimFilters] = useState({
    search: '',
    status: '',
    regime: '',
    created_from: '',
    created_to: '',
  });
  const [modelPage, setModelPage] = useState(1);
  const [modelLimit, setModelLimit] = useState(8);
  const [modelTotal, setModelTotal] = useState(0);
  const [modelTotalPages, setModelTotalPages] = useState(1);
  const [modelFilters, setModelFilters] = useState({
    search: '',
    packing_method: '',
    has_blend: '',
    has_stl: '',
    created_from: '',
    created_to: '',
  });
  const [loading, setLoading] = useState(true);
  const [modelsRefreshing, setModelsRefreshing] = useState(false);
  const [simsRefreshing, setSimsRefreshing] = useState(false);
  const [loadError, setLoadError] = useState(null);
  const [opError, setOpError] = useState(null);
  const [opSuccess, setOpSuccess] = useState(null);
  const [actionBusyId, setActionBusyId] = useState(null);
  const [viewModalId, setViewModalId] = useState(null);
  const [viewDetail, setViewDetail] = useState(null);
  const [viewLoading, setViewLoading] = useState(false);

  const loadModels = useCallback(async ({ silent = false } = {}) => {
    if (!silent) setModelsRefreshing(true);
    setLoadError(null);
    try {
      const [modelData, meshData] = await Promise.all([
        listModels3D({
          page: modelPage,
          limit: modelLimit,
          search: modelFilters.search,
          packing_method: modelFilters.packing_method || null,
          has_blend: modelFilters.has_blend === '' ? null : modelFilters.has_blend === 'true',
          has_stl: modelFilters.has_stl === '' ? null : modelFilters.has_stl === 'true',
          created_from: modelFilters.created_from || null,
          created_to: modelFilters.created_to || null,
        }),
        listViewerMeshes({ q: modelFilters.search || undefined, limit: 500 }),
      ]);
      const dbItems = Array.isArray(modelData?.items) ? modelData.items : [];
      const merged = mergeDbModelsWithProjectMeshes(dbItems, meshData);
      setModels3d(merged);
      const extra = merged.length - dbItems.length;
      setModelTotal((modelData?.total || 0) + extra);
      setModelTotalPages(modelData?.total_pages || modelData?.pages || 1);
    } catch (err) {
      console.error('simulation history models:', err);
      if (isConnectionError(err)) {
        setLoadError(t('backendConnectionError'));
      } else {
        const detail = err.response?.data?.detail;
        setLoadError(
          typeof detail === 'string'
            ? detail
            : pt
              ? 'erro ao carregar modelos 3d'
              : 'failed to load 3d models'
        );
      }
      setModels3d([]);
      setModelTotal(0);
    } finally {
      if (!silent) setModelsRefreshing(false);
    }
  }, [modelFilters, modelLimit, modelPage, pt, t]);

  const loadSimulations = useCallback(async ({ silent = false } = {}) => {
    if (!silent) setSimsRefreshing(true);
    setLoadError(null);
    try {
      const simData = await listSimulations({
        page: simPage,
        limit: simLimit,
        search: simFilters.search,
        status: simFilters.status || null,
        regime: simFilters.regime || null,
        created_from: simFilters.created_from || null,
        created_to: simFilters.created_to || null,
      });
      const simItems = Array.isArray(simData?.items) ? simData.items : [];
      setSimulations(simItems.map((row) => mapApiSimulation(row, language)));
      setSimTotal(simData?.total || 0);
      setSimTotalPages(simData?.total_pages || simData?.pages || 1);
    } catch (err) {
      console.error('simulation history simulations:', err);
      if (isConnectionError(err)) {
        setLoadError(t('backendConnectionError'));
      } else {
        const detail = err.response?.data?.detail;
        setLoadError(
          typeof detail === 'string'
            ? detail
            : pt
              ? 'erro ao carregar simulações'
              : 'failed to load simulations'
        );
      }
      setSimulations([]);
      setSimTotal(0);
    } finally {
      if (!silent) setSimsRefreshing(false);
    }
  }, [language, simFilters, simLimit, simPage, pt, t]);

  const loadData = useCallback(async ({ silent = false } = {}) => {
    if (!silent) setLoading(true);
    setLoadError(null);
    await Promise.all([loadSimulations({ silent: true }), loadModels({ silent: true })]);
    if (!silent) setLoading(false);
  }, [loadModels, loadSimulations]);

  useEffect(() => {
    loadData();
    const timer = window.setInterval(loadData, 5000);
    return () => window.clearInterval(timer);
  }, [activeUserId, loadData]);

  const getStatusIcon = (status) => {
    switch (status) {
      case 'completed':
        return <ThemeIcon light="correctLight.png" dark="correctDark.png" alt="completed" className="status-icon completed" />;
      case 'running':
        return <ThemeIcon light="runLight.png" dark="runDark.png" alt="running" className="status-icon running" />;
      case 'pending':
        return <ThemeIcon light="job_monitor_clock_white.png" dark="job_monitor_clock_white.png" alt="pending" className="status-icon pending" />;
      case 'failed':
        return <ThemeIcon light="cancelLight.png" dark="cancelDark.png" alt="failed" className="status-icon failed" />;
      default:
        return null;
    }
  };

  const getStatusText = (status) => {
    switch (status) {
      case 'completed':
        return language === 'pt' ? 'Concluída' : 'Completed';
      case 'running':
        return language === 'pt' ? 'Em execução' : 'Running';
      case 'pending':
        return language === 'pt' ? 'Pendente' : 'Pending';
      case 'failed':
        return language === 'pt' ? 'Falhou' : 'Failed';
      default:
        return status;
    }
  };

  const flashSuccess = useCallback((msg) => {
    setOpSuccess(msg);
    setTimeout(() => setOpSuccess(null), 2500);
  }, []);

  const closeViewModal = useCallback(() => {
    setViewModalId(null);
    setViewDetail(null);
    setViewLoading(false);
  }, []);

  useEffect(() => {
    if (viewModalId == null) return;
    const onKey = (e) => {
      if (e.key === 'Escape') closeViewModal();
    };
    window.addEventListener('keydown', onKey);
    return () => window.removeEventListener('keydown', onKey);
  }, [viewModalId, closeViewModal]);

  const handleViewSimulation = async (id) => {
    setOpError(null);
    setViewModalId(id);
    setViewLoading(true);
    setViewDetail(null);
    try {
      const data = await getSimulation(id);
      setViewDetail(data);
    } catch (err) {
      console.error('erro ao obter simulacao:', err);
      if (isConnectionError(err)) setOpError(t('backendConnectionError'));
      else setOpError(err.response?.data?.detail || (pt ? 'falha ao carregar detalhes' : 'failed to load details'));
      closeViewModal();
    } finally {
      setViewLoading(false);
    }
  };

  const handleDownloadResults = async (id) => {
    setOpError(null);
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
      setTimeout(() => URL.revokeObjectURL(url), 1000);
      flashSuccess(pt ? 'dados baixados' : 'data downloaded');
    } catch (err) {
      console.error('erro ao baixar:', err);
      if (isConnectionError(err)) setOpError(t('backendConnectionError'));
      else setOpError(err.response?.data?.detail || (pt ? 'falha ao baixar' : 'download failed'));
    } finally {
      setActionBusyId(null);
    }
  };

  const handleDeleteSimulation = async (id) => {
    setOpError(null);
    const ok = window.confirm(
      pt
        ? `eliminar a simulação #${id} e todos os seus resultados? esta ação é irreversível.`
        : `delete simulation #${id} and all its results? this action cannot be undone.`
    );
    if (!ok) return;
    setActionBusyId(id);
    try {
      await deleteSimulation(id);
      flashSuccess(pt ? 'simulação eliminada' : 'simulation deleted');
      await loadData();
    } catch (err) {
      console.error('erro ao deletar:', err);
      if (isConnectionError(err)) setOpError(t('backendConnectionError'));
      else setOpError(err.response?.data?.detail || (pt ? 'falha ao eliminar' : 'delete failed'));
    } finally {
      setActionBusyId(null);
    }
  };

  const handleRerunSimulation = async (id) => {
    setOpError(null);
    const ok = window.confirm(
      pt
        ? `duplicar os parâmetros da simulação #${id} e criar uma nova execução?`
        : `clone parameters of simulation #${id} and create a new run?`
    );
    if (!ok) return;
    setActionBusyId(id);
    try {
      const src = await getSimulation(id);
      const payload = {
        bed_id: src.bed_id,
        name: `${src.name || (pt ? 'simulação' : 'simulation')} (${pt ? 're-execução' : 're-run'})`,
        description: src.description || '',
        regime: src.regime,
        inlet_velocity: src.inlet_velocity,
        fluid_density: src.fluid_density,
        fluid_viscosity: src.fluid_viscosity,
        solver: src.solver || 'simpleFoam',
        max_iterations: src.max_iterations ?? 1000,
        convergence_criteria: src.convergence_criteria ?? 1e-4,
        parameters_json: src.parameters_json || null,
      };
      const created = await createSimulationRecord(payload);
      flashSuccess(pt ? `nova simulação criada #${created.id}` : `new simulation created #${created.id}`);
      await loadData();
    } catch (err) {
      console.error('erro ao reexecutar:', err);
      if (isConnectionError(err)) setOpError(t('backendConnectionError'));
      else setOpError(err.response?.data?.detail || (pt ? 'falha ao reexecutar' : 'rerun failed'));
    } finally {
      setActionBusyId(null);
    }
  };

  const emptyNoData = !loading && !loadError && simTotal === 0 && modelTotal === 0;

  return (
    <div className="simulation-history">
      <div className="history-header">
        <div className="history-header-top">
          <div className="history-title">
            <ThemeIcon light="folderLight.png" dark="folderDark.png" alt="histórico" className="title-icon" />
            <h1>{language === 'pt' ? 'Histórico de simulações' : 'Simulation history'}</h1>
          </div>
          <button
            type="button"
            className="mesh-viewer-hub-btn mesh-viewer-hub-btn--compact"
            onClick={() => void loadData()}
            disabled={loading}
            aria-busy={loading || undefined}
          >
            <IconRefresh className="mesh-viewer-hub-btn__icon" aria-hidden />
            {loading ? '…' : pt ? 'atualizar' : 'refresh'}
          </button>
        </div>
        <p className="history-description">
          {language === 'pt'
            ? 'Visualize e gerencie todas as suas simulações cfd'
            : 'View and manage all your cfd simulations'}
        </p>
      </div>

      {loadError && <BackendConnectionError message={loadError} />}

      {opError && (
        <div className="history-op-error" role="alert">
          {opError}
        </div>
      )}

      {opSuccess && (
        <div className="history-op-success" role="status">
          {opSuccess}
        </div>
      )}

      {loading && (
        <div className="sim-history-loading">
          {language === 'pt' ? 'Carregando…' : 'Loading…'}
        </div>
      )}

      {!loading && emptyNoData && (
        <div className="sim-history-empty">
          <p>{language === 'pt' ? 'Nenhuma simulação encontrada' : 'No simulations found'}</p>
          <p className="sim-history-empty-hint">
            {language === 'pt'
              ? 'Use o wizard ou o pipeline para criar leitos e registar simulações'
              : 'Use the wizard or pipeline to create beds and register simulations'}
          </p>
        </div>
      )}

      <div className="history-panels">
      <section className="results-section history-panel" aria-labelledby="history-simulations-heading">
        <div className="results-section-heading">
          <div className="results-section-title">
            <h3 id="history-simulations-heading" className="history-section-heading">
              <ThemeIcon
                light="cfd_gear_white.png"
                dark="image-removebg-preview(12).png"
                alt=""
                className="results-section-icon"
              />
              <span>
                {pt ? 'Simulações' : 'Simulations'} ({simTotal})
              </span>
            </h3>
          </div>
          <div className="results-section-toolbar">
            <button
              type="button"
              className="mesh-viewer-hub-btn mesh-viewer-hub-btn--compact"
              onClick={() => void loadSimulations()}
              disabled={simsRefreshing || loading}
              aria-busy={simsRefreshing || undefined}
            >
              <IconRefresh className="mesh-viewer-hub-btn__icon" aria-hidden />
              {simsRefreshing ? '…' : pt ? 'atualizar' : 'refresh'}
            </button>
          </div>
        </div>

        <div className="history-filter-grid">
          <div className="search-container">
            <ThemeIcon light="triangle_white_outline.png" dark="triangle_black_outline.png" alt="buscar" className="search-icon" />
            <input
              type="text"
              placeholder={pt ? 'Buscar por nome, descrição ou id…' : 'Search by name, description or id…'}
              value={simFilters.search}
              onChange={(e) => {
                setSimPage(1);
                setSimFilters((prev) => ({ ...prev, search: e.target.value }));
              }}
              className="search-input"
            />
          </div>

          <select
            className="history-select"
            value={simFilters.status}
            onChange={(e) => {
              setSimPage(1);
              setSimFilters((prev) => ({ ...prev, status: e.target.value }));
            }}
          >
            <option value="">{pt ? 'Todos os estados' : 'All statuses'}</option>
            <option value="completed">{pt ? 'Concluída' : 'Completed'}</option>
            <option value="running">{pt ? 'Em execução' : 'Running'}</option>
            <option value="pending">{pt ? 'Pendente' : 'Pending'}</option>
            <option value="failed">{pt ? 'Falhou' : 'Failed'}</option>
          </select>

          <select
            className="history-select"
            value={simFilters.regime}
            onChange={(e) => {
              setSimPage(1);
              setSimFilters((prev) => ({ ...prev, regime: e.target.value }));
            }}
          >
            <option value="">{pt ? 'Todos os regimes' : 'All regimes'}</option>
            <option value="laminar">laminar</option>
            <option value="turbulent">turbulent</option>
          </select>

          <input
            type="date"
            className="history-date-input"
            value={simFilters.created_from}
            onChange={(e) => {
              setSimPage(1);
              setSimFilters((prev) => ({ ...prev, created_from: e.target.value }));
            }}
          />
          <input
            type="date"
            className="history-date-input"
            value={simFilters.created_to}
            onChange={(e) => {
              setSimPage(1);
              setSimFilters((prev) => ({ ...prev, created_to: e.target.value }));
            }}
          />

          <button
            type="button"
            className="history-clear-btn"
            onClick={() => {
              setSimPage(1);
              setSimFilters({
                search: '',
                status: '',
                regime: '',
                created_from: '',
                created_to: '',
              });
            }}
          >
            {pt ? 'Limpar filtros' : 'Clear filters'}
          </button>
        </div>

        {!loading && simTotal === 0 ? (
          <div className="sim-history-empty">
            <p>{pt ? 'Nenhuma simulação encontrada com os filtros atuais' : 'No simulations found for current filters'}</p>
          </div>
        ) : (
          <>
            <div className="casos-grid">
              {simulations.map((simulation) => (
                <div key={simulation.id} className="caso-card">
                  <div className="caso-header">
                    <h3>{simulation.name}</h3>
                    <span className={`status-badge ${getSimStatusBadgeClass(simulation.status)}`}>
                      {getStatusText(simulation.status)}
                    </span>
                  </div>
                  <div className="caso-info">
                    <div className="info-row">
                      <span className="info-label">id:</span>
                      <span>{simulation.id}</span>
                    </div>
                    <div className="info-row">
                      <span className="info-label">{pt ? 'criado:' : 'created:'}</span>
                      <span>{simulation.createdDate}</span>
                    </div>
                    <div className="info-row">
                      <span className="info-label">{pt ? 'duração:' : 'duration:'}</span>
                      <span>{simulation.duration}</span>
                    </div>
                    {simulation.status === 'running' ? (
                      <div className="info-row">
                        <span className="info-label">{pt ? 'progresso:' : 'progress:'}</span>
                        <span>{simulation.progress}%</span>
                      </div>
                    ) : null}
                  </div>
                  {simulation.description ? (
                    <div className="caso-caminho">
                      <strong>{pt ? 'descrição:' : 'description:'}</strong>
                      <code>{simulation.description}</code>
                    </div>
                  ) : null}
                  <div className="caso-acoes">
                    <button
                      type="button"
                      className="btn-mode-option"
                      onClick={() => handleViewSimulation(simulation.id)}
                      disabled={actionBusyId === simulation.id}
                    >
                      <ThemeIcon light="viewLight-removebg-preview.png" dark="viewDark-removebg-preview.png" alt="" className="btn-icon" />
                      {pt ? 'visualizar' : 'view'}
                    </button>
                    <button
                      type="button"
                      className="btn-mode-option"
                      onClick={() => handleDownloadResults(simulation.id)}
                      disabled={actionBusyId === simulation.id}
                    >
                      <ThemeIcon light="downloadLight-removebg-preview.png" dark="donwloadDark-removebg-preview.png" alt="" className="btn-icon" />
                      {pt ? 'baixar' : 'download'}
                    </button>
                    <button
                      type="button"
                      className="btn-mode-option"
                      onClick={() => handleDeleteSimulation(simulation.id)}
                      disabled={actionBusyId === simulation.id}
                    >
                      <ThemeIcon light="cancelLight.png" dark="cancelDark.png" alt="" className="btn-icon" />
                      {pt ? 'deletar' : 'delete'}
                    </button>
                    <button
                      type="button"
                      className="btn-mode-option"
                      onClick={() => handleRerunSimulation(simulation.id)}
                      disabled={actionBusyId === simulation.id}
                    >
                      <ThemeIcon light="runLight.png" dark="runDark.png" alt="" className="btn-icon" />
                      {pt ? 'reexecutar' : 'rerun'}
                    </button>
                  </div>
                </div>
              ))}
            </div>

            <PaginationControls
              page={simPage}
              totalPages={simTotalPages}
              total={simTotal}
              limit={simLimit}
              loading={loading || simsRefreshing}
              onPageChange={setSimPage}
              onLimitChange={(value) => {
                setSimPage(1);
                setSimLimit(value);
              }}
              label={pt ? 'Histórico de simulações' : 'Simulation history'}
              pt={pt}
            />
          </>
        )}
      </section>

      <section className="results-section history-panel" aria-labelledby="history-models-heading">
        <div className="results-section-heading">
          <div className="results-section-title">
            <h3 id="history-models-heading" className="history-section-heading">
              <ThemeIcon
                light="modelLight-removebg-preview.png"
                dark="modelDark-removebg-preview.png"
                alt=""
                className="results-section-icon"
              />
              <span>
                {pt ? 'Modelos 3D' : '3D models'} ({modelTotal})
              </span>
            </h3>
          </div>
          <div className="results-section-toolbar">
            <button
              type="button"
              className="mesh-viewer-hub-btn mesh-viewer-hub-btn--compact"
              onClick={() => void loadModels()}
              disabled={modelsRefreshing || loading}
              aria-busy={modelsRefreshing || undefined}
            >
              <IconRefresh className="mesh-viewer-hub-btn__icon" aria-hidden />
              {modelsRefreshing ? '…' : pt ? 'atualizar' : 'refresh'}
            </button>
          </div>
        </div>

        <div className="history-filter-grid">
          <div className="search-container">
            <ThemeIcon light="triangle_white_outline.png" dark="triangle_black_outline.png" alt="buscar" className="search-icon" />
            <input
              type="text"
              placeholder={pt ? 'Buscar modelo por nome ou descrição…' : 'Search model by name or description…'}
              value={modelFilters.search}
              onChange={(e) => {
                setModelPage(1);
                setModelFilters((prev) => ({ ...prev, search: e.target.value }));
              }}
              className="search-input"
            />
          </div>

          <select
            className="history-select"
            value={modelFilters.packing_method}
            onChange={(e) => {
              setModelPage(1);
              setModelFilters((prev) => ({ ...prev, packing_method: e.target.value }));
            }}
          >
            <option value="">{pt ? 'Todos os métodos' : 'All methods'}</option>
            <option value="spherical_packing">spherical_packing</option>
            <option value="hexagonal_3d">hexagonal_3d</option>
            <option value="rigid_body">rigid_body</option>
          </select>

          <select
            className="history-select"
            value={modelFilters.has_blend}
            onChange={(e) => {
              setModelPage(1);
              setModelFilters((prev) => ({ ...prev, has_blend: e.target.value }));
            }}
          >
            <option value="">{pt ? 'Blend: qualquer' : 'Blend: any'}</option>
            <option value="true">{pt ? 'Com .blend' : 'With .blend'}</option>
            <option value="false">{pt ? 'Sem .blend' : 'Without .blend'}</option>
          </select>

          <select
            className="history-select"
            value={modelFilters.has_stl}
            onChange={(e) => {
              setModelPage(1);
              setModelFilters((prev) => ({ ...prev, has_stl: e.target.value }));
            }}
          >
            <option value="">{pt ? 'Stl: qualquer' : 'Stl: any'}</option>
            <option value="true">{pt ? 'Com .stl' : 'With .stl'}</option>
            <option value="false">{pt ? 'Sem .stl' : 'Without .stl'}</option>
          </select>

          <input
            type="date"
            className="history-date-input"
            value={modelFilters.created_from}
            onChange={(e) => {
              setModelPage(1);
              setModelFilters((prev) => ({ ...prev, created_from: e.target.value }));
            }}
          />
          <input
            type="date"
            className="history-date-input"
            value={modelFilters.created_to}
            onChange={(e) => {
              setModelPage(1);
              setModelFilters((prev) => ({ ...prev, created_to: e.target.value }));
            }}
          />

          <button
            type="button"
            className="history-clear-btn"
            onClick={() => {
              setModelPage(1);
              setModelFilters({
                search: '',
                packing_method: '',
                has_blend: '',
                has_stl: '',
                created_from: '',
                created_to: '',
              });
            }}
          >
            {pt ? 'Limpar filtros' : 'Clear filters'}
          </button>
        </div>

        {!loading && modelTotal === 0 ? (
          <div className="sim-history-empty">
            <p>{pt ? 'Nenhum modelo 3D encontrado com os filtros atuais' : 'No 3d models found for current filters'}</p>
          </div>
        ) : (
          <>
            <div className="casos-grid">
              {models3d.map((model) => (
                <div key={`model-${model.id}`} className="caso-card">
                  <div className="caso-header">
                    <h3>{model.name}</h3>
                    <span className="status-badge status-configured">{pt ? 'modelo 3d' : '3d model'}</span>
                  </div>
                  <div className="caso-info">
                    <div className="info-row">
                      <span className="info-label">id:</span>
                      <span>{model.id}</span>
                    </div>
                    <div className="info-row">
                      <span className="info-label">{pt ? 'criado:' : 'created:'}</span>
                      <span>
                        {model.created_at
                          ? new Date(model.created_at).toLocaleString(pt ? 'pt-BR' : 'en-US')
                          : '—'}
                      </span>
                    </div>
                    <div className="info-row">
                      <span className="info-label">{pt ? 'método:' : 'method:'}</span>
                      <span>{model.packing_method || '—'}</span>
                    </div>
                    <div className="info-row">
                      <span className="info-label">{pt ? 'tamanho:' : 'size:'}</span>
                      <span>{formatBytes(model.size_bytes)}</span>
                    </div>
                    <div className="info-row">
                      <span className="info-label">{pt ? 'ficheiros:' : 'files:'}</span>
                      <span>
                        {model.blend_file_path ? '.blend ' : ''}
                        {model.stl_file_path ? '.stl' : '—'}
                      </span>
                    </div>
                  </div>
                  {model.description && (
                    <div className="caso-caminho">
                      <strong>{pt ? 'caminho:' : 'path:'}</strong>
                      <code title={model.description}>{model.description}</code>
                    </div>
                  )}
                  <div className="caso-acoes">
                    <button
                      type="button"
                      className="btn-mode-option"
                      onClick={() => {
                        const url = model.mesh_id
                          ? buildMeshStreamUrl(model.mesh_id)
                          : buildGeneratedFileUrl(model.blend_file_path || model.stl_file_path);
                        if (url) window.open(url, '_blank');
                      }}
                      disabled={!model.mesh_id && !buildGeneratedFileUrl(model.blend_file_path || model.stl_file_path)}
                    >
                      <ThemeIcon light="viewLight-removebg-preview.png" dark="viewDark-removebg-preview.png" alt="" className="btn-icon" />
                      {pt ? 'abrir' : 'open'}
                    </button>
                    <button
                      type="button"
                      className="btn-mode-option"
                      onClick={() => {
                        const url = buildGeneratedFileUrl(model.blend_file_path || model.stl_file_path);
                        if (url) window.open(url, '_blank');
                      }}
                      disabled={!buildGeneratedFileUrl(model.blend_file_path || model.stl_file_path)}
                    >
                      <ThemeIcon light="downloadLight-removebg-preview.png" dark="donwloadDark-removebg-preview.png" alt="" className="btn-icon" />
                      {pt ? 'baixar' : 'download'}
                    </button>
                  </div>
                </div>
              ))}
            </div>

            <PaginationControls
              page={modelPage}
              totalPages={modelTotalPages}
              total={modelTotal}
              limit={modelLimit}
              loading={loading || modelsRefreshing}
              onPageChange={setModelPage}
              onLimitChange={(value) => {
                setModelPage(1);
                setModelLimit(value);
              }}
              label={pt ? 'Modelos 3D' : '3D models'}
              pt={pt}
            />
          </>
        )}
      </section>
      </div>

      {viewModalId != null && (
        <div
          className="history-modal-overlay"
          role="dialog"
          aria-modal="true"
          aria-label={pt ? 'Detalhes da simulação' : 'Simulation details'}
          onClick={closeViewModal}
        >
          <div className="history-modal" onClick={(e) => e.stopPropagation()}>
            <div className="history-modal-header">
              <h2>
                {pt ? 'Detalhes da simulação' : 'Simulation details'}
                {viewDetail ? ` · #${viewDetail.id}` : ''}
              </h2>
              <button
                type="button"
                className="history-modal-close"
                onClick={closeViewModal}
                aria-label={pt ? 'Fechar' : 'Close'}
              >
                ×
              </button>
            </div>
            <div className="history-modal-body">
              {viewLoading && (
                <div className="history-modal-loading">
                  {pt ? 'Carregando…' : 'Loading…'}
                </div>
              )}
              {!viewLoading && viewDetail && (
                <div className="history-detail-grid">
                  <div className="history-detail-row">
                    <span className="history-detail-label">{pt ? 'Nome' : 'Name'}</span>
                    <span className="history-detail-value">{viewDetail.name || '—'}</span>
                  </div>
                  <div className="history-detail-row">
                    <span className="history-detail-label">{pt ? 'Estado' : 'Status'}</span>
                    <span className="history-detail-value">{getStatusText(viewDetail.status)}</span>
                  </div>
                  <div className="history-detail-row">
                    <span className="history-detail-label">{pt ? 'Leito' : 'Bed'}</span>
                    <span className="history-detail-value">#{viewDetail.bed_id}</span>
                  </div>
                  <div className="history-detail-row">
                    <span className="history-detail-label">{pt ? 'Regime' : 'Regime'}</span>
                    <span className="history-detail-value">{viewDetail.regime || '—'}</span>
                  </div>
                  <div className="history-detail-row">
                    <span className="history-detail-label">{pt ? 'Solver' : 'Solver'}</span>
                    <span className="history-detail-value">{viewDetail.solver || '—'}</span>
                  </div>
                  <div className="history-detail-row">
                    <span className="history-detail-label">{pt ? 'Velocidade de entrada' : 'Inlet velocity'}</span>
                    <span className="history-detail-value">{viewDetail.inlet_velocity} m/s</span>
                  </div>
                  <div className="history-detail-row">
                    <span className="history-detail-label">{pt ? 'Densidade' : 'Density'}</span>
                    <span className="history-detail-value">{viewDetail.fluid_density} kg/m³</span>
                  </div>
                  <div className="history-detail-row">
                    <span className="history-detail-label">{pt ? 'Viscosidade' : 'Viscosity'}</span>
                    <span className="history-detail-value">{viewDetail.fluid_viscosity} Pa·s</span>
                  </div>
                  <div className="history-detail-row">
                    <span className="history-detail-label">{pt ? 'Iterações máx.' : 'Max iterations'}</span>
                    <span className="history-detail-value">{viewDetail.max_iterations ?? '—'}</span>
                  </div>
                  <div className="history-detail-row">
                    <span className="history-detail-label">{pt ? 'Critério convergência' : 'Convergence criteria'}</span>
                    <span className="history-detail-value">{viewDetail.convergence_criteria ?? '—'}</span>
                  </div>
                  <div className="history-detail-row">
                    <span className="history-detail-label">{pt ? 'Progresso' : 'Progress'}</span>
                    <span className="history-detail-value">{viewDetail.progress ?? 0}%</span>
                  </div>
                  <div className="history-detail-row">
                    <span className="history-detail-label">{pt ? 'Queda de pressão' : 'Pressure drop'}</span>
                    <span className="history-detail-value">
                      {viewDetail.pressure_drop != null ? `${viewDetail.pressure_drop} Pa` : '—'}
                    </span>
                  </div>
                  <div className="history-detail-row">
                    <span className="history-detail-label">{pt ? 'Velocidade média' : 'Average velocity'}</span>
                    <span className="history-detail-value">
                      {viewDetail.average_velocity != null ? `${viewDetail.average_velocity} m/s` : '—'}
                    </span>
                  </div>
                  <div className="history-detail-row">
                    <span className="history-detail-label">{pt ? 'Número de Reynolds' : 'Reynolds number'}</span>
                    <span className="history-detail-value">{viewDetail.reynolds_number ?? '—'}</span>
                  </div>
                  <div className="history-detail-row">
                    <span className="history-detail-label">{pt ? 'Células de malha' : 'Mesh cells'}</span>
                    <span className="history-detail-value">{viewDetail.mesh_cells_count ?? '—'}</span>
                  </div>
                  <div className="history-detail-row">
                    <span className="history-detail-label">{pt ? 'Qualidade da malha' : 'Mesh quality'}</span>
                    <span className="history-detail-value">{viewDetail.mesh_quality ?? '—'}</span>
                  </div>
                  <div className="history-detail-row">
                    <span className="history-detail-label">{pt ? 'Duração' : 'Execution time'}</span>
                    <span className="history-detail-value">
                      {formatDurationSeconds(viewDetail.execution_time, language)}
                    </span>
                  </div>
                  <div className="history-detail-row">
                    <span className="history-detail-label">{pt ? 'Criado em' : 'Created at'}</span>
                    <span className="history-detail-value">
                      {viewDetail.created_at
                        ? new Date(viewDetail.created_at).toLocaleString(pt ? 'pt-BR' : 'en-US')
                        : '—'}
                    </span>
                  </div>
                  <div className="history-detail-row">
                    <span className="history-detail-label">{pt ? 'Iniciado em' : 'Started at'}</span>
                    <span className="history-detail-value">
                      {viewDetail.started_at
                        ? new Date(viewDetail.started_at).toLocaleString(pt ? 'pt-BR' : 'en-US')
                        : '—'}
                    </span>
                  </div>
                  <div className="history-detail-row">
                    <span className="history-detail-label">{pt ? 'Concluído em' : 'Completed at'}</span>
                    <span className="history-detail-value">
                      {viewDetail.completed_at
                        ? new Date(viewDetail.completed_at).toLocaleString(pt ? 'pt-BR' : 'en-US')
                        : '—'}
                    </span>
                  </div>
                  {viewDetail.description ? (
                    <div className="history-detail-row history-detail-row-wide">
                      <span className="history-detail-label">{pt ? 'Descrição' : 'Description'}</span>
                      <span className="history-detail-value">{viewDetail.description}</span>
                    </div>
                  ) : null}
                  {viewDetail.case_directory ? (
                    <div className="history-detail-row history-detail-row-wide">
                      <span className="history-detail-label">{pt ? 'Diretório do caso' : 'Case directory'}</span>
                      <code className="history-detail-code">{viewDetail.case_directory}</code>
                    </div>
                  ) : null}
                  {viewDetail.log_file_path ? (
                    <div className="history-detail-row history-detail-row-wide">
                      <span className="history-detail-label">{pt ? 'Arquivo de log' : 'Log file'}</span>
                      <code className="history-detail-code">{viewDetail.log_file_path}</code>
                    </div>
                  ) : null}
                  {viewDetail.parameters_json ? (
                    <div className="history-detail-row history-detail-row-wide">
                      <span className="history-detail-label">{pt ? 'Parâmetros' : 'Parameters'}</span>
                      <pre className="history-detail-json">
                        {JSON.stringify(viewDetail.parameters_json, null, 2)}
                      </pre>
                    </div>
                  ) : null}
                </div>
              )}
            </div>
            <div className="history-modal-footer">
              <button
                type="button"
                className="history-modal-btn"
                onClick={() => viewDetail && handleDownloadResults(viewDetail.id)}
                disabled={!viewDetail || actionBusyId === viewDetail?.id}
              >
                {pt ? 'Baixar json' : 'Download json'}
              </button>
              <button type="button" className="history-modal-btn primary" onClick={closeViewModal}>
                {pt ? 'Fechar' : 'Close'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default SimulationHistory;
