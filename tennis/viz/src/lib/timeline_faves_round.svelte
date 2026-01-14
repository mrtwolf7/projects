<script>
  import { onMount } from 'svelte';
  import * as d3 from 'd3';

  let data = [];
  let currentYear = 1980;
  let isPlaying = false;
  let timer;

  const width = 900;
  const height = 400;
  const margin = { top: 60, right: 30, bottom: 60, left: 60 };

  // Round metadata for mapping columns and display
  const rounds = [
    { key: 'fave_ratio_R16', label: 'R16' },
    { key: 'fave_ratio_QF', label: 'QF' },
    { key: 'fave_ratio_SF', label: 'SF' },
    { key: 'fave_ratio_F', label: 'F' }
  ];
  const tournaments = ["Wimbledon", "Roland Garros", "US Open", "Australian Open"];

  onMount(async () => {
    // We only load Grand Slams and ensure year is a number
    const raw = await d3.csv('/tournaments_rounds_all_years.csv');
    data = raw.filter(d => d.tourney_level === 'G').map(d => ({
      ...d,
      year: +d.year
    }));
  });

  // Scales
  $: x0 = d3.scaleBand()
    .domain(tournaments)
    .rangeRound([margin.left, width - margin.right])
    .paddingInner(0.2);

  $: x1 = d3.scaleBand()
    .domain(rounds.map(r => r.label))
    .rangeRound([0, x0.bandwidth()])
    .padding(0.05);

  $: y = d3.scaleLinear().domain([0, 1]).range([height - margin.bottom, margin.top]);

  $: color = d3.scaleOrdinal()
    .domain(rounds.map(r => r.label))
    .range(["#bae6fd", "#7dd3fc", "#38bdf8", "#0284c7"]); // Light to Dark Blues

  // Animation logic
  function togglePlay() {
    isPlaying = !isPlaying;
    if (isPlaying) {
      timer = setInterval(() => {
        if (currentYear < 2024) currentYear++;
        else isPlaying = false;
      }, 400);
    } else {
      clearInterval(timer);
    }
  }

  $: displayData = data.filter(d => d.year === currentYear);
</script>

<div class="controls">
  <button on:click={togglePlay} class:playing={isPlaying}>
    {isPlaying ? 'Pause' : 'Play History'}
  </button>
  <input type="range" min="1975" max="2024" bind:value={currentYear} />
  <span class="year-display">{currentYear}</span>
</div>

<svg {width} {height}>
  {#each y.ticks(5) as tick}
    <g transform="translate(0, {y(tick)})">
      <line x1={margin.left} x2={width - margin.right} stroke="#f1f5f9" />
      <text x={margin.left - 10} text-anchor="end" dominant-baseline="middle" font-size="12" fill="#94a3b8">{tick}</text>
    </g>
  {/each}

  {#each tournaments as tourney}
    {@const tourneyData = displayData.find(d => d.tournament === tourney)}
    <g transform="translate({x0(tourney)}, 0)">
      {#each rounds as round}
        {@const val = tourneyData ? +tourneyData[round.key] : 0}
        <rect
          x={x1(round.label)}
          y={y(val)}
          width={x1.bandwidth()}
          height={y(0) - y(val)}
          fill={color(round.label)}
          rx="2"
          style="transition: all 400ms cubic-bezier(0.4, 0, 0.2, 1);"
        />
      {/each}
      
      <text x={x0.bandwidth()/2} y={height - margin.bottom + 25} text-anchor="middle" font-weight="600" fill="#334155">
        {tourney}
      </text>
    </g>
  {/each}

  <g transform="translate({width - margin.right - 150}, 30)">
    {#each rounds as round, i}
      <g transform="translate(0, {i * 15})">
        <rect width="10" height="10" fill={color(round.label)} rx="2" />
        <text x="15" y="9" font-size="10" fill="#64748b">{round.label}</text>
      </g>
    {/each}
  </g>
</svg>

<style>
  .controls { display: flex; align-items: center; gap: 1rem; margin: 1rem 0; font-family: sans-serif; }
  .year-display { font-size: 1.5rem; font-weight: bold; color: #0284c7; width: 4rem; }
  button { padding: 0.5rem 1rem; cursor: pointer; border-radius: 4px; border: 1px solid #ccc; background: white; }
  button.playing { background: #f0f9ff; border-color: #0284c7; }
  input { flex-grow: 1; max-width: 300px; }
  svg { background: #fff; border-radius: 8px; }
</style>