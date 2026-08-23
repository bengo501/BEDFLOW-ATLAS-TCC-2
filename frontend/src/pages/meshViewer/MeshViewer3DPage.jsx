import { useCallback, useEffect, useRef, useState } from 'react';
import * as THREE from 'three';
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls.js';
import {
  listViewerMeshes,
  buildMeshStreamUrl,
  parseApiError,
  launchMeshDesktopViewer,
  launchMeshBlenderViewer,
} from '../services/api';
import { useLanguage } from '../context/LanguageContext';
import ThemeIcon from './ThemeIcon';
import '../styles/MeshViewer3DPage.css';
import { fitCameraToObject } from '../utils/viewerCamera';
import { countVertices, loadMeshFromBuffer } from '../utils/meshLoadThree';

const LS_LAST_MESH = 'bedflow_last_mesh_id';

const DESKTOP_OPEN3D_FORMATS = new Set(['stl', 'obj', 'ply']);

function meshGeometrySummary(m, pt) {
  if (!m?.geometry_mode) return null;
  const parts = [m.geometry_mode];
  if (m.porosity_result != null && !Number.isNaN(Number(m.porosity_result))) {
    parts.push(`ε ${(Number(m.porosity_result) * 100).toFixed(1)}%`);
  }
  if (m.porosity_method) parts.push(m.porosity_method);
  if (m.slice_axis) {
    const t = m.slice_thickness != null ? `${Number(m.slice_thickness) * 1000}mm` : '';
    parts.push(`fatia ${m.slice_axis}${t ? ` ${t}` : ''}`);
  }
  if (m.internal_cylinder_mode) {
    parts.push(m.internal_cylinder_mode.replace(/_/g, ' '));
  }
  return parts.join(' · ');
}

function appendGeometryMetaRows(info, pt) {
  if (!info) return null;
  const rows = [];
  if (info.representation_dimension) {
    rows.push({
      dt: pt ? 'dimensão' : 'dimension',
      dd: info.representation_dimension,
    });
  }
  if (info.geometry_mode) {
    rows.push({ dt: pt ? 'geometria' : 'geometry', dd: info.geometry_mode });
  }
  const motor =
    info.generation_backend ||
    (info.modeling_profile === 'python' ? 'python_engine' : info.modeling_profile);
  if (motor) {
    rows.push({ dt: pt ? 'motor' : 'backend', dd: motor });
  }
  if (info.bed_particle_layout) {
    rows.push({
      dt: pt ? 'layout partículas' : 'particle layout',
      dd: info.bed_particle_layout,
    });
  }
  if (info.job_id) {
    rows.push({ dt: 'job id', dd: info.job_id });
  }
  if (info.content_hash) {
    rows.push({
      dt: pt ? 'hash' : 'hash',
      dd: `${String(info.content_hash).slice(0, 16)}…`,
    });
  }
  if (info.packing_random_seed != null) {
    rows.push({ dt: pt ? 'seed empacotamento' : 'packing seed', dd: String(info.packing_random_seed) });
  }
  if (info.particles_seed != null) {
    rows.push({ dt: pt ? 'seed partículas' : 'particles seed', dd: String(info.particles_seed) });
  }
  if (info.packing_method) {
    rows.push({ dt: pt ? 'empacotamento' : 'packing', dd: info.packing_method });
  }
  if (info.particle_kind) {
    rows.push({ dt: pt ? 'partícula' : 'particle', dd: info.particle_kind });
  }
  if (info.porosity_result != null && !Number.isNaN(Number(info.porosity_result))) {
    let dd = `${(Number(info.porosity_result) * 100).toFixed(2)}%`;
    if (info.porosity_target != null) {
      dd += pt
        ? ` (alvo ${(Number(info.porosity_target) * 100).toFixed(0)}%)`
        : ` (target ${(Number(info.porosity_target) * 100).toFixed(0)}%)`;
    }
    rows.push({ dt: pt ? 'porosidade' : 'porosity', dd });
  }
  if (info.porosity_method) {
    rows.push({ dt: pt ? 'método ε' : 'porosity method', dd: info.porosity_method });
  }
  if (info.internal_cylinder_mode) {
    rows.push({
      dt: pt ? 'cilindro interno' : 'internal cylinder',
      dd: info.internal_cylinder_mode,
    });
  }
  if (info.boolean_outer_shell || info.boolean_inner_core) {
    const bits = [
      info.boolean_outer_shell,
      info.boolean_inner_core,
      info.boolean_particle_tools,
    ].filter(Boolean);
    rows.push({
      dt: pt ? 'booleanas' : 'booleans',
      dd: bits.join(' · ') || '—',
    });
  }
  if (info.boolean_warnings) {
    rows.push({ dt: pt ? 'avisos' : 'warnings', dd: info.boolean_warnings });
  }
  if (info.slice_axis) {
    rows.push({
      dt: pt ? 'fatia' : 'slice',
      dd: `${info.slice_axis}${info.slice_thickness != null ? ` · ${info.slice_thickness} m` : ''}${
        info.slice_position != null ? ` · pos ${info.slice_position}` : ''
      }`,
    });
  }
  if (info.sidecar_json) {
    rows.push({ dt: 'sidecar', dd: info.sidecar_json });
  }
  return rows;
}

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

export default function MeshViewer3DPage({ language, initialMeshId, onConsumedBootId }) {
  const { t } = useLanguage();
  const mountRef = useRef(null);
  const sceneRef = useRef(null);
  const cameraRef = useRef(null);
  const rendererRef = useRef(null);
  const controlsRef = useRef(null);
  const rootRef = useRef(null);
  const frameRef = useRef(null);
  const axesRef = useRef(null);
  const gridRef = useRef(null);
  const boxHelperRef = useRef(null);

  const [meshes, setMeshes] = useState([]);
  const [meshesForBlender, setMeshesForBlender] = useState([]);
  const [search, setSearch] = useState('');
  const [selectedId, setSelectedId] = useState(() => {
    try {
      return localStorage.getItem(LS_LAST_MESH) || '';
    } catch {
      return '';
    }
  });
  const [loadingList, setLoadingList] = useState(false);
  const [loadingMesh, setLoadingMesh] = useState(false);
  const [err, setErr] = useState(null);
  const [wireframe, setWireframe] = useState(false);
  const [showAxes, setShowAxes] = useState(true);
  const [viewerLightBg, setViewerLightBg] = useState(false);
  const [showFloor, setShowFloor] = useState(true);
  const [showBoundingBox, setShowBoundingBox] = useState(false);
  const [meta, setMeta] = useState(null);
  const [toolNotice, setToolNotice] = useState(null);
  const [toolModal, setToolModal] = useState(null);
  const [toolModalPickId, setToolModalPickId] = useState('');
  const [toolModalBusy, setToolModalBusy] = useState(false);
  const toolNoticeTimerRef = useRef(null);

  const pt = language === 'pt';

  const refreshList = useCallback(async () => {
    setLoadingList(true);
    setErr(null);
    try {
      const data = await listViewerMeshes({ q: search.trim() || undefined, limit: 120 });
      const all = data.meshes || [];
      setMeshes(all.filter((m) => (m.format || '').toLowerCase() !== 'blend'));
      setMeshesForBlender(all);
    } catch (e) {
      setErr(parseApiError(e));
      setMeshes([]);
    } finally {
      setLoadingList(false);
    }
  }, [search]);

  useEffect(() => {
    refreshList();
  }, [refreshList]);

  useEffect(() => {
    if (initialMeshId) {
      setSelectedId(initialMeshId);
      try {
        localStorage.setItem(LS_LAST_MESH, initialMeshId);
      } catch (_) {}
      if (onConsumedBootId) onConsumedBootId();
    }
  }, [initialMeshId, onConsumedBootId]);

  const applyWireframe = useCallback((root, on) => {
    if (!root) return;
    root.traverse((ch) => {
      if (ch.isMesh && ch.material) {
        const mats = Array.isArray(ch.material) ? ch.material : [ch.material];
        mats.forEach((m) => {
          if (m && m.wireframe !== undefined) m.wireframe = on;
        });
      }
    });
  }, []);

  const clearBoundingBox = useCallback(() => {
    const scene = sceneRef.current;
    const helper = boxHelperRef.current;
    if (scene && helper) {
      scene.remove(helper);
      if (helper.dispose) helper.dispose();
      boxHelperRef.current = null;
    }
  }, []);

  const clearRoot = useCallback(() => {
    const scene = sceneRef.current;
    const old = rootRef.current;
    clearBoundingBox();
    if (scene && old) {
      scene.remove(old);
      old.traverse((ch) => {
        if (ch.isMesh) {
          if (ch.geometry) ch.geometry.dispose();
          if (ch.material) {
            const ms = Array.isArray(ch.material) ? ch.material : [ch.material];
            ms.forEach((m) => m && m.dispose && m.dispose());
          }
        }
      });
      rootRef.current = null;
    }
  }, [clearBoundingBox]);

  const syncBoundingBox = useCallback(
    (root) => {
      const scene = sceneRef.current;
      if (!scene || !root) return;
      clearBoundingBox();
      if (!showBoundingBox) return;
      const helper = new THREE.BoxHelper(root, 0x111111);
      scene.add(helper);
      boxHelperRef.current = helper;
    },
    [clearBoundingBox, showBoundingBox],
  );

  const loadSelectedMesh = useCallback(async () => {
    const id = selectedId.trim();
    if (!id) {
      setErr(pt ? 'escolha um modelo na lista' : 'pick a model from the list');
      return;
    }
    const info = meshes.find((m) => m.mesh_id === id);
    const ext = (info?.format || 'stl').toLowerCase();
    if (ext === 'blend') {
      setErr(pt ? '.blend nao carrega no three.js; use blender' : '.blend cannot load in three.js; use blender');
      return;
    }
    const url = buildMeshStreamUrl(id);
    if (!url) return;

    setLoadingMesh(true);
    setErr(null);
    clearRoot();

    try {
      const res = await fetch(url);
      if (!res.ok) throw new Error(`http ${res.status}`);
      const buffer = await res.arrayBuffer();
      const { object: obj, viewHint, vertices: verts } = await loadMeshFromBuffer(
        buffer,
        ext || 'stl',
        info
      );
      applyWireframe(obj, wireframe);

      const scene = sceneRef.current;
      if (scene) {
        scene.add(obj);
        rootRef.current = obj;
        syncBoundingBox(obj);
        const cam = cameraRef.current;
        const ctr = controlsRef.current;
        if (cam && ctr) fitCameraToObject(cam, ctr, obj, 1.05, viewHint);
        setMeta({
          filename: info?.filename || 'mesh',
          format: ext,
          vertices: countVertices(obj),
          bytes: buffer.byteLength,
          path: info?.relative_path || '',
          source_hint: info?.source_hint || '',
          recommended_modes: info?.recommended_modes || '',
          geometry_mode: info?.geometry_mode || '',
          generation_backend: info?.generation_backend || '',
          packing_method: info?.packing_method || '',
          particle_kind: info?.particle_kind || '',
          porosity_target: info?.porosity_target,
          porosity_result: info?.porosity_result,
          porosity_method: info?.porosity_method || '',
          slice_axis: info?.slice_axis || '',
          internal_cylinder_mode: info?.internal_cylinder_mode || '',
          boolean_outer_shell: info?.boolean_outer_shell || '',
          boolean_inner_core: info?.boolean_inner_core || '',
          boolean_particle_tools: info?.boolean_particle_tools || '',
          boolean_warnings: info?.boolean_warnings || '',
          slice_thickness: info?.slice_thickness,
          slice_position: info?.slice_position,
          sidecar_json: info?.sidecar_json || '',
          representation_dimension: info?.representation_dimension || '',
          bed_particle_layout: info?.bed_particle_layout || '',
          content_hash: info?.content_hash || '',
          job_id: info?.job_id || '',
          packing_random_seed: info?.packing_random_seed,
          particles_seed: info?.particles_seed,
          modeling_profile: info?.modeling_profile || '',
        });
      }
      try {
        localStorage.setItem(LS_LAST_MESH, id);
      } catch (_) {}
    } catch (e) {
      const msg = e?.message || String(e);
      setErr(
        pt
          ? `falha ao carregar ou interpretar o modelo (${ext || '?'}): ${msg}`
          : `failed to load or parse model (${ext || '?'}): ${msg}`,
      );
    } finally {
      setLoadingMesh(false);
    }
  }, [selectedId, meshes, wireframe, clearRoot, applyWireframe, syncBoundingBox, pt]);

  useEffect(() => {
    const id = selectedId.trim();
    if (!id) return;
    const info = meshes.find((m) => m.mesh_id === id);
    const fmt = (info?.format || 'stl').toLowerCase();
    if (fmt === 'blend') return;
    void loadSelectedMesh();
  }, [selectedId, meshes.length, loadSelectedMesh]);

  useEffect(() => {
    if (!mountRef.current) return;

    const scene = new THREE.Scene();
    scene.background = new THREE.Color(0x1a1d24);
    sceneRef.current = scene;

    const camera = new THREE.PerspectiveCamera(
      55,
      mountRef.current.clientWidth / mountRef.current.clientHeight,
      0.001,
      5000
    );
    camera.position.set(0.2, 0.15, 0.25);
    cameraRef.current = camera;

    const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: false });
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    renderer.setSize(mountRef.current.clientWidth, mountRef.current.clientHeight);
    renderer.shadowMap.enabled = true;
    mountRef.current.appendChild(renderer.domElement);
    rendererRef.current = renderer;

    const controls = new OrbitControls(camera, renderer.domElement);
    controls.enableDamping = true;
    controls.dampingFactor = 0.06;
    controlsRef.current = controls;

    scene.add(new THREE.AmbientLight(0xffffff, 0.45));
    const d1 = new THREE.DirectionalLight(0xffffff, 0.85);
    d1.position.set(3, 5, 4);
    scene.add(d1);
    const d2 = new THREE.DirectionalLight(0xb8c4ff, 0.35);
    d2.position.set(-4, -2, -3);
    scene.add(d2);

    const grid = new THREE.GridHelper(2, 20, 0x444a55, 0x2f343d);
    scene.add(grid);
    gridRef.current = grid;

    const axes = new THREE.AxesHelper(0.15);
    axes.visible = true;
    scene.add(axes);
    axesRef.current = axes;

    const animate = () => {
      frameRef.current = requestAnimationFrame(animate);
      controls.update();
      renderer.render(scene, camera);
    };
    animate();

    const onResize = () => {
      if (!mountRef.current) return;
      const w = mountRef.current.clientWidth;
      const h = mountRef.current.clientHeight;
      camera.aspect = w / h;
      camera.updateProjectionMatrix();
      renderer.setSize(w, h);
    };
    window.addEventListener('resize', onResize);

    return () => {
      window.removeEventListener('resize', onResize);
      cancelAnimationFrame(frameRef.current);
      clearRoot();
      renderer.dispose();
      controls.dispose();
      if (mountRef.current && renderer.domElement.parentNode === mountRef.current) {
        mountRef.current.removeChild(renderer.domElement);
      }
      sceneRef.current = null;
      cameraRef.current = null;
      rendererRef.current = null;
      controlsRef.current = null;
      axesRef.current = null;
      gridRef.current = null;
    };
  }, [clearRoot]);

  useEffect(() => {
    const scene = sceneRef.current;
    if (!scene) return;
    scene.background = new THREE.Color(viewerLightBg ? 0xf4f4f4 : 0x1a1d24);
    const grid = gridRef.current;
    if (grid) grid.visible = showFloor;
  }, [viewerLightBg, showFloor]);

  useEffect(() => {
    const ax = axesRef.current;
    if (ax) ax.visible = showAxes;
  }, [showAxes]);

  useEffect(() => {
    const root = rootRef.current;
    if (root) syncBoundingBox(root);
    else clearBoundingBox();
  }, [showBoundingBox, syncBoundingBox, clearBoundingBox]);

  useEffect(() => {
    const root = rootRef.current;
    if (root) applyWireframe(root, wireframe);
  }, [wireframe, applyWireframe]);

  const resetCamera = () => {
    const root = rootRef.current;
    const cam = cameraRef.current;
    const ctr = controlsRef.current;
    if (root && cam && ctr) {
      const hint = meta?.geometry_mode
        ? {
            geometry_mode: meta.geometry_mode,
            slice_axis: meta.slice_axis,
          }
        : null;
      fitCameraToObject(cam, ctr, root, 1.05, hint);
    }
  };

  const showToolNotice = (payload) => {
    setToolNotice(payload);
    window.clearTimeout(toolNoticeTimerRef.current);
    toolNoticeTimerRef.current = window.setTimeout(() => setToolNotice(null), 3200);
  };

  const openToolModal = (kind) => {
    const pool =
      kind === 'desktop'
        ? meshes.filter((m) => DESKTOP_OPEN3D_FORMATS.has((m.format || '').toLowerCase()))
        : meshesForBlender;
    const preferred =
      kind === 'desktop'
        ? selectedId && pool.some((m) => m.mesh_id === selectedId)
          ? selectedId
          : pool[0]?.mesh_id || ''
        : selectedId && pool.some((m) => m.mesh_id === selectedId)
          ? selectedId
          : meshesForBlender[0]?.mesh_id || '';
    setToolModalPickId(preferred);
    setToolModal(kind);
  };

  const closeToolModal = (force = false) => {
    if (toolModalBusy && !force) return;
    setToolModal(null);
    setToolModalPickId('');
  };

  const confirmToolModal = async () => {
    const id = toolModalPickId.trim();
    if (!id || !toolModal) return;
    setToolModalBusy(true);
    try {
      if (toolModal === 'desktop') {
        await launchMeshDesktopViewer(id);
        showToolNotice({ ok: true, text: t('meshLaunchDesktopOk') });
      } else {
        await launchMeshBlenderViewer(id);
        showToolNotice({ ok: true, text: t('meshLaunchBlenderOk') });
      }
      setSelectedId(id);
      try {
        localStorage.setItem(LS_LAST_MESH, id);
      } catch (_) {}
      closeToolModal(true);
    } catch (e) {
      const detail = parseApiError(e);
      showToolNotice({ ok: false, text: detail || t('meshLaunchFail') });
    } finally {
      setToolModalBusy(false);
    }
  };

  useEffect(() => {
    if (toolModal == null) return undefined;
    const onKey = (e) => {
      if (e.key === 'Escape') closeToolModal();
    };
    window.addEventListener('keydown', onKey);
    return () => window.removeEventListener('keydown', onKey);
  }, [toolModal, toolModalBusy]);

  useEffect(() => {
    return () => {
      window.clearTimeout(toolNoticeTimerRef.current);
    };
  }, []);

  const toolModalMeshes =
    toolModal === 'desktop'
      ? meshes.filter((m) => DESKTOP_OPEN3D_FORMATS.has((m.format || '').toLowerCase()))
      : meshesForBlender;

  const lastId = (() => {
    try {
      return localStorage.getItem(LS_LAST_MESH) || '';
    } catch {
      return '';
    }
  })();

  return (
    <div className="mesh-viewer-page">
      <header className="mesh-viewer-page-heading">
        <ThemeIcon
          light="modelLight-removebg-preview.png"
          dark="modelDark-removebg-preview.png"
          alt=""
          className="mesh-viewer-page-title-icon"
        />
        <h1 className="mesh-viewer-page-title">
          {pt ? 'Visualização 3D' : '3D visualization'}
        </h1>
      </header>
      <div className="mesh-viewer-layout">
        <aside
          className={`mesh-viewer-sidebar ui-raised-surface${meta ? ' mesh-viewer-sidebar--has-meta' : ''}`}
        >
          <section className="mesh-viewer-subpanel">
          <label className="mesh-viewer-label">{pt ? 'pesquisar' : 'search'}</label>
          <div className="mesh-viewer-search-row">
            <input
              className="mesh-viewer-input"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder={pt ? 'filtro por nome…' : 'filter by name…'}
            />
            <button
              type="button"
              className="mesh-viewer-hub-btn mesh-viewer-hub-btn--compact"
              onClick={() => void refreshList()}
              disabled={loadingList}
            >
              <IconRefresh className="mesh-viewer-hub-btn__icon" aria-hidden />
              {loadingList ? '…' : pt ? 'atualizar' : 'refresh'}
            </button>
          </div>

          {lastId ? (
            <p className="mesh-viewer-hint">
              {pt ? 'último id:' : 'last id:'} <code>{lastId}</code>
            </p>
          ) : null}
          </section>

          <section className="mesh-viewer-subpanel mesh-viewer-subpanel--list">
            <ul className="mesh-viewer-list">
              {meshes.map((m) => (
                <li key={m.mesh_id}>
                  <button
                    type="button"
                    className={
                      m.mesh_id === selectedId ? 'mesh-viewer-li active' : 'mesh-viewer-li'
                    }
                    onClick={() => setSelectedId(m.mesh_id)}
                  >
                    <span className="mesh-li-name">{m.filename}</span>
                    <span className="mesh-li-meta">
                      {m.format} · {Math.round(m.size_bytes / 1024)} kb
                    </span>
                    {meshGeometrySummary(m, pt) ? (
                      <span className="mesh-li-geom" title={meshGeometrySummary(m, pt)}>
                        {meshGeometrySummary(m, pt)}
                      </span>
                    ) : null}
                    {m.recommended_modes ? (
                      <span className="mesh-li-rec" title={m.recommended_modes}>
                        {m.recommended_modes}
                      </span>
                    ) : null}
                  </button>
                </li>
              ))}
            </ul>
          </section>

          {err ? <div className="mesh-viewer-error">{err}</div> : null}
          {!err && meta?.representation_dimension === '2d' ? (
            <p className="mesh-viewer-hint">
              {pt
                ? `modelo 2d: para ver discos circulares, rode a câmara para a normal da fatia (eixo ${meta.slice_axis || 'y'}). vista ao longo do leito pode parecer hastes finas.`
                : `2d model: orbit camera toward slice normal (axis ${meta.slice_axis || 'y'}) for circular discs.`}
            </p>
          ) : null}

          <section className="mesh-viewer-subpanel mesh-viewer-subpanel--controls">
            <div className="mesh-viewer-actions-primary">
              <button
                type="button"
                className="mesh-viewer-hub-btn"
                disabled={loadingMesh || !selectedId}
                onClick={loadSelectedMesh}
              >
                <ThemeIcon
                  light="modelLight-removebg-preview.png"
                  dark="modelDark-removebg-preview.png"
                  alt=""
                  className="mesh-viewer-hub-btn__icon mesh-viewer-hub-btn__icon--img"
                  location="page"
                />
                {loadingMesh
                  ? pt
                    ? 'a carregar…'
                    : 'loading…'
                  : pt
                    ? 'carregar modelo'
                    : 'load model'}
              </button>
              <button type="button" className="mesh-viewer-hub-btn" onClick={resetCamera}>
                <IconRefresh className="mesh-viewer-hub-btn__icon" aria-hidden />
                {pt ? 'repor câmara' : 'reset camera'}
              </button>
            </div>
            <div className="mesh-viewer-actions-checks" role="group" aria-label={pt ? 'opcoes do visualizador' : 'viewer options'}>
              <label className="mesh-viewer-check">
                <input
                  type="checkbox"
                  checked={wireframe}
                  onChange={(e) => setWireframe(e.target.checked)}
                />
                {pt ? 'wireframe' : 'wireframe'}
              </label>
              <label className="mesh-viewer-check">
                <input
                  type="checkbox"
                  checked={showAxes}
                  onChange={(e) => setShowAxes(e.target.checked)}
                />
                {t('meshAxes')}
              </label>
              <label className="mesh-viewer-check">
                <input
                  type="checkbox"
                  checked={viewerLightBg}
                  onChange={(e) => setViewerLightBg(e.target.checked)}
                />
                {pt ? 'fundo claro' : 'light background'}
              </label>
              <label className="mesh-viewer-check">
                <input
                  type="checkbox"
                  checked={showFloor}
                  onChange={(e) => setShowFloor(e.target.checked)}
                />
                {pt ? 'chão' : 'floor'}
              </label>
              <label className="mesh-viewer-check">
                <input
                  type="checkbox"
                  checked={showBoundingBox}
                  onChange={(e) => setShowBoundingBox(e.target.checked)}
                />
                {pt ? 'bounding box' : 'bounding box'}
              </label>
            </div>
          </section>

          <section className="mesh-viewer-subpanel mesh-viewer-subpanel--tools">
            <button
              type="button"
              className="mesh-viewer-btn mesh-viewer-btn-block"
              disabled={loadingList || meshes.length === 0}
              onClick={() => openToolModal('desktop')}
            >
              {t('meshDesktopViewerBtn')}
            </button>
            <button
              type="button"
              className="mesh-viewer-btn mesh-viewer-btn-block"
              disabled={loadingList || meshesForBlender.length === 0}
              onClick={() => openToolModal('blender')}
            >
              {t('meshBlenderViewerBtn')}
            </button>
          {toolNotice ? (
            <p
              className={
                toolNotice.ok
                  ? 'mesh-viewer-tool-notice'
                  : 'mesh-viewer-tool-notice mesh-viewer-tool-notice--err'
              }
            >
              {toolNotice.text}
            </p>
          ) : null}
          </section>

          {meta ? (
            <section className="mesh-viewer-subpanel mesh-viewer-subpanel--meta" aria-live="polite">
            <h3 className="mesh-viewer-meta-title">{pt ? 'dados do modelo' : 'model data'}</h3>
            <dl className="mesh-viewer-dl">
              <dt>{pt ? 'ficheiro' : 'file'}</dt>
              <dd>{meta.filename}</dd>
              <dt>formato</dt>
              <dd>{meta.format}</dd>
              <dt>{pt ? 'vértices (aprox.)' : 'vertices (approx.)'}</dt>
              <dd>{meta.vertices}</dd>
              <dt>{pt ? 'tamanho' : 'size'}</dt>
              <dd>{meta.bytes} bytes</dd>
              {meta.path && (
                <>
                  <dt>path</dt>
                  <dd className="mesh-dd-path">{meta.path}</dd>
                </>
              )}
              {meta.source_hint ? (
                <>
                  <dt>{pt ? 'origem (heuristica)' : 'source (heuristic)'}</dt>
                  <dd>{meta.source_hint}</dd>
                </>
              ) : null}
              {meta.recommended_modes ? (
                <>
                  <dt>{pt ? 'recomendado' : 'recommended'}</dt>
                  <dd>{meta.recommended_modes}</dd>
                </>
              ) : null}
              {appendGeometryMetaRows(meta, pt)?.map((row) => (
                <span key={row.dt}>
                  <dt>{row.dt}</dt>
                  <dd>{row.dd}</dd>
                </span>
              ))}
            </dl>
            </section>
          ) : null}
        </aside>

        <section className="mesh-viewer-canvas-panel ui-raised-surface">
          <div className="mesh-viewer-canvas-wrap" ref={mountRef} />
        </section>
      </div>

      {toolModal ? (
        <div
          className="mesh-viewer-modal-overlay"
          role="dialog"
          aria-modal="true"
          aria-labelledby="mesh-tool-modal-title"
          onClick={() => closeToolModal()}
        >
          <div className="mesh-viewer-modal ui-raised-surface" onClick={(e) => e.stopPropagation()}>
            <header className="mesh-viewer-modal-header">
              <h2 id="mesh-tool-modal-title" className="mesh-viewer-modal-title">
                {toolModal === 'desktop'
                  ? t('meshPickModelTitleDesktop')
                  : t('meshPickModelTitleBlender')}
              </h2>
              <button
                type="button"
                className="mesh-viewer-modal-close"
                onClick={() => closeToolModal()}
                aria-label={pt ? 'fechar' : 'close'}
              >
                ×
              </button>
            </header>
            <p className="mesh-viewer-modal-hint">{t('meshPickModelHint')}</p>
            {toolModalMeshes.length === 0 ? (
              <p className="mesh-viewer-modal-empty">
                {toolModal === 'desktop'
                  ? t('meshPickModelEmptyDesktop')
                  : t('meshPickModelEmptyBlender')}
              </p>
            ) : (
              <ul className="mesh-viewer-modal-list">
                {toolModalMeshes.map((m) => (
                  <li key={m.mesh_id}>
                    <button
                      type="button"
                      className={
                        m.mesh_id === toolModalPickId
                          ? 'mesh-viewer-modal-li active'
                          : 'mesh-viewer-modal-li'
                      }
                      onClick={() => setToolModalPickId(m.mesh_id)}
                    >
                      <span className="mesh-li-name">{m.filename}</span>
                      <span className="mesh-li-meta">
                        {m.format} · {Math.round(m.size_bytes / 1024)} kb
                      </span>
                    </button>
                  </li>
                ))}
              </ul>
            )}
            <footer className="mesh-viewer-modal-footer">
              <button
                type="button"
                className="mesh-viewer-btn"
                onClick={() => closeToolModal()}
                disabled={toolModalBusy}
              >
                {t('meshPickModelCancel')}
              </button>
              <button
                type="button"
                className="mesh-viewer-btn primary"
                disabled={toolModalBusy || !toolModalPickId.trim() || toolModalMeshes.length === 0}
                onClick={() => void confirmToolModal()}
              >
                {toolModalBusy ? '…' : t('meshPickModelOpen')}
              </button>
            </footer>
          </div>
        </div>
      ) : null}
    </div>
  );
}
