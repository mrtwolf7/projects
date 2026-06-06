# 🎵 Real-Time Instrument Tracker

An interactive web application built with **Streamlit**, **TensorFlow/Keras**, and **Librosa** that analyzes audio tracks and maps out which musical instruments are playing across the song's timeline. 

This project features a custom-built Convolutional Neural Network (CNN) trained from scratch on the **IRMAS Dataset** to recognize the unique timbral frequencies of 11 different acoustic and electric instruments.

---

## 🚀 Features

* **Cloud-Native Data Pipeline:** Streams audio training data directly into RAM via HTTP range requests—**0% local hard drive storage required**.
* **Custom Audio CNN:** A lightweight, optimized neural network utilizing Global Average Pooling and Batch Normalization to extract intricate acoustic features.
* **Interactive DAW Timeline:** A digital audio workstation (DAW)-style grid visualizer that updates dynamically with unique color codes for each instrument.
* **Playback Synced Cursor:** An interactive timeline controller that lets you scrub a tracking cursor across the visual grid to align perfectly with what you hear.

---

## 🛠️ Tech Stack

* **Frontend UI:** Streamlit, Plotly (Interactive Graphing)
* **Audio Processing:** Librosa, Soundfile
* **Machine Learning:** TensorFlow / Keras, Scikit-learn
* **Data Streaming:** Remotezip

---

## 📁 File Structure

```bash
├── app.py                      # Streamlit frontend user interface
├── analyse_track.py            # Audio processing & ML inference script
├── instrument_cnn_model.keras  # Trained Keras neural network weights
└── label_encoder.pkl           # Saved Scikit-learn instrument label mapper