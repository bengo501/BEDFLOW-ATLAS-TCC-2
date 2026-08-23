import { useCallback, useEffect, useMemo, useState } from 'react';
import { useLanguage } from '../context/LanguageContext';
import { getProfile, patchProfile } from '../services/api';
import { useActiveUser } from '../context/UserContext';
import BackendConnectionError from './BackendConnectionError';
import ThemeIcon from './ThemeIcon';
import '../styles/CasosCFD.css';
import '../styles/MeshViewer3DPage.css';
import './SimulationHistory.css';
import './ProfilePage.css';

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

function isConnectionError(err) {
  if (!err) return false;
  const noResponse = !err.response && !!err.request;
  const network =
    err.code === 'ERR_NETWORK' ||
    err.code === 'ECONNABORTED' ||
    (typeof err.message === 'string' && err.message.toLowerCase().includes('network'));
  return noResponse || network;
}

function initialsFromName(name) {
  const p = (name || '').trim().split(/\s+/).filter(Boolean);
  if (p.length >= 2) return (p[0][0] + p[1][0]).toUpperCase();
  if (p.length === 1 && p[0].length) return p[0].slice(0, 2).toUpperCase();
  return '?';
}

function roleLabel(role, pt) {
  const m = {
    researcher: pt ? 'Pesquisador' : 'Researcher',
    engineer: pt ? 'Engenheiro' : 'Engineer',
    student: pt ? 'Estudante' : 'Student',
    other: pt ? 'Outro' : 'Other',
  };
  return m[role] || role;
}

export default function ProfilePage() {
  const { language, t, setLanguage } = useLanguage();
  const pt = language === 'pt';
  const { activeUserId } = useActiveUser();

  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [saving, setSaving] = useState(false);
  const [connectionError, setConnectionError] = useState(null);
  const [opError, setOpError] = useState(null);

  const [displayName, setDisplayName] = useState('');
  const [email, setEmail] = useState('');
  const [organization, setOrganization] = useState('');
  const [role, setRole] = useState('researcher');
  const [bio, setBio] = useState('');
  const [preferredLanguage, setPreferredLanguage] = useState('pt');
  const [updatedAt, setUpdatedAt] = useState('');

  const loadProfile = useCallback(async ({ silent = false } = {}) => {
    if (!silent) setLoading(true);
    else setRefreshing(true);
    setConnectionError(null);
    setOpError(null);
    try {
      const p = await getProfile();
      setDisplayName(p.display_name || '');
      setEmail(p.email || '');
      setOrganization(p.organization || '');
      setRole(p.role || 'researcher');
      setBio(p.bio || '');
      setPreferredLanguage(p.preferred_language === 'en' ? 'en' : 'pt');
      setUpdatedAt(p.updated_at || '');
    } catch (err) {
      console.error(err);
      if (isConnectionError(err)) {
        setConnectionError(t('backendConnectionError'));
      } else {
        setOpError(
          err.response?.data?.detail ||
            err.message ||
            (pt ? 'não foi possível carregar o perfil' : 'could not load profile')
        );
      }
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  }, [pt, t, activeUserId]);

  useEffect(() => {
    void loadProfile();
  }, [loadProfile]);

  const avatarLetter = useMemo(() => initialsFromName(displayName), [displayName]);

  const handleSave = async () => {
    setSaving(true);
    setOpError(null);
    setConnectionError(null);
    try {
      const p = await patchProfile({
        display_name: displayName,
        email,
        organization,
        role,
        bio: bio.trim() ? bio : '',
        preferred_language: preferredLanguage,
      });
      setUpdatedAt(p.updated_at || '');
      if (p.preferred_language === 'pt' || p.preferred_language === 'en') {
        setLanguage(p.preferred_language);
      }
    } catch (err) {
      console.error(err);
      if (isConnectionError(err)) {
        setConnectionError(t('backendConnectionError'));
      } else {
        setOpError(
          err.response?.data?.detail ||
            err.message ||
            (pt ? 'falha ao salvar' : 'save failed')
        );
      }
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="tab-content">
      <div className="profile-page">
        {connectionError && <BackendConnectionError message={connectionError} />}

        {opError && (
          <div className="profile-op-error" role="alert">
            {opError}
          </div>
        )}

        <header className="profile-page-header">
          <div className="profile-page-title">
            <ThemeIcon
              light="profileLight.png"
              dark="profileLight.png"
              alt=""
              className="profile-page-title-icon"
              location="page"
            />
            <h1 className="profile-page-heading">{pt ? 'Perfil' : 'Profile'}</h1>
          </div>
        </header>

        <section className="casos-panel ui-raised-surface" aria-label={pt ? 'Perfil' : 'Profile'}>
          <div className="casos-panel-toolbar">
            <button
              type="button"
              className="mesh-viewer-hub-btn mesh-viewer-hub-btn--compact"
              onClick={() => void loadProfile({ silent: true })}
              disabled={loading || refreshing}
              title={pt ? 'atualizar dados do perfil' : 'refresh profile data'}
            >
              <IconRefresh className="mesh-viewer-hub-btn__icon" aria-hidden />
              {refreshing ? '…' : pt ? 'atualizar' : 'refresh'}
            </button>
          </div>

          {loading ? (
            <p className="profile-status">{pt ? 'A carregar…' : 'Loading…'}</p>
          ) : (
            <>
              <div className="profile-avatar-row">
                <div className="profile-avatar-placeholder" aria-hidden="true">
                  {avatarLetter}
                </div>
                <div className="profile-avatar-meta">
                  <strong>{displayName || (pt ? 'Sem nome' : 'No name')}</strong>
                  <span>
                    {pt ? 'Papel:' : 'Role:'} {roleLabel(role, pt)}
                  </span>
                  {updatedAt && (
                    <span className="profile-updated">
                      {pt ? 'Última atualização:' : 'Last updated:'}{' '}
                      {new Date(updatedAt).toLocaleString(pt ? 'pt-PT' : 'en-GB')}
                    </span>
                  )}
                </div>
              </div>

              <div className="history-filter-grid profile-field-grid">
                <div className="profile-field">
                  <label htmlFor="profile-name">{pt ? 'Nome' : 'Name'}</label>
                  <input
                    id="profile-name"
                    type="text"
                    className="history-select"
                    value={displayName}
                    onChange={(e) => setDisplayName(e.target.value)}
                    maxLength={200}
                    autoComplete="name"
                  />
                </div>
                <div className="profile-field">
                  <label htmlFor="profile-email">{pt ? 'E-mail' : 'Email'}</label>
                  <input
                    id="profile-email"
                    type="email"
                    className="history-select"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    maxLength={255}
                    autoComplete="email"
                  />
                </div>
                <div className="profile-field">
                  <label htmlFor="profile-org">{pt ? 'Instituição' : 'Organization'}</label>
                  <input
                    id="profile-org"
                    type="text"
                    className="history-select"
                    value={organization}
                    onChange={(e) => setOrganization(e.target.value)}
                    maxLength={300}
                  />
                </div>
                <div className="profile-field">
                  <label htmlFor="profile-role">{pt ? 'Papel' : 'Role'}</label>
                  <select
                    id="profile-role"
                    className="history-select"
                    value={role}
                    onChange={(e) => setRole(e.target.value)}
                  >
                    <option value="researcher">{roleLabel('researcher', pt)}</option>
                    <option value="engineer">{roleLabel('engineer', pt)}</option>
                    <option value="student">{roleLabel('student', pt)}</option>
                    <option value="other">{roleLabel('other', pt)}</option>
                  </select>
                </div>
                <div className="profile-field">
                  <label htmlFor="profile-lang">{pt ? 'Idioma preferido (ui)' : 'Preferred language (ui)'}</label>
                  <select
                    id="profile-lang"
                    className="history-select"
                    value={preferredLanguage}
                    onChange={(e) => setPreferredLanguage(e.target.value)}
                  >
                    <option value="pt">Português</option>
                    <option value="en">English</option>
                  </select>
                </div>
                <div className="profile-field profile-field-bio">
                  <label htmlFor="profile-bio">{pt ? 'Biografia / notas' : 'Bio / notes'}</label>
                  <textarea
                    id="profile-bio"
                    className="history-select profile-bio-input"
                    rows={5}
                    value={bio}
                    onChange={(e) => setBio(e.target.value)}
                    placeholder={
                      pt
                        ? 'Área de pesquisa, contatos, observações…'
                        : 'Research area, contacts, notes…'
                    }
                  />
                </div>
              </div>

              <div className="caso-acoes profile-acoes">
                <button
                  type="button"
                  className="btn-mode-option"
                  onClick={() => void handleSave()}
                  disabled={saving}
                >
                  {saving ? (pt ? 'Salvando…' : 'Saving…') : pt ? 'Salvar alterações' : 'Save changes'}
                </button>
                <button
                  type="button"
                  className="btn-mode-option"
                  disabled
                  title={pt ? 'Não há autenticação nesta versão do aplicativo' : 'No authentication in this app version'}
                >
                  {pt ? 'Alterar senha' : 'Change password'}
                </button>
              </div>
            </>
          )}
        </section>
      </div>
    </div>
  );
}
