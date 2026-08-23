import React, { useState, useEffect, useCallback, useMemo } from 'react';
import { createPortal } from 'react-dom';
import { useLanguage } from '../context/LanguageContext';
import ThemeIcon from './ThemeIcon';
import BackendConnectionError from './BackendConnectionError';
import PaginationControls from './PaginationControls';
import { listSimulations } from '../services/api';
import './ComparisonPage.css';

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

function mapApiToCard(item, language) {
  const date = item.created_at
    ? new Date(item.created_at).toLocaleDateString(language === 'pt' ? 'pt-BR' : 'en-US')
    : '—';
  let pressure = language === 'pt' ? 'n/d' : 'n/a';
  if (item.pressure_drop != null && Number.isFinite(Number(item.pressure_drop))) {
    pressure = `${Number(item.pressure_drop).toFixed(1)} pa`;
  }
  return {
    id: item.id,
    name: item.name,
    description: item.description || '',
    status: item.status,
    date,
    mainResults: {
      pressure,
      efficiency: language === 'pt' ? 'n/d' : 'n/a'
    },
    // campos crus para uso no modal de comparacao
    raw: {
      id: item.id,
      name: item.name,
      description: item.description || '',
      status: item.status,
      created_at: item.created_at || null,
      bed_id: item.bed_id ?? null,
      regime: item.regime ?? null,
      inlet_velocity: item.inlet_velocity ?? null,
      fluid_density: item.fluid_density ?? null,
      fluid_viscosity: item.fluid_viscosity ?? null,
      solver: item.solver ?? null,
      max_iterations: item.max_iterations ?? null,
      convergence_criteria: item.convergence_criteria ?? null,
      mesh_cells_count: item.mesh_cells_count ?? null,
      mesh_quality: item.mesh_quality ?? null,
      pressure_drop: item.pressure_drop ?? null,
      average_velocity: item.average_velocity ?? null,
      reynolds_number: item.reynolds_number ?? null,
      execution_time: item.execution_time ?? null,
      case_directory: item.case_directory ?? null,
      progress: item.progress ?? null
    }
  };
}

function formatValue(value, unit = '', language = 'pt', fractionDigits = null) {
  if (value === null || value === undefined || value === '') {
    return language === 'pt' ? 'n/d' : 'n/a';
  }
  if (typeof value === 'number' && Number.isFinite(value)) {
    const formatted = fractionDigits != null ? value.toFixed(fractionDigits) : String(value);
    return unit ? `${formatted} ${unit}` : formatted;
  }
  if (typeof value === 'string') {
    return unit ? `${value} ${unit}` : value;
  }
  return String(value);
}

function areValuesDifferent(a, b) {
  if (a === null || a === undefined) a = null;
  if (b === null || b === undefined) b = null;
  if (a === null && b === null) return false;
  if (a === null || b === null) return true;
  if (typeof a === 'number' && typeof b === 'number') {
    return Math.abs(a - b) > 1e-9;
  }
  return String(a) !== String(b);
}

function ComparisonPage() {
  const { language, t } = useLanguage();
  const [searchTerm, setSearchTerm] = useState('');
  const [activeFilter, setActiveFilter] = useState('all');
  const [selectedSimulations, setSelectedSimulations] = useState([]);
  const [simulations, setSimulations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [loadError, setLoadError] = useState(null);
  const [showCompareModal, setShowCompareModal] = useState(false);
  const [compareItems, setCompareItems] = useState([]);
  const [page, setPage] = useState(1);
  const [limit, setLimit] = useState(4);

  const loadSimulations = useCallback(async () => {
    setLoading(true);
    setLoadError(null);
    try {
      const data = await listSimulations({ page: 1, per_page: 100 });
      const items = Array.isArray(data?.items) ? data.items : [];
      setSimulations(items.map((row) => mapApiToCard(row, language)));
    } catch (err) {
      console.error('comparison page:', err);
      if (isConnectionError(err)) {
        setLoadError(t('backendConnectionError'));
      } else {
        const detail = err.response?.data?.detail;
        setLoadError(
          typeof detail === 'string'
            ? detail
            : language === 'pt'
              ? 'erro ao carregar simulações'
              : 'failed to load simulations'
        );
      }
      setSimulations([]);
    } finally {
      setLoading(false);
    }
  }, [language, t]);

  useEffect(() => {
    loadSimulations();
  }, [loadSimulations]);

  const openCompareModal = useCallback(() => {
    if (selectedSimulations.length !== 2) return;
    const items = selectedSimulations
      .map((id) => simulations.find((sim) => sim.id === id))
      .filter(Boolean);
    if (items.length !== 2) return;
    setCompareItems(items);
    setShowCompareModal(true);
  }, [selectedSimulations, simulations]);

  const closeCompareModal = useCallback(() => {
    setShowCompareModal(false);
  }, []);

  useEffect(() => {
    if (!showCompareModal) return undefined;
    const handleKey = (event) => {
      if (event.key === 'Escape') {
        setShowCompareModal(false);
      }
    };
    window.addEventListener('keydown', handleKey);
    return () => window.removeEventListener('keydown', handleKey);
  }, [showCompareModal]);

  const handleSearchChange = (event) => {
    setPage(1);
    setSearchTerm(event.target.value);
  };

  const handleSimulationSelect = (id) => {
    setSelectedSimulations((prevSelected) => {
      if (prevSelected.includes(id)) {
        return prevSelected.filter((simId) => simId !== id);
      }
      if (prevSelected.length < 2) {
        return [...prevSelected, id];
      }
      return prevSelected;
    });
  };

  const filteredSimulations = simulations.filter((sim) => {
    const desc = (sim.description || '').toLowerCase();
    const matchesSearch =
      sim.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      desc.includes(searchTerm.toLowerCase());
    const matchesFilter = activeFilter === 'all' || sim.status === activeFilter;
    return matchesSearch && matchesFilter;
  });

  const totalFiltered = filteredSimulations.length;
  const totalPages = Math.max(1, Math.ceil(totalFiltered / limit) || 1);
  const paginatedSimulations = useMemo(() => {
    const start = (page - 1) * limit;
    return filteredSimulations.slice(start, start + limit);
  }, [filteredSimulations, page, limit]);

  useEffect(() => {
    if (page > totalPages) setPage(totalPages);
  }, [page, totalPages]);

  const getStatusText = (status) => {
    switch (status) {
      case 'completed':
        return language === 'pt' ? 'Concluída' : 'completed';
      case 'running':
        return language === 'pt' ? 'Em execução' : 'running';
      case 'pending':
        return language === 'pt' ? 'Pendente' : 'pending';
      case 'failed':
        return language === 'pt' ? 'Falhou' : 'failed';
      default:
        return status;
    }
  };

  const getStatusClass = (status) => {
    switch (status) {
      case 'completed':
        return 'status-completed';
      case 'running':
        return 'status-running';
      case 'pending':
        return 'status-pending';
      case 'failed':
        return 'status-failed';
      default:
        return '';
    }
  };

  const getFilterCount = (filter) => {
    if (filter === 'all') return simulations.length;
    return simulations.filter((sim) => sim.status === filter).length;
  };

  const filterOptions = [
    { key: 'all', labelPt: 'Todas', labelEn: 'All' },
    { key: 'completed', labelPt: 'Concluídas', labelEn: 'Completed' },
    { key: 'running', labelPt: 'Em execução', labelEn: 'Running' },
    { key: 'pending', labelPt: 'Pendentes', labelEn: 'Pending' },
    { key: 'failed', labelPt: 'Falharam', labelEn: 'Failed' },
  ];

  const emptyNoData = !loading && !loadError && simulations.length === 0;
  const emptyFiltered =
    !loading && !loadError && simulations.length > 0 && filteredSimulations.length === 0;

  return (
    <div className="comparison-page">
      <div className="comparison-header">
        <div className="comparison-title">
          <ThemeIcon light="compareLight.png" dark="compareDark.png" alt="comparisons" className="title-icon" />
          <h1>{language === 'pt' ? 'Comparações' : 'Comparisons'}</h1>
        </div>
        <p className="comparison-description">
          {language === 'pt'
            ? 'Compare simulações lado a lado e analise diferenças'
            : 'Compare simulations side by side and analyze differences'}
        </p>
      </div>

      <div className="comparison-page-toolbar">
        <button type="button" className="comparison-toolbar-btn" onClick={loadSimulations} disabled={loading}>
          <IconRefresh className="comparison-toolbar-btn__icon" />
          {language === 'pt' ? 'Atualizar' : 'Refresh'}
        </button>
        <button
          type="button"
          className="comparison-toolbar-btn comparison-toolbar-btn--primary"
          onClick={openCompareModal}
          disabled={selectedSimulations.length !== 2}
          title={
            selectedSimulations.length !== 2
              ? language === 'pt'
                ? 'Selecione duas simulações para comparar'
                : 'Select two simulations to compare'
              : ''
          }
        >
          {language === 'pt' ? 'Comparar' : 'Compare'}
          {selectedSimulations.length > 0 && (
            <span className="compare-count">({selectedSimulations.length}/2)</span>
          )}
        </button>
      </div>

      {loadError && <BackendConnectionError message={loadError} />}

      <div className="selection-section">
        <h2>{language === 'pt' ? 'Selecionar simulações para comparar' : 'Select simulations to compare'}</h2>
        <p className="selection-instruction">
          {language === 'pt' ? 'Selecione exatamente duas simulações concluídas' : 'Select exactly two completed simulations'}
        </p>

        {loading && (
          <p className="comparison-loading">{language === 'pt' ? 'A carregar…' : 'Loading…'}</p>
        )}

        {!loading && !loadError && (
          <>
            <div className="comparison-controls">
              <div className="search-bar">
                <ThemeIcon
                  light="triangle_white_outline.png"
                  dark="triangle_black_outline.png"
                  alt=""
                  className="search-icon"
                />
                <input
                  type="text"
                  placeholder={language === 'pt' ? 'Buscar simulações…' : 'Search simulations…'}
                  value={searchTerm}
                  onChange={handleSearchChange}
                />
              </div>
              <div className="filter-chips" role="group" aria-label={language === 'pt' ? 'filtro de estado' : 'status filter'}>
                {filterOptions.map((opt) => (
                  <button
                    key={opt.key}
                    type="button"
                    className={`filter-chip ${activeFilter === opt.key ? 'active' : ''}`}
                    onClick={() => {
                      setPage(1);
                      setActiveFilter(opt.key);
                    }}
                  >
                    {language === 'pt' ? opt.labelPt : opt.labelEn} ({getFilterCount(opt.key)})
                  </button>
                ))}
              </div>
            </div>

            {emptyNoData && (
              <div className="comparison-empty">
                <p>{language === 'pt' ? 'Nenhuma simulação encontrada' : 'No simulations found'}</p>
                <p className="comparison-empty-hint">
                  {language === 'pt'
                    ? 'Com o backend ativo, as simulações registadas aparecem aqui'
                    : 'With the backend running, registered simulations appear here'}
                </p>
              </div>
            )}

            {emptyFiltered && (
              <div className="comparison-empty">
                <p>{language === 'pt' ? 'Nenhum resultado para os filtros atuais' : 'No results for current filters'}</p>
              </div>
            )}

            {!emptyNoData && filteredSimulations.length > 0 && (
              <>
              <div className="simulation-cards-grid">
                {paginatedSimulations.map((sim) => (
                  <div
                    key={sim.id}
                    className={`simulation-card ${selectedSimulations.includes(sim.id) ? 'selected' : ''} ${
                      sim.status === 'completed' ? '' : 'disabled'
                    }`}
                    onClick={() => sim.status === 'completed' && handleSimulationSelect(sim.id)}
                    onKeyDown={(e) => {
                      if (e.key === 'Enter' || e.key === ' ') {
                        e.preventDefault();
                        if (sim.status === 'completed') handleSimulationSelect(sim.id);
                      }
                    }}
                    role="button"
                    tabIndex={sim.status === 'completed' ? 0 : -1}
                  >
                    <input
                      type="checkbox"
                      checked={selectedSimulations.includes(sim.id)}
                      onChange={() => sim.status === 'completed' && handleSimulationSelect(sim.id)}
                      disabled={
                        sim.status !== 'completed' ||
                        (selectedSimulations.length === 2 && !selectedSimulations.includes(sim.id))
                      }
                    />
                    <div className="card-content">
                      <span className={`simulation-status ${getStatusClass(sim.status)}`}>{getStatusText(sim.status)}</span>
                      <h3>{sim.name}</h3>
                      <p className="simulation-description">{sim.description}</p>
                      <div className="simulation-meta">
                        <ThemeIcon
                          light="job_monitor_clock_white.png"
                          dark="job_monitor_clock_white.png"
                          alt=""
                          className="comparison-date-icon"
                        />
                        <span>{sim.date}</span>
                      </div>
                      {sim.status === 'completed' && (
                        <div className="main-results">
                          <h4>{language === 'pt' ? 'Resultados principais' : 'Main results'}</h4>
                          <p>
                            <strong>{language === 'pt' ? 'Queda de pressão' : 'Pressure drop'}:</strong> {sim.mainResults.pressure}
                          </p>
                          <p>
                            <strong>{language === 'pt' ? 'Eficiência' : 'Efficiency'}:</strong> {sim.mainResults.efficiency}
                          </p>
                        </div>
                      )}
                    </div>
                  </div>
                ))}
              </div>
              <PaginationControls
                page={page}
                totalPages={totalPages}
                total={totalFiltered}
                limit={limit}
                loading={loading}
                onPageChange={setPage}
                onLimitChange={(value) => {
                  setPage(1);
                  setLimit(value);
                }}
                label={language === 'pt' ? 'Comparações' : 'Comparisons'}
                limitOptions={[4, 8, 12, 20]}
                pt={language === 'pt'}
              />
              </>
            )}
          </>
        )}
      </div>

      {showCompareModal &&
        compareItems.length === 2 &&
        createPortal(
          <CompareModal
            leftItem={compareItems[0]}
            rightItem={compareItems[1]}
            onClose={closeCompareModal}
            language={language}
            getStatusText={getStatusText}
            getStatusClass={getStatusClass}
          />,
          document.body,
        )}
    </div>
  );
}

function CompareModal({ leftItem, rightItem, onClose, language, getStatusText, getStatusClass }) {
  const left = leftItem.raw;
  const right = rightItem.raw;

  const formatDate = (iso) => {
    if (!iso) return language === 'pt' ? 'n/d' : 'n/a';
    try {
      return new Date(iso).toLocaleString(language === 'pt' ? 'pt-BR' : 'en-US');
    } catch (_e) {
      return iso;
    }
  };

  const rows = [
    {
      key: 'name',
      label: language === 'pt' ? 'nome' : 'name',
      leftRaw: left.name,
      rightRaw: right.name,
      leftDisplay: left.name,
      rightDisplay: right.name
    },
    {
      key: 'status',
      label: language === 'pt' ? 'estado' : 'status',
      leftRaw: left.status,
      rightRaw: right.status,
      leftDisplay: getStatusText(left.status),
      rightDisplay: getStatusText(right.status),
      leftClass: `status-pill ${getStatusClass(left.status)}`,
      rightClass: `status-pill ${getStatusClass(right.status)}`
    },
    {
      key: 'created_at',
      label: language === 'pt' ? 'criada em' : 'created at',
      leftRaw: left.created_at,
      rightRaw: right.created_at,
      leftDisplay: formatDate(left.created_at),
      rightDisplay: formatDate(right.created_at)
    },
    {
      key: 'regime',
      label: language === 'pt' ? 'regime' : 'regime',
      leftRaw: left.regime,
      rightRaw: right.regime,
      leftDisplay: formatValue(left.regime, '', language),
      rightDisplay: formatValue(right.regime, '', language)
    },
    {
      key: 'solver',
      label: 'solver',
      leftRaw: left.solver,
      rightRaw: right.solver,
      leftDisplay: formatValue(left.solver, '', language),
      rightDisplay: formatValue(right.solver, '', language)
    },
    {
      key: 'inlet_velocity',
      label: language === 'pt' ? 'velocidade de entrada' : 'inlet velocity',
      leftRaw: left.inlet_velocity,
      rightRaw: right.inlet_velocity,
      leftDisplay: formatValue(left.inlet_velocity, 'm/s', language, 3),
      rightDisplay: formatValue(right.inlet_velocity, 'm/s', language, 3)
    },
    {
      key: 'fluid_density',
      label: language === 'pt' ? 'densidade do fluido' : 'fluid density',
      leftRaw: left.fluid_density,
      rightRaw: right.fluid_density,
      leftDisplay: formatValue(left.fluid_density, 'kg/m³', language, 2),
      rightDisplay: formatValue(right.fluid_density, 'kg/m³', language, 2)
    },
    {
      key: 'fluid_viscosity',
      label: language === 'pt' ? 'viscosidade do fluido' : 'fluid viscosity',
      leftRaw: left.fluid_viscosity,
      rightRaw: right.fluid_viscosity,
      leftDisplay: formatValue(left.fluid_viscosity, 'pa·s', language, 6),
      rightDisplay: formatValue(right.fluid_viscosity, 'pa·s', language, 6)
    },
    {
      key: 'max_iterations',
      label: language === 'pt' ? 'iterações máximas' : 'max iterations',
      leftRaw: left.max_iterations,
      rightRaw: right.max_iterations,
      leftDisplay: formatValue(left.max_iterations, '', language),
      rightDisplay: formatValue(right.max_iterations, '', language)
    },
    {
      key: 'convergence_criteria',
      label: language === 'pt' ? 'critério de convergência' : 'convergence criteria',
      leftRaw: left.convergence_criteria,
      rightRaw: right.convergence_criteria,
      leftDisplay: formatValue(left.convergence_criteria, '', language),
      rightDisplay: formatValue(right.convergence_criteria, '', language)
    },
    {
      key: 'mesh_cells_count',
      label: language === 'pt' ? 'células da malha' : 'mesh cells',
      leftRaw: left.mesh_cells_count,
      rightRaw: right.mesh_cells_count,
      leftDisplay: formatValue(left.mesh_cells_count, '', language),
      rightDisplay: formatValue(right.mesh_cells_count, '', language)
    },
    {
      key: 'mesh_quality',
      label: language === 'pt' ? 'qualidade da malha' : 'mesh quality',
      leftRaw: left.mesh_quality,
      rightRaw: right.mesh_quality,
      leftDisplay: formatValue(left.mesh_quality, '', language, 3),
      rightDisplay: formatValue(right.mesh_quality, '', language, 3)
    },
    {
      key: 'pressure_drop',
      label: language === 'pt' ? 'queda de pressão' : 'pressure drop',
      leftRaw: left.pressure_drop,
      rightRaw: right.pressure_drop,
      leftDisplay: formatValue(left.pressure_drop, 'pa', language, 2),
      rightDisplay: formatValue(right.pressure_drop, 'pa', language, 2)
    },
    {
      key: 'average_velocity',
      label: language === 'pt' ? 'velocidade média' : 'average velocity',
      leftRaw: left.average_velocity,
      rightRaw: right.average_velocity,
      leftDisplay: formatValue(left.average_velocity, 'm/s', language, 3),
      rightDisplay: formatValue(right.average_velocity, 'm/s', language, 3)
    },
    {
      key: 'reynolds_number',
      label: language === 'pt' ? 'número de reynolds' : 'reynolds number',
      leftRaw: left.reynolds_number,
      rightRaw: right.reynolds_number,
      leftDisplay: formatValue(left.reynolds_number, '', language, 1),
      rightDisplay: formatValue(right.reynolds_number, '', language, 1)
    },
    {
      key: 'execution_time',
      label: language === 'pt' ? 'tempo de execução' : 'execution time',
      leftRaw: left.execution_time,
      rightRaw: right.execution_time,
      leftDisplay: formatValue(left.execution_time, 's', language, 1),
      rightDisplay: formatValue(right.execution_time, 's', language, 1)
    },
    {
      key: 'case_directory',
      label: language === 'pt' ? 'diretório do caso' : 'case directory',
      leftRaw: left.case_directory,
      rightRaw: right.case_directory,
      leftDisplay: formatValue(left.case_directory, '', language),
      rightDisplay: formatValue(right.case_directory, '', language)
    }
  ];

  const diffCount = rows.filter((r) => areValuesDifferent(r.leftRaw, r.rightRaw)).length;

  const handleOverlayClick = (event) => {
    if (event.target === event.currentTarget) {
      onClose();
    }
  };

  return (
    <div className="compare-modal-overlay" onClick={handleOverlayClick} role="dialog" aria-modal="true">
      <div className="compare-modal">
        <div className="compare-modal-header">
          <div>
            <h2>{language === 'pt' ? 'Comparar simulações' : 'Compare simulations'}</h2>
            <p className="compare-modal-subtitle">
              {language === 'pt'
                ? `${diffCount} ${diffCount === 1 ? 'diferença encontrada' : 'diferenças encontradas'}`
                : `${diffCount} ${diffCount === 1 ? 'difference found' : 'differences found'}`}
            </p>
          </div>
          <button
            type="button"
            className="compare-modal-close"
            onClick={onClose}
            aria-label={language === 'pt' ? 'fechar' : 'close'}
          >
            ×
          </button>
        </div>

        <div className="compare-modal-body">
          <table className="compare-table">
            <thead>
              <tr>
                <th className="compare-field-col">{language === 'pt' ? 'Campo' : 'Field'}</th>
                <th>
                  <div className="compare-sim-header">
                    <span className="compare-sim-label">{language === 'pt' ? 'Simulação A' : 'Simulation A'}</span>
                    <span className="compare-sim-name">{left.name}</span>
                  </div>
                </th>
                <th>
                  <div className="compare-sim-header">
                    <span className="compare-sim-label">{language === 'pt' ? 'Simulação B' : 'Simulation B'}</span>
                    <span className="compare-sim-name">{right.name}</span>
                  </div>
                </th>
              </tr>
            </thead>
            <tbody>
              {rows.map((row) => {
                const different = areValuesDifferent(row.leftRaw, row.rightRaw);
                return (
                  <tr key={row.key} className={different ? 'compare-row diff-row' : 'compare-row'}>
                    <td className="compare-field-col">{row.label}</td>
                    <td className={different ? 'diff-cell' : ''}>
                      <span className={row.leftClass || ''}>{row.leftDisplay}</span>
                    </td>
                    <td className={different ? 'diff-cell' : ''}>
                      <span className={row.rightClass || ''}>{row.rightDisplay}</span>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>

        <div className="compare-modal-footer">
          <button type="button" className="compare-modal-close-btn" onClick={onClose}>
            {language === 'pt' ? 'fechar' : 'close'}
          </button>
        </div>
      </div>
    </div>
  );
}

export default ComparisonPage;
