<script>
  import { onMount } from 'svelte';
  import * as d3 from 'd3';

  let rawData = [];
  let filteredData = [];
  let decadeLookup = new Map();
  let hoveredPoint = null;
  
  const width = 1000; // Increased width to accommodate right legend
  const height = 400;
  const margin = { top: 60, right: 150, bottom: 40, left: 60 };

  onMount(async () => {
    rawData = await d3.csv('/tournaments_overall_all_years.csv');
  });

  $: {
    filteredData = rawData
      .filter(d => +d.year >= 1975 && d.tourney_level?.trim() === 'G')
      .map(d => ({
        year: new Date(+d.year, 0, 1),
        yearNum: +d.year,
        tournament: d.tournament,
        avg_diff_games: +d.avg_diff_games,
        decade: Math.floor(+d.year / 10) * 10
      }));

    const groups = d3.groups(filteredData, d => d.tournament, d => d.decade);
    decadeLookup = new Map();
    groups.forEach(([tourney, decadeBuckets]) => {
      decadeBuckets.forEach(([dec, values]) => {
        decadeLookup.set(`${tourney}-${dec}`, d3.mean(values, v => v.avg_diff_games));
      });
    });
  }

  $: series = d3.group(filteredData, d => d.tournament);
  $: tournamentList = Array.from(series.keys());

  let x, y, color, delaunay;
  $: if (filteredData.length > 0) {
    x = d3.scaleTime()
      .domain(d3.extent(filteredData, d => d.year))
      .range([margin.left, width - margin.right]);

    y = d3.scaleLinear()
      .domain(d3.extent(filteredData, d => d.avg_diff_games))
      .nice()
      .range([height - margin.bottom, margin.top]);

    color = d3.scaleOrdinal(d3.schemeCategory10).domain(tournamentList);
    delaunay = d3.Delaunay.from(filteredData, d => x(d.year), d => y(d.avg_diff_games));
  }

  $: line = d3.line().x(d => x(d.year)).y(d => y(d.avg_diff_games));

  // Determine which decade to show in the right legend
  // Defaults to the most recent decade in the data if not hovering
  $: displayDecade = hoveredPoint ? hoveredPoint.decade : 2020; 

  function handleMouseMove(event) {
    if (!delaunay) return;
    const [mx, my] = d3.pointer(event);
    const index = delaunay.find(mx, my);
    const closest = filteredData[index];
    if (Math.hypot(x(closest.year) - mx, y(closest.avg_diff_games) - my) < 50) {
      hoveredPoint = closest;
    } else {
      hoveredPoint = null;
    }
  }
</script>

<div class="chart-container">
  <svg {width} {height} on:mouseleave={() => hoveredPoint = null}>
    {#if x && y && filteredData.length > 0}
      
      <g class="legend-top" transform="translate({margin.left}, 20)">
        {#each tournamentList as tournament, i}
          <g transform="translate({i * 150}, 0)" opacity={hoveredPoint && hoveredPoint.tournament !== tournament ? 0.2 : 1}>
            <rect width="10" height="10" fill={color(tournament)} rx="2" />
            <text x="15" y="10" font-size="12" font-weight="500">{tournament}</text>
          </g>
        {/each}
      </g>

      <g class="legend-right" transform="translate({width - margin.right + 20}, {margin.top})">
        <text y="-10" font-size="12" font-weight="bold" fill="#374151">{displayDecade}s Averages</text>
        {#each tournamentList as tournament, i}
          {@const avg = decadeLookup.get(`${tournament}-${displayDecade}`)}
          <g transform="translate(0, {i * 25})" opacity={hoveredPoint && hoveredPoint.tournament !== tournament ? 0.3 : 1}>
            <circle r="4" fill={color(tournament)} cx="-10" cy="12" />
            <text y="15" font-size="11" fill="#4b5563">{tournament}:</text>
            <text x="100" y="15" font-size="11" font-weight="bold" text-anchor="end" fill="#111827">
              {avg ? avg.toFixed(3) : 'N/A'}
            </text>
          </g>
        {/each}
      </g>

      <g class="axis">
        {#each y.ticks(5) as tick}
          <g transform="translate(0, {y(tick)})">
            <line x1={margin.left} x2={width - margin.right} stroke="#f3f4f6" />
            <text x={margin.left - 10} text-anchor="end" dominant-baseline="middle" font-size="11" fill="#9ca3af">{tick}</text>
          </g>
        {/each}
        {#each x.ticks(10) as tick}
          <text x={x(tick)} y={height - margin.bottom + 20} text-anchor="middle" font-size="11" fill="#9ca3af">{tick.getFullYear()}</text>
        {/each}
      </g>

      {#each Array.from(series) as [tournament, values]}
        <path
          d={line(values)}
          fill="none"
          stroke={color(tournament)}
          stroke-width={hoveredPoint?.tournament === tournament ? 4 : 2}
          opacity={hoveredPoint ? (hoveredPoint.tournament === tournament ? 1 : 0.1) : 0.7}
          style="transition: all 0.2s ease; pointer-events: none;"
        />
      {/each}

      <rect {width} {height} fill="transparent" on:mousemove={handleMouseMove} />

      {#if hoveredPoint}
        <circle cx={x(hoveredPoint.year)} cy={y(hoveredPoint.avg_diff_games)} r="6" fill={color(hoveredPoint.tournament)} stroke="white" stroke-width="2" pointer-events="none" />
      {/if}

    {/if}
  </svg>
</div>

<style>
  .chart-container { width: 100%; display: flex; justify-content: center; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1); }
  svg { overflow: visible; }
</style>