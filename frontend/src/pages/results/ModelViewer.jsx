import { useEffect, useRef, useState } from 'react';
import * as THREE from 'three';
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls';
import { GLTFLoader } from 'three/examples/jsm/loaders/GLTFLoader';
import '../styles/ModelViewer.css';
import { fitCameraToObject } from '../utils/viewerCamera';
import { fetchMeshInfoFromFileUrl, loadMeshFromBuffer } from '../utils/meshLoadThree';

function ModelViewer({ modelPath, meshInfo = null }) {
  const mountRef = useRef(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const sceneRef = useRef(null);
  const cameraRef = useRef(null);
  const rendererRef = useRef(null);
  const controlsRef = useRef(null);
  const rootRef = useRef(null);

  useEffect(() => {
    if (!mountRef.current || !modelPath) return;

    const scene = new THREE.Scene();
    scene.background = new THREE.Color(0xf0f0f0);
    sceneRef.current = scene;

    const camera = new THREE.PerspectiveCamera(
      55,
      mountRef.current.clientWidth / Math.max(mountRef.current.clientHeight, 1),
      0.001,
      5000
    );
    camera.position.set(0.15, 0.15, 0.15);
    cameraRef.current = camera;

    const renderer = new THREE.WebGLRenderer({ antialias: true });
    renderer.setSize(mountRef.current.clientWidth, mountRef.current.clientHeight);
    renderer.shadowMap.enabled = true;
    mountRef.current.appendChild(renderer.domElement);
    rendererRef.current = renderer;

    const controls = new OrbitControls(camera, renderer.domElement);
    controls.enableDamping = true;
    controls.dampingFactor = 0.05;
    controlsRef.current = controls;

    scene.add(new THREE.AmbientLight(0xffffff, 0.55));
    const d1 = new THREE.DirectionalLight(0xffffff, 0.85);
    d1.position.set(3, 5, 4);
    scene.add(d1);

    const grid = new THREE.GridHelper(0.5, 10, 0x888888, 0xcccccc);
    scene.add(grid);

    let disposed = false;

    const loadModel = async () => {
      setLoading(true);
      setError(null);
      if (rootRef.current) {
        scene.remove(rootRef.current);
        rootRef.current = null;
      }

      const path = modelPath;
      const extMatch = /\.([a-z0-9]+)(\?|$)/i.exec(path || '');
      const ext = extMatch ? extMatch[1].toLowerCase() : 'stl';

      try {
        if (['stl', 'obj', 'ply', 'gltf', 'glb'].includes(ext)) {
          const res = await fetch(path);
          if (!res.ok) throw new Error(`http ${res.status}`);
          const buffer = await res.arrayBuffer();
          let info = meshInfo;
          if (!info?.geometry_mode) {
            const sidecar = await fetchMeshInfoFromFileUrl(path);
            if (sidecar) info = { ...info, ...sidecar };
          }
          const { object: root, viewHint } = await loadMeshFromBuffer(buffer, ext, info);
          if (disposed) return;
          root.traverse((child) => {
            if (child.isMesh) {
              child.castShadow = true;
              child.receiveShadow = true;
            }
          });
          scene.add(root);
          rootRef.current = root;
          if (cameraRef.current && controlsRef.current) {
            fitCameraToObject(cameraRef.current, controlsRef.current, root, 1.08, viewHint);
          }
          setLoading(false);
          return;
        }

        const glbPath = path.replace(/\.blend$/i, '.glb');
        const loader = new GLTFLoader();
        loader.load(
          glbPath,
          (gltf) => {
            if (disposed) return;
            const model = gltf.scene;
            scene.add(model);
            rootRef.current = model;
            if (cameraRef.current && controlsRef.current) {
              fitCameraToObject(cameraRef.current, controlsRef.current, model);
            }
            setLoading(false);
          },
          undefined,
          () => {
            if (disposed) return;
            createPlaceholderGeometry(scene);
            setLoading(false);
            setError('modelo glb não encontrado; mostrando representação simplificada');
          }
        );
      } catch (err) {
        if (disposed) return;
        console.error('erro ao carregar modelo:', err);
        createPlaceholderGeometry(scene);
        setLoading(false);
        setError(err.message || 'erro ao carregar modelo');
      }
    };

    loadModel();

    const animate = () => {
      if (disposed) return;
      requestAnimationFrame(animate);
      controls.update();
      renderer.render(scene, camera);
    };
    animate();

    const handleResize = () => {
      if (!mountRef.current) return;
      const w = mountRef.current.clientWidth;
      const h = mountRef.current.clientHeight;
      camera.aspect = w / Math.max(h, 1);
      camera.updateProjectionMatrix();
      renderer.setSize(w, h);
    };
    window.addEventListener('resize', handleResize);

    return () => {
      disposed = true;
      window.removeEventListener('resize', handleResize);
      if (mountRef.current && renderer.domElement.parentNode === mountRef.current) {
        mountRef.current.removeChild(renderer.domElement);
      }
      renderer.dispose();
      controls.dispose();
    };
  }, [modelPath, meshInfo]);

  const createPlaceholderGeometry = (scene) => {
    const cylinderGeometry = new THREE.CylinderGeometry(0.025, 0.025, 0.1, 32);
    const cylinderMaterial = new THREE.MeshStandardMaterial({
      color: 0x4caf50,
      transparent: true,
      opacity: 0.3,
      side: THREE.DoubleSide,
    });
    const cylinder = new THREE.Mesh(cylinderGeometry, cylinderMaterial);
    scene.add(cylinder);
    rootRef.current = cylinder;
  };

  return (
    <div className="model-viewer">
      <div className="viewer-header">
        <h4>visualização 3d do modelo</h4>
        <div className="viewer-controls-info">
          <span>arraste para rotacionar</span>
          <span>scroll para zoom</span>
        </div>
      </div>

      {loading && (
        <div className="viewer-loading">
          <div className="loading-spinner"></div>
          <p>carregando modelo 3d...</p>
        </div>
      )}

      {error && (
        <div className="viewer-error">
          <p>erro ao carregar modelo</p>
          <small>{error}</small>
        </div>
      )}

      <div ref={mountRef} className="viewer-canvas" />

      <div className="viewer-info">
        <div className="info-badge">
          <span className="info-label">arquivo:</span>
          <span className="info-value">{modelPath?.split('/').pop() || 'modelo'}</span>
        </div>
        {meshInfo?.geometry_mode ? (
          <div className="info-badge">
            <span className="info-label">geometria:</span>
            <span className="info-value">{meshInfo.geometry_mode}</span>
          </div>
        ) : null}
      </div>
    </div>
  );
}

export default ModelViewer;
