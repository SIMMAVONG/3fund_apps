# python -m streamlit run app.py
import io
import pandas as pd
import streamlit as st
import db

st.set_page_config(page_title="ລະບົບບັນຊີກອງທຶນ", page_icon="💰", layout="wide")
db.init()
fmt = lambda v: f"{v:,.0f}"

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+Lao:wght@400;600;700&display=swap');
html, body, .stApp, p, label, h1, h2, h3, h4, input, textarea, button,
[data-testid="stMetricLabel"], [data-testid="stMetricValue"] {font-family:'Noto Sans Lao',sans-serif;}
#MainMenu, footer {visibility:hidden;}
.block-container {padding-top:2rem; max-width:1400px;}
[data-testid="stMetric"] {background:#fff; border:1px solid #e6e9ef; border-radius:14px;
  padding:14px 18px; box-shadow:0 1px 3px rgba(16,24,40,.06);}
[data-testid="stMetricValue"] {font-weight:700; color:#0b3d91;}
.hero {background:linear-gradient(120deg,#0b3d91,#1f6feb); color:#fff; border-radius:16px;
  padding:22px 28px; margin-bottom:18px;}
.hero h1 {color:#fff; margin:0; font-size:1.7rem;} .hero p {margin:4px 0 0; opacity:.85;}
.badge {display:inline-block; padding:2px 10px; border-radius:999px; font-size:.78rem;
  font-weight:600; background:#e8f0fe; color:#0b3d91;}
.badge.admin {background:#fde8e8; color:#a31515;}
div[data-testid="stForm"] {background:#fff; border-radius:14px; border:1px solid #e6e9ef;}
.stButton>button, .stDownloadButton>button {border-radius:10px; font-weight:600;}
</style>""", unsafe_allow_html=True)


def hero(title: str, sub: str = ""):
    st.markdown(f'<div class="hero"><h1>{title}</h1><p>{sub}</p></div>', unsafe_allow_html=True)


# =====================  ໜ້າ ເຂົ້າສູ່ລະບົບ / ລົງທະບຽນ  =====================
def auth_page():
    hero("💰 ລະບົບບັນຊີເກັບເງິນກອງທຶນ", "ກະລຸນາເຂົ້າສູ່ລະບົບເພື່ອໃຊ້ງານ")
    _, mid, _ = st.columns([1, 1.3, 1])
    with mid:
        if db.user_count() == 0:
            st.info("🔧 ການຕັ້ງຄ່າຄັ້ງທຳອິດ: ບັນຊີທີ່ລົງທະບຽນຄົນທຳອິດຈະເປັນ **ຜູ້ຄຸມລະບົບ (Admin)**")
            with st.form("first_admin"):
                u = st.text_input("ຊື່ຜູ້ໃຊ້ (a-z, 0-9)")
                n = st.text_input("ຊື່ ແລະ ນາມສະກຸນ")
                p1 = st.text_input("ລະຫັດຜ່ານ (ຢ່າງໜ້ອຍ 8 ຕົວ)", type="password")
                p2 = st.text_input("ຢືນຢັນລະຫັດຜ່ານ", type="password")
                if st.form_submit_button("ສ້າງບັນຊີ Admin", type="primary"):
                    if p1 != p2:
                        st.error("ລະຫັດຜ່ານບໍ່ກົງກັນ")
                    else:
                        ok, msg = db.register(u, n, p1)
                        (st.success if ok else st.error)(msg)
                        if ok:
                            st.rerun()
            return
        t_in, t_reg = st.tabs(["🔐 ເຂົ້າສູ່ລະບົບ", "📝 ລົງທະບຽນ"])
        with t_in:
            with st.form("login"):
                u = st.text_input("ຊື່ຜູ້ໃຊ້")
                p = st.text_input("ລະຫັດຜ່ານ", type="password")
                if st.form_submit_button("ເຂົ້າສູ່ລະບົບ", type="primary", width="stretch"):
                    ok, msg, user = db.login(u, p)
                    if ok:
                        st.session_state["user"] = user
                        st.rerun()
                    else:
                        st.error(msg)
        with t_reg:
            with st.form("register"):
                u = st.text_input("ຊື່ຜູ້ໃຊ້ (a-z, 0-9, _ .)", key="ru")
                n = st.text_input("ຊື່ ແລະ ນາມສະກຸນ", key="rn")
                p1 = st.text_input("ລະຫັດຜ່ານ (ຢ່າງໜ້ອຍ 8 ຕົວ)", type="password", key="rp1")
                p2 = st.text_input("ຢືນຢັນລະຫັດຜ່ານ", type="password", key="rp2")
                if st.form_submit_button("ລົງທະບຽນ", width="stretch"):
                    if p1 != p2:
                        st.error("ລະຫັດຜ່ານບໍ່ກົງກັນ")
                    else:
                        ok, msg = db.register(u, n, p1)
                        (st.success if ok else st.error)(msg)
            st.caption("ຫຼັງລົງທະບຽນ ຕ້ອງລໍຖ້າ Admin ອະນຸມັດກ່ອນຈຶ່ງເຂົ້າໃຊ້ໄດ້")


user = st.session_state.get("user")
if user:  # ກວດສິດຄືນທຸກຄັ້ງ (ຖ້າ admin ປິດບັນຊີ ຫຼື ປ່ຽນສິດ ຈະມີຜົນທັນທີ)
    fresh = db.get_user(user["id"])
    if not fresh or fresh["status"] != "active":
        st.session_state.pop("user", None)
        user = None
    else:
        user = st.session_state["user"] = {**user, **fresh}
if not user:
    auth_page()
    st.stop()
IS_ADMIN = user["role"] == "admin"
ps = db.periods()


def _isnum(v):
    return v is not None and v == v  # ບໍ່ແມ່ນ None/NaN


MY_RANGE = (None if IS_ADMIN or not (_isnum(user.get("range_from")) and _isnum(user.get("range_to")))
            else (int(user["range_from"]), int(user["range_to"])))
_va = user.get("view_all")
VIEW_ALL = IS_ADMIN or _va is None or bool(_va)


def in_my_range(df):
    """ສຳລັບໜ້າປ້ອນຂໍ້ມູນ: ສະເພາະເລກທີທີ່ຮັບຜິດຊອບ (Admin ເຫັນທັງໝົດ)"""
    if IS_ADMIN:
        return df
    if MY_RANGE is None:
        return df.iloc[0:0]
    return df[(df.book_no >= MY_RANGE[0]) & (df.book_no <= MY_RANGE[1])]


def scope_df(df):
    """ສຳລັບໜ້າເບິ່ງຂໍ້ມູນ: ຖ້າ Admin ບໍ່ອະນຸຍາດໃຫ້ເບິ່ງທັງໝົດ ຈະເຫັນສະເພາະຂອບເຂດຂອງຕົນ"""
    return df if VIEW_ALL else in_my_range(df)


def range_text():
    return f"ເລກທີ {MY_RANGE[0]}–{MY_RANGE[1]}" if MY_RANGE else "ຍັງບໍ່ໄດ້ຮັບມອບໝາຍ"


def cur_period():
    return st.session_state.get("period") or (ps[-1] if ps else None)


# =====================  ໜ້າສຳລັບທຸກຄົນ  =====================
def page_dashboard():
    hero("📊 ພາບລວມ", f"ເດືອນ {cur_period() or '-'}")
    p = cur_period()
    if not p:
        st.warning("ຍັງບໍ່ມີຂໍ້ມູນ" + (" — ໄປໜ້າ 'ນຳເຂົ້າ / ສຳຮອງ' ເພື່ອນຳເຂົ້າ Excel" if IS_ADMIN else ""))
        return
    df = db.add_calc(scope_df(db.load_month(p)))
    if not IS_ADMIN and not VIEW_ALL:
        st.caption(f"ສະແດງສະເພາະຂອບເຂດຂອງເຈົ້າ: {range_text()}")
    s = db.summary(df)
    a, b, c, d = st.columns(4)
    a.metric("ຈຳນວນລູກຄ້າ", fmt(len(df)))
    b.metric("ເງິນຝາກເດືອນນີ້", fmt(s["dep"]))
    c.metric("ເງິນຝາກຍ້າຍໄປເດືອນໜ້າ", fmt(s["dep_next"]))
    d.metric("ເງິນກູ້ຄ້າງໄປເດືອນໜ້າ", fmt(s["loan_next"]))
    a, b, c, d = st.columns(4)
    a.metric("ຖອນເດືອນນີ້", fmt(s["wd"]))
    b.metric("ລາຍຮັບທັງໝົດ", fmt(s["income"]))
    c.metric("ລາຍຈ່າຍທັງໝົດ", fmt(s["expense"]))
    d.metric("ຍອດເຫຼືອ", fmt(s["balance"]))
    tr = db.trend(None if VIEW_ALL else MY_RANGE)
    if not tr.empty:
        st.subheader("ແນວໂນ້ມລາຍເດືອນ")
        st.line_chart(tr.rename(columns={"dep_next": "ເງິນຝາກທັງໝົດ", "loan_next": "ເງິນກູ້ຄ້າງ"}))


def page_search():
    hero("🔎 ຄົ້ນຫາລູກຄ້າ", "ເບິ່ງຂໍ້ມູນເທົ່ານັ້ນ — ບໍ່ສາມາດແກ້ໄຂ ຫຼື ລຶບໄດ້")
    p = cur_period()
    if not p:
        return
    df = db.add_calc(scope_df(db.load_month(p)))
    q = st.text_input("ຄົ້ນຫາດ້ວຍຊື່ ຫຼື ເລກທີປຶ້ມ", placeholder="ພິມຊື່ ຫຼື ເລກທີ...")
    if q:
        df = df[df.name.fillna("").str.contains(q) | df.book_no.astype(str).eq(q.strip())]
    show = df[["book_no", "name", "tx_date", "old_dep", "dep", "wd", "dep_next",
               "loan_total", "interest_due", "accrued_prev", "interest_actual",
               "repay", "new_loan", "accrued_next", "loan_next",
               "app_fee", "booklet_fee"]]
    money = lambda t: st.column_config.NumberColumn(t, format="%,.0f")
    st.dataframe(show, hide_index=True, width="stretch", height=380, column_config={
        "book_no": st.column_config.NumberColumn("ເລກທີປຶ້ມ", pinned=True),
        "name": st.column_config.TextColumn("ຊື່ ແລະ ນາມສະກຸນ", pinned=True),
        "tx_date": "ວັນທີ",
        "old_dep": money("ຝາກເກົ່າ"),
        "dep": money("ຝາກເດືອນນີ້"),
        "wd": money("ຖອນ"),
        "dep_next": money("ຍ້າຍໄປເດືອນໜ້າ"),
        "loan_total": money("ເງິນກູ້"),
        "interest_due": money("ດອກເບ້ຍເດືອນນີ້"),
        "accrued_prev": money("ດອກຄ້າງເດືອນກ່ອນ"),
        "interest_actual": money("ດອກທີ່ຈ່າຍແລ້ວ"),
        "repay": money("ສົ່ງຄືນເງິນກູ້"),
        "new_loan": money("ກູ້ໃໝ່"),
        "accrued_next": money("ດອກຄ້າງຈ່າຍລວມ"),
        "loan_next": money("ກູ້ຄ້າງໄປເດືອນໜ້າ"),
        "app_fee": money("ໃບຄຳຮ້ອງ"),
        "booklet_fee": money("ຄ່າປຶ້ມນ້ອຍ")})
    st.caption(f"ພົບ {len(df)} ລາຍການ")
    if len(df):
        st.subheader("ປະຫວັດລູກຄ້າ")
        opts = {f"{int(r.book_no):03d} · {r['name']}": int(r.book_no) for _, r in df.iterrows()}
        pick = st.selectbox("ເລືອກລູກຄ້າ", list(opts))
        h = db.member_history(opts[pick])
        if len(h):
            hist_cols = {
                "period": "ເດືອນ", "old_dep": "ຝາກເກົ່າ", "dep": "ຝາກ", "wd": "ຖອນ",
                "dep_next": "ຍ້າຍໄປໜ້າ", "loan_total": "ເງິນກູ້", "new_loan": "ກູ້ໃໝ່",
                "repay": "ສົ່ງຄືນ", "loan_next": "ກູ້ຄ້າງ",
                "interest_due": "ດອກເບ້ຍເດືອນນີ້", "accrued_prev": "ດອກຄ້າງເດືອນກ່ອນ",
                "interest_actual": "ດອກທີ່ຈ່າຍແລ້ວ", "accrued_next": "ດອກເບ້ຍຄ້າງຈ່າຍລວມ"}
            hv = h[list(hist_cols)]
            st.dataframe(hv, hide_index=True, width="stretch",
                         column_config={
                             "period": st.column_config.TextColumn("ເດືອນ", pinned=True),
                             **{k: money(v) for k, v in hist_cols.items() if k != "period"}})
            buf = io.BytesIO()
            hv.rename(columns=hist_cols).to_excel(buf, index=False)
            st.download_button("⬇️ ດາວໂຫຼດປະຫວັດລູກຄ້ານີ້ (Excel)", buf.getvalue(),
                               f"history_{opts[pick]:03d}.xlsx")
            st.line_chart(h.set_index("period")[["dep_next"]].rename(
                columns={"dep_next": "ເງິນຝາກສະສົມ"}))


def page_entry():
    p = ps[-1] if (ps and not IS_ADMIN) else cur_period()
    hero("✍️ ປ້ອນຂໍ້ມູນ", f"ເດືອນ {p or '-'} · ບັນທຶກເພີ່ມໄດ້ເທົ່ານັ້ນ, ການແກ້ໄຂ/ລຶບເປັນສິດຂອງ Admin")
    if not p:
        return
    if db.period_locked(p):
        st.error("🔒 ເດືອນນີ້ຖືກລັອກແລ້ວ — ປ້ອນຂໍ້ມູນບໍ່ໄດ້")
        return
    cur = in_my_range(db.load_month(p))
    if not IS_ADMIN:
        if MY_RANGE is None:
            st.warning("ເຈົ້າຍັງບໍ່ໄດ້ຮັບມອບໝາຍຂອບເຂດເລກທີປຶ້ມ — ກະລຸນາຕິດຕໍ່ Admin")
            return
        done = int(cur.tx_date.notna().sum())
        st.info(f"📌 ໜ້າທີ່ຂອງເຈົ້າ: **{range_text()}** · ມີລາຍການເດືອນນີ້ແລ້ວ {done}/{len(cur)} ຄົນ")
    opts = {f"{int(r.book_no):03d} · {r['name']}": int(r.book_no) for _, r in cur.iterrows()}
    pick = st.selectbox("ເລືອກລູກຄ້າ (ພິມເພື່ອຄົ້ນຫາ)", list(opts), index=None,
                        placeholder="ພິມຊື່ ຫຼື ເລກທີປຶ້ມ...")
    if st.session_state.get("flash"):
        st.success(st.session_state.pop("flash"))
    if not pick:
        return
    bn = opts[pick]
    row = db.add_calc(cur[cur.book_no == bn]).iloc[0]
    a, b, c, d, e = st.columns(5)
    a.metric("ຍອດເງິນຝາກປະຈຸບັນ", fmt(row.dep_next))
    b.metric("ເງິນກູ້ຄ້າງ", fmt(row.loan_next))
    c.metric("ດອກຄ້າງເດືອນກ່ອນ", fmt(row.accrued_prev))
    d.metric("ດອກເບ້ຍເດືອນນີ້", fmt(row.interest_due))
    e.metric("ດອກເບ້ຍຄ້າງຈ່າຍລວມ", fmt(row.accrued_next),
             help="ດອກຄ້າງເດືອນກ່ອນ + ດອກເບ້ຍເດືອນນີ້ − ດອກທີ່ຈ່າຍແລ້ວ")
    with st.form("entry", clear_on_submit=True):
        kind = st.radio("ປະເພດລາຍການ", list(db.ENTRY_TYPES), horizontal=True)
        amt = st.number_input("ຈຳນວນເງິນ (ກີບ)", min_value=0, step=1000, format="%d")
        note = st.text_input("ໝາຍເຫດ (ບໍ່ບັງຄັບ)")
        sure = st.checkbox("ຂ້ອຍກວດສອບແລ້ວວ່າຂໍ້ມູນຖືກຕ້ອງ")
        if st.form_submit_button("💾 ບັນທຶກ", type="primary"):
            if not sure:
                st.warning("ກະລຸນາຕິກຢືນຢັນກ່ອນບັນທຶກ")
            else:
                ok, msg = db.add_entry(p, bn, db.ENTRY_TYPES[kind], float(amt),
                                       user["username"], IS_ADMIN, note)
                if ok:
                    st.session_state["flash"] = msg
                    st.rerun()
                st.error(msg)
    log = db.audit_df(300)
    mine = log[(log.username == user["username"]) & (log.action == "entry")].head(8)
    if len(mine):
        st.subheader("ລາຍການທີ່ເຈົ້າບັນທຶກຫຼ້າສຸດ")
        st.dataframe(mine[["ts", "detail"]], hide_index=True, width="stretch",
                     column_config={"ts": "ເວລາ", "detail": "ລາຍລະອຽດ"})


def page_account():
    hero("👤 ບັນຊີຂອງຂ້ອຍ", f"{user['full_name']} · @{user['username']}")
    if not IS_ADMIN:
        st.info(f"ຂອບເຂດທີ່ຮັບຜິດຊອບ: **{range_text()}**")
    with st.form("chpw"):
        o = st.text_input("ລະຫັດຜ່ານເກົ່າ", type="password")
        n1 = st.text_input("ລະຫັດຜ່ານໃໝ່ (ຢ່າງໜ້ອຍ 8 ຕົວ)", type="password")
        n2 = st.text_input("ຢືນຢັນລະຫັດຜ່ານໃໝ່", type="password")
        if st.form_submit_button("ປ່ຽນລະຫັດຜ່ານ", type="primary"):
            if n1 != n2:
                st.error("ລະຫັດຜ່ານໃໝ່ບໍ່ກົງກັນ")
            else:
                ok, msg = db.change_password(user["id"], o, n1)
                (st.success if ok else st.error)(msg)


# =====================  ໜ້າສະເພາະ Admin  =====================
def page_ledger():
    hero("📒 ແກ້ໄຂບັນຊີປະຈຳເດືອນ", "Admin ເທົ່ານັ້ນ")
    p = cur_period()
    if not p:
        return
    locked = db.period_locked(p)
    c1, c2 = st.columns([3, 1])
    c1.subheader(f"ເດືອນ {p}" + ("  🔒" if locked else ""))
    if c2.button("🔓 ປົດລັອກ" if locked else "🔒 ລັອກເດືອນນີ້", width="stretch"):
        db.set_lock(p, not locked, user["username"]); st.rerun()
    raw = db.load_month(p)
    q = st.text_input("🔎 ຄົ້ນຫາຊື່ ຫຼື ເລກທີປຶ້ມ", key="lq")
    view = raw
    if q:
        view = raw[raw.name.fillna("").str.contains(q) | raw.book_no.astype(str).eq(q.strip())]
    rate = db.get_rate()
    calc = db.add_calc(view, rate)
    labels = {"book_no": "ເລກທີປຶ້ມ", "name": "ຊື່ ແລະ ນາມສະກຸນ", "tx_date": "ວັນທີ",
              **db.INPUT_COLS, **db.CALC_COLS, "closed": "ປິດບັນຊີ"}
    order = ["book_no", "name", "tx_date", "old_dep", "dep", "wd", "dep_next", "loan_total",
             "interest_due", "accrued_prev", "interest_actual", "repay", "new_loan",
             "accrued_next", "loan_next", "app_fee", "booklet_fee", "closed"]
    calc["tx_date"] = pd.to_datetime(calc["tx_date"], errors="coerce")
    cfg = {k: st.column_config.NumberColumn(labels[k], format="%,.0f")
           for k in [*db.INPUT_COLS, *db.CALC_COLS]}
    cfg.update({"book_no": st.column_config.NumberColumn("ເລກທີປຶ້ມ"),
                "name": st.column_config.TextColumn("ຊື່ ແລະ ນາມສະກຸນ"),
                "tx_date": st.column_config.DateColumn("ວັນທີ"),
                "closed": st.column_config.CheckboxColumn("ປິດບັນຊີ")})
    edited = st.data_editor(calc[order], hide_index=True, width="stretch", height=520,
                            disabled=["book_no", *db.CALC_COLS], column_config=cfg)
    b1, b2, b3 = st.columns(3)
    if b1.button("💾 ບັນທຶກການແກ້ໄຂ", type="primary"):
        db.save_month(p, edited)
        db.audit(user["username"], "admin_save_month", f"{p} ({len(edited)} ແຖວ)")
        st.success("ບັນທຶກແລ້ວ"); st.rerun()
    if b2.button("➕ ເປີດເດືອນໜ້າ (ຍົກຍອດອັດຕະໂນມັດ)"):
        n = db.rollover(p)
        db.audit(user["username"], "rollover", f"{p} -> {n}")
        st.session_state["period"] = n; st.rerun()
    buf = io.BytesIO()
    db.add_calc(db.load_month(p), rate).rename(columns=labels).to_excel(buf, index=False)
    b3.download_button("⬇️ ດາວໂຫຼດ Excel ເດືອນນີ້", buf.getvalue(), f"fund_{p}.xlsx")


def page_summary():
    hero("🧮 ສະຫຼຸບບັນຊີ", f"ເດືອນ {cur_period() or '-'}")
    p = cur_period()
    if not p:
        return
    full = db.add_calc(db.load_month(p))
    with db.conn() as c:
        ex = pd.read_sql_query("SELECT id,label,amount FROM extras WHERE period=?", c, params=(p,))
    s = db.summary(full, ex.amount.sum())
    a, b, c_ = st.columns(3)
    a.metric("ລາຍຮັບທັງໝົດ", fmt(s["income"])); b.metric("ລາຍຈ່າຍທັງໝົດ", fmt(s["expense"]))
    c_.metric("ຍອດເຫຼືອ", fmt(s["balance"]))
    st.caption("ລາຍຮັບ = ເງິນຝາກ + ດອກເບ້ຍຕົວຈິງ + ສົ່ງຄືນເງິນກູ້ + ໃບຄຳຮ້ອງ + ຄ່າປຶ້ມນ້ອຍ | ລາຍຈ່າຍ = ຖອນ + ກູ້ໃໝ່")
    st.markdown("**ລາຍການເງິນກູ້ຄ້າງເພີ່ມເຕີມ**")
    new_ex = st.data_editor(ex, num_rows="dynamic", hide_index=True, column_config={"id": None}, key="extras")
    if st.button("ບັນທຶກລາຍການເພີ່ມເຕີມ"):
        with db.conn() as c:
            c.execute("DELETE FROM extras WHERE period=?", (p,))
            for _, r in new_ex.dropna(subset=["label"]).iterrows():
                c.execute("INSERT INTO extras(period,label,amount) VALUES(?,?,?)",
                          (p, r.label, float(r.amount or 0)))
        db.audit(user["username"], "extras", p); st.rerun()
    st.metric("ລວມເງິນກູ້ຢືມທັງໝົດ (ລວມລາຍການເພີ່ມ)", fmt(s["loan_with_extra"]))


def page_members():
    hero("👥 ສະມາຊິກ / ລູກຄ້າ", "ເພີ່ມລູກຄ້າໃໝ່")
    st.dataframe(db.members().rename(columns={"book_no": "ເລກທີປຶ້ມ", "name": "ຊື່", "active": "ໃຊ້ງານ"}),
                 hide_index=True, width="stretch")
    with st.form("addm"):
        n = st.number_input("ເລກທີປຶ້ມໃໝ່", 1, 9999, step=1)
        nm = st.text_input("ຊື່ ແລະ ນາມສະກຸນ")
        if st.form_submit_button("ເພີ່ມສະມາຊິກ", type="primary") and nm:
            try:
                db.add_member(int(n), nm, ps[-1] if ps else None)
                db.audit(user["username"], "add_member", f"#{int(n)} {nm}")
                st.success("ເພີ່ມແລ້ວ"); st.rerun()
            except Exception as e:
                st.error(f"ເພີ່ມບໍ່ໄດ້ (ເລກທີປຶ້ມຊ້ຳ?): {e}")


def page_dividend():
    hero("🎁 ປັນຜົນທ້າຍປີ", "Admin ເທົ່ານັ້ນ")
    year = st.number_input("ປີ", 2020, 2100, 2025, step=1)
    dv = db.load_dividend(int(year))
    if dv.empty:
        st.info("ຍັງບໍ່ມີຂໍ້ມູນປັນຜົນປີນີ້")
        if st.button("ສ້າງແຖວຈາກລາຍຊື່"):
            m = db.members()
            db.save_dividend(int(year), pd.DataFrame({
                "book_no": m.book_no, "tx_date": None, "capital": 0.0, "div_interest": 0.0,
                "wd_interest": 0.0, "wd_capital": 0.0, "receiver": None}))
            st.rerun()
        return
    mo = lambda t: st.column_config.NumberColumn(t, format="%,.0f")
    ed = st.data_editor(dv, hide_index=True, width="stretch", height=520,
                        disabled=["book_no", "name", "total", "wd_total", "carry_year"],
                        column_config={"book_no": "ເລກທີ", "name": "ຊື່", "tx_date": "ວັນທີ",
                                       "capital": mo("ຕົ້ນທຶນທັງໝົດ"), "div_interest": mo("ດອກເບ້ຍປັນຜົນ"),
                                       "total": mo("ລວມເງິນທັງໝົດ"), "wd_interest": mo("ຖອນດອກເບ້ຍ"),
                                       "wd_capital": mo("ຖອນຕົ້ນທຶນ"), "wd_total": mo("ລວມເງິນຖອນ"),
                                       "carry_year": mo("ຍອດຍົກໄປປີໜ້າ"), "receiver": "ຜູ້ຮັບເງິນ"})
    if st.button("💾 ບັນທຶກປັນຜົນ", type="primary"):
        db.save_dividend(int(year), ed)
        db.audit(user["username"], "save_dividend", str(int(year))); st.rerun()
    st.metric("ລວມຍອດຍົກໄປປີໜ້າ", fmt(db.load_dividend(int(year)).carry_year.sum()))


def page_users():
    hero("🛡️ ຈັດການຜູ້ໃຊ້", "ອະນຸມັດ, ປິດ/ເປີດ, ກຳນົດສິດ, ຣີເຊັດລະຫັດຜ່ານ")
    us = db.list_users()
    pend = us[us.status == "pending"]
    if len(pend):
        st.warning(f"⏳ ມີ {len(pend)} ຄົນລໍຖ້າອະນຸມັດ")
    gaps = db.unassigned_ids()
    if gaps:
        st.warning(f"⚠️ ເລກທີປຶ້ມທີ່ຍັງບໍ່ມີຜູ້ຮັບຜິດຊອບ: {db.compress_ranges(gaps)}")
    else:
        st.success("✅ ທຸກເລກທີປຶ້ມມີຜູ້ຮັບຜິດຊອບແລ້ວ")
    if st.session_state.get("flash_users"):
        st.success(st.session_state.pop("flash_users"))
    st.dataframe(us.rename(columns={"id": "ID", "username": "ຊື່ຜູ້ໃຊ້", "full_name": "ຊື່",
                                    "role": "ສິດ", "status": "ສະຖານະ", "created_at": "ສ້າງເມື່ອ",
                                    "last_login": "ເຂົ້າລ່າສຸດ", "range_from": "ແຕ່ເລກທີ",
                                    "range_to": "ຮອດເລກທີ", "view_all": "ເບິ່ງທັງໝົດ"}),
                 hide_index=True, width="stretch")
    opts = {f"{r.username} · {r.full_name} [{r.status}/{r.role}]": int(r.id) for _, r in us.iterrows()}
    pick = st.selectbox("ເລືອກຜູ້ໃຊ້", list(opts), index=None)
    if pick:
        uid = opts[pick]
        c1, c2, c3 = st.columns(3)
        if c1.button("✅ ອະນຸມັດ / ເປີດໃຊ້"):
            ok, m = db.update_user(uid, user["username"], status="active"); (st.success if ok else st.error)(m); st.rerun()
        if c2.button("⛔ ປິດການໃຊ້ງານ"):
            ok, m = db.update_user(uid, user["username"], status="disabled"); (st.success if ok else st.error)(m); st.rerun()
        role = c3.selectbox("ສິດ", ["user", "admin"], index=0 if "/user]" in pick else 1)
        if c3.button("ບັນທຶກສິດ"):
            ok, m = db.update_user(uid, user["username"], role=role); (st.success if ok else st.error)(m); st.rerun()
        urow = us[us.id == uid].iloc[0]
        if urow.role == "user":
            st.markdown("**ຂອບເຂດເລກທີປຶ້ມທີ່ຮັບຜິດຊອບ** (ປ້ອນຂໍ້ມູນໄດ້ສະເພາະຂອບເຂດນີ້)")
            with st.form("scope"):
                f1, f2 = st.columns(2)
                rf = f1.number_input("ແຕ່ເລກທີ", 1, 99999,
                                     int(urow.range_from) if _isnum(urow.range_from) else 1, step=1)
                rt = f2.number_input("ຮອດເລກທີ", 1, 99999,
                                     int(urow.range_to) if _isnum(urow.range_to) else 1, step=1)
                va = st.checkbox("ອະນຸຍາດໃຫ້ເບິ່ງຂໍ້ມູນລູກຄ້າທຸກຄົນ (ຖ້າບໍ່ຕິກ ຈະເຫັນສະເພາະຂອບເຂດຂອງຕົນ)",
                                 value=bool(urow.view_all) if _isnum(urow.view_all) else True)
                if st.form_submit_button("💾 ບັນທຶກຂອບເຂດ", type="primary"):
                    ok, m = db.set_user_scope(uid, int(rf), int(rt), va, user["username"])
                    if ok:
                        st.session_state["flash_users"] = m
                        st.rerun()
                    st.error(m)
        with st.form("resetpw", clear_on_submit=True):
            npw = st.text_input("ກຳນົດລະຫັດຜ່ານໃໝ່ໃຫ້ຜູ້ໃຊ້ (ຢ່າງໜ້ອຍ 8 ຕົວ)", type="password")
            if st.form_submit_button("ຣີເຊັດລະຫັດຜ່ານ"):
                ok, m = db.update_user(uid, user["username"], new_pw=npw); (st.success if ok else st.error)(m)


def page_audit():
    hero("🧾 ບັນທຶກການເຄື່ອນໄຫວ", "ທຸກການເຂົ້າລະບົບ, ປ້ອນ ແລະ ແກ້ໄຂຂໍ້ມູນ ຖືກບັນທຶກໄວ້")
    st.dataframe(db.audit_df(1000), hide_index=True, width="stretch", height=600,
                 column_config={"ts": "ເວລາ", "username": "ຜູ້ໃຊ້", "action": "ການກະທຳ", "detail": "ລາຍລະອຽດ"})


def page_system():
    hero("⚙️ ຕັ້ງຄ່າ / ນຳເຂົ້າ / ສຳຮອງ", "Admin ເທົ່ານັ້ນ")
    if st.session_state.get("import_msg"):
        _m, _notes = st.session_state.pop("import_msg")
        (st.success if _m.startswith("✅") else st.error)(_m)
        for _n in _notes:
            st.warning("⚠️ " + _n)
    rate = st.number_input("ອັດຕາດອກເບ້ຍເງິນກູ້ (%/ເດືອນ)", 0.0, 100.0, db.get_rate() * 100, 0.1)
    if st.button("ບັນທຶກອັດຕາ"):
        db.set_rate(rate / 100); db.audit(user["username"], "set_rate", str(rate)); st.success("ບັນທຶກແລ້ວ")
    st.divider()
    st.subheader("💾 ສຳຮອງຖານຂໍ້ມູນ")
    st.download_button("⬇️ ດາວໂຫຼດ fund.db (ເກັບໄວ້ບ່ອນປອດໄພ)", db.backup_bytes(), "fund_backup.db")
    st.divider()
    st.subheader("⬆️ ນຳເຂົ້າ Excel")
    up = st.file_uploader("ໄຟລ໌ .xlsx", type="xlsx")
    only = st.checkbox("ນຳເຂົ້າສະເພາະເດືອນຫຼ້າສຸດ")
    if up and st.button("ນຳເຂົ້າ"):
        try:
            with st.spinner("ກຳລັງນຳເຂົ້າ ກະລຸນາລໍຖ້າ..."):
                done = db.import_excel(up, only_latest=only)
            db.audit(user["username"], "import_excel", ", ".join(done))
            allm = [int(k) for k in db.members().book_no]
            notes = []
            for p in done:
                have = set(db.load_month(p).book_no)
                miss = [k for k in allm if k not in have]
                if miss:
                    notes.append(f"ເດືອນ {p}: ຂາດເລກທີ {db.compress_ranges(miss)}")
            if not done:
                st.session_state["import_msg"] = (
                    "❌ ບໍ່ພົບຊີດປະຈຳເດືອນທີ່ອ່ານໄດ້ໃນໄຟລ໌ (ກວດຊື່ຊີດ ແລະ ຫົວຄໍລຳ D1/H1)", [])
            else:
                st.session_state["import_msg"] = (
                    f"✅ ນຳເຂົ້າແລ້ວ {len(done)} ເດືອນ ({', '.join(done)}) · "
                    f"ລູກຄ້າທັງໝົດໃນລະບົບ {len(allm)} ຄົນ", notes)
            st.rerun()
        except Exception as e:
            st.error(f"ນຳເຂົ້າບໍ່ສຳເລັດ: {e}")
    st.divider()
    st.subheader("🔍 ກວດຍອດຍົກ")
    st.caption("ກວດວ່າ 'ເງິນເກົ່າ' ຂອງແຕ່ລະເດືອນ ກົງກັບ 'ຍອດຍົກ' ຂອງເດືອນກ່ອນ ບໍ່")
    if st.button("ກວດສອບ"):
        r = db.check_carry(); st.write(f"ພົບຜິດດ່ຽງ {len(r)} ລາຍການ")
        st.dataframe(r, hide_index=True, width="stretch")


# =====================  ເມນູ + ແຖບຂ້າງ  =====================
common = [st.Page(page_dashboard, title="ພາບລວມ", icon="📊", url_path="home", default=True),
          st.Page(page_search, title="ຄົ້ນຫາລູກຄ້າ", icon="🔎", url_path="search"),
          st.Page(page_entry, title="ປ້ອນຂໍ້ມູນ", icon="✍️", url_path="entry"),
          st.Page(page_account, title="ບັນຊີຂອງຂ້ອຍ", icon="👤", url_path="account")]
admin_pages = [st.Page(page_ledger, title="ແກ້ໄຂບັນຊີ", icon="📒", url_path="ledger"),
               st.Page(page_summary, title="ສະຫຼຸບບັນຊີ", icon="🧮", url_path="summary"),
               st.Page(page_members, title="ສະມາຊິກ", icon="👥", url_path="members"),
               st.Page(page_dividend, title="ປັນຜົນທ້າຍປີ", icon="🎁", url_path="dividend"),
               st.Page(page_users, title="ຈັດການຜູ້ໃຊ້", icon="🛡️", url_path="users"),
               st.Page(page_audit, title="ບັນທຶກການເຄື່ອນໄຫວ", icon="🧾", url_path="audit"),
               st.Page(page_system, title="ຕັ້ງຄ່າ / ສຳຮອງ", icon="⚙️", url_path="system")]
nav = st.navigation({"ການໃຊ້ງານ": common, "ຜູ້ຄຸມລະບົບ": admin_pages} if IS_ADMIN else common)

with st.sidebar:
    st.markdown(f"**{user['full_name']}**  \n"
                f"<span class='badge {'admin' if IS_ADMIN else ''}'>{'Admin' if IS_ADMIN else 'ຜູ້ໃຊ້'}</span>",
                unsafe_allow_html=True)
    if ps:
        st.selectbox("📅 ເລືອກເດືອນ", ps, index=len(ps) - 1, key="period")
    if st.button("🚪 ອອກຈາກລະບົບ", width="stretch"):
        db.audit(user["username"], "logout")
        st.session_state.clear(); st.rerun()
nav.run()