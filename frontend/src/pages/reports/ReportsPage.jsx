import { useCallback, useEffect, useState } from 'react';
import JSZip from 'jszip';
import { useLanguage } from '../context/LanguageContext';
import {
  listReports,
  getReport,
  createReport,
  updateReport,
  deleteReport,
  reportsCatalog,
  reportsResultsForSimulation,
  addReportAttachment,
  removeReportAttachment,
} from '../services/api';
import BackendConnectionError from './BackendConnectionError';
import PaginationControls from './PaginationControls';
import ThemeIcon from './ThemeIcon';
import './ReportsPage.css';

function isConnectionError(err) {
  if (!err) return false;
  const noResponse = !err.response && !!err.request;
  const network =
    err.code === 'ERR_NETWORK' ||
    err.code === 'ECONNABORTED' ||
    (typeof err.message === 'string' && err.message.toLowerCase().includes('network'));
  return noResponse || network;
}

function statusLabel(status, pt) {
  const m = {
    draft: pt ? 'Rascunho' : 'Draft',
    planned: pt ? 'Planeado' : 'Planned',
    published: pt ? 'Publicado' : 'Published',
  };
  return m[status] || status;
}

function kindLabel(kind, pt) {
  const m = {
    simulation: pt ? 'simulação' : 'simulation',
    template: pt ? 'template .bed' : '.bed template',
    result: pt ? 'resultado' : 'result',
    data_note: pt ? 'dados / nota' : 'data note',
  };
  return m[kind] || kind;
}

function slugify(s) {
  return String(s || 'relatorio')
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '')
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/^-+|-+$/g, '')
    .slice(0, 60) || 'relatorio';
}

function escapeHtml(s) {
  return String(s ?? '')
    .replaceAll('&', '&amp;')
    .replaceAll('<', '&lt;')
    .replaceAll('>', '&gt;')
    .replaceAll('"', '&quot;')
    .replaceAll("'", '&#39;');
}

function buildPreviewHtml(detail, pt) {
  const title = escapeHtml(detail.title || (pt ? 'relatório' : 'report'));
  const statusTxt = escapeHtml(detail.status || 'draft');
  const created = detail.created_at
    ? new Date(detail.created_at).toLocaleString(pt ? 'pt-PT' : 'en-GB')
    : '—';
  const updated = detail.updated_at
    ? new Date(detail.updated_at).toLocaleString(pt ? 'pt-PT' : 'en-GB')
    : '—';
  const body = escapeHtml(detail.body || '');
  const atts = Array.isArray(detail.attachments) ? detail.attachments : [];
  const attachmentsHtml = atts.length
    ? atts
        .map((a) => {
          const k = escapeHtml(kindLabel(a.kind, pt));
          const ref = escapeHtml(a.display_ref || a.ref_id || '');
          const note = a.note
            ? a.kind === 'data_note'
              ? `<pre class="att-data">${escapeHtml(a.note)}</pre>`
              : `<div class="att-note">${escapeHtml(a.note)}</div>`
            : '';
          return `<li class="att"><div class="att-head"><span class="att-kind">${k}</span><span class="att-ref">${ref}</span></div>${note}</li>`;
        })
        .join('')
    : `<li class="att empty">${escapeHtml(pt ? 'sem anexos.' : 'no attachments.')}</li>`;

  const labels = {
    status: pt ? 'estado' : 'status',
    created: pt ? 'criado' : 'created',
    updated: pt ? 'atualizado' : 'updated',
    body: pt ? 'conteúdo' : 'body',
    attachments: pt ? 'anexos' : 'attachments',
    generated: pt ? 'gerado em' : 'generated at',
  };
  const now = new Date().toLocaleString(pt ? 'pt-PT' : 'en-GB');

  return `<!doctype html>
<html lang="${pt ? 'pt' : 'en'}">
<head>
<meta charset="utf-8" />
<title>${title}</title>
<style>
  * { box-sizing: border-box; }
  body { font-family: 'Segoe UI', Roboto, Arial, sans-serif; color: #1a1a1a; background: #fff; margin: 2rem; line-height: 1.5; }
  h1 { font-size: 1.6rem; margin: 0 0 0.25rem; }
  .meta { color: #555; font-size: 0.85rem; margin-bottom: 1.25rem; }
  .meta span { margin-right: 1rem; }
  .pill { display: inline-block; padding: 0.1rem 0.5rem; border-radius: 999px; background: #eef; color: #224; font-size: 0.75rem; font-weight: 600; }
  h2 { font-size: 1.1rem; margin: 1.5rem 0 0.5rem; border-bottom: 1px solid #ddd; padding-bottom: 0.25rem; }
  .body { white-space: pre-wrap; font-family: inherit; font-size: 0.95rem; border: 1px solid #e5e5e5; padding: 1rem; border-radius: 6px; background: #fafafa; }
  ul.atts { list-style: none; padding: 0; margin: 0; }
  .att { border: 1px solid #e5e5e5; border-radius: 6px; padding: 0.75rem; margin-bottom: 0.5rem; }
  .att.empty { color: #666; font-style: italic; }
  .att-head { display: flex; gap: 0.75rem; align-items: center; margin-bottom: 0.25rem; }
  .att-kind { font-weight: 600; color: #335; font-size: 0.8rem; text-transform: uppercase; }
  .att-ref { color: #222; }
  .att-note { font-size: 0.9rem; color: #333; margin-top: 0.25rem; }
  .att-data { background: #f3f3f3; padding: 0.5rem; border-radius: 4px; font-size: 0.8rem; white-space: pre-wrap; overflow-x: auto; }
  footer { margin-top: 2rem; color: #888; font-size: 0.75rem; text-align: right; }
  @media print {
    body { margin: 1rem; }
    h2 { page-break-after: avoid; }
    .att { page-break-inside: avoid; }
  }
</style>
</head>
<body>
  <h1>${title}</h1>
  <div class="meta">
    <span><strong>${escapeHtml(labels.status)}:</strong> <span class="pill">${statusTxt}</span></span>
    <span><strong>${escapeHtml(labels.created)}:</strong> ${escapeHtml(created)}</span>
    <span><strong>${escapeHtml(labels.updated)}:</strong> ${escapeHtml(updated)}</span>
  </div>
  <h2>${escapeHtml(labels.body)}</h2>
  <div class="body">${body || '—'}</div>
  <h2>${escapeHtml(labels.attachments)} (${atts.length})</h2>
  <ul class="atts">${attachmentsHtml}</ul>
  <footer>${escapeHtml(labels.generated)}: ${escapeHtml(now)}</footer>
</body>
</html>`;
}

function buildReportMd(detail, pt) {
  const atts = Array.isArray(detail.attachments) ? detail.attachments : [];
  const lines = [];
  lines.push(`# ${detail.title || (pt ? 'relatório' : 'report')}`);
  lines.push('');
  lines.push(`- **${pt ? 'estado' : 'status'}**: ${detail.status || 'draft'}`);
  if (detail.created_at) lines.push(`- **${pt ? 'criado' : 'created'}**: ${detail.created_at}`);
  if (detail.updated_at) lines.push(`- **${pt ? 'atualizado' : 'updated'}**: ${detail.updated_at}`);
  lines.push('');
  lines.push(`## ${pt ? 'conteúdo' : 'body'}`);
  lines.push('');
  lines.push(detail.body || '—');
  lines.push('');
  lines.push(`## ${pt ? 'anexos' : 'attachments'} (${atts.length})`);
  lines.push('');
  if (!atts.length) {
    lines.push(`_${pt ? 'sem anexos.' : 'no attachments.'}_`);
  } else {
    for (const a of atts) {
      lines.push(`### ${kindLabel(a.kind, pt)} — ${a.display_ref || a.ref_id || ''}`);
      if (a.note) {
        if (a.kind === 'data_note') {
          lines.push('');
          lines.push('```');
          lines.push(a.note);
          lines.push('```');
        } else {
          lines.push('');
          lines.push(a.note);
        }
      }
      lines.push('');
    }
  }
  return lines.join('\n');
}

/**
 * relatórios persistidos (reports + report_attachments); modal para editar e anexar entidades.
 */
export default function ReportsPage() {
  const { language, t } = useLanguage();
  const pt = language === 'pt';

  const [reports, setReports] = useState([]);
  const [page, setPage] = useState(1);
  const [limit, setLimit] = useState(8);
  const [total, setTotal] = useState(0);
  const [totalPages, setTotalPages] = useState(1);
  const [filters, setFilters] = useState({
    search: '',
    status: '',
    created_from: '',
    created_to: '',
  });
  const [loading, setLoading] = useState(true);
  const [connectionError, setConnectionError] = useState(null);
  const [opError, setOpError] = useState(null);
  const [opSuccess, setOpSuccess] = useState(null);
  const [exporting, setExporting] = useState(false);

  const [modalOpen, setModalOpen] = useState(false);
  const [activeReportId, setActiveReportId] = useState(null);
  const [detailLoading, setDetailLoading] = useState(false);
  const [detail, setDetail] = useState(null);
  const [localTitle, setLocalTitle] = useState('');
  const [localBody, setLocalBody] = useState('');
  const [localStatus, setLocalStatus] = useState('draft');
  const [saving, setSaving] = useState(false);

  const [catalog, setCatalog] = useState(null);
  const [addSimId, setAddSimId] = useState('');
  const [addTmplId, setAddTmplId] = useState('');
  const [pickSimForResult, setPickSimForResult] = useState('');
  const [resultRows, setResultRows] = useState([]);
  const [addResultId, setAddResultId] = useState('');
  const [dataNoteText, setDataNoteText] = useState('');
  const [attBusy, setAttBusy] = useState(false);

  const loadReports = useCallback(async () => {
    setLoading(true);
    setConnectionError(null);
    setOpError(null);
    try {
      const data = await listReports({
        page,
        limit,
        search: filters.search,
        status: filters.status || null,
        created_from: filters.created_from || null,
        created_to: filters.created_to || null,
      });
      setReports(Array.isArray(data?.items) ? data.items : []);
      setTotal(data?.total || 0);
      setTotalPages(data?.total_pages || data?.pages || 1);
    } catch (err) {
      console.error(err);
      if (isConnectionError(err)) {
        setConnectionError(t('backendConnectionError'));
        setReports([]);
      } else {
        setOpError(
          err.response?.data?.detail ||
            err.message ||
            (pt ? 'falha ao carregar relatórios' : 'failed to load reports')
        );
        setReports([]);
        setTotal(0);
      }
    } finally {
      setLoading(false);
    }
  }, [filters, limit, page, pt, t]);

  useEffect(() => {
    loadReports();
  }, [loadReports]);

  const closeModal = useCallback(() => {
    setModalOpen(false);
    setActiveReportId(null);
    setDetail(null);
    setAddSimId('');
    setAddTmplId('');
    setPickSimForResult('');
    setResultRows([]);
    setAddResultId('');
    setDataNoteText('');
  }, []);

  useEffect(() => {
    if (!modalOpen) return;
    const onKey = (e) => {
      if (e.key === 'Escape') closeModal();
    };
    window.addEventListener('keydown', onKey);
    return () => window.removeEventListener('keydown', onKey);
  }, [modalOpen, closeModal]);

  const loadCatalog = useCallback(async () => {
    if (catalog) return;
    try {
      setConnectionError(null);
      const c = await reportsCatalog();
      setCatalog(c);
    } catch (err) {
      if (isConnectionError(err)) setConnectionError(t('backendConnectionError'));
      else setCatalog({ simulations: [], templates: [] });
    }
  }, [catalog, t]);

  const openReport = async (id) => {
    setActiveReportId(id);
    setModalOpen(true);
    setDetail(null);
    setDetailLoading(true);
    setOpError(null);
    setConnectionError(null);
    await loadCatalog();
    try {
      const d = await getReport(id);
      setDetail(d);
      setLocalTitle(d.title);
      setLocalBody(d.body || '');
      setLocalStatus(d.status || 'draft');
    } catch (err) {
      console.error(err);
      if (isConnectionError(err)) setConnectionError(t('backendConnectionError'));
      else setOpError(err.response?.data?.detail || err.message);
      closeModal();
    } finally {
      setDetailLoading(false);
    }
  };

  const handleCreate = async () => {
    setOpError(null);
    setConnectionError(null);
    try {
      const created = await createReport({
        title: pt ? 'novo relatório' : 'new report',
        body: '',
        status: 'draft',
      });
      await loadReports();
      await openReport(created.id);
    } catch (err) {
      console.error(err);
      if (isConnectionError(err)) setConnectionError(t('backendConnectionError'));
      else setOpError(err.response?.data?.detail || (pt ? 'não foi possível criar' : 'create failed'));
    }
  };

  const saveFields = async () => {
    if (!activeReportId) return;
    setSaving(true);
    setOpError(null);
    setConnectionError(null);
    try {
      const d = await updateReport(activeReportId, {
        title: localTitle,
        body: localBody,
        status: localStatus,
      });
      setDetail(d);
      await loadReports();
    } catch (err) {
      console.error(err);
      if (isConnectionError(err)) setConnectionError(t('backendConnectionError'));
      else setOpError(err.response?.data?.detail || (pt ? 'falha ao guardar' : 'save failed'));
    } finally {
      setSaving(false);
    }
  };

  const handleDeleteReport = async () => {
    if (!activeReportId) return;
    const ok = window.confirm(
      pt ? 'eliminar este relatório e todos os anexos?' : 'delete this report and all attachments?'
    );
    if (!ok) return;
    setConnectionError(null);
    setOpError(null);
    try {
      await deleteReport(activeReportId);
      closeModal();
      await loadReports();
    } catch (err) {
      console.error(err);
      if (isConnectionError(err)) setConnectionError(t('backendConnectionError'));
      else setOpError(err.response?.data?.detail || (pt ? 'falha ao eliminar' : 'delete failed'));
    }
  };

  const refreshDetail = async () => {
    if (!activeReportId) return;
    try {
      const d = await getReport(activeReportId);
      setDetail(d);
    } catch (err) {
      if (isConnectionError(err)) setConnectionError(t('backendConnectionError'));
    }
  };

  useEffect(() => {
    if (!pickSimForResult) {
      setResultRows([]);
      setAddResultId('');
      return;
    }
    let cancelled = false;
    (async () => {
      try {
        const rows = await reportsResultsForSimulation(Number(pickSimForResult));
        if (!cancelled) setResultRows(Array.isArray(rows) ? rows : []);
      } catch {
        if (!cancelled) setResultRows([]);
      }
    })();
    return () => {
      cancelled = true;
    };
  }, [pickSimForResult]);

  const flashSuccess = useCallback((msg) => {
    setOpSuccess(msg);
    setTimeout(() => setOpSuccess(null), 2500);
  }, []);

  const attachSimulation = async () => {
    if (!activeReportId || !addSimId) return;
    setAttBusy(true);
    setOpError(null);
    setConnectionError(null);
    try {
      await addReportAttachment(activeReportId, {
        kind: 'simulation',
        ref_id: String(addSimId),
      });
      setAddSimId('');
      await refreshDetail();
      await loadReports();
      flashSuccess(pt ? 'simulação anexada' : 'simulation attached');
    } catch (err) {
      if (isConnectionError(err)) setConnectionError(t('backendConnectionError'));
      else setOpError(err.response?.data?.detail || (pt ? 'falha no anexo' : 'attach failed'));
    } finally {
      setAttBusy(false);
    }
  };

  const attachTemplate = async () => {
    if (!activeReportId || !addTmplId) return;
    setAttBusy(true);
    setOpError(null);
    setConnectionError(null);
    try {
      await addReportAttachment(activeReportId, {
        kind: 'template',
        ref_id: addTmplId,
      });
      setAddTmplId('');
      await refreshDetail();
      await loadReports();
      flashSuccess(pt ? 'template anexado' : 'template attached');
    } catch (err) {
      if (isConnectionError(err)) setConnectionError(t('backendConnectionError'));
      else setOpError(err.response?.data?.detail || (pt ? 'falha no anexo' : 'attach failed'));
    } finally {
      setAttBusy(false);
    }
  };

  const attachResult = async () => {
    if (!activeReportId || !addResultId) return;
    setAttBusy(true);
    setOpError(null);
    setConnectionError(null);
    try {
      await addReportAttachment(activeReportId, {
        kind: 'result',
        ref_id: String(addResultId),
      });
      setAddResultId('');
      await refreshDetail();
      await loadReports();
      flashSuccess(pt ? 'resultado anexado' : 'result attached');
    } catch (err) {
      if (isConnectionError(err)) setConnectionError(t('backendConnectionError'));
      else setOpError(err.response?.data?.detail || (pt ? 'falha no anexo' : 'attach failed'));
    } finally {
      setAttBusy(false);
    }
  };

  const attachDataNote = async () => {
    if (!activeReportId || !dataNoteText.trim()) return;
    setAttBusy(true);
    setOpError(null);
    setConnectionError(null);
    try {
      await addReportAttachment(activeReportId, {
        kind: 'data_note',
        note: dataNoteText.trim(),
      });
      setDataNoteText('');
      await refreshDetail();
      await loadReports();
      flashSuccess(pt ? 'nota anexada' : 'note attached');
    } catch (err) {
      if (isConnectionError(err)) setConnectionError(t('backendConnectionError'));
      else setOpError(err.response?.data?.detail || (pt ? 'falha no anexo' : 'attach failed'));
    } finally {
      setAttBusy(false);
    }
  };

  const detach = async (attachmentId) => {
    if (!activeReportId) return;
    setAttBusy(true);
    setOpError(null);
    setConnectionError(null);
    try {
      await removeReportAttachment(activeReportId, attachmentId);
      await refreshDetail();
      await loadReports();
      flashSuccess(pt ? 'anexo removido' : 'attachment removed');
    } catch (err) {
      if (isConnectionError(err)) setConnectionError(t('backendConnectionError'));
      else setOpError(err.response?.data?.detail || (pt ? 'falha ao remover' : 'remove failed'));
    } finally {
      setAttBusy(false);
    }
  };

  const handlePreviewPdf = () => {
    setOpError(null);
    if (!detail) {
      setOpError(pt ? 'abra um relatório primeiro.' : 'open a report first.');
      return;
    }
    try {
      const html = buildPreviewHtml(detail, pt);
      const w = window.open('', '_blank');
      if (!w) {
        setOpError(
          pt
            ? 'o navegador bloqueou a janela de pré-visualização. permita pop-ups para este site.'
            : 'browser blocked the preview window. allow pop-ups for this site.'
        );
        return;
      }
      w.document.open();
      w.document.write(html);
      w.document.close();
      w.focus();
      w.onload = () => {
        try {
          w.print();
        } catch {
          // o usuario pode imprimir manualmente via ctrl+p
        }
      };
    } catch (err) {
      setOpError(err.message || (pt ? 'falha ao gerar pré-visualização' : 'preview failed'));
    }
  };

  const handleExportBundle = async () => {
    setOpError(null);
    if (!detail) {
      setOpError(pt ? 'abra um relatório primeiro.' : 'open a report first.');
      return;
    }
    setExporting(true);
    try {
      const zip = new JSZip();
      const reportMeta = {
        id: detail.id,
        title: detail.title,
        status: detail.status,
        created_at: detail.created_at,
        updated_at: detail.updated_at,
        body: detail.body || '',
        exported_at: new Date().toISOString(),
      };
      zip.file('report.json', JSON.stringify(reportMeta, null, 2));
      zip.file('report.md', buildReportMd(detail, pt));
      const atts = Array.isArray(detail.attachments) ? detail.attachments : [];
      zip.file('attachments.json', JSON.stringify(atts, null, 2));

      if (atts.some((a) => a.kind === 'data_note' && a.note)) {
        const notesFolder = zip.folder('notes');
        atts
          .filter((a) => a.kind === 'data_note' && a.note)
          .forEach((a) => {
            notesFolder.file(`nota_${a.id}.txt`, a.note);
          });
      }

      const blob = await zip.generateAsync({ type: 'blob' });
      const url = URL.createObjectURL(blob);
      const filename = `relatorio_${detail.id}_${slugify(detail.title)}.zip`;
      const a = document.createElement('a');
      a.href = url;
      a.download = filename;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      setTimeout(() => URL.revokeObjectURL(url), 1000);
      flashSuccess(pt ? 'pacote exportado' : 'bundle exported');
    } catch (err) {
      setOpError(err.message || (pt ? 'falha ao exportar pacote' : 'export failed'));
    } finally {
      setExporting(false);
    }
  };

  return (
    <div className="tab-content">
      <div className="reports-page">
        {connectionError && <BackendConnectionError message={connectionError} />}

        {opError && (
          <div className="reports-op-error" role="alert">
            {opError}
          </div>
        )}

        {opSuccess && (
          <div className="reports-op-success" role="status">
            {opSuccess}
          </div>
        )}

        <div className="reports-layout">
          <header className="reports-page-header">
            <div className="reports-page-title">
              <ThemeIcon light="folderLight.png" dark="folderDark.png" alt="" className="reports-page-title-icon" />
              <h1 className="reports-page-heading">{pt ? 'Relatórios' : 'Reports'}</h1>
            </div>
            <p className="reports-page-lead">
              {pt
                ? 'Documentos técnicos guardados na base de dados. Clique num relatório para editar o texto e associar simulações, templates, resultados ou notas de dados.'
                : 'Technical documents stored in the database. Click a report to edit text and link simulations, templates, results, or data notes.'}
            </p>
          </header>

          <div className="reports-page-toolbar">
            <button type="button" className="reports-btn-primary" onClick={handleCreate}>
              {pt ? 'Criar relatório' : 'Create report'}
            </button>
          </div>

          <section className="reports-mockup-card" aria-label={pt ? 'Relatórios' : 'Reports'}>
            <div className="reports-toolbar">
              <div className="reports-toolbar-grid">
                <input
                  type="search"
                  className="reports-filter-input"
                  value={filters.search}
                  onChange={(e) => {
                    setPage(1);
                    setFilters((prev) => ({ ...prev, search: e.target.value }));
                  }}
                  placeholder={pt ? 'Buscar por título ou conteúdo…' : 'Search by title or body…'}
                />
                <select
                  className="reports-filter-input"
                  value={filters.status}
                  onChange={(e) => {
                    setPage(1);
                    setFilters((prev) => ({ ...prev, status: e.target.value }));
                  }}
                >
                  <option value="">{pt ? 'Todos os estados' : 'All statuses'}</option>
                  <option value="draft">{statusLabel('draft', pt)}</option>
                  <option value="planned">{statusLabel('planned', pt)}</option>
                  <option value="published">{statusLabel('published', pt)}</option>
                </select>
                <input
                  type="date"
                  className="reports-filter-input"
                  value={filters.created_from}
                  onChange={(e) => {
                    setPage(1);
                    setFilters((prev) => ({ ...prev, created_from: e.target.value }));
                  }}
                />
                <input
                  type="date"
                  className="reports-filter-input"
                  value={filters.created_to}
                  onChange={(e) => {
                    setPage(1);
                    setFilters((prev) => ({ ...prev, created_to: e.target.value }));
                  }}
                />
              </div>
              <div className="reports-toolbar-actions">
                <button
                  type="button"
                  onClick={() => {
                    setPage(1);
                    setFilters({ search: '', status: '', created_from: '', created_to: '' });
                  }}
                  disabled={loading}
                >
                  {pt ? 'Limpar filtros' : 'Clear filters'}
                </button>
                <button type="button" onClick={() => loadReports()} disabled={loading}>
                  {pt ? 'Atualizar lista' : 'Refresh list'}
                </button>
              </div>
            </div>

            {loading ? (
              <p className="reports-status">{pt ? 'A carregar…' : 'Loading…'}</p>
            ) : reports.length === 0 ? (
              <p className="reports-status">
                {pt
                  ? 'Nenhum relatório. Use «Criar relatório» para começar.'
                  : 'No reports yet. Use «Create report» to start.'}
              </p>
            ) : (
              <ul className="reports-mock-list reports-mock-list-clickable">
                {reports.map((row) => (
                  <li key={row.id}>
                    <button
                      type="button"
                      className="reports-row-hit"
                      onClick={() => openReport(row.id)}
                    >
                      <span className="reports-row-title">{row.title}</span>
                      <span className={`reports-status-pill status-${row.status}`}>
                        {statusLabel(row.status, pt)}
                      </span>
                      <span className="reports-row-meta">
                        {row.attachment_count ?? 0}{' '}
                        {pt ? 'Anexos' : 'attachments'} ·{' '}
                        {row.updated_at
                          ? new Date(row.updated_at).toLocaleString(pt ? 'pt-PT' : 'en-GB')
                          : '—'}
                      </span>
                    </button>
                  </li>
                ))}
              </ul>
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
              label={pt ? 'Relatórios' : 'Reports'}
              pt={pt}
            />

          </section>
        </div>

        {modalOpen && (
          <div
            className="reports-modal-overlay"
            role="presentation"
            onClick={(e) => {
              if (e.target === e.currentTarget) closeModal();
            }}
          >
            <div
              className="reports-modal"
              role="dialog"
              aria-modal="true"
              aria-labelledby="reports-modal-title"
            >
              <div className="reports-modal-header">
                <h2 id="reports-modal-title">{pt ? 'Editar relatório' : 'Edit report'}</h2>
                <button type="button" className="reports-modal-close" onClick={closeModal}>
                  ×
                </button>
              </div>

              {detailLoading ? (
                <p className="reports-modal-loading">{pt ? 'A carregar…' : 'Loading…'}</p>
              ) : detail ? (
                <div className="reports-modal-body">
                  <label className="reports-field">
                    <span>{pt ? 'título' : 'title'}</span>
                    <input
                      type="text"
                      value={localTitle}
                      onChange={(e) => setLocalTitle(e.target.value)}
                      maxLength={500}
                    />
                  </label>
                  <label className="reports-field">
                    <span>{pt ? 'estado' : 'status'}</span>
                    <select
                      value={localStatus}
                      onChange={(e) => setLocalStatus(e.target.value)}
                    >
                      <option value="draft">{statusLabel('draft', pt)}</option>
                      <option value="planned">{statusLabel('planned', pt)}</option>
                      <option value="published">{statusLabel('published', pt)}</option>
                    </select>
                  </label>
                  <label className="reports-field reports-field-grow">
                    <span>{pt ? 'conteúdo' : 'body'}</span>
                    <textarea
                      value={localBody}
                      onChange={(e) => setLocalBody(e.target.value)}
                      rows={8}
                      placeholder={
                        pt
                          ? 'sumário, método, conclusões, referências…'
                          : 'summary, method, conclusions, references…'
                      }
                    />
                  </label>

                  <div className="reports-modal-actions">
                    <button type="button" onClick={saveFields} disabled={saving}>
                      {saving ? (pt ? 'a guardar…' : 'saving…') : pt ? 'guardar texto' : 'save text'}
                    </button>
                    <button
                      type="button"
                      className="reports-btn-danger"
                      onClick={handleDeleteReport}
                    >
                      {pt ? 'eliminar relatório' : 'delete report'}
                    </button>
                  </div>

                  <div className="reports-actions-mock">
                    <button type="button" onClick={handlePreviewPdf}>
                      {pt ? 'pré-visualizar pdf' : 'preview pdf'}
                    </button>
                    <button type="button" onClick={handleExportBundle} disabled={exporting}>
                      {exporting
                        ? (pt ? 'a exportar…' : 'exporting…')
                        : (pt ? 'exportar pacote' : 'export bundle')}
                    </button>
                  </div>

                  <h3 className="reports-attach-heading">{pt ? 'anexos' : 'attachments'}</h3>
                  <ul className="reports-attach-list">
                    {detail.attachments?.length ? (
                      detail.attachments.map((a) => (
                        <li key={a.id}>
                          <div className="reports-attach-top">
                            <div className="reports-attach-main">
                              <span className="reports-attach-kind">{kindLabel(a.kind, pt)}</span>
                              <span className="reports-attach-ref">{a.display_ref}</span>
                            </div>
                            <button
                              type="button"
                              className="reports-attach-remove"
                              onClick={() => detach(a.id)}
                              disabled={attBusy}
                            >
                              {pt ? 'remover' : 'remove'}
                            </button>
                          </div>
                          {a.note && a.kind !== 'data_note' && (
                            <span className="reports-attach-note">{a.note}</span>
                          )}
                          {a.kind === 'data_note' && a.note && (
                            <pre className="reports-attach-data">{a.note}</pre>
                          )}
                        </li>
                      ))
                    ) : (
                      <li className="reports-attach-empty">
                        {pt ? 'sem anexos.' : 'no attachments.'}
                      </li>
                    )}
                  </ul>

                  <div className="reports-attach-add">
                    <h4>{pt ? 'adicionar simulação' : 'add simulation'}</h4>
                    <div className="reports-attach-row">
                      <select
                        value={addSimId}
                        onChange={(e) => setAddSimId(e.target.value)}
                        aria-label={pt ? 'simulação' : 'simulation'}
                      >
                        <option value="">{pt ? '— escolher —' : '— choose —'}</option>
                        {(catalog?.simulations || []).map((s) => (
                          <option key={s.id} value={String(s.id)}>
                            #{s.id} · {s.name} ({s.status})
                          </option>
                        ))}
                      </select>
                      <button type="button" onClick={attachSimulation} disabled={attBusy || !addSimId}>
                        {pt ? 'anexar' : 'attach'}
                      </button>
                    </div>

                    <h4>{pt ? 'adicionar template .bed' : 'add .bed template'}</h4>
                    <div className="reports-attach-row">
                      <select
                        value={addTmplId}
                        onChange={(e) => setAddTmplId(e.target.value)}
                        aria-label={pt ? 'template' : 'template'}
                      >
                        <option value="">{pt ? '— escolher —' : '— choose —'}</option>
                        {(catalog?.templates || []).map((x) => (
                          <option key={x.id} value={x.id}>
                            {x.name} [{x.tag}]
                          </option>
                        ))}
                      </select>
                      <button type="button" onClick={attachTemplate} disabled={attBusy || !addTmplId}>
                        {pt ? 'anexar' : 'attach'}
                      </button>
                    </div>

                    <h4>{pt ? 'adicionar resultado (orm)' : 'add result (orm)'}</h4>
                    <div className="reports-attach-row reports-attach-stack">
                      <select
                        value={pickSimForResult}
                        onChange={(e) => setPickSimForResult(e.target.value)}
                        aria-label={pt ? 'simulação para resultados' : 'simulation for results'}
                      >
                        <option value="">{pt ? '— simulação —' : '— simulation —'}</option>
                        {(catalog?.simulations || []).map((s) => (
                          <option key={s.id} value={String(s.id)}>
                            #{s.id} · {s.name}
                          </option>
                        ))}
                      </select>
                      <select
                        value={addResultId}
                        onChange={(e) => setAddResultId(e.target.value)}
                        aria-label={pt ? 'resultado' : 'result'}
                      >
                        <option value="">{pt ? '— resultado —' : '— result —'}</option>
                        {resultRows.map((r) => (
                          <option key={r.id} value={String(r.id)}>
                            #{r.id} · {r.name} ({r.result_type})
                            {r.value != null ? ` = ${r.value}${r.unit ? ` ${r.unit}` : ''}` : ''}
                          </option>
                        ))}
                      </select>
                      <button type="button" onClick={attachResult} disabled={attBusy || !addResultId}>
                        {pt ? 'anexar' : 'attach'}
                      </button>
                    </div>

                    <h4>{pt ? 'nota / dados livres' : 'free-form data note'}</h4>
                    <div className="reports-attach-row reports-attach-stack">
                      <textarea
                        rows={4}
                        value={dataNoteText}
                        onChange={(e) => setDataNoteText(e.target.value)}
                        placeholder={
                          pt
                            ? 'cole métricas, tabelas, json, observações…'
                            : 'paste metrics, tables, json, notes…'
                        }
                      />
                      <button
                        type="button"
                        onClick={attachDataNote}
                        disabled={attBusy || !dataNoteText.trim()}
                      >
                        {pt ? 'anexar nota' : 'attach note'}
                      </button>
                    </div>
                  </div>
                </div>
              ) : null}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
