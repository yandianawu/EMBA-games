import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import random
import datetime

# Set page configuration
st.set_page_config(
    page_title="The Power Game - Facilitation Portal",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ----------------------------------------------------
# 1. State Management & Mock Data Pre-loading
# ----------------------------------------------------

# Initialize calibration evaluation responses if not exists
if 'responses' not in st.session_state:
    st.session_state.responses = [
        {"Timestamp": "2026-09-01 14:02:15", "Student_ID": "EMBA_04", "Language": "French (Français)", "Q1_Clarity_Rating": 5, "Q2_Naturalness_Rating": 4, "Translation_Comments": "The term 'cagnotte' is perfect for 'pool'. Very clear." or ""},
        {"Timestamp": "2026-09-01 14:05:32", "Student_ID": "EMBA_11", "Language": "Simplified Chinese (简体中文)", "Q1_Clarity_Rating": 4, "Q2_Naturalness_Rating": 5, "Translation_Comments": "对‘提议人’和‘应答者’的翻译非常符合行为经济学标准。" or ""},
        {"Timestamp": "2026-09-01 14:08:44", "Student_ID": "EMBA_15", "Language": "Japanese (日本語)", "Q1_Clarity_Rating": 5, "Q2_Naturalness_Rating": 3, "Translation_Comments": "‘拒絶権’ is correct, but perhaps '拒否権' is more commonly used in corporate governance slides." or ""},
        {"Timestamp": "2026-09-01 14:12:01", "Student_ID": "EMBA_02", "Language": "Spanish (Español)", "Q1_Clarity_Rating": 4, "Q2_Naturalness_Rating": 4, "Translation_Comments": "Clear explanation of the veto probability." or ""},
        {"Timestamp": "2026-09-01 14:15:19", "Student_ID": "EMBA_09", "Language": "German (Deutsch)", "Q1_Clarity_Rating": 3, "Q2_Naturalness_Rating": 4, "Translation_Comments": "A bit formal, but highly accurate." or ""}
    ]

# Initialize gameplay logs if not exists
if 'game_logs' not in st.session_state:
    st.session_state.game_logs = [
        {"Timestamp": "2026-09-01 14:10:05", "Student_ID": "EMBA_04", "Language": "French (Français)", "Role": "Proposer", "Power_Prob_Pi": 0.1, "Offer": 30, "Threshold": 25, "Veto_Enforced": "No", "Outcome": "Accepted", "Student_Payout": 70, "Opponent_Payout": 30},
        {"Timestamp": "2026-09-01 14:11:15", "Student_ID": "EMBA_11", "Language": "Simplified Chinese (简体中文)", "Role": "Proposer", "Power_Prob_Pi": 0.9, "Offer": 40, "Threshold": 35, "Veto_Enforced": "Yes", "Outcome": "Accepted", "Student_Payout": 60, "Opponent_Payout": 40},
        {"Timestamp": "2026-09-01 14:12:30", "Student_ID": "EMBA_15", "Language": "Japanese (日本語)", "Role": "Responder", "Power_Prob_Pi": 0.9, "Offer": 32, "Threshold": 35, "Veto_Enforced": "Yes", "Outcome": "Rejected", "Student_Payout": 0, "Opponent_Payout": 0},
        {"Timestamp": "2026-09-01 14:13:45", "Student_ID": "EMBA_02", "Language": "Spanish (Español)", "Role": "Responder", "Power_Prob_Pi": 0.1, "Offer": 22, "Threshold": 30, "Veto_Enforced": "No", "Outcome": "Accepted", "Student_Payout": 22, "Opponent_Payout": 78},
        {"Timestamp": "2026-09-01 14:14:50", "Student_ID": "EMBA_09", "Language": "German (Deutsch)", "Role": "Proposer", "Power_Prob_Pi": 0.9, "Offer": 45, "Threshold": 40, "Veto_Enforced": "Yes", "Outcome": "Accepted", "Student_Payout": 55, "Opponent_Payout": 45}
    ]

# Default selected language session state
if 'selected_lang' not in st.session_state:
    st.session_state.selected_lang = "Simplified Chinese (简体中文)"

if 'current_student_id' not in st.session_state:
    st.session_state.current_student_id = ""

# ----------------------------------------------------
# 2. Text Corpus: 17 Languages Standardized Scripts
# ----------------------------------------------------
default_english_instructions = """In today's experiment, there are two possible roles for you to play: the Proposer and the Responder. \n\nIn every round, one Proposer and one Responder will be paired to determine how to divide a pool of 100 dollars between them. The computer assigns the random matching so that pairings will change from round to round. You will not be able to identify who is your opponent in the game and you will never be re-matched with the same Proposer or Responder. \n\nFor a Proposer, the decision task is to determine how much out of 100 dollars to offer to the Responder. The offer can be any integer number from 0 to 100. If an offer is accepted, the Responder will get the amount proposed and the Proposer will keep the rest of the pool. \n\nIn this game, it is possible for Responders to have an option to reject offers by Proposers. The probability for a Responder to have such an option is determined randomly. At the beginning of each round, both the Proposer and the Responder will be informed of this probability (π).\n\nFor the Responder, the decision is to indicate the minimum amount that he/she is willing to accept, which is referred to as the threshold. If the responder is granted the veto option (with probability π) and the offer meets or exceeds the threshold, the offer is accepted; otherwise, both players receive zero. If the responder is not granted the veto, the Proposer's offer is automatically implemented."""

default_translations = {
    "English": default_english_instructions,
    "Simplified Chinese (简体中文)": """在今天的实验中，您将扮演两种可能的角色：提议人（Proposer）和应答者（Responder）。\n\n在每一轮中，一名提议人和一名应答者将被配对，以决定如何分配100美元的资金池。电脑随机匹配，因此每轮的对手都会改变。您将无法识别游戏中的对手，也永远不会与同一个提议人或应答者再次配对。\n\n对于提议人，决策任务是确定从100美元中分出多少给应答者。提议金额可以是0到100之间的任意整数。如果提议被接受，应答者将获得提议的金额，而提议人将保留资金池的其余部分。\n\n在这场游戏中，应答者有可能拥有拒绝提议人提议的权利。应答者获得该否决权的概率是随机决定的。在每一轮开始时，提议人和应答者都会被告知这个概率 (π)。\n\n对于应答者，决策是指出他/她愿意接受的最低金额，这在游戏中被称为“最低接受额（Threshold）”。如果在该轮中应答者被随机授予了否决权（概率为 π），且提议达到或超过了最低接受额，则提议被接受；否则，双方均获得0美元。如果电脑没有赋予应答者否决权，则直接按照提议人的方案进行分配。""",
    "Traditional Chinese (繁體中文)": """在今天的實驗中，您將扮演兩種可能的角色：提議人（Proposer）和應答者（Responder）。\n\n在每一輪中，一名提議人和一名應答者將被配對，以決定如何分配100美元的資金池。電腦隨機匹配，因此每輪的對手都會改變。您將無法識別遊戲中的對手，也永遠不會與同一個提議人或應答者再次配對。\n\n對於提議人，決策任務是確定從100美元中分出多少給應答者。提議金額可以是0到100之間的任意整數。如果提議被接受，應答者將獲得提議的金額，而提議人將保留資金池的其餘部分。\n\n在這場遊戲中，應答者有可能擁有拒絕提議人提議的權利。應答者獲得該否決權的概率是隨機決定的。在每一輪開始時，提議人和應答者都會被告知這個概率 (π)。\n\n對於應答者，決策是指出他/她願意接受的最低金額，這在遊戲中被稱為“最低接受額（Threshold）”。如果在該輪中應答者被隨機授予了否決權（概率為 π），且提議達到或超過了最低接受額，則提議被接受；否則，雙方均獲得0美元。如果電腦沒有賦予應答者否決權，則直接按照提議人的方案進行分配。""",
    "Japanese (日本語)": """本日の実験では、「提案者（Proposer）」または「応答者（Responder）」という2つの役割のいずれかを担っていただきます。\n\n各ラウンドにおいて、提案者1名と応答者1名がペアになり、100ドルの資金をどのように分配するかを決定します。ペアはコンピュータによってランダムに決定され、ラウンドごとに変更されます。相手が誰であるかを特定することはできず、同じ相手と再びペアになることもありません。\n\n提案者の意思決定タスクは、100ドルのうち応答者にいくら提示（オファー）するかを決定することです。提示額は0から100までの整数で指定できます。オファーが受け入れられた場合、応答者は提案された金額を受け取り、提案者は残りの額を受け取ります。\n\nこのゲームでは、応答者が提案者のオファーを拒否する権利（拒否権）を持つ場合があります。応答者がこの権利を持つ確率はランダムに決定されます。各ラウンドの開始時に、提案者と応答者の双方にこの確率（π）が通知されます。\n\n応答者の意思決定は、自身が受け入れることができる最低金額（閾値 / Threshold）を示すことです。応答者に拒否権が付与され（確率 π）、オファーが閾値以上であった場合、オファーは受け入れられます。そうでない場合、双方の取り分は0ドルとなります。拒否権が付与されなかった場合は、閾値に関わらず、提案者のオファー通りに分配されます。""",
    "French (Français)": """Dans l'expérience d'aujourd'hui, vous pouvez jouer deux rôles : le Proposeur (Proposer) et le Répondant (Responder).\n\nÀ chaque tour, un Proposeur et un Répondant seront associés pour déterminer comment diviser une cagnotte de 100 dollars entre eux. L'ordinateur attribue l'appariement de manière aléatoire afin que les paires changent de tour en tour. Vous ne pourrez pas identifier votre adversaire et vous ne serez jamais remis en paire avec le même joueur.\n\nPour le Proposeur, la tâche de décision consiste à déterminer quel montant (un nombre entier de 0 à 100) offrir au Répondant. Si une offre est acceptée, le Répondant obtient le montant proposé et le Proposeur garde le reste de la cagnotte.\n\nDans ce jeu, il est possible pour le Répondant d'avoir l'option de rejeter l'offre du Proposeur (droit de veto). La probabilité pour qu'un Répondant dispose de cette option est déterminée de manière aléatoire. Au début de chaque tour, le Proposeur et le Répondant sont informés de cette probabilité (π).\n\nPour le Répondant, la décision consiste à indiquer le montant minimum qu'il est prêt à accepter, appelé le \"seuil\" (Threshold). Si le Répondant obtient l'option de rejeter l'offre (avec une probabilité π) et que l'offre est supérieure ou égale au seuil, elle est acceptée. Sinon, les deux joueurs obtiennent 0 dollar. Si le veto n'est pas activé par l'ordinateur, l'offre du Proposeur est automatiquement validée.""",
    "German (Deutsch)": """Im heutigen Experiment gibt es zwei mögliche Rollen: den Antragssteller (Proposer) und den Empfänger (Responder).\n\nIn jeder Runde werden ein Antragssteller und ein Empfänger einander zugewiesen, um zu entscheiden, wie ein Betrag von 100 Dollar zwischen ihnen aufgeteilt wird. Die Zuweisung erfolgt zufällig durch den Computer, sodass sich die Paarungen von Runde zu Runde ändern. Sie können Ihren Spielpartner nicht identifizieren und werden niemals mit derselben Person erneut gepaart.\n\nFür den Antragssteller besteht die Aufgabe darin, zu bestimmen, wie viel von den 100 Dollar dem Empfänger angeboten werden soll. Das Angebot kann jede ganze Zahl von 0 bis 100 sein. Wird das Angebot angenommen, erhält der Empfänger den angebotenen Betrag und der Antragssteller behält den Rest.\n\nIn diesem Spiel haben Empfänger unter Umständen die Möglichkeit, Angebote des Antragsstellers abzulehnen (Veto-Recht). Die Wahrscheinlichkeit, dass ein Empfänger dieses Recht erhält, wird zufällig bestimmt. Zu Beginn jeder Runde werden beide Spieler über diese Wahrscheinlichkeit (π) informiert.\n\nFür den Empfänger besteht die Entscheidung darin, den Mindestbetrag anzugeben, den er bereit ist zu akzeptieren (den Schwellenwert / Threshold). Wenn dem Empfänger das Vetorecht zugesprochen wird (mit Wahrscheinlichkeit π) und das Angebot den Schwellenwert erreicht oder übersteigt, wird es angenommen. Andernfalls erhalten beide Spieler 0 Dollar. Wird kein Veto gewährt, wird die Aufteilung automatisch gemäß dem Angebot des Antragsstellers durchgeführt.""",
    "Spanish (Español)": """En el experimento de hoy, hay dos roles posibles: el Proponente (Proposer) y el Receptor (Responder).\n\nEn cada ronda, un Proponente y un Receptor se emparejarán para determinar cómo dividir una suma de 100 dólares. El emparejamiento es aleatorio, por lo que las parejas cambiarán de ronda en ronda. No podrá identificar a su oponente y nunca volverá a jugar con el mismo Proponente o Receptor.\n\nPara el Proponente, la decisión consiste en determinar cuánto de los 100 dólares ofrecer al Receptor. La oferta puede ser cualquier número entero entre 0 y 100. Si la oferta es aceptada, el Receptor obtendrá la cantidad propuesta y el Proponente se quedará con el resto.\n\nEn este juego, es posible que el Receptor tenga la opción de rechazar las ofertas (derecho de veto). La probabilidad de que el Receptor tenga esta opción se determina al azar. Al principio de cada ronda, ambos jugadores serán informados de esta probabilidad (π).\n\nPara el Receptor, la decisión consiste en indicar la cantidad mínima que está dispuesto a aceptar, conocida como el \"umbral\" (Threshold). Si el Receptor cuenta con la opción de veto (con probabilidad π) y la oferta es igual o mayor al umbral, la oferta se acepta. De lo contrario, ambos reciben 0 dólares. Si el ordenador no otorga la opción de veto, la oferta del Proponente se implementa automáticamente.""",
    "Arabic (العربية)": """في تجربة اليوم، هناك دوران محتملان لك: مقدم الاقتراح (Proposer) والمستجيب (Responder).\n\nفي كل جولة، سيتم تقسيم مبلغ 100 دولار بين مقدم الاقتراح والمستجيب. يخصص الكمبيوتر المطابقة العشوائية بحيث تتغير الشراكات من جولة إلى جولة. لن تتمكن من تحديد هوية خصمك ولن يتم إقرانك بنفس الشخص مرة أخرى.\n\nبالنسبة لمقدم الاقتراح، تتمثل المهمة في تحديد المبلغ الذي سيقدمه للمستجيب من أصل 100 دولار (بين 0 و100). إذا تم قبول العرض، يحصل المستجيب على المبلغ المقترح ويحتفظ مقدم الاقتراح بالباقي.\n\nفي هذه اللعبة، قد يكون للمستجيب خيار رفض العروض (حق الفيتو). يتم تحديد احتمال حصول المستجيب على هذا الخيار عشوائيًا (π) ويتم إبلاغ الطرفين به في بداية كل جولة.\n\nبالنسبة للمستجيب، القرار هو تحديد الحد الأدنى للمبلغ الذي يقبل به (Threshold). إذا مُنح المستجيب خيار الرفض وكان العرض أكبر من أو يساوي هذا الحد، يتم قبول العرض. خلاف ذلك، يحصل كلا اللاعبين على 0. وإذا لم يمنح الكمبيوتر خيار الرفض، يتم تقسيم المبلغ وفقًا لعرض مقدم الاقتراح تلقائيًا.""",
    "Korean (한국어)": """오늘 실험에서 당신은 제안자(Proposer)와 응답자(Responder) 중 하나의 역할을 맡게 됩니다.\n\n매 라운드마다 한 명의 제안자와 한 명의 응답자가 매칭되어 100달러를 어떻게 나눌지 결정합니다. 컴퓨터가 무작위로 매칭을 수행하므로 상대방은 매 라운드 변경됩니다. 상대방이 누구인지 식별할 수 없으며, 동일한 제안자 혹은 응답자와 다시 매칭되지 않습니다.\n\n제안자는 100달러 중 응답자에게 제안할 금액을 결정합니다. 제안 금액은 0에서 100 사이의 정수여야 합니다. 제안이 수락되면 응답자는 제안된 금액을 받고, 제안자는 남은 금액을 가집니다.\n\n이 게임에서 응답자는 제안을 거절할 수 있는 권한(거부권)을 가질 수 있습니다. 응답자가 거부권을 가질 확률(π)은 무작위로 결정되며, 라운드 시작 시 제안자와 응답자 모두에게 알려집니다.\n\n응답자는 수락할 용의가 있는 최소 금액인 '수락 한계선(Threshold)'을 설정합니다. 응답자에게 거부권이 부여되고(확률 π), 제안된 금액이 한계선 이상이면 수락되지만, 한계선 미만이면 거절되어 두 플레이어 모두 0달러를 받습니다. 거부권이 부여되지 않은 경우에는 한계선과 상관없이 제안자의 제안대로 분배됩니다.""",
    "Indonesian (Bahasa Indonesia)": """Dalam eksperimen hari ini, ada dua peran yang mungkin Anda mainkan: Pengusul (Proposer) dan Penerima (Responder).\n\nDi setiap putaran, satu Pengusul dan satu Penerima akan dipasangkan untuk menentukan bagaimana membagi dana sebesar 100 dolar. Komputer mengatur pencocokan secara acak sehingga pasangan akan berubah dari putaran ke putaran. Anda tidak akan dapat mengidentifikasi siapa lawan Anda dan tidak akan pernah dipasangkan kembali dengan Pengusul atau Penerima yang sama.\n\nUntuk Pengusul, tugas keputusan adalah menentukan seberapa banyak dari 100 dolar yang akan ditawarkan kepada Penerima (antara 0 hingga 100). Jika penawaran diterima, Penerima akan mendapatkan jumlah yang diusulkan dan Pengusul akan menyimpan sisanya.\n\nDalam permainan ini, Penerima mungkin memiliki opsi untuk menolak penawaran (hak veto). Probabilitas bagi Penerima untuk memiliki opsi tersebut ditentukan secara acak. Di awal setiap putaran, kedua pemain akan diberitahu tentang probabilitas ini (π).\n\nUntuk Penerima, keputusannya adalah menentukan jumlah minimum yang bersedia ia terima, yang disebut sebagai \"ambang batas\" (Threshold). Jika Penerima diberikan opsi veto (dengan probabilitas π) dan penawaran memenuhi atau melebihi ambang batas, penawaran diterima. Jika tidak, kedua pemain mendapatkan 0. Jika opsi veto tidak aktif, penawaran Pengusul otomatis dijalankan.""",
    "Italian (Italiano)": """Nell'esperimento di oggi, ci sono due ruoli possibili: il Proponente (Proposer) e il Ricevente (Responder).\n\nIn ogni round, un Proponente e un Ricevente saranno accoppiati per decidere come dividere un budget di 100 dollari. Il computer assegna gli abbinamenti in modo casuale, quindi le coppie cambieranno di round in round. Non sarete in grado di identificare il vostro avversario e non giocherete mai con lo stesso partner.\n\nPer il Proponente, il compito consiste nel determinare quanto, su 100 dollari, offrire al Ricevente. L'offerta può essere qualsiasi numero intero da 0 a 100. Se l'offerta viene accettata, il Ricevente ottiene la somma proposta e il Proponente tiene il resto.\n\nIn questo gioco, è possibile per i Riceventi avere l'opzione di rifiutare l'offerta (diritto di veto). La probabilità di avere questa opzione è determinata in modo casuale. All'inizio di ogni round, entrambi i giocatori saranno informati di questa probabilità (π).\n\nPer il Ricevente, la decisione consiste nell'indicare la somma minima che è disposto ad accettare, denominata \"soglia\" (Threshold). Se il Ricevente ottiene l'opzione di rifiuto (con probabilità π) e l'offerta è pari o superiore alla soglia, viene accettata. Altrimenti, entrambi i giocatori ottengono 0 dollari. Se il computer non assegna l'opzione di veto, l'offerta del Proponente viene implementata automaticamente.""",
    "Polish (Polski)": """W dzisiejszym eksperymencie możesz wcielić się w jedną z dwóch ról: Proponującego (Proposer) lub Reagującego (Responder).\n\nW każdej rundzie jeden Proponujący i jeden Reagujący są dobierani w parę, aby podzielić między sobą kwotę 100 dolarów. Dopasowanie jest losowe, dzięki czemu pary zmieniają się z rundy na rundę. Nie będziesz w stanie zidentyfikować swojego przeciwnika i nigdy nie zostaniesz ponownie dopasowany do tej samej osoby.\n\nZadaniem Proponującego jest określenie, jaką część ze 100 dolarów zaoferować Reagującemu. Oferta może być dowolną liczbą całkowitą od 0 do 100. Jeśli oferta zostanie zaakceptowana, Reagujący otrzymuje zaproponowaną kwotę, a Proponujący zatrzymuje resztę.\n\nW tej grze Reagujący mogą mieć możliwość odrzucenia oferty (prawo weta). Prawdopodobieństwo przyznania tego prawa jest ustalane losowo. Na początku każdej rundy obaj gracze są informowani o tym prawdopodobieństwie (π).\n\nDecyzja Reagującego polega na wskazaniu minimalnej kwoty, jaką jest gotów przyjąć, zwanej \"progiem\" (Threshold). Jeśli Reagujący otrzyma prawo weta (z prawdopodobieństwem π) i oferta jest równa lub wyższa od progu, zostaje ona zaakceptowana. W przeciwnym razie obaj gracze otrzymują 0 dolarów. Jeśli weto nie zostanie przyznane, oferta Proponującego jest automatycznie realizowana.""",
    "Russian (Русский)": """В сегодняшнем эксперименте вам предстоит сыграть одну из двух ролей: Инициатор (Proposer) или Ответчик (Responder).\n\nВ каждом раунде Инициатор и Ответчик объединяются в пары, чтобы разделить сумму в 100 долларов. Компьютер распределяет участников случайным образом, поэтому пары меняются от раунда к раунду. Вы не сможете идентифицировать своего оппонента и никогда не будете повторно объединены в пару с тем же игроком.\n\nДля Инициатора задача состоит в том, чтобы определить, какую сумму из 100 долларов предложить Ответчику (целое число от 0 до 100). Если предложение принято, Ответчик получает предложенную сумму, а Инициатор оставляет себе остаток.\n\nВ этой игре у Ответчиков может быть возможность отклонить предложение (право вето). Вероятность того, что Ответчик получит такое право, определяется случайным образом. В начале каждого раунда оба игрока информируются об этой вероятности (π).\n\nДля Ответчика решение состоит в том, чтобы указать минимальную сумму, которую он/она готов принять — «порог» (Threshold). Если Ответчику предоставляется право вето (с вероятностью π) и предложение превышает или равно порогу, оно принимается. В противном случае оба игрока получают 0 долларов. Если право вето не предоставлено, предложение Инициатора реализуется автоматически.""",
    "Greek (Ελληνικά)": """Στο σημερινό πείραμα, υπάρχουν δύο πιθανοί ρόλοι: ο Προτείνων (Proposer) και ο Αποδέκτης (Responder).\n\nΣε κάθε γύρο, ένας Προτείνων και ένας Αποδέκτης συνδυάζονται για να αποφασίσουν πώς θα διαιρέσουν ένα ποσό 100 δολαρίων. Η αντιστοίχιση γίνεται τυχαία από τον υπολογιστή, έτσι ώστε τα ζευγάρια να αλλάζουν από γύρο σε γύρο. Δεν θα μπορείτε να αναγνωρίσετε τον αντίπαλό σας και δεν θα αντιστοιχηθείτε ποτέ ξανά με τον ίδιο παίκτη.\n\nΓια τον Προτείνοντα, η απόφαση είναι να καθορίσει πόσα από τα 100 δολάρια θα προσφέρει στον Αποδέκτη (ακέραιος αριθμός από 0 έως 100). Εάν η προσφορά γίνει αποδεκτή, ο Αποδέκτης λαμβάνει το προτεινόμενο ποσό και ο Προτείνων κρατά τα υπόλοιπα.\n\nΣε αυτό το παιχνίδι, είναι πιθανό ο Αποδέκτης να έχει την επιλογή να απορρίψει την προσφορά (δικαίωμα αρνησικυρίας / βέτο). Η πιθανότητα να έχει αυτή την επιλογή καθορίζεται τυχαία. Στην αρχή κάθε γύρου, και οι δύο παίκτες ενημερώνονται για αυτή την πιθανότητα (π).\n\nΓια τον Αποδέκτη, η απόφαση είναι να δηλώσει το ελάχιστο ποσό που είναι διατεθειμένος να αποδεχτεί, το οποίο αναφέρεται ως \"όριο αποδοχής\" (Threshold). Εάν ο Αποδέκτης έχει δικαίωμα βέτο (με πιθανότητα π) και η προσφορά είναι ίση ή μεγαλύτερη από το όριο, η προσφορά γίνεται αποδεκτή. Διαφορετικά, και οι δύο παίκτες λαμβάνουν 0. Εάν δεν δοθεί δικαίωμα βέτο, η προσφορά του Προτείνοντος εφαρμόζεται αυτόματα.""",
    "Turkish (Türkçe)": """Bugünkü deneyde üstlenebileceğiniz iki rol bulunmaktadır: Teklif Eden (Proposer) ve Yanıtlayan (Responder).\n\nHer turda, bir Teklif Eden ve bir Yanıtlayan, 100 dolarlık bir havuzu aralarında nasıl böleceklerini belirlemek üzere eşleştirilir. Bilgisayar eşleştirmeleri rastgele yapar, bu nedenle eşler turdan tura değişir. Rakibinizin kim olduğunu bilemezsiniz og aynı kişiyle asla tekrar eşleşmezsiniz.\n\nTeklif Eden için görev, 100 dolardan ne kadarını Yanıtlayan'a teklif edeceğini belirlemektir (0 ile 100 arasında bir tam sayı). Teklif kabul edilirse, Yanıtlayan teklif edilen miktarı alır, Teklif Eden ise kalan miktarı kendine saklar.\n\nBu oyunda Yanıtlayan'ın teklifi reddetme seçeneği (veto yetkisi) olabilir. Yanıtlayan'ın bu yetkiye sahip olma olasılığı rastgele belirlenir. Her turun başında hem Teklif Eden hem de Yanıtlayan bu olasılık (π) hakkında bilgilendirilir.\n\nYanıtlayan için karar, kabul etmeye hazır olduğu minimum miktarı, yani \"eşik değerini\" (Threshold) belirtmektir. Yanıtlayan'a veto hakkı verilir (π olasılığıyla) og teklif eşik değerine eşit veya ondan büyükse teklif kabul edilir. Aksi takdirde her iki oyuncu da 0 alır. Veto hakkı verilmezse, Teklif Eden'in teklifi doğrudan uygulanır.""",
    "Afrikaans (Afrikaans)": """In vandag se eksperiment is daar twee moontlike rolle wat jy kan speel: die Voorsteller (Proposer) en die Respondent (Responder).\n\nIn elke rondte sal een Voorsteller en een Respondent gepaar word om te besluit hoe om 'n poel van 100 dollar tussen hulle te verdeel. Die rekenaar kies die parings lukraak sodat dit van rondte tot rondte verander. Jy sal nie jou opponent kan identifiseer nie en sal nooit weer met dieselfde persoon gepaar word nie.\n\nVir 'n Voorsteller is die taak om te besluit hoeveel van die 100 dollar om vir die Respondent aan te bied (enige heelgetal van 0 tot 100). As die aanbod aanvaar word, kry die Respondent die voorgestelde bedrag en die Voorsteller hou die res.\n\nIn hierdie speletjie is dit moontlik dat die Respondent die opsie het om die aanbod te verwerp (vetoreg). Die waarskynlikheid dat 'n Respondent hierdie opsie sal kry, word lukraak bepaal. Aan die begin van elke rondte sal beide spelers ingelig word oor hierdie waarskynlikheid (π).\n\nVir die Respondent is die besluit om die minimum bedrag aan te dui wat hy/sy bereid is om te aanvaar, bekend as die \"drempel\" (Threshold). As die Respondent wel vetoreg kry (met waarskynlikheid π) en die aanbod is gelyk aan of hoër as die drempel, word dit aanvaar. Indien nie, kry beide spelers 0 dollar. As geen vetoreg toegestaan word nie, word die Voorsteller se aanbod outomaties toegepas.""",
    "Welsh (Cymraeg)": """Yn yr arbrawf heddiw, mae dwy rôl bosibl i chi eu chwarae: y Cynigydd (Proposer) ac y Sefydlydd (Responder).\n\nYm mhob rownd, bydd un Cynigydd ac un Sefydlydd yn cael eu paru i benderfynu sut i rannu cronfa o 100 doler rhyngddynt. Mae'r cyfrifiadur yn pennu'r paru ar hap fel bod y partneriaid yn newid o rownd i rownd. Ni fyddwch yn gallu nodi pwy yw eich gwrthwynebydd ac ni fyddwch byth yn cael eich paru â'r un person acen eto.\n\nAr gyfer Cynigydd, y penderfyniad yw faint o'r 100 doler i'w gynnig i'r Sefydlydd (unrhyw gyfanrif o 0 i 100). Os caiff y cynnig ei dderbyn, bydd y Sefydlydd yn cael y swm a gynigiwyd ac mae'r Cynigydd yn cadw'r gweddill.\n\nYn y gêm hon, mae'n bosibl i Sefydlydd gael yr opsiwn i wrthod y cynnig (hawl feto). Mae'r tebygolrwydd y bydd gan Sefydlydd yr opsiwn hwn yn cael ei benderfynu ar hap. Ar ddechrau pob rownd, bydd y ddau chwaraewr yn cael eu hysbysu o'r tebygolrwydd hwn (π).\n\nAr gyfer y Sefydlydd, y penderfyniad yw nodi'r swm lleiaf y mae'n fodlon ei dderbyn, sef y \"trothwy\" (Threshold). Os rhoddir hawl feto i'r Sefydlydd (gyda thebygolrwydd π) a bod y cynnig yn gyfartal neu'n fwy na'r trothwy, mae'r cynnig yn cael ei dderbyn. Fel arall, mae'r ddau chwaraewr yn cael 0. Os na roddir hawl feto, gweithredir cynnig y Cynigydd yn awtomatig."""
}

pdi_values = {
    "English": 0.35,
    "Simplified Chinese (简体中文)": 0.44,
    "Traditional Chinese (繁體中文)": 0.49,
    "Japanese (日本語)": 0.35,
    "French (Français)": 0.32,
    "German (Deutsch)": 0.21,
    "Spanish (Español)": 0.20,
    "Arabic (العربية)": 0.50,
    "Korean (한국어)": 0.22,
    "Indonesian (Bahasa Indonesia)": 0.28,
    "Italian (Italiano)": 0.19,
    "Polish (Polski)": 0.47,
    "Russian (Русский)": 0.36,
    "Greek (Ελληνικά)": 0.15,
    "Turkish (Türkçe)": 0.16,
    "Afrikaans (Afrikaans)": 0.26,
    "Welsh (Cymraeg)": 0.33
}

ui_translations = {
    "English": {
        "title": "Modified Ultimatum Game (The Power Game)",
        "welcome": "Welcome to the game! Please make your strategic choice below.",
        "role": "Your Assigned Role:",
        "proposer": "Proposer",
        "responder": "Responder",
        "assigned_pi": "Assigned Veto Probability (π):",
        "p_high": "High Power (90% chance of veto)",
        "p_low": "Low Power (10% chance of veto)",
        "input_offer": "How much out of 100 dollars would you like to offer to the Responder?",
        "input_threshold": "What is the minimum amount of money (out of 100) you are willing to accept if you have the veto option?",
        "submit": "Submit Decision",
        "result_title": "Round Results",
        "veto_enforced": "Was the Responder's veto option active in this round?",
        "yes": "Yes",
        "no": "No",
        "your_choice": "Your choice:",
        "opponent_choice": "Opponent's choice:",
        "outcome": "Outcome:",
        "accepted": "Accepted! The pool is split.",
        "rejected": "Rejected! Both players receive 0.",
        "payout": "Your payout:",
        "partner_payout": "Opponent's payout:"
    },
    "Simplified Chinese (简体中文)": {
        "title": "修改版最后通牒博弈（权力博弈）",
        "welcome": "欢迎进入博弈环节！请在下方做出您的战略决策。",
        "role": "您被分配的角色：",
        "proposer": "提议人 (Proposer)",
        "responder": "应答者 (Responder)",
        "assigned_pi": "被分配的否决权概率 (π)：",
        "p_high": "高权力 (90% 否决权概率)",
        "p_low": "低权力 (10% 否决权概率)",
        "input_offer": "您想提议分给应答者多少美元（范围：0至100）？",
        "input_threshold": "如果电脑赋予您否决权，您愿意接受的最低金额（最低接受额）是多少（范围：0至100）？",
        "submit": "提交决策",
        "result_title": "本轮博弈结果",
        "veto_enforced": "应答者的否决权在这一轮中是否被激活？",
        "yes": "是 (Yes)",
        "no": "否 (No)",
        "your_choice": "您的决策：",
        "opponent_choice": "对手的决策：",
        "outcome": "博弈结果：",
        "accepted": "接受提议！资金分配成功。",
        "rejected": "拒绝提议！双方本轮收益为0美元。",
        "payout": "您的收益：",
        "partner_payout": "对手的收益："
    },
    "Traditional Chinese (繁體中文)": {
        "title": "修改版最後通牒博弈（權力博弈）",
        "welcome": "歡迎進入博弈環節！請在下方做出您的戰略決策。",
        "role": "您被分配的角色：",
        "proposer": "提議人 (Proposer)",
        "responder": "應答者 (Responder)",
        "assigned_pi": "被分配的否決權概率 (π)：",
        "p_high": "高權力 (90% 否決權概率)",
        "p_low": "低權力 (10% 否決權概率)",
        "input_offer": "您想提議分給應答者多少美元（範圍：0至100）？",
        "input_threshold": "如果電腦賦予您否決權，您願意接受的最低金額（最低接受額）是多少（範圍：0至100）？",
        "submit": "提交決策",
        "result_title": "本輪博弈結果",
        "veto_enforced": "應答者的否決權在這一輪中是否被激活？",
        "yes": "是 (Yes)",
        "no": "否 (No)",
        "your_choice": "您的決策：",
        "opponent_choice": "對手的決策：",
        "outcome": "博弈結果：",
        "accepted": "接受提議！資金分配成功。",
        "rejected": "拒絕提議！雙方本輪收益為0美元。",
        "payout": "您的收益：",
        "partner_payout": "對手的收益："
    },
    "Japanese (日本語)": {
        "title": "修正版最後通牒ゲーム（パワーゲーム）",
        "welcome": "ゲームへようこそ！以下から戦略的な意思決定を行ってください。",
        "role": "あなたの役割：",
        "proposer": "提案者 (Proposer)",
        "responder": "応答者 (Responder)",
        "assigned_pi": "割り当てられた拒否権確率 (π)：",
        "p_high": "高パワー (90%の確率で拒否権発動)",
        "p_low": "低パワー (10%の確率で拒否権発動)",
        "input_offer": "100ドルのうち、応答者にいくら提示（オファー）しますか？（0〜100の整数）",
        "input_threshold": "拒否権が有効な場合、あなたが受け入れる最低金額（閾値）はいくらですか？（0〜100の整数）",
        "submit": "決定を送信",
        "result_title": "今回の対戦結果",
        "veto_enforced": "応答者の拒否権は発動しましたか？",
        "yes": "はい (Yes)",
        "no": "いいえ (No)",
        "your_choice": "あなたの決定：",
        "opponent_choice": "対戦相手の決定：",
        "outcome": "結果：",
        "accepted": "合意成立！資金が分配されました。",
        "rejected": "拒否！双方の取り分は0ドルとなりました。",
        "payout": "あなたの獲得額：",
        "partner_payout": "対戦相手の獲得額："
    },
    "French (Français)": {
        "title": "Jeu de l'Ultimatum Modifié (Le Jeu du Pouvoir)",
        "welcome": "Bienvenue dans le jeu ! Veuillez faire votre choix stratégique ci-dessous.",
        "role": "Votre Rôle Assigné :",
        "proposer": "Proposeur (Proposer)",
        "responder": "Répondant (Responder)",
        "assigned_pi": "Probabilité de Veto Assignée (π) :",
        "p_high": "Pouvoir Élevé (90% de chance de veto)",
        "p_low": "Pouvoir Faible (10% de chance de veto)",
        "input_offer": "Combien sur la cagnotte de 100 dollars souhaitez-vous offrir au Répondant ?",
        "input_threshold": "Quel est le montant minimum (sur 100) que vous êtes prêt à accepter si vous avez l'option de veto ?",
        "submit": "Soumettre la Décision",
        "result_title": "Résultats du Tour",
        "veto_enforced": "L'option de veto du Répondant a-t-elle été activée ce tour-ci ?",
        "yes": "Oui (Yes)",
        "no": "Non (No)",
        "your_choice": "Votre choix :",
        "opponent_choice": "Choix de l'adversaire :",
        "outcome": "Résultat :",
        "accepted": "Accepté ! La cagnotte est divisée.",
        "rejected": "Rejeté ! Les deux joueurs reçoivent 0 $.",
        "payout": "Votre gain :",
        "partner_payout": "Gain de l'adversaire :"
    },
    "German (Deutsch)": {
        "title": "Modifiziertes Ultimatum-Spiel (Das Macht-Spiel)",
        "welcome": "Willkommen zum Spiel! Bitte treffen Sie unten Ihre strategische Entscheidung.",
        "role": "Ihre zugewiesene Rolle:",
        "proposer": "Antragssteller (Proposer)",
        "responder": "Empfänger (Responder)",
        "assigned_pi": "Zugewiesene Veto-Wahrscheinlichkeit (π):",
        "p_high": "Hohe Macht (90% Veto-Chance)",
        "p_low": "Geringe Macht (10% Veto-Chance)",
        "input_offer": "Wie viel von den 100 Dollar möchten Sie dem Empfänger anbieten?",
        "input_threshold": "Was ist der Mindestbetrag (von 100), den Sie bereit sind zu akzeptieren, wenn Sie das Vetorecht haben?",
        "submit": "Entscheidung senden",
        "result_title": "Ergebnis der Runde",
        "veto_enforced": "War das Veto-Recht des Empfängers in dieser Runde aktiv?",
        "yes": "Ja (Yes)",
        "no": "Nein (No)",
        "your_choice": "Ihre Entscheidung:",
        "opponent_choice": "Entscheidung des Gegners:",
        "outcome": "Ergebnis:",
        "accepted": "Angenommen! Der Betrag wurde aufgeteilt.",
        "rejected": "Abgelehnt! Beide Spieler erhalten 0 $.",
        "payout": "Ihr Gewinn:",
        "partner_payout": "Gewinn des Gegners:"
    },
    "Spanish (Español)": {
        "title": "Juego del Ultimátum Modificado (El Juego del Poder)",
        "welcome": "¡Bienvenido al juego! Por favor, tome su decisión estratégica a continuación.",
        "role": "Su Rol Asignado:",
        "proposer": "Proponente (Proposer)",
        "responder": "Receptor (Responder)",
        "assigned_pi": "Probabilidad de Veto Asignada (π):",
        "p_high": "Poder Alto (90% de probabilidad de veto)",
        "p_low": "Poder Bajo (10% de probabilidad de veto)",
        "input_offer": "¿Cuánto de los 100 dólares desea ofrecer al Receptor?",
        "input_threshold": "¿Cuál es la cantidad mínima (de 100) que está dispuesto a aceptar si tiene la opción de veto?",
        "submit": "Enviar Decisión",
        "result_title": "Resultados de la Ronda",
        "veto_enforced": "¿Se activó la opción de veto del Receptor en esta ronda?",
        "yes": "Sí (Yes)",
        "no": "No (No)",
        "your_choice": "Su decisión:",
        "opponent_choice": "Decisión del oponente:",
        "outcome": "Resultado:",
        "accepted": "¡Aceptado! Se divide el fondo.",
        "rejected": "¡Rechazado! Ambos jugadores reciben 0 $.",
        "payout": "Su ganancia:",
        "partner_payout": "Ganancia del oponente:"
    }
}

# Helper to retrieve UI translations with a safe fallback to English
def get_ui_text(lang_key, key_name):
    # Map raw language name to translation key
    clean_key = "English"
    for k in ui_translations.keys():
        if k in lang_key:
            clean_key = k
            break
    return ui_translations[clean_key].get(key_name, ui_translations["English"][key_name])

# ----------------------------------------------------
# 3. Sidebar Instructor Controls
# ----------------------------------------------------
st.sidebar.image("https://upload.wikimedia.org/wikipedia/commons/e/e2/San_Jose_State_University_seal.svg", width=80)
st.sidebar.title("Instructor Command Center")
st.sidebar.write("EMBA International Course Facilitation")

st.sidebar.markdown("---")
st.sidebar.subheader("⚙️ Classroom Experiment Settings")

pi_assignment_mode = st.sidebar.radio(
    "Veto Probability (π) Assignment Mode:",
    options=["Automatic Split (50% Low, 50% High π)", "Manual Student Choice"],
    index=0,
    help="Automatic mode distributes half the students to π = 0.1 and half to π = 0.9 based on Student ID."
)

st.sidebar.info("""
**Research Parameters in Play (from your paper):**
- **Low Power condition:** π = 0.10 (10% Veto probability)
- **High Power condition:** π = 0.90 (90% Veto probability)
- **Pool Size:** 100 USD
""")

st.sidebar.markdown("---")
st.sidebar.subheader("🛠️ Step-by-Step Lesson Plan")
st.sidebar.info("""
1. **Instruction Calibration (15 mins)**: Students view instructions, select native languages, and submit audits.
2. **Interactive Gameplay (20 mins)**: Students play in their selected language to experience strategic veto power first-hand!
3. **Course Analytics (15 mins)**: Project the Live Instructor tab to analyze rating variances and play payoffs!
4. **Research presentation (10 mins)**: Connect outcomes to GLOBE Power Distance findings in your slides.
""")

st.sidebar.markdown("---")
st.sidebar.subheader("🔧 Dynamic Translation Customizer")

if 'custom_translations' not in st.session_state:
    st.session_state.custom_translations = default_translations.copy()

selected_custom_lang = st.sidebar.selectbox("Select Language to Customize:", list(default_translations.keys()))

custom_text = st.sidebar.text_area(
    f"Edit instructions for {selected_custom_lang}:",
    value=st.session_state.custom_translations[selected_custom_lang],
    height=150
)

if st.sidebar.button("💾 Save Translation Updates"):
    st.session_state.custom_translations[selected_custom_lang] = custom_text
    st.sidebar.success(f"Updated translation for {selected_custom_lang}!")

# ----------------------------------------------------
# 4. Main Title and Navigation Tab Structures
# ----------------------------------------------------
st.markdown("<h1 style='color: #1e3d59; font-size: 34px;'>⚖️ EMBA Course Facilitator: The Power Game</h1>", unsafe_allow_html=True)
st.markdown("##### Bridging Culture, Language, and Distributive Fairness in International Negotiations")
st.markdown("---")

tab1, tab2, tab3 = st.tabs([
    "🌎 STEP 1: Language & Evaluation", 
    "🎮 STEP 2: Play the Power Game", 
    "📊 STEP 3: Instructor Course Analytics"
])

# ----------------------------------------------------
# Tab 1: STEP 1 - Instruction Calibration
# ----------------------------------------------------
with tab1:
    st.markdown("### Part 1: Linguistic Relativity & Instruction Calibration Portal")
    st.markdown("""
    Welcome to the calibration step. Before we launch into the bilateral bargaining simulation, 
    every international executive should verify that they fully comprehend the rules. 
    
    Choose your preferred language to read the game rules side-by-side with the English baseline. 
    Then, submit your rating on clarity and naturalness.
    """)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("<h4 style='color: #17b978;'>1. English Rules (Baseline)</h4>", unsafe_allow_html=True)
        st.info(st.session_state.custom_translations["English"])
        
    with col2:
        st.markdown("<h4 style='color: #17b978;'>2. Localized Rules (Your Target Language)</h4>", unsafe_allow_html=True)
        
        student_lang_select = st.selectbox(
            "Select your native or preferred language to inspect:",
            options=[l for l in list(default_translations.keys()) if l != "English"],
            index=1 # Default to Simplified Chinese
        )
        
        # Save chosen language to session state so Tab 2 adapts automatically
        st.session_state.selected_lang = student_lang_select
        
        st.success(st.session_state.custom_translations[student_lang_select])

    st.markdown("---")
    st.markdown("<h4 style='color: #1e3d59;'>✍️ Student Calibration Feedback</h4>", unsafe_allow_html=True)
    st.markdown("Submit your feedback below. This evaluation form measures translation naturalness without disclosing underlying research hypotheses to avoid priming.")
    
    with st.form("feedback_form"):
        col_id1, col_id2 = st.columns([1, 2])
        with col_id1:
            eval_student_id = st.text_input("Anonymous Student ID:", value=st.session_state.current_student_id, placeholder="e.g. EMBA_12")
            if eval_student_id:
                st.session_state.current_student_id = eval_student_id
        
        col_r1, col_r2 = st.columns(2)
        with col_r1:
            st.markdown("**Question 1: Rules Clarity**")
            q1_rating = st.radio(
                "On a scale of 1-5, how clear were the game rules to you?",
                options=[1, 2, 3, 4, 5],
                index=4,
                horizontal=True,
                help="1 = Completely Confusing, 5 = Extremely Clear"
            )
        with col_r2:
            st.markdown("**Question 2: Translation Naturalness**")
            q2_rating = st.radio(
                "On a scale of 1-5, how natural and appropriate was the localized translation?",
                options=[1, 2, 3, 4, 5],
                index=4,
                horizontal=True,
                help="1 = Unnatural/Incorrect, 5 = Flawless and Culturally Natural"
            )
            
        st.markdown("**Question 3: Qualitative Translation Audit**")
        comments = st.text_area(
            "Please comment on where the translation is not accurate or point out specific terms that could be refined:",
            placeholder="e.g., 'In paragraph 4, the word used for veto feels too formal. It is better to use...' (Optional)"
        )
        
        submit_btn = st.form_submit_button("📤 Submit Evaluation Feedback")
        
        if submit_btn:
            if not eval_student_id:
                st.error("Please enter a Student ID before submitting.")
            else:
                new_entry = {
                    "Timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "Student_ID": eval_student_id,
                    "Language": student_lang_select,
                    "Q1_Clarity_Rating": q1_rating,
                    "Q2_Naturalness_Rating": q2_rating,
                    "Translation_Comments": comments if comments else "No comments."
                }
                st.session_state.responses.append(new_entry)
                st.balloons()
                st.success(f"Thank you, {eval_student_id}! Your feedback has been recorded successfully. Please proceed to STEP 2.")

# ----------------------------------------------------
# Tab 2: STEP 2 - Interactive Game Play (Localized)
# ----------------------------------------------------
with tab2:
    selected_lang_play = st.session_state.selected_lang
    st.markdown(f"### {get_ui_text(selected_lang_play, 'title')}")
    st.markdown(f"*{get_ui_text(selected_lang_play, 'welcome')}*")
    st.markdown("---")
    
    # Check student ID
    if not st.session_state.current_student_id:
        st.warning("⚠️ Please enter your Anonymous Student ID in Tab 1 (Step 1) before playing!")
        st.stop()
        
    student_id = st.session_state.current_student_id
    
    # Resolve Assigned Veto Probability (pi)
    assigned_pi = 0.5 # fallback
    if pi_assignment_mode == "Automatic Split (50% Low, 50% High π)":
        # Hash student ID to divide cleanly 50/50
        try:
            numeric_part = int(''.join(filter(str.isdigit, student_id)))
            assigned_pi = 0.1 if numeric_part % 2 == 0 else 0.9
        except ValueError:
            # Fallback if no digits in ID
            assigned_pi = 0.1 if len(student_id) % 2 == 0 else 0.9
    else:
        # Manual Mode: Let students select their assigned probability
        assigned_pi_select = st.radio(
            "Select your assigned Veto Probability condition (provided by instructor):",
            options=[0.1, 0.9],
            format_func=lambda x: "π = 0.10 (Low Veto Power)" if x == 0.1 else "π = 0.90 (High Veto Power)",
            horizontal=True
        )
        assigned_pi = assigned_pi_select
        
    # Language culture PDI factor
    lang_pdi = pdi_values.get(selected_lang_play, 0.35)
    
    # Game setup layout
    col_play1, col_play2 = st.columns([1, 1])
    
    with col_play1:
        st.markdown(f"##### 👤 **Player ID:** `{student_id}`")
        st.markdown(f"##### 🌎 **Language Mode:** `{selected_lang_play}`")
        st.markdown(f"##### 🎯 **{get_ui_text(selected_lang_play, 'assigned_pi')}** `π = {assigned_pi:.2f}`")
        if assigned_pi == 0.9:
            st.info(get_ui_text(selected_lang_play, "p_high"))
        else:
            st.info(get_ui_text(selected_lang_play, "p_low"))
            
        st.markdown("---")
        st.markdown(f"#### 🎭 **{get_ui_text(selected_lang_play, 'role')}**")
        student_role = st.selectbox(
            "Choose your role for this round:",
            options=["Proposer", "Responder"],
            format_func=lambda x: get_ui_text(selected_lang_play, 'proposer') if x == "Proposer" else get_ui_text(selected_lang_play, 'responder')
        )
        
    with col_play2:
        st.markdown("#### ⚡ **Submit Your Strategy**")
        
        # We wrap the gameplay actions inside an input block
        if student_role == "Proposer":
            # Input offer
            user_offer = st.number_input(
                get_ui_text(selected_lang_play, 'input_offer'),
                min_value=0, max_value=100, value=35, step=1
            )
            
            if st.button(get_ui_text(selected_lang_play, 'submit'), key="btn_proposer"):
                # Simulate empirical Responder threshold based on selected language and PDI
                # From paper: higher power distance correlates with higher thresholds. 
                # Let's write a realistic threshold response:
                base_threshold = 20 if assigned_pi == 0.1 else 30
                # Add PDI scaling effect
                calibrated_threshold = int(base_threshold + (25 * lang_pdi))
                # Add a touch of behavioral variance (randomness)
                opponent_threshold = min(100, max(0, calibrated_threshold + random.randint(-4, 4)))
                
                # Resolve veto activation by coin toss
                veto_enforced = "Yes" if random.random() < assigned_pi else "No"
                
                # Resolve outcomes
                if veto_enforced == "No":
                    outcome = "Accepted"
                    student_payout = 100 - user_offer
                    opponent_payout = user_offer
                else:
                    if user_offer >= opponent_threshold:
                        outcome = "Accepted"
                        student_payout = 100 - user_offer
                        opponent_payout = user_offer
                    else:
                        outcome = "Rejected"
                        student_payout = 0
                        opponent_payout = 0
                        
                # Log outcome in session state
                st.session_state.game_logs.append({
                    "Timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "Student_ID": student_id,
                    "Language": selected_lang_play,
                    "Role": "Proposer",
                    "Power_Prob_Pi": assigned_pi,
                    "Offer": user_offer,
                    "Threshold": opponent_threshold,
                    "Veto_Enforced": veto_enforced,
                    "Outcome": outcome,
                    "Student_Payout": student_payout,
                    "Opponent_Payout": opponent_payout
                })
                
                # Show results card
                st.markdown("---")
                st.markdown(f"### 📋 {get_ui_text(selected_lang_play, 'result_title')}")
                
                col_res1, col_res2 = st.columns(2)
                with col_res1:
                    st.metric(get_ui_text(selected_lang_play, 'your_choice') + f" ({get_ui_text(selected_lang_play, 'proposer')})", f"{user_offer} USD")
                    st.metric(get_ui_text(selected_lang_play, 'opponent_choice') + f" ({get_ui_text(selected_lang_play, 'responder')})", f"{opponent_threshold} USD")
                with col_res2:
                    st.metric(get_ui_text(selected_lang_play, 'veto_enforced'), get_ui_text(selected_lang_play, 'yes') if veto_enforced == "Yes" else get_ui_text(selected_lang_play, 'no'))
                    
                    if outcome == "Accepted":
                        st.success(get_ui_text(selected_lang_play, 'accepted'))
                    else:
                        st.error(get_ui_text(selected_lang_play, 'rejected'))
                        
                st.markdown(f"💰 **{get_ui_text(selected_lang_play, 'payout')}** `{student_payout} USD` | **{get_ui_text(selected_lang_play, 'partner_payout')}** `{opponent_payout} USD`")
                if outcome == "Accepted":
                    st.balloons()
                    
        else: # Student is Responder
            user_threshold = st.number_input(
                get_ui_text(selected_lang_play, 'input_threshold'),
                min_value=0, max_value=100, value=30, step=1
            )
            
            if st.button(get_ui_text(selected_lang_play, 'submit'), key="btn_responder"):
                # Simulate empirical Proposer offer based on language PDI
                # Higher power distance/PDI = higher offer
                base_offer = 22 if assigned_pi == 0.1 else 32
                calibrated_offer = int(base_offer + (25 * lang_pdi))
                opponent_offer = min(100, max(0, calibrated_offer + random.randint(-5, 5)))
                
                # Resolve veto activation by coin toss
                veto_enforced = "Yes" if random.random() < assigned_pi else "No"
                
                # Resolve outcomes
                if veto_enforced == "No":
                    outcome = "Accepted"
                    student_payout = opponent_offer
                    opponent_payout = 100 - opponent_offer
                else:
                    if opponent_offer >= user_threshold:
                        outcome = "Accepted"
                        student_payout = opponent_offer
                        opponent_payout = 100 - opponent_offer
                    else:
                        outcome = "Rejected"
                        student_payout = 0
                        opponent_payout = 0
                        
                # Log outcome
                st.session_state.game_logs.append({
                    "Timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "Student_ID": student_id,
                    "Language": selected_lang_play,
                    "Role": "Responder",
                    "Power_Prob_Pi": assigned_pi,
                    "Offer": opponent_offer,
                    "Threshold": user_threshold,
                    "Veto_Enforced": veto_enforced,
                    "Outcome": outcome,
                    "Student_Payout": student_payout,
                    "Opponent_Payout": opponent_payout
                })
                
                # Show results card
                st.markdown("---")
                st.markdown(f"### 📋 {get_ui_text(selected_lang_play, 'result_title')}")
                
                col_res1, col_res2 = st.columns(2)
                with col_res1:
                    st.metric(get_ui_text(selected_lang_play, 'your_choice') + f" ({get_ui_text(selected_lang_play, 'responder')})", f"{user_threshold} USD")
                    st.metric(get_ui_text(selected_lang_play, 'opponent_choice') + f" ({get_ui_text(selected_lang_play, 'proposer')})", f"{opponent_offer} USD")
                with col_res2:
                    st.metric(get_ui_text(selected_lang_play, 'veto_enforced'), get_ui_text(selected_lang_play, 'yes') if veto_enforced == "Yes" else get_ui_text(selected_lang_play, 'no'))
                    
                    if outcome == "Accepted":
                        st.success(get_ui_text(selected_lang_play, 'accepted'))
                    else:
                        st.error(get_ui_text(selected_lang_play, 'rejected'))
                        
                st.markdown(f"💰 **{get_ui_text(selected_lang_play, 'payout')}** `{student_payout} USD` | **{get_ui_text(selected_lang_play, 'partner_payout')}** `{opponent_payout} USD`")
                if outcome == "Accepted":
                    st.balloons()

# ----------------------------------------------------
# Tab 3: STEP 3 - Instructor Course Analytics
# ----------------------------------------------------
with tab3:
    st.markdown("<h3 style='color: #1e3d59;'>📊 Live Classroom Research & Analytics Panel</h3>", unsafe_allow_html=True)
    st.markdown("""
    This control panel allows the facilitator to monitor ratings of different language instructions 
    and track gameplay allocations across classes in real-time.
    """)
    
    # Layout sections
    sub_tab1, sub_tab2 = st.tabs(["📝 1. Instruction Evaluation Logs", "🎮 2. Gameplay Outcome Logs"])
    
    with sub_tab1:
        st.markdown("#### Dynamic Translation Evaluations")
        df_responses = pd.DataFrame(st.session_state.responses)
        
        if not df_responses.empty:
            col_stat1, col_stat2, col_stat3 = st.columns(3)
            with col_stat1:
                st.metric("Total Evaluations", len(df_responses))
            with col_stat2:
                st.metric("Avg Clarity Rating (Q1)", f"{df_responses['Q1_Clarity_Rating'].mean():.2f} / 5.00")
            with col_stat3:
                st.metric("Avg Naturalness (Q2)", f"{df_responses['Q2_Naturalness_Rating'].mean():.2f} / 5.00")
                
            st.markdown("---")
            st.dataframe(df_responses, use_container_width=True)
            
            # Export CSV
            csv_eval = df_responses.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Download Translation Evaluations (.CSV)",
                data=csv_eval,
                file_name=f"emba_classroom_evaluations_{datetime.date.today().strftime('%Y_%m_%d')}.csv",
                mime="text/csv",
                key="dl_eval"
            )
        else:
            st.info("No translation feedback recorded yet.")
            
    with sub_tab2:
        st.markdown("#### Live Course Gameplay Ledgers")
        df_games = pd.DataFrame(st.session_state.game_logs)
        
        if not df_games.empty:
            col_g1, col_g2, col_g3 = st.columns(3)
            with col_g1:
                st.metric("Total Trials Played", len(df_games))
            with col_g2:
                # Average offer from student proposer rounds
                proposer_only = df_games[df_games['Role'] == "Proposer"]
                if not proposer_only.empty:
                    st.metric("Mean Proposer Offer (USD)", f"${proposer_only['Offer'].mean():.1f}")
                else:
                    st.metric("Mean Proposer Offer (USD)", "N/A")
            with col_g3:
                # Average threshold from student responder rounds
                responder_only = df_games[df_games['Role'] == "Responder"]
                if not responder_only.empty:
                    st.metric("Mean Responder Threshold (USD)", f"${responder_only['Threshold'].mean():.1f}")
                else:
                    st.metric("Mean Responder Threshold (USD)", "N/A")
                    
            st.markdown("---")
            st.dataframe(df_games, use_container_width=True)
            
            # Classroom Analysis Plotly Scatter
            st.markdown("##### 📈 Culture and Allocation Analysis (Classroom vs. Theory)")
            st.markdown("""
            This plot automatically places your students' offers side-by-side with the GLOBE Power Distance 
            Indices to verify if high Power Distance languages (like Chinese/Arabic) elicit more generous offers 
            under bargaining structures than low Power Distance languages.
            """)
            
            # Map PDI scores to the dataframe
            df_games['Power_Distance_Index'] = df_games['Language'].map(pdi_values)
            
            fig_classroom = px.scatter(
                df_games,
                x="Power_Distance_Index",
                y="Offer",
                color="Role",
                size="Student_Payout",
                hover_data=["Student_ID", "Language", "Power_Prob_Pi"],
                labels={
                    "Power_Distance_Index": "GLOBE Power Distance Index (PDI)",
                    "Offer": "Bargaining Offer Amount (USD)"
                },
                title="Proposer Offers vs. Language Power Distance Index",
                trendline="ols" if len(df_games) > 4 else None,
                template="plotly_white"
            )
            st.plotly_chart(fig_classroom, use_container_width=True)
            
            # Export CSV
            csv_game = df_games.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Download Student Gameplay Records (.CSV)",
                data=csv_game,
                file_name=f"emba_power_game_trials_{datetime.date.today().strftime('%Y_%m_%d')}.csv",
                mime="text/csv",
                key="dl_game"
            )
        else:
            st.info("No gameplay rounds completed yet. Student choices will appear here instantly upon submission.")
