import { useEffect } from 'react';

const useKeyboardShortcuts = (handlers) => {
  useEffect(() => {
    const handleKeyPress = (event) => {
      // Ctrl/Cmd + Key shortcuts
      if ((event.ctrlKey || event.metaKey) && !event.shiftKey) {
        switch (event.key.toLowerCase()) {
          case 'n': // Nuevo Perfil
            event.preventDefault();
            handlers.newProfile?.();
            break;
          case 'o': // Abrir/Importar
            event.preventDefault();
            handlers.importConfig?.();
            break;
          case 's': // Guardar/Exportar
            event.preventDefault();
            handlers.exportConfig?.();
            break;
          case 'f': // Buscar Item
            event.preventDefault();
            handlers.searchItem?.();
            break;
          default:
            break;
        }
      }
      
      // Ctrl/Cmd + Shift + Key shortcuts
      if ((event.ctrlKey || event.metaKey) && event.shiftKey) {
        switch (event.key.toLowerCase()) {
          case 's': // Iniciar/Detener Escaneo
            event.preventDefault();
            handlers.toggleScan?.();
            break;
          case 'a': // Análisis de Mercado
            event.preventDefault();
            handlers.marketAnalysis?.();
            break;
          default:
            break;
        }
      }

      // Function key shortcuts
      switch (event.key) {
        case 'F5': // Actualizar Datos
          event.preventDefault();
          handlers.refresh?.();
          break;
        case 'F1': // Ayuda
          event.preventDefault();
          handlers.showHelp?.();
          break;
        default:
          break;
      }
    };

    window.addEventListener('keydown', handleKeyPress);
    return () => window.removeEventListener('keydown', handleKeyPress);
  }, [handlers]);
};

export default useKeyboardShortcuts;
