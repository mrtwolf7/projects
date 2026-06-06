import io
import pickle
import numpy as np
import librosa
import tensorflow as tf

# IRMAS official class code translation map
INSTRUMENT_MAP = {
    'cel': 'Cello',
    'cla': 'Clarinet',
    'flu': 'Flute',
    'gac': 'Acoustic Guitar',
    'gel': 'Electric Guitar',
    'org': 'Organ',
    'pia': 'Piano',
    'sax': 'Saxophone',
    'tru': 'Trumpet',
    'vio': 'Violin',
    'voi': 'Human Voice'
}

def analyze_track_timeline(uploaded_file):
    model = tf.keras.models.load_model("instrument_cnn_model.keras")
    with open("label_encoder.pkl", "rb") as f:
        label_encoder = pickle.load(f)
    
    classes = label_encoder.classes_  # ['cel', 'gac'...]
    
    file_bytes = io.BytesIO(uploaded_file.read())
    y, sr = librosa.load(file_bytes, sr=16000)
    total_duration = int(librosa.get_duration(y=y, sr=sr))
    
    window_size_sec = 3
    window_samples = window_size_sec * sr
    timeline_records = []
    
    # Translate the class list into human names right away
    human_instruments = [INSTRUMENT_MAP.get(c, c) for c in classes]
    
    for current_sec in range(0, total_duration - window_size_sec + 1):
        start_sample = current_sec * sr
        end_sample = start_sample + window_samples
        audio_chunk = y[start_sample:end_sample]
        
        mel_spec = librosa.feature.melspectrogram(y=audio_chunk, sr=sr, n_mels=128)
        mel_spec_db = librosa.power_to_db(mel_spec, ref=np.max)
        
        if mel_spec_db.shape[1] != 94:
            mel_spec_db = librosa.util.fix_length(mel_spec_db, size=94, axis=1)
            
        input_tensor = np.expand_dims(mel_spec_db, axis=(0, -1))
        predictions = model.predict(input_tensor, verbose=0)[0]
        
        for idx, short_name in enumerate(classes):
            # Translate short code to full name
            full_name = INSTRUMENT_MAP.get(short_name, short_name)
            confidence_score = float(predictions[idx])
            is_active = 1 if confidence_score > 0.25 else 0
            
            timeline_records.append({
                "Second": current_sec,
                "Instrument": full_name,  # Matches friendly names
                "Confidence": confidence_score,
                "Status": is_active
            })
            
    return timeline_records, total_duration, human_instruments