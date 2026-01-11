<script>
  import { onMount } from 'svelte';
  import * as d3 from 'd3';

  let rawData = [];
  let filteredData = [];
  let hoveredPoint = null;
  
  const width = 900;
  const height = 400;
  const margin = { top: 60, right: 60, bottom: 40, left: 60 };

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
        fave_ratio: +d.fave_ratio
      }));
  }

  $: series = d3.group(filteredData, d => d.tournament);

  let x, y, color, delaunay;

  $: if (filteredData.length > 0) {
    x = d3.scaleTime()
      .domain(d3.extent(filteredData, d => d.year))
      .range([margin.left, width - margin.right]);

    y = d3.scaleLinear()
      .domain(d3.extent(filteredData, d => d.fave_ratio))
      .nice()
      .range([height - margin.bottom, margin.top]);

    color = d3.scaleOrdinal(d3.schemeCategory10)
      .domain(Array.from(series.keys()));

    delaunay = d3.Delaunay.from(filteredData, d => x(d.year), d => y(d.fave_ratio));
  }

  $: line = d3.line()
    .x(d => x(d.year))
    .y(d => y(d.fave_ratio));

  function handleMouseMove(event) {
    if (!delaunay) return;
    const [mx, my] = d3.pointer(event);
    const index = delaunay.find(mx, my);
    const closest = filteredData[index];

    const dx = x(closest.year) - mx;
    const dy = y(closest.fave_ratio) - my;
    // Only show tooltip if mouse is within 50px of a point
    hoveredPoint = Math.hypot(dx, dy) < 50 ? closest : null;
  }
</script>

<div class="chart-container">
  <svg {width} {height} on:mouseleave={() => hoveredPoint = null}>
    {#if x && y && filteredData.length > 0}
      
      <g class="legend" transform="translate({margin.left}, 20)">
        {#each Array.from(series.keys()) as tournament, i}
          <g transform="translate({i * 150}, 0)" opacity={hoveredPoint && hoveredPoint.tournament !== tournament ? 0.2 : 1}>
            <rect width="12" height="12" fill={color(tournament)} rx="2" />
            <text x="18" y="10" font-size="12" fill="#374151" font-weight="500">{tournament}</text>
          </g>
        {/each}
      </g>

      <g class="axis y-axis">
        {#each y.ticks(5) as tick}
          <g transform="translate(0, {y(tick)})">
            <line x1={margin.left} x2={width - margin.right} stroke="#f3f4f6" />
            <text x={margin.left - 10} text-anchor="end" dominant-baseline="middle" font-size="12" fill="#9ca3af">{tick}</text>
          </g>
        {/each}
      </g>

      <g class="axis x-axis" transform="translate(0, {height - margin.bottom})">
        <line x1={margin.left} x2={width - margin.right} stroke="#9ca3af" />
        {#each x.ticks(10) as tick}
          <g transform="translate({x(tick)}, 0)">
            <line y2="6" stroke="#9ca3af" />
            <text y="20" text-anchor="middle" font-size="12" fill="#9ca3af">
              {tick.getFullYear()}
            </text>
          </g>
        {/each}
      </g>

      {#each Array.from(series) as [tournament, values]}
        <path
          d={line(values)}
          fill="none"
          stroke={color(tournament)}
          stroke-width={hoveredPoint?.tournament === tournament ? 4 : 2}
          opacity={hoveredPoint ? (hoveredPoint.tournament === tournament ? 1 : 0.1) : 0.8}
          style="transition: all 0.1s ease; pointer-events: none;"
        />
      {/each}

      <rect 
        {width} {height} 
        fill="transparent" 
        on:mousemove={handleMouseMove}
      />

      {#if hoveredPoint}
        <g transform="translate({x(hoveredPoint.year)}, {y(hoveredPoint.fave_ratio)})" pointer-events="none">
          <circle r="6" fill={color(hoveredPoint.tournament)} stroke="white" stroke-width="2" />
          <g transform="translate(10, -40)">
            <rect width="140" height="45" fill="white" stroke="#ddd" rx="4" />
            <text x="8" y="18" font-size="11" font-weight="bold" fill="#111827">{hoveredPoint.tournament}</text>
            <text x="8" y="34" font-size="11" fill="#4b5563">{hoveredPoint.yearNum}: {hoveredPoint.fave_ratio.toFixed(3)}</text>
          </g>
        </g>
      {/if}

    {/if}
  </svg>
</div>

<style>
  .chart-container { width: 100%; display: flex; justify-content: center; margin-top: 2rem;}
  svg { overflow: visible; cursor: crosshair; }
</style>