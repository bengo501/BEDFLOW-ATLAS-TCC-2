import { useCallback, useEffect, useState } from 'react';
import { listUsers } from '../services/api';
import ThemeIcon from './ThemeIcon';
import './UserSwitcherModal.css';

function roleLabel(role, pt) {
  const m = {
    researcher: pt ? 'pesquisador' : 'researcher',
    engineer: pt ? 'engenheiro' : 'engineer',
    student: pt ? 'estudante' : 'student',
    other: pt ? 'outro' : 'other',
  };
  return m[role] || role || (pt ? 'sem papel' : 'no role');
}

function initialsFromName(name, fallback) {
  const p = (name || '').trim().split(/\s+/).filter(Boolean);
  if (p.length >= 2) return (p[0][0] + p[1][0]).toUpperCase();
  if (p.length === 1 && p[0].length) return p[0].slice(0, 2).toUpperCase();
  return (fallback || '?').toString().slice(0, 2).toUpperCase();
}

// modal que exibe a lista de utilizadores disponiveis e permite trocar o ativo
// usado a partir do botao redondo no header e tambem automaticamente na primeira
// abertura da aplicacao (controlado pelo App.jsx via flag em localStorage)
export default function UserSwitcherModal({ activeUserId, onSelect, onClose, language }) {
  const pt = language === 'pt';
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const loadUsers = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const rows = await listUsers();
      setUsers(Array.isArray(rows) ? rows : []);
    } catch (err) {
      console.error('user switcher modal:', err);
      setError(
        pt ? 'falha ao carregar utilizadores' : 'failed to load users'
      );
      setUsers([]);
    } finally {
      setLoading(false);
    }
  }, [pt]);

  useEffect(() => {
    loadUsers();
  }, [loadUsers]);

  useEffect(() => {
    const handleKey = (event) => {
      if (event.key === 'Escape') {
        onClose();
      }
    };
    window.addEventListener('keydown', handleKey);
    return () => window.removeEventListener('keydown', handleKey);
  }, [onClose]);

  const handleOverlayClick = (event) => {
    if (event.target === event.currentTarget) {
      onClose();
    }
  };

  return (
    <div
      className="user-switcher-overlay"
      onClick={handleOverlayClick}
      role="dialog"
      aria-modal="true"
      aria-label={pt ? 'selecionar utilizador ativo' : 'select active user'}
    >
      <div className="user-switcher-modal">
        <div className="user-switcher-header">
          <div>
            <h2>{pt ? 'selecionar utilizador ativo' : 'select active user'}</h2>
            <p className="user-switcher-subtitle">
              {pt
                ? 'cada utilizador tem os seus próprios leitos, simulações, relatórios e templates.'
                : 'each user has their own beds, simulations, reports and templates.'}
            </p>
          </div>
          <button
            type="button"
            className="user-switcher-close"
            onClick={onClose}
            aria-label={pt ? 'fechar' : 'close'}
          >
            ×
          </button>
        </div>

        <div className="user-switcher-body">
          {loading && (
            <p className="user-switcher-status">{pt ? 'a carregar…' : 'loading…'}</p>
          )}

          {!loading && error && (
            <p className="user-switcher-error" role="alert">{error}</p>
          )}

          {!loading && !error && users.length === 0 && (
            <p className="user-switcher-status">
              {pt ? 'nenhum utilizador disponível' : 'no users available'}
            </p>
          )}

          {!loading && !error && users.length > 0 && (
            <ul className="user-switcher-list">
              {users.map((u) => {
                const isActive = u.id === activeUserId;
                const name = (u.display_name || '').trim() || (pt ? 'sem nome' : 'no name');
                return (
                  <li key={u.id}>
                    <button
                      type="button"
                      className={isActive ? 'user-switcher-item active' : 'user-switcher-item'}
                      onClick={() => onSelect(u.id)}
                    >
                      <span className="user-switcher-avatar" aria-hidden="true">
                        {initialsFromName(u.display_name, u.id)}
                      </span>
                      <span className="user-switcher-meta">
                        <span className="user-switcher-name">{name}</span>
                        <span className="user-switcher-role">
                          {roleLabel(u.role, pt)} · id {u.id}
                        </span>
                      </span>
                      {isActive && (
                        <span className="user-switcher-active-pill">
                          <ThemeIcon
                            light="runLight.png"
                            dark="runLight.png"
                            alt=""
                            className="user-switcher-active-icon"
                            location="header"
                          />
                          {pt ? 'ativo' : 'active'}
                        </span>
                      )}
                    </button>
                  </li>
                );
              })}
            </ul>
          )}
        </div>

        <div className="user-switcher-footer">
          <button
            type="button"
            className="user-switcher-close-btn"
            onClick={onClose}
          >
            {pt ? 'fechar' : 'close'}
          </button>
        </div>
      </div>
    </div>
  );
}
