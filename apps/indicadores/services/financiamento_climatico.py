import re
from collections import defaultdict

from apps.indicadores.models import RegistroFinanciamento

CHART_COLORS = [
    "#2c7873",
    "#1a3d4d",
    "#6fb3b8",
    "#f4a261",
    "#e76f51",
    "#52b788",
    "#90e0ef",
    "#ffd166",
    "#ef476f",
    "#118ab2",
]


def _parse_num(v) -> float:
    if v is None:
        return 0.0
    if isinstance(v, (int, float)):
        return float(v)
    s = str(v).strip()
    if not s or s in ("nan", "None", "N/A", "-"):
        return 0.0
    s = re.sub(r"^\d{4}\s*[-–]\s*", "", s)
    s = s.replace("R$", "").replace("R $", "").strip()
    if "," in s:
        s = s.replace(".", "").replace(",", ".")
    else:
        s = s.replace(".", "")
    nums = re.findall(r"[\d]+\.?[\d]*", s)
    try:
        return float(nums[0]) if nums else 0.0
    except (ValueError, IndexError):
        return 0.0


def _fmt_brl(v) -> str:
    if v == 0:
        return "—"
    if v >= 1_000_000:
        return f"R$ {v/1_000_000:.1f} MI"
    if v >= 1_000:
        return f"R$ {v/1_000:.1f} MIL"
    return f"R$ {v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def _split_multi(val_str: str) -> list:
    if not val_str:
        return []
    return [v.strip() for v in val_str.split(",") if v.strip()]


def _aplicar_filtros(qs, filtros: dict):
    programa_vals = _split_multi(filtros.get("programa", ""))
    setor_vals = _split_multi(filtros.get("setor", ""))
    modalidade_vals = _split_multi(filtros.get("modalidade", ""))
    origem_vals = _split_multi(filtros.get("origem", ""))
    ente_vals = _split_multi(filtros.get("ente", ""))

    if programa_vals:
        qs = qs.filter(programa__in=programa_vals)
    if setor_vals:
        qs = qs.filter(setor__in=setor_vals)
    if modalidade_vals:
        qs = qs.filter(modalidade__in=modalidade_vals)
    if origem_vals:
        qs = qs.filter(origem__in=origem_vals)
    if ente_vals:
        qs = qs.filter(ente__in=ente_vals)

    return qs


# ── API pública ───────────────────────────────────────────────────


def get_filtros(lang: str = "pt") -> dict:
    qs = RegistroFinanciamento.objects.filter(lang=lang)

    def uniq(field):
        vals = qs.values_list(field, flat=True).distinct()
        return sorted({v for v in vals if v and v.strip() and not v.strip().isdigit()})

    return {
        "programas": uniq("programa"),
        "setores": uniq("setor"),
        "modalidades": uniq("modalidade"),
        "origens": uniq("origem"),
        "entes": uniq("ente"),
    }


def get_tabela(filtros: dict, lang: str = "pt") -> list:
    qs = RegistroFinanciamento.objects.filter(lang=lang)
    qs = _aplicar_filtros(qs, filtros)

    return [
        {
            "programa": reg.programa,
            "setor": reg.setor,
            "modalidade": reg.modalidade,
            "origem": reg.origem,
            "valor": reg.valor,
            "contrapartida": reg.contrapartida,
            "federal": reg.federal,
            "estadual": reg.estadual,
            "municipal": reg.municipal,
        }
        for reg in qs
    ]


def get_graficos(filtros: dict, lang: str = "pt") -> dict:
    qs = RegistroFinanciamento.objects.filter(lang=lang)
    qs = _aplicar_filtros(qs, filtros)
    registros = list(qs)

    # ── Gráfico 1: Valor por Setor ─────────────────────────────
    setor_totals: dict[str, float] = defaultdict(float)
    for reg in registros:
        if reg.setor:
            setor_totals[reg.setor] += _parse_num(reg.valor)

    if setor_totals:
        sorted_setor = sorted(setor_totals.items(), key=lambda x: x[1])
        setor_data = {
            "labels": [s for s, _ in sorted_setor],
            "values": [round(v, 2) for _, v in sorted_setor],
            "texts": [_fmt_brl(v) for _, v in sorted_setor],
        }
    else:
        setor_data = {"labels": [], "values": [], "texts": []}

    # ── Gráfico 2: Origem dos Recursos ─────────────────────────
    origem_counts: dict[str, int] = defaultdict(int)
    for reg in registros:
        if reg.origem:
            origem_counts[reg.origem] += 1

    if origem_counts:
        sorted_origem = sorted(origem_counts.items(), key=lambda x: -x[1])
        labels = [o for o, _ in sorted_origem]
        origem_data = {
            "labels": labels,
            "values": [c for _, c in sorted_origem],
            "colors": CHART_COLORS[: len(labels)],
        }
    else:
        origem_data = {"labels": [], "values": [], "colors": []}

    # ── Gráfico 3: Repasse por Ente Federado ───────────────────
    fed_v = sum(_parse_num(r.federal) for r in registros)
    est_v = sum(_parse_num(r.estadual) for r in registros)
    mun_v = sum(_parse_num(r.municipal) for r in registros)

    ente_labels = (
        ["Federal", "State", "Municipal"] if lang == "en" else ["Federal", "Estadual", "Municipal"]
    )
    ente_data = {
        "labels": ente_labels,
        "values": [round(fed_v, 2), round(est_v, 2), round(mun_v, 2)],
        "texts": [_fmt_brl(fed_v), _fmt_brl(est_v), _fmt_brl(mun_v)],
    }

    return {"setor": setor_data, "origem": origem_data, "ente": ente_data}
