import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import random

# Page configuration
st.set_page_config(
    page_title="The Power Game & Culturally Embedded AI",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for executive/professional look
st.markdown("""
<style>
    .reportview-container {
        background: #f8f9fa;
    }
    .main-title {
        font-size: 38px;
        font-weight: 800;
        color: #1e3d59;
        margin-bottom: 5px;
    }
    .subtitle {
        font-size: 18px;
        color: #17b978;
        font-weight: 500;
        margin-bottom: 25px;
    }
    .card {
        background-color: white;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        margin-bottom: 20px;
    }
    .metric-value {
        font-size: 28px;
        font-weight: bold;
        color: #1e3d59;
    }
</style>
""", unsafe_with_html=True)

# Define research data
data_languages = {
    'Language': [
        'Simplified Chinese', 'Traditional Chinese', 'Japanese', 'Arabic', 'German', 
        'Polish', 'Turkish', 'Spanish', 'Greek', 'Korean', 'English', 'French', 
        'Indonesian', 'Italian', 'Welsh', 'Afrikaans', 'Russian'
    ],
    'Mean Offer': [
        39.56, 38.45, 35.97, 34.10, 34.04, 33.70, 33.14, 32.46, 31.97, 31.92, 
        31.80, 31.71, 30.31, 30.25, 29.16, 28.98, 27.60
    ],
    'Std Dev': [
        19.96, 13.66, 15.74, 16.71, 16.87, 16.71, 14.87, 17.36, 17.33, 15.09, 
        16.40, 16.71, 16.59, 18.05, 19.31, 18.40, 19.13
    ],
    'Power Distance (GLOBE)': [
        0.44, 0.49, 0.35, 0.50, 0.21, 0.47, 0.16, 0.20, 0.15, 0.22, 
        0.35, 0.32, 0.28, 0.19, 0.33, 0.26, 0.36
    ],
    'Region': [
        'East Asia', 'East Asia', 'East Asia', 'Middle East', 'Europe', 
        'Europe', 'Middle East', 'Latin America/Europe', 'Europe', 'East Asia', 
        'Anglo', 'Europe', 'Southeast Asia', 'Europe', 'Anglo', 'Africa', 'Eastern Europe'
    ]
}

df_research = pd.DataFrame(data_languages)

# Game Instructions (English) - using raw string to prevent warnings
instructions_en = r"""
In today's experiment, there are two possible roles for you to play: the **Proposer** and the **Responder**. 
In every round, one Proposer and one Responder will be paired to determine how to divide a pool of **100 dollars** between them. 
The pairings change from round to round. You will not be able to identify who is your opponent in the game.

* **For a Proposer**: The decision task is to determine how much out of 100 dollars to offer to the Responder. The offer can be any integer from 0 to 100.
* **For a Responder**: The decision is to indicate the minimum amount (out of the pool) that he/she is willing to accept, which is referred as the **threshold** in the game. The threshold can be any integer from 0 to 100.

**The Power Mechanism (Veto Probability \pi):**
In this game, Responders may have an option to reject offers by Proposers. The probability for a Responder to have such an option is determined randomly and is denoted as **\pi** (e.g., 10% for Low Power, 90% for High Power). 

The final distribution of the 100 dollars is determined as follows:
1. **If the computer does NOT give the Responder the option to reject** (probability $1 - \pi$): The pool is divided according to the Proposer's offer. Proposer keeps $(100 - Offer)$, and Responder gets $Offer$.
2. **If the computer DOES give the Responder the option to reject** (probability $\pi$):
   * If **Offer $\ge$ Threshold**: The offer is accepted. Proposer keeps $(100 - Offer)$, and Responder gets $Offer$.
   * If **Offer $<$ Threshold**: The offer is rejected. Both players get **0 dollars**.
"""

# Translations dict
translations = {
    'Simplified Chinese (简体中文)': r"""
在今天的实验中，您将扮演两种可能的角色之一：**提议人** (Proposer) 和 **应答者** (Responder)。
在每一轮中，一名提议人和一名应答者将被配对，以决定如何分配两人生意中价值 **100元** 的总收益。
配对是随机分配的，每一轮都会发生变化。您将无法得知对手的身份。

* **提议人 (Proposer) 的任务**：决定从100元中分给应答者多少钱。提议额可以是 0 到 100 之间的任意整数。
* **应答者 (Responder) 的任务**：设定一个您愿意接受的最低金额，在游戏中被称为**接受门槛** (threshold)。门槛可以是 0 到 100 之间的任意整数。

**权力机制（否决权概率 \pi）：**
应答者有一定概率获得拒绝提议的选项。应答者拥有该选项的概率是随机决定的，记为 **\pi**（例如：10% 代表低权力，90% 代表高权力）。

最终分配结果如下：
1. **如果电脑未赋予应答者拒绝的权力**（概率为 $1 - \pi$）：收益直接根据提议人的提议进行分配。提议人获得 $(100 - 提议额)$，应答者获得 $提议额$。
2. **如果电脑赋予了应答者拒绝的权力**（概率为 $\pi$）：
   * 如果 **提议额 $\ge$ 门槛**：提议被接受。提议人获得 $(100 - 提议额)$，应答者获得 $提议额$。
   * 如果 **提议额 $<$ 门槛**：提议被拒绝。**双方最终得分均为 0元**。
""",
    'Traditional Chinese (繁體中文)': r"""
在今天的實驗中，您將扮演兩種可能的角色之一：**提議人** (Proposer) 和 **應答者** (Responder)。
在每一輪中，一名提議人和一名應答者將被配對，以決定如何分配兩人生意中價值 **100元** 的總收益。
配對是隨機分配的，每一輪都會發生變化。您將無法得知對手的身份。

* **提議人 (Proposer) 的任務**：決定從100元中分給應答者多少錢。提議額可以是 0 到 100 之間的任意整數。
* **應答者 (Responder) 的任務**：設定一個您願意接受的最低金額，在遊戲中被稱為**接受門檻** (threshold)。門檻可以是 0 到 100 之間的任意整數。

**權力機制（否決權概率 \pi）：**
應答者有一定概率獲得拒絕提議的選項。應答者擁有該選項的概率是隨機決定的，記為 **\pi**（例如：10% 代表低權力，90% 代表高權力）。

最終分配結果如下：
1. **如果電腦未賦予應答者拒絕的權力**（概率為 $1 - \pi$）：收益直接根據提議人的提議進行分配。提議人獲得 $(100 - 提議額)$，應答者獲得 $提議額$。
2. **如果電腦賦予了應答者拒絕的權力**（概率為 $\pi$）：
   * 如果 **提議額 $\ge$ 門檻**：提議被接受。提議人獲得 $(100 - 提議額)$，應答者獲得 $提議額$。
   * 如果 **提議額 $<$ 門檻**：提議被拒絕。**雙方最終得分均為 0元**。
""",
    'French (Français)': r"""
Dans l'expérience d'aujourd'hui, il y a deux rôles possibles pour vous : le **Proposeur** et le **Répondant**. 
À chaque tour, un Proposeur et un Répondant seront associés pour déterminer comment diviser une cagnotte de **100 dollars** entre eux. 
L'ordinateur attribue l'appariement aléatoire de sorte que les paires changeront de tour en tour. Vous ne pourrez pas identifier qui est votre adversaire.

* **Pour un Proposeur** : La tâche de décision consiste à déterminer combien sur 100 dollars offrir au Répondant. L'offre peut être n'importe quel nombre entier de 0 à 100.
* **Pour le Répondant** : La décision est d'indiquer le montant minimum qu'il/elle est prêt(e) à accepter, ce qui est appelé le **seuil** dans le jeu. Le seuil peut être n'importe quel nombre entier de 0 à 100.

**Le Mécanisme de Pouvoir (Probabilité de Veto \pi) :**
Dans ce jeu, il est possible pour les Répondants d'avoir la possibilité de rejeter les offres des Proposeurs. La probabilité pour un Répondant d'avoir une telle option est déterminée aléatoirement, notée **\pi** (ex. 10% pour un pouvoir faible, 90% pour un pouvoir élevé).

La répartition finale des 100 dollars est déterminée comme suit :
1. **Si l'ordinateur ne donne pas au Répondant l'option de rejet** (probabilité $1 - \pi$) : La cagnotte est divisée selon l'offre du Proposeur. Le Proposeur garde $(100 - Offre)$, et le Répondant obtient $Offre$.
2. **Si l'ordinateur donne au Répondant l'option de rejet** (probabilité $\pi$) :
   * Si **Offre $\ge$ Seuil** : Le Répondant accepte l'offre. Le Proposeur garde $(100 - Offre)$, et le Répondant obtient $Offre$.
   * Si **Offre $<$ Seuil** : Le Répondant rejette l'offre. Les deux joueurs obtiennent **0 dollar**.
""",
    'Japanese (日本語)': r"""
今日の実験では、あなたが果たすべき役割は2つあります：**提案者** (Proposer) と **応答者** (Responder)。
各ラウンドで、1人の提案者と1人の応答者がペアになり、**100ドル**のプールをどのように分配するかを決定します。
ペアリングはランダムに変更され、対戦相手を特定することはできません。

* **提案者 (Proposer) の決定**: 100ドルのうち、応答者にいくら提供するかを決定します。提案額は0から100の任意の整数です。
* **応答者 (Responder) の決定**: 自分が受け入れることができる最小額を設定します。これはゲーム内では**閾値** (threshold) と呼ばれます。閾値は0から100の任意の整数です。

**権力メカニズム（拒否権の確率 \pi）：**
このゲームでは、応答者が提案者のオファーを拒否するオプション（拒否権）を持つ場合があります。このオプションが応答者に与えられる確率は、ランダムに決定され、**\pi**と表記されます（例：10%は低権力、90%は高権力）。

最終的な100ドルの分配は以下のように決定されます：
1. **コンピューターが応答者に拒否権を与えない場合**（確率 $1 - \pi$）：プールは提案者のオファーに従って分割されます。提案者は $(100 - オファー)$ を受け取り、応答者は $オファー$ を受け取ります。
2. **コンピューターが応答者に拒否権を与える場合**（確率 $\pi$）：
   * **オファー $\ge$ 閾値** の場合：オファーは受け入れられます。提案者は $(100 - オファー)$、応答者は $オファー$ を受け取ります。
   * **オファー $<$ 閾値** の場合：オファーは拒否されます。**両方のプレイヤーが0ドル**になります。
""",
    'German (Deutsch)': r"""
In dem heutigen Experiment gibt es zwei mögliche Rollen für Sie: den **Antragsteller** (Proposer) und den **Empfänger** (Responder). 
In jeder Runde werden ein Antragsteller und ein Empfänger gepaart, um zu bestimmen, wie ein Pool von **100 Dollar** zwischen ihnen aufgeteilt wird. 
Die Paarungen ändern sich von Runde zu Runde und Sie können Ihren Partner nicht identifizieren.

* **Für einen Antragsteller**: Die Aufgabe besteht darin, festzulegen, wie viel von den 100 Dollar dem Empfänger angeboten wird. Das Angebot kann jede ganze Zahl von 0 bis 100 sein.
* **Für einen Empfänger**: Die Entscheidung besteht darin, den Mindestbetrag anzugeben, den er/sie bereit ist zu akzeptieren, was im Spiel als **Schwellenwert** (threshold) bezeichnet wird. Der Schwellenwert kann jede ganze Zahl von 0 bis 100 sein.

**Der Machtmechanismus (Veto-Wahrscheinlichkeit \pi):**
In diesem Spiel haben Empfänger möglicherweise die Option, Angebote abzulehnen. Die Wahrscheinlichkeit dafür wird zufällig bestimmt und als **\pi** bezeichnet (z.B. 10% für geringe Macht, 90% für hohe Macht).

Die endgültige Aufteilung der 100 Dollar erfolgt wie folgt:
1. **Wenn der Computer dem Empfänger KEINE Option zur Ablehnung gibt** (Wahrscheinlichkeit $1 - \pi$): Der Pool wird gemäß dem Angebot des Antragstellers geteilt. Der Antragsteller behält $(100 - Angebot)$ und der Empfänger erhält das $Angebot$.
2. **Wenn der Computer dem Empfänger die Option zur Ablehnung GIBT** (Wahrscheinlichkeit $\pi$):
   * Wenn **Angebot $\ge$ Schwellenwert**: Das Angebot wird angenommen. Der Antragsteller behält $(100 - Angebot)$ und der Empfänger erhält das $Angebot$.
   * Wenn **Angebot $<$ Schwellenwert**: Das Angebot wird abgelehnt. Beide Spieler erhalten **0 Dollar**.
""",
    'Spanish (Español)': r"""
En el experimento de hoy, hay dos roles posibles para usted: el **Proponente** (Proposer) y el **Receptor** (Responder). 
En cada ronda, se emparejará a un Proponente y a un Receptor para determinar cómo dividir un fondo de **100 dólares** entre ellos. 
El emparejamiento es aleatorio y cambia de ronda en ronda. No podrá identificar quién es su oponente.

* **Para un Proponente**: La tarea de decisión es determinar cuánto de los 100 dólares ofrecer al Receptor. La oferta puede ser cualquier número entero de 0 a 100.
* **Para un Receptor**: La decisión es indicar la cantidad mínima que está dispuesto/a a aceptar, lo que se denomina **umbral** (threshold) en el juego. El umbral puede ser cualquier número entero de 0 a 100.

**El Mecanismo de Poder (Probabilidad de Veto \pi):**
En este juego, es posible que los Receptores tengan la opción de rechazar las ofertas de los Proponentes. La probabilidad de que tengan dicha opción se determina al azar y se denota como **\pi** (por ejemplo, 10% para bajo poder, 90% para alto poder).

La distribución final de los 100 dólares se determina de la siguiente manera:
1. **Si la computadora NO otorga al Receptor la opción de rechazar** (probabilidad $1 - \pi$): El fondo se divide según la oferta del Proponente. El Proponente se queda con $(100 - Oferta)$ y el Receptor obtiene la $Oferta$.
2. **Si la computadora SÍ otorga al Receptor la opción de rechazar** (probabilidad $\pi$):
   * Si **Oferta $\ge$ Umbral**: La oferta es aceptada. El Proponente se queda con $(100 - Oferta)$ y el Receptor obtiene la $Oferta$.
   * Si **Oferta $<$ Umbral**: La oferta es rechazada. Ambos jugadores obtienen **0 dólares**.
"""
}

# Sidebar Navigation
st.sidebar.image("https://upload.wikimedia.org/wikipedia/commons/e/e5/San_Jose_State_University_seal.svg", width=100) # Optional placeholder or school logo
st.sidebar.title("EMBA Session 1")
st.sidebar.markdown("**Linguistic Relativity, Power & Fairness**")
menu = st.sidebar.radio("Navigation", ["1. Live Interactive Power Game", "2. 17-Language Instruction Checker", "3. Research Insights & Charts", "4. Lesson Plan & Materials"])

st.sidebar.markdown("---")
st.sidebar.markdown("Developed for international EMBA training events on **Culturally Embedded AI Biases**.")

# Tab 1: Live Interactive Power Game
if menu == "1. Live Interactive Power Game":
    st.markdown('<div class="main-title">Interactive Power Game</div>', unsafe_with_html=True)
    st.markdown('<div class="subtitle">Experience the modified ultimatum game in real-time. Play vs. an AI agent configured with culturally embedded strategies.</div>', unsafe_with_html=True)
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.markdown("### Game Setup")
        role = st.radio("Choose Your Role:", ["Proposer (You) vs. AI Responder", "Responder (You) vs. AI Proposer"])
        pi = st.slider("Responder Veto Probability (pi):", min_value=0.0, max_value=1.0, value=0.5, step=0.1, 
                       help="High pi = High Responder Veto Power. Low pi = Low Responder Power (closer to Dictator Game).")
        
        ai_culture = st.selectbox("Configure AI Partner's Cultural Context:", df_research['Language'].tolist(), index=10, # default English
                                  help="The AI's strategy will dynamically mirror the empirical behavior of Large Language Models prompted in this language.")
        
        # Pull cultural metrics to drive AI behavior
        pdi_val = df_research[df_research['Language'] == ai_culture]['Power Distance (GLOBE)'].values[0]
        mean_off = df_research[df_research['Language'] == ai_culture]['Mean Offer'].values[0]
        
        st.markdown(f"""
        **AI Cultural Metrics:**
        * Language: `{ai_culture}`
        * Normalized Power Distance Index (PDI): `{pdi_val:.2f}` 
        * Empirical Proposer Offer in Research: `{mean_off:.2f} / 100`
        """)
        
        st.markdown("---")
        st.markdown("### Your Decision")
        
        if "Proposer" in role:
            user_offer = st.number_input("Your Offer to Responder (0 to 100):", min_value=0, max_value=100, value=30, step=1)
            user_decision = user_offer
        else:
            user_threshold = st.number_input("Your Minimum Acceptable Threshold (0 to 100):", min_value=0, max_value=100, value=25, step=1)
            user_decision = user_threshold
            
        play_btn = st.button("Play Round & Resolve Outcome 🎲", type="primary")
        
    with col2:
        st.markdown("### Interactive Simulation & Visual Feedback")
        
        if play_btn:
            # Simulate the partner's decision based on research parameters
            # Proposer offer rises with both high PDI and high Veto Probability (pi)
            # Responder threshold rises with high PDI and high Veto Probability (pi)
            if "Proposer" in role:
                # AI is Responder. Let's calculate its threshold.
                # Heuristic: base threshold ~ 25. High PDI increases threshold. High pi increases threshold.
                base_threshold = 20 + (pdi_val * 15) + (pi * 15)
                # Add some realistic random variation around standard deviation
                ai_threshold = int(np.clip(np.random.normal(base_threshold, 8), 0, 100))
                
                # Determine if veto is granted this round
                veto_active = random.random() < pi
                
                st.markdown(f"#### Round Outcome")
                st.write(f"🤝 **You offered:** `${user_offer}`")
                st.write(f"🤖 **AI Responder Threshold ({ai_culture} context):** `${ai_threshold}`")
                st.write(f"⚡ **Veto Probability (pi) was set to:** `{pi*100:.0f}%`")
                
                if veto_active:
                    st.info("📢 **Veto Option Activated:** The computer granted the Responder the option to reject.")
                    if user_offer >= ai_threshold:
                        st.success(f"✅ **Offer Accepted!** Since your offer of `${user_offer}` is greater than or equal to the AI's threshold of `${ai_threshold}`.")
                        p_earning = 100 - user_offer
                        r_earning = user_offer
                    else:
                        st.error(f"❌ **Offer Rejected!** Since your offer of `${user_offer}` is less than the AI's threshold of `${ai_threshold}`.")
                        p_earning = 0
                        r_earning = 0
                else:
                    st.warning("🔒 **No Veto Option:** The computer did NOT grant the Responder the option to reject. Your offer applies unilaterally!")
                    st.success(f"✅ **Offer Enforced!**")
                    p_earning = 100 - user_offer
                    r_earning = user_offer
                    
            else:
                # AI is Proposer. Let's calculate its offer.
                # Heuristic: base offer ~ 30. High PDI increases offer. High pi increases offer.
                base_offer = 25 + (pdi_val * 15) + (pi * 20)
                ai_offer = int(np.clip(np.random.normal(base_offer, 8), 0, 100))
                
                veto_active = random.random() < pi
                
                st.markdown(f"#### Round Outcome")
                st.write(f"🤖 **AI Proposer Offer ({ai_culture} context):** `${ai_offer}`")
                st.write(f"🤝 **You set a Threshold of:** `${user_threshold}`")
                st.write(f"⚡ **Veto Probability (pi) was set to:** `{pi*100:.0f}%`")
                
                if veto_active:
                    st.info("📢 **Veto Option Activated:** The computer granted you the option to reject.")
                    if ai_offer >= user_threshold:
                        st.success(f"✅ **You Accepted!** Since the AI's offer of `${ai_offer}` met your threshold of `${user_threshold}`.")
                        p_earning = 100 - ai_offer
                        r_earning = ai_offer
                    else:
                        st.error(f"❌ **You Rejected!** Since the AI's offer of `${ai_offer}` was below your threshold of `${user_threshold}`.")
                        p_earning = 0
                        r_earning = 0
                else:
                    st.warning("🔒 **No Veto Option:** The computer did NOT grant you the option to reject. The AI's offer applies unilaterally.")
                    st.success(f"✅ **Offer Enforced!**")
                    p_earning = 100 - ai_offer
                    r_earning = ai_offer
            
            # Display final scorecard
            st.markdown("### Earnings Scorecard")
            score_col1, score_col2 = st.columns(2)
            with score_col1:
                st.metric("Proposer Earnings", f"${p_earning}")
            with score_col2:
                st.metric("Responder Earnings", f"${r_earning}")
                
            # Connect back to theory
            st.info("""
            **EMBA Teaching Point:** Notice how the AI's decisions adjust based on its configured 'Language Context' PDI. 
            In high Power Distance cultures (e.g. Traditional or Simplified Chinese, Polish), agents tend to make larger offers 
            and demand higher thresholds, expecting hierarchy but also expecting stronger distributive fairness to maintain equilibrium. 
            Conversely, under lower PDI languages, offers are tighter.
            """)
        else:
            st.markdown("""
            <div style='text-align: center; padding: 50px; border: 2px dashed #ccc; border-radius: 10px; color: #666;'>
                <h3>Awaiting Your Move</h3>
                <p>Configure the game setup on the left and click <b>Play Round & Resolve Outcome</b> to simulate the transaction!</p>
            </div>
            """, unsafe_with_html=True)

# Tab 2: 17-Language Instruction Checker
elif menu == "2. 17-Language Instruction Checker":
    st.markdown('<div class="main-title">Multi-Language Prompt Translation Explorer</div>', unsafe_with_html=True)
    st.markdown('<div class="subtitle">Select a target language to check how the exact same mathematical game rules are presented. Observe the linguistic relativity first-hand.</div>', unsafe_with_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🇬🇧 English Reference Instructions")
        st.write(instructions_en)
        
    with col2:
        st.markdown("### 🌐 Target Language Translation")
        selected_lang = st.selectbox("Select Target Language to View Translation:", list(translations.keys()))
        st.markdown(f"#### {selected_lang}")
        st.write(translations[selected_lang])
        
    st.markdown("---")
    st.markdown("### 💡 Interactive Activity: Spot the Translation Framing")
    st.markdown(r"""
    Have your EMBA students select their native or preferred language. Ask them to check:
    1. **Are the core game mechanics exactly preserved?** (The back-translation cosine similarity score in the research paper averages a near-perfect **0.97** across all models [419]).
    2. **Does the linguistic tone feel different?** For instance, in Chinese or Japanese, honorifics or implicit social status markers are embedded [389]. In English, the language is transactional. 
    3. **This is the core concept of the Sapir-Whorf Hypothesis (Linguistic Relativity):** The language of the prompt activates culturally distinct behavioral schemas in the neural network weights of generative AI agents, resulting in different choices despite identical rules [388-390]!
    """)

# Tab 3: Research Insights & Charts
elif menu == "3. Research Insights & Charts":
    st.markdown('<div class="main-title">Generative AI Cross-Country Game Results</div>', unsafe_with_html=True)
    st.markdown('<div class="subtitle">Empirical evidence of culturally embedded biases across GPT-4.1, Gemini 2.5 Flash, and Claude 4 Sonnet.</div>', unsafe_with_html=True)
    
    tab_view1, tab_view2 = st.tabs(["📊 Offers by Language", "📈 Power Distance Correlation"])
    
    with tab_view1:
        st.markdown("### Average Proposer Offers in the Power Game")
        st.write("This bar chart displays the mean amount offered out of a $100 endowment, pooled across 3 major LLMs prompted in 17 different languages.")
        
        # Sorted chart
        df_sorted = df_research.sort_values(by='Mean Offer', ascending=False)
        fig_bar = px.bar(
            df_sorted, 
            x='Language', 
            y='Mean Offer', 
            color='Region',
            text='Mean Offer',
            error_y='Std Dev',
            title='Proposer Offers by Prompt Language (Pooled LLMs)',
            labels={'Mean Offer': 'Average Offer ($)', 'Language': 'Prompt Language'},
            color_discrete_sequence=px.colors.qualitative.Bold
        )
        fig_bar.update_traces(texttemplate='%{text:.1f}', textposition='outside')
        fig_bar.update_layout(uniformtext_minsize=8, uniformtext_mode='hide', height=500)
        st.plotly_chart(fig_bar, use_container_width=True)
        
        st.markdown("""
        **Core Finding:** The prompt language alone drives highly significant shifts in offer sizes, ranging from a high of **$39.56** in Simplified Chinese to a low of **$27.60** in Russian [428-433].
        """)
        
    with tab_view2:
        st.markdown("### Offer Sizes vs. GLOBE Power Distance Values")
        st.write("Does the variation correlate with human culture? Below is the scatter plot of the average LLM Proposer offers against the normalized country-level GLOBE Power Distance Value (PDI) [436-438].")
        
        fig_scatter = px.scatter(
            df_research,
            x='Power Distance (GLOBE)',
            y='Mean Offer',
            text='Language',
            color='Region',
            size=[10]*len(df_research),
            trendline='ols',
            title='LLM Proposer Offer vs. Normalized GLOBE Power Distance Values',
            labels={'Power Distance (GLOBE)': 'Normalized Power Distance Index (0 = Min, 1 = Max)', 'Mean Offer': 'Average Proposer Offer ($)'},
            height=600
        )
        fig_scatter.update_traces(textposition='top center')
        st.plotly_chart(fig_scatter, use_container_width=True)
        
        st.markdown("""
        **Key Takeaway:** There is a highly significant positive correlation ($p < 0.001$ for offers, $p < 0.05$ for thresholds) [436]. 
        Languages associated with higher power-distance societies (e.g., Chinese, Arabic, Polish) systematically produce higher offers 
        and set higher thresholds [437-440]. The model-level regressions (Claude 4, GPT-4.1, Gemini 2.5) confirm this positive gradient is stable across architectures [438, 481-482].
        """)

# Tab 4: Lesson Plan & Materials
elif menu == "4. Lesson Plan & Materials":
    st.markdown('<div class="main-title">Session 1 Lesson Plan (1 Hour)</div>', unsafe_with_html=True)
    st.markdown('<div class="subtitle">Full syllabus and facilitation guide for your EMBA training session.</div>', unsafe_with_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        ### ⏱️ Session Timeline (60 Minutes)
        
        * **00:00 - 00:10 (10 mins) | Introduction & Game Launch**
          * Explain the Modified Ultimatum Game rules.
          * Introduce the Veto Probability (pi) as the measure of responder power.
        * **00:10 - 00:25 (15 mins) | Interactive Activity (Game Play)**
          * Have students pair up and play the game using the slips in **CUFE game_Wu.docx** (or let them run this Streamlit app locally!).
          * Alternatively, run the "Live Interactive Game" tab on the projector and play rounds collectively.
        * **00:25 - 00:35 (10 mins) | Translation Comparison Activity**
          * Have students switch to the **17-Language Instruction Checker** tab.
          * Let multilingual students compare English with their native/learned language. Ask: *Does the tone feel different? Does it encode social status differently?*
        * **00:35 - 00:55 (20 mins) | Executive Lecture & Presentation**
          * Use the **Research Insights & Charts** tab.
          * Contrast human behavior in the game (US vs. China, from the **Power and Fairness CUFE.pptx** slides) with LLM agent behavior (from the **Cross-Country Game Working Paper**).
          * Highlight how prompt language activates culturally contingent decision thresholds in AI.
        * **00:55 - 01:00 (5 mins) | Q&A & Key Takeaways**
          * Emphasize the risk of deploying "universal" multilingual AI agents in corporate negotiation, HR screening, or procurement without language-specific audits [444-445].
        """)
        
    with col2:
        st.markdown("""
        ### 📦 Required Materials
        
        1. **CUFE game_Wu.docx**: Contains the user slips and formal instructions for playing the game manually by hand [32-33].
        2. **Power and Fairness CUFE.pptx**: Excellent slides for comparing Chinese and US human-subject behavior [489, 507-508].
        3. **New LLM Cross Country Game Working Paper**: The master text for discussing the statistical findings, translations similarity, and GLOBE correlation indices [368-372].
        4. **This Web Application (`power_game_app.py`)**: Can be deployed on a local laptop or a server for students to play during the event.
        
        ### 🔑 Key Teaching Messages for EMBA Executives
        
        1. **Language is NOT neutral in AI**: When you deploy a global Customer Service Agent, Procurement Negotiator, or HR Screening bot, prompting it in Spanish vs. Japanese vs. German literally alters its decision threshold without you writing any custom code [373, 444].
        2. **Cultural Schema Activation**: LLMs are trained on massive corpora from different cultures. Prompting in a specific language acts as a "cultural key" that retrieves specific behavioral norms embedded in that training data [373, 447-448].
        3. **The Multi-Objective Audit Requirement**: Multinational corporations must execute language-specific behavioral audits on their generative AI agent fleets before launching them across borders [444-445].
        """)

st.markdown("---")
st.caption("EMBA Consortium Training Companion App • Grounded in the latest academic studies on AI Social Intelligence and Linguistic Relativity.")
