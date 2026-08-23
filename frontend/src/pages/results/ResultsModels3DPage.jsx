import { useState, useEffect, useCallback } from 'react'
import {
  listModels3D,
  listViewerMeshes,
  mergeDbModelsWithProjectMeshes,
  buildGeneratedFileUrl,
  buildMeshStreamUrl,
} from '../../services/api'
import ModelViewer from '../ModelViewer'
import ThemeIcon from '../ThemeIcon'
import BackendConnectionError from '../BackendConnectionError'
import PaginationControls from '../PaginationControls'
import { useLanguage } from '../../context/LanguageContext'
import { useActiveUser } from '../../context/UserContext'
import '../../styles/CasosCFD.css'
import '../../styles/MeshViewer3DPage.css'
import '../SimulationHistory.css'
import { IconRefresh, formatBytes, isConnectionError } from './resultsShared'

function getModelPreviewPath(model) {
  if (model.mesh_id) return buildMeshStreamUrl(model.mesh_id)
  if (
    model.blend_file_path &&
    String(model.blend_file_path).toLowerCase().endsWith('.blend') &&
    !model.stl_file_path
  ) {
    return null
  }
  return model.preview_model_url
    ? buildGeneratedFileUrl(model.preview_model_url.replace(/^\/files\//, ''))
    : buildGeneratedFileUrl(model.stl_file_path || model.blend_file_path)
}

function getModelDownloadPath(model) {
  return buildGeneratedFileUrl(model.stl_file_path || model.blend_file_path)
}

function ResultsModels3DPage({ onOpenInViewer }) {
  const { t, language } = useLanguage()
  const { activeUserId } = useActiveUser()
  const pt = language === 'pt'
  const [models, setModels] = useState([])
  const [selectedModel, setSelectedModel] = useState(null)
  const [loading, setLoading] = useState(true)
  const [refreshing, setRefreshing] = useState(false)
  const [loadError, setLoadError] = useState(null)
  const [modelPage, setModelPage] = useState(1)
  const [modelLimit, setModelLimit] = useState(8)
  const [modelTotal, setModelTotal] = useState(0)
  const [modelTotalPages, setModelTotalPages] = useState(1)
  const [modelFilters, setModelFilters] = useState({
    search: '',
    packing_method: '',
    has_blend: '',
    has_stl: '',
    created_from: '',
    created_to: '',
  })

  const loadModels = useCallback(
    async ({ silent = false } = {}) => {
      if (!silent) setRefreshing(true)
      setLoadError(null)
      try {
        const [modelsData, meshData] = await Promise.all([
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
        ])
        const dbItems = Array.isArray(modelsData?.items) ? modelsData.items : []
        const merged = mergeDbModelsWithProjectMeshes(dbItems, meshData)
        setModels(merged)
        const extra = merged.length - dbItems.length
        setModelTotal((modelsData?.total || 0) + extra)
        setModelTotalPages(modelsData?.total_pages || modelsData?.pages || 1)
      } catch (err) {
        console.error('erro ao carregar modelos 3d:', err)
        if (isConnectionError(err)) {
          setLoadError(t('backendConnectionError'))
        } else {
          const detail = err.response?.data?.detail
          setLoadError(
            typeof detail === 'string'
              ? detail
              : pt
                ? 'erro ao carregar modelos 3d'
                : 'failed to load 3d models'
          )
        }
        setModels([])
        setModelTotal(0)
      } finally {
        if (!silent) setRefreshing(false)
      }
    },
    [modelFilters, modelLimit, modelPage, pt, t]
  )

  const loadData = useCallback(
    async ({ silent = false } = {}) => {
      if (!silent) setLoading(true)
      await loadModels({ silent: true })
      if (!silent) setLoading(false)
    },
    [loadModels]
  )

  useEffect(() => {
    loadData()
    const timer = window.setInterval(loadData, 5000)
    return () => window.clearInterval(timer)
  }, [activeUserId, loadData])

  return (
    <div className="simulation-history">
      <div className="history-header">
        <div className="history-header-top">
          <div className="history-title">
            <ThemeIcon
              light="modelLight-removebg-preview.png"
              dark="modelDark-removebg-preview.png"
              alt=""
              className="results-section-icon"
            />
            <h1>{pt ? 'Modelos 3D' : '3D models'}</h1>
          </div>
        </div>
      </div>

      {loadError && <BackendConnectionError message={loadError} />}

      <section className="results-section history-panel" aria-labelledby="models-3d-heading">
        <div className="results-section-heading">
          <div className="results-section-title">
            <h3 id="models-3d-heading" className="history-section-heading">
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
              disabled={refreshing || loading}
              aria-busy={refreshing || undefined}
            >
              <IconRefresh className="mesh-viewer-hub-btn__icon" aria-hidden />
              {refreshing ? '…' : pt ? 'atualizar' : 'refresh'}
            </button>
          </div>
        </div>

        <div className="history-filter-grid">
          <div className="search-container">
            <ThemeIcon
              light="triangle_white_outline.png"
              dark="triangle_black_outline.png"
              alt="buscar"
              className="search-icon"
            />
            <input
              type="text"
              placeholder={pt ? 'Buscar modelo por nome ou descrição…' : 'Search model by name or description…'}
              value={modelFilters.search}
              onChange={(e) => {
                setModelPage(1)
                setModelFilters((prev) => ({ ...prev, search: e.target.value }))
              }}
              className="search-input"
            />
          </div>

          <select
            className="history-select"
            value={modelFilters.packing_method}
            onChange={(e) => {
              setModelPage(1)
              setModelFilters((prev) => ({ ...prev, packing_method: e.target.value }))
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
              setModelPage(1)
              setModelFilters((prev) => ({ ...prev, has_blend: e.target.value }))
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
              setModelPage(1)
              setModelFilters((prev) => ({ ...prev, has_stl: e.target.value }))
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
              setModelPage(1)
              setModelFilters((prev) => ({ ...prev, created_from: e.target.value }))
            }}
            aria-label={pt ? 'Criado a partir de' : 'Created from'}
          />
          <input
            type="date"
            className="history-date-input"
            value={modelFilters.created_to}
            onChange={(e) => {
              setModelPage(1)
              setModelFilters((prev) => ({ ...prev, created_to: e.target.value }))
            }}
            aria-label={pt ? 'Criado até' : 'Created to'}
          />

          <button
            type="button"
            className="history-clear-btn"
            onClick={() => {
              setModelPage(1)
              setModelFilters({
                search: '',
                packing_method: '',
                has_blend: '',
                has_stl: '',
                created_from: '',
                created_to: '',
              })
            }}
          >
            {pt ? 'Limpar filtros' : 'Clear filters'}
          </button>
        </div>

        {loading ? (
          <div className="sim-history-loading">{pt ? 'Carregando…' : 'Loading…'}</div>
        ) : modelTotal === 0 ? (
          <div className="sim-history-empty">
            <p>
              {pt
                ? 'Nenhum modelo 3D encontrado com os filtros atuais'
                : 'No 3d models found for current filters'}
            </p>
          </div>
        ) : (
          <>
            <div className="casos-grid">
              {models.map((model) => {
                const previewPath = getModelPreviewPath(model)
                const downloadPath = getModelDownloadPath(model)
                const canPreview = Boolean(previewPath)
                const canOpenViewer = Boolean(model.mesh_id && typeof onOpenInViewer === 'function')
                return (
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
                        <span className="info-label">{pt ? 'geometria:' : 'geometry:'}</span>
                        <span>{model.geometry_mode || 'full_3d'}</span>
                      </div>
                      {(model.porosity_target != null || model.porosity_result != null) && (
                        <div className="info-row">
                          <span className="info-label">{pt ? 'porosidade:' : 'porosity:'}</span>
                          <span>
                            {model.porosity_result != null
                              ? `${(model.porosity_result * 100).toFixed(1)}%`
                              : '—'}
                            {model.porosity_target != null
                              ? ` (alvo ${(model.porosity_target * 100).toFixed(0)}%)`
                              : ''}
                          </span>
                        </div>
                      )}
                      {model.geometry_mode === 'pseudo_2d_thin_slice' && model.slice_axis && (
                        <div className="info-row">
                          <span className="info-label">{pt ? 'fatia:' : 'slice:'}</span>
                          <span>
                            {model.slice_axis}
                            {model.slice_thickness != null
                              ? ` · ${(model.slice_thickness * 1000).toFixed(2)} mm`
                              : ''}
                          </span>
                        </div>
                      )}
                      {model.geometry_mode === 'pseudo_2d_statistical' && (
                        <div className="info-row">
                          <span className="info-label">{pt ? 'reconstrução:' : 'reconstruction:'}</span>
                          <span>rsa 2d (motor python)</span>
                        </div>
                      )}
                      {model.internal_cylinder_mode && (
                        <div className="info-row">
                          <span className="info-label">{pt ? 'cilindro interno:' : 'internal cylinder:'}</span>
                          <span>{model.internal_cylinder_mode}</span>
                        </div>
                      )}
                      {(model.boolean_outer_shell || model.boolean_inner_core) && (
                        <div className="info-row">
                          <span className="info-label">{pt ? 'booleanas:' : 'booleans:'}</span>
                          <span>
                            {[model.boolean_outer_shell, model.boolean_inner_core, model.boolean_particle_tools]
                              .filter(Boolean)
                              .join(' · ')}
                          </span>
                        </div>
                      )}
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
                    {model.description ? (
                      <div className="caso-caminho">
                        <strong>{pt ? 'caminho:' : 'path:'}</strong>
                        <code title={model.description}>{model.description}</code>
                      </div>
                    ) : null}
                    <div className="caso-acoes">
                      <button
                        type="button"
                        className="btn-mode-option"
                        onClick={() => setSelectedModel({ ...model, path: previewPath })}
                        disabled={!canPreview}
                        title={pt ? 'pré-visualização rápida' : 'quick preview'}
                      >
                        <ThemeIcon
                          light="viewLight-removebg-preview.png"
                          dark="viewDark-removebg-preview.png"
                          alt=""
                          className="btn-icon"
                        />
                        {pt ? 'pré-visualizar' : 'preview'}
                      </button>
                      <button
                        type="button"
                        className="btn-mode-option"
                        onClick={() => onOpenInViewer(model.mesh_id)}
                        disabled={!canOpenViewer}
                        title={
                          canOpenViewer
                            ? pt
                              ? 'abrir na página visualização 3d'
                              : 'open in 3d viewer page'
                            : pt
                              ? 'disponível apenas para malhas indexadas no viewer'
                              : 'only for meshes indexed in the viewer'
                        }
                      >
                        <ThemeIcon
                          light="cfd_gear_white.png"
                          dark="cfd_gear_white.png"
                          alt=""
                          className="btn-icon"
                        />
                        {pt ? 'visualização 3d' : '3d viewer'}
                      </button>
                      <button
                        type="button"
                        className="btn-mode-option"
                        onClick={() => {
                          if (downloadPath) window.open(downloadPath, '_blank', 'noopener,noreferrer')
                        }}
                        disabled={!downloadPath}
                      >
                        <ThemeIcon
                          light="downloadLight-removebg-preview.png"
                          dark="donwloadDark-removebg-preview.png"
                          alt=""
                          className="btn-icon"
                        />
                        {pt ? 'baixar' : 'download'}
                      </button>
                    </div>
                  </div>
                )
              })}
            </div>

            <PaginationControls
              page={modelPage}
              totalPages={modelTotalPages}
              total={modelTotal}
              limit={modelLimit}
              loading={loading || refreshing}
              onPageChange={setModelPage}
              onLimitChange={(value) => {
                setModelPage(1)
                setModelLimit(value)
              }}
              label={pt ? 'Modelos 3D' : '3D models'}
              pt={pt}
            />
          </>
        )}
      </section>

      {selectedModel ? (
        <div className="modal-overlay" onClick={() => setSelectedModel(null)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <button type="button" className="modal-close" onClick={() => setSelectedModel(null)}>
              x
            </button>
            <h3>
              {pt ? 'Visualização 3d' : '3d preview'}: {selectedModel.name}
            </h3>
            <ModelViewer modelPath={selectedModel.path} meshInfo={selectedModel} />
          </div>
        </div>
      ) : null}
    </div>
  )
}

export default ResultsModels3DPage
