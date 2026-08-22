<script>
    import { onMount } from 'svelte';
    import { scaleLinear } from 'd3-scale';
    import { extent } from 'd3-array';
    import { axisBottom, axisLeft } from 'd3-axis';
    import { select } from 'd3-selection';

    export let data = [];

    let chartContainer;

    onMount(() => {
        drawChart();
    });

    function drawChart() {
        const margin = {
            top: 40,
            right: 30,
            bottom: 70,
            left: 75
        };

        const width = 1000;
        const height = 550;

        const innerWidth = width - margin.left - margin.right;
        const innerHeight = height - margin.top - margin.bottom;

        const svg = select(chartContainer)
            .append('svg')
            .attr('width', width)
            .attr('height', height);

        const chart = svg
            .append('g')
            .attr(
                'transform',
                `translate(${margin.left},${margin.top})`
            );

        // X axis
        // Reversed so that the event (0 hours)
        // is on the right.
        const x = scaleLinear()
            .domain(extent(data, d => d.horizon_hours))
            .range([innerWidth, 0]);

        // Y axis
        const y = scaleLinear()
            .domain(extent(data, d => d.temp_diff))
            .nice()
            .range([innerHeight, 0]);

        // X axis
        chart
            .append('g')
            .attr(
                'transform',
                `translate(0,${innerHeight})`
            )
            .call(axisBottom(x));

        // Y axis
        chart
            .append('g')
            .call(axisLeft(y));

        // X label
        chart
            .append('text')
            .attr('x', innerWidth / 2)
            .attr('y', innerHeight + 50)
            .attr('text-anchor', 'middle')
            .attr('fill', 'currentColor')
            .text('Hours before event');

        // Y label
        chart
            .append('text')
            .attr('transform', 'rotate(-90)')
            .attr('x', -innerHeight / 2)
            .attr('y', -55)
            .attr('text-anchor', 'middle')
            .attr('fill', 'currentColor')
            .text('Predicted − Actual Temperature (°C)');

        // Grid
        chart
            .append('g')
            .attr('class', 'grid')
            .call(
                axisLeft(y)
                    .tickSize(-innerWidth)
                    .tickFormat('')
            );

        // Zero-error line
        chart
            .append('line')
            .attr('x1', 0)
            .attr('x2', innerWidth)
            .attr('y1', y(0))
            .attr('y2', y(0))
            .attr('stroke', 'currentColor')
            .attr('stroke-opacity', 0.4)
            .attr('stroke-dasharray', '4 4');

        // Scatter points
        chart
            .selectAll('circle')
            .data(data)
            .join('circle')
            .attr('cx', d => x(d.horizon_hours))
            .attr('cy', d => y(d.temp_diff))
            .attr('r', 3)
            .attr('fill', '#4f46e5')
            .attr('fill-opacity', 0.25);

        // Title
        svg
            .append('text')
            .attr('x', width / 2)
            .attr('y', 20)
            .attr('text-anchor', 'middle')
            .attr('font-size', '18px')
            .attr('font-weight', '600')
            .attr('fill', 'currentColor')
            .text('Temperature prediction error vs forecast horizon');
    }
</script>

<div bind:this={chartContainer}></div>

<style>
    :global(.grid line) {
        stroke: currentColor;
        stroke-opacity: 0.1;
    }

    :global(.grid path) {
        stroke-width: 0;
    }

    svg {
        display: block;
    }
</style>
