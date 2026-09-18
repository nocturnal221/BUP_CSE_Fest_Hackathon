import React, { useState, useEffect } from 'react';
import {
  Zap,
  BatteryCharging,
  Sun,
  AlertCircle,
  Play,
  RotateCcw,
  CheckCircle2,
  TrendingDown,
  Activity,
  FileText,
  Sliders,
  Plus,
  Trash2,
  Copy,
  ExternalLink
} from 'lucide-react';
import { PRESET_SCENARIOS } from './data/presets';

const API_BASE_URL = window.location.port === '5173' ? 'http://127.0.0.1:8000' : '';

export default function App() {
  // Preset selector
  const [selectedPresetId, setSelectedPresetId] = useState(PRESET_SCENARIOS[0].id);

  // Form states initialized with Preset 0
  const [scenarioId, setScenarioId] = useState(PRESET_SCENARIOS[0].id);
  const [operatorNotes, setOperatorNotes] = useState([...PRESET_SCENARIOS[0].operator_notes]);
  const [battery, setBattery] = useState({ ...PRESET_SCENARIOS[0].battery });
  const [hours, setHours] = useState([...PRESET_SCENARIOS[0].hours]);

  // UI / Execution states
  const [backendHealth, setBackendHealth] = useState({ status: 'checking', message: 'Connecting...' });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [result, setResult] = useState(null);
  const [copied, setCopied] = useState(false);

  // Check health of Django API on mount
  useEffect(() => {
    checkHealth();
  }, []);

  const checkHealth = async () => {
    try {
      const res = await fetch(`${API_BASE_URL}/health`);
      if (res.ok) {
        setBackendHealth({ status: 'online', message: 'API Online' });
      } else {
        setBackendHealth({ status: 'offline', message: `HTTP ${res.status}` });
      }
    } catch {
      setBackendHealth({ status: 'offline', message: 'Backend Offline' });
    }
  };

  const handleSelectPreset = (preset) => {
    setSelectedPresetId(preset.id);
    setScenarioId(preset.id);
    setOperatorNotes([...preset.operator_notes]);
    setBattery({ ...preset.battery });
    setHours([...preset.hours]);
    setError(null);
  };

  const handleNoteChange = (index, value) => {
    const updated = [...operatorNotes];
    updated[index] = value;
    setOperatorNotes(updated);
  };

  const handleAddNote = () => {
    if (operatorNotes.length < 3) {
      setOperatorNotes([...operatorNotes, '']);
    }
  };

  const handleRemoveNote = (index) => {
    if (operatorNotes.length > 1) {
      setOperatorNotes(operatorNotes.filter((_, i) => i !== index));
    }
  };

  const handleBatteryChange = (field, value) => {
    setBattery({
      ...battery,
      [field]: parseFloat(value) || 0.0
    });
  };

  const handleRunOptimization = async () => {
    setLoading(true);
    setError(null);

    const payload = {
      scenario_id: scenarioId,
      operator_notes: operatorNotes.filter((n) => n.trim().length > 0),
      hours: hours,
      battery: battery
    };

    try {
      const response = await fetch(`${API_BASE_URL}/optimize-energy`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(payload)
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || JSON.stringify(data));
      }

      setResult(data);
    } catch (err) {
      setError(err.message || 'An error occurred during optimization');
    } finally {
      setLoading(false);
    }
  };

  const handleCopyJson = () => {
    if (result) {
      navigator.clipboard.writeText(JSON.stringify(result, null, 2));
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  return (
    <div className="app-container">
      {/* Navigation Header */}
      <header className="app-header">
        <div className="brand-section">
          <div className="brand-logo-badge">
            <Zap size={22} />
          </div>
          <div>
            <div className="brand-title">
              Grid<span>Wise</span>
              <span className="brand-tag">v2.0 LP + LLM</span>
            </div>
            <p style={{ fontSize: '12px', color: 'var(--text-muted)' }}>
              Smart Campus Microgrid Energy Optimization System
            </p>
          </div>
        </div>

        <div className="header-status">
          <button
            onClick={checkHealth}
            className="health-badge"
            title="Click to re-check backend status"
            style={{ cursor: 'pointer', border: 'none' }}
          >
            <span className={`status-dot ${backendHealth.status === 'offline' ? 'offline' : ''}`} />
            <span>{backendHealth.message}</span>
          </button>
        </div>
      </header>

      {/* Preset Scenarios Bar */}
      <section className="presets-bar">
        <div className="presets-header">
          <div className="presets-title">
            <Sliders size={14} />
            <span>Benchmark Challenge Presets</span>
          </div>
          <span style={{ fontSize: '12px', color: 'var(--text-muted)' }}>
            1-Click Load Pre-Configured Campus Datasets
          </span>
        </div>
        <div className="preset-chips">
          {PRESET_SCENARIOS.map((preset) => (
            <button
              key={preset.id}
              onClick={() => handleSelectPreset(preset)}
              className={`preset-btn ${selectedPresetId === preset.id ? 'active' : ''}`}
            >
              <span>{preset.name}</span>
            </button>
          ))}
        </div>
      </section>

      {/* Main Workspace Layout */}
      <main className="workspace-grid">
        {/* Left Column: Input Form */}
        <section className="card">
          <div className="card-title">
            <div className="card-title-text">
              <Sliders size={18} color="var(--accent-blue)" />
              <span>Input Parameters</span>
            </div>
            <button
              onClick={() => handleSelectPreset(PRESET_SCENARIOS.find((p) => p.id === selectedPresetId))}
              className="btn-icon"
              title="Reset parameters"
            >
              <RotateCcw size={15} />
            </button>
          </div>

          {/* Scenario ID */}
          <div className="form-group">
            <label className="form-label">Scenario ID</label>
            <input
              type="text"
              value={scenarioId}
              onChange={(e) => setScenarioId(e.target.value)}
              className="form-input"
              placeholder="e.g. SAMPLE-01"
            />
          </div>

          {/* Operator Notes */}
          <div className="form-group">
            <div className="form-label">
              <span>Natural Language Operator Notes</span>
              <span style={{ fontSize: '11px', color: 'var(--text-muted)' }}>
                {operatorNotes.length}/3 notes
              </span>
            </div>
            <div className="notes-container">
              {operatorNotes.map((note, idx) => (
                <div key={idx} className="note-item">
                  <textarea
                    value={note}
                    onChange={(e) => handleNoteChange(idx, e.target.value)}
                    className="form-textarea"
                    placeholder={`Operator note ${idx + 1}...`}
                  />
                  {operatorNotes.length > 1 && (
                    <button
                      type="button"
                      onClick={() => handleRemoveNote(idx)}
                      className="btn-icon"
                      title="Remove note"
                    >
                      <Trash2 size={16} />
                    </button>
                  )}
                </div>
              ))}
            </div>

            {operatorNotes.length < 3 && (
              <button type="button" onClick={handleAddNote} className="add-note-btn">
                <Plus size={14} />
                <span>Add Note</span>
              </button>
            )}
          </div>

          {/* Battery Configuration */}
          <div className="form-group">
            <label className="form-label">Battery Storage Limits (BESS)</label>
            <div className="battery-grid">
              <div>
                <label style={{ fontSize: '11px', color: 'var(--text-muted)' }}>Capacity (kWh)</label>
                <input
                  type="number"
                  value={battery.capacity_kwh}
                  onChange={(e) => handleBatteryChange('capacity_kwh', e.target.value)}
                  className="form-input"
                  step="10"
                />
              </div>
              <div>
                <label style={{ fontSize: '11px', color: 'var(--text-muted)' }}>Initial Energy (kWh)</label>
                <input
                  type="number"
                  value={battery.initial_energy_kwh}
                  onChange={(e) => handleBatteryChange('initial_energy_kwh', e.target.value)}
                  className="form-input"
                  step="5"
                />
              </div>
              <div>
                <label style={{ fontSize: '11px', color: 'var(--text-muted)' }}>Min Reserve (kWh)</label>
                <input
                  type="number"
                  value={battery.minimum_energy_kwh}
                  onChange={(e) => handleBatteryChange('minimum_energy_kwh', e.target.value)}
                  className="form-input"
                  step="5"
                />
              </div>
              <div>
                <label style={{ fontSize: '11px', color: 'var(--text-muted)' }}>Max Rate (kW)</label>
                <input
                  type="number"
                  value={battery.max_charge_kwh_per_hour}
                  onChange={(e) => handleBatteryChange('max_charge_kwh_per_hour', e.target.value)}
                  className="form-input"
                  step="5"
                />
              </div>
            </div>
          </div>

          {/* Error Message */}
          {error && (
            <div
              style={{
                background: 'rgba(244, 63, 94, 0.1)',
                border: '1px solid rgba(244, 63, 94, 0.3)',
                padding: '12px 14px',
                borderRadius: 'var(--radius-md)',
                color: 'var(--accent-rose)',
                fontSize: '13px',
                display: 'flex',
                gap: '8px',
                alignItems: 'flex-start'
              }}
            >
              <AlertCircle size={16} style={{ flexShrink: 0, marginTop: '2px' }} />
              <div>{error}</div>
            </div>
          )}

          {/* CTA Run Optimization Button */}
          <button
            type="button"
            onClick={handleRunOptimization}
            disabled={loading}
            className="cta-button"
          >
            {loading ? (
              <>
                <Activity size={18} className="spinner" />
                <span>Solving Linear Optimization...</span>
              </>
            ) : (
              <>
                <Play size={18} fill="currentColor" />
                <span>Run Smart Optimization</span>
              </>
            )}
          </button>
        </section>

        {/* Right Column: Output Results */}
        <section style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
          {result ? (
            <>
              {/* KPI Summary Cards */}
              <div className="kpi-grid">
                <div className="kpi-card">
                  <div className="kpi-title">
                    <TrendingDown size={14} color="var(--accent-emerald)" />
                    <span>Total Cost</span>
                  </div>
                  <div className="kpi-value">
                    {result.total_cost_bdt.toLocaleString()}
                    <span className="kpi-unit">BDT</span>
                  </div>
                </div>

                <div className="kpi-card">
                  <div className="kpi-title">
                    <Zap size={14} color="var(--accent-blue)" />
                    <span>Grid Import</span>
                  </div>
                  <div className="kpi-value">
                    {result.total_grid_kwh.toLocaleString()}
                    <span className="kpi-unit">kWh</span>
                  </div>
                </div>

                <div className="kpi-card">
                  <div className="kpi-title">
                    <Activity size={14} color="var(--accent-amber)" />
                    <span>Peak Grid Draw</span>
                  </div>
                  <div className="kpi-value">
                    {result.peak_grid_kwh.toLocaleString()}
                    <span className="kpi-unit">kWh</span>
                  </div>
                </div>

                <div className="kpi-card">
                  <div className="kpi-title">
                    <BatteryCharging size={14} color="var(--accent-purple)" />
                    <span>Battery Status</span>
                  </div>
                  <div className="kpi-value" style={{ fontSize: '20px' }}>
                    {battery.capacity_kwh}
                    <span className="kpi-unit">kWh cap</span>
                  </div>
                </div>
              </div>

              {/* Plan Strategy Summary */}
              <div className="card" style={{ padding: '16px 20px' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <CheckCircle2 size={16} color="var(--accent-emerald)" />
                    <span style={{ fontSize: '14px', fontWeight: 600 }}>Optimization Strategy</span>
                  </div>
                  <button
                    onClick={handleCopyJson}
                    className="btn-icon"
                    title="Copy full JSON output"
                    style={{ width: 'auto', padding: '4px 10px', height: '28px', fontSize: '12px', gap: '6px' }}
                  >
                    <Copy size={13} />
                    <span>{copied ? 'Copied!' : 'JSON'}</span>
                  </button>
                </div>
                <p style={{ fontSize: '13px', color: 'var(--text-secondary)', marginTop: '6px' }}>
                  {result.plan_summary}
                </p>
              </div>

              {/* Directive Interpretations */}
              <div className="card">
                <div className="card-title">
                  <div className="card-title-text">
                    <FileText size={18} color="var(--accent-purple)" />
                    <span>Interpreted Directives & Guardrails</span>
                  </div>
                  <span style={{ fontSize: '12px', color: 'var(--text-muted)' }}>
                    {result.directive_interpretation.length} note(s) processed
                  </span>
                </div>

                <div className="directives-list">
                  {result.directive_interpretation.map((dir, idx) => (
                    <div key={idx} className="directive-card">
                      <div className="directive-header">
                        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                          <span style={{ fontSize: '12px', color: 'var(--text-muted)' }}>
                            Note #{dir.note_index}
                          </span>
                          <span className="directive-type-pill">{dir.directive_type}</span>
                        </div>
                        <span
                          className={`directive-applies-badge ${dir.applies ? 'active' : 'noop'}`}
                        >
                          {dir.applies ? 'Applies' : 'No-Op (Distractor)'}
                        </span>
                      </div>
                      <div className="directive-explanation">{dir.explanation}</div>
                      {dir.structured_adjustment && (
                        <div
                          style={{
                            fontSize: '11px',
                            fontFamily: 'var(--font-mono)',
                            color: 'var(--accent-blue)',
                            background: 'rgba(59, 130, 246, 0.08)',
                            padding: '4px 8px',
                            borderRadius: 'var(--radius-sm)',
                            alignSelf: 'flex-start'
                          }}
                        >
                          Adjustment: {JSON.stringify(dir.structured_adjustment)}
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              </div>

              {/* 24-Hour Dispatch Plan Table */}
              <div className="card">
                <div className="card-title">
                  <div className="card-title-text">
                    <Zap size={18} color="var(--accent-emerald)" />
                    <span>24-Hour Optimal Dispatch Plan</span>
                  </div>
                  <span style={{ fontSize: '12px', color: 'var(--text-muted)' }}>
                    Start-to-End Hourly Balance
                  </span>
                </div>

                <div className="schedule-table-container">
                  <table className="schedule-table">
                    <thead>
                      <tr>
                        <th>Hour</th>
                        <th>Grid Import</th>
                        <th>Solar Used</th>
                        <th>Battery Action</th>
                        <th>Battery Energy</th>
                      </tr>
                    </thead>
                    <tbody>
                      {result.hourly_plan.map((item) => {
                        const socPercent = Math.min(
                          100,
                          Math.max(0, (item.battery_energy_after_kwh / battery.capacity_kwh) * 100)
                        );
                        return (
                          <tr key={item.hour}>
                            <td>
                              <span className="hour-badge">
                                {item.hour.toString().padStart(2, '0')}:00
                              </span>
                            </td>
                            <td>
                              <span>{item.grid_kwh.toFixed(1)} kWh</span>
                            </td>
                            <td>
                              <span>{item.solar_used_kwh.toFixed(1)} kWh</span>
                            </td>
                            <td>
                              <span className={`battery-action-badge ${item.battery_action}`}>
                                {item.battery_action}
                                {item.battery_action !== 'idle' && ` (${item.battery_kwh.toFixed(1)} kWh)`}
                              </span>
                            </td>
                            <td>
                              <span>{item.battery_energy_after_kwh.toFixed(1)} kWh</span>
                              <div className="mini-bar-track" title={`${socPercent.toFixed(1)}% SoC`}>
                                <div
                                  className="mini-bar-fill"
                                  style={{
                                    width: `${socPercent}%`,
                                    background:
                                      socPercent < 25
                                        ? 'var(--accent-rose)'
                                        : socPercent > 75
                                        ? 'var(--accent-emerald)'
                                        : 'var(--accent-blue)'
                                  }}
                                />
                              </div>
                            </td>
                          </tr>
                        );
                      })}
                    </tbody>
                  </table>
                </div>
              </div>
            </>
          ) : (
            /* Empty State */
            <div
              className="card"
              style={{
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'center',
                justifyContent: 'center',
                minHeight: '380px',
                textAlign: 'center',
                gap: '14px',
                color: 'var(--text-muted)'
              }}
            >
              <div
                style={{
                  width: '64px',
                  height: '64px',
                  borderRadius: '50%',
                  background: 'rgba(59, 130, 246, 0.1)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  color: 'var(--accent-blue)'
                }}
              >
                <Zap size={30} />
              </div>
              <h3 style={{ fontSize: '18px', color: 'var(--text-primary)', fontWeight: 600 }}>
                Awaiting Optimization Run
              </h3>
              <p style={{ maxWidth: '380px', fontSize: '13px' }}>
                Select a benchmark challenge preset or enter custom notes and battery parameters on the left, then click <strong>Run Smart Optimization</strong>.
              </p>
            </div>
          )}
        </section>
      </main>
    </div>
  );
}
