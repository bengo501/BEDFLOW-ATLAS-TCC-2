import './PaginationControls.css'

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

export default function PaginationControls({
  page = 1,
  totalPages = 1,
  total = 0,
  limit = 20,
  limitOptions = [8, 12, 20, 50],
  loading = false,
  onPageChange,
  onLimitChange,
  label,
  pt = true,
}) {
  const pages = pageWindow(page, totalPages)

  return (
    <div className="pagination-controls">
      <div className="pagination-summary">
        {label ? <span>{label} · </span> : null}
        <span>
          {pt ? 'Total filtrado' : 'Filtered total'}: {total}
        </span>
        <span>
          {pt ? 'Página' : 'Page'} {page} / {totalPages}
        </span>
      </div>

      <div className="pagination-actions">
        {onLimitChange ? (
          <label className="pagination-limit">
            <span>{pt ? 'Itens' : 'Items'}</span>
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
          {pt ? 'Anterior' : 'Previous'}
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
          {pt ? 'Próxima' : 'Next'}
        </button>
      </div>
    </div>
  )
}
