import { useState, useEffect, useCallback } from 'react'
import {
  listBedFiles,
  getBedFileContent,
  buildBedFileDownloadUrl,
  buildGeneratedFileUrl,
  parseApiError,
} from '../../services/api'
import ThemeIcon from '../ThemeIcon'
import BackendConnectionError from '../BackendConnectionError'
import PaginationControls from '../PaginationControls'
import { useLanguage } from '../../context/LanguageContext'
import { useActiveUser } from '../../context/UserContext'
import '../../styles/CasosCFD.css'
import '../../styles/MeshViewer3DPage.css'
import '../../styles/BedLoadModal.css'
import '../SimulationHistory.css'
import { IconRefresh, formatBytes, isConnectionError } from './resultsShared'

function originLabel(item, pt) {
  const o = String(item?.source || item?.origin || '').toLowerCase()
  if (o === 'web') return pt ? 'web' : 'web'
  if (o === 'wizard') return 'wizard'
  return pt ? 'terminal' : 'terminal'
}

function originBadgeClass(item) {
  const o = String(item?.source || item?.origin || '').toLowerCase()
  if (o === 'web') return 'status-completed'
  if (o === 'wizard') return 'status-configured'
  return 'status-meshed'
}

function modeLabel(mode, pt) {
  if (!mode) return '—'
  const m = String(mode)
  const map = {
    interactive: pt ? 'criar básico' : 'basic create',
    generation_3d: pt ? 'geração 3d' : '3d generation',
    pipeline_completo: pt ? 'pipeline completo' : 'full pipeline',
    blender_interactive: pt ? 'blender interativo' : 'blender interactive',
    blender: 'blender',
    bed_editor: pt ? 'editor .bed' : '.bed editor',
    template_json: pt ? 'template json' : 'json template',
    template: pt ? 'template' : 'template',
    migrated: pt ? 'migrado (raiz)' : 'migrated (root)',
  }
  return map[m] || m
}

function buildJsonUrl(jsonRel) {
  if (!jsonRel) return null
  return buildGeneratedFileUrl(jsonRel) || buildBedFileDownloadUrl(jsonRel)
}

export default function ResultsBedCodePage() {
  const { t, language } = useLanguage()
  const { activeUserId } = useActiveUser()
  const pt = language === 'pt'

  const [items, setItems] = useState([])
  const [loading, setLoading] = useState(true)
  const [refreshing, setRefreshing] = useState(false)
  const [loadError, setLoadError] = useState(null)
  const [page, setPage] = useState(1)
  const [limit, setLimit] = useState(8)
  const [total, setTotal] = useState(0)
  const [totalPages, setTotalPages] = useState(1)
  const [filters, setFilters] = useState({
    search: '',
    has_json: '',
    origin: '',
    creation_mode: '',
  })
  const [selected, setSelected] = useState(null)
  const [contentLoading, setContentLoading] = useState(false)
  const [copyMsg, setCopyMsg] = useState('')

  const loadList = useCallback(
    async ({ silent = false } = {}) => {
      if (!silent) setRefreshing(true)
      setLoadError(null)
      try {
        const data = await listBedFiles({
          page,
          limit,
          search: filters.search || null,
          has_json:
            filters.has_json === ''
              ? null
              : filters.has_json === 'true',
          origin: filters.origin || null,
          creation_mode: filters.creation_mode || null,
        })
        setItems(Array.isArray(data?.items) ? data.items : [])
        setTotal(data?.total ?? 0)
        setTotalPages(data?.total_pages ?? 1)
      } catch (err) {
        console.error('erro ao carregar ficheiros .bed:', err)
        if (isConnectionError(err)) {
          setLoadError(t('backendConnectionError'))
        } else {
          const detail = err.response?.data?.detail
          setLoadError(
            typeof detail === 'string'
              ? detail
              : pt
                ? 'erro ao carregar ficheiros .bed'
                : 'failed to load .bed files'
          )
        }
        setItems([])
        setTotal(0)
      } finally {
        if (!silent) setRefreshing(false)
      }
    },
    [filters, limit, page, pt, t]
  )

  const loadData = useCallback(
    async ({ silent = false } = {}) => {
      if (!silent) setLoading(true)
      await loadList({ silent: true })
      if (!silent) setLoading(false)
    },
    [loadList]
  )

  useEffect(() => {
    loadData()
    const timer = window.setInterval(() => loadData({ silent: true }), 8000)
    return () => window.clearInterval(timer)
  }, [activeUserId, loadData])

  const openBed = async (item) => {
    setContentLoading(true)
    setCopyMsg('')
    try {
      const data = await getBedFileContent(item.relative_path)
      setSelected({ ...item, ...data })
    } catch (err) {
      console.error(err)
      alert(
        parseApiError(err) ||
          (pt ? 'não foi possível abrir o ficheiro' : 'could not open file')
      )
    } finally {
      setContentLoading(false)
    }
  }

  const copyContent = async () => {
    if (!selected?.content) return
    try {
      await navigator.clipboard.writeText(selected.content)
      setCopyMsg(pt ? 'código copiado' : 'code copied')
    } catch {
      setCopyMsg(pt ? 'falha ao copiar' : 'copy failed')
    }
  }

  return (
    <div className="simulation-history">
      <div className="history-header">
        <div className="history-header-top">
          <div className="history-title">
            <ThemeIcon
              light="textEditorLight.png"
              dark="textEditor.png"
              alt=""
              className="results-section-icon"
            />
            <h1>{pt ? 'código .bed' : '.bed code'}</h1>
          </div>
        </div>
        <p className="history-subtitle">
          {pt
            ? 'ficheiros .bed gerados na web ou no terminal (local_data/beds, dsl, legado)'
            : '.bed files from web or terminal (local_data/beds, dsl, legacy)'}
        </p>
      </div>

      {loadError && <BackendConnectionError message={loadError} />}

      <section className="results-section history-panel" aria-labelledby="bed-code-heading">
        <div className="results-section-heading">
          <div className="results-section-title">
            <h3 id="bed-code-heading" className="history-section-heading">
              <ThemeIcon
                light="textEditorLight.png"
                dark="textEditor.png"
                alt=""
                className="results-section-icon"
              />
              <span>
                {pt ? 'ficheiros .bed' : '.bed files'} ({total})
              </span>
            </h3>
          </div>
          <div className="results-section-toolbar">
            <button
              type="button"
              className="mesh-viewer-hub-btn mesh-viewer-hub-btn--compact"
              onClick={() => void loadList()}
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
              placeholder={pt ? 'buscar por nome ou caminho…' : 'search by name or path…'}
              value={filters.search}
              onChange={(e) => {
                setPage(1)
                setFilters((prev) => ({ ...prev, search: e.target.value }))
              }}
              className="search-input"
            />
          </div>

          <select
            className="history-select"
            value={filters.has_json}
            onChange={(e) => {
              setPage(1)
              setFilters((prev) => ({ ...prev, has_json: e.target.value }))
            }}
          >
            <option value="">{pt ? 'json: qualquer' : 'json: any'}</option>
            <option value="true">{pt ? 'com .bed.json' : 'with .bed.json'}</option>
            <option value="false">{pt ? 'sem .bed.json' : 'without .bed.json'}</option>
          </select>

          <select
            className="history-select"
            value={filters.origin}
            onChange={(e) => {
              setPage(1)
              setFilters((prev) => ({ ...prev, origin: e.target.value }))
            }}
          >
            <option value="">{pt ? 'origem: qualquer' : 'origin: any'}</option>
            <option value="web">{pt ? 'web (wizard)' : 'web (wizard)'}</option>
            <option value="wizard">wizard</option>
            <option value="terminal">{pt ? 'terminal' : 'terminal'}</option>
          </select>

          <select
            className="history-select"
            value={filters.creation_mode}
            onChange={(e) => {
              setPage(1)
              setFilters((prev) => ({ ...prev, creation_mode: e.target.value }))
            }}
          >
            <option value="">{pt ? 'modo: qualquer' : 'mode: any'}</option>
            <option value="interactive">{pt ? 'criar básico' : 'basic create'}</option>
            <option value="generation_3d">{pt ? 'geração 3d' : '3d generation'}</option>
            <option value="pipeline_completo">{pt ? 'pipeline completo' : 'full pipeline'}</option>
            <option value="blender_interactive">blender</option>
            <option value="bed_editor">{pt ? 'editor .bed' : '.bed editor'}</option>
          </select>

          <button
            type="button"
            className="history-clear-btn"
            onClick={() => {
              setPage(1)
              setFilters({ search: '', has_json: '', origin: '', creation_mode: '' })
            }}
          >
            {pt ? 'limpar filtros' : 'clear filters'}
          </button>
        </div>

        {loading ? (
          <div className="sim-history-loading">{pt ? 'carregando…' : 'loading…'}</div>
        ) : total === 0 ? (
          <div className="sim-history-empty">
            <p>{pt ? 'nenhum ficheiro .bed encontrado' : 'no .bed files found'}</p>
            <p className="hint">
              {pt
                ? 'use criação (web) ou o wizard no terminal; os ficheiros aparecem em local_data/beds'
                : 'use creation (web) or the terminal wizard; files appear under local_data/beds'}
            </p>
          </div>
        ) : (
          <>
            <div className="casos-grid">
              {items.map((item) => {
                const downloadUrl = buildBedFileDownloadUrl(item.relative_path)
                const jsonUrl = buildJsonUrl(item.json_relative_path)
                return (
                  <div key={item.relative_path} className="caso-card">
                    <div className="caso-header">
                      <h3>{item.filename}</h3>
                      <span className={`status-badge ${originBadgeClass(item)}`}>
                        {originLabel(item, pt)}
                      </span>
                    </div>
                    <div className="caso-info">
                      <div className="info-row">
                        <span className="info-label">{pt ? 'modo:' : 'mode:'}</span>
                        <span>{modeLabel(item.creation_mode, pt)}</span>
                      </div>
                      <div className="info-row">
                        <span className="info-label">{pt ? 'criado:' : 'created:'}</span>
                        <span>
                          {item.created_at
                            ? new Date(item.created_at).toLocaleString(pt ? 'pt-BR' : 'en-US')
                            : '—'}
                        </span>
                      </div>
                      <div className="info-row">
                        <span className="info-label">{pt ? 'pasta:' : 'folder:'}</span>
                        <span>{item.storage_folder || '—'}</span>
                      </div>
                      <div className="info-row">
                        <span className="info-label">{pt ? 'tamanho:' : 'size:'}</span>
                        <span>{formatBytes(item.size_bytes)}</span>
                      </div>
                      <div className="info-row">
                        <span className="info-label">{pt ? 'modificado:' : 'modified:'}</span>
                        <span>
                          {item.mtime_iso
                            ? new Date(item.mtime_iso).toLocaleString(pt ? 'pt-BR' : 'en-US')
                            : '—'}
                        </span>
                      </div>
                      <div className="info-row">
                        <span className="info-label">json:</span>
                        <span>{item.has_json ? (pt ? 'sim' : 'yes') : (pt ? 'não' : 'no')}</span>
                      </div>
                    </div>
                    <div className="caso-caminho">
                      <strong>{pt ? 'caminho:' : 'path:'}</strong>
                      <code title={item.relative_path}>{item.relative_path}</code>
                    </div>
                    <div className="caso-acoes">
                      <button
                        type="button"
                        className="btn-mode-option"
                        onClick={() => void openBed(item)}
                        disabled={contentLoading}
                      >
                        <ThemeIcon
                          light="textEditorLight.png"
                          dark="textEditor.png"
                          alt=""
                          className="btn-icon"
                        />
                        {pt ? 'ver código' : 'view code'}
                      </button>
                      <button
                        type="button"
                        className="btn-mode-option"
                        onClick={() => {
                          if (downloadUrl) {
                            window.open(downloadUrl, '_blank', 'noopener,noreferrer')
                          }
                        }}
                      >
                        <ThemeIcon
                          light="downloadLight-removebg-preview.png"
                          dark="donwloadDark-removebg-preview.png"
                          alt=""
                          className="btn-icon"
                        />
                        .bed
                      </button>
                      {item.has_json && jsonUrl ? (
                        <button
                          type="button"
                          className="btn-mode-option"
                          onClick={() => window.open(jsonUrl, '_blank', 'noopener,noreferrer')}
                        >
                          <ThemeIcon
                            light="folderLight.png"
                            dark="folderDark.png"
                            alt=""
                            className="btn-icon"
                          />
                          json
                        </button>
                      ) : null}
                    </div>
                  </div>
                )
              })}
            </div>

            <PaginationControls
              page={page}
              totalPages={totalPages}
              total={total}
              limit={limit}
              loading={loading || refreshing}
              onPageChange={setPage}
              onLimitChange={(value) => {
                setPage(1)
                setLimit(value)
              }}
              label={pt ? 'código .bed' : '.bed code'}
              pt={pt}
            />
          </>
        )}
      </section>

      {selected && (
        <div
          className="modal-overlay"
          role="presentation"
          onClick={() => setSelected(null)}
        >
          <div
            className="modal-content bed-code-modal"
            role="dialog"
            aria-labelledby="bed-code-modal-title"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="modal-header">
              <h2 id="bed-code-modal-title">{selected.filename}</h2>
              <button
                type="button"
                className="btn-close"
                onClick={() => setSelected(null)}
                aria-label={pt ? 'fechar' : 'close'}
              >
                ×
              </button>
            </div>
            <p className="wizard-hint-muted">
              <code>{selected.relative_path}</code>
              {' · '}
              {originLabel(selected, pt)}
              {' · '}
              {modeLabel(selected.creation_mode, pt)}
              {selected.has_json && selected.json_relative_path
                ? ` · json: ${selected.json_relative_path}`
                : ''}
            </p>
            <div className="bed-code-editor-section">
              <textarea
                className="bed-code-textarea"
                readOnly
                value={selected.content}
                rows={22}
                spellCheck={false}
              />
            </div>
            <div className="bed-code-actions">
              <button type="button" className="btn-mode-option" onClick={() => void copyContent()}>
                <ThemeIcon
                  light="textEditorLight.png"
                  dark="textEditor.png"
                  alt=""
                  className="btn-icon"
                />
                {pt ? 'copiar código' : 'copy code'}
              </button>
              <button
                type="button"
                className="btn-primary"
                onClick={() => {
                  const url = buildBedFileDownloadUrl(selected.relative_path)
                  if (url) window.open(url, '_blank', 'noopener,noreferrer')
                }}
              >
                {pt ? 'descarregar .bed' : 'download .bed'}
              </button>
              {copyMsg ? <span className="wizard-cli-launch-msg">{copyMsg}</span> : null}
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
