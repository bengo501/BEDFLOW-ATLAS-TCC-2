import { useCallback, useEffect, useState } from 'react';
import { useLanguage } from '../context/LanguageContext';
import { useTheme } from '../context/ThemeContext';
import { useAppUi } from '../context/AppUiContext';
import { getSettings, patchSettings, postAdminDevShutdown, getApiBase } from '../services/api';
import BackendConnectionError from './BackendConnectionError';
import ThemeIcon from './ThemeIcon';
import './SettingsPage.css';

function isConnectionError(err) {
  if (!err) return false;
  const noResponse = !err.response && !!err.request;
  const network =
    err.code === 'ERR_NETWORK' ||
    err.code === 'ECONNABORTED' ||
    (typeof err.message === 'string' && err.message.toLowerCase().includes('network'));
  return noResponse || network;
}

function apiBaseUrl() {
  return String(getApiBase()).replace(/\/$/, '');
}

/**
 * @param {{ navigateTab: (tab: string) => void, onLogout?: () => void }} props
 */
export default function SettingsPage({ navigateTab, onLogout }) {
  const { language, t, setLanguage } = useLanguage();
  const { setThemeMode } = useTheme();
  const { applySettingsFromApi, setSimpleMode, setDevMode } = useAppUi();
  const pt = language === 'pt';

  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [connectionError, setConnectionError] = useState(null);
  const [opError, setOpError] = useState(null);
  const [devMsg, setDevMsg] = useState('');

  const [themeMode, setThemeModeLocal] = useState('system');
  const [lang, setLangLocal] = useState('pt');
  const [jobsPollSec, setJobsPollSec] = useState(5);
  const [advancedHints, setAdvancedHints] = useState(false);
  const [simpleModeDraft, setSimpleModeDraft] = useState(false);
  const [devModeDraft, setDevModeDraft] = useState(false);

  const [dbNotes, setDbNotes] = useState('');
  const [clientTimeoutSec, setClientTimeoutSec] = useState(30);

  const [ofSolver, setOfSolver] = useState('simpleFoam');
  const [ofMaxIter, setOfMaxIter] = useState(1000);
  const [ofTurb, setOfTurb] = useState('kEpsilon');
  const [ofConv, setOfConv] = useState(1e-6);

  const [modelingProfile, setModelingProfile] = useState('blender');
  const [modelingNotes, setModelingNotes] = useState('');
  const [cfdOtherNotes, setCfdOtherNotes] = useState('');

  const [updatedAt, setUpdatedAt] = useState('');

  const load = useCallback(async () => {
    setLoading(true);
    setConnectionError(null);
    setOpError(null);
    try {
      const s = await getSettings();
      const tm = s.theme_mode === 'dark' || s.theme_mode === 'light' || s.theme_mode === 'system'
        ? s.theme_mode
        : 'system';
      setThemeModeLocal(tm);
      const lg = s.language === 'en' ? 'en' : 'pt';
      setLangLocal(lg);
      const j = Number(s.jobs_poll_interval_sec);
      setJobsPollSec(Number.isFinite(j) && j >= 3 && j <= 120 ? j : 5);
      setAdvancedHints(!!s.show_advanced_hints);
      setSimpleModeDraft(!!s.simple_mode);
      setDevModeDraft(!!s.dev_mode);
      setDbNotes(s.database_ui?.notes ?? '');
      const ct = Number(s.database_ui?.client_timeout_sec);
      setClientTimeoutSec(Number.isFinite(ct) && ct >= 5 && ct <= 600 ? ct : 30);
      setOfSolver(s.openfoam_defaults?.solver ?? 'simpleFoam');
      const mi = Number(s.openfoam_defaults?.max_iterations);
      setOfMaxIter(Number.isFinite(mi) && mi >= 1 ? mi : 1000);
      setOfTurb(s.openfoam_defaults?.turbulence_model ?? 'kEpsilon');
      const cv = Number(s.openfoam_defaults?.convergence);
      setOfConv(Number.isFinite(cv) && cv > 0 ? cv : 1e-6);
      setModelingProfile(s.modeling?.profile === 'python' ? 'python' : 'blender');
      setModelingNotes(s.modeling?.notes ?? '');
      setCfdOtherNotes(s.cfd_other?.notes ?? '');
      setUpdatedAt(s.updated_at || '');
      applySettingsFromApi(s);
      localStorage.setItem(
        'jobsPollIntervalSec',
        String(Number.isFinite(j) && j >= 3 && j <= 120 ? j : 5)
      );
    } catch (err) {
      console.error(err);
      if (isConnectionError(err)) {
        setConnectionError(t('backendConnectionError'));
      } else {
        setOpError(
          err.response?.data?.detail ||
            err.message ||
            (pt ? 'não foi possível carregar as configurações' : 'could not load settings')
        );
      }
    } finally {
      setLoading(false);
    }
  }, [applySettingsFromApi, pt, t]);

  useEffect(() => {
    load();
  }, [load]);

  const onThemeChange = (value) => {
    setThemeModeLocal(value);
  };

  const onLangChange = (value) => {
    setLangLocal(value);
    setLanguage(value);
  };

  const handleSave = async () => {
    setSaving(true);
    setOpError(null);
    setConnectionError(null);
    try {
      const s = await patchSettings({
        theme_mode: themeMode,
        language: lang,
        jobs_poll_interval_sec: jobsPollSec,
        show_advanced_hints: advancedHints,
        simple_mode: simpleModeDraft,
        dev_mode: devModeDraft,
        database_ui: {
          notes: dbNotes,
          client_timeout_sec: clientTimeoutSec,
        },
        openfoam_defaults: {
          solver: ofSolver,
          max_iterations: ofMaxIter,
          turbulence_model: ofTurb,
          convergence: ofConv,
        },
        modeling: {
          profile: modelingProfile,
          notes: modelingNotes,
        },
        cfd_other: {
          notes: cfdOtherNotes,
        },
      });
      setUpdatedAt(s.updated_at || '');
      localStorage.setItem('jobsPollIntervalSec', String(jobsPollSec));
      applySettingsFromApi(s);
      setThemeMode(themeMode);
      setLanguage(lang);
    } catch (err) {
      console.error(err);
      if (isConnectionError(err)) {
        setConnectionError(t('backendConnectionError'));
      } else {
        setOpError(
          err.response?.data?.detail ||
            err.message ||
            (pt ? 'falha ao guardar' : 'save failed')
        );
      }
    } finally {
      setSaving(false);
    }
  };

  const openSwagger = () => {
    window.open(`${apiBaseUrl()}/docs`, '_blank', 'noopener,noreferrer');
  };

  const tryQuitFrontend = () => {
    window.close();
    setDevMsg(
      pt
        ? 'se o separador não fechar, foi aberto manualmente: feche-o à mão ou use atalho do navegador.'
        : 'if the tab did not close, it was opened manually: close it yourself or use a browser shortcut.'
    );
  };

  const shutdownBackend = async () => {
    setDevMsg('');
    try {
      await postAdminDevShutdown();
      setDevMsg(
        pt
          ? 'pedido de encerramento enviado. o backend deve parar em breve; reinicie uvicorn ou o container manualmente.'
          : 'shutdown request sent. the backend should stop shortly; restart uvicorn or your container manually.'
      );
    } catch (err) {
      const detail = err.response?.data?.detail;
      setDevMsg(
        typeof detail === 'string'
          ? detail
          : pt
            ? 'falha ao encerrar (confirme ALLOW_DEV_SHUTDOWN=1 no servidor).'
            : 'shutdown failed (set ALLOW_DEV_SHUTDOWN=1 on the server).'
      );
    }
  };

  const handleLogout = () => {
    if (typeof onLogout === 'function') {
      onLogout();
    }
  };

  return (
    <div className="tab-content">
      <div className="settings-page">
        {connectionError && <BackendConnectionError message={connectionError} />}

        {opError && (
          <div className="settings-op-error" role="alert">
            {opError}
          </div>
        )}

        {devMsg && (
          <div className="settings-dev-msg" role="status">
            {devMsg}
          </div>
        )}

        <header className="settings-page-header">
          <div className="settings-page-title">
            <ThemeIcon light="settingsLight.png" dark="settingsLight.png" alt="" className="settings-page-title-icon" />
            <h1 className="settings-page-heading">{t('systemSettings')}</h1>
          </div>
        </header>

        <div className="settings-page-layout">
          <div className="settings-main">
            {updatedAt && (
              <p className="settings-meta">
                {pt ? 'Última atualização na base:' : 'Last saved:'}{' '}
                {new Date(updatedAt).toLocaleString(pt ? 'pt-BR' : 'en-GB')}
              </p>
            )}

            {loading ? (
              <p className="settings-status">{pt ? 'A carregar…' : 'Loading…'}</p>
            ) : (
              <>
                <div className="settings-grid">
                  <section className="setting-card">
                    <h3>{t('theme')}</h3>
                    <p className="setting-card-desc">{t('themeDesc')}</p>
                    <label className="settings-control">
                      <span>{pt ? 'Modo' : 'Mode'}</span>
                      <select
                        value={themeMode}
                        onChange={(e) => onThemeChange(e.target.value)}
                        aria-label={t('theme')}
                      >
                        <option value="light">{pt ? 'Claro' : 'Light'}</option>
                        <option value="dark">{pt ? 'Escuro' : 'Dark'}</option>
                        <option value="system">{pt ? 'Sistema' : 'System'}</option>
                      </select>
                    </label>
                  </section>

                  <section className="setting-card">
                    <h3>{t('language')}</h3>
                    <p className="setting-card-desc">{t('languageDesc')}</p>
                    <label className="settings-control">
                      <span>{pt ? 'Idioma da interface' : 'Interface language'}</span>
                      <select
                        value={lang}
                        onChange={(e) => onLangChange(e.target.value)}
                        aria-label={t('language')}
                      >
                        <option value="pt">Português (Brasil)</option>
                        <option value="en">English</option>
                      </select>
                    </label>
                  </section>

                  <section className="setting-card setting-card-wide">
                    <h3>{pt ? 'Modo simples e modo dev' : 'Simple mode and dev mode'}</h3>
                    <p className="setting-card-desc">
                      {pt
                        ? 'Modo simples reduz o menu lateral às áreas principais do fluxo cfd. Modo dev mostra, em cada página, referências de api e persistência.'
                        : 'Simple mode trims the sidebar to core cfd areas. Dev mode shows api and persistence hints on every page.'}
                    </p>
                    <label className="settings-check">
                      <input
                        type="checkbox"
                        checked={simpleModeDraft}
                        onChange={(e) => {
                          const v = e.target.checked;
                          setSimpleModeDraft(v);
                          setSimpleMode(v);
                        }}
                      />
                      <span>{pt ? 'Modo simples (menu reduzido)' : 'Simple mode (reduced menu)'}</span>
                    </label>
                    <label className="settings-check">
                      <input
                        type="checkbox"
                        checked={devModeDraft}
                        onChange={(e) => {
                          const v = e.target.checked;
                          setDevModeDraft(v);
                          setDevMode(v);
                        }}
                      />
                      <span>{pt ? 'Modo dev (painel por página)' : 'Dev mode (per-page panel)'}</span>
                    </label>
                  </section>

                  <section className="setting-card setting-card-wide">
                    <h3>{pt ? 'Banco de dados (interface)' : 'Database (ui)'}</h3>
                    <p className="setting-card-desc">
                      {pt
                        ? 'Notas e tempo limite do cliente http (axios) para pedidos ao backend. Não altera a url da base no servidor.'
                        : 'Notes and axios client timeout for backend requests. Does not change the server database url.'}
                    </p>
                    <label className="settings-control settings-control-stack">
                      <span>{pt ? 'Notas / checklist' : 'Notes / checklist'}</span>
                      <textarea
                        className="settings-textarea"
                        rows={3}
                        value={dbNotes}
                        onChange={(e) => setDbNotes(e.target.value)}
                        placeholder={pt ? 'ex.: usar postgresql em produção; backup diário…' : 'e.g. use postgresql in prod; daily backup…'}
                      />
                    </label>
                    <label className="settings-control">
                      <span>{pt ? 'Timeout cliente (s)' : 'Client timeout (s)'}</span>
                      <input
                        type="number"
                        min={5}
                        max={600}
                        value={clientTimeoutSec}
                        onChange={(e) => setClientTimeoutSec(Number(e.target.value))}
                      />
                    </label>
                    <button
                      type="button"
                      className="settings-link-btn"
                      onClick={() => navigateTab('database')}
                    >
                      {pt ? 'Abrir painel banco de dados' : 'Open database panel'}
                    </button>
                  </section>

                  <section className="setting-card setting-card-wide">
                    <h3>{pt ? 'Parâmetros padrão openfoam' : 'Default openfoam parameters'}</h3>
                    <p className="setting-card-desc">
                      {pt
                        ? 'Referência para formulários e futuros templates de caso; o motor openfoam continua a ser configurado nos ficheiros do caso.'
                        : 'Reference for forms and future case templates; the openfoam engine is still driven by case files.'}
                    </p>
                    <div className="settings-inline-grid">
                      <label className="settings-control">
                        <span>Solver</span>
                        <input
                          type="text"
                          value={ofSolver}
                          onChange={(e) => setOfSolver(e.target.value)}
                        />
                      </label>
                      <label className="settings-control">
                        <span>{pt ? 'Iterações máx.' : 'Max iterations'}</span>
                        <input
                          type="number"
                          min={1}
                          max={100000}
                          value={ofMaxIter}
                          onChange={(e) => setOfMaxIter(Number(e.target.value))}
                        />
                      </label>
                      <label className="settings-control">
                        <span>{pt ? 'Turbulência' : 'Turbulence'}</span>
                        <input
                          type="text"
                          value={ofTurb}
                          onChange={(e) => setOfTurb(e.target.value)}
                        />
                      </label>
                      <label className="settings-control">
                        <span>{pt ? 'Convergência' : 'Convergence'}</span>
                        <input
                          type="number"
                          step="any"
                          min={1e-12}
                          value={ofConv}
                          onChange={(e) => setOfConv(Number(e.target.value))}
                        />
                      </label>
                    </div>
                  </section>

                  <section className="setting-card setting-card-wide">
                    <h3>{pt ? 'Modelagem 3d' : '3d modeling'}</h3>
                    <p className="setting-card-desc">
                      {pt
                        ? 'O pipeline suporta geração via blender e caminhos python/stl; escolha o perfil preferido para a equipa.'
                        : 'The pipeline supports blender generation and python/stl paths; pick the preferred profile for your team.'}
                    </p>
                    <label className="settings-control">
                      <span>{pt ? 'Perfil' : 'Profile'}</span>
                      <select
                        value={modelingProfile}
                        onChange={(e) => setModelingProfile(e.target.value)}
                      >
                        <option value="blender">blender</option>
                        <option value="python">python / stl</option>
                      </select>
                    </label>
                    <label className="settings-control settings-control-stack">
                      <span>{pt ? 'Notas' : 'Notes'}</span>
                      <textarea
                        className="settings-textarea"
                        rows={2}
                        value={modelingNotes}
                        onChange={(e) => setModelingNotes(e.target.value)}
                        placeholder={pt ? 'Caminhos, scripts, versão do blender…' : 'Paths, scripts, blender version…'}
                      />
                    </label>
                  </section>

                  <section className="setting-card setting-card-wide">
                    <h3>{pt ? 'Outros softwares cfd' : 'Other cfd software'}</h3>
                    <p className="setting-card-desc">
                      {pt
                        ? 'Campo livre para ansys, fluent, su2, etc. (apenas documentação na interface).'
                        : 'Free text for ansys, fluent, su2, etc. (documentation in the ui only).'}
                    </p>
                    <textarea
                      className="settings-textarea"
                      rows={3}
                      value={cfdOtherNotes}
                      onChange={(e) => setCfdOtherNotes(e.target.value)}
                    />
                  </section>

                  <section className="setting-card">
                    <h3>{t('simulations')}</h3>
                    <p className="setting-card-desc">{t('simulationsDesc')}</p>
                    <label className="settings-control">
                      <span>
                        {pt
                          ? 'Intervalo de atualização dos jobs (s)'
                          : 'Jobs list refresh interval (s)'}
                      </span>
                      <input
                        type="number"
                        min={3}
                        max={120}
                        value={jobsPollSec}
                        onChange={(e) => setJobsPollSec(Number(e.target.value))}
                      />
                    </label>
                    <p className="setting-card-hint settings-hint-small">
                      {pt
                        ? 'Afeta a página «jobs» (recarregue a aba para aplicar o novo intervalo).'
                        : 'Affects the «jobs» page (reload that tab to apply the new interval).'}
                    </p>
                    <button
                      type="button"
                      className="settings-link-btn"
                      onClick={() => navigateTab('jobs')}
                    >
                      {pt ? 'Abrir jobs' : 'Open jobs'}
                    </button>
                  </section>

                  <section className="setting-card setting-card-wide">
                    <h3>{pt ? 'Avançado' : 'Advanced'}</h3>
                    <p className="setting-card-desc">
                      {pt
                        ? 'Dicas técnicas adicionais nas áreas de simulação e pipeline (reservado para extensões futuras da ui).'
                        : 'Extra technical hints in simulation and pipeline areas (reserved for future ui extensions).'}
                    </p>
                    <label className="settings-check">
                      <input
                        type="checkbox"
                        checked={advancedHints}
                        onChange={(e) => setAdvancedHints(e.target.checked)}
                      />
                      <span>{pt ? 'Ativar dicas avançadas' : 'Enable advanced hints'}</span>
                    </label>
                  </section>

                  <section className="setting-card setting-card-wide">
                    <h3>{pt ? 'Sessão' : 'Session'}</h3>
                    <p className="setting-card-desc">
                      {pt
                        ? 'Sem login real: limpa preferências locais e repõe idioma/tema padrão.'
                        : 'No real login: clears local preferences and resets default language/theme.'}
                    </p>
                    <button type="button" className="settings-danger-btn" onClick={handleLogout}>
                      {pt ? 'Sair / deslogar' : 'Log out'}
                    </button>
                  </section>

                  <section className="setting-card setting-card-wide">
                    <h3>{pt ? 'Desenvolvimento e serviço' : 'Development and service'}</h3>
                    <p className="setting-card-desc">
                      {pt
                        ? 'Swagger abre num novo separador. Encerrar o backend requer ALLOW_DEV_SHUTDOWN=1. O navegador não fecha abas abertas pelo utilizador por segurança.'
                        : 'Swagger opens in a new tab. Backend shutdown needs ALLOW_DEV_SHUTDOWN=1. Browsers block closing user-opened tabs.'}
                    </p>
                    <div className="settings-btn-row">
                      <button type="button" className="settings-link-btn" onClick={openSwagger}>
                        Swagger /docs
                      </button>
                      <button type="button" className="settings-link-btn" onClick={shutdownBackend}>
                        {pt ? 'Encerrar backend' : 'Shutdown backend'}
                      </button>
                      <button type="button" className="settings-link-btn" onClick={tryQuitFrontend}>
                        {pt ? 'Tentar fechar este separador' : 'Try to close this tab'}
                      </button>
                    </div>
                    <p className="setting-card-hint settings-hint-small">
                      {pt
                        ? '«Reiniciar» backend = encerrar processo e voltar a correr uvicorn ou docker compose up manualmente.'
                        : '«Restart» backend = stop the process and run uvicorn or docker compose up again manually.'}
                    </p>
                  </section>
                </div>

                <div className="settings-footer-actions">
                  <button type="button" className="settings-save-btn" onClick={handleSave} disabled={saving}>
                    {saving ? (pt ? 'Salvando…' : 'Saving…') : pt ? 'Salvar configurações' : 'Save settings'}
                  </button>
                  <button type="button" className="settings-reload-btn" onClick={() => load()} disabled={loading}>
                    {pt ? 'Recarregar da base' : 'Reload from database'}
                  </button>
                </div>
              </>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
