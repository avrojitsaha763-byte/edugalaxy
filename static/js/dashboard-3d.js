/* dashboard-3d.js - EduGalaxy Orbital Command Hub — Full God Mode */
(function() {
    'use strict';

    if (typeof THREE === 'undefined') {
        window.addEventListener('load', () => initHub());
        return;
    }
    initHub();

    function initHub() {
        const canvas = document.getElementById('orbital-canvas');
        if (!canvas) return;

        const scene = new THREE.Scene();
        const camera = new THREE.PerspectiveCamera(55, window.innerWidth / window.innerHeight, 0.1, 8000);
        camera.position.set(0, 80, 900);
        camera.lookAt(0, 0, 0);

        const renderer = new THREE.WebGLRenderer({ canvas, antialias: true, alpha: false });
        renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
        renderer.setSize(window.innerWidth, window.innerHeight);
        renderer.setClearColor(0x000510, 1);

        // ── DEEP SPACE BACKGROUND ──
        const bgScene = new THREE.Scene();
        const bgCam = new THREE.OrthographicCamera(-1, 1, 1, -1, 0, 1);
        const bgMat = new THREE.ShaderMaterial({
            uniforms: { time: { value: 0 } },
            vertexShader: `void main() { gl_Position = vec4(position, 1.0); }`,
            fragmentShader: `
                uniform float time;
                void main() {
                    vec2 uv = gl_FragCoord.xy / vec2(1920.0, 1080.0);
                    vec3 col = vec3(0.0, 0.02, 0.05);
                    float n1 = sin(uv.x*2.0 + time*0.05) * cos(uv.y*3.0 + time*0.04);
                    col += vec3(0.0, 0.06, 0.12) * smoothstep(0.3, 0.7, n1*0.5+0.5);
                    float n2 = cos(uv.x*4.0 - time*0.03) * sin(uv.y*2.0 + time*0.06);
                    col += vec3(0.04, 0.0, 0.08) * smoothstep(0.4, 0.7, n2*0.5+0.5);
                    gl_FragColor = vec4(col, 1.0);
                }
            `,
            depthWrite: false
        });
        bgScene.add(new THREE.Mesh(new THREE.PlaneGeometry(2, 2), bgMat));

        // ── STARS ──
        const starGeo = new THREE.BufferGeometry();
        const sp = new Float32Array(8000 * 3);
        for (let i = 0; i < 8000; i++) {
            sp[i*3]     = (Math.random() - 0.5) * 8000;
            sp[i*3 + 1] = (Math.random() - 0.5) * 8000;
            sp[i*3 + 2] = (Math.random() - 0.5) * 6000 - 500;
        }
        starGeo.setAttribute('position', new THREE.BufferAttribute(sp, 3));
        const stars = new THREE.Points(starGeo, new THREE.PointsMaterial({ color: 0x88ccff, size: 1.4, transparent: true, opacity: 0.7 }));
        scene.add(stars);

        // ── PRIMARY PLANET (large, right side) ──
        const planetGeo = new THREE.SphereGeometry(320, 64, 64);
        const planetMat = new THREE.MeshPhongMaterial({
            color: 0x0a2a4a,
            emissive: 0x001122,
            specular: 0x003366,
            shininess: 60
        });
        const planet = new THREE.Mesh(planetGeo, planetMat);
        planet.position.set(500, -150, -200);
        scene.add(planet);

        // Planet continent-like surface detail (simple noise overlay sphere)
        const surfaceGeo = new THREE.SphereGeometry(322, 32, 32);
        const surfaceMat = new THREE.MeshBasicMaterial({
            color: 0x00f3ff,
            transparent: true,
            opacity: 0.04,
            wireframe: true
        });
        const surface = new THREE.Mesh(surfaceGeo, surfaceMat);
        planet.add(surface);

        // ── ATMOSPHERE GLOW ──
        const atmGeo = new THREE.SphereGeometry(365, 64, 64);
        const atmMat = new THREE.MeshBasicMaterial({
            color: 0x00f3ff,
            transparent: true,
            opacity: 0.06,
            side: THREE.BackSide,
            blending: THREE.AdditiveBlending
        });
        planet.add(new THREE.Mesh(atmGeo, atmMat));

        // ── RING SYSTEM ──
        const ringGeo = new THREE.RingGeometry(380, 500, 128);
        const ringMat = new THREE.MeshBasicMaterial({
            color: 0x004466,
            transparent: true,
            opacity: 0.35,
            side: THREE.DoubleSide
        });
        const ring = new THREE.Mesh(ringGeo, ringMat);
        ring.rotation.x = Math.PI / 2.5;
        planet.add(ring);

        // ── RING GLOW ──
        const ringGlowGeo = new THREE.RingGeometry(381, 499, 128);
        const ringGlowMat = new THREE.MeshBasicMaterial({
            color: 0x00f3ff,
            transparent: true,
            opacity: 0.08,
            side: THREE.DoubleSide,
            blending: THREE.AdditiveBlending
        });
        const ringGlow = new THREE.Mesh(ringGlowGeo, ringGlowMat);
        ringGlow.rotation.x = Math.PI / 2.5;
        planet.add(ringGlow);

        // ── MOON / SATELLITE ──
        const moonGeo = new THREE.SphereGeometry(28, 32, 32);
        const moonMat = new THREE.MeshPhongMaterial({ color: 0x445566, emissive: 0x001122 });
        const moon = new THREE.Mesh(moonGeo, moonMat);
        scene.add(moon);

        // ── ORBITAL STATION ──
        const stationGroup = new THREE.Group();

        // Central hub
        const hubGeo = new THREE.CylinderGeometry(30, 30, 15, 16);
        const hubMat = new THREE.MeshPhongMaterial({ color: 0x334455, emissive: 0x00f3ff, emissiveIntensity: 0.2 });
        stationGroup.add(new THREE.Mesh(hubGeo, hubMat));

        // Solar panels
        for (let side of [-1, 1]) {
            const panelGeo = new THREE.BoxGeometry(80, 2, 20);
            const panelMat = new THREE.MeshPhongMaterial({ color: 0x223344, emissive: 0x0044aa, emissiveIntensity: 0.3 });
            const panel = new THREE.Mesh(panelGeo, panelMat);
            panel.position.x = side * 55;
            stationGroup.add(panel);
        }

        // Station glow
        const staPl = new THREE.PointLight(0x00f3ff, 1.5, 300);
        stationGroup.add(staPl);

        stationGroup.position.set(-300, 100, 0);
        scene.add(stationGroup);

        // ── LIGHTING ──
        const sunLight = new THREE.DirectionalLight(0x4488ff, 2.5);
        sunLight.position.set(-1500, 800, 1200);
        scene.add(sunLight);
        const rimLight = new THREE.DirectionalLight(0x9d4edd, 1.2);
        rimLight.position.set(1000, -400, -800);
        scene.add(rimLight);
        scene.add(new THREE.AmbientLight(0x081020, 2));

        // ── ANIMATE ──
        const clock = new THREE.Clock();

        function animate() {
            requestAnimationFrame(animate);
            const dt = clock.getDelta();
            const elapsed = clock.getElapsedTime();

            bgMat.uniforms.time.value = elapsed;

            // Slow star drift
            stars.rotation.y += 0.00005;

            // Planet rotation
            planet.rotation.y += 0.0008;
            surface.rotation.y -= 0.0003;

            // Moon orbit
            moon.position.x = planet.position.x + Math.sin(elapsed * 0.4) * 500;
            moon.position.y = planet.position.y + Math.cos(elapsed * 0.2) * 80;
            moon.position.z = planet.position.z + Math.cos(elapsed * 0.4) * 500;
            moon.rotation.y += 0.003;

            // Station slow orbit
            stationGroup.rotation.y += 0.002;
            stationGroup.position.x = -300 + Math.sin(elapsed * 0.15) * 30;
            stationGroup.position.y = 100 + Math.cos(elapsed * 0.1) * 20;
            staPl.intensity = 1.3 + Math.sin(elapsed * 3) * 0.2;

            renderer.autoClear = false;
            renderer.clear();
            renderer.render(bgScene, bgCam);
            renderer.render(scene, camera);
        }

        // ── MOUSE PARALLAX ──
        window.addEventListener('mousemove', (e) => {
            const x = (e.clientX / window.innerWidth - 0.5) * 80;
            const y = (e.clientY / window.innerHeight - 0.5) * 50;
            if (typeof gsap !== 'undefined') {
                gsap.to(camera.position, { x: x * 0.5, y: 80 - y * 0.5, duration: 2.5, ease: 'power2.out' });
            }
        });

        window.addEventListener('resize', () => {
            camera.aspect = window.innerWidth / window.innerHeight;
            camera.updateProjectionMatrix();
            renderer.setSize(window.innerWidth, window.innerHeight);
        });

        animate();
    }
})();
