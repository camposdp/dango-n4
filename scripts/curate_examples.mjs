import fs from "node:fs";

const dataPath = "public/study-data.json";

const cardFixes = {
  "unit-29-p86-07": { term: "すっかり" },
  "unit-30-p88-02": { term: "まず" },
};

const fixes = {
  "unit-01-p16-03": {
    ja: "仕事はもうほとんど終わりました。",
    en: "I have already finished most of my work.",
    pt: "Já terminei quase todo o trabalho.",
  },
  "unit-01-p16-07": {
    ja: "あなたに会えてうれしい。",
    en: "I'm glad I was able to meet you.",
    pt: "Fico feliz por poder encontrá-lo.",
  },
  "unit-01-p16-09": {
    ja: "ごはんを冷凍しておく。",
    en: "to freeze rice",
    pt: "deixar o arroz congelado",
  },
  "unit-01-p17-01": {
    ja: "料理がたくさん残った。",
    en: "A lot of food was left over.",
    pt: "Sobrou bastante comida.",
  },
  "unit-02-p18-05": {
    ja: "この料理はぜんぜんおいしくない。",
    en: "This food doesn't taste good at all.",
    pt: "Esta comida não é nem um pouco gostosa.",
  },
  "unit-02-p18-06": null,
  "unit-02-p19-02": null,
  "unit-02-p19-03": null,
  "unit-02-p19-04": null,
  "unit-03-p20-08": {
    ja: "用事がすむ。",
    en: "My errand is finished.",
    pt: "Terminei o que tinha para fazer.",
  },
  "unit-03-p21-01": {
    ja: "彼の言ったことが全部うそだと知って、怒った。",
    en: "I was upset when I learned that what he said was all lies.",
    pt: "Fiquei bravo porque soube que tudo o que ele disse era mentira.",
  },
  "unit-04-p22-01": {
    ja: "犬の世話をする。",
    en: "to look after the dog",
    pt: "cuidar do cachorro",
  },
  "unit-04-p22-07": {
    ja: "彼のかわりに、式に出席する。",
    en: "I will attend the ceremony in his place.",
    pt: "Irei participar da cerimônia no lugar dele.",
  },
  "unit-04-p23-02": {
    ja: "ちょっと、先生に相談があるんですが。",
    en: "Excuse me, there is something I'd like to talk to you about.",
    pt: "Por favor, quero me consultar com o professor.",
  },
  "unit-05-p26-01": null,
  "unit-05-p26-02": {
    ja: "となりの町に引っ越す。",
    en: "to move to a neighboring town",
    pt: "mudar para a cidade vizinha",
  },
  "unit-05-p26-05": {
    ja: "となりの席に移る。",
    en: "to move to the next seat",
    pt: "mudar para o assento ao lado",
  },
  "unit-05-p26-08": {
    ja: "〜を片づける。",
    en: "to tidy up",
    pt: "arrumar; limpar",
  },
  "unit-05-p26-10": {
    ja: "三か月で日本語を覚えたの？すごいね！",
    en: "You learned Japanese in three months? That's amazing!",
    pt: "Você aprendeu japonês em três meses? Que incrível!",
  },
  "unit-06-p28-01": null,
  "unit-06-p28-06": {
    ja: "今日のニュースにびっくりした。",
    en: "I was surprised at today's news.",
    pt: "Fiquei surpreso com a notícia de hoje.",
  },
  "unit-06-p28-08": {
    ja: "ろうかを通って部屋に行く。",
    en: "to pass through a corridor to get to a room",
    pt: "ir ao quarto passando pelo corredor",
  },
  "unit-07-p30-08": {
    ja: "地下鉄に乗り換える。",
    en: "to transfer to the subway",
    pt: "fazer baldeação para o metrô",
  },
  "unit-07-p30-10": {
    ja: "このレストランはいつも混んでいる。",
    en: "This restaurant is always crowded.",
    pt: "Este restaurante está sempre cheio.",
  },
  "unit-08-p32-03": {
    ja: "しばらくお休みします。",
    en: "We will be closed for a while.",
    pt: "Ficaremos fechados por um tempo.",
  },
  "unit-08-p32-04": {
    ja: "コンビニのATMを利用する。",
    en: "to use the ATM at a convenience store",
    pt: "usar o caixa eletrônico da loja de conveniência",
  },
  "unit-08-p33-07": null,
  "unit-08-p33-08": null,
  "unit-09-p36-02": {
    ja: "甘いものばかり食べていると、太りますよ。",
    en: "You will get fat if you eat nothing but sweets.",
    pt: "Se você ficar comendo só doces, vai engordar.",
  },
  "unit-09-p36-03": {
    ja: "親に心配をかける。",
    en: "to make one's parents worry",
    pt: "preocupar os pais",
  },
  "unit-09-p36-06": {
    ja: "日本の文化に興味がある。",
    en: "I am interested in Japanese culture.",
    pt: "Tenho interesse pela cultura japonesa.",
  },
  "unit-09-p37-03": {
    ja: "パーティーを開く。",
    en: "to hold a party",
    pt: "realizar uma festa",
  },
  "unit-09-p37-04": {
    ja: "彼女の歌は本当にすばらしい。",
    en: "Her song is really wonderful.",
    pt: "A música dela é realmente maravilhosa.",
  },
  "unit-10-p38-01": {
    ja: "田中さんからパーティーに招待されて、夫といっしょに出かけた。",
    en: "I was invited to a party by Mr. Tanaka and went out with my husband.",
    pt: "Fui convidada pelo Sr. Tanaka para uma festa e saí com meu marido.",
  },
  "unit-10-p38-02": null,
  "unit-10-p39-02": null,
  "unit-10-p39-03": null,
  "unit-11-p40-02": null,
  "unit-11-p40-03": {
    ja: "旅館に泊まる。",
    en: "to stay at a Japanese-style inn",
    pt: "hospedar-se em uma pousada japonesa",
  },
  "unit-12-p42-07": {
    ja: "ぜひ、遊びに来てください。",
    en: "By all means, come visit.",
    pt: "Venha nos visitar, sem falta.",
  },
  "unit-12-p42-08": {
    ja: "あなたが来られないなんて、非常に残念です。",
    en: "It's a real pity that you cannot come.",
    pt: "É realmente uma pena que você não possa vir.",
  },
  "unit-12-p43-02": null,
  "unit-13-p46-02": {
    ja: "レストランでアルバイトをする。",
    en: "to work part-time at a restaurant",
    pt: "fazer bico em um restaurante",
  },
  "unit-13-p46-04": {
    ja: "面接試験を受ける。",
    en: "to take an interview",
    pt: "fazer uma entrevista",
  },
  "unit-13-p46-06": null,
  "unit-13-p46-09": {
    ja: "事務所の中を案内する。",
    en: "to show someone around an office",
    pt: "mostrar o escritório para alguém",
  },
  "unit-13-p47-01": {
    ja: "部屋に花をかざる。",
    en: "to decorate a room with flowers",
    pt: "enfeitar o quarto com flores",
  },
  "unit-13-p47-03": null,
  "unit-14-p48-04": {
    ja: "五年ほど前から、日本に住んでいます。",
    en: "I have been living in Japan since about five years ago.",
    pt: "Moro no Japão há uns cinco anos.",
  },
  "unit-14-p48-10": {
    ja: "子どもの名前を考える。",
    en: "to think of a name for a child",
    pt: "pensar no nome da criança",
  },
  "unit-15-p50-01": null,
  "unit-15-p50-05": {
    ja: "別のを見せてください。",
    en: "Please show me a different one.",
    pt: "Mostre-me outro, por favor.",
  },
  "unit-15-p50-07": null,
  "unit-15-p51-08": null,
  "unit-16-p52-01": {
    ja: "海外旅行",
    en: "overseas trip",
    pt: "viagem ao exterior",
  },
  "unit-16-p52-03": {
    ja: "私に直接電話をください。",
    en: "Please call me directly.",
    pt: "Ligue diretamente para mim.",
  },
  "unit-16-p52-04": {
    ja: "ただ今戻りました。",
    en: "I'm back.",
    pt: "Voltei agora.",
  },
  "unit-16-p52-07": {
    ja: "風で木が倒れる。",
    en: "The tree falls because of the wind.",
    pt: "A árvore cai por causa do vento.",
  },
  "unit-16-p52-08": {
    ja: "友だちと競争する。",
    en: "to compete with friends",
    pt: "competir com os amigos",
  },
  "unit-16-p52-09": {
    ja: "試合に勝つ。",
    en: "to win a match",
    pt: "vencer uma partida",
  },
  "unit-17-p56-03": {
    ja: "面接試験を受ける。",
    en: "to take an interview",
    pt: "fazer uma entrevista",
  },
  "unit-17-p56-05": {
    ja: "日本の法律について調べる。",
    en: "to do research on Japanese law",
    pt: "pesquisar sobre a legislação japonesa",
  },
  "unit-17-p56-07": {
    ja: "土曜日のご都合はいかがですか。",
    en: "Would Saturday be convenient for you?",
    pt: "Sábado seria conveniente para você?",
  },
  "unit-17-p56-08": null,
  "unit-17-p56-09": {
    ja: "使い方を説明してもらえますか。",
    en: "Could you explain how to use this?",
    pt: "Você poderia me explicar como usar?",
  },
  "unit-18-p58-04": null,
  "unit-18-p58-05": {
    ja: "今年、息子が小学校に入学する。",
    en: "This year my son will enter primary school.",
    pt: "Este ano, meu filho vai entrar na escola primária.",
  },
  "unit-18-p58-06": {
    ja: "数学の予習をする。",
    en: "to prepare for math class",
    pt: "estudar matemática com antecedência",
  },
  "unit-18-p58-07": null,
  "unit-18-p58-10": {
    ja: "時間はあまりないけれど、できるだけがんばろう。",
    en: "I don't have much time, but I will do my best.",
    pt: "Não tenho muito tempo, mas vou me esforçar ao máximo.",
  },
  "unit-18-p58-11": {
    ja: "大学を卒業したら、公務員になるつもりです。",
    en: "After I graduate from university, I intend to become a civil servant.",
    pt: "Depois de me formar na universidade, pretendo ser funcionário público.",
  },
  "unit-19-p61-03": null,
  "unit-20-p62-02": {
    ja: "けんかで友だちを泣かせた。",
    en: "I fought with my friend and made them cry.",
    pt: "Briguei com meu amigo e o fiz chorar.",
  },
  "unit-20-p62-04": {
    ja: "彼はとてもまじめな人です。",
    en: "He is a very serious person.",
    pt: "Ele é uma pessoa muito séria.",
  },
  "unit-20-p62-06": {
    ja: "得意なスポーツはありますか。",
    en: "Is there any sport you are good at?",
    pt: "Há algum esporte em que você é bom?",
  },
  "unit-20-p63-02": null,
  "unit-21-p66-03": null,
  "unit-21-p66-04": null,
  "unit-21-p66-05": {
    ja: "そこにある本は、そのままにしておいてください。",
    en: "Please leave the books over there as they are.",
    pt: "Deixe os livros aí como estão.",
  },
  "unit-21-p66-06": null,
  "unit-21-p67-01": null,
  "unit-22-p68-04": {
    ja: "彼女は自分の考えをはっきり言う。",
    en: "She says what she thinks in a straightforward manner.",
    pt: "Ela fala claramente o que pensa.",
  },
  "unit-22-p68-05": null,
  "unit-22-p68-06": {
    ja: "仕事の帰りにコンビニに寄った。",
    en: "I stopped by a convenience store on the way home from work.",
    pt: "Passei em uma loja de conveniência na volta do trabalho.",
  },
  "unit-22-p68-07": null,
  "unit-22-p68-08": null,
  "unit-22-p68-09": {
    ja: "駅前でタクシーを拾う。",
    en: "to pick up a taxi in front of the station",
    pt: "pegar um táxi em frente à estação",
  },
  "unit-22-p68-10": null,
  "unit-22-p69-01": null,
  "unit-22-p69-02": null,
  "unit-23-p70-06": null,
  "unit-23-p71-05": null,
  "unit-24-p72-02": {
    ja: "この間行ったレストラン、おいしかったですね。",
    en: "The restaurant we went to the other day was good, wasn't it?",
    pt: "Aquele restaurante a que fomos outro dia estava bom, não estava?",
  },
  "unit-24-p72-03": null,
  "unit-24-p72-04": null,
  "unit-24-p72-05": {
    ja: "急いで準備してください。",
    en: "Please prepare quickly.",
    pt: "Apresse-se com os preparativos.",
  },
  "unit-24-p72-09": {
    ja: "今、財布がないことにはじめて気づいた。",
    en: "Only now did I notice that I don't have my wallet.",
    pt: "Só agora percebi que estou sem a carteira.",
  },
  "unit-24-p72-10": {
    ja: "お客さんに一生懸命あやまった。",
    en: "I apologized to the customer as sincerely as I could.",
    pt: "Pedi desculpas ao cliente com todo o empenho.",
  },
  "unit-24-p73-02": null,
  "unit-24-p73-03": null,
  "unit-25-p76-02": {
    ja: "ダイエットをして、5キロやせた。",
    en: "I went on a diet and lost 5 kilos.",
    pt: "Fiz dieta e emagreci 5 quilos.",
  },
  "unit-25-p76-06": {
    ja: "自転車のタイヤに空気を入れる。",
    en: "to inflate the tires of a bicycle",
    pt: "colocar ar no pneu da bicicleta",
  },
  "unit-25-p77-01": null,
  "unit-25-p77-02": null,
  "unit-26-p78-01": {
    ja: "天気予報によると、明日は晴れるらしいよ。",
    en: "According to the weather forecast, tomorrow the weather will be fine.",
    pt: "Segundo a previsão do tempo, parece que amanhã vai fazer sol.",
  },
  "unit-26-p78-07": null,
  "unit-26-p78-08": {
    ja: "道を渡るときは、車に注意しよう。",
    en: "Be careful of cars when crossing the road.",
    pt: "Preste atenção aos carros ao atravessar a rua.",
  },
  "unit-27-p80-02": {
    ja: "急いで角を曲がったら、人にぶつかった。",
    en: "I turned the corner in a hurry and bumped into someone.",
    pt: "Virei a esquina às pressas e esbarrei em alguém.",
  },
  "unit-27-p80-03": null,
  "unit-27-p80-06": {
    ja: "119番で救急車を呼ぶ。",
    en: "to call 119 for an ambulance",
    pt: "chamar uma ambulância ligando para 119",
  },
  "unit-27-p80-07": {
    ja: "大けがにならなくて、よかった。",
    en: "Thank goodness it wasn't a serious injury.",
    pt: "Ainda bem que não foi um ferimento grave.",
  },
  "unit-27-p81-02": {
    ja: "私の父は10年前に亡くなった。",
    en: "My father died ten years ago.",
    pt: "Meu pai faleceu há dez anos.",
  },
  "unit-28-p82-05": {
    ja: "お風呂をわかす。",
    en: "to prepare a bath",
    pt: "esquentar a água da banheira",
  },
  "unit-28-p82-07": {
    ja: "留守番電話にメッセージを入れる。",
    en: "to leave a message on the answering machine",
    pt: "deixar uma mensagem na secretária eletrônica",
  },
  "unit-29-p86-01": {
    ja: "これで、授業を終わりにします。",
    en: "This brings us to the end of today's class.",
    pt: "Vamos encerrar a aula por aqui.",
  },
  "unit-29-p86-03": {
    ja: "雪が降って、道がすべりやすくなっている。",
    en: "It snowed, so the road has become slippery.",
    pt: "Nevou e a pista está escorregadia.",
  },
  "unit-29-p86-05": {
    ja: "ボールを打つ。",
    en: "to hit a ball",
    pt: "bater na bola",
  },
  "unit-29-p86-06": null,
  "unit-29-p86-07": {
    ja: "料理はすっかりなくなった。",
    en: "There isn't even a bit of food left.",
    pt: "A comida acabou completamente.",
  },
  "unit-29-p86-08": null,
  "unit-29-p86-10": {
    ja: "もうすぐ仕事が終わる。",
    en: "I'm getting off work soon.",
    pt: "O trabalho vai terminar em breve.",
  },
  "unit-29-p87-01": null,
  "unit-30-p88-02": {
    ja: "まず最初に、自己紹介をします。",
    en: "First, let me introduce myself.",
    pt: "Primeiro, vou me apresentar.",
  },
  "unit-30-p88-03": {
    ja: "ここで遊んではだめですよ。",
    en: "You should not play here.",
    pt: "Não pode brincar aqui.",
  },
  "unit-30-p88-06": {
    ja: "あなただけには、決して負けない。",
    en: "I'm never going to lose to you.",
    pt: "Jamais vou perder para você.",
  },
  "unit-30-p88-07": {
    ja: "どうぞ、仕事を続けてください。",
    en: "Please continue working.",
    pt: "Continue o trabalho, por favor.",
  },
  "unit-30-p88-08": {
    ja: "出発まで、十分時間がある。",
    en: "We have enough time before departure.",
    pt: "Há tempo suficiente até a partida.",
  },
  "unit-30-p89-01": null,
  "unit-30-p89-03": null,
  "unit-30-p89-05": null,
  "unit-30-p89-06": null,
  "unit-31-p90-02": null,
  "unit-31-p90-03": {
    ja: "学校の成績が上がる。",
    en: "A student's marks at school rise.",
    pt: "As notas da escola sobem.",
  },
  "unit-31-p90-05": {
    ja: "魚を釣る。",
    en: "to catch fish",
    pt: "pescar peixe",
  },
  "unit-31-p90-10": {
    ja: "昔のことを思い出す。",
    en: "to recall the past",
    pt: "lembrar-se de coisas antigas",
  },
  "unit-31-p91-02": null,
  "unit-32-p92-04": {
    ja: "動物をいじめてはいけません。",
    en: "Do not be cruel to animals.",
    pt: "Não maltrate os animais.",
  },
  "unit-32-p92-06": {
    ja: "ここから、富士山がよく見える。",
    en: "From here, you can see Mt. Fuji clearly.",
    pt: "Daqui, dá para ver bem o Monte Fuji.",
  },
  "unit-32-p92-09": {
    ja: "気分はどうですか。",
    en: "How do you feel?",
    pt: "Como você está se sentindo?",
  },
  "unit-32-p93-03": null,
  "unit-32-p93-05": null,
};

const data = JSON.parse(fs.readFileSync(dataPath, "utf8"));
const cards = new Map();

for (const chapter of data.chapters) {
  for (const card of chapter.cards) {
    cards.set(card.id, card);
  }
}

for (const [id, example] of Object.entries(fixes)) {
  const card = cards.get(id);
  if (!card) {
    throw new Error(`Card not found: ${id}`);
  }
  card.example = example;
}

for (const [id, patch] of Object.entries(cardFixes)) {
  const card = cards.get(id);
  if (!card) {
    throw new Error(`Card not found: ${id}`);
  }
  Object.assign(card, patch);
}

for (const chapter of data.chapters) {
  if (chapter.kind !== "unit") {
    continue;
  }
  for (const card of chapter.cards) {
    if (!card.example) {
      continue;
    }
    for (const key of ["ja", "en", "pt"]) {
      if (!card.example[key] || !String(card.example[key]).trim()) {
        throw new Error(`Incomplete example translation on ${card.id}: missing ${key}`);
      }
      card.example[key] = String(card.example[key]).trim();
    }
  }
}

fs.writeFileSync(dataPath, `${JSON.stringify(data, null, 2)}\n`, "utf8");
console.log(`Curated ${Object.keys(fixes).length} example entries.`);
