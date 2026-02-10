<script>
  import { onMount } from "svelte";
  import * as d3 from "d3";

  /*********************************
   * 🔧 CONFIG
   *********************************/
  export let DATA_URL = "/second_serve_overall.csv";
  export let TOP_K = 15; 
  export let MIN_MATCHES = 300;

  const WIDTH = 900;
  const HEIGHT = 500;
  const MARGIN = { top: 40, right: 20, bottom: 100, left: 60 };

  let careerLeaderboard = [];
  let isLoading = true;

  // Scales
  $: yScale = d3.scaleLinear()
    // Finding the min value to start the axis slightly below the lowest player
    .domain([
      d3.min(careerLeaderboard, d => d.weightedAvg) - 1 || 45, 
      d3.max(careerLeaderboard, d => d.weightedAvg) + 1 || 60
    ])
    .range([HEIGHT - MARGIN.bottom, MARGIN.top]);

  $: xScale = d3.scaleBand()
    .domain(careerLeaderboard.map(d => d.player))
    .range([MARGIN.left, WIDTH - MARGIN.right])
    .padding(0.2);

  const colorScale = d3.scaleOrdinal(d3.schemeTableau10);

  onMount(async () => {
    const data = await d3.csv(DATA_URL, d3.autoType);

    const playerStats = d3.rollup(
      data,
      v => {
        const totalMatches = d3.sum(v, d => d.matches_tot);
        const weightedSum = d3.sum(v, d => d.perc_2nd_overall * d.matches_tot);
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

    isLoading = false;
  });
</script>

<style>
  .chart-container {
    width: 100%;
    max-width: 900px;
    margin: 2rem auto;
    font-family: system-ui, sans-serif;
  }

  .title { text-align: center; margin-bottom: 1rem; }
  
  svg { 
    background: #fdfdfd; 
    overflow: visible; 
  }

  .bar {
    transition: opacity 0.2s;
  }
  .bar:hover { opacity: 0.8; }

  .label {
    font-size: 12px;
    font-weight: 600;
    fill: #333;
  }

  .value-text {
    font-size: 11px;
    font-weight: bold;
    fill: #444;
    text-anchor: middle;
  }

  .axis-label {
    font-size: 10px;
    fill: #999;
  }
</style>

<div class="chart-container">
  <div class="title">
    <h2>All-Time 2nd Serve Leaders</h2>
    <p>Weighted Career Average (Min. {MIN_MATCHES} Matches)</p>
  </div>

  {#if isLoading}
    <p>Loading data...</p>
  {:else}
    <svg width={WIDTH} height={HEIGHT}>
      <g>
        {#each yScale.ticks(5) as tick}
          <line 
            x1={MARGIN.left} x2={WIDTH - MARGIN.right} 
            y1={yScale(tick)} y2={yScale(tick)} 
            stroke="#eee" 
          />
          <text class="axis-label" x={MARGIN.left - 10} y={yScale(tick)} text-anchor="end" alignment-baseline="middle">
            {tick}%
          </text>
        {/each}
      </g>

      {#each careerLeaderboard as d}
        <g>
          <rect
            class="bar"
            x={xScale(d.player)}
            y={yScale(d.weightedAvg)}
            width={xScale.bandwidth()}
            height={HEIGHT - MARGIN.bottom - yScale(d.weightedAvg)}
            fill={colorScale(d.player)}
            rx="4"
          />
          
          <text 
            class="value-text" 
            x={xScale(d.player) + xScale.bandwidth() / 2} 
            y={yScale(d.weightedAvg) - 8}
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
    </svg>
  {/if}
</div>