<script>
    import { onMount } from 'svelte';
    import { csvParse } from 'd3-dsv';

    import ObservedRainFrequencyHeatmap from '$lib/ObservedRainFrequencyHeatmap.svelte';
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

    <p> 
        Looking at this, I could finally understand where my confusion was coming from. You can see that, with the exception of "Heavy Rain",
        all the other rain related conditions are widely used, even when the rain probability is way below 50%! Personally, knowing that "Thundery Showers" and "Light
        Rain Showers" are used even when the rain probability is around 30% really causes a headache. And being a user, the first thing you see is the weather icon - it strongly influences your
        plans; note also that the rain probability is always reprensented by the same rain icon, regardless of the value.
    </p>
    <p>
        Ok, but after all, how many times did it really rain? Did the predictions got more accurate getting closer to the predicted event?
    </p>

    <ObservedRainFrequencyHeatmap data={weatherData} />
    <p>
        What the heatmap is showing is the difference between how many times did it actually rain compared to the predicted rain interval, grouped by time.
        So, for instance, if between 5 to 6 hours before the predicted event BBC predicted 30-40% of rain probability and it rained 50% of the times, the heatmap would show +10%.
        This means that any time it rained within the predicted interval, the heatmap just shows a 0% - coloured with a neutral white, it is more blue if it rained more than predicted, more red if it rained less.
    </p>
    <p>
        Looking at the heatmap there are some interesting bits to notice:
    </p> 
    <ul>
        <li> between 10 to 4 days before the event, BBC tended to overestimate the rain probability, quite significantly for high values. It rained between 20% to 40% less; </li>
        <li> interestingly most of the correct prediction happened between 3 days to 12 hours before the event, while many predictions got increasingly wrong as approaching to the event; </li>
        <li> the most correct predictions sit in the extreme values, both high and low, while the rain probabilities between 30% to 70% are the ones with the highest differences between the actual times it really rained. </li>
    </ul>
    <p>
        So, as a user, when is the best time to get the most accurate rain prediction? <strong> BBC predicted the probability that there would be rain the most accurate between 9 to 12 hours before the event </strong>, while it got incredibly worse approaching to the event, especially 3-4 hours before. 
        Other decent predictions could also be found between 1-2 days before the event.
    </p>
    <p>
        Overall it rained way less than predicted and a similar outcome can be found by looking at the temperatures. I also found this to be very off at times and so I tried to understand
        how the forecatst varied approaching to the event, more spefically the difference between Predicted and Actual temperature over time:
    </p>
    <TemperatureScatter data={weatherData} />

    <p>
        It does not come as a surprise that predictions are more accurate as approaching to the event, however up to one week before, 
        <strong> predictions can be off by 10° (underestimating the heat) and 6° (overestimating it) </strong>. In general there are 
        more predictions underestimating the temperature than overestimating it. <br>
        But I wanted to understand if there was any factor making the predictions more or less wrong, and by how much?
        Looking at how wrong the predictions were depending on the actual temperature, there is quite a big difference, especially up to one week before:
    </p>
    <TemperatureMAE data={weatherData} />
    <p>
        The blue line repreents the absolute difference across all the temperatures, while the greyed out lines are different for each temperature: 
        from that it can be noticed that the higher the temperature the least accurate the prediction was - up to one week - then, as expected they all converge 
        as the event approaches.
    </p>
    <p>
        One question then has to be asked: <strong> Can we predict whether a BBC forecast will be correct? <strong>
    </p>

{/if}



