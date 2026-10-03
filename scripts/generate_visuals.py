import argparse
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch, Rectangle


DEFAULT_OUT = Path(__file__).resolve().parents[1] / "docs" / "images"
OUT = DEFAULT_OUT

NAVY = "#17324D"
BLUE = "#2F6B9A"
TEAL = "#2A8C82"
GOLD = "#D8A43B"
LIGHT = "#EDF3F7"
INK = "#24313D"
MUTED = "#607282"
WHITE = "#FFFFFF"


def setup(title: str, subtitle: str, size=(13.2, 7.4)):
    fig, ax = plt.subplots(figsize=size)
    fig.patch.set_facecolor(WHITE)
    ax.set_facecolor(WHITE)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    ax.text(0.04, 0.95, title, fontsize=20, fontweight="bold", color=NAVY, va="top")
    ax.text(0.04, 0.905, subtitle, fontsize=9.5, color=MUTED, va="top")
    return fig, ax


def box(ax, x, y, w, h, title, detail="", color=BLUE, fontsize=10):
    patch = FancyBboxPatch(
        (x, y), w, h,
        boxstyle="round,pad=0.008,rounding_size=0.014",
        linewidth=1.2, edgecolor=color, facecolor=WHITE,
    )
    ax.add_patch(patch)
    ax.add_patch(Rectangle((x, y + h - 0.014), w, 0.014, color=color, linewidth=0))
    ax.text(x + w / 2, y + h * 0.60, title, ha="center", va="center",
            fontsize=fontsize, fontweight="bold", color=INK)
    if detail:
        ax.text(x + w / 2, y + h * 0.28, detail, ha="center", va="center",
                fontsize=7.5, color=MUTED, linespacing=1.25)


def arrow(ax, p1, p2, color=MUTED, style="-"):
    ax.add_patch(FancyArrowPatch(
        p1, p2, arrowstyle="-|>", mutation_scale=12,
        linewidth=1.2, color=color, linestyle=style,
        connectionstyle="arc3,rad=0",
    ))


def architecture():
    fig, ax = setup(
        "Arquitectura preliminar del framework Lumina",
        "Diseño modular por responsabilidades; las etapas predictivas permanecen bloqueadas hasta recibir contrato y datos reales.",
    )

    box(ax, 0.05, 0.73, 0.20, 0.10, "Configuración + contrato", "YAML · roles · reglas · rutas", NAVY)
    box(ax, 0.31, 0.73, 0.20, 0.10, "ReadinessChecker", "Comprueba prerrequisitos", GOLD)
    box(ax, 0.57, 0.73, 0.20, 0.10, "PipelineOrchestrator", "Coordina; no mezcla funciones", TEAL)
    box(ax, 0.82, 0.73, 0.13, 0.10, "RunContext", "ID · fecha · estado", NAVY, 9)
    arrow(ax, (0.25, 0.78), (0.31, 0.78))
    arrow(ax, (0.51, 0.78), (0.57, 0.78))
    arrow(ax, (0.77, 0.78), (0.82, 0.78), style="--")

    stages = [
        ("1", "DataLoader", "CSV → DataFrame", BLUE),
        ("2", "DataValidator", "observa contrato", BLUE),
        ("3", "DataCleaner", "reglas explícitas", BLUE),
        ("4", "DataProfiler", "perfil genérico", TEAL),
        ("5", "EDAVisualizer", "figuras configuradas", TEAL),
        ("6", "DataPreprocessor", "split temporal + pipeline", GOLD),
        ("7", "ModelTrainer", "estimador externo", GOLD),
        ("8", "ModelEvaluator", "baseline + métricas", GOLD),
        ("9", "ReportGenerator", "JSON · tablas · figuras", NAVY),
    ]
    row1_x = [0.035, 0.225, 0.415, 0.605, 0.795]
    row2_x = [0.13, 0.35, 0.57, 0.79]
    positions = [(x, 0.52) for x in row1_x] + [(x, 0.35) for x in row2_x]
    w, h = 0.17, 0.115
    for i, ((num, name, detail, color), (x, y)) in enumerate(zip(stages, positions)):
        box(ax, x, y, w, h, name, detail, color, 8.5)
        ax.text(x + 0.012, y + h - 0.026, num, color=WHITE, fontsize=7.5,
                fontweight="bold", ha="center", va="center")
        if i < 4:
            arrow(ax, (x + w, y + h / 2), (row1_x[i + 1], y + h / 2), color="#8A9AA8")
        elif 5 <= i < 8:
            arrow(ax, (x + w, y + h / 2), (row2_x[i - 4], y + h / 2), color="#8A9AA8")
    arrow(ax, (0.88, 0.52), (0.215, 0.465), color="#8A9AA8")
    arrow(ax, (0.67, 0.73), (0.67, 0.64), color=TEAL)
    ax.text(0.67, 0.665, "coordina", fontsize=7.5, color=TEAL, ha="center")

    ax.add_patch(FancyBboxPatch(
        (0.05, 0.105), 0.90, 0.13,
        boxstyle="round,pad=0.012,rounding_size=0.012",
        facecolor=LIGHT, edgecolor="#C9D8E3", linewidth=1,
    ))
    ax.text(0.075, 0.207, "Compuertas de avance", fontsize=10.5, fontweight="bold", color=NAVY)
    gates = [
        (0.08, "Perfilado", "fuente + columnas"),
        (0.36, "Visualización", "roles configurados"),
        (0.64, "Modelado", "target + horizonte + datos suficientes"),
    ]
    for x, title, detail in gates:
        ax.text(x, 0.16, title, fontsize=9.2, fontweight="bold", color=INK)
        ax.text(x, 0.125, detail, fontsize=7.8, color=MUTED)
    ax.text(0.50, 0.045, "Estado actual: diseño y código verificables · ejecución analítica de Lumina: pendiente de datos reales",
            fontsize=9, color=NAVY, ha="center", fontweight="bold")
    fig.savefig(OUT / "arquitectura_framework.png", dpi=220, bbox_inches="tight", facecolor=WHITE)
    plt.close(fig)


def class_diagram():
    fig, ax = setup(
        "Mapa de clases y responsabilidades",
        "Cada clase tiene una función principal; el orquestador depende de interfaces pequeñas y resultados tipados.",
    )
    groups = [
        (0.04, 0.58, 0.22, 0.26, "core", NAVY, ["FrameworkConfig", "DatasetContract", "ReadinessChecker", "RunContext"]),
        (0.29, 0.58, 0.22, 0.26, "data", BLUE, ["DataLoader", "DataValidator", "DataCleaner", "DataProfiler"]),
        (0.54, 0.58, 0.20, 0.26, "analysis", TEAL, ["EDAVisualizer", "DataPreprocessor"]),
        (0.77, 0.58, 0.19, 0.26, "modeling", GOLD, ["ModelTrainer", "ModelEvaluator"]),
    ]
    for x, y, w, h, title, color, items in groups:
        ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.01,rounding_size=0.012",
                                    facecolor=WHITE, edgecolor=color, linewidth=1.3))
        ax.add_patch(Rectangle((x, y + h - 0.055), w, 0.055, color=color, linewidth=0))
        ax.text(x + 0.015, y + h - 0.028, title, color=WHITE, fontsize=10, fontweight="bold", va="center")
        for j, item in enumerate(items):
            yy = y + h - 0.09 - j * 0.043
            ax.text(x + 0.018, yy, item, fontsize=8.5, color=INK, va="center")
            if j < len(items) - 1:
                ax.plot([x + 0.015, x + w - 0.015], [yy - 0.021, yy - 0.021], color="#E5EBF0", lw=0.7)

    box(ax, 0.22, 0.30, 0.25, 0.13, "PipelineOrchestrator", "assess() · run_profile()", TEAL, 10)
    box(ax, 0.54, 0.30, 0.22, 0.13, "ReportGenerator", "serializa resultados y manifiesto", NAVY, 10)
    arrow(ax, (0.15, 0.58), (0.30, 0.43))
    arrow(ax, (0.40, 0.58), (0.37, 0.43))
    arrow(ax, (0.64, 0.58), (0.45, 0.43))
    arrow(ax, (0.86, 0.58), (0.47, 0.38), style="--")
    arrow(ax, (0.47, 0.365), (0.54, 0.365))

    ax.add_patch(FancyBboxPatch((0.08, 0.09), 0.84, 0.11, boxstyle="round,pad=0.012,rounding_size=0.012",
                                facecolor=LIGHT, edgecolor="#C9D8E3", linewidth=1))
    ax.text(0.10, 0.158, "Resultados tipados", fontsize=10, fontweight="bold", color=NAVY)
    ax.text(0.10, 0.118,
            "ReadinessResult · ValidationResult · CleaningResult · ProfileResult · PreprocessingResult · TrainingResult · EvaluationResult · RunResult",
            fontsize=8.2, color=INK)
    fig.savefig(OUT / "mapa_clases.png", dpi=220, bbox_inches="tight", facecolor=WHITE)
    plt.close(fig)


def proposed_visualizations():
    fig, axes = plt.subplots(1, 3, figsize=(13.2, 4.8))
    fig.patch.set_facecolor(WHITE)
    fig.suptitle("Visualizaciones exploratorias propuestas", x=0.055, ha="left", y=0.98,
                 fontsize=20, fontweight="bold", color=NAVY)
    fig.text(0.055, 0.91, "Bocetos conceptuales: no contienen observaciones, escalas ni resultados de Lumina.",
             fontsize=9.5, color=MUTED)

    titles = ["Serie temporal", "Mapa de calor", "Distribución y atípicos"]
    questions = [
        "¿Cómo cambian ventas o demanda\npor periodo y unidad de análisis?",
        "¿Qué segmentos muestran patrones\ndistintos por categoría y ubicación?",
        "¿Hay dispersión, asimetría o valores\nque requieran validación de negocio?",
    ]
    for ax, title, question in zip(axes, titles, questions):
        ax.set_facecolor(WHITE)
        ax.set_xticks([])
        ax.set_yticks([])
        for spine in ax.spines.values():
            spine.set_color("#CDD8E1")
        ax.set_title(title, loc="left", fontsize=12, fontweight="bold", color=NAVY, pad=12)
        ax.text(0.0, -0.16, question, transform=ax.transAxes, fontsize=8.5, color=MUTED, va="top")

    # Esquema de serie, sin escalas ni valores.
    axes[0].plot([0.08, 0.08, 0.92], [0.86, 0.12, 0.12], color="#A8B7C3", lw=1.2)
    axes[0].plot([0.12, 0.27, 0.42, 0.58, 0.73, 0.88],
                 [0.30, 0.45, 0.37, 0.66, 0.58, 0.78], color=TEAL, lw=2.3)
    axes[0].scatter([0.12, 0.27, 0.42, 0.58, 0.73, 0.88],
                    [0.30, 0.45, 0.37, 0.66, 0.58, 0.78], color=TEAL, s=20)
    axes[0].text(0.5, 0.02, "tiempo", ha="center", color=MUTED, fontsize=8)

    # Matriz ilustrativa sin valores.
    palette = [[LIGHT, "#CFE2E0", "#8FC3BD", "#5AA59D"],
               ["#DDE8EF", "#9BBFD5", "#5F91B1", "#376E94"],
               ["#F3E7C9", "#E6C978", "#D8A43B", "#B47A16"]]
    for row in range(3):
        for col in range(4):
            axes[1].add_patch(Rectangle((0.13 + col * 0.19, 0.25 + row * 0.18), 0.17, 0.16,
                                        color=palette[row][col], ec=WHITE, lw=1))
    axes[1].text(0.5, 0.12, "segmentos configurables", ha="center", color=MUTED, fontsize=8)

    # Cajas ilustrativas sin etiquetas numéricas.
    for i, (cx, color, low, q1, med, q3, high) in enumerate([
        (0.28, BLUE, 0.22, 0.36, 0.48, 0.63, 0.80),
        (0.68, GOLD, 0.18, 0.29, 0.43, 0.56, 0.74),
    ]):
        axes[2].plot([cx, cx], [low, high], color=color, lw=1.5)
        axes[2].plot([cx - 0.08, cx + 0.08], [low, low], color=color, lw=1.5)
        axes[2].plot([cx - 0.08, cx + 0.08], [high, high], color=color, lw=1.5)
        axes[2].add_patch(Rectangle((cx - 0.12, q1), 0.24, q3 - q1, fill=False, ec=color, lw=2))
        axes[2].plot([cx - 0.12, cx + 0.12], [med, med], color=color, lw=2)
    axes[2].scatter([0.68], [0.86], s=28, facecolors=WHITE, edgecolors=GOLD, lw=1.5)
    axes[2].text(0.48, 0.08, "grupos definidos en el contrato", ha="center", color=MUTED, fontsize=8)

    fig.subplots_adjust(left=0.055, right=0.97, top=0.82, bottom=0.25, wspace=0.22)
    fig.savefig(OUT / "visualizaciones_propuestas.png", dpi=220, bbox_inches="tight", facecolor=WHITE)
    plt.close(fig)


def generate_all(output_dir: Path) -> tuple[Path, ...]:
    """Genera los tres visuales conceptuales sin utilizar datos de negocio."""

    global OUT
    OUT = output_dir
    OUT.mkdir(parents=True, exist_ok=True)

    architecture()
    class_diagram()
    proposed_visualizations()

    return (
        OUT / "arquitectura_framework.png",
        OUT / "mapa_clases.png",
        OUT / "visualizaciones_propuestas.png",
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Genera los diagramas reproducibles del framework Lumina."
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_OUT,
        help="Carpeta donde se guardarán los tres archivos PNG.",
    )
    return parser.parse_args()


if __name__ == "__main__":
    paths = generate_all(parse_args().output_dir)
    print("Visuales creados:")
    for path in paths:
        print(f"- {path.resolve()}")

