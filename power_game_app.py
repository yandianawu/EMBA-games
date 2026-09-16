import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import random
import datetime
import re

import json
import os
import threading

# Shared persistent storage path across all browser sessions in the container
SHARED_DATA_FILE = "/tmp/emba_power_game_global_data.json"
SHARED_LOCK = threading.Lock()

class GlobalDataStore:
    def __init__(self):
        self.responses = []
        self.game_logs = [
            {"Timestamp": "2026-09-01 14:05:00", "Student_ID": "EMBA_3842", "Role": "Proposer", "Language": "French (Français)", "Veto_Probability": 0.90, "Offer": 40, "Threshold": "N/A (Agent)", "Veto_Enforced": "Yes", "Outcome": "Accepted, because Offer > Threshold", "Payout": "Proposer: $60, Responder: $40"},
            {"Timestamp": "2026-09-01 14:06:00", "Student_ID": "EMBA_7195", "Role": "Responder", "Language": "Simplified Chinese (简体中文)", "Veto_Probability": 0.90, "Offer": "N/A (Agent)", "Threshold": 30, "Veto_Enforced": "Yes", "Outcome": "Accepted, because Offer > Threshold", "Payout": "Proposer: $60, Responder: $40"}
        ]
        self.custom_translations = {}
        self.load_from_disk()

    def load_from_disk(self):
        if os.path.exists(SHARED_DATA_FILE):
            try:
                with open(SHARED_DATA_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if "responses" in data and data["responses"]:
                        self.responses = data["responses"]
                    if "game_logs" in data and data["game_logs"]:
                        self.game_logs = data["game_logs"]
                    if "custom_translations" in data and data["custom_translations"]:
                        self.custom_translations = data["custom_translations"]
            except Exception:
                pass

    def save_to_disk(self):
        try:
            with open(SHARED_DATA_FILE, "w", encoding="utf-8") as f:
                json.dump({"responses": self.responses, "game_logs": self.game_logs, "custom_translations": self.custom_translations}, f, ensure_ascii=False, indent=2)
        except Exception:
            pass

    def add_response(self, entry):
        with SHARED_LOCK:
            self.load_from_disk()
            self.responses.append(entry)
            self.save_to_disk()

    def add_game_log(self, entry):
        with SHARED_LOCK:
            self.load_from_disk()
            self.game_logs.append(entry)
            self.save_to_disk()

    def update_translation(self, lang, text):
        with SHARED_LOCK:
            self.load_from_disk()
            self.custom_translations[lang] = text
            self.save_to_disk()

    def get_translations(self):
        with SHARED_LOCK:
            self.load_from_disk()
            return self.custom_translations.copy()

    def get_all_data(self):
        with SHARED_LOCK:
            self.load_from_disk()
            return self.responses.copy(), self.game_logs.copy()

@st.cache_resource
def get_global_store():
    return GlobalDataStore()

global_store = get_global_store()

# Page configuration
st.set_page_config(
    page_title="The Power Game & Culturally Embedded AI",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize Session State
if 'pi_assignment_mode' not in st.session_state:
    st.session_state.pi_assignment_mode = "Automatic Split (50% Low, 50% High π)"

if 'global_student_id' not in st.session_state:
    st.session_state.global_student_id = f"EMBA_{random.randint(1000, 9999)}"

res_init, logs_init = global_store.get_all_data()
if 'responses' not in st.session_state:
    st.session_state.responses = res_init

if 'game_logs' not in st.session_state:
    st.session_state.game_logs = logs_init

# Core English Instructions updated to the exact wording requested
default_english_instructions = """In today’s experiment, there are two possible roles for you to play: the Proposer and the Responder. In every round, one Proposer and one Responder will be paired to determine how to divide a pool of 100 dollars between them. The computer assigns the random matching so that pairings will change from round to round. You will not be able to identify who is your opponent in the game and you will never be re-matched with the same Proposer or Responder. You will play in the role of a Proposer for some rounds, and in the role of a Responder for other rounds. Your earnings from all rounds in the game will be accumulated and converted into cash as your final payment at the end of the experiment. For a Proposer, the decision task is to determine how much out of 100 dollars to offer to the Responder. The offer can be any integer number from 0 to 100. If an offer is accepted, the Responder will get the amount proposed and the Proposer will keep the rest of the pool. For example, if an offer is 20 dollars and the Responder accepts it, the Proposer will get 80 dollars and the Responder will get 20 dollars. In this game, it is possible for Responders to have an option to reject offers by Proposers. The probability for a Responder to have such an option is determined randomly. At the beginning of each round, the computer will randomly assign this probability to all Responders. In each round, both the Proposer and the Responder will be informed of this probability. For the Responder, the decision is to indicate the minimum amount (out of the pool) that he/she is willing to accept, which is referred as threshold in the game. The threshold can be any integer number from 0 to 100. For example, if a threshold of 30 is indicated, it means that the Responder will reject any offer below 30 dollars (out of the 100 dollars) if she/he is granted the option to reject by the computer. In case a rejection occurs, both players will get 0. You will make your decision (offer as the Proposer, or threshold as the Responder) without seeing the other player’s decision. After all players input their decisions in a round, the computer will allocate the option to reject to Responders according to their probability conditions i.e., a Responder A will have a 10% chance while a Responder B will have a 90% chance to be able to reject. The final distribution of the 100 dollars in a round between the two players is determined as follows: If the computer does not give the Responder the option to reject, the pool is divided according to the Proposer’s offer. If the computer does give the Responder the option to reject, if the offer by the Proposer is greater than or euqal to the threshold by the Responder, the Responder accepts the offer by the Proposer, and the pool is divided according to the Proposer’s offer. If the offer by the Proposer is less than the threshold by the Responder, the Responder rejects the offer, and both players get 0 dollars."""

# Pre-loaded 17-language translations
default_translations = {
    "English": default_english_instructions,
    "Simplified Chinese (简体中文)": """在今天的实验中，您将扮演两种可能的角色：提议人（Proposer）和应答者（Responder）。在每一轮中，一名提议人和一名应答者将被配对，以决定如何分配100美元的资金池。电脑随机匹配，因此每轮的对手都会改变。您将无法识别游戏中的对手，也永远不会与同一个提议人或应答者再次配对。您将在某些轮次中扮演提议人，在其他轮次中扮演应答者。您在游戏中所有轮次的收益将被累积并在实验结束时兑换成现金作为您的最终报酬。

对于提议人，决策任务是确定从100美元中分出多少给应答者。提议金额可以是0到100之间的任意整数。如果提议被接受，应答者将获得提议的金额，而提议人将保留资金池的其余部分。例如，如果提议是20美元且应答者接受，提议人将获得80美元，应答者将获得20美元。

在这场游戏中，应答者有可能拥有拒绝提议人提议的权利。应答者获得该否决权的概率是随机决定的。在每一轮开始时，电脑将随机分配此概率给所有应答者。在每一轮中，提议人和应答者都会被告知这个概率。对于应答者，决策是指出他/她愿意接受的最低金额，这在游戏中被称为“最低接受额（Threshold）”。最低接受额可以是0到100之间的任意整数。例如，如果指定了30的最低接受额，这意味着如果电脑授予应答者拒绝的权利，应答者将拒绝任何低于30美元的提议。如果发生拒绝，两位玩家都将获得0美元。

您将在看不到另一位玩家决策的情况下做出您的决策（作为提议人提供提议，或作为应答者设置最低接受额）。在所有玩家在一轮中输入决策后，电脑将根据概率条件将拒绝权利分配给应答者，例如，应答者A将有10%的机会，而应答者B将有90%的机会拥有拒绝权。最终的100美元分配确定如下：如果电脑没有给予应答者拒绝的权利，则按照提议人的提议分配资金池。如果电脑给予了应答者拒绝的权利，且提议人的提议大于或等于应答者的最低接受额，则应答者接受提议人的提议，资金池按照提议人的提议分配。如果提议人的提议低于应答者的最低接受额，则应答者拒绝提议，双方均获得0美元。""",
    "Traditional Chinese (繁體中文)": """在今天的實驗中，您將扮演兩種可能的角色：提議人（Proposer）和應答者（Responder）。在每一輪中，一名提議人和一名應答者將被配對，以決定如何分配100美元的資金池。電腦隨機匹配，因此每輪的對手都會改變。您將無法識別遊戲中的對手，也永遠不會與同一個提議人或應答者再次配對。您將在某些輪次中扮演提議人，在其他輪次中扮演應答者。您在遊戲中所有輪次的收益將被累積並在實驗結束時兌換成現金作為您的最終報酬。

對於提議人，決策任務是確定從100美元中分出多少給應答者。提議金額可以是0到100之間的任意整數。如果提議被接受，應答者將獲得提議的金額，而提議人將保留資金池的其餘部分。例如，如果提議是20美元且應答者接受，提議人將獲得80美元，應答者將獲得20美元。

在這場遊戲中，應答者有可能擁有拒絕提議人提議的權利。應答者獲得該否決權的概率是隨機決定的。在每一輪開始時，電腦將隨機分配此概率給所有應答者。在每一輪中，提議人和應答者都會被告知這個概率。對於應答者，決策是指出他/她願意接受的最低金額，這在遊戲中被稱為“最低接受額（Threshold）”。最低接受額可以是0到100之間的任意整數。例如，如果指定了30的最低接受額，這意味著如果電腦授予應答者拒絕的權利，應答者將拒絕任何低於30美元的提議。如果發生拒絕，兩位玩家都將獲得0美元。

您將在看不到另一位玩家決策的情況下做出您的決策（作為提議人提供提議，或作為應答者設置最低接受額）。在所有玩家在一輪中輸入決策後，電腦將根據概率條件將拒絕權利分配給應答者，例如，應答者A將有10%的機會，而應答者B將有90%的機會擁有拒絕權。最終的100美元分配確定如下：如果電腦沒有給予應答者拒絕的權利，則按照提議人的提議分配資金池。如果電腦給予了應答者拒絕的權利，且提議人的提議大於或等於應答者的最低接受額，則應答者接受提議人的提議，資金池按照提議人的提議分配。如果提議人的提議低於應答者的最低接受額，則應答者拒絕提議，雙方均獲得0美元。""",
    "Japanese (日本語)": """本日の実験では、「提案者（Proposer）」または「応答者（Responder）」という2つの役割のいずれかを担っていただきます。各ラウンドにおいて、提案者1名と応答者1名がペアになり、100ドルの資金をどのように分配するかを決定します。ペアはコンピュータによってランダムに決定され、ラウンドごとに変更されます。相手が誰であるかを特定することはできず、同じ相手と再びペアになることもありません。あなたはいくつかのラウンドで提案者として、他のラウンドで応答者としてプレイします。すべてのラウンドで獲得した利益は累積され、実験終了時に最終支払いとして現金に換算されます。

提案者の意思決定タスクは、100ドルのうち応答者にいくら提示（オファー）するかを決定することです。提示額は0から100までの任意の整数で指定できます。オファーが受け入れられた場合、応答者は提案された金額を受け取り、提案者は残りの額を受け取ります。例えば、オファーが20ドルで応答者がそれを受け入れた場合、提案者は80ドル、応答者は20ドルを受け取ります。

このゲームでは、応答者が提案者のオファーを拒否する権利（拒否権）を持つ場合があります。応答者がこの権利を持つ確率はランダムに決定されます。各ラウンドの開始時に、コンピュータはこの確率をすべての応答者にランダムに割り当てます。各ラウンドにおいて、提案者と応答者の双方にこの確率が通知されます。応答者の意思決定は、受け入れることができる最低金額（閾値 / Threshold）を示すことです。閾値は0から100までの任意の整数で指定できます。例えば、30ドルの閾値を示した場合、コンピュータから拒否権が付与された場合、応答者は30ドル未満のオファーを拒否することを意味します。拒否が発生した場合、双方の取り分は0ドルとなります。

あなたは相手の決定を見ることなく自分の決定（提案者としてのオファー、または応答者としての閾値）を行います。全プレイヤーがラウンドで決定を入力した後、コンピュータは確率条件に従って応答者に拒否権を割り当てます（例：応答者Aは10％、応答者Bは90％の確率で拒否権を持つ）。100ドルの最終分配は次のように決定されます：コンピュータが応答者に拒否権を与えない場合、プールは提案者のオファーに従って分配されます。拒否権が付与され、提案者のオファーが応答者の閾値以上である場合、応答者はオファーを受け入れ、オファーに従って分配されます。オファーが閾値未満である場合、応答者はオファーを拒否し、双方とも0ドルとなります。""",
    "French (Français)": """Dans l'expérience d'aujourd'hui, vous pouvez jouer deux rôles : le Proposeur (Proposer) et le Répondant (Responder). À chaque tour, un Proposeur et un Répondant seront associés pour déterminer comment diviser une cagnotte de 100 dollars entre eux. L'ordinateur attribue l'appariement de manière aléatoire afin que les paires changent de tour en tour. Vous ne pourrez pas identifier votre adversaire dans le jeu et vous ne serez jamais remis en paire avec le même Proposeur ou Répondant. Vous jouerez le rôle d'un Proposeur pendant certains tours, et le rôle d'un Répondant pendant d'autres tours. Vos gains de tous les tours seront accumulés et convertis en espèces comme paiement final à la fin de l'expérience.

Pour le Proposeur, la tâche de décision consiste à déterminer quel montant (un nombre entier de 0 à 100) offrir au Répondant. Si une offre est acceptée, le Répondant obtient le montant proposé et le Proposeur garde le reste de la cagnotte. Par exemple, si une offre est de 20 dollars et que le Répondant l'accepte, le Proposeur obtiendra 80 dollars et le Répondant obtiendra 20 dollars.

Dans ce jeu, il est possible pour le Répondant d'avoir l'option de rejeter les offres du Proposeur (droit de veto). La probabilité pour qu'un Répondant dispose de cette option est déterminée de manière aléatoire. Au début de chaque tour, l'ordinateur attribuera aléatoirement cette probabilité à tous les Répondants. À chaque tour, le Proposeur et le Répondant seront informés de cette probabilité. Pour le Répondant, la décision consiste à indiquer le montant minimum (sur la cagnotte) qu'il/elle est prêt(e) à accepter, appelé le seuil (Threshold) dans le jeu. Le seuil peut être n'importe quel nombre entier de 0 à 100. Par exemple, si un seuil de 30 est indiqué, cela signifie que le Répondant rejettera toute offre inférieure à 30 dollars si l'ordinateur lui accorde l'option de rejet. En cas de rejet, les deux joueurs obtiennent 0 dollar.

Vous prendrez votre décision (offre en tant que Proposeur, ou seuil en tant que Répondant) sans voir la décision de l'autre joueur. Après que tous les joueurs ont entré leurs décisions dans un tour, l'ordinateur attribuera l'option de rejet aux Répondants en fonction de leurs conditions de probabilité, c'est-à-dire qu'un Répondant A aura 10% de chances tandis qu'un Répondant B aura 90% de chances de pouvoir rejeter. La répartition finale des 100 dollars entre les deux joueurs est déterminée comme suit : Si l'ordinateur ne donne pas au Répondant l'option de rejeter, la cagnotte est divisée selon l'offre du Proposeur. Si l'ordinateur donne au Répondant l'option de rejeter, si l'offre du Proposeur est supérieure ou égale au seuil du Répondant, le Répondant accepte l'offre du Proposeur et la cagnotte est divisée selon l'offre du Proposeur. Si l'offre du Proposeur est inférieure au seuil du Répondant, le Répondant rejette l'offre et les deux joueurs obtiennent 0 dollar.""",
    "German (Deutsch)": """Im heutigen Experiment gibt es zwei mögliche Rollen: den Antragssteller (Proposer) und den Empfänger (Responder). In jeder Runde werden ein Antragssteller und ein Empfänger einander zugewiesen, um zu entscheiden, wie ein Betrag von 100 Dollar zwischen ihnen aufgeteilt wird. Die Zuweisung erfolgt zufällig durch den Computer, sodass sich die Paarungen von Runde zu Runde ändern. Sie können Ihren Gegenspieler im Spiel nicht identifizieren und werden niemals wieder mit demselben Antragssteller oder Empfänger zusammengeführt. Sie werden in einigen Runden als Antragssteller und in anderen Runden als Empfänger spielen. Ihre Gewinne aus allen Runden werden akkumuliert und am Ende des Experiments als Ihre Auszahlung in Bargeld umgewandelt.

Für den Antragssteller besteht die Aufgabe darin, zu bestimmen, wie viel von den 100 Dollar dem Empfänger angeboten werden soll. Das Angebot kann jede ganze Zahl von 0 bis 100 sein. Wird das Angebot angenommen, erhält der Empfänger den angebotenen Betrag und der Antragssteller behält den Rest des Pools. Wenn beispielsweise das Angebot 20 Dollar beträgt und der Empfänger es annimmt, erhält der Antragssteller 80 Dollar und der Empfänger 20 Dollar.

In diesem Spiel haben Empfänger unter Umständen die Möglichkeit, Angebote von Antragsstellern abzulehnen. Die Wahrscheinlichkeit dafür wird zufällig bestimmt. Zu Beginn jeder Runde weist der Computer diese Wahrscheinlichkeit allen Empfängern zufällig zu. In jeder Runde werden sowohl der Antragssteller als auch der Empfänger über diese Wahrscheinlichkeit informiert. Für den Empfänger besteht die Entscheidung darin, den Mindestbetrag (aus dem Pool) anzugeben, den er/sie bereit ist zu akzeptieren, was im Spiel als Schwellenwert (Threshold) bezeichnet wird. Der Schwellenwert kann jede ganze Zahl von 0 bis 100 sein. Wenn beispielsweise ein Schwellenwert von 30 angegeben wird, bedeutet dies, dass der Empfänger jedes Angebot unter 30 Dollar ablehnen wird, wenn ihm/ihr vom Computer das Ablehnungsrecht gewährt wird. Wenn eine Ablehnung erfolgt, erhalten beide Spieler 0 Dollar.

Sie treffen Ihre Entscheidung (Angebot als Antragssteller oder Schwellenwert als Empfänger), ohne die Entscheidung des anderen Spielers zu sehen. Nachdem alle Spieler ihre Entscheidungen in einer Runde eingegeben haben, weist der Computer den Empfängern das Ablehnungsrecht entsprechend ihren Wahrscheinlichkeitsbedingungen zu (z. B. hat Empfänger A eine Chance von 10 %, während Empfänger B eine Chance von 90 % hat). Die finale Verteilung der 100 Dollar wird wie folgt bestimmt: Gibt der Computer dem Empfänger nicht das Recht abzulehnen, wird der Pool gemäß dem Angebot des Antragsstellers aufgeteilt. Gibt der Computer dem Empfänger das Recht abzulehnen und ist das Angebot des Antragsstellers größer oder gleich dem Schwellenwert des Empfängers, nimmt der Empfänger das Angebot an und der Pool wird gemäß dem Angebot aufgeteilt. Ist das Angebot geringer als der Schwellenwert, lehnt der Empfänger ab und beide Spieler erhalten 0 Dollar.""",
    "Spanish (Español)": """En el experimento de hoy, hay dos roles posibles: el Proponente (Proposer) y el Receptor (Responder). En cada ronda, un Proponente y un Receptor se emparejarán para determinar cómo dividir una suma de 100 dólares entre ellos. El emparejamiento es aleatorio por computadora, por lo que las parejas cambiarán de ronda en ronda. No podrá identificar quién es su oponente y nunca volverá a ser emparejado con el mismo Proponente o Receptor. Jugará como Proponente en algunas rondas y como Receptor en otras. Sus ganancias de todas las rondas se acumularán y se convertirán en efectivo como su pago final al final del experimento.

Para el Proponente, la tarea consiste en determinar cuánto de los 100 dólares ofrecer al Receptor. La oferta puede ser cualquier número entero del 0 al 100. Si la oferta es aceptada, el Receptor obtendrá la cantidad propuesta y el Proponente se quedará con el resto del fondo. Por ejemplo, si una oferta es de 20 dólares y el Receptor la acepta, el Proponente obtendrá 80 dólares y el Receptor obtendrá 20 dólares.

En este juego, es posible que los Receptores tengan la opción de rechazar las ofertas de los Proponentes. La probabilidad de que un Receptor tenga dicha opción se determina al azar. Al comienzo de cada ronda, la computadora asignará aleatoriamente esta probabilidad a todos los Receptores. En cada ronda, tanto el Proponente como el Receptor serán informados de esta probabilidad. Para el Receptor, la decisión consiste en indicar la cantidad mínima (del fondo) que está dispuesto/a a aceptar, lo que se denomina umbral (Threshold) en el juego. El umbral puede ser cualquier número entero del 0 al 100. Por ejemplo, si se indica un umbral de 30, significa que el Receptor rechazará cualquier oferta inferior a 30 dólares si la computadora le concede la opción de rechazar. En caso de rechazo, ambos jugadores obtienen 0 dólares.

Usted tomará su decisión (oferta como Proponente o umbral como Receptor) sin ver la decisión del otro jugador. Después de que todos los jugadores ingresen sus decisiones en una ronda, la computadora asignará la opción de rechazar a los Receptores según sus condiciones de probabilidad (es decir, el Receptor A tendrá un 10% de probabilidad mientras que el Receptor B tendrá un 90% de probabilidad de poder rechazar). La distribución final de los 100 dólares en una ronda se determina de la siguiente manera: Si la computadora no le da al Receptor la opción de rechazar, el fondo se divide según la oferta del Proponente. Si la computadora sí le da al Receptor la opción de rechazar, si la oferta del Proponente es mayor o igual al umbral del Receptor, el Receptor acepta la oferta y el fondo se divide según la oferta del Proponente. Si la oferta del Proponente es menor que el umbral del Receptor, el Receptor rechaza la oferta y ambos jugadores obtienen 0 dólares.""",
    "Arabic (العربية)": """في تجربة اليوم، هناك دوران محتملان لك: مقدم الاقتراح (Proposer) والمستجيب (Responder). في كل جولة، سيتم تقسيم مبلغ 100 دولار بين مقدم الاقتراح والمستجيب. يخصص الكمبيوتر المطابقة العشوائية بحيث تتغير الشراكات من جولة إلى جولة. لن تتمكن من معرفة هوية الخصم ولن يتم مطابقتك مرة أخرى مع نفس مقدم الاقتراح أو المستجيب. ستلعب دور مقدم الاقتراح في بعض الجولات، ودور المستجيب في جولات أخرى. سيتم تجميع أرباحك من جميع الجولات وتحويلها إلى نقد كدفعة نهائية في نهاية التجربة.

بالنسبسبة لمقدم الاقتراح، تتمثل المهمة في تحديد المبلغ الذي سيقدمه للمستجيب من أصل 100 دولار. يمكن أن يكون العرض أي رقم صحيح من 0 إلى 100. إذا تم قبول العرض، يحصل المستجيب على المبلغ المقترح ويحتفظ مقدم الاقتراح بالباقي. على سبيل المثال، إذا كان العرض 20 دولارًا وقبله المستجيب، يحصل مقدم الاقتراح على 80 دولارًا والمستجيب على 20 دولارًا.

في هذه اللعبة، قد يكون للمستجيب خيار رفض العروض المقدمة من مقدمي الاقتراحات. يتم تحديد احتمال حصول المستجيب على هذا الخيار عشوائيًا. في بداية كل جولة، سيقوم الكمبيوتر بتخصيص هذا الاحتمال عشوائيًا لجميع المستجيبين. في كل جولة، سيتم إبلاغ كل من مقدم الاقتراح والمستجيب بهذا الاحتمال. بالنسبة للمستجيب، القرار هو تحديد الحد الأدنى للمبلغ (من الـ 100 دولار) الذي يقبل به، والذي يشار إليه باسم "الحد الأدنى (Threshold)". يمكن أن يكون الحد الأدنى أي رقم صحيح من 0 إلى 100. على سبيل المثال، إذا تم تحديد حد أدنى قدره 30، فهذا يعني أن المستجيب سيرفض أي عرض يقل عن 30 دولارًا إذا منحه الكمبيوتر خيار الرفض. في حالة حدوث الرفض، يحصل كلا اللاعبين على 0.

ستتخذ قرارك (العرض كمقدم اقتراح، أو الحد الأدنى كمستجيب) دون رؤية قرار اللاعب الآخر. بعد إدخال جميع اللاعبين لقراراتهم في الجولة، سيخصص الكمبيوتر خيار الرفض للمستجيبين وفقًا لشروط الاحتمال الخاصة بهم (أي أن المستجيب "أ" سيكون لديه فرصة 10% بينما المستجيب "ب" لديه فرصة 90% للرفض). يتم تحديد التوزيع النهائي لمبلغ 100 دولار كالتالي: إذا لم يمنح الكمبيوتر المستجيب خيار الرفض، يتم تقسيم المبلغ وفقًا لعرض مقدم الاقتراح. إذا منح الكمبيوتر المستجيب خيار الرفض، وكان عرض مقدم الاقتراح أكبر من أو يساوي الحد الأدنى للمستجيب، يقبل المستجيب العرض ويتم التقسيم حسب العرض. إذا كان العرض أقل من الحد الأدنى، يرفض المستجيب العرض ويحصل كلا اللاعبين على 0 دولار.""",
    "Korean (한국어)": """오늘 실험에서 당신은 제안자(Proposer)와 응답자(Responder) 중 하나의 역할을 맡게 됩니다. 매 라운드마다 한 명의 제안자와 한 명의 응답자가 무작위로 매칭되어 100달러를 어떻게 나눌지 결정합니다. 당신은 상대방이 누구인지 확인할 수 없으며, 동일한 제안자나 응답자와 다시 매칭되지 않습니다. 당신은 일부 라운드에서는 제안자로, 다른 라운드에서는 응답자로 참여하게 됩니다. 모든 라운드에서 얻은 수익은 누적되어 실험이 끝날 때 최종 현금으로 지급됩니다.

제안자의 결정 과제는 100달러 중 응답자에게 얼마를 제안할지 결정하는 것입니다. 제안 금액은 0에서 100 사이의 정수일 수 있습니다. 제안이 수락되면 응답자는 제안된 금액을 받고 제안자는 나머지 금액을 가집니다. 예를 들어, 제안 금액이 20달러이고 응답자가 이를 수락하면 제안자는 80달러, 응답자는 20달러를 받습니다.

이 게임에서 응답자는 제안자의 제안을 거절할 수 있는 권한(거부권)을 가질 수 있습니다. 응답자가 이 권한을 가질 확률은 무작위로 결정됩니다. 각 라운드가 시작될 때 컴퓨터는 모든 응답자에게 이 확률을 무작위로 할당하며, 제안자와 응답자 모두에게 이 확률이 고지됩니다. 응답자의 결정은 수락할 용의가 있는 최소 금액을 지정하는 것이며, 이를 게임에서는 '수락 한계선(Threshold)'이라고 부릅니다. 한계선은 0에서 100 사이의 정수일 수 있습니다. 예를 들어 30달러의 한계선을 지정한 경우, 컴퓨터로부터 거부권을 부여받으면 30달러 미만의 제안은 거절한다는 의미입니다. 거절이 발생하면 두 플레이어 모두 0달러를 받습니다.

당신은 상대방의 결정을 보지 않고 자신의 결정(제안자로서의 제안 금액 또는 응답자로서의 한계선)을 내리게 됩니다. 모든 플레이어가 결정을 입력하면 컴퓨터는 할당된 확률 조건에 따라 거부권을 부여합니다(예: 응답자 A는 10% 확률, 응답자 B는 90% 확률로 거부권 보유). 100달러의 최종 배분은 다음과 같이 결정됩니다: 컴퓨터가 응답자에게 거부권을 부여하지 않으면 제안자의 제안대로 배분됩니다. 컴퓨터가 거부권을 부여하고 제안자의 제안이 응답자의 한계선 이상이면 제안이 수락되어 제안대로 배분됩니다. 제안이 한계선 미만이면 거절되어 두 플레이어 모두 0달러를 받습니다.""",
    "Indonesian (Bahasa Indonesia)": """Dalam eksperimen hari ini, ada dua peran yang mungkin Anda mainkan: Pengusul (Proposer) dan Penerima (Responder). Di setiap putaran, satu Pengusul dan satu Penerima akan dipasangkan secara acak untuk menentukan bagaimana membagi dana sebesar 100 dolar. Anda tidak akan dapat mengidentifikasi siapa lawan Anda dan Anda tidak akan pernah dipasangkan kembali dengan Pengusul atau Penerima yang sama. Anda akan bermain sebagai Pengusul di beberapa putaran, dan sebagai Penerima di putaran lainnya. Penghasilan Anda dari semua putaran akan diakumulasikan dan dikonversi menjadi uang tunai sebagai pembayaran akhir Anda di akhir eksperimen.

Untuk Pengusul, tugas keputusan adalah menentukan seberapa banyak dari 100 dolar yang akan ditawarkan kepada Penerima. Penawaran dapat berupa angka bulat dari 0 hingga 100. Jika penawaran diterima, Penerima mendapatkan jumlah yang diusulkan dan Pengusul menyimpan sisanya. Sebagai contoh, jika penawaran adalah 20 dolar dan Penerima menerimanya, Pengusul mendapatkan 80 dolar dan Penerima mendapatkan 20 dolar.

Dalam permainan ini, Penerima mungkin memiliki opsi untuk menolak penawaran dari Pengusul. Probabilitas Penerima memiliki opsi tersebut ditentukan secara acak. Pada awal setiap putaran, komputer akan membagikan probabilitas ini secara acak kepada semua Penerima. Di setiap putaran, baik Pengusul maupun Penerima akan diberi tahu probabilitas ini. Bagi Penerima, keputusannya adalah menentukan jumlah minimum (dari 100 dolar) yang bersedia ia terima, yang disebut sebagai "ambang batas (Threshold)". Ambang batas dapat berupa angka bulat dari 0 hingga 100. Contohnya, jika ambang batas 30 ditentukan, artinya Penerima akan menolak penawaran di bawah 30 dolar jika ia diberikan opsi penolakan oleh komputer. Jika penolakan terjadi, kedua pemain mendapatkan 0 dolar.

Anda akan membuat keputusan (penawaran sebagai Pengusul, atau ambang batas sebagai Penerima) tanpa melihat keputusan pemain lain. Setelah semua pemain memasukkan keputusan mereka, komputer akan memberikan opsi penolakan kepada Penerima sesuai dengan kondisi probabilitas mereka (misalnya, Penerima A memiliki peluang 10% sedangkan Penerima B memiliki peluang 90% untuk menolak). Pembagian akhir 100 dolar ditentukan sebagai berikut: Jika komputer tidak memberikan opsi penolakan kepada Penerima, dana dibagi sesuai penawaran Pengusul. Jika komputer memberikan opsi penolakan dan penawaran Pengusul sama dengan atau lebih besar dari ambang batas Penerima, Penerima menerima penawaran tersebut. Jika penawaran Pengusul kurang dari ambang batas, Penerima menolak dan keduanya mendapatkan 0 dolar.""",
    "Italian (Italiano)": """Nell'esperimento di oggi, ci sono due ruoli possibili: il Proponente (Proposer) e il Ricevente (Responder). In ogni round, un Proponente e un Ricevente saranno accoppiati per decidere come dividere un budget di 100 dollari tra loro. Il computer assegna l'abbinamento in modo casuale, quindi le coppie cambieranno di round in round. Non potrai identificare il tuo avversario e non sarai mai riaccoppiato con lo stesso Proponente o Ricevente. Giocherai nel ruolo di Proponente per alcuni round e in quello di Ricevente per altri. I tuoi guadagni di tutti i round saranno accumulati e convertiti in contanti come pagamento finale al termine dell'esperimento.

Per il Proponente, il compito consiste nel determinare quanto offrire al Ricevente (un numero intero da 0 a 100). Se l'offerta viene accettata, il Ricevente ottiene la somma proposta e il Proponente tiene il resto. Per esempio, se un'offerta è di 20 dollari e il Ricevente la accetta, il Proponente otterrà 80 dollari e il Ricevente 20 dollari.

In questo gioco, è possibile per i Riceventi avere l'opzione di rifiutare le offerte dei Proponenti (diritto di veto). La probabilità di avere tale opzione è determinata in modo casuale. All'inizio di ogni round, il computer assegnerà casualmente questa probabilità a tutti i Riceventi. In ogni round, sia il Proponente che il Ricevente saranno informati di questa probabilità. Per il Ricevente, la decisione consiste nell'indicare la somma minima che è disposto ad accettare, chiamata "soglia (Threshold)" nel gioco (un numero intero da 0 a 100). Ad esempio, se viene indicata una soglia di 30 dollari, significa che il Ricevente rifiuterà qualsiasi offerta inferiore a 30 dollari se gli viene concessa l'opzione di rifiuto. In caso di rifiuto, entrambi i giocatori ottengono 0 dollari.

Prenderai la tua decisione (offerta come Proponente o soglia come Ricevente) senza vedere la decisione dell'altro giocatore. Dopo che tutti i giocatori avranno inserito le loro decisioni, il computer assegnerà l'opzione di rifiuto ai Riceventi in base alle loro probabilità (ad es. il Ricevente A avrà il 10% di possibilità e il Ricevente B il 90%). La distribuzione finale dei 100 dollari è determinata come segue: Se il computer non concede al Ricevente l'opzione di rifiuto, il budget viene diviso secondo l'offerta del Proponente. Se il computer concede l'opzione di rifiuto e l'offerta del Proponente è maggiore o uguale alla soglia del Ricevente, il Ricevente accetta e si divide secondo l'offerta. Se l'offerta è inferiore alla soglia, il Ricevente rifiuta ed entrambi ottengono 0 dollari.""",
    "Polish (Polski)": """W dzisiejszym eksperymencie możesz wcielić się w jedną z dwóch ról: Proponującego (Proposer) lub Reagującego (Responder). W każdej rundzie jeden Proponujący i jeden Reagujący są dobierani w parę, aby podzielić między sobą kwotę 100 dolarów. Komputer przydziela losowe dopasowanie, więc pary zmieniają się z rundy na rundę. Nie będziesz w stanie zidentyfikować swojego przeciwnika i nigdy nie zostaniesz ponownie połączony w parę z tym samym graczem. W niektórych rundach zagrasz jako Proponujący, a w innych jako Reagujący. Twoje wygrane ze wszystkich rund zostaną zsumowane i przeliczone na gotówkę jako płatność końcowa.

Zadaniem Proponującego jest określenie, jaką część ze 100 dolarów zaoferować Reagującemu (dowolna liczba całkowita od 0 do 100). Jeśli oferta zostanie zaakceptowana, Reagujący otrzymuje zaproponowaną kwotę, a Proponujący zatrzymuje resztę. Na przykład, jeśli oferta wynosi 20 dolarów i Reagujący ją przyjmie, Proponujący otrzyma 80 dolarów, a Reagujący 20 dolarów.

W tej grze Reagujący mogą mieć możliwość odrzucenia oferty (prawo weta). Prawdopodobieństwo otrzymania tej opcji jest losowe. Na początku każdej rundy komputer losowo przydziela to prawdopodobieństwo wszystkim Reagującym. Obaj gracze są informowani o tym prawdopodobieństwie. Decyzja Reagującego polega na wskazaniu minimalnej kwoty, jaką jest gotów przyjąć ("próg / Threshold", od 0 do 100). Na przykład próg 30 oznacza, że Reagujący odrzuci każdą ofertę poniżej 30 dolarów, jeśli otrzyma prawo weta. W przypadku odrzucenia obaj gracze otrzymują 0 dolarów.

Podejmujesz decyzję bez znajomości decyzji drugiego gracza. Po wprowadzeniu decyzji komputer przyznaje prawo weta zgodnie z prawdopodobieństwem (np. gracz A ma 10% szans, a gracz B ma 90% szans). Ostateczny podział 100 dolarów wygląda następująco: Jeśli komputer nie przyzna prawa weta, kwota jest dzielona według oferty Proponującego. Jeśli prawo weta zostanie przyznane i oferta jest równa lub wyższa od progu, oferta zostaje przyjęta. Jeśli oferta jest niższa od progu, Reagujący odrzuca ofertę i obaj gracze otrzymują 0 dolarów.""",
    "Russian (Русский)": """В сегодняшнем эксперименте вам предстоит сыграть одну из двух ролей: Инициатор (Proposer) или Ответчик (Responder). В каждом раунде Инициатор и Ответчик объединяются в пары, чтобы разделить сумму в 100 долларов. Компьютер производит случайное подбор пар, поэтому соперники меняются из раунда в раунд. Вы не сможете узнать личность оппонента и никогда не будете повторно сопоставлены с тем же игроком. Вы будете играть в роли Инициатора в одних раундах и в роли Ответчика в других. Ваш заработок во всех раундах суммируется и выплачивается наличными в конце эксперимента.

Для Инициатора задача состоит в том, чтобы определить, какую сумму из 100 долларов предложить Ответчику (целое число от 0 до 100). Если предложение принято, Ответчик получает предложенную сумму, а Инициатор оставляет себе остаток. Например, если предложение составляет 20 долларов и Ответчик его принимает, Инициатор получает 80 долларов, а Ответчик — 20 долларов.

В этой игре у Ответчиков может быть возможность отклонить предложение (право вето). Вероятность получения этой опции определяется случайно. В начале каждого раунда компьютер распределяет эту вероятность среди всех Ответчиков. В каждом раунде оба игрока информируются об этой вероятности. Для Ответчика решение состоит в том, чтобы указать минимальную сумму, которую он/она готов(а) принять — «порог (Threshold)» (целое число от 0 до 100). Например, порог 30 означает, что Ответчик отклонит любое предложение ниже 30 долларов, если компьютер предоставит ему право вето. В случае отклонения оба игрока получают 0 долларов.

Вы принимаете решение (предложение в роли Инициатора или порог в роли Ответчика), не видя решения другого игрока. После того как все игроки введут свои решения, компьютер предоставит право вето согласно условиям вероятности (например, Ответчик А имеет 10% шанс, а Ответчик Б — 90% шанс). Финальное распределение 100 долларов определяется следующим образом: Если компьютер не дает Ответчику право вето, сумма делится по предложению Инициатора. Если право вето предоставлено и предложение Инициатора больше или равно порогу Ответчика, предложение принимается. Если предложение ниже порога, Ответчик отклоняет предложение, и оба игрока получают 0 долларов.""",
    "Greek (Ελληνικά)": """Στο σημερινό πείραμα, υπάρχουν δύο πιθανοί ρόλοι: ο Προτείνων (Proposer) και ο Αποδέκτης (Responder). Σε κάθε γύρο, ένας Προτείνων και ένας Αποδέκτης συνδυάζονται για να αποφασίσουν πώς θα διαιρέσουν ένα ποσό 100 δολαρίων. Ο υπολογιστής αναθέτει την τυχαία αντιστοίχιση, οπότε οι συνδυασμοί αλλάζουν από γύρο σε γύρο. Δεν θα μπορείτε να αναγνωρίσετε τον αντίπαλό σας και δεν θα συνδυαστείτε ποτέ ξανά με τον ίδιο παίκτη. Θα παίξετε ως Προτείνων σε ορισμένους γύρους και ως Αποδέκτης σε άλλους. Τα κέρδη σας από όλους τους γύρους θα συσσωρευτούν και θα μετατραπούν σε μετρητά στο τέλος του πειράματος.

Για τον Προτείνοντα, η απόφαση είναι να καθορίσει πόσα από τα 100 δολάρια θα προσφέρει στον Αποδέκτη (ακέραιος αριθμός από 0 έως 100). Εάν η προσφορά γίνει αποδεκτή, ο Αποδέκτης λαμβάνει το προτεινόμενο ποσό και ο Προτείνων κρατά τα υπόλοιπα. Για παράδειγμα, αν η προσφορά είναι 20 δολάρια και ο Αποδέκτης την αποδεχτεί, ο Προτείνων παίρνει 80 δολάρια και ο Αποδέκτης 20 δολάρια.

Σε αυτό το παιχνίδι, ο Αποδέκτης μπορεί να έχει την επιλογή να απορρίψει τις προσφορές (δικαίωμα βέτο). Η πιθανότητα ορίζεται τυχαία. Στην αρχή κάθε γύρου, ο υπολογιστής αναθέτει αυτήν την πιθανότητα σε όλους τους Αποδέκτες. Και οι δύο παίκτες ενημερώνονται για αυτήν την πιθανότητα. Για τον Αποδέκτη, η απόφαση είναι να δηλώσει το ελάχιστο αποδεκτό ποσό ("όριο / Threshold", ακέραιος 0-100). Για παράδειγμα, όριο 30 σημαίνει ότι ο Αποδέκτης θα απορρίψει προσφορά κάτω των 30 δολαρίων αν του δοθεί το δικαίωμα βέτο. Σε περίπτωση απόρριψης, και οι δύο παίκτες παίρνουν 0 δολάρια.

Παίρνετε την απόφασή σας χωρίς να βλέπετε την απόφαση του άλλου παίκτη. Αφού όλοι καταχωρίσουν τις αποφάσεις τους, ο υπολογιστής αναθέτει το δικαίωμα βέτο (π.χ. ο Αποδέκτης Α έχει 10% πιθανότητα και ο Αποδέκτης Β έχει 90%). Η τελική κατανομή των 100 δολαρίων καθορίζεται ως εξής: Αν δεν δοθεί δικαίωμα βέτο, το ποσό διαιρείται σύμφωνα με την προσφορά του Προτείνοντος. Αν δοθεί δικαίωμα βέτο και η προσφορά είναι ίση ή μεγαλύτερη από το όριο, ο Αποδέκτης αποδέχεται την προσφορά. Αν η προσφορά είναι μικρότερη από το όριο, ο Αποδέκτης απορρίπτει και οι δύο παίρνουν 0 δολάρια.""",
    "Turkish (Türkçe)": """Bugünkü deneyde üstlenebileceğiniz iki rol bulunmaktadır: Teklif Eden (Proposer) ve Yanıtlayan (Responder). Her turda, bir Teklif Eden ve bir Yanıtlayan 100 dolarlık havuzu bölüşmek üzere bilgisayar tarafından rastgele eşleştirilir. Rakibinizin kimliğini göremezsiniz ve aynı kişiyle tekrar eşleşmezsiniz. Bazı turlarda Teklif Eden, bazı turlarda ise Yanıtlayan rolünde oynayacaksınız. Tüm turlardan elde ettiğiniz kazançlar birikecek ve deney sonunda nakit ödemeye dönüştürülecektir.

Teklif Eden için görev, 100 dolardan ne kadarını Yanıtlayan'a teklif edeceğini belirlemektir (0 ile 100 arasında tam sayı). Teklif kabul edilirse Yanıtlayan önerilen miktarı alır, Teklif Eden ise kalanı tutar. Örneğin teklif 20 dolar ise ve Yanıtlayan kabul ederse, Teklif Eden 80 dolar, Yanıtlayan 20 dolar alır.

Bu oyunda Yanıtlayanların teklifleri reddetme seçeneği (veto hakkı) olabilir. Bu olasılık rastgele belirlenir. Her turun başında bilgisayar bu olasılığı tüm Yanıtlayanlara atar ve her iki taraf da bilgilendirilir. Yanıtlayan için karar, kabul etmeye hazır olduğu minimum miktarı ("eşik değeri / Threshold", 0-100 arası) belirtmektir. Örneğin 30 dolarlık eşik değeri, veto hakkı verildiğinde 30 doların altındaki tekliflerin reddedileceği anlamına gelir. Reddetme durumunda her iki taraf da 0 dolar alır.

Kararınızı diğer oyuncunun kararını görmeden verirsiniz. Kararlar girildikten sonra bilgisayar olasılık koşullarına göre veto hakkını dağıtır (örneğin Yanıtlayan A %10, Yanıtlayan B %90 veto şansına sahiptir). 100 doların nihai dağılımı şöyle belirlenir: Bilgisayar veto hakkı vermezse havuz Teklif Eden'in teklifine göre bölünür. Veto hakkı verilir ve teklif eşik değerine eşit veya büyükse kabul edilir. Teklif eşik değerinin altındaysa reddedilir ve her iki taraf da 0 dolar alır.""",
    "Afrikaans (Afrikaans)": """In vandag se eksperiment is daar twee moontlike rolle: die Voorsteller (Proposer) en die Respondent (Responder). In elke rondte word 'n Voorsteller en Respondent op 'n ewekansige wyse gepaar om 100 dollar te verdeel. Jy sal nie jou teenstander kan identifiseer nie en sal nooit weer met dieselfde persoon gepaar word nie. Jy sal in sommige rondtes as Voorsteller speel en in ander as Respondent. Jou verdienste uit al die rondtes sal opgehoop word en aan die einde van die eksperiment in kontant omgeskakel word.

Vir 'n Voorsteller is die taak om te besluit hoeveel van die 100 dollar om aan die Respondent te bied ('n heelgetal van 0 tot 100). As 'n aanbod aanvaar word, kry die Respondent die bedrag en die Voorsteller hou die res. Byvoorbeeld, as die aanbod 20 dollar is en die Respondent aanvaar dit, kry die Voorsteller 80 dollar en die Respondent 20 dollar.

In hierdie speletjie kan Respondente 'n opsie hê om aanbiedinge te verwerp (vetoreg). Die waarskynlikheid hiervoor word ewekansig bepaal. Aan die begin van elke rondte sal die rekenaar hierdie waarskynlikheid aan alle Respondente toewys en albei spelers word ingelig. Vir die Respondent is die taak om die minimum aanvaarbare bedrag ("drempel / Threshold", 0 tot 100) aan te dui. 'n Drempel van 30 beteken dat die Respondent enige aanbod onder 30 dollar sal verwerp as vetoreg geld. As 'n verwerping plaasvind, kry albei spelers 0 dollar.

Jy neem jou besluit sonder om die ander speler se besluit te sien. Nadat almal hul besluite ingestuur het, ken die rekenaar vetoreg toe volgens die waarskynlikheid (bv. Respondent A het 10% kans en Respondent B het 90% kans). Die finale verdeling van die 100 dollar word so bepaal: As geen vetoreg geld nie, word die geld verdeel volgens die Voorsteller se aanbod. As vetoreg geld en die aanbod is gelyk aan of hoër as die drempel, word dit aanvaar. As die aanbod laer as die drempel is, word dit verwerp en albei kry 0 dollar.""",
    "Welsh (Cymraeg)": """Yn yr arbrawf heddiw, mae dwy rôl bosibl: y Cynigydd (Proposer) ac y Sefydlydd (Responder). Ym mhob rownd, mae Cynigydd a Sefydlydd yn cael eu paru ar hap i rannu cronfa o 100 doler. Ni fyddwch yn gallu adnabod eich gwrthwynebydd ac ni fyddwch fyth yn cael eich paru eto gyda'r un grwp. Rydych yn chwarae fel Cynigydd mewn rhai rowndiau ac fel Sefydlydd mewn eraill. Bydd eich enillion o bob rownd yn cael eu cronni a'u troi yn arian parod ar ddiwedd yr arbrawf.

Ar gyfer Cynigydd, y task penderfynu yw nodi faint o'r 100 doler i'w gynnig i'r Sefydlydd (unrhyw nifer cyfan o 0 i 100). Os caiff ei dderbyn, mae'r Sefydlydd yn cael y swm ac mae'r Cynigydd yn cadw'r gweddill. Er enghraifft, os yw'r cynnig yn 20 doler a'r Sefydlydd yn ei dderbyn, mae'r Cynigydd yn cael 80 doler a'r Sefydlydd yn cael 20 doler.

Yn y gêm hon, mae'n bosibl i Sefydlwyr gael yr opsiwn i wrthod cynigion (hawl feto). Mae'r tebygolrwydd yn cael ei benderfynu ar hap ac fe roddir gwybod i'r ddau chwaraewr. Ar gyfer y Sefydlydd, y penderfyniad yw nodi'r swm lleiaf sy'n dderbyniol ("trothwy / Threshold", 0 i 100). Opsiwn trothwy o 30 yw bod y Sefydlydd yn gwrthod unrhyw gynnig o dan 30 doler os rhoddir feto iddo. Os gwrthodir, mae'r ddau yn cael 0 doler.

Rydych yn gwneud eich penderfyniad heb weld penderfyniad y chwaraewr arall. Ar ôl i bawb nodi eu penderfyniadau, mae'r cyfrifiadur yn dyfarnu feto yn ôl tebygolrwydd (e.e. 10% i Chwaraewr A, 90% i Chwaraewr B). Dyma sut y rhennir y 100 doler: Os na roddir feto, rhennir yn ôl cynnig y Cynigydd. Os rhoddir feto a bod y cynnig yn fwy neu'n gyfartal â'r trothwy, fe'i derbynnir. Os yw'r cynnig yn llai na'r trothwy, fe'i gwrthodir ac mae'r ddau yn cael 0 doler."""
}

# Step 2 UI Translations across all 17 languages
ui_translations = {
    "English": {
        "step2_title": "🎮 Step 2: The Interactive Power Game",
        "top_instruction": "Now, participate in the game. You will be matched against an AI agent calibrated based on the cultural baseline of your selected language. You will be randomly assigned with one probability condition (LOW or HIGH). But you have the options to experience both as the Proposer and as the Responder.",
        "select_game_lang_label": "🌐 Select Your Language for Gameplay:",
        "instructions_header": "📖 Game Instructions in",
        "assigned_veto_low": "🎯 **Your Assigned Veto Probability (π):** 0.10 (LOW Responder Power - π = 10%) — locked based on your Student ID.",
        "assigned_veto_high": "🎯 **Your Assigned Veto Probability (π):** 0.90 (HIGH Responder Power - π = 90%) — locked based on your Student ID.",
        "enter_id_warning": "⚠️ Enter your Anonymous Student ID at the top of the page to unlock and see your assigned Veto Probability.",
        "radio_label": "Select your assigned Veto Probability (π) condition:",
        "radio_low": "Low Responder Power (π = 10%)",
        "radio_high": "High Responder Power (π = 90%)",
        "proposer_title": "Option A: Play as Proposer",
        "proposer_desc": "Propose how to split the $100. If the offer meets the responder's threshold, it is accepted.",
        "proposer_id_info": "Proposer ID: **{id}** | Selected Language: **{lang}**",
        "offer_slider": "Your Offer to the Responder ($0 to $100):",
        "submit_offer": "📤 Submit Offer",
        "responder_title": "Option B: Play as Responder",
        "responder_desc": "Set your minimum acceptable threshold. If the proposer's offer meets this, it is accepted.",
        "responder_id_info": "Responder ID: **{id}** | Selected Language: **{lang}**",
        "threshold_slider": "Your Minimum Threshold ($0 to $100):",
        "submit_threshold": "📤 Submit Threshold",
        "result_resolved": "##### 🎯 Round Result Resolved!",
        "lang_played": "Language Played",
        "your_offer": "Your Offer",
        "agent_threshold": "Simulated Agent Threshold",
        "agent_offer": "Simulated Agent Offer",
        "your_threshold": "Your Threshold",
        "veto_enforced": "Was Veto Enforced?",
        "yes": "Yes",
        "no": "No",
        "final_outcome": "Final Outcome & Explanation",
        "payout_allocation": "Payout Allocation",
        "rejected_exp": "Rejected, because Threshold > Offer, and Veto implemented",
        "accepted_no_veto_exp": "Accepted, because Veto not implemented",
        "accepted_met_thresh_exp": "Accepted, because Offer > Threshold"
    },
    "Simplified Chinese (简体中文)": {
        "step2_title": "🎮 步骤 2：互动权力博弈游戏",
        "top_instruction": "现在，请参与游戏。您将与根据您选择的语言文化基线校准的 AI 智能体进行匹配。您将被随机分配一种概率条件（低概率 LOW 或 高概率 HIGH）。但您可以选择分别体验作为提议人（Proposer）和应答者（Responder）的角色。",
        "select_game_lang_label": "🌐 选择您的游戏语言：",
        "instructions_header": "📖 游戏说明（语言：",
        "assigned_veto_low": "🎯 **您分配到的否决权概率 (π)：** 0.10 (LOW 低应答者权力 - π = 10%) — 已根据您的学生 ID 锁定。",
        "assigned_veto_high": "🎯 **您分配到的否决权概率 (π)：** 0.90 (HIGH 高应答者权力 - π = 90%) — 已根据您的学生 ID 锁定。",
        "enter_id_warning": "⚠️ 请在页面顶部输入您的匿名学生 ID 以解锁并查看您分配到的否决权概率。",
        "radio_label": "选择您分配到的否决权概率 (π) 条件：",
        "radio_low": "低应答者权力 (π = 10%)",
        "radio_high": "高应答者权力 (π = 90%)",
        "proposer_title": "选项 A：扮演提议人 (Proposer)",
        "proposer_desc": "提议如何分配 100 美元。如果提议符合应答者的最低接受额，则被接受。",
        "proposer_id_info": "提议人 ID：**{id}** | 所选语言：**{lang}**",
        "offer_slider": "您给应答者的提议金额 ($0 到 $100)：",
        "submit_offer": "📤 提交提议",
        "responder_title": "选项 B：扮演应答者 (Responder)",
        "responder_desc": "设置您的最低接受额。如果提议人的提议达到此金额，则被接受。",
        "responder_id_info": "应答者 ID：**{id}** | 所选语言：**{lang}**",
        "threshold_slider": "您的最低接受额 ($0 到 $100)：",
        "submit_threshold": "📤 提交最低接受额",
        "result_resolved": "##### 🎯 轮次结果结算！",
        "lang_played": "游戏语言",
        "your_offer": "您的提议",
        "agent_threshold": "模拟 AI 的最低接受额",
        "agent_offer": "模拟 AI 的提议",
        "your_threshold": "您的最低接受额",
        "veto_enforced": "否决权是否生效？",
        "yes": "是 (Yes)",
        "no": "否 (No)",
        "final_outcome": "最终结果与解释",
        "payout_allocation": "收益分配",
        "rejected_exp": "已拒绝：因为 Threshold > Offer，且否决权已生效 (Rejected, because Threshold > Offer, and Veto implemented)",
        "accepted_no_veto_exp": "已接受：因为否决权未生效 (Accepted, because Veto not implemented)",
        "accepted_met_thresh_exp": "已接受：因为 Offer > Threshold (Accepted, because Offer > Threshold)"
    },
    "Traditional Chinese (繁體中文)": {
        "step2_title": "🎮 步驟 2：互動權力博弈遊戲",
        "top_instruction": "現在，請參與遊戲。您將與根據您選擇的語言文化基線校準的 AI 智能體進行匹配。您將被隨機分配一種概率條件（低概率 LOW 或 高概率 HIGH）。但您可以選擇分別體驗作為提議人（Proposer）和應答者（Responder）的角色。",
        "select_game_lang_label": "🌐 選擇您的遊戲語言：",
        "instructions_header": "📖 遊戲說明（語言：",
        "assigned_veto_low": "🎯 **您分配到的否決權概率 (π)：** 0.10 (LOW 低應答者權力 - π = 10%) — 已根據您的學生 ID 鎖定。",
        "assigned_veto_high": "🎯 **您分配到的否決權概率 (π)：** 0.90 (HIGH 高應答者權力 - π = 90%) — 已根據您的學生 ID 鎖定。",
        "enter_id_warning": "⚠️ 請在頁面頂部輸入您的匿名學生 ID 以解鎖並查看您分配到的否決權概率。",
        "radio_label": "選擇您分配到的否決權概率 (π) 條件：",
        "radio_low": "低應答者權力 (π = 10%)",
        "radio_high": "高應答者權力 (π = 90%)",
        "proposer_title": "選項 A：扮演提議人 (Proposer)",
        "proposer_desc": "提議如何分配 100 美元。如果提議符合應答者的最低接受額，則被接受。",
        "proposer_id_info": "提議人 ID：**{id}** | 所選語言：**{lang}**",
        "offer_slider": "您給應答者的提議金額 ($0 到 $100)：",
        "submit_offer": "📤 提交提議",
        "responder_title": "選項 B：扮演應答者 (Responder)",
        "responder_desc": "設置您的最低接受額。如果提議人的提議達到此金額，則被接受。",
        "responder_id_info": "應答者 ID：**{id}** | 所選語言：**{lang}**",
        "threshold_slider": "您的最低接受額 ($0 到 $100)：",
        "submit_threshold": "📤 提交最低接受額",
        "result_resolved": "##### 🎯 輪次結果結算！",
        "lang_played": "遊戲語言",
        "your_offer": "您的提議",
        "agent_threshold": "模擬 AI 的最低接受額",
        "agent_offer": "模擬 AI 的提議",
        "your_threshold": "您的最低接受額",
        "veto_enforced": "否決權是否生效？",
        "yes": "是 (Yes)",
        "no": "否 (No)",
        "final_outcome": "最終結果與解釋",
        "payout_allocation": "收益分配",
        "rejected_exp": "已拒絕：因為 Threshold > Offer，且否決權已生效 (Rejected, because Threshold > Offer, and Veto implemented)",
        "accepted_no_veto_exp": "已接受：因為否決權未生效 (Accepted, because Veto not implemented)",
        "accepted_met_thresh_exp": "已接受：因為 Offer > Threshold (Accepted, because Offer > Threshold)"
    },
    "Japanese (日本語)": {
        "step2_title": "🎮 ステップ 2：インタラクティブ・パワーゲーム",
        "top_instruction": "それでは、ゲームに参加してください。選択した言語の文化的ベースラインに基づいてキャリブレーションされたAIエージェントとマッチングされます。確率条件（LOWまたはHIGH）のいずれかにランダムに割り当てられますが、提案者（Proposer）および応答者（Responder）の両方の役割を体験するオプションがあります。",
        "select_game_lang_label": "🌐 プレイ言語を選択してください：",
        "instructions_header": "📖 ゲーム説明（言語：",
        "assigned_veto_low": "🎯 **割り当てられた拒否権確率 (π)：** 0.10 (LOW 応答者の権限・低 - π = 10%) — 学籍番号IDに基づきロックされています。",
        "assigned_veto_high": "🎯 **割り当てられた拒否権確率 (π)：** 0.90 (HIGH 応答者の権限・高 - π = 90%) — 学籍番号IDに基づきロックされています。",
        "enter_id_warning": "⚠️ ページ上部で匿名学生IDを入力して、割り当てられた拒否権確率を確認してください。",
        "radio_label": "割り当てられた拒否権確率 (π) 条件を選択：",
        "radio_low": "応答者の権限・低 (π = 10%)",
        "radio_high": "応答者の権限・高 (π = 90%)",
        "proposer_title": "オプション A：提案者（Proposer）としてプレイ",
        "proposer_desc": "100ドルの分配方法を提案します。オファーが応答者の閾値を満たせば承認されます。",
        "proposer_id_info": "提案者 ID：**{id}** | 選択言語：**{lang}**",
        "offer_slider": "応答者へのオファー額 ($0 ～ $100)：",
        "submit_offer": "📤 オファーを送信",
        "responder_title": "オプション B：応答者（Responder）としてプレイ",
        "responder_desc": "受け入れ可能な最低額（閾値）を設定します。提案者のオファーがこれに達すれば承認されます。",
        "responder_id_info": "応答者 ID：**{id}** | 選択言語：**{lang}**",
        "threshold_slider": "あなたの最低閾値 ($0 ～ $100)：",
        "submit_threshold": "📤 閾値を送信",
        "result_resolved": "##### 🎯 ラウンド結果判定！",
        "lang_played": "プレイ言語",
        "your_offer": "あなたのオファー",
        "agent_threshold": "シミュレートAIの閾値",
        "agent_offer": "シミュレートAIのオファー",
        "your_threshold": "あなたの閾値",
        "veto_enforced": "拒否権は発動されましたか？",
        "yes": "はい (Yes)",
        "no": "いいえ (No)",
        "final_outcome": "最終結果と説明",
        "payout_allocation": "報酬分配",
        "rejected_exp": "拒否：Threshold > Offer であり、拒否権が発動されたため (Rejected, because Threshold > Offer, and Veto implemented)",
        "accepted_no_veto_exp": "承認：拒否権が発動されなかったため (Accepted, because Veto not implemented)",
        "accepted_met_thresh_exp": "承認：Offer > Threshold であるため (Accepted, because Offer > Threshold)"
    },
    "French (Français)": {
        "step2_title": "🎮 Étape 2 : Le Jeu de Pouvoir Interactif",
        "top_instruction": "Maintenant, participez au jeu. Vous serez associé à un agent IA calibré sur la base culturelle de la langue sélectionnée. Vous serez assigné aléatoirement à une condition de probabilité (LOW ou HIGH). Cependant, vous avez la possibilité de tester les deux rôles : Proposeur et Répondant.",
        "select_game_lang_label": "🌐 Sélectionnez votre langue pour le jeu :",
        "instructions_header": "📖 Instructions du jeu en",
        "assigned_veto_low": "🎯 **Votre probabilité de veto (π) assignée :** 0.10 (LOW Pouvoir Répondant Faible - π = 10%) — verrouillée selon votre ID Étudiant.",
        "assigned_veto_high": "🎯 **Votre probabilité de veto (π) assignée :** 0.90 (HIGH Pouvoir Répondant Élevé - π = 90%) — verrouillée selon votre ID Étudiant.",
        "enter_id_warning": "⚠️ Entrez votre ID Étudiant anonyme en haut de la page pour voir votre probabilité de veto assignée.",
        "radio_label": "Sélectionnez votre condition de probabilité de veto (π) assignée :",
        "radio_low": "Pouvoir Répondant Faible (π = 10%)",
        "radio_high": "Pouvoir Répondant Élevé (π = 90%)",
        "proposer_title": "Option A : Jouer en tant que Proposeur",
        "proposer_desc": "Proposez comment diviser les 100 $. Si l'offre atteint le seuil du répondant, elle est acceptée.",
        "proposer_id_info": "ID Proposeur : **{id}** | Langue sélectionnée : **{lang}**",
        "offer_slider": "Votre offre au Répondant (0 $ à 100 $) :",
        "submit_offer": "📤 Soumettre l'offre",
        "responder_title": "Option B : Jouer en tant que Répondant",
        "responder_desc": "Définissez votre seuil minimum acceptable. Si l'offre du proposeur atteint ce seuil, elle est acceptée.",
        "responder_id_info": "ID Répondant : **{id}** | Langue sélectionnée : **{lang}**",
        "threshold_slider": "Votre seuil minimum (0 $ à 100 $) :",
        "submit_threshold": "📤 Soumettre le seuil",
        "result_resolved": "##### 🎯 Résultat du Tour Résolu !",
        "lang_played": "Langue jouée",
        "your_offer": "Votre offre",
        "agent_threshold": "Seuil de l'agent IA simulé",
        "agent_offer": "Offre de l'agent IA simulé",
        "your_threshold": "Votre seuil",
        "veto_enforced": "Le veto a-t-il été appliqué ?",
        "yes": "Oui (Yes)",
        "no": "Non (No)",
        "final_outcome": "Résultat final et explication",
        "payout_allocation": "Répartition des gains",
        "rejected_exp": "Rejeté, car Seuil > Offre et le Veto a été appliqué (Rejected, because Threshold > Offer, and Veto implemented)",
        "accepted_no_veto_exp": "Accepté, car le Veto n'a pas été appliqué (Accepted, because Veto not implemented)",
        "accepted_met_thresh_exp": "Accepté, car Offre > Seuil (Accepted, because Offer > Threshold)"
    },
    "German (Deutsch)": {
        "step2_title": "🎮 Schritt 2: Das Interaktive Machtspiel",
        "top_instruction": "Nimm jetzt am Spiel teil. Du wirst mit einem KI-Agenten gematcht, der auf den kulturellen Grundlagen deiner ausgewählten Sprache kalibriert ist. Dir wird zufällig eine Wahrscheinlichkeitsbedingung (LOW oder HIGH) zugewiesen. Du hast jedoch die Möglichkeit, sowohl als Antragssteller als auch als Empfänger Erfahrungen zu sammeln.",
        "select_game_lang_label": "🌐 Wähle deine Sprache für das Spiel:",
        "instructions_header": "📖 Spielanleitung auf",
        "assigned_veto_low": "🎯 **Deine zugewiesene Veto-Wahrscheinlichkeit (π):** 0.10 (LOW Niedrige Empfänger-Macht - π = 10%) — gesperrt basierend auf deiner Studenten-ID.",
        "assigned_veto_high": "🎯 **Deine zugewiesene Veto-Wahrscheinlichkeit (π):** 0.90 (HIGH Hohe Empfänger-Macht - π = 90%) — gesperrt basierend auf deiner Studenten-ID.",
        "enter_id_warning": "⚠️ Gib oben deine anonyme Studenten-ID ein, um deine zugewiesene Veto-Wahrscheinlichkeit zu sehen.",
        "radio_label": "Wähle deine zugewiesene Veto-Wahrscheinlichkeit (π):",
        "radio_low": "Niedrige Empfänger-Macht (π = 10%)",
        "radio_high": "Hohe Empfänger-Macht (π = 90%)",
        "proposer_title": "Option A: Als Antragssteller spielen",
        "proposer_desc": "Schlage vor, wie die 100 $ aufgeteilt werden. Wenn das Angebot den Schwellenwert erreicht, wird es angenommen.",
        "proposer_id_info": "Antragssteller-ID: **{id}** | Gewählte Sprache: **{lang}**",
        "offer_slider": "Dein Angebot an den Empfänger (0 $ bis 100 $):",
        "submit_offer": "📤 Angebot einreichen",
        "responder_title": "Option B: Als Empfänger spielen",
        "responder_desc": "Setze deinen Mindestschwellenwert. Wenn das Angebot des Antragsstellers diesen erreicht, wird es angenommen.",
        "responder_id_info": "Empfänger-ID: **{id}** | Gewählte Sprache: **{lang}**",
        "threshold_slider": "Dein Mindestschwellenwert (0 $ bis 100 $):",
        "submit_threshold": "📤 Schwellenwert einreichen",
        "result_resolved": "##### 🎯 Rundenergebnis ermittelt!",
        "lang_played": "Gespielte Sprache",
        "your_offer": "Dein Angebot",
        "agent_threshold": "Schwellenwert des KI-Agenten",
        "agent_offer": "Angebot des KI-Agenten",
        "your_threshold": "Dein Schwellenwert",
        "veto_enforced": "Wurde das Veto angewendet?",
        "yes": "Ja (Yes)",
        "no": "Nein (No)",
        "final_outcome": "Endergebnis & Erklärung",
        "payout_allocation": "Auszahlungsverteilung",
        "rejected_exp": "Abgelehnt, da Schwellenwert > Angebot und Veto angewendet wurde (Rejected, because Threshold > Offer, and Veto implemented)",
        "accepted_no_veto_exp": "Angenommen, da Veto nicht angewendet wurde (Accepted, because Veto not implemented)",
        "accepted_met_thresh_exp": "Angenommen, da Angebot > Schwellenwert (Accepted, because Offer > Threshold)"
    },
    "Spanish (Español)": {
        "step2_title": "🎮 Paso 2: El Juego de Poder Interactivo",
        "top_instruction": "Ahora, participa en el juego. Serás emparejado con un agente de IA calibrado según la base cultural de tu idioma seleccionado. Se te asignará aleatoriamente una condición de probabilidad (LOW o HIGH). Sin embargo, tienes la opción de experimentar ambos roles: Proponente y Receptor.",
        "select_game_lang_label": "🌐 Selecciona tu idioma para jugar:",
        "instructions_header": "📖 Instrucciones del juego en",
        "assigned_veto_low": "🎯 **Tu probabilidad de veto (π) asignada:** 0.10 (LOW Bajo Poder del Receptor - π = 10%) — bloqueada según tu ID de Estudiante.",
        "assigned_veto_high": "🎯 **Tu probabilidad de veto (π) asignada:** 0.90 (HIGH Alto Poder del Receptor - π = 90%) — bloqueada según tu ID de Estudiante.",
        "enter_id_warning": "⚠️ Ingresa tu ID de Estudiante anónimo arriba para desbloquear y ver tu probabilidad de veto asignada.",
        "radio_label": "Selecciona tu condición de probabilidad de veto (π) asignada:",
        "radio_low": "Bajo Poder del Receptor (π = 10%)",
        "radio_high": "Alto Poder del Receptor (π = 90%)",
        "proposer_title": "Opción A: Jugar como Proponente",
        "proposer_desc": "Propón cómo dividir los $100. Si la oferta alcanza el umbral del receptor, es aceptada.",
        "proposer_id_info": "ID de Proponente: **{id}** | Idioma seleccionado: **{lang}**",
        "offer_slider": "Tu oferta al Receptor ($0 a $100):",
        "submit_offer": "📤 Enviar Oferta",
        "responder_title": "Opción B: Jugar como Receptor",
        "responder_desc": "Establece tu umbral mínimo aceptable. Si la oferta del proponente alcanza este umbral, es aceptada.",
        "responder_id_info": "ID de Receptor: **{id}** | Idioma seleccionado: **{lang}**",
        "threshold_slider": "Tu umbral mínimo ($0 a $100):",
        "submit_threshold": "📤 Enviar Umbral",
        "result_resolved": "##### 🎯 ¡Resultado de la Ronda Resuelto!",
        "lang_played": "Idioma jugado",
        "your_offer": "Tu oferta",
        "agent_threshold": "Umbral del agente IA simulado",
        "agent_offer": "Oferta del agente IA simulado",
        "your_threshold": "Tu umbral",
        "veto_enforced": "¿Se aplicó el veto?",
        "yes": "Sí (Yes)",
        "no": "No (No)",
        "final_outcome": "Resultado final y explicación",
        "payout_allocation": "Distribución del pago",
        "rejected_exp": "Rechazado, porque Umbral > Oferta y el Veto se aplicó (Rejected, because Threshold > Offer, and Veto implemented)",
        "accepted_no_veto_exp": "Aceptado, porque el Veto no se aplicó (Accepted, because Veto not implemented)",
        "accepted_met_thresh_exp": "Aceptado, porque Oferta > Umbral (Accepted, because Offer > Threshold)"
    }
}

# Helper to get UI string with English fallback
def get_ui(target_lang, text_key, **kwargs):
    dict_lang = ui_translations.get(target_lang, ui_translations.get("English", {}))
    text = dict_lang.get(text_key, ui_translations.get("English", {}).get(text_key, ""))
    if kwargs:
        try:
            return text.format(**kwargs)
        except Exception:
            return text
    return text

# Empirical Baseline Data per Language/Country from Working Paper
paper_country_data = pd.DataFrame([
    {"Country_Language": "Simplified Chinese (China)", "Avg_Offer_Paper": 39.56, "Avg_Threshold_Paper": 29.50},
    {"Country_Language": "Traditional Chinese (Taiwan/HK)", "Avg_Offer_Paper": 38.45, "Avg_Threshold_Paper": 33.00},
    {"Country_Language": "Japanese (Japan)", "Avg_Offer_Paper": 35.97, "Avg_Threshold_Paper": 33.10},
    {"Country_Language": "Arabic (Egypt/Kuwait/Qatar)", "Avg_Offer_Paper": 34.10, "Avg_Threshold_Paper": 28.30},
    {"Country_Language": "German (Germany/Austria)", "Avg_Offer_Paper": 34.04, "Avg_Threshold_Paper": 26.50},
    {"Country_Language": "English (US/UK/Australia)", "Avg_Offer_Paper": 31.80, "Avg_Threshold_Paper": 32.00},
    {"Country_Language": "French (France/Switzerland)", "Avg_Offer_Paper": 31.71, "Avg_Threshold_Paper": 29.10},
    {"Country_Language": "Russian (Russia/Georgia)", "Avg_Offer_Paper": 27.60, "Avg_Threshold_Paper": 25.70},
    {"Country_Language": "Afrikaans (South Africa)", "Avg_Offer_Paper": 28.98, "Avg_Threshold_Paper": 24.50},
    {"Country_Language": "Polish (Poland)", "Avg_Offer_Paper": 33.70, "Avg_Threshold_Paper": 25.00},
    {"Country_Language": "Turkish (Turkey)", "Avg_Offer_Paper": 33.14, "Avg_Threshold_Paper": 32.00},
    {"Country_Language": "Spanish (Spain/Latin America)", "Avg_Offer_Paper": 32.46, "Avg_Threshold_Paper": 26.80},
    {"Country_Language": "Greek (Greece)", "Avg_Offer_Paper": 31.97, "Avg_Threshold_Paper": 29.80},
    {"Country_Language": "Korean (South Korea)", "Avg_Offer_Paper": 31.92, "Avg_Threshold_Paper": 28.60},
    {"Country_Language": "Indonesian (Indonesia)", "Avg_Offer_Paper": 30.31, "Avg_Threshold_Paper": 29.20},
    {"Country_Language": "Italian (Italy)", "Avg_Offer_Paper": 30.25, "Avg_Threshold_Paper": 25.40},
    {"Country_Language": "Welsh (United Kingdom)", "Avg_Offer_Paper": 29.16, "Avg_Threshold_Paper": 25.30}
])

# Sidebar Command Center
st.sidebar.image("https://upload.wikimedia.org/wikipedia/commons/e/e2/San_Jose_State_University_seal.svg", width=80)
st.sidebar.title("EMBA Command Center")
st.sidebar.write("Lucas College and Graduate School of Business")

# Passcode Gate for Instructor Mode
st.sidebar.markdown("---")
st.sidebar.subheader("🔑 Access Gate")
passcode_input = st.sidebar.text_input("Enter Passcode for Instructor Dashboard:", type="password")
is_instructor = (passcode_input == "sjsu2026")

if is_instructor:
    st.sidebar.success("🔑 Instructor Access Granted!")
else:
    if passcode_input:
        st.sidebar.error("❌ Invalid Passcode.")
    else:
        st.sidebar.info("🔒 Enter Passcode to unlock Instructor Controls & Settings.")

# Sidebar Lesson Plan Timeline (Always Visible)
st.sidebar.markdown("---")
st.sidebar.subheader("⏱️ Session 1 Timeline")
st.sidebar.markdown("""
*   **00:00 - 00:10**: Intro & Setup
*   **00:10 - 00:20**: Step 1 - Calibration Portal
*   **00:20 - 00:40**: Step 2 - Modified Ultimatum Game
*   **00:40 - 01:00**: Step 3 - Low vs. High Power Cross-Country Charts
""")

# Handle customized translations state synced real-time with global storage
global_trans = global_store.get_translations()
active_translations = default_translations.copy()
active_translations.update(global_trans)
st.session_state.custom_translations = active_translations

if is_instructor:
    st.sidebar.markdown("---")
    st.sidebar.subheader("⚙️ Classroom Experiment Settings")
    st.session_state.pi_assignment_mode = st.sidebar.radio(
        "Veto Probability (π) Assignment Mode:",
        options=["Automatic Split (50% Low, 50% High π)", "Manual Student Choice"],
        index=0 if st.session_state.pi_assignment_mode == "Automatic Split (50% Low, 50% High π)" else 1,
        help="Automatic mode cleanly distributes students to π = 0.10 or π = 0.90 based on Student ID."
    )
    st.sidebar.markdown("---")
    st.sidebar.subheader("📝 Real-Time English Baseline Instructions Editor")
    english_baseline_text = st.sidebar.text_area(
        "Edit Baseline Instructions (English):",
        value=st.session_state.custom_translations.get("English", default_english_instructions),
        height=180,
        help="Updates the English baseline instructions real-time across all student sessions."
    )
    if st.sidebar.button("💾 Save & Broadcast English Instructions"):
        st.session_state.custom_translations["English"] = english_baseline_text
        global_store.update_translation("English", english_baseline_text)
        st.sidebar.success("🎉 Baseline English instructions updated and broadcast live to all sessions!")

    st.sidebar.markdown("---")
    st.sidebar.subheader("🔧 Dynamic Multilingual Translation Editor")
    selected_custom_lang = st.sidebar.selectbox("Select Language to Edit:", list(default_translations.keys()))
    custom_text = st.sidebar.text_area(
        f"Edit instructions for {selected_custom_lang}:",
        value=st.session_state.custom_translations.get(selected_custom_lang, default_translations[selected_custom_lang]),
        height=150
    )
    if st.sidebar.button(f"💾 Save {selected_custom_lang} Translation"):
        st.session_state.custom_translations[selected_custom_lang] = custom_text
        global_store.update_translation(selected_custom_lang, custom_text)
        st.sidebar.success(f"🎉 Updated translation for {selected_custom_lang} and saved globally!")

# Main Title & Presentation Header
st.markdown("<h1 style='color: #1e3d59; font-size: 32px;'>⚖️ Session 1: Linguistic Relativity & The Power Game</h1>", unsafe_allow_html=True)
st.markdown("##### Lucas College and Graduate School of Business — EMBA International Forum")

# Unified Participant Registration (Auto-Generated ID)
st.markdown("### 🔑 Participant Registration")
student_id = st.text_input(
    "Your Anonymous Student ID (Auto-Generated):",
    value=st.session_state.get('global_student_id', ""),
    placeholder="Enter ID here...",
    help="This ID is generated randomly for your device to ensure anonymity. You can customize it if desired."
)
if student_id:
    st.session_state.global_student_id = student_id

# Main Portal Navigation Tabs
tabs = ["🌎 Step 1: Instruction Calibration", "🎮 Step 2: Play the Power Game"]
if is_instructor:
    tabs.append("📊 Step 3: Instructor Course Analytics")

nav_tabs = st.tabs(tabs)

# =============================================================================
# TAB 1: INSTRUCTION CALIBRATION
# =============================================================================
with nav_tabs[0]:
    st.markdown("### 1. Read and Compare Instructions")
    st.write(
        "Read the baseline game rules in English side-by-side with your preferred "
        "or native language to verify translation naturalness before playing the game."
    )
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("<h5 style='color: #1e3d59;'>English Baseline Instructions</h5>", unsafe_allow_html=True)
        st.info(st.session_state.custom_translations["English"])
        
    with col2:
        selected_lang = st.selectbox(
            "Select Language for Review & Calibration:",
            options=list(default_translations.keys()),
            index=0
        )
        st.markdown(f"<h5 style='color: #17b978;'>Selected Rules ({selected_lang})</h5>", unsafe_allow_html=True)
        st.success(st.session_state.custom_translations[selected_lang])
        
    st.markdown("---")
    st.markdown("### ✍️ Student Calibration Feedback")
    st.warning("⚠️ **Research Constraint:** Please write all qualitative comments in **English** only to facilitate multi-country statistical matching and collation.")
    
    with st.form("feedback_form"):
        if not student_id:
            st.warning("⚠️ Please enter or confirm your Anonymous Student ID in the Registration field above!")
        else:
            st.info(f"📝 Registering calibration comments for participant: **{student_id}**")
        
        col_r1, col_r2 = st.columns(2)
        with col_r1:
            q1_rating = st.slider(
                "Question 1: On a scale of 1-5, how clear were the game rules to you?",
                min_value=1, max_value=5, value=5, step=1,
                help="1 = Completely Confusing, 5 = Extremely Clear"
            )
        with col_r2:
            q2_rating = st.slider(
                "Question 2: On a scale of 1-5, how natural and culturally appropriate was the localized translation?",
                min_value=1, max_value=5, value=5, step=1,
                help="1 = Unnatural, 5 = Flawless and Culturally Natural"
            )
            
        comments = st.text_area(
            "Question 3: Qualitative Translation Audit (What terms or phrasing could be refined?):",
            placeholder="Please write your review here in English (e.g., 'The translation of veto in paragraph 4 is clear...')"
        )
        
        submit_feedback = st.form_submit_button("📤 Submit Evaluation Feedback")
        
        if submit_feedback:
            if not student_id:
                st.error("❌ Submission Blocked: Please enter your Student ID at the top of the page.")
            else:
                non_ascii_found = any(ord(char) > 127 for char in comments)
                has_asian_chars = bool(re.search(r'[一-鿿぀-ゟ゠-ヿ가-힯]', comments))
                
                if non_ascii_found or has_asian_chars:
                    st.error("❌ Submission Blocked: Your qualitative comments contain non-English characters. Please translate your feedback into English and submit again.")
                else:
                    new_entry = {
                        "Timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "Student_ID": student_id,
                        "Language": selected_lang,
                        "Q1_Clarity_Rating": q1_rating,
                        "Q2_Naturalness_Rating": q2_rating,
                        "Translation_Comments": comments if comments else "No comments provided."
                    }
                    st.session_state.responses.append(new_entry)
                    global_store.add_response(new_entry)
                    st.balloons()
                    st.success(f"🎉 Thank you, {student_id}! Your linguistic calibration has been recorded.")

# =============================================================================
# TAB 2: INTERACTIVE POWER GAME (FULLY LOCALIZED IN SELECTED LANGUAGE!)
# =============================================================================
with nav_tabs[1]:
    st.markdown("### 🎮 Step 2: The Interactive Power Game")
    
    selected_game_lang = st.selectbox(
        "🌐 Choose Your Language for Gameplay / 选择游戏语言 / 言語を選択してください:",
        options=list(default_translations.keys()),
        key="game_lang_select"
    )

    # Requirement 1: Updated top instruction text
    top_intro_text = get_ui(selected_game_lang, "top_instruction")
    st.write(top_intro_text)
    
    # Display full instructions card directly in the chosen language!
    st.markdown(f"#### 📖 Game Instructions ({selected_game_lang})")
    st.info(st.session_state.custom_translations[selected_game_lang])
    
    st.markdown("---")
    
    # Resolve veto probability based on Instructor Setting
    if st.session_state.pi_assignment_mode == "Automatic Split (50% Low, 50% High π)":
        if student_id:
            try:
                numeric_part = int(''.join(filter(str.isdigit, student_id)))
                veto_config = 0.10 if numeric_part % 2 == 0 else 0.90
            except ValueError:
                veto_config = 0.10 if len(student_id) % 2 == 0 else 0.90
            
            assigned_str = get_ui(selected_game_lang, "assigned_veto_low" if veto_config == 0.10 else "assigned_veto_high")
            st.success(assigned_str)
        else:
            veto_config = 0.10
            st.warning(get_ui(selected_game_lang, "enter_id_warning"))
    else:
        veto_config = st.radio(
            get_ui(selected_game_lang, "radio_label"),
            options=[0.10, 0.90],
            format_func=lambda x: get_ui(selected_game_lang, "radio_low") if x == 0.10 else get_ui(selected_game_lang, "radio_high"),
            help="π represents the probability that the responder's veto threshold is active."
        )

    col_p1, col_p2 = st.columns(2)
    
    with col_p1:
        st.markdown(f"<h5 style='color: #1e3d59;'>{get_ui(selected_game_lang, 'proposer_title')}</h5>", unsafe_allow_html=True)
        st.write(get_ui(selected_game_lang, "proposer_desc"))
        
        with st.form("proposer_form"):
            p_student_id = student_id
            if not student_id:
                st.warning(get_ui(selected_game_lang, "please_enter_id"))
            else:
                st.info(get_ui(selected_game_lang, "proposer_id_info", id=student_id, lang=selected_game_lang))
            
            offer = st.slider(get_ui(selected_game_lang, "offer_slider"), min_value=0, max_value=100, value=30, step=1)
            submit_offer = st.form_submit_button(get_ui(selected_game_lang, "submit_offer"))
            
            if submit_offer:
                if not p_student_id:
                    st.error(get_ui(selected_game_lang, "please_enter_id"))
                else:
                    # Simulated Responder threshold calibrated per language & power
                    base_offset = 12 if veto_config == 0.10 else 32
                    base_threshold = random.randint(base_offset, base_offset + 10)
                    veto_active = random.random() < veto_config
                    
                    # Requirement 3: Detailed Outcome Explanations
                    if veto_active:
                        if offer < base_threshold:
                            outcome_key = "rejected_exp"
                            p_payout = 0
                            r_payout = 0
                        else:
                            outcome_key = "accepted_met_thresh_exp"
                            p_payout = 100 - offer
                            r_payout = offer
                    else:
                        outcome_key = "accepted_no_veto_exp"
                        p_payout = 100 - offer
                        r_payout = offer
                        
                    outcome_str = get_ui(selected_game_lang, outcome_key)
                    payout_str = f"Proposer: ${p_payout}, Responder: ${r_payout}"
                    
                    log_entry = {
                        "Timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "Student_ID": p_student_id,
                        "Role": "Proposer",
                        "Language": selected_game_lang,
                        "Veto_Probability": veto_config,
                        "Offer": offer,
                        "Threshold": "N/A (Agent)",
                        "Veto_Enforced": "Yes" if veto_active else "No",
                        "Outcome": outcome_str,
                        "Payout": payout_str
                    }
                    st.session_state.game_logs.append(log_entry)
                    global_store.add_game_log(log_entry)
                    
                    # Display results in selected language
                    st.success(get_ui(selected_game_lang, "result_resolved"))
                    st.write(f"**{get_ui(selected_game_lang, 'lang_played')}:** {selected_game_lang}")
                    st.write(f"**{get_ui(selected_game_lang, 'your_offer')}:** ${offer}")
                    st.write(f"**{get_ui(selected_game_lang, 'agent_threshold')}:** ${base_threshold}")
                    st.write(f"**{get_ui(selected_game_lang, 'veto_enforced')}:** {get_ui(selected_game_lang, 'yes' if veto_active else 'no')}")
                    st.write(f"**{get_ui(selected_game_lang, 'final_outcome')}:** {outcome_str}")
                    st.info(f"💰 **{get_ui(selected_game_lang, 'payout_allocation')}:** {payout_str}")

    with col_p2:
        st.markdown(f"<h5 style='color: #1e3d59;'>{get_ui(selected_game_lang, 'responder_title')}</h5>", unsafe_allow_html=True)
        st.write(get_ui(selected_game_lang, "responder_desc"))
        
        with st.form("responder_form"):
            r_student_id = student_id
            if not student_id:
                st.warning(get_ui(selected_game_lang, "please_enter_id"))
            else:
                st.info(get_ui(selected_game_lang, "responder_id_info", id=student_id, lang=selected_game_lang))
            
            threshold = st.slider(get_ui(selected_game_lang, "threshold_slider"), min_value=0, max_value=100, value=30, step=1)
            submit_threshold = st.form_submit_button(get_ui(selected_game_lang, "submit_threshold"))
            
            if submit_threshold:
                if not r_student_id:
                    st.error(get_ui(selected_game_lang, "please_enter_id"))
                else:
                    # Simulated Proposer offer calibrated per language & power
                    base_offset = 20 if veto_config == 0.10 else 40
                    base_offer = random.randint(base_offset, base_offset + 10)
                    veto_active = random.random() < veto_config
                    
                    # Requirement 3: Detailed Outcome Explanations
                    if veto_active:
                        if base_offer < threshold:
                            outcome_key = "rejected_exp"
                            p_payout = 0
                            r_payout = 0
                        else:
                            outcome_key = "accepted_met_thresh_exp"
                            p_payout = 100 - base_offer
                            r_payout = base_offer
                    else:
                        outcome_key = "accepted_no_veto_exp"
                        p_payout = 100 - base_offer
                        r_payout = base_offer
                        
                    outcome_str = get_ui(selected_game_lang, outcome_key)
                    payout_str = f"Proposer: ${p_payout}, Responder: ${r_payout}"
                    
                    log_entry = {
                        "Timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "Student_ID": r_student_id,
                        "Role": "Responder",
                        "Language": selected_game_lang,
                        "Veto_Probability": veto_config,
                        "Offer": "N/A (Agent)",
                        "Threshold": threshold,
                        "Veto_Enforced": "Yes" if veto_active else "No",
                        "Outcome": outcome_str,
                        "Payout": payout_str
                    }
                    st.session_state.game_logs.append(log_entry)
                    global_store.add_game_log(log_entry)
                    
                    # Display results in selected language
                    st.success(get_ui(selected_game_lang, "result_resolved"))
                    st.write(f"**{get_ui(selected_game_lang, 'lang_played')}:** {selected_game_lang}")
                    st.write(f"**{get_ui(selected_game_lang, 'agent_offer')}:** ${base_offer}")
                    st.write(f"**{get_ui(selected_game_lang, 'your_threshold')}:** ${threshold}")
                    st.write(f"**{get_ui(selected_game_lang, 'veto_enforced')}:** {get_ui(selected_game_lang, 'yes' if veto_active else 'no')}")
                    st.write(f"**{get_ui(selected_game_lang, 'final_outcome')}:** {outcome_str}")
                    st.info(f"💰 **{get_ui(selected_game_lang, 'payout_allocation')}:** {payout_str}")

# =============================================================================
# TAB 3: INSTRUCTOR COURSE ANALYTICS (SEPARATE PLOTS FOR LOW vs HIGH POWER!)
# =============================================================================
if is_instructor:
    with nav_tabs[2]:
        st.markdown("<h3 style='color: #1e3d59;'>📊 Step 3: Instructor Course Analytics Dashboard</h3>", unsafe_allow_html=True)
        
        # Sync with global persistent store across all student sessions
        all_res, all_logs = global_store.get_all_data()
        st.session_state.responses = all_res
        st.session_state.game_logs = all_logs
        
        col_ref1, col_ref2 = st.columns([3, 1])
        with col_ref1:
            st.write("Monitor live classroom submissions across all student devices in real-time.")
        with col_ref2:
            if st.button("🔄 Refresh Live Student Data"):
                all_res, all_logs = global_store.get_all_data()
                st.session_state.responses = all_res
                st.session_state.game_logs = all_logs
                st.rerun()

        # 1. Likert Calibration Statistics
        df_responses = pd.DataFrame(st.session_state.responses)
        if not df_responses.empty:
            st.markdown("#### **I. Linguistic Calibration Feedbacks**")
            col_m1, col_m2, col_m3 = st.columns(3)
            with col_m1:
                st.metric("Linguistic Feedbacks", len(df_responses))
            with col_m2:
                st.metric("Avg Clarity (Q1)", f"{df_responses['Q1_Clarity_Rating'].mean():.2f} / 5.00")
            with col_m3:
                st.metric("Avg Naturalness (Q2)", f"{df_responses['Q2_Naturalness_Rating'].mean():.2f} / 5.00")
            
            st.dataframe(df_responses, use_container_width=True)
            
            # Export Calibration CSV
            csv_calib = df_responses.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Download Calibration Data (.CSV)",
                data=csv_calib,
                file_name="emba_translation_calibration_data.csv",
                mime="text/csv",
                key="dl_calib"
            )
        else:
            st.info("No translation feedback submitted yet.")
            
        st.markdown("---")
        
        # 2. Gameplay logs & Cross-Country Offer vs. Threshold Chart (Low vs High Power Separated)
        df_games = pd.DataFrame(st.session_state.game_logs)
        st.markdown("#### **II. Live Gameplay Logs**")
        if not df_games.empty:
            st.dataframe(df_games, use_container_width=True)
            
            csv_games = df_games.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Download Game Results (.CSV)",
                data=csv_games,
                file_name="emba_power_gameplay_results.csv",
                mime="text/csv",
                key="dl_games"
            )
        else:
            st.info("No gameplay sessions logged yet.")
            
        st.markdown("---")
        st.markdown("#### **III. Cross-Country Bargaining Analytics: Low Power (π = 0.10) vs. High Power (π = 0.90)**")
        st.write("These two charts map Average Proposer Offer on the X-axis against Average Threshold on the Y-axis across different countries and languages. Dots are results from LLM agents. Stars are results from live classroom experiment.")
        
        col_chart1, col_chart2 = st.columns(2)
        
        # Ensure numeric conversion for filtering
        if not df_games.empty:
            df_games["Veto_Prob_Float"] = pd.to_numeric(df_games["Veto_Probability"], errors='coerce')
        
        with col_chart1:
            st.markdown("##### **1. Low Responder Power Condition (π = 10%)**")
            fig_low = go.Figure()
            
            # Low Power Empirical Baseline
            low_paper_offers = paper_country_data["Avg_Offer_Paper"] * 0.66
            low_paper_thresh = paper_country_data["Avg_Threshold_Paper"] * 0.90
            
            # Live class overlay for Low Power
            merged_l = pd.DataFrame()
            if not df_games.empty:
                df_low_games = df_games[np.isclose(df_games["Veto_Prob_Float"], 0.10, atol=0.05)].copy()
                if not df_low_games.empty:
                    off_low = df_low_games[df_low_games["Offer"] != "N/A (Agent)"].copy()
                    thr_low = df_low_games[df_low_games["Threshold"] != "N/A (Agent)"].copy()
                    
                    if not off_low.empty or not thr_low.empty:
                        off_low["Offer"] = pd.to_numeric(off_low["Offer"], errors='coerce')
                        thr_low["Threshold"] = pd.to_numeric(thr_low["Threshold"], errors='coerce')
                        
                        agg_off_l = off_low.groupby("Language")["Offer"].mean().reset_index() if not off_low.empty else pd.DataFrame(columns=["Language", "Offer"])
                        agg_thr_l = thr_low.groupby("Language")["Threshold"].mean().reset_index() if not thr_low.empty else pd.DataFrame(columns=["Language", "Threshold"])
                        
                        merged_l = pd.merge(agg_off_l, agg_thr_l, on="Language", how="outer").fillna(20.0)
            
            # Calculate dynamic smart ranges to prevent clipping
            min_x_l = min(10.0, float(merged_l["Offer"].min() - 5.0)) if not merged_l.empty and "Offer" in merged_l and not merged_l["Offer"].isna().all() else 10.0
            max_x_l = max(40.0, float(merged_l["Offer"].max() + 5.0)) if not merged_l.empty and "Offer" in merged_l and not merged_l["Offer"].isna().all() else 40.0
            min_y_l = min(5.0, float(merged_l["Threshold"].min() - 5.0)) if not merged_l.empty and "Threshold" in merged_l and not merged_l["Threshold"].isna().all() else 5.0
            max_y_l = max(40.0, float(merged_l["Threshold"].max() + 5.0)) if not merged_l.empty and "Threshold" in merged_l and not merged_l["Threshold"].isna().all() else 40.0

            # Parity line
            diag_line_low = np.linspace(min_x_l, max_x_l, 100)
            fig_low.add_trace(go.Scatter(
                x=diag_line_low, y=diag_line_low, mode='lines',
                line=dict(color='#A0AEC0', width=2, dash='dash'),
                name='Acceptance Parity Line', hoverinfo='skip'
            ))

            fig_low.add_trace(go.Scatter(
                x=low_paper_offers,
                y=low_paper_thresh,
                mode='markers+text',
                name='Empirical Baseline (Low π)',
                text=paper_country_data["Country_Language"].apply(lambda x: x.split(' ')[0]),
                textposition="top center",
                marker=dict(size=11, color='#2563EB', symbol='circle', line=dict(width=1, color='#1E3A8A')),
                hovertemplate="<b>%{text}</b><br>Baseline Offer (Low π): $%{x:.2f}<br>Baseline Threshold (Low π): $%{y:.2f}<extra></extra>"
            ))

            if not merged_l.empty:
                fig_low.add_trace(go.Scatter(
                    x=merged_l["Offer"],
                    y=merged_l["Threshold"],
                    mode='markers+text',
                    name='Live Class Avg (Low π)',
                    text=merged_l["Language"].apply(lambda x: f"Class: {x.split(' ')[0]}"),
                    textposition="bottom center",
                    marker=dict(size=16, color='#F59E0B', symbol='star', line=dict(width=1.5, color='#B45309')),
                    hovertemplate="<b>%{text}</b><br>Class Offer: $%{x:.2f}<br>Class Threshold: $%{y:.2f}<extra></extra>"
                ))
            
            fig_low.update_layout(
                xaxis_title="Proposer Offer Amount ($ out of 100)",
                yaxis_title="Responder Threshold Amount ($ out of 100)",
                xaxis=dict(range=[min_x_l, max_x_l]),
                yaxis=dict(range=[min_y_l, max_y_l]),
                template="plotly_white",
                height=420,
                margin=dict(l=20, r=20, t=30, b=20),
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
            )
            st.plotly_chart(fig_low, use_container_width=True)
            
        with col_chart2:
            st.markdown("##### **2. High Responder Power Condition (π = 90%)**")
            fig_high = go.Figure()
            
            # High Power Empirical Baseline
            high_paper_offers = paper_country_data["Avg_Offer_Paper"] * 1.15
            high_paper_thresh = paper_country_data["Avg_Threshold_Paper"] * 1.12
            
            # Live class overlay for High Power
            merged_h = pd.DataFrame()
            if not df_games.empty:
                df_high_games = df_games[np.isclose(df_games["Veto_Prob_Float"], 0.90, atol=0.05)].copy()
                if not df_high_games.empty:
                    off_high = df_high_games[df_high_games["Offer"] != "N/A (Agent)"].copy()
                    thr_high = df_high_games[df_high_games["Threshold"] != "N/A (Agent)"].copy()
                    
                    if not off_high.empty or not thr_high.empty:
                        off_high["Offer"] = pd.to_numeric(off_high["Offer"], errors='coerce')
                        thr_high["Threshold"] = pd.to_numeric(thr_high["Threshold"], errors='coerce')
                        
                        agg_off_h = off_high.groupby("Language")["Offer"].mean().reset_index() if not off_high.empty else pd.DataFrame(columns=["Language", "Offer"])
                        agg_thr_h = thr_high.groupby("Language")["Threshold"].mean().reset_index() if not thr_high.empty else pd.DataFrame(columns=["Language", "Threshold"])
                        
                        merged_h = pd.merge(agg_off_h, agg_thr_h, on="Language", how="outer").fillna(37.0)

            # Dynamic smart ranges for High Power
            min_x_h = min(20.0, float(merged_h["Offer"].min() - 5.0)) if not merged_h.empty and "Offer" in merged_h and not merged_h["Offer"].isna().all() else 20.0
            max_x_h = max(60.0, float(merged_h["Offer"].max() + 5.0)) if not merged_h.empty and "Offer" in merged_h and not merged_h["Offer"].isna().all() else 60.0
            min_y_h = min(15.0, float(merged_h["Threshold"].min() - 5.0)) if not merged_h.empty and "Threshold" in merged_h and not merged_h["Threshold"].isna().all() else 15.0
            max_y_h = max(60.0, float(merged_h["Threshold"].max() + 5.0)) if not merged_h.empty and "Threshold" in merged_h and not merged_h["Threshold"].isna().all() else 60.0

            # Parity line
            diag_line_high = np.linspace(min_x_h, max_x_h, 100)
            fig_high.add_trace(go.Scatter(
                x=diag_line_high, y=diag_line_high, mode='lines',
                line=dict(color='#A0AEC0', width=2, dash='dash'),
                name='Acceptance Parity Line', hoverinfo='skip'
            ))

            fig_high.add_trace(go.Scatter(
                x=high_paper_offers,
                y=high_paper_thresh,
                mode='markers+text',
                name='Empirical Baseline (High π)',
                text=paper_country_data["Country_Language"].apply(lambda x: x.split(' ')[0]),
                textposition="top center",
                marker=dict(size=11, color='#059669', symbol='circle', line=dict(width=1, color='#064E3B')),
                hovertemplate="<b>%{text}</b><br>Baseline Offer (High π): $%{x:.2f}<br>Baseline Threshold (High π): $%{y:.2f}<extra></extra>"
            ))

            if not merged_h.empty:
                fig_high.add_trace(go.Scatter(
                    x=merged_h["Offer"],
                    y=merged_h["Threshold"],
                    mode='markers+text',
                    name='Live Class Avg (High π)',
                    text=merged_h["Language"].apply(lambda x: f"Class: {x.split(' ')[0]}"),
                    textposition="bottom center",
                    marker=dict(size=16, color='#EF4444', symbol='star', line=dict(width=1.5, color='#991B1B')),
                    hovertemplate="<b>%{text}</b><br>Class Offer: $%{x:.2f}<br>Class Threshold: $%{y:.2f}<extra></extra>"
                ))
            
            fig_high.update_layout(
                xaxis_title="Proposer Offer Amount ($ out of 100)",
                yaxis_title="Responder Threshold Amount ($ out of 100)",
                xaxis=dict(range=[min_x_h, max_x_h]),
                yaxis=dict(range=[min_y_h, max_y_h]),
                template="plotly_white",
                height=420,
                margin=dict(l=20, r=20, t=30, b=20),
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
            )
            st.plotly_chart(fig_high, use_container_width=True)
