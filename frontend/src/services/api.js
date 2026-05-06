// modulo que centraliza o cliente http axios para falar com o backend fastapi
// cada export e uma funcao fina que escolhe metodo url e parametros e devolve response data
import axios from 'axios';

export function getApiBase() {
  return (
    (typeof import.meta !== 'undefined' && import.meta.env && import.meta.env.VITE_API_URL) ||
    'http://localhost:8000'
  );
}

const api = axios.create({
  baseURL: getApiBase(),
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// chave fixa no local storage do browser para o id escolhido
const ACTIVE_USER_STORAGE = 'cfd_active_user_id';

// copia o id do storage para o cabecalho default do axios
// todas as chamadas api get post etc passam a incluir x user id
export function syncAxiosUserHeader() {
  try {
    const raw = localStorage.getItem(ACTIVE_USER_STORAGE);
    const n = parseInt(raw, 10);
    const id = Number.isFinite(n) && n >= 1 ? n : 1;
    api.defaults.headers.common['X-User-Id'] = String(id);
  } catch (_) {
    api.defaults.headers.common['X-User-Id'] = '1';
  }
}

// grava novo id e refresca o cabecalho imediatamente
export function setStoredActiveUserId(id) {
  const n = parseInt(String(id), 10);
  const v = Number.isFinite(n) && n >= 1 ? n : 1;
  localStorage.setItem(ACTIVE_USER_STORAGE, String(v));
  syncAxiosUserHeader();
  return v;
}

// le o id atual ou devolve 1 se nada estiver guardado
export function getStoredActiveUserId() {
  try {
    const raw = localStorage.getItem(ACTIVE_USER_STORAGE);
    const n = parseInt(raw, 10);
    return Number.isFinite(n) && n >= 1 ? n : 1;
  } catch (_) {
    return 1;
  }
}

// arranque do modulo garante cabecalho antes do primeiro pedido
syncAxiosUserHeader();

export function parseApiError(err) {
  if (err == null) return 'erro desconhecido';
  const data = err.response?.data;
  if (data == null) return err.message || 'erro de rede';
  const d = data.detail;
  if (typeof d === 'string') return d;
  if (Array.isArray(d)) {
    return d
      .map((x) => (typeof x === 'object' && x.msg ? x.msg : JSON.stringify(x)))
      .join('; ');
  }
  return err.message || 'erro';
}

// envia objeto parameters no corpo e espera caminhos dos ficheiros bed e json gerados
export const compileBed = async (parameters) => {
  const response = await api.post('/api/bed/compile', { parameters });
  return response.data;
};

// pede geracao de modelo 3d a partir do json
// open blender quando true pode abrir gui no servidor se o backend permitir
export const generateModel = async (jsonFile, openBlender = false) => {
  const response = await api.post('/api/model/generate', {
    json_file: jsonFile,
    open_blender: openBlender
  });
  return response.data;
};

// cria caso de simulacao ligando json e blend
// run simulation true pede execucao imediata no backend
export const createSimulation = async (jsonFile, blendFile, runSimulation = false) => {
  const response = await api.post('/api/simulation/create', {
    json_file: jsonFile,
    blend_file: blendFile,
    run_simulation: runSimulation
  });
  return response.data;
};

// le estado atual de um job por id uuid
export const getJobStatus = async (jobId) => {
  const response = await api.get(`/api/job/${jobId}`);
  return response.data;
};

export async function pollJobUntilDone(jobId, options = {}) {
  const intervalMs = options.intervalMs ?? 2000;
  const onUpdate = options.onUpdate;
  for (;;) {
    const job = await getJobStatus(jobId);
    if (onUpdate) onUpdate(job);
    if (job.status === 'completed') return job;
    if (job.status === 'failed') {
      throw new Error(job.error_message || 'job falhou');
    }
    await new Promise((r) => setTimeout(r, intervalMs));
  }
}

// lista jobs com filtros opcionais de estado e tipo
export const listJobs = async (status = null, jobType = null) => {
  const params = {};
  if (status) params.status = status;
  if (jobType) params.job_type = jobType;
  
  const response = await api.get('/api/jobs', { params });
  return response.data;
};

// inventario de ficheiros por tipo logico bed json blend stl simulations
export const listFiles = async (fileType) => {
  const response = await api.get(`/api/files/${fileType}`);
  return response.data;
};

// devolve url absoluta para o browser fazer download direto sem axios blob
export const downloadFile = (fileType, filename) => {
  return `${getApiBase()}/api/files/download/${fileType}/${filename}`;
};

// estado geral da api e flags de servicos externos
export const getSystemStatus = async () => {
  const response = await api.get('/api/status');
  return response.data;
};

// inventario de malhas para o visualizador 3d (stl, obj, ply, gltf, glb, blend)
export const listViewerMeshes = async ({ q, limit } = {}) => {
  const params = {};
  if (q) params.q = q;
  if (limit != null) params.limit = limit;
  const response = await api.get('/api/viewer/meshes', { params });
  return response.data;
};

export const buildMeshStreamUrl = (meshId) => {
  if (!meshId) return null;
  return `${getApiBase()}/api/viewer/mesh-stream?mesh_id=${encodeURIComponent(meshId)}`;
};

// transforma um caminho relativo dentro de generated em url publica do backend
export const buildGeneratedFileUrl = (relativePath) => {
  if (!relativePath) return null;
  const normalized = String(relativePath).replace(/\\/g, '/').replace(/^\/+/, '');
  if (normalized.startsWith('local_data/')) {
    return `${getApiBase()}/files/${normalized.slice('local_data/'.length)}`;
  }
  if (normalized.startsWith('generated/')) {
    return `${getApiBase()}/generated/${normalized.slice('generated/'.length)}`;
  }
  return `${getApiBase()}/files/${normalized}`;
};

// endpoint consolidado do dashboard com metricas e listas recentes
export const getDashboardSummary = async (recent_limit = 8) => {
  const response = await api.get('/api/dashboard/summary', {
    params: { recent_limit }
  });
  return response.data;
};

// agregados para graficos do dashboard contagens medias etc
export const getSimulationsSummary = async () => {
  const response = await api.get('/api/simulations/summary');
  return response.data;
};

// lista curta ordenada por data para widgets recentes
export const listRecentSimulations = async (limit = 8) => {
  const response = await api.get('/api/simulations/recent', {
    params: { limit }
  });
  return response.data;
};

// lista completa com paginacao e filtros bed id e status
export const listSimulations = async ({
  page = 1,
  limit = 20,
  per_page = null,
  bed_id = null,
  status = null,
  search = null,
  regime = null,
  solver = null,
  created_from = null,
  created_to = null,
} = {}) => {
  const params = { page, limit: per_page ?? limit };
  if (bed_id != null && bed_id !== '') params.bed_id = bed_id;
  if (status != null && status !== '') params.status = status;
  if (search != null && search !== '') params.search = search;
  if (regime != null && regime !== '') params.regime = regime;
  if (solver != null && solver !== '') params.solver = solver;
  if (created_from != null && created_from !== '') params.created_from = created_from;
  if (created_to != null && created_to !== '') params.created_to = created_to;
  const response = await api.get('/api/simulations', { params });
  return response.data;
};

// lista unificada de modelos 3d persistidos na tabela beds
export const listModels3D = async ({
  page = 1,
  limit = 20,
  per_page = null,
  search = null,
  packing_method = null,
  has_blend = null,
  has_stl = null,
  created_from = null,
  created_to = null,
} = {}) => {
  const response = await api.get('/api/models-3d', {
    params: {
      page,
      limit: per_page ?? limit,
      ...(search ? { search } : {}),
      ...(packing_method ? { packing_method } : {}),
      ...(has_blend !== null ? { has_blend } : {}),
      ...(has_stl !== null ? { has_stl } : {}),
      ...(created_from ? { created_from } : {}),
      ...(created_to ? { created_to } : {}),
    }
  });
  return response.data;
};

// feed agregado para a pagina de historico
export const getHistoryFeed = async ({
  page = 1,
  limit = 20,
  entry_type = 'all',
  search = null,
  status = null,
  packing_method = null,
  created_from = null,
  created_to = null,
} = {}) => {
  const response = await api.get('/api/history', {
    params: {
      page,
      limit,
      entry_type,
      ...(search ? { search } : {}),
      ...(status ? { status } : {}),
      ...(packing_method ? { packing_method } : {}),
      ...(created_from ? { created_from } : {}),
      ...(created_to ? { created_to } : {}),
    }
  });
  return response.data;
};

// detalhes completos de uma simulacao pelo id
export const getSimulation = async (simulationId) => {
  const response = await api.get(`/api/simulations/${simulationId}`);
  return response.data;
};

// remover simulacao do banco
export const deleteSimulation = async (simulationId) => {
  const response = await api.delete(`/api/simulations/${simulationId}`);
  return response.data;
};

// criar novo registo de simulacao na base a partir de um payload
export const createSimulationRecord = async (payload) => {
  const response = await api.post('/api/simulations', payload);
  return response.data;
};

// metricas e ficheiros associados a uma simulacao na base sql
export const getSimulationResults = async (
  simulationId,
  {
    resultType = null,
    search = null,
    page = 1,
    limit = 20,
  } = {}
) => {
  const params = { page, limit };
  if (resultType) params.result_type = resultType;
  if (search) params.search = search;
  const response = await api.get(`/api/results/simulation/${simulationId}`, { params });
  return response.data;
};

// templates texto bed guardados na tabela bed templates
export const listTemplates = async ({
  page = 1,
  limit = 20,
  search = null,
  tag = null,
  source = null,
  created_from = null,
  created_to = null,
} = {}) => {
  const response = await api.get('/api/templates/list', {
    params: {
      page,
      limit,
      ...(search ? { search } : {}),
      ...(tag ? { tag } : {}),
      ...(source ? { source } : {}),
      ...(created_from ? { created_from } : {}),
      ...(created_to ? { created_to } : {}),
    }
  });
  return response.data;
};

// busca um template por id string uuid
export const getTemplate = async (templateId) => {
  const response = await api.get(`/api/templates/${templateId}`);
  return response.data;
};

// grava nome conteudo tag e origem com defaults seguros
export const saveTemplate = async (payload) => {
  const response = await api.post('/api/templates/save', {
    name: payload.name,
    content: payload.content,
    tag: payload.tag ?? 'bed',
    source: payload.source ?? 'editor',
  });
  return response.data;
};

// apaga template sem corpo de resposta util
export const deleteTemplate = async (templateId) => {
  await api.delete(`/api/templates/${templateId}`);
};

// cria copia no servidor com novo id
export const duplicateTemplate = async (templateId) => {
  const response = await api.post(`/api/templates/${templateId}/duplicate`);
  return response.data;
};

// painel admin mostra motor sql contagens e ultimos eventos
export const getDatabasePanel = async () => {
  const response = await api.get('/api/database/panel');
  return response.data;
};

// regista clique de backup ou teste de ligacao no painel
export const postDatabasePanelEvent = async (eventType, detail = null) => {
  const response = await api.post('/api/database/events', {
    event_type: eventType,
    detail,
  });
  return response.data;
};

// crud simples de relatorios markdown ou texto livre
export const listReports = async ({
  page = 1,
  limit = 20,
  search = null,
  status = null,
  created_from = null,
  created_to = null,
} = {}) => {
  const response = await api.get('/api/reports', {
    params: {
      page,
      limit,
      ...(search ? { search } : {}),
      ...(status ? { status } : {}),
      ...(created_from ? { created_from } : {}),
      ...(created_to ? { created_to } : {}),
    }
  });
  return response.data;
};

export const getReport = async (reportId) => {
  const response = await api.get(`/api/reports/${reportId}`);
  return response.data;
};

export const createReport = async (payload) => {
  const response = await api.post('/api/reports', payload);
  return response.data;
};

export const updateReport = async (reportId, payload) => {
  const response = await api.patch(`/api/reports/${reportId}`, payload);
  return response.data;
};

export const deleteReport = async (reportId) => {
  await api.delete(`/api/reports/${reportId}`);
};

// meta para autocompletar anexos com simulacoes e templates existentes
export const reportsCatalog = async () => {
  const response = await api.get('/api/reports/meta/catalog');
  return response.data;
};

// lista resultados possiveis para uma simulacao escolhida
export const reportsResultsForSimulation = async (simulationId) => {
  const response = await api.get('/api/reports/meta/results', {
    params: { simulation_id: simulationId },
  });
  return response.data;
};

export const addReportAttachment = async (reportId, payload) => {
  const response = await api.post(`/api/reports/${reportId}/attachments`, payload);
  return response.data;
};

export const removeReportAttachment = async (reportId, attachmentId) => {
  await api.delete(`/api/reports/${reportId}/attachments/${attachmentId}`);
};

// pede get api users sem corpo json so precisa do cabecalho x user id para consistencia
export const listUsers = async () => {
  const response = await api.get('/api/users');
  return response.data;
};

// perfil do utilizador ativo (cabeçalho x-user-id)
export const getProfile = async () => {
  const response = await api.get('/api/profile');
  return response.data;
};

export const patchProfile = async (payload) => {
  const response = await api.patch('/api/profile', payload);
  return response.data;
};

// preferencias globais tema idioma timeouts openfoam
export const getSettings = async () => {
  const response = await api.get('/api/settings');
  return response.data;
};

export const patchSettings = async (payload) => {
  const response = await api.patch('/api/settings', payload);
  return response.data;
};

// cuidado so funciona se o servidor tiver env allow dev shutdown
export const postAdminDevShutdown = async () => {
  const response = await api.post('/api/admin/dev/shutdown');
  return response.data;
};

// texto explicando como correr o wizard no terminal do sistema
export const getWizardCliInstructions = async () => {
  const response = await api.get('/api/wizard/cli-instructions');
  return response.data;
};

// pede ao sistema operativo abrir terminal com comando sugerido
export const launchWizardCliTerminal = async () => {
  const response = await api.post('/api/wizard/launch-cli-terminal');
  return response.data;
};

export const postBedWizard = async (body) => {
  const r = await api.post('/api/bed/wizard', body);
  return r.data;
};

export const postBedProcess = async (body) => {
  const r = await api.post('/api/bed/process', body);
  return r.data;
};

export const getBedTemplateDefault = async () => {
  const r = await api.get('/api/bed/template/default');
  return r.data;
};

export const postPipelineFullSimulation = async (body, query = {}) => {
  const r = await api.post('/api/pipeline/full-simulation', body, { params: query });
  return r.data;
};

export const getPipelineJob = async (jobId) => {
  const r = await api.get(`/api/pipeline/job/${jobId}`);
  return r.data;
};

export async function pollPipelineJobUntilDone(jobId, options = {}) {
  const intervalMs = options.intervalMs ?? 2000;
  const onUpdate = options.onUpdate;
  for (;;) {
    const job = await getPipelineJob(jobId);
    if (onUpdate) onUpdate(job);
    if (job.status === 'completed') return job;
    if (job.status === 'failed') {
      throw new Error(job.error_message || 'pipeline falhou');
    }
    await new Promise((r) => setTimeout(r, intervalMs));
  }
}

export const postCfdRunFromWizard = async (body) => {
  const r = await api.post('/api/cfd/run-from-wizard', body);
  return r.data;
};

export const postCfdCreateCase = async (body) => {
  const r = await api.post('/api/cfd/create-case', body);
  return r.data;
};

export const postCfdCreateCaseOnly = async (body) => {
  const r = await api.post('/api/cfd/create-case-only', body);
  return r.data;
};

export const postCfdCreate = async (body) => {
  const r = await api.post('/api/cfd/create', body);
  return r.data;
};

export const getCfdList = async () => {
  const r = await api.get('/api/cfd/list');
  return r.data;
};

export const getCfdStatus = async (simulationId) => {
  const r = await api.get(`/api/cfd/status/${simulationId}`);
  return r.data;
};

export const deleteCfdSimulation = async (simulationId) => {
  const r = await api.delete(`/api/cfd/${simulationId}`);
  return r.data;
};

export const getCasosList = async () => {
  const r = await api.get('/api/casos/list');
  return r.data;
};

export const getCasoDetalhes = async (nomeCaso) => {
  const r = await api.get(`/api/casos/${encodeURIComponent(nomeCaso)}/detalhes`);
  return r.data;
};

export const deleteCaso = async (nomeCaso) => {
  const r = await api.delete(`/api/casos/${encodeURIComponent(nomeCaso)}`);
  return r.data;
};

export const updateTemplate = async (templateId, payload) => {
  const r = await api.put(`/api/templates/${templateId}`, {
    name: payload.name,
    content: payload.content,
    tag: payload.tag ?? 'bed',
    source: payload.source ?? 'editor',
  });
  return r.data;
};

export default api;
