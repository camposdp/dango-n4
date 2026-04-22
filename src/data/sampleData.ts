import type { StudyData } from "../types";

export const sampleData: StudyData = {
  appName: "Dango N4 - ダン語 N4",
  source: "Nihongo Challenge Kotoba N4",
  createdBy: "Daniel Prado de Campos",
  generatedAt: "sample",
  chapters: [
    {
      id: "unit-01",
      kind: "unit",
      number: 1,
      title: "1・スーパーで買い物",
      subtitle: "Compras no Supermercado",
      pages: [16, 17],
      cards: [
        {
          id: "sample-01",
          chapterId: "unit-01",
          page: 16,
          term: "スーパー",
          meanings: { en: "supermarket", pt: "supermercado" },
        },
        {
          id: "sample-02",
          chapterId: "unit-01",
          page: 16,
          term: "半額",
          reading: "はんがく",
          meanings: { en: "half price", pt: "metade do preco" },
        },
        {
          id: "sample-03",
          chapterId: "unit-01",
          page: 17,
          term: "残る",
          reading: "のこる",
          meanings: { en: "to be left", pt: "sobrar" },
          example: {
            ja: "料理がたくさん残った。",
            en: "A lot of food was left over.",
            pt: "Sobrou bastante comida.",
          },
        },
        {
          id: "sample-04",
          chapterId: "unit-01",
          page: 17,
          term: "足りる",
          reading: "たりる",
          meanings: { en: "to be enough", pt: "ser suficiente" },
          example: {
            ja: "5000円あれば足りる。",
            en: "5,000 yen will be enough.",
            pt: "5.000 ienes e suficiente.",
          },
        },
      ],
      exercises: [
        {
          id: "sample-ex-01",
          chapterId: "unit-01",
          kind: "unit",
          title: "1・スーパーで買い物",
          page: 17,
          lines: [
            "1 （　）に入ることばをえらんでください。",
            "スポーツは全部好きですが、（　）サッカーが好きです。",
            "1 少し　2 特に　3 ほとんど　4 必ず",
          ],
        },
      ],
    },
  ],
};
