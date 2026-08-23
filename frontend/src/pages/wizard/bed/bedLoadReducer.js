export const defaultUseOriginal = () => ({
  generation_backend: true,
  geometry_mode: true,
  'packing.method': true,
  slice: true,
  statistical_2d: true,
  export: true,
});

export const initialBedLoadState = {
  step: 1,
  phase: 'idle',
  file: { name: '', size: 0, content: '' },
  parsed: null,
  parseWarnings: [],
  useOriginal: defaultUseOriginal(),
  overrides: {},
  working: null,
  runConfig: {
    runType: 'compile_only',
    generation_backend: 'python_engine',
    geometry_mode: 'full_3d',
    packingMethodSource: 'from_bed',
    packing_method: '',
    exportFormats: ['stl_binary'],
    viewerTarget: 'none',
    openBlender: false,
  },
  result: null,
  error: null,
  errorDetail: null,
  jobProgress: 0,
  jobStatus: null,
  jobMessage: null,
};

export function hubModeToDefaultRunType(hubMode) {
  if (hubMode === 'blender_interactive') return 'generate_and_view';
  if (hubMode === 'pipeline_completo') return 'pipeline_full';
  if (hubMode === 'pipeline_blender_cfd') return 'pipeline_blender_cfd';
  if (hubMode === 'cfd_only') return 'cfd_only';
  return 'compile_only';
}

function syncRunConfigFromParsed(state) {
  const p = state.parsed;
  if (!p) return state.runConfig;
  const gb = String(p.generation_backend || 'blender');
  const backend =
    gb.includes('python') || gb === 'pure_python' ? 'python_engine' : 'blender';
  return {
    ...state.runConfig,
    generation_backend: backend,
    geometry_mode: p.geometry_mode || 'full_3d',
    packing_method: p.packing?.method || '',
    runType: hubModeToDefaultRunType(state.hubMode),
  };
}

export function bedLoadReducer(state, action) {
  switch (action.type) {
    case 'SET_HUB_MODE':
      return {
        ...state,
        hubMode: action.hubMode,
        runConfig: {
          ...state.runConfig,
          runType: hubModeToDefaultRunType(action.hubMode),
        },
      };
    case 'SET_FILE':
      return {
        ...state,
        step: 1,
        phase: 'file_selected',
        file: action.file,
        error: null,
        errorDetail: null,
      };
    case 'PARSE_START':
      return { ...state, phase: 'parsing', error: null, errorDetail: null };
    case 'PARSE_OK': {
      const next = {
        ...state,
        phase: 'parsed',
        parsed: action.parsed,
        parseWarnings: action.warnings || [],
        step: 2,
        overrides: {},
        useOriginal: defaultUseOriginal(),
      };
      return {
        ...next,
        runConfig: syncRunConfigFromParsed(next),
      };
    }
    case 'SET_USE_ORIGINAL': {
      const useOriginal = {
        ...state.useOriginal,
        [action.key]: action.useOriginal,
      };
      let overrides = { ...state.overrides };
      if (action.useOriginal && action.key === 'packing.method') {
        const nextPack = { ...overrides };
        delete nextPack.packing;
        overrides = nextPack;
      }
      return {
        ...state,
        useOriginal,
        overrides,
        phase: state.phase === 'parsed' ? 'parsed' : 'ready',
      };
    }
    case 'PARSE_FAIL':
      return {
        ...state,
        phase: 'error',
        error: action.message,
        errorDetail: action.detail,
      };
    case 'SET_RUN_CONFIG':
      return {
        ...state,
        runConfig: { ...state.runConfig, ...action.patch },
        phase: state.phase === 'parsed' ? 'ready' : state.phase,
      };
    case 'SET_OVERRIDE': {
      const key = action.key;
      const useOriginal = { ...state.useOriginal, [key]: false };
      const overrides = { ...state.overrides, ...action.value };
      return {
        ...state,
        useOriginal,
        overrides,
        phase: 'ready',
      };
    }
    case 'RESET_OVERRIDES': {
      const p = state.parsed;
      const gb = String(p?.generation_backend || 'blender');
      const backend =
        gb.includes('python') || gb === 'pure_python' ? 'python_engine' : 'blender';
      return {
        ...state,
        overrides: {},
        useOriginal: defaultUseOriginal(),
        runConfig: {
          ...state.runConfig,
          generation_backend: backend,
          geometry_mode: p?.geometry_mode || 'full_3d',
          packingMethodSource: 'from_bed',
          packing_method: p?.packing?.method || '',
        },
        phase: 'parsed',
      };
    }
    case 'SET_WORKING':
      return {
        ...state,
        working: action.working,
        phase: state.phase === 'running' ? 'running' : 'ready',
      };
    case 'GO_STEP':
      return { ...state, step: action.step };
    case 'RUN_START':
      return {
        ...state,
        phase: 'running',
        error: null,
        jobProgress: 0,
        jobStatus: 'queued',
        jobMessage: null,
      };
    case 'RUN_PROGRESS':
      return {
        ...state,
        phase: 'running',
        jobProgress: action.jobProgress ?? state.jobProgress,
        jobStatus: action.jobStatus ?? state.jobStatus,
        jobMessage: action.jobMessage ?? state.jobMessage,
      };
    case 'RUN_OK':
      return {
        ...state,
        phase: 'success',
        result: action.result,
        jobProgress: action.result?.run?.job_final?.progress ?? 100,
        jobStatus: action.result?.run?.job_final?.status ?? 'completed',
        jobMessage: null,
      };
    case 'RUN_FAIL':
      return {
        ...state,
        phase: 'error',
        error: action.message,
        errorDetail: action.detail,
      };
    case 'RESET_ERROR':
      return {
        ...state,
        phase: state.parsed
          ? 'parsed'
          : state.file?.content?.trim()
            ? 'file_selected'
            : 'idle',
        error: null,
        errorDetail: null,
      };
    default:
      return state;
  }
}

const DEFAULT_SLICE = {
  slice_enabled: true,
  slice_axis: 'y',
  slice_position: '0.0',
  slice_thickness: '0.002',
  keep_only_intersecting_particles: true,
  preserve_original_packing: true,
};

const DEFAULT_STATISTICAL = {
  domain_width: '0.05',
  domain_height: '0.1',
  target_porosity: '0.4',
  tolerance: '0.02',
  max_attempts: '50',
  slice_thickness: '0.002',
  seed: '42',
};

function mergeSliceOverride(parsed, overrides) {
  return {
    ...DEFAULT_SLICE,
    ...(parsed?.slice || {}),
    ...(overrides.slice || {}),
  };
}

function mergeStatOverride(parsed, overrides) {
  return {
    ...DEFAULT_STATISTICAL,
    ...(parsed?.statistical_2d || {}),
    ...(overrides.statistical_2d || {}),
  };
}

export function buildOverridesPayload(state) {
  const { runConfig, overrides, useOriginal, parsed } = state;
  const out = {};
  const geom =
    useOriginal.geometry_mode !== false
      ? parsed?.geometry_mode || 'full_3d'
      : runConfig.geometry_mode;

  if (useOriginal.generation_backend === false) {
    out.generation_backend = runConfig.generation_backend;
  }
  if (useOriginal.geometry_mode === false) {
    out.geometry_mode = runConfig.geometry_mode;
  }
  if (
    runConfig.packingMethodSource !== 'from_bed' &&
    useOriginal['packing.method'] === false
  ) {
    out.packing = {
      ...(overrides.packing || {}),
      method: runConfig.packing_method,
    };
  }
  if (geom === 'pseudo_2d_thin_slice') {
    const needSlice =
      useOriginal.slice === false ||
      (useOriginal.geometry_mode === false && !parsed?.slice);
    if (needSlice) {
      out.slice = mergeSliceOverride(parsed, overrides);
    }
  }
  if (geom === 'pseudo_2d_statistical' && useOriginal.statistical_2d === false) {
    out.statistical_2d = mergeStatOverride(parsed, overrides);
  }
  if (useOriginal.export === false && overrides.export) {
    out.export = overrides.export;
  }
  if (Object.keys(out).length === 0) {
    return {};
  }
  return out;
}
