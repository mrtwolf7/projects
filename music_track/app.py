import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from analyse_track import analyze_track_timeline 

st.set_page_config(layout="wide")
st.title("🎵 Real-Time Instrument Tracker")
st.write("Upload a song snippet to map out exactly which instruments are playing over time.")

# Distinct bright hex colors assigned individually to instruments
COLOR_PALETTE = {
    'Cello': '#FF4B4B', 'Clarinet': '#FFCE56', 'Flute': '#4BC0C0',
    'Acoustic Guitar': '#36A2EB', 'Electric Guitar': '#9966FF', 'Organ': '#FF9F40',
    'Piano': '#00DF89', 'Saxophone': '#E7E9ED', 'Trumpet': '#FF6384',
    'Violin': '#AD73FF', 'Human Voice': '#ACD373'
}

uploaded_file = st.file_uploader("Choose an audio file...", type=["mp3", "wav"])

if uploaded_file is not None:
    
    # 1. Run Pipeline and cache results in session state so it doesn't re-run on slide
    if "ml_df" not in st.session_state:
        with st.spinner("Analyzing track timeline with your Trained CNN Model..."):
            timeline_data, duration_secs, instruments = analyze_track_timeline(uploaded_file)
            st.session_state.ml_df = pd.DataFrame(timeline_data)
            st.session_state.duration_secs = duration_secs
            st.session_state.instruments = instruments
            
    df = st.session_state.ml_df
    duration_secs = st.session_state.duration_secs
    instruments = st.session_state.instruments

    st.write("### 1. Listen to the Track")
    st.audio(uploaded_file, format="audio/mp3")

    st.write("### 2. Timeline Tracking Controls")
    # Interactive Slider replacing the buggy JS tracker hook
    current_pos = st.slider(
        "Match the slider position to the audio timestamp to update the tracker line:", 
        min_value=0, 
        max_value=duration_secs - 3, 
        value=0,
        step=1
    )

    # 2. Build Multi-Color Plotly Timeline Grid manually via Scatter Blocks
    fig = go.Figure()

    for inst in instruments:
        # Filter for active time frames belonging to this specific instrument
        inst_df = df[(df["Instrument"] == inst) & (df["Status"] == 1)]
        color = COLOR_PALETTE.get(inst, "#00DF89")
        
        fig.add_trace(go.Scatter(
            x=inst_df["Second"],
            y=inst_df["Instrument"],
            mode='markers',
            marker=dict(symbol='square', size=22, color=color, line=dict(width=0)),
            name=inst,
            hoverinfo='text',
            text=[f"{inst} playing at {s}s" for s in inst_df["Second"]]
        ))

    # 3. ADD THE PROGRESS CURSOR INDICATOR LINE (Controlled by slider)
    fig.add_vline(x=current_pos, line_width=4, line_dash="solid", line_color="#FF4B4B")

    # Layout tuning mimicking a native multi-track Audio DAW workstation
    fig.update_layout(
        showlegend=False,
        xaxis=dict(title="Timeline (Seconds)", range=[-0.5, duration_secs-2.5], dtick=1, gridcolor="#222", zeroline=False),
        yaxis=dict(title="Instruments", categoryarray=instruments, gridcolor="#222"),
        plot_bgcolor="#111",
        paper_bgcolor="#111",
        font_color="white",
        height=450,
        margin=dict(l=50, r=50, t=20, b=20)
    )

    st.plotly_chart(fig, use_container_width=True)
    st.info(f"📍 Current display window centered around: **{current_pos} seconds**")