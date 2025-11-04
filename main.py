from datetime import date

import polars as pl
import streamlit as st

# ===========================
# CONFIGURACIÓN
# ===========================
st.set_page_config(page_title="Gestor de Presupuestos", page_icon="💰", layout="wide")
st.title("💰 Gestor de Presupuestos")
st.markdown(
    "Crea presupuestos seleccionando productos y variantes con precios distintos."
)

# ===========================
# DATOS FICTICIOS
# ===========================
productos = pl.DataFrame(
    {
        "id_producto": [1, 2, 3],
        "nombre": ["Puerta de madera", "Ventana de aluminio", "Pintura acrílica"],
        "categoria": ["Carpintería", "Carpintería", "Pintura"],
    }
)

variantes = pl.DataFrame(
    {
        "id_variante": [1, 2, 3, 4, 5],
        "id_producto": [1, 1, 2, 3, 3],
        "descripcion": [
            "Puerta 90x200",
            "Puerta 80x200",
            "Ventana 100x100",
            "Lata 4L blanca",
            "Lata 4L color",
        ],
        "precio_unitario": [250.0, 230.0, 180.0, 70.0, 85.0],
    }
)

# ===========================
# SIDEBAR
# ===========================
st.sidebar.header("Opciones")
accion = st.sidebar.selectbox(
    "Selecciona una acción", ["🧾 Nuevo presupuesto", "📊 Ver presupuestos"]
)

# ===========================
# CREAR NUEVO PRESUPUESTO
# ===========================
if accion == "🧾 Nuevo presupuesto":
    st.subheader("🧾 Crear nuevo presupuesto")

    cliente = st.text_input("Cliente")
    fecha = st.date_input("Fecha", value=date.today())

    st.markdown("### 🛠️ Agregar productos")

    # Producto seleccionado
    producto_sel = st.selectbox("Selecciona un producto", productos["nombre"].to_list())

    if producto_sel:
        id_prod = productos.filter(pl.col("nombre") == producto_sel)["id_producto"][0]
        variantes_prod = variantes.filter(pl.col("id_producto") == id_prod)

        variante_sel = st.selectbox(
            "Selecciona una variante", variantes_prod["descripcion"].to_list()
        )
        cantidad = st.number_input("Cantidad", min_value=1, step=1)

        if st.button("Agregar al presupuesto"):
            st.session_state.setdefault("items", [])
            var_info = variantes_prod.filter(
                pl.col("descripcion") == variante_sel
            ).to_dicts()[0]
            total_item = cantidad * var_info["precio_unitario"]

            st.session_state["items"].append(
                {
                    "Producto": producto_sel,
                    "Variante": variante_sel,
                    "Cantidad": cantidad,
                    "Precio Unitario": var_info["precio_unitario"],
                    "Subtotal": total_item,
                }
            )
            st.success(f"✅ {producto_sel} ({variante_sel}) agregado al presupuesto.")

    # Mostrar tabla del presupuesto actual
    if "items" in st.session_state and st.session_state["items"]:
        st.markdown("### 🧮 Detalle del presupuesto actual")
        df_items = pl.DataFrame(st.session_state["items"])
        st.dataframe(df_items.to_pandas(), use_container_width=True)
        total_general = df_items["Subtotal"].sum()
        st.markdown(f"### 💵 Total: **${total_general:.2f}**")

        if st.button("Finalizar presupuesto"):
            st.success("✅ Presupuesto generado (mockup, sin persistencia todavía).")

# ===========================
# VER PRESUPUESTOS (demo)
# ===========================
else:
    st.subheader("📊 Presupuestos guardados")
    st.info("Por ahora no hay persistencia, esta sección se implementará después.")
