export type Example = {
  ja?: string;
  kana?: string;
  en?: string;
  pt?: string;
};

export type Flashcard = {
  id: string;
  chapterId: string;
  page: number;
  term: string;
  reading?: string;
  meanings: {
    en?: string;
    pt?: string;
  };
  example?: Example;
};

export type ExerciseSet = {
  id: string;
  chapterId: string;
  kind?: "unit" | "review" | "appendix";
  reviewFor?: string[];
  title: string;
  page: number;
  lines: string[];
  answer?: string;
  questions?: ExerciseQuestion[];
};

export type ExerciseQuestion = {
  id: string;
  prompt: string[];
  options: Array<{
    id: string;
    text: string;
  }>;
  answerId: string;
  answerSource?: "provided" | "suggested";
};

export type Chapter = {
  id: string;
  kind?: "unit" | "review" | "appendix";
  number?: number;
  title: string;
  subtitle?: string;
  pages: number[];
  cards: Flashcard[];
  exercises: ExerciseSet[];
};

export type StudyData = {
  appName: string;
  source: string;
  createdBy: string;
  generatedAt: string;
  chapters: Chapter[];
};
