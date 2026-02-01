<script>
  import Timeline from '$lib/timeline_faves.svelte';
  import TimelineRounds from '$lib/timeline_faves_round.svelte';
  import AvgWinnerGames from '$lib/winner_games.svelte';
  import AvgDiffGames from '$lib/games_diff.svelte';
  import WinnerRank from '$lib/winner_ranking.svelte';
</script>

<article>
  <h1>Is tennis becoming more predictable?</h1>

  <p>
    Ok, I hear you out everyone "Tennis is sooo boring! And it has always been!" - well, 
    if you never found yourself lost in one of Federer's drop shots, then ok, I agree with you:
    but at that point the problem is not tennis really.
  <p>
  <p>
    I wanted to prove you wrong and show that tennis can also be very entertaining, but in the end
    this is really personal taste AND showing that a match is entertaining is quite hard to do just by using
    data, and I would need very granular data - which I do not have.
    So I decided to answer another question: is tennis becoming more predictable?
    I focused on ATP only, starting by looking at Grand Slams, because arguably the most important
    tournaments.
  </p>
  <p>
    The first angle I looked at was tournament predictability: <strong>are Grand Slam tournaments 
    more predictable these days than they were in the past? </strong>
    To do so, I started by looking at the ratio of matches won by players with the higher 
    ranking from 1975 to 2024. Higher values represent lower predictability:
  </p>

  <Timeline />

  <p>
    Looking at the plot, you can see that the "favourite players" ratio increases significantly
    from the 1970s up to 1990s, it continues to increase slower up to 2010s and then it softly decreases.
    In numbers, while on average in the 70s the ratio was around 0.3 - meaning the 70% of the matches
    were won by players with lower ranking - it went up to 0.5 in the 80s, up to almost 0.75 in the 10s
    and then decrease to 0.7 in the 20s.
  </p>
  <p>
    While this is already telling us something about historical trends for all matches in the tournaments
    I wanted to take a closer look at the tournament predictability by analysing only the matches in the second week
    (from round of 16 onwards) - come on, let's be honest, these are the games we are more interested in:
  </p>
  <TimelineRounds />
  <p>
    On average, the favourites ratio is between 0.05-0-1 higher in these tournaments rounds than in the overall tournament,
    meaning the earliest rounds are where surprising results are more likely to happen.
  </p>
  <p>
    There is not a big difference between the R16, QF, SF and F - values are very similar, between
    0.68 up to 0.77. There is not any notable difference in the tournaments either: Roland Garros seems to
    be slightly more unpredictable than the other across the 80s and 90s, then this role is played by the 
    Australian Open in the 00s and US Open in the 10s.
    Roughly speaking this means that <strong> from R16 onwards the player with the highest ranking wins the match 
    around 70% or more of the time </strong>.
  </p>
  <p>
    Ok, the matches are usually won by the player with the higher ranking, but are they interesting? 
    Are they tight?
  </p>
  <p>
    To answer this question, I have computed what is the average number of games won by the winner for every match.
    The minimum is 18 (it's the result of a three set match) and every number close to it shows no much competitiveness
    in the match:
  </p>
  <AvgWinnerGames />
  <p>
    <strong>The average across the tournaments across the decades is very similar and stable around 21 games </strong>, meaning that
    it takes on average more than 3 sets for the winner to win the match.
    Ok, but how tight were this sets? There is quite a big difference if a set is 6-0 or 6-4 and this metric does not 
    catch it.
  </p>
  <p>
    To find out about it, I have analysed the average games difference:
  </p>
  <AvgDiffGames />
  <p>
    While there was quite a relevant difference between the tournaments during the 80s,
    this become very small in the 90s and 00s when all the Grand Slam tournaments were following 
    a very similar behaviour.
    The US Open and Wimbledon are the ones showing more stable trends of a decreasing games difference
    across the decades: this is true for Roland Garros and Australian Open as well, but they show
    less stable trends.
    <strong> Overall the games difference is decreasing </strong> for the Grand Slam tournaments, going from more
    than 7 games difference in the 70s to 6 (or even less) in the 20s: this suggests that <strong> the matches
    are becoming tighter and tighter. </strong>
  </p>
  <p>
    So, overall, how predictable are the Grand Slam tournaments? How easy is to predict who is going to win the 
    tournament just by looking at their ranking?
  </p>

  <WinnerRank />

  <p>
    Well, we have to admit, it is not that hard to predict, but but but there are some differences among the
    tournaments.
  </p>
  <p>
    Wimbledon - despite being the most fascinating imo - is also the easiest to predict. <strong> More than 75%
    of the times the winner is someone from the top 3 </strong>: the other three tournaments go from 68% for the US Open 
    to 54-56% for Roland Garros and Australian Open.
    Roland Garros is the one more open to outsiders: 16% of the times the winner's ranking was outisde the top10
    and 28% of the times the winner was out of the top 5.
  </p>
  <p>
    It is interesting to notice how it seems that #2 have better chances of winning the US Open than #1 and how #4 have never 
    won Wimbledon from 1975 onwards.
  </p> 
  <p>
    What is the moral of the story? What did we learn?
    From 1975 to 2024, the men's Grand Slam tournaments have been quite predictable: depending on the tournament
    <strong> you could guess who the winner is going to be just by looking at the ranking in a good number of cases. </strong>
    Overall players with a higher ranking have an increasing chance of winning the match, especially from R16 onwards (70% or higher) and 
    this number is increasing as the years pass. <strong> However, while a player still roughly needs to win 21 games to win the match, 
    the games difference is decreasing across the years. </strong>
  </p>
  <p>
    We can say that the Grand Slam tournaments are becoming more predictable but the matches are tighter. So, we know who
    is going to win, but they have to fight a little harder.
</article>

<style>
  article {
    max-width: 960px;
    margin: 3rem auto;
    padding: 0 1rem;
  }

  h1 {
    font-size: 2rem;
    margin-bottom: 0.5rem;
  }

  p {
    line-height: 1.6;
    margin-bottom: 1rem;
    color: #444;
  }
</style>
