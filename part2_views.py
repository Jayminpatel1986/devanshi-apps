# -*- coding: utf-8 -*-
# =======================================================================================================================
# ⚠️ આવશ્યક એઆઈ ડાયરેક્ટિવ અને ડાયનામિક રૂલબુક ગવર્નન્સ (કાયમી અમર એઆઈ હેડર - માસ્ટર ૧૦ લોજિક અને મલ્ટી-સ્ટોર SaaS આવૃત્તિ)
# =======================================================================================================================
# [કડક ચેતવણી - Gemini, ChatGPT, Claude, Cursor અથવા અન્ય કોઈપણ AI મોડેલ અને ડેવલપર માટે બંધનકર્તા આદેશ]:
# ૧. આ હેડર 'અમર' (Immortal) છે. આ ફાઇલ part2_views.py છે (મૂળ રોયલ નેવી બ્લુ લેઆઉટ + ૧૨ શીટ્સ + F1 થી F8 + Accept? Yes/No).
# ૨. જૂના કોડનું એક પણ ફંક્શન, ડ્રોપડાઉન, ગાણિતિક સૂત્ર કે CRUD બટન કાઢવું સખત પ્રતિબંધિત છે.
# =======================================================================================================================

import datetime
import json
import sqlite3
import urllib.parse
from fastapi import Request
from fastapi.responses import HTMLResponse
import part1_core
from part1_core import (
    get_store_default_home, get_default_home_url,
    app, STORE_CFG, get_license_info, get_shop_feature_profile,
    get_current_bill_no, get_galla_balance, get_cumulative_unbanked_cash, get_active_db_file
)
import part2_b_counters
import part2_c_counters_extra
import part2_d_sheets

@app.get("/", response_class=HTMLResponse)
def root_view(
    request: Request = None,
    sheet: str = "", mode: str = "", msg: str = "", search_q: str = "",
    f4_sm_filter: str = "", u_tab: str = "customer", bb_view: str = "IN_STOCK",
    sel_cust: str = "", sel_sm_hist: str = "", sel_sm_due: str = "", sel_supp: str = "",
    sm_range: str = "TODAY", from_d: str = "", to_d: str = "", f2_bill_type: str = "", bill_type: str = "", prefill_imei: str = "", sm_staff: str = "ALL", snap_date: str = ""
):
    cookie_sid = ""
    if request and hasattr(request, "cookies"):
        cookie_sid = urllib.parse.unquote(request.cookies.get("devanshi_shop_id") or "").strip().upper()
    active_sid = (cookie_sid or STORE_CFG.get("shop_id", "DEVANSHI")).strip().upper()
    shop_prof_early = get_shop_feature_profile(active_sid)
    is_active, status_text, days_left = get_license_info(active_sid)
    store_title = shop_prof_early.get("store_name") or ("દેવાંશી મોબાઈલ" if active_sid == "DEVANSHI" else ("મનસ્વી ટેલિકોમ" if active_sid == "MANSHVI" else f"દુકાન {active_sid}"))
    if not is_active:
        upi_id = STORE_CFG.get("super_admin_upi", "pateljay17@okhdfcbank")
        admin_mob = STORE_CFG.get("super_admin_mobile", "9725721215")
        return HTMLResponse(f"""
        <!DOCTYPE html><html lang="gu"><head><meta charset="UTF-8"><meta name="viewport" id="erp_main_viewport" content="width=1366, initial-scale=0.28, minimum-scale=0.2, maximum-scale=3.0, user-scalable=yes"><link rel="manifest" href="/manifest.json"><title>સોફ્ટવેર લૉક - {store_title}</title></head>
        <body style="margin:0; padding:30px; font-family:'Segoe UI',sans-serif; background:#0f172a; color:white; display:flex; align-items:center; justify-content:center; min-height:90vh;">
            <div style="background:#1e293b; border:2px solid #ef4444; border-radius:12px; padding:28px; max-width:480px; text-align:center; box-shadow:0 20px 40px rgba(0,0,0,0.6);">
                <h1 style="color:#ef4444; margin:0 0 10px 0;">🔒 સોફ્ટવેર લૉક કરવામાં આવ્યું છે</h1>
                <h3 style="color:#fde047; margin:0 0 12px 0;">સ્થિતિ: {status_text}</h3>
                <p style="font-size:13.5px; color:#cbd5e1;">૧૦ દિવસનો ડેમો સમય અથવા ભાડાની મુદત પૂર્ણ થઈ છે. સોફ્ટવેર ચાલુ રાખવા નીચેના QR કોડ પર પેમેન્ટ કરી સંપર્ક કરો:</p>
                <div style="background:white; padding:12px; border-radius:10px; display:inline-block; margin:12px 0; border:2px solid #ca8a04;">
                    <img src="/vault/jaymin_upi_qr.png" onerror="this.src='/vault/image.png'" style="width:210px; height:auto; border-radius:6px; display:block; margin:auto;">
                    <div style="color:#0f172a; font-weight:bold; margin-top:6px;">UPI: {upi_id}</div>
                </div>
                <div style="background:#334155; padding:10px; border-radius:8px; font-weight:bold; font-size:15px; color:#38bdf8;">
                    📞 કોન્ટેક્ટ એડમિન (જયમીનભાઈ): {admin_mob}
                </div>
                                <div style="background:#1e293b; border:1.5px solid #ca8a04; border-radius:8px; padding:12px; margin-top:14px; text-align:left;">
                    <div style="color:#fde047; font-weight:bold; font-size:12.5px; margin-bottom:6px; text-align:center;">👑 સુપર એડમિન માસ્ટર અનલૉક પેનલ (જયમીનભાઈ)</div>
                    <form action="/api/admin-license-unlock" method="POST" style="display:flex; flex-direction:column; gap:6px;">
                        <input type="hidden" name="target_shop_id" value="{active_sid}">
                        <input type="password" name="admin_pin" placeholder="માસ્ટર સિક્રેટ PIN નાખો" required style="width:100%; box-sizing:border-box; padding:6px; border-radius:4px; border:1px solid #475569; background:#0f172a; color:white; font-size:12px;">
                        <select name="unlock_type" style="width:100%; box-sizing:border-box; padding:6px; border-radius:4px; border:1px solid #475569; background:#0f172a; color:white; font-size:11px; font-weight:bold;">
                            <option value="30_DAYS">📅 ૩૦ દિવસનું સબસ્ક્રિપ્શન રિન્યુ (+30 Days)</option>
                            <option value="365_DAYS">📆 ૧ વર્ષનું સબસ્ક્રિપ્શન (+365 Days)</option>
                            <option value="LIFETIME">🏆 કાયમી ફુલ લાયસન્સ (Lifetime)</option>
                            <option value="RESET_CLOCK">⏰ તારીખ છેડછાડ રીસેટ અને અનલૉક (Reset Clock)</option>
                        </select>
                        <button type="submit" style="background:linear-gradient(135deg, #16a34a, #15803d); color:white; border:none; padding:6px; border-radius:5px; font-weight:bold; cursor:pointer; font-size:12px;">🔓 અનલૉક & રિન્યુ</button>
                    </form>
                </div>
                <div style="margin-top:14px;"><a href="/login" style="color:#fde047; text-decoration:none; font-weight:bold;">← લૉગિન પેજ પર જાઓ</a></div>
            </div>
        </body></html>
        """)

    shop_prof = shop_prof_early
    db_file = get_active_db_file(active_sid)
    store_title = shop_prof.get("store_name") or store_title
    conn = sqlite3.connect(db_file, timeout=60.0)
    c = conn.cursor()

    c.execute("SELECT store_mode, accessories_part2_active, pref_lang, subscription_mode, custom_comm_enabled, custom_comm_deduction, custom_comm_pct, default_home_tab, COALESCE(active_subparts, ''), COALESCE(rent_profile_completed, 0), COALESCE(max_discount_alert_pct, 2.0) FROM shop_custom_settings WHERE shop_id=?", (shop_prof.get("shop_id"),))
    extra_s = c.fetchone() or ("FRANCHISE_HO", 0, "gu", "RENT", 1, 500.0, 20.0, "F2")
    shop_prof["store_mode"] = extra_s[0] or "FRANCHISE_HO"
    shop_prof["accessories_part2_active"] = bool(extra_s[1]) if extra_s[1] is not None else False
    shop_prof["pref_lang"] = extra_s[2] or "gu"
    shop_prof["subscription_mode"] = extra_s[3] or "RENT"
    shop_prof["custom_comm_enabled"] = bool(extra_s[4]) if extra_s[4] is not None else True
    shop_prof["custom_comm_deduction"] = float(extra_s[5] if extra_s[5] is not None else 500.0)
    shop_prof["custom_comm_pct"] = float(extra_s[6] if extra_s[6] is not None else 20.0)
    def_home = STORE_CFG.get("default_home_tab") or (extra_s[7] if len(extra_s) > 7 and extra_s[7] else "F2")
    shop_prof["default_home_tab"] = def_home
    raw_subp = (extra_s[8] if len(extra_s) > 8 and extra_s[8] else part1_core.ALL_23_SUBPARTS)
    shop_prof["active_subparts"] = [x.strip() for x in raw_subp.split(",") if x.strip()]
    rent_prof_done = int(extra_s[9] if len(extra_s) > 9 and extra_s[9] is not None else 0)
    shop_prof["max_discount_alert_pct"] = float(extra_s[10] if len(extra_s) > 10 and extra_s[10] is not None else 2.0)
    # 👑 પરમિશનનો કાયદો: દુકાનનો મુખ્ય માલિક (Owner) કે સુપર એડમિન જે ટીકમાર્ક કરે એટલું જ સ્ટાફ જોઈ શકે અને કામ કરી શકે!
    early_uid = STORE_CFG.get("current_user_id", shop_prof.get("shop_id", "DEVANSHI"))
    if request and hasattr(request, "cookies"):
        c_u = request.cookies.get("devanshi_user_id")
        if c_u and early_uid != "SUPER_ADMIN":
            early_uid = urllib.parse.unquote(c_u)
    if early_uid and early_uid not in ("SUPER_ADMIN", "manshvi", "devanshi"):
        try:
            m_conn = sqlite3.connect(part1_core.MASTER_DB_FILE, timeout=30.0)
            mc = m_conn.cursor()
            mc.execute("SELECT role_type, permissions_json FROM store_partners_users WHERE UPPER(user_id)=UPPER(?) AND UPPER(store_id)=UPPER(?) LIMIT 1", (early_uid, shop_prof.get("shop_id", "DEVANSHI")))
            u_p_row = mc.fetchone()
            m_conn.close()
            if u_p_row and str(u_p_row[0]).upper() != "OWNER":
                raw_p = json.loads(u_p_row[1] or "{}")
                if raw_p and not raw_p.get("all"):
                    allowed_cnts = [c_k for c_k in ["F1","F2","F3","F4","F5","F6","F7","F8"] if raw_p.get(c_k) or (c_k=="F2" and raw_p.get("F2_BILLING")) or (c_k=="F1" and raw_p.get("F1_PURCHASE")) or (c_k=="F3" and raw_p.get("F3_LEDGER")) or (c_k=="F8" and raw_p.get("F8_AUDIT"))]
                    if allowed_cnts:
                        shop_prof["active_counters"] = [c_k for c_k in shop_prof.get("active_counters", allowed_cnts) if c_k in allowed_cnts]
                        if def_home in ("F1","F2","F3","F4","F5","F6","F7","F8") and def_home not in shop_prof["active_counters"]:
                            def_home = shop_prof["active_counters"][0]
                    all_s_keys = ["SMART_TERMINAL","LIVE_STOCK_VIEW","UNIVERSAL_SEARCH","APX_SALES_RAW","BUYBACK_STOCK","CUSTOMER_DUE","SUPPLIER_PURCHASE","ACCESSORIES_LEDGER","RECHARGE_LAPU_VIEW","DAILY_SUMMARY","GALLA_AUDIT_HISTORY","SALESMAN_360_MATRIX","STAFF_ATTENDANCE_SHEET","BARCODE_AUDIT","OLD_STOCK_CLEARANCE","GST_SUMMARY_SHEET","SMART_DESK_GROWTH","GUJARATI_CONFIG"]
                    allowed_shts = [s_k for s_k in all_s_keys if raw_p.get(s_k) or (s_k=="LIVE_STOCK_VIEW" and raw_p.get("VIEW_STOCK")) or (s_k=="UNIVERSAL_SEARCH" and raw_p.get("SEARCH_HISTORY"))]
                    if allowed_shts:
                        if "SMART_TERMINAL" not in allowed_shts and allowed_cnts:
                            allowed_shts.insert(0, "SMART_TERMINAL")
                        shop_prof["active_sheets"] = [s_k for s_k in shop_prof.get("active_sheets", allowed_shts) if s_k in allowed_shts]
                    g_map = [("BANK_CASH","GALLA_BANK_CASH"),("ACC_DCASH","GALLA_ACC_DCASH"),("RECHARGE","GALLA_RECHARGE"),("EXTRA_CASH","GALLA_EXTRA_CASH")]
                    if any(raw_p.get(gk_p) for _, gk_p in g_map):
                        shop_prof["active_gallas"] = [gk for gk, gk_p in g_map if raw_p.get(gk_p)]
                    all_sub_k = ["F1_1","F1_2","F1_3","F1_5","F2_1","F2_2","F2_3","F3_1","F3_2","F3_3","F3_4","F3_5","F3_6","F4_1","F4_2","F5_1","F5_2","F5_3","F5_4","F6_1","F7_1","F7_2","F7_3","F8_1","F8_2","F8_3"]
                    explicit_subs = [sk for sk in all_sub_k if raw_p.get(sk)]
                    if explicit_subs:
                        shop_prof["active_subparts"] = [sk for sk in shop_prof.get("active_subparts", explicit_subs) if sk in explicit_subs]
        except Exception:
            pass
    cur_sid_check = str(shop_prof.get("shop_id", "")).strip().upper()
    if shop_prof["subscription_mode"] == "RENT" and not rent_prof_done and cur_sid_check not in ("DEVANSHI", "MANSHVI") and not (sheet or mode or msg):
        conn.close()
        from fastapi.responses import RedirectResponse
        return RedirectResponse(url="/store-setup?rent_onboarding=1", status_code=303)
    allowed_cnt_list = shop_prof.get("active_counters") or ["F1", "F2", "F3", "F4", "F5", "F6", "F7", "F8"]
    first_allowed_cnt = allowed_cnt_list[0] if allowed_cnt_list else "F2"
    if not sheet and not mode:
        if def_home in ("F1", "F2", "F3", "F4", "F5", "F6", "F7", "F8"):
            sheet = "SMART_TERMINAL"
            mode = def_home if def_home in allowed_cnt_list else first_allowed_cnt
        else:
            sheet = def_home
            mode = first_allowed_cnt
    elif sheet in ("F1", "F2", "F3", "F4", "F5", "F6", "F7", "F8"):
        mode = sheet if sheet in allowed_cnt_list else first_allowed_cnt
        sheet = "SMART_TERMINAL"
    else:
        sheet = sheet or "SMART_TERMINAL"
        if sheet == "SMART_TERMINAL" and not mode:
            mode = def_home if (def_home in ("F1", "F2", "F3", "F4", "F5", "F6", "F7", "F8") and def_home in allowed_cnt_list) else first_allowed_cnt
        else:
            mode = mode if (mode and mode in allowed_cnt_list) else first_allowed_cnt
    eff_bt = f2_bill_type or bill_type
    if eff_bt:
        shop_prof["f2_bill_type"] = eff_bt
        STORE_CFG["f2_bill_type"] = eff_bt

    # Save exact active page (sheet & mode) so "⬅️ મુખ્ય ERP પર પાછા જાઓ" always returns to the exact last open page!
    if sheet == "SMART_TERMINAL":
        STORE_CFG["last_active_url"] = f"/?sheet=SMART_TERMINAL&mode={mode}"
    else:
        STORE_CFG["last_active_url"] = f"/?sheet={sheet}"
    STORE_CFG["last_active_sheet"] = sheet
    STORE_CFG["last_active_mode"] = mode

    st_mode = (shop_prof.get("store_mode") or "FRANCHISE_HO").upper()
    is_retail_mode = ("RETAIL" in st_mode or "STANDALONE" in st_mode)
    shop_prof["store_mode"] = "RETAIL_STANDALONE" if is_retail_mode else "FRANCHISE_HO"
    st_mode = shop_prof["store_mode"]
    mode_badge_str = "🏪 પર્સનલ રિટેલ સ્ટોર મોડ (Retail Mode)" if is_retail_mode else "👑 ફ્રેન્ચાઇઝી સ્ટોર મોડ (Franchise HO)"
    sub_type_str = "ડેમો મોડ (DEMO)" if STORE_CFG.get("license_mode") == "TRIAL" else "ભાડા મોડ (RENT)"
    license_display = f"મોડ: {mode_badge_str} | પ્લાન: {sub_type_str} ({status_text} - બાકી દિવસો: {days_left})"

    bank_cash = get_galla_balance("BANK_CASH")
    acc_dcash = get_galla_balance("ACC_DCASH")
    recharge_cash = get_galla_balance("RECHARGE")
    extra_cash = get_galla_balance("EXTRA_CASH")

    today_str = str(datetime.date.today())
    c.execute("SELECT SUM(gift_amt) FROM live_terminal_grid WHERE substr(entry_time, 1, 10) = ?", (today_str,))
    r_gift = c.fetchone()
    today_gift = float(r_gift[0] if (r_gift and r_gift[0] is not None) else 0.0)

    c.execute("SELECT COUNT(*) FROM finance_do_list WHERE status = 'PENDING'")
    active_do_count = c.fetchone()[0] or 0
    c.execute("SELECT COUNT(*) FROM apx_sales_raw WHERE status = 'PENDING'")
    pending_apx_count = c.fetchone()[0] or 0

    c.execute("SELECT id, name, designation, fixed_salary FROM config_staff")
    staff_db_rows = c.fetchall()
    staff_list = [f"{r[1]} ({r[2]})" for r in staff_db_rows]

    c.execute("SELECT id, party_name, category FROM config_parties")
    party_db_rows = c.fetchall()

    c.execute("SELECT head_name FROM config_expense_heads")
    exp_heads = [r[0] for r in c.fetchall()]

    c.execute("SELECT bank_name FROM config_banks")
    bank_opts = [r[0] for r in c.fetchall()]

    c.execute("SELECT name FROM config_categories")
    cat_opts = [r[0] for r in c.fetchall()]

    c.execute("SELECT title FROM config_designations")
    desig_opts = [r[0] for r in c.fetchall()]

    c.execute("SELECT id, title FROM config_designations")
    desig_db_rows = c.fetchall()

    c.execute("SELECT id, name FROM config_categories")
    cat_db_rows = c.fetchall()

    c.execute("SELECT date, model, imei, salesman, total_cost, purchase_cost, repair_cost, source_type FROM buyback_stock WHERE status='IN_STOCK' ORDER BY id DESC")
    bb_stock_opts = c.fetchall()

    c.execute("SELECT id, company, customer_name, imei, loan_amt, phone, scheme_name, net_bank_amt, customer_address, customer_pincode, COALESCE(doc_path,''), COALESCE(brand,'Vivo'), COALESCE(model,''), COALESCE(do_ref_no,''), COALESCE(app_deal_id,''), COALESCE(emi_amt,0) FROM finance_do_list WHERE status = 'PENDING' ORDER BY id DESC")
    dos = c.fetchall()

    c.execute("SELECT bill_no, bill_date, customer_name, phone, model, imei, mop_price, id, customer_address, customer_pincode FROM apx_sales_raw WHERE status = 'PENDING' ORDER BY bill_no ASC")
    pending_apx_bills = c.fetchall()

    c.execute("SELECT imei, model, brand, sale_rate, party_name, entry_date, purchase_rate FROM live_stock WHERE status='IN_STOCK'")
    stock_inward_map = {
        row[0]: {'model': row[1], 'brand': row[2], 'mop': row[3], 'party': row[4], 'date': row[5], 'dp': row[6]}
        for row in c.fetchall()
    }

    current_bill = get_current_bill_no()

    # --- નિયમ ૦.૨: દરેક પેમેન્ટ ડ્રોપ-ડાઉનમાં ચારેય સ્વતંત્ર ગલ્લા ફરજિયાત ---
    all_galla_meta = [
        ("BANK_CASH", "૧. બેંક કેશ (ગલ્લો ૧ - મુખ્ય કાઉન્ટર ગલ્લો)"),
        ("ACC_DCASH", "૨. એક્સેસરીઝ કેશ (ગલ્લો ૨)"),
        ("RECHARGE", "૩. રિચાર્જ કેશ (ગલ્લો ૩)"),
        ("EXTRA_CASH", "૪. એક્સ્ટ્રા કેશ (ગલ્લો ૪)")
    ]
    all_galla_options = "".join([
        f'<option value="{gk}">{gl}</option>' for gk, gl in all_galla_meta
    ])

    indian_lang_options = """
        <option value="gu">૧. ગુજરાતી (Gujarati)</option>
        <option value="hi">૨. હિન્દી (Hindi)</option>
        <option value="en">૩. અંગ્રેજી (English)</option>
        <option value="mr">૪. મરાઠી (Marathi)</option>
        <option value="pa">૫. પંજાબી (Punjabi)</option>
        <option value="bn">૬. બંગાળી (Bengali)</option>
        <option value="ta">૭. તમિલ (Tamil)</option>
        <option value="te">૮. તેલુગુ (Telugu)</option>
        <option value="kn">૯. કન્નડ (Kannada)</option>
        <option value="ml">૧૦. મલયાલમ (Malayalam)</option>
        <option value="or">૧૧. ઉડિયા (Odia)</option>
        <option value="ur">૧૨. ઉર્દૂ (Urdu)</option>
    """

    c.execute("SELECT id, title, start_time, end_time FROM custom_store_reminders WHERE store_id=? AND is_active=1", (shop_prof.get("shop_id"),))
    custom_rems = c.fetchall()
    rem_items = []
    current_hour = datetime.datetime.now().hour
    if 17 <= current_hour <= 19:
        rem_items.append("<span>⚠️ <b>[સાંજનું રીમાઇન્ડર 17:00-19:00]:</b> આજનો સ્ટોક રિપોર્ટ અને દૈનિક સેલ્સ બિલ / હિસાબ ચેક કર્યા કે બાકી છે?</span>")
    for cr in custom_rems:
        rem_items.append(f"<span>🔔 <b>[{cr[2]} થી {cr[3]}] {cr[1]}</b> <a href='/delete-custom-reminder?id={cr[0]}&pin=1986' onclick='return confirmDeleteReminder(this, {cr[0]})' style='color:#dc2626; text-decoration:none; font-size:11px;'>[✖]</a></span>")
    rem_joined = " | ".join(rem_items) if rem_items else "<span>🔔 દૈનિક રિમાઇન્ડર બાર સક્રિય (સાંજે ૫ થી ૭ ઓટો એલર્ટ)</span>"
    reminder_html = f"""
    <div style="background:#fef9c3; border:1px solid #eab308; color:#854d0e; padding:5px 12px; margin:4px 8px; font-weight:bold; border-radius:4px; display:flex; justify-content:space-between; align-items:center; font-size:11.5px; flex-wrap:wrap; gap:6px;">
        <div>{rem_joined}</div>
        <button type="button" onclick="document.getElementById('add_rem_box').style.display='flex'" style="background:#ca8a04; color:white; border:none; padding:3px 8px; border-radius:3px; cursor:pointer; font-weight:bold; font-size:11px;">[+ નવું રિમાઇન્ડર ઉમેરો]</button>
    </div>
    <form id="add_rem_box" action="/add-custom-reminder" method="post" style="display:none; gap:6px; align-items:center; background:#fffbeb; border:1px solid #f59e0b; padding:6px 12px; margin:4px 8px; border-radius:4px;">
        <b>નવું રિમાઇન્ડર:</b>
        <input type="text" name="title" placeholder="રિમાઇન્ડર સૂચના લખો (દા.ત. બેંકમાં કેશ ભરવી, સ્ટોક ગણતરી)..." required style="flex:1; padding:4px 8px;">
        <span>સમય:</span>
        <input type="time" name="start_time" value="17:00" style="padding:3px;"> થી <input type="time" name="end_time" value="19:00" style="padding:3px;">
        <button type="submit" style="background:#16a34a; color:white; border:none; padding:4px 12px; border-radius:3px; font-weight:bold; cursor:pointer;">સેવ કરો</button>
        <button type="button" onclick="document.getElementById('add_rem_box').style.display='none'" style="background:#dc2626; color:white; border:none; padding:4px 8px; border-radius:3px; cursor:pointer;">✖</button>
    </form>
    """

    if sheet == "SMART_TERMINAL":
        sheet_content = part2_b_counters.render_smart_terminal(
            conn=conn, c=c, mode=mode, f4_sm_filter=f4_sm_filter, staff_list=staff_list,
            party_db_rows=party_db_rows, cat_opts=cat_opts, bb_stock_opts=bb_stock_opts,
            dos=dos, pending_apx_bills=pending_apx_bills, stock_inward_map=stock_inward_map,
            current_bill=current_bill, all_galla_options=all_galla_options, bank_opts=bank_opts,
            exp_heads=exp_heads, today_str=today_str, shop_prof=shop_prof
        )
    elif sheet == "UNIVERSAL_SEARCH":
        sheet_content = part2_b_counters.render_universal_search(
            conn=conn, c=c, search_q=search_q, u_tab=u_tab, sel_cust=sel_cust,
            sel_sm_hist=sel_sm_hist, sel_sm_due=sel_sm_due, sel_supp=sel_supp,
            bb_view=bb_view, bb_stock_opts=bb_stock_opts, staff_list=staff_list,
            all_galla_options=all_galla_options, indian_lang_options=indian_lang_options, shop_prof=shop_prof
        )
    elif sheet == "LIVE_STOCK_VIEW":
        sheet_content = part2_d_sheets.render_live_stock_view(conn, c)
    else:
        sheet_content = part2_d_sheets.render_other_sheets(
            sheet=sheet, conn=conn, c=c, sm_range=sm_range, from_d=from_d, to_d=to_d,
            today_str=today_str, dos=dos, desig_opts=desig_opts, cat_opts=cat_opts,
            staff_db_rows=staff_db_rows, party_db_rows=party_db_rows, desig_db_rows=desig_db_rows,
            cat_db_rows=cat_db_rows, shop_prof=shop_prof, sm_staff=sm_staff, snap_date=snap_date
        )

    # નિયમ ૨૩૫: સુપર એડમિન SaaS મોડ્યુલ લાયસન્સિંગ (Tick/Untick) અમલ
    active_mods = shop_prof.get("mods") or {}
    if not active_mods.get("mod_accessories", 1):
        shop_prof["accessories_part2_active"] = False
        if "ACCESSORIES_LEDGER" in shop_prof.get("active_sheets", []):
            shop_prof["active_sheets"] = [s for s in shop_prof["active_sheets"] if s != "ACCESSORIES_LEDGER"]
    if not active_mods.get("mod_smart_khata", 1):
        if "CUSTOMER_DUE" in shop_prof.get("active_sheets", []):
            shop_prof["active_sheets"] = [s for s in shop_prof["active_sheets"] if s != "CUSTOMER_DUE"]

    # નિયમ ૨૩૨ & ૨૩૭: વેપારી પેમેન્ટ ડ્યુ-ડેટ શેડ્યુલર અને લાલ/પીળી બત્તી એલર્ટ બેનર
    vendor_due_alert_banner_html = ""
    if active_mods.get("mod_vendor_due_alerts", 1):
        try:
            from part1_core import add_col_if_missing
            add_col_if_missing(conn, "supplier_purchase_ledger", "credit_days", "INTEGER DEFAULT 0")
            add_col_if_missing(conn, "supplier_purchase_ledger", "due_date", "TEXT DEFAULT ''")
            c.execute("""SELECT id, date, supplier_name, bill_no, total_bill, paid_amt, balance_due, COALESCE(due_date,''), COALESCE(credit_days,0)
                         FROM supplier_purchase_ledger
                         WHERE balance_due > 0
                         ORDER BY CASE WHEN due_date != '' THEN due_date ELSE date END ASC LIMIT 8""")
            due_supp_rows = c.fetchall()
            due_alerts_list = []
            today_d_obj = datetime.date.today()
            for dsr in due_supp_rows:
                ds_id, ds_dt, ds_sup, ds_bno, ds_tot, ds_pd, ds_bal, ds_duedt, ds_cdays = dsr
                eff_due_str = ds_duedt
                if not eff_due_str and ds_dt:
                    try:
                        b_d = datetime.datetime.strptime(str(ds_dt)[:10], "%Y-%m-%d").date()
                        eff_due_str = str(b_d + datetime.timedelta(days=int(ds_cdays or 7)))
                    except Exception:
                        eff_due_str = ds_dt
                days_rem = 999
                try:
                    d_o = datetime.datetime.strptime(str(eff_due_str)[:10], "%Y-%m-%d").date()
                    days_rem = (d_o - today_d_obj).days
                except Exception:
                    pass
                if days_rem <= 3:
                    badge_col = "#dc2626" if days_rem <= 0 else "#d97706"
                    status_lbl = f"🚨 મુદત પૂરી / આજે ચૂકવવાના ({eff_due_str})" if days_rem <= 0 else f"⚠️ {days_rem} દિવસ બાકી (ડ્યુ તારીખ: {eff_due_str})"
                    wa_rem_msg = urllib.parse.quote(f"નમસ્તે {ds_sup}, બિલ નંબર {ds_bno} ના બાકી ₹{float(ds_bal or 0):,.0f} (ડ્યુ તારીખ: {eff_due_str}) ની નોંધ.")
                    due_alerts_list.append(
                        f"<div style='display:flex; justify-content:space-between; align-items:center; gap:8px; padding:4px 0; border-bottom:1px dashed #fca5a5;'>"
                        f"<span><b style='background:{badge_col}; color:white; padding:2px 6px; border-radius:4px; font-size:11px;'>{status_lbl}</b> "
                        f"વેપારી: <b>{ds_sup}</b> (બિલ: {ds_bno} | ખરીદી: {ds_dt}) — ચૂકવવાના બાકી: <b style='color:#dc2626; font-size:13px;'>₹{float(ds_bal or 0):,.0f}</b></span>"
                        f"<span style='display:flex; gap:5px;'>"
                        f"<a href='/?sheet=SMART_TERMINAL&mode=F3' style='background:#15803d; color:white; padding:3px 9px; border-radius:4px; text-decoration:none; font-weight:bold; font-size:11px;'>💸 F3 પેમેન્ટ ચૂકવો</a>"
                        f"<a href='https://api.whatsapp.com/send?text={wa_rem_msg}' target='_blank' style='background:#25D366; color:#0f172a; padding:3px 8px; border-radius:4px; text-decoration:none; font-weight:bold; font-size:11px;'>📲 WhatsApp</a>"
                        f"</span></div>"
                    )
            if due_alerts_list:
                vendor_due_alert_banner_html = (
                    f"<div id='vendor_due_alert_container' style='background:#fff1f2; border:2px solid #e11d48; color:#881337; padding:8px 12px; margin:6px 8px; border-radius:6px; font-size:12px; box-shadow:0 3px 10px rgba(225,29,72,0.15);'>"
                    f"<div style='display:flex; justify-content:space-between; align-items:center; border-bottom:1.5px solid #fecdd3; padding-bottom:4px; margin-bottom:6px;'>"
                    f"<span style='font-weight:900; font-size:12.5px; color:#be123c;'>⏰ વેપારી પેમેન્ટ ડ્યુ-ડેટ રિમાઇન્ડર (Vendor Payment Due-Date Alert - {len(due_alerts_list)} બિલ):</span>"
                    f"<div style='display:flex; gap:6px; align-items:center;'>"
                    f"<span style='font-size:11px; color:#9f1239;'>(માત્ર ઓનર / પાર્ટનર / એકાઉન્ટન્ટ માટે)</span>"
                    f"<button type='button' onclick=\"this.closest('#vendor_due_alert_container').style.display='none'; sessionStorage.setItem('hide_vendor_due_alert','1');\" style='background:#be123c; color:white; border:none; padding:4px 10px; border-radius:4px; font-weight:bold; font-size:11px; cursor:pointer;'>✖ એલર્ટ હાઇડ કરો</button>"
                    f"</div></div>"
                    + "".join(due_alerts_list) +
                    "</div>"
                )
        except Exception:
            pass

    inter_galla_global_alert_html = vendor_due_alert_banner_html
    try:
        c.execute("""SELECT id, tx_date, lender_galla, borrower_galla, amount, COALESCE(settled_amt,0), remarks
                     FROM inter_galla_debt_ledger WHERE status='PENDING' ORDER BY id DESC""")
        pend_ig_rows = c.fetchall()
        g_bal_map = {
            "BANK_CASH": bank_cash,
            "ACC_DCASH": acc_dcash,
            "RECHARGE": recharge_cash,
            "EXTRA_CASH": extra_cash
        }
        g_lbl_gu = {
            "BANK_CASH": "ગલ્લો ૧ (બેંક કેશ)",
            "ACC_DCASH": "ગલ્લો ૨ (એક્સેસરીઝ D-Cash)",
            "RECHARGE": "ગલ્લો ૩ (રિચાર્જ કેશ)",
            "EXTRA_CASH": "ગલ્લો ૪ (એક્સ્ટ્રા કેશ)"
        }
        ready_alerts = []
        for ig_r in pend_ig_rows:
            ig_id, ig_dt, l_gal, b_gal, ig_amt, ig_set, ig_rem = ig_r
            rem_debt = max(0.0, float(ig_amt or 0) - float(ig_set or 0))
            b_avail = float(g_bal_map.get(b_gal, 0.0))
            if rem_debt > 0 and b_avail > 0:
                ready_alerts.append(
                    f"<div style='display:flex; justify-content:space-between; align-items:center; gap:8px; padding:4px 0; border-bottom:1px dashed #f59e0b;'>"
                    f"<span>🔔 <b>ક્રોસ-ગલ્લા ઉછીના વસૂલાત ટ્રીગર ({ig_dt}):</b> <b>{g_lbl_gu.get(b_gal, b_gal)}</b> માં હવે <b>₹{b_avail:,.0f}</b> કેશ હાજર છે! "
                    f"<b>{g_lbl_gu.get(l_gal, l_gal)}</b> માંથી ઉછીના ચૂકવેલા <b>₹{rem_debt:,.0f}</b> ({ig_rem}) પાછા જમા કરો:</span>"
                    f"<a href='/api/settle-inter-galla-debt?debt_id={ig_id}' style='background:#dc2626; color:white; padding:4px 10px; border-radius:4px; text-decoration:none; font-weight:900; font-size:11.5px; white-space:nowrap;'>⚡ ૧-ક્લિક પરત સેટલ (₹{min(rem_debt, b_avail):,.0f})</a>"
                    f"</div>"
                )
        if ready_alerts:
            inter_galla_global_alert_html = (
                "<div style='background:#fef3c7; border:2px solid #d97706; color:#92400e; padding:8px 12px; margin:6px 8px; border-radius:6px; font-size:12px;'>"
                + "".join(ready_alerts) +
                "</div>"
            )
    except Exception:
        pass
    conn.close()

    def tab_cls(target):
        return "active" if sheet == target else ""

    msg_html = f"<div style='background:#dcfce7; border:1px solid #16a34a; color:#166534; padding:8px 12px; margin:6px 8px; font-weight:bold; border-radius:4px;'>{msg}</div>" if msg else ""
    if STORE_CFG.get("ota_banner_active"):
        ota_m = STORE_CFG.get("ota_banner_msg", "🔔 જયમીનભાઈએ આ સુધારા-વધારા કર્યા છે અને તમારું સોફ્ટવેર ઓટોમેટિક અપડેટ થઈ ગયું છે!")
        ota_t = STORE_CFG.get("ota_banner_time", "")
        ota_v = STORE_CFG.get("applied_ota_version", "")
        msg_html = f"""
        <div id="ota_live_banner" style="background:linear-gradient(90deg, #065f46, #15803d); border:2px solid #fde047; color:#ffffff; padding:10px 16px; margin:6px 8px; border-radius:6px; display:flex; justify-content:space-between; align-items:center; box-shadow:0 4px 12px rgba(0,0,0,0.2);">
            <div>
                <span style="background:#fde047; color:#0f172a; padding:2px 8px; border-radius:4px; font-weight:800; font-size:11.5px; margin-right:8px;">🚀 ઓટો-અપડેટ સફળ ({ota_v})</span>
                <b style="font-size:13px;">{ota_m}</b>
                <span style="font-size:11px; color:#bbf7d0; margin-left:8px;">({ota_t})</span>
            </div>
            <a href="/api/dismiss-ota-banner?return_to=HOME" style="background:#fde047; color:#0f172a; padding:5px 12px; border-radius:4px; text-decoration:none; font-weight:800; font-size:12px;">✓ ઓકે, સમજી ગયા</a>
        </div>
        """ + msg_html

    cur_role = "👑 દુકાનદાર (Owner)"
    cur_user_id = active_sid
    if request and hasattr(request, "cookies"):
        c_role = request.cookies.get("devanshi_user_role")
        c_uid = request.cookies.get("devanshi_user_id")
        if c_role:
            cur_role = urllib.parse.unquote(c_role)
        if c_uid:
            cur_user_id = urllib.parse.unquote(c_uid)



    cur_sid_up = str(shop_prof.get("shop_id", "")).upper()
    if cur_sid_up in ("DEVANSHI", "MANSHVI"):
        other_sample = "MANSHVI" if cur_sid_up == "DEVANSHI" else "DEVANSHI"
        other_lbl = "🏪 મનસ્વી (રિટેલ સેમ્પલ)" if other_sample == "MANSHVI" else "👑 દેવાંશી (ફ્રેન્ચાઇઝી સેમ્પલ)"
        sample_top_btns = (
            f'<span style="background:#16a34a; color:#fde047; border:1px solid #fde047; padding:3px 7px; border-radius:4px; font-weight:900; font-size:10.5px;">♾️ લાઇફટાઇમ માસ્ટર સેમ્પલ</span>'
            f'<a href="/jaymin-open-sample/{other_sample}" style="background:#7c3aed; color:white; border:1px solid #d8b4fe; padding:4px 8px; border-radius:4px; font-weight:bold; font-size:10.5px; text-decoration:none;">⇄ {other_lbl} ખોલો</a>'
            f'<button type="button" onclick="triggerSampleWipeFromTerminal(\'{cur_sid_up}\')" style="background:#dc2626; color:white; border:1px solid #fca5a5; padding:4px 9px; border-radius:4px; font-weight:bold; font-size:11px; cursor:pointer;">🧹 ૧-ક્લિક ડમી ડેટા સાફ કરો</button>'
            f'<form action="/master-seed-sample-store" method="post" style="display:inline; margin:0;"><input type="hidden" name="shop_id" value="{cur_sid_up}"><input type="hidden" name="return_to" value="TERMINAL"><button type="submit" style="background:#15803d; color:white; border:1px solid #86efac; padding:4px 9px; border-radius:4px; font-weight:bold; font-size:11px; cursor:pointer;">🔄 સેમ્પલ ડેટા ભરો</button></form>'
        )
    else:
        sample_top_btns = ""
    
    # સુરક્ષા ફિલ્ટર: વેપારી પેમેન્ટ ડ્યુ-ડેટ એલર્ટ સામાન્ય સેલ્સમેન કે સ્ટાફને ન દેખાય — ફક્ત ઓનર, પાર્ટનર, એકાઉન્ટન્ટને જ દેખાય
    is_mgmt_role = (str(cur_user_id).upper() in ("SUPER_ADMIN", "ADMIN", "1986") or any(k in str(cur_role).upper() for k in ["OWNER", "ઓનર", "દુકાનદાર", "PARTNER", "પાર્ટનર", "ACCOUNTANT", "એકાઉન્ટન્ટ", "SUPER_ADMIN", "સુપર એડમિન"]))
    if not is_mgmt_role:
        inter_galla_global_alert_html = ""

    super_admin_back_btn = '<a href="/super-admin?pin=1986" style="background:#ca8a04; color:white; padding:4px 9px; border-radius:4px; text-decoration:none; font-weight:bold; font-size:11px; border:1px solid #fef08a;">⬅️ સુપર એડમિન હબ</a>' if cur_user_id == "SUPER_ADMIN" else ""
    # સ્તર ૧: ટોચની કંટ્રોલ પટ્ટી (Top Control Bar - #0b1528 - 100% Responsive Wrap, Never Clips Logout!)
    user_top_bar_html = f"""
    <div style="background:#0b1528; color:white; padding:5px 8px; display:flex; justify-content:space-between; align-items:center; border-bottom:2px solid #38bdf8; font-size:11px; flex-wrap:wrap; gap:4px; width:100%; box-sizing:border-box;">
        <div style="display:flex; align-items:center; gap:4px; flex-wrap:wrap;">
            <button type="button" onclick="goBackUniversalHistory()" style="background:#eab308; color:#0f172a; border:1px solid #fef08a; padding:3px 8px; border-radius:4px; font-weight:900; font-size:10.5px; cursor:pointer;" title="અગાઉના ચાલુ કામ પર પાછા જાઓ (Esc કી / Mobile Back - ભરેલો ડેટા સચવાયેલો રહેશે!)">⬅️ પાછા (Esc)</button>
            <span style="background:#1e293b; color:#cbd5e1; padding:2px 6px; border-radius:4px; font-size:10.5px; border:1px solid #475569;">Shop ID: <b>{shop_prof.get('shop_id', 'DEVANSHI')}</b> | ID: {cur_user_id}</span>
            <span style="background:#78350f; color:#fef08a; padding:2px 6px; border-radius:4px; font-weight:bold; font-size:10.5px; border:1px solid #eab308;">{cur_role}</span>
            <span style="background:#0f766e; color:white; padding:2px 6px; border-radius:4px; font-weight:bold; font-size:10.5px;">{mode_badge_str}</span>
            {sample_top_btns}
        </div>
        <div style="display:flex; align-items:center; gap:4px; flex-wrap:wrap; justify-content:flex-end; max-width:100%;">
            <select id="soundbox_mode_sel" onchange="setSoundboxMode(this.value)" style="background:#1e293b; color:#fde047; border:1px solid #475569; padding:2px 4px; border-radius:4px; font-size:10px; font-weight:bold;" title="સાઉન્ડબોક્સ કંટ્રોલ">
                <option value="SILENT">🔇 અવાજ બંધ (Silent)</option>
                <option value="BEEP">🔔 માત્ર બીપ (Beep)</option>
                <option value="VOICE">🔊 બોલતો અવાજ (Voice)</option>
            </select>
            <input type="range" id="soundbox_vol_slider" min="0.1" max="1.0" step="0.1" value="0.8" onchange="localStorage.setItem('devanshi_sb_vol', this.value)" style="width:42px; accent-color:#fde047;" title="સાઉન્ડબોક્સ અવાજ (Volume)">
            <button type="button" onclick="stopSoundboxSpeech()" style="background:#475569; color:white; border:none; padding:2px 5px; border-radius:4px; font-size:10px; cursor:pointer;" title="અવાજ રોકો (Esc)">⏹️</button>
            <button type="button" onclick="sendStuckScreenAlertToAdmin()" style="background:#e11d48; color:white; border:1px solid #fda4af; padding:3px 6px; border-radius:4px; font-weight:bold; font-size:10px; cursor:pointer; white-space:nowrap;" title="ક્યાંક અટક્યા હોવ તો જયમીનભાઈના લેપટોપ/મોબાઈલ પર તમારી ચાલુ સ્ક્રીન (AnyDesk Mode) તરત મોકલો">🖥️ લાઈવ મદદ (AnyDesk)</button>
            <button type="button" onclick="openExtraErpWindow()" style="background:#0284c7; color:white; border:1px solid #7dd3fc; padding:3px 6px; border-radius:4px; font-weight:bold; font-size:10px; cursor:pointer; white-space:nowrap;" title="હાલનું કામ અધૂરું રાખી બાજુમાં બીજી સ્વતંત્ર વિન્ડો ખોલી બિલ કે પ્રિન્ટ કાઢો">🗔 + બીજી વિન્ડો ખોલો</button>
            <button type="button" onclick="openInlineQuickCreateModal('PARTY', '')" style="background:#15803d; color:white; border:1px solid #86efac; padding:3px 6px; border-radius:4px; font-weight:bold; font-size:10px; cursor:pointer; white-space:nowrap;" title="ચાલુ કાઉન્ટરે નવું લેજર/વેપારી/બ્રાન્ડ/સ્ટાફ બનાવો (Alt+C)">➕ નવું લેજર (Alt+C)</button>
            <button type="button" onclick="openMobileQrModal()" style="background:#059669; color:white; border:1px solid #6ee7b7; padding:3px 6px; border-radius:4px; font-weight:bold; font-size:10px; cursor:pointer; white-space:nowrap;">📱 QR / App</button>
            <a href="/nextlevel-hifi-ai-hub" style="background:linear-gradient(135deg,#db2777,#9333ea); color:#fde047; border:1.5px solid #fde047; padding:3px 8px; border-radius:4px; font-weight:900; font-size:10.5px; text-decoration:none; white-space:nowrap;" title="૬ નેક્સ્ટ-લેવલ હાઈ-ફાઈ AI સુવિધાઓ (ગુજરાતી વૉઇસ બિલિંગ, CCTV ફૂટફોલ, Amazon/Flipkart ભાવ ટ્રેકર, AI સેલ્સ ટ્રેનર, Google 5-Star રિવ્યુ, ફેસ હાજરી)">🚀 6 Hi-Fi AI હબ</a>
            <button type="button" onclick="openAiAssistantModal()" style="background:linear-gradient(135deg,#7c3aed,#4f46e5); color:white; border:1px solid #fde047; padding:3px 6px; border-radius:4px; font-weight:bold; font-size:10px; cursor:pointer; white-space:nowrap;">🤖 વાઈફાઈ લાઈવ AI</button>
            <button type="button" onclick="openFieldConfigModal()" style="background:#0369a1; color:white; border:none; padding:3px 6px; border-radius:4px; font-weight:bold; font-size:10px; cursor:pointer; white-space:nowrap;">⚙️ ખાના કસ્ટમાઇઝ</button>
                        <select id="def_home_selector" onchange="changeDefaultLanding(this.value)" style="background:#1e293b; color:#38bdf8; border:1px solid #38bdf8; padding:2px 5px; border-radius:4px; font-size:10px; font-weight:bold; cursor:pointer;" title="ડિફોલ્ટ ઓપનિંગ પેજ">
                <option value="" disabled>🎯 ઓપનિંગ પેજ:</option>
                <option value="F2" {'selected' if def_home=='F2' else ''}>🎯 F2: વેચાણ/DO</option>
                <option value="F1" {'selected' if def_home=='F1' else ''}>🎯 F1: ખરીદી</option>
                <option value="F5" {'selected' if def_home=='F5' else ''}>🎯 F5: બાય-બેક</option>
                <option value="SALESMAN_360_MATRIX" {'selected' if def_home=='SALESMAN_360_MATRIX' else ''}>🎯 360° સેલ્સમેન</option>
                <option value="LIVE_STOCK_VIEW" {'selected' if def_home=='LIVE_STOCK_VIEW' else ''}>🎯 લાઈવ સ્ટોક</option>
                <option value="DAILY_SUMMARY" {'selected' if def_home=='DAILY_SUMMARY' else ''}>🎯 દૈનિક રોજમેળ</option>
                <option value="CUSTOMER_DUE" {'selected' if def_home=='CUSTOMER_DUE' else ''}>🎯 ગ્રાહક બાકી</option>
                <option value="UNIVERSAL_SEARCH" {'selected' if def_home=='UNIVERSAL_SEARCH' else ''}>🎯 360° સર્ચ</option>
                <option value="BUYBACK_STOCK" {'selected' if def_home=='BUYBACK_STOCK' else ''}>🎯 બાયબેક સ્ટોક</option>
                <option value="F3" {'selected' if def_home=='F3' else ''}>🎯 F3: રિચાર્જ</option>
                <option value="F4" {'selected' if def_home=='F4' else ''}>🎯 F4: બેંક જમા</option>
                <option value="F6" {'selected' if def_home=='F6' else ''}>🎯 F6: પેમેન્ટ/ખર્ચ</option>
                <option value="F7" {'selected' if def_home=='F7' else ''}>🎯 F7: રિપેરિંગ</option>
                <option value="F8" {'selected' if def_home=='F8' else ''}>🎯 F8: ૪-ગલ્લા ઓડિટ</option>
            </select>
            <a href="/mobile-app-installer" style="background:#16a34a; color:white; padding:3px 6px; border-radius:4px; text-decoration:none; font-weight:bold; font-size:10px; border:1px solid #86efac; white-space:nowrap;" title="મોબાઈલ, iPhone અને ટેબ્લેટમાં APK / App ઇન્સ્ટોલ કરો">📲 APK / મોબાઈલ App</a>
            <button type="button" onclick="toggleMobileOriginalDesktopLayout()" id="btn_layout_toggle" style="background:#eab308; color:#0f172a; padding:3px 6px; border-radius:4px; font-weight:900; font-size:10px; border:1px solid #fef08a; cursor:pointer; white-space:nowrap;" title="મોબાઈલમાં કોમ્પ્યુટર જેવું ઓરિજિનલ લેઆઉટ કે મોબાઈલ ઝૂમ બદલો">🖥️ ઓરિજિનલ લેઆઉટ</button>
            <a href="/store-setup" style="background:#0284c7; color:white; padding:3px 6px; border-radius:4px; text-decoration:none; font-weight:bold; font-size:10px; border:1px solid #7dd3fc; white-space:nowrap;">⚙️ મારી દુકાન સુવિધાઓ</a>
            {super_admin_back_btn}
            <a href="/logout" onclick="return confirm('શું તમે લૉગ આઉટ કરવા માંગો છો?')" style="background:#dc2626; color:white; padding:3px 8px; border-radius:4px; text-decoration:none; font-weight:800; font-size:10.5px; border:1px solid #fca5a5; white-space:nowrap;">🚪 લૉગ આઉટ</a>
        </div>
    </div>
    """

    # સ્તર ૩: ૧૮ બિલ્ટ-ઇન શીટ્સ નેવિગેશન બાર (સંપૂર્ણ ગુજરાતીમાં કોમ્પેક્ટ ગ્રીડ)
    all_sheet_defs = [
        ("SMART_TERMINAL", "૧. સ્માર્ટ કાઉન્ટર (F1-F8)"),
        ("LIVE_STOCK_VIEW", "૨. લાઈવ મોબાઈલ સ્ટોક"),
        ("UNIVERSAL_SEARCH", "૩. 360° યુનિવર્સલ સર્ચ"),
        ("APX_SALES_RAW", "૪. વેચાણ & DO રજીસ્ટર"),
        ("BUYBACK_STOCK", "૫. જૂના ફોન (બાય-બેક) સ્ટોક"),
        ("CUSTOMER_DUE", "૬. ગ્રાહક બાકી ઉધાર ખાતાવહી"),
        ("SUPPLIER_PURCHASE", "૭. વેપારી ખરીદી ખાતાવહી"),
        ("ACCESSORIES_LEDGER", "૮. એસેસરીઝ સ્ટોક & D-Cash"),
        ("RECHARGE_LAPU_VIEW", "૯. રિચાર્જ & LAPU બેલેન્સ"),
        ("DAILY_SUMMARY", "૧૦. દૈનિક રોજમેળ & નફો (P&L)"),
        ("GALLA_AUDIT_HISTORY", "૧૧. ૪-ગલ્લા કેશ ઓડિટ લોગ"),
        ("SALESMAN_360_MATRIX", "૧૨. સેલ્સમેન & બ્રાન્ડ 360°"),
        ("STAFF_ATTENDANCE_SHEET", "૧૩. સ્ટાફ સેલ્ફી હાજરી & પગાર"),
        ("BARCODE_AUDIT", "૧૪. ૪-કલર બારકોડ ઓડિટ"),
        ("OLD_STOCK_CLEARANCE", "૧૫. ૬૦+ દિવસ જૂનો સ્ટોક"),
        ("GST_SUMMARY_SHEET", "૧૬. GST રિટર્ન સમરી (B2B/B2C)"),
        ("SMART_DESK_GROWTH", "૧૭. માસિક & વાર્ષિક ગ્રોથ (YoY)"),
        ("GUJARATI_CONFIG", "૧૮. માસ્ટર સેટિંગ & ટેલી લેજર")
    ]
    active_sheets_list = list(shop_prof.get("active_sheets") or [k for k, _ in all_sheet_defs])
    if "SMART_TERMINAL" not in active_sheets_list:
        active_sheets_list.insert(0, "SMART_TERMINAL")
    visible_sheet_links = [
        f'<a href="/?sheet={s_id}" class="sh-btn {tab_cls(s_id)}">{s_name}</a>'
        for s_id, s_name in all_sheet_defs if s_id in active_sheets_list
    ]
    # ૧૮ શીટ્સ ૨ સુઘડ હરોળમાં (9 columns x 2 rows, compact 11px font)
    sheets_bar_html = f'<div class="sheets-bar-grid" style="display:grid; grid-template-columns:repeat(9, 1fr); gap:3px; background:#0f172a; padding:4px 6px;">' + "".join(visible_sheet_links) + '</div>'

    # સ્તર ૪: ૪ ગલ્લા + ગિફ્ટ + પેન્ડિંગ DO (૬ સમરી બોક્સ)
    active_gallas_list = list(shop_prof.get("active_gallas") or ["BANK_CASH", "ACC_DCASH", "RECHARGE", "EXTRA_CASH"])
    # 👑 ગલ્લા સિક્યુરિટી: સેલ્સમેન, પ્રોમોટર કે સ્ટાફને ગલ્લો ૪ (નફો/તિજોરી) ક્યારેય ન દેખાવો જોઈએ!
    if early_uid and early_uid not in ("SUPER_ADMIN", "manshvi", "devanshi"):
        try:
            m_conn = sqlite3.connect(part1_core.MASTER_DB_FILE, timeout=30.0)
            mc = m_conn.cursor()
            mc.execute("SELECT role_type, permissions_json FROM store_partners_users WHERE UPPER(user_id)=UPPER(?) AND UPPER(store_id)=UPPER(?) LIMIT 1", (early_uid, shop_prof.get("shop_id", "DEVANSHI")))
            u_p_check = mc.fetchone()
            m_conn.close()
            if u_p_check and str(u_p_check[0]).upper() not in ("OWNER", "PARTNER", "ACCOUNTANT"):
                if "EXTRA_CASH" in active_gallas_list:
                    active_gallas_list.remove("EXTRA_CASH")
                urole_u = str(u_p_check[0]).upper()
                if "RECHARGE" in urole_u:
                    active_gallas_list = [g for g in active_gallas_list if g == "RECHARGE"]
                elif "ACC" in urole_u:
                    active_gallas_list = [g for g in active_gallas_list if g == "ACC_DCASH"]
        except Exception:
            pass
    badge_cards = []
    if "BANK_CASH" in active_gallas_list:
        badge_cards.append(f'<a href="/?sheet=SMART_TERMINAL&mode=F8" class="b-card" style="text-decoration:none; display:block;" title="ક્લિક કરી ગલ્લા ૧ નો વિગતવાર હિસાબ ખોલો"><div class="b-title" style="background:#15803d;">૧. બેંક કેશ (ગલ્લો ૧)</div><div class="b-val" style="color:#15803d;">₹{bank_cash:,.0f}</div></a>')
    if "ACC_DCASH" in active_gallas_list:
        badge_cards.append(f'<a href="/?sheet=ACCESSORIES_LEDGER" class="b-card" style="text-decoration:none; display:block;" title="ક્લિક કરી એક્સેસરીઝ D-Cash લેજર ખોલો"><div class="b-title" style="background:#0369a1;">૨. એક્સેસરીઝ કેશ (ગલ્લો ૨)</div><div class="b-val" style="color:#0369a1;">₹{acc_dcash:,.0f}</div></a>')
    if "RECHARGE" in active_gallas_list:
        badge_cards.append(f'<a href="/?sheet=RECHARGE_LAPU_VIEW" class="b-card" style="text-decoration:none; display:block;" title="ક્લિક કરી રિચાર્જ & LAPU લેજર ખોલો"><div class="b-title" style="background:#6b21a8;">૩. રિચાર્જ કેશ (ગલ્લો ૩)</div><div class="b-val" style="color:#6b21a8;">₹{recharge_cash:,.0f}</div></a>')
    if "EXTRA_CASH" in active_gallas_list:
        badge_cards.append(f'<a href="/?sheet=DAILY_SUMMARY" class="b-card" style="text-decoration:none; display:block;" title="ક્લિક કરી ગલ્લા ૪ અને ચોખ્ખા નફાનું લેજર ખોલો"><div class="b-title" style="background:#b45309;">૪. એક્સ્ટ્રા કેશ (ગલ્લો ૪)</div><div class="b-val" style="color:#b45309;">₹{extra_cash:,.0f}</div></a>')
    _act_subs_set = set(shop_prof.get("active_subparts") or [])
    _act_cnts_set = set(shop_prof.get("active_counters") or [])
    if "F2" in _act_cnts_set or "F3_5" in _act_subs_set:
        badge_cards.append(f'<a href="/?sheet=DAILY_SUMMARY" class="b-card" style="text-decoration:none; display:block;" title="ક્લિક કરી આજની ગિફ્ટ અને રોજમેળ જુઓ"><div class="b-title" style="background:#c2410c;">ગિફ્ટ (આજે આપેલી)</div><div class="b-val" style="color:#c2410c;">₹{today_gift:,.0f}</div></a>')
    if "F2_3" in _act_subs_set or "APX_SALES_RAW" in active_sheets_list:
        badge_cards.append(f'<a href="/?sheet=APX_SALES_RAW" class="b-card" style="text-decoration:none; display:block;" title="ક્લિક કરી પેન્ડિંગ DO અને વેચાણ રજીસ્ટર ખોલો"><div class="b-title" style="background:#0f766e;">પેન્ડિંગ DO / બિલ</div><div class="b-val" style="color:#0f766e;">DO: {active_do_count} | બિલ: {pending_apx_count}</div></a>')
    if not badge_cards:
        badge_cards.append(f'<a href="/?sheet=DAILY_SUMMARY" class="b-card" style="text-decoration:none; display:block;"><div class="b-title" style="background:#15803d;">દુકાન સિલક</div><div class="b-val" style="color:#15803d;">₹{bank_cash+extra_cash:,.0f}</div></a>')

    franchise_btn3_html = (
        "<button class=\"act-btn\" style=\"background:#0d9488;\" onclick=\"openInlineQuickCreateModal('PARTY', '')\">➕ નવું લેજર / બ્રાન્ડ (Alt+C)</button>"
        if (st_mode == "RETAIL_STANDALONE" or "F2" not in _act_cnts_set) else
        "<button class=\"act-btn\" style=\"background:#d97706;\" onclick=\"document.getElementById('apx_import_file').click()\">📥 સેલ્સ બિલ ઇમ્પોર્ટ (Bulk)</button>"
    )
    franchise_btn4_html = (
        "<a href=\"/?sheet=SMART_TERMINAL&mode=F2\" class=\"act-btn\" style=\"background:#15803d;\">⚡ વેચાણ બિલ કાઉન્ટર (F2)</a>"
        if "F2" in _act_cnts_set else
        f"<a href=\"/?sheet=SMART_TERMINAL&mode={first_allowed_cnt}\" class=\"act-btn\" style=\"background:#15803d;\">⚡ મુખ્ય કાઉન્ટર ({first_allowed_cnt})</a>"
    )
    btn1_pur_html = "" if not ("F1_1" in _act_subs_set or "F1_2" in _act_subs_set) else "<button class=\"act-btn\" style=\"background:#0284c7;\" onclick=\"document.getElementById('stock_import_file').click()\">📥 ૧. ખરીદી બિલ AI ઇમ્પોર્ટ</button>"
    btn2_do_html = "" if "F2_3" not in _act_subs_set else "<button class=\"act-btn\" style=\"background:#0369a1;\" onclick=\"document.getElementById('do_import_file').click()\">📥 ૨. ફાઇનાન્સ DO ઇમ્પોર્ટ</button>"
    badges_grid_html = f'<div class="badges-grid" style="display:grid; grid-template-columns:repeat({max(1, len(badge_cards))}, 1fr); gap:5px; padding:6px 8px; background:#f1f5f9; border-bottom:1px solid #cbd5e1;">' + "".join(badge_cards) + '</div>'

    full_html = f"""<!DOCTYPE html>
    <html lang="gu">
    <head><meta charset="UTF-8"><meta name="viewport" id="erp_main_viewport" content="width=1366, initial-scale=0.28, minimum-scale=0.2, maximum-scale=3.0, user-scalable=yes"><link rel="manifest" href="/manifest.json"><title>{store_title} - MASTER ERP TERMINAL</title>
    <link href="https://fonts.googleapis.com/css2?family=Noto+Sans+Gujarati:wght@400;600;700;800&display=swap" rel="stylesheet">
    <style>
        body {{ font-family:'Noto Sans Gujarati','Segoe UI',sans-serif; background:#e2e8f0; margin:0; padding:8px; font-size:13px; color:#0f172a; }}
        .container {{ max-width:1420px; margin:auto; background:white; border-radius:8px; box-shadow:0 4px 14px rgba(0,0,0,0.12); overflow:hidden; border:1px solid #94a3b8; }}
        .main-header {{ background:#0f2043; color:white; text-align:center; padding:10px 12px 6px; font-size:19px; font-weight:800; letter-spacing:0.8px; }}
        .sub-bar {{ background:#0f2043; color:#38bdf8; text-align:center; padding:0 10px 8px; font-size:11.5px; font-weight:600; border-bottom:1px solid #334155; }}
        .sh-btn {{ padding:7px 4px; color:#cbd5e1; text-decoration:none; font-weight:700; font-size:11.5px; background:#1e293b; text-align:center; border-radius:4px; border:1px solid #334155; display:block; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }}
        .sh-btn:hover {{ background:#334155; color:white; }}
        .sh-btn.active {{ background:#0284c7 !important; color:white !important; border-color:#38bdf8 !important; box-shadow:0 0 6px rgba(56,189,248,0.5); }}
        .b-card {{ text-align:center; border-radius:4px; border:1px solid rgba(0,0,0,0.15); background:white; overflow:hidden; box-shadow:0 1px 3px rgba(0,0,0,0.06); }}
        .b-title {{ padding:4px 2px; color:white; font-weight:800; font-size:11.5px; }}
        .b-val {{ padding:5px 2px; background:white; font-size:14px; font-weight:800; }}
        .act-btn {{ border:none; padding:6px 4px; color:white; font-weight:700; border-radius:4px; cursor:pointer; text-align:center; text-decoration:none; display:block; font-size:11px; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; box-shadow:0 1px 2px rgba(0,0,0,0.1); }}
        .act-btn:hover {{ opacity:0.92; }}
        .f-btn {{ padding:8px 4px; color:white; font-weight:800; text-align:center; border-radius:4px; text-decoration:none; font-size:11.5px; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; display:block; }}
        .mode-banner {{ background:#e0f2fe; color:#0369a1; padding:8px 12px; font-weight:800; font-size:13px; border-left:4px solid #0284c7; margin:6px 8px; border-radius:0 4px 4px 0; display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:6px; }}
        .term-form {{ max-width:980px; margin:8px; background:#f8fafc; padding:12px; border:1px solid #cbd5e1; border-radius:6px; }}
        .f-row {{ display:flex; align-items:center; margin-bottom:5px; gap:6px; }}
        .f-row .lbl {{ width:235px; font-weight:700; color:#1e293b; text-align:right; padding-right:8px; font-size:12px; flex-shrink:0; }}
        .f-row input, .f-row select, .f-row textarea {{ flex:1; padding:6px 9px; border:1px solid #94a3b8; border-radius:4px; font-size:12.5px; background:white; color:#0f172a; outline:none; }}
        .f-row input:focus, .f-row select:focus {{ border-color:#0284c7; box-shadow:0 0 0 2px rgba(2,132,199,0.2); font-weight:600; }}
        .btn-wrap {{ margin-top:10px; margin-left:243px; }}
        .btn-save {{ background:#0f2043; color:white; border:none; padding:9px 20px; font-size:13.5px; font-weight:800; border-radius:4px; cursor:pointer; width:100%; box-shadow:0 2px 4px rgba(0,0,0,0.15); }}
        .grid-head {{ background:#0f2043; color:white; padding:7px 12px; font-weight:800; font-size:12.5px; margin-top:12px; display:flex; justify-content:space-between; align-items:center; }}
        table.live-grid {{ width:100%; border-collapse:collapse; font-size:11.5px; }}
        table.live-grid th {{ background:#1e293b; color:#f8fafc; border:1px solid #334155; padding:6px; font-weight:700; }}
        table.live-grid td {{ border:1px solid #e2e8f0; padding:5px 6px; text-align:center; color:#1e293b; }}
        table.live-grid tr:nth-child(even) {{ background:#f8fafc; }}
        /* ટેલી સ્ટાઇલ Accept? [Yes (Y) / No (N)] બોક્સ */
        .tally-accept-overlay {{ display:none; position:fixed; top:0; left:0; width:100%; height:100%; background:rgba(0,0,0,0.65); backdrop-filter:blur(3px); z-index:99999; align-items:center; justify-content:center; }}
        .tally-accept-card {{ width:370px; background:#0f172a; border:2px solid #38bdf8; border-radius:10px; box-shadow:0 15px 35px rgba(0,0,0,0.5); color:white; text-align:center; padding:20px 24px; }}

        /* 📱💻🖥️ ૧૦૦% યુનિવર્સલ રિસ્પોન્સિવ ડિઝાઇન (Mobile, Tablet, Laptop, Large Desktop) */
        @media (min-width: 1440px) {{
            .container {{ max-width: 98vw; }}
            .term-form {{ max-width: 1180px; }}
        }}
        @media (max-width: 1100px) {{
            .sheets-bar-grid {{ grid-template-columns: repeat(6, 1fr) !important; }}
            .action-8-grid {{ grid-template-columns: repeat(4, 1fr) !important; }}
            .badges-grid {{ grid-template-columns: repeat(3, 1fr) !important; }}
        }}
        @media (max-width: 768px) {{
            body {{ padding: 2px; font-size: 12px; }}
            .main-header {{ font-size: 15px; padding: 8px 6px 4px; }}
            .sub-bar {{ font-size: 10.5px; padding: 0 6px 6px; }}
            .sheets-bar-grid {{ grid-template-columns: repeat(3, 1fr) !important; gap: 3px !important; }}
            .badges-grid {{ grid-template-columns: repeat(2, 1fr) !important; }}
            .action-8-grid {{ grid-template-columns: repeat(2, 1fr) !important; }}
            .f-counters-grid {{ grid-template-columns: repeat(4, 1fr) !important; }}
            .f-row {{ flex-direction: column; align-items: stretch !important; gap: 3px; margin-bottom: 8px; }}
            .f-row .lbl {{ width: 100% !important; text-align: left !important; padding-right: 0 !important; font-size: 11.5px; }}
            .f-row input, .f-row select, .f-row textarea {{ width: 100% !important; max-width: 100% !important; box-sizing: border-box; }}
            .btn-wrap {{ margin-left: 0 !important; }}
            table.live-grid {{ display: block; overflow-x: auto; white-space: nowrap; -webkit-overflow-scrolling: touch; }}
        }}
    </style>
    </head>
    <body>
    <div class="container">
        {user_top_bar_html}
        <div class="main-header">{store_title} - MASTER ERP TERMINAL</div>
        <div class="sub-bar">{license_display} | <b style="color:#fde047;">📌 વર્ઝન: {STORE_CFG.get('ota_version_id', '2026.11.12.001') if not str(STORE_CFG.get('ota_version_id','')).startswith('v4') else '2026.11.12.001'}</b> | 90-Day FIFO બેકઅપ + લાઈવ ક્લાઉડ સિંક સક્રિય</div>
        {sheets_bar_html}
        {badges_grid_html}

        <!-- મલ્ટી-ફાઇલ AI ઇમ્પોર્ટ ફોર્મ્સ (૧૦-૨૦ ફાઇલો એકસાથે) -->
        <form id="f_stk_imp" action="/import-purchase-invoice" method="post" enctype="multipart/form-data" style="display:none;">
            <input type="file" id="stock_import_file" name="files" multiple onchange="document.getElementById('f_stk_imp').submit()">
        </form>
        <form id="f_do_imp" action="/import-do-pdf" method="post" enctype="multipart/form-data" style="display:none;">
            <input type="file" id="do_import_file" name="files" multiple onchange="document.getElementById('f_do_imp').submit()">
        </form>
        <form id="f_apx_imp" action="/import-apx-sales" method="post" enctype="multipart/form-data" style="display:none;">
            <input type="file" id="apx_import_file" name="files" multiple onchange="document.getElementById('f_apx_imp').submit()">
        </form>

        <!-- સ્તર ૫: ક્રમબદ્ધ એક્શન અને AI સ્માર્ટ ઇમ્પોર્ટ ટૂલબાર બટનો (દુકાનના સક્રિય ઓપ્શન મુજબ ઓટો-ફિલ્ટર) -->
        <div class="action-8-grid" style="display:grid; grid-template-columns:repeat(auto-fit, minmax(145px, 1fr)); gap:4px; padding:6px 8px; background:#e2e8f0; border-bottom:1px solid #cbd5e1;">
            {btn1_pur_html}
            {btn2_do_html}
            {franchise_btn3_html}
            {franchise_btn4_html}
            <button class="act-btn" style="background:#7c3aed;" onclick="openAiAssistantModal()">🤖 વાઈફાઈ લાઈવ AI & સ્કીમ</button>
            <a href="/mobile-scan" target="_blank" class="act-btn" style="background:#059669;">📷 મોબાઇલ કેમેરા સ્કેન</a>
            <a href="/eod-summary-report" class="act-btn" style="background:#2563eb;">💬 રોજમેળ & WhatsApp PDF</a>
            <a href="/undo-last" class="act-btn" style="background:#dc2626;" onclick="return confirm('શું તમે છેલ્લો વ્યવહાર રદ (Undo) કરવા માંગો છો? (તેની રોકડ અને સ્ટોક અસર પણ આપોઆપ રિવર્સ થઈ જશે!)')">↩️ છેલ્લો વ્યવહાર રદ (Undo)</a>
        </div>

        {inter_galla_global_alert_html if (is_mgmt_role and sheet == 'SMART_TERMINAL' and mode in ('F2', 'F1', '') and not request.cookies.get('dismiss_vendor_alert_' + str(datetime.date.today()))) else ''}
        {msg_html}
        {sheet_content}
    </div>

    <!-- ⚠️ ટેલી સ્ટાઇલ [ Accept? Yes (Y) / No (N) ] પોપ-અપ બોક્સ (નિયમ ૦.૧) -->
    <div class="tally-accept-overlay" id="tally_accept_modal">
        <div class="tally-accept-card">
            <div style="font-size:18px; font-weight:800; color:#fde047; margin-bottom:8px;">Accept ?</div>
            <div style="font-size:12.5px; color:#cbd5e1; margin-bottom:16px;" id="tally_accept_desc">
                શું તમે આ કાઉન્ટર વ્યવહાર ખાતાવહીમાં સેવ કરવા માંગો છો?
            </div>
            <div style="display:flex; gap:14px; justify-content:center;">
                <button type="button" id="btn_tally_yes" onclick="confirmTallyAccept(true)" style="padding:8px 24px; font-size:13.5px; font-weight:800; border-radius:6px; border:none; background:#16a34a; color:white; cursor:pointer;">Yes (Y / Enter)</button>
                <button type="button" id="btn_tally_no" onclick="confirmTallyAccept(false)" style="padding:8px 24px; font-size:13.5px; font-weight:800; border-radius:6px; border:none; background:#dc2626; color:white; cursor:pointer;">No (N / Esc)</button>
            </div>
            <div style="font-size:11px; color:#94a3b8; margin-top:10px;">કીબોર્ડ શોર્ટકટ: <b>Y</b> અથવા <b>Enter</b> = સેવ | <b>N</b> અથવા <b>Esc</b> = રદ કરી પાછા ફોર્મમાં</div>
        </div>
    </div>

    <!-- ⚙️ ખાના કસ્ટમાઇઝેશન મોડલ (દુકાનદારે બંધ કરેલા ખાનાં ઓટો-સ્કિપ થશે) -->
    <div class="tally-accept-overlay" id="field_config_modal">
        <div style="width:95%; max-width:560px; background:white; border:2px solid #0f2043; border-radius:10px; overflow:hidden; color:#0f172a;">
            <div style="background:#0f2043; color:white; padding:10px 16px; font-weight:800; display:flex; justify-content:space-between; align-items:center;">
                <span>⚙️ દુકાન જરૂરિયાત મુજબ ખાના કસ્ટમાઇઝ કરો (Auto-Skip)</span>
                <button type="button" onclick="closeFieldConfigModal()" style="background:none; border:none; color:white; font-size:16px; cursor:pointer;">✖</button>
            </div>
            <div style="padding:16px; font-size:12px;">
                <p style="margin-bottom:10px; color:#475569;">જે ખાનાં અન-ટીક કરશો તે ફોર્મમાં હાઇડ થઈ જશે અને Enter આપતાં ઓટો-સ્કિપ થશે:</p>
                <div id="dynamic_field_toggles" style="display:grid; grid-template-columns:1fr 1fr; gap:8px; max-height:320px; overflow-y:auto;"></div>
                <div style="margin-top:14px; text-align:right;">
                    <button type="button" onclick="closeFieldConfigModal()" style="background:#0284c7; color:white; border:none; padding:8px 18px; border-radius:4px; font-weight:bold; cursor:pointer;">[ સેટિંગ્સ સાચવો ]</button>
                </div>
            </div>
        </div>
    </div>


    <!-- 🤖 બિલ્ટ-ઇન દેવાંશી AI આસિસ્ટન્ટ & સ્માર્ટ લર્નિંગ બલ્ક રીડર (એન્ટી-કોપી સિક્યુરિટી ગાર્ડરેલ્સ સાથે) -->
    <div class="tally-accept-overlay" id="ai_assistant_modal">
        <div style="width:95%; max-width:650px; background:white; border:2px solid #7c3aed; border-radius:10px; overflow:hidden; color:#0f172a; box-shadow:0 20px 40px rgba(0,0,0,0.5);">
            <div style="background:#4c1d95; color:white; padding:10px 16px; font-weight:800; display:flex; justify-content:space-between; align-items:center;">
                <span>🤖 દેવાંશી AI સ્માર્ટ આસિસ્ટન્ટ & પ્રાઇસ-ડ્રોપ / સ્કીમ / બલ્ક PDF રીડર</span>
                <button type="button" onclick="document.getElementById('ai_assistant_modal').style.display='none'" style="background:none; border:none; color:white; font-size:16px; cursor:pointer;">✖</button>
            </div>
            <div style="padding:14px; font-size:12.5px;">
                <div style="background:#f3e8ff; border:1px solid #c4b5fd; padding:8px 12px; border-radius:6px; margin-bottom:10px; color:#5b21b6; font-weight:bold;">
                    🛡️ સિક્યુરિટી ગાર્ડરેલ સક્રિય: આ AI માત્ર આપની દુકાનના બિલ, DO, પ્રાઇસ-ડ્રોપ, સ્કીમ લેટર અને હિસાબમાં મદદ કરશે. સોફ્ટવેરનો સોર્સ કોડ, ડેટાબેઝ સ્ટ્રક્ચર કે અન્ય સ્ટોરની માહિતી સંપૂર્ણ ગોપનીય અને લોક છે.
                </div>
                <form action="/ai-smart-scheme-pricedrop-upload" method="post" enctype="multipart/form-data" style="background:#f8fafc; border:1px solid #cbd5e1; padding:10px; border-radius:6px; margin-bottom:12px;">
                    <div style="font-weight:bold; color:#0f2043; margin-bottom:6px;">📄 ૧. કંપની સ્કીમ લેટર / પ્રાઇસ-ડ્રોપ / પ્રાઇસ-હાઇક / GST સર્ક્યુલર અપલોડ કરો (તારીખ-લોક સાથે):</div>
                    <div style="display:grid; grid-template-columns:1fr 1fr 1fr; gap:6px; margin-bottom:6px;">
                        <select name="doc_type" style="padding:5px; font-weight:bold;">
                            <option value="PURCHASE_INVOICE">🧾 ૧. વેપારી ખરીદી બિલ (Purchase Invoice)</option>
                            <option value="FINANCE_DO">🏦 ૨. ફાઇનાન્સ ડિલિવરી ઓર્ડર (Finance DO)</option>
                            <option value="PRICE_DROP">📉 ૩. ભાવ-ઘટાડો પ્રોટેક્શન (Price-Drop Letter)</option>
                            <option value="COMPANY_SCHEME">🎁 ૪. વેપારી સ્કીમ & ક્રેડિટ નોટ (Scheme / CN)</option>
                            <option value="BANK_UPI_SLIP">💳 ૫. બેંક સ્લિપ & UPI પેમેન્ટ સ્ક્રીનશોટ (UTR/F4)</option>
                            <option value="CUSTOMER_KYC">🪪 ૬. ગ્રાહક KYC (આધાર કાર્ડ / પાન કાર્ડ)</option>
                            <option value="BUYBACK_DOC">📱 ૭. જૂના ફોન બાયબેક બિલ / આઈડી (F5 Buy-back)</option>
                            <option value="PRICE_HIKE">📈 ૮. પ્રાઇસ-હાઇક (Price Hike)</option>
                            <option value="GST_RATE_UPDATE">⚖️ ૯. ઓટો-GST રેટ અપડેટ (Date-Locked)</option>
                        </select>
                        <input type="date" name="valid_from" value="{today_str}" title="કઈ તારીખથી લાગુ (Effective From)" style="padding:5px;">
                        <input type="date" name="valid_to" value="{today_str}" title="કઈ તારીખ સુધી (Valid To)" style="padding:5px;">
                    </div>
                    <div style="display:flex; gap:6px;">
                        <input type="file" name="files" multiple required style="flex:1; padding:4px; background:white; border:1px solid #94a3b8; border-radius:4px;">
                        <button type="submit" style="background:#16a34a; color:white; border:none; padding:6px 14px; border-radius:4px; font-weight:bold; cursor:pointer;">📥 AI રીડ & સેવ કરો</button>
                    </div>
                </form>
                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:6px; flex-wrap:wrap; gap:4px;">
                    <div style="font-weight:bold; color:#0f2043;">💬 ૨. દેવાંશી 360° સ્માર્ટ મુનીમજી & વાઈફાઈ લાઈવ AI (બોલીને 🎤 કે લખીને પૂછો):</div>
                    <span style="background:#dcfce7; color:#15803d; border:1px solid #16a34a; padding:2px 8px; border-radius:4px; font-size:11px; font-weight:800;">📶 Wi-Fi Live AI + 360° DB સક્રિય</span>
                </div>
                <div style="display:flex; gap:5px; flex-wrap:wrap; margin-bottom:8px;">
                    <button type="button" onclick="quickAskMunimji('Vivo નું આખું લેજર અને સ્ટોક બતાવ')" style="background:#e0f2fe; color:#0369a1; border:1px solid #7dd3fc; padding:4px 8px; border-radius:4px; font-size:11px; font-weight:bold; cursor:pointer;">📦 Vivo નું આખું લેજર</button>
                    <button type="button" onclick="quickAskMunimji('આ મહિનામાં રિપેરિંગ કેટલું થયું અને કેટલો નફો થયો?')" style="background:#fef3c7; color:#92400e; border:1px solid #fde047; padding:4px 8px; border-radius:4px; font-size:11px; font-weight:bold; cursor:pointer;">🛠️ આ મહિનાનું રિપેરિંગ</button>
                    <button type="button" onclick="quickAskMunimji('આજનો ૪ ગલ્લાનો હિસાબ અને ચોખ્ખો નફો કેટલો છે?')" style="background:#dcfce7; color:#166534; border:1px solid #86efac; padding:4px 8px; border-radius:4px; font-size:11px; font-weight:bold; cursor:pointer;">💰 ૪-ગલ્લા & ચોખ્ખો નફો</button>
                    <button type="button" onclick="quickAskMunimji('કયા ગ્રાહક પાસે કેટલા ઉધાર બાકી છે?')" style="background:#fee2e2; color:#991b1b; border:1px solid #fca5a5; padding:4px 8px; border-radius:4px; font-size:11px; font-weight:bold; cursor:pointer;">⚠️ ગ્રાહક બાકી ઉધાર</button>
                    <button type="button" onclick="quickAskMunimji('કયા વેપારી (Supplier) ને કેટલા રૂપિયા ચૂકવવાના બાકી છે?')" style="background:#f3e8ff; color:#6b21a8; border:1px solid #d8b4fe; padding:4px 8px; border-radius:4px; font-size:11px; font-weight:bold; cursor:pointer;">🧾 વેપારી બાકી ખાતાવહી</button>
                </div>
                <div style="display:flex; gap:6px; margin-bottom:8px;">
                    <input type="text" id="ai_chat_input" onkeydown="handleAiChatKeydown(event)" placeholder="અહીં પ્રશ્ન કે ૧૫-અંક IMEI લખો (દા.ત. Vivo નું લેજર બતાવ / આ મહિનાનું રિપેરિંગ / GST નિયમ)..." style="flex:1; padding:8px; border:2px solid #7c3aed; border-radius:4px; font-weight:bold;">
                    <button type="button" onclick="startAiVoiceMic()" style="background:#059669; color:white; border:none; padding:7px 12px; border-radius:4px; font-weight:bold; cursor:pointer;" title="બોલીને પૂછો">🎤 બોલો</button>
                    <button type="button" onclick="askDevanshiAi()" style="background:#7c3aed; color:white; border:none; padding:7px 16px; border-radius:4px; font-weight:bold; cursor:pointer;">પૂછો (Ask AI)</button>
                </div>
                <div id="ai_chat_response" style="background:#f1f5f9; border:1px solid #cbd5e1; padding:10px; border-radius:6px; min-height:60px; max-height:240px; overflow-y:auto; font-weight:bold; color:#1e293b; white-space:pre-wrap; line-height:1.45;">નમસ્તે! હું દેવાંશી 360° વાઈફાઈ લાઈવ AI મુનીમજી છું. આપ કોઈપણ બ્રાન્ડનું લેજર ('Vivo નું આખું લેજર'), ૧૫-અંક IMEI કુંડળી, ચાલુ મહિનાનું રિપેરિંગ, ૪-ગલ્લા સિલક કે વેપારી/ગ્રાહક બાકી વિશે પૂછી શકો છો.</div>
            </div>
        </div>
    </div>


    <!-- ➕ યુનિવર્સલ ઇનલાઇન ક્વિક-ક્રિએટ પોપ-અપ (Tally Alt+C Style - પેજ રીલોડ વગર વેપારી, ગ્રાહક, બ્રાન્ડ, સ્ટાફ, કેટેગરી, હોદ્દો બનાવો) -->
    
<!-- 🛒 ઓનલાઈન MOP & બેંક ઓફર કેલ્ક્યુલેટર મોડલ (Amazon / Flipkart / Brand e-Store) -->
<div class="tally-accept-overlay" id="online_price_spy_modal" style="display:none; z-index:99999;">
    <div style="width:96%; max-width:820px; background:white; border:2px solid #ea580c; border-radius:10px; box-shadow:0 12px 36px rgba(0,0,0,0.35); overflow:hidden; font-family:sans-serif;">
        <div style="background:linear-gradient(135deg, #ea580c 0%, #c2410c 100%); color:white; padding:12px 18px; font-weight:800; display:flex; justify-content:space-between; align-items:center;">
            <span style="font-size:14.5px;">🛒 Amazon / Flipkart / Brand e-Store લાઈવ MOP ટ્રેકર & બેંક ઓફર કેલ્ક્યુલેટર</span>
            <button type="button" onclick="closeOnlinePriceSpyModal()" style="background:rgba(255,255,255,0.2); border:none; color:white; font-size:16px; font-weight:bold; cursor:pointer; width:30px; height:30px; border-radius:50%;">✕</button>
        </div>
        <div style="padding:16px; max-height:85vh; overflow-y:auto;">
            <!-- Search & Quick Selection -->
            <div style="margin-bottom:12px;">
                <div style="font-weight:bold; font-size:12px; color:#334155; margin-bottom:4px;">૧. મોબાઇલ મોડેલ સર્ચ કરો અથવા પસંદ કરો:</div>
                <div style="display:flex; gap:6px; margin-bottom:8px;">
                    <input type="text" id="spy_model_name" oninput="calcSpyOffers()" placeholder="દા.ત. Vivo Y58 5G, Vivo V40, Samsung A15 5G, iPhone 15..." style="flex:1; padding:8px 12px; border:2px solid #0284c7; border-radius:6px; font-weight:bold; font-size:13px;">
                    <button type="button" onclick="calcSpyOffers()" style="background:#0284c7; color:white; border:none; padding:8px 14px; border-radius:6px; font-weight:bold; cursor:pointer;">🔍 તપાસો</button>
                </div>
                <div style="display:flex; gap:5px; flex-wrap:wrap;">
                    <span style="font-size:11px; color:#64748b; font-weight:bold; align-self:center;">ટોપ મોડેલ્સ:</span>
                    <button type="button" onclick="selectSpyModelPill('Vivo Y58 5G (8/128)', 15499)" style="background:#f1f5f9; border:1px solid #cbd5e1; padding:3px 8px; border-radius:4px; font-size:11px; cursor:pointer;">Vivo Y58 (₹15,499)</button>
                    <button type="button" onclick="selectSpyModelPill('Vivo V40 5G (8/128)', 34999)" style="background:#f1f5f9; border:1px solid #cbd5e1; padding:3px 8px; border-radius:4px; font-size:11px; cursor:pointer;">Vivo V40 (₹34,999)</button>
                    <button type="button" onclick="selectSpyModelPill('Samsung Galaxy A15 5G', 16499)" style="background:#f1f5f9; border:1px solid #cbd5e1; padding:3px 8px; border-radius:4px; font-size:11px; cursor:pointer;">Samsung A15 (₹16,499)</button>
                    <button type="button" onclick="selectSpyModelPill('iPhone 15 128GB', 69999)" style="background:#f1f5f9; border:1px solid #cbd5e1; padding:3px 8px; border-radius:4px; font-size:11px; cursor:pointer;">iPhone 15 (₹69,999)</button>
                    <button type="button" onclick="selectSpyModelPill('OnePlus Nord CE4', 24999)" style="background:#f1f5f9; border:1px solid #cbd5e1; padding:3px 8px; border-radius:4px; font-size:11px; cursor:pointer;">OnePlus CE4 (₹24,999)</button>
                    <button type="button" onclick="selectSpyModelPill('Realme 12 Pro 5G', 21999)" style="background:#f1f5f9; border:1px solid #cbd5e1; padding:3px 8px; border-radius:4px; font-size:11px; cursor:pointer;">Realme 12 Pro (₹21,999)</button>
                </div>
            </div>

            <!-- 4-Pillar Live Price Comparison Grid -->
            <div style="display:grid; grid-template-columns:repeat(auto-fit, minmax(160px, 1fr)); gap:10px; margin-bottom:14px;">
                <!-- Card 1: Our Offline Store -->
                <div style="background:#f0fdf4; border:2px solid #16a34a; border-radius:8px; padding:10px; text-align:center;">
                    <div style="font-size:11px; font-weight:800; color:#15803d;">🏪 આપણી ઓફલાઇન દુકાન</div>
                    <div style="font-size:20px; font-weight:900; color:#166534; margin:4px 0;">₹<span id="spy_store_mop">15,499</span></div>
                    <div style="font-size:11px; color:#15803d; font-weight:bold;">🎁 ₹798 ની ગિફ્ટ્સ ફ્રી!</div>
                    <div style="font-size:10px; color:#475569; margin-top:2px;">11D ગ્લાસ + સ્મોક કવર + ડેટા ટ્રાન્સફર</div>
                </div>

                <!-- Card 2: Amazon Live -->
                <div style="background:#fff7ed; border:2px solid #ea580c; border-radius:8px; padding:10px; text-align:center;">
                    <div style="font-size:11px; font-weight:800; color:#c2410c;">🛒 Amazon લાઈવ MOP</div>
                    <div style="font-size:20px; font-weight:900; color:#9a3412; margin:4px 0;">₹<span id="spy_amz_mop">15,999</span></div>
                    <div style="font-size:11px; color:#ea580c;" id="spy_amz_offer">MRP ₹19,999 (20% Off)</div>
                    <a id="spy_amz_link" href="https://www.amazon.in/s?k=Vivo+Y58+5G" target="_blank" style="display:inline-block; margin-top:4px; font-size:11px; color:#0284c7; text-decoration:underline; font-weight:bold;">Amazon પર જુઓ ↗</a>
                </div>

                <!-- Card 3: Flipkart Live -->
                <div style="background:#eff6ff; border:2px solid #2563eb; border-radius:8px; padding:10px; text-align:center;">
                    <div style="font-size:11px; font-weight:800; color:#1d4ed8;">⚡ Flipkart લાઈવ MOP</div>
                    <div style="font-size:20px; font-weight:900; color:#1e40af; margin:4px 0;">₹<span id="spy_fk_mop">15,999</span></div>
                    <div style="font-size:11px; color:#2563eb;" id="spy_fk_offer">ઓનલાઈન સેલ ઓફર</div>
                    <a id="spy_fk_link" href="https://www.flipkart.com/search?q=Vivo+Y58+5G" target="_blank" style="display:inline-block; margin-top:4px; font-size:11px; color:#0284c7; text-decoration:underline; font-weight:bold;">Flipkart પર જુઓ ↗</a>
                </div>

                <!-- Card 4: Brand Official e-Store -->
                <div style="background:#faf5ff; border:2px solid #9333ea; border-radius:8px; padding:10px; text-align:center;">
                    <div style="font-size:11px; font-weight:800; color:#7e22ce;">🏢 બ્રાન્ડ e-Store (Official)</div>
                    <div style="font-size:20px; font-weight:900; color:#6b21a8; margin:4px 0;">₹<span id="spy_brand_mop">15,999</span></div>
                    <div style="font-size:11px; color:#7e22ce;" id="spy_brand_name">Vivo Official Store</div>
                    <a id="spy_brand_link" href="https://www.google.com/search?q=Vivo+official+store+price" target="_blank" style="display:inline-block; margin-top:4px; font-size:11px; color:#0284c7; text-decoration:underline; font-weight:bold;">ઓફિશિયલ સાઇટ ↗</a>
                </div>
            </div>

            <!-- Instant Bank Credit Card Discount Calculator -->
            <div style="background:#f8fafc; border:1.5px solid #cbd5e1; border-radius:8px; padding:12px; margin-bottom:12px;">
                <div style="font-weight:800; font-size:12.5px; color:#0f172a; margin-bottom:6px; display:flex; justify-content:space-between;">
                    <span>💳 બેંક ક્રેડિટ કાર્ડ ઇન્સ્ટન્ટ કેશબેક કેલ્ક્યુલેટર:</span>
                    <span style="color:#ea580c; font-size:11.5px;">લાઈવ ઓફર સરખામણી</span>
                </div>
                <div style="display:flex; gap:8px; align-items:center; flex-wrap:wrap; margin-bottom:8px;">
                    <select id="spy_bank_sel" onchange="calcSpyOffers()" style="flex:1; min-width:220px; padding:7px 10px; border:2px solid #0284c7; border-radius:6px; font-weight:bold; font-size:12.5px;">
                        <option value="NONE">૧. કોઈ કાર્ડ ઓફર નથી (સામાન્ય રોકડ / UPI)</option>
                        <option value="HDFC_2000">૨. HDFC Bank CC: Flat ₹2,000 Instant Off</option>
                        <option value="ICICI_1500">૩. ICICI Bank CC: Flat ₹1,500 Instant Off</option>
                        <option value="SBI_1000">૪. SBI Card CC: Flat ₹1,000 Instant Discount</option>
                        <option value="AXIS_1500">૫. Axis Bank CC: Flat ₹1,500 Instant Cashback</option>
                        <option value="KOTAK_1000">૬. Kotak / Federal CC: Flat ₹1,000 Instant Off</option>
                    </select>
                </div>
                <div style="display:flex; justify-content:space-around; background:white; border:1px solid #e2e8f0; border-radius:6px; padding:8px;">
                    <div style="text-align:center;">
                        <div style="font-size:11px; color:#64748b;">ઓનલાઈન નેટ ઇફેક્ટિવ ભાવ:</div>
                        <div style="font-size:16px; font-weight:800; color:#ea580c;">₹<span id="spy_net_online">15,999</span></div>
                    </div>
                    <div style="border-left:1px solid #cbd5e1;"></div>
                    <div style="text-align:center;">
                        <div style="font-size:11px; color:#64748b;">આપણો કાઉન્ટર ઑફર ભાવ:</div>
                        <div style="font-size:16px; font-weight:900; color:#15803d;">₹<span id="spy_net_offline">15,499</span></div>
                    </div>
                </div>
            </div>

            <!-- Gujarati Counter Sales Pitch -->
            <div style="margin-bottom:14px;">
                <div style="font-weight:800; font-size:12px; color:#854d0e; margin-bottom:4px;">🗣️ ગ્રાહકને ઓનલાઈનથી રોકી ૧૦ મિનિટમાં ડીલ ક્લોઝ કરવા માટે તૈયાર ગુજરાતી સેલ્સ પિચ:</div>
                <div id="spy_pitch_box" style="background:#fefce8; border:1.5px solid #ca8a04; border-radius:6px; padding:10px 14px; font-size:12.5px; line-height:1.6; color:#854d0e;">
                    "સાહેબ, ઓનલાઈન કરતાં આપણી પાસે ₹૨૦૦ સસ્તો પડશે અને સાથે ₹૭૯૮ ના ઓરિજિનલ 11D ટેમ્પર્ડ ગ્લાસ + સ્મોક કવર તદ્દન ફ્રી ચડાવી આપીશું! સૌથી મોટો ફાયદો એ કે ઓનલાઇનમાં પાર્સલમાં ખોટો કે તૂટેલો ફોન નીકળે તો ૧૫ દિવસ કસ્ટમર કેરમાં દોડવું પડે, જ્યારે અહીં તમારી નજર સામે સીલ પેક બોક્સ ખુલે છે, જૂના ફોનનો તમામ ડેટા ૧૦ મિનિટમાં ફ્રી શિફ્ટ કરી આપીએ છીએ અને ૧ વર્ષની હાથોહાથ સર્વિસ વોરંટી આપણી દુકાન તરફથી મળે છે!"
                </div>
            </div>

            <!-- Action Buttons -->
            <div style="display:flex; justify-content:flex-end; gap:8px;">
                <button type="button" onclick="applySpyPriceToBilling()" style="background:linear-gradient(135deg, #15803d, #166534); color:white; border:none; padding:10px 20px; border-radius:6px; font-weight:bold; font-size:13px; cursor:pointer; box-shadow:0 2px 6px rgba(22,101,52,0.3);">✅ આ MOP બિલમાં ભરો (Apply to Bill)</button>
                <button type="button" onclick="closeOnlinePriceSpyModal()" style="background:#64748b; color:white; border:none; padding:10px 18px; border-radius:6px; font-weight:bold; font-size:13px; cursor:pointer;">બંધ કરો (Close)</button>
            </div>
        </div>
    </div>
</div>

<!-- 🧠 AI સેલ્સ કોચ ક્લોઝિંગ પિચ મોડલ -->
<div class="tally-accept-overlay" id="salesman_closing_pitch_modal" style="display:none; z-index:99999;">
    <div style="width:96%; max-width:680px; background:white; border:2px solid #0284c7; border-radius:10px; box-shadow:0 12px 36px rgba(0,0,0,0.35); overflow:hidden; font-family:sans-serif;">
        <div style="background:linear-gradient(135deg, #0284c7 0%, #0369a1 100%); color:white; padding:12px 18px; font-weight:800; display:flex; justify-content:space-between; align-items:center;">
            <span style="font-size:14.5px;">🧠 AI સેલ્સ કોચ: ગ્રાહકને ઓનલાઈનથી રોકી ૧૦ મિનિટમાં ડીલ ક્લોઝ કરવાની ગુજરાતી પિચ</span>
            <button type="button" onclick="closeSalesmanClosingPitchModal()" style="background:rgba(255,255,255,0.2); border:none; color:white; font-size:16px; font-weight:bold; cursor:pointer; width:30px; height:30px; border-radius:50%;">✕</button>
        </div>
        <div style="padding:16px; max-height:80vh; overflow-y:auto; font-size:13px; line-height:1.6;">
            <div style="background:#f0f9ff; border:1px solid #bae6fd; border-radius:6px; padding:10px 14px; margin-bottom:10px;">
                <b style="color:#0369a1;">૧. ઓનલાઈન સરખામણી સામે ડિફેન્સ પિચ:</b>
                <p style="margin:4px 0 0; color:#0f172a;">"સાહેબ, ઓનલાઈનમાં ડિલિવરીમાં ૩ દિવસ લાગે છે અને જો બોક્સમાં સ્ક્રેચ કે ખામી નીકળી તો રિટર્ન માટે કસ્ટમર કેરમાં ૧૫ દિવસ ધક્કા ખાવા પડે છે. જ્યારે અહીં તમે જાતે બોક્સની સીલ ખોલો છો, જૂના ફોનનો તમામ ડેટા, WhatsApp ચેટ્સ અને ફોટા અમે ફ્રીમાં ટ્રાન્સફર કરી આપીએ છીએ અને ૧ વર્ષ સુધી ફોનમાં કંઈ પણ થાય તો દુકાન પર સીધો અમારો સ્ટાફ હાજર છે!"</p>
            </div>
            <div style="background:#fefce8; border:1px solid #fef08a; border-radius:6px; padding:10px 14px; margin-bottom:10px;">
                <b style="color:#a16207;">૨. ભાવ તફાવત અને ફ્રી ગિફ્ટ્સ વેલ્યુ પિચ:</b>
                <p style="margin:4px 0 0; color:#0f172a;">"સાહેબ, ઓનલાઈનમાં તમને ફક્ત ફોન મળશે, જ્યારે અમે તમને સાથે ₹૪૯૯ નો 11D ઓરિજિનલ ટેમ્પર્ડ ગ્લાસ ફ્રી લગાવી આપીએ છીએ + ₹૨૯૯ નું બ્રાન્ડેડ કવર ફ્રી આપીએ છીએ. એટલે કે તમને સીધો ₹૮૦૦ નો રોકડિયો ફાયદો આપણી દુકાન પર જ મળી રહ્યો છે!"</p>
            </div>
            <div style="background:#f0fdf4; border:1px solid #bbf7d0; border-radius:6px; padding:10px 14px; margin-bottom:12px;">
                <b style="color:#15803d;">૩. ફાઇનાન્સ 0% વ્યાજ / સરળ હપ્તા પિચ:</b>
                <p style="margin:4px 0 0; color:#0f172a;">"જો ક્રેડિટ કાર્ડ ન હોય તો પણ ચિંતા નથી! અમે બજાજ/TVS/IDFC ફાઇનાન્સમાં ફક્ત ₹0 અથવા ઓછા ડાઉન પેમેન્ટમાં ૦% વ્યાજે ફોન હાથમાં આપી દઈએ છીએ. ૧૦ મિનિટમાં ફક્ત આધાર કાર્ડ પર લોન મંજૂર!"</p>
            </div>
            <div style="text-align:right;">
                <button type="button" onclick="closeSalesmanClosingPitchModal()" style="background:#0284c7; color:white; border:none; padding:8px 18px; border-radius:6px; font-weight:bold; cursor:pointer;">સમજાઈ ગયું (Close)</button>
            </div>
        </div>
    </div>
</div>

<div class="tally-accept-overlay" id="inline_quick_create_modal">
        <div style="width:95%; max-width:520px; background:white; border:2px solid #15803d; border-radius:10px; overflow:hidden; color:#0f172a; box-shadow:0 20px 40px rgba(0,0,0,0.6);">
            <div style="background:#15803d; color:white; padding:10px 16px; font-weight:800; display:flex; justify-content:space-between; align-items:center;">
                <span id="iqc_title">➕ ચાલુ કાઉન્ટરે નવું લેજર / માસ્ટર ઉમેરો (Alt+C)</span>
                <button type="button" onclick="document.getElementById('inline_quick_create_modal').style.display='none'" style="background:none; border:none; color:white; font-size:16px; cursor:pointer;">✖</button>
            </div>
            <div style="padding:14px; font-size:12.5px;">
                <input type="hidden" id="iqc_target_select_id" value="">
                <div class="f-row">
                    <div class="lbl" style="width:150px;">૧. શું બનાવવું છે?:</div>
                    <select id="iqc_entity_type" onchange="renderIqcFields()" style="font-weight:bold; color:#0f2043;">
                        <option value="PARTY">૧. નવો વેપારી / સપ્લાયર (Supplier Ledger)</option>
                        <option value="CUSTOMER">૨. નવો ગ્રાહક / ઉધાર ખાતું (Customer Ledger)</option>
                        <option value="STAFF">૩. નવો સેલ્સમેન / સ્ટાફ / કારીગર (Staff)</option>
                        <option value="BRAND">૪. નવી મોબાઈલ / પ્રોડક્ટ બ્રાન્ડ (Brand)</option>
                        <option value="CATEGORY">૫. નવી અન્ડર-કેટેગરી (Under Category)</option>
                        <option value="DESIGNATION">૬. નવો સ્ટાફ હોદ્દો (Designation)</option>
                        <option value="EXPENSE_HEAD">૭. નવું ખર્ચ ખાતું (Expense Head)</option>
                        <option value="BANK">૮. નવું બેંક ખાતું (Bank Account)</option>
                    </select>
                </div>
                <div class="f-row">
                    <div class="lbl" style="width:150px;">૨. નામ / શીર્ષક *:</div>
                    <input type="text" id="iqc_name" placeholder="અહીં નામ લખો..." required>
                </div>
                <div class="f-row" id="iqc_sub_row">
                    <div class="lbl" style="width:150px;" id="iqc_sub_lbl">૩. અન્ડર-કેટેગરી / હોદ્દો:</div>
                    <input type="text" id="iqc_sub_val" list="iqc_sub_datalist" placeholder="કેટેગરી પસંદ કરો અથવા નવી લખો (આપોઆપ બની જશે)..." style="flex:1;">
                    <datalist id="iqc_sub_datalist">
                        <option value="મોબાઈલ હેન્ડસેટ">
                        <option value="મોબાઈલ એક્સેસરીઝ">
                        <option value="લેપટોપ / TV / AC">
                        <option value="રીચાર્જ ડિસ્ટ્રિબ્યુટર">
                        <option value="સેલ્સમેન">
                        <option value="એકાઉન્ટન્ટ">
                        <option value="રિપેરિંગ કારીગર">
                    </datalist>
                </div>
                <div class="f-row" id="iqc_mob_row">
                    <div class="lbl" style="width:150px;">૪. ૧૦-અંક મોબાઈલ:</div>
                    <input type="text" id="iqc_mobile" maxlength="10" placeholder="૧૦-અંક મોબાઈલ નંબર">
                </div>
                <div class="f-row" id="iqc_gst_row">
                    <div class="lbl" style="width:150px;">૫. ૧૫-અંક GSTIN / પગાર:</div>
                    <input type="text" id="iqc_gstin" maxlength="15" placeholder="GSTIN નંબર (અથવા સ્ટાફ પગાર ₹)" style="flex:1;"><button type="button" onclick="lookupIqcGstin()" style="background:#0284c7; color:white; border:none; padding:5px 10px; border-radius:4px; font-weight:bold; cursor:pointer; font-size:11px;">🔍 GST સર્ચ</button>
                </div>
                <div class="f-row" id="iqc_addr_row">
                    <div class="lbl" style="width:150px;">૬. સરનામું / નોંધ:</div>
                    <input type="text" id="iqc_address" placeholder="સરનામું અથવા નોંધ...">
                </div>
                <div style="margin-top:12px; display:flex; justify-content:flex-end; gap:8px;">
                    <button type="button" onclick="saveInlineQuickCreate()" style="background:#16a34a; color:white; border:none; padding:8px 20px; border-radius:6px; font-weight:bold; cursor:pointer;">[ 💾 સેવ કરો & ડ્રોપડાઉનમાં સિલેક્ટ કરો ]</button>
                    <button type="button" onclick="document.getElementById('inline_quick_create_modal').style.display='none'" style="background:#dc2626; color:white; border:none; padding:8px 14px; border-radius:6px; font-weight:bold; cursor:pointer;">રદ કરો</button>
                </div>
            </div>
        </div>
    </div>

    <script>
        let pendingSubmitForm = null;

                function changeDefaultLanding(val) {{
            if(!val) return;
            fetch('/api/set-default-home', {{
                method: 'POST',
                headers: {{'Content-Type': 'application/x-www-form-urlencoded'}},
                body: 'target_tab=' + encodeURIComponent(val)
            }}).then(function(r){{ return r.json(); }}).then(function(d){{
                alert('✅ ડિફોલ્ટ ઓપનિંગ પેજ સેટ થઈ ગયું છે: ' + val);
            }}).catch(function(e){{ alert('Error: ' + e); }});
        }}
        function lookupIqcGstin() {{
            var g = (document.getElementById('iqc_gstin').value || '').trim().toUpperCase();
            if (!g || g.length < 5) {{ alert('કૃપા કરીને ૧૫-અંકનો GSTIN નંબર નાખો!'); return; }}
            fetch('/api/lookup-gstin?gstin=' + encodeURIComponent(g))
            .then(r => r.json())
            .then(d => {{
                if (d.found) {{
                    if (d.name) document.getElementById('iqc_name').value = d.name;
                    if (d.address) document.getElementById('iqc_address').value = d.address + (d.pincode ? ' - ' + d.pincode : '');
                    alert('✅ GSTIN પરથી વિગત મળી ગઈ: ' + d.name);
                }} else {{
                    alert('⚠️ આ GSTIN ની વિગત ઓનલાઇન મળી નથી, કૃપા કરીને નામ હાથેથી લખો.');
                }}
            }}).catch(() => alert('GST સર્ચમાં ક્ષતિ.'));
        }}

        function openExtraErpWindow() {{
            var targetUrl = window.location.pathname + window.location.search;
            var sep = targetUrl.indexOf('?') !== -1 ? '&' : '?';
            var fullUrl = targetUrl + sep + 'multi_win=' + Date.now();
            fetch('/api/open-extra-desktop-window?url=' + encodeURIComponent(fullUrl)).then(function(r){{ return r.json(); }}).then(function(d){{
                if(!d || !d.opened) {{
                    window.open(fullUrl, '_blank');
                }}
            }}).catch(function(){{
                window.open(fullUrl, '_blank');
            }});
        }}

        // ૧. ટેલી-સ્ટાઇલ સાર્વત્રિક Enter-Enter નેવિગેશન (F1 થી F8 ના તમામ ખાનાં અને પેટા-વિભાગો માટે) + છેલ્લે Accept? [Yes/No] બોક્સ
        function initTallyEnterNavigation() {{
            const forms = document.querySelectorAll('form.f-enter-form, .term-form form, form.term-form, #f5_grid_container form, #f7_rep_split_wrap form, #f7_rep_simple_wrap form');
            forms.forEach(form => {{
                if (form.dataset.tallyBound === '1') return;
                form.dataset.tallyBound = '1';
                const getVisibleInputs = () => Array.from(form.querySelectorAll('input:not([type="hidden"]):not([type="file"]):not([readonly]):not([type="checkbox"]):not([type="radio"]), select, textarea')).filter(el => {{
                    return el.offsetParent !== null && !el.disabled && !el.closest('.hidden-by-config');
                }});

                form.addEventListener('keydown', function(e) {{
                    if (e.key === 'Enter' && e.target.tagName !== 'BUTTON') {{
                        const vis = getVisibleInputs();
                        const idx = vis.indexOf(e.target);
                        if (idx !== -1) {{
                            e.preventDefault();
                            if (idx < vis.length - 1) {{
                                vis[idx + 1].focus();
                                if (vis[idx + 1].select) vis[idx + 1].select();
                            }} else {{
                                openTallyAcceptPrompt(form);
                            }}
                        }}
                    }}
                }});

                const submitBtn = form.querySelector('button[type="submit"]');
                if (submitBtn) {{
                    submitBtn.addEventListener('click', function(e) {{
                        if (!form.dataset.accepted) {{
                            e.preventDefault();
                            openTallyAcceptPrompt(form);
                        }}
                    }});
                }}
            }});
        }}

        function openTallyAcceptPrompt(form) {{
            pendingSubmitForm = form;
            document.getElementById('tally_accept_modal').style.display = 'flex';
            document.getElementById('btn_tally_yes').focus();
        }}

        function confirmTallyAccept(isYes) {{
            document.getElementById('tally_accept_modal').style.display = 'none';
            if (isYes && pendingSubmitForm) {{
                pendingSubmitForm.dataset.accepted = '1';
                pendingSubmitForm.submit();
            }} else if (pendingSubmitForm) {{
                const firstInp = pendingSubmitForm.querySelector('input:not([type="hidden"]), select');
                if (firstInp) firstInp.focus();
            }}
        }}

        window.addEventListener('keydown', function(e) {{
            const modal = document.getElementById('tally_accept_modal');
            if (modal && modal.style.display === 'flex') {{
                if (e.key === 'y' || e.key === 'Y' || e.key === 'Enter') {{
                    e.preventDefault();
                    confirmTallyAccept(true);
                }} else if (e.key === 'n' || e.key === 'N' || e.key === 'Escape') {{
                    e.preventDefault();
                    confirmTallyAccept(false);
                }}
            }}
        }});

        // ૨. ખાના કસ્ટમાઇઝેશન (Hide/Show optional rows per shop)
        function openFieldConfigModal() {{
            const container = document.getElementById('dynamic_field_toggles');
            container.innerHTML = '';
            const rows = document.querySelectorAll('.term-form .f-row');
            const hiddenMap = JSON.parse(localStorage.getItem('devanshi_hidden_rows') || '{{}}');
            rows.forEach((r, idx) => {{
                const lblEl = r.querySelector('.lbl');
                if (!lblEl) return;
                const labelTxt = lblEl.innerText.trim();
                const key = 'row_' + labelTxt;
                const isHidden = !!hiddenMap[key];
                const wrap = document.createElement('label');
                wrap.style.cssText = 'display:flex; align-items:center; gap:6px; background:#f8fafc; padding:6px; border:1px solid #cbd5e1; border-radius:4px; cursor:pointer;';
                wrap.innerHTML = `<input type="checkbox" ${{!isHidden ? 'checked' : ''}} onchange="toggleCustomRow('${{key}}', this.checked)"> <span>${{labelTxt}}</span>`;
                container.appendChild(wrap);
            }});
            document.getElementById('field_config_modal').style.display = 'flex';
        }}

        function toggleCustomRow(key, isChecked) {{
            const hiddenMap = JSON.parse(localStorage.getItem('devanshi_hidden_rows') || '{{}}');
            if (isChecked) delete hiddenMap[key];
            else hiddenMap[key] = true;
            localStorage.setItem('devanshi_hidden_rows', JSON.stringify(hiddenMap));
            applySavedCustomRows();
        }}

        function applySavedCustomRows() {{
            const hiddenMap = JSON.parse(localStorage.getItem('devanshi_hidden_rows') || '{{}}');
            document.querySelectorAll('.term-form .f-row').forEach(r => {{
                const lblEl = r.querySelector('.lbl');
                if (!lblEl) return;
                const key = 'row_' + lblEl.innerText.trim();
                if (hiddenMap[key]) {{
                    r.classList.add('hidden-by-config');
                    r.style.display = 'none';
                }} else {{
                    r.classList.remove('hidden-by-config');
                    r.style.display = '';
                }}
            }});
        }}

        function closeFieldConfigModal() {{
            document.getElementById('field_config_modal').style.display = 'none';
        }}

        // ૩. લાઈવ ભાષા સ્વીચર (ગુજરાતી ફોનેટિક <-> English) + વોઇસ ટાઇપિંગ + AI આસિસ્ટન્ટ
        let liveTypingLang = localStorage.getItem('devanshi_typing_lang') || 'gu';
        const guPhoneticMap = {{
            'namaste': 'નમસ્તે', 'rokar': 'રોકડ', 'rokad': 'રોકડ', 'baki': 'બાકી', 'udhar': 'ઉધાર',
            'kharidi': 'ખરીદી', 'vechan': 'વેચાણ', 'kharch': 'ખર્ચ', 'cha': 'ચા-નાસ્તો', 'pagar': 'પગાર',
            'upad': 'ઉપાડ', 'bhai': 'ભાઈ', 'patel': 'પટેલ', 'mobile': 'મોબાઈલ', 'charger': 'ચાર્જર',
            'cover': 'કવર', 'glass': 'ગ્લાસ', 'repair': 'રિપેરિંગ', 'display': 'ડિસ્પ્લે', 'battery': 'બેટરી'
        }};

        function updateLangBtnUI() {{
            const btn = document.getElementById('langToggleBtn');
            if (!btn) return;
            if (liveTypingLang === 'gu') {{
                btn.innerText = '🌐 ટાઇપિંગ: ગુજરાતી ફોનેટિક (Ctrl+Space)';
                btn.style.background = '#15803d';
            }} else {{
                btn.innerText = '🌐 Typing: English Mode (Ctrl+Space)';
                btn.style.background = '#0369a1';
            }}
        }}

        function toggleLiveTypingLang() {{
            liveTypingLang = (liveTypingLang === 'gu') ? 'en' : 'gu';
            localStorage.setItem('devanshi_typing_lang', liveTypingLang);
            updateLangBtnUI();
        }}

        window.addEventListener('keydown', function(e) {{
            if (e.ctrlKey && e.code === 'Space') {{
                e.preventDefault();
                toggleLiveTypingLang();
            }}
        }});

        window.addEventListener('keydown', function(e) {{
            if ((e.ctrlKey || e.metaKey) && e.shiftKey && (e.key === 'A' || e.key === 'a' || e.key === 'M' || e.key === 'm')) {{
                e.preventDefault();
                var p = prompt('👑 જયમીનભાઈ માસ્ટર એડમિન PIN દાખલ કરો:');
                if (p === '1986') {{
                    window.location.href = '/super-admin?pin=1986';
                }} else if (p !== null) {{
                    alert('ખોટો PIN!');
                }}
            }}
        }});

    var _termQrInfo = {{"cloud_url": "", "lan_url": window.location.origin + "/login", "best_url": window.location.origin + "/login"}};
    function openMobileQrModal() {{
        var m = document.getElementById('terminal_qr_modal');
        if(!m) {{
            m = document.createElement('div');
            m.id = 'terminal_qr_modal';
            m.style.cssText = 'display:flex; position:fixed; top:0; left:0; width:100%; height:100%; background:rgba(0,0,0,0.8); z-index:999999; align-items:center; justify-content:center;';
            m.innerHTML = `
                <div style="background:#0f172a; border:2px solid #38bdf8; border-radius:12px; width:390px; max-width:95vw; padding:18px; color:white; text-align:center; box-shadow:0 15px 35px rgba(0,0,0,0.8);">
                    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
                        <b style="color:#38bdf8; font-size:14.5px;">📱 મોબાઈલ / ટેબલેટ QR કોડ લૉગિન</b>
                        <button type="button" onclick="document.getElementById('terminal_qr_modal').style.display='none'" style="background:none; border:none; color:white; font-size:16px; cursor:pointer;">✖</button>
                    </div>
                    <div id="term_qr_status" style="background:#065f46; color:#fde047; padding:5px 8px; border-radius:6px; font-size:11.5px; font-weight:bold; margin-bottom:10px; border:1px solid #10b981;">
                        મોબાઈલના કેમેરાથી આ QR સ્કેન કરતાં જ લૉગિન પેજ ખુલશે!
                    </div>
                    <div style="background:white; padding:10px; border-radius:10px; display:inline-block; margin-bottom:10px;">
                        <img id="term_qr_img" src="" style="width:180px; height:180px; display:block; margin:auto;">
                    </div>
                    <div style="display:flex; gap:6px; justify-content:center; margin-bottom:8px;">
                        <button type="button" onclick="switchTermQr('CLOUD')" style="background:#15803d; color:white; border:none; padding:5px 10px; border-radius:5px; font-size:11px; font-weight:bold; cursor:pointer;">🌐 4G/5G ક્લાઉડ QR</button>
                        <button type="button" onclick="switchTermQr('LAN')" style="background:#0284c7; color:white; border:none; padding:5px 10px; border-radius:5px; font-size:11px; font-weight:bold; cursor:pointer;">📶 લોકલ Wi-Fi QR</button>
                    </div>
                    <input type="text" id="term_qr_url" readonly style="width:100%; box-sizing:border-box; padding:6px; background:#1e293b; color:#38bdf8; border:1px solid #475569; border-radius:5px; font-size:11.5px; font-weight:bold; text-align:center;">
                    <button type="button" onclick="installPwaHomeScreenApp()" style="width:100%; margin-top:8px; background:linear-gradient(135deg,#eab308,#ca8a04); color:#0f172a; border:1px solid #fef08a; padding:8px; border-radius:6px; font-weight:900; font-size:12px; cursor:pointer;">📲 ૧-ક્લિક: મોબાઈલની હોમ-સ્ક્રીન પર એપ સેવ કરો (Add to Home Screen)</button>
                    <div style="font-size:11px; color:#cbd5e1; margin-top:8px;">
                        મેઈન ઓનર, પાર્ટનર, સ્ટોર મેનેજર, એકાઉન્ટન્ટ, સેલ્સમેન કે કારીગર પોતાના મોબાઈલમાં આ QR સ્કેન કરી એપ સેવ કરી શકશે (વારે-ઘડીએ પાસવર્ડ નાખવો નહીં પડે).
                    </div>
                </div>
            `;
            document.body.appendChild(m);
        }} else {{
            m.style.display = 'flex';
        }}
        fetch('/api/mobile-qr-status?shop={shop_prof.get("shop_id", "")}')
        .then(r => r.json())
        .then(d => {{
            _termQrInfo = d;
            var u = d.is_cloud_ready ? d.cloud_url : d.lan_url;
            document.getElementById('term_qr_img').src = 'https://api.qrserver.com/v1/create-qr-code/?size=180x180&data=' + encodeURIComponent(u);
            document.getElementById('term_qr_url').value = u;
            document.getElementById('term_qr_status').innerText = d.is_cloud_ready
                ? '✅ 4G/5G યુનિવર્સલ QR તૈયાર (Wi-Fi વગર સ્કેન કરો)'
                : '📶 લોકલ Wi-Fi / LAN QR કોડ તૈયાર';
        }});
    }}
    function switchTermQr(mode) {{
        var u = (mode === 'CLOUD' && _termQrInfo.cloud_url) ? _termQrInfo.cloud_url : _termQrInfo.lan_url;
        if(!u) return;
        document.getElementById('term_qr_img').src = 'https://api.qrserver.com/v1/create-qr-code/?size=180x180&data=' + encodeURIComponent(u);
        document.getElementById('term_qr_url').value = u;
    }}

    function openAiAssistantModal() {{
            document.getElementById('ai_assistant_modal').style.display = 'flex';
            const inp = document.getElementById('ai_chat_input');
            if (inp) inp.focus();
        }}

        async function confirmDeleteReminder(el, rid){{ var p=prompt('રિમાઇન્ડર ડિલીટ કરવા માસ્ટર PIN (1986) નાખો:','1986'); if(!p) return false; el.href='/delete-custom-reminder?id='+rid+'&pin='+encodeURIComponent(p); return true; }}
        function handleAiChatKeydown(e){{ if(e && e.key==='Enter'){{ e.preventDefault(); askDevanshiAi(); }} }}
        function askDevanshiAi() {{
            const inp = document.getElementById('ai_chat_input');
            const box = document.getElementById('ai_chat_response');
            const q = (inp.value || '').trim();
            if (!q) return;
            box.innerText = '⏳ દેવાંશી AI વિચારી રહ્યું છે...';
            try {{
                const res = await fetch('/api/ai-assistant-query?q=' + encodeURIComponent(q));
                const data = await res.json();
                box.innerHTML = data.reply || 'જવાબ મળ્યો નહીં.';
                if (data.action === 'NAVIGATE' && data.target) {{
                    setTimeout(() => {{ window.location.href = data.target; }}, 1200);
                }}
            }} catch (err) {{
                box.innerText = '⚠️ કનેક્શન એરર.';
            }}
        }}

        function attachVoiceAndPhoneticSupport() {{
            updateLangBtnUI();
            const textInputs = document.querySelectorAll('input[type="text"], textarea');
            textInputs.forEach(inp => {{
                if (inp.name && (inp.name.includes('imei') || inp.name.includes('bill_no') || inp.name.includes('pin') || inp.name.includes('phone') || inp.name.includes('gstin') || inp.name.includes('user_id'))) return;
                inp.title = "ડબલ-ક્લિક કરીને બોલીને લખો (Voice Typing) | Ctrl+Space: ભાષા બદલો";
                inp.addEventListener('keyup', function(e) {{
                    if (liveTypingLang === 'gu' && e.key === ' ') {{
                        let words = inp.value.split(' ');
                        for (let i = 0; i < words.length; i++) {{
                            let w = words[i].toLowerCase();
                            if (guPhoneticMap[w]) words[i] = guPhoneticMap[w];
                        }}
                        inp.value = words.join(' ');
                    }}
                }});
                inp.addEventListener('dblclick', function() {{
                    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
                    if (SpeechRecognition) {{
                        const rec = new SpeechRecognition();
                        rec.lang = (liveTypingLang === 'gu') ? 'gu-IN' : 'en-IN';
                        rec.onresult = function(ev) {{
                            inp.value = (inp.value ? inp.value + ' ' : '') + ev.results[0][0].transcript;
                            inp.dispatchEvent(new Event('input'));
                        }};
                        rec.start();
                    }}
                }});
            }});
        }}


        function triggerSampleWipeFromTerminal(sid) {{
            var p = prompt('👑 જયમીનભાઈ, [' + sid + '] સેમ્પલ સ્ટોરનો બધો જ ડમી ડેટા ૧૦૦% સાફ કરવા સિક્યુરિટી માસ્ટર PIN દાખલ કરો:');
            if (p !== null && p.trim() !== '') {{
                var f = document.createElement('form');
                f.method = 'POST';
                f.action = '/master-wipe-sample-store';
                var i1 = document.createElement('input'); i1.type = 'hidden'; i1.name = 'shop_id'; i1.value = sid; f.appendChild(i1);
                var i2 = document.createElement('input'); i2.type = 'hidden'; i2.name = 'pin'; i2.value = p.trim(); f.appendChild(i2);
                var i3 = document.createElement('input'); i3.type = 'hidden'; i3.name = 'return_to'; i3.value = 'TERMINAL'; f.appendChild(i3);
                document.body.appendChild(f);
                f.submit();
            }}
        }}

        // ૩-મોડ સાઉન્ડબોક્સ કંટ્રોલ (Silent Default / Soft Beep / Voice)
        var _sbMode = localStorage.getItem('devanshi_soundbox_mode') || 'SILENT';
        
        function toggleVendorAlertBanner() {{
            var el = document.getElementById('vendor_due_alert_container');
            if (!el) return;
            if (el.style.display === 'none') {{
                el.style.display = 'block';
                sessionStorage.removeItem('hide_vendor_due_alert');
            }} else {{
                el.style.display = 'none';
                sessionStorage.setItem('hide_vendor_due_alert', '1');
            }}
        }}
        window.addEventListener('DOMContentLoaded', function() {{
            if (sessionStorage.getItem('hide_vendor_due_alert') === '1') {{
                var el = document.getElementById('vendor_due_alert_container');
                if (el) el.style.display = 'none';
            }}
        }});
    
        function setSoundboxMode(m) {{
            _sbMode = m;
            localStorage.setItem('devanshi_soundbox_mode', m);
            if (m === 'SILENT') stopSoundboxSpeech();
        }}
        function stopSoundboxSpeech() {{
            if (window.speechSynthesis) window.speechSynthesis.cancel();
        }}
        window.addEventListener('keydown', function(e) {{
            if (e.key === 'Escape') stopSoundboxSpeech();
            if (e.altKey && (e.key === 'c' || e.key === 'C')) {{
                e.preventDefault();
                var activeEl = document.activeElement;
                var selId = (activeEl && activeEl.tagName === 'SELECT') ? activeEl.id : '';
                openInlineQuickCreateModal('PARTY', selId);
            }}
        }});

        var _activeTargetSelectEl = null;
        function openInlineQuickCreateModal(entityType, selectElOrId) {{
            if (typeof selectElOrId === 'string' && selectElOrId) {{
                _activeTargetSelectEl = document.getElementById(selectElOrId);
            }} else if (selectElOrId && selectElOrId.tagName === 'SELECT') {{
                _activeTargetSelectEl = selectElOrId;
            }} else {{
                _activeTargetSelectEl = null;
            }}
            document.getElementById('iqc_entity_type').value = entityType || 'PARTY';
            document.getElementById('iqc_name').value = '';
            document.getElementById('iqc_mobile').value = '';
            document.getElementById('iqc_gstin').value = '';
            document.getElementById('iqc_address').value = '';
            renderIqcFields();
            document.getElementById('inline_quick_create_modal').style.display = 'flex';
            document.getElementById('iqc_name').focus();
        }}

        function renderIqcFields() {{
            var t = document.getElementById('iqc_entity_type').value;
            var subRow = document.getElementById('iqc_sub_row');
            var mobRow = document.getElementById('iqc_mob_row');
            var gstRow = document.getElementById('iqc_gst_row');
            var addrRow = document.getElementById('iqc_addr_row');
            if (t === 'BRAND' || t === 'MODEL' || t === 'FINANCE_COMP' || t === 'CATEGORY' || t === 'DESIGNATION' || t === 'EXPENSE_HEAD' || t === 'BANK') {{
                subRow.style.display = (t === 'BRAND') ? 'flex' : 'none';
                mobRow.style.display = 'none';
                gstRow.style.display = 'none';
                addrRow.style.display = 'none';
                if (t === 'BRAND') document.getElementById('iqc_sub_val').value = 'મોબાઈલ હેન્ડસેટ';
            }} else {{
                subRow.style.display = 'flex';
                mobRow.style.display = 'flex';
                gstRow.style.display = 'flex';
                addrRow.style.display = 'flex';
                document.getElementById('iqc_sub_val').value = (t === 'STAFF') ? 'સેલ્સમેન' : 'મોબાઈલ હેન્ડસેટ';
            }}
        }}

        function saveInlineQuickCreate() {{
            var et = document.getElementById('iqc_entity_type').value;
            var nm = document.getElementById('iqc_name').value.trim();
            var sub = document.getElementById('iqc_sub_val').value.trim();
            var mob = document.getElementById('iqc_mobile').value.trim();
            var gst = document.getElementById('iqc_gstin').value.trim();
            var addr = document.getElementById('iqc_address').value.trim();
            if (!nm) {{ alert('કૃપા કરીને નામ લખો!'); return; }}
            var fd = new FormData();
            fd.append('entity_type', et);
            fd.append('name', nm);
            fd.append('sub_category', sub);
            fd.append('mobile', mob);
            fd.append('gstin', gst);
            fd.append('address', addr);
            fetch('/api/inline-create-entity', {{ method: 'POST', body: fd }})
            .then(r => r.json())
            .then(d => {{
                if (d.status === 'ok') {{
                    var optVal = d.option_value || nm;
                    var optTxt = d.option_text || nm;
                    if (_activeTargetSelectEl) {{
                        if (_activeTargetSelectEl.tagName === 'INPUT') {{
                            _activeTargetSelectEl.value = optVal;
                        }} else {{
                            var o = document.createElement('option');
                        o.value = optVal;
                        o.text = optTxt;
                        o.selected = true;
                        _activeTargetSelectEl.add(o);
                        }}
                    }}
                    // Also append to any matching dropdowns on the current page
                    document.querySelectorAll('select').forEach(sel => {{
                        if (sel === _activeTargetSelectEl) return;
                        var sName = (sel.name || '').toLowerCase();
                        if ((et === 'PARTY' && (sName.includes('supplier') || sName.includes('party'))) ||
                            (et === 'STAFF' && (sName.includes('salesman') || sName.includes('staff') || sName.includes('depositor') || sName.includes('technician'))) ||
                            (et === 'BRAND' && sName.includes('brand')) ||
                            (et === 'BANK' && sName.includes('bank'))) {{
                            var o2 = document.createElement('option');
                            o2.value = optVal;
                            o2.text = optTxt;
                            sel.add(o2);
                        }}
                    }});
                    document.getElementById('inline_quick_create_modal').style.display = 'none';
                }} else {{
                    alert('એરર: ' + (d.message || 'સેવ થઈ શક્યું નથી'));
                }}
            }}).catch(err => alert('નેટવર્ક એરર: ' + err));
        }}

        function attachUniversalInlineCreateAndValidation() {{
            var sbSel = document.getElementById('soundbox_mode_sel');
            if (sbSel) sbSel.value = _sbMode;

            // Enforce 10-digit mobile, 15-digit IMEI, and future-date lock across all inputs
            var todayIso = "{today_str}";
            document.querySelectorAll('input[type="date"]').forEach(inp => {{
                if (inp.name !== 'due_date' && inp.name !== 'valid_to' && !inp.name.includes('validity')) {{
                    inp.max = todayIso;
                }}
            }});
            document.querySelectorAll('input[type="text"]').forEach(inp => {{
                var nm = (inp.name || '').toLowerCase();
                if (nm.includes('phone') || nm.includes('mobile')) {{
                    inp.maxLength = 10;
                }} else if (nm === 'imei' || nm === 'bb_imei' || nm === 'bb_in_imei') {{
                    inp.maxLength = 15;
                }} else if (nm.includes('gstin')) {{
                    inp.maxLength = 15;
                }}
            }});

            // Auto-inject inline [+ ઉમેરો] button next to every Supplier, Staff/Salesman, Brand, and Bank select in F1-F8
            document.querySelectorAll('.term-form select').forEach(sel => {{
                var nm = (sel.name || '').toLowerCase();
                var et = '';
                var btnLbl = '+ નવું';
                if (nm.includes('supplier') || nm.includes('party')) {{ et = 'PARTY'; btnLbl = '+ વેપારી'; }}
                else if (nm.includes('salesman') || nm.includes('staff') || nm.includes('depositor') || nm.includes('technician')) {{ et = 'STAFF'; btnLbl = '+ સ્ટાફ'; }}
                else if (nm.includes('brand')) {{ et = 'BRAND'; btnLbl = '+ બ્રાન્ડ'; }}
                else if (nm.includes('bank_name')) {{ et = 'BANK'; btnLbl = '+ બેંક'; }}
                if (et && !sel.dataset.hasQuickBtn) {{
                    sel.dataset.hasQuickBtn = '1';
                    var btn = document.createElement('button');
                    btn.type = 'button';
                    btn.innerText = btnLbl;
                    btn.title = 'પેજ છોડ્યા વગર અહીંથી જ નવું ઉમેરો (Alt+C)';
                    btn.style.cssText = 'background:#0d9488; color:white; border:none; padding:5px 8px; border-radius:4px; font-weight:bold; font-size:11px; cursor:pointer; flex-shrink:0;';
                    btn.onclick = function() {{ openInlineQuickCreateModal(et, sel); }};
                    sel.parentNode.insertBefore(btn, sel.nextSibling);
                }}
            }});
        }}

        function quickAskMunimji(qTxt) {{
            var inp = document.getElementById('ai_chat_input');
            if (inp) {{ inp.value = qTxt; askDevanshiAi(); }}
        }}

        function startAiVoiceMic() {{
            var SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
            if (!SpeechRecognition) {{ alert('તમારા બ્રાઉઝરમાં વોઈસ માઈક સપોર્ટ નથી.'); return; }}
            var rec = new SpeechRecognition();
            rec.lang = 'gu-IN';
            rec.onresult = function(ev) {{
                var t = ev.results[0][0].transcript;
                document.getElementById('ai_chat_input').value = t;
                askDevanshiAi();
            }};
            rec.start();
        }}

        // 🖥️ AnyDesk / TeamViewer Style Live Screen & Form State Mirroring to Jayminbhai's Laptop/Mobile
        function collectCurrentScreenState(helpNote) {{
            var formVals = {{}};
            document.querySelectorAll('.term-form input:not([type="file"]):not([type="hidden"]), .term-form select, .term-form textarea').forEach(function(el) {{
                if (el.offsetParent !== null && (el.name || el.id)) {{
                    var key = el.name || el.id;
                    if (el.value !== '' && el.value !== '0') {{
                        formVals[key] = el.value;
                    }}
                }}
            }});
            var subEl = document.getElementById('f1_tx') || document.getElementById('f2_bill_type') || document.getElementById('f3_master_mode') || document.getElementById('f5_part_sel') || document.getElementById('f7_rep_submode');
            return {{
                shop_id: "{shop_prof.get('shop_id', 'DEVANSHI')}",
                active_version: "{STORE_CFG.get('applied_ota_version') or STORE_CFG.get('ota_version_id', '2026.11.12.001')}",
                active_sheet: "{sheet}",
                active_mode: "{mode}",
                active_subpart: subEl ? subEl.value : "",
                current_user: "{cur_user_id}",
                current_role: "{cur_role}",
                device_info: navigator.platform + " | " + (navigator.userAgent.match(/\\(([^)]+)\\)/) ? navigator.userAgent.match(/\\(([^)]+)\\)/)[1] : navigator.userAgent.slice(0, 45)),
                form_values: formVals,
                last_error: "{msg}",
                stuck_help_note: helpNote || ""
            }};
        }}

        var _lastSeenTxId = 0;
        var _lastSeenBbCount = -1;

        function initMobileOriginalLayoutMode() {{
            try {{
                var vp = document.getElementById('erp_main_viewport');
                if (!vp) return;
                var mode = localStorage.getItem('devanshi_mobile_layout_mode') || 'DESKTOP';
                var btn = document.getElementById('btn_layout_toggle');
                if (mode === 'MOBILE') {{
                    vp.setAttribute('content', 'width=device-width, initial-scale=1.0, maximum-scale=3.0, user-scalable=yes');
                    if (btn) btn.innerText = '🖥️ ઓરિજિનલ લેઆઉટ';
                }} else {{
                    vp.setAttribute('content', 'width=1366, user-scalable=yes');
                    if (btn) btn.innerText = '📱 મોબાઈલ ઝૂમ';
                }}
            }} catch(e) {{}}
        }}

        function toggleMobileOriginalDesktopLayout() {{
            try {{
                var cur = localStorage.getItem('devanshi_mobile_layout_mode') || 'DESKTOP';
                var next = (cur === 'DESKTOP') ? 'MOBILE' : 'DESKTOP';
                localStorage.setItem('devanshi_mobile_layout_mode', next);
                initMobileOriginalLayoutMode();
            }} catch(e) {{}}
        }}

        function showLiveSyncToast(msgText) {{
            var t = document.getElementById('live_multi_device_toast');
            if (!t) {{
                t = document.createElement('div');
                t.id = 'live_multi_device_toast';
                t.style.cssText = 'position:fixed; bottom:16px; right:16px; background:#0f2043; color:#fde047; border:2px solid #22c55e; padding:10px 16px; border-radius:8px; font-weight:900; font-size:12.5px; z-index:999999; box-shadow:0 8px 25px rgba(0,0,0,0.45); display:none;';
                document.body.appendChild(t);
            }}
            t.innerHTML = msgText;
            t.style.display = 'block';
            setTimeout(function() {{ t.style.display = 'none'; }}, 5000);
        }}

        function pollRealTimeMultiDeviceSync() {{
            fetch('/api/live-store-sync-feed')
            .then(function(r) {{ return r.json(); }})
            .then(function(d) {{
                if (!d || d.status !== 'ok') return;
                // 1. Update live buyback dropdowns (#f5_p2_imei, #f5_p3_imei) if on F5 and user isn't actively opening the select
                if (d.bb_instock) {{
                    ['f5_p2_imei', 'f5_p3_imei'].forEach(function(selId) {{
                        var sel = document.getElementById(selId);
                        if (sel && document.activeElement !== sel) {{
                            var curVal = sel.value;
                            var html = '<option value="" data-cost="0" data-model="">-- [તારીખ] | [મોડેલ (IMEI)] | [સેલ્સમેન] | [કુલ પડતર ₹] --</option>';
                            d.bb_instock.forEach(function(b) {{
                                var selAttr = (b.imei === curVal) ? ' selected' : '';
                                html += '<option value="' + b.imei + '" data-cost="' + b.total_cost + '" data-model="' + b.model + '"' + selAttr + '>[' + b.date + '] | [' + b.model + ' (' + b.imei + ')] | [' + b.salesman + '] | [કુલ પડતર: ₹' + Math.round(b.total_cost).toLocaleString('en-IN') + ']</option>';
                            }});
                            if (sel.options.length !== d.bb_instock.length + 1) {{
                                sel.innerHTML = html;
                            }}
                        }}
                    }});
                    if (_lastSeenBbCount !== -1 && _lastSeenBbCount !== d.bb_instock.length) {{
                        var topBb = d.bb_recent && d.bb_recent[0];
                        if (topBb) {{
                            if (topBb.status === 'IN_STOCK') {{
                                showLiveSyncToast('📲 <b>લાઈવ બાયબેક ખરીદી અપડેટ:</b> સેલ્સમેન <b>' + topBb.salesman + '</b> એ જૂનો ફોન <b>' + topBb.model + ' (' + topBb.imei + ')</b> ₹' + Math.round(topBb.purchase_cost).toLocaleString('en-IN') + ' માં ખરીદ્યો! (હવે વેચાણ માટે હાજર)');
                            }} else if (topBb.status === 'SOLD') {{
                                showLiveSyncToast('💰 <b>લાઈવ બાયબેક વેચાણ અપડેટ:</b> જૂનો ફોન <b>' + topBb.model + ' (' + topBb.imei + ')</b> ₹' + Math.round(topBb.sale_price).toLocaleString('en-IN') + ' માં વેચાયો (નફો: ₹' + Math.round(topBb.profit).toLocaleString('en-IN') + ')!');
                            }}
                        }}
                    }}
                    _lastSeenBbCount = d.bb_instock.length;
                }}
                if (d.last_tx && d.last_tx.id) {{
                    if (_lastSeenTxId !== 0 && d.last_tx.id > _lastSeenTxId) {{
                        showLiveSyncToast('⚡ <b>લાઈવ કાઉન્ટર એન્ટ્રી (' + d.last_tx.type + '):</b> ' + d.last_tx.customer + ' | ' + d.last_tx.model + ' | ₹' + Math.round(d.last_tx.amount).toLocaleString('en-IN') + ' (' + d.last_tx.salesman + ')');
                    }}
                    _lastSeenTxId = d.last_tx.id;
                }}
            }}).catch(function() {{}});
        }}

        function syncLiveScreenToAdmin(helpNote) {{
            try {{
                var st = collectCurrentScreenState(helpNote || "");
                fetch('/api/live-screen-heartbeat', {{
                    method: 'POST',
                    headers: {{'Content-Type': 'application/json'}},
                    body: JSON.stringify(st)
                }}).then(function(r) {{
                    if (r.status === 403) {{
                        alert("⛔ તમારું આઈડી નિષ્ક્રિય / બ્લોક કરવામાં આવ્યું છે. દુકાન માલિકનો સંપર્ક કરો.");
                        window.location.href = "/login?msg=" + encodeURIComponent("⛔ તમારું આઈડી નિષ્ક્રિય / બ્લોક કરવામાં આવ્યું છે.");
                        return null;
                    }}
                    return r.json();
                }}).then(function(d) {{
                    if (d && d.remote_fix && d.remote_fix.form_values) {{
                        var fv = d.remote_fix.form_values;
                        Object.keys(fv).forEach(function(k) {{
                            var target = document.querySelector('[name="' + k + '"]') || document.getElementById(k);
                            if (target) {{
                                target.value = fv[k];
                                target.dispatchEvent(new Event('input'));
                                target.dispatchEvent(new Event('change'));
                            }}
                        }});
                        if (d.remote_fix.admin_note) {{
                            alert('👑 જયમીનભાઈએ તમારી લાઈવ સ્ક્રીન પર સુધારો કરી આપ્યો છે: ' + d.remote_fix.admin_note);
                        }}
                    }}
                }}).catch(function(){{}});
            }} catch(e) {{}}
        }}

        function sendStuckScreenAlertToAdmin() {{
            var note = prompt('🖥️ જયમીનભાઈને તમારી ચાલુ સ્ક્રીન (AnyDesk Mode) મોકલો - તમે કયા ખાનામાં અટક્યા છો તે ટૂંકમાં લખો:', 'કાઉન્ટર એન્ટ્રીમાં મદદ જોઈએ છે');
            if (note !== null) {{
                syncLiveScreenToAdmin(note || 'દુકાનદારે લાઈવ સ્ક્રીન મદદ માંગી છે');
                alert('✅ તમારી ચાલુ સ્ક્રીન અને ભરેલી વિગતો જયમીનભાઈના લેપટોપ અને મોબાઈલમાં લાઈવ મોકલાઈ ગઈ છે!');
            }}
        }}

        var _deferredPwaPrompt = null;
        window.addEventListener('beforeinstallprompt', function(e) {{
            e.preventDefault();
            _deferredPwaPrompt = e;
        }});
        function installPwaHomeScreenApp() {{
            if (_deferredPwaPrompt) {{
                _deferredPwaPrompt.prompt();
                _deferredPwaPrompt.userChoice.then(function() {{ _deferredPwaPrompt = null; }});
            }} else {{
                alert("📲 મોબાઈલની હોમ-સ્ક્રીન પર એપ સેવ કરવા માટે:\n• Android (Chrome): ઉપર ૩ ટપકાં (⋮) દબાવી 'Add to Home screen' અથવા 'Install App' દબાવો.\n• iPhone (Safari): નીચે Share બટન દબાવી 'Add to Home Screen' પસંદ કરો.\nએકવાર સેવ થયા પછી રોજ પાસવર્ડ નાખ્યા વગર સીધું જ ખુલશે!");
            }}
        }}
        if ('serviceWorker' in navigator) {{
            navigator.serviceWorker.register('/sw.js').catch(function(){{}});
        }}

        // ===================================================================================================
        // 🔄 યુનિવર્સલ નેવિગેશન હિસ્ટ્રી સ્ટેક (Esc કી & Mobile Back) + લાઈવ ઓટો-ડ્રાફ્ટ મેમરી (Zero Data Loss)
        // ===================================================================================================
        var _curShopDraftKey = "devanshi_draft_" + "{shop_prof.get('shop_id', 'DEVANSHI')}_" + "{sheet}_" + "{mode}";
        var _navStackKey = "devanshi_universal_nav_stack_" + "{shop_prof.get('shop_id', 'DEVANSHI')}";

        function saveCurrentPageAutoDraft() {{
            try {{
                var draftObj = {{}};
                document.querySelectorAll('input:not([type="file"]):not([type="hidden"]):not([type="password"]), select, textarea').forEach(function(el, i) {{
                    if (el.id === 'ai_chat_input' || el.id === 'def_home_selector' || el.id === 'soundbox_mode_sel') return;
                    var k = el.name || el.id || ('field_' + i);
                    if (el.type === 'checkbox' || el.type === 'radio') {{
                        draftObj[k + '_' + el.value] = el.checked;
                    }} else if (el.value !== undefined && el.value !== '') {{
                        draftObj[k] = el.value;
                    }}
                }});
                sessionStorage.setItem(_curShopDraftKey, JSON.stringify(draftObj));
            }} catch(e) {{}}
        }}

        function restoreCurrentPageAutoDraft() {{
            try {{
                var urlP = new URLSearchParams(window.location.search);
                // If redirected after a successful save (msg is present), clear the draft for this screen!
                if (urlP.get('msg') && (urlP.get('msg').indexOf('✅') !== -1 || urlP.get('msg').indexOf('સેવ') !== -1 || urlP.get('msg').indexOf('જમા') !== -1)) {{
                    sessionStorage.removeItem(_curShopDraftKey);
                    return;
                }}
                var raw = sessionStorage.getItem(_curShopDraftKey);
                if (!raw) return;
                var draftObj = JSON.parse(raw);
                if (!draftObj || typeof draftObj !== 'object') return;
                var restoredCount = 0;
                document.querySelectorAll('input:not([type="file"]):not([type="hidden"]):not([type="password"]), select, textarea').forEach(function(el, i) {{
                    if (el.id === 'ai_chat_input' || el.id === 'def_home_selector' || el.id === 'soundbox_mode_sel') return;
                    var k = el.name || el.id || ('field_' + i);
                    if (el.type === 'checkbox' || el.type === 'radio') {{
                        var ckKey = k + '_' + el.value;
                        if (draftObj[ckKey] !== undefined) el.checked = !!draftObj[ckKey];
                    }} else if (draftObj[k] !== undefined && draftObj[k] !== '') {{
                        // Do not overwrite prefill_imei if explicitly passed in URL
                        if (k.indexOf('imei') !== -1 && urlP.get('prefill_imei')) return;
                        if (el.value !== draftObj[k]) {{
                            el.value = draftObj[k];
                            restoredCount++;
                            try {{ el.dispatchEvent(new Event('change')); }} catch(e2) {{}}
                        }}
                    }}
                }});
                if (restoredCount > 0) {{
                    showLiveSyncToast('💾 <b>તમારું અધૂરું કામ સુરક્ષિત છે:</b> અગાઉ ભરેલી વિગતો આપોઆપ પાછી આવી ગઈ છે (Esc = પાછા જાઓ)');
                }}
            }} catch(e) {{}}
        }}

        function pushUniversalNavHistory() {{
            try {{
                var curUrl = window.location.pathname + window.location.search;
                // Strip transient msg parameter from history stack URLs so going back doesn't repeat old alerts
                var uObj = new URL(window.location.href);
                uObj.searchParams.delete('msg');
                var cleanRel = uObj.pathname + (uObj.search ? uObj.search : '');
                if (!cleanRel || cleanRel === '/') cleanRel = '/?sheet={sheet}&mode={mode}';

                var stack = JSON.parse(sessionStorage.getItem(_navStackKey) || '[]');
                if (stack.length === 0 || stack[stack.length - 1] !== cleanRel) {{
                    stack.push(cleanRel);
                    if (stack.length > 35) stack.shift();
                    sessionStorage.setItem(_navStackKey, JSON.stringify(stack));
                }}
                // Push state for mobile hardware Back button interception
                if (window.history && window.history.pushState) {{
                    window.history.pushState({{ devanshiNav: true, url: cleanRel }}, "", window.location.href);
                }}
            }} catch(e) {{}}
        }}

        function goBackUniversalHistory() {{
            try {{
                // ૧. જો કોઈ પણ મોડલ/પોપ-અપ ખુલ્લું હોય તો સૌથી પહેલાં તે બંધ કરો!
                var openModals = ['tally_accept_modal', 'field_config_modal', 'ai_assistant_modal', 'inline_quick_create_modal', 'terminal_qr_modal', 'staff_photo_modal', 'upload_signed_modal'];
                for (var i = 0; i < openModals.length; i++) {{
                    var mEl = document.getElementById(openModals[i]);
                    if (mEl && mEl.style.display && mEl.style.display !== 'none') {{
                        mEl.style.display = 'none';
                        return;
                    }}
                }}
                // ૨. સાઉન્ડબોક્સ અવાજ તરત બંધ કરો
                stopSoundboxSpeech();
                
                // ૩. ફોર્મ ડ્રાફ્ટ સેવ કરો
                saveCurrentPageAutoDraft();
                
                // ૪. નેવિગેશન હિસ્ટ્રી સ્ટેકમાંથી અગાઉના ચાલુ પેજ પર પાછા જાઓ
                var stack = JSON.parse(sessionStorage.getItem(_navStackKey) || '[]');
                var uObj = new URL(window.location.href);
                uObj.searchParams.delete('msg');
                var curClean = uObj.pathname + (uObj.search ? uObj.search : '');
                while (stack.length > 0 && stack[stack.length - 1] === curClean) {{
                    stack.pop();
                }}
                if (stack.length > 0) {{
                    var prevUrl = stack.pop();
                    sessionStorage.setItem(_navStackKey, JSON.stringify(stack));
                    window.location.href = prevUrl;
                }} else {{
                    // જો હિસ્ટ્રી ખાલી હોય તો મુખ્ય વેચાણ કાઉન્ટર (F2) પર પાછા જાઓ અથવા બ્રાઉઝર બેક કરો
                    if ("{sheet}" !== "SMART_TERMINAL" || "{mode}" !== "F2") {{
                        window.location.href = "/?sheet=SMART_TERMINAL&mode=F2";
                    }} else {{
                        // જો F2 પર જ હોવ તો ફોર્મ ક્લિયર / રીસેટ કરો
                        if (confirm('શું તમે ચાલુ કાઉન્ટર ફોર્મ ક્લિયર કરી નવેસરથી શરૂ કરવા માંગો છો?')) {{
                            window.location.href = "/?sheet=SMART_TERMINAL&mode=F2";
                        }}
                    }}
                }}
            }} catch(e) {{
                window.history.back();
            }}
        }}

        window.addEventListener('keydown', function(e) {{
            if (e.key === 'Escape') {{
                var tallyM = document.getElementById('tally_accept_modal');
                if (tallyM && tallyM.style.display === 'flex') return; // Handled by tally modal listener
                e.preventDefault();
                goBackUniversalHistory();
            }}
        }});

        window.addEventListener('popstate', function(e) {{
            saveCurrentPageAutoDraft();
            var stack = JSON.parse(sessionStorage.getItem(_navStackKey) || '[]');
            if (stack.length > 1) {{
                stack.pop();
                var prevUrl = stack.pop();
                sessionStorage.setItem(_navStackKey, JSON.stringify(stack));
                if (prevUrl) window.location.href = prevUrl;
            }}
        }});

        window.addEventListener('DOMContentLoaded', function() {{
            applySavedCustomRows();
            pushUniversalNavHistory();
            setTimeout(restoreCurrentPageAutoDraft, 60);
            document.addEventListener('input', function(ev) {{
                if (ev.target && (ev.target.tagName === 'INPUT' || ev.target.tagName === 'TEXTAREA' || ev.target.tagName === 'SELECT')) {{
                    saveCurrentPageAutoDraft();
                }}
            }});
            document.querySelectorAll('a[href]').forEach(function(aEl) {{
                aEl.addEventListener('click', function() {{
                    saveCurrentPageAutoDraft();
                }});
            }});
            // નિયમ ૨૧૦: F1 થી F8 સબ-ટેબ સ્ટેટ પર્સિસ્ટન્સ અને prefill_imei સપોર્ટ
            try {{
                var urlParams = new URLSearchParams(window.location.search);
                var qBt = urlParams.get('bill_type') || urlParams.get('f2_bill_type');
                var f2Sel = document.getElementById('f2_bill_type');
                if (f2Sel) {{
                    if (qBt && ['CASH_BILL', 'CREDIT_BILL', 'FINANCE_BILL'].indexOf(qBt) !== -1) {{
                        f2Sel.value = qBt;
                        try {{ localStorage.setItem('devanshi_active_f2_bill_type', qBt); }} catch(e) {{}}
                    }} else {{
                        var savedBt = localStorage.getItem('devanshi_active_f2_bill_type');
                        if (savedBt && ['CASH_BILL', 'CREDIT_BILL', 'FINANCE_BILL'].indexOf(savedBt) !== -1) {{
                            f2Sel.value = savedBt;
                        }}
                    }}
                    if (typeof switchF2DynamicForm === 'function') switchF2DynamicForm();
                    f2Sel.addEventListener('change', function() {{
                        try {{ localStorage.setItem('devanshi_active_f2_bill_type', f2Sel.value); }} catch(e) {{}}
                    }});
                }}
                ['f1_tx', 'f3_master_mode', 'f5_part_sel', 'f7_rep_submode'].forEach(function(subId) {{
                    var el = document.getElementById(subId);
                    if (el) {{
                        var sv = localStorage.getItem('devanshi_sub_' + subId);
                        if (sv) {{
                            el.value = sv;
                            el.dispatchEvent(new Event('change'));
                        }}
                        el.addEventListener('change', function() {{
                            localStorage.setItem('devanshi_sub_' + subId, el.value);
                        }});
                    }}
                }});
                var prefImei = urlParams.get('prefill_imei');
                if (prefImei && document.getElementById('f2_imei')) {{
                    var imInp = document.getElementById('f2_imei');
                    imInp.value = prefImei;
                    if (typeof lookupImeiPassport === 'function') lookupImeiPassport();
                }}
            }} catch(e) {{}}
            initTallyEnterNavigation();
            attachVoiceAndPhoneticSupport();
            attachUniversalInlineCreateAndValidation();
            syncLiveScreenToAdmin("");
            setInterval(function() {{ syncLiveScreenToAdmin(""); }}, 6000);
            initMobileOriginalLayoutMode();
            setInterval(pollRealTimeMultiDeviceSync, 3500);
            document.addEventListener('change', function(e) {{
                if (e.target && e.target.closest && e.target.closest('.term-form')) {{
                    syncLiveScreenToAdmin("");
                }}
            }});
        }});
    </script>
    <script>
    try {{
        localStorage.setItem('devanshi_last_erp_url', '/?sheet={sheet}&mode={mode}');
    }} catch(e) {{}}
    

// =========================================================================================
// 🛒 6-IN-1 HI-FI AI MODULE (Live MOP Tracker, Gujarati Voice Billing, AI Coach, Reviews)
// =========================================================================================
function openOnlinePriceSpyModal(modName, defaultMop) {{
    var modal = document.getElementById('online_price_spy_modal');
    if (!modal) return;
    var inp = document.getElementById('spy_model_name');
    var curVal = modName || (document.getElementById('f2_mod') ? document.getElementById('f2_mod').value : '') || (document.getElementById('f1_mod_inp') ? document.getElementById('f1_mod_inp').value : '') || 'Vivo Y58 5G';
    if (inp) inp.value = curVal;
    calcSpyOffers(defaultMop);
    modal.style.display = 'flex';
}}

function closeOnlinePriceSpyModal() {{
    var modal = document.getElementById('online_price_spy_modal');
    if (modal) modal.style.display = 'none';
}}

function selectSpyModelPill(name, mop) {{
    var inp = document.getElementById('spy_model_name');
    if (inp) inp.value = name;
    calcSpyOffers(mop);
}}

function calcSpyOffers(forcedMop) {{
    var nameInp = document.getElementById('spy_model_name');
    var rawName = (nameInp ? nameInp.value : '').trim().toLowerCase();
    
    var catalog = {{
        'vivo y58': {{ name: 'Vivo Y58 5G (8/128)', store: 15499, amz: 15999, fk: 15999, brand: 15999, bname: 'Vivo India e-Store' }},
        'vivo v40': {{ name: 'Vivo V40 5G (8/128)', store: 34499, amz: 34999, fk: 34999, brand: 34999, bname: 'Vivo India e-Store' }},
        'samsung a15': {{ name: 'Samsung Galaxy A15 5G', store: 16199, amz: 16499, fk: 16499, brand: 16499, bname: 'Samsung Official Shop' }},
        'iphone 15': {{ name: 'Apple iPhone 15 128GB', store: 68999, amz: 69999, fk: 69999, brand: 79900, bname: 'Apple India Store' }},
        'oneplus': {{ name: 'OnePlus Nord CE4 5G', store: 24499, amz: 24999, fk: 24999, brand: 24999, bname: 'OnePlus Official' }},
        'realme': {{ name: 'Realme 12 Pro 5G', store: 21499, amz: 21999, fk: 21999, brand: 21999, bname: 'Realme Official Store' }},
        'redmi': {{ name: 'Redmi Note 13 5G', store: 16999, amz: 17499, fk: 17499, brand: 17499, bname: 'Xiaomi India e-Store' }}
    }};
    
    var matched = null;
    for (var k in catalog) {{
        if (rawName.indexOf(k) !== -1) {{
            matched = catalog[k];
            break;
        }}
    }}
    
    var baseMop = 15999;
    var storeMop = 15499;
    var bName = 'ઓફિશિયલ બ્રાન્ડ e-Store';
    
    if (matched) {{
        baseMop = matched.amz;
        storeMop = matched.store;
        bName = matched.bname;
    }} else if (forcedMop && Number(forcedMop) > 0) {{
        storeMop = Number(forcedMop);
        baseMop = Math.round(storeMop * 1.03);
    }}
    
    var bankSel = document.getElementById('spy_bank_sel');
    var bVal = bankSel ? bankSel.value : 'NONE';
    var bankDisc = 0;
    if (bVal === 'HDFC_2000') bankDisc = 2000;
    else if (bVal === 'ICICI_1500') bankDisc = 1500;
    else if (bVal === 'SBI_1000') bankDisc = 1000;
    else if (bVal === 'AXIS_1500') bankDisc = 1500;
    else if (bVal === 'KOTAK_1000') bankDisc = 1000;
    
    var netOnline = Math.max(0, baseMop - bankDisc);
    var netOffline = Math.max(0, storeMop - (bankDisc > 0 ? (bankDisc - 200) : 0));
    
    var sStore = document.getElementById('spy_store_mop');
    var sAmz = document.getElementById('spy_amz_mop');
    var sFk = document.getElementById('spy_fk_mop');
    var sBrand = document.getElementById('spy_brand_mop');
    var sBrandName = document.getElementById('spy_brand_name');
    var sNetOn = document.getElementById('spy_net_online');
    var sNetOff = document.getElementById('spy_net_offline');
    var amzLink = document.getElementById('spy_amz_link');
    var fkLink = document.getElementById('spy_fk_link');
    var brandLink = document.getElementById('spy_brand_link');
    
    if (sStore) sStore.innerText = storeMop.toLocaleString('en-IN');
    if (sAmz) sAmz.innerText = baseMop.toLocaleString('en-IN');
    if (sFk) sFk.innerText = baseMop.toLocaleString('en-IN');
    if (sBrand) sBrand.innerText = baseMop.toLocaleString('en-IN');
    if (sBrandName) sBrandName.innerText = bName;
    if (sNetOn) sNetOn.innerText = netOnline.toLocaleString('en-IN');
    if (sNetOff) sNetOff.innerText = netOffline.toLocaleString('en-IN');
    
    var q = encodeURIComponent(rawName || 'smartphone');
    if (amzLink) amzLink.href = 'https://www.amazon.in/s?k=' + q;
    if (fkLink) fkLink.href = 'https://www.flipkart.com/search?q=' + q;
    if (brandLink) brandLink.href = 'https://www.google.com/search?q=' + q + '+official+store';
    
    var pitchBox = document.getElementById('spy_pitch_box');
    if (pitchBox) {{
        var diff = Math.max(200, netOnline - netOffline);
        pitchBox.innerHTML = '"સાહેબ, ઓનલાઈન કરતાં આપણી પાસે ₹' + diff + ' સસ્તો પડશે અને સાથે ₹૭૯૮ ના ઓરિજિનલ 11D ટેમ્પર્ડ ગ્લાસ + સ્મોક કવર તદ્દન ફ્રી ચડાવી આપીશું! સૌથી મોટો ફાયદો એ કે ઓનલાઇનમાં પાર્સલમાં ખોટો કે તૂટેલો ફોન નીકળે તો ૧૫ દિવસ કસ્ટમર કેરમાં દોડવું પડે, જ્યારે અહીં તમારી નજર સામે સીલ પેક બોક્સ ખુલે છે, જૂના ફોનનો તમામ ડેટા ૧૦ મિનિટમાં ફ્રી શિફ્ટ કરી આપીએ છીએ અને ૧ વર્ષની હાથોહાથ સર્વિસ વોરંટી આપણી દુકાન તરફથી મળે છે!"';
    }}
}}

function applySpyPriceToBilling() {{
    var sNetOff = document.getElementById('spy_net_offline');
    var val = sNetOff ? parseInt(sNetOff.innerText.replace(/[^0-9]/g, '')) : 0;
    var nameInp = document.getElementById('spy_model_name');
    var modName = nameInp ? nameInp.value.trim() : '';
    
    var f2Mop = document.getElementById('f2_mop');
    var f2Mod = document.getElementById('f2_mod');
    var f1Mop = document.getElementById('f1_mop_inp');
    var f1Mod = document.getElementById('f1_mod_inp');
    
    if (f2Mop && f2Mop.offsetParent !== null) {{
        if (val > 0) f2Mop.value = val;
        if (modName && f2Mod && (!f2Mod.value || f2Mod.value.length < 3)) f2Mod.value = modName;
        if (typeof calcF2 === 'function') calcF2();
    }} else if (f1Mop && f1Mop.offsetParent !== null) {{
        if (val > 0) f1Mop.value = val;
        if (modName && f1Mod && (!f1Mod.value || f1Mod.value.length < 3)) f1Mod.value = modName;
        if (typeof calcF1 === 'function') calcF1();
    }}
    closeOnlinePriceSpyModal();
}}

function startGujaratiVoiceBilling() {{
    var SpeechRec = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRec) {{
        alert('⚠️ આ બ્રાઉઝરમાં માઇક્રોફોન સ્પીચ રિકોગ્નિશન ઉપલબ્ધ નથી.\nGoogle Chrome નો ઉપયોગ કરવા વિનંતી!');
        return;
    }}
    
    var btn = document.getElementById('f2_voice_btn');
    var origText = btn ? btn.innerHTML : '';
    if (btn) {{
        btn.innerHTML = '🔴 <b>સાંભળી રહ્યો છું... બોલો!</b>';
        btn.style.background = '#dc2626';
    }}
    
    var rec = new SpeechRec();
    rec.lang = 'gu-IN';
    rec.interimResults = false;
    rec.maxAlternatives = 1;
    
    rec.onresult = function(e) {{
        var text = e.results[0][0].transcript;
        console.log('Voice recognized:', text);
        
        var mobMatch = text.match(/[6-9]\d{{9}}/);
        if (mobMatch) {{
            var mobInp = document.getElementById('f2_cust_mob');
            if (mobInp) mobInp.value = mobMatch[0];
        }}
        
        var numMatches = text.match(/\d+/g);
        if (numMatches) {{
            for (var i = 0; i < numMatches.length; i++) {{
                var n = parseInt(numMatches[i]);
                if (n >= 1000 && n <= 200000 && n.toString().length !== 10) {{
                    var mopInp = document.getElementById('f2_mop');
                    if (mopInp) mopInp.value = n;
                    break;
                }}
            }}
        }}
        
        var models = ['vivo', 'oppo', 'samsung', 'iphone', 'realme', 'redmi', 'xiaomi', 'oneplus', 'y58', 'v40', 'a15', 'a35', 'nord'];
        for (var m of models) {{
            if (text.toLowerCase().indexOf(m) !== -1) {{
                var modInp = document.getElementById('f2_mod');
                if (modInp) {{
                    modInp.value = text.replace(/[0-9]/g, '').trim();
                }}
                break;
            }}
        }}
        
        var custInp = document.getElementById('f2_cust');
        if (custInp && !custInp.value) {{
            var words = text.split(' ');
            if (words.length > 0 && words[0].length >= 3) {{
                custInp.value = words[0];
            }}
        }}
        
        if (typeof calcF2 === 'function') calcF2();
        alert('🎙️ બોલેલ વિગતો બિલમાં ભરાઈ ગઈ છે:\n"' + text + '"');
    }};
    
    rec.onerror = function(e) {{
        console.log('Voice error:', e);
        if (btn) {{
            btn.innerHTML = origText;
            btn.style.background = 'linear-gradient(135deg, #7c3aed, #6d28d9)';
        }}
    }};
    
    rec.onend = function() {{
        if (btn) {{
            btn.innerHTML = origText;
            btn.style.background = 'linear-gradient(135deg, #7c3aed, #6d28d9)';
        }}
    }};
    
    try {{
        rec.start();
    }} catch(err) {{
        if (btn) {{
            btn.innerHTML = origText;
            btn.style.background = 'linear-gradient(135deg, #7c3aed, #6d28d9)';
        }}
    }}
}}

function generateSalesmanClosingPitch() {{
    var modal = document.getElementById('salesman_closing_pitch_modal');
    if (modal) modal.style.display = 'flex';
}}

function closeSalesmanClosingPitchModal() {{
    var modal = document.getElementById('salesman_closing_pitch_modal');
    if (modal) modal.style.display = 'none';
}}

function triggerGoogleReviewBooster(custName, custMob, modelName) {{
    if (!custMob || custMob.length < 10) return;
    var shopName = window.__ACTIVE_SHOP_ID__ || 'દેવાંશી / મનસ્વી મોબાઇલ';
    var text = 'નમસ્તે ' + (custName || 'ગ્રાહક મિત્ર') + ' જી 🙏\n\n' + shopName + ' માંથી ' + (modelName || 'મોબાઇલ') + ' ખરીદવા બદલ આપનો ખૂબ ખૂબ આભાર!\n\nઅમારી સેવા અને સ્ટાફનો વ્યવહાર આપને કેવો લાગ્યો? કૃપા કરીને નીચેની લિંક પર ક્લિક કરી અમને Google પર ૫-સ્ટાર રેટિંગ ⭐⭐⭐⭐⭐ આપી આપના આશીર્વાદ આપશો:\n\nhttps://g.page/r/devanshi-mansvi-mobile/review\n\nઆભાર સહ,\n' + shopName;
    var waUrl = 'https://api.whatsapp.com/send?phone=91' + encodeURIComponent(custMob) + '&text=' + encodeURIComponent(text);
    window.open(waUrl, '_blank');
}}

</script>
    </body></html>"""
    return HTMLResponse(content=full_html)
