import { useCallback, useEffect, useRef, useState } from 'react';
import * as THREE from 'three';
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls.js';
import { STLLoader } from 'three/examples/jsm/loaders/STLLoader.js';
import { OBJLoader } from 'three/examples/jsm/loaders/OBJLoader.js';
import { PLYLoader } from 'three/examples/jsm/loaders/PLYLoader.js';
import { GLTFLoader } from 'three/examples/jsm/loaders/GLTFLoader.js';
import { listViewerMeshes, buildMeshStreamUrl, parseApiError } from '../services/api';
import '../styles/MeshViewer3DPage.css';

const LS_LAST_MESH = 'bedflow_last_mesh_id';

function countVertices(obj) {
  let n = 0;
  obj.traverse((ch) => {
    if (ch.isMesh && ch.geometry) {
      const g = ch.geometry;
      const pos = g.attributes && g.attributes.position;
      if (pos) n += pos.count;
    }
  });
  return n;
}

async function parseToObject3D(ext, buffer) {
  const e = ext.toLowerCase().replace(/^\./, '');
  if (e === 'stl') {
    const geom = new STLLoader().parse(buffer);
    geom.computeVertexNormals();
    const mat = new THREE.MeshStandardMaterial({
      color: 0x8b7355,
      metalness: 0.15,
      roughness: 0.65,
      side: THREE.DoubleSide,
    });
    return new THREE.Mesh(geom, mat);
  }
  if (e === 'obj') {
    const text = new TextDecoder('utf-8').decode(buffer);
    const obj = new OBJLoader().parse(text);
    obj.traverse((ch) => {
      if (ch.isMesh && ch.material) {
        const m = ch.material;
        if (!m.vertexColors) {
          ch.material = new THREE.MeshStandardMaterial({
            color: 0x7a9e9f,
            metalness: 0.12,
            roughness: 0.7,
            side: THREE.DoubleSide,
          });
        }
      }
    });
    return obj;
  }
  if (e === 'ply') {
    const geom = new PLYLoader().parse(buffer);
    geom.computeVertexNormals();
    const mat = new THREE.MeshStandardMaterial({
      color: 0x6b8e8f,
      metalness: 0.1,
      roughness: 0.75,
      side: THREE.DoubleSide,
    });
    return new THREE.Mesh(geom, mat);
  }
  if (e === 'gltf' || e === 'glb') {
    return new Promise((resolve, reject) => {
      const loader = new GLTFLoader();
      loader.parse(
        buffer,
        '',
        (gltf) => resolve(gltf.scene),
        (err) => reject(err || new Error('gltf parse'))
      );
    });
  }
  throw new Error(`formato nao suportado no viewer: ${e}`);
}

function fitCameraToObject(camera, controls, root, margin = 1.35) {
  const box = new THREE.Box3().setFromObject(root);
  if (box.isEmpty()) return;
  const size = box.getSize(new THREE.Vector3());
  const center = box.getCenter(new THREE.Vector3());
  const maxDim = Math.max(size.x, size.y, size.z) || 1;
  const dist = maxDim * margin;
  camera.near = Math.max(maxDim / 2000, 0.0001);
  camera.far = Math.max(maxDim * 200, 1000);
  camera.updateProjectionMatrix();
  camera.position.set(center.x + dist * 0.7, center.y + dist * 0.55, center.z + dist * 0.7);
  controls.target.copy(center);
  controls.update();
}

export default function MeshViewer3DPage({ language, initialMeshId, onConsumedBootId }) {
  const mountRef = useRef(null);
  const sceneRef = useRef(null);
  const cameraRef = useRef(null);
  const rendererRef = useRef(null);
  const controlsRef = useRef(null);
  const rootRef = useRef(null);
  const frameRef = useRef(null);

  const [meshes, setMeshes] = useState([]);
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
  const [meta, setMeta] = useState(null);

  const pt = language === 'pt';

  const refreshList = useCallback(async () => {
    setLoadingList(true);
    setErr(null);
    try {
      const data = await listViewerMeshes({ q: search.trim() || undefined, limit: 120 });
      setMeshes(data.meshes || []);
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

  const clearRoot = useCallback(() => {
    const scene = sceneRef.current;
    const old = rootRef.current;
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
  }, []);

  const loadSelectedMesh = useCallback(async () => {
    const id = selectedId.trim();
    if (!id) {
      setErr(pt ? 'escolha um modelo na lista' : 'pick a model from the list');
      return;
    }
    const info = meshes.find((m) => m.mesh_id === id);
    const ext = info ? info.format : '';
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
      const obj = await parseToObject3D(ext || 'stl', buffer);
      applyWireframe(obj, wireframe);

      const scene = sceneRef.current;
      if (scene) {
        scene.add(obj);
        rootRef.current = obj;
        const cam = cameraRef.current;
        const ctr = controlsRef.current;
        if (cam && ctr) fitCameraToObject(cam, ctr, obj);
        setMeta({
          filename: info?.filename || 'mesh',
          format: ext,
          vertices: countVertices(obj),
          bytes: buffer.byteLength,
          path: info?.relative_path || '',
        });
      }
      try {
        localStorage.setItem(LS_LAST_MESH, id);
      } catch (_) {}
    } catch (e) {
      setErr(e.message || String(e));
    } finally {
      setLoadingMesh(false);
    }
  }, [selectedId, meshes, wireframe, clearRoot, applyWireframe, pt]);

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
    };
  }, [clearRoot]);

  useEffect(() => {
    const root = rootRef.current;
    if (root) applyWireframe(root, wireframe);
  }, [wireframe, applyWireframe]);

  const resetCamera = () => {
    const root = rootRef.current;
    const cam = cameraRef.current;
    const ctr = controlsRef.current;
    if (root && cam && ctr) fitCameraToObject(cam, ctr, root);
  };

  const lastId = (() => {
    try {
      return localStorage.getItem(LS_LAST_MESH) || '';
    } catch {
      return '';
    }
  })();

  return (
    <div className="mesh-viewer-page">
      <div className="mesh-viewer-layout">
        <aside className="mesh-viewer-sidebar">
          <h2 className="mesh-viewer-title">
            {pt ? 'visualização 3d' : '3d visualization'}
          </h2>
          <p className="mesh-viewer-lead">
            {pt
              ? 'malhas servidas pela api a partir de local_data e pastas geradas.'
              : 'meshes served by the api from local_data and generated folders.'}
          </p>

          <label className="mesh-viewer-label">{pt ? 'pesquisar' : 'search'}</label>
          <div className="mesh-viewer-search-row">
            <input
              className="mesh-viewer-input"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder={pt ? 'filtro por nome…' : 'filter by name…'}
            />
            <button type="button" className="mesh-viewer-btn" onClick={() => refreshList()}>
              {loadingList ? '…' : pt ? 'atualizar' : 'refresh'}
            </button>
          </div>

          {lastId && (
            <p className="mesh-viewer-hint">
              {pt ? 'último id:' : 'last id:'} <code>{lastId}</code>
            </p>
          )}

          <div className="mesh-viewer-list-wrap">
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
                  </button>
                </li>
              ))}
            </ul>
          </div>

          {err && <div className="mesh-viewer-error">{err}</div>}

          <div className="mesh-viewer-actions">
            <button
              type="button"
              className="mesh-viewer-btn primary"
              disabled={loadingMesh || !selectedId}
              onClick={loadSelectedMesh}
            >
              {loadingMesh
                ? pt
                  ? 'a carregar…'
                  : 'loading…'
                : pt
                  ? 'carregar modelo'
                  : 'load model'}
            </button>
            <label className="mesh-viewer-check">
              <input
                type="checkbox"
                checked={wireframe}
                onChange={(e) => setWireframe(e.target.checked)}
              />
              {pt ? 'wireframe' : 'wireframe'}
            </label>
            <button type="button" className="mesh-viewer-btn" onClick={resetCamera}>
              {pt ? 'repor câmara' : 'reset camera'}
            </button>
          </div>

          {meta && (
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
            </dl>
          )}
        </aside>

        <div className="mesh-viewer-canvas-wrap" ref={mountRef} />
      </div>
    </div>
  );
}
