import { useReducer, useCallback, useEffect } from 'react';
import { useLanguage } from '../../context/LanguageContext';
import {
  bedLoadReducer,
  initialBedLoadState,
  buildOverridesPayload,
  hubModeToDefaultRunType,
} from './bedLoadReducer';
import { getBedTemplateDefault, resolveMeshIdForRelativePath } from '../../services/api';
import {
  parseBedFile,
  compileBedWithOverrides,
  executeBedRun,
  formatApiError,
} from './bedLoadApi';
import ParseSummaryCards from './ParseSummaryCards';
import OverrideDiffTable from './OverrideDiffTable';
import BedLoadConfigForm from './BedLoadConfigForm';
import '../../styles/BedLoadModal.css';

const MAX_BYTES = 2 * 1024 * 1024;

export default function BedLoadModal({
  hubMode,
  initialContent = '',
  initialFilename = '',
  onClose,
  onSuccess,
  onNavigateTab,
  onOpenMeshViewer,
}) {
  const { t } = useLanguage();
  const [state, dispatch] = useReducer(bedLoadReducer, {
    ...initialBedLoadState,
    hubMode,
    file: {
      name: initialFilename,
      size: initialContent?.length || 0,
      content: initialContent,
    },
    phase: initialContent?.trim() ? 'file_selected' : 'idle',
    runConfig: {
      ...initialBedLoadState.runConfig,
      runType: hubModeToDefaultRunType(hubMode),
    },
  });

  useEffect(() => {
    dispatch({ type: 'SET_HUB_MODE', hubMode });
  }, [hubMode]);

  const handleFile = useCallback((file) => {
    if (!file?.name?.toLowerCase().endsWith('.bed')) return;
    if (file.size > MAX_BYTES) {
      dispatch({
        type: 'PARSE_FAIL',
        message: t('bedLoadFileTooLarge'),
      });
      return;
    }
    const reader = new FileReader();
    reader.onload = (e) => {
      dispatch({
        type: 'SET_FILE',
        file: {
          name: file.name,
          size: file.size,
          content: e.target?.result || '',
        },
      });
    };
    reader.readAsText(file);
  }, [t]);

  const goNext = async () => {
    if (state.step === 1) {
      if (!state.file.content?.trim()) {
        dispatch({ type: 'PARSE_FAIL', message: t('bedLoadEmptyFile') });
        return;
      }
      dispatch({ type: 'PARSE_START' });
      try {
        const res = await parseBedFile(
          state.file.content,
          state.file.name || 'leito.bed',
        );
        dispatch({
          type: 'PARSE_OK',
          parsed: res.parsed,
          warnings: res.warnings,
        });
        dispatch({ type: 'GO_STEP', step: 2 });
      } catch (err) {
        dispatch({
          type: 'PARSE_FAIL',
          message: formatApiError(err),
          detail: err?.response?.data?.detail,
        });
      }
      return;
    }
    if (state.step === 2) {
      dispatch({ type: 'GO_STEP', step: 3 });
      return;
    }
  };

  const goBack = () => {
    if (state.step > 1) dispatch({ type: 'GO_STEP', step: state.step - 1 });
  };

  const handleExecute = async () => {
    const geom = state.runConfig.geometry_mode;
    const isPython =
      state.runConfig.generation_backend === 'python_engine' ||
      String(state.runConfig.generation_backend).includes('python');
    if (geom === 'pseudo_2d_statistical' && !isPython) {
      dispatch({
        type: 'RUN_FAIL',
        message: t('bedLoadStatisticalPythonOnly'),
      });
      return;
    }

    dispatch({ type: 'RUN_START' });
    try {
      const overrides = buildOverridesPayload(state);
      const saveToDb =
        state.runConfig.runType !== 'compile_only' ||
        state.runConfig.viewerTarget !== 'none';
      const compiled = await compileBedWithOverrides({
        content: state.file.content,
        filename: state.file.name || 'leito.bed',
        overrides,
        hubMode,
        saveToDb,
      });
      dispatch({ type: 'SET_WORKING', working: compiled });

      const runResult = await executeBedRun({
        runType: state.runConfig.runType,
        compileResult: compiled,
        runConfig: state.runConfig,
        hubMode,
        onProgress: (p) => dispatch({ type: 'RUN_PROGRESS', ...p }),
      });

      dispatch({ type: 'RUN_OK', result: { ...compiled, run: runResult } });

      if (onSuccess) {
        onSuccess({
          compile: compiled,
          run: runResult,
          viewerTarget: state.runConfig.viewerTarget,
        });
      }

      if (runResult.open_viewer && state.runConfig.viewerTarget === 'web_viewer') {
        const rel = runResult.stl_path;
        if (rel && onOpenMeshViewer) {
          const meshId = await resolveMeshIdForRelativePath(rel);
          if (meshId) {
            onOpenMeshViewer(meshId);
          } else if (onNavigateTab) {
            onNavigateTab('mesh-viewer');
          }
        } else if (onNavigateTab) {
          onNavigateTab('mesh-viewer');
        }
      }
    } catch (err) {
      dispatch({
        type: 'RUN_FAIL',
        message: formatApiError(err),
        detail: err?.response?.data,
      });
    }
  };

  const stepLabels = [
    t('bedLoadStepSelect'),
    t('bedLoadStepParse'),
    t('bedLoadStepConfig'),
  ];

  const canNext =
    state.step === 1
      ? state.file.content?.trim()
      : state.step === 2
        ? state.phase === 'parsed'
        : false;

  const canExecute =
    state.step === 3 &&
    (state.phase === 'ready' || state.phase === 'parsed') &&
    state.phase !== 'running';

  return (
    <div
      className="criar-dock-backdrop bed-load-backdrop"
      role="presentation"
      onClick={onClose}
    >
      <div
        className="criar-dock-shell bed-load-shell"
        role="dialog"
        aria-labelledby="bed-load-title"
        onClick={(e) => e.stopPropagation()}
      >
        <header className="bed-load-header">
          <div>
            <h2 id="bed-load-title" className="bed-load-title">
              {t('bedFileModalTitle')}
            </h2>
            <p className="bed-load-subtitle">
              {t('bedLoadHubMode')}: {hubMode}
            </p>
          </div>
          <button
            type="button"
            className="criar-cli-panel-close"
            onClick={onClose}
            aria-label={t('close')}
          >
            ×
          </button>
        </header>

        <nav className="bed-load-stepper" aria-label={t('bedLoadSteps')}>
          {stepLabels.map((label, i) => {
            const n = i + 1;
            const active = state.step === n;
            const done = state.step > n;
            return (
              <span
                key={label}
                className={`bed-load-step${active ? ' bed-load-step--active' : ''}${done ? ' bed-load-step--done' : ''}`}
              >
                {n}. {label}
              </span>
            );
          })}
        </nav>

        <div className="bed-load-body">
          {state.error && (
            <div className="bed-load-error" role="alert">
              <p>{state.error}</p>
              {(state.errorDetail?.stderr ||
                (typeof state.errorDetail === 'object' &&
                  state.errorDetail?.message)) && (
                <pre>
                  {state.errorDetail?.stderr ||
                    (typeof state.errorDetail === 'string'
                      ? state.errorDetail
                      : JSON.stringify(state.errorDetail, null, 2))}
                </pre>
              )}
              <button
                type="button"
                className="btn-secondary"
                onClick={() => dispatch({ type: 'RESET_ERROR' })}
              >
                {t('bedLoadDismissError')}
              </button>
            </div>
          )}

          {state.phase === 'success' && state.result && (
            <div className="bed-load-success" role="status">
              <p>{t('bedLoadSuccess')}</p>
              <p className="bed-load-paths">
                json: {state.result.json_file}
              </p>
              {state.result.run?.job_id && (
                <p>job: {state.result.run.job_id}</p>
              )}
              {state.result.run?.blend_file && (
                <p className="bed-load-paths">
                  blend: {state.result.run.blend_file}
                </p>
              )}
              {state.result.run?.stl_path && (
                <p className="bed-load-paths">
                  stl: {state.result.run.stl_path}
                </p>
              )}
              {state.result.run?.case_dir && (
                <p className="bed-load-paths">
                  cfd: {state.result.run.case_dir}
                </p>
              )}
              {state.result.diff_from_parsed?.length > 0 && (
                <OverrideDiffTable
                  diff={state.result.diff_from_parsed}
                  t={t}
                />
              )}
              {onNavigateTab && (
                <div className="bed-load-success-actions">
                  <button
                    type="button"
                    className="btn-secondary"
                    onClick={() => onNavigateTab('results')}
                  >
                    {t('bedLoadGoResults')}
                  </button>
                  <button
                    type="button"
                    className="btn-secondary"
                    onClick={() => onNavigateTab('mesh-viewer')}
                  >
                    {t('bedLoadGoViewer')}
                  </button>
                </div>
              )}
            </div>
          )}

          {state.step === 1 && state.phase !== 'success' && (
            <div className="bed-load-step-content">
              <label className="bed-load-upload">
                <span>{t('bedLoadChooseFile')}</span>
                <input
                  type="file"
                  accept=".bed"
                  onChange={(e) => {
                    const f = e.target.files?.[0];
                    if (f) handleFile(f);
                  }}
                />
              </label>
              {state.file.name && (
                <p className="bed-load-file-meta">
                  {state.file.name} ({Math.round(state.file.size / 1024)} kb)
                </p>
              )}
              <button
                type="button"
                className="btn-secondary bed-load-template-btn"
                onClick={() => {
                  void (async () => {
                    try {
                      const data = await getBedTemplateDefault();
                      dispatch({
                        type: 'SET_FILE',
                        file: {
                          name: data.filename || 'template_padrao.bed',
                          size: (data.content || '').length,
                          content: data.content || '',
                        },
                      });
                    } catch (err) {
                      dispatch({
                        type: 'PARSE_FAIL',
                        message: formatApiError(err),
                      });
                    }
                  })();
                }}
              >
                {t('bedEditorLoadTemplateBtn')}
              </button>
              <details className="bed-load-editor-details">
                <summary>{t('bedEditorSectionTitle')}</summary>
                <textarea
                  className="bed-load-editor"
                  value={state.file.content}
                  onChange={(e) =>
                    dispatch({
                      type: 'SET_FILE',
                      file: {
                        name: state.file.name || 'leito.bed',
                        size: e.target.value.length,
                        content: e.target.value,
                      },
                    })
                  }
                  rows={12}
                />
              </details>
            </div>
          )}

          {state.step === 2 && state.phase !== 'success' && (
            <div className="bed-load-step-content">
              {state.phase === 'parsing' && (
                <p className="bed-load-status">{t('bedLoadParsing')}</p>
              )}
              {state.parsed && (
                <ParseSummaryCards
                  parsed={state.parsed}
                  warnings={state.parseWarnings}
                  t={t}
                />
              )}
            </div>
          )}

          {state.step === 3 && state.phase !== 'success' && (
            <div className="bed-load-step-content">
              <BedLoadConfigForm
                state={state}
                dispatch={dispatch}
                t={t}
                hubMode={hubMode}
              />
              {state.working?.diff_from_parsed?.length > 0 && (
                <>
                  <p className="bed-load-diff-title">{t('bedLoadDiffTitle')}</p>
                  <OverrideDiffTable
                    diff={state.working.diff_from_parsed}
                    t={t}
                  />
                </>
              )}
              {state.phase === 'running' && (
                <div className="bed-load-job-running">
                  <p className="bed-load-status">{t('bedLoadJobRunning')}</p>
                  {state.jobStatus && (
                    <p className="bed-load-job-status">
                      {t('bedLoadJobStatus')}: {state.jobStatus}
                      {state.jobMessage ? ` — ${state.jobMessage}` : ''}
                    </p>
                  )}
                  <div
                    className="bed-load-progress-bar"
                    role="progressbar"
                    aria-valuenow={state.jobProgress}
                    aria-valuemin={0}
                    aria-valuemax={100}
                  >
                    <div
                      className="bed-load-progress-fill"
                      style={{ width: `${state.jobProgress}%` }}
                    />
                  </div>
                  <p className="bed-load-job-progress">
                    {t('bedLoadJobProgress')}: {state.jobProgress}%
                  </p>
                </div>
              )}
            </div>
          )}
        </div>

        <footer className="bed-load-footer">
          {state.step > 1 && state.phase !== 'success' && (
            <button type="button" className="btn-secondary" onClick={goBack}>
              {t('bedLoadBack')}
            </button>
          )}
          {state.step < 3 && state.phase !== 'success' && (
            <button
              type="button"
              className="btn-primary"
              disabled={!canNext || state.phase === 'parsing'}
              onClick={() => void goNext()}
            >
              {state.step === 1 && state.phase === 'parsing'
                ? t('bedLoadParsing')
                : t('bedLoadNext')}
            </button>
          )}
          {state.step === 3 && state.phase !== 'success' && (
            <>
              <button
                type="button"
                className="btn-secondary"
                onClick={() => dispatch({ type: 'RESET_OVERRIDES' })}
              >
                {t('bedLoadUseOriginal')}
              </button>
              <button
                type="button"
                className="btn-primary"
                disabled={!canExecute || state.phase === 'running'}
                onClick={() => void handleExecute()}
              >
                {state.phase === 'running'
                  ? t('bedLoadRunning')
                  : t('bedLoadExecute')}
              </button>
            </>
          )}
          {state.phase === 'success' && (
            <button type="button" className="btn-primary" onClick={onClose}>
              {t('close')}
            </button>
          )}
          {state.phase !== 'success' && (
            <button type="button" className="btn-secondary" onClick={onClose}>
              {t('cancel')}
            </button>
          )}
        </footer>
      </div>
    </div>
  );
}
