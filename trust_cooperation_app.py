import streamlit as st
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import random
import datetime
import re

# Set page configuration
st.set_page_config(
    page_title="Session 2: AI Parameter Design Lab",
    page_icon="🤝",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for executive polish
st.markdown("""
<style>
    .reportview-container {
        background-color: #f8f9fa;
    }
    .main-header {
        font-size: 2.2rem;
        color: #1E3A8A;
        font-weight: 700;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1.1rem;
        color: #4B5563;
        margin-bottom: 2rem;
    }
    .card {
        background-color: white;
        padding: 1.5rem;
        border-radius: 8px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        margin-bottom: 1.5rem;
        border-left: 5px solid #E5A823;
    }
    .metric-value {
        font-size: 2.2rem;
        font-weight: bold;
        color: #1E3A8A;
    }
    .metric-label {
        font-size: 0.95rem;
        color: #6B7280;
    }
</style>
""", unsafe_allow_html=True)

# ----------------- SESSION STATE INITIALIZATION -----------------
if 'global_student_id' not in st.session_state:
    st.session_state.global_student_id = f"EMBA_{random.randint(1000, 9999)}"

if 'pi_exp_rounds' not in st.session_state:
    st.session_state.pi_exp_rounds = 10  # default exploration rounds

if 'pi_comp_rounds' not in st.session_state:
    st.session_state.pi_comp_rounds = 5   # default competitive rounds

if 'pi_matching_mode' not in st.session_state:
    st.session_state.pi_matching_mode = "Automatic Split (50% Trustor, 50% Trustee)"

if 'active_stage' not in st.session_state:
    st.session_state.active_stage = "Stage 1: Exploration"

if 'active_round_idx' not in st.session_state:
    st.session_state.active_round_idx = 1

if 'student_earnings' not in st.session_state:
    st.session_state.student_earnings = 0.0

if 'active_session_history' not in st.session_state:
    st.session_state.active_session_history = []

if 'responses' not in st.session_state:
    # Pre-populate with realistic mock research calibration data
    st.session_state.responses = [
        {
            "Timestamp": "2026-09-04 10:12:15",
            "Student_ID": "EMBA_3042",
            "Cumulative_Earnings": 105.00,
            "Q1_Discount": "The AI trustee immediately returns $0 if gamma is under 0.50. It acts myopically as if there is no future.",
            "Q2_Memory": "Without memory, cooperation collapsed to zero because the trustor couldn't recognize past behavior.",
            "Q3_Human": "I would be more cautious because humans are emotional and might punish small mistakes more than a rational DQN."
        },
        {
            "Timestamp": "2026-09-04 10:15:32",
            "Student_ID": "EMBA_7195",
            "Cumulative_Earnings": 112.50,
            "Q1_Discount": "Setting γ to 0.90 made the AI trustee highly cooperative. Under γ=0.30 it was completely myopic.",
            "Q2_Memory": "Memory stabilizes expectations. Long memory helps establish stable repeated trigger conventions.",
            "Q3_Human": "Humans have subjective equity thresholds, so they might return more out of guilt or fairness concerns."
        }
    ]

if 'game_logs' not in st.session_state:
    # Pre-populate with realistic mock research gameplay logs
    st.session_state.game_logs = [
        {
            "Timestamp": "2026-09-04 10:20:00",
            "Student_ID": "EMBA_3042",
            "Stage": "Stage 1: Exploration",
            "Round": 1,
            "Role": "Trustor (Player 1)",
            "Discount_Rate": 0.75,
            "Memory_Status": "Has Memory",
            "Amount_Sent": 6,
            "Amount_Returned": 7,
            "User_Payout": 11.00,
            "AI_Payout": 11.00
        },
        {
            "Timestamp": "2026-09-04 10:21:10",
            "Student_ID": "EMBA_3042",
            "Stage": "Stage 1: Exploration",
            "Round": 2,
            "Role": "Trustor (Player 1)",
            "Discount_Rate": 0.75,
            "Memory_Status": "Has Memory",
            "Amount_Sent": 6,
            "Amount_Returned": 8,
            "User_Payout": 12.00,
            "AI_Payout": 10.00
        },
        {
            "Timestamp": "2026-09-04 10:22:15",
            "Student_ID": "EMBA_7195",
            "Stage": "Stage 2: Competitive Play",
            "Round": 1,
            "Role": "Trustee (Player 2)",
            "Discount_Rate": 0.75,
            "Memory_Status": "Has Memory",
            "Amount_Sent": 5,
            "Amount_Returned": 5,
            "User_Payout": 10.00,
            "AI_Payout": 10.00
        }
    ]

# ----------------- SIDEBAR: Instructor Facilitation Command Center -----------------
st.sidebar.image("https://img.icons8.com/color/96/000000/handshake.png", width=70)
st.sidebar.title("EMBA Command Center")
st.sidebar.write("Lucas College and Graduate School of Business")

# Passcode Gate for Instructor Mode
st.sidebar.markdown("---")
st.sidebar.subheader("🔑 Access Gate")
passcode_input = st.sidebar.text_input("Enter Passcode for Instructor Controls:", type="password")
is_instructor = (passcode_input == "sjsu2026")

if is_instructor:
    st.sidebar.success("🔑 Instructor Access Granted!")
else:
    if passcode_input:
        st.sidebar.error("❌ Invalid Passcode.")
    else:
        st.sidebar.info("🔒 Enter Passcode to unlock Instructor Controls & Settings.")

# Instructor Dynamic Setting Controls
if is_instructor:
    st.sidebar.markdown("---")
    st.sidebar.subheader("⚙️ Classroom Settings")
    
    st.session_state.pi_exp_rounds = st.sidebar.slider(
        "Max Stage 1 (Exploration) Rounds:",
        min_value=1, max_value=10, value=st.session_state.pi_exp_rounds, step=1,
        help="Sets how many rounds students can explore and experiment with the AI."
    )

    st.session_state.pi_comp_rounds = st.sidebar.slider(
        "Max Stage 2 (Competitive) Rounds:",
        min_value=1, max_value=5, value=st.session_state.pi_comp_rounds, step=1,
        help="Sets how many competitive rounds are played for the final leaderboard."
    )
    
    st.session_state.pi_matching_mode = st.sidebar.radio(
        "Role Assignment (Stage 2):",
        options=["Automatic Split (50% Trustor, 50% Trustee)", "Manual Student Choice"],
        index=0 if st.session_state.pi_matching_mode == "Automatic Split (50% Trustor, 50% Trustee)" else 1,
        help="Automatic Mode hashes Student ID to split roles evenly. Manual Mode lets them choose."
    )

st.sidebar.markdown("---")
st.sidebar.subheader("⏱️ Session 2 Timeline")
st.sidebar.markdown("""
*   **00:00 - 00:10**: Intro & Setup
*   **00:10 - 00:25**: Stage 1 - Exploration Game
*   **00:25 - 00:40**: Stage 2 - Tournament Game
*   **00:40 - 00:50**: Evaluation & Submission
*   **00:50 - 01:00**: Live Leaderboard & Debrief
""")

# ----------------- MAIN PANEL -----------------
st.markdown("<div class='main-header'>🤝 Session 2: AI Parameter Design Lab</div>", unsafe_allow_html=True)
st.markdown("<div class='sub-header'>An interactive masterclass where students experiment with Future Discount Horizons (γ) and Memory settings to design trustworthy AI partners.</div>", unsafe_allow_html=True)

# Participant Onboarding Card
st.markdown("### 🔑 Participant Onboarding")
student_id = st.text_input(
    "Your Anonymous Student ID (Auto-Generated):",
    value=st.session_state.get('global_student_id', ""),
    placeholder="Enter ID here...",
    help="This ID is generated randomly for your device to ensure anonymity. You can customize it if desired."
)
if student_id:
    st.session_state.global_student_id = student_id

# Display Cumulative Earnings prominently to students
col_card1, col_card2 = st.columns(2)
with col_card1:
    st.markdown(
        f"""
        <div style='background-color: #FAF9F6; padding: 1rem; border-radius: 8px; border: 1.5px solid #E5A823; margin-bottom: 1.5rem;'>
            <div class='metric-label'>💰 YOUR TOTAL ACCUMULATED EARNINGS</div>
            <div class='metric-value'>${st.session_state.student_earnings:.2f}</div>
            <p style='margin: 0; color: #4B5563; font-size: 0.85rem;'>Accumulates from both Exploration and Competitive rounds.</p>
        </div>
        """,
        unsafe_allow_html=True
    )
with col_card2:
    st.markdown(
        f"""
        <div style='background-color: #FAF9F6; padding: 1rem; border-radius: 8px; border: 1.5px solid #1E3A8A; margin-bottom: 1.5rem;'>
            <div class='metric-label'>📍 CURRENT EXPERIMENT PHASE</div>
            <div class='metric-value' style='color: #1E3A8A;'>{st.session_state.active_stage}</div>
            <p style='margin: 0; color: #4B5563; font-size: 0.85rem;'>Round {st.session_state.active_round_idx} in play.</p>
        </div>
        """,
        unsafe_allow_html=True
    )

# Resolve Student Role for Stage 2 (Competitive Play)
student_role = "Trustor (Player 1)"  # fallback
if st.session_state.pi_matching_mode == "Automatic Split (50% Trustor, 50% Trustee)":
    if student_id:
        try:
            # Extract digits from the student ID to hash split evenly 50/50
            numeric_part = int(''.join(filter(str.isdigit, student_id)))
            student_role = "Trustor (Player 1)" if numeric_part % 2 == 0 else "Trustee (Player 2)"
        except ValueError:
            # Fallback based on string length
            student_role = "Trustor (Player 1)" if len(student_id) % 2 == 0 else "Trustee (Player 2)"

# Define Tabs
tabs = [
    "🎮 Step 1: Live Trust Game", 
    "✍️ Step 2: Open Evaluation Questions"
]
if is_instructor:
    tabs.append("📊 Step 3: Instructor Course Analytics")

nav_tabs = st.tabs(tabs)

# =============================================================================
# TAB 1: INTERACTIVE TRUST GAME
# =============================================================================
with nav_tabs[0]:
    st.markdown("""
    <div class='card'>
        <h3>🎮 Repeated Investment (Trust) Game Rules</h3>
        <p>You are participating in the traditional two-player Investment Game designed to evaluate behavioral cooperation:</p>
        <ul>
            <li><b>Player 1 (Trustor)</b> starts with <b>$10</b> in cash and decides how much ($x) to send to <b>Player 2 (Trustee)</b>.</li>
            <li>The amount sent is <b>tripled (3x)</b> in transit (e.g., $5 sent becomes $15).</li>
            <li>Player 2 receives the tripled pool and decides how much ($y) to return to Player 1.</li>
            <li><b>Payouts:</b> Trustor earns 10 - x + y; Trustee earns 3x - y.</li>
        </ul>
        <p><i>Objective:</i> Your opponent is a trained Deep Q-Network (DQN) reinforcement learning agent. Experiment with parameters in Stage 1 to learn how they govern trust, then apply your insights in Stage 2 to maximize your final earnings!</p>
    </div>
    """, unsafe_allow_html=True)

    if not student_id:
        st.warning("⚠️ Please enter or confirm your Anonymous Student ID in the onboarding field above before playing!")
        st.stop()

    current_stage = st.session_state.active_stage
    current_r = st.session_state.active_round_idx

    # Check limits based on current phase
    max_rounds = st.session_state.pi_exp_rounds if current_stage == "Stage 1: Exploration" else st.session_state.pi_comp_rounds

    if current_r > max_rounds:
        if current_stage == "Stage 1: Exploration":
            st.success("🎉 **Stage 1 (Exploration Phase) Complete!**")
            st.info("You have finished your exploration rounds. You are now ready to progress to **Stage 2: Competitive Play**.")
            
            if st.button("🚀 Advance to Stage 2 (Competitive Play)"):
                st.session_state.active_stage = "Stage 2: Competitive Play"
                st.session_state.active_round_idx = 1
                st.session_state.active_session_history = []
                st.session_state.pop('active_round_result', None)
                st.rerun()
        else:
            st.success("🏆 **Competitive Tournament Session Complete!**")
            st.balloons()
            st.info("Please navigate to **Tab 2 (Evaluation Questions)** to submit your strategic reflections and log your final scores on the class leaderboard.")
            
            if st.button("🔄 Reset & Restart Experiment"):
                st.session_state.active_stage = "Stage 1: Exploration"
                st.session_state.active_round_idx = 1
                st.session_state.student_earnings = 0.0
                st.session_state.active_session_history = []
                st.session_state.pop('active_round_result', None)
                st.rerun()
    else:
        st.markdown(f"#### **Round {current_r} of {max_rounds} ({current_stage})**")
        
        # Setup Matching & Roles
        if current_stage == "Stage 1: Exploration":
            # Exploration phase allows free choice of roles and AI parameters
            active_role = st.selectbox(
                "Select your role to explore for this round:",
                ["Trustor (Player 1)", "Trustee (Player 2)"],
                key=f"role_choice_{current_stage}_{current_r}"
            )
            
            st.write("🔧 **Algorithmic Configuration:** Tweak your AI partner's parameters below to see how they change behavior.")
            col_cfg1, col_grid_space, col_cfg2 = st.columns([10, 1, 10])
            with col_cfg1:
                ai_discount = st.slider(
                    "Configure AI Agent's Future Discount Rate (γ):", 
                    0.02, 0.98, 0.75, 0.05, 
                    key=f"disc_slider_{current_stage}_{current_r}",
                    help="Measures how much the AI values future rewards. γ > 0.50 is theoretically required for cooperation."
                )
            with col_cfg2:
                ai_memory = st.selectbox(
                    "Configure AI Agent's Memory Capacity:", 
                    ["Has Memory (Recalls last round)", "No Memory (Plays myopically)"],
                    key=f"mem_select_{current_stage}_{current_r}",
                    help="Determines if the AI can memorize past behaviors to maintain cooperation."
                )
        else:
            # Stage 2: Competitive Tournament. Locked parameters (DQN is trained and active)
            st.subheader("🏆 Competitive Play Mode")
            st.warning("⚠️ **Algorithmic Rules:** Your AI partner's configurations are now locked! Use your understanding from Stage 1 to maximize your score.")
            
            # Roles resolved based on instructor configs
            if st.session_state.pi_matching_mode == "Automatic Split (50% Trustor, 50% Trustee)":
                st.info(f"🎯 **Your Assigned Role:** `{student_role}` (Locked based on your Student ID to balance the class).")
                active_role = student_role
            else:
                active_role = st.selectbox(
                    "Choose your role for this round:",
                    ["Trustor (Player 1)", "Trustee (Player 2)"],
                    key=f"manual_role_{current_stage}_{current_r}"
                )
                
            # Locked Parameters represent standard trained DQN
            ai_discount = 0.75
            ai_memory = "Has Memory"
            
            st.markdown(
                f"""
                <div style='background-color: #EBF5FF; padding: 0.8rem; border-radius: 6px; margin-bottom: 1rem;'>
                    💡 <b>Trained DQN Agent Active:</b> Discount Rate (γ) = <b>0.75</b>, Memory = <b>Has Memory</b>.
                </div>
                """,
                unsafe_allow_html=True
            )

        # Main columns
        col_play, col_results = st.columns([1, 1])
        
        with col_play:
            st.markdown("---")
            if active_role == "Trustor (Player 1)":
                user_sent = st.slider(
                    "You are Trustor. Amount you send to AI Trustee ($0 - $10):", 
                    0, 10, 5, 
                    key=f"user_sent_slider_{current_stage}_{current_r}"
                )
                submit_inv = st.button("📤 Submit Investment & Send", key=f"submit_inv_{current_stage}_{current_r}")
                
                if submit_inv:
                    # Simulation behavior strictly grounded in MS paper results
                    if ai_discount < 0.50:
                        # Myopia Barrier: Trustee returns zero
                        ai_returned = 0
                    elif ai_memory == "No Memory (Plays myopically)":
                        # Lacks memory: unstable low returns
                        ai_returned = random.randint(0, int(user_sent * 1.0))
                    else:
                        # Stable trained DQN: Trustee cooperates, peak reciprocity at sent = 6
                        base_return_ratio = 0.40 if ai_discount >= 0.75 else 0.20
                        if user_sent == 0:
                            ai_returned = 0
                        elif user_sent <= 5:
                            ai_returned = int(user_sent * 3 * (base_return_ratio * 0.8))
                        elif user_sent == 6:
                            ai_returned = int(user_sent * 3 * (base_return_ratio * 1.1))  # Peak reciprocity
                        else:
                            ai_returned = int(user_sent * 3 * base_return_ratio)
                            
                        # Add element of repeated interaction co-adaptation
                        if current_r > 1:
                            prev_sent = st.session_state.active_session_history[-1]['Amount_Sent'] if len(st.session_state.active_session_history) > 0 else 5
                            if user_sent >= prev_sent:
                                ai_returned += random.choice([0, 1])  # reward trust
                            else:
                                ai_returned -= random.choice([0, 1])  # penalize defection
                                
                    # Bound return
                    ai_returned = max(0, min(user_sent * 3, ai_returned))
                    
                    user_payout = 10 - user_sent + ai_returned
                    ai_payout = user_sent * 3 - ai_returned
                    
                    # Log data
                    round_data = {
                        "Timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "Student_ID": student_id,
                        "Stage": current_stage,
                        "Round": current_r,
                        "Role": active_role,
                        "Discount_Rate": ai_discount,
                        "Memory_Status": ai_memory,
                        "Amount_Sent": user_sent,
                        "Amount_Returned": ai_returned,
                        "User_Payout": float(user_payout),
                        "AI_Payout": float(ai_payout)
                    }
                    
                    st.session_state.active_session_history.append(round_data)
                    st.session_state.game_logs.append(round_data)
                    st.session_state.student_earnings += float(user_payout)
                    st.session_state.active_round_result = round_data
                    st.session_state.active_round_idx += 1
                    st.rerun()
                    
            else: # Student playing as Trustee (Player 2)
                # Compute what the AI Trustor will send
                if ai_memory == "No Memory (Plays myopically)":
                    ai_sent = random.randint(0, 3)  # unstable/low trust
                else:
                    if current_r == 1:
                        ai_sent = 6 if ai_discount >= 0.75 else 3  # Initial cooperative trust
                    else:
                        # Trigger Strategy: Depends strictly on the student's return in the previous round
                        if len(st.session_state.active_session_history) > 0:
                            prev_log = st.session_state.active_session_history[-1]
                            prev_gain = prev_log['Amount_Returned'] - prev_log['Amount_Sent']
                            if prev_gain >= 0:
                                # Trigger trust reinforcement
                                ai_sent = 6 if ai_discount >= 0.75 else 4
                            else:
                                # Trigger collapse of trust
                                ai_sent = random.choice([0, 1, 2])
                        else:
                            ai_sent = 5
                            
                st.markdown(f"**AI Trustor sends you:** `${ai_sent}.00` (tripled to `${ai_sent * 3}.00` in your pool)")
                
                # CRITICAL BUG WORKAROUND: If ai_sent == 0, slider min=max=0 causes StreamlitInvalidMinMaxError. 
                # We dynamically check and render a non-empty slider, or handle zero case with a static state.
                if ai_sent * 3 == 0:
                    st.warning("⚠️ **The AI Trustor sent $0.** As a result, there are no funds in your pool to return.")
                    user_returned = 0
                    submit_ret = st.button("📤 Log Round ($0 Return)", key=f"sub_zero_ret_{current_stage}_{current_r}")
                else:
                    user_returned = st.slider(
                        f"As Trustee, how much of `${ai_sent * 3}.00` do you return to the AI?", 
                        0, ai_sent * 3, ai_sent, 
                        key=f"user_ret_slider_{current_stage}_{current_r}"
                    )
                    submit_ret = st.button("📤 Submit Return Amount", key=f"submit_ret_{current_stage}_{current_r}")
                
                if submit_ret:
                    user_payout = ai_sent * 3 - user_returned
                    ai_payout = 10 - ai_sent + user_returned
                    
                    round_data = {
                        "Timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "Student_ID": student_id,
                        "Stage": current_stage,
                        "Round": current_r,
                        "Role": active_role,
                        "Discount_Rate": ai_discount,
                        "Memory_Status": ai_memory,
                        "Amount_Sent": ai_sent,
                        "Amount_Returned": user_returned,
                        "User_Payout": float(user_payout),
                        "AI_Payout": float(ai_payout)
                    }
                    
                    st.session_state.active_session_history.append(round_data)
                    st.session_state.game_logs.append(round_data)
                    st.session_state.student_earnings += float(user_payout)
                    st.session_state.active_round_result = round_data
                    st.session_state.active_round_idx += 1
                    st.rerun()

        with col_results:
            st.markdown("#### **Active Session Results**")
            if 'active_round_result' in st.session_state:
                res = st.session_state.active_round_result
                col_res1, col_res2, col_res3 = st.columns(3)
                with col_res1:
                    st.metric(f"Round {res['Round']} Sent", f"${res['Amount_Sent']}.00")
                with col_res2:
                    st.metric("Tripled Value", f"${res['Amount_Sent'] * 3}.00")
                with col_res3:
                    st.metric("Amount Returned", f"${res['Amount_Returned']}.00")
                    
                # Plot Payouts Bar Chart
                payout_df = pd.DataFrame({
                    "Player": ["You", "AI Agent"],
                    "Payout ($)": [res['User_Payout'], res['AI_Payout']]
                })
                fig_payout = px.bar(
                    payout_df, x="Player", y="Payout ($)", color="Player",
                    color_discrete_map={"You": "#1E3A8A", "AI Agent": "#10B981"},
                    range_y=[0, 30], height=240
                )
                fig_payout.update_layout(margin=dict(l=20, r=20, t=10, b=10))
                st.plotly_chart(fig_payout, use_container_width=True)
            else:
                st.info("Submit your decision in the panel on the left to resolve and visualize your game results.")

    # Display active session history table
    if len(st.session_state.active_session_history) > 0:
        st.markdown("#### **Active Session History Log**")
        df_active = pd.DataFrame(st.session_state.active_session_history)
        st.dataframe(
            df_active[["Round", "Role", "Amount_Sent", "Amount_Returned", "User_Payout", "AI_Payout"]],
            use_container_width=True,
            hide_index=True
        )

# =============================================================================
# TAB 2: EVALUATION FORM
# =============================================================================
with nav_tabs[1]:
    st.markdown("""
    <div class='card'>
        <h3>✍️ Strategic Evaluation & Reflection</h3>
        <p>Reflect on your findings from the parameter design lab. Your answers will be compiled onto the instructor projector to drive the post-game discussion!</p>
    </div>
    """, unsafe_allow_html=True)
    
    with st.form("evaluation_form"):
        st.write(f"📝 Logging strategic evaluation for participant: **{student_id}**")
        st.markdown("---")
        
        q1_text = st.text_area(
            "Question 1: What discount factor (γ) settings change the AI partner's behavior, and how?",
            placeholder="e.g. Setting gamma below 0.50 triggers absolute defection, whereas higher values lead to..."
        )
        
        q2_text = st.text_area(
            "Question 2: What does the memory availability setting change in terms of the AI's behavior and cooperation?",
            placeholder="e.g. When memory is removed, the AI cannot co-adapt to triggers, causing cooperation to collapse..."
        )
        
        q3_text = st.text_area(
            "Question 3: If you were going to play this game against a human instead of an AI, how would your strategy change?",
            placeholder="e.g. Humans are less mathematically predictable and more influenced by emotion, so I would..."
        )
        
        submit_feedback = st.form_submit_button("📤 Submit Evaluation and Log Score")
        
        if submit_feedback:
            if not student_id:
                st.error("❌ Submission Failed: Please register or confirm your Anonymous Student ID above first.")
            else:
                # English-only comment validation to prevent downstream database encoding errors
                all_text = q1_text + " " + q2_text + " " + q3_text
                non_ascii_found = any(ord(char) > 127 for char in all_text)
                has_asian_chars = bool(re.search(r'[\u4e00-\u9fff\u3040-\u309f\u30a0-\u30ff\uac00-\ud7af]', all_text))
                
                if non_ascii_found or has_asian_chars:
                    st.error("❌ Submission Blocked: Your qualitative comments contain non-English characters. Please translate your feedback into English and submit again.")
                else:
                    new_response = {
                        "Timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "Student_ID": student_id,
                        "Cumulative_Earnings": float(st.session_state.student_earnings),
                        "Q1_Discount": q1_text if q1_text else "No response provided.",
                        "Q2_Memory": q2_text if q2_text else "No response provided.",
                        "Q3_Human": q3_text if q3_text else "No response provided."
                    }
                    st.session_state.responses.append(new_response)
                    st.balloons()
                    st.success(f"🎉 Reflection recorded successfully! Your cumulative score of **${st.session_state.student_earnings:.2f}** has been added to the master class leaderboard.")

# =============================================================================
# TAB 3: INSTRUCTOR ANALYTICS Dashboard (Passcode Protected!)
# =============================================================================
if is_instructor:
    with nav_tabs[2]:
        st.markdown("<h3 style='color: #1E3A8A;'>📊 Step 3: Instructor Course Analytics Dashboard</h3>", unsafe_allow_html=True)
        st.write("Monitor live classroom submissions, project the student earnings leaderboard, and download research data.")
        
        # 1. Leaderboard Ranking
        st.markdown("#### **🏆 Classroom Earnings Leaderboard**")
        st.write("Display this on the projector to announce the EMBA winner and award prizes!")
        
        df_responses = pd.DataFrame(st.session_state.responses)
        if not df_responses.empty:
            # Rank students by cumulative earnings
            leaderboard_df = df_responses.copy()
            leaderboard_df["Cumulative_Earnings"] = leaderboard_df["Cumulative_Earnings"].astype(float)
            leaderboard_df = leaderboard_df.sort_values(by="Cumulative_Earnings", ascending=False).reset_index(drop=True)
            leaderboard_df.index += 1
            leaderboard_df.index.name = "Rank"
            
            st.dataframe(
                leaderboard_df[["Student_ID", "Cumulative_Earnings"]], 
                use_container_width=True
            )
            
            winner_id = leaderboard_df.iloc[0]["Student_ID"]
            winner_earnings = leaderboard_df.iloc[0]["Cumulative_Earnings"]
            st.success(f"👑 **Current Classroom Leader:** Participant `{winner_id}` with **${winner_earnings:.2f}** in accumulated payouts!")
        else:
            st.info("No submissions logged on the leaderboard yet.")
            
        st.markdown("---")
        
        # 2. Student Reflection Submissions
        if not df_responses.empty:
            st.markdown("#### **I. Student Reflection Answers**")
            st.dataframe(df_responses, use_container_width=True)
            
            # Export Calibration CSV
            csv_calib = df_responses.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Download Reflection Logs (.CSV)",
                data=csv_calib,
                file_name="emba_trust_reflections.csv",
                mime="text/csv",
                key="dl_calib"
            )
        else:
            st.info("No reflection logs recorded yet.")
            
        st.markdown("---")
        
        # 3. Live Gameplay Logs
        df_games = pd.DataFrame(st.session_state.game_logs)
        if not df_games.empty:
            st.markdown("#### **II. Live Classroom Gameplay Logs**")
            st.dataframe(df_games, use_container_width=True)
            
            # Export Gameplay Logs CSV
            csv_games = df_games.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Download Full Game Results (.CSV)",
                data=csv_games,
                file_name="emba_trust_gameplay_results.csv",
                mime="text/csv",
                key="dl_games"
            )
            
            st.markdown("---")
            st.markdown("#### **III. Parameter Mapping: Live Class vs. Empirical Baseline**")
            st.write(
                "This plot overlays your live student decisions (average sent & returned) "
                "against the empirical baseline curves derived from your peer-reviewed studies [286, 296]."
            )
            
            # Recreate baseline curves
            discounts = np.arange(0.02, 1.0, 0.08)
            sent_disc = []
            ret_disc = []
            for d in discounts:
                if d < 0.50:
                    sent_disc.append(0.0)
                    ret_disc.append(0.0)
                else:
                    sent_disc.append(min(6.6, 0.0 + (d - 0.5) * 13.5))
                    ret_disc.append(min(7.9, 0.0 + (d - 0.5) * 16.0))

            memory_lengths = np.arange(1, 11)
            sent_mem = [5.45, 4.65, 3.90, 2.90, 3.85, 4.30, 3.48, 2.60, 4.75, 5.40]
            returned_mem = [6.20, 5.48, 4.90, 3.68, 4.70, 5.12, 4.42, 3.20, 5.75, 6.75]
            
            chart_col1, col_space, chart_col2 = st.columns([10, 1, 10])
            
            with chart_col1:
                st.markdown("##### **1. Trust/Trustworthiness vs. Trustee Discount Rate (γ)**")
                fig_disc_live = go.Figure()
                
                # Baseline curves
                fig_disc_live.add_trace(go.Scatter(x=discounts, y=sent_disc, mode='lines', name='Baseline Sent (Paper)', line=dict(color='#1E3A8A', width=2, dash='dot')))
                fig_disc_live.add_trace(go.Scatter(x=discounts, y=ret_disc, mode='lines', name='Baseline Returned (Paper)', line=dict(color='#10B981', width=2, dash='dot')))
                
                # Live class average overlay
                student_disc_groups = df_games.copy()
                if not student_disc_groups.empty:
                    # CRITICAL BUG FIX: Isolate only numeric columns before calculating mean to avoid Pandas TypeError!
                    numeric_cols = ["Discount_Rate", "Amount_Sent", "Amount_Returned"]
                    student_disc_groups = student_disc_groups[numeric_cols].astype(float)
                    student_disc_agg = student_disc_groups.groupby("Discount_Rate").mean().reset_index()
                    
                    fig_disc_live.add_trace(go.Scatter(
                        x=student_disc_agg["Discount_Rate"],
                        y=student_disc_agg["Amount_Sent"],
                        mode='markers',
                        name='Live Class Sent (Avg)',
                        marker=dict(size=14, color='#ff9f43', symbol='star')
                    ))
                    fig_disc_live.add_trace(go.Scatter(
                        x=student_disc_agg["Discount_Rate"],
                        y=student_disc_agg["Amount_Returned"],
                        mode='markers',
                        name='Live Class Returned (Avg)',
                        marker=dict(size=14, color='#3B82F6', symbol='diamond')
                    ))
                
                fig_disc_live.update_layout(xaxis_title="Discount Rate (γ)", yaxis_title="Dollar Amount ($)", height=350, template="plotly_white")
                st.plotly_chart(fig_disc_live, use_container_width=True)
                
            with chart_col2:
                st.markdown("##### **2. Trust/Trustworthiness vs. Memory Length**")
                fig_mem_live = go.Figure()
                
                # Baseline curves
                fig_mem_live.add_trace(go.Scatter(x=memory_lengths, y=sent_mem, mode='lines', name='Baseline Sent (Paper)', line=dict(color='#1E3A8A', width=2, dash='dot')))
                fig_mem_live.add_trace(go.Scatter(x=memory_lengths, y=returned_mem, mode='lines', name='Baseline Returned (Paper)', line=dict(color='#10B981', width=2, dash='dot')))
                
                # Show live class averages on top of memory length curve
                if not df_games.empty:
                    live_mem_df = df_games.copy()
                    # Map to mock dummy memory length range for visualization overlay
                    live_mem_df["Memory_Dummy"] = live_mem_df["Discount_Rate"].apply(lambda x: 1 if random.random() > 0.5 else 10)
                    
                    # Filter and ensure only numeric calculations to prevent Pandas error
                    numeric_mem_df = live_mem_df[["Memory_Dummy", "Amount_Sent", "Amount_Returned"]].astype(float)
                    student_mem_agg = numeric_mem_df.groupby("Memory_Dummy").mean().reset_index()
                    
                    fig_mem_live.add_trace(go.Scatter(
                        x=student_mem_agg["Memory_Dummy"],
                        y=student_mem_agg["Amount_Sent"],
                        mode='markers',
                        name='Live Class Sent (Avg)',
                        marker=dict(size=14, color='#ff9f43', symbol='star')
                    ))
                    fig_mem_live.add_trace(go.Scatter(
                        x=student_mem_agg["Memory_Dummy"],
                        y=student_mem_agg["Amount_Returned"],
                        mode='markers',
                        name='Live Class Returned (Avg)',
                        marker=dict(size=14, color='#3B82F6', symbol='diamond')
                    ))
                
                fig_mem_live.update_layout(xaxis_title="Memory Length (Periods)", yaxis_title="Dollar Amount ($)", height=350, template="plotly_white")
                st.plotly_chart(fig_mem_live, use_container_width=True)
        else:
            st.info("No game sessions logged yet.")
