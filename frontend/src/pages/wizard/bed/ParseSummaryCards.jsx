function Card({ title, children }) {
  return (
    <div className="bed-load-summary-card">
      <h4>{title}</h4>
      {children}
    </div>
  );
}

export default function ParseSummaryCards({ parsed, warnings, t }) {
  if (!parsed) return null;
  const bed = parsed.bed || {};
  const particles = parsed.particles || {};
  const packing = parsed.packing || {};

  return (
    <div className="bed-load-summary-grid">
      {warnings?.length > 0 && (
        <div className="bed-load-warnings" role="status">
          {warnings.map((w) => (
            <p key={w}>{w}</p>
          ))}
        </div>
      )}
      <Card title={t('bedLoadSummaryBed')}>
        <p>ø: {bed.diameter} m</p>
        <p>h: {bed.height} m</p>
        <p>{t('bedLoadWall')}: {bed.wall_thickness} m</p>
        {bed.internal_cylinder_mode && (
          <p>icm: {bed.internal_cylinder_mode}</p>
        )}
      </Card>
      <Card title={t('bedLoadSummaryParticles')}>
        <p>{particles.kind}</p>
        <p>n: {particles.count}</p>
        <p>ø: {particles.diameter} m</p>
      </Card>
      <Card title={t('bedLoadSummaryPacking')}>
        <p>{packing.method}</p>
        {packing.gap != null && <p>gap: {packing.gap}</p>}
      </Card>
      <Card title={t('bedLoadSummaryPipeline')}>
        <p>geometry_mode: {parsed.geometry_mode}</p>
        <p>backend: {parsed.generation_backend}</p>
        {parsed.export?.formats?.length > 0 && (
          <p>export: {parsed.export.formats.join(', ')}</p>
        )}
      </Card>
      {parsed.slice && (
        <Card title={t('bedLoadSummarySlice')}>
          <p>axis: {parsed.slice.slice_axis}</p>
          <p>thickness: {parsed.slice.slice_thickness}</p>
        </Card>
      )}
      {parsed.statistical_2d && (
        <Card title={t('bedLoadSummaryStat2d')}>
          <p>
            {parsed.statistical_2d.domain_width} ×{' '}
            {parsed.statistical_2d.domain_height}
          </p>
          <p>ε: {parsed.statistical_2d.target_porosity}</p>
        </Card>
      )}
    </div>
  );
}
