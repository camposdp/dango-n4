export type Example = {
  ja?: string;
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
  title: string;
  page: number;
  lines: string[];
};

export type Chapter = {
  id: string;
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
