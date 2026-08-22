<script>
    import { onMount } from 'svelte';
    import { scaleLinear, scalePoint } from 'd3-scale';
    import { axisBottom, axisLeft } from 'd3-axis';
    import { select } from 'd3-selection';
    import { max } from 'd3-array';

    export let data = [];

    let chartContainer;

    const bins = [
        0, 1, 2, 3, 4, 5, 6, 9, 12,
        18, 24,
        36, 48,
        72,
        96,
        120,
        168,
        240
    ];

    const labels = [
        "0-1", "1-2", "2-3", "3-4", "4-5", "5-6",
        "6-9", "9-12", "12-18", "18-24",
        "24-36", "36-48", "48-72", "72-96",
        "96-120", "120-168", "168-240"
    ];

    onMount(() => {
        drawChart();
    });

    function getBinIndex(horizon) {
        for (let i = 0; i < bins.length - 1; i++) {
            if (
                horizon >= bins[i] &&
                horizon < bins[i + 1]
            ) {
                return i;
            }
        }

        if (horizon === bins[bins.length - 1]) {
            return bins.length - 2;
        }

        return null;
    }

    function drawChart() {
        const observations = data
            .map(d => ({
                // Floor temperature to integer
                temp: Math.floor(d.actual_temp),
                horizon: d.horizon_hours,
                error: Math.abs(d.temp - d.actual_temp)
            }))
            .filter(d =>
                Number.isFinite(d.temp) &&
                Number.isFinite(d.horizon) &&
                Number.isFinite(d.error)
            );

        // --------------------------------------------------
        // Overall MAE
        // --------------------------------------------------

        const overall = labels.map((label, binIndex) => {
            const values = observations.filter(
                d => getBinIndex(d.horizon) === binIndex
            );

            return {
                label,
                mae: values.length
                    ? values.reduce(
                        (sum, d) => sum + d.error,
                        0
                    ) / values.length
                    : null
            };
        });

        // --------------------------------------------------
        // MAE for each integer actual temperature
        // --------------------------------------------------

        const temperatures = [
            ...new Set(observations.map(d => d.temp))
        ].sort((a, b) => a - b);

        const temperatureLines = temperatures.map(temp => ({
            temp,

            values: labels.map((label, binIndex) => {
                const values = observations.filter(
                    d =>
                        d.temp === temp &&
                        getBinIndex(d.horizon) === binIndex
                );

                return {
                    label,
                    mae: values.length
                        ? values.reduce(
                            (sum, d) => sum + d.error,
                            0
                        ) / values.length
                        : null
                };
            })
        }));

        // --------------------------------------------------
        // Dimensions
        // --------------------------------------------------

        const margin = {
            top: 50,
            right: 30,
            bottom: 90,
            left: 70
        };

        const width = 1000;
        const height = 550;

        const innerWidth =
            width - margin.left - margin.right;

        const innerHeight =
            height - margin.top - margin.bottom;

        // --------------------------------------------------
        // SVG
        // --------------------------------------------------

        const svg = select(chartContainer)
            .append("svg")
            .attr("width", width)
            .attr("height", height);

        const chart = svg
            .append("g")
            .attr(
                "transform",
                `translate(${margin.left},${margin.top})`
            );

        // --------------------------------------------------
        // Scales
        // --------------------------------------------------

        const x = scalePoint()
            .domain(labels)
            .range([innerWidth, 0])
            .padding(0.5);

        const maxMAE = max([
            ...overall
                .map(d => d.mae)
                .filter(v => v !== null),

            ...temperatureLines.flatMap(line =>
                line.values
                    .map(d => d.mae)
                    .filter(v => v !== null)
            )
        ]);

        const y = scaleLinear()
            .domain([0, maxMAE])
            .nice()
            .range([innerHeight, 0]);

        // --------------------------------------------------
        // Axes
        // --------------------------------------------------

        chart
            .append("g")
            .attr(
                "transform",
                `translate(0,${innerHeight})`
            )
            .call(axisBottom(x))
            .selectAll("text")
            .attr("transform", "rotate(-45)")
            .style("text-anchor", "end");

        chart
            .append("g")
            .call(axisLeft(y));

        // --------------------------------------------------
        // Grid
        // --------------------------------------------------

        chart
            .append("g")
            .attr("class", "grid")
            .call(
                axisLeft(y)
                    .tickSize(-innerWidth)
                    .tickFormat("")
            );

        // --------------------------------------------------
        // Axis labels
        // --------------------------------------------------

        chart
            .append("text")
            .attr("x", innerWidth / 2)
            .attr("y", innerHeight + 80)
            .attr("text-anchor", "middle")
            .attr("fill", "currentColor")
            .text("Forecast horizon (hours)");

        chart
            .append("text")
            .attr("transform", "rotate(-90)")
            .attr("x", -innerHeight / 2)
            .attr("y", -50)
            .attr("text-anchor", "middle")
            .attr("fill", "currentColor")
            .text("Mean Absolute Error (°C)");

        // --------------------------------------------------
        // Line helper
        // --------------------------------------------------

        function linePath(values) {
            const points = values
                .filter(d => d.mae !== null)
                .map(d => ({
                    x: x(d.label),
                    y: y(d.mae)
                }));

            if (points.length < 2) {
                return null;
            }

            return points
                .map((p, i) =>
                    `${i === 0 ? "M" : "L"}${p.x},${p.y}`
                )
                .join(" ");
        }

        // --------------------------------------------------
        // Temperature lines
        // --------------------------------------------------

        const tempGroup = chart
            .append("g")
            .attr("class", "temperature-lines");

        const temperatureLabel = chart
            .append("text")
            .attr("x", innerWidth - 10)
            .attr("y", 25)
            .attr("text-anchor", "end")
            .attr("font-size", "17px")
            .attr("font-weight", "600")
            .attr("fill", "#111")
            .attr("opacity", 0);

        temperatureLines.forEach(line => {
            const path = linePath(line.values);

            if (!path) return;

            const visibleLine = tempGroup
                .append("path")
                .attr("class", "temperature-line")
                .attr("d", path)
                .attr("fill", "none")
                .attr("stroke", "#777")
                .attr("stroke-width", 1.5)
                .attr("stroke-opacity", 0.15);

            tempGroup
                .append("path")
                .attr("class", "temperature-hitbox")
                .attr("d", path)
                .attr("fill", "none")
                .attr("stroke", "transparent")
                .attr("stroke-width", 14)
                .style("cursor", "pointer")

                .on("mouseenter", () => {
                    tempGroup
                        .selectAll(".temperature-line")
                        .attr("stroke-opacity", 0.04);

                    visibleLine
                        .attr("stroke", "#111")
                        .attr("stroke-width", 3)
                        .attr("stroke-opacity", 1);

                    temperatureLabel
                        .text(`Actual temperature: ${line.temp}°C`)
                        .attr("opacity", 1);
                })

                .on("mouseleave", () => {
                    tempGroup
                        .selectAll(".temperature-line")
                        .attr("stroke", "#777")
                        .attr("stroke-width", 1.5)
                        .attr("stroke-opacity", 0.15);

                    temperatureLabel.attr("opacity", 0);
                });
        });

        // --------------------------------------------------
        // Overall MAE
        // --------------------------------------------------

        const overallPath = linePath(overall);

        chart
            .append("path")
            .attr("d", overallPath)
            .attr("fill", "none")
            .attr("stroke", "#2563eb")
            .attr("stroke-width", 3);

        chart
            .selectAll(".overall-point")
            .data(
                overall.filter(d => d.mae !== null)
            )
            .join("circle")
            .attr("class", "overall-point")
            .attr("cx", d => x(d.label))
            .attr("cy", d => y(d.mae))
            .attr("r", 4)
            .attr("fill", "#2563eb");

        // --------------------------------------------------
        // Title
        // --------------------------------------------------

        svg
            .append("text")
            .attr("x", width / 2)
            .attr("y", 22)
            .attr("text-anchor", "middle")
            .attr("font-size", "18px")
            .attr("font-weight", "600")
            .attr("fill", "currentColor")
            .text("Temperature prediction error vs forecast horizon");
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