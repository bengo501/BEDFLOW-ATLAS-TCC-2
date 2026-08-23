// componentes auxiliares para o wizard
import { useState } from 'react';
import { useLanguage } from '../context/LanguageContext';
import { getApiBase } from '../services/api';
import ThemeIcon from './ThemeIcon';

const REPO_BASE = 'https://github.com/bengo501/CFD-PIPELINE-TCC-1';

export const HelpModal = ({ show, onClose, section, paramHelp }) => {
  if (!show) return null;

  const sections = {
    'bed': 'geometria do leito',
    'lids': 'tampas',
    'particles': 'partículas',
    'packing': 'empacotamento',
    'export': 'exportação',
    'cfd': 'simulação cfd'
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h2>ajuda - parâmetros</h2>
          <button className="modal-close" onClick={onClose}>×</button>
        </div>
        
        <div className="modal-body">
          <div className="help-sections">
            {Object.entries(sections).map(([key, title]) => (
              <div key={key} className="help-section">
                <h3>{title}</h3>
                <div className="help-params">
                  {Object.entries(paramHelp)
                    .filter(([paramKey]) => paramKey.startsWith(`${key}.`))
                    .map(([paramKey, info]) => (
                      <div key={paramKey} className="help-param">
                        <h4>{paramKey.split('.')[1]}</h4>
                        <p><strong>descrição:</strong> {info.desc}</p>
                        {info.min !== undefined && (
                          <p><strong>range:</strong> {info.min}{info.unit} a {info.max}{info.unit}</p>
                        )}
                        <p><strong>exemplo:</strong> {info.exemplo}</p>
                      </div>
                    ))
                  }
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

export const DocsModal = ({ show, onClose }) => {
  if (!show) return null;

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content modal-docs" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h2>documentação do wizard</h2>
          <button className="modal-close" onClick={onClose}>×</button>
        </div>
        
        <div className="modal-body">
          <div className="docs-content">
            <section>
              <h3>sobre o wizard</h3>
              <p>
                o wizard permite criar arquivos .bed para definir leitos empacotados.
                esses arquivos são usados para gerar modelos 3D e simulações CFD.
              </p>
            </section>

            <section>
              <h3>modos disponíveis</h3>
              <ul>
                <li><strong>questionário interativo:</strong> preencha formulários passo a passo</li>
                <li><strong>editor de template:</strong> edite diretamente um arquivo .bed de exemplo</li>
                <li><strong>modo blender:</strong> gere apenas modelo 3D (sem CFD)</li>
                <li><strong>blender interativo:</strong> gere e abra automaticamente no blender</li>
              </ul>
            </section>

            <section>
              <h3>parâmetros principais</h3>
              <ul>
                <li><strong>geometria:</strong> diâmetro, altura, espessura da parede</li>
                <li><strong>partículas:</strong> tipo, tamanho, quantidade, densidade</li>
                <li><strong>empacotamento:</strong> método físico, gravidade, tempo</li>
                <li><strong>exportação:</strong> formatos de saída (blend, gltf, obj, stl)</li>
              </ul>
            </section>

            <section>
              <h3>dicas</h3>
              <ul>
                <li>use valores padrão para começar rapidamente</li>
                <li>digite ? em campos numéricos para ver ajuda</li>
                <li>comece com poucas partículas (50-100) para testes</li>
                <li>aumente gradualmente para modelos finais (500-1000+)</li>
              </ul>
            </section>

            <section>
              <h3>formatos de exportação</h3>
              <ul>
                <li><strong>.blend:</strong> arquivo nativo blender (completo)</li>
                <li><strong>.gltf/.glb:</strong> formato web (usado pelo visualizador)</li>
                <li><strong>.obj:</strong> formato universal (importar em outros programas)</li>
                <li><strong>.fbx:</strong> formato autodesk (unity, unreal)</li>
                <li><strong>.stl:</strong> impressão 3D, CAD</li>
              </ul>
            </section>

            <section>
              <h3>links úteis</h3>
              <ul>
                <li><a href={`${String(getApiBase()).replace(/\/$/, '')}/docs`} target="_blank" rel="noopener noreferrer">
                  documentação da api
                </a></li>
                <li><a href="https://github.com" target="_blank" rel="noopener noreferrer">
                  código fonte no github
                </a></li>
              </ul>
            </section>
          </div>
        </div>
      </div>
    </div>
  );
};

export const CreditsModal = ({ show, onClose }) => {
  const { language } = useLanguage();
  if (!show) return null;

  const pt = language === 'pt';

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content modal-credits-simple" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header modal-header--footer-modals">
          <h2>{pt ? 'Créditos' : 'Credits'}</h2>
          <button type="button" className="modal-close" onClick={onClose}>×</button>
        </div>

        <div className="modal-body">
          <div className="credits-content credits-content--plain">
            {pt ? (
              <>
                <p className="credits-lead">
                  Projeto de trabalho de conclusão de curso desenvolvido na pucrs / escola politécnica, em colaboração com o
                  laboratório lope.
                </p>
                <p>
                  <strong>Aluno:</strong> Bernardo Klein Heitz
                </p>
                <p>
                  <strong>Orientador</strong> — trabalho de conclusão de curso (ciência da computação): prof. Marco Aurélio
                  Mangan
                </p>
                <p>
                  <strong>Orientadora</strong> — iniciação científica voluntária: prof. Soraia Raupp Musse
                </p>
                <p>
                  <strong>Orientadores</strong> — bolsa de iniciação científica lope:
                  <br />
                  prof. Rubem Mário Vargas
                  <br />
                  Doutorando Henrique Martins Tavares
                </p>
              </>
            ) : (
              <>
                <p className="credits-lead">
                  Final project developed at pucrs / school of engineering, in collaboration with the lope laboratory.
                </p>
                <p>
                  <strong>Student:</strong> Bernardo Klein Heitz
                </p>
                <p>
                  <strong>Advisor</strong> — final project (computer science): prof. Marco Aurélio Mangan
                </p>
                <p>
                  <strong>Advisor</strong> — voluntary scientific initiation: prof. Soraia Raupp Musse
                </p>
                <p>
                  <strong>Advisors</strong> — lope scientific initiation scholarship:
                  <br />
                  prof. Rubem Mário Vargas
                  <br />
                  doctoral researcher Henrique Martins Tavares
                </p>
              </>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

const FOOTER_PROJECT_LINKS = [
    {
      key: 'github',
      labelPt: 'GitHub',
      labelEn: 'GitHub',
      href: REPO_BASE,
      iconLight: 'githubLight.png',
      iconDark: 'githubLight.png',
      kind: 'a',
    },
    {
      key: 'issues',
      labelPt: 'Issues',
      labelEn: 'Issues',
      href: `${REPO_BASE}/issues`,
      iconLight: 'issuesLight.png',
      iconDark: 'issuesLight.png',
      kind: 'a',
    },
    {
      key: 'kanban',
      labelPt: 'Kanban',
      labelEn: 'Kanban',
      href: 'https://github.com/users/bengo501/projects/2',
      iconLight: 'kanbanLight.png',
      iconDark: 'kanbanLight.png',
      kind: 'a',
    },
    {
      key: 'sobre',
      labelPt: 'Sobre',
      labelEn: 'About',
      iconLight: 'profileLight.png',
      iconDark: 'profileLight.png',
      kind: 'credits',
    },
    {
      key: 'readme',
      labelPt: 'Mais informações',
      labelEn: 'More information',
      href: `${REPO_BASE}/blob/main/README.md`,
      iconLight: 'docsLight.png',
      iconDark: 'docsLight.png',
      kind: 'a',
    },
    {
      key: 'repos',
      labelPt: 'Mais projetos',
      labelEn: 'More projects',
      href: 'https://github.com/bengo501?tab=repositories',
      iconLight: 'folderLight.png',
      iconDark: 'folderDark.png',
      kind: 'a',
    },
    {
      key: 'help',
      labelPt: 'Ajuda',
      labelEn: 'Help',
      iconLight: 'helpLight.png',
      iconDark: 'helpLight.png',
      kind: 'help',
    },
    {
      key: 'docs',
      labelPt: 'Documentação',
      labelEn: 'Documentation',
      iconLight: 'docsLight.png',
      iconDark: 'docsLight.png',
      kind: 'docs',
    },
];

const FOOTER_TECH_ROWS = [
    { key: 'openfoam', label: 'OpenFOAM', ver: '11', href: 'https://www.openfoam.org/', iconLight: 'triangle_white_outline.png', iconDark: 'triangle_black_outline.png' },
    { key: 'blender', label: 'Blender', ver: '4.x', href: 'https://www.blender.org/', iconLight: 'blenderLight.png', iconDark: 'blenderLight.png' },
    { key: 'react', label: 'React', ver: '18', href: 'https://react.dev/', iconLight: 'reactLight.png', iconDark: 'reactLight.png' },
    { key: 'vite', label: 'Vite', ver: '5.x', href: 'https://vitejs.dev/', iconLight: 'viteLight.png', iconDark: 'viteLight.png' },
    { key: 'python', label: 'Python', ver: '3.11', href: 'https://www.python.org/', iconLight: 'pythonLogoLight.png', iconDark: 'pythonLogoLight.png' },
    { key: 'wsl', label: 'WSL', ver: '2', href: 'https://learn.microsoft.com/windows/wsl/', iconLight: 'wslLogoLight.png', iconDark: 'wslLogoLight.png' },
    { key: 'javascript', label: 'JavaScript', ver: 'ES6+', href: 'https://developer.mozilla.org/docs/Web/JavaScript', iconLight: 'jsLight.png', iconDark: 'jsLight.png' },
    { key: 'java', label: 'Java', ver: '17', href: 'https://openjdk.org/', iconLight: 'javaLight.png', iconDark: 'javaLight.png' },
    { key: 'css', label: 'CSS', ver: '3', href: 'https://developer.mozilla.org/docs/Web/CSS', iconLight: 'cssLight.png', iconDark: 'cssLight.png' },
    { key: 'antlr', label: 'ANTLR', ver: '4.x', href: 'https://www.antlr.org/', iconLight: 'antlrLight.png', iconDark: 'antlrLight.png' },
    { key: 'fastapi', label: 'FastAPI', ver: '0.x', href: 'https://fastapi.tiangolo.com/', iconLight: 'fastApiLight.png', iconDark: 'fastApiLight.png' },
    { key: 'railway', label: 'Railway', ver: 'cloud', href: 'https://railway.app/', iconLight: 'railwayLight.png', iconDark: 'railwayLight.png' },
    { key: 'three', label: 'Three.js', ver: 'r150+', href: 'https://threejs.org/', iconLight: 'cfd_gear_white.png', iconDark: 'cfd_gear_white.png' },
    { key: 'axios', label: 'Axios', ver: '1.x', href: 'https://axios-http.com/', iconLight: 'docsLight.png', iconDark: 'docsLight.png' },
    { key: 'docker', label: 'Docker', ver: '', href: 'https://www.docker.com/', iconLight: 'pipelineLight.png', iconDark: 'pipeline.png' },
    { key: 'sqlalchemy', label: 'SQLAlchemy', ver: '2.x', href: 'https://www.sqlalchemy.org/', iconLight: 'pythonLogoLight.png', iconDark: 'pythonLogoLight.png' },
    { key: 'uvicorn', label: 'Uvicorn', ver: '0.x', href: 'https://www.uvicorn.org/', iconLight: 'fastApiLight.png', iconDark: 'fastApiLight.png' },
    { key: 'pydantic', label: 'Pydantic', ver: '2.x', href: 'https://docs.pydantic.dev/', iconLight: 'pythonLogoLight.png', iconDark: 'pythonLogoLight.png' },
    { key: 'numpy', label: 'NumPy', ver: '1.x', href: 'https://numpy.org/', iconLight: 'pythonLogoLight.png', iconDark: 'pythonLogoLight.png' },
    { key: 'openmpi', label: 'Open MPI', ver: '', href: 'https://www.open-mpi.org/', iconLight: 'triangle_white_outline.png', iconDark: 'triangle_black_outline.png' },
];

const FOOTER_DB_ROWS = [
    { key: 'pg', label: 'PostgreSQL', ver: '15', href: 'https://www.postgresql.org/', iconLight: '2106624.png', iconDark: 'postgresqlDark.png' },
    { key: 'redis', label: 'Redis', ver: '7', href: 'https://redis.io/', iconLight: 'redis.png', iconDark: 'redisDark.png' },
    { key: 'minio', label: 'MinIO', ver: 'S3', href: 'https://min.io/', iconLight: 'minio.png', iconDark: 'minioDark.png' },
    { key: 'sqlite', label: 'SQLite', ver: '3', href: 'https://www.sqlite.org/', iconLight: 'docsLight.png', iconDark: 'docsLight.png' },
    { key: 'celery', label: 'Celery', ver: '', href: 'https://docs.celeryq.dev/', iconLight: 'pythonLogoLight.png', iconDark: 'pythonLogoLight.png' },
];

function footerSaibaRowIcon(light, dark, invert = false) {
  return (
    <ThemeIcon
      light={light}
      dark={dark}
      alt=""
      className={`footer-saiba-row-icon${invert ? ' footer-saiba-row-icon--inv' : ''}`}
      location="footer"
    />
  );
}

/** modal do footer por secção: project | tech | database */
export const FooterInfoModal = ({
  variant,
  show,
  onClose,
  onOpenHelp,
  onOpenDocs,
  onOpenCredits,
}) => {
  const { language } = useLanguage();
  if (!show || !variant) return null;

  const pt = language === 'pt';

  const titles = {
    project: pt ? 'Projeto' : 'Project',
    tech: pt ? 'Tecnologias' : 'Technologies',
    database: pt ? 'Banco de dados' : 'Database',
  };

  const runAction = (fn) => {
    onClose();
    if (typeof fn === 'function') {
      window.setTimeout(() => fn(), 0);
    }
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div
        className={`modal-content modal-footer-saiba-mais modal-footer-saiba-mais--${variant}`}
        onClick={(e) => e.stopPropagation()}
      >
        <div className="modal-header modal-header--footer-modals">
          <h2>{titles[variant]}</h2>
          <button type="button" className="modal-close" onClick={onClose} aria-label={pt ? 'fechar' : 'close'}>
            ×
          </button>
        </div>

        <div className="modal-body modal-body--footer-saiba modal-body--footer-saiba-single">
          {variant === 'project' && (
            <section className="footer-saiba-section footer-saiba-section--solo">
              <ul className="footer-saiba-linklist">
                {FOOTER_PROJECT_LINKS.map((row) => (
                  <li key={row.key}>
                    {row.kind === 'a' && (
                      <a href={row.href} target="_blank" rel="noopener noreferrer" className="footer-saiba-row">
                        {footerSaibaRowIcon(row.iconLight, row.iconDark)}
                        <span className="footer-saiba-row-label">{pt ? row.labelPt : row.labelEn}</span>
                      </a>
                    )}
                    {row.kind === 'credits' && (
                      <button
                        type="button"
                        className="footer-saiba-row footer-saiba-row--btn"
                        onClick={() => runAction(onOpenCredits)}
                      >
                        {footerSaibaRowIcon(row.iconLight, row.iconDark)}
                        <span className="footer-saiba-row-label">{pt ? row.labelPt : row.labelEn}</span>
                      </button>
                    )}
                    {row.kind === 'help' && (
                      <button
                        type="button"
                        className="footer-saiba-row footer-saiba-row--btn"
                        onClick={() => runAction(onOpenHelp)}
                      >
                        {footerSaibaRowIcon(row.iconLight, row.iconDark)}
                        <span className="footer-saiba-row-label">{pt ? row.labelPt : row.labelEn}</span>
                      </button>
                    )}
                    {row.kind === 'docs' && (
                      <button
                        type="button"
                        className="footer-saiba-row footer-saiba-row--btn"
                        onClick={() => runAction(onOpenDocs)}
                      >
                        {footerSaibaRowIcon(row.iconLight, row.iconDark)}
                        <span className="footer-saiba-row-label">{pt ? row.labelPt : row.labelEn}</span>
                      </button>
                    )}
                  </li>
                ))}
              </ul>
            </section>
          )}

          {variant === 'tech' && (
            <section className="footer-saiba-section footer-saiba-section--solo">
              <ul className="footer-saiba-techlist">
                {FOOTER_TECH_ROWS.map((row) => (
                  <li key={row.key}>
                    <a
                      href={row.href}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="footer-saiba-row footer-saiba-row--spread"
                    >
                      {footerSaibaRowIcon(row.iconLight, row.iconDark)}
                      <span className="footer-saiba-name">{row.label}</span>
                      {row.ver ? <span className="footer-saiba-ver">{row.ver}</span> : null}
                    </a>
                  </li>
                ))}
              </ul>
            </section>
          )}

          {variant === 'database' && (
            <section className="footer-saiba-section footer-saiba-section--solo">
              <ul className="footer-saiba-techlist">
                {FOOTER_DB_ROWS.map((row) => (
                  <li key={row.key}>
                    <a
                      href={row.href}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="footer-saiba-row footer-saiba-row--spread"
                    >
                      {footerSaibaRowIcon(row.iconLight, row.iconDark, true)}
                      <span className="footer-saiba-name">{row.label}</span>
                      {row.ver ? <span className="footer-saiba-ver">{row.ver}</span> : null}
                    </a>
                  </li>
                ))}
              </ul>
            </section>
          )}
        </div>
      </div>
    </div>
  );
};

export const TemplateEditor = ({ show, onClose, onSubmit }) => {
  const [templateText, setTemplateText] = useState(
    `// template padrao para leito empacotado
// edite os valores conforme necessario

bed {
    diameter = 0.05 m;           // diametro do leito
    height = 0.1 m;              // altura do leito
    wall_thickness = 0.002 m;    // espessura da parede
    clearance = 0.01 m;          // folga superior
    material = "steel";          // material da parede
    roughness = 0.0 m;           // rugosidade (opcional)
}

lids {
    top_type = "flat";           // tipo da tampa superior
    bottom_type = "flat";        // tipo da tampa inferior
    top_thickness = 0.003 m;     // espessura tampa superior
    bottom_thickness = 0.003 m;  // espessura tampa inferior
    seal_clearance = 0.001 m;    // folga do selo (opcional)
}

particles {
    kind = "sphere";             // tipo de particula
    diameter = 0.005 m;          // diametro das particulas
    count = 100;                 // numero de particulas
    target_porosity = 0.4;       // porosidade alvo (opcional)
    density = 2500.0 kg/m3;      // densidade do material
    mass = 0.0 g;                // massa das particulas (opcional)
    restitution = 0.3;           // coeficiente de restituicao (opcional)
    friction = 0.5;              // coeficiente de atrito (opcional)
    rolling_friction = 0.1;      // atrito de rolamento (opcional)
    linear_damping = 0.1;        // amortecimento linear (opcional)
    angular_damping = 0.1;       // amortecimento angular (opcional)
    seed = 42;                   // seed para reproducibilidade (opcional)
}

packing {
    method = "rigid_body";       // metodo de empacotamento
    gravity = -9.81 m/s2;        // gravidade
    substeps = 10;               // sub-passos de simulacao (opcional)
    iterations = 10;             // iteracoes (opcional)
    damping = 0.1;               // amortecimento (opcional)
    rest_velocity = 0.01 m/s;    // velocidade de repouso (opcional)
    max_time = 5.0 s;            // tempo maximo (opcional)
    collision_margin = 0.001 m;  // margem de colisao (opcional)
}

export {
    formats = ["blend", "glb", "obj"];  // formatos de exportacao
    units = "m";                         // unidades de saida (opcional)
    scale = 1.0;                         // escala (opcional)
    wall_mode = "surface";               // modo da parede
    fluid_mode = "none";                 // modo do fluido
    manifold_check = true;               // verificar manifold (opcional)
    merge_distance = 0.001 m;            // distancia de fusao (opcional)
}

// secao CFD (opcional - descomente se necessario)
/*
cfd {
    regime = "laminar";                  // regime CFD
    inlet_velocity = 0.1 m/s;            // velocidade de entrada (opcional)
    fluid_density = 1.225 kg/m3;         // densidade do fluido (opcional)
    fluid_viscosity = 1.8e-5 Pa.s;      // viscosidade do fluido (opcional)
    max_iterations = 1000;               // iteracoes maximas (opcional)
    convergence_criteria = 1e-6;         // criterio de convergencia (opcional)
    write_fields = false;                // escrever campos (opcional)
}
*/`
  );

  if (!show) return null;

  const handleSubmit = () => {
    onSubmit(templateText);
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content modal-template" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h2>editor de template .bed</h2>
          <button className="modal-close" onClick={onClose}>×</button>
        </div>
        
        <div className="modal-body">
          <p className="template-hint">
            edite o template abaixo e clique em "usar este template" para continuar
          </p>
          <textarea
            className="template-editor"
            value={templateText}
            onChange={(e) => setTemplateText(e.target.value)}
            spellCheck={false}
          />
        </div>
        
        <div className="modal-footer">
          <button className="btn btn-secondary" onClick={onClose}>
            cancelar
          </button>
          <button className="btn btn-primary" onClick={handleSubmit}>
            usar este template
          </button>
        </div>
      </div>
    </div>
  );
};

