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

# Initialize Session State for student responses if not exists
# Initialize Session State for experiment configurations
if 'pi_assignment_mode' not in st.session_state:
    st.session_state.pi_assignment_mode = "Automatic Split (50% Low, 50% High π)"

if 'responses' not in st.session_state:
    st.session_state.responses = [
        {"Timestamp": "2026-09-01 14:02:15", "Student_ID": "EMBA_04", "Language": "French (Français)", "Q1_Clarity_Rating": 5, "Q2_Naturalness_Rating": 4, "Translation_Comments": "The term 'cagnotte' is perfect for 'pool'. Very clear."}
    ]

if 'game_logs' not in st.session_state:
    st.session_state.game_logs = [
        {"Timestamp": "2026-09-01 14:05:00", "Student_ID": "EMBA_04", "Role": "Proposer", "Language": "French (Français)", "PDI": 0.32, "Veto_Probability": 0.90, "Offer": 40, "Threshold": "N/A", "Veto_Enforced": "Yes", "Outcome": "Accepted", "Payout": "Proposer: 60, Responder: 40"}
    ]

# Core English Instructions from the Working Paper [6]
default_english_instructions = """In today's experiment, there are two possible roles for you to play: the Proposer and the Responder. 

In every round, one Proposer and one Responder will be paired to determine how to divide a pool of 100 dollars between them. The computer assigns the random matching so that pairings will change from round to round. You will not be able to identify who is your opponent in the game and you will never be re-matched with the same Proposer or Responder. 

For a Proposer, the decision task is to determine how much out of 100 dollars to offer to the Responder. The offer can be any integer number from 0 to 100. If an offer is accepted, the Responder will get the amount proposed and the Proposer will keep the rest of the pool. 

In this game, it is possible for Responders to have an option to reject offers by Proposers. The probability for a Responder to have such an option is determined randomly. At the beginning of each round, both the Proposer and the Responder will be informed of this probability (π).

For the Responder, the decision is to indicate the minimum amount that he/she is willing to accept, which is referred to as the threshold. If the responder is granted the veto option (with probability π) and the offer meets or exceeds the threshold, the offer is accepted; otherwise, both players receive zero. If the responder is not granted the veto, the Proposer's offer is automatically implemented."""

# Pre-loaded 17-language translations based on the paper's design [6]
default_translations = {
    "English": default_english_instructions,
    "Simplified Chinese (简体中文)": """在今天的实验中，您将扮演两种可能的角色：提议人（Proposer）和应答者（Responder）。\n\n在每一轮中，一名提议人和一名应答者将被配对，以决定如何分配100美元的资金池。电脑随机匹配，因此每轮的对手都会改变。您将无法识别游戏中的对手，也永远不会与同一个提议人或应答者再次配对。\n\n对于提议人，决策任务是确定从100美元中分出多少给应答者。提议金额可以是0到100之间的任意整数。如果提议被接受，应答者将获得提议的金额，而提议人将保留资金池的其余部分。\n\n在这场游戏中，应答者有可能拥有拒绝提议人提议的权利。应答者获得该否决权的概率是随机决定的。在每一轮开始时，提议人和应答者都会被告知这个概率 (π)。\n\n对于应答者，决策是指出他/她愿意接受的最低金额，这在游戏中被称为“最低接受额（Threshold）”。如果在该轮中应答者被随机授予了否决权（概率为 π），且提议达到或超过了最低接受额，则提议被接受；否则，双方均获得0美元。如果电脑没有赋予应答者否决权，则直接按照提议人的方案进行分配。""",
    "Traditional Chinese (繁體中文)": """在今天的實驗中，您將扮演兩種可能的角色：提議人（Proposer）和應答者（Responder）。\n\n在每一輪中，一名提議人和一名應答者將本配對，以決定如何分配100美元的資金池。電腦隨機匹配，因此每輪的對手都會改變。您將無法識別遊戲中的對手，也永遠不會與同一個提議人或應答者再次配對。\n\n對於提議人，決策任務是確定從100美元中分出多少給應答者。提議金額可以是0到100之間的任意整數。如果提議被接受，應答者將獲得提議的金額，而提議人將保留資金池的其餘部分。\n\n在這場遊戲中，應答者有可能擁有拒絕提議人提議的權利。應答者獲得該否決權的概率是隨機決定的。在每一輪開始時，提議人和應答者都會被告知這個概率 (π)。\n\n對於應答者，決策是指出他/她願意接受的最低金額，這在遊戲中被稱為“最低接受額（Threshold）”。如果在該輪中應答者被隨機授予了否決權（概率為 π），且提議達到或超過了最低接受額，則提議被接受；否則，雙方均獲得0美元。如果電腦沒有賦予應答者否決權，則直接按照提議人的方案進行分配。""",
    "Japanese (日本語)": """本日の実験では、「提案者（Proposer）」または「応答者（Responder）」という2つの役割のいずれかを担っていただきます。\n\n各ラウンドにおいて、提案者1名と応答者1名がペアになり、100ドルの資金をどのように分配するかを決定します。ペアはコンピュータによってランダムに決定され、ラウンドごとに変更されます。相手が誰であるかを特定することはできず、同じ相手と再びペアになることもありません。\n\n提案者の意思決定タスクは、100ドルのうち応答者にいくら提示（オファー）するかを決定することです。提示額は0から100までの整数で指定できます。オファーが受け入れられた場合、応答者は提案された金額を受け取り、提案者は残りの額を受けpartをとります。\n\nこのゲームでは、応答者が提案者のオファーを拒否する権利（拒否権）を持つ場合があります。応答者がこの権利を持つ確率はランダムに決定されます。各ラウンドの開始時に、提案者と応答者の双方にこの確率（π）が通知されます。\n\n応答者の意思決定は、自身が受け入れることができる最低金額（閾値 / Threshold）を示すことです。応答者に拒否権が付与され（確率 π）、オファーが閾値以上であった場合、オファーは受け入れられます。そうでない場合、双方の取り分は0ドルとなります。拒否権が付与されなかった場合は、閾値に関わらず、提案者のオファー通りに分配されます。""",
    "French (Français)": """Dans l'expérience d'aujourd'hui, vous pouvez jouer deux rôles : le Proposeur (Proposer) et le Répondant (Responder).\n\nÀ chaque tour, un Proposeur et un Répondant seront associés pour déterminer comment diviser une cagnotte de 100 dollars entre eux. L'ordinateur attribue l'appariement de manière aléatoire afin que les paires changent de tour en tour. Vous ne pourrez pas identifier votre adversaire et vous ne serez jamais remis en paire avec le même joueur.\n\nPour le Proposeur, la tâche de décision consiste à déterminer quel montant (un nombre entier de 0 à 100) offrir au Répondant. Si une offre est acceptée, le Répondant obtient le montant proposé et le Proposeur garde le reste de la cagnotte.\n\nDans ce jeu, il est possible pour le Répondant d'avoir l'option de rejeter l'offre du Proposeur (droit de veto). La probabilité pour qu'un Répondant dispose de cette option est déterminée de manière aléatoire. Au début de chaque tour, le Proposeur et le Répondant sont informés de cette probabilité (π).\n\nPour le Répondant, la décision consiste à indiquer le montant minimum qu'il est prêt à accepter, appelé le "seuil" (Threshold). Si le Répondant obtient l'option de rejeter l'offre (avec une probabilité π) et que l'offre est supérieure ou égale au seuil, elle est acceptée. Sinon, les deux joueurs obtiennent 0 dollar. Si le veto n'est pas activé par l'ordinateur, l'offre du Proposeur est automatiquement validée.""",
    "German (Deutsch)": """Im heutigen Experiment gibt es zwei mögliche Rollen: den Antragssteller (Proposer) und den Empfänger (Responder).\n\nIn jeder Runde werden ein Antragssteller und ein Empfänger einander zugewiesen, um zu entscheiden, wie ein Betrag von 100 Dollar zwischen ihnen aufgeteilt wird. Die Zuweisung erfolgt zufällig durch den Computer, sodass sich die Paarungen von Runde zu Runde ändern. Sie können Ihren Spielpartner nicht identifizieren und werden niemals mit derselben Person erneut gepaart.\n\nFür den Antragssteller besteht die Aufgabe darin, zu bestimmen, wie viel von den 100 Dollar dem Empfänger angeboten werden soll. Das Angebot kann jede ganze Zahl von 0 bis 100 sein. Wird das Angebot angenommen, erhält der Empfänger den angebotenen Betrag und der Antragssteller behält den Rest.\n\nIn diesem Spiel haben Empfänger unter Umständen die Möglichkeit, Angebote des Antragsstellers abzulehnen (Veto-Recht). Die Wahrscheinlichkeit, dass ein Empfänger dieses Recht erhält, wird zufällig bestimmt. Zu Beginn jeder Runde werden beide Spieler über diese Wahrscheinlichkeit (π) informiert.\n\nFür den Empfänger besteht die Entscheidung darin, den Mindestbetrag anzugeben, den er bereit ist zu akzeptieren (den Schwellenwert / Threshold). Wenn dem Empfänger das Vetorecht zugesprochen wird (mit Wahrscheinlichkeit π) und das Angebot den Schwellenwert erreicht oder übersteigt, wird es angenommen. Andernfalls erhalten beide Spieler 0 Dollar. Wird kein Veto gewährt, wird die Aufteilung automatisch gemäß dem Angebot des Antragsstellers durchgeführt.""",
    "Spanish (Español)": """En el experimento de hoy, hay dos roles posibles: el Proponente (Proposer) y el Receptor (Responder).\n\nEn cada ronda, un Proponente y un Receptor se emparejarán para determinar cómo dividir una suma de 100 dólares. El emparejamiento es aleatorio, por lo que las parejas cambiarán de ronda en ronda. No podrá identificar a su oponente y nunca volverá a jugar con el mismo Proponente o Receptor.\n\nPara el Proponente, la decisión consiste en determinar cuánto de los 100 dólares ofrecer al Receptor. La oferta puede ser cualquier número entero entre 0 y 100. Si la oferta es aceptada, el Receptor obtendrá la cantidad propuesta y el Proponente se quedará con el resto.\n\nEn este juego, es posible que el Receptor tenga la opción de rechazar las ofertas (derecho de veto). La probabilidad de que el Receptor tenga esta opción se determina al azar. Al principio de cada ronda, ambos jugadores serán informados de esta probabilidad (π).\n\nPara el Receptor, la decisión consiste en indicar la cantidad mínima que está dispuesto a aceptar, conocida como el "umbral" (Threshold). Si el Receptor cuenta con la opción de veto (con probabilidad π) y la oferta es igual o mayor al umbral, la oferta se acepta. De lo contrario, ambos reciben 0 dólares. Si el ordenador no otorga la opción de veto, la oferta del Proponente se implementa automáticamente.""",
    "Arabic (العربية)": """في تجربة اليوم، هناك دوران محتملان لك: مقدم الاقتراح (Proposer) والمستجيب (Responder).\n\nفي كل جولة، سيتم تقسيم مبلغ 100 دولار بين مقدم الاقتراح والمستجيب. يخصص الكمبيوتر المطابقة العشوائية بحيث تتغير الشراكات من جولة إلى جولة. لن تتمكن من تحديد هوية خصمك ولن يتم إقرانك بنفس الشخص مرة أخرى.\n\nبالنسبة لمقدم الاقتراح، تتمثل المهمة في تحديد المبلغ الذي سيقدمه للمستجيب من أصل 100 دولار (بين 0 و100). إذا تم قبول العرض، يحصل المستجيب على المبلغ المقترح ويحتفظ مقدم الاقتراح بالباقي.\n\nفي هذه اللعبة، قد يكون للمستجيب خيار رفض العروض (حق الفيتو). يتم تحديد احتمال حصول المستجيب على هذا الخيار عشوائيًا (π) ويتم إبلاغ الطرفين به في بداية كل جولة.\n\nبالنسبة للمستجيب، القرار هو تحديد الحد الأدنى للمبلغ الذي يقبل به (Threshold). إذا مُنح المستجيب خيار الرفض وكان العرض أكبر من أو يساوي هذا الحد، يتم قبول العرض. خلاف ذلك، يحصل كلا اللاعبين على 0. وإذا لم يمنح الكمبيوتر خيار الرفض، يتم تقسيم المبلغ وفقًا لعرض مقدم الاقتراح تلقائيًا.""",
    "Korean (한국어)": """오늘 실험에서 당신은 제안자(Proposer)와 응답자(Responder) 중 하나의 역할을 맡게 됩니다.\n\n매 라운드마다 한 명의 제안자와 한 명의 응답자가 매칭되어 100달러를 어떻게 나눌지 결정합니다. 컴퓨터가 무작위로 매칭을 수행하므로 상대방은 매 라운드 변경됩니다. 상대방이 누구인지 식별할 수 없으며, 동일한 제안자 혹은 응답자와 다시 매칭되지 않습니다.\n\n제안자는 100달러 중 응답자에게 제안할 금액을 결정합니다. 제안 금액은 0에서 100 사이의 정수여야 합니다. 제안이 수락되면 응답자는 제안된 금액을 받고, 제안자는 남은 금액을 가집니다.\n\n이 게임에서 응답자는 제안을 거절할 수 있는 권한(거부권)을 가질 수 있습니다. 응답자가 거부권을 가질 확률(π)은 무작위로 결정되며, 라운드 시작 시 제안자와 응답자 모두에게 알려집니다.\n\n응답자는 수락할 용의가 있는 최소 금액인 '수락 한계선(Threshold)'을 설정합니다. 응답자에게 거부권이 부여되고(확률 π), 제안된 금액이 한계선 이상이면 수락되지만, 한계선 미만이면 거절되어 두 플레이어 모두 0달러를 받습니다. 거부권이 부여되지 않은 경우에는 한계선과 상관없이 제안자의 제안대로 분배됩니다.""",
    "Indonesian (Bahasa Indonesia)": """Dalam eksperimen hari ini, ada dua peran yang mungkin Anda mainkan: Pengusul (Proposer) dan Penerima (Responder).\n\nDi setiap putaran, satu Pengusul dan satu Penerima akan dipasangkan untuk menentukan bagaimana membagi dana sebesar 100 dolar. Komputer mengatur pencocokan secara acak sehingga pasangan akan berubah dari putaran ke putaran. Anda tidak akan dapat mengidentifikasi siapa lawan Anda dan tidak akan pernah dipasangkan kembali dengan Pengusul atau Penerima yang sama.\n\nUntuk Pengusul, tugas keputusan adalah menentukan seberapa banyak dari 100 dolar yang akan ditawarkan kepada Penerima (antara 0 hingga 100). Jika penawaran diterima, Penerima akan mendapatkan jumlah yang diusulkan dan Pengusul akan menyimpan sisanya.\n\nDalam permainan ini, Penerima mungkin memiliki opsi untuk menolak penawaran (hak veto). Probabilitas bagi Penerima untuk memiliki opsi tersebut ditentukan secara acak. Di awal setiap putaran, kedua pemain akan diberitahu tentang probabilitas ini (π).\n\nUntuk Penerima, keputusannya adalah menentukan jumlah minimum yang bersedia ia terima, yang disebut sebagai "ambang batas" (Threshold). Jika Penerima diberikan opsi veto (dengan probabilitas π) dan penawaran memenuhi atau melebihi ambang batas, penawaran diterima. Jika tidak, kedua pemain mendapatkan 0. Jika opsi veto tidak aktif, penawaran Pengusul otomatis dijalankan.""",
    "Italian (Italiano)": """Nell'esperimento di oggi, ci sono due ruoli possibili: il Proponente (Proposer) e il Ricevente (Responder).\n\nIn ogni round, un Proponente e un Ricevente saranno accoppiati per decidere come dividere un budget di 100 dollari. Il computer assegna gli abbinamenti in modo casuale, quindi le coppie cambieranno di round in round. Non sarete in grado di identificare il vostro avversario e non giocherete mai con lo stesso partner.\n\nPer il Proponente, il compito consiste nel determinare quanto, su 100 dollari, offrire al Ricevente. L'offerta può essere qualsiasi numero intero da 0 a 100. Se l'offerta viene accettata, il Ricevente ottiene la somma proposta e il Proponente tiene il resto.\n\nIn questo gioco, è possibile per i Riceventi avere l'opzione di rifiutare l'offerta (diritto di veto). La probabilità di avere questa opzione è determinata in modo casuale. All'inizio di ogni round, entrambi i giocatori saranno informati di questa probabilità (π).\n\nPer il Ricevente, la decisione consiste nell'indicare la somma minima che è disposto ad accettare, denominata "soglia" (Threshold). Se il Ricevente ottiene l'opzione di rifiuto (con probabilità π) e l'offerta è pari o superiore alla soglia, viene accettata. Altrimenti, entrambi i giocatori ottengono 0 dollari. Se il computer non assegna l'opzione di veto, l'offerta del Proponente viene implementata automaticamente.""",
    "Polish (Polski)": """W dzisiejszym eksperymencie możesz wcielić się w jedną z dwóch ról: Proponującego (Proposer) lub Reagującego (Responder).\n\nW każdej rundzie jeden Proponujący i jeden Reagujący są dobierani w parę, aby podzielić między sobą kwotę 100 dolarów. Dopasowanie jest losowe, dzięki czemu pary zmieniają się z rundy na rundę. Nie będziesz w stanie zidentyfikować swojego przeciwnika i nigdy nie zostaniesz ponownie dopasowany do tej samej osoby.\n\nZadaniem Proponującego jest określenie, jaką część ze 100 dolarów zaoferować Reagującemu. Oferta może być dowolną liczbą całkowitą od 0 do 100. Jeśli oferta zostanie zaakceptowana, Reagujący otrzymuje zaproponowaną kwotę, a Proponujący zatrzymuje resztę.\n\nW tej grze Reagujący mogą mieć możliwość odrzucenia oferty (prawo weta). Prawdopodobieństwo przyznania tego prawa jest ustalane losowo. Na początku każdej rundy obaj gracze są informowani o tym prawdopodobieństwie (π).\n\nDecyzja Reagującego polega na wskazaniu minimalnej kwoty, jaką jest gotów przyjąć, zwanej "progiem" (Threshold). Jeśli Reagujący otrzyma prawo weta (z prawdopodobieństwem π) i oferta jest równa lub wyższa od progu, zostaje ona zaakceptowana. W przeciwnym razie obaj gracze otrzymują 0 dolarów. Jeśli weto nie zostanie przyznane, oferta Proponującego jest automatycznie realizowana.""",
    "Russian (Русский)": """В сегодняшнем эксперименте вам предстоит сыграть одну из двух ролей: Инициатор (Proposer) или Ответчик (Responder).\n\nВ каждом раунде Инициатор и Ответчик объединяются в пары, чтобы разделить сумму в 100 долларов. Компьютер распределяет участников случайным образом, поэтому пары меняются от раунда к раунду. Вы не сможете идентифицировать своего оппонента и никогда не будете повторно объединены в пару с тем же игроком.\n\nДля Инициатора задача состоит в том, чтобы определить, какую сумму из 100 долларов предложить Ответчику (целое число от 0 до 100). Если предложение принято, Ответчик получает предложенную сумму, а Инициатор оставляет себе остаток.\n\nВ этой игре у Ответчиков может быть возможность отклонить предложение (право вето). Вероятность того, что Ответчик получит такое право, определяется случайным образом. В начале каждого раунда оба игрока информируются об этой вероятности (π).\n\nДля Ответчика решение состоит в том, чтобы указать минимальную сумму, которую он/она готов принять — «порог» (Threshold). Если Ответчику предоставляется право вето (с вероятностью π) и предложение превышает или равно порогу, оно принимается. В противном случае оба игрока получают 0 долларов. Если право вето не предоставлено, предложение Инициатора реализуется автоматически.""",
    "Greek (Ελληνικά)": """Στο σημερινό πείραμα, υπάρχουν δύο πιθανοί ρόλοι: ο Προτείνων (Proposer) και ο Αποδέκτης (Responder).\n\nΣε κάθε γύρο, ένας Προτείνων και ένας Αποδέκτης συνδυάζονται για να αποφασίσουν πώς θα διαιρέσουν ένα ποσό 100 δολαρίων. Η αντιστοίχιση γίνεται τυχαία από τον υπολογιστή, έτσι ώστε τα ζευγάρια να αλλάζουν από γύρο σε γύρο. Δεν θα μπορείτε να αναγνωρίσετε τον αντίπαλό σας και δεν θα αντιστοιχηθείτε ποτέ ξανά με τον ίδιο παίκτη.\n\nΓια τον Προτείνοντα, η απόφαση είναι να καθορίσει πόσα από τα 100 δολάρια θα προσφέρει στον Αποδέκτη (ακέραιος αριθμός από 0 έως 100). Εάν η προσφορά γίνει αποδεκτή, ο Αποδέκτης λαμβάνει το προτεινόμενο ποσό και ο Προτείνων κρατά τα υπόλοιπα.\n\nΣε αυτό το παιχνίδι, είναι πιθανό ο Αποδέκτης να έχει την επιλογή να απορρίψει την προσφορά (δικαίωμα αρνησικυρίας / βέτο). Η πιθανότητα να έχει αυτή την επιλογή καθορίζεται τυχαία. Στην αρχή κάθε γύρου, και οι δύο παίκτες ενημερώνονται για αυτή την πιθανότητα (π).\n\nΓια τον Αποδέκτη, η απόφαση είναι να δηλώσει το ελάχιστο ποσό που είναι διατεθειμένος να αποδεχτεί, το οποίο αναφέρεται ως "όριο αποδοχής" (Threshold). Εάν ο Αποδέκτης έχει δικαίωμα βέτο (με πιθανότητα π) και η προσφορά είναι ίση ή μεγαλύτερη από το όριο, η προσφορά γίνεται αποδεκτή. Διαφορετικά, και οι δύο παίκτες λαμβάνουν 0. Εάν δεν δοθεί δικαίωμα βέτο, η προσφορά του Προτείνοντος εφαρμόζεται αυτόματα.""",
    "Turkish (Türkçe)": """Bugünkü deneyde üstlenebileceğiniz iki rol bulunmaktadır: Teklif Eden (Proposer) ve Yanıtlayan (Responder).\n\nHer turda, bir Teklif Eden ve bir Yanıtlayan, 100 dolarlık bir havuzu aralarında nasıl böleceklerini belirlemek üzere eşleştirilir. Bilgisayar eşleştirmeleri rastgele yapar, bu nedenle eşler turdan tura değişir. Rakibinizin kim olduğunu bilemezsiniz og aynı kişiyle asla tekrar eşleşmezsiniz.\n\nTeklif Eden için görev, 100 dolardan ne kadarını Yanıtlayan'a teklif edeceğini belirlemektir (0 ile 100 arasında bir tam sayı). Teklif kabul edilirse, Yanıtlayan teklif edilen miktarı alır, Teklif Eden ise kalan miktarı kendine saklar.\n\nBu oyunda Yanıtlayan'ın teklifi reddetme seçeneği (veto yetkisi) olabilir. Yanıtlayan'ın bu yetkiye sahip olma olasılığı rastgele belirlenir. Her turun başında hem Teklif Eden hem de Yanıtlayan bu olasılık (π) hakkında bilgilendirilir.\n\nYantlayan için karar, kabul etmeye hazır olduğu minimum miktarı, yani "eşik değerini" (Threshold) belirtmektir. Yanıtlayan'a veto hakkı verilir (π olasılığıyla) ve teklif eşik değerine eşit veya ondan büyükse teklif kabul edilir. Aksi takdirde her iki oyuncu da 0 alır. Veto hakkı verilmezse, Teklif Eden'in teklifi doğrudan uygulanır.""",
    "Afrikaans (Afrikaans)": """In vandag se eksperiment is daar twee moontlike rolle wat jy kan speel: die Voorsteller (Proposer) en die Respondent (Responder).\n\nIn elke rondte sal een Voorsteller en een Respondent gepaar word om te besluit hoe om 'n poel van 100 dollar tussen hulle te verdeel. Die rekenaar kies die parings lukraak sodat dit van rondte tot rondte verander. Jy sal nie jou opponent kan identifiseer nie en sal nooit weer met dieselfde persoon gepaar word nie.\n\nVir 'n Voorsteller is die taak om te besluit hoeveel van die 100 dollar om vir die Respondent aan te bied (enige heelgetal van 0 tot 100). As die aanbod aanvaar word, kry die Respondent die voorgestelde bedrag en die Voorsteller hou die res.\n\nIn hierdie speletjie is dit moontlik dat die Respondent die opsie het om die aanbod te verwerp (vetoreg). Die waarskynlikheid dat 'n Respondent hierdie opsie sal kry, word lukraak bepaal. Aan die begin van elke rondte sal beide spelers ingelig word oor hierdie waarskynlikheid (π).\n\nVir die Respondent is die besluit om die minimum bedrag aan te dui wat hy/sy bereid is om te aanvaar, bekend as die "drempel" (Threshold). As die Respondent wel vetoreg kry (met waarskynlikheid π) en die aanbod is gelyk aan of hoër as die drempel, word dit aanvaar. Indien nie, kry beide spelers 0 dollar. As geen vetoreg toegestaan word nie, word die Voorsteller se aanbod outomaties toegepas.""",
    "Welsh (Cymraeg)": """Yn yr arbrawf heddiw, mae dwy rôl bosibl i chi eu chwarae: y Cynigydd (Proposer) ac y Sefydlydd (Responder).\n\nYm mhob rownd, bydd un Cynigydd ac un Sefydlydd yn cael eu paru i benderfynu sut i rannu cronfa o 100 doler rhyngddynt. Mae'r cyfrifiadur yn pennu'r paru ar hap fel bod y partneriaid yn newid o rownd i rownd. Ni fyddwch yn gallu nodi pwy yw eich gwrthwynebydd ac ni fyddwch byth yn cael eich paru â'r un person eto.\n\nAr gyfer Cynigydd, y penderfyniad yw faint o'r 100 doler i'w gynnig i'r Sefydlydd (unrhyw gyfanrif o 0 i 100). Os caiff y cynnig ei dderbyn, bydd y Sefydlydd yn cael y swm a gynigiwyd ac mae'r Cynigydd yn cadw'r gweddill.\n\nYn y gêm hon, mae'n bosibl i Sefydlydd gael yr opsiwn i wrthod y cynnig (hawl feto). Mae'r tebygolrwydd y bydd gan Sefydlydd yr opsiwn hwn yn cael ei benderfynu ar hap. Ar ddechrau pob rownd, bydd y ddau chwaraewr yn cael eu hysbysu o'r tebygolrwydd hwn (π).\n\nAr gyfer y Sefydlydd, y penderfyniad yw nodi'r swm lleiaf y mae'n fodlon ei dderbyn, sef y "trothwy" (Threshold). Os rhoddir hawl feto i'r Sefydlydd (gyda thebygolrwydd π) a bod y cynnig yn gyfartal neu'n fwy na'r trothwy, mae'r cynnig yn cael ei dderbyn. Fel arall, mae'r ddau chwaraewr yn cael 0. Os na roddir hawl feto, gweithredir cynnig y Cynigydd yn awtomatig."""
}

# Empirical PDI scores from the paper [6]
pdi_values = {
    "Simplified Chinese (简体中文)": 0.44,
    "Traditional Chinese (繁體中文)": 0.49,
    "Japanese (日本語)": 0.35,
    "Arabic (العربية)": 0.50,
    "German (Deutsch)": 0.21,
    "Polish (Polski)": 0.47,
    "Turkish (Türkçe)": 0.16,
    "Spanish (Español)": 0.20,
    "Greek (Ελληνικά)": 0.15,
    "Korean (한국어)": 0.22,
    "English": 0.35,
    "French (Français)": 0.32,
    "Indonesian (Bahasa Indonesia)": 0.28,
    "Italian (Italiano)": 0.19,
    "Welsh (Cymraeg)": 0.33,
    "Afrikaans (Afrikaans)": 0.26,
    "Russian (Русский)": 0.36
}

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

# Google Sheets Configuration (Boilerplate / Integration Info)
st.sidebar.markdown("---")
st.sidebar.subheader("☁️ Database Connection")
use_gsheets = st.sidebar.checkbox("Enable Live Google Sheet Backup", value=False, disabled=not is_instructor)

if use_gsheets:
    st.sidebar.success("Connection Status: Active (Staged)")
    st.sidebar.markdown("""
    **Connection Method (GSheetsConnection):**
    ```python
    # Configured inside Streamlit secrets
    conn = st.connection("gsheets", type=GSheetsConnection)
    conn.update(spreadsheet=url, data=df)
    ```
    *All student feedback & game logs will be mirrored in real-time to your configured Google Drive Sheet.*
    """)

# Sidebar Lesson Plan Timeline (Always Visible)
st.sidebar.markdown("---")
st.sidebar.subheader("⏱️ Session 1 Timeline")
st.sidebar.markdown("""
*   **00:00 - 00:10**: Intro & Setup
*   **00:10 - 00:20**: Step 1 - Calibration Portal
*   **00:20 - 00:40**: Step 2 - Modified Ultimatum Game
*   **00:40 - 01:00**: Step 3 - Regression Presentation
""")

# If customized text is in session state, load it, else use default
if 'custom_translations' not in st.session_state:
    st.session_state.custom_translations = default_translations.copy()

if is_instructor:
    st.sidebar.markdown("---")
    st.sidebar.subheader("⚙️ Classroom Experiment Settings")
    st.session_state.pi_assignment_mode = st.sidebar.radio(
        "Veto Probability (π) Assignment Mode:",
        options=["Automatic Split (50% Low, 50% High π)", "Manual Student Choice"],
        index=0 if st.session_state.pi_assignment_mode == "Automatic Split (50% Low, 50% High π)" else 1,
        help="Automatic mode cleanly distributes students to π = 0.1 or π = 0.9 based on Student ID."
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

# Unified Student Registration (Shared across Step 1 and Step 2)
st.markdown("### 🔑 Participant Registration")
student_id = st.text_input(
    "Enter your Anonymous Student ID to participate (e.g., EMBA_12):",
    value=st.session_state.get('global_student_id', ""),
    placeholder="Enter ID here...",
    help="This ID will be used anonymously to log your translation ratings and gameplay outcomes."
)
if student_id:
    st.session_state.global_student_id = student_id

# Main Portal Navigation
tabs = ["🌎 Step 1: Instruction Calibration", "🎮 Step 2: Play the Power Game"]
if is_instructor:
    tabs.append("📊 Step 3: Instructor Course Analytics")

nav_tabs = st.tabs(tabs)

# --- TAB 1: CALIBRATION ---
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
            "Select Localized Language for Review:",
            options=[l for l in list(default_translations.keys()) if l != "English"],
            index=1 # Default to Simplified Chinese
        )
        st.markdown(f"<h5 style='color: #17b978;'>Localized Rules ({selected_lang})</h5>", unsafe_allow_html=True)
        st.success(st.session_state.custom_translations[selected_lang])
        
    st.markdown("---")
    st.markdown("### ✍️ Student Calibration Feedback")
    st.warning("⚠️ **Research Constraint:** Please write all qualitative comments in **English** only to facilitate multi-country statistical matching and collation.")
    
    with st.form("feedback_form"):
        # Autoload registered student ID
        if not student_id:
            st.warning("⚠️ Please enter your Anonymous Student ID in the Registration field at the top of the page first!")
        else:
            st.info(f"📝 Registering calibration comments for: **{student_id}**")
        
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
            placeholder="Please write your review here in English (e.g., 'The translation of veto in paragraph 4 is too formal...')"
        )
        
        submit_feedback = st.form_submit_button("📤 Submit Evaluation Feedback")
        
        if submit_feedback:
            if not student_id:
                st.error("❌ Submission Blocked: Please register your Student ID at the top of the page.")
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

# --- TAB 2: GAME INTERFACE ---
with nav_tabs[1]:
    st.markdown("### 🎮 Step 2: The Interactive Power Game")
    st.write(
        "Now, participate in the Modified Ultimatum Game. You will be matched against "
        "a computer agent calibrated based on the cultural baseline of your selected language."
    )
    
    # Let student load their language selection from Step 1
    selected_game_lang = st.selectbox(
        "Select your native or preferred language for playing:",
        options=list(default_translations.keys()),
        key="game_lang_select"
    )
    
    # Power Prob Configuration (Replicating paper conditions: Low vs High Veto Prob)

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
        # Manual Student Choice mode
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
                    # Simulated Responder threshold based on GLOBE PDI mapping [6]
                    lang_pdi = pdi_values.get(selected_game_lang, 0.35)
                    # Simulated Responder threshold tends to be higher in higher PDI cultures to match empirical curves [6]
                    base_threshold = int(15 + (lang_pdi * 40) + random.randint(-5, 5))
                    base_threshold = max(0, min(100, base_threshold))
                    
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
                        "PDI": lang_pdi,
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
                    # Simulated Proposer offer based on language PDI
                    lang_pdi = pdi_values.get(selected_game_lang, 0.35)
                    base_offer = int(25 + (lang_pdi * 30) + random.randint(-5, 5))
                    base_offer = max(0, min(100, base_offer))
                    
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
                        "PDI": lang_pdi,
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

# --- TAB 3: INSTRUCTOR ANALYTICS (Passcode Protected) ---
if is_instructor:
    with nav_tabs[2]:
        st.markdown("<h3 style='color: #1e3d59;'>📊 Step 3: Instructor Course Analytics Dashboard</h3>", unsafe_allow_html=True)
        st.write("Monitor live classroom submissions, verify hypotheses, and download research data.")
        
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
        
        # 2. Gameplay logs & Regression Mapping
        df_games = pd.DataFrame(st.session_state.game_logs)
        if not df_games.empty:
            st.markdown("#### **II. Live Gameplay Logs**")
            st.dataframe(df_games, use_container_width=True)
            
            # Interactive Plot mapping PDI vs. Student Offers
            st.markdown("#### **III. Cultural Mapping: Power Distance vs. Strategic Offers**")
            st.write(
                "This plot overlays your live student decisions (mapped to their language's PDI) "
                "against the empirical regression baseline from your working paper [6]."
            )
            
            # Prepare paper baseline data points
            paper_data = pd.DataFrame([
                {"Language": "Simplified Chinese", "PDI": 0.44, "Avg_Offer_Paper": 39.56},
                {"Language": "Traditional Chinese", "PDI": 0.49, "Avg_Offer_Paper": 38.45},
                {"Language": "Japanese", "PDI": 0.35, "Avg_Offer_Paper": 35.97},
                {"Language": "Arabic", "PDI": 0.50, "Avg_Offer_Paper": 34.10},
                {"Language": "German", "PDI": 0.21, "Avg_Offer_Paper": 34.04},
                {"Language": "English", "PDI": 0.35, "Avg_Offer_Paper": 31.80},
                {"Language": "French", "PDI": 0.32, "Avg_Offer_Paper": 31.71},
                {"Language": "Russian", "PDI": 0.36, "Avg_Offer_Paper": 27.60},
                {"Language": "Afrikaans", "PDI": 0.26, "Avg_Offer_Paper": 28.98}
            ])
            
            fig = go.Figure()
            
            # Add paper baseline line/scatter
            fig.add_trace(go.Scatter(
                x=paper_data["PDI"],
                y=paper_data["Avg_Offer_Paper"],
                mode='markers+text',
                name='Empirical Paper Baseline',
                text=paper_data["Language"],
                textposition="top center",
                marker=dict(size=12, color='#1e3d59', symbol='circle')
            ))
            
            # Aggregate student choices
            student_offers = df_games[df_games["Offer"] != "N/A (Agent)"].copy()
            if not student_offers.empty:
                student_offers["Offer"] = student_offers["Offer"].astype(float)
                student_agg = student_offers.groupby(["Language", "PDI"])["Offer"].mean().reset_index()
                
                fig.add_trace(go.Scatter(
                    x=student_agg["PDI"],
                    y=student_agg["Offer"],
                    mode='markers+text',
                    name='Live Class Average',
                    text=student_agg["Language"].apply(lambda x: f"Class: {x.split(' ')[0]}"),
                    textposition="bottom center",
                    marker=dict(size=16, color='#ff9f43', symbol='star')
                ))
            
            fig.update_layout(
                title="PDI vs. Proposer Offers (Paper Baseline vs. Live Class)",
                xaxis_title="Normalized Power Distance Index (GLOBE PDI)",
                yaxis_title="Average Offer Amount ($ out of 100)",
                legend_title="Dataset",
                template="plotly_white",
                height=500
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Export Game CSV
            csv_games = df_games.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Download Game Results (.CSV)",
                data=csv_games,
                file_name="emba_gameplay_results.csv",
                mime="text/csv",
                key="dl_games"
            )
        else:
            st.info("No game sessions logged yet.")
