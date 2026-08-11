import streamlit as st
import matplotlib.patches as patches
import matplotlib.pyplot as plt

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

def draw_matplotlib_scheme(psw, psh, rects, is_formatting, is_turn_over, grip, sheet_type):
    fig, ax = plt.subplots(figsize=(6, 6))
    ax.set_xlim(0, psw)
    ax.set_ylim(0, psh)
    ax.set_aspect('equal')
    
    sheet_rect = patches.Rectangle((0, 0), psw, psh, linewidth=1, edgecolor='black', facecolor='#f0f0f0')
    ax.add_patch(sheet_rect)
    
    if not is_formatting:
        if "плаки" in sheet_type.lower():
            mx, my = 9, 10
            limit_rect = patches.Rectangle((mx, my), psw - 18, psh - 20, linewidth=1, edgecolor='red', linestyle='--', facecolor='none')
        else:
            mx, my = 2.5, 3
            limit_rect = patches.Rectangle((mx, my), psw - 5, psh - grip, linewidth=1, edgecolor='red', linestyle='--', facecolor='none')
        ax.add_patch(limit_rect)
    else:
        mx, my = 0, 0

    if is_turn_over:
        ax.axvline(x=psw/2, color='red', linestyle='--')

    for (rx, ry, rw, rh) in rects:
        x1 = mx + rx
        y1 = my + ry
        fill_color = "#e1f5fe" if rw < rh else "#c8e6c9"
        border_color = "blue" if rw < rh else "#2e7d32"
        rect = patches.Rectangle((x1, y1), rw, rh, linewidth=1, edgecolor=border_color, facecolor=fill_color)
        ax.add_patch(rect)

    ax.invert_yaxis()
    plt.axis('off')
    st.pyplot(fig)

if st.button("ИЗЧИСЛИ И ПОКАЖИ СХЕМА", type="primary"):
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
        
        if "плаки" in full_choice.lower():
            lim_w = psw_mm - 18 
            lim_h = psh_mm - 20
            grip_mm = 10 
        elif is_formatting:
            lim_w, lim_h = psw_mm, psh_mm
            grip_mm = 0
        else:
            grip_mm = 3 if useful_grip else 10
            lim_w = psw_mm - 5 
            lim_h = psh_mm - (grip_mm + 3)

        def solve_guillotine(SW, SH, IW, IH):
            memo = {}
            def helper(w, h):
                if w < min(IW, IH) or h < min(IW, IH):
                    return 0, []
                key = (round(w, 1), round(h, 1))
                if key in memo:
                    return memo[key]

                best_cnt = 0
                best_rects = []

                if w >= IW and h >= IH:
                    best_cnt = 1
                    best_rects = [(0, 0, IW, IH)]

                if w >= IH and h >= IW:
                    if 1 > best_cnt:
                        best_cnt = 1
                        best_rects = [(0, 0, IH, IW)]

                cut_x = set()
                x = IW
                while x < w: cut_x.add(x); x += IW
                x = IH
                while x < w: cut_x.add(x); x += IH

                for cx in cut_x:
                    c1, r1 = helper(cx, h)
                    c2, r2 = helper(w - cx, h)
                    if c1 + c2 > best_cnt:
                        best_cnt = c1 + c2
                        shifted_r2 = [(rx + cx, ry, rw, rh) for (rx, ry, rw, rh) in r2]
                        best_rects = r1 + shifted_r2

                cut_y = set()
                y = IH
                while y < h: cut_y.add(y); y += IH
                y = IW
                while y < h: cut_y.add(y); y += IW

                for cy in cut_y:
                    c1, r1 = helper(w, cy)
                    c2, r2 = helper(w, h - cy)
                    if c1 + c2 > best_cnt:
                        best_cnt = c1 + c2
                        shifted_r2 = [(rx, ry + cy, rw, rh) for (rx, ry, rw, rh) in r2]
                        best_rects = r1 + shifted_r2

                memo[key] = (best_cnt, best_rects)
                return memo[key]

            return helper(SW, SH)

        if turn_over and not is_formatting:
            half_w = lim_w / 2
            cnt1, rects1 = solve_guillotine(half_w, lim_h, pw, ph)
            rects2 = [(rx + half_w, ry, rw, rh) for (rx, ry, rw, rh) in rects1]
            best_cnt = cnt1 * 2
            best_rects = rects1 + rects2
        else:
            best_cnt, best_rects = solve_guillotine(lim_w, lim_h, pw, ph)

        st.success(f"Брой в листа: {int(best_cnt)}")
        area_pct = (best_cnt * pw * ph) / (psw_mm * psh_mm) * 100
        st.info(f"Използваема площ: {area_pct:.1f}%")
        
        st.subheader("Визуализация на монтажа:")
        draw_matplotlib_scheme(psw_mm, psh_mm, best_rects, is_formatting, (turn_over and not is_formatting), grip_mm, full_choice)
        
    except Exception as e:
        st.error(f"Невалидни данни или грешка при изчислението: {e}")
