<script>
  import { onMount } from 'svelte';
  import * as d3 from 'd3';

  let rawData = [];
  let pieData = [];
  let hoveredSlice = null;

  const width = 1100;
  const radius = 100;

  const categories = ["1", "2", "3", "4", "5", "<=10", "10+"];
  
  // Categorical colors (Tableau 10 inspired)
  const color = d3.scaleOrdinal()
    .domain(categories)
    .range(["#4e79a7", "#f28e2c", "#e15759", "#76b7b2", "#59a14f", "#edc949", "#af7aa1"]);

  onMount(async () => {
    const csv = await d3.csv('/tournaments_overall_all_years.csv');
    rawData = csv.filter(d => +d.year >= 1975 && d.tourney_level === 'G');

    const tournamentNames = ["Wimbledon", "Roland Garros", "US Open", "Australian Open"];
    
    pieData = tournamentNames.map(tourney => {
      const tourneyWinners = rawData.filter(d => d.tournament === tourney);
      const total = tourneyWinners.length;
      const counts = categories.map(cat => ({ category: cat, count: 0 }));

      tourneyWinners.forEach(d => {
        const rank = +d.final_winner_rank;
        if (rank === 1) counts[0].count++;
        else if (rank === 2) counts[1].count++;
        else if (rank === 3) counts[2].count++;
        else if (rank === 4) counts[3].count++;
        else if (rank === 5) counts[4].count++;
        else if (rank > 5 && rank <= 10) counts[5].count++;
        else if (rank > 10) counts[6].count++;
      });

      return { tournament: tourney, counts, total };
    });
  });

  $: pieGenerator = d3.pie().value(d => d.count).sort(null);
  $: arcGenerator = d3.arc().innerRadius(0).outerRadius(radius);
  $: hoveredArc = d3.arc().innerRadius(0).outerRadius(radius * 1.08);
  $: labelArc = d3.arc().innerRadius(radius * 0.6).outerRadius(radius * 0.6);
</script>

<div class="container">
  <div class="pies-row">
    {#each pieData as item}
      <div class="pie-group">
        <svg width={radius * 2.5} height={radius * 2.5}>
          <g transform="translate({radius * 1.25}, {radius * 1.25})">
            {#each pieGenerator(item.counts) as slice}
              {#if slice.data.count > 0}
                <path 
                  d={hoveredSlice === slice ? hoveredArc(slice) : arcGenerator(slice)} 
                  fill={color(slice.data.category)} 
                  stroke="#fff"
                  stroke-width="1.5"
                  on:mouseenter={() => hoveredSlice = slice}
                  on:mouseleave={() => hoveredSlice = null}
                  style="transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1); cursor: pointer;"
                />
                
                {#if (slice.endAngle - slice.startAngle) > 0.3}
                  <text
                    transform="translate({labelArc.centroid(slice)})"
                    dy="0.35em"
                    text-anchor="middle"
                    font-size="12"
                    fill="white"
                    font-weight="900"
                    pointer-events="none"
                  >
                    #{slice.data.category}
                  </text>
                {/if}
              {/if}
            {/each}
          </g>
        </svg>
        <h3>{item.tournament}</h3>
        
        <div class="info-box">
          {#if hoveredSlice && pieData.find(p => p.counts.includes(hoveredSlice.data))?.tournament === item.tournament}
            {@const percentage = ((hoveredSlice.data.count / item.total) * 100).toFixed(1)}
            <div class="status">
              <span class="dot" style="background: {color(hoveredSlice.data.category)}"></span>
              <strong>Rank #{hoveredSlice.data.category}:</strong> 
              {percentage}% <span class="count">({hoveredSlice.data.count} wins)</span>
            </div>
          {:else}
            <span class="placeholder">Hover for details</span>
          {/if}
        </div>
      </div>
    {/each}
  </div>
</div>

<style>
  .container {
    width: 100%;
    display: flex;
    justify-content: center;
    padding: 1rem 0;
  }

  .pies-row {
    display: flex;
    flex-direction: row;
    justify-content: space-between;
    width: 100%;
    max-width: 1100px;
  }

  .pie-group {
    display: flex;
    flex-direction: column;
    align-items: center;
    flex: 1;
  }

  h3 {
    margin: 10px 0;
    font-size: 1.1rem;
    color: #1e293b;
    font-weight: 800;
    text-transform: uppercase;
    letter-spacing: 0.5px;
  }

  .info-box {
    height: 40px;
    font-size: 0.85rem;
    color: #334155;
    display: flex;
    align-items: center;
    justify-content: center;
  }

  .status {
    display: flex;
    align-items: center;
    gap: 6px;
  }

  .dot {
    width: 8px;
    height: 8px;
    border-radius: 50%;
  }

  .count {
    color: #64748b;
    font-size: 0.8rem;
  }

  .placeholder {
    color: #cbd5e1;
    font-style: italic;
  }

  path:hover {
    filter: saturate(1.2) brightness(1.1);
  }
</style>