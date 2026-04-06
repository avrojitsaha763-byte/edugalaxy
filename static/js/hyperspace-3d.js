/* hyperspace-3d.js - EduGalaxy Hyperspace Tunnel (Full Warp Speed) */
(function() {
    'use strict';

    if (typeof THREE === 'undefined') {
        window.addEventListener('load', () => initHyperspace());
        return;
    }
    initHyperspace();

    function initHyperspace() {
        const canvas = document.getElementById('hyperspace-canvas');
        if (!canvas) return;

        const scene = new THREE.Scene();
        const camera = new THREE.PerspectiveCamera(80, canvas.clientWidth / canvas.clientHeight, 0.1, 6000);
        camera.position.z = 800;

        const renderer = new THREE.WebGLRenderer({ canvas, antialias: true, alpha: false });
        renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
        renderer.setSize(canvas.clientWidth, canvas.clientHeight);
        renderer.setClearColor(0x000005, 1);

        // ── HYPERSPACE TUNNEL STREAKS ──
        // Radially emanating from center, elongated
        const streaks = [];
        const STREAK_COUNT = 600;

        function createStreak() {
            // Random angle around center
            const angle = Math.random() * Math.PI * 2;
            const radius = Math.random() * 300 + 20;  // distance from center axis
            const x = Math.cos(angle) * radius;
            const y = Math.sin(angle) * radius;
            const z = -(Math.random() * 5000 + 500);
            const len = Math.random() * 300 + 80;

            // Color: cyan, white, or electric blue
            const palette = [0x00f3ff, 0xffffff, 0x4488ff, 0xaaddff];
            const col = palette[Math.floor(Math.random() * palette.length)];

            const mat = new THREE.LineBasicMaterial({
                color: col,
                transparent: true,
                opacity: 0.6 + Math.random() * 0.4,
                blending: THREE.AdditiveBlending
            });
            const pts = [
                new THREE.Vector3(x, y, z),
                new THREE.Vector3(x, y, z + len)
            ];
            const geo = new THREE.BufferGeometry().setFromPoints(pts);
            const line = new THREE.Line(geo, mat);
            line.userData = { speed: 120 + Math.random() * 200, startZ: z, x, y };
            scene.add(line);
            streaks.push(line);
        }

        for (let i = 0; i < STREAK_COUNT; i++) createStreak();

        // ── TUNNEL RING ──
        // Faint rings to give tunnel depth perception
        const rings = [];
        for (let i = 0; i < 20; i++) {
            const ringGeo = new THREE.RingGeometry(200 + i * 15, 205 + i * 15, 64);
            const ringMat = new THREE.MeshBasicMaterial({
                color: 0x00f3ff,
                transparent: true,
                opacity: 0.04,
                side: THREE.DoubleSide,
                blending: THREE.AdditiveBlending
            });
            const ring = new THREE.Mesh(ringGeo, ringMat);
            ring.position.z = -i * 300 - 200;
            scene.add(ring);
            rings.push(ring);
        }

        // ── CENTRAL LENS FLARE DOT ──
        const flareGeo = new THREE.SphereGeometry(8, 16, 16);
        const flareMat = new THREE.MeshBasicMaterial({ color: 0xffffff, transparent: true, opacity: 0.9, blending: THREE.AdditiveBlending });
        const flare = new THREE.Mesh(flareGeo, flareMat);
        flare.position.z = 200;
        scene.add(flare);

        const flarGlow = new THREE.PointLight(0x00f3ff, 2, 500);
        scene.add(flarGlow);

        // ── COCKPIT VIGNETTE (CSS overlay, not 3D) ──
        // Already handled by cockpit-hud in HTML

        const clock = new THREE.Clock();
        let speed = 150; // base warp speed

        function animate() {
            requestAnimationFrame(animate);
            const dt = clock.getDelta();
            const elapsed = clock.getElapsedTime();

            // Move all streaks toward camera
            for (let i = 0; i < streaks.length; i++) {
                const s = streaks[i];
                s.position.z += s.userData.speed * dt;
                // Streaks spread out as they approach (perspective)
                const progress = (s.position.z + 5000) / 5000;
                s.scale.set(1 + progress * 0.3, 1 + progress * 0.3, 1);

                if (s.position.z > 1000) {
                    s.position.z = s.userData.startZ;
                    // Reset position
                    const angle = Math.random() * Math.PI * 2;
                    const radius = Math.random() * 300 + 20;
                    s.userData.x = Math.cos(angle) * radius;
                    s.userData.y = Math.sin(angle) * radius;
                    s.position.x = 0;
                    s.position.y = 0;
                }
            }

            // Rings pulse toward camera
            rings.forEach((ring, idx) => {
                ring.position.z += 50 * dt;
                if (ring.position.z > 200) ring.position.z = -5800;
                ring.material.opacity = 0.03 + Math.sin(elapsed * 2 + idx) * 0.02;
            });

            // Flare pulse
            flareMat.opacity = 0.7 + Math.sin(elapsed * 3) * 0.2;
            flarGlow.intensity = 1.5 + Math.sin(elapsed * 2) * 0.5;

            renderer.render(scene, camera);
        }

        // ── MOUSE TILT ──
        const target = canvas.parentElement;
        if (target) {
            target.addEventListener('mousemove', (e) => {
                const rect = canvas.getBoundingClientRect();
                const x = ((e.clientX - rect.left) / rect.width - 0.5) * 80;
                const y = ((e.clientY - rect.top) / rect.height - 0.5) * 60;
                if (typeof gsap !== 'undefined') {
                    gsap.to(camera.position, { x: x, y: -y, duration: 1.5, ease: 'power2.out' });
                    gsap.to(camera.rotation, { z: x * 0.003, duration: 1.5 });
                }
            });
        }

        // Resize
        const resizeObs = new ResizeObserver(() => {
            camera.aspect = canvas.clientWidth / canvas.clientHeight;
            camera.updateProjectionMatrix();
            renderer.setSize(canvas.clientWidth, canvas.clientHeight);
        });
        resizeObs.observe(canvas);

        animate();
    }
})();
