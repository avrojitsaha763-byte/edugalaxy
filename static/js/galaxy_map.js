/**
 * galaxy_map.js - Three.js Subject Galaxy Navigation
 * Subjects are planets in a high-tech 3D map.
 */

class GalaxyMap {
    constructor(containerId, subjects) {
        this.container = document.getElementById(containerId);
        this.subjects = subjects;
        this.scene = new THREE.Scene();
        this.camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 2000);
        this.renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
        this.raycaster = new THREE.Raycaster();
        this.mouse = new THREE.Vector2();
        this.planets = [];
        
        this.init();
    }

    init() {
        this.renderer.setSize(window.innerWidth, window.innerHeight);
        this.renderer.setPixelRatio(window.devicePixelRatio);
        this.container.appendChild(this.renderer.domElement);

        this.camera.position.z = 600;

        // Lighting
        const ambientLight = new THREE.AmbientLight(0x404040, 2);
        this.scene.add(ambientLight);

        const pointLight = new THREE.PointLight(0x00ff87, 2, 1000);
        pointLight.position.set(0, 0, 100);
        this.scene.add(pointLight);

        // Subject Planets Creation
        const radius = 350;
        this.subjects.forEach((subject, index) => {
            const angle = (index / this.subjects.length) * Math.PI * 2;
            const x = Math.cos(angle) * radius;
            const y = Math.sin(angle) * (radius * 0.5); // Elliptical orbit
            const z = Math.sin(angle) * 100;

            const planet = this.createPlanet(subject);
            planet.position.set(x, y, z);
            this.scene.add(planet);
            this.planets.push(planet);
        });

        // Stars
        this.createStars();

        window.addEventListener('mousemove', (e) => this.onMouseMove(e));
        window.addEventListener('click', (e) => this.onClick(e));
        window.addEventListener('resize', () => this.onWindowResize());

        this.animate();
    }

    createPlanet(subject) {
        const colors = {
            'math': 0x22d3ee,
            'english': 0x818cf8,
            'science': 0x4ade80,
            'evs': 0x4ade80,
            'gk': 0xfbbf24,
            'sst': 0xf6ad55,
            'hindi': 0xfacc15,
            'computer': 0x00d4ff
        };
        const color = colors[subject.toLowerCase()] || 0xffffff;

        const group = new THREE.Group();

        // Planet Mesh
        const geometry = new THREE.SphereGeometry(30, 32, 32);
        const material = new THREE.MeshPhongMaterial({
            color: color,
            emissive: color,
            emissiveIntensity: 0.2,
            shininess: 50
        });
        const mesh = new THREE.Mesh(geometry, material);
        group.add(mesh);

        // Rings
        const ringGeo = new THREE.RingGeometry(40, 42, 64);
        const ringMat = new THREE.MeshBasicMaterial({ color: color, side: THREE.DoubleSide, transparent: true, opacity: 0.3 });
        const ring = new THREE.Mesh(ringGeo, ringMat);
        ring.rotation.x = Math.PI / 2;
        group.add(ring);

        group.userData = { subject: subject, originalColor: color };
        return group;
    }

    createStars() {
        const geometry = new THREE.BufferGeometry();
        const vertices = [];
        for (let i = 0; i < 2000; i++) {
            vertices.push((Math.random() - 0.5) * 2000, (Math.random() - 0.5) * 2000, (Math.random() - 0.5) * 2000);
        }
        geometry.setAttribute('position', new THREE.Float32BufferAttribute(vertices, 3));
        const material = new THREE.PointsMaterial({ color: 0xffffff, size: 2, sizeAttenuation: true });
        const stars = new THREE.Points(geometry, material);
        this.scene.add(stars);
    }

    onMouseMove(event) {
        this.mouse.x = (event.clientX / window.innerWidth) * 2 - 1;
        this.mouse.y = -(event.clientY / window.innerHeight) * 2 + 1;
    }

    onClick(event) {
        this.raycaster.setFromCamera(this.mouse, this.camera);
        const intersects = this.raycaster.intersectObjects(this.planets, true);

        if (intersects.length > 0) {
            let obj = intersects[0].object;
            while(obj.parent && !obj.userData.subject) {
                obj = obj.parent;
            }
            if(obj.userData.subject) {
                window.location.href = `/learn/interactive?subject=${obj.userData.subject}`;
            }
        }
    }

    onWindowResize() {
        this.camera.aspect = window.innerWidth / window.innerHeight;
        this.camera.updateProjectionMatrix();
        this.renderer.setSize(window.innerWidth, window.innerHeight);
    }

    animate() {
        requestAnimationFrame(() => this.animate());

        // Parallax
        this.camera.position.x += (this.mouse.x * 50 - this.camera.position.x) * 0.05;
        this.camera.position.y += (this.mouse.y * 50 - this.camera.position.y) * 0.05;
        this.camera.lookAt(0, 0, 0);

        this.planets.forEach((planet, i) => {
            planet.rotation.y += 0.01;
            // Hover effect check via raycast in animate? No, just interaction
        });

        this.renderer.render(this.scene, this.camera);
    }
}
