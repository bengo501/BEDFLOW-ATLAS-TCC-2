import { useState, useEffect, useCallback } from 'react'
import {
  listSimulations,
  getSimulation,
  getSimulationResults,
  deleteSimulation,
  createSimulationRecord,
} from '../../services/api'
import { useLanguage } from '../../context/LanguageContext'
import { useActiveUser } from '../../context/UserContext'
import ThemeIcon from '../ThemeIcon'
import '../../styles/CasosCFD.css'
import '../../styles/MeshViewer3DPage.css'
import '../SimulationHistory.css'
import '../PaginationControls.css'
import {
  IconRefresh,
  isConnectionError,
  mapApiSimulation,
  getSimStatusBadgeClass,
  getStatusText,
  slugify,
} from './resultsShared'
import SimulationDetailModal from './SimulationDetailModal'

function pageWindow(current, total, size = 5) {
  const start = Math.max(1, current - Math.floor(size / 2))
  const end = Math.min(total, start + size - 1)
  const adjustedStart = Math.max(1, end - size + 1)
  const pages = []
  for (let p = adjustedStart; p <= end; p += 1) {
    pages.push(p)
  }
  return pages
}

function SimPagination({
  page,
  totalPages,
  total,
  limit,
  loading,
  onPageChange,
  onLimitChange,
  label,
  pt,
}) {
  const pages = pageWindow(page, totalPages)
  const limitOptions = [8, 12, 20, 50]

  return (
    <div className="pagination-controls">
      <div className="pagination-summary">
        {label ? <span>{label} · </span> : null}
        <span>
          {pt ? 'total filtrado' : 'filtered total'}: {total}
        </span>
        <span>
          {pt ? 'página' : 'page'} {page} / {totalPages}
        </span>
      </div>

      <div className="pagination-actions">
        {onLimitChange ? (
          <label className="pagination-limit">
            <span>{pt ? 'itens' : 'items'}</span>
            <select
              value={limit}
              onChange={(e) => onLimitChange(Number(e.target.value))}
              disabled={loading}
            >
              {limitOptions.map((option) => (
                <option key={option} value={option}>
                  {option}
                </option>
              ))}
            </select>
          </label>
        ) : null}

        <button
          type="button"
          onClick={() => onPageChange?.(Math.max(1, page - 1))}
          disabled={loading || page <= 1}
        >
          {pt ? 'anterior' : 'previous'}
        </button>

        <div className="pagination-pages">
          {pages.map((pageNumber) => (
            <button
              key={pageNumber}
              type="button"
              className={pageNumber === page ? 'active' : ''}
              onClick={() => onPageChange?.(pageNumber)}
              disabled={loading}
            >
              {pageNumber}
            </button>
          ))}
        </div>

        <button
          type="button"
          onClick={() => onPageChange?.(Math.min(totalPages, page + 1))}
          disabled={loading || page >= totalPages}
        >
          {pt ? 'próxima' : 'next'}
        </button>
      </div>
    </div>
  )
}

export default function ResultsSimulationsPage() {
  const { language, t } = useLanguage()
  const { activeUserId } = useActiveUser()
  const pt = language === 'pt'

  const [simulations, setSimulations] = useState([])
  const [simPage, setSimPage] = useState(1)
  const [simLimit, setSimLimit] = useState(8)
  const [simTotal, setSimTotal] = useState(0)
  const [simTotalPages, setSimTotalPages] = useState(1)
  const [simFilters, setSimFilters] = useState({
    search: '',
    status: '',
    regime: '',
    created_from: '',
    created_to: '',
  })
  const [loading, setLoading] = useState(true)
  const [simsRefreshing, setSimsRefreshing] = useState(false)
  const [loadError, setLoadError] = useState(null)
  const [opError, setOpError] = useState(null)
  const [opSuccess, setOpSuccess] = useState(null)
  const [actionBusyId, setActionBusyId] = useState(null)
  const [viewModalId, setViewModalId] = useState(null)
  const [viewDetail, setViewDetail] = useState(null)
  const [viewLoading, setViewLoading] = useState(false)
  const [selectedSimulation, setSelectedSimulation] = useState(null)
  const [selectedSimulationResults, setSelectedSimulationResults] = useState([])
  const [simulationResultsLoading, setSimulationResultsLoading] = useState(false)
  const [simulationResultsMeta, setSimulationResultsMeta] = useState({
    page: 1,
    limit: 12,
    total: 0,
    total_pages: 1,
  })
  const [simulationResultsFilter, setSimulationResultsFilter] = useState({
    resultType: '',
    search: '',
  })

  const loadSimulations = useCallback(
    async ({ silent = false } = {}) => {
      if (!silent) setSimsRefreshing(true)
      setLoadError(null)
      try {
        const simData = await listSimulations({
          page: simPage,
          limit: simLimit,
          search: simFilters.search,
          status: simFilters.status || null,
          regime: simFilters.regime || null,
          created_from: simFilters.created_from || null,
          created_to: simFilters.created_to || null,
        })
        const simItems = Array.isArray(simData?.items) ? simData.items : []
        setSimulations(simItems.map((row) => mapApiSimulation(row, language)))
        setSimTotal(simData?.total || 0)
        setSimTotalPages(simData?.total_pages || simData?.pages || 1)
      } catch (err) {
        console.error('results simulations:', err)
        if (isConnectionError(err)) {
          setLoadError(t('backendConnectionError'))
        } else {
          const detail = err.response?.data?.detail
          setLoadError(
            typeof detail === 'string'
              ? detail
              : pt
                ? 'erro ao carregar simulações'
                : 'failed to load simulations'
          )
        }
        setSimulations([])
        setSimTotal(0)
      } finally {
        if (!silent) setSimsRefreshing(false)
      }
    },
    [language, simFilters, simLimit, simPage, pt, t]
  )

  const refreshAll = useCallback(
    async ({ silent = false } = {}) => {
      if (!silent) setLoading(true)
      await loadSimulations({ silent: true })
      if (!silent) setLoading(false)
    },
    [loadSimulations]
  )

  useEffect(() => {
    refreshAll()
    const timer = window.setInterval(() => refreshAll({ silent: true }), 5000)
    return () => window.clearInterval(timer)
  }, [activeUserId, refreshAll])

  const flashSuccess = useCallback((msg) => {
    setOpSuccess(msg)
    window.setTimeout(() => setOpSuccess(null), 2500)
  }, [])

  const closeViewModal = useCallback(() => {
    setViewModalId(null)
    setViewDetail(null)
    setViewLoading(false)
  }, [])

  useEffect(() => {
    if (viewModalId == null) return
    const onKey = (e) => {
      if (e.key === 'Escape') closeViewModal()
    }
    window.addEventListener('keydown', onKey)
    return () => window.removeEventListener('keydown', onKey)
  }, [viewModalId, closeViewModal])

  const handleViewSimulation = async (id) => {
    setOpError(null)
    setViewModalId(id)
    setViewLoading(true)
    setViewDetail(null)
    try {
      const data = await getSimulation(id)
      setViewDetail(data)
    } catch (err) {
      console.error('erro ao obter simulacao:', err)
      if (isConnectionError(err)) setOpError(t('backendConnectionError'))
      else {
        setOpError(
          err.response?.data?.detail ||
            (pt ? 'falha ao carregar detalhes' : 'failed to load details')
        )
      }
      closeViewModal()
    } finally {
      setViewLoading(false)
    }
  }

  const handleDownloadResults = async (id) => {
    setOpError(null)
    setActionBusyId(id)
    try {
      const data = await getSimulation(id)
      const filename = `simulacao_${data.id}_${slugify(data.name)}.json`
      const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' })
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = filename
      document.body.appendChild(a)
      a.click()
      document.body.removeChild(a)
      window.setTimeout(() => URL.revokeObjectURL(url), 1000)
      flashSuccess(pt ? 'dados baixados' : 'data downloaded')
    } catch (err) {
      console.error('erro ao baixar:', err)
      if (isConnectionError(err)) setOpError(t('backendConnectionError'))
      else {
        setOpError(err.response?.data?.detail || (pt ? 'falha ao baixar' : 'download failed'))
      }
    } finally {
      setActionBusyId(null)
    }
  }

  const handleDeleteSimulation = async (id) => {
    setOpError(null)
    const ok = window.confirm(
      pt
        ? `eliminar a simulação #${id} e todos os seus resultados? esta ação é irreversível.`
        : `delete simulation #${id} and all its results? this action cannot be undone.`
    )
    if (!ok) return
    setActionBusyId(id)
    try {
      await deleteSimulation(id)
      flashSuccess(pt ? 'simulação eliminada' : 'simulation deleted')
      await refreshAll({ silent: true })
    } catch (err) {
      console.error('erro ao deletar:', err)
      if (isConnectionError(err)) setOpError(t('backendConnectionError'))
      else {
        setOpError(err.response?.data?.detail || (pt ? 'falha ao eliminar' : 'delete failed'))
      }
    } finally {
      setActionBusyId(null)
    }
  }

  const handleRerunSimulation = async (id) => {
    setOpError(null)
    const ok = window.confirm(
      pt
        ? `duplicar os parâmetros da simulação #${id} e criar uma nova execução?`
        : `clone parameters of simulation #${id} and create a new run?`
    )
    if (!ok) return
    setActionBusyId(id)
    try {
      const src = await getSimulation(id)
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
      }
      const created = await createSimulationRecord(payload)
      flashSuccess(
        pt ? `nova simulação criada #${created.id}` : `new simulation created #${created.id}`
      )
      await refreshAll({ silent: true })
    } catch (err) {
      console.error('erro ao reexecutar:', err)
      if (isConnectionError(err)) setOpError(t('backendConnectionError'))
      else {
        setOpError(err.response?.data?.detail || (pt ? 'falha ao reexecutar' : 'rerun failed'))
      }
    } finally {
      setActionBusyId(null)
    }
  }

  const handleOpenSimulationResults = async (
    simulationId,
    options = {
      page: simulationResultsMeta.page,
      limit: simulationResultsMeta.limit,
      resultType: simulationResultsFilter.resultType,
      search: simulationResultsFilter.search,
    }
  ) => {
    setOpError(null)
    try {
      setSimulationResultsLoading(true)
      const [sim, results] = await Promise.all([
        getSimulation(simulationId),
        getSimulationResults(simulationId, options),
      ])
      setSelectedSimulation(sim)
      setSelectedSimulationResults(Array.isArray(results?.items) ? results.items : [])
      setSimulationResultsMeta({
        page: results?.page || options.page || 1,
        limit: results?.limit || options.limit || 12,
        total: results?.total || 0,
        total_pages: results?.total_pages || results?.pages || 1,
      })
    } catch (err) {
      console.error('erro ao carregar resultados da simulação:', err)
      if (isConnectionError(err)) setOpError(t('backendConnectionError'))
      else {
        setOpError(
          err.response?.data?.detail ||
            (pt ? 'falha ao carregar resultados' : 'failed to load results')
        )
      }
    } finally {
      setSimulationResultsLoading(false)
    }
  }

  const closeResultsModal = () => {
    setSelectedSimulation(null)
    setSelectedSimulationResults([])
    setSimulationResultsFilter({ resultType: '', search: '' })
    setSimulationResultsMeta({ page: 1, limit: 12, total: 0, total_pages: 1 })
  }

  return (
    <div className="results-container">
      <header className="results-page-header">
        <div className="results-page-title">
          <img
            src="/image/cfd_gear_white.png"
            alt=""
            className="results-section-icon"
            width={26}
            height={26}
          />
          <h1 className="results-page-heading">{pt ? 'simulações' : 'simulations'}</h1>
        </div>
      </header>

      {loadError && (
        <div className="history-op-error" role="alert">
          {loadError}
        </div>
      )}

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

      <div className="results-layout">
        <section className="results-section">
          <div className="results-section-heading">
            <div className="results-section-title">
              <h3>
                <img
                  src="/image/cfd_gear_white.png"
                  alt=""
                  className="results-section-icon"
                  width={22}
                  height={22}
                />
                {pt ? 'simulações' : 'simulations'} ({simTotal})
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
              <input
                type="text"
                placeholder={
                  pt ? 'buscar por nome, descrição ou id…' : 'search by name, description or id…'
                }
                value={simFilters.search}
                onChange={(e) => {
                  setSimPage(1)
                  setSimFilters((prev) => ({ ...prev, search: e.target.value }))
                }}
                className="search-input"
              />
            </div>

            <select
              className="history-select"
              value={simFilters.status}
              onChange={(e) => {
                setSimPage(1)
                setSimFilters((prev) => ({ ...prev, status: e.target.value }))
              }}
            >
              <option value="">{pt ? 'todos os estados' : 'all statuses'}</option>
              <option value="completed">{pt ? 'concluída' : 'completed'}</option>
              <option value="running">{pt ? 'em execução' : 'running'}</option>
              <option value="pending">{pt ? 'pendente' : 'pending'}</option>
              <option value="failed">{pt ? 'falhou' : 'failed'}</option>
            </select>

            <select
              className="history-select"
              value={simFilters.regime}
              onChange={(e) => {
                setSimPage(1)
                setSimFilters((prev) => ({ ...prev, regime: e.target.value }))
              }}
            >
              <option value="">{pt ? 'todos os regimes' : 'all regimes'}</option>
              <option value="laminar">laminar</option>
              <option value="turbulent">turbulent</option>
            </select>

            <input
              type="date"
              className="history-date-input"
              value={simFilters.created_from}
              onChange={(e) => {
                setSimPage(1)
                setSimFilters((prev) => ({ ...prev, created_from: e.target.value }))
              }}
            />
            <input
              type="date"
              className="history-date-input"
              value={simFilters.created_to}
              onChange={(e) => {
                setSimPage(1)
                setSimFilters((prev) => ({ ...prev, created_to: e.target.value }))
              }}
            />

            <button
              type="button"
              className="history-clear-btn"
              onClick={() => {
                setSimPage(1)
                setSimFilters({
                  search: '',
                  status: '',
                  regime: '',
                  created_from: '',
                  created_to: '',
                })
              }}
            >
              {pt ? 'limpar filtros' : 'clear filters'}
            </button>
          </div>

          {loading ? (
            <p>{pt ? 'carregando…' : 'loading…'}</p>
          ) : simTotal === 0 ? (
            <p className="empty-state">
              {pt ? 'nenhuma simulação encontrada' : 'no simulations found'}
            </p>
          ) : (
            <>
              <div className="casos-grid">
                {simulations.map((simulation) => (
                  <div key={simulation.id} className="caso-card">
                    <div className="caso-header">
                      <h3>{simulation.name}</h3>
                      <span
                        className={`status-badge ${getSimStatusBadgeClass(simulation.status)}`}
                      >
                        {getStatusText(simulation.status, language)}
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
                      {simulation.regime ? (
                        <div className="info-row">
                          <span className="info-label">{pt ? 'regime:' : 'regime:'}</span>
                          <span>{simulation.raw?.regime || simulation.regime || '—'}</span>
                        </div>
                      ) : null}
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
                        <ThemeIcon light="docsLight.png" dark="docsLight.png" alt="" className="btn-icon" />
                        {pt ? 'visualizar' : 'view'}
                      </button>
                      <button
                        type="button"
                        className="btn-mode-option"
                        onClick={() => {
                          setSimulationResultsFilter({ resultType: '', search: '' })
                          setSimulationResultsMeta({ page: 1, limit: 12, total: 0, total_pages: 1 })
                          handleOpenSimulationResults(simulation.id, { page: 1, limit: 12 })
                        }}
                        disabled={actionBusyId === simulation.id}
                      >
                        <ThemeIcon light="folderLight.png" dark="folderLight.png" alt="" className="btn-icon" />
                        {pt ? 'resultados' : 'results'}
                      </button>
                      <button
                        type="button"
                        className="btn-mode-option"
                        onClick={() => handleDownloadResults(simulation.id)}
                        disabled={actionBusyId === simulation.id}
                      >
                        <ThemeIcon light="downloadLight-removebg-preview.png" dark="donwloadDark-removebg-preview.png" alt="" className="btn-icon" />
                        json
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

              <SimPagination
                page={simPage}
                totalPages={simTotalPages}
                total={simTotal}
                limit={simLimit}
                loading={loading || simsRefreshing}
                onPageChange={setSimPage}
                onLimitChange={(value) => {
                  setSimPage(1)
                  setSimLimit(value)
                }}
                label={pt ? 'simulações' : 'simulations'}
                pt={pt}
              />
            </>
          )}
        </section>
      </div>

      <SimulationDetailModal
        pt={pt}
        language={language}
        viewModalId={viewModalId}
        viewDetail={viewDetail}
        viewLoading={viewLoading}
        actionBusyId={actionBusyId}
        onClose={closeViewModal}
        onDownload={handleDownloadResults}
      />

      {selectedSimulation && (
        <div className="modal-overlay" onClick={closeResultsModal}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <button type="button" className="modal-close" onClick={closeResultsModal}>
              ×
            </button>

            <h3>
              {pt ? 'resultados da simulação' : 'simulation results'}: {selectedSimulation.name}
            </h3>

            {simulationResultsLoading ? (
              <p>{pt ? 'carregando…' : 'loading…'}</p>
            ) : selectedSimulationResults.length === 0 ? (
              <p>
                {pt
                  ? 'nenhum resultado persistido para esta simulação'
                  : 'no persisted results for this simulation'}
              </p>
            ) : (
              <>
                <div className="results-filters">
                  <input
                    type="search"
                    className="search-input"
                    placeholder={pt ? 'buscar resultado…' : 'search result…'}
                    value={simulationResultsFilter.search}
                    onChange={(e) =>
                      setSimulationResultsFilter((prev) => ({
                        ...prev,
                        search: e.target.value,
                      }))
                    }
                  />
                  <select
                    className="search-input"
                    value={simulationResultsFilter.resultType}
                    onChange={(e) =>
                      setSimulationResultsFilter((prev) => ({
                        ...prev,
                        resultType: e.target.value,
                      }))
                    }
                  >
                    <option value="">{pt ? 'todos os tipos' : 'all types'}</option>
                    <option value="field">field</option>
                    <option value="metric">metric</option>
                    <option value="validation">validation</option>
                    <option value="visualization">visualization</option>
                  </select>
                  <button
                    type="button"
                    className="btn-small"
                    onClick={() =>
                      handleOpenSimulationResults(selectedSimulation.id, {
                        page: 1,
                        limit: simulationResultsMeta.limit,
                        resultType: simulationResultsFilter.resultType || null,
                        search: simulationResultsFilter.search || null,
                      })
                    }
                  >
                    {pt ? 'aplicar filtros' : 'apply filters'}
                  </button>
                </div>
                <div className="files-grid">
                  {selectedSimulationResults.map((result) => (
                    <div key={result.id} className="file-card">
                      <div className="file-info">
                        <h4 className="file-name">{result.name}</h4>
                        <p className="file-size">{result.result_type}</p>
                        <p className="file-date">
                          {result.value != null
                            ? `${result.value} ${result.unit || ''}`.trim()
                            : pt
                              ? 'sem valor escalar'
                              : 'no scalar value'}
                        </p>
                        <p className="file-size">{result.file_type || 'json'}</p>
                      </div>
                    </div>
                  ))}
                </div>
                <SimPagination
                  page={simulationResultsMeta.page}
                  totalPages={simulationResultsMeta.total_pages}
                  total={simulationResultsMeta.total}
                  limit={simulationResultsMeta.limit}
                  loading={simulationResultsLoading}
                  onPageChange={(page) =>
                    handleOpenSimulationResults(selectedSimulation.id, {
                      page,
                      limit: simulationResultsMeta.limit,
                      resultType: simulationResultsFilter.resultType || null,
                      search: simulationResultsFilter.search || null,
                    })
                  }
                  onLimitChange={(value) =>
                    handleOpenSimulationResults(selectedSimulation.id, {
                      page: 1,
                      limit: value,
                      resultType: simulationResultsFilter.resultType || null,
                      search: simulationResultsFilter.search || null,
                    })
                  }
                  label={pt ? 'resultados persistidos' : 'persisted results'}
                  pt={pt}
                />
              </>
            )}
          </div>
        </div>
      )}
    </div>
  )
}
