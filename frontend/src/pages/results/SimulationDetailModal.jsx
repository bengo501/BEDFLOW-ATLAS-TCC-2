import {
  formatDurationSeconds,
  getStatusText,
} from './resultsShared'
import '../SimulationHistory.css'

export default function SimulationDetailModal({
  pt,
  language,
  viewModalId,
  viewDetail,
  viewLoading,
  actionBusyId,
  onClose,
  onDownload,
}) {
  if (viewModalId == null) return null

  return (
    <div
      className="history-modal-overlay"
      role="dialog"
      aria-modal="true"
      aria-label={pt ? 'detalhes da simulação' : 'simulation details'}
      onClick={onClose}
    >
      <div className="history-modal" onClick={(e) => e.stopPropagation()}>
        <div className="history-modal-header">
          <h2>
            {pt ? 'detalhes da simulação' : 'simulation details'}
            {viewDetail ? ` · #${viewDetail.id}` : ''}
          </h2>
          <button type="button" className="history-modal-close" onClick={onClose} aria-label={pt ? 'fechar' : 'close'}>
            ×
          </button>
        </div>
        <div className="history-modal-body">
          {viewLoading && (
            <div className="history-modal-loading">{pt ? 'carregando…' : 'loading…'}</div>
          )}
          {!viewLoading && viewDetail && (
            <div className="history-detail-grid">
              <div className="history-detail-row">
                <span className="history-detail-label">{pt ? 'nome' : 'name'}</span>
                <span className="history-detail-value">{viewDetail.name || '—'}</span>
              </div>
              <div className="history-detail-row">
                <span className="history-detail-label">{pt ? 'estado' : 'status'}</span>
                <span className="history-detail-value">{getStatusText(viewDetail.status, language)}</span>
              </div>
              <div className="history-detail-row">
                <span className="history-detail-label">{pt ? 'leito' : 'bed'}</span>
                <span className="history-detail-value">#{viewDetail.bed_id}</span>
              </div>
              <div className="history-detail-row">
                <span className="history-detail-label">{pt ? 'regime' : 'regime'}</span>
                <span className="history-detail-value">{viewDetail.regime || '—'}</span>
              </div>
              <div className="history-detail-row">
                <span className="history-detail-label">{pt ? 'criado em' : 'created at'}</span>
                <span className="history-detail-value">
                  {viewDetail.created_at
                    ? new Date(viewDetail.created_at).toLocaleString(pt ? 'pt-BR' : 'en-US')
                    : '—'}
                </span>
              </div>
              <div className="history-detail-row">
                <span className="history-detail-label">{pt ? 'duração' : 'duration'}</span>
                <span className="history-detail-value">
                  {formatDurationSeconds(viewDetail.execution_time, language)}
                </span>
              </div>
              {viewDetail.description ? (
                <div className="history-detail-row history-detail-row-wide">
                  <span className="history-detail-label">{pt ? 'descrição' : 'description'}</span>
                  <span className="history-detail-value">{viewDetail.description}</span>
                </div>
              ) : null}
            </div>
          )}
        </div>
        <div className="history-modal-footer">
          <button
            type="button"
            className="history-modal-btn"
            onClick={() => viewDetail && onDownload(viewDetail.id)}
            disabled={!viewDetail || actionBusyId === viewDetail?.id}
          >
            {pt ? 'baixar json' : 'download json'}
          </button>
          <button type="button" className="history-modal-btn primary" onClick={onClose}>
            {pt ? 'fechar' : 'close'}
          </button>
        </div>
      </div>
    </div>
  )
}
