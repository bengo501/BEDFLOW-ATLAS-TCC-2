/**
 * secção do passo 3 com toggle «usar valor do .bed» vs «sobrescrever».
 * useOriginal[key] === true (ou undefined) → só mostra hint do parse.
 */
export default function OverrideSection({
  sectionKey,
  title,
  useOriginal,
  onToggleOriginal,
  parsedHint,
  children,
  t,
}) {
  const fromBed = useOriginal[sectionKey] !== false;

  return (
    <section className="bed-load-config-section">
      <div className="bed-load-section-head">
        <h4>{title}</h4>
        <label className="bed-load-toggle-label">
          <input
            type="checkbox"
            checked={fromBed}
            onChange={(e) => onToggleOriginal(sectionKey, e.target.checked)}
          />
          <span>{t('bedLoadUseSectionOriginal')}</span>
        </label>
      </div>
      {fromBed && parsedHint ? (
        <p className="bed-load-parsed-hint">{parsedHint}</p>
      ) : null}
      {!fromBed ? children : null}
    </section>
  );
}
