import { useCallback, useEffect, useState } from 'react';
import { useLanguage } from '../context/LanguageContext';
import { getDatabasePanel, postDatabasePanelEvent } from '../services/api';
import BackendConnectionError from './BackendConnectionError';
import ThemeIcon from './ThemeIcon';
import './DatabasePage.css';

function isConnectionError(err) {
  if (!err) return false;
  const noResponse = !err.response && !!err.request;
  const network =
    err.code === 'ERR_NETWORK' ||
    err.code === 'ECONNABORTED' ||
    (typeof err.message === 'string' && err.message.toLowerCase().includes('network'));
  return noResponse || network;
}

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

function IconLink({ className }) {
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
      <path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71" />
      <path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71" />
    </svg>
  );
}

function IconCloudUpload({ className }) {
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
      <path d="M4 14.899A7 7 0 1 1 15.71 8h1.79a4.5 4.5 0 0 1 2.5 8.242" />
      <path d="M12 12v9" />
      <path d="m16 16-4-4-4 4" />
    </svg>
  );
}

function eventLabel(type, pt) {
  if (type === 'backup_request') return pt ? 'Pedido de backup' : 'Backup request';
  if (type === 'connection_test') return pt ? 'Teste de ligação' : 'Connection test';
  return type;
}

/**
 * painel banco de dados: contagens reais (sqlalchemy) e registo de eventos em admin_panel_events.
 */
export default function DatabasePage() {
  const { language, t } = useLanguage();
  const pt = language === 'pt';

  const [panel, setPanel] = useState(null);
  const [loading, setLoading] = useState(true);
  const [connectionError, setConnectionError] = useState(null);
  const [opError, setOpError] = useState(null);
  const [actionLoading, setActionLoading] = useState(false);

  const loadPanel = useCallback(async () => {
    setLoading(true);
    setConnectionError(null);
    setOpError(null);
    try {
      const data = await getDatabasePanel();
      setPanel(data);
    } catch (err) {
      console.error(err);
      if (isConnectionError(err)) {
        setConnectionError(t('backendConnectionError'));
        setPanel(null);
      } else {
        setOpError(
          err.response?.data?.detail ||
            err.message ||
            (pt ? 'Não foi possível carregar o painel.' : 'Could not load panel.')
        );
      }
    } finally {
      setLoading(false);
    }
  }, [pt, t]);

  useEffect(() => {
    loadPanel();
  }, [loadPanel]);

  const runAction = async (eventType) => {
    setActionLoading(true);
    setOpError(null);
    setConnectionError(null);
    try {
      await postDatabasePanelEvent(eventType);
      await loadPanel();
    } catch (err) {
      console.error(err);
      if (isConnectionError(err)) setConnectionError(t('backendConnectionError'));
      else
        setOpError(
          err.response?.data?.detail || (pt ? 'A ação falhou.' : 'Action failed.')
        );
    } finally {
      setActionLoading(false);
    }
  };

  const counts = panel?.counts;
  const rows =
    counts != null
      ? [
          [
            pt ? 'Leitos (tabela beds)' : 'Beds table',
            String(counts.beds),
            pt ? 'Registos' : 'Rows',
          ],
          [
            pt ? 'Simulações (simulations)' : 'Simulations',
            String(counts.simulations),
            pt ? 'Registos' : 'Rows',
          ],
          [
            pt ? 'Resultados (results)' : 'Results',
            String(counts.results),
            pt ? 'Registos' : 'Rows',
          ],
          [
            pt ? 'Templates .bed (bed_templates)' : 'Bed templates',
            String(counts.bed_templates),
            pt ? 'Registos' : 'Rows',
          ],
        ]
      : [];

  const integ = panel?.integrations || {};
  const integRows = [
    [
      pt ? 'Redis (filas / cache)' : 'Redis (queues / cache)',
      integ.redis || '—',
      pt ? 'Estado' : 'Status',
    ],
    [
      pt ? 'Armazenamento de objetos (S3 / MinIO)' : 'Object storage (S3 / MinIO)',
      integ.object_storage || '—',
      pt ? 'Estado' : 'Status',
    ],
  ];

  return (
    <div className="tab-content">
      <div className="database-page">
        {connectionError && <BackendConnectionError message={connectionError} />}

        {opError && (
          <div className="database-op-error" role="alert">
            {opError}
          </div>
        )}

        <div className="database-page-heading" aria-label={pt ? 'banco de dados' : 'database'}>
          <ThemeIcon
            light="database-01-svgrepo-com.svg"
            dark="database-01-svgrepo-com.svg"
            alt=""
            className="database-page-heading-icon"
            location="page"
          />
          <h2 className="database-page-title">{pt ? 'Banco de dados' : 'Database'}</h2>
        </div>

        <div className="database-layout">
          <section
            className="database-mockup-card"
            aria-label={pt ? 'Painel do motor SQL' : 'SQL engine panel'}
          >
            <p className="database-mockup-lead">
              {pt
                ? 'Visão operacional do SQLite/PostgreSQL usado pela API: contagens das tabelas principais e histórico de pedidos feitos a partir desta página.'
                : 'Operational view of the SQLite/PostgreSQL used by the API: main table counts and history of requests made from this page.'}
            </p>

            {loading ? (
              <p className="database-status">{pt ? 'A carregar…' : 'Loading…'}</p>
            ) : panel ? (
              <>
                <div
                  className={`database-connection-banner ${panel.connected ? 'ok' : 'bad'}`}
                  role="status"
                >
                  <span className="database-connection-label">
                    {pt ? 'Motor SQL' : 'SQL engine'}
                  </span>
                  <span className="database-connection-value">{panel.database_display}</span>
                  <span className="database-connection-badge">
                    {panel.connected
                      ? pt
                        ? 'Ligado'
                        : 'Connected'
                      : pt
                        ? 'Indisponível'
                        : 'Unavailable'}
                  </span>
                  {panel.checked_at && (
                    <span className="database-checked-at">
                      {pt ? 'Verificado:' : 'Checked:'}{' '}
                      {new Date(panel.checked_at).toLocaleString(pt ? 'pt-PT' : 'en-GB')}
                    </span>
                  )}
                </div>
                {panel.error && (
                  <p className="database-panel-error" role="alert">
                    {panel.error}
                  </p>
                )}

                <h3 className="database-subheading">
                  {pt ? 'Dados persistidos (ORM)' : 'Persisted data (ORM)'}
                </h3>
                <ul className="database-mock-list">
                  {rows.map(([title, value, kind]) => (
                    <li key={title}>
                      <span>{title}</span>
                      <span>
                        {value} · {kind}
                      </span>
                    </li>
                  ))}
                </ul>

                <h3 className="database-subheading">
                  {pt ? 'Integrações externas' : 'External integrations'}
                </h3>
                <ul className="database-mock-list database-mock-list-muted">
                  {integRows.map(([title, value, kind]) => (
                    <li key={title}>
                      <span>{title}</span>
                      <span>
                        {value} · {kind}
                      </span>
                    </li>
                  ))}
                </ul>

                <h3 className="database-subheading">
                  {pt ? 'Registo de ações (admin_panel_events)' : 'Action log (admin_panel_events)'}
                </h3>
                {panel.recent_events?.length ? (
                  <ul className="database-events-list">
                    {panel.recent_events.map((ev) => (
                      <li key={ev.id}>
                        <span className="database-events-type">{eventLabel(ev.event_type, pt)}</span>
                        <time dateTime={ev.created_at}>
                          {ev.created_at
                            ? new Date(ev.created_at).toLocaleString(pt ? 'pt-PT' : 'en-GB')
                            : '—'}
                        </time>
                        {ev.detail && (
                          <span className="database-events-detail">{ev.detail}</span>
                        )}
                      </li>
                    ))}
                  </ul>
                ) : (
                  <p className="database-events-empty">
                    {pt
                      ? 'Ainda não há eventos. Use os botões abaixo para registar pedidos.'
                      : 'No events yet. Use the buttons below to log requests.'}
                  </p>
                )}

                <div className="database-actions-mock">
                  <button
                    type="button"
                    className="database-btn-with-icon"
                    onClick={() => loadPanel()}
                    disabled={loading || actionLoading}
                  >
                    <IconRefresh className="database-btn-svg" />
                    {pt ? 'Atualizar' : 'Refresh'}
                  </button>
                  <button
                    type="button"
                    className="database-btn-with-icon"
                    onClick={() => runAction('connection_test')}
                    disabled={actionLoading || !!connectionError}
                  >
                    <IconLink className="database-btn-svg" />
                    {pt ? 'Testar ligação' : 'Test connection'}
                  </button>
                  <button
                    type="button"
                    className="database-btn-with-icon"
                    onClick={() => runAction('backup_request')}
                    disabled={actionLoading || !!connectionError}
                  >
                    <IconCloudUpload className="database-btn-svg" />
                    {pt ? 'Pedir backup manual' : 'Request manual backup'}
                  </button>
                </div>
                <p className="database-actions-hint">
                  {pt
                    ? 'O backup manual apenas regista o pedido na base de dados; a cópia física (pg_dump, ficheiro SQLite, etc.) deve ser feita à parte nos seus scripts de operação.'
                    : 'Manual backup only logs the request in the database; physical backup (pg_dump, SQLite file copy, etc.) must be done separately in your ops scripts.'}
                </p>
              </>
            ) : null}
          </section>
        </div>
      </div>
    </div>
  );
}
