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


def translate_columns(df):
    return df.rename(columns=COLUMN_LABELS)


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
