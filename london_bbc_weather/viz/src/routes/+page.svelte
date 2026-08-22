<script>
    import { onMount } from 'svelte';
    import { csvParse } from 'd3-dsv';

    import RainProbabilityConditions from '$lib/RainProbabilityConditions.svelte';
    import RainProbabilityDist from '$lib/RainProbabilityDist.svelte';
    import TemperatureScatter from '$lib/TemperatureScatter.svelte';
    import TemperatureMAE from '$lib/TemperatureMAE.svelte';

    let weatherData = [];
    let loading = true;
    let error = null;

    onMount(async () => {
        try {
            const response = await fetch('/london_weather_full.csv');

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}`);
            }

            const text = await response.text();

            weatherData = csvParse(text, row => {
                const temp = +row.temp;
                const actual_temp = +row.actual_temp;

                return {
                    scrape_time: row.scrape_time,
                    forecast_time: row.forecast_time,

                    temp: temp,
                    temp_perc: +row.temp_perc,
                    rain_prob: +row.rain_prob,

                    condition: row.condition,

                    wind_speed: +row.wind_speed,
                    wind_direction: +row.wind_direction,
                    humidity: +row.humidity,
                    pressure: +row.pressure,

                    horizon_hours: +row.horizon_hours,

                    observation_time: row.observation_time,
                    actual_temp: actual_temp,
                    actual_humidity: +row.actual_humidity,
                    actual_precipitation: +row.actual_precipitation,
                    actual_pressure: +row.actual_pressure,
                    actual_wind_speed: +row.actual_wind_speed,
                    actual_wind_direction: +row.actual_wind_direction,

                    temp_diff: temp - actual_temp
                };
            });

            console.log(`Loaded ${weatherData.length} rows`);

        } catch (e) {
            error = e.message;
        } finally {
            loading = false;
        }
    });
</script>

<h1>London BBC Weather</h1>

{#if loading}

    <p>Loading data...</p>

{:else if error}

    <p>Error: {error}</p>

{:else}
    <p> 
        As human beings, we are scared of the unknown and that is why we have always tried to reduce the margin of uncertainty
        and predict as much of the future as we could, with more or less succesful results.
        A type of event that we predict is the weather; knowing what the weather is like is so crucial for us to organise a good part of our life: 
        what are the plans for the weekend, where and when to on holidays, and really many of our decisions, small or big, depend on the weather. Or better, 
        on the weather forecasts.
    </p>
    <p> 
        I have lived a good part of my life in Rome, where I have to say, I have seen the weather becoming more and more stable - it is very often sunny, and so 
        I was not really looking at the weather forecast very regularly.
        However, since I moved to London I often found myself using BBC website to check the weather forecasts, and many times I found these to be confusing and 
        not accurate.
        Where is the confusion coming from? I realised that as a user, first of all, I found that there was some ambiguity around the weather condition and rain probability.
        There was not a 1:1 relationship and actually at times even "Sunny" conditions would lead to a non small rain probability.
        Here you can simulate what conditions would appear depending on the rain probability.
    </p>


    <RainProbabilityConditions data={weatherData} />

    <p> 
        I decided to study this problem in detail: I have collected snapshots of the forecast every 3 hours from XX May to 
        XX June, then analysed the data and compared it with what the weather then actually was.
        Continuing the investigation on rain probability and weather conditions, I have tried to look at the problem from a 
        different angle, i.e. what is the interval of rain probability given a weather condition.
    </p>

    <RainProbabilityDist data={weatherData} />
    <TemperatureScatter data={weatherData} />
    <TemperatureMAE data={weatherData} />

{/if}



