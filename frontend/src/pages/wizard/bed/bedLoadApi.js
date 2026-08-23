import {
  postBedParse,
  postBedCompileFromBed,
  generateModel,
  postPipelineFullSimulation,
  pollJobUntilDone,
  pollPipelineJobUntilDone,
  postCfdCreateCase,
  postCfdCreateCaseOnly,
  parseApiError,
} from '../../services/api';
import { modelingProfileFromBackend } from '../../lib/pipelineParams';

export { modelingProfileFromBackend };

function pathsFromJobFinal(jobFinal) {
  const meta = jobFinal?.metadata || {};
  const blend_file =
    meta.blend_file ||
    meta.geometry_file ||
    (jobFinal?.output_files && jobFinal.output_files[0]) ||
    null;
  const geom = meta.geometry_file || null;
  const stl_path =
    meta.stl_path ||
    meta.stl_file ||
    (geom && String(geom).toLowerCase().endsWith('.stl') ? geom : null);
  return { blend_file, stl_path };
}

export async function parseBedFile(content, filename) {
  return postBedParse({ content, filename });
}

export async function compileBedWithOverrides({
  content,
  filename,
  overrides,
  hubMode,
  saveToDb,
}) {
  return postBedCompileFromBed({
    content,
    filename,
    overrides: overrides || {},
    hub_mode: hubMode,
    save_to_db: !!saveToDb,
  });
}

export async function executeBedRun({
  runType,
  compileResult,
  runConfig,
  hubMode,
  onProgress,
}) {
  const jsonFile = compileResult.json_file;
  const bedFile = compileResult.bed_file;
  const profile = modelingProfileFromBackend(runConfig.generation_backend);

  if (runType === 'compile_only') {
    return {
      kind: 'compile_only',
      json_file: jsonFile,
      bed_file: bedFile,
      bed_id: compileResult.bed_id,
    };
  }

  const emitProgress = (job) => {
    if (onProgress) {
      onProgress({
        jobProgress: job.progress ?? 0,
        jobStatus: job.status,
        jobMessage: job.message || job.error_message || '',
      });
    }
  };

  if (runType === 'generate_model' || runType === 'generate_and_view') {
    const openBlender =
      runType === 'generate_and_view' && runConfig.viewerTarget === 'blender';
    const gen = await generateModel(jsonFile, openBlender, profile);
    if (!gen.job_id) {
      throw new Error('api não devolveu job_id para geração do modelo');
    }
    const jobFinal = await pollJobUntilDone(gen.job_id, {
      onUpdate: emitProgress,
    });
    if (jobFinal.status === 'failed') {
      throw new Error(jobFinal.error_message || 'job de modelo falhou');
    }
    const { blend_file, stl_path } = pathsFromJobFinal(jobFinal);
    return {
      kind: runType,
      job_id: gen.job_id,
      json_file: jsonFile,
      bed_file: bedFile,
      job_final: jobFinal,
      blend_file,
      stl_path,
      open_viewer: runType === 'generate_and_view',
    };
  }

  if (runType === 'pipeline_full') {
    const pipe = await postPipelineFullSimulation({
      json_file: jsonFile,
      bed_file: bedFile || '',
    });
    if (!pipe.job_id) {
      throw new Error('api não devolveu job_id para pipeline completo');
    }
    const jobFinal = await pollPipelineJobUntilDone(pipe.job_id, {
      onUpdate: emitProgress,
    });
    if (jobFinal.status === 'failed') {
      throw new Error(jobFinal.error_message || 'pipeline falhou');
    }
    const { blend_file, stl_path } = pathsFromJobFinal(jobFinal);
    return {
      kind: 'pipeline_full',
      job_id: pipe.job_id,
      json_file: jsonFile,
      bed_file: bedFile,
      job_final: jobFinal,
      blend_file,
      stl_path,
    };
  }

  if (runType === 'pipeline_blender_cfd') {
    const genStart = await generateModel(jsonFile, false, profile);
    if (!genStart.job_id) {
      throw new Error('api não devolveu job_id para geração do modelo');
    }
    const jobFinal = await pollJobUntilDone(genStart.job_id, {
      onUpdate: emitProgress,
    });
    if (jobFinal.status === 'failed') {
      throw new Error(jobFinal.error_message || 'job de modelo falhou');
    }
    const blendRel =
      jobFinal.metadata?.blend_file ||
      jobFinal.metadata?.geometry_file ||
      (jobFinal.output_files && jobFinal.output_files[0]);
    if (!blendRel) {
      throw new Error('job de modelo não devolveu caminho blend/stl');
    }
    const cfdResult = await postCfdCreateCase({
      blend_file: blendRel,
      json_file: jsonFile,
      case_name: `leito_${Date.now()}`,
    });
    const { stl_path } = pathsFromJobFinal(jobFinal);
    return {
      kind: 'pipeline_blender_cfd',
      job_id: genStart.job_id,
      job_final: jobFinal,
      blend_file: blendRel,
      stl_path,
      case_dir: cfdResult.case_dir,
      json_file: jsonFile,
      bed_file: bedFile,
    };
  }

  if (runType === 'cfd_only') {
    const cfdResult = await postCfdCreateCaseOnly({
      json_file: jsonFile,
      case_name: `leito_${Date.now()}`,
    });
    return {
      kind: 'cfd_only',
      case_dir: cfdResult.case_dir,
      json_file: jsonFile,
    };
  }

  throw new Error(`tipo de execução desconhecido: ${runType}`);
}

export function formatApiError(err) {
  const d = err?.response?.data?.detail;
  if (typeof d === 'object' && d !== null) {
    if (d.stderr) return String(d.stderr);
    if (d.message) return String(d.message);
    if (Array.isArray(d.errors) && d.errors.length) {
      return d.errors.map((e) => e.message || JSON.stringify(e)).join('; ');
    }
  }
  const msg = parseApiError(err);
  if (msg && msg !== 'erro' && msg !== 'erro de rede') return msg;
  return err?.message || 'erro desconhecido';
}
