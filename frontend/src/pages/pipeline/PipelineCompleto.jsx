import { useState } from 'react';
import ThemeIcon from './ThemeIcon';
import '../styles/PipelineCompleto.css';
import '../styles/PipelineCompletoFull.css';
import {
  getJobStatus,
  postBedWizard,
  generateModel,
  postCfdRunFromWizard,
  getCfdStatus,
  parseApiError,
} from '../services/api';
import {
  defaultPipelineCompactParams,
  toBedWizardRequest,
  modelingProfileFromBackend,
  validatePipelineGeometryBackend,
} from '../lib/pipelineParams';

/**
 * pipeline completo web (fluxo curto): bed wizard → modelo 3d → cfd opcional
 */
const PipelineCompleto = () => {
  const [etapaAtual, setEtapaAtual] = useState('inicio');
  const [parametros, setParametros] = useState(defaultPipelineCompactParams);
  const [dadosPipeline, setDadosPipeline] = useState(null);
  const [log, setLog] = useState([]);
  const [erro, setErro] = useState(null);
  const [progresso, setProgresso] = useState(0);

  const adicionarLog = (mensagem, tipo = 'info') => {
    const timestamp = new Date().toLocaleTimeString();
    setLog((prev) => [...prev, { timestamp, mensagem, tipo }]);
  };

  const aguardarJobModelo = (jobId) =>
    new Promise((resolve, reject) => {
      const poll = async () => {
        try {
          const job = await getJobStatus(jobId);
          if (job.status === 'completed') {
            resolve(job);
            return;
          }
          if (job.status === 'failed') {
            reject(new Error(job.error_message || 'falha na geração do modelo 3d'));
            return;
          }
          const pct = job.progress ?? 0;
          setProgresso(25 + Math.round(pct * 0.25));
          adicionarLog(`  job modelo: ${job.status} (${pct}%)`, 'info');
          setTimeout(poll, 2000);
        } catch (e) {
          reject(e);
        }
      };
      poll();
    });

  const iniciarPipeline = async () => {
    const validationErr = validatePipelineGeometryBackend(parametros);
    if (validationErr) {
      setErro(validationErr);
      setEtapaAtual('erro');
      return;
    }

    setErro(null);
    setLog([]);
    setProgresso(0);

    const wizardPayload = toBedWizardRequest(parametros, {
      mode: 'pipeline_completo',
    });

    try {
      setEtapaAtual('compilando');
      setProgresso(10);
      adicionarLog('compilando arquivo .bed com antlr...', 'info');

      const dadosCompilacao = await postBedWizard(wizardPayload);
      adicionarLog(`arquivo .bed compilado: ${dadosCompilacao.bed_file}`, 'success');
      adicionarLog(`arquivo .json gerado: ${dadosCompilacao.json_file}`, 'success');
      setProgresso(25);

      setEtapaAtual('gerando3d');
      adicionarLog('gerando modelo 3d...', 'info');

      const profile = modelingProfileFromBackend(parametros.generation_backend);
      const jobInicio = await generateModel(
        dadosCompilacao.json_file,
        false,
        profile,
      );
      const jobId = jobInicio.job_id;
      if (!jobId) {
        throw new Error('api não devolveu job_id para o modelo 3d');
      }
      adicionarLog(`modelo 3d em fila (job: ${jobId})`, 'info');
      const jobFinal = await aguardarJobModelo(jobId);
      const caminhoModelo =
        jobFinal.metadata?.blend_file ||
        jobFinal.metadata?.geometry_file ||
        (jobFinal.output_files && jobFinal.output_files[0]) ||
        '(ver output_files no job)';
      adicionarLog('modelo 3d concluído', 'success');
      adicionarLog(`modelo 3d: ${caminhoModelo}`, 'success');
      setProgresso(50);

      if (wizardPayload.params.cfd) {
        setEtapaAtual('cfd');
        adicionarLog('criando caso openfoam...', 'info');

        const dadosCFD = await postCfdRunFromWizard({
          fileName: wizardPayload.fileName,
          runSimulation: true,
        });
        adicionarLog(`caso cfd criado: ${dadosCFD.simulation_id}`, 'success');
        setProgresso(75);

        setEtapaAtual('executando');
        adicionarLog('executando simulação cfd...', 'info');

        await new Promise((resolve, reject) => {
          const intervalo = setInterval(async () => {
            try {
              const status = await getCfdStatus(dadosCFD.simulation_id);
              setProgresso(75 + Math.round((status.progress || 0) * 0.25));

              if (status.status === 'completed') {
                clearInterval(intervalo);
                adicionarLog('simulação cfd concluída', 'success');
                setEtapaAtual('concluido');
                setProgresso(100);
                setDadosPipeline({
                  bedFile: dadosCompilacao.bed_file,
                  jsonFile: dadosCompilacao.json_file,
                  modelFile: caminhoModelo,
                  cfdCase: status.case_dir,
                  simulationId: dadosCFD.simulation_id,
                });
                resolve();
              } else if (status.status === 'error') {
                clearInterval(intervalo);
                reject(new Error(status.error || 'erro na simulação'));
              } else {
                adicionarLog(
                  `  ${status.message} (${status.progress}%)`,
                  'info',
                );
              }
            } catch (err) {
              clearInterval(intervalo);
              reject(err);
            }
          }, 3000);
        });
      } else {
        setEtapaAtual('concluido');
        setProgresso(100);
        adicionarLog('pipeline concluído (sem simulação cfd)', 'success');
        setDadosPipeline({
          bedFile: dadosCompilacao.bed_file,
          jsonFile: dadosCompilacao.json_file,
          modelFile: caminhoModelo,
        });
      }
    } catch (err) {
      const msg = parseApiError(err) || err.message || 'erro';
      setErro(msg);
      adicionarLog(`erro: ${msg}`, 'error');
      setEtapaAtual('erro');
    }
  };

  const renderParams = () => (
    <div className="pipeline-config">
      <h2>parâmetros do pipeline</h2>
      <p className="pipeline-description">
        configure o leito e o motor antes de compilar .bed e gerar o modelo 3d
      </p>

      <label>
        nome do ficheiro .bed
        <input
          type="text"
          value={parametros.fileName}
          onChange={(e) =>
            setParametros({ ...parametros, fileName: e.target.value })
          }
        />
      </label>

      <div className="config-section">
        <h3>leito e partículas</h3>
        <div className="config-grid">
          <label>
            diâmetro (m)
            <input
              type="number"
              step="0.001"
              value={parametros.diameter}
              onChange={(e) =>
                setParametros({
                  ...parametros,
                  diameter: parseFloat(e.target.value),
                })
              }
            />
          </label>
          <label>
            altura (m)
            <input
              type="number"
              step="0.001"
              value={parametros.height}
              onChange={(e) =>
                setParametros({
                  ...parametros,
                  height: parseFloat(e.target.value),
                })
              }
            />
          </label>
          <label>
            partículas (n)
            <input
              type="number"
              value={parametros.particle_count}
              onChange={(e) =>
                setParametros({
                  ...parametros,
                  particle_count: parseInt(e.target.value, 10),
                })
              }
            />
          </label>
          <label>
            ø partícula (m)
            <input
              type="number"
              step="0.0001"
              value={parametros.particle_diameter}
              onChange={(e) =>
                setParametros({
                  ...parametros,
                  particle_diameter: parseFloat(e.target.value),
                })
              }
            />
          </label>
        </div>
      </div>

      <div className="config-section">
        <h3>geometria e motor</h3>
        <div className="config-grid">
          <label>
            geometry_mode
            <select
              value={parametros.geometry_mode}
              onChange={(e) => {
                const gm = e.target.value;
                setParametros((prev) => ({
                  ...prev,
                  geometry_mode: gm,
                  generation_backend:
                    gm === 'pseudo_2d_statistical'
                      ? 'python_engine'
                      : prev.generation_backend,
                  statistical_2d: {
                    ...prev.statistical_2d,
                    domain_width: prev.diameter,
                    domain_height: prev.height,
                  },
                }));
              }}
            >
              <option value="full_3d">full_3d</option>
              <option value="pseudo_2d_thin_slice">pseudo_2d_thin_slice</option>
              <option value="pseudo_2d_statistical">
                pseudo_2d_statistical
              </option>
            </select>
          </label>
          <label>
            generation_backend
            <select
              value={parametros.generation_backend}
              disabled={parametros.geometry_mode === 'pseudo_2d_statistical'}
              onChange={(e) =>
                setParametros({
                  ...parametros,
                  generation_backend: e.target.value,
                })
              }
            >
              <option value="blender">blender</option>
              <option value="python_engine">python_engine</option>
            </select>
          </label>
        </div>
        {parametros.geometry_mode === 'pseudo_2d_thin_slice' && (
          <div className="config-grid">
            <label>
              slice_axis
              <select
                value={parametros.slice?.slice_axis || 'y'}
                onChange={(e) =>
                  setParametros({
                    ...parametros,
                    slice: { ...parametros.slice, slice_axis: e.target.value },
                  })
                }
              >
                <option value="x">x</option>
                <option value="y">y</option>
                <option value="z">z</option>
              </select>
            </label>
            <label>
              slice_thickness (m)
              <input
                type="number"
                step="0.0001"
                value={parametros.slice?.slice_thickness ?? 0.002}
                onChange={(e) =>
                  setParametros({
                    ...parametros,
                    slice: {
                      ...parametros.slice,
                      slice_thickness: parseFloat(e.target.value),
                    },
                  })
                }
              />
            </label>
          </div>
        )}
        {parametros.geometry_mode === 'pseudo_2d_statistical' && (
          <div className="config-grid">
            <label>
              target_porosity
              <input
                type="number"
                step="0.01"
                value={parametros.statistical_2d?.target_porosity ?? 0.38}
                onChange={(e) =>
                  setParametros({
                    ...parametros,
                    statistical_2d: {
                      ...parametros.statistical_2d,
                      target_porosity: parseFloat(e.target.value),
                    },
                  })
                }
              />
            </label>
          </div>
        )}
      </div>

      <div className="config-section">
        <h3>cfd (opcional)</h3>
        <label className="pipeline-cfd-toggle">
          <input
            type="checkbox"
            checked={parametros.includeCfd}
            onChange={(e) =>
              setParametros({ ...parametros, includeCfd: e.target.checked })
            }
          />
          incluir simulação cfd após o modelo 3d
        </label>
      </div>

      <div className="config-actions">
        <button
          type="button"
          className="btn-voltar"
          onClick={() => setEtapaAtual('inicio')}
        >
          voltar
        </button>
        <button
          type="button"
          className="btn-executar"
          onClick={() => void iniciarPipeline()}
        >
          iniciar pipeline
        </button>
      </div>
    </div>
  );

  const renderConteudo = () => {
    switch (etapaAtual) {
      case 'inicio':
        return (
          <div className="pipeline-inicio">
            <h2>pipeline completo - leitos empacotados</h2>
            <p className="descricao">
              execute o pipeline: compilar .bed → gerar 3d → cfd (opcional)
            </p>

            <div className="fluxo-visual">
              <div className="fluxo-etapa">
                <span className="fluxo-numero">1</span>
                <span className="fluxo-texto">criar parâmetros (.bed)</span>
              </div>
              <div className="fluxo-seta">→</div>
              <div className="fluxo-etapa">
                <span className="fluxo-numero">2</span>
                <span className="fluxo-texto">compilar dsl (.json)</span>
              </div>
              <div className="fluxo-seta">→</div>
              <div className="fluxo-etapa">
                <span className="fluxo-numero">3</span>
                <span className="fluxo-texto">gerar 3d</span>
              </div>
              <div className="fluxo-seta">→</div>
              <div className="fluxo-etapa">
                <span className="fluxo-numero">4</span>
                <span className="fluxo-texto">simular (openfoam)</span>
              </div>
            </div>

            <div className="opcoes-inicio">
              <button
                type="button"
                className="btn btn-primary btn-large"
                onClick={() => setEtapaAtual('params')}
              >
                configurar e iniciar
              </button>
            </div>
          </div>
        );

      case 'params':
        return renderParams();

      case 'compilando':
      case 'gerando3d':
      case 'cfd':
      case 'executando':
        return renderExecutando();

      case 'concluido':
        return renderConcluido();

      case 'erro':
        return renderErro();

      default:
        return null;
    }
  };

  const renderExecutando = () => (
    <div className="pipeline-executando">
      <h2>executando pipeline</h2>

      <div className="etapas-status">
        <div
          className={`etapa-item ${etapaAtual === 'compilando' ? 'ativa' : progresso > 25 ? 'concluida' : ''}`}
        >
          <ThemeIcon
            light="textEditorLight.png"
            dark="textEditor.png"
            alt=""
            className="etapa-icone"
          />
          <span className="etapa-nome">compilando dsl</span>
        </div>
        <div
          className={`etapa-item ${etapaAtual === 'gerando3d' ? 'ativa' : progresso > 50 ? 'concluida' : ''}`}
        >
          <span className="etapa-icone etapa-marcador" aria-hidden="true">
            3d
          </span>
          <span className="etapa-nome">gerando modelo 3d</span>
        </div>
        <div
          className={`etapa-item ${etapaAtual === 'cfd' || etapaAtual === 'executando' ? 'ativa' : progresso > 75 ? 'concluida' : ''}`}
        >
          <span className="etapa-icone etapa-marcador" aria-hidden="true">
            cfd
          </span>
          <span className="etapa-nome">cfd</span>
        </div>
      </div>

      <div className="progress-container">
        <div className="progress-bar">
          <div className="progress-fill" style={{ width: `${progresso}%` }} />
        </div>
        <span className="progress-text">{progresso}%</span>
      </div>

      <div className="log-container">
        <h3>log de execução</h3>
        <div className="log-content">
          {log.map((entrada, idx) => (
            <div key={idx} className={`log-entry log-${entrada.tipo}`}>
              <span className="log-time">{entrada.timestamp}</span>
              <span className="log-message">{entrada.mensagem}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );

  const renderConcluido = () => (
    <div className="pipeline-concluido">
      <div className="success-header">
        <span className="success-icon" aria-hidden="true">
          ok
        </span>
        <h2>pipeline executado com sucesso</h2>
      </div>

      {dadosPipeline && (
        <div className="resultados">
          <h3>arquivos gerados</h3>
          <div className="resultado-item">
            <strong>arquivo .bed:</strong>
            <code>{dadosPipeline.bedFile}</code>
          </div>
          <div className="resultado-item">
            <strong>parâmetros json:</strong>
            <code>{dadosPipeline.jsonFile}</code>
          </div>
          <div className="resultado-item">
            <strong>modelo 3d:</strong>
            <code>{dadosPipeline.modelFile}</code>
          </div>
          {dadosPipeline.cfdCase && (
            <div className="resultado-item">
              <strong>caso cfd:</strong>
              <code>{dadosPipeline.cfdCase}</code>
            </div>
          )}
        </div>
      )}

      <div className="acoes-final">
        <button
          type="button"
          className="btn btn-primary"
          onClick={() => {
            setEtapaAtual('inicio');
            setParametros(defaultPipelineCompactParams());
            setDadosPipeline(null);
            setLog([]);
          }}
        >
          executar novo pipeline
        </button>
      </div>
    </div>
  );

  const renderErro = () => (
    <div className="pipeline-erro">
      <div className="erro-header">
        <span className="erro-icon" aria-hidden="true">
          !
        </span>
        <h2>erro no pipeline</h2>
      </div>
      <div className="erro-message">
        <strong>erro:</strong> {erro}
      </div>
      <div className="acoes-erro">
        <button
          type="button"
          className="btn btn-primary"
          onClick={() => setEtapaAtual('params')}
        >
          tentar novamente
        </button>
      </div>
    </div>
  );

  return (
    <div className="pipeline-completo">
      <div className="pipeline-header">
        <h1>pipeline completo (fluxo curto)</h1>
        <p className="subtitle">
          compilar .bed, gerar modelo 3d e opcionalmente simular cfd
        </p>
      </div>
      {renderConteudo()}
    </div>
  );
};

export default PipelineCompleto;
