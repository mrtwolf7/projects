<script>
    import { onMount } from 'svelte';
    import { scaleLinear, scaleBand } from 'd3-scale';
    import { axisBottom, axisLeft } from 'd3-axis';
    import { select } from 'd3-selection';
    import { max } from 'd3-array';

    export let data = [];

    let chartContainer;

    const width = 1100;
    const margin = {
        top: 50,
        right: 120,
        bottom: 60,
        left: 180
    };

    const height = 650;

    const innerWidth =
        width - margin.left - margin.right;

    const innerHeight =
        height - margin.top - margin.bottom;

    onMount(() => {
        drawChart();
    });

    function drawChart() {

        // --------------------------------------------------
        // 1. Prepare data
        // --------------------------------------------------

        const observations = data
            .map(d => ({
                condition: d.condition,
                probability: Number(d.rain_prob)
            }))
            .filter(d =>
                d.condition &&
                Number.isFinite(d.probability)
            );

        // --------------------------------------------------
        // 2. Group observations by condition
        // --------------------------------------------------

        const grouped = {};

        observations.forEach(d => {
            if (!grouped[d.condition]) {
                grouped[d.condition] = [];
            }

            grouped[d.condition].push(d.probability);
        });

        // --------------------------------------------------
        // 3. Calculate statistics
        // --------------------------------------------------

        function quantile(values, q) {
            const sorted = [...values].sort((a, b) => a - b);

            const position =
                (sorted.length - 1) * q;

            const lower = Math.floor(position);
            const upper = Math.ceil(position);

            if (lower === upper) {
                return sorted[lower];
            }

            return (
                sorted[lower] +
                (sorted[upper] - sorted[lower]) *
                (position - lower)
            );
        }

        const statistics = Object.entries(grouped)
            .map(([condition, values]) => {

                const q1 = quantile(values, 0.25);
                const median = quantile(values, 0.50);
                const q3 = quantile(values, 0.75);

                const iqr = q3 - q1;

                const lowerLimit =
                    q1 - 1.5 * iqr;

                const upperLimit =
                    q3 + 1.5 * iqr;

                const lowerWhisker =
                    Math.min(
                        ...values.filter(
                            v => v >= lowerLimit
                        )
                    );

                const upperWhisker =
                    Math.max(
                        ...values.filter(
                            v => v <= upperLimit
                        )
                    );

                return {
                    condition,
                    values,
                    q1,
                    median,
                    q3,
                    lowerWhisker,
                    upperWhisker,
                    n: values.length
                };
            })
            .sort((a, b) =>
                a.median - b.median
            );

        // --------------------------------------------------
        // 4. SVG
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
        // 5. Scales
        // --------------------------------------------------

        const x = scaleLinear()
            .domain([0, 100])
            .range([0, innerWidth]);

        const y = scaleBand()
            .domain(
                statistics.map(d => d.condition)
            )
            .range([0, innerHeight])
            .padding(0.35);

        // --------------------------------------------------
        // 6. Axes
        // --------------------------------------------------

        chart
            .append("g")
            .attr(
                "transform",
                `translate(0,${innerHeight})`
            )
            .call(
                axisBottom(x)
                    .ticks(10)
                    .tickFormat(d => `${d}%`)
            );

        chart
            .append("g")
            .call(axisLeft(y));

        // --------------------------------------------------
        // 7. Grid
        // --------------------------------------------------

        chart
            .append("g")
            .attr("class", "grid")
            .call(
                axisBottom(x)
                    .ticks(10)
                    .tickSize(innerHeight)
                    .tickFormat("")
            );

        // --------------------------------------------------
        // 8. Axis labels
        // --------------------------------------------------

        chart
            .append("text")
            .attr("x", innerWidth / 2)
            .attr("y", innerHeight + 50)
            .attr("text-anchor", "middle")
            .attr("fill", "currentColor")
            .text("Probability of rain");

        chart
            .append("text")
            .attr("transform", "rotate(-90)")
            .attr("x", -innerHeight / 2)
            .attr("y", -135)
            .attr("text-anchor", "middle")
            .attr("fill", "currentColor")
            .text("BBC Weather condition");

        // --------------------------------------------------
        // 9. Boxplots
        // --------------------------------------------------

        const boxGroup = chart
            .append("g")
            .attr("class", "boxplots");

        statistics.forEach(stat => {

            const cy =
                y(stat.condition) +
                y.bandwidth() / 2;

            const boxHeight =
                y.bandwidth();

            // ----------------------------------------------
            // Whisker
            // ----------------------------------------------

            boxGroup
                .append("line")
                .attr("x1", x(stat.lowerWhisker))
                .attr("x2", x(stat.upperWhisker))
                .attr("y1", cy)
                .attr("y2", cy)
                .attr("stroke", "currentColor")
                .attr("stroke-width", 1);

            // Lower whisker
            boxGroup
                .append("line")
                .attr("x1", x(stat.lowerWhisker))
                .attr("x2", x(stat.lowerWhisker))
                .attr("y1", cy - boxHeight * 0.25)
                .attr("y2", cy + boxHeight * 0.25)
                .attr("stroke", "currentColor");

            // Upper whisker
            boxGroup
                .append("line")
                .attr("x1", x(stat.upperWhisker))
                .attr("x2", x(stat.upperWhisker))
                .attr("y1", cy - boxHeight * 0.25)
                .attr("y2", cy + boxHeight * 0.25)
                .attr("stroke", "currentColor");

            // ----------------------------------------------
            // Box: Q1 → Q3
            // ----------------------------------------------

            boxGroup
                .append("rect")
                .attr("x", x(stat.q1))
                .attr("y", cy - boxHeight / 2)
                .attr(
                    "width",
                    x(stat.q3) - x(stat.q1)
                )
                .attr("height", boxHeight)
                .attr("fill", "currentColor")
                .attr("fill-opacity", 0.12)
                .attr("stroke", "currentColor");

            // ----------------------------------------------
            // Median
            // ----------------------------------------------

            boxGroup
                .append("line")
                .attr("x1", x(stat.median))
                .attr("x2", x(stat.median))
                .attr("y1", cy - boxHeight / 2)
                .attr("y2", cy + boxHeight / 2)
                .attr("stroke", "currentColor")
                .attr("stroke-width", 3);

            // ----------------------------------------------
            // Sample size
            // ----------------------------------------------

            boxGroup
                .append("text")
                .attr("x", innerWidth + 15)
                .attr("y", cy + 4)
                .attr("fill", "currentColor")
                .attr("font-size", "11px")
                .text(`n=${stat.n.toLocaleString()}`);
        });

        // --------------------------------------------------
        // 10. Individual observations
        // --------------------------------------------------

        /*
         * The dataset is large, so don't draw every point.
         * Sample up to 600 observations per condition.
         */

        const dots = [];

        statistics.forEach(stat => {

            const sampleSize = Math.min(
                stat.values.length,
                600
            );

            const shuffled = [...stat.values]
                .sort(() => Math.random() - 0.5)
                .slice(0, sampleSize);

            shuffled.forEach(probability => {

                dots.push({
                    condition: stat.condition,
                    probability
                });
            });
        });

        chart
            .append("g")
            .attr("class", "observations")
            .selectAll("circle")
            .data(dots)
            .join("circle")
            .attr(
                "cx",
                d => x(d.probability)
            )
            .attr(
                "cy",
                d =>
                    y(d.condition) +
                    y.bandwidth() / 2 +
                    (Math.random() - 0.5) *
                    y.bandwidth() * 0.7
            )
            .attr("r", 1.5)
            .attr("fill", "currentColor")
            .attr("fill-opacity", 0.12);

        // --------------------------------------------------
        // 11. Title
        // --------------------------------------------------

        svg
            .append("text")
            .attr("x", width / 2)
            .attr("y", 25)
            .attr("text-anchor", "middle")
            .attr("font-size", "18px")
            .attr("font-weight", "600")
            .attr("fill", "currentColor")
            .text(
                "Rain probability by BBC Weather condition"
            );
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
        max-width: 100%;
        height: auto;
    }
</style>