import { useState, useEffect, useMemo } from 'react';
import '../styles/CasosCFD.css';
import '../styles/MeshViewer3DPage.css';
import ThemeIcon from './ThemeIcon';
import BackendConnectionError from './BackendConnectionError';
import PaginationControls from './PaginationControls';
import { getCasosList, getCasoDetalhes, deleteCaso } from '../services/api';

/** instruções wsl genéricas (sem caminho absoluto do utilizador) */
function buildComandoWsl(caso) {
  const rel = (caso.caminho_relativo || `local_data/simulations/${caso.nome}`).replace(/\\/g, '/');
  return `# abrir wsl
wsl

# navegar até o caso (substitua unidade, utilizador e pasta do projeto)
cd /mnt/<unidade>/Users/<utilizador>/<pasta-do-projeto>/${rel}

# carregar openfoam
source /opt/openfoam11/etc/bashrc

# executar
./Allrun`;
}

function IconRefresh({ className }) {
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
  );
}

const CasosCFD = () => {
  const [casos, setCasos] = useState([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState(null);
  const [casoSelecionado, setCasoSelecionado] = useState(null);
  const [page, setPage] = useState(1);
  const [limit, setLimit] = useState(4);

  useEffect(() => {
    carregarCasos();
  }, []);

  const carregarCasos = async () => {
    const fullScreenLoad = casos.length === 0;
    if (fullScreenLoad) setLoading(true);
    else setRefreshing(true);
    setError(null);

    try {
      const data = await getCasosList();
      setCasos(data.casos);
      setPage(1);
    } catch (err) {
      setError('erro de conexão com o backend');
      console.error('erro:', err);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  const totalCasos = casos.length;
  const totalPages = Math.max(1, Math.ceil(totalCasos / limit) || 1);
  const paginatedCasos = useMemo(() => {
    const start = (page - 1) * limit;
    return casos.slice(start, start + limit);
  }, [casos, page, limit]);

  useEffect(() => {
    if (page > totalPages) setPage(totalPages);
  }, [page, totalPages]);

  const obterDetalhes = async (nomeCaso) => {
    try {
      const data = await getCasoDetalhes(nomeCaso);
      setCasoSelecionado(data);
    } catch (err) {
      console.error('erro ao obter detalhes:', err);
    }
  };

  const deletarCaso = async (nomeCaso) => {
    if (!confirm(`tem certeza que deseja deletar o caso "${nomeCaso}"? esta ação não pode ser desfeita!`)) {
      return;
    }

    try {
      await deleteCaso(nomeCaso);
      alert('caso deletado com sucesso!');
      carregarCasos();
      setCasoSelecionado(null);
    } catch (err) {
      alert('erro de conexão');
      console.error('erro:', err);
    }
  };

  const getStatusBadge = (status) => {
    const statusMap = {
      configured: { text: 'configurado', class: 'status-configured', desc: 'pronto para executar' },
      meshed: { text: 'com malha', class: 'status-meshed', desc: 'malha gerada' },
      running: { text: 'executando', class: 'status-running', desc: 'simulação em andamento' },
      completed: { text: 'concluído', class: 'status-completed', desc: 'simulação finalizada' },
      unknown: { text: 'desconhecido', class: 'status-unknown', desc: 'status indefinido' },
    };

    const info = statusMap[status] || statusMap.unknown;

    return (
      <span className={`status-badge ${info.class}`} title={info.desc}>
        {info.text}
      </span>
    );
  };

  const abrirExplorador = (caminho) => {
    navigator.clipboard.writeText(caminho);
    alert(`caminho copiado!\n\n${caminho}\n\nabra o explorador de arquivos e cole o caminho na barra de endereço.`);
  };

  if (loading) {
    return (
      <div className="casos-cfd">
        <div className="loading">carregando casos...</div>
      </div>
    );
  }

  return (
    <div className="casos-cfd">
      <div className="casos-header">
        <div className="casos-title-row">
          <ThemeIcon
            light="folderLight.png"
            dark="folderLight.png"
            alt=""
            className="casos-title-icon"
            location="page"
          />
          <h2>Casos CFD</h2>
        </div>
      </div>

      {error && <BackendConnectionError message={error} />}

      <section className="casos-panel ui-raised-surface" aria-label="lista de casos cfd">
        <div className="casos-panel-toolbar">
          <button
            type="button"
            className="mesh-viewer-hub-btn mesh-viewer-hub-btn--compact"
            onClick={() => void carregarCasos()}
            disabled={refreshing}
            title="atualizar lista de casos"
          >
            <IconRefresh className="mesh-viewer-hub-btn__icon" aria-hidden />
            {refreshing ? '…' : 'atualizar'}
          </button>
        </div>

        {casos.length === 0 ? (
          <div className="sem-casos sem-casos--in-panel">
            <p>nenhum caso cfd encontrado</p>
            <p className="hint">use o wizard para criar leitos e gerar casos cfd</p>
          </div>
        ) : (
          <>
          <div className="casos-grid">
            {paginatedCasos.map((caso) => (
              <div key={caso.nome} className="caso-card">
                <div className="caso-header">
                  <h3>{caso.nome}</h3>
                  {getStatusBadge(caso.status)}
                </div>

                <div className="caso-info">
                  <div className="info-row">
                    <span className="info-label">criado:</span>
                    <span>{new Date(caso.created_at).toLocaleString()}</span>
                  </div>

                  <div className="info-row">
                    <span className="info-label">tamanho:</span>
                    <span>{caso.tamanho_mb} mb</span>
                  </div>

                  <div className="info-row">
                    <span className="info-label">pastas de tempo:</span>
                    <span>{caso.pastas_tempo} resultado(s)</span>
                  </div>

                  <div className="info-row">
                    <span className="info-label">malha:</span>
                    <span>{caso.tem_malha ? 'gerada' : 'não gerada'}</span>
                  </div>
                </div>

                <div className="caso-caminho">
                  <strong>caminho:</strong>
                  <code onClick={() => abrirExplorador(caso.caminho)} title="clique para copiar">
                    {caso.caminho_relativo}
                  </code>
                </div>

                {caso.logs.length > 0 && (
                  <div className="caso-logs">
                    <strong>logs:</strong>
                    <div className="logs-list">
                      {caso.logs.map((log) => (
                        <span key={log} className="log-badge">
                          {log}
                        </span>
                      ))}
                    </div>
                  </div>
                )}

                <div className="caso-acoes">
                  <button
                    type="button"
                    className="btn-mode-option"
                    onClick={() => obterDetalhes(caso.nome)}
                  >
                    <ThemeIcon light="docsLight.png" dark="docsLight.png" alt="" className="btn-icon" />
                    ver detalhes
                  </button>

                  {caso.status === 'configured' && (
                    <button type="button" className="btn-mode-option">
                      <ThemeIcon light="runLight.png" dark="runDark.png" alt="" className="btn-icon" />
                      executar no wsl
                    </button>
                  )}

                  <button
                    type="button"
                    className="btn-mode-option"
                    onClick={() => deletarCaso(caso.nome)}
                  >
                    <ThemeIcon light="cancelLight.png" dark="cancelDark.png" alt="" className="btn-icon" />
                    deletar
                  </button>
                </div>
              </div>
            ))}
          </div>

          <PaginationControls
            page={page}
            totalPages={totalPages}
            total={totalCasos}
            limit={limit}
            loading={loading}
            onPageChange={setPage}
            onLimitChange={(value) => {
              setPage(1);
              setLimit(value);
            }}
            label="Casos CFD"
            limitOptions={[4, 8, 12, 20]}
            pt
          />
          </>
        )}
      </section>

      {casoSelecionado && (
        <div
          className="casos-modal-overlay"
          role="presentation"
          onClick={() => setCasoSelecionado(null)}
        >
          <div
            className="casos-modal ui-raised-surface"
            role="dialog"
            aria-modal="true"
            aria-labelledby="casos-modal-title"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="casos-modal-header modal-header--footer-modals">
              <h2 id="casos-modal-title">detalhes do caso: {casoSelecionado.nome}</h2>
              <button
                type="button"
                className="casos-modal-close"
                onClick={() => setCasoSelecionado(null)}
                aria-label="fechar"
              >
                ×
              </button>
            </div>

            <div className="casos-modal-body">
              <div className="casos-detalhe-block">
                <h4>status</h4>
                {getStatusBadge(casoSelecionado.status)}
              </div>

              <div className="casos-detalhe-block">
                <h4>informações</h4>
                <p>
                  <strong>criado:</strong> {new Date(casoSelecionado.created_at).toLocaleString()}
                </p>
                <p>
                  <strong>modificado:</strong> {new Date(casoSelecionado.modified_at).toLocaleString()}
                </p>
                <p>
                  <strong>tamanho:</strong> {casoSelecionado.tamanho_mb} mb
                </p>
              </div>

              <div className="casos-detalhe-block">
                <h4>arquivos</h4>
                <p>allrun: {casoSelecionado.tem_allrun ? 'sim' : 'não'}</p>
                <p>geometria stl: {casoSelecionado.tem_stl ? 'sim' : 'não'}</p>
                <p>malha: {casoSelecionado.tem_malha ? 'sim' : 'não'}</p>
              </div>

              {casoSelecionado.tempos_disponiveis && (
                <div className="casos-detalhe-block">
                  <h4>tempos disponíveis ({casoSelecionado.tempos_disponiveis.length})</h4>
                  <div className="tempos-list">
                    {casoSelecionado.tempos_disponiveis.slice(0, 10).map((t) => (
                      <span key={t} className="tempo-badge">
                        {t}
                      </span>
                    ))}
                    {casoSelecionado.tempos_disponiveis.length > 10 && (
                      <span className="tempo-badge">+{casoSelecionado.tempos_disponiveis.length - 10} mais</span>
                    )}
                  </div>
                </div>
              )}

              {casoSelecionado.configuracao && (
                <div className="casos-detalhe-block">
                  <h4>configuração temporal</h4>
                  <p>
                    <strong>tempo inicial:</strong> {casoSelecionado.configuracao.startTime}
                  </p>
                  <p>
                    <strong>tempo final:</strong> {casoSelecionado.configuracao.endTime}
                  </p>
                  <p>
                    <strong>delta t:</strong> {casoSelecionado.configuracao.deltaT}
                  </p>
                </div>
              )}

              <div className="casos-detalhe-block">
                <h4>como executar</h4>
                <p className="casos-comando-hint">
                  substitua os marcadores &lt;unidade&gt;, &lt;utilizador&gt; e &lt;pasta-do-projeto&gt; pelo seu
                  ambiente windows.
                </p>
                <pre className="casos-comando-wsl">{buildComandoWsl(casoSelecionado)}</pre>
                <button
                  type="button"
                  className="btn-mode-option casos-comando-copy"
                  onClick={() => {
                    void navigator.clipboard.writeText(buildComandoWsl(casoSelecionado));
                  }}
                >
                  copiar comandos
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default CasosCFD;
