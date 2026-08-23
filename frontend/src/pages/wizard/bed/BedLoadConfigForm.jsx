import OverrideSection from './OverrideSection';

export default function BedLoadConfigForm({
  state,
  dispatch,
  t,
  hubMode,
}) {
  const { runConfig, parsed, overrides, useOriginal } = state;
  const isPython =
    runConfig.generation_backend === 'python_engine' ||
    String(runConfig.generation_backend).includes('python');
  const geom =
    useOriginal.geometry_mode !== false
      ? parsed?.geometry_mode || 'full_3d'
      : runConfig.geometry_mode;
  const packingFromBed = useOriginal['packing.method'] !== false;
  const packingMethod = packingFromBed
    ? parsed?.packing?.method
    : runConfig.packing_method || runConfig.packingMethodSource;

  const setRun = (patch) =>
    dispatch({ type: 'SET_RUN_CONFIG', patch });

  const toggleOriginal = (key, useOrig) => {
    dispatch({ type: 'SET_USE_ORIGINAL', key, useOriginal: useOrig });
    if (key === 'packing.method' && useOrig) {
      setRun({ packingMethodSource: 'from_bed' });
    }
  };

  const setSliceField = (field, value) => {
    const base = overrides.slice ||
      parsed?.slice || {
        slice_enabled: true,
        slice_axis: 'y',
        slice_position: '0.0',
        slice_thickness: '0.002',
        keep_only_intersecting_particles: true,
      };
    dispatch({
      type: 'SET_OVERRIDE',
      key: 'slice',
      value: { slice: { ...base, [field]: value } },
    });
  };

  const setStatField = (field, value) => {
    const base = overrides.statistical_2d ||
      parsed?.statistical_2d || {
        domain_width: '0.05',
        domain_height: '0.1',
        target_porosity: '0.4',
        tolerance: '0.02',
        max_attempts: '50',
        slice_thickness: '0.002',
        seed: '42',
      };
    dispatch({
      type: 'SET_OVERRIDE',
      key: 'statistical_2d',
      value: { statistical_2d: { ...base, [field]: value } },
    });
  };

  const runTypes = [
    { id: 'compile_only', label: t('bedLoadRunCompile'), show: true },
    { id: 'generate_model', label: t('bedLoadRunGenerate'), show: true },
    { id: 'generate_and_view', label: t('bedLoadRunGenerateView'), show: true },
    {
      id: 'pipeline_full',
      label: t('bedLoadRunPipeline'),
      show: hubMode === 'pipeline_completo',
    },
    {
      id: 'pipeline_blender_cfd',
      label: t('bedLoadRunPipeCfd'),
      show: hubMode === 'pipeline_blender_cfd',
    },
    { id: 'cfd_only', label: t('bedLoadRunCfdOnly'), show: hubMode === 'cfd_only' },
  ].filter((r) => r.show);

  const parsedBackendHint = `${t('bedLoadBackend')}: ${parsed?.generation_backend ?? '—'}`;
  const parsedGeomHint = `geometry_mode: ${parsed?.geometry_mode ?? 'full_3d'}`;
  const parsedPackHint = `${t('bedLoadPackingSource')}: ${parsed?.packing?.method ?? '—'}`;

  return (
    <div className="bed-load-config-form">
      <OverrideSection
        sectionKey="generation_backend"
        title={t('bedLoadBackend')}
        useOriginal={useOriginal}
        onToggleOriginal={toggleOriginal}
        parsedHint={parsedBackendHint}
        t={t}
      >
        <label>
          {t('bedLoadBackend')}
          <select
            value={runConfig.generation_backend}
            onChange={(e) => {
              const v = e.target.value;
              setRun({ generation_backend: v });
              dispatch({
                type: 'SET_OVERRIDE',
                key: 'generation_backend',
                value: { generation_backend: v },
              });
            }}
          >
            <option value="python_engine">{t('bedLoadBackendPython')}</option>
            <option value="blender">{t('bedLoadBackendBlender')}</option>
          </select>
        </label>
      </OverrideSection>

      <OverrideSection
        sectionKey="geometry_mode"
        title={t('bedLoadSectionGeometry')}
        useOriginal={useOriginal}
        onToggleOriginal={toggleOriginal}
        parsedHint={parsedGeomHint}
        t={t}
      >
        <label>
          geometry_mode
          <select
            value={runConfig.geometry_mode}
            onChange={(e) => {
              const v = e.target.value;
              setRun({ geometry_mode: v });
              const patch = { geometry_mode: v };
              if (v === 'pseudo_2d_thin_slice') {
                patch.slice = {
                  slice_enabled: true,
                  slice_axis: parsed?.slice?.slice_axis || 'y',
                  slice_position: String(
                    parsed?.slice?.slice_position ?? '0.0',
                  ),
                  slice_thickness: String(
                    parsed?.slice?.slice_thickness ?? '0.002',
                  ),
                  keep_only_intersecting_particles: true,
                  preserve_original_packing: true,
                };
                dispatch({
                  type: 'SET_OVERRIDE',
                  key: 'geometry_mode',
                  value: patch,
                });
                dispatch({
                  type: 'SET_USE_ORIGINAL',
                  key: 'slice',
                  useOriginal: !!parsed?.slice,
                });
              } else if (v === 'pseudo_2d_statistical') {
                patch.statistical_2d = {
                  domain_width: String(
                    parsed?.statistical_2d?.domain_width ?? '0.05',
                  ),
                  domain_height: String(
                    parsed?.statistical_2d?.domain_height ?? '0.1',
                  ),
                  target_porosity: String(
                    parsed?.statistical_2d?.target_porosity ?? '0.4',
                  ),
                  tolerance: String(
                    parsed?.statistical_2d?.tolerance ?? '0.02',
                  ),
                  max_attempts: String(
                    parsed?.statistical_2d?.max_attempts ?? '50',
                  ),
                  slice_thickness: String(
                    parsed?.statistical_2d?.slice_thickness ?? '0.002',
                  ),
                  seed: String(parsed?.statistical_2d?.seed ?? '42'),
                };
                dispatch({
                  type: 'SET_OVERRIDE',
                  key: 'geometry_mode',
                  value: patch,
                });
              } else {
                dispatch({
                  type: 'SET_OVERRIDE',
                  key: 'geometry_mode',
                  value: patch,
                });
              }
            }}
          >
            <option value="full_3d">full_3d</option>
            <option value="pseudo_2d_thin_slice">pseudo_2d_thin_slice</option>
            <option value="pseudo_2d_statistical">pseudo_2d_statistical</option>
          </select>
        </label>
        {runConfig.geometry_mode === 'pseudo_2d_statistical' &&
          !(
            runConfig.generation_backend === 'python_engine' ||
            String(runConfig.generation_backend).includes('python')
          ) && (
          <p className="bed-load-hint bed-load-hint--warn">
            {t('bedLoadStatisticalPythonOnly')}
          </p>
        )}
      </OverrideSection>

      <OverrideSection
        sectionKey="packing.method"
        title={t('bedLoadSectionPacking')}
        useOriginal={useOriginal}
        onToggleOriginal={(key, useOrig) => {
          toggleOriginal(key, useOrig);
          if (!useOrig && runConfig.packingMethodSource === 'from_bed') {
            setRun({
              packingMethodSource: 'hexagonal_3d',
              packing_method: parsed?.packing?.method || 'hexagonal_3d',
            });
          }
        }}
        parsedHint={parsedPackHint}
        t={t}
      >
        <label>
          {t('bedLoadPackingSource')}
          <select
            value={
              runConfig.packingMethodSource === 'from_bed'
                ? runConfig.packing_method || 'hexagonal_3d'
                : runConfig.packingMethodSource
            }
            onChange={(e) => {
              const m = e.target.value;
              setRun({
                packingMethodSource: m,
                packing_method: m,
              });
              dispatch({
                type: 'SET_OVERRIDE',
                key: 'packing.method',
                value: { packing: { method: m } },
              });
            }}
          >
            <option value="spherical_packing">spherical_packing</option>
            <option value="hexagonal_3d">hexagonal_3d</option>
            <option value="rigid_body">rigid_body</option>
            <option value="dem">dem</option>
          </select>
        </label>
        {(packingMethod === 'rigid_body' || packingMethod === 'dem') && (
          <p className="bed-load-hint">{t('bedLoadPackingPhysicsHint')}</p>
        )}
      </OverrideSection>

      {geom === 'pseudo_2d_thin_slice' && (
        <OverrideSection
          sectionKey="slice"
          title={t('bedLoadSectionSlice')}
          useOriginal={useOriginal}
          onToggleOriginal={toggleOriginal}
          parsedHint={
            parsed?.slice
              ? `axis: ${parsed.slice.slice_axis}, thickness: ${parsed.slice.slice_thickness}`
              : t('bedLoadDiffEmpty')
          }
          t={t}
        >
          <label>
            slice_axis
            <select
              value={
                overrides.slice?.slice_axis ||
                parsed?.slice?.slice_axis ||
                'y'
              }
              onChange={(e) => setSliceField('slice_axis', e.target.value)}
            >
              <option value="x">x</option>
              <option value="y">y</option>
              <option value="z">z</option>
            </select>
          </label>
          <label>
            slice_thickness (m)
            <input
              type="text"
              value={
                overrides.slice?.slice_thickness ??
                parsed?.slice?.slice_thickness ??
                '0.002'
              }
              onChange={(e) =>
                setSliceField('slice_thickness', e.target.value)
              }
            />
          </label>
          <label>
            slice_position
            <input
              type="text"
              value={
                overrides.slice?.slice_position ??
                parsed?.slice?.slice_position ??
                '0.0'
              }
              onChange={(e) =>
                setSliceField('slice_position', e.target.value)
              }
            />
          </label>
        </OverrideSection>
      )}

      {geom === 'pseudo_2d_statistical' && (
        <OverrideSection
          sectionKey="statistical_2d"
          title={t('bedLoadSectionStat2d')}
          useOriginal={useOriginal}
          onToggleOriginal={toggleOriginal}
          parsedHint={
            parsed?.statistical_2d
              ? `ε: ${parsed.statistical_2d.target_porosity}`
              : t('bedLoadDiffEmpty')
          }
          t={t}
        >
          <label>
            domain_width
            <input
              type="text"
              value={
                overrides.statistical_2d?.domain_width ??
                parsed?.statistical_2d?.domain_width ??
                '0.05'
              }
              onChange={(e) => setStatField('domain_width', e.target.value)}
            />
          </label>
          <label>
            domain_height
            <input
              type="text"
              value={
                overrides.statistical_2d?.domain_height ??
                parsed?.statistical_2d?.domain_height ??
                '0.1'
              }
              onChange={(e) => setStatField('domain_height', e.target.value)}
            />
          </label>
          <label>
            target_porosity
            <input
              type="text"
              value={
                overrides.statistical_2d?.target_porosity ??
                parsed?.statistical_2d?.target_porosity ??
                '0.4'
              }
              onChange={(e) =>
                setStatField('target_porosity', e.target.value)
              }
            />
          </label>
        </OverrideSection>
      )}

      <OverrideSection
        sectionKey="export"
        title={t('bedLoadSectionExport')}
        useOriginal={useOriginal}
        onToggleOriginal={toggleOriginal}
        parsedHint={
          parsed?.export?.formats?.length
            ? parsed.export.formats.join(', ')
            : 'stl_binary'
        }
        t={t}
      >
        {!isPython && (
          <label>
            <input
              type="checkbox"
              checked={runConfig.exportFormats?.includes('blend')}
              onChange={(e) => {
                const fmts = e.target.checked
                  ? ['stl_binary', 'blend']
                  : ['stl_binary'];
                setRun({ exportFormats: fmts });
                dispatch({
                  type: 'SET_OVERRIDE',
                  key: 'export',
                  value: { export: { formats: fmts } },
                });
              }}
            />
            blend
          </label>
        )}
      </OverrideSection>

      <section className="bed-load-config-section bed-load-config-section--run">
        <h4>{t('bedLoadSectionRun')}</h4>
        <label>
          {t('bedLoadRunType')}
          <select
            value={runConfig.runType}
            onChange={(e) => setRun({ runType: e.target.value })}
          >
            {runTypes.map((r) => (
              <option key={r.id} value={r.id}>
                {r.label}
              </option>
            ))}
          </select>
        </label>
        <label>
          {t('bedLoadViewer')}
          <select
            value={runConfig.viewerTarget}
            onChange={(e) => setRun({ viewerTarget: e.target.value })}
          >
            <option value="none">{t('bedLoadViewerNone')}</option>
            <option value="web_viewer">{t('bedLoadViewerWeb')}</option>
            {!isPython && (
              <option value="blender">{t('bedLoadViewerBlender')}</option>
            )}
          </select>
        </label>
      </section>
    </div>
  );
}
