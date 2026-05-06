import { useState, useEffect, useCallback, useRef } from 'react'
import Dashboard from './components/Dashboard'
import SimulationHistory from './components/SimulationHistory'
import ComparisonPage from './components/ComparisonPage'
import BedWizard from './components/BedWizard'
import CFDSimulation from './components/CFDSimulation'
import CasosCFD from './components/CasosCFD'
import JobStatus from './components/JobStatus'
import ResultsList from './components/ResultsList'
import TemplateEditor from './components/TemplateEditor'
import ProfilePage from './components/ProfilePage'
import ReportsPage from './components/ReportsPage'
import DatabasePage from './components/DatabasePage'
import SavedTemplatesPage from './components/SavedTemplatesPage'
import SettingsPage from './components/SettingsPage'
import MeshViewer3DPage from './components/MeshViewer3DPage'
import DevModePanel from './components/DevModePanel'
import ThemeIcon from './components/ThemeIcon'
import { HelpModal, DocsModal, CreditsModal } from './components/WizardHelpers'
import UserSwitcherModal from './components/UserSwitcherModal'
import { getSystemStatus, getSettings } from './services/api'
import api from './services/api'
import { useLanguage } from './context/LanguageContext'
import { useTheme } from './context/ThemeContext'
import { useAppUi } from './context/AppUiContext'
import { useActiveUser } from './context/UserContext'

const SIMPLE_MODE_TABS = new Set([
  'dashboard',
  'wizard',
  'mesh-viewer',
  'cfd',
  'casos',
  'jobs',
  'results',
  'history',
  'settings',
])

/** secções da sidebar que ainda têm submenu (dropdown) */
const COLLAPSIBLE_NAV_SECTIONS = new Set(['templates', 'simulation', 'analysis', 'results'])

function App() {
  const { language, toggleLanguage, t, setLanguage } = useLanguage();
  const { theme, toggleTheme, setThemeMode } = useTheme();
  const { simpleMode, devMode, applySettingsFromApi, setSimpleMode, setDevMode } = useAppUi();
  const { activeUserId, setActiveUserId } = useActiveUser();
  const [activeTab, setActiveTab] = useState('dashboard') // dashboard, create, wizard, pipeline, cfd, jobs, results
  const [wizardResetKey, setWizardResetKey] = useState(0)
  const [systemStatus, setSystemStatus] = useState(null)
  const [backendUnreachable, setBackendUnreachable] = useState(false)
  const [currentJob, setCurrentJob] = useState(null)
  const [lastBedFile, setLastBedFile] = useState(null)
  const [isScrolled, setIsScrolled] = useState(false)
  const [showHelp, setShowHelp] = useState(false)
  const [showDocs, setShowDocs] = useState(false)
  const [showCredits, setShowCredits] = useState(false)
  const [showUserSwitcher, setShowUserSwitcher] = useState(false)
  const [expandedSections, setExpandedSections] = useState({})
  const [bootMeshViewerId, setBootMeshViewerId] = useState(null)
  const mainContentRef = useRef(null)
  const settingsAppliedRef = useRef(false)

  useEffect(() => {
    window.scrollTo({ top: 0, left: 0, behavior: 'auto' })
    const el = mainContentRef.current
    if (el) {
      el.scrollTo({ top: 0, left: 0, behavior: 'auto' })
    }
  }, [activeTab])

  useEffect(() => {
    try {
      const p = new URLSearchParams(window.location.search)
      const id = p.get('meshViewerId')
      if (id && id.length >= 8) {
        setBootMeshViewerId(id)
        setActiveTab('mesh-viewer')
        const u = new URL(window.location.href)
        u.searchParams.delete('meshViewerId')
        const qs = u.searchParams.toString()
        window.history.replaceState({}, '', `${u.pathname}${qs ? `?${qs}` : ''}${u.hash}`)
      }
    } catch (_e) {
      /* ignore */
    }
  }, [])

  useEffect(() => {
    const suffix = language === 'pt' ? 'pipeline cfd' : 'cfd pipeline'
    document.title = `${t('appCreativeTitle')} — ${suffix}`
  }, [language, t])

  // abre o modal de escolha de utilizador apenas na primeirissima
  // execucao; a flag userSwitcherSeen e gravada apos qualquer interacao
  useEffect(() => {
    try {
      const seen = localStorage.getItem('userSwitcherSeen')
      if (!seen) setShowUserSwitcher(true)
    } catch (_e) {
      // localStorage indisponivel, ignorar
    }
  }, [])

  const handleUserSwitcherSelect = useCallback((id) => {
    setActiveUserId(id)
    setShowUserSwitcher(false)
    try {
      localStorage.setItem('userSwitcherSeen', '1')
    } catch (_e) {}
  }, [setActiveUserId])

  const handleUserSwitcherClose = useCallback(() => {
    setShowUserSwitcher(false)
    try {
      localStorage.setItem('userSwitcherSeen', '1')
    } catch (_e) {}
  }, [])

  useEffect(() => {
    if (settingsAppliedRef.current) return;
    settingsAppliedRef.current = true;
    let cancelled = false;
    getSettings()
      .then((s) => {
        if (cancelled) return;
        applySettingsFromApi(s);
        const tm =
          s.theme_mode === 'dark' || s.theme_mode === 'light' || s.theme_mode === 'system'
            ? s.theme_mode
            : 'system';
        setThemeMode(tm);
        setLanguage(s.language === 'en' ? 'en' : 'pt');
        const j = Number(s.jobs_poll_interval_sec);
        if (Number.isFinite(j) && j >= 3 && j <= 120) {
          localStorage.setItem('jobsPollIntervalSec', String(j));
        }
      })
      .catch(() => {});
    return () => {
      cancelled = true;
    };
  }, [applySettingsFromApi, setLanguage, setThemeMode]);

  useEffect(() => {
    if (!simpleMode) return;
    if (!SIMPLE_MODE_TABS.has(activeTab)) {
      setExpandedSections((prev) => {
        const next = {};
        Object.keys(prev).forEach((k) => {
          next[k] = false;
        });
        return next;
      });
      setActiveTab('dashboard');
    }
  }, [simpleMode, activeTab]);

  const checkSystemStatus = useCallback(async () => {
    try {
      const status = await getSystemStatus()
      setSystemStatus(status)
      setBackendUnreachable(false)
    } catch (error) {
      console.error('erro ao verificar sistema:', error)
      setSystemStatus(null)
      setBackendUnreachable(true)
    }
  }, [])

  useEffect(() => {
    checkSystemStatus()
    const pollId = setInterval(checkSystemStatus, 25000)
    return () => clearInterval(pollId)
  }, [checkSystemStatus])

  useEffect(() => {
    // detectar scroll para encolher header
    const handleScroll = () => {
      if (window.scrollY > 50) {
        setIsScrolled(true)
      } else {
        setIsScrolled(false)
      }
    }

    const handleKeyDown = (event) => {
      if (event.key === 'Escape') {
        if (showHelp) setShowHelp(false)
        if (showDocs) setShowDocs(false)
        if (showCredits) setShowCredits(false)
      }
    }

    window.addEventListener('scroll', handleScroll)
    window.addEventListener('keydown', handleKeyDown)
    return () => {
      window.removeEventListener('scroll', handleScroll)
      window.removeEventListener('keydown', handleKeyDown)
    }
  }, [showHelp, showDocs, showCredits])

  const handleLogout = useCallback(() => {
    sessionStorage.clear();
    [
      'app_simple_mode',
      'app_dev_mode',
      'jobsPollIntervalSec',
      'theme',
      'themeMode',
      'language',
      'cfd_active_user_id',
    ].forEach((k) => localStorage.removeItem(k));
    setSimpleMode(false);
    setDevMode(false);
    setThemeMode('system');
    setLanguage('pt');
    api.defaults.timeout = 30000;
    setExpandedSections((prev) => {
      const next = {};
      Object.keys(prev).forEach((k) => {
        next[k] = false;
      });
      return next;
    });
    setActiveTab('dashboard');
  }, [setDevMode, setLanguage, setSimpleMode, setThemeMode]);

  const navigateToTab = (tab) => {
    const sectionByTab = {
      dashboard: 'dashboard',
      wizard: 'create',
      'mesh-viewer': 'dashboard',
      templates: 'templates',
      'templates-saved': 'templates',
      cfd: 'simulation',
      casos: 'simulation',
      database: 'database',
      comparisons: 'analysis',
      reports: 'analysis',
      jobs: 'results',
      results: 'results',
      history: 'results',
      profile: 'profile',
      settings: 'settings',
    }
    const sec = sectionByTab[tab]
    setExpandedSections((prev) => {
      const next = {}
      Object.keys(prev).forEach((k) => {
        next[k] = false
      })
      if (sec && COLLAPSIBLE_NAV_SECTIONS.has(sec)) {
        next[sec] = true
      }
      return next
    })
    setActiveTab(tab)
  }

  const handleJobCreated = (job) => {
    setCurrentJob(job)
    navigateToTab('jobs')
  }

  const resetToCreationHome = () => {
    setExpandedSections((prev) => {
      const newState = {};
      Object.keys(prev).forEach((key) => {
        newState[key] = false;
      });
      return newState;
    });
    setActiveTab('wizard');
    setWizardResetKey((k) => k + 1);
  };

  const goToCreationMode = () => {
    resetToCreationHome();
  };

  const toggleSection = (section) => {
    setExpandedSections(prev => {
      // se a seção já está aberta, fecha ela
      if (prev[section]) {
        return {
          ...prev,
          [section]: false
        };
      }
      
      // se não está aberta, fecha todas as outras e abre apenas esta
      const newState = {};
      Object.keys(prev).forEach(key => {
        newState[key] = false;
      });
      newState[section] = true;
      
      return newState;
    });
  }

  return (
    <div className="app">
      {/* header */}
      <header className={`header ${isScrolled ? 'header-scrolled' : ''}`}>
        <div className="header-content">
          <div className="header-left">
            <button
              type="button"
              className="logo-container logo-container-btn"
              onClick={resetToCreationHome}
              title={language === 'pt' ? 'ir para criar' : 'go to create'}
              aria-label={language === 'pt' ? 'ir para criar' : 'go to create'}
            >
              <img 
                src="/image/cfdPipelineLight.png" 
                alt="cfd pipeline logo" 
                className={`logo-icon ${theme === 'dark' ? 'logo-dark' : 'logo-light'}`}
              />
              <div className="logo-text">
                <h1>{t('appCreativeTitle')}</h1>
                <span className="subtitle">{t('appTagline')}</span>
              </div>
            </button>
          </div>
          
          <div className="header-right">
            <button
              type="button"
              className="new-simulation-btn"
              onClick={goToCreationMode}
            >
              <ThemeIcon light="runLight.png" dark="runLight.png" alt={t('headerStartButton')} className="btn-icon" />
              {t('headerStartButton')}
            </button>
            <div className="system-status">
              {systemStatus && (
                <>
                  <div className="status-item">
                    <ThemeIcon 
                      light={systemStatus.api === 'running' ? "onlineLight.png" : "offlineLight.png"} 
                      dark={systemStatus.api === 'running' ? "onlineDark.png" : "offlineDark.png"} 
                      alt={systemStatus.api === 'running' ? 'online' : 'offline'} 
                      className="status-icon" 
                      location="header"
                    />
                    <span className="status-label">
                      {systemStatus.api === 'running' ? t('online') : t('offline')}
                    </span>
                  </div>
                  <div className="status-item">
                    <ThemeIcon light="jobLight.png" dark="jobDark.png" alt="jobs" className="status-icon" location="header" />
                    <span className="status-label">
                      {systemStatus.jobs?.running || 0} {t('running')}
                    </span>
                  </div>
                </>
              )}
            </div>
            
            <button 
              type="button"
              className="theme-toggle" 
              onClick={toggleTheme} 
              title={theme === 'light' ? (language === 'pt' ? 'modo escuro' : 'dark mode') : (language === 'pt' ? 'modo claro' : 'light mode')}
              aria-label={theme === 'light' ? 'toggle dark mode' : 'toggle light mode'}
            >
              <ThemeIcon 
                light="image-removebg-preview(15).png" 
                dark="darkmode_moon_sun_white.png" 
                alt={theme === 'light' ? 'dark mode' : 'light mode'} 
                className="theme-icon" 
                location="header"
              />
              <span className="theme-text">{theme === 'light' ? (language === 'pt' ? 'escuro' : 'dark') : (language === 'pt' ? 'claro' : 'light')}</span>
            </button>

            <div className="header-lang-cluster">
              {backendUnreachable && (
                <button
                  type="button"
                  className="header-backend-warning"
                  onClick={() => checkSystemStatus()}
                  title={t('backendConnectionError')}
                  aria-label={t('backendConnectionError')}
                >
                  <ThemeIcon
                    light="offlineLight.png"
                    dark="offlineDark.png"
                    alt=""
                    className="header-warning-icon"
                    location="header"
                  />
                </button>
              )}

              <button 
                type="button"
                className="language-toggle" 
                onClick={toggleLanguage} 
                title={language === 'pt' ? 'switch to english' : 'mudar para português'}
                aria-label={language === 'pt' ? 'mudar idioma' : 'change language'}
              >
                <ThemeIcon 
                  light={language === 'pt' ? "brazil_flag_icon_white.png" : "usa_flag_icon_white_50stars.png"} 
                  dark={language === 'pt' ? "brazil_flag_icon_white.png" : "usa_flag_icon_white_50stars.png"} 
                  alt={language === 'pt' ? 'brasil' : 'usa'} 
                  className="flag" 
                  location="header"
                />
                <span className="lang-text">{language === 'pt' ? 'br' : 'us'}</span>
              </button>

              <button
                type="button"
                className="user-switcher-btn"
                onClick={(e) => { e.stopPropagation(); setShowUserSwitcher(true); }}
                title={language === 'pt' ? 'trocar utilizador' : 'switch user'}
                aria-label={language === 'pt' ? 'trocar utilizador' : 'switch user'}
              >
                <ThemeIcon
                  light="profileLight.png"
                  dark="profileLight.png"
                  alt=""
                  className="user-switcher-icon"
                  location="header"
                />
              </button>
            </div>
          </div>
        </div>
      </header>



      <div className="app-body">
        {/* sidebar (barra lateral) */}
        <aside className="sidebar">
          <nav className="sidebar-nav">
            <div className="nav-section">
              <button
                type="button"
                className={`nav-item nav-item-root nav-item-folder-face ${activeTab === 'dashboard' ? 'active' : ''}`}
                onClick={() => navigateToTab('dashboard')}
              >
                <ThemeIcon light="analiseLight.png" dark="analiseLight.png" alt="dashboard" className="nav-icon" location="sidebar" />
                <span className="nav-label">{language === 'pt' ? 'dashboard' : 'dashboard'}</span>
              </button>
            </div>

            <div className="nav-section">
              <button
                type="button"
                className={`nav-item nav-item-root nav-item-folder-face ${activeTab === 'mesh-viewer' ? 'active' : ''}`}
                onClick={() => navigateToTab('mesh-viewer')}
              >
                <ThemeIcon light="cfd_gear_white.png" dark="cfd_gear_white.png" alt="3d" className="nav-icon" location="sidebar" />
                <span className="nav-label">{language === 'pt' ? 'visualização 3d' : '3d viewer'}</span>
              </button>
            </div>

            <div className="nav-section">
              <button
                type="button"
                className={`nav-item nav-item-root nav-item-folder-face ${activeTab === 'wizard' ? 'active' : ''}`}
                onClick={() => navigateToTab('wizard')}
              >
                <ThemeIcon light="create_bed_white.png" dark="create_bed_white.png" alt={t('create')} className="nav-icon" location="sidebar" />
                <span className="nav-label">{t('create')}</span>
              </button>
            </div>

            {!simpleMode && (
            <div className="nav-section">
              <div
                className="nav-section-header"
                onClick={() => toggleSection('templates')}
                role="button"
                tabIndex={0}
                aria-expanded={!!expandedSections.templates}
                onKeyDown={(e) => {
                  if (e.key === 'Enter' || e.key === ' ') {
                    e.preventDefault();
                    toggleSection('templates');
                  }
                }}
              >
                <h3 className="nav-section-title">
                  <ThemeIcon light="folderLight.png" dark="folderDark.png" alt="templates" className="section-icon" location="sidebar" />
                  templates
                </h3>
                <span className="nav-folder-toggle" aria-hidden="true">
                  {expandedSections.templates ? '−' : '+'}
                </span>
              </div>
              {expandedSections.templates && (
                <div className="nav-subsection">
                  <button
                    className={`nav-item ${activeTab === 'templates' ? 'active' : ''}`}
                    onClick={() => setActiveTab('templates')}
                  >
                    <ThemeIcon light="textEditorLight.png" dark="textEditorLight.png" alt="templates" className="nav-icon" />
                    <span className="nav-label">templates</span>
                  </button>
                  <button
                    className={`nav-item ${activeTab === 'templates-saved' ? 'active' : ''}`}
                    onClick={() => setActiveTab('templates-saved')}
                  >
                    <ThemeIcon light="folderLight.png" dark="folderLight.png" alt="templates salvos" className="nav-icon" />
                    <span className="nav-label">{language === 'pt' ? 'templates salvos' : 'saved templates'}</span>
                  </button>
                </div>
              )}
            </div>
            )}

            <div className="nav-section">
              <div
                className="nav-section-header"
                onClick={() => toggleSection('simulation')}
                role="button"
                tabIndex={0}
                aria-expanded={!!expandedSections.simulation}
                onKeyDown={(e) => {
                  if (e.key === 'Enter' || e.key === ' ') {
                    e.preventDefault();
                    toggleSection('simulation');
                  }
                }}
              >
                <h3 className="nav-section-title">
                  <ThemeIcon light="cfd_gear_white.png" dark="cfd_gear_white.png" alt="simulation" className="section-icon" location="sidebar" />
                  {t('simulation')}
                </h3>
                <span className="nav-folder-toggle" aria-hidden="true">
                  {expandedSections.simulation ? '−' : '+'}
                </span>
              </div>
              {expandedSections.simulation && (
                <div className="nav-subsection">
                  <button
                    className={`nav-item ${activeTab === 'cfd' ? 'active' : ''}`}
                    onClick={() => setActiveTab('cfd')}
                  >
                    <ThemeIcon light="cfd_gear_white.png" dark="cfd_gear_white.png" alt="simulações CFD" className="nav-icon" />
                    <span className="nav-label">{t('cfdSimulation')}</span>
                  </button>
                  <button
                    className={`nav-item ${activeTab === 'casos' ? 'active' : ''}`}
                    onClick={() => setActiveTab('casos')}
                  >
                    <ThemeIcon light="folderLight.png" dark="folderLight.png" alt="casos cfd" className="nav-icon" />
                    <span className="nav-label">{t('casosCfd')}</span>
                  </button>
                </div>
              )}
            </div>

            {!simpleMode && (
            <div className="nav-section">
              <button
                type="button"
                className={`nav-item nav-item-root nav-item-folder-face ${activeTab === 'database' ? 'active' : ''}`}
                onClick={() => navigateToTab('database')}
              >
                <ThemeIcon light="database-01-svgrepo-com.svg" dark="database-01-svgrepo-com.svg" alt="database" className="nav-icon database-icon" location="sidebar" />
                <span className="nav-label">{language === 'pt' ? 'banco de dados' : 'database'}</span>
              </button>
            </div>
            )}

            {!simpleMode && (
            <div className="nav-section">
              <div
                className="nav-section-header"
                onClick={() => toggleSection('analysis')}
                role="button"
                tabIndex={0}
                aria-expanded={!!expandedSections.analysis}
                onKeyDown={(e) => {
                  if (e.key === 'Enter' || e.key === ' ') {
                    e.preventDefault();
                    toggleSection('analysis');
                  }
                }}
              >
                <h3 className="nav-section-title">
                  <ThemeIcon light="analiseLight.png" dark="analiseLight.png" alt="analysis" className="section-icon" location="sidebar" />
                  {language === 'pt' ? 'análises' : 'analysis'}
                </h3>
                <span className="nav-folder-toggle" aria-hidden="true">
                  {expandedSections.analysis ? '−' : '+'}
                </span>
              </div>
              {expandedSections.analysis && (
                <div className="nav-subsection">
                  <button
                    className={`nav-item ${activeTab === 'comparisons' ? 'active' : ''}`}
                    onClick={() => setActiveTab('comparisons')}
                  >
                    <ThemeIcon light="compareLight.png" dark="compareLight.png" alt="comparações" className="nav-icon" />
                    <span className="nav-label">{language === 'pt' ? 'comparações' : 'comparisons'}</span>
                  </button>
                  <button
                    className={`nav-item ${activeTab === 'reports' ? 'active' : ''}`}
                    onClick={() => setActiveTab('reports')}
                  >
                    <ThemeIcon light="folderLight.png" dark="folderLight.png" alt="relatórios" className="nav-icon" />
                    <span className="nav-label">{language === 'pt' ? 'relatórios' : 'reports'}</span>
                  </button>
                </div>
              )}
            </div>
            )}

            <div className="nav-section">
              <div
                className="nav-section-header"
                onClick={() => toggleSection('results')}
                role="button"
                tabIndex={0}
                aria-expanded={!!expandedSections.results}
                onKeyDown={(e) => {
                  if (e.key === 'Enter' || e.key === ' ') {
                    e.preventDefault();
                    toggleSection('results');
                  }
                }}
              >
                <h3 className="nav-section-title">
                  <ThemeIcon light="cfd_gear_white.png" dark="cfd_gear_white.png" alt="results" className="section-icon" location="sidebar" />
                  {t('results')}
                </h3>
                <span className="nav-folder-toggle" aria-hidden="true">
                  {expandedSections.results ? '−' : '+'}
                </span>
              </div>
              {expandedSections.results && (
                <div className="nav-subsection">
                  <button
                    className={`nav-item ${activeTab === 'jobs' ? 'active' : ''}`}
                    onClick={() => setActiveTab('jobs')}
                  >
                    <ThemeIcon light="jobLight.png" dark="jobLight.png" alt="jobs" className="nav-icon" />
                    <span className="nav-label">{t('jobs')} ({systemStatus?.jobs?.total || 0})</span>
                  </button>
                  <button
                    className={`nav-item ${activeTab === 'results' ? 'active' : ''}`}
                    onClick={() => setActiveTab('results')}
                  >
                    <ThemeIcon light="folderLight.png" dark="folderLight.png" alt="results" className="nav-icon" />
                    <span className="nav-label">{t('results')}</span>
                  </button>
                  <button
                    className={`nav-item ${activeTab === 'history' ? 'active' : ''}`}
                    onClick={() => setActiveTab('history')}
                  >
                    <ThemeIcon light="folderLight.png" dark="folderLight.png" alt="histórico" className="nav-icon" />
                    <span className="nav-label">{language === 'pt' ? 'histórico' : 'history'}</span>
                  </button>
                </div>
              )}
            </div>

            {!simpleMode && (
            <div className="nav-section">
              <button
                type="button"
                className={`nav-item nav-item-root nav-item-folder-face ${activeTab === 'profile' ? 'active' : ''}`}
                onClick={() => navigateToTab('profile')}
              >
                <ThemeIcon light="profileLight.png" dark="profileLight.png" alt="profile" className="nav-icon" location="sidebar" />
                <span className="nav-label">{language === 'pt' ? 'perfil' : 'profile'}</span>
              </button>
            </div>
            )}

            <div className="nav-section">
              <button
                type="button"
                className={`nav-item nav-item-root nav-item-folder-face ${activeTab === 'settings' ? 'active' : ''}`}
                onClick={() => navigateToTab('settings')}
              >
                <ThemeIcon light="settingsLight.png" dark="settingsLight.png" alt="settings" className="nav-icon" location="sidebar" />
                <span className="nav-label">{t('configuracoes')}</span>
              </button>
            </div>
          </nav>
        </aside>

        {/* conteúdo principal */}
        <main className="main-content" ref={mainContentRef}>
          {devMode && <DevModePanel activeTab={activeTab} />}
          {activeTab === 'wizard' && (
            <div className="tab-content">
              <BedWizard key={wizardResetKey} />
            </div>
          )}

          {activeTab === 'mesh-viewer' && (
            <div className="tab-content">
              <MeshViewer3DPage
                language={language}
                initialMeshId={bootMeshViewerId}
                onConsumedBootId={() => setBootMeshViewerId(null)}
              />
            </div>
          )}

          {activeTab === 'cfd' && (
            <div className="tab-content">
              <CFDSimulation bedFileName={lastBedFile} />
            </div>
          )}

          {activeTab === 'casos' && (
            <div className="tab-content">
              <CasosCFD />
            </div>
          )}

          {activeTab === 'jobs' && (
            <div className="tab-content">
              <JobStatus currentJob={currentJob} />
            </div>
          )}

          {activeTab === 'results' && (
            <div className="tab-content">
              <ResultsList />
            </div>
          )}

          {activeTab === 'history' && (
            <div className="tab-content">
              <SimulationHistory />
            </div>
          )}

          {activeTab === 'comparisons' && (
            <div className="tab-content">
              <ComparisonPage />
            </div>
          )}

          {activeTab === 'templates' && (
            <div className="tab-content">
              <TemplateEditor />
            </div>
          )}

          {activeTab === 'templates-saved' && <SavedTemplatesPage />}

          {activeTab === 'database' && <DatabasePage />}

          {activeTab === 'reports' && <ReportsPage />}

          {activeTab === 'dashboard' && (
            <div className="tab-content">
              <Dashboard />
            </div>
          )}

          {activeTab === 'profile' && <ProfilePage />}

          {activeTab === 'settings' && (
            <SettingsPage navigateTab={navigateToTab} onLogout={handleLogout} />
          )}
        </main>
      </div>

      {/* footer */}
      <footer className="footer">
        <div className="footer-content">
          <div className="footer-section footer-info">
            <div className="footer-logo">
              <ThemeIcon 
                light="cfdPipelineLight.png" 
                dark="cfdPipelineLight.png" 
                alt={t('footerLogoAlt')} 
                className="footer-icon"
                location="footer"
              />
              <span className="footer-title footer-brand-title">{t('footerBrandName')}</span>
            </div>
            <p className="footer-description">
              {language === 'pt' 
                ? 'sistema de simulação de leitos empacotados com openfoam e blender'
                : 'packed bed simulation system with openfoam and blender'}
            </p>
            <div className="footer-version">
              <span className="version-badge">v0.1.0</span>
              <span className="version-status">beta</span>
            </div>
            
            <div className="footer-section footer-academic">
              <h4>{language === 'pt' ? 'acadêmico' : 'academic'}</h4>
              <div className="academic-logos">
                <a 
                  href="https://vhlab.com.br/" 
                  target="_blank" 
                  rel="noopener noreferrer"
                >
                  <img 
                    src="/image/logo-light.png" 
                    alt="pucrs logo" 
                    className="academic-logo"
                  />
                </a>
                <a 
                  href="https://portal.pucrs.br/" 
                  target="_blank" 
                  rel="noopener noreferrer"
                >
                  <img 
                    src="/image/escola-politecnica.png" 
                    alt="escola politecnica / vhlab" 
                    className="academic-logo"
                  />
                </a>
                <a 
                  href="https://www.politecnica.pucrs.br/laboratorios/lope/" 
                  target="_blank" 
                  rel="noopener noreferrer"
                >
                  <img 
                    src="/image/logo_lope.png" 
                    alt="lope laboratorio" 
                    className="academic-logo"
                  />
                </a>
              </div>
              <p className="academic-info">
              <strong>{language === 'pt' ? 'trabalho de conclusão de curso' : 'final project'}</strong><br />
                {language === 'pt' ? 'ciência da computação' : 'computer science'}<br />
                {language === 'pt' ? 'engenharia química' : 'chemical engineering'}
              </p>
              <p className="academic-year">2024/2026</p>
            </div>
          </div>

          <div className="footer-section footer-links">
            <h4>{language === 'pt' ? 'projeto' : 'project'}</h4>
            <ul>
              <li>
                <a href="https://github.com/bengo501/CFD-PIPELINE-TCC-1" target="_blank" rel="noopener noreferrer">
                  <ThemeIcon light="githubLight.png" dark="githubLight.png" alt="github" className="link-icon" location="footer" />
                  github
                </a>
              </li>
              <li>
                <a href="https://github.com/bengo501/CFD-PIPELINE-TCC-1/issues" target="_blank" rel="noopener noreferrer">
                  <ThemeIcon light="issuesLight.png" dark="issuesLight.png" alt="issues" className="link-icon" />
                  {language === 'pt' ? 'issues' : 'issues'}
                </a>
              </li>
              <li>
                <a href="https://github.com/users/bengo501/projects/2" target="_blank" rel="noopener noreferrer">
                  <ThemeIcon light="kanbanLight.png" dark="kanbanLight.png" alt="kanban" className="link-icon" />
                  {language === 'pt' ? 'kanban' : 'kanban'}
                </a>
              </li>
              <li>
                <button type="button" className="footer-about-btn" onClick={() => setShowCredits(true)}>
                  <ThemeIcon light="profileLight.png" dark="profileLight.png" alt="" className="link-icon" location="footer" />
                  {language === 'pt' ? 'sobre' : 'about'}
                </button>
              </li>
              <li>
                <a
                  href="https://github.com/bengo501/CFD-PIPELINE-TCC-1/blob/main/README.md"
                  target="_blank"
                  rel="noopener noreferrer"
                >
                  <ThemeIcon light="docsLight.png" dark="docsLight.png" alt="" className="link-icon" location="footer" />
                  {language === 'pt' ? 'mais informações' : 'more information'}
                </a>
              </li>
              <li>
                <a href="https://github.com/bengo501?tab=repositories" target="_blank" rel="noopener noreferrer">
                  <ThemeIcon light="folderLight.png" dark="folderLight.png" alt="" className="link-icon" location="footer" />
                  {language === 'pt' ? 'mais projetos' : 'more projects'}
                </a>
              </li>
              <li>
                <button className="footer-help-btn" onClick={() => setShowHelp(true)}>
                  <ThemeIcon light="helpLight.png" dark="helpLight.png" alt="ajuda" className="link-icon" location="footer" />
                  {language === 'pt' ? 'ajuda' : 'help'}
                </button>
              </li>
              <li>
                <button className="footer-docs-btn" onClick={() => setShowDocs(true)}>
                  <ThemeIcon light="docsLight.png" dark="docsLight.png" alt="documentação" className="link-icon" location="footer" />
                  {language === 'pt' ? 'documentação' : 'documentation'}
                </button>
              </li>
            </ul>
          </div>

          <div className="footer-section footer-tech">
            <h4>{language === 'pt' ? 'tecnologias' : 'technologies'}</h4>
            <ul>
              <li>
                <ThemeIcon light="triangle_white_outline.png" dark="triangle_white_outline.png" alt="openfoam" className="tech-icon openfoam-icon" />
                <span className="tech-badge">openfoam</span>
                <span className="tech-version">11</span>
              </li>
              <li>
                <ThemeIcon light="blenderLight.png" dark="blenderLight.png" alt="blender" className="tech-icon" />
                <span className="tech-badge">blender</span>
                <span className="tech-version">4.x</span>
              </li>
              <li>
                <ThemeIcon light="reactLight.png" dark="reactLight.png" alt="react" className="tech-icon" />
                <span className="tech-badge">react</span>
                <span className="tech-version">18</span>
              </li>
              <li>
                <ThemeIcon light="viteLight.png" dark="viteLight.png" alt="vite" className="tech-icon" />
                <span className="tech-badge">vite</span>
                <span className="tech-version">5.x</span>
              </li>
              <li>
                <ThemeIcon light="pythonLogoLight.png" dark="pythonLogoLight.png" alt="python" className="tech-icon" />
                <span className="tech-badge">python</span>
                <span className="tech-version">3.11</span>
              </li>
              <li>
                <ThemeIcon light="wslLogoLight.png" dark="wslLogoLight.png" alt="wsl" className="tech-icon" />
                <span className="tech-badge">wsl</span>
                <span className="tech-version">2</span>
              </li>
              <li>
                <ThemeIcon light="jsLight.png" dark="jsLight.png" alt="javascript" className="tech-icon" />
                <span className="tech-badge">javascript</span>
                <span className="tech-version">es6+</span>
              </li>
              <li>
                <ThemeIcon light="javaLight.png" dark="javaLight.png" alt="java" className="tech-icon" />
                <span className="tech-badge">java</span>
                <span className="tech-version">17</span>
              </li>
              <li>
                <ThemeIcon light="cssLight.png" dark="cssLight.png" alt="css" className="tech-icon" />
                <span className="tech-badge">css</span>
                <span className="tech-version">3</span>
              </li>
              <li>
                <ThemeIcon light="antlrLight.png" dark="antlrLight.png" alt="antlr" className="tech-icon" />
                <span className="tech-badge">antlr</span>
                <span className="tech-version">4.x</span>
              </li>
              <li>
                <ThemeIcon light="fastApiLight.png" dark="fastApiLight.png" alt="fastapi" className="tech-icon" />
                <span className="tech-badge">fastapi</span>
                <span className="tech-version">0.x</span>
              </li>
              <li>
                <ThemeIcon light="railwayLight.png" dark="railwayLight.png" alt="railway" className="tech-icon" />
                <span className="tech-badge">railway</span>
                <span className="tech-version">cloud</span>
              </li>
            </ul>
          </div>

          <div className="footer-section footer-database">
            <h4>{language === 'pt' ? 'banco de dados' : 'database'}</h4>
            <ul>
              <li>
                <ThemeIcon light="2106624.png" dark="postgresqlDark.png" alt="postgresql" className="db-icon" />
                <span className="db-badge">postgresql</span>
                <span className="db-version">15</span>
              </li>
              <li>
                <ThemeIcon light="redis.png" dark="redisDark.png" alt="redis" className="db-icon" />
                <span className="db-badge">redis</span>
                <span className="db-version">7</span>
              </li>
              <li>
                <ThemeIcon light="minio.png" dark="minioDark.png" alt="minio" className="db-icon" />
                <span className="db-badge">minio</span>
                <span className="db-version">s3</span>
              </li>
            </ul>
          </div>

          <div className="footer-section footer-credits">
            <h4>{language === 'pt' ? 'créditos' : 'credits'}</h4>
            <p className="credits-text">
              {language === 'pt'
                ? 'projeto de trabalho de conclusão de curso desenvolvido na pucrs / escola politécnica, em colaboração com o laboratório lope.'
                : 'final project developed at pucrs / school of engineering, in collaboration with lope laboratory.'}
            </p>
            <div className="footer-credits-detail">
              {language === 'pt' ? (
                <>
                  <p>
                    <strong>aluno:</strong> Bernardo Klein Heitz
                  </p>
                  <p>
                    <strong>orientador</strong> — trabalho de conclusão de curso (ciência da computação): prof. Marco Aurélio Mangan
                  </p>
                  <p>
                    <strong>orientadora</strong> — iniciação científica voluntária: prof. Soraia Raupp Musse
                  </p>
                  <p>
                    <strong>orientadores</strong> — bolsa de iniciação científica lope:<br />
                    prof. Rubem Mário Vargas<br />
                    Doutorando Henrique Martins Tavares
                  </p>
                </>
              ) : (
                <>
                  <p>
                    <strong>student:</strong> Bernardo Klein Heitz
                  </p>
                  <p>
                    <strong>advisor</strong> — final project (computer science): prof. Marco Aurélio Mangan
                  </p>
                  <p>
                    <strong>advisor</strong> — voluntary scientific initiation: prof. Soraia Raupp Musse
                  </p>
                  <p>
                    <strong>advisors</strong> — lope scientific initiation scholarship:<br />
                    prof. Rubem Mário Vargas<br />
                    doctoral researcher Henrique Martins Tavares
                  </p>
                </>
              )}
            </div>
            <button
              className="footer-credits-btn"
              onClick={() => setShowCredits(true)}
            >
              {language === 'pt' ? 'ver créditos' : 'view credits'}
            </button>
          </div>

        </div>

        <div className="footer-bottom">
          <div className="footer-bottom-content">
            <p className="copyright">
              © 2024-2026 {t('footerBrandName')}.
              {language === 'pt' ? ' código aberto sob licença mit.' : ' open source under mit license.'}
            </p>
            <div className="footer-social">
              <a href="https://github.com/bengo501" target="_blank" rel="noopener noreferrer" title="github profile">
                <img src="/image/githubProfileLight.png" alt="github profile" className="social-icon" />
              </a>
            </div>
          </div>
        </div>
      </footer>

      {/* modais de ajuda e documentação */}
      <HelpModal 
        show={showHelp} 
        onClose={() => setShowHelp(false)} 
        section="general"
        paramHelp={{
          'bed.diameter': {
            desc: 'diâmetro interno do leito cilíndrico',
            min: 0.01,
            max: 1.0,
            unit: 'm',
            exemplo: '0.05m para leito de 5cm'
          },
          'bed.height': {
            desc: 'altura do leito empacotado',
            min: 0.01,
            max: 2.0,
            unit: 'm',
            exemplo: '0.1m para leito de 10cm'
          },
          'particles.diameter': {
            desc: 'diâmetro das partículas esféricas',
            min: 0.001,
            max: 0.01,
            unit: 'm',
            exemplo: '0.005m para partículas de 5mm'
          },
          'particles.count': {
            desc: 'número de partículas no leito',
            min: 10,
            max: 10000,
            unit: '',
            exemplo: '100 partículas'
          }
        }}
      />
      
      <DocsModal 
        show={showDocs} 
        onClose={() => setShowDocs(false)} 
      />
      <CreditsModal 
        show={showCredits} 
        onClose={() => setShowCredits(false)} 
      />

      {showUserSwitcher && (
        <UserSwitcherModal
          activeUserId={activeUserId}
          onSelect={handleUserSwitcherSelect}
          onClose={handleUserSwitcherClose}
          language={language}
        />
      )}
    </div>
  )
}

export default App

