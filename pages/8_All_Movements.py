import streamlit as st
from utils.ui import enable_select_all_inputs, format_and_translate_columns, format_date_value, render_brand_header

from utils.movements import (
    get_all_movements,
    cancel_movement
)

render_brand_header("📋 Todas as Movimentações")

enable_select_all_inputs()

# -------------------
# FILTERS
# -------------------

movement_type_options = {
    "Todos": "ALL",
    "Entrada": "IN",
    "Saída": "OUT",
}

movement_type_label = {
    "IN": "Entrada",
    "OUT": "Saída",
}

col1, col2 = st.columns(2)

with col1:
    movement_type_display = st.selectbox(
        "Tipo de Movimentação",
        list(movement_type_options.keys())
    )
    movement_type = movement_type_options[movement_type_display]

with col2:
    search = st.text_input(
        "Buscar Produto"
    )

# -------------------
# LOAD DATA
# -------------------

df = get_all_movements(
    movement_type,
    search
)

df["Status_Code"] = df["Status"]

df["Status"] = df["Status"].map({
    1: "🟢 Ativa",
    0: "🔴 Cancelada"
})

# -------------------
# TABLE
# -------------------

display_df = df.drop(columns=["id", "Status_Code"]).copy()
display_df["Type"] = display_df["Type"].map(movement_type_label).fillna(display_df["Type"])

display_df = display_df.rename(columns={
    "Cancellation_Reason": "Motivo do Cancelamento",
    "Cancellation_Date": "Data do Cancelamento",
})

st.data_editor(
    format_and_translate_columns(display_df),
    use_container_width=True,
    hide_index=True,
    disabled=True
)

st.info(f"Total de registros: {len(df)}")

st.divider()

# -------------------
# SELECT MOVEMENT
# -------------------

if len(df) > 0:

    options = {}

    for _, row in df.iterrows():

        label = (
            f"{format_date_value(row['Date'])} | "
            f"{movement_type_label.get(row['Type'], row['Type'])} | "
            f"{row['Product']} | "
            f"Qtd: {row['Quantity']}"
        )

        options[label] = row["id"]

    selected = st.selectbox(
        "Selecionar Movimentação",
        list(options.keys())
    )

    movement_id = options[selected]

    movement = df[df["id"] == movement_id].iloc[0]

    st.subheader("Detalhes da Movimentação")

    col1, col2 = st.columns(2)

    with col1:
        st.write(f"**Data:** {format_date_value(movement['Date'])}")
        st.write(f"**Código:** {movement['Code']}")
        st.write(f"**Produto:** {movement['Product']}")
        st.write(f"**Tipo:** {movement_type_label.get(movement['Type'], movement['Type'])}")

    with col2:
        st.write(f"**Quantidade:** {movement['Quantity']}")
        st.write(f"**Observação:** {movement['Observation']}")
        st.write(f"**Status:** {movement['Status']}")

        if movement["Status_Code"] == 0:
            st.write(f"**Motivo do Cancelamento:** {movement['Cancellation_Reason'] or '-'}")
            st.write(f"**Data do Cancelamento:** {format_date_value(movement['Cancellation_Date']) or '-'}")

    st.divider()

    if movement["Status_Code"] == 1:

        st.subheader("Cancelar Movimentação")

        cancellation_reason = st.text_area(
            "Motivo do cancelamento",
            placeholder="Explique por que esta movimentação está sendo cancelada."
        )

        confirm_cancel = st.checkbox(
            "Confirmo que desejo cancelar esta movimentação."
        )

        can_cancel = cancellation_reason.strip() and confirm_cancel

        if not can_cancel:
            st.info("Preencha o motivo e marque a confirmação para liberar o cancelamento.")

        if st.button(
            "❌ Cancelar Movimentação",
            type="primary",
            use_container_width=True,
            disabled=not can_cancel,
        ):

            rows_updated = cancel_movement(movement_id, cancellation_reason)

            if rows_updated:
                st.success(
                    "Movimentação cancelada com sucesso!"
                )
                st.rerun()
            else:
                st.warning("Esta movimentação já estava cancelada ou não foi encontrada.")

    else:

        st.warning("Esta movimentação já foi cancelada.")

else:

    st.warning("Nenhuma movimentação encontrada.")


