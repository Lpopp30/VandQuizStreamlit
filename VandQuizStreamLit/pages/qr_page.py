from io import BytesIO
import qrcode
import streamlit as st

# --- 3. QR-KODE GENERATOR (SIDEBAR OG BUND) ---
st.markdown("---")
st.header("📱 Generer QR-kode til siden")
st.write(
    "Indtast linket til din live hjemmeside (eller en infoside om vand), så"
    " laves der en QR-kode:"
)

# Indstillinger i sidebaren til QR-koden
st.sidebar.header("QR-kode Indstillinger")
box_size = st.sidebar.slider(
    "QR Størrelse (Resolution)", min_value=5, max_value=20, value=10
)
border_size = st.sidebar.slider(
    "QR Kantbredde", min_value=1, max_value=5, value=2
)

# Felt til URL
default_url = "https://vandquizapp-mz5wyvntkhf9hyarhqyrnn.streamlit.app/"

if default_url:
  # Generer QR-koden ved hjælp af qrcode-biblioteket
  qr = qrcode.QRCode(
      version=1,
      error_correction=qrcode.constants.ERROR_CORRECT_M,
      box_size=box_size,
      border=border_size,
  )
  qr.add_data(default_url)
  qr.make(fit=True)

  # Lav billedet
  img = qr.make_image(fill_color="black", back_color="white")

  # Gem i hukommelsen til Streamlit
  buf = BytesIO()
  img.save(buf, format="PNG")
  byte_im = buf.getvalue()

# Du kan f.eks. bare slette st.columns og lade QR-koden ligge direkte på siden, eller rette den til:
col1 = st.container()
with col1:
  st.subheader("Genereret QR-kode:")
  st.image(byte_im, caption=f"Link: {default_url}", use_container_width=True)

  st.download_button(
      label="📥 Download QR-kode",
      data=byte_im,
      file_name="vand_quiz_qrcode.png",
      mime="image/png",
  )

st.markdown("---")
st.markdown("Lavet med ❤️ af dig i Streamlit & Python.")
