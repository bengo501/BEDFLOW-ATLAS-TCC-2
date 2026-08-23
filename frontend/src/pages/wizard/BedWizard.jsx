import { useState, useMemo, useEffect } from 'react';
import BedPreview3D from './BedPreview3D';
import { HelpModal, DocsModal } from './WizardHelpers';
import ThemeIcon from './ThemeIcon';
import BackendConnectionError from './BackendConnectionError';
import { useLanguage } from '../context/LanguageContext';
import {
  getWizardCliInstructions,
  launchWizardCliTerminal,
  postBedWizard,
  generateModel,
  postPipelineFullSimulation,
  getBedTemplateDefault,
  parseApiError,
} from '../services/api';
import BedLoadModal from './bed/BedLoadModal';
import {
  ICM_HOLLOW,
  ICM_VISIBLE,
  ICM_SOLID,
  modeIncludesInnerCore,
  EXPORT_MAIN_VISIBILITY_KEYS,
  syncVisibilityOnModeChange,
  exportMainLabelKey,
  internalCylinderModeHintKey,
  internalCylinderExportNoteKey,
} from '../lib/bedInternalCylinderUi';
import '../styles/BedWizard.css';
import '../styles/CasosCFD.css';
import '../styles/TemplateEditor.css';

const REPO_PLACEHOLDER = '<raiz-do-repositorio>';

function randomSeedValue() {
  return String(Math.floor(Math.random() * 2147483646) + 1);
}

function SeedFieldRow({ label, value, onChange, onGenerate, hint, id }) {
  return (
    <div className="form-group seed-field-row">
      <label htmlFor={id}>{label}</label>
      <div className="seed-field-input-row">
        <input
          id={id}
          type="number"
          min="1"
          max="2147483647"
          value={value}
          onChange={onChange}
        />
        <button type="button" className="btn-seed-generate" onClick={onGenerate}>
          gerar
        </button>
      </div>
      {hint ? <small>{hint}</small> : null}
    </div>
  );
}

function modelingProfileFromBackend(generationBackend) {
  const gb = String(generationBackend || '').toLowerCase();
  if (gb.includes('python') || gb === 'pure_python') return 'python';
  return 'blender';
}

const MODES_WITH_OPTIONAL_CFD = ['interactive', 'pipeline_completo'];

const DEFAULT_CFD_PARAMS = {
  regime: 'laminar',
  inlet_velocity: '0.1',
  fluid_density: '1.225',
  fluid_viscosity: '1.8e-5',
  max_iterations: '1000',
  convergence_criteria: '1e-6',
  write_fields: false,
};

function buildCliPreset(kind) {
  if (kind === 'quick-tests') {
    return {
      windows_cmd: `cd /d "${REPO_PLACEHOLDER}" && python dsl\\wizard_quick_tests.py`,
      unix_sh: `cd "${REPO_PLACEHOLDER}" && python3 dsl/wizard_quick_tests.py`,
      hintKey: 'quickTestsCliHint',
      script_exists: true,
      offline: false,
    };
  }
  if (kind === 'setup-install') {
    return {
      windows_cmd: `cd /d "${REPO_PLACEHOLDER}"\r\npython -m pip install -r dsl\\requirements-terminal.txt`,
      unix_sh: `cd "${REPO_PLACEHOLDER}"\npython3 -m pip install -r dsl/requirements-terminal.txt`,
      hintKey: 'terminalSetupHint',
      script_exists: true,
      offline: false,
    };
  }
  if (kind === 'wizard-run') {
    return {
      windows_cmd: `cd /d "${REPO_PLACEHOLDER}" && python bed_wizard.py`,
      unix_sh: `cd "${REPO_PLACEHOLDER}" && python3 bed_wizard.py`,
      hintKey: 'terminalSetupRunHint',
      script_exists: true,
      offline: false,
    };
  }
  return {
    windows_cmd: `cd /d "${REPO_PLACEHOLDER}" && python bed_wizard.py`,
    unix_sh: `cd "${REPO_PLACEHOLDER}" && python3 bed_wizard.py`,
    hintKey: 'terminalSetupRunHint',
    script_exists: true,
    offline: false,
  };
}

function IconCopy({ className }) {
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
      <rect x="9" y="9" width="13" height="13" rx="2" ry="2" />
      <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1" />
    </svg>
  );
}

function IconArrowRight({ className }) {
  return (
    <svg
      className={className}
      width="16"
      height="16"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2.2"
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden
    >
      <path d="M5 12h14M13 6l6 6-6 6" />
    </svg>
  );
}

const BedWizard = ({ onNavigateTab, onOpenMeshViewer } = {}) => {
  const { language, t } = useLanguage();
  const pt = language === 'pt';
  const [step, setStep] = useState(0);
  const [mode, setMode] = useState(null);
  const [params, setParams] = useState({
    bed: {
      diameter: '0.05',
      height: '0.1',
      wall_thickness: '0.002',
      clearance: '0.01',
      material: 'steel',
      roughness: '0.0',
      internal_cylinder_mode: 'hollow_boolean_applied',
      visibility: {
        show_outer_cylinder: true,
        show_internal_cylinder: false,
        show_particles: true,
        show_boolean_tools: false,
        export_boolean_tools: false,
      },
    },
    lids: {
      top_type: 'flat',
      bottom_type: 'flat',
      top_thickness: '0.003',
      bottom_thickness: '0.003',
      seal_clearance: '0.001'
    },
    particles: {
      kind: 'sphere',
      diameter: '0.005',
      count: '100',
      target_porosity: '0.4',
      density: '2500.0',
      mass: '0.0',
      restitution: '0.3',
      friction: '0.5',
      rolling_friction: '0.1',
      linear_damping: '0.1',
      angular_damping: '0.1',
      seed: '42'
    },
    packing: {
      method: 'rigid_body',
      gravity: '-9.81',
      substeps: '10',
      iterations: '10',
      damping: '0.1',
      rest_velocity: '0.01',
      max_time: '5.0',
      collision_margin: '0.001',
      gap: '0.0001',
      random_seed: '42',
      max_placement_attempts: '500000',
      strict_validation: true,
      step_x: '',
      dem: {
        time_step: '0.0001',
        steps: '30000',
        gravity: '9.81',
        stiffness: '5000',
        damping: '0.2',
        friction: '0.2',
        settle_threshold: '0.001',
        max_velocity_threshold: '0.01',
        seed: '42',
      },
    },
    export: {
      formats: ['stl_binary', 'blend'],
      units: 'm',
      scale: '1.0',
      wall_mode: 'surface',
      fluid_mode: 'none',
      manifold_check: true,
      merge_distance: '0.001'
    },
    geometry_mode: 'full_3d',
    generation_backend: 'blender',
    slice: null,
    statistical_2d: null,
    cfd: { ...DEFAULT_CFD_PARAMS },
  });
  const [includeCFD, setIncludeCFD] = useState(false);

  const showCfdSteps = MODES_WITH_OPTIONAL_CFD.includes(mode);
  const [fileName, setFileName] = useState('meu_leito.bed');

  // informações de ajuda para cada parâmetro
  const paramHelp = {
    'bed.diameter': {
      desc: 'diâmetro interno do leito cilíndrico',
      min: 0.01, max: 2.0, unit: 'm',
      exemplo: 'leito de 5cm = 0.05m'
    },
    'bed.height': {
      desc: 'altura total do leito cilíndrico',
      min: 0.01, max: 5.0, unit: 'm',
      exemplo: 'leito de 10cm = 0.1m'
    },
    'bed.wall_thickness': {
      desc: 'espessura da parede do cilindro',
      min: 0.0001, max: 0.1, unit: 'm',
      exemplo: 'parede de 2mm = 0.002m'
    },
    'particles.count': {
      desc: 'quantidade total de partículas',
      min: 1, max: 10000, unit: '',
      exemplo: '100 partículas = empacotamento rápido'
    },
    'particles.diameter': {
      desc: 'diâmetro das partículas esféricas',
      min: 0.0001, max: 0.5, unit: 'm',
      exemplo: 'partícula de 5mm = 0.005m'
    }
  };

  const [showHelp, setShowHelp] = useState(false);
  const [helpSection, setHelpSection] = useState(null);
  const [showDocs, setShowDocs] = useState(false);
  const [bedLoadOpen, setBedLoadOpen] = useState(null);
  const [wizardConnectionError, setWizardConnectionError] = useState(null);
  const [submitBusy, setSubmitBusy] = useState(false);
  const [criarDock, setCriarDock] = useState(null);
  const [wizardCliBackend, setWizardCliBackend] = useState({ script_exists: true, offline: true });
  const [wizardCliError, setWizardCliError] = useState(null);
  const [wizardCliBusy, setWizardCliBusy] = useState(false);
  const [wizardCliLaunchMsg, setWizardCliLaunchMsg] = useState('');

  const skipPackingStep = params.geometry_mode === 'pseudo_2d_statistical';

  const steps = useMemo(() => {
    const list = [
      { title: t('selectMode'), section: 'mode' },
      { title: t('bedGeometry'), section: 'bed' },
      { title: t('lids'), section: 'lids' },
      { title: t('particles'), section: 'particles' },
      ...(skipPackingStep ? [] : [{ title: t('packing'), section: 'packing' }]),
      { title: t('pipelineStep'), section: 'pipeline' },
      { title: t('export'), section: 'export' },
    ];
    if (showCfdSteps) {
      list.push({ title: t('cfdParams'), section: 'cfd-toggle' });
      if (includeCFD) {
        list.push({ title: t('cfdParamsConfigure'), section: 'cfd-form' });
      }
    }
    list.push({ title: t('confirmation'), section: 'confirm' });
    return list;
  }, [language, showCfdSteps, includeCFD, t, skipPackingStep]);

  const currentSection = steps[step]?.section;

  useEffect(() => {
    if (step > 0 && step >= steps.length) {
      setStep(steps.length - 1);
    }
  }, [step, steps.length]);

  const handleModeSelect = (selectedMode) => {
    setMode(selectedMode);
    setIncludeCFD(false);
    setStep(1);
  };

  const handleIncludeCfdChange = (checked) => {
    setIncludeCFD(checked);
    if (checked) {
      setParams((prev) => ({
        ...prev,
        cfd: prev.cfd || { ...DEFAULT_CFD_PARAMS },
      }));
    }
  };

  useEffect(() => {
    if (step !== 0) return undefined;
    let cancelled = false;
    void (async () => {
      try {
        const data = await getWizardCliInstructions();
        if (!cancelled) {
          setWizardCliBackend({ script_exists: data.script_exists, offline: false });
          if (!data.script_exists) setWizardCliError(t('wizardCliLoadError'));
        }
      } catch {
        if (!cancelled) {
          setWizardCliBackend({ script_exists: true, offline: true });
        }
      }
    })();
    return () => {
      cancelled = true;
    };
  }, [step, t]);

  const openQuickTestsDock = () => {
    setCriarDock('quick-tests');
    setWizardCliError(null);
    setWizardCliLaunchMsg('');
  };

  const openTerminalSetupDock = () => {
    setCriarDock('terminal-setup');
    setWizardCliError(null);
    setWizardCliLaunchMsg('');
  };

  const closeCriarDock = () => {
    setCriarDock(null);
    setWizardCliLaunchMsg('');
  };

  const handleLaunchWizardCli = async () => {
    setWizardCliBusy(true);
    setWizardCliLaunchMsg('');
    try {
      await launchWizardCliTerminal();
      setWizardCliLaunchMsg(t('wizardCliLaunchOk'));
    } catch {
      setWizardCliLaunchMsg(t('wizardCliLaunchFail'));
    } finally {
      setWizardCliBusy(false);
    }
  };

  const handleInputChange = (section, field, value) => {
    setParams((prev) => {
      const next = {
        ...prev,
        [section]: {
          ...prev[section],
          [field]: value,
        },
      };
      if (section === 'packing' && field === 'method') {
        if (value === 'dem') {
          next.generation_backend = 'python_engine';
        }
      }
      return next;
    });
  };

  const generateSeedFor = (section, field) => {
    handleInputChange(section, field, randomSeedValue());
  };

  const handleMetaChange = (field, value) => {
    setParams((prev) => {
      const next = { ...prev, [field]: value };
      if (field === 'geometry_mode') {
        if (value === 'pseudo_2d_thin_slice') {
          next.slice = prev.slice || {
            slice_enabled: true,
            slice_thickness: '0.002',
            slice_axis: 'y',
            slice_position: '0.0',
            min_slice_particle_radius: '0.00001',
            keep_only_intersecting_particles: true,
            preserve_original_packing: true,
            debug_export_gizmos: false,
          };
          next.statistical_2d = null;
        } else if (value === 'pseudo_2d_statistical') {
          next.generation_backend = 'python_engine';
          next.packing = {
            ...(prev.packing || {}),
            method: 'statistical_reconstruction',
          };
          next.slice = null;
          const bed = prev.bed || {};
          next.statistical_2d = prev.statistical_2d || {
            domain_width: String(bed.diameter ?? '0.05'),
            domain_height: String(bed.height ?? '0.1'),
            target_porosity: String(prev.particles?.target_porosity ?? '0.4'),
            tolerance: '0.02',
            max_attempts: '50',
            slice_thickness: '0.002',
            seed: String(prev.particles?.seed ?? '42'),
          };
        } else {
          next.slice = null;
          next.statistical_2d = null;
        }
      }
      return next;
    });
  };

  const handleSliceChange = (field, value) => {
    setParams((prev) => ({
      ...prev,
      slice: {
        ...(prev.slice || {
          slice_enabled: true,
          slice_thickness: '0.002',
          slice_axis: 'z',
          slice_position: '0.0',
          min_slice_particle_radius: '0.00001',
          keep_only_intersecting_particles: true,
          preserve_original_packing: true,
          debug_export_gizmos: false,
        }),
        [field]: value,
      },
    }));
  };

  const handleStatistical2DChange = (field, value) => {
    setParams((prev) => ({
      ...prev,
      statistical_2d: {
        ...(prev.statistical_2d || {
          domain_width: String(prev.bed?.diameter ?? '0.05'),
          domain_height: String(prev.bed?.height ?? '0.1'),
          target_porosity: String(prev.particles?.target_porosity ?? '0.4'),
          tolerance: '0.02',
          max_attempts: '50',
          slice_thickness: '0.002',
          seed: String(prev.particles?.seed ?? '42'),
        }),
        [field]: value,
      },
    }));
  };

  const handleDemChange = (field, value) => {
    setParams((prev) => ({
      ...prev,
      packing: {
        ...prev.packing,
        dem: {
          ...(prev.packing.dem || {
            time_step: '0.0001',
            steps: '30000',
            gravity: '9.81',
            stiffness: '5000',
            damping: '0.2',
            friction: '0.2',
            settle_threshold: '0.001',
            max_velocity_threshold: '0.01',
            seed: '42',
          }),
          [field]: value,
        },
      },
    }));
  };

  const handleNext = () => {
    if (step < steps.length - 1) {
      // sempre ir para próximo passo sequencialmente
      // não pular mais automaticamente
      setStep(step + 1);
    }
  };

  const handlePrev = () => {
    if (step > 0) {
      // sempre voltar sequencialmente
      setStep(step - 1);
    }
  };

  const wantsModel3dAfterWizard = () =>
    mode === 'blender' ||
    mode === 'blender_interactive' ||
    mode === 'interactive';

  const handleSubmit = async () => {
    if (submitBusy) return;
    setSubmitBusy(true);
    try {
      setWizardConnectionError(null);
      const bedData = {
        mode: mode,
        fileName: fileName,
        params: {
          ...params,
          cfd: showCfdSteps && includeCFD ? params.cfd : null,
        },
      };

      const result = await postBedWizard(bedData);
      const profile = modelingProfileFromBackend(params.generation_backend);
      const icm = params.bed?.internal_cylinder_mode || ICM_HOLLOW;
      let msg = `${pt ? 'sucesso' : 'success'}: ${fileName}\njson: ${result.json_file}`;
      if (icm === ICM_SOLID) {
        msg += `\n\n${t('bedSolidSlowHint')}`;
      }

      if (wantsModel3dAfterWizard()) {
        const ask =
          mode === 'blender_interactive'
            ? t('bedWizardConfirmGenerate3dBlender')
            : t('bedWizardConfirmGenerate3d');
        if (window.confirm(ask)) {
          const gen = await generateModel(
            result.json_file,
            mode === 'blender_interactive',
            profile,
          );
          msg += `\n\n${t('bedWizardJobStarted')}: ${gen.job_id}`;
          msg += `\n${t('bedWizardMonitorJobs')}`;
        }
      }

      alert(msg);

      if (mode === 'pipeline_completo') {
        if (confirm('deseja executar o pipeline completo agora? (modelo 3d + simulação cfd)')) {
          const pipelineResult = await postPipelineFullSimulation(
            {
              bed: params.bed,
              lids: params.lids,
              particles: params.particles,
              packing: params.packing,
              export: params.export,
              geometry_mode: params.geometry_mode,
              generation_backend: params.generation_backend,
              slice: params.slice,
              statistical_2d: params.statistical_2d,
              cfd: includeCFD && params.cfd
                ? {
                    regime: params.cfd.regime,
                    inlet_velocity: params.cfd.inlet_velocity,
                    fluid_density: params.cfd.fluid_density,
                    fluid_viscosity: params.cfd.fluid_viscosity,
                    max_iterations: params.cfd.max_iterations,
                    convergence_criteria: params.cfd.convergence_criteria,
                    write_fields: params.cfd.write_fields,
                  }
                : null,
            },
            { modeling_profile: modelingProfileFromBackend(params.generation_backend) },
          );
          alert(`pipeline completo iniciado!\njob_id: ${pipelineResult.job_id}\nmonitore o progresso na seção 'jobs'`);
        }
      }

      setStep(0);
      setMode(null);
    } catch (error) {
      console.error('erro:', error);
      const msg = parseApiError(error) || 'erro ao criar arquivo .bed';
      alert(msg);
      if (
        error?.code === 'ERR_NETWORK' ||
        (!error?.response && error?.request)
      ) {
        setWizardConnectionError(t('backendConnectionError'));
      } else {
        setWizardConnectionError(null);
      }
    } finally {
      setSubmitBusy(false);
    }
  };

  const goHubTab = (tab) => {
    if (typeof onNavigateTab === 'function') onNavigateTab(tab);
  };

  const renderCliCommandsBlock = (preset, { showLaunch = false, templateCopyButtons = false } = {}) => (
    <div className="wizard-cli-commands">
      <p className="wizard-cli-hint">{t(preset.hintKey)}</p>
      <label>windows (cmd)</label>
      <pre>{preset.windows_cmd}</pre>
      <button
        type="button"
        className={templateCopyButtons ? 'btn-copy' : 'btn-secondary btn-mode-option'}
        onClick={() => navigator.clipboard.writeText(preset.windows_cmd)}
      >
        {templateCopyButtons ? (
          <>
            <IconCopy className="template-toolbar-svg" />
            {pt ? 'copiar' : 'copy'}
          </>
        ) : (
          t('wizardCliCopyWin')
        )}
      </button>
      <label>linux / mac / wsl (bash)</label>
      <pre>{preset.unix_sh}</pre>
      <button
        type="button"
        className={templateCopyButtons ? 'btn-copy' : 'btn-secondary btn-mode-option'}
        onClick={() => navigator.clipboard.writeText(preset.unix_sh)}
      >
        {templateCopyButtons ? (
          <>
            <IconCopy className="template-toolbar-svg" />
            {pt ? 'copiar' : 'copy'}
          </>
        ) : (
          t('wizardCliCopyUnix')
        )}
      </button>
      {showLaunch && (
        <div className="wizard-cli-actions">
          <button
            type="button"
            className="btn-primary btn-mode-option"
            title={wizardCliBackend.offline ? t('wizardCliLaunchNeedsBackend') : undefined}
            disabled={
              wizardCliBusy || !wizardCliBackend.script_exists || wizardCliBackend.offline
            }
            onClick={() => {
              void handleLaunchWizardCli();
            }}
          >
            {t('wizardCliOpenTerminal')}
          </button>
        </div>
      )}
    </div>
  );

  const renderCliPanel = ({
    title,
    intro,
    presets,
    showLaunch = false,
    compact = false,
    onClose,
    titleIcon,
    templateCopyButtons = false,
  }) => (
    <div className={`criar-cli-panel${compact ? ' criar-cli-panel--compact' : ''}`}>
      <div className="criar-cli-panel-head">
        <div className="criar-cli-panel-title-row">
          {titleIcon && (
            <ThemeIcon
              light={titleIcon.light}
              dark={titleIcon.dark}
              alt=""
              className="criar-cli-panel-title-icon"
            />
          )}
          <h3 id="criar-dock-title" className="criar-cli-panel-title">{title}</h3>
        </div>
        {onClose && (
          <button type="button" className="criar-cli-panel-close" onClick={onClose} aria-label={t('close')}>
            ×
          </button>
        )}
      </div>
      {intro && <p className="wizard-cli-intro">{intro}</p>}
      {wizardCliError && <p className="wizard-cli-err">{wizardCliError}</p>}
      {presets.map((preset) => (
        <div key={preset.hintKey} className="criar-cli-preset-block">
          {renderCliCommandsBlock(preset, {
            showLaunch: preset.showLaunch ?? showLaunch,
            templateCopyButtons,
          })}
        </div>
      ))}
      {wizardCliLaunchMsg && <p className="wizard-cli-launch-msg">{wizardCliLaunchMsg}</p>}
      {!compact && <p className="wizard-cli-foot">{t('wizardCliFootnote')}</p>}
    </div>
  );

  const renderModeSelection = () => {
    const bedFileButtons = (modeKey) => (
      <div className="mode-options">
        <button
          type="button"
          className="btn-mode-option"
          onClick={(e) => {
            e.stopPropagation();
            setMode(modeKey);
            setBedLoadOpen({ hubMode: modeKey });
          }}
        >
          <ThemeIcon light="folderLight.png" dark="folderDark.png" alt="" className="btn-icon" />
          {t('loadBedFile')}
        </button>
        <button
          type="button"
          className="btn-mode-option"
          onClick={(e) => {
            e.stopPropagation();
            setMode(modeKey);
            void (async () => {
              try {
                setWizardConnectionError(null);
                const data = await getBedTemplateDefault();
                setBedLoadOpen({
                  hubMode: modeKey,
                  initialContent: data.content,
                  initialFilename: data.filename || 'template_padrao.bed',
                });
              } catch (error) {
                console.error('erro:', error);
                setWizardConnectionError(t('backendConnectionError'));
              }
            })();
          }}
        >
          <ThemeIcon light="textEditorLight.png" dark="textEditor.png" alt="" className="btn-icon" />
          {t('editBedFile')}
        </button>
      </div>
    );

    const cardKey =
      (fn) => (e) => {
        if (e.key === 'Enter' || e.key === ' ') {
          e.preventDefault();
          fn();
        }
      };

    return (
      <div className="mode-selection mode-selection--criar-hub">
        <div className="mode-cards mode-cards-terminal mode-cards-criar-all">
          <div
            className="mode-card"
            role="button"
            tabIndex={0}
            onClick={() => handleModeSelect('interactive')}
            onKeyDown={cardKey(() => handleModeSelect('interactive'))}
          >
            <ThemeIcon light="textEditorLight.png" dark="textEditor.png" alt="" className="mode-icon-small" />
            <h3>{t('hubBasicTitle')}</h3>
            <p className="mode-card-desc">{t('hubBasicDesc')}</p>
            {bedFileButtons('interactive')}
          </div>
          <div
            className="mode-card"
            role="button"
            tabIndex={0}
            onClick={() => handleModeSelect('blender_interactive')}
            onKeyDown={cardKey(() => handleModeSelect('blender_interactive'))}
          >
            <ThemeIcon light="blenderLight.png" dark="blender-svgrepo-com.svg" alt="" className="mode-icon-small" />
            <h3>{t('hubGen3dTitle')}</h3>
            <p className="mode-card-desc">{t('hubGen3dDesc')}</p>
            {bedFileButtons('blender_interactive')}
          </div>
          <div
            className="mode-card"
            role="button"
            tabIndex={0}
            onClick={() => handleModeSelect('pipeline_completo')}
            onKeyDown={cardKey(() => handleModeSelect('pipeline_completo'))}
          >
            <ThemeIcon light="pipelineLight.png" dark="pipeline.png" alt="" className="mode-icon-small" />
            <h3>{t('hubPipeTitle')}</h3>
            <p className="mode-card-desc">{t('hubPipeDesc')}</p>
            {bedFileButtons('pipeline_completo')}
          </div>
          <div
            className="mode-card"
            role="button"
            tabIndex={0}
            onClick={() => handleModeSelect('pipeline_blender_cfd')}
            onKeyDown={cardKey(() => handleModeSelect('pipeline_blender_cfd'))}
          >
            <div className="mode-icon-combo">
              <ThemeIcon light="blenderLight.png" dark="blender-svgrepo-com.svg" alt="" className="mode-icon-small" />
              <span className="plus-symbol">+</span>
              <ThemeIcon light="cfd_gear_white.png" dark="image-removebg-preview(12).png" alt="" className="mode-icon-small" />
            </div>
            <h3>{t('hubPipeBlenderCfdTitle')}</h3>
            <p className="mode-card-desc">{t('hubPipeBlenderCfdDesc')}</p>
            {bedFileButtons('pipeline_blender_cfd')}
          </div>
          <div
            className="mode-card"
            role="button"
            tabIndex={0}
            onClick={() => handleModeSelect('cfd_only')}
            onKeyDown={cardKey(() => handleModeSelect('cfd_only'))}
          >
            <ThemeIcon light="cfd_gear_white.png" dark="image-removebg-preview(12).png" alt="" className="mode-icon-small" />
            <h3>{t('hubCfdOnlyTitle')}</h3>
            <p className="mode-card-desc">{t('hubCfdOnlyDesc')}</p>
            {bedFileButtons('cfd_only')}
          </div>
          <div
            className="mode-card"
            role="button"
            tabIndex={0}
            onClick={() => goHubTab('templates')}
            onKeyDown={cardKey(() => goHubTab('templates'))}
          >
            <ThemeIcon light="textEditorLight.png" dark="textEditor.png" alt="" className="mode-icon-small" />
            <h3>{t('hubCardTemplatesTitle')}</h3>
            <p className="mode-card-desc">{t('hubCardTemplatesDesc')}</p>
          </div>
          <div
            className="mode-card"
            role="button"
            tabIndex={0}
            onClick={() => goHubTab('casos')}
            onKeyDown={cardKey(() => goHubTab('casos'))}
          >
            <ThemeIcon light="cfd_gear_white.png" dark="image-removebg-preview(12).png" alt="" className="mode-icon-small" />
            <h3>{t('hubCardCfdTitle')}</h3>
            <p className="mode-card-desc">{t('hubCardCfdDesc')}</p>
          </div>
          <div
            className="mode-card"
            role="button"
            tabIndex={0}
            onClick={openTerminalSetupDock}
            onKeyDown={cardKey(openTerminalSetupDock)}
          >
            <div className="mode-card-title-row">
              <ThemeIcon light="docsLight.png" dark="docsLight.png" alt="" className="mode-icon-small mode-icon-terminal-setup" />
              <h3>{t('terminalSetupTitle')}</h3>
            </div>
            <p className="mode-card-desc">{t('hubCardTerminalSetupDesc')}</p>
          </div>
          <div
            className="mode-card"
            role="button"
            tabIndex={0}
            onClick={openQuickTestsDock}
            onKeyDown={cardKey(openQuickTestsDock)}
          >
            <ThemeIcon light="runLight.png" dark="runDark.png" alt="" className="mode-icon-small" />
            <h3>{t('hubCardQuickTitle')}</h3>
            <p className="mode-card-desc">{t('hubCardQuickDesc')}</p>
          </div>
        </div>
      </div>
    );
  };

  // renderizar seção bed
  const renderBedSection = () => (
    <div className="form-section">
      <h2>geometria do leito</h2>
      <div className="form-grid">
        <div className="form-group">
          <label>diâmetro (m)</label>
          <input
            type="number"
            step="0.001"
            value={params.bed.diameter}
            onChange={(e) => handleInputChange('bed', 'diameter', e.target.value)}
          />
          <small>ex: 0.05m = 5cm</small>
        </div>
        
        <div className="form-group">
          <label>altura (m)</label>
          <input
            type="number"
            step="0.001"
            value={params.bed.height}
            onChange={(e) => handleInputChange('bed', 'height', e.target.value)}
          />
          <small>ex: 0.1m = 10cm</small>
        </div>
        
        <div className="form-group">
          <label>espessura da parede (m)</label>
          <input
            type="number"
            step="0.0001"
            value={params.bed.wall_thickness}
            onChange={(e) => handleInputChange('bed', 'wall_thickness', e.target.value)}
          />
          <small>ex: 0.002m = 2mm</small>
        </div>
        
        <div className="form-group">
          <label>folga superior (m)</label>
          <input
            type="number"
            step="0.001"
            value={params.bed.clearance}
            onChange={(e) => handleInputChange('bed', 'clearance', e.target.value)}
          />
          <small>espaço livre acima das partículas</small>
        </div>
        
        <div className="form-group">
          <label>material da parede</label>
          <input
            type="text"
            value={params.bed.material}
            onChange={(e) => handleInputChange('bed', 'material', e.target.value)}
          />
          <small>ex: steel, aluminum, glass</small>
        </div>
        
        <div className="form-group">
          <label>rugosidade (m) - opcional</label>
          <input
            type="number"
            step="0.0001"
            value={params.bed.roughness}
            onChange={(e) => handleInputChange('bed', 'roughness', e.target.value)}
          />
          <small>0.0 = superfície lisa</small>
        </div>

        {(() => {
          const icmMode =
            params.bed.internal_cylinder_mode || ICM_HOLLOW;
          const exportNoteKey = internalCylinderExportNoteKey(icmMode);
          const setVisibility = (patch) => {
            setParams((prev) => ({
              ...prev,
              bed: {
                ...prev.bed,
                visibility: {
                  ...(prev.bed.visibility || {}),
                  ...patch,
                },
              },
            }));
          };
          const advancedChecks = [
            ...(modeIncludesInnerCore(icmMode)
              ? [
                  {
                    key: 'omit_inner',
                    checked: !params.bed.visibility?.show_internal_cylinder,
                    onChange: (checked) =>
                      setVisibility({ show_internal_cylinder: !checked }),
                    label: t('bedExportOmitInner'),
                  },
                ]
              : []),
            {
              key: 'show_boolean_tools',
              checked: Boolean(params.bed.visibility?.show_boolean_tools),
              onChange: (checked) =>
                setVisibility({ show_boolean_tools: checked }),
              label: t('bedExportBooleanViewport'),
            },
            {
              key: 'export_boolean_tools',
              checked: Boolean(params.bed.visibility?.export_boolean_tools),
              onChange: (checked) =>
                setVisibility({ export_boolean_tools: checked }),
              label: t('bedExportBooleanFile'),
            },
          ];

          return (
            <div className="bed-shell-export-block">
              <div className="bed-icm-panel">
                <label htmlFor="bed-icm-mode">{t('bedIcmLabel')}</label>
                <select
                  id="bed-icm-mode"
                  className="bed-icm-select"
                  value={icmMode}
                  onChange={(e) => {
                    const mode = e.target.value;
                    setParams((prev) => ({
                      ...prev,
                      bed: {
                        ...prev.bed,
                        internal_cylinder_mode: mode,
                        visibility: syncVisibilityOnModeChange(
                          mode,
                          prev.bed?.visibility,
                        ),
                      },
                    }));
                  }}
                >
                  <optgroup label={t('bedIcmGroupRecommended')}>
                    <option value={ICM_HOLLOW}>{t('bedIcmHollow')}</option>
                  </optgroup>
                  <optgroup label={t('bedIcmGroupAdvanced')}>
                    <option value={ICM_VISIBLE}>{t('bedIcmVisible')}</option>
                    <option value={ICM_SOLID}>{t('bedIcmSolid')}</option>
                  </optgroup>
                </select>
                <p className="bed-icm-hint" role="note">
                  {t(internalCylinderModeHintKey(icmMode))}
                </p>
                <small>{t('bedIcmPackingNote')}</small>
              </div>

              <div className="bed-export-panel">
                <h3 className="bed-export-title">{t('bedExportTitle')}</h3>
                <p className="bed-export-lead">{t('bedExportHint')}</p>
                <div className="bed-export-checklist" role="group">
                  {EXPORT_MAIN_VISIBILITY_KEYS.map((key) => (
                    <label key={key} className="bed-export-check">
                      <input
                        type="checkbox"
                        checked={Boolean(params.bed.visibility?.[key])}
                        onChange={(e) =>
                          setVisibility({ [key]: e.target.checked })
                        }
                      />
                      <span>{t(exportMainLabelKey(key))}</span>
                    </label>
                  ))}
                </div>
                {exportNoteKey ? (
                  <p className="bed-export-derived" role="status">
                    {t(exportNoteKey)}
                  </p>
                ) : null}

                <details className="bed-export-advanced">
                  <summary>{t('bedExportAdvancedSummary')}</summary>
                  <div className="bed-export-checklist bed-export-checklist--nested">
                    {advancedChecks.map((item) => (
                      <label key={item.key} className="bed-export-check">
                        <input
                          type="checkbox"
                          checked={item.checked}
                          onChange={(e) => item.onChange(e.target.checked)}
                        />
                        <span>{item.label}</span>
                      </label>
                    ))}
                  </div>
                  <p className="bed-export-advanced-hint">
                    {t('bedExportBooleanHint')}
                  </p>
                </details>
              </div>
            </div>
          );
        })()}
      </div>
    </div>
  );

  // renderizar seção lids
  const renderLidsSection = () => (
    <div className="form-section">
      <h2>tampas</h2>
      <div className="form-grid">
        <div className="form-group">
          <label>tipo tampa superior</label>
          <select
            value={params.lids.top_type}
            onChange={(e) => handleInputChange('lids', 'top_type', e.target.value)}
          >
            <option value="flat">plana</option>
            <option value="hemispherical">hemisférica</option>
            <option value="none">sem tampa</option>
          </select>
        </div>
        
        <div className="form-group">
          <label>tipo tampa inferior</label>
          <select
            value={params.lids.bottom_type}
            onChange={(e) => handleInputChange('lids', 'bottom_type', e.target.value)}
          >
            <option value="flat">plana</option>
            <option value="hemispherical">hemisférica</option>
            <option value="none">sem tampa</option>
          </select>
        </div>
        
        <div className="form-group">
          <label>espessura tampa superior (m)</label>
          <input
            type="number"
            step="0.0001"
            value={params.lids.top_thickness}
            onChange={(e) => handleInputChange('lids', 'top_thickness', e.target.value)}
          />
          <small>ex: 0.003m = 3mm</small>
        </div>
        
        <div className="form-group">
          <label>espessura tampa inferior (m)</label>
          <input
            type="number"
            step="0.0001"
            value={params.lids.bottom_thickness}
            onChange={(e) => handleInputChange('lids', 'bottom_thickness', e.target.value)}
          />
          <small>ex: 0.003m = 3mm</small>
        </div>

        <div className="form-group">
          <label>folga do selo (m)</label>
          <input
            type="number"
            step="0.0001"
            value={params.lids.seal_clearance}
            onChange={(e) => handleInputChange('lids', 'seal_clearance', e.target.value)}
          />
          <small>espaço entre tampa e parede</small>
        </div>
      </div>
    </div>
  );

  // renderizar seção particles
  const renderParticlesSection = () => (
    <div className="form-section">
      <h2>partículas</h2>
      <div className="form-grid">
        <div className="form-group">
          <label>tipo de partícula</label>
          <select
            value={params.particles.kind}
            onChange={(e) => handleInputChange('particles', 'kind', e.target.value)}
          >
            <option value="sphere">esfera</option>
            <option value="cube">cubo</option>
            <option value="cylinder">cilindro</option>
          </select>
        </div>
        
        <div className="form-group">
          <label>diâmetro (m)</label>
          <input
            type="number"
            step="0.0001"
            value={params.particles.diameter}
            onChange={(e) => handleInputChange('particles', 'diameter', e.target.value)}
          />
          <small>ex: 0.005m = 5mm</small>
        </div>
        
        <div className="form-group">
          <label>quantidade</label>
          <input
            type="number"
            value={params.particles.count}
            onChange={(e) => handleInputChange('particles', 'count', e.target.value)}
          />
          <small>100 = rápido, 1000 = detalhado</small>
        </div>

        <div className="form-group">
          <label>porosidade alvo</label>
          <input
            type="number"
            step="0.01"
            min="0"
            max="1"
            value={params.particles.target_porosity}
            onChange={(e) => handleInputChange('particles', 'target_porosity', e.target.value)}
          />
          <small>ex: 0.4 = 40% vazio</small>
        </div>
        
        <div className="form-group">
          <label>densidade (kg/m³)</label>
          <input
            type="number"
            step="10"
            value={params.particles.density}
            onChange={(e) => handleInputChange('particles', 'density', e.target.value)}
          />
          <small>vidro = 2500, aço = 7850</small>
        </div>

        <div className="form-group">
          <label>massa (g) — opcional</label>
          <input
            type="number"
            step="0.1"
            min="0"
            value={params.particles.mass}
            onChange={(e) => handleInputChange('particles', 'mass', e.target.value)}
          />
          <small>0 = calcular automaticamente</small>
        </div>
        
        <SeedFieldRow
          id="particles-seed"
          label="seed para reproducibilidade"
          value={params.particles.seed}
          onChange={(e) => handleInputChange('particles', 'seed', e.target.value)}
          onGenerate={() => generateSeedFor('particles', 'seed')}
          hint="vazio no motor = aleatório; número fixo = mesmo empacotamento"
        />
      </div>
      
      <details className="advanced-params" open>
        <summary>propriedades adicionais das partículas</summary>
        <div className="form-grid">
          <div className="form-group">
            <label>restituição (quique)</label>
            <input
              type="number"
              step="0.1"
              min="0"
              max="1"
              value={params.particles.restitution}
              onChange={(e) => handleInputChange('particles', 'restitution', e.target.value)}
            />
            <small>0.0 = sem quique, 1.0 = quique total</small>
          </div>
          
          <div className="form-group">
            <label>atrito</label>
            <input
              type="number"
              step="0.1"
              min="0"
              max="1"
              value={params.particles.friction}
              onChange={(e) => handleInputChange('particles', 'friction', e.target.value)}
            />
            <small>0.5 = atrito moderado</small>
          </div>

          <div className="form-group">
            <label>atrito de rolamento</label>
            <input
              type="number"
              step="0.1"
              min="0"
              max="1"
              value={params.particles.rolling_friction}
              onChange={(e) => handleInputChange('particles', 'rolling_friction', e.target.value)}
            />
          </div>

          <div className="form-group">
            <label>amortecimento linear</label>
            <input
              type="number"
              step="0.1"
              min="0"
              max="1"
              value={params.particles.linear_damping}
              onChange={(e) => handleInputChange('particles', 'linear_damping', e.target.value)}
            />
          </div>

          <div className="form-group">
            <label>amortecimento angular</label>
            <input
              type="number"
              step="0.1"
              min="0"
              max="1"
              value={params.particles.angular_damping}
              onChange={(e) => handleInputChange('particles', 'angular_damping', e.target.value)}
            />
          </div>
        </div>
      </details>
    </div>
  );

  // renderizar seção packing
  const renderPackingSection = () => {
    if (params.geometry_mode === 'pseudo_2d_statistical') {
      return (
        <div className="form-section">
          <h2>empacotamento</h2>
          <p className="wizard-hint-muted">
            {pt
              ? 'no modo estatístico o empacotamento 3d é ignorado; a porosidade vem da reconstrução 2d (rsa).'
              : 'statistical mode skips 3d packing; porosity comes from 2d rsa reconstruction.'}
          </p>
        </div>
      );
    }
    return (
    <div className="form-section">
      <h2>empacotamento</h2>
      <div className="form-grid">
        <div className="form-group">
          <label>método</label>
          <select
            value={params.packing.method}
            onChange={(e) => handleInputChange('packing', 'method', e.target.value)}
          >
            <option value="rigid_body">corpo rígido (física)</option>
              <option value="spherical_packing">empacotamento esférico</option>
              <option value="hexagonal_3d">grade hexagonal 3d</option>
              <option value="dem">dem (elementos discretos)</option>
          </select>
        </div>

        {params.packing.method === 'rigid_body' && (
          <>
            <div className="form-group">
              <label>gravidade (m/s²)</label>
              <input
                type="number"
                step="0.1"
                value={params.packing.gravity}
                onChange={(e) => handleInputChange('packing', 'gravity', e.target.value)}
              />
            </div>
            <div className="form-group">
              <label>sub-passos</label>
              <input
                type="number"
                value={params.packing.substeps}
                onChange={(e) => handleInputChange('packing', 'substeps', e.target.value)}
              />
            </div>
            <div className="form-group">
              <label>iterações</label>
              <input
                type="number"
                value={params.packing.iterations}
                onChange={(e) => handleInputChange('packing', 'iterations', e.target.value)}
              />
            </div>
            <div className="form-group">
              <label>amortecimento</label>
              <input
                type="number"
                step="0.1"
                min="0"
                max="1"
                value={params.packing.damping}
                onChange={(e) => handleInputChange('packing', 'damping', e.target.value)}
              />
            </div>
            <div className="form-group">
              <label>velocidade de repouso (m/s)</label>
              <input
                type="number"
                step="0.001"
                value={params.packing.rest_velocity}
                onChange={(e) => handleInputChange('packing', 'rest_velocity', e.target.value)}
              />
            </div>
            <div className="form-group">
              <label>tempo máximo (s)</label>
              <input
                type="number"
                step="0.5"
                value={params.packing.max_time}
                onChange={(e) => handleInputChange('packing', 'max_time', e.target.value)}
              />
            </div>
            <div className="form-group">
              <label>margem de colisão (m)</label>
              <input
                type="number"
                step="0.0001"
                value={params.packing.collision_margin}
                onChange={(e) => handleInputChange('packing', 'collision_margin', e.target.value)}
              />
            </div>
          </>
        )}

        {params.packing.method === 'dem' && (
          <>
            <div className="form-group">
              <label>passo de tempo (s)</label>
              <input
                type="number"
                step="0.00001"
                value={params.packing.dem?.time_step || '0.0001'}
                onChange={(e) => handleDemChange('time_step', e.target.value)}
              />
            </div>
            <div className="form-group">
              <label>passos de simulação</label>
              <input
                type="number"
                value={params.packing.dem?.steps || '30000'}
                onChange={(e) => handleDemChange('steps', e.target.value)}
              />
            </div>
            <div className="form-group">
              <label>gravidade (m/s²)</label>
              <input
                type="number"
                step="0.1"
                value={params.packing.dem?.gravity || '9.81'}
                onChange={(e) => handleDemChange('gravity', e.target.value)}
              />
            </div>
            <div className="form-group">
              <label>rigidez normal</label>
              <input
                type="number"
                value={params.packing.dem?.stiffness || '5000'}
                onChange={(e) => handleDemChange('stiffness', e.target.value)}
              />
            </div>
            <div className="form-group">
              <label>amortecimento</label>
              <input
                type="number"
                step="0.01"
                value={params.packing.dem?.damping || '0.2'}
                onChange={(e) => handleDemChange('damping', e.target.value)}
              />
            </div>
            <div className="form-group">
              <label>atrito</label>
              <input
                type="number"
                step="0.01"
                value={params.packing.dem?.friction || '0.2'}
                onChange={(e) => handleDemChange('friction', e.target.value)}
              />
            </div>
            <div className="form-group">
              <label>limiar de repouso (m/s)</label>
              <input
                type="number"
                step="0.0001"
                value={params.packing.dem?.settle_threshold || '0.001'}
                onChange={(e) => handleDemChange('settle_threshold', e.target.value)}
              />
            </div>
            <SeedFieldRow
              id="packing-dem-seed"
              label="seed dem"
              value={params.packing.dem?.seed || '42'}
              onChange={(e) => handleDemChange('seed', e.target.value)}
              onGenerate={() => handleDemChange('seed', randomSeedValue())}
            />
            <p className="form-hint">
              dem requer motor python_engine. no blender use spherical_packing ou rigid_body.
            </p>
          </>
        )}

        {(params.packing.method === 'spherical_packing' || params.packing.method === 'hexagonal_3d') && (
          <>
            <div className="form-group">
              <label>gap entre superfícies (m)</label>
              <input
                type="number"
                step="0.0001"
                value={params.packing.gap}
                onChange={(e) => handleInputChange('packing', 'gap', e.target.value)}
              />
            </div>
            {params.packing.method === 'spherical_packing' && (
              <>
                <SeedFieldRow
                  id="packing-random-seed"
                  label="random seed"
                  value={params.packing.random_seed}
                  onChange={(e) =>
                    handleInputChange('packing', 'random_seed', e.target.value)
                  }
                  onGenerate={() => generateSeedFor('packing', 'random_seed')}
                  hint="usado pelo empacotamento esférico e hexagonal"
                />
                <div className="form-group">
                  <label>máx. tentativas de colocação</label>
                  <input
                    type="number"
                    value={params.packing.max_placement_attempts}
                    onChange={(e) => handleInputChange('packing', 'max_placement_attempts', e.target.value)}
                  />
                </div>
              </>
            )}
            {params.packing.method === 'hexagonal_3d' && (
              <SeedFieldRow
                id="packing-hex-seed"
                label="random seed"
                value={params.packing.random_seed}
                onChange={(e) =>
                  handleInputChange('packing', 'random_seed', e.target.value)
                }
                onGenerate={() => generateSeedFor('packing', 'random_seed')}
                hint="baralha candidatos da grade antes de escolher as posições"
              />
            )}
            {params.packing.method === 'hexagonal_3d' && (
              <div className="form-group">
                <label>passo horizontal step_x (m)</label>
                <input
                  type="text"
                  value={params.packing.step_x}
                  onChange={(e) => handleInputChange('packing', 'step_x', e.target.value)}
                  placeholder="vazio = automático"
                />
              </div>
            )}
            <div className="form-group checkbox-group">
              <label>
                <input
                  type="checkbox"
                  checked={Boolean(params.packing.strict_validation)}
                  onChange={(e) => handleInputChange('packing', 'strict_validation', e.target.checked)}
                />
                validação estrita (strict_validation)
              </label>
            </div>
          </>
        )}
      </div>
    </div>
    );
  };

  const renderPipelineSection = () => (
    <div className="form-section">
      <h2>{t('pipelineStep')}</h2>
      <div className="form-grid">
        <div className="form-group">
          <label>{pt ? 'modo de geometria' : 'geometry mode'}</label>
          <select
            value={params.geometry_mode}
            onChange={(e) => handleMetaChange('geometry_mode', e.target.value)}
          >
            <option value="full_3d">{pt ? 'volume completo (full_3d)' : 'full volume (full_3d)'}</option>
            <option value="pseudo_2d_thin_slice">
              {pt ? 'fatia fina pseudo 2d' : 'thin pseudo-2d slice'}
            </option>
            <option value="pseudo_2d_statistical">
              {pt ? 'reconstrução 2d estatística' : 'statistical pseudo-2d'}
            </option>
          </select>
        </div>

        <div className="form-group">
          <label>{pt ? 'motor de geração' : 'generation backend'}</label>
          <select
            value={params.generation_backend}
            onChange={(e) => handleMetaChange('generation_backend', e.target.value)}
            disabled={params.geometry_mode === 'pseudo_2d_statistical'}
          >
            <option value="blender">{pt ? 'blender — malha via blender' : 'blender'}</option>
            <option value="python_engine">
              {pt ? 'python engine — malha via motor feito em python' : 'python engine'}
            </option>
          </select>
          {params.geometry_mode === 'pseudo_2d_statistical' && (
            <small className="field-hint">
              {pt ? 'modo estatístico exige motor python.' : 'statistical mode requires python engine.'}
            </small>
          )}
        </div>

        {params.geometry_mode === 'pseudo_2d_thin_slice' && params.slice && (
          <>
            <div className="form-group">
              <label>{pt ? 'eixo do corte' : 'slice axis'}</label>
              <select
                value={params.slice.slice_axis}
                onChange={(e) => handleSliceChange('slice_axis', e.target.value)}
              >
                <option value="x">x</option>
                <option value="y">y</option>
                <option value="z">z</option>
              </select>
            </div>
            <div className="form-group">
              <label>{pt ? 'espessura da fatia (m)' : 'slice thickness (m)'}</label>
              <input
                type="number"
                step="0.0001"
                min="0.0001"
                value={params.slice.slice_thickness ?? '0.002'}
                onChange={(e) => handleSliceChange('slice_thickness', e.target.value)}
              />
            </div>
            <div className="form-group">
              <label>{pt ? 'raio mínimo na secção (m)' : 'min slice radius (m)'}</label>
              <input
                type="number"
                step="0.000001"
                min="0"
                value={params.slice.min_slice_particle_radius ?? '0.00001'}
                onChange={(e) =>
                  handleSliceChange('min_slice_particle_radius', e.target.value)
                }
              />
            </div>
            <p className="field-hint">
              {pt
                ? 'casco e partículas usam a mesma espessura; discos finos no eixo do corte. perto da parede o centro pode ser encostado a r_int.'
                : 'shell and particles share slice thickness; thin discs along the cut axis. near the wall centers may snap to r_int.'}
            </p>
            <div className="form-group">
              <label>{pt ? 'posição central (m)' : 'slice position (m)'}</label>
              <input
                type="number"
                step="0.001"
                value={params.slice.slice_position}
                onChange={(e) => handleSliceChange('slice_position', e.target.value)}
              />
            </div>
            <div className="form-group checkbox-group">
              <label>
                <input
                  type="checkbox"
                  checked={Boolean(params.slice.keep_only_intersecting_particles)}
                  onChange={(e) =>
                    handleSliceChange('keep_only_intersecting_particles', e.target.checked)
                  }
                />
                {pt ? 'manter só partículas na fatia' : 'keep only particles in slice'}
              </label>
            </div>
            <div className="form-group checkbox-group">
              <label>
                <input
                  type="checkbox"
                  checked={Boolean(params.slice.preserve_original_packing)}
                  onChange={(e) =>
                    handleSliceChange('preserve_original_packing', e.target.checked)
                  }
                />
                {pt ? 'preservar coordenadas originais' : 'preserve original coordinates'}
              </label>
            </div>
            <div className="form-group checkbox-group">
              <label>
                <input
                  type="checkbox"
                  checked={Boolean(params.slice.debug_export_gizmos)}
                  onChange={(e) => handleSliceChange('debug_export_gizmos', e.target.checked)}
                />
                {pt ? 'exportar gizmos de debug' : 'export debug gizmos'}
              </label>
            </div>
          </>
        )}

        {params.geometry_mode === 'pseudo_2d_statistical' && params.statistical_2d && (
          <>
            <div className="form-group">
              <label>{pt ? 'largura do domínio 2d (m)' : '2d domain width (m)'}</label>
              <input
                type="number"
                step="0.001"
                value={params.statistical_2d.domain_width}
                onChange={(e) => handleStatistical2DChange('domain_width', e.target.value)}
              />
            </div>
            <div className="form-group">
              <label>{pt ? 'altura do domínio 2d (m)' : '2d domain height (m)'}</label>
              <input
                type="number"
                step="0.001"
                value={params.statistical_2d.domain_height}
                onChange={(e) => handleStatistical2DChange('domain_height', e.target.value)}
              />
            </div>
            <div className="form-group">
              <label>{pt ? 'porosidade alvo' : 'target porosity'}</label>
              <input
                type="number"
                step="0.01"
                min="0"
                max="1"
                value={params.statistical_2d.target_porosity}
                onChange={(e) => handleStatistical2DChange('target_porosity', e.target.value)}
              />
            </div>
            <div className="form-group">
              <label>{pt ? 'tolerância' : 'tolerance'}</label>
              <input
                type="number"
                step="0.01"
                value={params.statistical_2d.tolerance}
                onChange={(e) => handleStatistical2DChange('tolerance', e.target.value)}
              />
            </div>
            <div className="form-group">
              <label>{pt ? 'máx. tentativas' : 'max attempts'}</label>
              <input
                type="number"
                value={params.statistical_2d.max_attempts}
                onChange={(e) => handleStatistical2DChange('max_attempts', e.target.value)}
              />
            </div>
            <div className="form-group">
              <label>{pt ? 'espessura da geometria fina (m)' : 'thin 3d thickness (m)'}</label>
              <input
                type="number"
                step="0.0001"
                value={params.statistical_2d.slice_thickness}
                onChange={(e) => handleStatistical2DChange('slice_thickness', e.target.value)}
              />
            </div>
          </>
        )}
      </div>
    </div>
  );

  // renderizar seção export
  const renderExportSection = () => {
    const formatosDisponiveis = [
      { value: 'stl_binary', label: 'stl binário (impressão 3d / openfoam)' },
      { value: 'obj', label: 'obj (universal)' },
      { value: 'blend', label: 'blend (nativo blender)' },
      { value: 'gltf', label: 'gltf (web — vários ficheiros)' },
      { value: 'glb', label: 'glb (web — ficheiro único)' },
      { value: 'fbx', label: 'fbx (unity, unreal)' },
    ];

    const toggleFormato = (formato) => {
      const formatos = params.export.formats || [];
      const novosFormatos = formatos.includes(formato)
        ? formatos.filter(f => f !== formato)
        : [...formatos, formato];
      
      handleInputChange('export', 'formats', novosFormatos);
    };

    return (
      <div className="form-section">
        <h2>exportação</h2>
        
        <div className="form-group">
          <label>formatos de exportação</label>
          <div className="checkbox-group-formats">
            {formatosDisponiveis.map(({ value, label }) => (
              <label key={value} className="checkbox-format">
                <input
                  type="checkbox"
                  checked={params.export.formats?.includes(value) || false}
                  onChange={() => toggleFormato(value)}
                />
                {label}
              </label>
            ))}
          </div>
          <small>
            selecionados: {params.export.formats?.length || 0} formato(s) - 
            recomendado: blend + glb + obj
          </small>
        </div>
        
        <div className="form-grid">
          <div className="form-group">
            <label>modo da parede</label>
            <select
              value={params.export.wall_mode}
              onChange={(e) => handleInputChange('export', 'wall_mode', e.target.value)}
            >
              <option value="surface">superfície (recomendado)</option>
              <option value="solid">sólido</option>
            </select>
            <small>surface = melhor para cfd</small>
          </div>
          
          <div className="form-group">
            <label>modo do fluido</label>
            <select
              value={params.export.fluid_mode}
              onChange={(e) => handleInputChange('export', 'fluid_mode', e.target.value)}
            >
              <option value="none">nenhum (recomendado)</option>
              <option value="cavity">cavidade</option>
            </select>
          </div>

          <div className="form-group">
            <label>unidades</label>
            <select
              value={params.export.units}
              onChange={(e) => handleInputChange('export', 'units', e.target.value)}
            >
              <option value="m">metros (m)</option>
              <option value="mm">milímetros (mm)</option>
              <option value="cm">centímetros (cm)</option>
            </select>
          </div>

          <div className="form-group">
            <label>escala</label>
            <input
              type="text"
              value={params.export.scale}
              onChange={(e) => handleInputChange('export', 'scale', e.target.value)}
            />
            <small>fator aplicado na exportação (ex.: 1.0)</small>
          </div>

          <div className="form-group">
            <label>distância de merge (m)</label>
            <input
              type="number"
              step="0.0001"
              value={params.export.merge_distance}
              onChange={(e) => handleInputChange('export', 'merge_distance', e.target.value)}
            />
          </div>
          
          <div className="form-group checkbox-group">
            <label>
              <input
                type="checkbox"
                checked={params.export.manifold_check}
                onChange={(e) => handleInputChange('export', 'manifold_check', e.target.checked)}
              />
              verificar manifold (recomendado)
            </label>
            <small>garante integridade da malha</small>
          </div>
        </div>
      </div>
    );
  };

  const renderCfdToggleSection = () => (
    <div className="form-section">
      <h2>{t('cfdParams')}</h2>
      <div className="checkbox-group">
        <label>
          <input
            type="checkbox"
            checked={includeCFD}
            onChange={(e) => handleIncludeCfdChange(e.target.checked)}
          />
          {t('cfdIncludeLabel')}
        </label>
      </div>
      <p className="wizard-hint-muted">
        {pt
          ? 'se marcar, na próxima página poderá configurar regime, fluido e convergência.'
          : 'if checked, the next page lets you configure regime, fluid and convergence.'}
      </p>
    </div>
  );

  const renderCfdSection = () => {
    const cfd = params.cfd || DEFAULT_CFD_PARAMS;
    return (
      <div className="form-section">
        <h2>{t('cfdParamsConfigure')}</h2>
        <div className="form-grid">
          <div className="form-group">
            <label>regime</label>
            <select
              value={cfd.regime}
              onChange={(e) => handleInputChange('cfd', 'regime', e.target.value)}
            >
              <option value="laminar">laminar</option>
              <option value="turbulent_rans">turbulento (rans)</option>
            </select>
          </div>

          <div className="form-group">
            <label>velocidade de entrada (m/s)</label>
            <input
              type="number"
              step="0.01"
              value={cfd.inlet_velocity}
              onChange={(e) => handleInputChange('cfd', 'inlet_velocity', e.target.value)}
            />
            <small>ex: 0.1 m/s = escoamento lento</small>
          </div>

          <div className="form-group">
            <label>densidade do fluido (kg/m³)</label>
            <input
              type="number"
              step="0.001"
              value={cfd.fluid_density}
              onChange={(e) => handleInputChange('cfd', 'fluid_density', e.target.value)}
            />
            <small>ar ≈ 1.225, água ≈ 1000</small>
          </div>

          <div className="form-group">
            <label>viscosidade do fluido (pa·s)</label>
            <input
              type="text"
              value={cfd.fluid_viscosity}
              onChange={(e) => handleInputChange('cfd', 'fluid_viscosity', e.target.value)}
            />
            <small>ar ≈ 1.8e-5, água ≈ 1e-3</small>
          </div>

          <div className="form-group">
            <label>iterações máximas</label>
            <input
              type="number"
              value={cfd.max_iterations}
              onChange={(e) => handleInputChange('cfd', 'max_iterations', e.target.value)}
            />
          </div>

          <div className="form-group">
            <label>critério de convergência</label>
            <input
              type="text"
              value={cfd.convergence_criteria}
              onChange={(e) => handleInputChange('cfd', 'convergence_criteria', e.target.value)}
            />
            <small>ex: 1e-6</small>
          </div>

          <div className="form-group checkbox-group">
            <label>
              <input
                type="checkbox"
                checked={Boolean(cfd.write_fields)}
                onChange={(e) => handleInputChange('cfd', 'write_fields', e.target.checked)}
              />
              escrever campos (velocidade/pressão)
            </label>
          </div>
        </div>
      </div>
    );
  };

  // renderizar confirmação
  const renderConfirmation = () => (
    <div className="form-section confirmation">
      <h2>confirmação dos parâmetros</h2>
      {(params.bed?.internal_cylinder_mode || ICM_HOLLOW) === ICM_SOLID && (
        <p className="bed-wizard-slow-hint" role="note">
          {t('bedSolidSlowHint')}
        </p>
      )}
      <BedPreview3D params={params} />
      
      <div className="summary-grid">
        <div className="summary-card">
          <h3>geometria</h3>
          <p>leito: {params.bed.diameter}m × {params.bed.height}m</p>
          <p>parede: {params.bed.material}</p>
        </div>
        
        <div className="summary-card">
          <h3>partículas</h3>
          <p>{params.particles.count} {params.particles.kind}</p>
          <p>diâmetro: {params.particles.diameter}m</p>
          <p>densidade: {params.particles.density} kg/m³</p>
          <p>porosidade: {params.particles.target_porosity}</p>
          <p>restituição: {params.particles.restitution}, atrito: {params.particles.friction}</p>
          <p>seed: {params.particles.seed}</p>
        </div>

        <div className="summary-card">
          <h3>{pt ? 'geometria e motor' : 'geometry and engine'}</h3>
          <p>{pt ? 'modo' : 'mode'}: {params.geometry_mode}</p>
          <p>{pt ? 'motor' : 'backend'}: {params.generation_backend}</p>
          {params.geometry_mode === 'pseudo_2d_thin_slice' && params.slice && (
            <p>
              {pt ? 'fatia' : 'slice'} {params.slice.slice_axis} @ {params.slice.slice_position}m
            </p>
          )}
          {params.geometry_mode === 'pseudo_2d_statistical' && params.statistical_2d && (
            <p>
              {pt ? 'domínio 2d' : '2d domain'}: {params.statistical_2d.domain_width}×
              {params.statistical_2d.domain_height}m, ε alvo: {params.statistical_2d.target_porosity}
            </p>
          )}
        </div>
        
        <div className="summary-card">
          <h3>empacotamento</h3>
          <p>método: {params.packing.method}</p>
          {params.packing.method === 'rigid_body' && (
            <p>gravidade: {params.packing.gravity} m/s²</p>
          )}
          {(params.packing.method === 'spherical_packing' || params.packing.method === 'hexagonal_3d') && (
            <>
              <p>gap: {params.packing.gap} m</p>
              {params.packing.strict_validation && <p>validação estrita: sim</p>}
            </>
          )}
        </div>
        
        <div className="summary-card">
          <h3>exportação</h3>
          <p>formatos: {params.export.formats.join(', ')}</p>
          <p>unidades: {params.export.units}, escala: {params.export.scale}</p>
          <p>modo parede: {params.export.wall_mode}</p>
          <p>merge: {params.export.merge_distance} m</p>
        </div>

        {showCfdSteps && includeCFD && params.cfd && (
          <div className="summary-card">
            <h3>cfd</h3>
            <p>regime: {params.cfd.regime}</p>
            <p>entrada: {params.cfd.inlet_velocity} m/s</p>
            <p>ρ: {params.cfd.fluid_density} kg/m³, μ: {params.cfd.fluid_viscosity} pa·s</p>
            <p>iterações: {params.cfd.max_iterations}, convergência: {params.cfd.convergence_criteria}</p>
          </div>
        )}
      </div>
      
      <div className="form-group">
        <label>nome do arquivo</label>
        <input
          type="text"
          value={fileName}
          onChange={(e) => setFileName(e.target.value)}
          placeholder="meu_leito.bed"
        />
      </div>
    </div>
  );



  return (
    <div className="bed-wizard">
      {wizardConnectionError && (
        <BackendConnectionError message={wizardConnectionError} />
      )}
      {/* modais */}
      <HelpModal 
        show={showHelp} 
        onClose={() => setShowHelp(false)} 
        section={helpSection}
        paramHelp={paramHelp}
      />
      
      <DocsModal 
        show={showDocs} 
        onClose={() => setShowDocs(false)} 
      />
      

      {/* modal de opções de arquivo .bed */}
      {criarDock && (
        <div
          className="criar-dock-backdrop"
          role="presentation"
          onClick={closeCriarDock}
        >
          <div
            className="criar-dock-shell"
            role="dialog"
            aria-labelledby="criar-dock-title"
            onClick={(e) => e.stopPropagation()}
          >
            {criarDock === 'quick-tests' &&
              renderCliPanel({
                title: t('quickTestsDockTitle'),
                intro: t('quickTestsDockIntro'),
                presets: [buildCliPreset('quick-tests')],
                compact: true,
                onClose: closeCriarDock,
              })}
            {criarDock === 'terminal-setup' &&
              renderCliPanel({
                title: t('terminalSetupTitle'),
                intro: t('terminalSetupIntro'),
                presets: [
                  buildCliPreset('setup-install'),
                  { ...buildCliPreset('wizard-run'), showLaunch: true },
                ],
                compact: true,
                onClose: closeCriarDock,
                titleIcon: { light: 'docsLight.png', dark: 'docsLight.png' },
                templateCopyButtons: true,
              })}
          </div>
        </div>
      )}

      {bedLoadOpen && (
        <BedLoadModal
          hubMode={bedLoadOpen.hubMode}
          initialContent={bedLoadOpen.initialContent || ''}
          initialFilename={bedLoadOpen.initialFilename || ''}
          onClose={() => setBedLoadOpen(null)}
          onSuccess={() => {
            setBedLoadOpen(null);
            setStep(0);
            setMode(null);
          }}
          onNavigateTab={onNavigateTab}
          onOpenMeshViewer={onOpenMeshViewer}
        />
      )}
    
      {/* header com progresso */}
      {step > 0 && (
        <div className="wizard-header">
          <div className="progress-bar">
            <div 
              className="progress-fill" 
              style={{ width: `${(step / (steps.length - 1)) * 100}%` }}
            ></div>
          </div>
          <div className="step-indicator">
            passo {step} de {steps.length - 1}: {steps[step].title}
          </div>
        </div>
      )}

      {/* conteúdo do wizard */}
      <div className={step === 0 ? 'wizard-content wizard-content--step0-hub' : 'wizard-content'}>
        {step === 0 && (
          <>
            <header className="criar-hub-page-heading">
              <ThemeIcon
                light="create_bed_white.png"
                dark="create_bed_white.png"
                alt=""
                className="criar-hub-title-icon"
              />
              <h1 className="criar-hub-page-title">{t('selectMode')}</h1>
            </header>
            <div className="criar-hub-cards-panel">{renderModeSelection()}</div>
          </>
        )}
        {currentSection === 'bed' && renderBedSection()}
        {currentSection === 'lids' && renderLidsSection()}
        {currentSection === 'particles' && renderParticlesSection()}
        {currentSection === 'packing' && renderPackingSection()}
        {currentSection === 'pipeline' && renderPipelineSection()}
        {currentSection === 'export' && renderExportSection()}
        {currentSection === 'cfd-toggle' && renderCfdToggleSection()}
        {currentSection === 'cfd-form' && renderCfdSection()}
        {currentSection === 'confirm' && renderConfirmation()}
      </div>

      {/* botões de navegação */}
      {step > 0 && (
        <div className="wizard-footer wizard-footer-nav caso-acoes">
          <button type="button" className="btn-mode-option wizard-nav-btn" onClick={handlePrev}>
            <ThemeIcon light="cancelLight.png" dark="cancelDark.png" alt="" className="btn-icon" />
            {pt ? 'voltar' : 'back'}
          </button>
          {step < steps.length - 1 ? (
            <button type="button" className="btn-mode-option wizard-nav-btn wizard-nav-btn--next" onClick={handleNext}>
              <IconArrowRight className="btn-icon wizard-nav-arrow" />
              {pt ? 'próximo' : 'next'}
            </button>
          ) : (
            <button
              type="button"
              className="btn-mode-option wizard-nav-btn"
              disabled={submitBusy}
              onClick={() => void handleSubmit()}
            >
              <ThemeIcon light="textEditorLight.png" dark="textEditor.png" alt="" className="btn-icon" />
              {submitBusy
                ? t('bedWizardSubmitBusy')
                : pt
                  ? 'gerar .bed'
                  : 'generate .bed'}
            </button>
          )}
        </div>
      )}
    </div>
  );
};

export default BedWizard;

