export function IconRefresh({ className }) {
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

export function isConnectionError(err) {
  if (!err) return false
  const noResponse = !err.response && !!err.request
  const network =
    err.code === 'ERR_NETWORK' ||
    err.code === 'ECONNABORTED' ||
    (typeof err.message === 'string' && err.message.toLowerCase().includes('network'))
  return noResponse || network
}

export function formatDurationSeconds(sec, language) {
  if (typeof sec !== 'number' || sec < 0 || Number.isNaN(sec)) return '—'
  const s = Math.floor(sec)
  const h = Math.floor(s / 3600)
  const m = Math.floor((s % 3600) / 60)
  if (h > 0) return language === 'pt' ? `${h}h ${m}m` : `${h}h ${m}m`
  if (m > 0) return language === 'pt' ? `${m}m` : `${m}m`
  return language === 'pt' ? `${s}s` : `${s}s`
}

export function mapApiSimulation(item, language) {
  const created = item.created_at ? new Date(item.created_at) : null
  const createdDate = created
    ? created.toLocaleString(language === 'pt' ? 'pt-BR' : 'en-US')
    : '—'
  return {
    id: item.id,
    name: item.name,
    description: item.description || '',
    status: item.status,
    regime: item.regime,
    createdDate,
    duration: formatDurationSeconds(item.execution_time, language),
    bedId: item.bed_id,
    progress: typeof item.progress === 'number' ? item.progress : 0,
    raw: item,
  }
}

export function getSimStatusBadgeClass(status) {
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

export function getStatusText(status, language) {
  const pt = language === 'pt'
  switch (status) {
    case 'completed':
      return pt ? 'concluída' : 'completed'
    case 'running':
      return pt ? 'em execução' : 'running'
    case 'pending':
      return pt ? 'pendente' : 'pending'
    case 'failed':
      return pt ? 'falhou' : 'failed'
    default:
      return status
  }
}

export function formatBytes(bytes) {
  if (typeof bytes !== 'number' || bytes < 0) return '—'
  if (bytes < 1024) return `${bytes} B`
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`
}

export function slugify(s) {
  return String(s || 'simulacao')
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '')
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/^-+|-+$/g, '')
    .slice(0, 60) || 'simulacao'
}
