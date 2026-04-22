import {
  ArrowLeft,
  ArrowRight,
  BookOpen,
  Check,
  ChevronDown,
  Eye,
  EyeOff,
  Layers,
  RotateCcw,
  Sparkles,
  X,
} from "lucide-react";
import { useEffect, useMemo, useRef, useState } from "react";
import { sampleData } from "./data/sampleData";
import type { Chapter, ExerciseSet, Flashcard, StudyData } from "./types";

type Tab = "cards" | "exercises";
type Grade = "remembered" | "missed";

const DATA_URL = "/study-data.json";

function normalizeData(data: StudyData): StudyData {
  return {
    ...data,
    chapters: data.chapters.map((chapter) => ({
      ...chapter,
      cards: chapter.cards.map((card) => ({ ...card, chapterId: chapter.id })),
      exercises: chapter.exercises.map((exercise) => ({ ...exercise, chapterId: chapter.id })),
    })),
  };
}

function hasSelection(selection: Set<string>, id: string) {
  return selection.size === 0 || selection.has(id);
}

function termView(card: Flashcard) {
  if (!card.reading) {
    return <span>{card.term}</span>;
  }

  return (
    <ruby>
      {card.term}
      <rt>{card.reading}</rt>
    </ruby>
  );
}

function compactCount(value: number, singular: string, plural: string) {
  return `${value} ${value === 1 ? singular : plural}`;
}

export function App() {
  const [data, setData] = useState<StudyData>(sampleData);
  const [dataMode, setDataMode] = useState<"generated" | "sample">("sample");
  const [activeTab, setActiveTab] = useState<Tab>("cards");
  const [selectedCardChapters, setSelectedCardChapters] = useState<Set<string>>(new Set());
  const [selectedExerciseChapters, setSelectedExerciseChapters] = useState<Set<string>>(new Set());
  const [showExamples, setShowExamples] = useState(true);
  const [isFilterOpen, setIsFilterOpen] = useState(false);
  const [cardIndex, setCardIndex] = useState(0);
  const [revealed, setRevealed] = useState(false);
  const [dragOffset, setDragOffset] = useState(0);
  const [stats, setStats] = useState({ remembered: 0, missed: 0 });
  const [exerciseGrades, setExerciseGrades] = useState<Record<string, Grade>>({});
  const dragStart = useRef<number | null>(null);

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
        setDataMode("generated");
      })
      .catch(() => {
        setData(normalizeData(sampleData));
        setDataMode("sample");
      });
  }, []);

  const chapters = data.chapters;
  const filterableChapters = useMemo(
    () =>
      activeTab === "cards"
        ? chapters.filter((chapter) => chapter.cards.length > 0)
        : chapters.filter((chapter) => chapter.exercises.length > 0),
    [activeTab, chapters],
  );
  const activeSelection = activeTab === "cards" ? selectedCardChapters : selectedExerciseChapters;
  const selectedLabel =
    activeSelection.size === 0
      ? "Todos os capítulos"
      : compactCount(activeSelection.size, "capítulo", "capítulos");

  const deck = useMemo(() => {
    return chapters.flatMap((chapter) => (hasSelection(selectedCardChapters, chapter.id) ? chapter.cards : []));
  }, [chapters, selectedCardChapters]);

  const exercises = useMemo(() => {
    return chapters.flatMap((chapter) =>
      hasSelection(selectedExerciseChapters, chapter.id) ? chapter.exercises : [],
    );
  }, [chapters, selectedExerciseChapters]);

  const currentCard = deck[cardIndex % Math.max(deck.length, 1)];

  useEffect(() => {
    setCardIndex(0);
    setRevealed(false);
  }, [selectedCardChapters]);

  const toggleChapter = (chapterId: string) => {
    const setter = activeTab === "cards" ? setSelectedCardChapters : setSelectedExerciseChapters;
    setter((current) => {
      const next = new Set(current);
      if (next.has(chapterId)) {
        next.delete(chapterId);
      } else {
        next.add(chapterId);
      }
      return next;
    });
  };

  const selectAllActive = () => {
    if (activeTab === "cards") {
      setSelectedCardChapters(new Set());
    } else {
      setSelectedExerciseChapters(new Set());
    }
  };

  const gradeCard = (grade: Grade) => {
    if (deck.length === 0) {
      return;
    }
    setStats((current) => ({
      remembered: current.remembered + (grade === "remembered" ? 1 : 0),
      missed: current.missed + (grade === "missed" ? 1 : 0),
    }));
    setCardIndex((current) => (current + 1) % deck.length);
    setRevealed(false);
    setDragOffset(0);
  };

  const resetSession = () => {
    setCardIndex(0);
    setRevealed(false);
    setStats({ remembered: 0, missed: 0 });
    setDragOffset(0);
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
            <Sparkles size={18} aria-hidden="true" />
            <span>Dango N4 - 段語 N4</span>
          </div>
          <h1>Dango N4 - 段語 N4</h1>
        </div>

        <nav className="tabList" aria-label="Modo de estudo">
          <button
            className={activeTab === "cards" ? "active" : ""}
            type="button"
            onClick={() => setActiveTab("cards")}
          >
            <Layers size={18} aria-hidden="true" />
            Cards
          </button>
          <button
            className={activeTab === "exercises" ? "active" : ""}
            type="button"
            onClick={() => setActiveTab("exercises")}
          >
            <BookOpen size={18} aria-hidden="true" />
            Exercícios
          </button>
        </nav>
      </header>

      <section className="controlsBand" aria-label="Controles de revisão">
        <div className="selectWrap">
          <button className="selectButton" type="button" onClick={() => setIsFilterOpen((open) => !open)}>
            <span>{selectedLabel}</span>
            <ChevronDown size={18} aria-hidden="true" />
          </button>
          {isFilterOpen && (
            <div className="chapterMenu">
              <button className="chapterOption all" type="button" onClick={selectAllActive}>
                <Check size={16} aria-hidden="true" />
                Revisar todos
              </button>
              {filterableChapters.map((chapter) => (
                <label className="chapterOption" key={chapter.id}>
                  <input
                    checked={activeSelection.has(chapter.id)}
                    type="checkbox"
                    onChange={() => toggleChapter(chapter.id)}
                  />
                  <span>{chapter.title}</span>
                </label>
              ))}
            </div>
          )}
        </div>

        <button className="toggleButton" type="button" onClick={() => setShowExamples((value) => !value)}>
          {showExamples ? <Eye size={18} aria-hidden="true" /> : <EyeOff size={18} aria-hidden="true" />}
          Frases
        </button>

        <button className="iconButton" type="button" title="Reiniciar sessão" onClick={resetSession}>
          <RotateCcw size={18} aria-hidden="true" />
        </button>
      </section>

      {activeTab === "cards" ? (
        <FlashcardPanel
          card={currentCard}
          count={deck.length}
          dataMode={dataMode}
          dragOffset={dragOffset}
          index={cardIndex}
          onGrade={gradeCard}
          onPointerDown={onPointerDown}
          onPointerMove={onPointerMove}
          onPointerUp={onPointerUp}
          onReveal={() => setRevealed((value) => !value)}
          revealed={revealed}
          showExamples={showExamples}
          stats={stats}
        />
      ) : (
        <ExercisesPanel
          chapters={chapters}
          exercises={exercises}
          grades={exerciseGrades}
          onGrade={(exerciseId, grade) =>
            setExerciseGrades((current) => ({ ...current, [exerciseId]: grade }))
          }
        />
      )}

      <footer className="credit">
        Criado por Daniel Prado de Campos para treinar o livro Nihongo Challenge Kotoba N4.
      </footer>
    </main>
  );
}

type FlashcardPanelProps = {
  card?: Flashcard;
  count: number;
  dataMode: "generated" | "sample";
  dragOffset: number;
  index: number;
  onGrade: (grade: Grade) => void;
  onPointerDown: (event: React.PointerEvent<HTMLButtonElement>) => void;
  onPointerMove: (event: React.PointerEvent<HTMLButtonElement>) => void;
  onPointerUp: () => void;
  onReveal: () => void;
  revealed: boolean;
  showExamples: boolean;
  stats: { remembered: number; missed: number };
};

function FlashcardPanel({
  card,
  count,
  dataMode,
  dragOffset,
  index,
  onGrade,
  onPointerDown,
  onPointerMove,
  onPointerUp,
  onReveal,
  revealed,
  showExamples,
  stats,
}: FlashcardPanelProps) {
  if (!card) {
    return (
      <section className="emptyState">
        <Layers size={28} aria-hidden="true" />
        <p>Nenhum card encontrado para a seleção atual.</p>
      </section>
    );
  }

  const rotate = dragOffset / 18;
  const intent = dragOffset > 30 ? "right" : dragOffset < -30 ? "left" : "";

  return (
    <section className="studyGrid">
      <div className="sessionStats">
        <span>{count} cards</span>
        <span>{index + 1} atual</span>
        <span>{stats.remembered} lembrei</span>
        <span>{stats.missed} revisar</span>
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
        <span className="chapterPill">Página {card.page}</span>
        {!revealed ? (
          <div className="cardFace">
            <div className="jpTerm">{termView(card)}</div>
            {showExamples && card.example?.ja && <p className="exampleJa">{card.example.ja}</p>}
          </div>
        ) : (
          <div className="cardFace back">
            <div className="meaningBlock">
              {card.meanings.pt && <p>{card.meanings.pt}</p>}
              {card.meanings.en && <small>{card.meanings.en}</small>}
            </div>
            {showExamples && (card.example?.pt || card.example?.en) && (
              <div className="exampleBack">
                {card.example?.pt && <p>{card.example.pt}</p>}
                {card.example?.en && <small>{card.example.en}</small>}
              </div>
            )}
          </div>
        )}
      </button>

      <div className="swipeActions">
        <button className="missed" type="button" onClick={() => onGrade("missed")}>
          <ArrowLeft size={20} aria-hidden="true" />
          Não lembrei
        </button>
        <button className="remembered" type="button" onClick={() => onGrade("remembered")}>
          Lembrei
          <ArrowRight size={20} aria-hidden="true" />
        </button>
      </div>

      {dataMode === "sample" && <p className="dataNote">Base de amostra ativa.</p>}
    </section>
  );
}

type ExercisesPanelProps = {
  chapters: Chapter[];
  exercises: ExerciseSet[];
  grades: Record<string, Grade>;
  onGrade: (exerciseId: string, grade: Grade) => void;
};

function ExercisesPanel({ chapters, exercises, grades, onGrade }: ExercisesPanelProps) {
  const chapterById = useMemo(() => new Map(chapters.map((chapter) => [chapter.id, chapter])), [chapters]);

  if (exercises.length === 0) {
    return (
      <section className="emptyState">
        <BookOpen size={28} aria-hidden="true" />
        <p>Nenhum exercício encontrado para a seleção atual.</p>
      </section>
    );
  }

  return (
    <section className="exerciseList">
      {exercises.map((exercise) => {
        const grade = grades[exercise.id];
        return (
          <article className={`exerciseItem ${grade ?? ""}`} key={exercise.id}>
            <div className="exerciseHeader">
              <div>
                <span>{chapterById.get(exercise.chapterId)?.title ?? exercise.title}</span>
                <small>Página {exercise.page}</small>
              </div>
              <div className="exerciseActions">
                <button
                  className={grade === "missed" ? "active missed" : "missed"}
                  type="button"
                  onClick={() => onGrade(exercise.id, "missed")}
                  title="Marcar para revisar"
                >
                  <X size={17} aria-hidden="true" />
                </button>
                <button
                  className={grade === "remembered" ? "active remembered" : "remembered"}
                  type="button"
                  onClick={() => onGrade(exercise.id, "remembered")}
                  title="Marcar como feito"
                >
                  <Check size={17} aria-hidden="true" />
                </button>
              </div>
            </div>
            <div className="exerciseText">
              {exercise.lines.map((line, lineIndex) => (
                <p key={`${exercise.id}-${lineIndex}`}>{line}</p>
              ))}
            </div>
          </article>
        );
      })}
    </section>
  );
}
