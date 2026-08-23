import { useState } from 'react';
import { useLanguage } from '../context/LanguageContext';
import { getDevInfoForTab } from '../config/devTabEndpoints';
import './DevModePanel.css';

export default function DevModePanel({ activeTab }) {
  const { language } = useLanguage();
  const pt = language === 'pt';
  const [open, setOpen] = useState(true);
  const info = getDevInfoForTab(activeTab);

  return (
    <div className={`dev-mode-panel ${open ? 'dev-mode-panel-open' : 'dev-mode-panel-collapsed'}`}>
      <button
        type="button"
        className="dev-mode-panel-toggle"
        onClick={() => setOpen((o) => !o)}
        aria-expanded={open}
      >
        {pt ? 'modo dev' : 'dev mode'} — {activeTab}
        <span className="dev-mode-chevron">{open ? (pt ? 'recolher' : 'collapse') : pt ? 'expandir' : 'expand'}</span>
      </button>
      {open && (
        <div className="dev-mode-panel-body">
          <div className="dev-mode-col">
            <h4 className="dev-mode-heading">{pt ? 'api (referência)' : 'api (reference)'}</h4>
            <ul>
              {info.api.map((line) => (
                <li key={line}>
                  <code>{line}</code>
                </li>
              ))}
            </ul>
          </div>
          <div className="dev-mode-col">
            <h4 className="dev-mode-heading">{pt ? 'persistência de dados' : 'data persistence'}</h4>
            <ul>
              {info.persistence.map((line) => (
                <li key={line}>{line}</li>
              ))}
            </ul>
          </div>
        </div>
      )}
    </div>
  );
}
