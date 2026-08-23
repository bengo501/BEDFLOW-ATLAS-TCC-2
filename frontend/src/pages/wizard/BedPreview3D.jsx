import { useEffect, useRef } from 'react';
import * as THREE from 'three';
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls';
import '../styles/BedPreview3D.css';

const BedPreview3D = ({ params }) => {
  const mountRef = useRef(null);
  const sceneRef = useRef(null);
  const rendererRef = useRef(null);
  const controlsRef = useRef(null);

  useEffect(() => {
    if (!mountRef.current || !params) return;

    // criar cena
    const scene = new THREE.Scene();
    scene.background = new THREE.Color(0xf0f0f0);
    sceneRef.current = scene;

    // criar camera
    const camera = new THREE.PerspectiveCamera(
      75,
      mountRef.current.clientWidth / mountRef.current.clientHeight,
      0.001,
      1000
    );
    camera.position.set(0.15, 0.15, 0.15);
    camera.lookAt(0, 0, 0);

    // criar renderer
    const renderer = new THREE.WebGLRenderer({ antialias: true });
    renderer.setSize(mountRef.current.clientWidth, mountRef.current.clientHeight);
    renderer.shadowMap.enabled = true;
    renderer.shadowMap.type = THREE.PCFSoftShadowMap;
    mountRef.current.appendChild(renderer.domElement);
    rendererRef.current = renderer;

    // adicionar controles
    const controls = new OrbitControls(camera, renderer.domElement);
    controls.enableDamping = true;
    controls.dampingFactor = 0.05;
    controls.minDistance = 0.05;
    controls.maxDistance = 1;
    controlsRef.current = controls;

    // adicionar luzes
    const ambientLight = new THREE.AmbientLight(0xffffff, 0.6);
    scene.add(ambientLight);

    const directionalLight = new THREE.DirectionalLight(0xffffff, 0.8);
    directionalLight.position.set(0.2, 0.3, 0.2);
    directionalLight.castShadow = true;
    directionalLight.shadow.mapSize.width = 2048;
    directionalLight.shadow.mapSize.height = 2048;
    scene.add(directionalLight);

    const directionalLight2 = new THREE.DirectionalLight(0xffffff, 0.4);
    directionalLight2.position.set(-0.2, -0.1, -0.2);
    scene.add(directionalLight2);

    // adicionar grid
    const gridHelper = new THREE.GridHelper(0.5, 10, 0x888888, 0xcccccc);
    gridHelper.position.y = 0;
    scene.add(gridHelper);

    // criar geometria do leito
    createBedGeometry(scene, params);

    // animation loop
    const animate = () => {
      requestAnimationFrame(animate);
      controls.update();
      renderer.render(scene, camera);
    };
    animate();

    // handle resize
    const handleResize = () => {
      if (!mountRef.current) return;
      const width = mountRef.current.clientWidth;
      const height = mountRef.current.clientHeight;
      camera.aspect = width / height;
      camera.updateProjectionMatrix();
      renderer.setSize(width, height);
    };
    window.addEventListener('resize', handleResize);

    // cleanup
    return () => {
      window.removeEventListener('resize', handleResize);
      if (mountRef.current && renderer.domElement) {
        mountRef.current.removeChild(renderer.domElement);
      }
      renderer.dispose();
      controls.dispose();
    };
  }, [params]);

  const createBedGeometry = (scene, params) => {
    if (!params.bed || !params.particles) return;

    // converter strings para números
    const bedDiameter = parseFloat(params.bed.diameter);
    const bedHeight = parseFloat(params.bed.height);
    const bedWallThickness = parseFloat(params.bed.wall_thickness);
    const particleDiameter = parseFloat(params.particles.diameter);
    const particleCount = parseInt(params.particles.count);

    // criar cilindro externo (parede)
    const outerRadius = bedDiameter / 2;
    const innerRadius = outerRadius - bedWallThickness;
    
    const cylinderGeometry = new THREE.CylinderGeometry(
      outerRadius,
      outerRadius,
      bedHeight,
      32,
      1,
      true
    );
    const cylinderMaterial = new THREE.MeshStandardMaterial({
      color: 0x4CAF50,
      transparent: true,
      opacity: 0.3,
      side: THREE.DoubleSide,
      metalness: 0.3,
      roughness: 0.7
    });
    const cylinder = new THREE.Mesh(cylinderGeometry, cylinderMaterial);
    cylinder.castShadow = true;
    cylinder.receiveShadow = true;
    scene.add(cylinder);

    // criar linha de contorno do cilindro
    const edgesGeometry = new THREE.EdgesGeometry(cylinderGeometry);
    const edgesMaterial = new THREE.LineBasicMaterial({ color: 0x2E7D32, linewidth: 2 });
    const edges = new THREE.LineSegments(edgesGeometry, edgesMaterial);
    cylinder.add(edges);

    // criar tampas se existirem
    if (params.lids) {
      const topType = params.lids.top_type;
      const bottomType = params.lids.bottom_type;

      // tampa inferior
      if (bottomType !== 'none') {
        const bottomLidGeometry = bottomType === 'hemispherical'
          ? new THREE.SphereGeometry(outerRadius, 32, 16, 0, Math.PI * 2, 0, Math.PI / 2)
          : new THREE.CylinderGeometry(outerRadius, outerRadius, 0.001, 32);
        
        const lidMaterial = new THREE.MeshStandardMaterial({
          color: 0x2196F3,
          transparent: true,
          opacity: 0.5,
          metalness: 0.5,
          roughness: 0.5
        });
        
        const bottomLid = new THREE.Mesh(bottomLidGeometry, lidMaterial);
        bottomLid.position.y = bottomType === 'hemispherical' ? -bedHeight / 2 : -bedHeight / 2;
        bottomLid.castShadow = true;
        bottomLid.receiveShadow = true;
        scene.add(bottomLid);
      }

      // tampa superior
      if (topType !== 'none') {
        const topLidGeometry = topType === 'hemispherical'
          ? new THREE.SphereGeometry(outerRadius, 32, 16, 0, Math.PI * 2, Math.PI / 2, Math.PI / 2)
          : new THREE.CylinderGeometry(outerRadius, outerRadius, 0.001, 32);
        
        const lidMaterial = new THREE.MeshStandardMaterial({
          color: 0x2196F3,
          transparent: true,
          opacity: 0.5,
          metalness: 0.5,
          roughness: 0.5
        });
        
        const topLid = new THREE.Mesh(topLidGeometry, lidMaterial);
        topLid.position.y = topType === 'hemispherical' ? bedHeight / 2 : bedHeight / 2;
        topLid.castShadow = true;
        topLid.receiveShadow = true;
        scene.add(topLid);
      }
    }

    // criar partículas (sample representativo para performance)
    const maxParticlesToShow = Math.min(particleCount, 200); // limitar para performance
    const particleRadius = particleDiameter / 2;
    
    let particleGeometry;
    switch (params.particles.kind) {
      case 'cube':
        particleGeometry = new THREE.BoxGeometry(particleDiameter, particleDiameter, particleDiameter);
        break;
      case 'cylinder':
        particleGeometry = new THREE.CylinderGeometry(
          particleRadius, 
          particleRadius, 
          particleDiameter, 
          16
        );
        break;
      case 'sphere':
      default:
        particleGeometry = new THREE.SphereGeometry(particleRadius, 16, 16);
        break;
    }

    const particleMaterial = new THREE.MeshStandardMaterial({
      color: 0xFF9800,
      metalness: 0.2,
      roughness: 0.8
    });

    // criar instanced mesh para melhor performance
    const instancedMesh = new THREE.InstancedMesh(
      particleGeometry,
      particleMaterial,
      maxParticlesToShow
    );
    instancedMesh.castShadow = true;
    instancedMesh.receiveShadow = true;

    // distribuir partículas de forma aleatória dentro do cilindro
    const matrix = new THREE.Matrix4();
    const position = new THREE.Vector3();
    const quaternion = new THREE.Quaternion();
    const scale = new THREE.Vector3(1, 1, 1);

    for (let i = 0; i < maxParticlesToShow; i++) {
      // gerar posição aleatória dentro do cilindro
      const angle = Math.random() * Math.PI * 2;
      const radius = Math.random() * (innerRadius - particleRadius);
      const x = Math.cos(angle) * radius;
      const z = Math.sin(angle) * radius;
      const y = (Math.random() - 0.5) * (bedHeight - particleDiameter * 2);

      position.set(x, y, z);

      // rotação aleatória
      quaternion.setFromEuler(
        new THREE.Euler(
          Math.random() * Math.PI,
          Math.random() * Math.PI,
          Math.random() * Math.PI
        )
      );

      matrix.compose(position, quaternion, scale);
      instancedMesh.setMatrixAt(i, matrix);
    }

    instancedMesh.instanceMatrix.needsUpdate = true;
    scene.add(instancedMesh);

    // adicionar texto informativo
    if (particleCount > maxParticlesToShow) {
      console.log(`preview: mostrando ${maxParticlesToShow} de ${particleCount} partículas`);
    }
  };

  return (
    <div className="bed-preview-3d">
      <div className="preview-header">
        <h3>preview 3D do leito</h3>
        <div className="preview-controls-info">
          <span>🖱️ arraste para rotacionar</span>
          <span>🔍 scroll para zoom</span>
        </div>
      </div>
      <div ref={mountRef} className="preview-canvas" />
      {params && (
        <div className="preview-info">
          <div className="info-item">
            <span className="info-label">geometria:</span>
            <span className="info-value">
              ø {params.bed?.diameter}m × {params.bed?.height}m
            </span>
          </div>
          <div className="info-item">
            <span className="info-label">partículas:</span>
            <span className="info-value">
              {params.particles?.count} {params.particles?.kind} 
              (ø {params.particles?.diameter}m)
            </span>
          </div>
          <div className="info-item">
            <span className="info-label">material:</span>
            <span className="info-value">
              {params.bed?.material} ({params.particles?.density} kg/m³)
            </span>
          </div>
        </div>
      )}
    </div>
  );
};

export default BedPreview3D;

