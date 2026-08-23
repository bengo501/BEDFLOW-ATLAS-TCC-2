import { useCallback, useEffect, useRef, useState } from 'react';
import { useLanguage } from '../context/LanguageContext';
import {
  listTemplates,
  saveTemplate,
  getTemplate,
  deleteTemplate,
  duplicateTemplate,
} from '../services/api';
import BackendConnectionError from './BackendConnectionError';
import PaginationControls from './PaginationControls';
import ThemeIcon from './ThemeIcon';
import './SavedTemplatesPage.css';

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

function IconImportFile({ className }) {
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
      <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
      <polyline points="17 8 12 3 7 8" />
      <line x1="12" y1="3" x2="12" y2="15" />
    </svg>
  );
}

function isConnectionError(err) {
  if (!err) return false;
  const noResponse = !err.response && !!err.request;
  const network =
    err.code === 'ERR_NETWORK' ||
    err.code === 'ECONNABORTED' ||
    (typeof err.message === 'string' && err.message.toLowerCase().includes('network'));
  return noResponse || network;
}

function sourceLabel(source, pt) {
  const s = (source || 'editor').toLowerCase();
  if (s === 'import') return pt ? 'Importação' : 'Import';
  if (s === 'duplicate') return pt ? 'Duplicado' : 'Duplicate';
  return pt ? 'Editor' : 'Editor';
}

function formatUpdatedLine(iso, pt) {
  if (!iso) return '';
  const capitalizeFirst = (s) => {
    if (!s || typeof s !== 'string') return s;
    const c = s.charAt(0);
    if (!c || c === c.toLowerCase() && c === c.toUpperCase()) return s;
    return c.toLocaleUpperCase(pt ? 'pt' : 'en') + s.slice(1);
  };
  try {
    const d = new Date(iso);
    const now = Date.now();
    const sec = Math.round((now - d.getTime()) / 1000);
    const rtf = new Intl.RelativeTimeFormat(pt ? 'pt' : 'en', { numeric: 'auto' });
    if (Math.abs(sec) < 60) return capitalizeFirst(rtf.format(-sec, 'second'));
    const min = Math.round(sec / 60);
    if (Math.abs(min) < 60) return capitalizeFirst(rtf.format(-min, 'minute'));
    const h = Math.round(min / 60);
    if (Math.abs(h) < 48) return capitalizeFirst(rtf.format(-h, 'hour'));
    const days = Math.round(h / 24);
    if (Math.abs(days) < 14) return capitalizeFirst(rtf.format(-days, 'day'));
    return capitalizeFirst(
      d.toLocaleDateString(pt ? 'pt-PT' : 'en-GB', {
        day: '2-digit',
        month: 'short',
        year: 'numeric',
      })
    );
  } catch {
    return iso;
  }
}

/**
 * biblioteca de templates .bed persistidos no banco (api /api/templates/*).
 */
export default function SavedTemplatesPage({ onEditTemplate }) {
  const { language, t } = useLanguage();
  const pt = language === 'pt';
  const fileRef = useRef(null);

  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [page, setPage] = useState(1);
  const [limit, setLimit] = useState(8);
  const [total, setTotal] = useState(0);
  const [totalPages, setTotalPages] = useState(1);
  const [filters, setFilters] = useState({
    search: '',
    tag: '',
    source: '',
  });
  const [selectedId, setSelectedId] = useState(null);
  const [connectionError, setConnectionError] = useState(null);
  const [opError, setOpError] = useState(null);

  const loadTemplates = useCallback(async () => {
    setLoading(true);
    setConnectionError(null);
    setOpError(null);
    try {
      const data = await listTemplates({
        page,
        limit,
        search: filters.search,
        tag: filters.tag || null,
        source: filters.source || null,
      });
      setItems(Array.isArray(data?.items) ? data.items : []);
      setTotal(data?.total || 0);
      setTotalPages(data?.total_pages || data?.pages || 1);
    } catch (err) {
      console.error(err);
      if (isConnectionError(err)) {
        setConnectionError(t('backendConnectionError'));
        setItems([]);
      } else {
        setOpError(
          err.response?.data?.detail ||
            err.message ||
            (pt ? 'Não foi possível carregar os templates.' : 'Could not load templates.')
        );
        setItems([]);
        setTotal(0);
      }
    } finally {
      setLoading(false);
    }
  }, [filters, limit, page, pt, t]);

  useEffect(() => {
    loadTemplates();
  }, [loadTemplates]);

  const toggleSelect = (id) => {
    setSelectedId((prev) => (prev === id ? null : id));
    setOpError(null);
  };

  const handleDuplicate = async () => {
    if (!selectedId) return;
    setOpError(null);
    setConnectionError(null);
    try {
      await duplicateTemplate(selectedId);
      await loadTemplates();
      setSelectedId(null);
    } catch (err) {
      console.error(err);
      if (isConnectionError(err)) setConnectionError(t('backendConnectionError'));
      else
        setOpError(
          err.response?.data?.detail ||
            (pt ? 'Falha ao duplicar.' : 'Duplicate failed.')
        );
    }
  };

  const handleEdit = async () => {
    if (!selectedId || !onEditTemplate) return;
    setOpError(null);
    setConnectionError(null);
    try {
      const data = await getTemplate(selectedId);
      onEditTemplate({
        id: data.id,
        name: data.name,
        content: data.content,
      });
    } catch (err) {
      console.error(err);
      if (isConnectionError(err)) setConnectionError(t('backendConnectionError'));
      else
        setOpError(
          err.response?.data?.detail ||
            (pt ? 'Não foi possível abrir o editor.' : 'Could not open editor.')
        );
    }
  };

  const handleDelete = async () => {
    if (!selectedId) return;
    const ok = window.confirm(
      pt ? 'Eliminar este template da base de dados?' : 'Delete this template from the database?'
    );
    if (!ok) return;
    setOpError(null);
    setConnectionError(null);
    try {
      await deleteTemplate(selectedId);
      setSelectedId(null);
      await loadTemplates();
    } catch (err) {
      console.error(err);
      if (isConnectionError(err)) setConnectionError(t('backendConnectionError'));
      else
        setOpError(
          err.response?.data?.detail || (pt ? 'Falha ao eliminar.' : 'Delete failed.')
        );
    }
  };

  const handleImportClick = () => {
    fileRef.current?.click();
  };

  const handleImportFile = async (event) => {
    const file = event.target.files?.[0];
    event.target.value = '';
    if (!file) return;

    const reader = new FileReader();
    reader.onload = async () => {
      const content = typeof reader.result === 'string' ? reader.result : '';
      const defaultName = file.name.replace(/\.bed$/i, '') || file.name || 'importado';
      const nameInput = window.prompt(
        pt ? 'Nome do template na biblioteca:' : 'Template name in library:',
        defaultName
      );
      if (!nameInput || !nameInput.trim()) return;

      setOpError(null);
      setConnectionError(null);
      try {
        await saveTemplate({
          name: nameInput.trim(),
          content,
          tag: 'bed',
          source: 'import',
        });
        await loadTemplates();
      } catch (err) {
        console.error(err);
        if (isConnectionError(err)) setConnectionError(t('backendConnectionError'));
        else
          setOpError(
            err.response?.data?.detail || (pt ? 'Falha ao importar.' : 'Import failed.')
          );
      }
    };
    reader.readAsText(file);
  };

  return (
    <div className="tab-content">
      <div className="saved-templates-page">
        {connectionError && <BackendConnectionError message={connectionError} />}

        {opError && (
          <div className="saved-templates-op-error" role="alert">
            {opError}
          </div>
        )}

        <div className="saved-templates-page-heading" aria-label={pt ? 'templates salvos' : 'saved templates'}>
          <ThemeIcon
            light="folderLight.png"
            dark="folderDark.png"
            alt=""
            className="saved-templates-page-heading-icon"
            location="page"
          />
          <h2 className="saved-templates-page-title">{pt ? 'Templates salvos' : 'Saved templates'}</h2>
        </div>

        <div className="saved-templates-layout">
          <section
            className="saved-templates-mockup-card"
            aria-label={pt ? 'Biblioteca de templates' : 'Template library'}
          >
            <div className="saved-templates-toolbar">
              <input
                type="search"
                value={filters.search}
                onChange={(e) => {
                  setPage(1);
                  setFilters((prev) => ({ ...prev, search: e.target.value }));
                }}
                placeholder={pt ? 'Pesquisar por nome ou etiqueta…' : 'Search by name or tag…'}
                aria-label={pt ? 'Pesquisar templates' : 'Search templates'}
              />
              <select
                className="saved-templates-select"
                value={filters.tag}
                onChange={(e) => {
                  setPage(1);
                  setFilters((prev) => ({ ...prev, tag: e.target.value }));
                }}
              >
                <option value="">{pt ? 'Todas as etiquetas' : 'All tags'}</option>
                <option value="bed">bed</option>
                <option value="preset">preset</option>
                <option value="cfd">cfd</option>
              </select>
              <select
                className="saved-templates-select"
                value={filters.source}
                onChange={(e) => {
                  setPage(1);
                  setFilters((prev) => ({ ...prev, source: e.target.value }));
                }}
              >
                <option value="">{pt ? 'Todas as origens' : 'All sources'}</option>
                <option value="editor">{pt ? 'Editor' : 'Editor'}</option>
                <option value="import">{pt ? 'Importação' : 'Import'}</option>
                <option value="duplicate">{pt ? 'Duplicado' : 'Duplicate'}</option>
              </select>
              <button
                type="button"
                className="saved-templates-refresh saved-templates-btn-with-icon"
                onClick={() => loadTemplates()}
                disabled={loading}
              >
                <IconRefresh className="saved-templates-btn-svg" />
                {pt ? 'Atualizar' : 'Refresh'}
              </button>
              <button
                type="button"
                className="saved-templates-refresh"
                onClick={() => {
                  setPage(1);
                  setFilters({ search: '', tag: '', source: '' });
                }}
                disabled={loading}
              >
                {pt ? 'Limpar filtros' : 'Clear filters'}
              </button>
            </div>

            {loading ? (
              <p className="saved-templates-status">{pt ? 'A carregar…' : 'Loading…'}</p>
            ) : items.length === 0 ? (
              <p className="saved-templates-status">
                {total === 0
                  ? pt
                    ? 'Nenhum template na biblioteca. Importe um .bed ou guarde a partir do editor.'
                    : 'No templates yet. Import a .bed or save from the editor.'
                  : pt
                    ? 'Nenhum resultado para a pesquisa.'
                    : 'No matches for your search.'}
              </p>
            ) : (
              <div className="saved-templates-grid">
                {items.map((row) => {
                  const meta = pt
                    ? `Atualizado ${formatUpdatedLine(row.updated_at, true)} · Origem: ${sourceLabel(row.source, true)}`
                    : `Updated ${formatUpdatedLine(row.updated_at, false)} · Source: ${sourceLabel(row.source, false)}`;
                  return (
                    <article
                      key={row.id}
                      className={`saved-templates-card ${selectedId === row.id ? 'selected' : ''}`}
                    >
                      <button
                        type="button"
                        className="saved-templates-card-hit"
                        onClick={() => toggleSelect(row.id)}
                        aria-pressed={selectedId === row.id}
                      >
                        <span className="saved-templates-card-title">{row.name}</span>
                        <span className="saved-templates-card-tag">{row.tag || 'bed'}</span>
                        <span className="saved-templates-card-meta">{meta}</span>
                      </button>
                    </article>
                  );
                })}
              </div>
            )}

            <PaginationControls
              page={page}
              totalPages={totalPages}
              total={total}
              limit={limit}
              loading={loading}
              onPageChange={setPage}
              onLimitChange={(value) => {
                setPage(1);
                setLimit(value);
              }}
              label={pt ? 'Templates .bed' : '.bed templates'}
              pt={pt}
            />

            <input
              ref={fileRef}
              type="file"
              accept=".bed,text/plain"
              className="saved-templates-file-input"
              aria-hidden
              tabIndex={-1}
              onChange={handleImportFile}
            />

            <div className="saved-templates-actions">
              <button type="button" disabled={!selectedId || !onEditTemplate} onClick={() => void handleEdit()}>
                {pt ? 'Editar template' : 'Edit template'}
              </button>
              <button type="button" className="saved-templates-btn-with-icon" onClick={handleImportClick}>
                <IconImportFile className="saved-templates-btn-svg" />
                {pt ? 'Importar ficheiro' : 'Import file'}
              </button>
              <button type="button" disabled={!selectedId} onClick={handleDuplicate}>
                {pt ? 'Duplicar selecionado' : 'Duplicate selected'}
              </button>
              <button type="button" disabled={!selectedId} onClick={handleDelete}>
                {pt ? 'Eliminar' : 'Delete'}
              </button>
            </div>
          </section>
        </div>
      </div>
    </div>
  );
}
