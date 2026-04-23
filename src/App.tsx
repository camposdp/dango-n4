import {
  ArrowLeft,
  ArrowRight,
  BookOpen,
  Check,
  Download,
  Eye,
  EyeOff,
  Layers,
  RotateCcw,
  Upload,
  X,
} from "lucide-react";
import { Fragment, useEffect, useMemo, useRef, useState } from "react";
import { sampleData } from "./data/sampleData";
import type { Chapter, ExerciseQuestion, ExerciseSet, Flashcard, StudyData } from "./types";

type Tab = "cards" | "exercises";
type Grade = "remembered" | "missed";
type Language = "pt" | "en";

type UiCopy = {
  reviewControls: string;
  language: string;
  translationLanguage: string;
  examples: string;
  exportProgress: string;
  importProgress: string;
  resetSession: string;
  chaptersFilter: string;
  cards: string;
  exercises: string;
  all: string;
  chapterSingular: string;
  chapterPlural: string;
  sessionReset: string;
  progressExported: string;
  progressImported: string;
  progressImportFailed: string;
  credit: string;
  completionTitle: string;
  completionBody: string;
  restart: string;
  noCards: string;
  current: string;
  rememberedStat: string;
  reviewStat: string;
  reviewedChapter: string;
  pendingChapter: string;
  page: string;
  missedButton: string;
  rememberedButton: string;
};

const UI_COPY: Record<Language, UiCopy> = {
  pt: {
    reviewControls: "Controles de revisão",
    language: "Idioma",
    translationLanguage: "Idioma da tradução",
    examples: "Frases",
    exportProgress: "Exportar progresso",
    importProgress: "Importar progresso",
    resetSession: "Reiniciar sessão",
    chaptersFilter: "Filtro de capítulos",
    cards: "Cards",
    exercises: "Exercícios",
    all: "Todos",
    chapterSingular: "capítulo",
    chapterPlural: "capítulos",
    sessionReset: "Sessão reiniciada.",
    progressExported: "Progresso exportado.",
    progressImported: "Progresso importado.",
    progressImportFailed: "Não foi possível importar o progresso.",
    credit: "Criado por Daniel Prado de Campos para treinar o livro Nihongo Challenge Kotoba N4.",
    completionTitle: "Revisão completa",
    completionBody: "Todos os cards desta seleção foram lembrados.",
    restart: "Revisar novamente",
    noCards: "Nenhum card encontrado para a seleção atual.",
    current: "atual",
    rememberedStat: "lembrei",
    reviewStat: "revisar",
    reviewedChapter: "revisado",
    pendingChapter: "pendente",
    page: "Página",
    missedButton: "Não lembrei",
    rememberedButton: "Lembrei",
  },
  en: {
    reviewControls: "Review controls",
    language: "Language",
    translationLanguage: "Translation language",
    examples: "Examples",
    exportProgress: "Export progress",
    importProgress: "Import progress",
    resetSession: "Restart session",
    chaptersFilter: "Chapter filter",
    cards: "Cards",
    exercises: "Exercises",
    all: "All",
    chapterSingular: "chapter",
    chapterPlural: "chapters",
    sessionReset: "Session restarted.",
    progressExported: "Progress exported.",
    progressImported: "Progress imported.",
    progressImportFailed: "Could not import progress.",
    credit: "Created by Daniel Prado de Campos to practice Nihongo Challenge Kotoba N4.",
    completionTitle: "Review complete",
    completionBody: "All cards in this selection were remembered.",
    restart: "Review again",
    noCards: "No cards found for the current selection.",
    current: "current",
    rememberedStat: "remembered",
    reviewStat: "review",
    reviewedChapter: "reviewed",
    pendingChapter: "pending",
    page: "Page",
    missedButton: "Forgot",
    rememberedButton: "Remembered",
  },
};

type ExerciseCard = {
  id: string;
  setId: string;
  chapterId: string;
  title: string;
  page: number;
  prompt: string[];
  options: ExerciseQuestion["options"];
  answerId: string;
  answerSource?: "provided" | "suggested";
};

type SavedState = {
  selectedCardChapters: string[];
  selectedExerciseChapters: string[];
  includeReviewExercises: boolean;
  language: Language;
  showExamples: boolean;
  cardIndex: number;
  exerciseIndex: number;
  cardQueueIds?: string[];
  cardReviewIds?: string[];
  cardComplete?: boolean;
  exerciseQueueIds?: string[];
  exerciseReviewIds?: string[];
  exerciseComplete?: boolean;
  rememberedKanjiCardIds?: string[];
  stats: { remembered: number; missed: number };
  exerciseResponses: Record<string, { answerId: string; checked: boolean; grade?: Grade }>;
};

const DATA_URL = "/study-data.json";
const SAVE_KEY = "dango-n4-state-v2";

function normalizeData(data: StudyData): StudyData {
  return {
    ...data,
    chapters: data.chapters.map((chapter) => ({
      ...chapter,
      kind: chapter.kind ?? (chapter.number ? "unit" : "review"),
      cards: chapter.cards.map((card) => ({ ...card, chapterId: chapter.id })),
      exercises: chapter.exercises.map((exercise) => ({
        ...exercise,
        kind: exercise.kind ?? (chapter.kind === "review" ? "review" : "unit"),
        chapterId: chapter.id,
      })),
    })),
  };
}

function hasSelection(selection: Set<string>, id: string) {
  return selection.size === 0 || selection.has(id);
}

function hasKanji(value: string) {
  return /[\u4e00-\u9faf々]/.test(value);
}

function compactCount(value: number, singular: string, plural: string) {
  return `${value} ${value === 1 ? singular : plural}`;
}

function termView(card: Flashcard) {
  if (!card.reading) {
    return <span>{card.term}</span>;
  }

  const parenthetical = card.term.match(/^(.+?)([（(].*[）)])$/);
  if (parenthetical && !hasKanji(parenthetical[2])) {
    const reading = card.reading.replace(/[（(].*?[）)]/g, "");
    return (
      <>
        <ruby>
          {parenthetical[1]}
          <rt>{reading}</rt>
        </ruby>
        {parenthetical[2]}
      </>
    );
  }

  return (
    <ruby>
      {card.term}
      <rt>{card.reading}</rt>
    </ruby>
  );
}

function normalizeLanguage(value: unknown): Language {
  return value === "en" ? "en" : "pt";
}

function choiceLabel(language: Language) {
  if (language === "pt") {
    return "Português";
  }
  return "English";
}

function renderTextByLanguage(source: { pt?: string; en?: string }, language: Language) {
  const value = source[language];
  return value ? <p>{value}</p> : null;
}

function exampleTermTarget(term: string) {
  return term.replace(/[（(].*?[）)]/g, "").trim();
}

function termDensityClass(term: string) {
  const visibleLength = [...term.replace(/[（）()]/g, "")].length;
  if (visibleLength >= 9) {
    return "ultraCompact";
  }
  if (visibleLength >= 7) {
    return "extraCompact";
  }
  if (visibleLength >= 5) {
    return "compact";
  }
  return "";
}

function exampleJaView(card: Flashcard) {
  const text = card.example?.ja;
  const target = exampleTermTarget(card.term);
  if (!text || !card.reading || !target || !text.includes(target)) {
    return text;
  }

  return text.split(target).map((part, index) => (
    <Fragment key={`${card.id}-example-${index}`}>
      {index > 0 && (
        <ruby>
          {target}
          <rt>{card.reading}</rt>
        </ruby>
      )}
      {part}
    </Fragment>
  ));
}

function splitExerciseSet(set: ExerciseSet): ExerciseCard[] {
  if (set.questions?.length) {
    return set.questions.map((question) => ({
      id: question.id,
      setId: set.id,
      chapterId: set.chapterId,
      title: set.title,
      page: set.page,
      prompt: question.prompt,
      options: question.options,
      answerId: question.answerId,
      answerSource: question.answerSource,
    }));
  }
  return [];
}

function encodeSave(state: SavedState) {
  const payload = JSON.stringify({ app: "dango-n4", version: 2, state });
  return new Blob([new TextEncoder().encode(payload)], { type: "application/octet-stream" });
}

function decodeSave(buffer: ArrayBuffer): SavedState {
  const decoded = new TextDecoder().decode(buffer);
  const payload = JSON.parse(decoded) as { app?: string; state?: SavedState };
  if (payload.app !== "dango-n4" || !payload.state) {
    throw new Error("Invalid progress file.");
  }
  return payload.state;
}

function toSavedState(args: {
  selectedCardChapters: Set<string>;
  selectedExerciseChapters: Set<string>;
  includeReviewExercises: boolean;
  language: Language;
  showExamples: boolean;
  cardIndex: number;
  exerciseIndex: number;
  cardQueueIds: string[];
  cardReviewIds: string[];
  cardComplete: boolean;
  exerciseQueueIds: string[];
  exerciseReviewIds: string[];
  exerciseComplete: boolean;
  rememberedKanjiCardIds: Set<string>;
  stats: { remembered: number; missed: number };
  exerciseResponses: Record<string, { answerId: string; checked: boolean; grade?: Grade }>;
}): SavedState {
  return {
    ...args,
    selectedCardChapters: [...args.selectedCardChapters],
    selectedExerciseChapters: [...args.selectedExerciseChapters],
    rememberedKanjiCardIds: [...args.rememberedKanjiCardIds],
  };
}

export function App() {
  const [data, setData] = useState<StudyData>(normalizeData(sampleData));
  const [selectedCardChapters, setSelectedCardChapters] = useState<Set<string>>(new Set());
  const [selectedExerciseChapters, setSelectedExerciseChapters] = useState<Set<string>>(new Set());
  const [includeReviewExercises, setIncludeReviewExercises] = useState(true);
  const [language, setLanguage] = useState<Language>("pt");
  const [showExamples, setShowExamples] = useState(true);
  const [cardIndex, setCardIndex] = useState(0);
  const [exerciseIndex, setExerciseIndex] = useState(0);
  const [cardQueueIds, setCardQueueIds] = useState<string[]>([]);
  const [cardReviewIds, setCardReviewIds] = useState<string[]>([]);
  const [cardComplete, setCardComplete] = useState(false);
  const [exerciseQueueIds, setExerciseQueueIds] = useState<string[]>([]);
  const [exerciseReviewIds, setExerciseReviewIds] = useState<string[]>([]);
  const [exerciseComplete, setExerciseComplete] = useState(false);
  const [rememberedKanjiCardIds, setRememberedKanjiCardIds] = useState<Set<string>>(new Set());
  const [revealed, setRevealed] = useState(false);
  const [dragOffset, setDragOffset] = useState(0);
  const [stats, setStats] = useState({ remembered: 0, missed: 0 });
  const [exerciseResponses, setExerciseResponses] = useState<
    Record<string, { answerId: string; checked: boolean; grade?: Grade }>
  >({});
  const [saveMessage, setSaveMessage] = useState("");
  const [saveLoaded, setSaveLoaded] = useState(false);
  const dragStart = useRef<number | null>(null);
  const importRef = useRef<HTMLInputElement | null>(null);

  useEffect(() => {
    fetch(DATA_URL, { cache: "no-store" })
      .then((response) => {
        if (!response.ok) {
          throw new Error("No generated data");
        }
        return response.json() as Promise<StudyData>;
      })
      .then((payload) => {
        setData(normalizeData(payload));
      })
      .catch(() => {
        setData(normalizeData(sampleData));
      });
  }, []);

  useEffect(() => {
    const raw = localStorage.getItem(SAVE_KEY);
    if (!raw) {
      setSaveLoaded(true);
      return;
    }
    try {
      const state = JSON.parse(raw) as SavedState;
      setSelectedCardChapters(new Set(state.selectedCardChapters ?? []));
      setSelectedExerciseChapters(new Set(state.selectedExerciseChapters ?? []));
      setIncludeReviewExercises(state.includeReviewExercises ?? true);
      setLanguage(normalizeLanguage(state.language));
      setShowExamples(state.showExamples ?? true);
      setCardIndex(state.cardIndex ?? 0);
      setExerciseIndex(state.exerciseIndex ?? 0);
      setCardQueueIds(state.cardQueueIds ?? []);
      setCardReviewIds(state.cardReviewIds ?? []);
      setCardComplete(state.cardComplete ?? false);
      setExerciseQueueIds(state.exerciseQueueIds ?? []);
      setExerciseReviewIds(state.exerciseReviewIds ?? []);
      setExerciseComplete(state.exerciseComplete ?? false);
      setRememberedKanjiCardIds(new Set(state.rememberedKanjiCardIds ?? []));
      setStats(state.stats ?? { remembered: 0, missed: 0 });
      setExerciseResponses(state.exerciseResponses ?? {});
    } catch {
      localStorage.removeItem(SAVE_KEY);
    }
    setSaveLoaded(true);
  }, []);

  const unitChapters = useMemo(
    () => data.chapters.filter((chapter) => chapter.kind === "unit" && chapter.number && chapter.number <= 32),
    [data.chapters],
  );

  const chapterKanjiCardIds = useMemo(() => {
    return new Map(
      unitChapters.map((chapter) => [
        chapter.id,
        chapter.cards.filter((card) => hasKanji(card.term)).map((card) => card.id),
      ]),
    );
  }, [unitChapters]);

  const completedCardChapters = useMemo(() => {
    const completed = new Set<string>();
    for (const [chapterId, kanjiCardIds] of chapterKanjiCardIds) {
      if (kanjiCardIds.length > 0 && kanjiCardIds.every((id) => rememberedKanjiCardIds.has(id))) {
        completed.add(chapterId);
      }
    }
    return completed;
  }, [chapterKanjiCardIds, rememberedKanjiCardIds]);

  const chapterById = useMemo(() => new Map(data.chapters.map((chapter) => [chapter.id, chapter])), [data.chapters]);

  const deck = useMemo(() => {
    return unitChapters.flatMap((chapter) =>
      hasSelection(selectedCardChapters, chapter.id) ? chapter.cards : [],
    );
  }, [selectedCardChapters, unitChapters]);

  const exerciseSets = useMemo(() => {
    const selected = selectedExerciseChapters;
    return data.chapters.flatMap((chapter) =>
      chapter.exercises.filter((exercise) => {
        if (exercise.kind !== "unit" && exercise.kind !== "review") {
          return false;
        }
        if (exercise.kind === "review") {
          if (!includeReviewExercises) {
            return false;
          }
          if (selected.size === 0) {
            return true;
          }
          return (exercise.reviewFor ?? []).some((chapterId) => selected.has(chapterId));
        }
        return hasSelection(selected, exercise.chapterId);
      }),
    );
  }, [data.chapters, includeReviewExercises, selectedExerciseChapters]);

  const exerciseCards = useMemo(() => exerciseSets.flatMap(splitExerciseSet), [exerciseSets]);
  const deckById = useMemo(() => new Map(deck.map((card) => [card.id, card])), [deck]);
  const exerciseById = useMemo(() => new Map(exerciseCards.map((exercise) => [exercise.id, exercise])), [exerciseCards]);
  const activeCardQueue = useMemo(() => cardQueueIds.filter((id) => deckById.has(id)), [cardQueueIds, deckById]);
  const activeExerciseQueue = useMemo(
    () => exerciseQueueIds.filter((id) => exerciseById.has(id)),
    [exerciseById, exerciseQueueIds],
  );
  const currentCard = cardComplete ? undefined : deckById.get(activeCardQueue[cardIndex]);
  const currentExercise = exerciseComplete ? undefined : exerciseById.get(activeExerciseQueue[exerciseIndex]);
  const copy = UI_COPY[language];
  const selectedCardLabel =
    selectedCardChapters.size === 0
      ? `32 ${copy.chapterPlural}`
      : compactCount(selectedCardChapters.size, copy.chapterSingular, copy.chapterPlural);
  const selectedExerciseLabel =
    selectedExerciseChapters.size === 0
      ? `32 ${copy.chapterPlural}`
      : compactCount(selectedExerciseChapters.size, copy.chapterSingular, copy.chapterPlural);

  useEffect(() => {
    if (!saveLoaded) {
      return;
    }
    const state = toSavedState({
      selectedCardChapters,
      selectedExerciseChapters,
      includeReviewExercises,
      language,
      showExamples,
      cardIndex,
      exerciseIndex,
      cardQueueIds,
      cardReviewIds,
      cardComplete,
      exerciseQueueIds,
      exerciseReviewIds,
      exerciseComplete,
      rememberedKanjiCardIds,
      stats,
      exerciseResponses,
    });
    localStorage.setItem(SAVE_KEY, JSON.stringify(state));
  }, [
    cardIndex,
    cardComplete,
    cardQueueIds,
    cardReviewIds,
    exerciseIndex,
    exerciseComplete,
    exerciseQueueIds,
    exerciseReviewIds,
    exerciseResponses,
    includeReviewExercises,
    language,
    rememberedKanjiCardIds,
    saveLoaded,
    selectedCardChapters,
    selectedExerciseChapters,
    showExamples,
    stats,
  ]);

  useEffect(() => {
    if (saveLoaded && deck.length > 0 && activeCardQueue.length === 0 && !cardComplete) {
      setCardQueueIds(deck.map((card) => card.id));
    }
  }, [activeCardQueue.length, cardComplete, deck, saveLoaded]);

  useEffect(() => {
    if (saveLoaded && exerciseCards.length > 0 && activeExerciseQueue.length === 0 && !exerciseComplete) {
      setExerciseQueueIds(exerciseCards.map((exercise) => exercise.id));
    }
  }, [activeExerciseQueue.length, exerciseCards, exerciseComplete, saveLoaded]);

  useEffect(() => {
    if (cardIndex >= activeCardQueue.length && activeCardQueue.length > 0) {
      setCardIndex(0);
    }
  }, [activeCardQueue.length, cardIndex]);

  useEffect(() => {
    if (exerciseIndex >= activeExerciseQueue.length && activeExerciseQueue.length > 0) {
      setExerciseIndex(0);
    }
  }, [activeExerciseQueue.length, exerciseIndex]);

  const restartCards = () => {
    setCardQueueIds(deck.map((card) => card.id));
    setCardReviewIds([]);
    setCardComplete(false);
    setCardIndex(0);
    setRevealed(false);
    setDragOffset(0);
  };

  const restartExercises = () => {
    setExerciseQueueIds(exerciseCards.map((exercise) => exercise.id));
    setExerciseReviewIds([]);
    setExerciseComplete(false);
    setExerciseIndex(0);
  };

  const toggleChapter = (target: "cards" | "exercises", chapterId: string) => {
    const setter = target === "cards" ? setSelectedCardChapters : setSelectedExerciseChapters;
    setter((current) => {
      const next = new Set(current);
      if (next.has(chapterId)) {
        next.delete(chapterId);
      } else {
        next.add(chapterId);
      }
      return next;
    });
    if (target === "cards") {
      setCardQueueIds([]);
      setCardReviewIds([]);
      setCardComplete(false);
      setCardIndex(0);
      setRevealed(false);
    } else {
      setExerciseQueueIds([]);
      setExerciseReviewIds([]);
      setExerciseComplete(false);
      setExerciseIndex(0);
    }
  };

  const resetSelection = (target: "cards" | "exercises") => {
    if (target === "cards") {
      setSelectedCardChapters(new Set());
      setCardQueueIds([]);
      setCardReviewIds([]);
      setCardComplete(false);
      setCardIndex(0);
      setRevealed(false);
    } else {
      setSelectedExerciseChapters(new Set());
      setExerciseQueueIds([]);
      setExerciseReviewIds([]);
      setExerciseComplete(false);
      setExerciseIndex(0);
    }
  };

  const gradeCard = (grade: Grade) => {
    if (!currentCard || activeCardQueue.length === 0) {
      return;
    }
    const nextReviewIds =
      grade === "missed" && !cardReviewIds.includes(currentCard.id)
        ? [...cardReviewIds, currentCard.id]
        : cardReviewIds;
    setStats((current) => ({
      remembered: current.remembered + (grade === "remembered" ? 1 : 0),
      missed: current.missed + (grade === "missed" ? 1 : 0),
    }));
    if (hasKanji(currentCard.term)) {
      setRememberedKanjiCardIds((current) => {
        const next = new Set(current);
        if (grade === "remembered") {
          next.add(currentCard.id);
        } else {
          next.delete(currentCard.id);
        }
        return next;
      });
    }
    if (cardIndex + 1 < activeCardQueue.length) {
      setCardReviewIds(nextReviewIds);
      setCardIndex((current) => current + 1);
    } else if (nextReviewIds.length > 0) {
      setCardQueueIds(nextReviewIds);
      setCardReviewIds([]);
      setCardIndex(0);
    } else {
      setCardQueueIds([]);
      setCardReviewIds([]);
      setCardComplete(true);
      setCardIndex(0);
    }
    setRevealed(false);
    setDragOffset(0);
  };

  const advanceExercise = (grade?: Grade) => {
    if (!currentExercise || activeExerciseQueue.length === 0) {
      return;
    }
    const nextReviewIds =
      grade === "missed" && !exerciseReviewIds.includes(currentExercise.id)
        ? [...exerciseReviewIds, currentExercise.id]
        : exerciseReviewIds;
    if (grade) {
      setExerciseResponses((current) => ({
        ...current,
        [currentExercise.id]: {
          answerId: current[currentExercise.id]?.answerId ?? "",
          checked: true,
          grade,
        },
      }));
    }
    if (exerciseIndex + 1 < activeExerciseQueue.length) {
      setExerciseReviewIds(nextReviewIds);
      setExerciseIndex((current) => current + 1);
    } else if (nextReviewIds.length > 0) {
      setExerciseResponses((current) => {
        const next = { ...current };
        for (const id of nextReviewIds) {
          next[id] = { answerId: "", checked: false };
        }
        return next;
      });
      setExerciseQueueIds(nextReviewIds);
      setExerciseReviewIds([]);
      setExerciseIndex(0);
    } else {
      setExerciseQueueIds([]);
      setExerciseReviewIds([]);
      setExerciseComplete(true);
      setExerciseIndex(0);
    }
  };

  const resetSession = () => {
    setCardIndex(0);
    setExerciseIndex(0);
    setCardQueueIds(deck.map((card) => card.id));
    setCardReviewIds([]);
    setCardComplete(false);
    setExerciseQueueIds(exerciseCards.map((exercise) => exercise.id));
    setExerciseReviewIds([]);
    setExerciseComplete(false);
    setRevealed(false);
    setStats({ remembered: 0, missed: 0 });
    setRememberedKanjiCardIds(new Set());
    setDragOffset(0);
    setExerciseResponses({});
    setSaveMessage(copy.sessionReset);
  };

  const exportProgress = () => {
    const state = toSavedState({
      selectedCardChapters,
      selectedExerciseChapters,
      includeReviewExercises,
      language,
      showExamples,
      cardIndex,
      exerciseIndex,
      cardQueueIds,
      cardReviewIds,
      cardComplete,
      exerciseQueueIds,
      exerciseReviewIds,
      exerciseComplete,
      rememberedKanjiCardIds,
      stats,
      exerciseResponses,
    });
    const blob = encodeSave(state);
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = `dango-n4-progress-${new Date().toISOString().slice(0, 10)}.dango`;
    link.click();
    URL.revokeObjectURL(url);
    setSaveMessage(copy.progressExported);
  };

  const importProgress = async (file: File | undefined) => {
    if (!file) {
      return;
    }
    try {
      const state = await file.arrayBuffer().then(decodeSave);
      const importedLanguage = normalizeLanguage(state.language);
      setSelectedCardChapters(new Set(state.selectedCardChapters ?? []));
      setSelectedExerciseChapters(new Set(state.selectedExerciseChapters ?? []));
      setIncludeReviewExercises(state.includeReviewExercises ?? true);
      setLanguage(importedLanguage);
      setShowExamples(state.showExamples ?? true);
      setCardIndex(state.cardIndex ?? 0);
      setExerciseIndex(state.exerciseIndex ?? 0);
      setCardQueueIds(state.cardQueueIds ?? []);
      setCardReviewIds(state.cardReviewIds ?? []);
      setCardComplete(state.cardComplete ?? false);
      setExerciseQueueIds(state.exerciseQueueIds ?? []);
      setExerciseReviewIds(state.exerciseReviewIds ?? []);
      setExerciseComplete(state.exerciseComplete ?? false);
      setRememberedKanjiCardIds(new Set(state.rememberedKanjiCardIds ?? []));
      setStats(state.stats ?? { remembered: 0, missed: 0 });
      setExerciseResponses(state.exerciseResponses ?? {});
      setSaveMessage(UI_COPY[importedLanguage].progressImported);
    } catch {
      setSaveMessage(copy.progressImportFailed);
    }
  };

  const onPointerDown = (event: React.PointerEvent<HTMLButtonElement>) => {
    dragStart.current = event.clientX;
    event.currentTarget.setPointerCapture(event.pointerId);
  };

  const onPointerMove = (event: React.PointerEvent<HTMLButtonElement>) => {
    if (dragStart.current === null) {
      return;
    }
    setDragOffset(Math.max(-120, Math.min(120, event.clientX - dragStart.current)));
  };

  const onPointerUp = () => {
    if (dragOffset > 80) {
      gradeCard("remembered");
    } else if (dragOffset < -80) {
      gradeCard("missed");
    } else {
      setDragOffset(0);
    }
    dragStart.current = null;
  };

  return (
    <main className="appShell">
      <header className="topbar">
        <div>
          <div className="brandMark">
            <DangoMark />
            <span>塵も積もれば山となる</span>
          </div>
          <h1>Dango N4 - ダン語 N4</h1>
        </div>
      </header>

      <section className="controlsBand" aria-label={copy.reviewControls}>
        <div className="controlGroup">
          <span className="controlLabel">{copy.language}</span>
          <div className="segmented" role="group" aria-label={copy.translationLanguage}>
            {(["pt", "en"] as Language[]).map((option) => (
              <button
                className={language === option ? "active" : ""}
                key={option}
                type="button"
                onClick={() => setLanguage(option)}
              >
                {choiceLabel(option)}
              </button>
            ))}
          </div>
        </div>

        <button className="toggleButton" type="button" onClick={() => setShowExamples((value) => !value)}>
          {showExamples ? <Eye size={18} aria-hidden="true" /> : <EyeOff size={18} aria-hidden="true" />}
          {copy.examples}
        </button>

        <div className="saveActions">
          <button className="iconButton" type="button" title={copy.exportProgress} onClick={exportProgress}>
            <Download size={18} aria-hidden="true" />
          </button>
          <button className="iconButton" type="button" title={copy.importProgress} onClick={() => importRef.current?.click()}>
            <Upload size={18} aria-hidden="true" />
          </button>
          <button className="iconButton" type="button" title={copy.resetSession} onClick={resetSession}>
            <RotateCcw size={18} aria-hidden="true" />
          </button>
          <input
            ref={importRef}
            className="fileInput"
            type="file"
            accept=".dango,application/octet-stream,application/json"
            onChange={(event) => importProgress(event.target.files?.[0])}
          />
        </div>
      </section>

      <ChapterSelector
        chapters={unitChapters}
        copy={copy}
        label={selectedCardLabel}
        mode="cards"
        selected={selectedCardChapters}
        completed={completedCardChapters}
        onReset={() => resetSelection("cards")}
        onToggle={(chapterId) => toggleChapter("cards", chapterId)}
      />

      <FlashcardPanel
        card={currentCard}
        complete={cardComplete}
        copy={copy}
        count={activeCardQueue.length}
        dragOffset={dragOffset}
        index={cardIndex}
        language={language}
        onGrade={gradeCard}
        onPointerDown={onPointerDown}
        onPointerMove={onPointerMove}
        onPointerUp={onPointerUp}
        onReveal={() => setRevealed((value) => !value)}
        onRestart={restartCards}
        revealed={revealed}
        showExamples={showExamples}
        stats={stats}
      />

      <footer className="credit">
        {copy.credit}
        {saveMessage && <span>{saveMessage}</span>}
      </footer>
    </main>
  );
}

function DangoMark() {
  return (
    <span className="dangoMark" aria-hidden="true">
      <span />
      <span />
      <span />
    </span>
  );
}

type ChapterSelectorProps = {
  chapters: Chapter[];
  copy: UiCopy;
  label: string;
  mode: Tab;
  selected: Set<string>;
  completed?: Set<string>;
  onReset: () => void;
  onToggle: (chapterId: string) => void;
};

function ChapterSelector({ chapters, completed = new Set(), copy, label, mode, selected, onReset, onToggle }: ChapterSelectorProps) {
  return (
    <section className="chapterSelector" aria-label={copy.chaptersFilter}>
      <div className="selectorHeader">
        <div>
          <span className="controlLabel">{mode === "cards" ? copy.cards : copy.exercises}</span>
          <strong>{label}</strong>
        </div>
        {mode === "cards" && (
          <div className="selectorLegend" aria-hidden="true">
            <span className="legendItem reviewed">
              <span />
              {copy.reviewedChapter}
            </span>
            <span className="legendItem pending">
              <span />
              {copy.pendingChapter}
            </span>
          </div>
        )}
        <button className={selected.size === 0 ? "active" : ""} type="button" onClick={onReset}>
          {copy.all}
        </button>
      </div>
      <div className="chapterChips">
        {chapters.map((chapter) => {
          const isCompleted = completed.has(chapter.id);
          const stateLabel = isCompleted ? copy.reviewedChapter : copy.pendingChapter;
          return (
            <button
              className={`${selected.has(chapter.id) ? "active" : ""} ${isCompleted ? "reviewed" : "pending"}`}
              key={chapter.id}
              type="button"
              onClick={() => onToggle(chapter.id)}
              title={`${chapter.title} - ${stateLabel}`}
              aria-label={`${chapter.title} - ${stateLabel}`}
            >
              <span>{chapter.number}</span>
            </button>
          );
        })}
      </div>
    </section>
  );
}

type FlashcardPanelProps = {
  card?: Flashcard;
  complete: boolean;
  copy: UiCopy;
  count: number;
  dragOffset: number;
  index: number;
  language: Language;
  onGrade: (grade: Grade) => void;
  onPointerDown: (event: React.PointerEvent<HTMLButtonElement>) => void;
  onPointerMove: (event: React.PointerEvent<HTMLButtonElement>) => void;
  onPointerUp: () => void;
  onReveal: () => void;
  onRestart: () => void;
  revealed: boolean;
  showExamples: boolean;
  stats: { remembered: number; missed: number };
};

function FlashcardPanel({
  card,
  complete,
  copy,
  count,
  dragOffset,
  index,
  language,
  onGrade,
  onPointerDown,
  onPointerMove,
  onPointerUp,
  onReveal,
  onRestart,
  revealed,
  showExamples,
  stats,
}: FlashcardPanelProps) {
  if (complete) {
    return (
      <section className="completionState">
        <Check size={30} aria-hidden="true" />
        <strong>{copy.completionTitle}</strong>
        <p>{copy.completionBody}</p>
        <button className="primary" type="button" onClick={onRestart}>
          {copy.restart}
        </button>
      </section>
    );
  }

  if (!card) {
    return (
      <section className="emptyState">
        <Layers size={28} aria-hidden="true" />
        <p>{copy.noCards}</p>
      </section>
    );
  }

  const rotate = dragOffset / 18;
  const intent = dragOffset > 30 ? "right" : dragOffset < -30 ? "left" : "";

  return (
    <section className="studyGrid">
      <div className="sessionStats">
        <span>{count} cards</span>
        <span>{index + 1} {copy.current}</span>
        <span>{stats.remembered} {copy.rememberedStat}</span>
        <span>{stats.missed} {copy.reviewStat}</span>
      </div>

      <button
        className={`flashcard ${revealed ? "revealed" : ""} ${intent}`}
        onClick={onReveal}
        onPointerDown={onPointerDown}
        onPointerMove={onPointerMove}
        onPointerUp={onPointerUp}
        style={{ transform: `translateX(${dragOffset}px) rotate(${rotate}deg)` }}
        type="button"
      >
        <span className="chapterPill">{copy.page} {card.page}</span>
        {!revealed ? (
          <div className="cardFace">
            <div className={`jpTerm ${termDensityClass(card.term)}`}>{termView(card)}</div>
            {showExamples && card.example?.ja && (
              <div className="exampleBlock">
                <p className="exampleJa">{exampleJaView(card)}</p>
                {card.example.kana && <p className="exampleKana">{card.example.kana}</p>}
              </div>
            )}
          </div>
        ) : (
          <div className="cardFace back">
            <div className="meaningBlock">{renderTextByLanguage(card.meanings, language)}</div>
            {showExamples && card.example?.[language] && (
              <div className="exampleBack">{renderTextByLanguage(card.example, language)}</div>
            )}
          </div>
        )}
      </button>

      <div className="swipeActions">
        <button className="missed" type="button" onClick={() => onGrade("missed")}>
          <ArrowLeft size={20} aria-hidden="true" />
          {copy.missedButton}
        </button>
        <button className="remembered" type="button" onClick={() => onGrade("remembered")}>
          {copy.rememberedButton}
          <ArrowRight size={20} aria-hidden="true" />
        </button>
      </div>
    </section>
  );
}

type ExercisesPanelProps = {
  chapterById: Map<string, Chapter>;
  complete: boolean;
  exercise?: ExerciseCard;
  index: number;
  responses: Record<string, { answerId: string; checked: boolean; grade?: Grade }>;
  total: number;
  onAnswer: (exerciseId: string, answerId: string) => void;
  onCheck: (exerciseId: string) => void;
  onGrade: (exerciseId: string, grade: Grade) => void;
  onNext: () => void;
  onPrevious: () => void;
  onRestart: () => void;
};

function ExercisesPanel({
  chapterById,
  complete,
  exercise,
  index,
  responses,
  total,
  onAnswer,
  onCheck,
  onGrade,
  onNext,
  onPrevious,
  onRestart,
}: ExercisesPanelProps) {
  if (complete) {
    return (
      <section className="completionState">
        <Check size={30} aria-hidden="true" />
        <strong>Exercícios completos</strong>
        <p>Todas as questões desta seleção foram acertadas.</p>
        <button className="primary" type="button" onClick={onRestart}>
          Revisar novamente
        </button>
      </section>
    );
  }

  if (!exercise) {
    return (
      <section className="emptyState">
        <BookOpen size={28} aria-hidden="true" />
        <p>Nenhum exercício encontrado para a seleção atual.</p>
      </section>
    );
  }

  const response = responses[exercise.id] ?? { answerId: "", checked: false };
  const chapter = chapterById.get(exercise.chapterId);
  const selectedOption = exercise.options.find((option) => option.id === response.answerId);
  const correctOption = exercise.options.find((option) => option.id === exercise.answerId) ?? exercise.options[0];

  return (
    <section className="exerciseFlow">
      <div className="sessionStats">
        <span>{total} questões</span>
        <span>{index + 1} atual</span>
        <span>{chapter?.title ?? exercise.title}</span>
        <span>Página {exercise.page}</span>
      </div>

      <article className={`exerciseCard ${response.grade ?? ""}`}>
        <div className="exercisePrompt">
          {exercise.prompt.map((line, lineIndex) => (
            <p key={`${exercise.id}-${lineIndex}`}>{line}</p>
          ))}
        </div>

        <div className="optionList" role="radiogroup" aria-label="Alternativas">
          {exercise.options.map((option) => {
            const isSelected = response.answerId === option.id;
            const isCorrect = response.checked && option.id === correctOption?.id;
            const isWrong = response.checked && isSelected && option.id !== correctOption?.id;
            return (
              <button
                className={`${isSelected ? "selected" : ""} ${isCorrect ? "correct" : ""} ${isWrong ? "wrong" : ""}`}
                key={option.id}
                type="button"
                onClick={() => onAnswer(exercise.id, option.id)}
              >
                <span>{option.id}</span>
                {option.text}
              </button>
            );
          })}
        </div>

        {response.checked && (
          <div className="answerReveal">
            <strong>Conferência</strong>
            <p>
              Resposta correta: {correctOption?.id}. {correctOption?.text}
            </p>
            {exercise.answerSource === "suggested" && (
              <small>Gabarito sugerido a partir da transcrição. Revise se notar OCR estranho.</small>
            )}
            {selectedOption && <small>Sua resposta: {selectedOption.id}. {selectedOption.text}</small>}
          </div>
        )}

        <div className="exerciseNav">
          <button type="button" onClick={onPrevious}>
            <ArrowLeft size={18} aria-hidden="true" />
            Anterior
          </button>
          {!response.checked ? (
            <button className="primary" type="button" onClick={() => onCheck(exercise.id)}>
              Conferir
            </button>
          ) : (
            <div className="gradeButtons">
              <button className="missed" type="button" onClick={() => onGrade(exercise.id, "missed")}>
                <X size={18} aria-hidden="true" />
                Errei
              </button>
              <button className="remembered" type="button" onClick={() => onGrade(exercise.id, "remembered")}>
                <Check size={18} aria-hidden="true" />
                Acertei
              </button>
            </div>
          )}
          <button type="button" onClick={onNext}>
            Próxima
            <ArrowRight size={18} aria-hidden="true" />
          </button>
        </div>
      </article>
    </section>
  );
}
