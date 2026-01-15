<script>
  import { onMount } from 'svelte';
  import * as d3 from 'd3';

  let rawData = [];
  let aggregatedDecades = [];
  let currentDecade = 1980;
  let isPlaying = false;
  let timer;

  const width = 1100;
  const height = 450;
  const margin = { top: 80, right: 200, bottom: 60, left: 60 };

  const rounds = [
    { key: 'fave_ratio_R16', label: 'R16' },
    { key: 'fave_ratio_QF', label: 'QF' },
    { key: 'fave_ratio_SF', label: 'SF' },
    { key: 'fave_ratio_F', label: 'F' }
  ];
  
  const tournaments = ["Wimbledon", "Roland Garros", "US Open", "Australian Open"];
  const decades = [1970, 1980, 1990, 2000, 2010, 2020];

  onMount(async () => {
    const csv = await d3.csv('/tournaments_rounds_all_years.csv');
    
    // Aggregate by decade and tournament
    const grouped = d3.groups(
      csv.filter(d => d.tourney_level === 'G'),
      d => Math.floor(+d.year / 10) * 10,
      d => d.tournament
    );

    aggregatedDecades = grouped.flatMap(([decade, tournamentGroups]) => {
      return tournamentGroups.map(([tournament, entries]) => {
        const result = { decade, tournament };
        rounds.forEach(r => {
          const vals = entries.map(e => +e[r.key]).filter(v => !isNaN(v));
          result[r.key] = vals.length > 0 ? d3.mean(vals) : 0;
        });
        return result;
      });
    });
  });

  // Scales
  $: x0 = d3.scaleBand()
    .domain(tournaments)
    .rangeRound([margin.left, width - margin.right])
    .paddingInner(0.3);

  $: x1 = d3.scaleBand()
    .domain(rounds.map(r => r.label))
    .rangeRound([0, x0.bandwidth()])
    .padding(0.1);

  $: y = d3.scaleLinear().domain([0, 1.1]).range([height - margin.bottom, margin.top]);

  $: color = d3.scaleOrdinal()
    .domain(rounds.map(r => r.label))
    .range(["#bae6fd", "#7dd3fc", "#38bdf8", "#0284c7"]);

  // Current view data
  $: displayData = aggregatedDecades.filter(d => d.decade === currentDecade);

  // Global Round Averages for the sidebar and Delta calculation
  $: globalRoundAverages = rounds.map(r => {
    const values = displayData.map(d => d[r.key]).filter(v => v !== undefined);
    const avg = values.length > 0 ? d3.mean(values) : null;
    return { label: r.label, key: r.key, value: avg };
  });

  function togglePlay() {
    isPlaying = !isPlaying;
    if (isPlaying) {
      timer = setInterval(() => {
        const idx = decades.indexOf(currentDecade);
        if (idx < decades.length - 1) {
          currentDecade = decades[idx + 1];
        } else {
          isPlaying = false;
          clearInterval(timer);
        }
      }, 1500);
    } else {
      clearInterval(timer);
    }
  }
</script>

<div class="container">
  <div class="controls">
    <button on:click={togglePlay} class:active={isPlaying}>
      {isPlaying ? 'Pause' : 'Play Timeline'}
    </button>
    <div class="slider-box">
      <input type="range" min="1970" max="2020" step="10" bind:value={currentDecade} />
      <span class="decade-label">{currentDecade}s</span>
    </div>
  </div>

  <svg {width} {height}>
    {#each [0, 0.25, 0.5, 0.75, 1] as tick}
      <g transform="translate(0, {y(tick)})">
        <line x1={margin.left} x2={width - margin.right} stroke="#f1f5f9" />
        <text x={margin.left - 10} text-anchor="end" dominant-baseline="middle" font-size="11" fill="#94a3b8">{tick}</text>
      </g>
    {/each}

    {#each tournaments as tourney}
      {@const tourneyData = displayData.find(d => d.tournament === tourney)}
      <g transform="translate({x0(tourney)}, 0)">
        {#each rounds as round}
          {@const val = tourneyData ? tourneyData[round.key] : 0}
          {@const globalRef = globalRoundAverages.find(g => g.key === round.key)}
          {@const globalAvg = globalRef ? globalRef.value : null}
          
          <rect
            x={x1(round.label)}
            y={y(val)}
            width={x1.bandwidth()}
            height={Math.max(0, y(0) - y(val))}
            fill={color(round.label)}
            rx="2"
            style="transition: all 600ms ease-in-out;"
          />

          <text
            x={x1(round.label) + x1.bandwidth() / 2}
            y={y(val) - 6}
            text-anchor="middle"
            font-size="10"
            font-weight="700"
            fill="#475569"
            style="transition: all 600ms ease-in-out;"
          >
            {val ? val.toFixed(2) : '0.00'}
          </text>

          {#if tourneyData && globalAvg !== null}
            {@const delta = val - globalAvg}
            <text
              x={x1(round.label) + x1.bandwidth() / 2}
              y={y(val) - 20}
              text-anchor="middle"
              font-size="9"
              font-weight="800"
              fill={delta >= 0 ? "#10b981" : "#ef4444"}
              style="transition: all 600ms ease-in-out;"
            >
              {delta >= 0 ? '▲' : '▼'}{Math.abs(delta).toFixed(2)}
            </text>
          {/if}
        {/each}
        
        <text x={x0.bandwidth()/2} y={height - margin.bottom + 25} text-anchor="middle" font-size="13" font-weight="800" fill="#1e293b">
          {tourney}
        </text>
      </g>
    {/each}

    <g transform="translate({width - margin.right + 40}, {margin.top})">
      <text y="-25" font-size="14" font-weight="900" fill="#0f172a">Decade Global Avg</text>
      {#each globalRoundAverages as g, i}
        <g transform="translate(0, {i * 55})">
          <rect width="4" height="30" fill={color(g.label)} rx="2" />
          <text x="12" y="10" font-size="11" font-weight="bold" fill="#64748b">{g.label}</text>
          <text x="12" y="28" font-size="18" font-weight="900" fill="#0f172a">
            {g.value !== null ? g.value.toFixed(3) : '---'}
          </text>
        </g>
      {/each}
    </g>
  </svg>
</div>

<style>
  .container { font-family: system-ui, -apple-system, sans-serif; display: flex; flex-direction: column; align-items: center; }
  .controls { display: flex; align-items: center; gap: 2rem; margin: 1.5rem 0; background: #f8fafc; padding: 1rem 2rem; border-radius: 50px; border: 1px solid #e2e8f0; }
  .slider-box { display: flex; align-items: center; gap: 1rem; }
  .decade-label { font-size: 1.5rem; font-weight: 900; color: #0284c7; min-width: 80px; }
  
  button { 
    padding: 10px 20px; 
    border-radius: 25px; 
    border: none; 
    background: #0284c7; 
    color: white; 
    font-weight: 700; 
    cursor: pointer; 
    transition: transform 0.1s;
  }
  button:active { transform: scale(0.95); }
  button.active { background: #ef4444; }

  input[type="range"] { width: 200px; cursor: pointer; }
  svg { background: white; border-radius: 16px; filter: drop-shadow(0 4px 6px rgb(0 0 0 / 0.05)); }
</style>