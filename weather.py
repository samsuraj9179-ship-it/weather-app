import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime

# 1. Page Configuration
st.set_page_config(page_title="Weather App", layout="wide")

# --- ANIMATION HTML GENERATOR ---
def generate_bg_html(weather_main, is_night):
    weather_main = weather_main.lower()
    
    if "rain" in weather_main or "drizzle" in weather_main or "thunderstorm" in weather_main:
        bg = "linear-gradient(to bottom, #1f3a5f, #0d1b2a)"
        elements = "".join([f'<div class="rain-drop" style="left:{i*2}%; animation-duration:{0.5+(i%5)*0.2}s; animation-delay:{i*0.1}s;"></div>' for i in range(50)])
    
    elif "snow" in weather_main:
        bg = "linear-gradient(to bottom, #4a6984, #1e3d59)"
        elements = "".join([f'<div class="snowflake" style="left:{i*2}%; width:{4+(i%4)}px; height:{4+(i%4)}px; animation-duration:{2+(i%4)}s; animation-delay:{i*0.2}s;"></div>' for i in range(40)])
    
    elif "cloud" in weather_main:
        bg = "linear-gradient(to bottom, #233142, #455d7a)" if is_night else "linear-gradient(to bottom, #5d7b93, #a2b5c6)"
        elements = "".join([f'<div class="cloud-anim" style="top:{10+(i*15)}%; width:{250+(i*50)}px; height:{150+(i*30)}px; animation-duration:{25+(i*10)}s; animation-delay:-{i*5}s;"></div>' for i in range(5)])
    
    elif is_night:
        bg = "linear-gradient(to bottom, #0f2027, #203a43, #2c5364)"
        elements = "".join([f'<div class="star" style="top:{10*(i%10)}%; left:{3*(i%33)}%; width:{2+(i%3)}px; height:{2+(i%3)}px; animation-delay:{i*0.3}s;"></div>' for i in range(30)])
    
    else: 
        bg = "linear-gradient(to bottom, #1e3c72, #2a5298)"
        elements = '<div class="sun-glow"></div>'
        
    return f'<div class="weather-anim-bg" style="background: {bg};">{elements}</div>'

if "bg_html" not in st.session_state:
    current_hour = datetime.now().hour
    is_default_night = current_hour < 6 or current_hour > 18
    default_weather = "night" if is_default_night else "clear"
    st.session_state.bg_html = generate_bg_html(default_weather, is_default_night)

bg_container = st.empty()
bg_container.markdown(st.session_state.bg_html, unsafe_allow_html=True)

# --- GLOBAL CSS ---
st.markdown("""
    <style>
    .stApp, [data-testid="stAppViewContainer"], [data-testid="stHeader"] {
        background: transparent !important;
        background-color: transparent !important;
    }

    .block-container {
        position: relative;
        z-index: 10;
    }

    .weather-anim-bg {
        position: fixed;
        top: 0;
        left: 0;
        width: 100vw;
        height: 100vh;
        z-index: -1;
        pointer-events: none;
        overflow: hidden;
    }

    .rain-drop {
        position: absolute;
        background: linear-gradient(transparent, rgba(255,255,255,0.6));
        width: 1px;
        height: 25px;
        opacity: 0.7;
        animation: fall linear infinite;
    }
    @keyframes fall {
        0% { transform: translateY(-50px); }
        100% { transform: translateY(105vh); }
    }

    .snowflake {
        position: absolute;
        background: rgba(255, 255, 255, 0.8);
        border-radius: 50%;
        animation: snowfall linear infinite;
    }
    @keyframes snowfall {
        0% { transform: translateY(-20px) translateX(0); }
        100% { transform: translateY(105vh) translateX(20px); }
    }
    
    .cloud-anim {
        position: absolute;
        background: rgba(255, 255, 255, 0.25);
        border-radius: 50%;
        filter: blur(20px);
        animation: drift linear infinite;
    }
    @keyframes drift {
        0% { transform: translateX(-30vw); }
        100% { transform: translateX(120vw); }
    }

    .star {
        position: absolute;
        background: white;
        border-radius: 50%;
        animation: twinkle 3s infinite ease-in-out;
    }
    @keyframes twinkle {
        0%, 100% { opacity: 0.2; transform: scale(0.8); }
        50% { opacity: 1; transform: scale(1.2); }
    }

    .sun-glow {
        position: absolute;
        top: -10%;
        right: -10%;
        width: 50vw;
        height: 50vw;
        background: radial-gradient(circle, rgba(255,204,0,0.15) 0%, transparent 70%);
        border-radius: 50%;
        animation: pulse 6s infinite alternate;
    }
    @keyframes pulse {
        0% { transform: scale(1); opacity: 0.6; }
        100% { transform: scale(1.15); opacity: 1; }
    }

    h1, h2, h3, h4, h5, h6, p, span, label {
        color: white !important;
    }

    div[data-testid="stTextInput"] div[data-baseweb="base-input"] {
        background-color: rgba(255, 255, 255, 0.1) !important;
        border: 1px solid rgba(255, 255, 255, 0.3) !important;
        border-radius: 8px !important;
    }
    div[data-testid="stTextInput"] div[data-baseweb="base-input"]:focus-within {
        border-color: white !important;
        box-shadow: 0 0 8px rgba(255, 255, 255, 0.4) !important;
    }
    div[data-testid="stTextInput"] div[data-baseweb="input"] {
        background-color: transparent !important;
    }
    div[data-testid="stTextInput"] input {
        color: white !important;
        background-color: transparent !important;
        -webkit-text-fill-color: white !important;
    }
    
    div[data-testid="stButton"] button {
        background-color: rgba(255, 255, 255, 0.15) !important;
        color: white !important;
        border: 1px solid rgba(255, 255, 255, 0.3) !important;
        padding: 10px 25px;
    }
    div[data-testid="stButton"] button:hover {
        background-color: rgba(255, 255, 255, 0.3) !important;
        border-color: white !important;
        color: white !important;
    }

    /* --- NEW REUSABLE GLASS CARD CLASS --- */
    .glass-card {
        background: rgba(255, 255, 255, 0.15);
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        border-radius: 20px;
        padding: 30px;
        border: 1px solid rgba(255, 255, 255, 0.2);
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.1);
        transition: all 0.3s ease; /* Smooth transition for hover */
    }

    /* Added transition to tabs and forecast cards as well */
    div[data-testid="stTabs"] {
        background: rgba(255, 255, 255, 0.15);
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        border-radius: 20px;
        padding: 20px;
        border: 1px solid rgba(255, 255, 255, 0.2);
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.1);
        margin-bottom: 20px;
        transition: all 0.3s ease;
    }
    
    .forecast-card {
        background: rgba(255, 255, 255, 0.15);
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        border-radius: 15px;
        padding: 15px;
        border: 1px solid rgba(255, 255, 255, 0.2);
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.1);
        text-align: center;
        transition: all 0.3s ease;
    }

    /* --- NEW GLOWING HOVER EFFECTS --- */
    .glass-card:hover, .forecast-card:hover, div[data-testid="stTabs"]:hover {
        background: rgba(255, 255, 255, 0.22);
        border: 1px solid rgba(255, 255, 255, 0.6);
        box-shadow: 0 0 20px rgba(255, 255, 255, 0.4), 0 8px 32px 0 rgba(0, 0, 0, 0.2);
        transform: translateY(-5px); /* Lifts the card slightly upwards */
    }
    </style>
""", unsafe_allow_html=True)

st.title("🌤️ Real-Time Weather Forecaster")
API_KEY = "52043e5887b9f729a483fc2c95987fc5"

custom_icons = {
    "01d": "☀️", "01n": "🌕",
    "02d": "⛅", "02n": "☁️",
    "03d": "☁️", "03n": "☁️",
    "04d": "☁️", "04n": "☁️",
    "09d": "🌧️", "09n": "🌧️",
    "10d": "🌦️", "10n": "🌧️",
    "11d": "⛈️", "11n": "⛈️",
    "13d": "❄️", "13n": "❄️",
    "50d": "🌫️", "50n": "🌫️"
}

@st.cache_data
def get_user_city():
    try:
        response = requests.get("https://ipapi.co/json/", timeout=3)
        data = response.json()
        return data.get("city", "Bhubaneswar")
    except Exception:
        return "Bhubaneswar"

default_city = get_user_city()
city = st.text_input("Enter City Name", default_city)

if st.button("Get Weather"):
    if not API_KEY:
        st.warning("Please insert your API key first!")
    elif city:
        current_url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric"
        forecast_url = f"https://api.openweathermap.org/data/2.5/forecast?q={city}&appid={API_KEY}&units=metric"
        
        try:
            curr_response = requests.get(current_url, timeout=5)
            curr_data = curr_response.json()
            
            if curr_response.status_code == 200:
                weather_main = curr_data["weather"][0]["main"]
                icon_code = curr_data["weather"][0]["icon"]
                is_night = "n" in icon_code
                
                new_bg_html = generate_bg_html(weather_main, is_night)
                st.session_state.bg_html = new_bg_html
                bg_container.markdown(new_bg_html, unsafe_allow_html=True)

                temp = curr_data["main"]["temp"]
                feels_like = curr_data["main"]["feels_like"]
                humidity = curr_data["main"]["humidity"]
                pressure = curr_data["main"]["pressure"]
                visibility = curr_data.get("visibility", 10000) / 1000
                description = curr_data["weather"][0]["description"].capitalize()
                wind_speed = curr_data["wind"]["speed"]
                
                weather_icon = custom_icons.get(icon_code, "🌍")
                
                timezone_offset = curr_data["timezone"]
                sunrise_ts = curr_data["sys"]["sunrise"] + timezone_offset
                sunset_ts = curr_data["sys"]["sunset"] + timezone_offset
                
                sunrise_time = datetime.utcfromtimestamp(sunrise_ts).strftime("%I:%M %p")
                sunset_time = datetime.utcfromtimestamp(sunset_ts).strftime("%I:%M %p")
                
                col_main, col_metrics = st.columns([1.15, 1])
                
                with col_main:
                    # Cleaned up HTML utilizing the new .glass-card class
                    st.markdown(f"""
                    <div class="glass-card" style="display: flex; align-items: center; justify-content: center; gap: 30px; height: 100%;">
                        <div style="font-size: 90px; line-height: 1;">{weather_icon}</div>
                        <div style="color: white; line-height: 1.4;">
                            <h2 style="margin: 0; font-size: 1.8rem; font-weight: 500;">{city.capitalize()}</h2>
                            <h1 style="margin: 0; font-size: 3.5rem; font-weight: bold;">{temp}°C</h1>
                            <p style="margin: 0; font-size: 1.1rem; opacity: 0.9;">Feels like {feels_like}°C</p>
                            <h3 style="margin: 10px 0 5px 0; font-weight: 500;">{description}</h3>
                            <p style="margin: 0; opacity: 0.8;">Humidity: {humidity}% | Wind: {wind_speed} m/s</p>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col_metrics:
                    # Cleaned up HTML utilizing the new .glass-card class
                    st.markdown(f"""
                    <div class="glass-card" style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px; height: 100%; color: white;">
                        <div><p style="margin:0; opacity:0.8; font-size: 1rem;">Pressure</p><h3 style="margin:0; font-size: 1.4rem;">{pressure} hPa</h3></div>
                        <div><p style="margin:0; opacity:0.8; font-size: 1rem;">Visibility</p><h3 style="margin:0; font-size: 1.4rem;">{visibility} km</h3></div>
                        <div><p style="margin:0; opacity:0.8; font-size: 1rem;">Sunrise</p><h3 style="margin:0; font-size: 1.4rem;">{sunrise_time}</h3></div>
                        <div><p style="margin:0; opacity:0.8; font-size: 1rem;">Sunset</p><h3 style="margin:0; font-size: 1.4rem;">{sunset_time}</h3></div>
                    </div>
                    """, unsafe_allow_html=True)
                
                forecast_response = requests.get(forecast_url, timeout=5)
                if forecast_response.status_code == 200:
                    forecast_data = forecast_response.json()
                    
                    st.markdown("<br>", unsafe_allow_html=True)
                    st.subheader("📈 24-Hour Trend")
                    
                    trend_list = forecast_data["list"][:8]
                    times = [datetime.strptime(x["dt_txt"], "%Y-%m-%d %H:%M:%S").strftime("%I %p") for x in trend_list]
                    temps = [x["main"]["temp"] for x in trend_list]
                    precips = [x.get("pop", 0) * 100 for x in trend_list]
                    winds = [x["wind"]["speed"] for x in trend_list]
                    
                    def create_glass_chart(x_data, y_data, color_hex, unit):
                        fig = go.Figure()
                        text_labels = [f"{round(y, 1)}{unit}" for y in y_data]
                        
                        fig.add_trace(go.Scatter(
                            x=x_data, y=y_data,
                            fill='tozeroy',
                            fillcolor=f"rgba({int(color_hex[1:3], 16)}, {int(color_hex[3:5], 16)}, {int(color_hex[5:7], 16)}, 0.4)",
                            mode='lines+markers+text', 
                            text=text_labels,          
                            textposition='top center', 
                            textfont=dict(color='white', size=12),
                            marker=dict(size=8, color=color_hex, line=dict(width=2, color='white')),
                            line=dict(color=color_hex, width=3),
                            hovertemplate='Time: %{x}<br>Value: %{y}' + unit + '<extra></extra>',
                            cliponaxis=False
                        ))
                        
                        fig.update_layout(
                            paper_bgcolor='rgba(0,0,0,0)',
                            plot_bgcolor='rgba(0,0,0,0)',
                            font=dict(color='white'),
                            margin=dict(l=40, r=40, t=40, b=10),
                            xaxis=dict(
                                showgrid=True, 
                                gridcolor='rgba(255,255,255,0.1)', 
                                zeroline=False,
                                tickfont=dict(color='rgba(255,255,255,0.8)')
                            ),
                            yaxis=dict(
                                showgrid=True, 
                                gridcolor='rgba(255,255,255,0.1)', 
                                zeroline=False, 
                                visible=True, 
                                tickfont=dict(color='rgba(255,255,255,0.8)')
                            )
                        )
                        return fig

                    tab1, tab2, tab3 = st.tabs(["Temperature", "Precipitation", "Wind"])
                    
                    with tab1:
                        st.plotly_chart(create_glass_chart(times, temps, "#f5b041", "°C"), use_container_width=True, config={'displayModeBar': False})
                    with tab2:
                        st.plotly_chart(create_glass_chart(times, precips, "#5dade2", "%"), use_container_width=True, config={'displayModeBar': False})
                    with tab3:
                        st.plotly_chart(create_glass_chart(times, winds, "#aab7b8", " m/s"), use_container_width=True, config={'displayModeBar': False})
                    
                    st.markdown("<br>", unsafe_allow_html=True)
                    st.subheader("📅 5-Day Forecast (3-Hour Intervals)")
                    
                    cols = st.columns(5)
                    daily_forecasts = forecast_data["list"][::8]
                    
                    for i, day in enumerate(cols):
                        if i < len(daily_forecasts):
                            item = daily_forecasts[i]
                            dt_txt = item["dt_txt"].split(" ")[0]
                            date_formatted = datetime.strptime(dt_txt, "%Y-%m-%d").strftime("%b %d")
                            day_temp = item["main"]["temp"]
                            day_desc = item["weather"][0]["description"].capitalize()
                            
                            day_icon_code = item["weather"][0]["icon"]
                            day_icon = custom_icons.get(day_icon_code, "🌍")
                            
                            with day:
                                st.markdown(f"""
                                <div class="forecast-card">
                                    <h4 style="margin: 0; font-size: 1rem; opacity: 0.9;">{date_formatted}</h4>
                                    <div style="font-size: 45px; margin: 10px 0; line-height: 1;">{day_icon}</div>
                                    <h3 style="margin: 0; font-size: 1.2rem;">{day_temp}°C</h3>
                                    <p style="margin: 0; font-size: 0.8rem; opacity: 0.8;">{day_desc}</p>
                                </div>
                                """, unsafe_allow_html=True)
                
            else:
                st.error("City not found. Please check the spelling and try again.")
                
        except Exception as e:
            st.error(f"An unexpected error occurred: {e}")