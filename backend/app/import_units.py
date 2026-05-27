from __future__ import annotations

import argparse

from sqlalchemy import delete, select

from app.db import Base, engine, get_session
from app.models import Unit


def _cnpj_join(primary: str | None, obs: str | None) -> str | None:
    parts: list[str] = []
    if primary and primary.strip() and primary.strip() != "-":
        parts.append(primary.strip())
    if obs and obs.strip() and obs.strip() != "-":
        raw = obs.strip()
        # separators in the sheet are " - " (not the hyphen inside CNPJ suffixes)
        for p in raw.split(" - "):
            p = p.strip().strip(",")
            if p and p != "-":
                parts.append(p)
    if not parts:
        return None
    # dedupe preserving order
    seen: set[str] = set()
    out: list[str] = []
    for p in parts:
        if p in seen:
            continue
        seen.add(p)
        out.append(p)
    return "; ".join(out)


UNITS: list[dict[str, str | None]] = [
    {"external_id": "028", "name": "Alameda", "cnpj": _cnpj_join("46.293.199/0001-94", "51.404.209/0001-51 - 50.926.356/0001-29"), "address": "Rua Arlindo Marchetti, 338"},
    {"external_id": "223", "name": "xxxx (223)", "cnpj": _cnpj_join("47.366.534/0001-08", None), "address": "Evoque Academia XIV LTDA ( BUTATÃ)"},
    {"external_id": "224", "name": "xxxx (224)", "cnpj": _cnpj_join("43.907.713/0001-46", None), "address": "PB8 02 Academia de Ginastica LTDA"},
    {"external_id": "225", "name": "xxxx (225)", "cnpj": _cnpj_join("55.012.616/0001-74", None), "address": "Evoque Fitness Goiania LTDA"},
    {"external_id": "226", "name": "xxxx (226)", "cnpj": _cnpj_join("21.450.425/0001-72", None), "address": "LOURIVAL CARMO MONACO & CIA LTDA - EPP (CERTIFICADO A3)"},
    {"external_id": "001", "name": "Guilhermina", "cnpj": _cnpj_join("47.647.908/0001-55", "31.834.358/0017-00"), "address": "Rua Flamengo, 321"},
    {"external_id": "004", "name": "Diadema", "cnpj": _cnpj_join("31.834.358/0028-63", "47.370.893/0001-11"), "address": "Av. Antônio Piranga, 887"},
    {"external_id": "005", "name": "Shopping Maua", "cnpj": _cnpj_join("31.834.358/0001-43", "31.834.358/0003-05 - 31.834.358/0012-04"), "address": "Mauá Plaza Shopping, Av. Gov. Mario Covas Júnior"},
    {"external_id": "006", "name": "Ribeirão", "cnpj": _cnpj_join("38.444.145/0001-54", "31.834.358/0014-68"), "address": "Av. Francisco Monteiro, 702"},
    {"external_id": "007", "name": "Homero thon", "cnpj": _cnpj_join("40.018.076/0001-69", None), "address": "Rua Giovanni Battista Pirelli, 1645"},
    {"external_id": "008", "name": "Portugal", "cnpj": _cnpj_join("31.834.358/0019-72", "41.905.020/0001-99"), "address": "Av. Portugal, 472 - Jardim Pilar"},
    {"external_id": "009", "name": "Valo Velho", "cnpj": _cnpj_join("31.834.358/0008-10", "43.759.273/0001-81"), "address": "Estrada de Itapecerica, 8742"},
    {"external_id": "010", "name": "Itamarati", "cnpj": _cnpj_join("31.834.358/0011-15", "46.501.833/0001-37"), "address": "Av. Itamarati, 2890"},
    {"external_id": "011", "name": "Rio Branco", "cnpj": _cnpj_join("46.240.161/0001-53", "31.834.358/0010-34"), "address": "Av. Rio Branco, 1457"},
    {"external_id": "012", "name": "Pereira Barreto", "cnpj": _cnpj_join("46.505.951/0001-13", None), "address": "Av. Pereira Barreto, 900"},
    {"external_id": "013", "name": "Giovani Breda", "cnpj": _cnpj_join("47.011.718/0001-47", None), "address": "Praça Giovani Breda, 1678"},
    {"external_id": "014", "name": "Boqueirão", "cnpj": _cnpj_join("31.834.358/0016-20", "44.683.895/0001-81"), "address": "Av. Pres. Castelo Branco, 1486"},
    {"external_id": "015", "name": "Parque do Carmo", "cnpj": _cnpj_join("48.465.034/0001-88", "31.834.358/0026-00"), "address": "Av. Afonso de Sampaio e Sousa, 558"},
    {"external_id": "016", "name": "Zaíra", "cnpj": _cnpj_join("50.164.971/0001-45", None), "address": "Av. Brigadeiro Faria Lima, 43"},
    {"external_id": "017", "name": "Heliópolis", "cnpj": _cnpj_join("50.165.014/0001-33", None), "address": "Av. Alm. Delamare, 1641"},
    {"external_id": "018", "name": "Corporativo", "cnpj": _cnpj_join("49.540.642/0001-72", None), "address": None},
    {"external_id": "019", "name": "Pimentas", "cnpj": _cnpj_join("50.165.271/0001-75", None), "address": "Av. José Miguel Ackel, 1032"},
    {"external_id": "020", "name": "Guaianases", "cnpj": _cnpj_join("51.108.528/0001-10", None), "address": "Rua Luís Mateus, 618"},
    {"external_id": "021", "name": "Av Goias", "cnpj": _cnpj_join("47.367.634/0001-40", "31.834.358/0025-10"), "address": "Av. Goiás, 1631"},
    {"external_id": "022", "name": "Bom Clima", "cnpj": _cnpj_join("51.241.515/0001-14", "31.834.358/0023-59"), "address": "Av. João Bernardo Medeiros, 425"},
    {"external_id": "024", "name": "Jaguare", "cnpj": _cnpj_join("31.834.358/0024-30", "51.245.230/0001-51 - 51.241.235/0001-06"), "address": "Praça Bento de Assis, 14"},
    {"external_id": "025", "name": "Itaquera Tennessee", "cnpj": _cnpj_join("51.404.136/0001-06", "51.241.683/0001-00 - 31.834.358/0027-82"), "address": "Rua Padre Viegas de Menezes, 445"},
    {"external_id": "026", "name": "Extrema", "cnpj": _cnpj_join("52.528.857/0001-82", "51.451.055/0001-59"), "address": "Av. Vereador José Ferreira, 607"},
    {"external_id": "027", "name": "Mogi das Cruzes", "cnpj": _cnpj_join("51.404.126/0001-62", "31.834.358/0029-44"), "address": "Av. Braz de Pina, 509"},
    {"external_id": "029", "name": "Jardim Goias", "cnpj": _cnpj_join("17.662.322/0001-07", None), "address": "Rua Cinquenta e Quatro, 208"},
    {"external_id": "030", "name": "Passeio das Aguas", "cnpj": _cnpj_join("20.972.975/0001-99", None), "address": "Av. Perimetral Norte, 8303"},
    {"external_id": "031", "name": "São Vicente", "cnpj": _cnpj_join("51.408.082/0001-49", "31.834.358/0009-09"), "address": "Av. Presidente Wilson, 962"},
    {"external_id": "032", "name": "Camilópolis", "cnpj": _cnpj_join("51.241.439/0001-47", None), "address": "Rua Olímpia, 307"},
    {"external_id": "033", "name": "Indaiatuba", "cnpj": _cnpj_join("31.834.358/0005-77", None), "address": "Av. Eng. Fábio Roberto Barnabé, 2685"},
    {"external_id": "034", "name": "Vila Prudente", "cnpj": _cnpj_join("52.272.330/0001-30", "52.272.308/0001-90 - 31.834.358/0020-06"), "address": "Av. Professor Luiz Ignácio Anhaia Mello, 3660"},
    {"external_id": "035", "name": "Laranjal Paulista", "cnpj": _cnpj_join("31.834.358/0006-58", "52.353.867/0001-24"), "address": "Av. Cesário Carlos de Almeida, 92"},
    {"external_id": "036", "name": "Sacomã", "cnpj": _cnpj_join("51.536.950/0001-76", "31.834.358/0021-97"), "address": "Estrada das Lágrimas, 810"},
    {"external_id": "037", "name": "Vila Nova", "cnpj": _cnpj_join("31.834.358/0007-39", None), "address": "Av. Quinta Avenida, S/N"},
    {"external_id": "038", "name": "Sapopemba", "cnpj": _cnpj_join("31.834.358/0002-24", None), "address": None},
    {"external_id": "039", "name": "Poa", "cnpj": _cnpj_join("31.834.358/0013-87", None), "address": None},
    {"external_id": "040", "name": "Curitiba", "cnpj": _cnpj_join("31.834.358/0018-91", None), "address": None},
    {"external_id": "041", "name": "Franca", "cnpj": _cnpj_join("31.834.358/0015-49", None), "address": None},
    {"external_id": "042", "name": "Itaquera Americano", "cnpj": None, "address": None},
    {"external_id": "043", "name": "Centro Alto", "cnpj": None, "address": None},
    {"external_id": "044", "name": "Paraisopolis", "cnpj": None, "address": None},
    {"external_id": "045", "name": "Guapituba", "cnpj": None, "address": None},
    {"external_id": "046", "name": "Rui Barbosa", "cnpj": None, "address": None},
    {"external_id": "047", "name": "Ipiranga Silva Bueno", "cnpj": None, "address": None},
    {"external_id": "048", "name": "Vila Luzita", "cnpj": None, "address": None},
    {"external_id": "049", "name": "Ipiranga Clube", "cnpj": None, "address": None},
    {"external_id": "050", "name": "Tres Barras", "cnpj": None, "address": None},
    {"external_id": "130", "name": "Jardim São Paulo", "cnpj": _cnpj_join("31.834.358/0004-96", None), "address": "Rua Sarautaia, 205"},
    {"external_id": "131", "name": "Carapicuíba", "cnpj": _cnpj_join("52.272.262/0001-62", None), "address": "Estrada da Fazendinha, 50"},
]


def replace_units() -> int:
    Base.metadata.create_all(bind=engine)
    with get_session() as session:
        session.execute(delete(Unit))
        session.commit()
        for u in UNITS:
            session.add(Unit(name=u["name"].strip(), external_id=u["external_id"], cnpj=u["cnpj"], address=u["address"]))
        session.commit()
    return len(UNITS)


def upsert_units() -> tuple[int, int]:
    Base.metadata.create_all(bind=engine)
    created = 0
    updated = 0
    with get_session() as session:
        for u in UNITS:
            name = (u["name"] or "").strip()
            external_id = (u["external_id"] or "").strip() or None
            cnpj = (u["cnpj"] or "").strip() or None
            address = (u["address"] or "").strip() or None

            existing = session.scalar(select(Unit).where(Unit.name == name))
            if existing:
                existing.external_id = external_id
                existing.cnpj = cnpj
                existing.address = address
                updated += 1
            else:
                session.add(Unit(name=name, external_id=external_id, cnpj=cnpj, address=address))
                created += 1
        session.commit()
    return created, updated


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--replace", action="store_true", help="Substitui toda a tabela units pelos dados atuais.")
    args = parser.parse_args()

    if args.replace:
        total = replace_units()
        print(f"OK replaced total={total}")
    else:
        c, u = upsert_units()
        print(f"OK created={c} updated={u} total={len(UNITS)}")
