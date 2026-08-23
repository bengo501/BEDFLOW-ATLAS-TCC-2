import { useState, useEffect, useCallback } from 'react'
import {
  listModels3D,
  listSimulations,
  getSimulation,
  getSimulationResults,
  buildGeneratedFileUrl,
  buildMeshStreamUrl,
  listViewerMeshes,
  mergeDbModelsWithProjectMeshes,
} from '../services/api'
import ModelViewer from './ModelViewer'
import ThemeIcon from './ThemeIcon'
import BackendConnectionError from './BackendConnectionError'
import PaginationControls from './PaginationControls'
import { useLanguage } from '../context/LanguageContext'
import { useActiveUser } from '../context/UserContext'
import '../styles/CasosCFD.css'
import '../styles/MeshViewer3DPage.css'

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
  )
}

function getSimStatusBadgeClass(status) {
  switch (status) {
    case 'completed':
      return 'status-completed'
    case 'running':
      return 'status-running'
    case 'pending':
      return 'status-configured'
    case 'failed':
      return 'status-unknown'
    default:
      return 'status-unknown'
  }
}

function formatBytes(bytes) {
  if (typeof bytes !== 'number' || bytes < 0) return '—'
  if (bytes < 1024) return `${bytes} B`
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`
}

function ResultsList() {
  const { t, language } = useLanguage()
  const { activeUserId } = useActiveUser()
  const [models, setModels] = useState([])
  const [simulations, setSimulations] = useState([])
  const [selectedModel, setSelectedModel] = useState(null)
  const [selectedSimulation, setSelectedSimulation] = useState(null)
  const [selectedSimulationResults, setSelectedSimulationResults] = useState([])
  const [simulationResultsLoading, setSimulationResultsLoading] = useState(false)
  const [simulationResultsMeta, setSimulationResultsMeta] = useState({ page: 1, limit: 12, total: 0, total_pages: 1 })
  const [simulationResultsFilter, setSimulationResultsFilter] = useState({ resultType: '', search: '' })
  const [loading, setLoading] = useState(false)
  const [modelsRefreshing, setModelsRefreshing] = useState(false)
  const [simsRefreshing, setSimsRefreshing] = useState(false)
  const [connectionError, setConnectionError] = useState(null)
  const pt = language === 'pt'
  const [modelPage, setModelPage] = useState(1)
  const [modelLimit, setModelLimit] = useState(8)
  const [modelTotal, setModelTotal] = useState(0)
  const [modelTotalPages, setModelTotalPages] = useState(1)
  const [modelFilters, setModelFilters] = useState({
    search: '',
    packing_method: '',
    has_blend: '',
    has_stl: '',
  })
  const [simPage, setSimPage] = useState(1)
  const [simLimit, setSimLimit] = useState(8)
  const [simTotal, setSimTotal] = useState(0)
  const [simTotalPages, setSimTotalPages] = useState(1)
  const [simFilters, setSimFilters] = useState({
    search: '',
    status: '',
    regime: '',
  })

  const loadModels = useCallback(async ({ silent = false } = {}) => {
    if (!silent) setModelsRefreshing(true)
    try {
      setConnectionError(null)
      const [modelsData, meshData] = await Promise.all([
        listModels3D({
          page: modelPage,
          limit: modelLimit,
          search: modelFilters.search,
          packing_method: modelFilters.packing_method || null,
          has_blend: modelFilters.has_blend === '' ? null : modelFilters.has_blend === 'true',
          has_stl: modelFilters.has_stl === '' ? null : modelFilters.has_stl === 'true',
        }),
        listViewerMeshes({ q: modelFilters.search || undefined, limit: 500 }),
      ])
      const dbItems = Array.isArray(modelsData?.items) ? modelsData.items : []
      const merged = mergeDbModelsWithProjectMeshes(dbItems, meshData)
      setModels(merged)
      const extra = merged.length - dbItems.length
      setModelTotal((modelsData?.total || 0) + extra)
      setModelTotalPages(modelsData?.total_pages || modelsData?.pages || 1)
    } catch (error) {
      console.error('erro ao carregar modelos:', error)
      setConnectionError(t('backendConnectionError'))
      setModels([])
    } finally {
      if (!silent) setModelsRefreshing(false)
    }
  }, [modelFilters, modelLimit, modelPage, t])

  const loadSimulations = useCallback(async ({ silent = false } = {}) => {
    if (!silent) setSimsRefreshing(true)
    try {
      setConnectionError(null)
      const simsData = await listSimulations({
        page: simPage,
        limit: simLimit,
        search: simFilters.search,
        status: simFilters.status || null,
        regime: simFilters.regime || null,
      })
      setSimulations(Array.isArray(simsData?.items) ? simsData.items : [])
      setSimTotal(simsData?.total || 0)
      setSimTotalPages(simsData?.total_pages || simsData?.pages || 1)
    } catch (error) {
      console.error('erro ao carregar simulações:', error)
      setConnectionError(t('backendConnectionError'))
      setSimulations([])
    } finally {
      if (!silent) setSimsRefreshing(false)
    }
  }, [simFilters, simLimit, simPage, t])

  const loadData = useCallback(async ({ silent = false } = {}) => {
    if (!silent) setLoading(true)
    await Promise.all([loadModels({ silent: true }), loadSimulations({ silent: true })])
    if (!silent) setLoading(false)
  }, [loadModels, loadSimulations])

  useEffect(() => {
    loadData()
    const timer = window.setInterval(loadData, 5000)
    return () => window.clearInterval(timer)
  }, [activeUserId, loadData])

  const handleOpenSimulationResults = async (
    simulationId,
    options = {
      page: simulationResultsMeta.page,
      limit: simulationResultsMeta.limit,
      resultType: simulationResultsFilter.resultType,
      search: simulationResultsFilter.search,
    }
  ) => {
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
    } catch (error) {
      console.error('erro ao carregar resultados da simulação:', error)
      setConnectionError(t('backendConnectionError'))
    } finally {
      setSimulationResultsLoading(false)
    }
  }

  const handleDownloadSimulationJson = async (simulationId) => {
    try {
      const data = await getSimulation(simulationId)
      const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' })
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `simulacao_${simulationId}.json`
      document.body.appendChild(a)
      a.click()
      document.body.removeChild(a)
      setTimeout(() => URL.revokeObjectURL(url), 1000)
    } catch (error) {
      console.error('erro ao baixar json da simulação:', error)
      setConnectionError(t('backendConnectionError'))
    }
  }

  const getModelPreviewPath = (model) => {
    if (model.mesh_id) return buildMeshStreamUrl(model.mesh_id)
    const fileRel = model.stl_file_path || model.blend_file_path
    if (fileRel && String(fileRel).toLowerCase().endsWith('.blend') && !model.stl_file_path) {
      return null
    }
    return model.preview_model_url
      ? buildGeneratedFileUrl(model.preview_model_url.replace(/^\/files\//, ''))
      : buildGeneratedFileUrl(model.stl_file_path || model.blend_file_path)
  }

  const getModelDownloadPath = (model) => {
    return buildGeneratedFileUrl(model.stl_file_path || model.blend_file_path)
  }

  return (
    <div className="results-container">
      <header className="results-page-header">
        <div className="results-page-title">
          <ThemeIcon light="folderLight.png" dark="folderDark.png" alt="" className="results-page-title-icon" />
          <h1 className="results-page-heading">{language === 'pt' ? 'Resultados' : 'Results'}</h1>
        </div>
      </header>

      {connectionError && <BackendConnectionError message={connectionError} />}

      <div className="results-layout">
        <section className="results-section">
          <div className="results-section-heading">
            <div className="results-section-title">
              <h3>
                <ThemeIcon light="modelLight-removebg-preview.png" dark="modelDark-removebg-preview.png" alt="modelos" className="results-section-icon" />
                {pt ? 'Modelos 3D' : '3D models'} ({modelTotal})
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

          <div className="results-filters">
            <input
              type="search"
              className="search-input"
              placeholder={language === 'pt' ? 'Buscar modelo…' : 'Search model…'}
              value={modelFilters.search}
              onChange={(e) => {
                setModelPage(1)
                setModelFilters((prev) => ({ ...prev, search: e.target.value }))
              }}
            />
            <select
              className="search-input"
              value={modelFilters.packing_method}
              onChange={(e) => {
                setModelPage(1)
                setModelFilters((prev) => ({ ...prev, packing_method: e.target.value }))
              }}
            >
              <option value="">{language === 'pt' ? 'Todos os métodos' : 'All methods'}</option>
              <option value="spherical_packing">spherical_packing</option>
              <option value="hexagonal_3d">hexagonal_3d</option>
              <option value="rigid_body">rigid_body</option>
            </select>
            <select
              className="search-input"
              value={modelFilters.has_blend}
              onChange={(e) => {
                setModelPage(1)
                setModelFilters((prev) => ({ ...prev, has_blend: e.target.value }))
              }}
            >
              <option value="">{language === 'pt' ? 'Blend: qualquer' : 'Blend: any'}</option>
              <option value="true">{language === 'pt' ? 'Com .blend' : 'With .blend'}</option>
              <option value="false">{language === 'pt' ? 'Sem .blend' : 'Without .blend'}</option>
            </select>
            <button
              className="btn-small"
              onClick={() => {
                setModelPage(1)
                setModelFilters({ search: '', packing_method: '', has_blend: '', has_stl: '' })
              }}
            >
              {language === 'pt' ? 'Limpar filtros' : 'Clear filters'}
            </button>
          </div>

          {loading ? (
            <p>{language === 'pt' ? 'Carregando…' : 'Loading…'}</p>
          ) : models.length === 0 ? (
            <p className="empty-state">{language === 'pt' ? 'Nenhum modelo encontrado' : 'No models found'}</p>
          ) : (
            <div className="casos-grid">
              {models.map((model) => (
                <div key={model.id} className="caso-card">
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
                      onClick={() => setSelectedModel({ ...model, path: getModelPreviewPath(model) })}
                      disabled={!getModelPreviewPath(model)}
                    >
                      <ThemeIcon light="viewLight-removebg-preview.png" dark="viewDark-removebg-preview.png" alt="" className="btn-icon" />
                      {pt ? 'visualizar' : 'view'}
                    </button>
                    <button
                      type="button"
                      className="btn-mode-option"
                      onClick={() => window.open(getModelDownloadPath(model), '_blank')}
                      disabled={!getModelDownloadPath(model)}
                    >
                      <ThemeIcon light="downloadLight-removebg-preview.png" dark="donwloadDark-removebg-preview.png" alt="" className="btn-icon" />
                      {pt ? 'baixar' : 'download'}
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
          <PaginationControls
            page={modelPage}
            totalPages={modelTotalPages}
            total={modelTotal}
            limit={modelLimit}
            loading={loading || modelsRefreshing}
            onPageChange={setModelPage}
            onLimitChange={(value) => {
              setModelPage(1)
              setModelLimit(value)
            }}
            label={pt ? 'Modelos 3D' : '3D models'}
            pt={pt}
          />
        </section>

        <section className="results-section">
          <div className="results-section-heading">
            <div className="results-section-title">
              <h3>
                <ThemeIcon light="cfd_gear_white.png" dark="image-removebg-preview(12).png" alt="simulações" className="results-section-icon" />
                {pt ? 'Simulações' : 'Simulations'} ({simTotal})
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

          <div className="results-filters">
            <input
              type="search"
              className="search-input"
              placeholder={language === 'pt' ? 'Buscar simulação…' : 'Search simulation…'}
              value={simFilters.search}
              onChange={(e) => {
                setSimPage(1)
                setSimFilters((prev) => ({ ...prev, search: e.target.value }))
              }}
            />
            <select
              className="search-input"
              value={simFilters.status}
              onChange={(e) => {
                setSimPage(1)
                setSimFilters((prev) => ({ ...prev, status: e.target.value }))
              }}
            >
              <option value="">{language === 'pt' ? 'Todos os estados' : 'All statuses'}</option>
              <option value="completed">{language === 'pt' ? 'Concluída' : 'Completed'}</option>
              <option value="running">{language === 'pt' ? 'Em execução' : 'Running'}</option>
              <option value="pending">{language === 'pt' ? 'Pendente' : 'Pending'}</option>
              <option value="failed">{language === 'pt' ? 'Falhou' : 'Failed'}</option>
            </select>
            <select
              className="search-input"
              value={simFilters.regime}
              onChange={(e) => {
                setSimPage(1)
                setSimFilters((prev) => ({ ...prev, regime: e.target.value }))
              }}
            >
              <option value="">{language === 'pt' ? 'Todos os regimes' : 'All regimes'}</option>
              <option value="laminar">laminar</option>
              <option value="turbulent">turbulent</option>
            </select>
            <button
              className="btn-small"
              onClick={() => {
                setSimPage(1)
                setSimFilters({ search: '', status: '', regime: '' })
              }}
            >
              {language === 'pt' ? 'Limpar filtros' : 'Clear filters'}
            </button>
          </div>

          {loading ? (
            <p>{language === 'pt' ? 'Carregando…' : 'Loading…'}</p>
          ) : simulations.length === 0 ? (
            <p className="empty-state">{language === 'pt' ? 'Nenhuma simulação encontrada' : 'No simulations found'}</p>
          ) : (
            <div className="casos-grid">
              {simulations.map((sim) => (
                <div key={sim.id} className="caso-card">
                  <div className="caso-header">
                    <h3>{sim.name}</h3>
                    <span className={`status-badge ${getSimStatusBadgeClass(sim.status)}`}>{sim.status}</span>
                  </div>
                  <div className="caso-info">
                    <div className="info-row">
                      <span className="info-label">id:</span>
                      <span>{sim.id}</span>
                    </div>
                    <div className="info-row">
                      <span className="info-label">{pt ? 'criado:' : 'created:'}</span>
                      <span>
                        {sim.created_at
                          ? new Date(sim.created_at).toLocaleString(pt ? 'pt-BR' : 'en-US')
                          : '—'}
                      </span>
                    </div>
                    <div className="info-row">
                      <span className="info-label">{pt ? 'regime:' : 'regime:'}</span>
                      <span>{sim.regime || '—'}</span>
                    </div>
                    <div className="info-row">
                      <span className="info-label">{pt ? 'estado:' : 'status:'}</span>
                      <span>{sim.status}</span>
                    </div>
                  </div>
                  <div className="caso-acoes">
                    <button
                      type="button"
                      className="btn-mode-option"
                      onClick={() => {
                        setSimulationResultsFilter({ resultType: '', search: '' })
                        setSimulationResultsMeta({ page: 1, limit: 12, total: 0, total_pages: 1 })
                        handleOpenSimulationResults(sim.id, { page: 1, limit: 12 })
                      }}
                    >
                      <ThemeIcon light="viewLight-removebg-preview.png" dark="viewDark-removebg-preview.png" alt="" className="btn-icon" />
                      {pt ? 'resultados' : 'results'}
                    </button>
                    <button
                      type="button"
                      className="btn-mode-option"
                      onClick={() => handleDownloadSimulationJson(sim.id)}
                    >
                      <ThemeIcon light="downloadLight-removebg-preview.png" dark="donwloadDark-removebg-preview.png" alt="" className="btn-icon" />
                      json
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
          <PaginationControls
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
            label={pt ? 'Simulações' : 'Simulations'}
            pt={pt}
            
          />
        </section>
      </div>

      {selectedModel && (
        <div className="modal-overlay" onClick={() => setSelectedModel(null)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <button
              className="modal-close"
              onClick={() => setSelectedModel(null)}
            >
              x
            </button>

            <h3>{language === 'pt' ? 'Visualização 3d' : '3d preview'}: {selectedModel.name}</h3>

            <ModelViewer modelPath={selectedModel.path} meshInfo={selectedModel} />
          </div>
        </div>
      )}

      {selectedSimulation && (
        <div className="modal-overlay" onClick={() => setSelectedSimulation(null)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <button
              className="modal-close"
              onClick={() => setSelectedSimulation(null)}
            >
              x
            </button>

            <h3>{language === 'pt' ? 'Resultados da simulação' : 'Simulation results'}: {selectedSimulation.name}</h3>

            {simulationResultsLoading ? (
              <p>{language === 'pt' ? 'Carregando…' : 'Loading…'}</p>
            ) : selectedSimulationResults.length === 0 ? (
              <p>{language === 'pt' ? 'Nenhum resultado persistido para esta simulação' : 'No persisted results for this simulation'}</p>
            ) : (
              <>
                <div className="results-filters">
                  <input
                    type="search"
                    className="search-input"
                    placeholder={language === 'pt' ? 'Buscar resultado…' : 'Search result…'}
                    value={simulationResultsFilter.search}
                    onChange={(e) => setSimulationResultsFilter((prev) => ({ ...prev, search: e.target.value }))}
                  />
                  <select
                    className="search-input"
                    value={simulationResultsFilter.resultType}
                    onChange={(e) => setSimulationResultsFilter((prev) => ({ ...prev, resultType: e.target.value }))}
                  >
                    <option value="">{language === 'pt' ? 'Todos os tipos' : 'All types'}</option>
                    <option value="field">field</option>
                    <option value="metric">metric</option>
                    <option value="validation">validation</option>
                    <option value="visualization">visualization</option>
                  </select>
                  <button
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
                    {language === 'pt' ? 'Aplicar filtros' : 'Apply filters'}
                  </button>
                </div>
                <div className="files-grid">
                  {selectedSimulationResults.map((result) => (
                    <div key={result.id} className="file-card">
                      <div className="file-info">
                        <h4 className="file-name">{result.name}</h4>
                        <p className="file-size">{result.result_type}</p>
                        <p className="file-date">
                          {result.value != null ? `${result.value} ${result.unit || ''}`.trim() : (language === 'pt' ? 'Sem valor escalar' : 'No scalar value')}
                        </p>
                        <p className="file-size">{result.file_type || 'json'}</p>
                      </div>
                    </div>
                  ))}
                </div>
                <PaginationControls
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
                  label={language === 'pt' ? 'Resultados persistidos' : 'Persisted results'}
                  pt={language === 'pt'}
                />
              </>
            )}
          </div>
        </div>
      )}
    </div>
  )
}

export default ResultsList

