<script>
  import { onMount } from "svelte";
  import * as d3 from "d3";

  /*********************************
   * 🔧 CONFIG
   *********************************/
  export let DATA_URL = "/second_serve_overall.csv";
  export let TOP_K = 15;
  export let DURATION_PER_YEAR = 2000; 
  export let START_YEAR = 1991;
  export let END_YEAR = 2024;

  const WIDTH = 900;
  const HEIGHT = 550;
  const MARGIN = { top: 40, right: 100, bottom: 20, left: 180 };
  const BAR_HEIGHT = 32;

  let data = [];
  let currentYear = START_YEAR;
  let ticker; 
  let interpolatedData = [];
  
  // Storage for processed cumulative data
  let cumulativeDataByYear = new Map(); 
  let playerRanksByYear = new Map();

  // Scales & Colors
  // Max value is now the highest cumulative sum reached by anyone in the final year
  let maxGlobalValue = 0;
  $: xScale = d3.scaleLinear().domain([0, maxGlobalValue]).range([0, WIDTH - MARGIN.left - MARGIN.right]);
  const colorScale = d3.scaleOrdinal(d3.schemeTableau10);

  onMount(async () => {
    const raw = await d3.csv(DATA_URL, d3.autoType);
    data = raw;
    
    // 1. Calculate Cumulative Sums
    const players = Array.from(new Set(data.map(d => d.player)));
    const years = d3.range(START_YEAR, END_YEAR + 1);
    
    // Helper to store running totals
    let runningTotals = {}; 
    players.forEach(p => runningTotals[p] = 0);

    years.forEach(year => {
      const yearRows = data.filter(d => d.year === year);
      
      // Update running totals with matches_2nd_w from this year
      yearRows.forEach(row => {
        runningTotals[row.player] += (row.matches_2nd_w || 0);
      });

      // Create a snapshot of all players and their current total
      const snapshot = players.map(p => ({
        player: p,
        cumulativeValue: runningTotals[p]
      }))
      .sort((a, b) => b.cumulativeValue - a.cumulativeValue);

      cumulativeDataByYear.set(year, snapshot);

      // Store ranks for this snapshot
      const ranks = new Map();
      snapshot.forEach((d, i) => ranks.set(d.player, i));
      playerRanksByYear.set(year, ranks);

      // Track the highest value for the X-axis scale
      const yearMax = d3.max(snapshot, d => d.cumulativeValue);
      if (yearMax > maxGlobalValue) maxGlobalValue = yearMax;
    });

    updateInterpolatedData(START_YEAR);
  });

  function updateInterpolatedData(yearFloat) {
    const yearLow = Math.floor(yearFloat);
    const yearHigh = Math.min(END_YEAR, yearLow + 1);
    const t = yearFloat - yearLow; 

    const d0 = cumulativeDataByYear.get(yearLow) || [];
    const d1 = cumulativeDataByYear.get(yearHigh) || d0;
    
    const r0 = playerRanksByYear.get(yearLow) || new Map();
    const r1 = playerRanksByYear.get(yearHigh) || r0;

    // Use players who have at least some wins to keep the list manageable
    interpolatedData = d0
      .map(start => {
        const end = d1.find(d => d.player === start.player) || start;
        
        const val = start.cumulativeValue + (end.cumulativeValue - start.cumulativeValue) * t;
        
        const rank0 = r0.get(start.player);
        const rank1 = r1.get(start.player);
        const interpolatedRank = rank0 + (rank1 - rank0) * t;

        return {
          player: start.player,
          value: val,
          rank: interpolatedRank
        };
      })
      .filter(d => d.rank < TOP_K + 0.5 && d.value > 0)
      .sort((a, b) => a.rank - b.rank);
    
    currentYear = yearLow;
  }

  function startRace() {
    if (ticker) ticker.stop();
    let startAt = currentYear >= END_YEAR ? START_YEAR : currentYear;
    const totalDuration = (END_YEAR - startAt) * DURATION_PER_YEAR;

    ticker = d3.timer(elapsed => {
      const p = Math.min(1, elapsed / totalDuration);
      const t = startAt + p * (END_YEAR - startAt);

      if (t >= END_YEAR) {
        updateInterpolatedData(END_YEAR);
        ticker.stop();
        ticker = null;
      } else {
        updateInterpolatedData(t);
      }
    });
  }

  function stopRace() {
    if (ticker) {
      ticker.stop();
      ticker = null;
    }
  }
</script>

<style>
  .container {
    display: flex;
    flex-direction: column;
    align-items: center;
    padding: 2rem;
    background: #fff;
  }
  svg {
    font-family: system-ui, -apple-system, sans-serif;
    overflow: visible;
  }
  .label {
    font-size: 13px;
    text-anchor: end;
    fill: #333;
    font-weight: 600;
  }
  .value {
    font-size: 12px;
    font-weight: 700;
    fill: #444;
  }
  .year-text {
    font-size: 100px;
    font-weight: 900;
    fill: #f3f3f3;
    text-anchor: end;
    pointer-events: none;
  }
  .title {
    font-size: 24px;
    font-weight: 800;
    margin-bottom: 10px;
    color: #222;
  }
  .controls {
    margin-top: 30px;
    display: flex;
    gap: 15px;
    align-items: center;
  }
  button {
    padding: 10px 24px;
    cursor: pointer;
    border-radius: 8px;
    border: 1px solid #ddd;
    background: #222;
    color: white;
    font-weight: bold;
  }
  button:hover { background: #444; }
  .year-display {
    font-family: monospace;
    font-size: 1.2rem;
    font-weight: bold;
  }
</style>

<div class="container">
  <div class="title">Total 2nd Serve Points Won (Cumulative)</div>
  
  <svg width={WIDTH} height={HEIGHT}>
    <g transform="translate({MARGIN.left}, {MARGIN.top})">
      
      <text class="year-text" x={WIDTH - MARGIN.left} y={HEIGHT - MARGIN.top - 20}>
        {currentYear}
      </text>

      {#each interpolatedData as d (d.player)}
        <g transform="translate(0, {d.rank * BAR_HEIGHT})">
          <rect
            fill={colorScale(d.player)}
            height={BAR_HEIGHT - 6}
            width={xScale(d.value)}
            rx="4"
          />

          <text class="label" x="-12" y={(BAR_HEIGHT - 6) / 2} dy=".35em">
            {d.player}
          </text>

          <text class="value" x={xScale(d.value) + 10} y={(BAR_HEIGHT - 6) / 2} dy=".35em">
            {Math.round(d.value).toLocaleString()}
          </text>
        </g>
      {/each}
    </g>
  </svg>

  <div class="controls">
    {#if !ticker}
      <button on:click={startRace}>▶ Play</button>
    {:else}
      <button on:click={stopRace} style="background: #eee; color: #333;">⏸ Pause</button>
    {/if}
    <div class="year-display">{currentYear}</div>
  </div>
</div>