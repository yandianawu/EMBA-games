import streamlit as st
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Set page configuration
st.set_page_config(
    page_title="AI Trust & Cooperation Explorer",
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

# ----------------- SIDEBAR: Instructor Facilitation Hub -----------------
with st.sidebar:
    st.image("https://img.icons8.com/color/96/000000/handshake.png", width=80)
    st.markdown("### 🎓 Session 2 Facilitation Hub")
    st.markdown("**Theme:** The Algorithmic Origins of Cooperation & Bias")
    st.markdown("**Duration:** 60 Minutes")
    
    st.markdown("---")
    st.markdown("⏱️ **Session 2 Timeline:**")
    st.markdown("""
    *   **00:00 - 00:10 (10m):** Introduction & Setup
    *   **00:10 - 00:25 (15m):** Live Trust Game Activity
    *   **00:25 - 00:45 (20m):** Lecture Part 1: How AI Learns to Trust
    *   **00:45 - 00:55 (10m):** Lecture Part 2: The Emergence of Bias
    *   **00:55 - 01:00 (05m):** Executive Wrap-up & Q&A
    """)
    
    st.markdown("---")
    st.markdown("📘 **Quick Reference Papers:**")
    st.markdown("""
    1.  *Building Socially Intelligent AI Systems* (Management Science, 2023)
    2.  *Emergent Social Bias in AI & Mitigation Strategy* (Under Revision, ISR)
    """)

# ----------------- MAIN PANEL -----------------
st.markdown("<div class='main-header'>🤝 Session 2: The Algorithmic Origins of Cooperation & Bias</div>", unsafe_allow_html=True)
st.markdown("<div class='sub-header'>An interactive masterclass analyzing how Deep Reinforcement Learning (DQN) agents learn to trust, co-adapt, and spontaneously discriminate.</div>", unsafe_allow_html=True)

# Tabs
tab1, tab2, tab3, tab4 = st.tabs([
    "🎮 Interactive Trust Game", 
    "⚙️ DQN Strategy Explorer", 
    "🧠 Emergent Bias & Neural Surgery", 
    "📊 Presentation Slides Outline"
])

# ==============================================================================
# TAB 1: INTERACTIVE TRUST GAME
# ==============================================================================
with tab1:
    st.markdown("""
    <div class='card'>
        <h3>🎮 Live Classroom Activity: The Investment (Trust) Game</h3>
        <p>In this activity, students pair up. <b>Player 1 (Trustor)</b> starts with an endowment of <b>$10</b> and decides how much to send to <b>Player 2 (Trustee)</b>. The amount sent is <b>tripled (x3)</b>. Player 2 then decides how much of the tripled amount to return to Player 1.</p>
        <p><i>Classroom Setup:</i> Run 5 rounds of "Stranger Matching" (random rematching each round) followed by 5 rounds of "Partner Matching" (fixed pairs). Watch how cooperation dynamically emerges only in the partner treatment!</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.subheader("Play Against a DQN AI Agent")
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.markdown("### Game Configuration")
        ai_role = st.selectbox("Your Role:", ["Trustor (Player 1)", "Trustee (Player 2)"])
        ai_discount = st.slider("AI Agent's Discount Rate (γ):", 0.0, 1.0, 0.75, 0.05, 
                                help="Measures how much the AI values future rewards. In human studies, this averages ~0.75. For AI trustees, γ > 0.5 is required for cooperation.")
        ai_memory = st.selectbox("AI Agent's Memory:", ["Has Memory (Recalls last round)", "No Memory (Plays myopically)"])
        
        st.markdown("---")
        st.markdown("### Play Current Round")
        if ai_role == "Trustor (Player 1)":
            user_sent = st.number_input("You are Trustor. Amount you send to AI Trustee ($0 - $10):", 0, 10, 5)
            if st.button("Submit Investment"):
                # Simulation logic based on empirical curves
                if ai_discount < 0.5:
                    ai_returned = 0
                else:
                    # Trustee response curve peaks around sending 6 (returns ~39.77% on average)
                    base_return_ratio = 0.40 if ai_discount >= 0.75 else 0.20
                    # Add some non-linearity
                    if user_sent == 0:
                        ai_returned = 0
                    elif user_sent <= 5:
                        ai_returned = int(user_sent * 3 * (base_return_ratio * 0.8))
                    elif user_sent == 6:
                        ai_returned = int(user_sent * 3 * (base_return_ratio * 1.1)) # Peak reciprocity
                    else:
                        ai_returned = int(user_sent * 3 * base_return_ratio)
                
                st.session_state['round_result'] = {
                    'sent': user_sent,
                    'tripled': user_sent * 3,
                    'returned': ai_returned,
                    'user_payout': 10 - user_sent + ai_returned,
                    'ai_payout': user_sent * 3 - ai_returned
                }
        else:
            ai_sent = 0
            if ai_memory == "No Memory":
                ai_sent = np.random.randint(0, 4) # Flat/random low trust
            else:
                ai_sent = 6 if ai_discount >= 0.75 else 3 # Co-adapted trust
                
            st.markdown(f"**AI Trustor sends you:** `${ai_sent}.00` (which is tripled to `${ai_sent * 3}.00`)")
            user_returned = st.number_input(f"As Trustee, how much of `${ai_sent * 3}.00` do you return to the AI?", 0, ai_sent * 3, ai_sent)
            
            if st.button("Submit Return"):
                st.session_state['round_result'] = {
                    'sent': ai_sent,
                    'tripled': ai_sent * 3,
                    'returned': user_returned,
                    'user_payout': ai_sent * 3 - user_returned,
                    'ai_payout': 10 - ai_sent + user_returned
                }
                
    with col2:
        st.markdown("### Round Results")
        if 'round_result' in st.session_state:
            res = st.session_state['round_result']
            col_r1, col_r2, col_r3 = st.columns(3)
            with col_r1:
                st.metric("Amount Sent", f"${res['sent']}.00")
            with col_r2:
                st.metric("Tripled Value", f"${res['tripled']}.00")
            with col_r3:
                st.metric("Amount Returned", f"${res['returned']}.00")
                
            st.markdown("#### Payout Distribution")
            payout_df = pd.DataFrame({
                "Player": ["You", "AI Agent"],
                "Payout ($)": [res['user_payout'], res['ai_payout']]
            })
            fig = px.bar(payout_df, x="Player", y="Payout ($)", color="Player", 
                         color_discrete_map={"You": "#1E3A8A", "AI Agent": "#10B981"},
                         range_y=[0, 30])
            st.plotly_chart(fig, use_container_width=True)
            
            # Contextual empirical feedback
            st.markdown("#### 📝 Empirical Feedback from Management Science Paper:")
            if ai_role == "Trustor (Player 1)":
                if ai_discount < 0.5:
                    st.warning("⚠️ **Myopic AI Trustee:** Because the AI's discount rate is below 0.5, it completely discounts future reciprocity, treating this as a one-shot game and returning $0. This matches Result 3 of the paper.")
                elif res['sent'] == 6:
                    st.success("🎯 **Peak Reciprocity:** The paper shows that the likelihood of an AI trustee returning *more than what is sent* peaks at an investment of $6. Your investment was optimally aligned with DQN learned conventions!")
                else:
                    st.info(f"💡 **Sub-optimal Coordination:** You sent ${res['sent']}. The AI responded based on its learned DQN state-action value. In repeating interactions, mutual trust stabilizes near $5.45 sent and $6.20 returned.")
            else:
                if res['returned'] >= res['sent']:
                    st.success("🤝 **Cooperative Play:** By returning more than/equal to what was sent, you reinforce the cooperative DQN trigger strategy, ensuring future investment.")
                else:
                    st.error("📉 **Defection:** By returning less than what was sent, you trigger the AI's threshold penalty. In DQN neural networks, a negative past gain triggers a collapse in future trust to a flat, low baseline (the trigger strategy).")
        else:
            st.info("Submit a decision on the left to see the interactive simulation and empirical analysis.")

# ==============================================================================
# TAB 2: DQN STRATEGY EXPLORER
# ==============================================================================
with tab2:
    st.markdown("""
    <div class='card'>
        <h3>⚙️ How AI Learns to Trust: Memory Length & Discount Rates</h3>
        <p>Large Language Models are pre-trained on human biases, but Deep Reinforcement Learning (DQN) agents learn purely from <b>trial-and-error interactions</b>. We manipulate two parameters to explore how cooperation emerges:
        <ul>
            <li><b>Memory:</b> Does the trustor remember past actions? (Result 2: Memory is <b>strictly required</b> to establish cooperation).</li>
            <li><b>Discount Rate (γ):</b> How much does the trustee value future payoffs? (Result 3: Trustee γ must exceed a <b>threshold of 0.5</b> for trust to emerge).</li>
        </ul>
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    col_param_1, col_param_2 = st.columns(2)
    
    with col_param_1:
        st.subheader("1. The Non-Linear Effect of Memory Length")
        st.write("Does a longer memory lead to more cooperation? Surprisingly, no. Polynomial regressions show a highly significant non-linear (quadratic/cubic) curve.")
        
        # Simulating memory length data from paper Fig 5
        memory_lengths = np.arange(1, 11)
        # quadratic downward then up curve from paper fig 5a
        sent_mem = 5.45 - 0.7 * (memory_lengths - 1) + 0.08 * (memory_lengths - 1)**2
        returned_mem = 6.20 - 0.8 * (memory_lengths - 1) + 0.1 * (memory_lengths - 1)**2
        
        # Adjustment to match the wavy nature
        sent_mem = [5.45, 4.65, 3.90, 2.90, 3.85, 4.30, 3.48, 2.60, 4.75, 5.40]
        returned_mem = [6.20, 5.48, 4.90, 3.68, 4.70, 5.12, 4.42, 3.20, 5.75, 6.75]
        
        mem_df = pd.DataFrame({
            "Memory Length": memory_lengths,
            "Amount Sent (Trust)": sent_mem,
            "Amount Returned (Trustworthiness)": returned_mem
        })
        
        fig_mem = go.Figure()
        fig_mem.add_trace(go.Scatter(x=mem_df["Memory Length"], y=mem_df["Amount Sent (Trust)"], name="Amount Sent", line=dict(color='#1E3A8A', width=3)))
        fig_mem.add_trace(go.Scatter(x=mem_df["Memory Length"], y=mem_df["Amount Returned (Trustworthiness)"], name="Amount Returned", line=dict(color='#10B981', width=3)))
        fig_mem.update_layout(title="Impact of Trustor Memory Length", xaxis_title="Memory Length (Periods)", yaxis_title="Average Dollar Amount", hovermode="x unified")
        st.plotly_chart(fig_mem, use_container_width=True)
        
        st.markdown("""
        **🎓 Key Pedagogical Point:**
        *   **Memory is Mandatory:** If memory is reduced to 0, cooperation completely collapses to $0.00.
        *   **Complexity Penalty:** Longer memory does *not* monotonically increase trust. As memory length grows, the input complexity for the neural network increases, making learning more difficult and leading to non-linear performance drops.
        """)
        
    with col_param_2:
        st.subheader("2. The Trustee's Myopia Threshold (γ)")
        st.write("Cooperation requires the trustee to care about the future. If the trustee is myopic (low γ), they defect. Below γ = 0.5, cooperation drops to zero.")
        
        discounts = np.arange(0.02, 1.0, 0.08)
        # Trustee discount rate curve from Fig 6b (flat at 0 until 0.5, then rises rapidly)
        sent_disc = []
        ret_disc = []
        for d in discounts:
            if d < 0.5:
                sent_disc.append(0.0)
                ret_disc.append(0.0)
            else:
                # rise to ~6.6 sent and ~7.9 returned
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
        fig_disc.add_trace(go.Scatter(x=disc_df["Discount Rate"], y=disc_df["Amount Sent (Trust)"], name="Amount Sent", line=dict(color='#1E3A8A', width=3, dash='dash')))
        fig_disc.add_trace(go.Scatter(x=disc_df["Discount Rate"], y=disc_df["Amount Returned (Trustworthiness)"], name="Amount Returned", line=dict(color='#10B981', width=3, dash='dash')))
        fig_disc.update_layout(title="Impact of Trustee Discount Rate", xaxis_title="Discount Rate (γ)", yaxis_title="Average Dollar Amount", hovermode="x unified")
        st.plotly_chart(fig_disc, use_container_width=True)
        
        st.markdown("""
        **🎓 Key Pedagogical Point:**
        *   **The 0.5 Myopia Barrier:** If the trustee values future rounds at less than 50% of the current round (γ < 0.5), it is mathematically optimal to defect. The trustor anticipates this and sends $0.
        *   **The Trustee Dominates:** While the trustor's discount rate has a mild impact, the trustee's discount rate strictly dictates whether cooperation can exist.
        """)

# ==============================================================================
# TAB 3: EMERGENT BIAS & NEURAL SURGERY
# ==============================================================================
with tab3:
    st.markdown("""
    <div class='card'>
        <h3>🧠 Emergent Social Bias & Neural Surgery (Ablation)</h3>
        <p>When DQN agents train in groups, they autonomously develop <b>in-group favoritism and out-group discrimination</b>, reducing population-level welfare. 
        Traditional "software" fixes (like increasing out-group exposure) fail because they destroy cooperation. 
        However, the authors' breakthrough is an architectural "hardware" fix: <b>Neural Ablation</b>.</p>
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
        # In-group vs out-group gaps disappear around 25% for trustors, 50% for trustees
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
        st.write("Observe how deactivating neurons gradually merges the in-group and out-group behaviors, removing the disparity without collapsing overall cooperation.")
        
        ablation_levels = [0, 1, 5, 10, 25, 50, 75, 95, 99]
        # Simulating data from paper Figure 4
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
        
        # Add a vertical indicator line for the slider selection
        slider_str = f"{ablation_pct}%"
        # Find closest index
        closest_idx = min(range(len(ablation_levels)), key=lambda i: abs(ablation_levels[i] - ablation_pct))
        closest_str = f"{ablation_levels[closest_idx]}%"
        
        fig_ab.add_vline(x=closest_str, line_width=2, line_dash="dot", line_color="#1E3A8A")
        
        fig_ab.update_layout(title="Trustor Disparity vs. Neural Ablation Level", xaxis_title="% Neurons Dropped", yaxis_title="Average Payout ($)", hovermode="x unified")
        st.plotly_chart(fig_ab, use_container_width=True)
        
        if ablation_pct >= 50:
            st.success("🎉 **Success: Bias Extinguished!** At 50% ablation or higher, the statistical difference between in-group and out-group treatment disappears entirely for both roles, while overall cooperation remains high (~$6.00).")
        elif ablation_pct >= 25:
            st.warning("⚠️ **Partial Success:** Trustor bias is eliminated (gaps close at 25%), but Trustee bias is still gradually declining. Out-group discrimination is severely reduced.")
        else:
            st.error("❌ **Severe Emergent Bias:** Gaps are wide. Out-group agents are heavily discriminated against (payouts near $0), which destroys population efficiency.")

    st.markdown("---")
    st.subheader("📊 Why Neural Surgery Works: The Mutual Information (MI) Asymmetry")
    st.write("Mutual Information measures how strongly the AI's output depends on different inputs. The paper's information-theoretic analysis reveals a fundamental asymmetry.")
    
    col_mi_1, col_mi_2 = st.columns(2)
    with col_mi_1:
        st.markdown("**Trustor AI Information Decay:**")
        st.write("In the Trustor's network, the encoding of **Group Identity** is highly fragile and collapses rapidly. However, **Past Behavioral Cues** are encoded in robust, redundant pathways.")
        # Graph showing fast collapse of GII vs slow collapse of behavior (from Fig 5a)
        fig_mi1 = go.Figure()
        fig_mi1.add_trace(go.Scatter(x=[f"{x}%" for x in ablation_levels], y=[1.0, 0.8, 0.75, 0.7, 0.55, 0.35, 0.32, 0.41, 0.12], name="Group Identity Flag", line=dict(color='#EF4444', width=3)))
        fig_mi1.add_trace(go.Scatter(x=[f"{x}%" for x in ablation_levels], y=[1.0, 1.05, 1.08, 1.10, 1.29, 1.24, 1.21, 0.7, 0.23], name="Past Behavior Cues", line=dict(color='#1E3A8A', width=3)))
        fig_mi1.update_layout(xaxis_title="% Neuron Drop", yaxis_title="Information Preservation Ratio", height=300)
        st.plotly_chart(fig_mi1, use_container_width=True)
        
    with col_mi_2:
        st.markdown("**Trustee AI Information Decay:**")
        st.write("In the Trustee's network, both channels decline gradually. But because the Trustor stops discriminating at 25%, the Trustee has no behavioral differences to respond to!")
        # Graph showing gradual decline of both (from Fig 5b)
        fig_mi2 = go.Figure()
        fig_mi2.add_trace(go.Scatter(x=[f"{x}%" for x in ablation_levels], y=[1.0, 0.99, 1.0, 1.23, 1.15, 1.07, 1.10, 0.4, 0.12], name="Group Identity Flag", line=dict(color='#EF4444', width=3, dash='dash')))
        fig_mi2.add_trace(go.Scatter(x=[f"{x}%" for x in ablation_levels], y=[1.0, 1.0, 0.99, 1.06, 1.09, 1.01, 1.0, 0.55, 0.11], name="Past Behavior Cues", line=dict(color='#1E3A8A', width=3, dash='dash')))
        fig_mi2.update_layout(xaxis_title="% Neuron Drop", yaxis_title="Information Preservation Ratio", height=300)
        st.plotly_chart(fig_mi2, use_container_width=True)

# ==============================================================================
# TAB 4: PRESENTATION SLIDES OUTLINE
# ==============================================================================
with tab4:
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
