import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import random
import datetime
import re

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

if 'responses' not in st.session_state:
    st.session_state.responses = [
        {"Timestamp": "2026-09-01 14:02:15", "Student_ID": "EMBA_3842", "Language": "French (Français)", "Q1_Clarity_Rating": 5, "Q2_Naturalness_Rating": 4, "Translation_Comments": "The term 'cagnotte' is perfect for 'pool'. Very clear."}
    ]

if 'game_logs' not in st.session_state:
    st.session_state.game_logs = [
        {"Timestamp": "2026-09-01 14:05:00", "Student_ID": "EMBA_3842", "Role": "Proposer", "Language": "French (Français)", "Veto_Probability": 0.90, "Offer": 40, "Threshold": "N/A (Agent)", "Veto_Enforced": "Yes", "Outcome": "Accepted", "Payout": "Proposer: 60, Responder: 40"},
        {"Timestamp": "2026-09-01 14:06:00", "Student_ID": "EMBA_7195", "Role": "Responder", "Language": "Simplified Chinese (简体中文)", "Veto_Probability": 0.90, "Offer": "N/A (Agent)", "Threshold": 30, "Veto_Enforced": "Yes", "Outcome": "Accepted", "Payout": "Proposer: 60, Responder: 40"}
    ]

# Core English Instructions updated to the exact wording requested
default_english_instructions = """In today’s experiment, there are two possible roles for you to play: the Proposer and the Responder. In every round, one Proposer and one Responder will be paired to determine how to divide a pool of 100 dollars between them. The computer assigns the random matching so that pairings will change from round to round. You will not be able to identify who is your opponent in the game and you will never be re-matched with the same Proposer or Responder. You will play in the role of a Proposer for some rounds, and in the role of a Responder for other rounds. Your earnings from all rounds in the game will be accumulated and converted into cash as your final payment at the end of the experiment. For a Proposer, the decision task is to determine how much out of 100 dollars to offer to the Responder. The offer can be any integer number from 0 to 100. If an offer is accepted, the Responder will get the amount proposed and the Proposer will keep the rest of the pool. For example, if an offer is 20 dollars and the Responder accepts it, the Proposer will get 80 dollars and the Responder will get 20 dollars. In this game, it is possible for Responders to have an option to reject offers by Proposers. The probability for a Responder to have such an option is determined randomly. At the beginning of each round, the computer will randomly assign this probability to all Responders. In each round, both the Proposer and the Responder will be informed of this probability. For the Responder, the decision is to indicate the minimum amount (out of the pool) that he/she is willing to accept, which is referred as threshold in the game. The threshold can be any integer number from 0 to 100. For example, if a threshold of 30 is indicated, it means that the Responder will reject any offer below 30 dollars (out of the 100 dollars) if she/he is granted the option to reject by the computer. In case a rejection occurs, both players will get 0. You will make your decision (offer as the Proposer, or threshold as the Responder) without seeing the other player’s decision. After all players input their decisions in a round, the computer will allocate the option to reject to Responders according to their probability conditions i.e., a Responder A will have a 10% chance while a Responder B will have a 90% chance to be able to reject. The final distribution of the 100 dollars in a round between the two players is determined as follows: If the computer does not give the Responder the option to reject, the pool is divided according to the Proposer’s offer. If the computer does give the Responder the option to reject, if the offer by the Proposer is greater than or euqal to the threshold by the Responder, the Responder accepts the offer by the Proposer, and the pool is divided according to the Proposer’s offer. If the offer by the Proposer is less than the threshold by the Responder, the Responder rejects the offer, and both players get 0 dollars. This is the first round. You will act as the Proposer. The probability of the Responder to have the reject option is 0.9. Please decide how much you will offer to the Responder for the current round. Provide just a single number with no explanations."""

# Pre-loaded 17-language translations
default_translations = {
    "English": default_english_instructions,
    "Simplified Chinese (简体中文)": """在今天的实验中，您将扮演两种可能的角色：提议人（Proposer）和应答者（Responder）。在每一轮中，一名提议人和一名应答者将被配对，以决定如何分配100美元的资金池。电脑随机匹配，因此每轮的对手都会改变。您将无法识别游戏中的对手，也永远不会与同一个提议人或应答者再次配对。您将在某些轮次中扮演提议人，在其他轮次中扮演应答者。您在游戏中所有轮次的收益将被累积并在实验结束时兑换成现金作为您的最终报酬。\n\n对于提议人，决策任务是确定从100美元中分出多少给应答者。提议金额可以是0到100之间的任意整数。如果提议被接受，应答者将获得提议的金额，而提议人将保留资金池的其余部分。例如，如果提议是20美元且应答者接受，提议人将获得80美元，应答者将获得20美元。\n\n在这场游戏中，应答者有可能拥有拒绝提议人提议的权利。应答者获得该否决权的概率是随机决定的。在每一轮开始时，电脑将随机分配此概率给所有应答者。在每一轮中，提议人和应答者都会被告知这个概率。对于应答者，决策是指出他/她愿意接受的最低金额，这在游戏中被称为“最低接受额（Threshold）”。最低接受额可以是0到100之间的任意整数。例如，如果指定了30的最低接受额，这意味着如果电脑授予应答者拒绝的权利，应答者将拒绝任何低于30美元的提议。如果发生拒绝，两位玩家都将获得0美元。\n\n您将在看不到另一位玩家决策的情况下做出您的决策。在所有玩家在一轮中输入决策后，电脑将根据概率条件将拒绝权利分配给应答者。最终的100美元分配确定如下：如果电脑没有给予应答者拒绝的权利，则按照提议人的提议分配。如果电脑给予了拒绝权利，且提议大于或等于最低接受额，则应答者接受提议；如果提议低于最低接受额，则应答者拒绝，双方均获得0美元。这是第一轮。您将扮演提议人。应答者拥有拒绝权利的概率是0.9。请决定您在本轮将向应答者提议多少金额。仅提供单个数字，无需任何解释。""",
    "Traditional Chinese (繁體中文)": """在今天的實驗中，您將扮演兩種可能的角色：提議人（Proposer）和應答者（Responder）。在每一輪中，一名提議人和一名應答者將被配對，以決定如何分配100美元的資金池。電腦隨機匹配，因此每輪的對手都會改變。您將無法識別遊戲中的對手，也永遠不會與同一個提議人或應答者再次配對。您將在某些輪次中扮演提議人，在其他輪次中扮演應答者。\n\n對於提議人，決策任務是確定從100美元中分出多少給應答者。提議金額可以是0到100之間的任意整數。如果提議被接受，應答者將獲得提議的金額，而提議人將保留資金池的其餘部分。\n\n在這場遊戲中，應答者有可能擁有拒絕提議人提議的權利。應答者獲得該否決權的概率是隨機決定的。在每一輪開始時，電腦將隨機分配此概率給所有應答者。在每一輪中，提議人和應答者都會被告知這個概率。對於應答者，決策是指出他/她願意接受的最低金額，這在遊戲中被稱為“最低接受額（Threshold）”。最低接受額可以是0到100之間的任意整數。\n\n您將在看不到另一位玩家決策的情況下做出您的決策。在所有玩家在一輪中輸入決策後，電腦將根據概率條件將拒絕權利分配給應答者。最終分配確定如下：如果電腦沒有給予應答者拒絕權利，則按照提議人的提議分配。如果電腦給予了拒絕權利，且提議大於或等於最低接受額，則應答者接受提議；否則雙方均獲得0美元。這是第一輪。您將扮演提議人。應答者擁有拒絕權利的概率是0.9。請決定您在本輪將向應答者提議多少金額。僅提供單個數字，無需任何解釋。""",
    "Japanese (日本語)": """本日の実験では、「提案者（Proposer）」または「応答者（Responder）」という2つの役割のいずれかを担っていただきます。各ラウンドにおいて、提案者1名と応答者1名がペアになり、100ドルの資金をどのように分配するかを決定します。ペアはコンピュータによってランダムに決定され、ラウンドごとに変更されます。相手が誰であるかを特定することはできず、同じ相手と再びペアになることもありません。\n\n提案者の意思決定タスクは、100ドルのうち応答者にいくら提示（オファー）するかを決定することです。提示額は0から100までの整数で指定できます。オファーが受け入れられた場合、応答者は提案された金額を受け取り、提案者は残りの額を受け取ります。\n\nこのゲームでは、応答者が提案者のオファーを拒否する権利（拒否権）を持つ場合があります。応答者がこの権利を持つ確率はランダムに決定されます。各ラウンドの開始時に、提案者と応答者の双方にこの確率が通知されます。応答者の意思決定は、自身が受け入れることができる最低金額（閾値 / Threshold）を示すことです。\n\n拒否権が付与され（確率 π）、オファーが閾値以上であった場合、オファーは受け入れられます。そうでない場合、双方の取り分は0ドルとなります。拒否権が付与されなかった場合は、提案者のオファー通りに分配されます。現在は第1ラウンドです。あなたは提案者として行動します。応答者が拒否権を持つ確率は0.9です。今ラウンドで応答者にいくら提案するか決定してください。説明は不要で、数字のみを入力してください。""",
    "French (Français)": """Dans l'expérience d'aujourd'hui, vous pouvez jouer deux rôles : le Proposeur (Proposer) et le Répondant (Responder). À chaque tour, un Proposeur et un Répondant seront associés pour déterminer comment diviser une cagnotte de 100 dollars entre eux. L'ordinateur attribue l'appariement de manière aléatoire afin que les paires changent de tour en tour. Vous ne pourrez pas identifier votre adversaire et vous ne serez jamais remis en paire avec le même joueur.\n\nPour le Proposeur, la tâche de décision consiste à déterminer quel montant (un nombre entier de 0 à 100) offrir au Répondant. Si une offre est acceptée, le Répondant obtient le montant proposé et le Proposeur garde le reste de la cagnotte.\n\nDans ce jeu, il est possible pour le Répondant d'avoir l'option de rejeter l'offre du Proposeur (droit de veto). La probabilité pour qu'un Répondant dispose de cette option est déterminée de manière aléatoire. Au début de chaque tour, les deux joueurs sont informés de cette probabilité. Pour le Répondant, la décision consiste à indiquer le montant minimum qu'il est prêt à accepter (seuil / Threshold).\n\nSi le Répondant obtient l'option de rejeter l'offre et que l'offre est supérieure ou égale au seuil, elle est acceptée. Sinon, les deux joueurs obtiennent 0 dollar. C'est le premier tour. Vous agirez en tant que Proposeur. La probabilité que le Répondant ait l'option de rejet est de 0,9. Veuillez décider du montant à offrir. Fournissez juste un seul nombre sans explications.""",
    "German (Deutsch)": """Im heutigen Experiment gibt es zwei mögliche Rollen: den Antragssteller (Proposer) und den Empfänger (Responder). In jeder Runde werden ein Antragssteller und ein Empfänger einander zugewiesen, um zu entscheiden, wie ein Betrag von 100 Dollar zwischen ihnen aufgeteilt wird. Die Zuweisung erfolgt zufällig durch den Computer, sodass sich die Paarungen von Runde zu Runde ändern.\n\nFür den Antragssteller besteht die Aufgabe darin, zu bestimmen, wie viel von den 100 Dollar dem Empfänger angeboten werden soll (ganze Zahl von 0 bis 100). Wird das Angebot angenommen, erhält der Empfänger den angebotenen Betrag und der Antragssteller behält den Rest.\n\nIn diesem Spiel haben Empfänger unter Umständen die Möglichkeit, Angebote des Antragsstellers abzulehnen (Veto-Recht). Die Wahrscheinlichkeit dafür wird zufällig bestimmt. Für den Empfänger besteht die Entscheidung darin, den Mindestbetrag anzugeben, den er bereit ist zu akzeptieren (Schwellenwert / Threshold).\n\nWird dem Empfänger das Vetorecht zugesprochen und das Angebot erreicht oder übersteigt den Schwellenwert, wird es angenommen. Andernfalls erhalten beide 0 Dollar. Dies ist die erste Runde. Sie agieren als Antragssteller. Die Wahrscheinlichkeit für das Vetorecht beträgt 0,9. Bitte geben Sie Ihr Angebot als einzelne Zahl ohne Erklärungen an.""",
    "Spanish (Español)": """En el experimento de hoy, hay dos roles posibles: el Proponente (Proposer) y el Receptor (Responder). En cada ronda, un Proponente y un Receptor se emparejarán para determinar cómo dividir una suma de 100 dólares. El emparejamiento es aleatorio, por lo que las parejas cambiarán de ronda en ronda.\n\nPara el Proponente, la decisión consiste en determinar cuánto de los 100 dólares ofrecer al Receptor (número entero entre 0 y 100). Si la oferta es aceptada, el Receptor obtendrá la cantidad propuesta y el Proponente se quedará con el resto.\n\nEn este juego, es posible que el Receptor tenga la opción de rechazar las ofertas (derecho de veto). La probabilidad de que el Receptor tenga esta opción se determina al azar. Para el Receptor, la decisión consiste en indicar la cantidad mínima que está dispuesto a aceptar, conocida como el "umbral" (Threshold).\n\nSi el Receptor cuenta con la opción de veto y la oferta es igual o mayor al umbral, la oferta se acepta. De lo contrario, ambos reciben 0 dólares. Esta es la primera ronda. Usted actuará como Proponente. La probabilidad de que el Receptor tenga la opción de rechazar es 0.9. Por favor, decida cuánto ofrecerá. Proporcione solo un número sin explicaciones.""",
    "Arabic (العربية)": """في تجربة اليوم، هناك دوران محتملان لك: مقدم الاقتراح (Proposer) والمستجيب (Responder). في كل جولة، سيتم تقسيم مبلغ 100 دولار بين مقدم الاقتراح والمستجيب. يخصص الكمبيوتر المطابقة العشوائية بحيث تتغير الشراكات من جولة إلى جولة.\n\nبالنسبة لمقدم الاقتراح، تتمثل المهمة في تحديد المبلغ الذي سيقدمه للمستجيب من أصل 100 دولار (بين 0 و100). إذا تم قبول العرض، يحصل المستجيب على المبلغ المقترح ويحتفظ مقدم الاقتراح بالباقي.\n\nفي هذه اللعبة، قد يكون للمستجيب خيار رفض العروض (حق الفيتو). بالنسبة للمستجيب، القرار هو تحديد الحد الأدنى للمبلغ الذي يقبل به (Threshold).\n\nإذا مُنح المستجيب خيار الرفض وكان العرض أكبر من أو يساوي هذا الحد، يتم قبول العرض. خلاف ذلك، يحصل كلا اللاعبين على 0. هذه هي الجولة الأولى. ستعمل كمقدم اقتراح. احتمال حصول المستجيب على خيار الرفض هو 0.9. يرجى تحديد المبلغ الذي ستعرضه برقم واحد فقط دون أي شرح.""",
    "Korean (한국어)": """오늘 실험에서 당신은 제안자(Proposer)와 응답자(Responder) 중 하나의 역할을 맡게 됩니다. 매 라운드마다 한 명의 제안자와 한 명의 응답자가 매칭되어 100달러를 어떻게 나눌지 결정합니다.\n\n제안자는 100달러 중 응답자에게 제안할 금액을 결정합니다(0에서 100 사이 정수). 제안이 수락되면 응답자는 제안된 금액을 받고, 제안자는 남은 금액을 가집니다.\n\n이 게임에서 응답자는 제안을 거절할 수 있는 권한(거부권)을 가질 수 있습니다. 응답자는 수락할 용의가 있는 최소 금액인 '수락 한계선(Threshold)'을 설정합니다.\n\n응답자에게 거부권이 부여되고 제안된 금액이 한계선 이상이면 수락되지만, 한계선 미만이면 거절되어 두 플레이어 모두 0달러를 받습니다. 첫 번째 라운드입니다. 당신은 제안자로 참여합니다. 응답자가 거부권을 가질 확률은 0.9입니다. 이번 라운드에 제안할 금액을 정해주세요. 설명 없이 숫자 하나만 입력해 주세요.""",
    "Indonesian (Bahasa Indonesia)": """Dalam eksperimen hari ini, ada dua peran yang mungkin Anda mainkan: Pengusul (Proposer) dan Penerima (Responder). Di setiap putaran, satu Pengusul dan satu Penerima akan dipasangkan untuk menentukan bagaimana membagi dana sebesar 100 dolar.\n\nUntuk Pengusul, tugas keputusan adalah menentukan seberapa banyak dari 100 dolar yang akan ditawarkan kepada Penerima (antara 0 hingga 100). Jika penawaran diterima, Penerima akan mendapatkan jumlah yang diusulkan dan Pengusul menyimpan sisanya.\n\nDalam permainan ini, Penerima mungkin memiliki opsi untuk menolak penawaran (hak veto). Untuk Penerima, keputusannya adalah menentukan jumlah minimum yang bersedia ia terima, yang disebut sebagai "ambang batas" (Threshold).\n\nJika Penerima diberikan opsi veto dan penawaran memenuhi atau melebihi ambang batas, penawaran diterima. Jika tidak, kedua pemain mendapatkan 0. Ini adalah putaran pertama. Anda bertindak sebagai Pengusul. Probabilitas Penerima memiliki opsi penolakan adalah 0,9. Silakan tentukan berapa banyak yang akan Anda tawarkan. Berikan satu angka saja tanpa penjelasan.""",
    "Italian (Italiano)": """Nell'esperimento di oggi, ci sono due ruoli possibili: il Proponente (Proposer) e il Ricevente (Responder). In ogni round, un Proponente e un Ricevente saranno accoppiati per decidere come dividere un budget di 100 dollari.\n\nPer il Proponente, il compito consiste nel determinare quanto, su 100 dollari, offrire al Ricevente (da 0 a 100). Se l'offerta viene accettata, il Ricevente ottiene la somma proposta e il Proponente tiene il resto.\n\nIn questo gioco, è possibile per i Riceventi avere l'opzione di rifiutare l'offerta (diritto di veto). Per il Ricevente, la decisione consiste nell'indicare la somma minima che è disposto ad accettare ("soglia" / Threshold).\n\nSe il Ricevente ottiene l'opzione di rifiuto e l'offerta è pari o superiore alla soglia, viene accettata. Altrimenti, entrambi ottengono 0 dollari. Questo è il primo round. Agirai come Proponente. La probabilità che il Ricevente abbia l'opzione di veto è 0,9. Decidi quanto offrire fornendo solo un numero senza spiegazioni.""",
    "Polish (Polski)": """W dzisiejszym eksperymencie możesz wcielić się w jedną z dwóch ról: Proponującego (Proposer) lub Reagującego (Responder). W każdej rundzie jeden Proponujący i jeden Reagujący są dobierani w parę, aby podzielić między sobą kwotę 100 dolarów.\n\nZadaniem Proponującego jest określenie, jaką część ze 100 dolarów zaoferować Reagującemu (od 0 do 100). Jeśli oferta zostanie zaakceptowana, Reagujący otrzymuje zaproponowaną kwotę, a Proponujący zatrzymuje resztę.\n\nW tej grze Reagujący mogą mieć możliwość odrzucenia oferty (prawo weta). Decyzja Reagującego polega na wskazaniu minimalnej kwoty, jaką jest gotów przyjąć ("próg" / Threshold).\n\nJeśli Reagujący otrzyma prawo weta i oferta jest równa lub wyższa od progu, zostaje zaakceptowana. W przeciwnym razie obaj gracze otrzymują 0 dolarów. To jest pierwsza runda. Występujesz jako Proponujący. Prawdopodobieństwo weta wynosi 0,9. Podaj swoją ofertę jako pojedynczą liczbę bez wyjaśnień.""",
    "Russian (Русский)": """В сегодняшнем эксперименте вам предстоит сыграть одну из двух ролей: Инициатор (Proposer) или Ответчик (Responder). В каждом раунде Инициатор и Ответчик объединяются в пары, чтобы разделить сумму в 100 долларов.\n\nДля Инициатора задача состоит в том, чтобы определить, какую сумму из 100 долларов предложить Ответчику (целое число от 0 до 100). Если предложение принято, Ответчик получает предложенную сумму, а Инициатор оставляет себе остаток.\n\nВ этой игре у Ответчиков может быть возможность отклонить предложение (право вето). Для Ответчика решение состоит в том, чтобы указать минимальную сумму — «порог» (Threshold).\n\nЕсли Ответчику предоставляется право вето и предложение превышает или равно порогу, оно принимается. В противном случае оба получают 0 долларов. Это первый раунд. Вы выступаете в роли Инициатора. Вероятность права вето у Ответчика составляет 0,9. Пожалуйста, укажите предложение одним числом без пояснений.""",
    "Greek (Ελληνικά)": """Στο σημερινό πείραμα, υπάρχουν δύο πιθανοί ρόλοι: ο Προτείνων (Proposer) και ο Αποδέκτης (Responder). Σε κάθε γύρο, ένας Προτείνων και ένας Αποδέκτης συνδυάζονται για να αποφασίσουν πώς θα διαιρέσουν ένα ποσό 100 δολαρίων.\n\nΓια τον Προτείνοντα, η απόφαση είναι να καθορίσει πόσα από τα 100 δολάρια θα προσφέρει στον Αποδέκτη (ακέραιος 0-100). Εάν η προσφορά γίνει αποδεκτή, ο Αποδέκτης λαμβάνει το προτεινόμενο ποσό.\n\nΣε αυτό το παιχνίδι, ο Αποδέκτης μπορεί να έχει δικαίωμα βέτο. Η απόφαση του Αποδέκτη είναι να δηλώσει το ελάχιστο αποδεκτό ποσό ("όριο" / Threshold).\n\nΕάν ο Αποδέκτης έχει δικαίωμα βέτο και η προσφορά είναι ίση ή μεγαλύτερη από το όριο, γίνετε αποδεκτή. Διαφορετικά, και οι δύο λαμβάνουν 0. Αυτός είναι ο πρώτος γύρος. Ενεργείτε ως Προτείνων. Η πιθανότητα βέτο είναι 0,9. Ορίστε την προσφορά σας με έναν μόνο αριθμό χωρίς εξηγήσεις.""",
    "Turkish (Türkçe)": """Bugünkü deneyde üstlenebileceğiniz iki rol bulunmaktadır: Teklif Eden (Proposer) ve Yanıtlayan (Responder). Her turda, bir Teklif Eden ve bir Yanıtlayan 100 dolarlık havuzu bölüşmek üzere eşleştirilir.\n\nTeklif Eden için görev, 100 dolardan ne kadarını Yanıtlayan'a teklif edeceğini belirlemektir (0-100 arası). Teklif kabul edilirse Yanıtlayan teklif edilen miktarı alır.\n\nYanıtlayan'ın teklifi reddetme seçeneği (veto hakkı) olabilir. Yanıtlayan kabul etmeye hazır olduğu minimum miktarı ("eşik değeri" / Threshold) belirtir.\n\nVeto hakkı verildiğinde teklif eşik değerine eşit veya büyükse kabul edilir; aksi halde her iki taraf da 0 alır. Bu birinci turdur. Teklif Eden olarak hareket ediyorsunuz. Veto olasılığı 0,9'dur. Lütfen teklifinizi açıklama yapmadan sadece tek bir sayı olarak belirtin.""",
    "Afrikaans (Afrikaans)": """In vandag se eksperiment is daar twee moontlike rolle: die Voorsteller (Proposer) en die Respondent (Responder). In elke rondte word 'n Voorsteller en Respondent gepaar om 100 dollar te verdeel.\n\nVir 'n Voorsteller is die taak om te besluit hoeveel van die 100 dollar om aan te bied (0 tot 100). As die aanbod aanvaar word, kry die Respondent die bedrag.\n\nDie Respondent kan 'n vetoreg hê om die aanbod te verwerp en dui 'n minimum aanvaarbare drempel (Threshold) aan.\n\nAs vetoreg geld en die aanbod is gelyk aan of hoër as die drempel, word dit aanvaar; anders kry albei 0 dollar. Dit is die eerste rondte. Jy is die Voorsteller. Die vetowaarskynlikheid is 0,9. Besluit hoeveel jy wil aanbied met net 'n enkele getal sonder verduidelikings.""",
    "Welsh (Cymraeg)": """Yn yr arbrawf heddiw, mae dwy rôl bosibl: y Cynigydd (Proposer) ac y Sefydlydd (Responder). Ym mhob rownd, mae Cynigydd a Sefydlydd yn cael eu paru i rannu cronfa o 100 doler.\n\nAr gyfer Cynigydd, y penderfyniad yw faint o'r 100 doler i'w gynnig i'r Sefydlydd (0 i 100). Os caiff ei dderbyn, mae'r Sefydlydd yn cael y swm.\n\nMae gan y Sefydlydd hawl feto bosibl ac mae'n nodi'r swm lleiaf sy'n dderbyniol ("trothwy" / Threshold).\n\nOs rhoddir hawl feto a bod y cynnig yn fwy neu'n gyfartal â'r trothwy, fe'i derbynnir; fel arall mae'r ddau yn cael 0 doler. Dyma'r rownd gyntaf. Rydych yn chwarae fel Cynigydd. Y tebygolrwydd feto yw 0.9. Nodwch eich cynnig fel un nifer yn unig heb esboniadau."""
}

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
*   **00:40 - 01:00**: Step 3 - Offer vs. Threshold Cross-Country Analytics
""")

# Handle customized translations state
if 'custom_translations' not in st.session_state:
    st.session_state.custom_translations = default_translations.copy()

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
    st.sidebar.subheader("🔧 Dynamic Translation Customizer")
    selected_custom_lang = st.sidebar.selectbox("Select Language to Edit:", list(default_translations.keys()))
    custom_text = st.sidebar.text_area(
        f"Edit instructions for {selected_custom_lang}:",
        value=st.session_state.custom_translations[selected_custom_lang],
        height=150
    )
    if st.sidebar.button("💾 Save Translation"):
        st.session_state.custom_translations[selected_custom_lang] = custom_text
        st.sidebar.success(f"Updated translation for {selected_custom_lang}!")

# Main Title & Presentation Header
st.markdown("<h1 style='color: #1e3d59; font-size: 32px;'>⚖️ Session 1: Linguistic Relativity & The Power Game</h1>", unsafe_allow_html=True)
st.markdown("##### Lucas College and Graduate School of Business — EMBA International Forum")

# Unified Participant Registration (Auto-Generated ID like Trust Game)
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
        # Request #3: Dropdown includes English as well for students who don't know a 2nd language!
        selected_lang = st.selectbox(
            "Select Language for Review & Calibration:",
            options=list(default_translations.keys()),
            index=0 # Default to English
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
                # English-only comment validation
                non_ascii_found = any(ord(char) > 127 for char in comments)
                has_asian_chars = bool(re.search(r'[\u4e00-\u9fff\u3040-\u309f\u30a0-\u30ff\uac00-\ud7af]', comments))
                
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
                    st.balloons()
                    st.success(f"🎉 Thank you, {student_id}! Your linguistic calibration has been recorded.")

# =============================================================================
# TAB 2: INTERACTIVE POWER GAME
# =============================================================================
with nav_tabs[1]:
    st.markdown("### 🎮 Step 2: The Interactive Power Game")
    st.write(
        "Now, participate in the Modified Ultimatum Game. You will be matched against "
        "a computer agent calibrated based on the cultural baseline of your selected language."
    )
    
    selected_game_lang = st.selectbox(
        "Select your native or preferred language for playing:",
        options=list(default_translations.keys()),
        key="game_lang_select"
    )
    
    # Resolve veto probability based on Instructor Setting
    if st.session_state.pi_assignment_mode == "Automatic Split (50% Low, 50% High π)":
        if student_id:
            try:
                numeric_part = int(''.join(filter(str.isdigit, student_id)))
                veto_config = 0.10 if numeric_part % 2 == 0 else 0.90
            except ValueError:
                veto_config = 0.10 if len(student_id) % 2 == 0 else 0.90
            st.success(f"🎯 **Your Assigned Veto Probability (π):** {veto_config:.2f} ({'Low Responder Power' if veto_config == 0.10 else 'High Responder Power'}) — locked based on your Student ID.")
        else:
            veto_config = 0.10
            st.warning("⚠️ Enter your Anonymous Student ID at the top of the page to unlock and see your assigned Veto Probability.")
    else:
        veto_config = st.radio(
            "Select your assigned Veto Probability (π) condition:",
            options=[0.10, 0.90],
            format_func=lambda x: f"Low Responder Power (π = {x*100:.0f}%)" if x == 0.10 else f"High Responder Power (π = {x*100:.0f}%)",
            help="π represents the probability that the responder's veto threshold is active."
        )
        st.write(f"In this round, the chance that the Responder's veto will be active is **{veto_config*100:.0f}%**.")

    col_p1, col_p2 = st.columns(2)
    
    with col_p1:
        st.markdown("<h5 style='color: #1e3d59;'>Option A: Play as Proposer</h5>", unsafe_allow_html=True)
        st.write("You propose how to split the $100. If the offer meets the responder's threshold, it is accepted.")
        
        with st.form("proposer_form"):
            p_student_id = student_id
            if not student_id:
                st.warning("⚠️ Please register your Student ID at the top of the page first.")
            else:
                st.info(f"Proposer ID: **{student_id}** (Status: Active)")
            offer = st.slider("Your Offer to the Responder ($0 to $100):", min_value=0, max_value=100, value=30, step=1)
            submit_offer = st.form_submit_button("📤 Submit Offer")
            
            if submit_offer:
                if not p_student_id:
                    st.error("Please enter your Student ID.")
                else:
                    # Simulated Responder threshold based on paper language baselines
                    base_threshold = random.randint(25, 35)
                    veto_active = random.random() < veto_config
                    
                    if veto_active:
                        if offer >= base_threshold:
                            outcome = "Accepted"
                            p_payout = 100 - offer
                            r_payout = offer
                        else:
                            outcome = "Rejected"
                            p_payout = 0
                            r_payout = 0
                    else:
                        outcome = "Accepted (No Veto Enforced)"
                        p_payout = 100 - offer
                        r_payout = offer
                        
                    payout_str = f"Proposer: {p_payout}, Responder: {r_payout}"
                    
                    st.session_state.game_logs.append({
                        "Timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "Student_ID": p_student_id,
                        "Role": "Proposer",
                        "Language": selected_game_lang,
                        "Veto_Probability": veto_config,
                        "Offer": offer,
                        "Threshold": "N/A (Agent)",
                        "Veto_Enforced": "Yes" if veto_active else "No",
                        "Outcome": outcome,
                        "Payout": payout_str
                    })
                    
                    st.success("##### 🎯 Round Result Resolved!")
                    st.write(f"**Your Offer:** ${offer}")
                    st.write(f"**Simulated Agent Threshold:** ${base_threshold}")
                    st.write(f"**Was Veto Enforced?** {'Yes' if veto_active else 'No'}")
                    st.write(f"**Final Outcome:** {outcome}")
                    st.info(f"💰 **Payout Allocation:** {payout_str}")

    with col_p2:
        st.markdown("<h5 style='color: #1e3d59;'>Option B: Play as Responder</h5>", unsafe_allow_html=True)
        st.write("Set your minimum acceptable threshold. If the proposer's offer meets this, it is accepted.")
        
        with st.form("responder_form"):
            r_student_id = student_id
            if not student_id:
                st.warning("⚠️ Please register your Student ID at the top of the page first.")
            else:
                st.info(f"Responder ID: **{student_id}** (Status: Active)")
            threshold = st.slider("Your Minimum Threshold ($0 to $100):", min_value=0, max_value=100, value=30, step=1)
            submit_threshold = st.form_submit_button("📤 Submit Threshold")
            
            if submit_threshold:
                if not r_student_id:
                    st.error("Please enter your Student ID.")
                else:
                    # Simulated Proposer offer based on paper language baselines
                    base_offer = random.randint(30, 40)
                    veto_active = random.random() < veto_config
                    
                    if veto_active:
                        if base_offer >= threshold:
                            outcome = "Accepted"
                            p_payout = 100 - base_offer
                            r_payout = base_offer
                        else:
                            outcome = "Rejected"
                            p_payout = 0
                            r_payout = 0
                    else:
                        outcome = "Accepted (No Veto Enforced)"
                        p_payout = 100 - base_offer
                        r_payout = base_offer
                        
                    payout_str = f"Proposer: {p_payout}, Responder: {r_payout}"
                    
                    st.session_state.game_logs.append({
                        "Timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "Student_ID": r_student_id,
                        "Role": "Responder",
                        "Language": selected_game_lang,
                        "Veto_Probability": veto_config,
                        "Offer": "N/A (Agent)",
                        "Threshold": threshold,
                        "Veto_Enforced": "Yes" if veto_active else "No",
                        "Outcome": outcome,
                        "Payout": payout_str
                    })
                    
                    st.success("##### 🎯 Round Result Resolved!")
                    st.write(f"**Simulated Agent Offer:** ${base_offer}")
                    st.write(f"**Your Threshold:** ${threshold}")
                    st.write(f"**Was Veto Enforced?** {'Yes' if veto_active else 'No'}")
                    st.write(f"**Final Outcome:** {outcome}")
                    st.info(f"💰 **Payout Allocation:** {payout_str}")

# =============================================================================
# TAB 3: INSTRUCTOR COURSE ANALYTICS (Passcode Protected!)
# =============================================================================
if is_instructor:
    with nav_tabs[2]:
        st.markdown("<h3 style='color: #1e3d59;'>📊 Step 3: Instructor Course Analytics Dashboard</h3>", unsafe_allow_html=True)
        st.write("Monitor live classroom submissions, verify cross-country offer vs. threshold dynamics, and download research data.")
        
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
        
        # 2. Gameplay logs & Cross-Country Offer vs. Threshold Chart (PDI REMOVED AS REQUESTED)
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
        # Request #4: Remove PDI, instead do a graph of Offer vs. Threshold for different countries!
        st.markdown("#### **III. Cross-Country Bargaining Analytics: Proposer Offer vs. Responder Threshold**")
        st.write(
            "This plot maps **Average Proposer Offer ($)** on the X-axis against **Average Responder Threshold ($)** "
            "on the Y-axis across different countries and languages, comparing empirical baseline research data with live classroom decisions."
        )
        
        # Render Interactive Plotly Scatter: Offer (X) vs Threshold (Y) by Country/Language
        fig_cross_country = go.Figure()
        
        # 1. 1:1 Parity Line (y = x) where Offer = Threshold
        diag_line = np.linspace(20, 45, 100)
        fig_cross_country.add_trace(go.Scatter(
            x=diag_line, y=diag_line,
            mode='lines',
            line=dict(color='#A0AEC0', width=2, dash='dash'),
            name='Acceptance Parity Line (Offer = Threshold)',
            hoverinfo='skip'
        ))
        
        # 2. Baseline Country Points (Paper Empirical Data)
        fig_cross_country.add_trace(go.Scatter(
            x=paper_country_data["Avg_Offer_Paper"],
            y=paper_country_data["Avg_Threshold_Paper"],
            mode='markers+text',
            name='Empirical Baseline (Paper)',
            text=paper_country_data["Country_Language"],
            textposition="top center",
            marker=dict(size=12, color='#1E3A8A', symbol='circle', line=dict(width=1, color='#0F172A')),
            hovertemplate="<b>%{text}</b><br>Baseline Offer: $%{x:.2f}<br>Baseline Threshold: $%{y:.2f}<extra></extra>"
        ))
        
        # 3. Live Class Average Overlay
        if not df_games.empty:
            # Separate offers and thresholds to calculate live language averages
            live_offers = df_games[df_games["Offer"] != "N/A (Agent)"].copy()
            live_thresh = df_games[df_games["Threshold"] != "N/A (Agent)"].copy()
            
            if not live_offers.empty or not live_thresh.empty:
                live_offers["Offer"] = pd.to_numeric(live_offers["Offer"], errors='coerce')
                live_thresh["Threshold"] = pd.to_numeric(live_thresh["Threshold"], errors='coerce')
                
                agg_off = live_offers.groupby("Language")["Offer"].mean().reset_index() if not live_offers.empty else pd.DataFrame(columns=["Language", "Offer"])
                agg_thr = live_thresh.groupby("Language")["Threshold"].mean().reset_index() if not live_thresh.empty else pd.DataFrame(columns=["Language", "Threshold"])
                
                live_merged = pd.merge(agg_off, agg_thr, on="Language", how="outer").fillna(30.0)
                
                fig_cross_country.add_trace(go.Scatter(
                    x=live_merged["Offer"],
                    y=live_merged["Threshold"],
                    mode='markers+text',
                    name='Live Class Average',
                    text=live_merged["Language"].apply(lambda x: f"Class: {x.split(' ')[0]}"),
                    textposition="bottom center",
                    marker=dict(size=16, color='#FF9F43', symbol='star', line=dict(width=1, color='#C2410C')),
                    hovertemplate="<b>%{text}</b><br>Class Avg Offer: $%{x:.2f}<br>Class Avg Threshold: $%{y:.2f}<extra></extra>"
                ))
        
        fig_cross_country.update_layout(
            title="Proposer Offer vs. Responder Threshold Across Languages & Countries",
            xaxis_title="Proposer Offer Amount ($ out of 100)",
            yaxis_title="Responder Threshold Amount ($ out of 100)",
            template="plotly_white",
            height=500,
            margin=dict(l=30, r=30, t=50, b=30),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        st.plotly_chart(fig_cross_country, use_container_width=True)
