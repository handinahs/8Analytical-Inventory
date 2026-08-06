from datetime import datetime
from pathlib import Path
import shutil

import streamlit as st
from utils.ui import render_brand_header

render_brand_header("💾 Backup do Banco")

DB_PATH = Path("estoque.db")
BACKUP_DIR = Path("backups")


def build_backup_name():
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    return f"backup_estoque_{timestamp}.db"


def create_backup():
    BACKUP_DIR.mkdir(exist_ok=True)
    backup_path = BACKUP_DIR / build_backup_name()
    shutil.copy2(DB_PATH, backup_path)
    return backup_path


if not DB_PATH.exists():
    st.error("Banco de dados estoque.db não encontrado na pasta do projeto.")
    st.stop()

file_size_mb = DB_PATH.stat().st_size / (1024 * 1024)
last_update = datetime.fromtimestamp(DB_PATH.stat().st_mtime).strftime("%d/%m/%Y %H:%M:%S")

col1, col2 = st.columns(2)

with col1:
    st.metric("Arquivo", DB_PATH.name)

with col2:
    st.metric("Tamanho", f"{file_size_mb:.2f} MB")

st.caption(f"Última alteração do banco: {last_update}")

st.divider()

st.subheader("Criar Backup")

st.info(
    "O backup cria uma cópia completa do banco atual. Seus dados continuam funcionando normalmente no app."
)

if st.button("Criar Backup Agora", type="primary", use_container_width=True):
    backup_path = create_backup()
    st.success(f"Backup criado com sucesso: {backup_path}")

st.divider()

st.subheader("Baixar Backup")

with DB_PATH.open("rb") as db_file:
    st.download_button(
        "Baixar Cópia do Banco Atual",
        data=db_file,
        file_name=build_backup_name(),
        mime="application/octet-stream",
        use_container_width=True,
    )

st.divider()

st.subheader("Backups Salvos")

if BACKUP_DIR.exists():
    backups = sorted(BACKUP_DIR.glob("backup_estoque_*.db"), reverse=True)
else:
    backups = []

if not backups:
    st.info("Nenhum backup salvo ainda.")
else:
    backup_rows = []

    for backup in backups[:20]:
        backup_rows.append({
            "Arquivo": backup.name,
            "Tamanho MB": round(backup.stat().st_size / (1024 * 1024), 2),
            "Criado em": datetime.fromtimestamp(backup.stat().st_mtime).strftime("%d/%m/%Y %H:%M:%S"),
        })

    st.dataframe(
        backup_rows,
        use_container_width=True,
        hide_index=True,
    )

