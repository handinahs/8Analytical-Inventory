from pathlib import Path

import pandas as pd
import streamlit as st
import streamlit.components.v1 as components


COLUMN_LABELS = {
    "Code": "Código",
    "Description": "Descrição",
    "Product": "Produto",
    "Unit": "Unidade",
    "Location": "Posição",
    "Quantity": "Quantidade",
    "Observation": "Observação",
    "Date": "Data",
    "Type": "Tipo",
    "Status": "Status",
    "Item": "Item",
    "To Buy": "Para Comprar",
    "In Stock": "Em Estoque",
    "Current_Stock": "Estoque Atual",
    "Current_Stock_Report": "Em Estoque",
}

DATE_COLUMNS = {
    "Date",
    "Data",
    "Cancellation_Date",
    "Data do Cancelamento",
}


def format_date_value(value):
    if value is None or pd.isna(value) or str(value).strip() == "":
        return ""

    parsed = pd.to_datetime(value, errors="coerce")
    if pd.isna(parsed):
        return value

    return parsed.strftime("%d/%m/%Y")


def format_date_columns(df):
    formatted_df = df.copy()

    for column in formatted_df.columns:
        if column in DATE_COLUMNS:
            formatted_df[column] = formatted_df[column].apply(format_date_value)

    return formatted_df


def translate_columns(df):
    return df.rename(columns=COLUMN_LABELS)


def format_and_translate_columns(df):
    return translate_columns(format_date_columns(df))


def render_brand_header(page_title):
    logo_path = Path("assets/logo_8analytical_inventory.png")

    if logo_path.exists():
        col_logo, col_brand = st.columns([0.08, 0.92])

        with col_logo:
            st.image(str(logo_path), width=46)

        with col_brand:
            st.markdown("**8Analytical Inventory**")
            st.caption("Controle de estoque e almoxarifado")
    else:
        st.markdown("**8Analytical Inventory**")
        st.caption("Controle de estoque e almoxarifado")

    st.title(page_title)


def enable_select_all_inputs():
    components.html(
        """
        <script>
        const doc = window.parent.document;

        function selectAll(element) {
            window.setTimeout(() => {
                try {
                    element.select();
                } catch (error) {
                    try {
                        element.setSelectionRange(0, element.value.length);
                    } catch (ignored) {}
                }
            }, 0);
        }

        function bindSelectAll() {
            const fields = doc.querySelectorAll('input:not([type="checkbox"]):not([type="radio"]), textarea');

            fields.forEach((field) => {
                if (field.dataset.selectAllOnFocus === 'true') {
                    return;
                }

                field.dataset.selectAllOnFocus = 'true';

                field.addEventListener('focus', () => selectAll(field));
                field.addEventListener('click', () => selectAll(field));
                field.addEventListener('mouseup', (event) => event.preventDefault());
            });
        }

        bindSelectAll();
        new MutationObserver(bindSelectAll).observe(doc.body, {
            childList: true,
            subtree: true
        });
        </script>
        """,
        height=0,
        width=0,
    )
