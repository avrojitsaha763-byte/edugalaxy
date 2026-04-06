/* holo-audio.js — EduGalaxy GOD MODE Ambient & AI Voice Engine */
(function() {
  'use strict';

  let audioCtx = null;
  let ambientOsc = null;
  let isMuted = false;

  // 1. AI VOICEOVERS MAPPING
  const voiceMap = {
    'page-home': "Welcome to the Battle Bridge, Commander.",
    'page-login': "Security Clearance required. Initialize retinal scan.",
    'page-signup': "Academy Enlistment active. Enter your pilot credentials.",
    'page-dashboard': "Galactic Command Center online. Scanning for new missions.",
    'page-learn': "Jedi Archives decrypted. Select a sector for training.",
    'page-interactive': "Holo-Deck training bay initialized. Focus on your path.",
    'page-leaderboard': "Senate Hall of Champions synchronized. Reviewing top telemetry.",
    'page-profile': "Pilot Dossier accessed. Biometric data current.",
    'page-games': "Battle Simulator Arena engaged. Prepare for combat simulations."
  };

  function playVoiceOver() {
    const bodyClass = document.body.className.split(' ').find(c => c.startsWith('page-'));
    const text = voiceMap[bodyClass];
    if (!text) return;

    // Wait for user interaction to play audio (browser policy)
    const speak = () => {
      const utterance = new SpeechSynthesisUtterance(text);
      const voices = window.speechSynthesis.getVoices();
      
      // Try to find a more robotic/techy voice if available
      const techVoice = voices.find(v => v.name.includes('Google UK English Male') || v.name.includes('Samantha'));
      if (techVoice) utterance.voice = techVoice;
      
      utterance.pitch = 0.85; // Slightly lower for a "command" feel
      utterance.rate = 0.95;  // Slightly slower for clarity
      utterance.volume = 0.6;
      window.speechSynthesis.speak(utterance);
    };

    if (window.speechSynthesis.getVoices().length > 0) {
      speak();
    } else {
      window.speechSynthesis.onvoiceschanged = speak;
    }
  }

  // 2. WEB AUDIO AMBIENT HUM
  function initAmbientHum() {
    if (audioCtx) return;
    audioCtx = new (window.AudioContext || window.webkitAudioContext)();
    
    // Low hum oscillator
    ambientOsc = audioCtx.createOscillator();
    const gainNode = audioCtx.createGain();
    const filter = audioCtx.createBiquadFilter();

    ambientOsc.type = 'sine';
    ambientOsc.frequency.setValueAtTime(55, audioCtx.currentTime); // Low A

    filter.type = 'lowpass';
    filter.frequency.setValueAtTime(200, audioCtx.currentTime);

    gainNode.gain.setValueAtTime(0, audioCtx.currentTime);
    gainNode.gain.linearRampToValueAtTime(0.08, audioCtx.currentTime + 2); // Fade in

    ambientOsc.connect(filter);
    filter.connect(gainNode);
    gainNode.connect(audioCtx.destination);

    ambientOsc.start();

    // Subtle LFO for "holographic oscillation"
    const lfo = audioCtx.createOscillator();
    const lfoGain = audioCtx.createGain();
    lfo.type = 'sine';
    lfo.frequency.setValueAtTime(0.5, audioCtx.currentTime);
    lfoGain.gain.setValueAtTime(5, audioCtx.currentTime);
    lfo.connect(lfoGain);
    lfoGain.connect(ambientOsc.frequency);
    lfo.start();
  }

  // Interaction trigger (browsers block audio until first click)
  function handleFirstInteraction() {
    initAmbientHum();
    playVoiceOver();
    document.removeEventListener('click', handleFirstInteraction);
  }

  document.addEventListener('click', handleFirstInteraction);
  
  // Auto-play attempt (some systems allow if volume 0 or low)
  window.addEventListener('load', () => {
    // We still show a small HUD element to indicate audio status
    const audioStatus = document.createElement('div');
    Object.assign(audioStatus.style, {
      position: 'fixed', bottom: '20px', left: '20px', zIndex: 100001,
      fontFamily: 'Orbitron, sans-serif', fontSize: '0.65rem', color: '#00f3ff',
      background: 'rgba(0,0,0,0.8)', padding: '6px 12px', borderRadius: '4px',
      border: '1px solid rgba(0,243,255,0.3)', cursor: 'pointer',
      display: 'flex', alignItems: 'center', gap: '8px', opacity: 0.7
    });
    audioStatus.innerHTML = '<span>🔊</span> NEURAL LINK: STANDBY (CLICK TO SYNC)';
    document.body.appendChild(audioStatus);

    audioStatus.onclick = () => {
      if (!audioCtx) {
        handleFirstInteraction();
        audioStatus.innerHTML = '<span>🔊</span> NEURAL LINK: ACTIVE';
        audioStatus.style.borderColor = '#39ff14';
        audioStatus.style.color = '#39ff14';
      } else {
        // Toggle mute logic could go here
      }
    };
  });

})();
