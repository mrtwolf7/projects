<script>
    import { onMount } from 'svelte';
    import { scaleLinear, scaleBand } from 'd3-scale';
    import { axisBottom, axisLeft } from 'd3-axis';
    import { select } from 'd3-selection';

    export let data = [];

    /*
     * ==========================================
     * EASY-TO-TWEAK PARAMETER
     * ==========================================
     *
     * An observation counts as "rain" when:
     *
     * actual_precipitation > rainThreshold
     *
     * Examples:
     * 0   = any recorded precipitation
     * 0.1 = at least 0.1 mm
     * 1   = at least 1 mm
     */

    const rainThreshold = 0;

    /*
     * ==========================================
     * HORIZON BINS
     * ==========================================
     */

    const horizonBins = [
        0, 1, 2, 3, 4, 5, 6, 9, 12,
        18, 24,
        36, 48,
        72,
        96,
        120,
        168,
        240
    ];

    const horizonLabels = [
        '0-1',
        '1-2',
        '2-3',
        '3-4',
        '4-5',
        '5-6',
        '6-9',
        '9-12',
        '12-18',
        '18-24',
        '24-36',
        '36-48',
        '48-72',
        '72-96',
        '96-120',
        '120-168',
        '168-240'
    ];

    /*
     * ==========================================
     * RAIN PROBABILITY BINS
     * ==========================================
     */

    const probabilityRanges = [
        { label: '0-10%', min: 0, max: 10 },
        { label: '10-20%', min: 10, max: 20 },
        { label: '20-30%', min: 20, max: 30 },
        { label: '30-40%', min: 30, max: 40 },
        { label: '40-50%', min: 40, max: 50 },
        { label: '50-60%', min: 50, max: 60 },
        { label: '60-70%', min: 60, max: 70 },
        { label: '70-80%', min: 70, max: 80 },
        { label: '80-90%', min: 80, max: 90 },
        { label: '90-100%', min: 90, max: 100 }
    ];

    const probabilityLabels =
        probabilityRanges.map(d => d.label);

    /*
     * ==========================================
     * CHART DIMENSIONS
     * ==========================================
     */

    let chartContainer;

    const width = 1100;
    const height = 650;

    const margin = {
        top: 70,
        right: 40,
        bottom: 120,
        left: 110
    };

    const innerWidth =
        width - margin.left - margin.right;

    const innerHeight =
        height - margin.top - margin.bottom;

    /*
     * ==========================================
     * INITIALISE
     * ==========================================
     */

    onMount(() => {
        drawChart();
    });

    /*
     * ==========================================
     * FIND HORIZON BIN
     * ==========================================
     */

    function getHorizonBin(horizon) {
        for (
            let i = 0;
            i < horizonBins.length - 1;
            i++
        ) {
            if (
                horizon >= horizonBins[i] &&
                horizon < horizonBins[i + 1]
            ) {
                return i;
            }
        }

        // Include exactly 240 in the final bin
        if (horizon === 240) {
            return horizonBins.length - 2;
        }

        return null;
    }

    /*
     * ==========================================
     * FIND RAIN PROBABILITY BIN
     * ==========================================
     */

    function getProbabilityBin(probability) {
        for (
            let i = 0;
            i < probabilityRanges.length;
            i++
        ) {
            const range = probabilityRanges[i];

            const isLastBin =
                i === probabilityRanges.length - 1;

            if (
                probability >= range.min &&
                (
                    probability < range.max ||
                    (
                        isLastBin &&
                        probability <= range.max
                    )
                )
            ) {
                return i;
            }
        }

        return null;
    }

    /*
     * ==========================================
     * MAIN CHART
     * ==========================================
     */

    function drawChart() {

        /*
         * ------------------------------------------
         * 1. PREPARE DATA
         * ------------------------------------------
         */

        const observations = data
            .map(d => ({
                horizon: Number(d.horizon_hours),
                probability: Number(d.rain_prob),
                precipitation: Number(
                    d.actual_precipitation
                )
            }))
            .filter(d =>
                Number.isFinite(d.horizon) &&
                Number.isFinite(d.probability) &&
                Number.isFinite(d.precipitation)
            );

        /*
         * ------------------------------------------
         * 2. CREATE HEATMAP CELLS
         * ------------------------------------------
         */

        const cells = [];

        for (
            let probabilityIndex = 0;
            probabilityIndex < probabilityRanges.length;
            probabilityIndex++
        ) {
            const probabilityRange =
                probabilityRanges[probabilityIndex];

            for (
                let horizonIndex = 0;
                horizonIndex < horizonLabels.length;
                horizonIndex++
            ) {

                const matching =
                    observations.filter(d =>
                        getProbabilityBin(
                            d.probability
                        ) === probabilityIndex &&
                        getHorizonBin(
                            d.horizon
                        ) === horizonIndex
                    );

                const n = matching.length;

                /*
                 * Count cases where it actually rained.
                 */

                const rainCount =
                    matching.filter(
                        d =>
                            d.precipitation >
                            rainThreshold
                    ).length;

                /*
                 * Observed rain frequency as a percentage.
                 */

                const observedFrequency =
                    n > 0
                        ? (rainCount / n) * 100
                        : null;

                /*
                 * ----------------------------------
                 * DELTA FROM PREDICTED INTERVAL
                 * ----------------------------------
                 *
                 * Predicted: 30-40%
                 *
                 * Observed: 55%
                 * Delta: +15%
                 *
                 * Observed: 25%
                 * Delta: -5%
                 *
                 * Observed: 35%
                 * Delta: 0%
                 */

                let delta = null;

                if (
                    observedFrequency !== null
                ) {
                    if (
                        observedFrequency <
                        probabilityRange.min
                    ) {
                        delta =
                            observedFrequency -
                            probabilityRange.min;

                    } else if (
                        observedFrequency >
                        probabilityRange.max
                    ) {
                        delta =
                            observedFrequency -
                            probabilityRange.max;

                    } else {
                        // The observed frequency falls
                        // inside the predicted interval.
                        delta = 0;
                    }
                }

                cells.push({
                    probabilityLabel:
                        probabilityRange.label,

                    probabilityMin:
                        probabilityRange.min,

                    probabilityMax:
                        probabilityRange.max,

                    horizonLabel:
                        horizonLabels[horizonIndex],

                    observedFrequency,

                    delta,

                    n,

                    rainCount
                });
            }
        }

        /*
         * ------------------------------------------
         * 3. CREATE SVG
         * ------------------------------------------
         */

        const svg =
            select(chartContainer)
                .append('svg')
                .attr('width', width)
                .attr('height', height);

        const chart =
            svg
                .append('g')
                .attr(
                    'transform',
                    `translate(${margin.left},${margin.top})`
                );

        /*
         * ------------------------------------------
         * 4. SCALES
         * ------------------------------------------
         *
         * Horizon is reversed:
         *
         * 168-240h → LEFT
         * 0-1h     → RIGHT
         */

        const x =
            scaleBand()
                .domain(
                    [...horizonLabels].reverse()
                )
                .range([0, innerWidth])
                .padding(0.04);

        /*
         * Higher probabilities at the top.
         */

        const y =
            scaleBand()
                .domain(
                    [...probabilityLabels].reverse()
                )
                .range([0, innerHeight])
                .padding(0.04);

        /*
         * ------------------------------------------
         * COLOUR SCALE
         * ------------------------------------------
         *
         * RED:
         * It rained LESS than predicted.
         *
         * WHITE:
         * Observed rain frequency was inside
         * the predicted probability interval.
         *
         * BLUE:
         * It rained MORE than predicted.
         *
         * The further from zero, the stronger
         * the colour.
         */

        const colourScale =
            scaleLinear()
                .domain([
                    -40,
                    -15,
                    0,
                    15,
                    40
                ])
                .range([
                    '#d73027',
                    '#fdae61',
                    '#ffffff',
                    '#67a9cf',
                    '#2166ac'
                ])
                .clamp(true);

        /*
         * ------------------------------------------
         * 5. X AXIS
         * ------------------------------------------
         */

        chart
            .append('g')
            .attr(
                'transform',
                `translate(0,${innerHeight})`
            )
            .call(
                axisBottom(x)
            )
            .selectAll('text')
            .attr(
                'transform',
                'rotate(-45)'
            )
            .style(
                'text-anchor',
                'end'
            );

        /*
         * ------------------------------------------
         * 6. Y AXIS
         * ------------------------------------------
         */

        chart
            .append('g')
            .call(
                axisLeft(y)
            );

        /*
         * ------------------------------------------
         * 7. AXIS LABELS
         * ------------------------------------------
         */

        chart
            .append('text')
            .attr(
                'x',
                innerWidth / 2
            )
            .attr(
                'y',
                innerHeight + 100
            )
            .attr(
                'text-anchor',
                'middle'
            )
            .attr(
                'fill',
                'currentColor'
            )
            .attr(
                'font-size',
                '14px'
            )
            .text(
                'Forecast horizon (hours before event)'
            );

        chart
            .append('text')
            .attr(
                'transform',
                'rotate(-90)'
            )
            .attr(
                'x',
                -innerHeight / 2
            )
            .attr(
                'y',
                -80
            )
            .attr(
                'text-anchor',
                'middle'
            )
            .attr(
                'fill',
                'currentColor'
            )
            .attr(
                'font-size',
                '14px'
            )
            .text(
                'Predicted rain probability'
            );

        /*
         * ------------------------------------------
         * 8. TOOLTIP
         * ------------------------------------------
         */

        const tooltip =
            select(chartContainer)
                .append('div')
                .attr(
                    'class',
                    'tooltip'
                )
                .style(
                    'opacity',
                    0
                );

        /*
         * ------------------------------------------
         * 9. HEATMAP CELLS
         * ------------------------------------------
         */

        chart
            .append('g')
            .attr(
                'class',
                'cells'
            )
            .selectAll('rect')
            .data(cells)
            .join('rect')

            .attr(
                'x',
                d =>
                    x(d.horizonLabel)
            )

            .attr(
                'y',
                d =>
                    y(d.probabilityLabel)
            )

            .attr(
                'width',
                x.bandwidth()
            )

            .attr(
                'height',
                y.bandwidth()
            )

            .attr(
                'fill',
                d =>
                    d.delta === null
                        ? '#eeeeee'
                        : colourScale(d.delta)
            )

            .attr(
                'stroke',
                '#dddddd'
            )

            .attr(
                'stroke-width',
                1
            )

            .style(
                'cursor',
                d =>
                    d.delta === null
                        ? 'default'
                        : 'pointer'
            )

            .on(
                'mouseenter',
                function(event, d) {

                    if (
                        d.observedFrequency === null
                    ) {
                        return;
                    }

                    select(this)
                        .attr(
                            'stroke',
                            '#222'
                        )
                        .attr(
                            'stroke-width',
                            2
                        );

                    const deltaText =
                        d.delta === 0
                            ? '0%'
                            : `${d.delta > 0 ? '+' : ''}${d.delta.toFixed(1)}%`;

                    let directionText;

                    if (d.delta < 0) {
                        directionText =
                            'It rained less often than predicted';

                    } else if (d.delta > 0) {
                        directionText =
                            'It rained more often than predicted';

                    } else {
                        directionText =
                            'Observed rain frequency was within the predicted interval';
                    }

                    tooltip
                        .style(
                            'opacity',
                            1
                        )
                        .html(`
                            <strong>
                                Predicted:
                                ${d.probabilityLabel}
                            </strong>

                            <br>

                            Horizon:
                            ${d.horizonLabel} hours

                            <br><br>

                            Observed rain:
                            <strong>
                                ${d.observedFrequency.toFixed(1)}%
                            </strong>

                            <br>

                            Delta:
                            <strong>
                                ${deltaText}
                            </strong>

                            <br>

                            ${directionText}

                            <br><br>

                            ${d.rainCount.toLocaleString()}
                            rainy observations
                            out of
                            ${d.n.toLocaleString()}
                        `);
                }
            )

            .on(
                'mousemove',
                function(event) {

                    const rect =
                        chartContainer
                            .getBoundingClientRect();

                    tooltip
                        .style(
                            'left',
                            `${event.clientX - rect.left + 15}px`
                        )
                        .style(
                            'top',
                            `${event.clientY - rect.top + 15}px`
                        );
                }
            )

            .on(
                'mouseleave',
                function() {

                    select(this)
                        .attr(
                            'stroke',
                            '#dddddd'
                        )
                        .attr(
                            'stroke-width',
                            1
                        );

                    tooltip
                        .style(
                            'opacity',
                            0
                        );
                }
            );

        /*
         * ------------------------------------------
         * 10. DELTA LABELS INSIDE CELLS
         * ------------------------------------------
         */

        chart
            .append('g')
            .attr(
                'class',
                'cell-labels'
            )
            .selectAll('text')
            .data(
                cells.filter(
                    d =>
                        d.delta !== null
                )
            )
            .join('text')

            .attr(
                'x',
                d =>
                    x(d.horizonLabel) +
                    x.bandwidth() / 2
            )

            .attr(
                'y',
                d =>
                    y(d.probabilityLabel) +
                    y.bandwidth() / 2 +
                    4
            )

            .attr(
                'text-anchor',
                'middle'
            )

            .attr(
                'font-size',
                '10px'
            )

            .attr(
                'font-weight',
                '600'
            )

            /*
             * Dark text for cells close to white.
             * White text for strong red/blue cells.
             */

            .attr(
                'fill',
                d =>
                    Math.abs(d.delta) < 12
                        ? '#222'
                        : '#ffffff'
            )

            .attr(
                'pointer-events',
                'none'
            )

            .text(d => {

                if (d.delta === 0) {
                    return '0%';
                }

                return `${d.delta > 0 ? '+' : ''}${d.delta.toFixed(0)}%`;
            });

        /*
         * ------------------------------------------
         * 11. TITLE
         * ------------------------------------------
         */

        svg
            .append('text')
            .attr(
                'x',
                width / 2
            )
            .attr(
                'y',
                28
            )
            .attr(
                'text-anchor',
                'middle'
            )
            .attr(
                'font-size',
                '20px'
            )
            .attr(
                'font-weight',
                '600'
            )
            .attr(
                'fill',
                'currentColor'
            )
            .text(
                'How close was the predicted rain probability?'
            );

        /*
         * ------------------------------------------
         * 12. SUBTITLE
         * ------------------------------------------
         */

        svg
            .append('text')
            .attr(
                'x',
                width / 2
            )
            .attr(
                'y',
                50
            )
            .attr(
                'text-anchor',
                'middle'
            )
            .attr(
                'font-size',
                '12px'
            )
            .attr(
                'fill',
                'currentColor'
            )
            .attr(
                'opacity',
                0.65
            )
            .text(
                `Rain = actual precipitation > ${rainThreshold} mm`
            );
    }
</script>

<div class="chart-wrapper">

    <div
        class="chart-container"
        bind:this={chartContainer}
    ></div>

    <div class="legend">

        <div class="legend-item">
            <span class="legend-colour red"></span>

            <span>
                Rained less than predicted
            </span>
        </div>

        <div class="legend-item">
            <span class="legend-colour neutral"></span>

            <span>
                Within predicted interval
            </span>
        </div>

        <div class="legend-item">
            <span class="legend-colour blue"></span>

            <span>
                Rained more than predicted
            </span>
        </div>

    </div>

</div>

<style>

    .chart-wrapper {
        width: 100%;
        overflow-x: auto;
    }

    .chart-container {
        position: relative;
        width: max-content;
    }

    :global(.tooltip) {
        position: absolute;
        pointer-events: none;

        background: rgba(
            20,
            20,
            20,
            0.95
        );

        color: white;

        padding: 10px 12px;

        border-radius: 6px;

        font-size: 12px;

        line-height: 1.5;

        white-space: nowrap;

        z-index: 10;
    }

    .legend {
        display: flex;
        justify-content: center;
        flex-wrap: wrap;

        gap: 25px;

        margin-top: 15px;

        font-size: 12px;
    }

    .legend-item {
        display: flex;
        align-items: center;

        gap: 7px;
    }

    .legend-colour {
        width: 14px;
        height: 14px;

        border-radius: 3px;
    }

    .red {
        background: #d73027;
    }

    .neutral {
        background: #ffffff;
        border: 1px solid #999999;
    }

    .blue {
        background: #2166ac;
    }

</style>