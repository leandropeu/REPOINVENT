from __future__ import annotations

from sqlalchemy import select

from app.db import Base, engine, get_session
from app.models import Unit


UNITS: list[dict[str, str | None]] = [
    {"name": "Alameda", "external_id": "028", "cnpj": None, "address": "Rua Arlindo Marchetti, 338 - SP"},
    {"name": "Av Goias", "external_id": "021", "cnpj": None, "address": "Av. Goiás, 1631 - SP"},
    {"name": "Bom Clima", "external_id": "022", "cnpj": None, "address": "Av. João Bernardo Medeiros, 425 - SP"},
    {"name": "Boqueirão", "external_id": "014", "cnpj": None, "address": "Av. Pres. Castelo Branco, 1486 - SP"},
    {"name": "Camilópolis", "external_id": "032", "cnpj": None, "address": "Rua Olímpia, 307 - SP"},
    {"name": "Carapicuíba", "external_id": "131", "cnpj": None, "address": "Estrada da Fazendinha, 50 - SP"},
    {"name": "Centro Alto", "external_id": "043", "cnpj": None, "address": "- SP"},
    {"name": "Curitiba", "external_id": "040", "cnpj": None, "address": "- PR"},
    {"name": "Diadema", "external_id": "004", "cnpj": None, "address": "Av. Antônio Piranga, 887 - SP"},
    {"name": "Extrema", "external_id": "026", "cnpj": None, "address": "Av. Vereador José Ferreira, 607 - MG"},
    {"name": "Franca", "external_id": "041", "cnpj": None, "address": "- SP"},
    {"name": "Giovani Breda", "external_id": "013", "cnpj": None, "address": "Praça Giovani Breda, 1678 - SP"},
    {"name": "Guaianases", "external_id": "020", "cnpj": None, "address": "Rua Luís Mateus, 618 - SP"},
    {"name": "Guapituba", "external_id": "045", "cnpj": None, "address": "- SP"},
    {"name": "Guilhermina", "external_id": "001", "cnpj": None, "address": "Rua Flamengo, 321 - SP"},
    {"name": "Heliópolis", "external_id": "017", "cnpj": None, "address": "Av. Alm. Delamare, 1641 - SP"},
    {"name": "Homero thon", "external_id": "007", "cnpj": None, "address": "Rua Giovanni Battista Pirelli, 1645 - SP"},
    {"name": "Indaiatuba", "external_id": "033", "cnpj": None, "address": "Av. Eng. Fábio Roberto Barnabé, 2685 - SP"},
    {"name": "Ipiranga Clube", "external_id": "049", "cnpj": None, "address": "- SP"},
    {"name": "Ipiranga Silva Bueno", "external_id": "047", "cnpj": None, "address": "- SP"},
    {"name": "Itamarati", "external_id": "010", "cnpj": None, "address": "Av. Itamarati, 2890 - SP"},
    {"name": "Itaquera Americano", "external_id": "042", "cnpj": None, "address": "- SP"},
    {"name": "Itaquera Tennessee", "external_id": "025", "cnpj": None, "address": "Rua Padre Viegas de Menezes, 445 - SP"},
    {"name": "Jaguare", "external_id": "024", "cnpj": None, "address": "Praça Bento de Assis, 14 - SP"},
    {"name": "Jardim Goias", "external_id": "029", "cnpj": None, "address": "Rua Cinquenta e Quatro, 208 - GO"},
    {"name": "Jardim São Paulo", "external_id": "130", "cnpj": None, "address": "Rua Sarautaia, 205 - GO"},
    {"name": "Laranjal Paulista", "external_id": "035", "cnpj": None, "address": "Av. Cesário Carlos de Almeida, 92 - SP"},
    {"name": "Mogi das Cruzes", "external_id": "027", "cnpj": None, "address": "Av. Braz de Pina, 509 - SP"},
    {"name": "Paraisopolis", "external_id": "044", "cnpj": None, "address": "- SP"},
    {"name": "Parque do Carmo", "external_id": "015", "cnpj": None, "address": "Av. Afonso de Sampaio e Sousa, 558 - SP"},
    {"name": "Passeio das Aguas", "external_id": "030", "cnpj": None, "address": "Av. Perimetral Norte, 8303 - GO"},
    {"name": "Pereira Barreto", "external_id": "012", "cnpj": None, "address": "Av. Pereira Barreto, 900 - SP"},
    {"name": "Pimentas", "external_id": "019", "cnpj": None, "address": "Av. José Miguel Ackel, 1032 - SP"},
    {"name": "Poa", "external_id": "039", "cnpj": None, "address": "- SP"},
    {"name": "Portugal", "external_id": "008", "cnpj": None, "address": "Av. Portugal, 472 - Jardim Pilar - SP"},
    {"name": "Ribeirão", "external_id": "006", "cnpj": None, "address": "Av. Francisco Monteiro, 702 - SP"},
    {"name": "Rio Branco", "external_id": "011", "cnpj": None, "address": "Av. Rio Branco, 1457 - SP"},
    {"name": "Rui Barbosa", "external_id": "046", "cnpj": None, "address": "- MS"},
    {"name": "Sacomã", "external_id": "036", "cnpj": None, "address": "Estrada das Lágrimas, 810 - SP"},
    {"name": "Sapopemba", "external_id": "038", "cnpj": None, "address": "- SP"},
    {"name": "Shopping Maua", "external_id": "005", "cnpj": None, "address": "Mauá Plaza Shopping, Av. Gov. Mario Covas Júnior - SP"},
    {"name": "São Vicente", "external_id": "031", "cnpj": None, "address": "Av. Presidente Wilson, 962 - SP"},
    {"name": "Tres Barras", "external_id": "050", "cnpj": None, "address": "- MS"},
    {"name": "Valo Velho", "external_id": "009", "cnpj": None, "address": "Estrada de Itapecerica, 8742 - SP"},
    {"name": "Vila Luzita", "external_id": "048", "cnpj": None, "address": "- SP"},
    {"name": "Vila Nova", "external_id": "037", "cnpj": None, "address": "Av. Quinta Avenida, S/N - GO"},
    {
        "name": "Vila Prudente",
        "external_id": "034",
        "cnpj": None,
        "address": "Av. Professor Luiz Ignácio Anhaia Mello, 3660 - SP",
    },
    {"name": "Zaíra", "external_id": "016", "cnpj": None, "address": "Av. Brigadeiro Faria Lima, 43 - SP"},
]


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
    c, u = upsert_units()
    print(f"OK created={c} updated={u} total={len(UNITS)}")

