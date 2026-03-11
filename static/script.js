/* static/script.js - EduGalaxy Extreme "Beyond Limits" Engine */

// ==========================================
// 1. THREE.JS ADVANCED 3D & POST-PROCESSING
// ==========================================
let scene, camera, renderer, composer;
let earth, blackHole, particles;
let isQuizPage = false;
let clock = new THREE.Clock();

function initAdvancedWebGL() {
    const canvas = document.getElementById('galaxy-canvas');
    if (!canvas || typeof THREE === 'undefined') return;

    // Detect Page
    const path = window.location.pathname;
    isQuizPage = path.includes('/quiz');
    const isSignup = path.includes('/signup');
    const isLogin = path.includes('/login');
    const isHome = path === '/' || path === '/home';

    // Basic Setup
    scene = new THREE.Scene();
    scene.fog = new THREE.FogExp2(0x02000a, 0.001);

    camera = new THREE.PerspectiveCamera(70, window.innerWidth / window.innerHeight, 0.1, 4000);
    camera.position.z = 300; // Base camera Z

    renderer = new THREE.WebGLRenderer({ canvas: canvas, antialias: true, alpha: false });
    renderer.setSize(window.innerWidth, window.innerHeight);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2)); // optimize
    renderer.setClearColor(0x02000a, 1);
    
    // Add Lights
    // Existing lights (AmbientLight and DirectionalLight) are replaced/augmented by the new lighting scheme
    // Cinematic Lighting for Asteroids and Ships
    const hemiLight = new THREE.HemisphereLight(0xffffff, 0x444455, 3.0); // Extreme bright ambient
    scene.add(hemiLight);

    const mainLight = new THREE.DirectionalLight(0xffffff, 8.0); // Extremely intense directional
    mainLight.position.set(500, 1000, 500);
    scene.add(mainLight);

    const blueLight = new THREE.PointLight(0x00d4ff, 4, 3000);
    blueLight.position.set(-500, 0, -1000);
    scene.add(blueLight);

    // Track state to update animation
    window.appState = { isHome, isSignup, isLogin, mouseX: 0, mouseY: 0 };

    // Context specific 3D Generation
    if (isSignup) {
        createNarutoLightspeed();
    } else if (isLogin) {
        createHolographicPortal();
    } else if (isHome) {
        createStarWarsGalaxy();
    } else if (isQuizPage) {
        createBlackHole();
        createParticleSystem(); // background stars
    } else {
        createGalaxyMap();
        createParticleSystem();
    }

    // EffectComposer Pipeline (Unreal Bloom)
    const renderScene = new THREE.RenderPass(scene, camera);
    const bloomPass = new THREE.UnrealBloomPass(new THREE.Vector2(window.innerWidth, window.innerHeight), 1.5, 0.4, 0.85);
    bloomPass.threshold = 0.1;
    bloomPass.strength = isSignup ? 2.5 : (isLogin ? 1.8 : 1.2); 
    bloomPass.radius = 0.8;

    composer = new THREE.EffectComposer(renderer);
    composer.addPass(renderScene);
    composer.addPass(bloomPass);

    // Mouse Parallax System
    document.addEventListener('mousemove', (event) => {
        // Normalized coordinates (-1 to 1)
        window.appState.mouseX = (event.clientX / window.innerWidth) * 2 - 1;
        window.appState.mouseY = -(event.clientY / window.innerHeight) * 2 + 1;
    });

    window.addEventListener('resize', () => {
        camera.aspect = window.innerWidth / window.innerHeight;
        camera.updateProjectionMatrix();
        renderer.setSize(window.innerWidth, window.innerHeight);
        composer.setSize(window.innerWidth, window.innerHeight);
    });

    // Boot Sequence Removal
    setTimeout(() => {
        const boot = document.getElementById('boot-sequence');
        if (boot) {
            gsap.to(boot, {opacity: 0, duration: 1, onComplete: () => boot.remove()});
        }
    }, 2500);

    // Run Render Loop
    animateWebGL();
}


// --- 1. STAR WARS GALAXY (Home Page) - BEYOND LIMITS UPGRADE ---
function createStarWarsGalaxy() {
    // A Sprawling Galaxy with Planets and Alien Warships
    const particleCount = 20000;
    const geometry = new THREE.BufferGeometry();
    const positions = new Float32Array(particleCount * 3);
    const colors = new Float32Array(particleCount * 3);
    const c1 = new THREE.Color(0x00f0ff); // Cyan stars
    const c2 = new THREE.Color(0xff7700); // Orange stars
    const c3 = new THREE.Color(0xff0055); // Red giant stars

    for (let i = 0; i < particleCount; i++) {
        // Deep Z spread for scrolling through
        const x = (Math.random() - 0.5) * 4000;
        const y = (Math.random() - 0.5) * 2000;
        const z = (Math.random() - 0.5) * 4000;

        positions[i*3] = x;
        positions[i*3+1] = y;
        positions[i*3+2] = z;

        const mixRatio = Math.random();
        let mixed;
        if(mixRatio < 0.4) mixed = c1;
        else if(mixRatio < 0.8) mixed = c2;
        else mixed = c3;
        
        colors[i*3] = mixed.r; colors[i*3+1] = mixed.g; colors[i*3+2] = mixed.b;
    }
    geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));
    geometry.setAttribute('color', new THREE.BufferAttribute(colors, 3));

    const material = new THREE.PointsMaterial({
        size: 3,
        vertexColors: true,
        transparent: true,
        opacity: 0.9,
        blending: THREE.AdditiveBlending,
        depthWrite: false
    });

    particles = new THREE.Points(geometry, material);
    scene.add(particles);

    // The Target Planet (Earth/Shield World)
    const planetGeo = new THREE.SphereGeometry(150, 64, 64);
    const planetMat = new THREE.MeshPhongMaterial({
        color: 0x00aaff,
        emissive: 0x002255,
        shininess: 60,
        transparent: true,
        opacity: 0.95
    });
    // Add grid wireframe to planet to make it look sci-fi
    const wireMat = new THREE.MeshBasicMaterial({ color: 0x00ff87, wireframe: true, transparent: true, opacity: 0.3 });
    earth = new THREE.Mesh(planetGeo, planetMat);
    const planetWire = new THREE.Mesh(planetGeo, wireMat);
    earth.add(planetWire);
    earth.position.set(-200, -100, -1000);
    scene.add(earth);

    // Alien Warships (Floating evil tech pyramids)
    const shipGeo = new THREE.TetrahedronGeometry(350); // MASSIVE Star Destroyers
    // Use MeshPhongMaterial now that we have bright lights, to get metallic shine
    const shipMat = new THREE.MeshPhongMaterial({ 
        color: 0xff1144, // Bright Crimson Red so they pop!
        emissive: 0x440011, // Slight red glow to ensure visibility
        specular: 0xffffff, 
        shininess: 100, 
        flatShading: true 
    }); 
    const shipGlowMat = new THREE.MeshBasicMaterial({ color: 0xffffff, wireframe: true, transparent: true, opacity: 0.8 }); // White glowing frame
    
    window.appState.warships = [];
    for(let i=0; i<8; i++) {
        const ship = new THREE.Mesh(shipGeo, shipMat);
        const glow = new THREE.Mesh(shipGeo, shipGlowMat);
        glow.scale.set(1.02, 1.02, 1.02); // slight outline
        ship.add(glow);

        // Spawn very tightly in front of camera
        ship.position.set((Math.random() - 0.5) * 800, (Math.random() - 0.5) * 600, -200 - (Math.random() * 800));
        ship.rotation.set(Math.random(), Math.random(), Math.random());
        // Custom data for rapid forward movement
        ship.userData = { speedX: (Math.random() - 0.5)*5, speedY: (Math.random() - 0.5)*5, speedZ: Math.random()*15+5 };
        scene.add(ship);
        window.appState.warships.push(ship);
    }

    // SATALLITES (Defending the planet)
    const satGeo = new THREE.BoxGeometry(30, 80, 10);
    // Use highly visible vibrant color
    const satMat = new THREE.MeshBasicMaterial({ color: 0x00ff87, wireframe: true, transparent: true, opacity: 0.8 });
    window.appState.satellites = [];
    for(let i=0; i<8; i++) {
        const sat = new THREE.Mesh(satGeo, satMat);
        // Position them starting nearer and flying around
        sat.position.set(-200 + (Math.random()-0.5)*800, -100 + (Math.random()-0.5)*500, -100 - (Math.random()*1500));
        scene.add(sat);
        window.appState.satellites.push(sat);
    }

    // ASTEROID BELT (using InstancedMesh for performance)
    const astGeo = new THREE.DodecahedronGeometry(150, 0); // MASSIVE rocks
    // Bright metallic rocks
    const astMat = new THREE.MeshPhongMaterial({ 
        color: 0xcccccc, // Very bright gray
        emissive: 0x111111,
        specular: 0xffffff,
        shininess: 50,
        flatShading: true 
    });
    const astCount = 100; // Less count but massive size
    const asteroids = new THREE.InstancedMesh(astGeo, astMat, astCount);
    const astDummy = new THREE.Object3D();
    for(let i=0; i<astCount; i++) {
        // Tight clustered spawn along the Z pathway
        astDummy.position.set((Math.random() - 0.5)*1500, (Math.random() - 0.5)*1000, 200 - Math.random()*2000);
        astDummy.rotation.set(Math.random()*Math.PI, Math.random()*Math.PI, 0);
        const scale = Math.random() * 2 + 1; // Between 1x and 3x size
        astDummy.scale.set(scale, scale, scale);
        astDummy.updateMatrix();
        asteroids.setMatrixAt(i, astDummy.matrix);
    }
    scene.add(asteroids);
    window.appState.asteroids = asteroids;

    // COSMIC RAYS / METEORITES (Fast moving lines)
    const meteorGeo = new THREE.CylinderGeometry(1, 1, 250, 4); // Thicker, longer beams
    const meteorMat = new THREE.MeshBasicMaterial({ color: 0xffaa00, transparent:true, opacity:0.9 });
    window.appState.meteors = [];
    for(let i=0; i<50; i++) {
        const meteor = new THREE.Mesh(meteorGeo, meteorMat);
        // Start them close to camera initially
        meteor.position.set((Math.random()-0.5)*3000, (Math.random()-0.5)*3000, 200 - Math.random()*3000);
        meteor.rotation.x = Math.PI/2; // point along Z
        scene.add(meteor);
        window.appState.meteors.push(meteor);
    }

    // LASERS (Shooting from ships)
    const laserGeo = new THREE.CylinderGeometry(2, 2, 300, 4); // Big visible lasers!
    const laserMat = new THREE.MeshBasicMaterial({ color: 0xff0055, transparent:true, opacity:1.0 });
    window.appState.lasers = [];
    for(let i=0; i<10; i++) {
        const laser = new THREE.Mesh(laserGeo, laserMat);
        laser.position.set(0, 0, 9999); // Hide initially
        laser.rotation.x = Math.PI/2;
        scene.add(laser);
        window.appState.lasers.push({ mesh: laser, active: false });
    }
}


// --- 2. NARUTO LIGHTSPEED (Signup Page) ---
function createNarutoLightspeed() {
    // Hyperspace stretched starfield
    const starCount = 5000;
    const geometry = new THREE.BufferGeometry();
    const positions = new Float32Array(starCount * 3);
    const velocities = [];

    for (let i = 0; i < starCount; i++) {
        positions[i*3] = (Math.random() - 0.5) * 2000;
        positions[i*3+1] = (Math.random() - 0.5) * 2000;
        positions[i*3+2] = (Math.random() - 0.5) * 2000;
        velocities.push(0); // initial speed
    }

    geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));
    
    // Stretch the points along Z using shader or simple lines. We'll use points with very fast movement
    const material = new THREE.PointsMaterial({
        color: 0xffffff,
        size: 3,
        transparent: true,
        blending: THREE.AdditiveBlending
    });

    particles = new THREE.Points(geometry, material);
    scene.add(particles);
    
    window.appState.velocities = velocities;
    
    // Add a glowing core tunnel
    const tunnelGeo = new THREE.CylinderGeometry(50, 400, 2000, 32, 1, true);
    const tunnelMat = new THREE.MeshBasicMaterial({
        color: 0xff7700,
        wireframe: true,
        transparent: true,
        opacity: 0.1,
        side: THREE.BackSide
    });
    const tunnel = new THREE.Mesh(tunnelGeo, tunnelMat);
    tunnel.rotation.x = Math.PI / 2;
    tunnel.position.z = -500;
    scene.add(tunnel);
    window.appState.tunnel = tunnel;

    camera.position.z = 100; // Close up
}


// --- 3. HOLOGRAPHIC CYBER PORTAL (Login Page) ---
function createHolographicPortal() {
    // Main rotating wireframe Torus Knot
    const geo = new THREE.TorusKnotGeometry(80, 20, 100, 16);
    
    // Custom shader for matrix-like sweeping lines
    const mat = new THREE.ShaderMaterial({
        uniforms: {
            time: { value: 0 },
            baseColor: { value: new THREE.Color(0x00ffa8) }
        },
        vertexShader: `
            varying vec2 vUv;
            varying vec3 vPosition;
            void main() {
                vUv = uv;
                vPosition = position;
                gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
            }
        `,
        fragmentShader: `
            uniform float time;
            uniform vec3 baseColor;
            varying vec2 vUv;
            varying vec3 vPosition;
            void main() {
                // Scanning lines effect along Y axis
                float scanline = sin(vPosition.y * 0.5 - time * 5.0) * 0.5 + 0.5;
                float grid = sin(vUv.x * 50.0) * sin(vUv.y * 50.0);
                
                vec3 finalColor = baseColor * (scanline + 0.2) + (grid * 0.3 * baseColor);
                float alpha = scanline * 0.8 + 0.2;
                
                if(grid < 0.1 && scanline < 0.2) discard; // Wireframe look
                
                gl_FragColor = vec4(finalColor, alpha);
            }
        `,
        transparent: true,
        wireframe: true,
        side: THREE.DoubleSide,
        blending: THREE.AdditiveBlending
    });

    earth = new THREE.Mesh(geo, mat); // reuse earth variable for main object
    scene.add(earth);

    // Background floating data crystals
    const crysGeo = new THREE.OctahedronGeometry(10);
    const crysMat = new THREE.MeshBasicMaterial({ color: 0x00f0ff, wireframe: true, transparent:true, opacity:0.5 });
    window.appState.crystals = [];
    for(let i=0; i<30; i++) {
        const c = new THREE.Mesh(crysGeo, crysMat);
        c.position.set((Math.random()-0.5)*800, (Math.random()-0.5)*800, -200 - Math.random()*400);
        scene.add(c);
        window.appState.crystals.push(c);
    }
}

// Fallback / legacy modes
function createParticleSystem() {
    // simple fallback stars
    const geometry = new THREE.BufferGeometry();
    const positions = new Float32Array(5000 * 3);
    for (let i = 0; i < 5000; i++) {
        positions[i*3] = (Math.random() - 0.5) * 2000;
        positions[i*3+1] = (Math.random() - 0.5) * 2000;
        positions[i*3+2] = (Math.random() - 0.5) * 2000;
    }
    geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));
    particles = new THREE.Points(geometry, new THREE.PointsMaterial({color: 0xffffff, size:1, transparent:true, opacity:0.5}));
    scene.add(particles);
}

function createGalaxyMap() {
    const geo = new THREE.IcosahedronGeometry(80, 1);
    const mat = new THREE.MeshBasicMaterial({ color: 0x00d4ff, wireframe: true, transparent: true, opacity: 0.3 });
    earth = new THREE.Mesh(geo, mat);
    scene.add(earth);
}

function createBlackHole() {
    const geo = new THREE.RingGeometry(20, 60, 64);
    const mat = new THREE.MeshBasicMaterial({ color: 0xff0055, side: THREE.DoubleSide, transparent:true, opacity:0.8 });
    blackHole = new THREE.Mesh(geo, mat);
    scene.add(blackHole);
}


// --- MAIN RENDER LOOP ---
function animateWebGL() {
    requestAnimationFrame(animateWebGL);
    let delta = clock.getDelta();
    let time = clock.getElapsedTime();

    const mx = window.appState.mouseX; // -1 to 1
    const my = window.appState.mouseY; // -1 to 1
    const scrollY = window.scrollY || document.documentElement.scrollTop;

    // 1. STAR WARS GALAXY ANIMATION (BEYOND LIMITS)
    if (window.appState.isHome) {
        if (particles) {
            particles.rotation.y += 0.0008;
            particles.rotation.z = mx * 0.1; // Space twists with mouse
        }
        if (earth) {
            earth.rotation.y += 0.003;
            // Native foolproof scroll zoom - moves camera deep into the Z axis!
            const targetZ = 300 - (scrollY * 1.2);
            camera.position.z += (targetZ - camera.position.z) * 0.1;
            
            // Mouse parallax effect on planet
            earth.position.x += ((mx * 120) - earth.position.x - 200) * 0.05; 
            earth.position.y += ((my * 120) - earth.position.y - 100) * 0.05; 
        }

        // Alien Warships (Moving, dodging mouse)
        if (window.appState.warships) {
            window.appState.warships.forEach((ship) => {
                ship.rotation.x += 0.01;
                ship.rotation.y += 0.02;
                ship.position.x += ship.userData.speedX;
                ship.position.y += ship.userData.speedY;
                ship.position.z += ship.userData.speedZ;
                
                // Avoid mouse heavily
                ship.position.x += mx * 5;
                ship.position.y += my * 5;

                // Loop if it passes the camera or gets too far away
                if(ship.position.z > camera.position.z + 500) {
                     ship.position.z = camera.position.z - 2000; 
                     ship.position.x = (Math.random() - 0.5) * 2000;
                     ship.position.y = (Math.random() - 0.5) * 1000;
                } else if (ship.position.z < camera.position.z - 3000) {
                     ship.position.z = camera.position.z + 500;
                     ship.position.x = (Math.random() - 0.5) * 2000;
                }
            });
        }

        // Meteors (Extreme Speed)
        if (window.appState.meteors) {
            window.appState.meteors.forEach((m) => {
                m.position.z += 50; // warp speed
                m.position.x -= mx * 20; // swift parallax dodging
                m.position.y -= my * 20;
                // Loop back directly in front of camera
                if(m.position.z > camera.position.z + 500) {
                    m.position.set((Math.random()-0.5)*3000, (Math.random()-0.5)*3000, camera.position.z - 3000);
                }
            });
        }

        // Action Lasers 
        if (window.appState.lasers) {
            window.appState.lasers.forEach(lObj => {
                if(!lObj.active && Math.random() < 0.02 && window.appState.warships.length > 0) {
                    // Fire laser!
                    lObj.active = true;
                    // Find a ship that is currently visible in front of camera to shoot from
                    const visibleShips = window.appState.warships.filter(s => s.position.z < camera.position.z && s.position.z > camera.position.z - 1500);
                    if (visibleShips.length > 0) {
                        const shooter = visibleShips[Math.floor(Math.random() * visibleShips.length)];
                        lObj.mesh.position.copy(shooter.position);
                        if(typeof audioEngine !== 'undefined') audioEngine.playSfx('laser');
                    } else {
                        lObj.active = false;
                    }
                }
                
                if (lObj.active) {
                    lObj.mesh.position.z += 80; // shoot forward FAST
                    lObj.mesh.position.x += mx * 2; // slight parallax curve
                    
                    if (lObj.mesh.position.z > camera.position.z + 500) {
                        lObj.active = false;
                        lObj.mesh.position.z = 9999; // hide
                    }
                }
            });
        }

        // Satellites orbiting randomly
        if (window.appState.satellites) {
            window.appState.satellites.forEach((sat, i) => {
                const angle = time * (0.5 + i*0.1);
                sat.position.x = earth.position.x + Math.cos(angle) * 200;
                sat.position.y = earth.position.y + Math.sin(angle*1.5) * 100;
                sat.position.z = earth.position.z + Math.sin(angle) * 200;
                sat.rotation.x += 0.02;
                sat.rotation.y += 0.03;
            });
        }

        // Asteroid InstancedMesh parallax
        if (window.appState.asteroids) {
            window.appState.asteroids.rotation.y = time * 0.02;
            window.appState.asteroids.position.x = mx * -150; // counter move
            window.appState.asteroids.position.y = my * -150; 
        }

        // Main Camera Parallax (on top of scroll zoom!)
        camera.position.x += (mx * 250 - camera.position.x) * 0.08;
        camera.position.y += (my * 250 - camera.position.y) * 0.08;
        // The camera target (look at) is offset slightly by mouse too
        const lookTarget = new THREE.Vector3(mx * -300, my * -300, camera.position.z - 800);
        camera.lookAt(lookTarget); 
    }

    // 2. NARUTO LIGHTSPEED ANIMATION
    else if (window.appState.isSignup) {
        if (particles) {
            const positions = particles.geometry.attributes.position.array;
            for(let i=0; i<window.appState.velocities.length; i++) {
                window.appState.velocities[i] += 1.0; // Accelerate faster
                const speed = window.appState.velocities[i];
                positions[i*3+2] += speed;
                
                // If past camera, reset far away
                if (positions[i*3+2] > 300) {
                    positions[i*3+2] = -2500;
                    window.appState.velocities[i] = 0;
                }
            }
            particles.geometry.attributes.position.needsUpdate = true;
        }
        if (window.appState.tunnel) {
            window.appState.tunnel.rotation.y += 0.02;
            // Heavy Tunnel Parallax
            window.appState.tunnel.position.x += ((mx * 500) - window.appState.tunnel.position.x) * 0.15;
            window.appState.tunnel.position.y += ((my * 500) - window.appState.tunnel.position.y) * 0.15;
        }
        
        // Shake camera heavily for lightspeed effect
        camera.position.x = (Math.random() - 0.5) * 4;
        camera.position.y = (Math.random() - 0.5) * 4;
        camera.lookAt(window.appState.tunnel.position);
    }

    // 3. HOLOGRAPHIC PORTAL ANIMATION
    else if (window.appState.isLogin) {
        if (earth) { // TorusKnot
            earth.rotation.y = time * 0.6;
            earth.rotation.x = time * 0.3;
            earth.material.uniforms.time.value = time;
            
            // Mouse Parallax interaction! Pulls the torus towards mouse EXTREMELY hard
            earth.position.x += ((mx * 300) - earth.position.x) * 0.1;
            earth.position.y += ((my * 300) - earth.position.y) * 0.1;
            earth.rotation.z = mx * 0.5; // slight twist
        }
        if (window.appState.crystals) {
            window.appState.crystals.forEach((c, i) => {
                c.rotation.y += 0.04;
                c.rotation.x += 0.02;
                c.position.y += Math.sin(time * 3 + i) * 1.5; // hover higher
                // crystals dodge cursor
                c.position.x += mx * 10;
            });
        }
        camera.position.x += (mx * 80 - camera.position.x) * 0.1;
        camera.position.y += (my * 80 - camera.position.y) * 0.1;
        camera.lookAt(0,0, -200);
    }

    // Default Fallback
    else {
        if (particles) particles.rotation.y += 0.0005;
        if (earth && !isQuizPage) earth.rotation.y += 0.002;
        camera.position.x += (mx * 50 - camera.position.x) * 0.05;
        camera.position.y += (my * 50 - camera.position.y) * 0.05;
        camera.lookAt(scene.position);
    }

    composer.render();
}


// ==========================================
// 2. TONE.JS GENERATIVE AMBIENT AUDIO
// ==========================================
class AdvancedAudioEngine {
    constructor() {
        this.isMuted = localStorage.getItem('eduGalaxyMuted') === 'true';
        this.synths = [];
        this.isInitialized = false;
        
        // Wait to init Tone.js until user interaction to bypass browser blocks
        document.body.addEventListener('click', () => {
            if(!this.isInitialized && !this.isMuted) this.initAudio();
        }, { once: true });
        
        this.updateToggleButton();
    }

    async initAudio() {
        if(typeof Tone === 'undefined') return;
        await Tone.start();
        this.isInitialized = true;
        
        // --- SWEET MELODIOUS AMBIENT SYMPHONY ---
        
        // Master FX Chain
        const masterChorus = new Tone.Chorus(4, 2.5, 0.5).toDestination().start();
        const masterReverb = new Tone.Reverb({ decay: 8, preDelay: 0.1, wet: 0.6 }).connect(masterChorus);
        
        // 1. Lush Ethereal Pad (The majestic background sweep)
        const padFilter = new Tone.Filter(600, "lowpass", -24).connect(masterReverb);
        const lfo = new Tone.LFO(0.1, 400, 1000).connect(padFilter.frequency).start(); // Evolving filter sweep
        
        const drone = new Tone.PolySynth(Tone.Synth, {
            oscillator: { type: "fatsine", spread: 20, count: 3 },
            envelope: { attack: 4, decay: 2, sustain: 1, release: 8 }
        }).connect(padFilter);
        drone.volume.value = -18; // Keep it subtle and sweet
        this.synths.push(drone);

        // 2. Sweet Crystal Arpeggiator (Starlight droplets)
        const delay = new Tone.PingPongDelay("8n.", 0.6).connect(masterReverb);
        const pluck = new Tone.PolySynth(Tone.FMSynth, {
            harmonicity: 3,
            modulationIndex: 2,
            oscillator: { type: "sine" },
            envelope: { attack: 0.02, decay: 0.3, sustain: 0.1, release: 1.5 },
            modulation: { type: "square" },
            modulationEnvelope: { attack: 0.01, decay: 0.1, sustain: 0, release: 0.1 }
        }).connect(delay);
        pluck.volume.value = -22; // Very gentle crystal sounds
        this.synths.push(pluck);

        // 3. Deep Cinematic Bass (Grounding the galaxy)
        const bassFilter = new Tone.Filter(150, "lowpass").toDestination();
        const bass = new Tone.Synth({
            oscillator: { type: "triangle" },
            envelope: { attack: 1, decay: 1, sustain: 1, release: 5 }
        }).connect(bassFilter);
        bass.volume.value = -14;
        this.synths.push(bass);

        if(!this.isMuted) {
            this.startAmbientMusic(drone, pluck, bass);
        }
    }

    startAmbientMusic(drone, pluck, bass) {
        // Melodious, uplifting, majestic chord progression (e.g. Fmaj9 -> Cmaj9 -> Am11 -> G6)
        // Creating a sense of wonder, discovery, and limitless potential
        const progressions = [
            { chords: ["F3", "A3", "C4", "E4", "G4"], bass: "F2", duration: "2m" }, // Fmaj9
            { chords: ["C3", "E3", "G3", "B3", "D4"], bass: "C2", duration: "2m" }, // Cmaj9
            { chords: ["A2", "C3", "E3", "G3", "D4"], bass: "A1", duration: "2m" }, // Am11
            { chords: ["G2", "B2", "D3", "E3", "A3"], bass: "G1", duration: "2m" }  // G6/9
        ];
        
        let progIndex = 0;

        // Play the lush pad and sub bass
        Tone.Transport.scheduleRepeat(time => {
            const current = progressions[progIndex];
            drone.triggerAttackRelease(current.chords, "2m", time);
            bass.triggerAttackRelease(current.bass, "2m", time);
            
            progIndex = (progIndex + 1) % progressions.length;
        }, "2m");

        // Random sweet crystalline arpeggiations synchronized with current chord
        Tone.Transport.scheduleRepeat(time => {
            if(Math.random() > 0.4) {
                // Pick notes from the currently playing chord safely
                const currentChord = progressions[progIndex === 0 ? progressions.length - 1 : progIndex - 1].chords;
                const pick = currentChord[Math.floor(Math.random() * currentChord.length)];
                // Shift up an octave for the twinkle effect
                const octaveUpNote = pick.charAt(0) + (parseInt(pick.charAt(1)) + 1).toString();
                // Random velocity for human feel
                pluck.triggerAttackRelease(octaveUpNote, "16n", time, Math.random() * 0.5 + 0.3);
            }
        }, "8n"); // Fast sparkling arps

        Tone.Transport.bpm.value = 75; // Slow, majestically paced
        Tone.Transport.start();
    }

    toggleMute() {
        this.isMuted = !this.isMuted;
        localStorage.setItem('eduGalaxyMuted', this.isMuted.toString());
        this.updateToggleButton();
        
        if(typeof Tone !== 'undefined') {
            Tone.Destination.mute = this.isMuted;
            if(!this.isInitialized && !this.isMuted) this.initAudio();
        }
    }

    updateToggleButton() {
        const btn = document.getElementById('audio-toggle-btn');
        if (btn) btn.innerHTML = this.isMuted ? '<i class="fas fa-volume-mute"></i>' : '<i class="fas fa-volume-up"></i>';
    }

    // High Quality UI Sound Effects
    playSfx(type) {
        if(this.isMuted || !this.isInitialized || typeof Tone === 'undefined') return;
        
        if(type === 'click') {
            // High-tech glass click
            const synth = new Tone.MembraneSynth({
                pitchDecay: 0.05,
                octaves: 4,
                oscillator: { type: 'sine' },
                envelope: { attack: 0.001, decay: 0.4, sustain: 0.01, release: 0.1 }
            }).toDestination();
            synth.volume.value = -20;
            synth.triggerAttackRelease("C6", "32n");
        } else if (type === 'laser') {
            // Intense Sci-Fi Laser Pew Pew
            const synth = new Tone.Synth({
                oscillator: { type: 'sawtooth' },
                envelope: { attack: 0.01, decay: 0.2, sustain: 0, release: 0.2 }
            }).toDestination();
            // Fast pitch drop
            synth.frequency.rampTo("C2", 0.2);
            synth.volume.value = -12;
            synth.triggerAttackRelease("C6", "8n");
        } else if (type === 'correct') {
            // Bright sparkling success chime
            const synth = new Tone.PolySynth(Tone.Synth, {
                oscillator: { type: 'triangle' },
                envelope: { attack: 0.01, decay: 0.3, sustain: 0.1, release: 1 }
            }).toDestination();
            synth.volume.value = -12;
            synth.triggerAttackRelease(["C5", "E5", "G5", "C6"], "8n");
        } else if (type === 'wrong') {
            const synth = new Tone.FMSynth({
                modulationIndex: 5,
                oscillator: { type: 'square' },
                modulation: { type: 'triangle' },
                envelope: { attack: 0.01, decay: 0.3, sustain: 0.1, release: 0.5 }
            }).toDestination();
            synth.volume.value = -15;
            synth.triggerAttackRelease("C2", "8n");
        }
    }
}

const audioEngine = new AdvancedAudioEngine();

// ==========================================
// 3. AI VOICEOVER (Web Speech SDK)
// ==========================================
class AIVoice {
    constructor() {
        this.synth = window.speechSynthesis;
    }
    speak(text) {
        if (audioEngine.isMuted) return;
        this.synth.cancel();
        let u = new SpeechSynthesisUtterance(text);
        u.pitch = 0.8; // Cyber voice
        u.rate = 1.1;
        this.synth.speak(u);
    }
}
const aiVoice = new AIVoice();


// ==========================================
// 4. GSAP PAGE LOGIC
// ==========================================
document.addEventListener('DOMContentLoaded', () => {
    
    // Boot sequence logging
    const bootLog = document.getElementById('boot-log');
    if (bootLog) {
        const msgs = ["[SYSTEM] WebGL Pipeline OK", "[SYSTEM] Advanced Harmonic Engine Online", "[AI] Neural matrix synchronized", "[LINK] Reality Bridge Established..."];
        msgs.forEach((m, i) => {
            setTimeout(() => bootLog.innerHTML += m + "<br>", i * 500);
        });
    }

    // Attach click audio globally
    document.querySelectorAll('.btn, .btn-primary, .btn-secondary, a, .subject-lab-card, .badge-card, .mode-tab').forEach(el => {
        el.addEventListener('mousedown', () => audioEngine.playSfx('click'));
        // 3D Magnetic Hover Effect
        el.addEventListener('mousemove', (e) => {
            const rect = el.getBoundingClientRect();
            const x = e.clientX - rect.left; 
            const y = e.clientY - rect.top;
            const cx = rect.width / 2;
            const cy = rect.height / 2;
            const rotX = ((y - cy) / cy) * -10; // Max 10deg rotation
            const rotY = ((x - cx) / cx) * 10;
            gsap.to(el, {
                rotationX: rotX, 
                rotationY: rotY, 
                z: 30, // pop out
                transformPerspective: 800,
                duration: 0.4, 
                ease: "power2.out"
            });
        });
        el.addEventListener('mouseleave', () => {
            gsap.to(el, { rotationX: 0, rotationY: 0, z: 0, duration: 0.6, ease: "bounce.out" });
        });
    });

    const toggleBtn = document.getElementById('audio-toggle-btn');
    if (toggleBtn) toggleBtn.addEventListener('click', () => audioEngine.toggleMute());

    initAdvancedWebGL();

    // GSAP Cinematic Page Entrance
    if (typeof gsap !== 'undefined') {
        gsap.set('#page-content', { opacity: 0, y: 40, scale: 0.98, rotationX: 5, transformPerspective: 1000 });
        gsap.to('#page-content', { 
            opacity: 1, 
            y: 0, 
            scale: 1, 
            rotationX: 0,
            duration: 1.5, 
            delay: 0.5,
            ease: "expo.out"
        });
        
        // Glitch effect on hovers
        document.querySelectorAll('.btn-primary').forEach(btn => {
            btn.addEventListener('mouseenter', () => gsap.to(btn, {skewX: -5, duration: 0.1, yoyo: true, repeat: 1}));
        });
    }

    // Quiz Logic
    if (document.querySelector('.quiz-container')) setupQuiz();
    
    // Leaderboard
    if (document.querySelector('.leaderboard-table')) aiVoice.speak("Displaying top tier cadets.");
});

function setupQuiz() {
    const questions = document.querySelectorAll('.question-card');
    let currentIndex = 0;

    if (questions.length > 0) {
        questions[0].classList.add('active');
        playQuestionVoice(questions[0]);
    }

    document.querySelectorAll('.option-label input[type="radio"]').forEach(radio => {
        radio.addEventListener('change', function() {
            audioEngine.playSfx('click');
            const currentCard = this.closest('.question-card');
            
            setTimeout(() => {
                if (currentIndex < questions.length - 1) {
                    currentCard.classList.remove('active');
                    currentIndex++;
                    questions[currentIndex].classList.add('active');
                    playQuestionVoice(questions[currentIndex]);
                    
                    if(blackHole) {
                        // Increase time uniform to make black hole spin faster with each question
                        gsap.to(blackHole.material.uniforms.time, { value: "+=2.0", duration: 1 });
                    }
                } else {
                    aiVoice.speak("Hyperspace transmission ready.");
                    document.querySelector('.quiz-submit').scrollIntoView();
                }
            }, 500);
        });
    });
}

function playQuestionVoice(cardEl) {
    const textEl = cardEl.querySelector('.question-text');
    if (textEl) aiVoice.speak("Parameter: " + textEl.innerText);
}

// ==========================================
// 5. CONFETTI SYSTEM
// ==========================================
function launchConfetti(x, y, count = 60) {
    const colors = ['#f97316','#a855f7','#06b6d4','#10b981','#fbbf24','#f43f5e','#fff'];
    for (let i = 0; i < count; i++) {
        const el = document.createElement('div');
        el.style.cssText = `
            position:fixed; z-index:99999; pointer-events:none;
            left:${x}px; top:${y}px;
            width:${Math.random()*8+4}px; height:${Math.random()*8+4}px;
            background:${colors[Math.floor(Math.random()*colors.length)]};
            border-radius:${Math.random() > 0.5 ? '50%' : '2px'};
            opacity:1;
        `;
        document.body.appendChild(el);
        const angle = Math.random() * Math.PI * 2;
        const speed = Math.random() * 6 + 3;
        const vx = Math.cos(angle) * speed;
        const vy = Math.sin(angle) * speed - 4;
        let px = x, py = y, gravity = 0.3, life = 1;
        function tick() {
            px += vx; py += vy + gravity; gravity += 0.15; life -= 0.02;
            el.style.left = px + 'px';
            el.style.top = py + 'px';
            el.style.opacity = life;
            el.style.transform = `rotate(${px*2}deg)`;
            if (life > 0) requestAnimationFrame(tick);
            else el.remove();
        }
        requestAnimationFrame(tick);
    }
}

// Full-screen confetti shower (for big achievements)
function confettiShower() {
    for (let i = 0; i < 5; i++) {
        setTimeout(() => {
            launchConfetti(Math.random() * window.innerWidth, -10, 40);
        }, i * 200);
    }
}

// ==========================================
// 6. TOAST NOTIFICATION SYSTEM
// ==========================================
function showToast(message, type = 'success', duration = 3500) {
    const container = getOrCreateToastContainer();
    const toast = document.createElement('div');
    const icon = type === 'success' ? '✅' : type === 'achievement' ? '🏆' : type === 'xp' ? '⚡' : '❌';
    toast.className = `edu-toast edu-toast-${type}`;
    toast.innerHTML = `<span class="toast-icon">${icon}</span><span class="toast-msg">${message}</span>`;
    toast.style.cssText = `
        display:flex; align-items:center; gap:12px; padding:14px 20px;
        background:${type==='success'?'rgba(16,185,129,0.95)':type==='achievement'?'rgba(168,85,247,0.95)':type==='xp'?'rgba(249,115,22,0.95)':'rgba(239,68,68,0.95)'};
        backdrop-filter:blur(20px); border-radius:16px; color:#fff;
        font-weight:700; font-size:0.95rem; box-shadow:0 8px 32px rgba(0,0,0,0.4);
        transform:translateX(100%); transition:transform 0.4s cubic-bezier(0.34,1.56,0.64,1);
        margin-bottom:10px; max-width:320px;
    `;
    container.appendChild(toast);
    requestAnimationFrame(() => { toast.style.transform = 'translateX(0)'; });
    setTimeout(() => {
        toast.style.transform = 'translateX(120%)';
        setTimeout(() => toast.remove(), 400);
    }, duration);
}

function getOrCreateToastContainer() {
    let c = document.getElementById('toast-container');
    if (!c) {
        c = document.createElement('div');
        c.id = 'toast-container';
        c.style.cssText = 'position:fixed;bottom:24px;right:24px;z-index:100000;display:flex;flex-direction:column;align-items:flex-end;';
        document.body.appendChild(c);
    }
    return c;
}

// ==========================================
// 7. SCROLL-REVEAL (IntersectionObserver)
// ==========================================
(function initScrollReveal() {
    const style = document.createElement('style');
    style.textContent = `
        .reveal { opacity:0; transform:translateY(30px); transition:opacity 0.7s ease, transform 0.7s cubic-bezier(0.4,0,0.2,1); }
        .reveal.revealed { opacity:1; transform:none; }
        .reveal-left { opacity:0; transform:translateX(-40px); transition:opacity 0.7s ease, transform 0.7s cubic-bezier(0.4,0,0.2,1); }
        .reveal-left.revealed { opacity:1; transform:none; }
        .reveal-scale { opacity:0; transform:scale(0.85); transition:opacity 0.6s ease, transform 0.6s cubic-bezier(0.34,1.56,0.64,1); }
        .reveal-scale.revealed { opacity:1; transform:none; }
    `;
    document.head.appendChild(style);

    function observe() {
        const targets = document.querySelectorAll('.step-card, .feature-hex, .subject-lab-card, .badge-card, .stat-card-new, .activity-item, .char-strip-card');
        targets.forEach((el, i) => {
            el.classList.add('reveal');
            el.style.transitionDelay = `${(i % 6) * 0.08}s`;
        });

        const io = new IntersectionObserver((entries) => {
            entries.forEach(e => { if (e.isIntersecting) { e.target.classList.add('revealed'); io.unobserve(e.target); } });
        }, { threshold: 0.1 });

        document.querySelectorAll('.reveal, .reveal-left, .reveal-scale').forEach(el => io.observe(el));
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', observe);
    } else {
        observe();
    }
})();

// ==========================================
// 8. ACHIEVEMENT BADGE HOVER TOOLTIPS
// ==========================================
document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('.badge-card[title]').forEach(badge => {
        badge.addEventListener('mouseenter', (e) => {
            const tip = document.createElement('div');
            tip.className = 'badge-tooltip';
            tip.textContent = e.target.getAttribute('title');
            tip.style.cssText = `
                position:fixed; z-index:50000; padding:8px 14px; background:rgba(10,10,30,0.95);
                border:1px solid rgba(255,255,255,0.2); border-radius:10px; color:#fff;
                font-size:0.8rem; font-weight:600; pointer-events:none; max-width:200px;
                box-shadow:0 8px 24px rgba(0,0,0,0.5);
                left:${e.clientX}px; top:${e.clientY - 50}px;
            `;
            document.body.appendChild(tip);
            badge._tip = tip;
        });
        badge.addEventListener('mouseleave', (e) => {
            if (badge._tip) { badge._tip.remove(); badge._tip = null; }
        });
    });
});
