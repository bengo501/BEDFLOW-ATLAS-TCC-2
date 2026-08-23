import { useLanguage } from '../context/LanguageContext';
import '../styles/BackendConnectionError.css';

/**
 * aviso visual único para falha de rede / backend indisponível (mesmo padrão da página casos cfd).
 */
export default function BackendConnectionError({ message, className = '' }) {
  const { t } = useLanguage();
  const text = message ?? t('backendConnectionError');

  return (
    <div
      className={`backend-connection-error ${className}`.trim()}
      role="alert"
    >
      <strong>{t('errorLabel')}</strong> {text}
    </div>
  );
}
