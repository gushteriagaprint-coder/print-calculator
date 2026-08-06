import streamlit as st

# Пълна база данни с формати
DATA = {
    "ДРУГ РАЗМЕР": [],
    "70x100": ["50x35", "35x25", "25x23.3", "25x17.5", "50x23", "35x33", "33x23", "50x25", "40x30", "30x20", "23x17.5", "35x20", "33x17.5", "45x25"],
    "64x90": ["32x30", "45x32", "45x21.3", "22.5x21", "32x22.5"],
    "50x70": ["50x35*", "35x25*", "25x23.3*", "25x17.5*", "50x23*"],
    "60x90": ["45x30", "45x20", "30x20-", "30x30"],
    "Himiya": ["30.5x21.5", "43x30.5"],
    "64x94": ["47x32", "31x21", "32x21"],
    "64x88": ["44x32", "44x21", "29x21", "32x29", "32x22"],
    "плаки": ["487x330"],
    "60x84": ["42x30", "30x28"],
    "61x86": ["43x30.5", "30.5x28.6", "30.5x21.5"],
    "43x61": ["43x30.5*", "30.5x21.5*"]
}

NAMED_SIZES = {"himiya": "43x61", "плаки": "48.7x33"}

st.title("🖨️ Печатен Калкулатор")

# Форма за въвеждане на данни
full_choice = st.selectbox("1. Избор на хартия:", list(DATA.keys()))

if full_choice == "ДРУГ РАЗМЕР":
    col1, col2 = st.columns(2)
    with col1:
        custom_w = st.text_input("Ширина (см)", "70")
    with col2:
        custom_h = st.text_input("Височина (см)", "100")
    print_options = ["Цял лист (ръчен)"]
else:
    print_options = [f"Цял лист ({full_choice})"] + DATA[full_choice]

print_choice = st.selectbox("2. Формат за пресмятане:", print_options)

col_w, col_h = st.columns(2)
with col_w:
    pw_str = st.text_input("3. Изделие Ш (мм):", "100")
with col_h:
    ph_str = st.text_input("4. Изделие В (мм):", "150")

turn_over = st.selectbox("5. С обръщане?", ["Не", "Да"]) == "Да"
useful_grip = st.selectbox("6. Полезен грайфер? (Офсет)", ["Не", "Да"]) == "Да"

if st.button("ИЗЧИСЛИ", type="primary"):
    try:
        is_formatting = "Цял лист" in print_choice
        
        def clean_val(txt):
            for char in ['*', '-', '(', ')']: txt = txt.replace(char, "")
            lookup = txt.lower().replace("цял лист", "").strip()
            if lookup in NAMED_SIZES: return NAMED_SIZES[lookup]
            return txt.lower().replace('х', 'x').replace(' ', '').replace(',', '.')

        if full_choice == "ДРУГ РАЗМЕР":
            psw_mm = float(custom_w.replace(',', '.')) * 10
            psh_mm = float(custom_h.replace(',', '.')) * 10
        else:
            fmt = clean_val(full_choice if is_formatting else print_choice)
            psw, psh = map(float, fmt.split('x'))
            psw_mm, psh_mm = (487, 330) if "плаки" in full_choice.lower() else (psw * 10, psh * 10)
        
        pw, ph = float(pw_str.replace(',', '.')), float(ph_str.replace(',', '.'))
        
        # Логика за работно поле
        if "плаки" in full_choice.lower():
            grip_mm = 10 
        elif is_formatting:
            grip_mm = 0
        else:
            grip_mm = 3 if useful_grip else 10
            
        lim_w = psw_mm - (18 if "плаки" in full_choice.lower() else (5 if not is_formatting else 0))
        lim_h = psh_mm - (20 if "плаки" in full_choice.lower() else ((grip_mm + 3) if not is_formatting else 0))

        def get_layout(SW, SH, IW, IH):
            c, r = int((SW + 0.1) // IW), int((SH + 0.1) // IH)
            total = c * r
            rw, rh = SW - (c * IW), SH - (r * IH)
            tR = total + (int((rw + 0.1) // IH) * int((SH + 0.1) // IW))
            tB = total + (int((SW + 0.1) // IH) * int((rh + 0.1) // IW))
            return (tR, c, r, IW, IH, int((rw + 0.1) // IH), int((SH + 0.1) // IW), "right") if tR >= tB else \
                   (tB, c, r, IW, IH, int((SW + 0.1) // IH), int((rh + 0.1) // IW), "bottom")

        if turn_over and not is_formatting:
            half_w = lim_w / 2
            res1, res2 = get_layout(half_w, lim_h, pw, ph), get_layout(half_w, lim_h, ph, pw)
            best = list(res1 if res1[0] >= res2[0] else res2)
            best[0] = int(best[0] * 2)
        else:
            res1, res2 = get_layout(lim_w, lim_h, pw, ph), get_layout(lim_w, lim_h, ph, pw)
            best = res1 if res1[0] >= res2[0] else res2

        st.success(f"Брой в листа: {int(best[0])}")
        area_pct = (int(best[0]) * pw * ph) / (psw_mm * psh_mm) * 100
        st.info(f"Използваема площ: {area_pct:.1f}%")
        
    except Exception as e:
        st.error(f"Невалидни данни или грешка при изчислението: {e}")