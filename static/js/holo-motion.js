/* holo-motion.js — EduGalaxy GOD MODE Universal Motion Engine */
(function() {
  'use strict';

  /* ── 1. LIGHTSABER CURSOR TRAIL ───────────────────────────── */
  const trailCanvas = document.createElement('canvas');
  trailCanvas.id = 'cursor-trail-canvas';
  Object.assign(trailCanvas.style, {
    position: 'fixed', top: 0, left: 0,
    width: '100vw', height: '100vh',
    pointerEvents: 'none', zIndex: 99999,
    mixBlendMode: 'screen'
  });
  document.body.appendChild(trailCanvas);

  const tCtx = trailCanvas.getContext('2d');
  let trailPoints = [];
  let mouseX = 0, mouseY = 0;

  function resizeTrailCanvas() {
    trailCanvas.width = window.innerWidth;
    trailCanvas.height = window.innerHeight;
  }
  resizeTrailCanvas();
  window.addEventListener('resize', resizeTrailCanvas);

  document.addEventListener('mousemove', e => {
    mouseX = e.clientX; mouseY = e.clientY;
    trailPoints.push({ x: mouseX, y: mouseY, age: 0, size: 6 });
    if (trailPoints.length > 40) trailPoints.shift();
  });

  function drawTrail() {
    tCtx.clearRect(0, 0, trailCanvas.width, trailCanvas.height);
    trailPoints.forEach((pt, i) => {
      pt.age++;
      const alpha = Math.max(0, 1 - pt.age / 40);
      const size = pt.size * alpha;
      const grad = tCtx.createRadialGradient(pt.x, pt.y, 0, pt.x, pt.y, size * 3);
      grad.addColorStop(0, `rgba(0,243,255,${alpha})`);
      grad.addColorStop(0.5, `rgba(157,78,221,${alpha * 0.5})`);
      grad.addColorStop(1, 'rgba(0,0,0,0)');
      tCtx.beginPath();
      tCtx.arc(pt.x, pt.y, size * 3, 0, Math.PI * 2);
      tCtx.fillStyle = grad;
      tCtx.fill();
    });
    trailPoints = trailPoints.filter(p => p.age < 40);
    requestAnimationFrame(drawTrail);
  }
  drawTrail();

  /* ── 2. 3D HOLO-CARD TILT ON MOUSE MOVE ────────────────────── */
  function applyHoloTilt(card, e) {
    const rect = card.getBoundingClientRect();
    const cx = rect.left + rect.width / 2;
    const cy = rect.top + rect.height / 2;
    const dx = (e.clientX - cx) / (rect.width / 2);
    const dy = (e.clientY - cy) / (rect.height / 2);
    const rotX = -dy * 15;
    const rotY = dx * 15;
    const glowX = 50 + dx * 30;
    const glowY = 50 + dy * 30;
    card.style.transform = `perspective(800px) rotateX(${rotX}deg) rotateY(${rotY}deg) scale3d(1.03,1.03,1.03)`;
    card.style.background = `radial-gradient(circle at ${glowX}% ${glowY}%, rgba(0,243,255,0.12) 0%, rgba(10,25,47,0.85) 60%)`;
    card.style.boxShadow = `0 0 30px rgba(0,243,255,0.4), 0 ${rotX * 0.5}px ${Math.abs(rotX) * 2}px rgba(157,78,221,0.2)`;
  }

  function resetHoloCard(card) {
    card.style.transform = 'perspective(800px) rotateX(0deg) rotateY(0deg) scale3d(1,1,1)';
    card.style.background = '';
    card.style.boxShadow = '';
  }

  function initHoloCards() {
    const cards = document.querySelectorAll('.holo-card, .glass-panel, .feature-card, .subject-card, .stat-card');
    cards.forEach(card => {
      card.style.transition = 'transform 0.1s ease-out, box-shadow 0.1s ease-out';
      card.style.willChange = 'transform';
      card.addEventListener('mousemove', e => applyHoloTilt(card, e));
      card.addEventListener('mouseleave', () => resetHoloCard(card));
    });
  }

  /* ── 3. TRIPLE-LAYER PARALLAX BACKGROUND ───────────────────── */
  const bgDeep = document.querySelector('.bg-deep');
  const bgMid = document.querySelector('.bg-mid');
  const bgFocus = document.querySelector('.bg-focus');

  document.addEventListener('mousemove', e => {
    const xFrac = (e.clientX / window.innerWidth - 0.5);
    const yFrac = (e.clientY / window.innerHeight - 0.5);
    
    // Different speeds for realistic depth (Slowest = Deepest)
    if (bgDeep) bgDeep.style.transform = `scale(1.1) translate(${xFrac * 15}px, ${yFrac * 10}px)`;
    if (bgMid)  bgMid.style.transform  = `scale(1.15) translate(${xFrac * 35}px, ${yFrac * 20}px)`;
    if (bgFocus) bgFocus.style.transform = `scale(1.2) translate(${xFrac * 60}px, ${yFrac * 40}px)`;

    // Update global mouse positions
    mouseX = e.clientX; mouseY = e.clientY;
  });

  /* ── 4. PERSPECTIVE STARFIELD ENGINE ───────────────────────── */
  const starCanvas = document.getElementById('parallax-starfield');
  if (starCanvas) {
    Object.assign(starCanvas.style, {
      position: 'fixed', top: 0, left: 0, width: '100vw', height: '100vh',
      pointerEvents: 'none', zIndex: -2, opacity: 0.4
    });
    const sCtx = starCanvas.getContext('2d');
    let stars = [];
    const STAR_COUNT = 150;

    function initStars() {
      starCanvas.width = window.innerWidth;
      starCanvas.height = window.innerHeight;
      stars = [];
      for (let i = 0; i < STAR_COUNT; i++) {
        stars.push({
          x: Math.random() * starCanvas.width - starCanvas.width / 2,
          y: Math.random() * starCanvas.height - starCanvas.height / 2,
          z: Math.random() * starCanvas.width,
          o: Math.random() * 0.5 + 0.5
        });
      }
    }
    initStars();
    window.addEventListener('resize', initStars);

    function drawStars() {
      sCtx.fillStyle = '#000';
      sCtx.fillRect(0, 0, starCanvas.width, starCanvas.height);
      const cx = starCanvas.width / 2;
      const cy = starCanvas.height / 2;

      stars.forEach(s => {
        s.z -= 1.5; // Star speed
        if (s.z <= 0) s.z = starCanvas.width;

        const sx = (s.x / s.z) * cx + cx;
        const sy = (s.y / s.z) * cy + cy;
        const size = (1 - s.z / starCanvas.width) * 2;
        
        if (sx < 0 || sx > starCanvas.width || sy < 0 || sy > starCanvas.height) return;

        sCtx.beginPath();
        sCtx.arc(sx, sy, size, 0, Math.PI * 2);
        sCtx.fillStyle = `rgba(0, 243, 255, ${s.o})`;
        sCtx.fill();
      });
      requestAnimationFrame(drawStars);
    }
    drawStars();
  }

  /* ── 5. DEVICE GYROSCOPE PARALLAX (Mobile) ──────────────────── */
  if (window.DeviceOrientationEvent) {
    window.addEventListener('deviceorientation', e => {
      const x = (e.gamma || 0) / 30;
      const y = (e.beta  || 0) / 30;
      const cards = document.querySelectorAll('.holo-card, .glass-panel');
      cards.forEach(card => {
        card.style.transform = `perspective(800px) rotateX(${y * -8}deg) rotateY(${x * 8}deg)`;
      });
      if (bgDeep) bgDeep.style.transform = `scale(1.1) translate(${x * 10}px, ${y * 8}px)`;
      if (bgMid)  bgMid.style.transform  = `scale(1.15) translate(${x * 25}px, ${y * 15}px)`;
    });
  }

  /* ── 6. FLOATING PARTICLES CANVAS ──────────────────────────── */
  const partCanvas = document.createElement('canvas');
  partCanvas.id = 'particle-canvas';
  Object.assign(partCanvas.style, {
    position: 'fixed', top: 0, left: 0,
    width: '100vw', height: '100vh',
    pointerEvents: 'none', zIndex: -1, opacity: '0.6'
  });
  document.body.insertBefore(partCanvas, document.body.firstChild);
  const pCtx = partCanvas.getContext('2d');

  function resizePartCanvas() {
    partCanvas.width = window.innerWidth;
    partCanvas.height = window.innerHeight;
  }
  resizePartCanvas();
  window.addEventListener('resize', resizePartCanvas);

  const PARTICLE_COUNT = 60;
  const particles = [];
  for (let i = 0; i < PARTICLE_COUNT; i++) {
    particles.push({
      x: Math.random() * window.innerWidth,
      y: Math.random() * window.innerHeight,
      r: Math.random() * 2 + 0.3,
      vx: (Math.random() - 0.5) * 0.4,
      vy: (Math.random() - 0.5) * 0.4,
      color: Math.random() > 0.6 ? '#00f3ff' : Math.random() > 0.5 ? '#9d4edd' : '#39ff14',
      pulse: Math.random() * Math.PI * 2
    });
  }

  function drawParticles() {
    pCtx.clearRect(0, 0, partCanvas.width, partCanvas.height);
    particles.forEach(p => {
      p.pulse += 0.02;
      p.x += p.vx; p.y += p.vy;
      if (p.x < 0) p.x = partCanvas.width;
      if (p.x > partCanvas.width) p.x = 0;
      if (p.y < 0) p.y = partCanvas.height;
      if (p.y > partCanvas.height) p.y = 0;
      const alpha = 0.4 + Math.sin(p.pulse) * 0.3;
      pCtx.beginPath();
      pCtx.arc(p.x, p.y, p.r, 0, Math.PI * 2);
      pCtx.globalAlpha = alpha;
      pCtx.fillStyle = p.color;
      pCtx.shadowBlur = 8;
      pCtx.shadowColor = p.color;
      pCtx.fill();
      pCtx.globalAlpha = 1;
      pCtx.shadowBlur = 0;
    });
    requestAnimationFrame(drawParticles);
  }
  drawParticles();

  /* ── 7. HYPERSPACE PAGE ENTRY ANIMATION ─────────────────────── */
  const warpOverlay = document.createElement('div');
  warpOverlay.id = 'warp-entry';
  Object.assign(warpOverlay.style, {
    position: 'fixed', inset: 0, zIndex: 100000,
    background: 'radial-gradient(ellipse at center, #ffffff 0%, #00f3ff 20%, #1a0a3e 60%, #000 100%)',
    opacity: 1, pointerEvents: 'none',
    transition: 'opacity 0.8s cubic-bezier(0.4,0,0.2,1)'
  });
  document.body.appendChild(warpOverlay);
  requestAnimationFrame(() => {
    setTimeout(() => { warpOverlay.style.opacity = '0'; }, 100);
    setTimeout(() => { warpOverlay.remove(); }, 900);
  });

  /* ── INIT ON DOM READY ───────────────────────────────────────── */
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initHoloCards);
  } else {
    initHoloCards();
    setTimeout(initHoloCards, 1000);
  }
})();
