import { useState, useEffect, useCallback, useRef } from 'react'
import Dashboard from './pages/dashboard/Dashboard'
import ComparisonPage from './pages/comparison/ComparisonPage'
import BedWizard from './pages/wizard/BedWizard'
import CasosCFD from './pages/casos/CasosCFD'
import JobStatus from './pages/jobs/JobStatus'
import ResultsSimulationsPage from './pages/results/ResultsSimulationsPage'
import ResultsModels3DPage from './pages/results/ResultsModels3DPage'
import ResultsBedCodePage from './pages/results/ResultsBedCodePage'
import TemplateEditor from './pages/templates/TemplateEditor'
import ProfilePage from './pages/profile/ProfilePage'
import ReportsPage from './pages/reports/ReportsPage'
import DatabasePage from './pages/database/DatabasePage'
import SavedTemplatesPage from './pages/templates/SavedTemplatesPage'
import SettingsPage from './pages/settings/SettingsPage'
import MeshViewer3DPage from './pages/meshViewer/MeshViewer3DPage'
import DevModePanel from './components/common/DevModePanel'
import ThemeIcon from './components/common/ThemeIcon'
import { HelpModal, DocsModal, CreditsModal, FooterInfoModal } from './components/modals/WizardHelpers'
import UserSwitcherModal from './components/modals/UserSwitcherModal'
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
  'casos',
  'jobs',
  'results-simulations',
  'results-models',
  'results-bed',
  'settings',
])

/** secções da sidebar que ainda têm submenu (dropdown) */
const COLLAPSIBLE_NAV_SECTIONS = new Set(['templates', 'analysis', 'history', 'history-results'])

/** abas dentro de histórico → resultados */
const HISTORY_RESULTS_TABS = new Set(['casos', 'results-simulations', 'results-models', 'results-bed'])

function App() {
  const { language, toggleLanguage, t, setLanguage } = useLanguage();
  const { theme, toggleTheme, setThemeMode } = useTheme();
  const { simpleMode, devMode, applySettingsFromApi, setSimpleMode, setDevMode } = useAppUi();
  const { activeUserId, setActiveUserId } = useActiveUser();
  const [activeTab, setActiveTab] = useState('dashboard')
  const [wizardResetKey, setWizardResetKey] = useState(0)
  const [systemStatus, setSystemStatus] = useState(null)
  const [backendUnreachable, setBackendUnreachable] = useState(false)
  const [currentJob, setCurrentJob] = useState(null)
  const [isScrolled, setIsScrolled] = useState(false)
  const [showHelp, setShowHelp] = useState(false)
  const [showDocs, setShowDocs] = useState(false)
  const [showCredits, setShowCredits] = useState(false)
  const [footerInfoModal, setFooterInfoModal] = useState(null)
  const [showUserSwitcher, setShowUserSwitcher] = useState(false)
  const [expandedSections, setExpandedSections] = useState({})
  const [bootMeshViewerId, setBootMeshViewerId] = useState(null)
  const [templateEditPayload, setTemplateEditPayload] = useState(null)
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
        const tm = s.theme_mode;
        if (tm === 'dark' || tm === 'light' || tm === 'system') {
          setThemeMode(tm);
        }
        const lg = s.language;
        if (lg === 'pt' || lg === 'en') {
          setLanguage(lg);
        }
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
        if (footerInfoModal) setFooterInfoModal(null)
      }
    }

    window.addEventListener('scroll', handleScroll)
    window.addEventListener('keydown', handleKeyDown)
    return () => {
      window.removeEventListener('scroll', handleScroll)
      window.removeEventListener('keydown', handleKeyDown)
    }
  }, [showHelp, showDocs, showCredits, footerInfoModal])

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
    api.defaults.timeout = 120000;
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
    let tabNorm = tab === 'cfd' ? 'casos' : tab
    if (tabNorm === 'results' || tabNorm === 'history') {
      tabNorm = 'results-simulations'
    }
    const sectionByTab = {
      dashboard: 'dashboard',
      wizard: 'create',
      'mesh-viewer': 'dashboard',
      templates: 'templates',
      'templates-saved': 'templates',
      casos: 'history',
      database: 'database',
      comparisons: 'analysis',
      reports: 'analysis',
      jobs: 'history',
      'results-simulations': 'history',
      'results-models': 'history',
      'results-bed': 'history',
      profile: 'profile',
      settings: 'settings',
    }
    const sec = sectionByTab[tabNorm]
    setExpandedSections((prev) => {
      const next = {}
      Object.keys(prev).forEach((k) => {
        next[k] = false
      })
      if (sec && COLLAPSIBLE_NAV_SECTIONS.has(sec)) {
        next[sec] = true
      }
      if (HISTORY_RESULTS_TABS.has(tabNorm)) {
        next.history = true
        next['history-results'] = true
      }
      return next
    })
    setActiveTab(tabNorm)
  }

  const handleJobCreated = (job) => {
    setCurrentJob(job)
    navigateToTab('jobs')
  }

  const openMeshInViewer = useCallback(
    (meshId) => {
      if (!meshId) return
      setBootMeshViewerId(String(meshId))
      navigateToTab('mesh-viewer')
    },
    [navigateToTab]
  )

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
    setExpandedSections((prev) => {
      if (prev[section]) {
        const next = { ...prev, [section]: false }
        if (section === 'history') {
          next['history-results'] = false
        }
        return next
      }
      if (section === 'history-results') {
        return { ...prev, history: true, 'history-results': true }
      }
      const newState = {}
      Object.keys(prev).forEach((key) => {
        newState[key] = false
      })
      newState[section] = true
      if (section === 'history' && prev['history-results']) {
        newState['history-results'] = true
      }
      return newState
    })
  }

  return (
    <div className="app">
      <div className={`app-shell-top ${isScrolled ? 'app-shell-top-scrolled' : ''}`}>
        <div className="app-brand" aria-label={t('appCreativeTitle')}>
          <button
            type="button"
            className="logo-container logo-container-btn app-brand-btn"
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

        <header className={`header ${isScrolled ? 'header-scrolled' : ''}`}>
          <div className="header-content">
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
      </div>

      <div className="app-body">
        {/* sidebar (barra lateral) */}
        <aside className="sidebar">
          <nav className="sidebar-nav">
            <div className="nav-section">
              <button
                type="button"
                className={`nav-item nav-item-root nav-item-folder-face nav-item-dashboard ${activeTab === 'dashboard' ? 'active' : ''}`}
                onClick={() => navigateToTab('dashboard')}
              >
                <ThemeIcon light="analiseLight.png" dark="analiseLight.png" alt="dashboard" className="nav-icon" location="sidebar" />
                <span className="nav-label">{language === 'pt' ? 'Dashboard' : 'Dashboard'}</span>
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
                onClick={() => toggleSection('history')}
                role="button"
                tabIndex={0}
                aria-expanded={!!expandedSections.history}
                onKeyDown={(e) => {
                  if (e.key === 'Enter' || e.key === ' ') {
                    e.preventDefault();
                    toggleSection('history');
                  }
                }}
              >
                <h3 className="nav-section-title">
                  <ThemeIcon light="folderLight.png" dark="folderDark.png" alt="histórico" className="section-icon" location="sidebar" />
                  {language === 'pt' ? 'histórico' : 'history'}
                </h3>
                <span className="nav-folder-toggle" aria-hidden="true">
                  {expandedSections.history ? '−' : '+'}
                </span>
              </div>
              {expandedSections.history && (
                <div className="nav-subsection">
                  <button
                    className={`nav-item ${activeTab === 'jobs' ? 'active' : ''}`}
                    onClick={() => navigateToTab('jobs')}
                  >
                    <ThemeIcon light="jobLight.png" dark="jobLight.png" alt="jobs" className="nav-icon" />
                    <span className="nav-label">{t('jobs')} ({systemStatus?.jobs?.total || 0})</span>
                  </button>

                  <div className="nav-subsection-nested">
                    <div
                      className="nav-section-header"
                      onClick={() => toggleSection('history-results')}
                      role="button"
                      tabIndex={0}
                      aria-expanded={!!expandedSections['history-results']}
                      onKeyDown={(e) => {
                        if (e.key === 'Enter' || e.key === ' ') {
                          e.preventDefault();
                          toggleSection('history-results');
                        }
                      }}
                    >
                      <h3 className="nav-section-title">
                        <ThemeIcon light="folderLight.png" dark="folderDark.png" alt="resultados" className="section-icon" location="sidebar" />
                        {t('results')}
                      </h3>
                      <span className="nav-folder-toggle" aria-hidden="true">
                        {expandedSections['history-results'] ? '−' : '+'}
                      </span>
                    </div>
                    {expandedSections['history-results'] && (
                      <div className="nav-nested-subsection">
                        <button
                          className={`nav-item ${activeTab === 'casos' ? 'active' : ''}`}
                          onClick={() => navigateToTab('casos')}
                        >
                          <ThemeIcon light="folderLight.png" dark="folderLight.png" alt="casos cfd" className="nav-icon" />
                          <span className="nav-label">{t('casosCfd')}</span>
                        </button>
                        <button
                          className={`nav-item ${activeTab === 'results-simulations' ? 'active' : ''}`}
                          onClick={() => navigateToTab('results-simulations')}
                        >
                          <ThemeIcon light="cfd_gear_white.png" dark="cfd_gear_white.png" alt="simulações" className="nav-icon" />
                          <span className="nav-label">{language === 'pt' ? 'simulações' : 'simulations'}</span>
                        </button>
                        <button
                          className={`nav-item ${activeTab === 'results-models' ? 'active' : ''}`}
                          onClick={() => navigateToTab('results-models')}
                        >
                          <ThemeIcon light="modelLight-removebg-preview.png" dark="modelDark-removebg-preview.png" alt="modelos 3d" className="nav-icon" />
                          <span className="nav-label">{language === 'pt' ? 'modelos 3D' : '3D models'}</span>
                        </button>
                        <button
                          className={`nav-item ${activeTab === 'results-bed' ? 'active' : ''}`}
                          onClick={() => navigateToTab('results-bed')}
                        >
                          <ThemeIcon light="textEditorLight.png" dark="textEditorLight.png" alt="código bed" className="nav-icon" location="sidebar" />
                          <span className="nav-label">{language === 'pt' ? 'código .bed' : '.bed code'}</span>
                        </button>
                      </div>
                    )}
                  </div>
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
              <BedWizard
                key={wizardResetKey}
                onNavigateTab={navigateToTab}
                onOpenMeshViewer={openMeshInViewer}
              />
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

          {activeTab === 'results-simulations' && (
            <div className="tab-content">
              <ResultsSimulationsPage />
            </div>
          )}

          {activeTab === 'results-models' && (
            <div className="tab-content">
              <ResultsModels3DPage onOpenInViewer={openMeshInViewer} />
            </div>
          )}

          {activeTab === 'results-bed' && (
            <div className="tab-content">
              <ResultsBedCodePage />
            </div>
          )}

          {activeTab === 'comparisons' && (
            <div className="tab-content">
              <ComparisonPage />
            </div>
          )}

          {activeTab === 'templates' && (
            <div className="tab-content">
              <TemplateEditor
                initialEdit={templateEditPayload}
                onEditConsumed={() => setTemplateEditPayload(null)}
              />
            </div>
          )}

          {activeTab === 'templates-saved' && (
            <SavedTemplatesPage
              onEditTemplate={(payload) => {
                setTemplateEditPayload(payload)
                navigateToTab('templates')
              }}
            />
          )}

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
          <div className="footer-section footer-brand">
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
                ? 'Sistema de simulação de leitos empacotados com openfoam e blender'
                : 'Packed bed simulation system with openfoam and blender'}
            </p>
            <div className="footer-version">
              <span className="version-badge">v0.1.0</span>
              <span className="version-status">beta</span>
            </div>
          </div>

          <div className="footer-section footer-academic">
              <h4>{language === 'pt' ? 'Acadêmico' : 'Academic'}</h4>
            <div className="academic-logos">
              <a href="https://portal.pucrs.br/" target="_blank" rel="noopener noreferrer">
                <img src="/image/logo-light.png" alt="pucrs logo" className="academic-logo" />
              </a>
              <a href="https://vhlab.com.br/" target="_blank" rel="noopener noreferrer">
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
                <img src="/image/logo_lope.png" alt="lope laboratorio" className="academic-logo" />
              </a>
            </div>
          </div>

          <div className="footer-section footer-actions-column">
            <button type="button" className="footer-hub-btn" onClick={() => setShowCredits(true)}>
              {language === 'pt' ? 'Créditos' : 'Credits'}
            </button>
            <button type="button" className="footer-hub-btn" onClick={() => setFooterInfoModal('project')}>
              {language === 'pt' ? 'Projeto' : 'Project'}
            </button>
            <button type="button" className="footer-hub-btn" onClick={() => setFooterInfoModal('tech')}>
              {language === 'pt' ? 'Tecnologias' : 'Technologies'}
            </button>
            <button type="button" className="footer-hub-btn" onClick={() => setFooterInfoModal('database')}>
              {language === 'pt' ? 'Banco de dados' : 'Database'}
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
      <FooterInfoModal
        variant={footerInfoModal}
        show={Boolean(footerInfoModal)}
        onClose={() => setFooterInfoModal(null)}
        onOpenCredits={() => setShowCredits(true)}
        onOpenHelp={() => setShowHelp(true)}
        onOpenDocs={() => setShowDocs(true)}
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

