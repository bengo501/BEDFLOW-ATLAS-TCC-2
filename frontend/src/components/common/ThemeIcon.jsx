import { useTheme } from '../context/ThemeContext';

/**
 * componente para exibir ícones que mudam conforme o tema e localização
 * 
 * lógica:
 * - header, footer, sidebar: sempre versão light/white
 * - outras páginas: light mode = dark icons, dark mode = light icons
 * 
 * uso:
 * <ThemeIcon light="blenderLight.png" dark="blenderDark.png" alt="blender" />
 * <ThemeIcon light="blenderLight.png" dark="blenderDark.png" alt="blender" location="header" />
 */
export default function ThemeIcon({ light, dark, alt, className = '', style = {}, location = 'page' }) {
  const { theme } = useTheme();
  
  let iconSrc;
  
  // header, footer, sidebar sempre usam versão light/white
  if (location === 'header' || location === 'footer' || location === 'sidebar') {
    iconSrc = `/image/${light}`;
  } else {
    // outras páginas seguem tema invertido
    iconSrc = theme === 'light' ? `/image/${dark}` : `/image/${light}`;
  }
  
  return (
    <img 
      src={iconSrc} 
      alt={alt} 
      className={className}
      style={style}
    />
  );
}
