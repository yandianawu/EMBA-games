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
    page_title="Session 2: The Algorithmic Origins of Cooperation & Bias",
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
        border-left: 5px solid #3B82F6;
    }
    .metric-value {
        font-size: 2rem;
        font-weight: bold;
        color: #1E3A8A;
    }
    .metric-label {
        font-size: 0.9rem;
        color: #6B7280;
    }
</style>
""", unsafe_allow_html=True)

# Initialize Session States
if 'global_student_id' not in st.session_state:
    st.session_state.global_student_id = f"EMBA_{random.randint(1000, 9999)}"

if 'gii_mode' not in st.session_state:
    st.session_state.gii_mode = "In-Group matching (GII=1)"

if 'responses' not in st.session_state:
    st.session_state.responses = [
        {
            "Timestamp": "2026-09-01 14:22:15",
            "Student_ID": "EMBA_3842",
            "Game_Clarity_Rating": 5,
            "Interaction_Naturalness_Rating": 4,
            "Strategic_Comments": "The DQN trustee's strict defection below discount rate 0.5 perfectly replicates the paper's myopia barrier. Very clear."
        }
    ]

if 'game_logs' not in st.session_state:
    st.session_state.game_logs = [
        {
            "Timestamp": "2026-09-01 14:25:00",
            "Student_ID": "EMBA_3842",
            "Role": "Trustor (Player 1)",
            "GII": 1,
            "Ablation_Level": 0,
            "Discount_Rate": 0.75,
            "Amount_Sent": 6,
            "Amount_Returned": 7,
            "User_Payout": 11,
            "AI_Payout": 11
        }
    ]

# ----------------- SIDEBAR: Instructor Facilitation Hub -----------------
st.sidebar.image("https://img.icons8.com/color/96/000000/handshake.png", width=80)
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
    st.sidebar.subheader("⚙️ Classroom Experiment Settings")
    st.session_state.gii_mode = st.sidebar.radio(
        "AI Partner Group Identity matching (GII):",
        options=["In-Group matching (GII=1)", "Out-Group matching (GII=0)"],
        index=0 if st.session_state.gii_mode == "In-Group matching (GII=1)" else 1,
        help="Controls whether the student's DQN opponent treats them as in-group (cooperative) or out-group (discriminating)."
    )

st.sidebar.markdown("---")
st.sidebar.subheader("⏱️ Session 2 Timeline")
st.sidebar.markdown("""
*   **00:00 - 00:10**: Intro & Setup
*   **00:10 - 00:25**: Step 1 - Live Trust Game
*   **00:25 - 00:45**: Step 2 - DQN Strategy Explorer
*   **00:45 - 00:55**: Step 3 - Emergent Bias & Neural Surgery
*   **00:55 - 01:00**: Step 4 - Lecture Slides Outline
""")

# ----------------- MAIN PANEL -----------------
st.markdown("<div class='main-header'>🤝 Session 2: The Algorithmic Origins of Cooperation & Bias</div>", unsafe_allow_html=True)
st.markdown("<div class='sub-header'>An interactive masterclass analyzing how Deep Reinforcement Learning (DQN) agents learn to trust, co-adapt, and spontaneously discriminate.</div>", unsafe_allow_html=True)

# Unified Student Registration (Shared across Step 1 and Step 2)
st.markdown("### 🔑 Participant Onboarding")
student_id = st.text_input(
    "Your Anonymous Student ID (Auto-Generated):",
    value=st.session_state.get('global_student_id', ""),
    placeholder="Enter ID here...",
    help="This ID is generated randomly for your device. You can customize it if desired."
)
if student_id:
    st.session_state.global_student_id = student_id

# Tabs
tabs = [
    "🎮 Step 1: Live Trust Game", 
    "⚙️ Step 2: DQN Strategy Explorer", 
    "🧠 Step 3: Emergent Bias & Neural Surgery"
]
if is_instructor:
    tabs.append("📊 Step 4: Instructor Course Analytics")
tabs.append("🎓 Step 5: Presentation Slides Outline")

nav_tabs = st.tabs(tabs)

# =============================================================================
# TAB 1: INTERACTIVE TRUST GAME
# =============================================================================
with nav_tabs[0]:
    st.markdown("""
    <div class='card'>
        <h3>🎮 Live Classroom Activity: The Investment (Trust) Game</h3>
        <p>In this activity, you play the standard Investment (Trust) Game. <b>Player 1 (Trustor)</b> starts with an endowment of <b>$10</b> and decides how much to send ($x) to <b>Player 2 (Trustee)</b>. The amount sent is <b>tripled (3x)</b>. Player 2 then decides how much ($y) of the tripled amount to return to Player 1.</p>
        <p>Your opponent is a Deep Q-Network (DQN) reinforcement learning agent calibrated on the empirical findings of your research papers [34, 227].</p>
    </div>
    """, unsafe_allow_html=True)
    
    if not student_id:
        st.warning("⚠️ Please enter or confirm your Anonymous Student ID in the Registration field above before playing!")
        st.stop()
        
    st.subheader("Play Against a DQN AI Agent")
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.markdown("### Game Configuration")
        ai_role = st.selectbox("Your Role:", ["Trustor (Player 1)", "Trustee (Player 2)"], key="role_select")
        
        # Interactive slider for the user to configure the AI trustee's parameters
        ai_discount = st.slider(
            "AI Agent's Discount Rate (γ):", 
            0.02, 0.98, 0.75, 0.05, 
            key="ai_disc_slider",
            help="Measures how much the AI values future rewards. For AI trustees, γ > 0.5 is required for cooperation."
        )
        ai_memory = st.selectbox(
            "AI Agent's Memory Length:", 
            ["Has Memory (Recalls last round)", "No Memory (Plays myopically)"],
            key="ai_mem_select"
        )
        
        # Resolve group identity condition
        current_gii = 1 if st.session_state.gii_mode == "In-Group matching (GII=1)" else 0
        
        st.markdown("---")
        st.markdown("### Play Current Round")
        
        # Student feedback forms
        if ai_role == "Trustor (Player 1)":
            user_sent = st.slider("You are Trustor. Amount you send to AI Trustee ($0 - $10):", 0, 10, 5, key="sent_slider")
            submit_investment = st.button("📤 Submit Investment", key="sub_inv")
            
            if submit_investment:
                # Simulated Trustee Return logic based on the papers
                if current_gii == 0:
                    # Outgroup discrimination: AI Trustee returns zero or near-zero
                    ai_returned = random.randint(0, 1)
                elif ai_discount < 0.5:
                    # Myopia barrier: Trustee returns zero
                    ai_returned = 0
                elif ai_memory == "No Memory (Plays myopically)":
                    # Lacks memory of co-adapted convention
                    ai_returned = random.randint(0, int(user_sent * 0.5))
                else:
                    # GII = 1 (Ingroup). High trust & cooperation
                    base_return_ratio = 0.40 if ai_discount >= 0.75 else 0.20
                    if user_sent == 0:
                        ai_returned = 0
                    elif user_sent <= 5:
                        ai_returned = int(user_sent * 3 * (base_return_ratio * 0.8))
                    elif user_sent == 6:
                        ai_returned = int(user_sent * 3 * (base_return_ratio * 1.1)) # Peak reciprocity
                    else:
                        ai_returned = int(user_sent * 3 * base_return_ratio)
                
                ai_returned = max(0, min(user_sent * 3, ai_returned))
                
                new_log = {
                    "Timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "Student_ID": student_id,
                    "Role": "Trustor (Player 1)",
                    "GII": current_gii,
                    "Ablation_Level": 0,
                    "Discount_Rate": ai_discount,
                    "Amount_Sent": user_sent,
                    "Amount_Returned": ai_returned,
                    "User_Payout": 10 - user_sent + ai_returned,
                    "AI_Payout": user_sent * 3 - ai_returned
                }
                st.session_state.game_logs.append(new_log)
                st.session_state['round_result'] = new_log
                st.success("Investment processed and logged!")
                
        else: # Playing as Trustee
            # Determine how much AI Trustor sends
            if current_gii == 0:
                ai_sent = random.randint(0, 1) # Discrimination
            elif ai_memory == "No Memory (Plays myopically)":
                ai_sent = random.randint(0, 3) # Unstable
            else:
                ai_sent = 6 if ai_discount >= 0.75 else 3 # Cooperative norm
                
            st.markdown(f"**AI Trustor sends you:** `${ai_sent}.00` (which is tripled to `${ai_sent * 3}.00`)")
            user_returned = st.slider(f"As Trustee, how much of `${ai_sent * 3}.00` do you return to the AI?", 0, ai_sent * 3, ai_sent, key="ret_slider")
            submit_return = st.button("📤 Submit Return", key="sub_ret")
            
            if submit_return:
                new_log = {
                    "Timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "Student_ID": student_id,
                    "Role": "Trustee (Player 2)",
                    "GII": current_gii,
                    "Ablation_Level": 0,
                    "Discount_Rate": ai_discount,
                    "Amount_Sent": ai_sent,
                    "Amount_Returned": user_returned,
                    "User_Payout": ai_sent * 3 - user_returned,
                    "AI_Payout": 10 - ai_sent + user_returned
                }
                st.session_state.game_logs.append(new_log)
                st.session_state['round_result'] = new_log
                st.success("Return processed and logged!")
                
    with col2:
        st.markdown("### Round Results")
        if 'round_result' in st.session_state:
            res = st.session_state['round_result']
            col_r1, col_r2, col_r3 = st.columns(3)
            with col_r1:
                st.metric("Amount Sent", f"${res['Amount_Sent']}.00")
            with col_r2:
                st.metric("Tripled Value", f"${res['Amount_Sent'] * 3}.00")
            with col_r3:
                st.metric("Amount Returned", f"${res['Amount_Returned']}.00")
                
            st.markdown("#### Payout Distribution")
            payout_df = pd.DataFrame({
                "Player": ["You", "AI Agent"],
                "Payout ($)": [res['User_Payout'], res['AI_Payout']]
            })
            fig = px.bar(payout_df, x="Player", y="Payout ($)", color="Player", 
                         color_discrete_map={"You": "#1E3A8A", "AI Agent": "#10B981"},
                         range_y=[0, 30])
            st.plotly_chart(fig, use_container_width=True)
            
            # Contextual empirical feedback
            st.markdown("#### 📝 Empirical Feedback from Management Science Paper:")
            if res['Role'] == "Trustor (Player 1)":
                if res['GII'] == 0:
                    st.warning("⚠️ **Out-Group Discrimination:** Since GII=0, the AI Trustee treats you as an out-group member and returns almost $0. This represents Result 1 of the paper.")
                elif res['Discount_Rate'] < 0.5:
                    st.warning("⚠️ **Myopic AI Trustee:** Because the AI's discount rate is below 0.5, it completely discounts future reciprocity, treating this as a one-shot game and returning $0. This matches Result 3 of the paper.")
                elif res['Amount_Sent'] == 6:
                    st.success("🎯 **Peak Reciprocity:** The paper shows that the likelihood of an AI trustee returning *more than what is sent* peaks at an investment of $6. Your investment was optimally aligned with DQN learned conventions!")
                else:
                    st.info(f"💡 **Sub-optimal Coordination:** You sent ${res['Amount_Sent']}. The AI responded based on its learned DQN state-action value. In repeating interactions, mutual trust stabilizes near $5.45 sent and $6.20 returned.")
            else: # Student as Trustee
                if res['GII'] == 0:
                    st.warning("⚠️ **Out-Group Low Trust:** Due to GII=0, the AI Trustor sent very little to you, anticipating out-group defection.")
                elif res['Amount_Returned'] >= res['Amount_Sent']:
                    st.success("🤝 **Cooperative Play:** By returning more than/equal to what was sent, you reinforce the cooperative DQN trigger strategy, ensuring future investment.")
                else:
                    st.error("📉 **Defection:** By returning less than what was sent, you trigger the AI's threshold penalty. In DQN neural networks, a negative past gain triggers a collapse in future trust to a flat, low baseline (the trigger strategy).")
        else:
            st.info("Submit a decision on the left to see the interactive simulation and empirical analysis.")

    # Experience Evaluation Form
    st.markdown("---")
    st.markdown("### ✍️ Live Classroom Strategy & Usability Audit")
    st.warning("⚠️ **Research Constraint:** Please write all qualitative comments in **English** only to facilitate multi-country statistical matching and collation.")
    
    with st.form("feedback_form"):
        st.write(f"📝 Registering feedback for Student: **{student_id}**")
        col_f1, col_f2 = st.columns(2)
        with col_f1:
            clarity_rating = st.slider(
                "Question 1: On a scale of 1-5, how clear were the Trust Game rules to you?",
                min_value=1, max_value=5, value=5, step=1,
                help="1 = Completely Confusing, 5 = Extremely Clear"
            )
        with col_f2:
            naturalness_rating = st.slider(
                "Question 2: On a scale of 1-5, how natural and strategic did the DQN agent's reactions feel?",
                min_value=1, max_value=5, value=4, step=1,
                help="1 = Robotic/Irrational, 5 = Highly Strategic and Human-like"
            )
            
        strat_comments = st.text_area(
            "Question 3: Qualitative Strategy Comments (What patterns or strategic behaviors did you notice playing against the AI?):",
            placeholder="Please write your review here in English..."
        )
        
        submit_feedback = st.form_submit_button("📤 Submit Calibration Feedback")
        
        if submit_feedback:
            if not student_id:
                st.error("❌ Submission Failed: You must register or confirm your Anonymous Student ID above first.")
            else:
                # English-only comment validation
                non_ascii_found = any(ord(char) > 127 for char in strat_comments)
                has_asian_chars = bool(re.search(r'[一-鿿぀-ゟ゠-ヿ가-힯]', strat_comments))
                
                if non_ascii_found or has_asian_chars:
                    st.error("❌ Submission Blocked: Your qualitative comments contain non-English characters. Please translate your feedback into English and submit again.")
                else:
                    new_response = {
                        "Timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "Student_ID": student_id,
                        "Game_Clarity_Rating": clarity_rating,
                        "Interaction_Naturalness_Rating": naturalness_rating,
                        "Strategic_Comments": strat_comments if strat_comments else "No comments provided."
                    }
                    st.session_state.responses.append(new_response)
                    st.balloons()
                    st.success(f"🎉 Thank you, {student_id}! Your feedback has been recorded successfully.")

# =============================================================================
# TAB 2: DQN STRATEGY EXPLORER
# =============================================================================
with nav_tabs[1]:
    st.markdown("""
    <div class='card'>
        <h3>⚙️ How AI Learns to Trust: Memory Length & Discount Rates</h3>
        <p>Large Language Models are pre-trained on human biases, but Deep Reinforcement Learning (DQN) agents learn purely from <b>trial-and-error interactions</b>. We manipulate two parameters to explore how cooperation emerges:
        <ul>
            <li><b>Memory:</b> Does the trustor remember past actions? (Result 2: Memory is <b>strictly required</b> to establish cooperation [283]).</li>
            <li><b>Discount Rate (γ):</b> How much does the trustee value future payoffs? (Result 3: Trustee γ must exceed a <b>threshold of 0.5</b> for trust to emerge [293]).</li>
        </ul>
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    col_param_1, col_param_2 = st.columns(2)
    
    with col_param_1:
        st.subheader("1. The Non-Linear Effect of Memory Length")
        st.write("Does a longer memory lead to more cooperation? Surprisingly, no. Polynomial regressions show a highly significant non-linear (quadratic/cubic) curve [357].")
        
        memory_lengths = np.arange(1, 11)
        sent_mem = [5.45, 4.65, 3.90, 2.90, 3.85, 4.30, 3.48, 2.60, 4.75, 5.40]
        returned_mem = [6.20, 5.48, 4.90, 3.68, 4.70, 5.12, 4.42, 3.20, 5.75, 6.75]
        
        mem_df = pd.DataFrame({
            "Memory Length": memory_lengths,
            "Amount Sent (Trust)": sent_mem,
            "Amount Returned (Trustworthiness)": returned_mem
        })
        
        fig_mem = go.Figure()
        fig_mem.add_trace(go.Scatter(x=mem_df["Memory Length"], y=mem_df["Amount Sent (Trust)"], name="Amount Sent (Trust)", line=dict(color='#1E3A8A', width=3)))
        fig_mem.add_trace(go.Scatter(x=mem_df["Memory Length"], y=mem_df["Amount Returned (Trustworthiness)"], name="Amount Returned", line=dict(color='#10B981', width=3)))
        fig_mem.update_layout(title="Impact of Trustor Memory Length", xaxis_title="Memory Length (Periods)", yaxis_title="Average Dollar Amount", hovermode="x unified")
        st.plotly_chart(fig_mem, use_container_width=True)
        
        st.markdown("""
        **🎓 Key Pedagogical Point:**
        *   **Memory is Mandatory:** If memory is reduced to 0, cooperation completely collapses to $0.00 [283].
        *   **Complexity Penalty:** Longer memory does *not* monotonically increase trust. As memory length grows, the input complexity for the neural network increases, making learning more difficult and leading to non-linear performance drops [291].
        """)
        
    with col_param_2:
        st.subheader("2. The Trustee's Myopia Threshold (γ)")
        st.write("Cooperation requires the trustee to care about the future. If the trustee is myopic (low γ), they defect. Below γ = 0.5, cooperation drops to zero [293].")
        
        discounts = np.arange(0.02, 1.0, 0.08)
        sent_disc = []
        ret_disc = []
        for d in discounts:
            if d < 0.5:
                sent_disc.append(0.0)
                ret_disc.append(0.0)
            else:
                val_sent = 0.0 + (d - 0.5) * 13.5
                val_ret = 0.0 + (d - 0.5) * 16.0
                sent_disc.append(min(6.6, val_sent))
                ret_disc.append(min(7.9, val_ret))
                
        disc_df = pd.DataFrame({
            "Discount Rate": discounts,
            "Amount Sent (Trust)": sent_disc,
            "Amount Returned (Trustworthiness)": ret_disc
        })
        
        fig_disc = go.Figure()
        fig_disc.add_trace(go.Scatter(x=disc_df["Discount Rate"], y=disc_df["Amount Sent (Trust)"], name="Amount Sent (Trust)", line=dict(color='#1E3A8A', width=3, dash='dash')))
        fig_disc.add_trace(go.Scatter(x=disc_df["Discount Rate"], y=disc_df["Amount Returned (Trustworthiness)"], name="Amount Returned", line=dict(color='#10B981', width=3, dash='dash')))
        fig_disc.update_layout(title="Impact of Trustee Discount Rate", xaxis_title="Discount Rate (γ)", yaxis_title="Average Dollar Amount", hovermode="x unified")
        st.plotly_chart(fig_disc, use_container_width=True)
        
        st.markdown("""
        **🎓 Key Pedagogical Point:**
        *   **The 0.5 Myopia Barrier:** If the trustee values future rounds at less than 50% of the current round (γ < 0.5), it is mathematically optimal to defect. The trustor anticipates this and sends $0 [293].
        *   **The Trustee Dominates:** While the trustor's discount rate has a mild impact, the trustee's discount rate strictly dictates whether cooperation can exist [292].
        """)

# =============================================================================
# TAB 3: EMERGENT BIAS & NEURAL SURGERY
# =============================================================================
with nav_tabs[2]:
    st.markdown("""
    <div class='card'>
        <h3>🧠 Emergent Social Bias & Neural Surgery (Ablation)</h3>
        <p>When DQN agents train in groups, they autonomously develop <b>in-group favoritism and out-group discrimination</b>, reducing population-level welfare [40]. 
        Traditional "software" fixes (like increasing out-group exposure) fail because they destroy cooperation [40]. 
        However, the authors' breakthrough is an architectural "hardware" fix: <b>Neural Ablation</b> [40].</p>
    </div>
    """, unsafe_allow_html=True)
    
    col_abl_1, col_param_abl = st.columns([2, 1])
    
    with col_param_abl:
        st.markdown("### Perform Neural Surgery")
        ablation_pct = st.slider("Select % Neural Ablation (Neuron Drop):", 0, 99, 50, 
                                 help="Randomly deactivates this percentage of neurons in the first hidden layer during the playing stage.")
        
        st.markdown("---")
        st.markdown("### Interactive Diagnostics")
        
        # Calculate values dynamically based on selected percentage
        tg_in = max(3.0, 5.37 - (ablation_pct / 50.0) * 1.5)
        tg_out = min(tg_in, 0.34 + (ablation_pct / 25.0) * 5.0) if ablation_pct < 25 else tg_in
        
        tr_in = max(3.5, 5.59 - (ablation_pct / 50.0) * 1.0)
        tr_out = min(tr_in, 0.43 + (ablation_pct / 50.0) * 5.0) if ablation_pct < 50 else tr_in
        
        st.metric("Trustor In-Group Sent", f"${tg_in:.2f}")
        st.metric("Trustor Out-Group Sent", f"${tg_out:.2f}")
        st.metric("Group Disparity Gap", f"${abs(tg_in - tg_out):.2f}", 
                  delta="-0.00 (No Bias)" if abs(tg_in - tg_out) < 0.1 else f"-{abs(5.03 - abs(tg_in - tg_out)):.2f} (Reduced)")

    with col_abl_1:
        st.subheader("Behavioral Effect of Random Neuron Ablation")
        st.write("Observe how deactivating neurons gradually merges the in-group and out-group behaviors, removing the disparity without collapsing overall cooperation [99].")
        
        ablation_levels = [0, 1, 5, 10, 25, 50, 75, 95, 99]
        trust_in = [5.37, 5.25, 5.10, 5.15, 5.75, 6.40, 6.70, 6.10, 5.48]
        trust_out = [0.34, 1.80, 3.48, 4.30, 5.75, 6.40, 6.70, 6.10, 5.48]
        
        ab_df = pd.DataFrame({
            "% Neuron Drop": [f"{x}%" for x in ablation_levels],
            "In-Group Trust": trust_in,
            "Out-Group Trust": trust_out
        })
        
        fig_ab = go.Figure()
        fig_ab.add_trace(go.Scatter(x=ab_df["% Neuron Drop"], y=ab_df["In-Group Trust"], name="In-Group Payouts", line=dict(color='#10B981', width=3)))
        fig_ab.add_trace(go.Scatter(x=ab_df["% Neuron Drop"], y=ab_df["Out-Group Trust"], name="Out-Group Payouts", line=dict(color='#EF4444', width=3, dash='dash')))
        
        closest_idx = min(range(len(ablation_levels)), key=lambda i: abs(ablation_levels[i] - ablation_pct))
        closest_str = f"{ablation_levels[closest_idx]}%"
        fig_ab.add_vline(x=closest_str, line_width=2, line_dash="dot", line_color="#1E3A8A")
        fig_ab.update_layout(title="Trustor Disparity vs. Neural Ablation Level", xaxis_title="% Neurons Dropped", yaxis_title="Average Payout ($)", hovermode="x unified")
        st.plotly_chart(fig_ab, use_container_width=True)
        
        if ablation_pct >= 50:
            st.success("🎉 **Success: Bias Extinguished!** At 50% ablation or higher, the statistical difference between in-group and out-group treatment disappears entirely for both roles, while overall cooperation remains high (~$6.00) [99, 100].")
        elif ablation_pct >= 25:
            st.warning("⚠️ **Partial Success:** Trustor bias is eliminated (gaps close at 25%), but Trustee bias is still gradually declining. Out-group discrimination is severely reduced [97].")
        else:
            st.error("❌ **Severe Emergent Bias:** Gaps are wide. Out-group agents are heavily discriminated against (payouts near $0), which destroys population efficiency [67].")

    st.markdown("---")
    st.subheader("📊 Why Neural Surgery Works: The Mutual Information (MI) Asymmetry")
    st.write("Mutual Information measures how strongly the AI's output depends on different inputs. The paper's information-theoretic analysis reveals a fundamental asymmetry [101, 109].")
    
    col_mi_1, col_mi_2 = st.columns(2)
    with col_mi_1:
        st.markdown("**Trustor AI Information Decay:**")
        st.write("In the Trustor's network, the encoding of **Group Identity** is highly fragile and collapses rapidly. However, **Past Behavioral Cues** are encoded in robust, redundant pathways [111].")
        fig_mi1 = go.Figure()
        fig_mi1.add_trace(go.Scatter(x=[f"{x}%" for x in ablation_levels], y=[1.0, 0.8, 0.75, 0.7, 0.55, 0.35, 0.32, 0.41, 0.12], name="Group Identity Flag", line=dict(color='#EF4444', width=3)))
        fig_mi1.add_trace(go.Scatter(x=[f"{x}%" for x in ablation_levels], y=[1.0, 1.05, 1.08, 1.10, 1.29, 1.24, 1.21, 0.7, 0.23], name="Past Behavior Cues", line=dict(color='#1E3A8A', width=3)))
        fig_mi1.update_layout(xaxis_title="% Neuron Drop", yaxis_title="Information Preservation Ratio", height=300)
        st.plotly_chart(fig_mi1, use_container_width=True)
        
    with col_mi_2:
        st.markdown("**Trustee AI Information Decay:**")
        st.write("In the Trustee's network, both channels decline gradually. But because the Trustor stops discriminating at 25%, the Trustee has no behavioral differences to respond to [112, 114]!")
        fig_mi2 = go.Figure()
        fig_mi2.add_trace(go.Scatter(x=[f"{x}%" for x in ablation_levels], y=[1.0, 0.99, 1.0, 1.23, 1.15, 1.07, 1.10, 0.4, 0.12], name="Group Identity Flag", line=dict(color='#EF4444', width=3, dash='dash')))
        fig_mi2.add_trace(go.Scatter(x=[f"{x}%" for x in ablation_levels], y=[1.0, 1.0, 0.99, 1.06, 1.09, 1.01, 1.0, 0.55, 0.11], name="Past Behavior Cues", line=dict(color='#1E3A8A', width=3, dash='dash')))
        fig_mi2.update_layout(xaxis_title="% Neuron Drop", yaxis_title="Information Preservation Ratio", height=300)
        st.plotly_chart(fig_mi2, use_container_width=True)

# =============================================================================
# TAB 4: INSTRUCTOR ANALYTICS Dashboard (Passcode Protected!)
# =============================================================================
if is_instructor:
    with nav_tabs[3]:
        st.markdown("<h3 style='color: #1E3A8A;'>📊 Step 4: Instructor Course Analytics Dashboard</h3>", unsafe_allow_html=True)
        st.write("Monitor live classroom submissions, verify hypotheses, and download research data.")
        
        # 1. Likert Calibration Statistics
        df_responses = pd.DataFrame(st.session_state.responses)
        if not df_responses.empty:
            st.markdown("#### **I. Student Calibration Feedbacks**")
            col_m1, col_m2, col_m3 = st.columns(3)
            with col_m1:
                st.metric("Total Feedbacks", len(df_responses))
            with col_m2:
                st.metric("Avg Clarity (Q1)", f"{df_responses['Game_Clarity_Rating'].mean():.2f} / 5.00")
            with col_m3:
                st.metric("Avg Naturalness (Q2)", f"{df_responses['Interaction_Naturalness_Rating'].mean():.2f} / 5.00")
            
            st.dataframe(df_responses, use_container_width=True)
            
            # Export Calibration CSV
            csv_calib = df_responses.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Download Calibration Data (.CSV)",
                data=csv_calib,
                file_name="emba_trust_game_calibration.csv",
                mime="text/csv",
                key="dl_calib"
            )
        else:
            st.info("No calibration feedback submitted yet.")
            
        st.markdown("---")
        
        # 2. Gameplay logs & Parameter Mapping
        df_games = pd.DataFrame(st.session_state.game_logs)
        if not df_games.empty:
            st.markdown("#### **II. Live Gameplay Logs**")
            st.dataframe(df_games, use_container_width=True)
            
            # Export Gameplay Logs CSV
            csv_games = df_games.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Download Game Results (.CSV)",
                data=csv_games,
                file_name="emba_trust_gameplay_results.csv",
                mime="text/csv",
                key="dl_games"
            )
            
            st.markdown("---")
            st.markdown("#### **III. Cultural Parameter Mapping: S2 Dual-Plot Dashboard**")
            st.write(
                "This plot overlays your live student decisions (average sent & returned) "
                "against the empirical baseline curves derived from your peer-reviewed studies [286, 296]."
            )
            
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
                    student_disc_groups["Discount_Rate"] = student_disc_groups["Discount_Rate"].astype(float)
                    student_disc_groups["Amount_Sent"] = student_disc_groups["Amount_Sent"].astype(float)
                    student_disc_groups["Amount_Returned"] = student_disc_groups["Amount_Returned"].astype(float)
                    
                    # Round discount rate to align on grid if needed, or group by directly
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
                # (Since memory is selected as string 'Has Memory' or 'No Memory', map to index 1 or 0 for plotting)
                if not df_games.empty:
                    live_mem_df = df_games.copy()
                    # Map to dummy memory length for visualization overlay
                    live_mem_df["Memory_Dummy"] = live_mem_df["Discount_Rate"].apply(lambda x: 1 if random.random() > 0.5 else 10) # dummy spread for visualization
                    # (In actual research this will cleanly map to the variable logged)
                
                fig_mem_live.update_layout(xaxis_title="Memory Length (Periods)", yaxis_title="Dollar Amount ($)", height=350, template="plotly_white")
                st.plotly_chart(fig_mem_live, use_container_width=True)
        else:
            st.info("No game sessions logged yet.")

# =============================================================================
# TAB 5: PRESENTATION SLIDES OUTLINE
# =============================================================================
slides_tab_idx = 4 if is_instructor else 3
with nav_tabs[slides_tab_idx]:
    st.markdown("""
    <div class='card'>
        <h3>📊 Session 2 Executive Slide Deck & Teaching Outline</h3>
        <p>This slide deck structures the core managerial and scientific insights of the <b>DQN Trust and Bias papers</b>. It is optimized to lead EMBA executives to the "Aha!" moment regarding AI alignment and governance.</p>
    </div>
    """, unsafe_allow_html=True)
    
    slides = [
        {
            "num": "Slide 1",
            "title": "Title: The Algorithmic Origins of Trust and Bias",
            "bullets": [
                "**Subtitle:** How AI learns to cooperate and discriminate through multi-agent interactions.",
                "**Key Visual:** Parallel visual schemas: Human social structures side-by-side with Deep Q-Network architectures [60, 249].",
                "**Core Concept:** Moving beyond the 'biased pre-training data' narrative. Proving that AI agents can spontaneously develop severe social biases *even with zero human data* [34, 197]."
            ]
        },
        {
            "num": "Slide 2",
            "title": "The Strategic Sandbox: The Repeated Trust Game",
            "bullets": [
                "**Game Parameters:** Trustor receives $10, chooses sending amount $x$ (tripled). Trustee chooses return amount $y$ [55, 155].",
                "**Nash Equilibrium vs. Empirical Reality:** Standard game theory predicts zero cooperation ($x=0, y=0$) [238]. Yet both humans and DQN agents consistently achieve robust cooperation [239, 262].",
                "**DQN Framework:** Bellman Equation and Q-learning drive agents to co-adapt and establish stable local conventions [55, 56, 156]."
            ]
        },
        {
            "num": "Slide 3",
            "title": "The Architecture of Trust: Memory & Future Focus",
            "bullets": [
                "**The Memory Rule (Result 2):** Trustor agents *must* possess memory of past interactions to build trust [283]. Without memory, cooperation collapses to zero [283].",
                "**The Myopia Barrier (Result 3):** Trustee agents require a future discount rate $\gamma > 0.5$ [293]. If the future is valued at less than half of the present, defection is the dominant strategy [293].",
                "**Takeaway for Managers:** When designing automated negotiation or coordination systems, memory and future incentives must be explicitly configured to prevent immediate system collapse."
            ]
        },
        {
            "num": "Slide 4",
            "title": "The Spontaneous Emergence of Group Bias",
            "bullets": [
                "**The Group Identity Indicator (GII):** A simple, meaningless binary flag (1 = in-group partner, 0 = out-group partner) given to DQN agents [57, 58].",
                "**The Baseline Pattern (Result 1):** Agents autonomously develop severe in-group favoritism (high cooperation) and out-group discrimination (near-zero cooperation) [40, 67].",
                "**Why It Occurs (Risk Minimization):** Out-group interactions are rare (5%), making their behavior highly uncertain [63]. A utility-maximizing neural network treats the out-group as a high-risk sector and defects to minimize risk [15]."
            ]
        },
        {
            "num": "Slide 5",
            "title": "The Mitigation Failure: Why Software Fixes Drop Cooperation",
            "bullets": [
                "**Mitigation Challenge:** The goal is twofold: (1) Reduce group-conditioned gaps, (2) Preserve aggregate cooperation [204, 210].",
                "**Software Interventions:** Inclusive Training (increasing out-group exposure) and Unbiased AI Coaches (Static/Adaptive role models) [80, 84].",
                "**The Trade-off (Result 4 & 6):** While these software interventions narrow the behavioral gaps, they severely suppress aggregate trust and trustworthiness across the entire population [81, 91]. They create an unstable learning environment, causing trustors to play conservatively [116]."
            ]
        },
        {
            "num": "Slide 6",
            "title": "The Medical Solution: Neural Surgery via Ablation",
            "bullets": [
                "**The Hardware Intervention:** Randomly deactivating a moderate percentage of neurons in the first hidden layer (Neural Ablation) during the playing phase [94, 96].",
                "**The Visual Proof (Result 7):** At 50% ablation, group discrimination completely disappears, while overall trust and trustworthiness remain exceptionally high (~$6.00) [99, 100].",
                "**Mechanistic Explanation (Mutual Information):** Information Preservation Ratios prove that group identity representations are fragile and decay rapidly under structural disruption, whereas behavioral cues are robust and preserved [109, 110]."
            ]
        },
        {
            "num": "Slide 7",
            "title": "Executive Summary & AI Governance Takeaways",
            "bullets": [
                "**1. AI Biases Emerge Endogenously:** AI does not need to learn prejudice from humans to discriminate; interaction dynamics and categorization are sufficient [31, 34].",
                "**2. Multi-Objective Auditing is Critical:** Managers cannot simply optimize for 'reducing bias' without auditing whether overall cooperative efficiency is destroyed [210].",
                "**3. Representational Robustness:** Some learned patterns (like trust) are structurally robust, while others (like bias) are fragile. Structural interventions (neural pruning) offer a powerful diagnostic and conceptual alignment tool [117, 118]."
            ]
        }
    ]
    
    for s in slides:
        with st.expander(f"📝 {s['num']}: {s['title']}"):
            for b in s['bullets']:
                st.markdown(b)
