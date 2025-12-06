<script>
	// Animated mentalist figure component
</script>

<div class="mentalist-container">
	<svg class="mentalist-svg" viewBox="0 0 200 300" xmlns="http://www.w3.org/2000/svg">
		<!-- Mystical glow background -->
		<defs>
			<filter id="glow">
				<feGaussianBlur stdDeviation="3" result="coloredBlur"/>
				<feMerge>
					<feMergeNode in="coloredBlur"/>
					<feMergeNode in="SourceGraphic"/>
				</feMerge>
			</filter>
			<radialGradient id="headGradient" cx="50%" cy="30%">
				<stop offset="0%" style="stop-color:#4a2c5a;stop-opacity:1" />
				<stop offset="100%" style="stop-color:#2d1b3d;stop-opacity:1" />
			</radialGradient>
			<radialGradient id="bodyGradient" cx="50%" cy="50%">
				<stop offset="0%" style="stop-color:#3a2547;stop-opacity:1" />
				<stop offset="100%" style="stop-color:#1a0f26;stop-opacity:1" />
			</radialGradient>
		</defs>
		
		<!-- Floating particles -->
		<circle class="particle particle-1" cx="50" cy="50" r="2" fill="#a78bfa" opacity="0.6"/>
		<circle class="particle particle-2" cx="150" cy="80" r="1.5" fill="#8b5cf6" opacity="0.5"/>
		<circle class="particle particle-3" cx="80" cy="200" r="2" fill="#c084fc" opacity="0.4"/>
		<circle class="particle particle-4" cx="120" cy="250" r="1.5" fill="#a78bfa" opacity="0.6"/>
		
		<!-- Body/Robe -->
		<ellipse class="body" cx="100" cy="170" rx="38" ry="55" fill="url(#bodyGradient)" filter="url(#glow)"/>
		
		<!-- Head -->
		<ellipse class="head" cx="100" cy="80" rx="35" ry="40" fill="url(#headGradient)"/>
		
		<!-- Wavy hair -->
		<path class="hair hair-1" d="M 65 70 Q 60 50, 55 60 Q 50 70, 55 80 Q 60 90, 65 85" 
			fill="#1a0a1a" stroke="#2d1b3d" stroke-width="1"/>
		<path class="hair hair-2" d="M 70 65 Q 65 45, 60 55 Q 55 65, 60 75 Q 65 85, 70 80" 
			fill="#1a0a1a" stroke="#2d1b3d" stroke-width="1"/>
		<path class="hair hair-3" d="M 135 70 Q 140 50, 145 60 Q 150 70, 145 80 Q 140 90, 135 85" 
			fill="#1a0a1a" stroke="#2d1b3d" stroke-width="1"/>
		<path class="hair hair-4" d="M 130 65 Q 135 45, 140 55 Q 145 65, 140 75 Q 135 85, 130 80" 
			fill="#1a0a1a" stroke="#2d1b3d" stroke-width="1"/>
		<path class="hair hair-5" d="M 75 75 Q 70 60, 75 70 Q 80 80, 85 75" 
			fill="#1a0a1a" stroke="#2d1b3d" stroke-width="1"/>
		<path class="hair hair-6" d="M 125 75 Q 130 60, 125 70 Q 120 80, 115 75" 
			fill="#1a0a1a" stroke="#2d1b3d" stroke-width="1"/>
		
		<!-- Eyes with mystical glow -->
		<ellipse class="eye eye-left" cx="90" cy="85" rx="4" ry="6" fill="#8b5cf6"/>
		<ellipse class="eye eye-right" cx="110" cy="85" rx="4" ry="6" fill="#8b5cf6"/>
		<circle class="eye-glow eye-glow-left" cx="90" cy="85" r="8" fill="#a78bfa" opacity="0.3"/>
		<circle class="eye-glow eye-glow-right" cx="110" cy="85" r="8" fill="#a78bfa" opacity="0.3"/>
		
		<!-- Mystical third eye -->
		<circle class="third-eye" cx="100" cy="75" r="3" fill="#c084fc" opacity="0.8"/>
		<circle class="third-eye-glow" cx="100" cy="75" r="12" fill="#a78bfa" opacity="0.2"/>
		
		<!-- Legs in padmasana (lotus) - extended horizontally by 40% -->
		<path class="leg leg-left" d="M 75 205 C 38 210, 27 225, 53 235 C 79 245, 127 245, 143 238 C 152 234, 149 228, 133 225" 
			fill="url(#bodyGradient)"/>
		<path class="leg leg-right" d="M 125 205 C 162 210, 173 225, 147 235 C 121 245, 73 245, 57 238 C 48 234, 51 228, 67 225" 
			fill="url(#bodyGradient)"/>

		<!-- Mystical energy lines -->
		<path class="energy energy-1" d="M 100 75 Q 85 100, 70 120" stroke="#a78bfa" stroke-width="1.5" 
			fill="none" opacity="0.5" stroke-dasharray="3,3"/>
		<path class="energy energy-2" d="M 100 75 Q 115 100, 130 120" stroke="#a78bfa" stroke-width="1.5" 
			fill="none" opacity="0.5" stroke-dasharray="3,3"/>
	</svg>
</div>

<style>
	.mentalist-container {
		display: flex;
		justify-content: center;
		align-items: center;
		position: relative;
		width: 100%;
		margin: 0 auto;
	}

	.mentalist-svg {
		width: 100%;
		max-width: 280px;
		height: auto;
		aspect-ratio: 2/3;
		filter: drop-shadow(0 0 20px var(--color-primary-glow));
		animation: float 3s ease-in-out infinite;
	}

	@keyframes float {
		0%, 100% {
			transform: translateY(0px);
		}
		50% {
			transform: translateY(-10px);
		}
	}

	.particle {
		animation: float-particle 4s ease-in-out infinite;
	}

	.particle-1 {
		animation-delay: 0s;
	}

	.particle-2 {
		animation-delay: 1s;
	}

	.particle-3 {
		animation-delay: 2s;
	}

	.particle-4 {
		animation-delay: 1.5s;
	}

	@keyframes float-particle {
		0%, 100% {
			transform: translate(0, 0);
			opacity: 0.3;
		}
		50% {
			transform: translate(10px, -20px);
			opacity: 0.8;
		}
	}

	.head {
		animation: head-sway 4s ease-in-out infinite;
		transform-origin: 100px 80px;
	}

	@keyframes head-sway {
		0%, 100% {
			transform: rotate(-2deg);
		}
		50% {
			transform: rotate(2deg);
		}
	}

	.hair {
		animation: hair-wave 2s ease-in-out infinite;
		transform-origin: 100px 80px;
	}

	.hair-1 { animation-delay: 0s; }
	.hair-2 { animation-delay: 0.2s; }
	.hair-3 { animation-delay: 0.1s; }
	.hair-4 { animation-delay: 0.3s; }
	.hair-5 { animation-delay: 0.15s; }
	.hair-6 { animation-delay: 0.25s; }

	@keyframes hair-wave {
		0%, 100% {
			transform: translateX(0) rotate(0deg);
		}
		50% {
			transform: translateX(2px) rotate(3deg);
		}
	}

	.eye-glow {
		animation: eye-pulse 2s ease-in-out infinite;
	}

	@keyframes eye-pulse {
		0%, 100% {
			opacity: 0.2;
			r: 8;
		}
		50% {
			opacity: 0.5;
			r: 12;
		}
	}

	.third-eye-glow {
		animation: third-eye-pulse 3s ease-in-out infinite;
	}

	@keyframes third-eye-pulse {
		0%, 100% {
			opacity: 0.1;
			r: 12;
		}
		50% {
			opacity: 0.4;
			r: 18;
		}
	}

	.energy {
		animation: energy-flow 2s linear infinite;
		stroke-dashoffset: 0;
	}

	@keyframes energy-flow {
		0% {
			stroke-dashoffset: 0;
			opacity: 0.3;
		}
		50% {
			opacity: 0.7;
		}
		100% {
			stroke-dashoffset: -20;
			opacity: 0.3;
		}
	}

	.hand {
		animation: hand-float 3s ease-in-out infinite;
	}

	.hand-left {
		animation-delay: 0s;
	}

	.hand-right {
		animation-delay: 0.5s;
	}

	@keyframes hand-float {
		0%, 100% {
			transform: translateY(0);
		}
		50% {
			transform: translateY(-2px);
		}
	}
</style>

