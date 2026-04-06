/* home-3d.js - EduGalaxy 3D Battlefield Engine — Full God Mode */
(function() {
    'use strict';

    // Guard: wait for THREE to be available
    if (typeof THREE === 'undefined') {
        console.warn('[home-3d] THREE not loaded yet, retrying...');
        window.addEventListener('load', function() { initBattlefield(); });
        return;
    }
    initBattlefield();

    function initBattlefield() {
        // ── CANVAS SETUP ──
        const canvas = document.getElementById('battlefield-canvas');
        if (!canvas) return;

        const scene = new THREE.Scene();
        const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 15000);
        camera.position.set(0, 0, 600);

        const renderer = new THREE.WebGLRenderer({ canvas, antialias: true, alpha: false });
        renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
        renderer.setSize(window.innerWidth, window.innerHeight);
        renderer.setClearColor(0x010208, 1);

        // ── DEEP SPACE BACKGROUND GRADIENT ──
        // Pure dark deep space with nebula clouds
        const bgScene = new THREE.Scene();
        const bgCamera = new THREE.OrthographicCamera(-1, 1, 1, -1, 0, 1);
        const bgGeo = new THREE.PlaneGeometry(2, 2);
        const bgMat = new THREE.ShaderMaterial({
            uniforms: { time: { value: 0 } },
            vertexShader: `void main() { gl_Position = vec4(position, 1.0); }`,
            fragmentShader: `
                uniform float time;
                void main() {
                    vec2 uv = gl_FragCoord.xy / vec2(1920.0, 1080.0);
                    vec3 col = vec3(0.004, 0.008, 0.02);
                    // Nebula purple cloud
                    float n1 = sin(uv.x * 3.0 + time * 0.1) * cos(uv.y * 2.5 + time * 0.07);
                    col += vec3(0.06, 0.0, 0.12) * max(n1 * 0.5 + 0.5, 0.0);
                    // Nebula cyan glow
                    float n2 = cos(uv.x * 2.0 - time * 0.05) * sin(uv.y * 3.5 + time * 0.08);
                    col += vec3(0.0, 0.05, 0.1) * max(n2 * 0.5 + 0.5, 0.0);
                    gl_FragColor = vec4(col, 1.0);
                }
            `,
            depthWrite: false
        });
        bgScene.add(new THREE.Mesh(bgGeo, bgMat));

        // ── 12,000 STARS ──
        const starGeo = new THREE.BufferGeometry();
        const starPos = new Float32Array(12000 * 3);
        const starColors = new Float32Array(12000 * 3);
        for (let i = 0; i < 12000; i++) {
            starPos[i*3]     = (Math.random() - 0.5) * 8000;
            starPos[i*3 + 1] = (Math.random() - 0.5) * 8000;
            starPos[i*3 + 2] = (Math.random() - 0.5) * 6000;
            const c = Math.random();
            if (c < 0.6) { starColors[i*3]=0.6; starColors[i*3+1]=0.8; starColors[i*3+2]=1.0; }       // blue-white
            else if (c < 0.8) { starColors[i*3]=0.0; starColors[i*3+1]=0.95; starColors[i*3+2]=1.0; } // cyan
            else { starColors[i*3]=0.6; starColors[i*3+1]=0.2; starColors[i*3+2]=0.9; }               // purple
        }
        starGeo.setAttribute('position', new THREE.BufferAttribute(starPos, 3));
        starGeo.setAttribute('color', new THREE.BufferAttribute(starColors, 3));
        const starMat = new THREE.PointsMaterial({ size: 1.8, vertexColors: true, transparent: true, opacity: 0.9 });
        const stars = new THREE.Points(starGeo, starMat);
        scene.add(stars);

        // ── LASER BOLTS ──
        const lasers = [];
        function spawnLaser() {
            const mat = new THREE.LineBasicMaterial({
                color: Math.random() > 0.5 ? 0x00f3ff : 0xff003c,
                transparent: true, opacity: 0.9,
                blending: THREE.AdditiveBlending
            });
            const x = (Math.random() - 0.5) * 4000;
            const y = (Math.random() - 0.5) * 2000;
            const z = -3000 - Math.random() * 3000;
            const len = 80 + Math.random() * 120;
            const pts = [new THREE.Vector3(x, y, z), new THREE.Vector3(x, y, z + len)];
            const geo = new THREE.BufferGeometry().setFromPoints(pts);
            const laser = new THREE.Line(geo, mat);
            laser.userData.speed = 400 + Math.random() * 300;
            laser.userData.life = 1.0;
            scene.add(laser);
            lasers.push(laser);
        }
        for (let i = 0; i < 60; i++) spawnLaser(); // Initial burst

        // ── X-WING STYLE SHIPS ──
        const ships = [];
        function createShip(allied) {
            const shipGroup = new THREE.Group();
            const bodyColor = allied ? 0x334455 : 0x443322;
            const glowColor = allied ? 0x00f3ff : 0xff4400;

            const body = new THREE.Mesh(
                new THREE.BoxGeometry(8, 3, 22),
                new THREE.MeshPhongMaterial({ color: bodyColor, emissive: glowColor, emissiveIntensity: 0.15 })
            );
            shipGroup.add(body);

            // Wings
            const wingL = new THREE.Mesh(
                new THREE.BoxGeometry(22, 1, 10),
                new THREE.MeshPhongMaterial({ color: bodyColor })
            );
            wingL.position.set(0, -1.5, 2);
            shipGroup.add(wingL);

            // Engine glow
            for (let ex of [-3.5, 3.5]) {
                const eng = new THREE.Mesh(
                    new THREE.CylinderGeometry(1.5, 1.5, 3, 8),
                    new THREE.MeshBasicMaterial({ color: glowColor })
                );
                eng.position.set(ex, -1, -10);
                eng.rotation.x = Math.PI / 2;
                shipGroup.add(eng);

                // Engine point light
                const pl = new THREE.PointLight(glowColor, 1.5, 80);
                pl.position.set(ex, -1, -12);
                shipGroup.add(pl);
            }

            const side = allied ? 1 : -1;
            shipGroup.position.set(
                side * (300 + Math.random() * 800),
                (Math.random() - 0.5) * 600,
                -1000 - Math.random() * 3000
            );
            shipGroup.rotation.y = allied ? 0.3 : -0.3;
            shipGroup.userData = {
                speed: 4 + Math.random() * 3,
                drift: (Math.random() - 0.5) * 0.008,
                allied,
                wobble: Math.random() * Math.PI * 2
            };
            scene.add(shipGroup);
            ships.push(shipGroup);
            return shipGroup;
        }

        for (let i = 0; i < 12; i++) createShip(true);
        for (let i = 0; i < 10; i++) createShip(false);

        // ── LIGHTING ──
        scene.add(new THREE.AmbientLight(0x0a1a33, 3));
        const sunLight = new THREE.DirectionalLight(0x4488ff, 2);
        sunLight.position.set(-500, 800, 500);
        scene.add(sunLight);
        const rimLight = new THREE.DirectionalLight(0x9d4edd, 1.5);
        rimLight.position.set(500, -200, -500);
        scene.add(rimLight);

        // ── EXPLOSION PARTICLES ──
        const explosions = [];
        function spawnExplosion() {
            const count = 30;
            const geo = new THREE.BufferGeometry();
            const pos = new Float32Array(count * 3);
            const x = (Math.random() - 0.5) * 3000;
            const y = (Math.random() - 0.5) * 1500;
            const z = -1000 - Math.random() * 3000;
            for (let i = 0; i < count; i++) {
                pos[i*3]     = x + (Math.random()-0.5) * 20;
                pos[i*3 + 1] = y + (Math.random()-0.5) * 20;
                pos[i*3 + 2] = z + (Math.random()-0.5) * 20;
            }
            geo.setAttribute('position', new THREE.BufferAttribute(pos, 3));
            const mat = new THREE.PointsMaterial({ color: 0xff6600, size: 5, transparent: true, opacity: 1, blending: THREE.AdditiveBlending });
            const pts = new THREE.Points(geo, mat);
            pts.userData.life = 1.0;
            scene.add(pts);
            explosions.push(pts);
        }

        // ── ANIMATE ──
        const clock = new THREE.Clock();
        let laserTimer = 0;
        let explosionTimer = 0;

        function animate() {
            requestAnimationFrame(animate);
            const dt = clock.getDelta();
            const elapsed = clock.getElapsedTime();

            bgMat.uniforms.time.value = elapsed;

            // Stars slow drift
            stars.rotation.y += 0.00008;
            stars.rotation.z += 0.00003;

            // Ships
            ships.forEach(ship => {
                const dir = ship.userData.allied ? -1 : 1;
                ship.position.z += ship.userData.speed;
                ship.position.x += Math.sin(elapsed * 0.3 + ship.userData.wobble) * 0.5;
                ship.rotation.z += ship.userData.drift;
                if (ship.position.z > 1000) {
                    ship.position.z = -4000 - Math.random() * 2000;
                    ship.position.x = dir * (300 + Math.random() * 800);
                    ship.position.y = (Math.random() - 0.5) * 600;
                }
            });

            // Lasers
            laserTimer += dt;
            if (laserTimer > 0.08) {
                spawnLaser();
                laserTimer = 0;
            }
            for (let i = lasers.length - 1; i >= 0; i--) {
                const l = lasers[i];
                l.position.z += l.userData.speed * dt;
                l.userData.life -= dt * 0.8;
                l.material.opacity = l.userData.life;
                if (l.userData.life <= 0 || l.position.z > 800) {
                    scene.remove(l);
                    l.geometry.dispose();
                    lasers.splice(i, 1);
                }
            }

            // Explosions
            explosionTimer += dt;
            if (explosionTimer > 1.5) {
                spawnExplosion();
                explosionTimer = Math.random() * 0.5;
            }
            for (let i = explosions.length - 1; i >= 0; i--) {
                const e = explosions[i];
                e.userData.life -= dt * 0.6;
                e.material.opacity = e.userData.life;
                const s = 1 + (1 - e.userData.life) * 3;
                e.scale.setScalar(s);
                if (e.userData.life <= 0) {
                    scene.remove(e);
                    e.geometry.dispose();
                    explosions.splice(i, 1);
                }
            }

            // Camera mouse parallax
            renderer.autoClear = false;
            renderer.clear();
            renderer.render(bgScene, bgCamera);
            renderer.render(scene, camera);
        }

        // ── MOUSE PARALLAX ──
        let mouseX = 0, mouseY = 0;
        window.addEventListener('mousemove', (e) => {
            mouseX = (e.clientX / window.innerWidth - 0.5) * 60;
            mouseY = (e.clientY / window.innerHeight - 0.5) * 40;
            if (typeof gsap !== 'undefined') {
                gsap.to(camera.position, { x: -mouseX, y: mouseY, duration: 2, ease: 'power2.out' });
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
