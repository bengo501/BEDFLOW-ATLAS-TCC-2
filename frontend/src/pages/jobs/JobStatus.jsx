import { useState, useEffect } from 'react'
import { listJobs, cancelJobs, restartJobs } from '../services/api'
import ThemeIcon from './ThemeIcon'
import BackendConnectionError from './BackendConnectionError'
import { useLanguage } from '../context/LanguageContext'
import '../styles/MeshViewer3DPage.css'
import '../styles/CasosCFD.css'

const ACTIVE_JOB_STATUSES = new Set(['queued', 'running'])

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

function JobStatus({ currentJob }) {
  const { t, language } = useLanguage()
  const pt = language === 'pt'
  const [jobs, setJobs] = useState([])
  const [selectedJob, setSelectedJob] = useState(null)
  const [refreshing, setRefreshing] = useState(false)
  const [jobsActionBusy, setJobsActionBusy] = useState(false)
  const [connectionError, setConnectionError] = useState(null)
  const [actionMessage, setActionMessage] = useState(null)

  useEffect(() => {
    void loadJobs()
    const sec = parseInt(localStorage.getItem('jobsPollIntervalSec'), 10)
    const pollSec = Number.isFinite(sec) && sec >= 3 && sec <= 120 ? sec : 5
    const interval = setInterval(() => void loadJobs({ silent: true }), pollSec * 1000)
    return () => clearInterval(interval)
  }, [])

  useEffect(() => {
    if (currentJob) {
      setSelectedJob(currentJob)
    }
  }, [currentJob])

  const loadJobs = async ({ silent = false } = {}) => {
    if (!silent) setRefreshing(true)
    try {
      const jobsList = await listJobs()
      setJobs(jobsList)
      setConnectionError(null)

      if (selectedJob) {
        const updated = jobsList.find((j) => j.job_id === selectedJob.job_id)
        if (updated) {
          setSelectedJob(updated)
        }
      }
    } catch (error) {
      console.error('erro ao carregar jobs:', error)
      setConnectionError(t('backendConnectionError'))
    } finally {
      if (!silent) setRefreshing(false)
    }
  }

  const handleRestartJobs = async () => {
    const ok = window.confirm(
      pt
        ? 'reiniciar todos os jobs com estado falhou? eles voltam para a fila.'
        : 'restart all failed jobs? they will return to the queue.'
    )
    if (!ok) return
    setJobsActionBusy(true)
    setActionMessage(null)
    try {
      const res = await restartJobs()
      setActionMessage(res?.message || (pt ? 'jobs reiniciados' : 'jobs restarted'))
      await loadJobs({ silent: true })
    } catch (error) {
      console.error('erro ao reiniciar jobs:', error)
      setConnectionError(t('backendConnectionError'))
    } finally {
      setJobsActionBusy(false)
    }
  }

  const handleCancelJobs = async () => {
    const ok = window.confirm(
      pt
        ? 'encerrar todos os jobs em fila ou em execução?'
        : 'terminate all queued or running jobs?'
    )
    if (!ok) return
    setJobsActionBusy(true)
    setActionMessage(null)
    try {
      const res = await cancelJobs()
      setActionMessage(res?.message || (pt ? 'jobs encerrados' : 'jobs terminated'))
      await loadJobs({ silent: true })
    } catch (error) {
      console.error('erro ao encerrar jobs:', error)
      setConnectionError(t('backendConnectionError'))
    } finally {
      setJobsActionBusy(false)
    }
  }

  const getStatusIcon = (status) => {
    switch (status) {
      case 'queued': return '⏳'
      case 'running': return '🔄'
      case 'completed': return '✅'
      case 'failed': return '❌'
      default: return '❔'
    }
  }

  const getStatusColor = (status) => {
    switch (status) {
      case 'queued': return 'status-queued'
      case 'running': return 'status-running'
      case 'completed': return 'status-completed'
      case 'failed': return 'status-failed'
      default: return ''
    }
  }

  const getJobTypeLabel = (jobType) => {
    switch (jobType) {
      case 'compile':
        return (
          <>
            <ThemeIcon light="textEditorLight.png" dark="textEditor.png" alt="compilação" className="status-icon" />
            {pt ? 'Compilação' : 'Compile'}
          </>
        )
      case 'generate_model':
        return pt ? 'Modelo 3D' : '3D model'
      case 'simulation':
        return pt ? 'Simulação' : 'Simulation'
      case 'full_pipeline':
        return pt ? 'Pipeline completo' : 'Full pipeline'
      default:
        return jobType
    }
  }

  const dateLocale = pt ? 'pt-BR' : 'en-US'
  const activeJobs = jobs.filter((j) => ACTIVE_JOB_STATUSES.has(j.status))
  const historyJobs = jobs.filter((j) => !ACTIVE_JOB_STATUSES.has(j.status))

  return (
    <div className="job-status-container">
      <header className="jobs-page-header">
        <div className="jobs-page-header-row">
          <div className="jobs-page-title">
            <ThemeIcon light="job_monitor_clock_white.png" dark="job_monitor_clock_white.png" alt="" className="jobs-page-title-icon" />
            <h1 className="jobs-page-heading">{pt ? 'Monitoramento de jobs' : 'Job monitoring'}</h1>
          </div>
        </div>
      </header>

      {actionMessage && (
        <p className="jobs-action-message" role="status">{actionMessage}</p>
      )}

      {connectionError && <BackendConnectionError message={connectionError} />}

      <section className="jobs-panel ui-raised-surface" aria-label={pt ? 'jobs ativos' : 'active jobs'}>
        <div className="jobs-panel-head">
          <h3 className="jobs-panel-title">
            {pt ? `fila e execução (${activeJobs.length})` : `queue and running (${activeJobs.length})`}
          </h3>
          <div className="jobs-panel-toolbar caso-acoes">
            <button
              type="button"
              className="btn-mode-option"
              onClick={() => void loadJobs()}
              disabled={refreshing || jobsActionBusy}
              aria-busy={refreshing || undefined}
            >
              <IconRefresh className="btn-icon" aria-hidden />
              {refreshing ? '…' : pt ? 'atualizar' : 'refresh'}
            </button>
            <button
              type="button"
              className="btn-mode-option"
              onClick={() => void handleRestartJobs()}
              disabled={refreshing || jobsActionBusy}
            >
              {pt ? 'reiniciar jobs' : 'restart jobs'}
            </button>
            <button
              type="button"
              className="btn-mode-option"
              onClick={() => void handleCancelJobs()}
              disabled={refreshing || jobsActionBusy}
            >
              {pt ? 'encerrar jobs' : 'terminate jobs'}
            </button>
          </div>
        </div>

        <div className="jobs-layout">
          <div className="jobs-list jobs-subpanel">
            {activeJobs.length === 0 ? (
              <p className="empty-state">{pt ? 'Nenhum job na fila ou em execução' : 'No queued or running jobs'}</p>
            ) : (
              <div className="jobs-items">
                {activeJobs.map((job) => (
                <div
                  key={job.job_id}
                  className={`job-item ${selectedJob?.job_id === job.job_id ? 'selected' : ''}`}
                  onClick={() => setSelectedJob(job)}
                  onKeyDown={(e) => {
                    if (e.key === 'Enter' || e.key === ' ') setSelectedJob(job)
                  }}
                  role="button"
                  tabIndex={0}
                >
                  <div className="job-header">
                    <span className="job-icon">{getStatusIcon(job.status)}</span>
                    <span className="job-type">{getJobTypeLabel(job.job_type)}</span>
                  </div>

                  <div className={`job-status ${getStatusColor(job.status)}`}>
                    {job.status}
                  </div>

                  <div className="job-progress">
                    <div
                      className="progress-bar"
                      style={{ width: `${job.progress}%` }}
                    />
                    <span className="progress-text">{job.progress}%</span>
                  </div>

                  <div className="job-time">
                    {new Date(job.created_at).toLocaleString(dateLocale)}
                  </div>
                </div>
                ))}
              </div>
            )}
          </div>

          <div className="job-details jobs-subpanel">
          {selectedJob ? (
            <>
              <h3>{pt ? 'Detalhes do job' : 'Job details'}</h3>

              <div className="detail-group">
                <label>{pt ? 'Id:' : 'Id:'}</label>
                <code>{selectedJob.job_id}</code>
              </div>

              <div className="detail-group">
                <label>{pt ? 'Tipo:' : 'Type:'}</label>
                <span>{getJobTypeLabel(selectedJob.job_type)}</span>
              </div>

              <div className="detail-group">
                <label>{pt ? 'Status:' : 'Status:'}</label>
                <span className={`badge ${getStatusColor(selectedJob.status)}`}>
                  {getStatusIcon(selectedJob.status)} {selectedJob.status}
                </span>
              </div>

              <div className="detail-group">
                <label>{pt ? 'Progresso:' : 'Progress:'}</label>
                <div className="progress-bar-large">
                  <div
                    className="progress-fill"
                    style={{ width: `${selectedJob.progress}%` }}
                  />
                  <span className="progress-label">{selectedJob.progress}%</span>
                </div>
              </div>

              <div className="detail-group">
                <label>{pt ? 'Criado em:' : 'Created:'}</label>
                <span>{new Date(selectedJob.created_at).toLocaleString(dateLocale)}</span>
              </div>

              <div className="detail-group">
                <label>{pt ? 'Atualizado em:' : 'Updated:'}</label>
                <span>{new Date(selectedJob.updated_at).toLocaleString(dateLocale)}</span>
              </div>

              {selectedJob.output_files && selectedJob.output_files.length > 0 && (
                <div className="detail-group">
                  <label>{pt ? 'Arquivos gerados:' : 'Output files:'}</label>
                  <ul className="output-files">
                    {selectedJob.output_files.map((file, idx) => (
                      <li key={idx}>
                        <code>{file}</code>
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              {selectedJob.error_message && (
                <div className="detail-group">
                  <label>{pt ? 'Erro:' : 'Error:'}</label>
                  <div className="error-message">
                    {selectedJob.error_message}
                  </div>
                </div>
              )}

              {selectedJob.metadata && Object.keys(selectedJob.metadata).length > 0 && (
                <div className="detail-group">
                  <label>metadata:</label>
                  <pre className="metadata">
                    {JSON.stringify(selectedJob.metadata, null, 2)}
                  </pre>
                </div>
              )}
            </>
          ) : (
            <p className="empty-state">{pt ? 'Selecione um job para ver detalhes' : 'Select a job to see details'}</p>
          )}
          </div>
        </div>
      </section>

      <section className="jobs-panel jobs-panel--history ui-raised-surface" aria-label={pt ? 'histórico de jobs' : 'job history'}>
        <h3 className="jobs-panel-title">
          {pt ? `jobs executados (${historyJobs.length})` : `finished jobs (${historyJobs.length})`}
        </h3>
        <p className="jobs-panel-hint">
          {pt
            ? 'concluídos, falhados, cancelados e outros estados finais.'
            : 'completed, failed, cancelled and other terminal states.'}
        </p>
        {historyJobs.length === 0 ? (
          <p className="empty-state">{pt ? 'Nenhum job finalizado ainda' : 'No finished jobs yet'}</p>
        ) : (
          <div className="jobs-history-items">
            {historyJobs.map((job) => (
              <div
                key={job.job_id}
                className={`job-item job-item--compact ${selectedJob?.job_id === job.job_id ? 'selected' : ''}`}
                onClick={() => setSelectedJob(job)}
                onKeyDown={(e) => {
                  if (e.key === 'Enter' || e.key === ' ') setSelectedJob(job)
                }}
                role="button"
                tabIndex={0}
              >
                <div className="job-header">
                  <span className="job-icon">{getStatusIcon(job.status)}</span>
                  <span className="job-type">{getJobTypeLabel(job.job_type)}</span>
                </div>
                <div className={`job-status ${getStatusColor(job.status)}`}>{job.status}</div>
                <div className="job-time">{new Date(job.created_at).toLocaleString(dateLocale)}</div>
              </div>
            ))}
          </div>
        )}
      </section>
    </div>
  )
}

export default JobStatus

