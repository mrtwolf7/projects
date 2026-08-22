<script>
    import drizzle from '$lib/assets/drizzle.png';
    import heavyRain from '$lib/assets/heavyrain.jpeg';
    import lightCloud from '$lib/assets/lightcloud.png';
    import lightRain from '$lib/assets/lightrain.png';
    import lightRainShowers from '$lib/assets/lightrainshowers.jpg';
    import partlyCloudy from '$lib/assets/partcloudy.png';
    import sunny from '$lib/assets/sunny.png';
    import sunnyIntervals from '$lib/assets/sunnyintervals.png';
    import thickCloud from '$lib/assets/thickcloud.jpeg';
    import thunderyShowers from '$lib/assets/thundershowers.png';

    export let data = [];

    let selectedProbability = 30;

    const conditionInfo = {
        'Drizzle': {
            image: drizzle,
            label: 'Drizzle'
        },
        'Heavy Rain': {
            image: heavyRain,
            label: 'Heavy Rain'
        },
        'Light Cloud': {
            image: lightCloud,
            label: 'Light Cloud'
        },
        'Light Rain': {
            image: lightRain,
            label: 'Light Rain'
        },
        'Light Rain Showers': {
            image: lightRainShowers,
            label: 'Light Rain Showers'
        },
        'Partly Cloudy': {
            image: partlyCloudy,
            label: 'Partly Cloudy'
        },
        'Sunny': {
            image: sunny,
            label: 'Sunny'
        },
        'Sunny Intervals': {
            image: sunnyIntervals,
            label: 'Sunny Intervals'
        },
        'Thick Cloud': {
            image: thickCloud,
            label: 'Thick Cloud'
        },
        'Thundery Showers': {
            image: thunderyShowers,
            label: 'Thundery Showers'
        }
    };

    $: filteredData = data.filter(d =>
        Number(d.rain_prob) === Number(selectedProbability) &&
        d.condition &&
        conditionInfo[d.condition]
    );

    $: total = filteredData.length;

    $: conditions = Object.entries(
        filteredData.reduce((acc, d) => {
            acc[d.condition] = (acc[d.condition] || 0) + 1;
            return acc;
        }, {})
    )
        .map(([condition, count]) => ({
            condition,
            count,
            percentage: total
                ? (count / total) * 100
                : 0,
            ...conditionInfo[condition]
        }))
        .sort((a, b) => b.percentage - a.percentage);
</script>

<section class="visualisation">

    <div class="intro">
        <h2>What does a rain probability actually mean?</h2>

        <p>
            Select the rain probability you see on BBC Weather.
            Below are the different weather conditions that have historically
            appeared with that same probability.
        </p>
    </div>

    <!-- Slider -->

    <div class="control">

        <label for="probability">
            Rain probability
        </label>

        <div class="probability-value">
            {selectedProbability}%
        </div>

        <input
            id="probability"
            type="range"
            min="0"
            max="100"
            step="1"
            bind:value={selectedProbability}
        />

        <div class="range-labels">
            <span>0%</span>
            <span>100%</span>
        </div>

    </div>

    <!-- Explanation -->

    {#if total > 0}

        <p class="result-intro">
            When BBC Weather showed a
            <strong>{selectedProbability}% chance of rain</strong>,
            these were the weather conditions shown:
        </p>

        <!-- Conditions -->

        <div class="conditions-grid">

            {#each conditions as item}

                <div class="condition-card">

                    <img
                        src={item.image}
                        alt={item.label}
                    />

                    <h3>{item.label}</h3>

                    <div class="percentage">
                        {item.percentage.toFixed(1)}%
                    </div>

                    <p>
                        {item.count.toLocaleString()}
                        observations
                    </p>

                </div>

            {/each}

        </div>

        <p class="footer">
            Based on {total.toLocaleString()} BBC Weather observations
            with a {selectedProbability}% rain probability.
        </p>

    {:else}

        <div class="no-data">

            <p>
                No observations found for exactly
                <strong>{selectedProbability}%</strong> rain probability.
            </p>

        </div>

    {/if}

</section>

<style>

    .visualisation {
        max-width: 1100px;
        margin: 0 auto;
        padding: 2rem;
    }

    .intro {
        text-align: center;
        margin-bottom: 2.5rem;
    }

    h2 {
        font-size: 2rem;
        margin-bottom: 0.75rem;
    }

    .intro p {
        max-width: 650px;
        margin: 0 auto;
        line-height: 1.6;
        opacity: 0.75;
    }

    /* -------------------------
       Slider
    ------------------------- */

    .control {
        max-width: 700px;
        margin: 0 auto 2.5rem;
        text-align: center;
    }

    .control label {
        display: block;
        font-weight: 600;
        margin-bottom: 0.5rem;
    }

    .probability-value {
        font-size: 3.5rem;
        font-weight: 700;
        margin-bottom: 1rem;
    }

    input[type="range"] {
        width: 100%;
        cursor: pointer;
    }

    .range-labels {
        display: flex;
        justify-content: space-between;
        margin-top: 0.4rem;
        font-size: 0.85rem;
        opacity: 0.6;
    }

    /* -------------------------
       Results
    ------------------------- */

    .result-intro {
        text-align: center;
        margin-bottom: 2rem;
        font-size: 1.1rem;
    }

    .conditions-grid {
        display: grid;
        grid-template-columns:
            repeat(auto-fit, minmax(170px, 1fr));

        gap: 1.5rem;
    }

    .condition-card {
        text-align: center;
        padding: 1.5rem 1rem;
        border: 1px solid rgba(128, 128, 128, 0.25);
        border-radius: 12px;
        transition:
            transform 0.2s ease,
            box-shadow 0.2s ease;
    }

    .condition-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 6px 20px rgba(0, 0, 0, 0.12);
    }

    .condition-card img {
        width: 100px;
        height: 100px;
        object-fit: contain;
        margin-bottom: 0.75rem;
    }

    .condition-card h3 {
        font-size: 1rem;
        margin: 0.5rem 0;
    }

    .percentage {
        font-size: 2rem;
        font-weight: 700;
        margin: 0.5rem 0;
    }

    .condition-card p {
        font-size: 0.8rem;
        opacity: 0.6;
        margin: 0;
    }

    .footer {
        text-align: center;
        margin-top: 2rem;
        font-size: 0.85rem;
        opacity: 0.6;
    }

    .no-data {
        text-align: center;
        padding: 3rem;
        opacity: 0.7;
    }

    @media (max-width: 600px) {

        .visualisation {
            padding: 1rem;
        }

        .probability-value {
            font-size: 3rem;
        }

        .conditions-grid {
            grid-template-columns:
                repeat(2, 1fr);
        }

    }

</style>