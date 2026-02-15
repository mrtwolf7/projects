<script>
  import { onMount } from "svelte";
  import * as d3 from "d3";

  /*********************************
   * 🔧 CONFIG & STATE
   *********************************/
  export let DATA_URL = "/second_serve_overall.csv";
  export let TOP_K = 15; 
  let MIN_MATCHES = 300; // Controlled by slider

  let rawData = [];
  let careerLeaderboard = [];
  let hoveredPlayer = null;

  const WIDTH = 900;
  const HEIGHT = 500;
  const MARGIN = { top: 60, right: 30, bottom: 120, left: 60 };

  // 1. DATA PROCESSING (Reactive to MIN_MATCHES)
  $: {
    if (rawData.length > 0) {
      const playerStats = d3.rollup(
        rawData,
        v => {
          const totalMatches = d3.sum(v, d => d.matches_w);
          const weightedSum = d3.sum(v, d => d.perc_2nd_w * d.matches_w);
          return {
            weightedAvg: totalMatches > 0 ? weightedSum / totalMatches : 0,
            totalMatches: totalMatches
          };
        },
        d => d.player
      );

      careerLeaderboard = Array.from(playerStats, ([player, stats]) => ({
        player,
        ...stats
      }))
      .filter(d => d.totalMatches >= MIN_MATCHES)
      .sort((a, b) => b.weightedAvg - a.weightedAvg)
      .slice(0, TOP_K);
    }
  }

  // 2. SCALES (Reactive to data changes)
  $: yScale = d3.scaleLinear()
    .domain([
      d3.min(careerLeaderboard, d => d.weightedAvg) - 0.5 || 48, 
      d3.max(careerLeaderboard, d => d.weightedAvg) + 0.5 || 60
    ])
    .range([HEIGHT - MARGIN.bottom, MARGIN.top]);

  $: xScale = d3.scaleBand()
    .domain(careerLeaderboard.map(d => d.player))
    .range([MARGIN.left, WIDTH - MARGIN.right])
    .padding(0.3);

  const colorScale = d3.scaleOrdinal(d3.schemeTableau10);

  onMount(async () => {
    rawData = await d3.csv(DATA_URL, d3.autoType);
  });
</script>

<style>
  .chart-container {
    width: 100%;
    max-width: 900px;
    margin: 1rem auto;
    font-family: system-ui, sans-serif;
  }

  .controls {
    display: flex;
    flex-direction: column;
    align-items: center;
    margin-bottom: 2rem;
    gap: 0.5rem;
    background: #f8f9fa;
    padding: 1rem;
    border-radius: 8px;
  }

  input[type="range"] { width: 300px; cursor: pointer; }

  svg { background: #fff; overflow: visible; }

  .bar {
    transition: all 0.2s ease;
    cursor: pointer;
  }

  .bar.dimmed { opacity: 0.3; }

  .label { font-size: 11px; font-weight: 600; fill: #333; }
  
  .value-text {
    font-size: 12px;
    font-weight: 800;
    fill: #222;
    text-anchor: middle;
  }

  .axis-label { font-size: 10px; fill: #999; }

  .tooltip-info {
    font-size: 14px;
    font-weight: bold;
    fill: #2c3e50;
    text-anchor: middle;
  }
</style>

<div class="chart-container">
  <div class="controls">
    <label for="matches">Minimum Career Wins: <strong>{MIN_MATCHES}</strong></label>
    <input 
      id="matches" 
      type="range" 
      min="50" 
      max="1000" 
      step="50" 
      bind:value={MIN_MATCHES} 
    />
    <small>Showing Top {careerLeaderboard.length} Players</small>
  </div>

  <svg width={WIDTH} height={HEIGHT}>
    <g>
      {#each yScale.ticks(5) as tick}
        <line 
          x1={MARGIN.left} x2={WIDTH - MARGIN.right} 
          y1={yScale(tick)} y2={yScale(tick)} 
          stroke="#f0f0f0" 
        />
        <text class="axis-label" x={MARGIN.left - 10} y={yScale(tick)} text-anchor="end" alignment-baseline="middle">
          {tick}%
        </text>
      {/each}
    </g>

    {#each careerLeaderboard as d}
      <g 
        on:mouseenter={() => hoveredPlayer = d} 
        on:mouseleave={() => hoveredPlayer = null}
      >
        <rect
          class="bar"
          class:dimmed={hoveredPlayer && hoveredPlayer.player !== d.player}
          x={xScale(d.player)}
          y={yScale(d.weightedAvg)}
          width={xScale.bandwidth()}
          height={HEIGHT - MARGIN.bottom - yScale(d.weightedAvg)}
          fill={colorScale(d.player)}
          rx="3"
        />
        
        <text 
          class="value-text" 
          x={xScale(d.player) + xScale.bandwidth() / 2} 
          y={yScale(d.weightedAvg) - 10}
        >
          {d.weightedAvg.toFixed(1)}%
        </text>

        <text
          class="label"
          transform="translate({xScale(d.player) + xScale.bandwidth() / 2}, {HEIGHT - MARGIN.bottom + 15}) rotate(45)"
          text-anchor="start"
        >
          {d.player}
        </text>
      </g>
    {/each}

    {#if hoveredPlayer}
      <text 
        class="tooltip-info" 
        x={WIDTH / 2} 
        y={MARGIN.top - 20}
      >
        {hoveredPlayer.player}: {hoveredPlayer.totalMatches} matches won
      </text>
    {/if}
  </svg>
</div>