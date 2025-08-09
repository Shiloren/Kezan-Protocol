import React, { useState } from 'react';
import PropTypes from 'prop-types';

const MenuItem = ({ label, children, isOpen, onClick }) => {
  return (
    <div className="relative">
      <button
        onClick={onClick}
        className={`px-4 py-2 text-warm-white hover:bg-graphite-soft ${
          isOpen ? 'bg-graphite-soft' : ''
        }`}
      >
        {label}
      </button>
      {isOpen && children && (
        <div className="absolute left-0 top-full mt-1 w-48 bg-black-mineral border border-steel-gray/20 rounded-md shadow-lg z-50">
          {children}
        </div>
      )}
    </div>
  );
};

const MenuBar = () => {
  const [openMenu, setOpenMenu] = useState(null);

  const handleMenuClick = (menuName) => {
    setOpenMenu(openMenu === menuName ? null : menuName);
  };

  const closeMenus = () => {
    setOpenMenu(null);
  };

  const menuItems = {
    file: [
      { label: 'Nuevo Perfil', action: () => {} },
      { label: 'Importar Configuración', action: () => {} },
      { label: 'Exportar Configuración', action: () => {} },
      { label: 'Cerrar', action: () => {} }
    ],
    scan: [
      { label: 'Iniciar Escaneo', action: () => {} },
      { label: 'Detener Escaneo', action: () => {} },
      { label: 'Configurar Intervalos', action: () => {} }
    ],
    items: [
      { label: 'Añadir Item', action: () => {} },
      { label: 'Gestionar Items', action: () => {} },
      { label: 'Ver Historial', action: () => {} },
      { label: 'Exportar Datos', action: () => {} }
    ],
    analysis: [
      { label: 'Ver Tendencias', action: () => {} },
      { label: 'Análisis de Mercado', action: () => {} },
      { label: 'Predicciones', action: () => {} }
    ],
    settings: [
      { label: 'Preferencias', action: () => {} },
      { label: 'API de Blizzard', action: () => {} },
      { label: 'Configuración de IA', action: () => {} },
      { label: 'Notificaciones', action: () => {} }
    ]
  };

  const renderMenuItem = (item) => (
    <button
      key={item.label}
      onClick={() => {
        item.action();
        closeMenus();
      }}
      className="w-full text-left px-4 py-2 text-warm-white hover:bg-graphite-soft transition-colors"
    >
      {item.label}
    </button>
  );

  return (
    <div className="relative">
      <div className="flex bg-black-mineral border-b border-steel-gray/20">
        <MenuItem
          label="Archivo"
          isOpen={openMenu === 'file'}
          onClick={() => handleMenuClick('file')}
        >
          <div className="py-1">
            {menuItems.file.map(renderMenuItem)}
          </div>
        </MenuItem>

        <MenuItem
          label="Escaneo"
          isOpen={openMenu === 'scan'}
          onClick={() => handleMenuClick('scan')}
        >
          <div className="py-1">
            {menuItems.scan.map(renderMenuItem)}
          </div>
        </MenuItem>

        <MenuItem
          label="Items"
          isOpen={openMenu === 'items'}
          onClick={() => handleMenuClick('items')}
        >
          <div className="py-1">
            {menuItems.items.map(renderMenuItem)}
          </div>
        </MenuItem>

        <MenuItem
          label="Análisis"
          isOpen={openMenu === 'analysis'}
          onClick={() => handleMenuClick('analysis')}
        >
          <div className="py-1">
            {menuItems.analysis.map(renderMenuItem)}
          </div>
        </MenuItem>

        <MenuItem
          label="Configuración"
          isOpen={openMenu === 'settings'}
          onClick={() => handleMenuClick('settings')}
        >
          <div className="py-1">
            {menuItems.settings.map(renderMenuItem)}
          </div>
        </MenuItem>
      </div>

      {/* Overlay para cerrar menús cuando se hace clic fuera */}
      {openMenu && (
        <div
          className="fixed inset-0 z-40"
          onClick={closeMenus}
        />
      )}
    </div>
  );
};

MenuItem.propTypes = {
  label: PropTypes.string.isRequired,
  children: PropTypes.node,
  isOpen: PropTypes.bool,
  onClick: PropTypes.func
};

export default MenuBar;
