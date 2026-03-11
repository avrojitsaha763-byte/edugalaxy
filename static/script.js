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

    isQuizPage = window.location.pathname.includes('/quiz');

    // Basic Setup
    scene = new THREE.Scene();
    scene.fog = new THREE.FogExp2(0x05010d, 0.0015);

    camera = new THREE.PerspectiveCamera(70, window.innerWidth / window.innerHeight, 0.1, 2000);
    camera.position.z = isQuizPage ? 150 : 300;

    renderer = new THREE.WebGLRenderer({ canvas: canvas, antialias: true, alpha: false });
    renderer.setSize(window.innerWidth, window.innerHeight);
    renderer.setPixelRatio(window.devicePixelRatio);
    renderer.setClearColor(0x05010d, 1);
    
    // Add Lights
    const ambientLight = new THREE.AmbientLight(0x404040, 2);
    scene.add(ambientLight);
    
    const dirLight = new THREE.DirectionalLight(0xffffff, 2);
    dirLight.position.set(50, 50, 100);
    scene.add(dirLight);

    // Context specific 3D Generation
    createParticleSystem();
    if (isQuizPage) {
        createBlackHole();
    } else if (window.location.pathname === '/' || window.location.pathname === '/home') {
        createHighResEarth();
    } else if (window.location.pathname.includes('/dashboard')) {
        createGalaxyMap();
    }

    // EffectComposer Pipeline (Unreal Bloom)
    const renderScene = new THREE.RenderPass(scene, camera);
    const bloomPass = new THREE.UnrealBloomPass(new THREE.Vector2(window.innerWidth, window.innerHeight), 1.5, 0.4, 0.85);
    bloomPass.threshold = 0.2;
    bloomPass.strength = isQuizPage ? 2.5 : 1.2; // Intense bloom for black hole
    bloomPass.radius = 0.5;

    composer = new THREE.EffectComposer(renderer);
    composer.addPass(renderScene);
    composer.addPass(bloomPass);

    // Mouse Parallax & Scroll variables
    let mouseX = 0, mouseY = 0;
    let targetX = 0, targetY = 0;

    document.addEventListener('mousemove', (event) => {
        mouseX = (event.clientX - window.innerWidth / 2);
        mouseY = (event.clientY - window.innerHeight / 2);
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

function createParticleSystem() {
    const starCount = 3000;
    const geometry = new THREE.BufferGeometry();
    const positions = new Float32Array(starCount * 3);
    const colors = new Float32Array(starCount * 3);

    const c1 = new THREE.Color(0x7b2ff7);
    const c2 = new THREE.Color(0x00d4ff);

    for (let i = 0; i < starCount; i++) {
        positions[i*3] = (Math.random() - 0.5) * 2000;
        positions[i*3+1] = (Math.random() - 0.5) * 2000;
        positions[i*3+2] = (Math.random() - 0.5) * 2000;

        const mixed = c1.clone().lerp(c2, Math.random());
        colors[i*3] = mixed.r; colors[i*3+1] = mixed.g; colors[i*3+2] = mixed.b;
    }

    geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));
    geometry.setAttribute('color', new THREE.BufferAttribute(colors, 3));

    const material = new THREE.PointsMaterial({
        size: 2, vertexColors: true, transparent: true, opacity: 0.8,
        blending: THREE.AdditiveBlending, depthWrite: false
    });

    particles = new THREE.Points(geometry, material);
    scene.add(particles);
}

// Procedural Earth using Canvas texture generation
function createHighResEarth() {
    const geo = new THREE.SphereGeometry(60, 64, 64);
    
    // Create a procedural texture to look like a planet
    const canvas = document.createElement('canvas');
    canvas.width = 1024; canvas.height = 512;
    const ctx = canvas.getContext('2d');
    
    // Base ocean
    ctx.fillStyle = '#001133';
    ctx.fillRect(0,0,1024,512);
    
    // Random continents
    ctx.fillStyle = '#00ff87';
    for(let i=0; i<200; i++) {
        ctx.beginPath();
        ctx.arc(Math.random()*1024, Math.random()*512, Math.random()*30, 0, Math.PI*2);
        ctx.fill();
    }
    // Clouds
    ctx.fillStyle = 'rgba(255,255,255,0.3)';
    for(let i=0; i<500; i++) {
        ctx.beginPath();
        ctx.arc(Math.random()*1024, Math.random()*512, Math.random()*20, 0, Math.PI*2);
        ctx.fill();
    }

    const tex = new THREE.CanvasTexture(canvas);
    
    const mat = new THREE.MeshPhongMaterial({
        map: tex,
        bumpMap: tex,
        bumpScale: 2,
        specular: new THREE.Color(0x333333),
        shininess: 15,
        emissive: new THREE.Color(0x0a0a2a),
        emissiveIntensity: 0.5
    });

    earth = new THREE.Mesh(geo, mat);
    earth.position.set(100, 0, -50);
    scene.add(earth);

    // Setup ScrollTrigger for cinematic camera
    if(typeof gsap !== 'undefined' && typeof ScrollTrigger !== 'undefined') {
        gsap.registerPlugin(ScrollTrigger);
        
        gsap.to(camera.position, {
            scrollTrigger: { trigger: "body", start: "top top", end: "bottom bottom", scrub: 1 },
            z: 100,
            x: 50,
            y: -20
        });
        
        gsap.to(earth.rotation, {
            scrollTrigger: { trigger: "body", start: "top top", end: "bottom bottom", scrub: 2 },
            y: Math.PI * 2
        });
    }
}

// Custom GLSL active Black Hole Shader
function createBlackHole() {
    const geo = new THREE.PlaneGeometry(300, 300);
    
    const uniforms = {
        time: { value: 1.0 },
        resolution: { value: new THREE.Vector2(window.innerWidth, window.innerHeight) }
    };

    const mat = new THREE.ShaderMaterial({
        uniforms: uniforms,
        vertexShader: `
            varying vec2 vUv;
            void main() {
                vUv = uv;
                gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
            }
        `,
        fragmentShader: `
            uniform float time;
            varying vec2 vUv;
            
            // Simple procedural black hole accretion disk
            void main() {
                vec2 center = vec2(0.5, 0.5);
                float dist = distance(vUv, center);
                
                // Event horizon
                if (dist < 0.1) {
                    gl_FragColor = vec4(0.0, 0.0, 0.0, 1.0);
                } else {
                    // Accretion disk spinning
                    float angle = atan(vUv.y - center.y, vUv.x - center.x);
                    float spiral = sin(angle * 10.0 - time * 5.0 + dist * 20.0);
                    
                    float intensity = (0.3 - dist) * 3.0;
                    intensity = max(0.0, intensity);
                    
                    float glow = abs(sin(dist * 50.0 - time * 2.0)) * 0.5 + 0.5;
                    
                    // Mix colors (Orange and Purple)
                    vec3 color = mix(vec3(1.0, 0.4, 0.1), vec3(0.5, 0.1, 1.0), spiral * 0.5 + 0.5);
                    
                    gl_FragColor = vec4(color * intensity * glow, 1.0);
                }
            }
        `,
        transparent: true,
        blending: THREE.AdditiveBlending
    });

    blackHole = new THREE.Mesh(geo, mat);
    blackHole.position.z = -50;
    scene.add(blackHole);
}

function createGalaxyMap() {
    // A cool hexagonal grid map for the dashboard
    const geo = new THREE.IcosahedronGeometry(80, 1);
    const mat = new THREE.MeshBasicMaterial({ color: 0x00d4ff, wireframe: true, transparent: true, opacity: 0.3 });
    const globe = new THREE.Mesh(geo, mat);
    scene.add(globe);
    earth = globe; // Reuse earth var for animation loop
}

function animateWebGL() {
    requestAnimationFrame(animateWebGL);
    let delta = clock.getDelta();

    if (particles) {
        particles.rotation.y += 0.0005;
    }

    if (earth && !isQuizPage) {
        earth.rotation.y += 0.002;
    }

    if (blackHole) {
        blackHole.material.uniforms.time.value += delta;
        // Make it spin faster if a specific class is active (e.g. user got wrong answer)
    }

    // Gentle camera drift
    camera.position.x += (Math.sin(clock.getElapsedTime() * 0.5) * 10 - camera.position.x) * 0.02;

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
        
        // 1. Drone Pad
        const filter = new Tone.Filter(800, "lowpass").toDestination();
        const reverb = new Tone.Reverb(4).connect(filter);
        const drone = new Tone.PolySynth(Tone.Synth, {
            oscillator: { type: "sine" },
            envelope: { attack: 2, decay: 1, sustain: 1, release: 4 }
        }).connect(reverb);
        drone.volume.value = -15;
        this.synths.push(drone);

        // 2. Arpeggiator (Plucks)
        const pingPong = new Tone.PingPongDelay("8n", 0.4).toDestination();
        const pluck = new Tone.Synth({
            oscillator: { type: "triangle" },
            envelope: { attack: 0.01, decay: 0.2, sustain: 0, release: 0.2 }
        }).connect(pingPong);
        pluck.volume.value = -20;
        this.synths.push(pluck);

        if(!this.isMuted) {
            this.startAmbientMusic(drone, pluck);
        }
    }

    startAmbientMusic(drone, pluck) {
        // Spacey chord progression depending on page
        let chords = [["C3", "G3", "D4"], ["A2", "E3", "C4"]];
        if (isQuizPage) chords = [["D2", "A2", "F3"], ["Eb2", "Bb2", "Gb3"]]; // Tenser chords

        // Play drone slowly
        Tone.Transport.scheduleRepeat(time => {
            const chord = chords[Math.floor(Math.random() * chords.length)];
            drone.triggerAttackRelease(chord, "2m", time);
        }, "2m");

        // Random arpeggiations for tech feel
        Tone.Transport.scheduleRepeat(time => {
            if(Math.random() > 0.5) {
                const notes = ["C4", "D4", "G4", "A4", "C5"];
                pluck.triggerAttackRelease(notes[Math.floor(Math.random() * notes.length)], "16n", time);
            }
        }, "4n");

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

    // UI Sound Effects
    playSfx(type) {
        if(this.isMuted || !this.isInitialized || typeof Tone === 'undefined') return;
        
        if(type === 'click') {
            const synth = new Tone.MembraneSynth().toDestination();
            synth.volume.value = -15;
            synth.triggerAttackRelease("C5", "32n");
        } else if (type === 'correct') {
            const synth = new Tone.PolySynth().toDestination();
            synth.volume.value = -10;
            synth.triggerAttackRelease(["C5", "E5", "G5"], "8n");
        } else if (type === 'wrong') {
            const synth = new Tone.FMSynth().toDestination();
            synth.volume.value = -10;
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
        const msgs = ["[SYSTEM] WebGL Pipeline OK", "[SYSTEM] Tone.js Synthesis active", "[AI] Neural matrix online", "[LINK] Establishing connection..."];
        msgs.forEach((m, i) => {
            setTimeout(() => bootLog.innerHTML += m + "<br>", i * 500);
        });
    }

    // Attach click audio globally
    document.querySelectorAll('.btn, a').forEach(el => {
        el.addEventListener('mousedown', () => audioEngine.playSfx('click'));
    });

    const toggleBtn = document.getElementById('audio-toggle-btn');
    if (toggleBtn) toggleBtn.addEventListener('click', () => audioEngine.toggleMute());

    initAdvancedWebGL();

    // GSAP Page Entrance
    if (typeof gsap !== 'undefined') {
        gsap.to('#page-content', { opacity: 1, duration: 1.5, delay: 0.5 });
        
        // Glitch effect on hovers
        document.querySelectorAll('.btn-primary').forEach(btn => {
            btn.addEventListener('mouseenter', () => gsap.to(btn, {skewX: -10, duration: 0.1, yoyo: true, repeat: 1}));
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
