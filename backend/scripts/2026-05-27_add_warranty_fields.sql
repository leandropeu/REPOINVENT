-- Migracao (SQLite) - adiciona campos de garantia na tabela equipment
-- Observacao: SQLite nao suporta "ADD COLUMN IF NOT EXISTS".
-- Se a coluna ja existir, remova a linha correspondente antes de executar.

ALTER TABLE equipment ADD COLUMN warranty INTEGER NOT NULL DEFAULT 0;
ALTER TABLE equipment ADD COLUMN warranty_expires_at DATE NULL;
ALTER TABLE equipment ADD COLUMN operator TEXT NULL;
ALTER TABLE equipment ADD COLUMN contract TEXT NULL;
