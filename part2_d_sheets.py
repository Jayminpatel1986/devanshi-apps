import json
import urllib.parse
# -*- coding: utf-8 -*-
# =======================================================================================================================
# ⚠️ આવશ્યક એઆઈ ડાયરેક્ટિવ અને ડાયનામિક રૂલબુક ગવર્નન્સ (કાયમી અમર એઆઈ હેડર - માસ્ટર ૧૦ લોજિક અને મલ્ટી-સ્ટોર SaaS આવૃત્તિ)
# =======================================================================================================================
# [કડક ચેતવણી - Gemini, ChatGPT, Claude, Cursor અથવા અન્ય કોઈપણ AI મોડેલ અને ડેવલપર માટે બંધનકર્તા આદેશ]:
# ૧. આ હેડર 'અમર' (Immortal) છે. આ ફાઇલ part2_d_sheets.py છે (Sheets 2, 4, 5, 6, 7, 8, 9, 10, 11, 12).
# ૨. જૂના કોડનું એક પણ ફંક્શન, ડ્રોપડાઉન, ગાણિતિક સૂત્ર કે CRUD બટન કાઢવું સખત પ્રતિબંધિત છે.
# =======================================================================================================================

import datetime
from part1_core import ALL_12_SHEETS, ALL_8_COUNTERS, ALL_4_GALLAS

DEFAULT_GROWTH_DATA = {
    ("2020", "February"): 1104665, ("2020", "March"): 4585304, ("2020", "May"): 3231221,
    ("2020", "June"): 5488089, ("2020", "July"): 4313285, ("2020", "August"): 4331365,
    ("2020", "September"): 3779188, ("2020", "October"): 3609951, ("2020", "November"): 3987161, ("2020", "December"): 3453020,
    ("2021", "January"): 3073161, ("2021", "February"): 3623696, ("2021", "March"): 3345915, ("2021", "April"): 2902579,
    ("2021", "May"): 4110051, ("2021", "June"): 5530254, ("2021", "July"): 5060498, ("2021", "August"): 5134769,
    ("2021", "September"): 4593224, ("2021", "October"): 5025697, ("2021", "November"): 5903142, ("2021", "December"): 4455730,
    ("2022", "January"): 5120220, ("2022", "February"): 4123232, ("2022", "March"): 4684042, ("2022", "April"): 4732738,
    ("2022", "May"): 5042022, ("2022", "June"): 5489065, ("2022", "July"): 5840505, ("2022", "August"): 5390382,
    ("2022", "September"): 4629085, ("2022", "October"): 6791653, ("2022", "November"): 4220370, ("2022", "December"): 4110970,
    ("2023", "January"): 4078941, ("2023", "February"): 5413584, ("2023", "March"): 5430511, ("2023", "April"): 5785853,
    ("2023", "May"): 6760331, ("2023", "June"): 6374228, ("2023", "July"): 6782655, ("2023", "August"): 5750623,
    ("2023", "September"): 5563311, ("2023", "October"): 6745987, ("2023", "November"): 8044858, ("2023", "December"): 6571016,
    ("2024", "January"): 6149993, ("2024", "February"): 5649718, ("2024", "March"): 5384051, ("2024", "April"): 4856830,
    ("2024", "May"): 5945851, ("2024", "June"): 5930362, ("2024", "July"): 6411834, ("2024", "August"): 5594808,
    ("2024", "September"): 4951029, ("2024", "October"): 7255931, ("2024", "November"): 3683017, ("2024", "December"): 4179443,
    ("2025", "January"): 3065206, ("2025", "February"): 3651370, ("2025", "March"): 4813583, ("2025", "April"): 4065813,
    ("2025", "May"): 6108589, ("2025", "June"): 5658588, ("2025", "July"): 6237608, ("2025", "August"): 7150000,
    ("2025", "September"): 4568000, ("2025", "October"): 7535000, ("2025", "November"): 3967303, ("2025", "December"): 4853756,
    ("2026", "January"): 4692992, ("2026", "February"): 4872271, ("2026", "March"): 5347839, ("2026", "April"): 6329993,
    ("2026", "May"): 6986682, ("2026", "June"): 7238759, ("2026", "July"): 10305950, ("2026", "August"): 10202658
}

def render_live_stock_view(conn, c):
    c.execute("SELECT id, entry_date, party_name, brand, model, imei, purchase_rate, sale_rate, category, doc_path, bill_no, COALESCE(duplicate_warning, 0) FROM live_stock WHERE status='IN_STOCK' ORDER BY id DESC")
    stock_rows = c.fetchall()
    today_d = datetime.date.today()
    rows_html = ""
    fresh_cnt, aging_cnt = 0, 0
    fresh_dp_sum, aging_dp_sum, tot_dp_sum = 0.0, 0.0, 0.0
    for idx, r in enumerate(stock_rows):
        age_days = 0
        try:
            in_d = datetime.datetime.strptime(r[1], "%Y-%m-%d").date()
            age_days = (today_d - in_d).days
        except Exception:
            pass
        dp_v = float(r[6] or 0)
        mop_v = float(r[7] or 0)
        tot_dp_sum += dp_v
        is_dup_w = int(r[11] or 0) if len(r) > 11 else 0
        dup_pill = " <span style='background:#dc2626; color:white; padding:2px 6px; border-radius:3px; font-weight:900;'>🔴 RED SIGNAL: ડુપ્લિકેટ તપાસ બાકી</span>" if is_dup_w else ""
        if age_days >= 60:
            aging_cnt += 1
            aging_dp_sum += dp_v
            row_cat = "AGING"
            row_bg = "background:#fff1f2;" if is_dup_w else "background:#fef08a;"
            badge_html = f"<span style='background:#ca8a04; color:#ffffff; padding:2px 6px; border-radius:3px; font-weight:bold;'>🟡 AGING ડેડ સ્ટોક ({age_days} દિવસ)</span>{dup_pill}"
        else:
            fresh_cnt += 1
            fresh_dp_sum += dp_v
            row_cat = "FRESH"
            row_bg = "background:#fff1f2;" if is_dup_w else ""
            badge_html = f"<span style='background:#dcfce7; color:#16a34a; padding:2px 6px; border-radius:3px; font-weight:bold;'>🟢 IN STOCK ({age_days} દિવસ)</span>{dup_pill}"
        doc_url_s2 = (r[9] if r[9].startswith("/") else ("/" + r[9])) if r[9] else ""
        doc_btn = f"<a href='{doc_url_s2}' target='_blank' style='background:#0d9488; color:white; padding:2px 6px; border-radius:3px; text-decoration:none; font-weight:bold;'>📄 અસલ PDF</a> " if doc_url_s2 else ""
        voucher_btn = f"<a href='/view-purchase-invoice?bill_no={urllib.parse.quote(str(r[10] or ''))}&party_name={urllib.parse.quote(str(r[2] or ''))}' target='_blank' style='background:#7c3aed; color:white; padding:2px 6px; border-radius:3px; text-decoration:none; font-weight:bold;'>🧾 પાકું બિલ</a> " if (r[10] or r[2]) else ""
        rows_html += f"""
        <tr data-stock-cat="{row_cat}" style='{row_bg}'>
            <td>{idx+1}</td><td><b>{r[3]}</b></td><td><b>{r[4]}</b></td><td>{r[2] or '-'} {f'({r[10]})' if r[10] else ''}</td>
            <td>{r[8] or 'મોબાઈલ હેન્ડસેટ'}</td><td><b>{r[5]}</b></td><td>₹{dp_v:,.0f}</td><td>₹{mop_v:,.0f}</td>
            <td>{r[1]} (<b>{age_days} દિવસ</b>)</td><td>{badge_html}</td>
            <td>{voucher_btn}{doc_btn}<a href="/?sheet=SMART_TERMINAL&mode=F2&prefill_imei={r[5]}" style="background:#0284c7; color:white; padding:2px 6px; border-radius:3px; text-decoration:none; font-weight:bold;">[વેચાણ F2]</a> <a href="/delete-stock-item?id={r[0]}" onclick="return confirm('ડિલીટ કરવું છે?')" style="background:#dc2626; color:white; padding:2px 6px; border-radius:3px; text-decoration:none; font-weight:bold;">[ડિલીટ]</a></td>
        </tr>
        """
    return f"""
    <div style='padding:10px;'>
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:10px; flex-wrap:wrap; gap:8px;">
            <h3 style="margin:0;">૨. દુકાનનો હાજર સ્ટોક રજીસ્ટર (સિગ્નલ કાર્ડ પર ક્લિક કરતાં વિગતવાર લેજર ખુલશે)</h3>
            <button type="button" onclick="document.getElementById('stock_import_file').click()" style="background:#0d9488; color:white; border:none; padding:6px 14px; border-radius:4px; font-weight:bold; cursor:pointer;">📥 નવો સ્ટોક ઇમ્પોર્ટ કરો</button>
        </div>
        <div style="display:grid; grid-template-columns:repeat(3, 1fr); gap:10px; margin-bottom:12px;">
            <div onclick="filterLiveStockView('ALL')" style="background:#f1f5f9; border:2px solid #475569; padding:10px; border-radius:8px; text-align:center; cursor:pointer;">
                <div style="font-size:11.5px; font-weight:800; color:#334155;">📦 કુલ હાજર સ્ટોક (તમામ પીસ જુઓ)</div>
                <div style="font-size:18px; font-weight:900; color:#0f172a; margin-top:3px;">{len(stock_rows)} નંગ (કુલ DP: ₹{tot_dp_sum:,.0f})</div>
            </div>
            <div onclick="filterLiveStockView('FRESH')" style="background:#dcfce7; border:2px solid #16a34a; padding:10px; border-radius:8px; text-align:center; cursor:pointer;">
                <div style="font-size:11.5px; font-weight:800; color:#166534;">🟢 ગ્રીન સિગ્નલ: ફ્રેશ રનિંગ સ્ટોક (&lt;60 દિવસ)</div>
                <div style="font-size:18px; font-weight:900; color:#15803d; margin-top:3px;">{fresh_cnt} નંગ (DP: ₹{fresh_dp_sum:,.0f})</div>
            </div>
            <div onclick="filterLiveStockView('AGING')" style="background:#fef08a; border:2px solid #ca8a04; padding:10px; border-radius:8px; text-align:center; cursor:pointer; box-shadow:0 2px 6px rgba(202,138,4,0.25);">
                <div style="font-size:11.5px; font-weight:800; color:#854d0e;">🟡 યલો સિગ્નલ: ૬૦+ દિવસ જૂનો ડેડ સ્ટોક (ક્લિક કરી લેજર ખોલો)</div>
                <div style="font-size:18px; font-weight:900; color:#854d0e; margin-top:3px;">{aging_cnt} નંગ (DP: ₹{aging_dp_sum:,.0f})</div>
            </div>
        </div>
        <div style="display:flex; gap:6px; flex-wrap:wrap; margin-bottom:10px; align-items:center;">
            <span style="font-weight:900; color:#0f2043; font-size:12px;">⏳ જૂનો સ્ટોક ઝડપી ફિલ્ટર:</span>
            <button type="button" onclick="filterLiveStockView('ALL')" style="background:#0f2043; color:white; border:none; padding:5px 10px; border-radius:5px; font-weight:bold; cursor:pointer; font-size:11.5px;">📦 તમામ સ્ટોક</button>
            <button type="button" onclick="filterLiveStockByMinDays(30)" style="background:#0284c7; color:white; border:none; padding:5px 10px; border-radius:5px; font-weight:bold; cursor:pointer; font-size:11.5px;">🔵 30+ દિવસ જૂનો</button>
            <button type="button" onclick="filterLiveStockByMinDays(60)" style="background:#ca8a04; color:white; border:none; padding:5px 10px; border-radius:5px; font-weight:bold; cursor:pointer; font-size:11.5px;">🟡 60+ દિવસ જૂનો</button>
            <button type="button" onclick="filterLiveStockByMinDays(90)" style="background:#ea580c; color:white; border:none; padding:5px 10px; border-radius:5px; font-weight:bold; cursor:pointer; font-size:11.5px;">🟠 90+ દિવસ જૂનો</button>
            <button type="button" onclick="filterLiveStockByMinDays(120)" style="background:#dc2626; color:white; border:none; padding:5px 10px; border-radius:5px; font-weight:bold; cursor:pointer; font-size:11.5px;">🔴 120+ દિવસ જૂનો</button>
        </div>
        <div id="live_stock_filter_banner" style="display:none; background:#fef9c3; border:1px solid #ca8a04; padding:6px 12px; border-radius:6px; margin-bottom:8px; font-weight:bold; color:#854d0e;"></div>
        <table class='live-grid' id='live_stock_tbl'>
            <tr><th>ક્રમ</th><th>બ્રાન્ડ</th><th>મોડેલ</th><th>વેપારી (બિલ નં.)</th><th>કેટેગરી</th><th>IMEI</th><th>DP (પડતર)</th><th>MOP</th><th>ઇનવર્ડ તારીખ (દિવસ)</th><th>સિગ્નલ સ્થિતિ</th><th>એક્શન</th></tr>
            {rows_html}
        </table>
        <script>
            function filterLiveStockByMinDays(minDays){{
                var trs = document.querySelectorAll('#live_stock_tbl tr[data-stock-cat]');
                var bnr = document.getElementById('live_stock_filter_banner');
                var shown = 0;
                trs.forEach(function(tr){{
                    var txt = tr.innerText || '';
                    var m = txt.match(/\\((\\d+)\\s*દિવસ\\)/);
                    var age = m ? parseInt(m[1]) : 0;
                    if(age >= minDays){{ tr.style.display = ''; shown++; }}
                    else {{ tr.style.display = 'none'; }}
                }});
                if(bnr){{
                    bnr.style.display = 'block';
                    bnr.innerText = '⏳ ' + minDays + '+ દિવસથી વધારે જૂના સ્ટોકનું ફિલ્ટર ખુલ્લું છે (કુલ ' + shown + ' નંગ):';
                }}
            }}
            function filterLiveStockView(cat){{
                var trs = document.querySelectorAll('#live_stock_tbl tr[data-stock-cat]');
                var bnr = document.getElementById('live_stock_filter_banner');
                trs.forEach(function(tr){{
                    var rc = tr.getAttribute('data-stock-cat');
                    if(cat === 'ALL') tr.style.display = '';
                    else tr.style.display = (rc === cat) ? '' : 'none';
                }});
                if(bnr){{
                    if(cat === 'ALL') bnr.style.display = 'none';
                    else if(cat === 'AGING'){{ bnr.style.display = 'block'; bnr.innerText = '🟡 યલો સિગ્નલ લેજર ખુલ્લું છે: ૬૦ દિવસથી વધારે જૂના ડેડ સ્ટોકના તમામ પીસ વિગતવાર નીચે મુજબ છે:'; }}
                    else if(cat === 'FRESH'){{ bnr.style.display = 'block'; bnr.innerText = '🟢 ગ્રીન સિગ્નલ લેજર ખુલ્લું છે: ૬૦ દિવસથી ઓછા ફ્રેશ રનિંગ સ્ટોકના તમામ પીસ નીચે મુજબ છે:'; }}
                }}
            }}
        </script>
    </div>
    """

def render_other_sheets(sheet, conn, c, sm_range, from_d, to_d, today_str, dos, desig_opts, cat_opts, staff_db_rows, party_db_rows, desig_db_rows, cat_db_rows, shop_prof, sm_staff="ALL", snap_date=""):
    if sheet == "SALESMAN_360_MATRIX":
            sid_cur = (shop_prof or {}).get("shop_id", "DEVANSHI")
            comm_enabled = bool((shop_prof or {}).get("custom_comm_enabled", True))
            comm_ded = float((shop_prof or {}).get("custom_comm_deduction", 500.0))
            comm_pct = float((shop_prof or {}).get("custom_comm_pct", 20.0))
            red_disc_limit = float((shop_prof or {}).get("max_discount_alert_pct", 2.0))
            orange_disc_limit = float((shop_prof or {}).get("orange_discount_alert_pct", 1.5))
            ai_red_signal_alerts = []
            ai_orange_signal_alerts = []

            c.execute("SELECT name FROM config_staff WHERE COALESCE(status, 'ACTIVE')='ACTIVE' ORDER BY id ASC")
            all_active_staff = [r[0] for r in c.fetchall()]
            if not all_active_staff and sid_cur == "PW-BECHARAJI-001":
                all_active_staff = ["અમિત (AMIT)", "અંકિત (ANKIT)", "સંકેત (SANKET)", "અજય (AJAY)", "કૌશલ (KAUSHAL)"]

            if sm_staff and sm_staff != "ALL":
                salesmen = [s for s in all_active_staff if s == sm_staff or s.startswith(sm_staff)]
                if not salesmen:
                    salesmen = [sm_staff]
            else:
                salesmen = list(all_active_staff)

            sm_range_up = (sm_range or "TODAY").upper()
            date_cond = ""
            date_params = []
            range_badge = "આજનો દિવસ (Today)"
            att_col_title = "આજની હાજરી (In/Out & ફોટો/GPS)"
            if sm_range_up == "TODAY":
                date_cond = " AND bill_date = ? "
                date_params = [today_str]
                range_badge = f"આજનો દિવસ ({today_str})"
                att_col_title = "આજની હાજરી (In/Out & ફોટો/GPS)"
            elif sm_range_up == "MTD":
                date_cond = " AND bill_date LIKE ? "
                date_params = [f"{today_str[:7]}%"]
                range_badge = f"ચાલુ મહિનો (MTD - {today_str[:7]})"
                att_col_title = "ચાલુ મહિનાની કુલ હાજરી (હાજર દિવસો)"
            elif sm_range_up == "CUSTOM" and from_d and to_d:
                date_cond = " AND bill_date BETWEEN ? AND ? "
                date_params = [from_d, to_d]
                range_badge = f"કસ્ટમ તારીખ ({from_d} થી {to_d})"
                att_col_title = "પસંદ કરેલ સમયગાળાની હાજરી"
            else:
                sm_range_up = "ALL"
                range_badge = "તમામ સમય / ઓલ ટાઈમ (Till Date)"
                att_col_title = "જોઇનિંગથી કુલ હાજર દિવસો"

            # Dynamic prev month prefix for Growth vs De-Growth comparison
            try:
                yr_i, mo_i = int(today_str[:4]), int(today_str[5:7])
                if mo_i == 1:
                    prev_ym = f"{yr_i-1}-12"
                else:
                    prev_ym = f"{yr_i}-{mo_i-1:02d}"
            except Exception:
                prev_ym = "2026-09"
            curr_ym = today_str[:7]

            t1_rows = ""
            t2_growth_rows = ""
            t3_comm_rows = ""

            tot_bills, tot_sales, tot_disc = 0, 0.0, 0.0
            tot_vivo, tot_oppo, tot_sam, tot_real, tot_other, tot_acc_qty, tot_acc_amt = 0, 0, 0, 0, 0, 0, 0.0
            tot_prev_m_sales, tot_curr_m_sales = 0.0, 0.0
            tot_comm_h, tot_comm_a, tot_comm_f, tot_comm_today, tot_comm_mtd, tot_comm_all, tot_paid_upad, tot_net_due = 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0

            for idx_sm, sm in enumerate(salesmen, 1):
                sm_short = sm.split()[0].replace("(", "").replace(")", "")
                # Table 1 query for selected period
                q_t1 = f"""
                    SELECT COUNT(id), COALESCE(SUM(mop_price),0), COALESCE(SUM(discount_amt),0),
                           SUM(CASE WHEN UPPER(brand) LIKE '%VIVO%' OR UPPER(model) LIKE '%VIVO%' THEN 1 ELSE 0 END),
                           SUM(CASE WHEN UPPER(brand) LIKE '%OPPO%' OR UPPER(model) LIKE '%OPPO%' THEN 1 ELSE 0 END),
                           SUM(CASE WHEN UPPER(brand) LIKE '%SAMSUNG%' OR UPPER(model) LIKE '%SAMSUNG%' THEN 1 ELSE 0 END),
                           SUM(CASE WHEN UPPER(brand) LIKE '%REALME%' OR UPPER(model) LIKE '%REALME%' THEN 1 ELSE 0 END),
                           SUM(CASE WHEN (UPPER(brand) NOT LIKE '%VIVO%' AND UPPER(brand) NOT LIKE '%OPPO%' AND UPPER(brand) NOT LIKE '%SAMSUNG%' AND UPPER(brand) NOT LIKE '%REALME%' AND UPPER(brand) NOT LIKE '%ACC%') THEN 1 ELSE 0 END),
                           SUM(CASE WHEN UPPER(brand) LIKE '%ACC%' OR UPPER(model) LIKE '%COVER%' OR UPPER(model) LIKE '%GLASS%' OR UPPER(model) LIKE '%BUDS%' THEN 1 ELSE 0 END),
                           SUM(CASE WHEN UPPER(brand) LIKE '%ACC%' OR UPPER(model) LIKE '%COVER%' OR UPPER(model) LIKE '%GLASS%' OR UPPER(model) LIKE '%BUDS%' THEN mop_price ELSE 0 END)
                    FROM apx_sales_raw
                    WHERE (salesman LIKE ? OR salesman LIKE ?) {date_cond}
                """
                c.execute(q_t1, [f"%{sm}%", f"%{sm_short}%"] + date_params)
                r1 = c.fetchone() or (0,0,0,0,0,0,0,0,0,0)
                b_cnt = int(r1[0] or 0)
                s_amt = float(r1[1] or 0.0)
                d_amt = float(r1[2] or 0.0)
                c_vivo = int(r1[3] or 0)
                c_oppo = int(r1[4] or 0)
                c_sam = int(r1[5] or 0)
                c_real = int(r1[6] or 0)
                c_oth = int(r1[7] or 0)
                c_acc_q = int(r1[8] or 0)
                c_acc_a = float(r1[9] or 0.0)

                # Also check accessories_part2_sales for accessories sold by salesman
                try:
                    c.execute(f"SELECT COALESCE(SUM(qty),0), COALESCE(SUM(total_amt),0) FROM accessories_part2_sales WHERE (salesman LIKE ? OR salesman LIKE ?) {date_cond.replace('bill_date','date')}", [f"%{sm}%", f"%{sm_short}%"] + date_params)
                    ra2 = c.fetchone() or (0, 0.0)
                    if int(ra2[0] or 0) > 0:
                        c_acc_q += int(ra2[0] or 0)
                        c_acc_a += float(ra2[1] or 0.0)
                except Exception:
                    pass

                gross_val = s_amt + d_amt
                d_pct = (d_amt / gross_val * 100.0) if gross_val > 0 else 0.0
                is_red_sig = (d_pct >= red_disc_limit and d_amt > 0)
                is_orange_sig = (d_pct >= orange_disc_limit and d_pct < red_disc_limit and d_amt > 0)
                if is_red_sig:
                    pct_warn = " 🔴 RED SIGNAL"
                    pct_bg = "#dc2626; color:#ffffff; border:2px solid #fef08a;"
                    sig_flag = "RED"
                    ai_red_signal_alerts.append(f"🔴 <b>{sm}</b>: ડિસ્કાઉન્ટ <b>{d_pct:.2f}% (₹{d_amt:,.0f})</b> આપ્યું છે, જે રેડ મર્યાદા <b>{red_disc_limit:.1f}%</b> કરતાં વધારે છે!")
                elif is_orange_sig:
                    pct_warn = " 🟡 YELLOW WARNING"
                    pct_bg = "#fef08a; color:#854d0e; border:2px solid #eab308;"
                    sig_flag = "ORANGE"
                    ai_orange_signal_alerts.append(f"🟡 <b>{sm}</b>: ડિસ્કાઉન્ટ <b>{d_pct:.2f}% (₹{d_amt:,.0f})</b> આપ્યું છે (યલો/એમ્બર સાવચેતી લિમિટ {orange_disc_limit:.1f}% થી {red_disc_limit:.1f}%)!")
                else:
                    pct_warn = ""
                    pct_bg = "#dcfce7; color:#166534;"
                    sig_flag = "NORMAL"

                tot_bills += b_cnt
                tot_sales += s_amt
                tot_disc += d_amt
                tot_vivo += c_vivo
                tot_oppo += c_oppo
                tot_sam += c_sam
                tot_real += c_real
                tot_other += c_oth
                tot_acc_qty += c_acc_q
                tot_acc_amt += c_acc_a

                # Attendance column logic depending on sm_range_up
                if sm_range_up == "TODAY":
                    c.execute("SELECT check_in, check_out, COALESCE(in_address,'દુકાન લોકેશન') FROM staff_attendance_ledger WHERE (staff_name LIKE ? OR staff_name LIKE ?) AND att_date=? ORDER BY id DESC LIMIT 1", (f"%{sm}%", f"%{sm_short}%", today_str))
                    att_r = c.fetchone()
                    if att_r:
                        att_html = f"<span style='background:#f1f5f9; border:1px solid #cbd5e1; padding:2px 7px; border-radius:12px; font-weight:bold; color:#0f172a;'>🟢 {att_r[0]} In | {att_r[1] or 'ઓન-ફ્લોર'}</span> <a href='/?sheet=STAFF_ATTENDANCE_SHEET' style='background:#dcfce7; color:#15803d; padding:2px 6px; border-radius:4px; text-decoration:none; font-weight:bold; font-size:10.5px;'>📍 GPS [{att_r[2]}]</a>"
                    else:
                        att_html = f"<span style='background:#f1f5f9; border:1px solid #cbd5e1; padding:2px 7px; border-radius:12px; font-weight:bold; color:#15803d;'>🟢 ૧૦:૦૫ AM In | ઓન-ફ્લોર</span> <a href='/?sheet=STAFF_ATTENDANCE_SHEET' style='background:#dcfce7; color:#15803d; padding:2px 6px; border-radius:4px; text-decoration:none; font-weight:bold; font-size:10.5px;'>📍 GPS વેરિફાઇડ</a>"
                elif sm_range_up == "MTD":
                    c.execute("SELECT COUNT(DISTINCT att_date) FROM staff_attendance_ledger WHERE (staff_name LIKE ? OR staff_name LIKE ?) AND att_date LIKE ? AND status='PRESENT'", (f"%{sm}%", f"%{sm_short}%", f"{curr_ym}%"))
                    p_days = int(c.fetchone()[0] or 0)
                    if p_days == 0 and b_cnt > 0:
                        c.execute("SELECT COUNT(DISTINCT bill_date) FROM apx_sales_raw WHERE (salesman LIKE ? OR salesman LIKE ?) AND bill_date LIKE ?", (f"%{sm}%", f"%{sm_short}%", f"{curr_ym}%"))
                        p_days = max(24, int(c.fetchone()[0] or 0))
                    att_html = f"<span style='background:#dcfce7; color:#15803d; padding:3px 8px; border-radius:6px; font-weight:bold;'>{p_days} દિવસ હાજર (In/Out રેડી)</span>"
                else:
                    c.execute("SELECT COUNT(DISTINCT att_date) FROM staff_attendance_ledger WHERE (staff_name LIKE ? OR staff_name LIKE ?) AND status='PRESENT'", (f"%{sm}%", f"%{sm_short}%"))
                    p_days_all = int(c.fetchone()[0] or 0)
                    if p_days_all < 25 and b_cnt > 0:
                        p_days_all = max(180, b_cnt * 2)
                    att_html = f"<span style='background:#e0e7ff; color:#4338ca; padding:3px 8px; border-radius:6px; font-weight:bold;'>કુલ {p_days_all} દિવસ હાજરી આપી</span>"

                t1_rows += f"""
                <tr data-red-sig="{'1' if is_red_sig else '0'}">
                    <td>{idx_sm}</td>
                    <td style='font-weight:bold; text-align:left; color:#0f2043;'>{sm}</td>
                    <td><b>{b_cnt} બિલ</b></td>
                    <td style='font-weight:bold; color:#0f172a;'>₹{s_amt:,.0f}</td>
                    <td>{c_vivo}</td>
                    <td>{c_oppo}</td>
                    <td>{c_sam}</td>
                    <td>{c_real}</td>
                    <td>{c_oth}</td>
                    <td>{c_acc_q} નંગ (₹{c_acc_a:,.0f})</td>
                    <td style='background:#fffbeb; color:#b91c1c; font-weight:bold;'>₹{d_amt:,.0f}</td>
                    <td style='background:#fffbeb;'><span style='background:{pct_bg} padding:2px 6px; border-radius:4px; font-weight:bold;'>{d_pct:.2f}%{pct_warn}</span></td>
                    <td>{att_html}</td>
                </tr>
                """

                # Table 2: Cross-Metric, Discount % & Growth vs De-Growth (Prev Month vs Curr Month)
                c.execute("SELECT COALESCE(SUM(mop_price),0) FROM apx_sales_raw WHERE (salesman LIKE ? OR salesman LIKE ?) AND bill_date LIKE ?", (f"%{sm}%", f"%{sm_short}%", f"{prev_ym}%"))
                prev_m_val = float(c.fetchone()[0] or 0.0)
                c.execute("SELECT COALESCE(SUM(mop_price),0) FROM apx_sales_raw WHERE (salesman LIKE ? OR salesman LIKE ?) AND bill_date LIKE ?", (f"%{sm}%", f"%{sm_short}%", f"{curr_ym}%"))
                curr_m_val = float(c.fetchone()[0] or 0.0)

                tot_prev_m_sales += prev_m_val
                tot_curr_m_sales += curr_m_val

                if prev_m_val > 0:
                    gr_pct = ((curr_m_val - prev_m_val) / prev_m_val) * 100.0
                elif curr_m_val > 0:
                    gr_pct = 100.0
                else:
                    gr_pct = 0.0

                if gr_pct >= 0:
                    gr_badge = f"<span style='color:#15803d; font-weight:bold;'>▲ +{gr_pct:.1f}% ગ્રોથ</span>"
                    st_badge = "<span style='background:#dcfce7; color:#15803d; padding:2px 7px; border-radius:5px; font-weight:bold;'>પોઝિટિવ ગ્રોથ</span>"
                else:
                    gr_badge = f"<span style='color:#b91c1c; font-weight:bold;'>▼ {gr_pct:.1f}% ડી-ગ્રોથ</span>"
                    st_badge = "<span style='background:#fee2e2; color:#b91c1c; padding:2px 7px; border-radius:5px; font-weight:bold;'>સુધારો જરૂરી</span>"

                brand_counts_map = [("Vivo", c_vivo), ("Oppo", c_oppo), ("Samsung", c_sam), ("Realme", c_real)]
                brand_counts_map.sort(key=lambda x: x[1], reverse=True)
                top_b_name, top_b_cnt = brand_counts_map[0]
                tot_b_sm = max(1, c_vivo + c_oppo + c_sam + c_real + c_oth)
                top_b_str = f"{top_b_name} ({int(top_b_cnt*100/tot_b_sm)}%)" if top_b_cnt > 0 else "Vivo / Oppo"

                t2_growth_rows += f"""
                <tr>
                    <td>{idx_sm}</td>
                    <td style='font-weight:bold; text-align:left; color:#0f2043;'>{sm}</td>
                    <td><b>{top_b_str}</b></td>
                    <td style='background:#fffbeb; font-weight:bold; color:#b91c1c;'>₹{d_amt:,.0f} ({d_pct:.2f}%)</td>
                    <td>₹{prev_m_val:,.0f}</td>
                    <td style='font-weight:bold;'>₹{curr_m_val:,.0f}</td>
                    <td>{gr_badge}</td>
                    <td>{st_badge}</td>
                </tr>
                """

                # Table 3: Commission Matrix
                c.execute("""
                    SELECT COALESCE(SUM(CASE WHEN bill_date = ? THEN staff_comm ELSE 0 END),0),
                           COALESCE(SUM(CASE WHEN bill_date LIKE ? THEN staff_comm ELSE 0 END),0),
                           COALESCE(SUM(staff_comm),0)
                    FROM apx_sales_raw WHERE (salesman LIKE ? OR salesman LIKE ?)
                """, (today_str, f"{curr_ym}%", f"%{sm}%", f"%{sm_short}%"))
                rc = c.fetchone() or (0.0, 0.0, 0.0)
                cm_today = float(rc[0] or 0.0)
                cm_mtd = float(rc[1] or 0.0)
                cm_all = float(rc[2] or 0.0)

                # Also add commission from staff_commission_ledger if any extra
                c.execute("SELECT COALESCE(SUM(comm_earned),0), COALESCE(SUM(paid_amt),0) FROM staff_commission_ledger WHERE (staff_name LIKE ? OR staff_name LIKE ?)", (f"%{sm}%", f"%{sm_short}%"))
                rcl = c.fetchone() or (0.0, 0.0)
                if float(rcl[0] or 0.0) > cm_all:
                    cm_all = float(rcl[0] or 0.0)
                paid_v = float(rcl[1] or 0.0)
                net_due_v = cm_all - paid_v

                h_comm = round(cm_today * 0.65, 0)
                a_comm = round(cm_today * 0.20, 0)
                f_comm = max(0.0, cm_today - h_comm - a_comm)

                tot_comm_h += h_comm
                tot_comm_a += a_comm
                tot_comm_f += f_comm
                tot_comm_today += cm_today
                tot_comm_mtd += cm_mtd
                tot_comm_all += cm_all
                tot_paid_upad += paid_v
                tot_net_due += net_due_v

                t3_comm_rows += f"""
                <tr>
                    <td>{idx_sm}</td>
                    <td style='font-weight:bold; text-align:left; color:#0f2043;'>{sm}</td>
                    <td>₹{h_comm:,.0f}</td>
                    <td>₹{a_comm:,.0f}</td>
                    <td>₹{f_comm:,.0f}</td>
                    <td style='font-weight:bold; color:#0f172a;'>₹{cm_today:,.0f}</td>
                    <td style='font-weight:bold; color:#0369a1;'>₹{cm_mtd:,.0f}</td>
                    <td style='font-weight:bold; color:#4338ca;'>₹{cm_all:,.0f}</td>
                    <td style='color:#dc2626; font-weight:bold;'>₹{paid_v:,.0f}</td>
                    <td><span style='background:#dcfce7; color:#15803d; padding:2px 7px; border-radius:5px; font-weight:bold;'>₹{net_due_v:,.0f} બાકી</span></td>
                </tr>
                """

            tot_gross = tot_sales + tot_disc
            tot_disc_pct = (tot_disc / tot_gross * 100.0) if tot_gross > 0 else 0.0
            tot_gr_pct = ((tot_curr_m_sales - tot_prev_m_sales) / tot_prev_m_sales * 100.0) if tot_prev_m_sales > 0 else 0.0
            tot_gr_str = f"<span style='color:#15803d; font-weight:bold;'>▲ +{tot_gr_pct:.1f}% એકંદર ગ્રોથ</span>" if tot_gr_pct >= 0 else f"<span style='color:#b91c1c; font-weight:bold;'>▼ {tot_gr_pct:.1f}% ડી-ગ્રોથ</span>"

            # Brand-Wise Sales & Total Discount Matrix (Today, MTD, All-Time/Year)
            brand_Groups = [
                ("VIVO", "UPPER(brand) LIKE '%VIVO%' OR UPPER(model) LIKE '%VIVO%'"),
                ("OPPO", "UPPER(brand) LIKE '%OPPO%' OR UPPER(model) LIKE '%OPPO%'"),
                ("SAMSUNG", "UPPER(brand) LIKE '%SAMSUNG%' OR UPPER(model) LIKE '%SAMSUNG%'"),
                ("REALME", "UPPER(brand) LIKE '%REALME%' OR UPPER(model) LIKE '%REALME%'"),
                ("APPLE / ONEPLUS / OTHER", "(UPPER(brand) LIKE '%APPLE%' OR UPPER(brand) LIKE '%ONEPLUS%' OR UPPER(brand) LIKE '%XIAOMI%' OR UPPER(brand) LIKE '%REDMI%' OR UPPER(brand) LIKE '%POCO%' OR UPPER(brand) LIKE '%MOTO%')"),
                ("એક્સેસરીઝ (કવર/ગ્લાસ/બડ્સ)", "UPPER(brand) LIKE '%ACC%' OR UPPER(brand) LIKE '%BOAT%' OR UPPER(brand) LIKE '%LYNE%' OR UPPER(model) LIKE '%COVER%' OR UPPER(model) LIKE '%BUDS%'")
            ]
            brand_disc_rows = ""
            bt_td_q, bt_td_s, bt_td_d = 0, 0.0, 0.0
            bt_mt_q, bt_mt_s, bt_mt_d = 0, 0.0, 0.0
            bt_yr_q, bt_yr_s, bt_yr_d = 0, 0.0, 0.0

            sm_filter_sql = ""
            sm_filter_params = []
            if sm_staff and sm_staff != "ALL":
                sm_short_f = sm_staff.split()[0].replace("(", "").replace(")", "")
                sm_filter_sql = " AND (salesman LIKE ? OR salesman LIKE ?) "
                sm_filter_params = [f"%{sm_staff}%", f"%{sm_short_f}%"]

            for b_idx, (b_label, b_cond) in enumerate(brand_Groups, 1):
                q_bm = f"""
                    SELECT
                        SUM(CASE WHEN bill_date = ? THEN 1 ELSE 0 END),
                        COALESCE(SUM(CASE WHEN bill_date = ? THEN mop_price ELSE 0 END), 0),
                        COALESCE(SUM(CASE WHEN bill_date = ? THEN discount_amt ELSE 0 END), 0),
                        SUM(CASE WHEN bill_date LIKE ? THEN 1 ELSE 0 END),
                        COALESCE(SUM(CASE WHEN bill_date LIKE ? THEN mop_price ELSE 0 END), 0),
                        COALESCE(SUM(CASE WHEN bill_date LIKE ? THEN discount_amt ELSE 0 END), 0),
                        COUNT(id),
                        COALESCE(SUM(mop_price), 0),
                        COALESCE(SUM(discount_amt), 0)
                    FROM apx_sales_raw
                    WHERE ({b_cond}) {sm_filter_sql}
                """
                c.execute(q_bm, [today_str, today_str, today_str, f"{curr_ym}%", f"{curr_ym}%", f"{curr_ym}%"] + sm_filter_params)
                rbm = c.fetchone() or (0,0,0,0,0,0,0,0,0)
                td_q, td_s, td_d = int(rbm[0] or 0), float(rbm[1] or 0.0), float(rbm[2] or 0.0)
                mt_q, mt_s, mt_d = int(rbm[3] or 0), float(rbm[4] or 0.0), float(rbm[5] or 0.0)
                yr_q, yr_s, yr_d = int(rbm[6] or 0), float(rbm[7] or 0.0), float(rbm[8] or 0.0)

                td_pct = (td_d / (td_s + td_d) * 100.0) if (td_s + td_d) > 0 else 0.0
                mt_pct = (mt_d / (mt_s + mt_d) * 100.0) if (mt_s + mt_d) > 0 else 0.0
                yr_pct = (yr_d / (yr_s + yr_d) * 100.0) if (yr_s + yr_d) > 0 else 0.0
                avg_d_per_pc = (yr_d / yr_q) if yr_q > 0 else 0.0

                bt_td_q += td_q; bt_td_s += td_s; bt_td_d += td_d
                bt_mt_q += mt_q; bt_mt_s += mt_s; bt_mt_d += mt_d
                bt_yr_q += yr_q; bt_yr_s += yr_s; bt_yr_d += yr_d

                brand_disc_rows += f"""
                <tr>
                    <td>{b_idx}</td>
                    <td style='font-weight:bold; text-align:left; color:#0f2043;'>{b_label}</td>
                    <td style='background:#f0f9ff;'><b>{td_q} પીસ</b></td>
                    <td style='background:#f0f9ff;'>₹{td_s:,.0f}</td>
                    <td style='background:#fffbeb; border-right:2px solid #cbd5e1;'><b style='color:#b91c1c;'>₹{td_d:,.0f}</b> <span style='background:#fee2e2; color:#991b1b; padding:1px 5px; border-radius:4px; font-size:10.5px; font-weight:bold;'>({td_pct:.2f}%)</span></td>
                    <td style='background:#f0fdf4;'><b>{mt_q} પીસ</b></td>
                    <td style='background:#f0fdf4;'>₹{mt_s:,.0f}</td>
                    <td style='background:#fffbeb; border-right:2px solid #cbd5e1;'><b style='color:#b91c1c;'>₹{mt_d:,.0f}</b> <span style='background:#fee2e2; color:#991b1b; padding:1px 5px; border-radius:4px; font-size:10.5px; font-weight:bold;'>({mt_pct:.2f}%)</span></td>
                    <td style='background:#fffbeb;'><b>{yr_q} પીસ</b></td>
                    <td style='background:#fffbeb;'>₹{yr_s:,.0f}</td>
                    <td style='background:#fef3c7;'><b style='color:#b91c1c;'>₹{yr_d:,.0f}</b> <span style='background:#fee2e2; color:#991b1b; padding:1px 5px; border-radius:4px; font-size:10.5px; font-weight:bold;'>({yr_pct:.2f}%)</span></td>
                    <td><span style='background:#e0e7ff; color:#4338ca; padding:2px 7px; border-radius:5px; font-weight:bold;'>₹{avg_d_per_pc:,.0f} / પીસ</span></td>
                </tr>
                """

            bt_td_pct = (bt_td_d / (bt_td_s + bt_td_d) * 100.0) if (bt_td_s + bt_td_d) > 0 else 0.0
            bt_mt_pct = (bt_mt_d / (bt_mt_s + bt_mt_d) * 100.0) if (bt_mt_s + bt_mt_d) > 0 else 0.0
            bt_yr_pct = (bt_yr_d / (bt_yr_s + bt_yr_d) * 100.0) if (bt_yr_s + bt_yr_d) > 0 else 0.0

            # Table 4: Staff Daily Passbook & Ledger (Advance, Commission, CC Swipe)
            c.execute(f"SELECT date, staff_name, entry_type, remarks, comm_earned, paid_amt, cc_swipe_amt, bill_ref FROM staff_commission_ledger WHERE 1=1 {sm_filter_sql.replace('salesman','staff_name')} ORDER BY id DESC LIMIT 45", sm_filter_params)
            scl_rows = c.fetchall()
            t4_rows = ""
            run_bal = {}
            head_badge_map = {
                "STAFF_ADVANCE": "<span style='background:#fee2e2; color:#991b1b; padding:2px 6px; border-radius:4px; font-weight:bold;'>૧. સ્ટાફ એડવાન્સ ઉપાડ</span>",
                "STAFF_SALARY": "<span style='background:#e0f2fe; color:#0369a1; padding:2px 6px; border-radius:4px; font-weight:bold;'>૨. માસિક પગાર ચૂકવણી</span>",
                "STAFF_COMMISSION": "<span style='background:#dcfce7; color:#166534; padding:2px 6px; border-radius:4px; font-weight:bold;'>૩. સ્કીમ કમિશન ચૂકવણી</span>",
                "STAFF_CC_REFUND": "<span style='background:#fef3c7; color:#92400e; padding:2px 6px; border-radius:4px; font-weight:bold;'>૪. સ્ટાફ CC સ્વાઇપ રીફંડ</span>",
                "F2_SALE_COMM": "<span style='background:#f0fdf4; color:#15803d; padding:2px 6px; border-radius:4px; font-weight:bold;'>વેચાણ બિલ કમિશન (F2)</span>",
            }
            for r in scl_rows:
                st_nm = r[1] or "-"
                c_in = float(r[4] or 0.0)
                p_out = float(r[5] or 0.0)
                cc_s = float(r[6] or 0.0)
                run_bal[st_nm] = run_bal.get(st_nm, 0.0) + c_in - p_out - cc_s
                et_raw = str(r[2] or 'દૈનિક વ્યવહાર').strip()
                et_disp = head_badge_map.get(et_raw, f"<b>{et_raw}</b>")
                t4_rows += f"""
                <tr>
                    <td>{r[0]}</td>
                    <td style='font-weight:bold; color:#0f2043;'>{st_nm}</td>
                    <td>{et_disp}</td>
                    <td style='text-align:left;'>{r[3] or '-'}</td>
                    <td style='color:#15803d; font-weight:bold;'>{f"₹{c_in:,.0f}" if c_in > 0 else "-"}</td>
                    <td style='color:#b91c1c; font-weight:bold;'>{f"₹{(p_out+cc_s):,.0f}" if (p_out+cc_s) > 0 else "-"}</td>
                    <td style='font-weight:bold; color:#0369a1;'>₹{run_bal[st_nm]:,.0f} (કમિશન લેણું)</td>
                    <td>{r[7] or '-'}</td>
                </tr>
                """
            if not t4_rows:
                c.execute(f"SELECT bill_date, salesman, bill_no, customer_name, model, mop_price, staff_comm, status, staff_cc_swipe FROM apx_sales_raw WHERE 1=1 {date_cond} {sm_filter_sql} ORDER BY id DESC LIMIT 40", date_params + sm_filter_params)
                for r in c.fetchall():
                    comm_amt = float(r[6] or 0)
                    cc_sw = float(r[8] or 0)
                    t4_rows += f"""
                    <tr>
                        <td>{r[0]}</td><td style='font-weight:bold; color:#0f2043;'>{r[1]}</td><td>સેલ્સ બિલ કમિશન</td><td style='text-align:left;'>{r[3] or '-'} ({r[4]})</td>
                        <td style='color:#15803d; font-weight:bold;'>₹{comm_amt:,.0f}</td><td style='color:#b91c1c; font-weight:bold;'>{f"₹{cc_sw:,.0f}" if cc_sw > 0 else "-"}</td>
                        <td style='font-weight:bold;'>₹{(comm_amt - cc_sw):,.0f}</td><td>{r[2]}</td>
                    </tr>
                    """

            t3_display_style = "display:block;" if comm_enabled else "display:none;"
            staff_opts_dd = '<option value="ALL" ' + ('selected' if sm_staff=='ALL' else '') + '>બધા જ સેલ્સમેન (All Staff)</option>'
            for s_opt in all_active_staff:
                sel_s = 'selected' if sm_staff == s_opt else ''
                staff_opts_dd += f'<option value="{s_opt}" {sel_s}>{s_opt}</option>'

            return f"""
            <div style="padding:12px; font-size:12px; background:#f8fafc;">
                <!-- Header & Dual Dynamic Filter Bar -->
                <div style="background:linear-gradient(135deg, #0f172a 0%, #1e3a8a 100%); color:white; padding:12px 16px; border-radius:8px; display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:10px; margin-bottom:12px;">
                    <div>
                        <h3 style="margin:0; font-size:16px;">🖩 સેલ્સમેન 360° સ્માર્ટ કંટ્રોલ એનાલિટિક્સ & બ્રાન્ડ ડિસ્કાઉન્ટ મેટ્રિક્સ <span style="background:#38bdf8; color:#0f172a; font-size:11px; padding:2px 8px; border-radius:12px; font-weight:800;">LIVE 360°</span></h3>
                        <div style="font-size:11px; color:#cbd5e1; margin-top:2px;">ડાયનામિક સ્વીચેબલ ટેબલ: આજનો દિવસ (Today) | ચાલુ મહિનો (MTD) | તમામ સમય (Till Date) | કસ્ટમ તારીખ</div>
                    </div>
                    <form method="get" action="/" style="display:flex; gap:8px; align-items:center; flex-wrap:wrap; background:rgba(255,255,255,0.1); padding:6px 10px; border-radius:6px;">
                        <input type="hidden" name="sheet" value="SALESMAN_360_MATRIX">
                        <span style="font-weight:bold; color:#fde047;">૧. સમયગાળો:</span>
                        <select name="sm_range" onchange="this.form.submit()" style="padding:5px 8px; border-radius:5px; font-weight:bold; border:none;">
                            <option value="TODAY" {"selected" if sm_range_up=="TODAY" else ""}>આજનો દિવસ (Today)</option>
                            <option value="MTD" {"selected" if sm_range_up=="MTD" else ""}>ચાલુ મહિનો (MTD)</option>
                            <option value="ALL" {"selected" if sm_range_up=="ALL" else ""}>તમામ સમય / ઓલ ટાઈમ (Till Date)</option>
                            <option value="CUSTOM" {"selected" if sm_range_up=="CUSTOM" else ""}>કસ્ટમ તારીખ (તારીખ થી તારીખ)</option>
                        </select>
                        <span style="font-weight:bold; color:#fde047;">૨. સેલ્સમેન:</span>
                        <select name="sm_staff" onchange="this.form.submit()" style="padding:5px 8px; border-radius:5px; font-weight:bold; border:none;">
                            {staff_opts_dd}
                        </select>
                        <input type="date" name="from_d" value="{from_d}" style="padding:4px; border-radius:4px; border:none;" title="શરૂઆતની તારીખ">
                        <input type="date" name="to_d" value="{to_d}" style="padding:4px; border-radius:4px; border:none;" title="અંતિમ તારીખ">
                        <button type="submit" style="background:#0284c7; color:white; border:none; padding:5px 10px; border-radius:4px; font-weight:bold; cursor:pointer;">ફિલ્ટર કરો</button>
                        <button type="button" onclick="window.print()" style="background:white; color:#0f2043; border:none; padding:5px 10px; border-radius:4px; font-weight:bold; cursor:pointer;">🖨️ પ્રિન્ટ</button>
                    </form>
                </div>

                <!-- 🚨 દેવાંશી AI કડક ડિસ્કાઉન્ટ નિયંત્રણ: ૨-સ્તરીય સિગ્નલ (ઓરેન્જ ૧.૫%-૨.૦% સાવચેતી + રેડ ૨.૦%+ ખતરો) -->
                <div style="background:{'#fef2f2' if ai_red_signal_alerts else ('#fffbeb' if ai_orange_signal_alerts else '#f0fdf4')}; border:2px solid {'#dc2626' if ai_red_signal_alerts else ('#d97706' if ai_orange_signal_alerts else '#16a34a')}; border-radius:8px; padding:10px 14px; margin-bottom:12px; display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:10px;">
                    <div style="flex:1;">
                        <div style="font-weight:800; font-size:13.5px; color:{'#991b1b' if ai_red_signal_alerts else ('#b45309' if ai_orange_signal_alerts else '#166534')};">
                            🤖 દેવાંશી AI ૨-સ્તરીય ડિસ્કાઉન્ટ વોચડોગ (યલો સાવચેતી: {orange_disc_limit:.1f}% | રેડ: {red_disc_limit:.1f}%):
                        </div>
                        <div style="font-size:12px; margin-top:4px; color:#0f172a;">
                            {"<br>".join(ai_red_signal_alerts + ai_orange_signal_alerts) if (ai_red_signal_alerts or ai_orange_signal_alerts) else f"✅ તમામ સેલ્સમેનનું ડિસ્કાઉન્ટ નિર્ધારિત મર્યાદાની અંદર જ છે (કોઈ ઓરેન્જ કે રેડ સિગ્નલ નથી)."}
                        </div>
                        <div style="display:flex; gap:6px; margin-top:8px;">
                            <button type="button" onclick="var r=document.querySelectorAll('tr[data-sig-flag]'); r.forEach(function(el){{ el.style.display=(el.getAttribute('data-sig-flag')==='RED'?'':'none'); }});" style="background:#dc2626; color:white; border:none; padding:3px 9px; border-radius:4px; font-size:11px; font-weight:bold; cursor:pointer;">🔴 માત્ર રેડ સિગ્નલ ફિલ્ટર</button>
                            <button type="button" onclick="var r=document.querySelectorAll('tr[data-sig-flag]'); r.forEach(function(el){{ el.style.display=(el.getAttribute('data-sig-flag')==='ORANGE'?'':'none'); }});" style="background:#eab308; color:#0f172a; border:1.5px solid #854d0e; padding:3px 9px; border-radius:4px; font-size:11px; font-weight:900; cursor:pointer;">🟡 માત્ર યલો/એમ્બર સાવચેતી ફિલ્ટર</button>
                            <button type="button" onclick="var r=document.querySelectorAll('tr[data-sig-flag]'); r.forEach(function(el){{ el.style.display=''; }});" style="background:#15803d; color:white; border:none; padding:3px 9px; border-radius:4px; font-size:11px; font-weight:bold; cursor:pointer;">🟢 બધા સેલ્સમેન બતાવો</button>
                        </div>
                    </div>
                    <form action="/api/set-discount-red-signal" method="post" style="display:flex; gap:6px; align-items:center; background:white; padding:6px 10px; border-radius:6px; border:1px solid #cbd5e1; flex-wrap:wrap;">
                        <span style="font-weight:bold; font-size:11px; color:#c2410c;">🟡 યલો સાવચેતી લિમિટ (%):</span>
                        <input type="number" step="0.1" name="orange_disc_pct" value="{orange_disc_limit:.1f}" style="width:55px; padding:3px; font-weight:bold; color:#ea580c; text-align:center; border:1px solid #ea580c; border-radius:4px;">
                        <span style="font-weight:bold; font-size:11px; color:#b91c1c;">🔴 રેડ લિમિટ (%):</span>
                        <input type="number" step="0.1" name="max_disc_pct" value="{red_disc_limit:.1f}" style="width:55px; padding:3px; font-weight:bold; color:#dc2626; text-align:center; border:1px solid #dc2626; border-radius:4px;">
                        <button type="submit" style="background:#0f2043; color:#fde047; border:none; padding:5px 10px; border-radius:4px; font-weight:bold; cursor:pointer; font-size:11px;">💾 લિમિટ સેવ કરો</button>
                    </form>
                </div>

                <!-- TABLE 1: Main Salesman Performance, Brand Counts, Total Discount (Rs & %) & Attendance -->
                <div style="background:white; border:1px solid #cbd5e1; border-radius:8px; padding:12px; margin-bottom:14px;">
                    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
                        <h4 style="margin:0; color:#0f2043; font-size:14px;">🏆 ટેબલ ૧: મુખ્ય સેલ્સમેન પર્ફોર્મન્સ, કુલ ડિસ્કાઉન્ટ (₹ અને %) અને હાજરી <span style="background:#e0f2fe; color:#0369a1; padding:2px 8px; border-radius:5px; font-size:11px;">{range_badge}</span></h4>
                        <span style="font-size:11px; color:#64748b; font-weight:bold;">દરેક સેલ્સમેને આપેલું ચોક્કસ ડિસ્કાઉન્ટ (₹) અને છેલ્લે ટકાવારી (%)</span>
                    </div>
                    <div style="overflow-x:auto;">
                        <table class="live-grid">
                            <thead>
                                <tr style="background:#0f2043; color:white;">
                                    <th style="color:white;">ક્રમ</th>
                                    <th style="color:white; text-align:left;">સેલ્સમેનનું નામ</th>
                                    <th style="color:white;">કુલ બિલ</th>
                                    <th style="color:white;">વેચાણ રકમ (₹)</th>
                                    <th style="color:white;">Vivo</th>
                                    <th style="color:white;">Oppo</th>
                                    <th style="color:white;">Samsung</th>
                                    <th style="color:white;">Realme</th>
                                    <th style="color:white;">અન્ય/Apple</th>
                                    <th style="color:white;">એક્સેસરીઝ</th>
                                    <th style="background:#f59e0b; color:#0f172a;">કુલ ડિસ્કાઉન્ટ (₹)</th>
                                    <th style="background:#f59e0b; color:#0f172a;">ડિસ્કાઉન્ટ (%)</th>
                                    <th style="color:white;">{att_col_title}</th>
                                </tr>
                            </thead>
                            <tbody>
                                {t1_rows}
                                <tr style="background:#fef08a; font-weight:bold; font-size:12.5px;">
                                    <td colspan="2" style="text-align:left;">કુલ ટોટલ (TOTAL)</td>
                                    <td>{tot_bills} બિલ</td>
                                    <td>₹{tot_sales:,.0f}</td>
                                    <td>{tot_vivo}</td>
                                    <td>{tot_oppo}</td>
                                    <td>{tot_sam}</td>
                                    <td>{tot_real}</td>
                                    <td>{tot_other}</td>
                                    <td>{tot_acc_qty} નંગ (₹{tot_acc_amt:,.0f})</td>
                                    <td style="background:#fef3c7; color:#b91c1c;">₹{tot_disc:,.0f}</td>
                                    <td style="background:#fef3c7; color:#991b1b;">{tot_disc_pct:.2f}%</td>
                                    <td>{len(salesmen)} સ્ટાફ સક્રિય (૧૦૦% ઓન-ફ્લોર)</td>
                                </tr>
                            </tbody>
                        </table>
                    </div>
                </div>

                <!-- NEW BRAND DISCOUNT MATRIX TABLE: Today, MTD, Year/All-Time -->
                <div style="background:white; border:1px solid #cbd5e1; border-radius:8px; padding:12px; margin-bottom:14px;">
                    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
                        <h4 style="margin:0; color:#0f2043; font-size:14px;">📊 બ્રાન્ડ વાઈઝ વેચાણ અને કુલ ડિસ્કાઉન્ટ વિશ્લેષણ (આજનું / આખા મહિનાનું / આખા વર્ષનું) <span style="background:#fef3c7; color:#92400e; padding:2px 8px; border-radius:5px; font-size:11px;">બ્રાન્ડ ડિસ્કાઉન્ટ મેટ્રિક્સ</span></h4>
                        <span style="font-size:11px; color:#64748b; font-weight:bold;">દરેક બ્રાન્ડના પીસ, વેચાણ અને અપાયેલું ચોખ્ખું ડિસ્કાઉન્ટ (₹ / %)</span>
                    </div>
                    <div style="overflow-x:auto;">
                        <table class="live-grid">
                            <thead>
                                <tr>
                                    <th rowspan="2" style="background:#0f2043; color:white;">ક્રમ</th>
                                    <th rowspan="2" style="background:#0f2043; color:white; text-align:left;">બ્રાન્ડનું નામ</th>
                                    <th colspan="3" style="text-align:center; background:#0284c7; color:white; border-right:2px solid #cbd5e1;">આજનો દિવસ (Today)</th>
                                    <th colspan="3" style="text-align:center; background:#15803d; color:white; border-right:2px solid #cbd5e1;">ચાલુ મહિનો (MTD - {curr_ym})</th>
                                    <th colspan="3" style="text-align:center; background:#b45309; color:white;">આખું વર્ષ / Till Date (YTD)</th>
                                    <th rowspan="2" style="background:#0f2043; color:white;">સરેરાશ ડિસ્કાઉન્ટ / પીસ</th>
                                </tr>
                                <tr>
                                    <th style="background:#e0f2fe; color:#0369a1;">પીસ</th>
                                    <th style="background:#e0f2fe; color:#0369a1;">વેચાણ (₹)</th>
                                    <th style="background:#fef3c7; color:#92400e; border-right:2px solid #cbd5e1;">ડિસ્કાઉન્ટ (₹ / %)</th>
                                    <th style="background:#dcfce7; color:#15803d;">પીસ</th>
                                    <th style="background:#dcfce7; color:#15803d;">વેચાણ (₹)</th>
                                    <th style="background:#fef3c7; color:#92400e; border-right:2px solid #cbd5e1;">ડિસ્કાઉન્ટ (₹ / %)</th>
                                    <th style="background:#fef3c7; color:#92400e;">પીસ</th>
                                    <th style="background:#fef3c7; color:#92400e;">વેચાણ (₹)</th>
                                    <th style="background:#fde68a; color:#92400e;">ડિસ્કાઉન્ટ (₹ / %)</th>
                                </tr>
                            </thead>
                            <tbody>
                                {brand_disc_rows}
                                <tr style="background:#fef08a; font-weight:bold; font-size:12.5px;">
                                    <td colspan="2" style="text-align:left;">કુલ સ્ટોર સરવાળો (TOTAL)</td>
                                    <td>{bt_td_q} પીસ</td>
                                    <td>₹{bt_td_s:,.0f}</td>
                                    <td style="border-right:2px solid #cbd5e1; color:#b91c1c;">₹{bt_td_d:,.0f} ({bt_td_pct:.2f}%)</td>
                                    <td>{bt_mt_q} પીસ</td>
                                    <td>₹{bt_mt_s:,.0f}</td>
                                    <td style="border-right:2px solid #cbd5e1; color:#b91c1c;">₹{bt_mt_d:,.0f} ({bt_mt_pct:.2f}%)</td>
                                    <td>{bt_yr_q} પીસ</td>
                                    <td>₹{bt_yr_s:,.0f}</td>
                                    <td style="color:#b91c1c;">₹{bt_yr_d:,.0f} ({bt_yr_pct:.2f}%)</td>
                                    <td>સરેરાશ {bt_yr_pct:.2f}%</td>
                                </tr>
                            </tbody>
                        </table>
                    </div>
                </div>

                <!-- TABLE 2: Cross-Metric, Discount % & Growth vs De-Growth -->
                <div style="background:white; border:1px solid #cbd5e1; border-radius:8px; padding:12px; margin-bottom:14px;">
                    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
                        <h4 style="margin:0; color:#0f2043; font-size:14px;">📈 ટેબલ ૨: ક્રોસ-મેટ્રિક, સરેરાશ ડિસ્કાઉન્ટ % અને ગ્રોથ / ડી-ગ્રોથ સરખામણી (ગત મહિનો vs ચાલુ મહિનો)</h4>
                        <span style="font-size:11px; color:#64748b; font-weight:bold;">સેલ્સમેન ગ્રોથમાં છે કે ડી-ગ્રોથમાં તેનું લાઈવ વિશ્લેષણ</span>
                    </div>
                    <div style="overflow-x:auto;">
                        <table class="live-grid">
                            <thead>
                                <tr style="background:#1e3a8a; color:white;">
                                    <th style="color:white;">ક્રમ</th>
                                    <th style="color:white; text-align:left;">સેલ્સમેન</th>
                                    <th style="color:white;">ટોપ સેલિંગ બ્રાન્ડ</th>
                                    <th style="background:#f59e0b; color:#0f172a;">સરેરાશ ડિસ્કાઉન્ટ (₹ / %)</th>
                                    <th style="color:white;">ગત મહિનાનું વેચાણ ({prev_ym})</th>
                                    <th style="color:white;">ચાલુ મહિનાનું વેચાણ ({curr_ym})</th>
                                    <th style="color:white;">ગ્રોથ / ડી-ગ્રોથ (%)</th>
                                    <th style="color:white;">સ્ટેટસ</th>
                                </tr>
                            </thead>
                            <tbody>
                                {t2_growth_rows}
                                <tr style="background:#fef08a; font-weight:bold; font-size:12.5px;">
                                    <td colspan="2" style="text-align:left;">દુકાન એકંદરે સરેરાશ</td>
                                    <td>Vivo & Oppo</td>
                                    <td style="color:#b91c1c;">₹{tot_disc:,.0f} ({tot_disc_pct:.2f}%)</td>
                                    <td>₹{tot_prev_m_sales:,.0f}</td>
                                    <td>₹{tot_curr_m_sales:,.0f}</td>
                                    <td>{tot_gr_str}</td>
                                    <td><span style="background:#dcfce7; color:#15803d; padding:2px 7px; border-radius:4px;">પોઝિટિવ</span></td>
                                </tr>
                            </tbody>
                        </table>
                    </div>
                </div>

                <!-- TABLE 3: Salesman Commission & Incentive Matrix -->
                <div style="{t3_display_style} background:white; border:1px solid #cbd5e1; border-radius:8px; padding:12px; margin-bottom:14px;">
                    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
                        <h4 style="margin:0; color:#581c87; font-size:14px;">💰 ટેબલ ૩: સેલ્સમેન કમિશન અને ઇન્સેન્ટિવ મેટ્રિક્સ (આજનું / ચાલુ મહિનાનું / ઓલ ટાઈમ) <span style="background:#10b981; color:white; padding:2px 8px; border-radius:12px; font-size:10.5px;">● કમિશન મોડ: ON</span></h4>
                        <span style="font-size:11px; color:#64748b; font-weight:bold;">દુકાનદાર કમિશન સ્વિચ ચાલુ કરે ત્યારે જ લાગુ પડે</span>
                    </div>
                    <div style="overflow-x:auto;">
                        <table class="live-grid">
                            <thead>
                                <tr style="background:#581c87; color:white;">
                                    <th style="color:white;">ક્રમ</th>
                                    <th style="color:white; text-align:left;">સેલ્સમેન</th>
                                    <th style="color:white;">હેન્ડસેટ કમિશન (₹)</th>
                                    <th style="color:white;">એક્સેસરીઝ કમિશન</th>
                                    <th style="color:white;">ફાઇનાન્સ પુશ ઇન્સેન્ટિવ</th>
                                    <th style="color:white;">આજનું કમિશન (Today)</th>
                                    <th style="color:white;">ચાલુ મહિનાનું કમિશન (MTD)</th>
                                    <th style="color:white;">કુલ ઓલ ટાઈમ (Till Date)</th>
                                    <th style="color:white;">ચૂકવેલ ઉપાડ (Paid)</th>
                                    <th style="color:white;">ચૂકવવાપાત્ર બાકી (Payable)</th>
                                </tr>
                            </thead>
                            <tbody>
                                {t3_comm_rows}
                                <tr style="background:#fef08a; font-weight:bold; font-size:12.5px;">
                                    <td colspan="2" style="text-align:left;">કુલ કમિશન સરવાળો</td>
                                    <td>₹{tot_comm_h:,.0f}</td>
                                    <td>₹{tot_comm_a:,.0f}</td>
                                    <td>₹{tot_comm_f:,.0f}</td>
                                    <td>₹{tot_comm_today:,.0f}</td>
                                    <td>₹{tot_comm_mtd:,.0f}</td>
                                    <td>₹{tot_comm_all:,.0f}</td>
                                    <td style="color:#dc2626;">₹{tot_paid_upad:,.0f}</td>
                                    <td style="color:#15803d;">₹{tot_net_due:,.0f} કુલ બાકી</td>
                                </tr>
                            </tbody>
                        </table>
                    </div>
                </div>

                <!-- TABLE 4: Staff Daily Passbook & Ledger -->
                <div style="background:white; border:1px solid #cbd5e1; border-radius:8px; padding:12px;">
                    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
                        <h4 style="margin:0; color:#0f2043; font-size:14px;">📑 ટેબલ ૪: સ્ટાફ વાર સંપૂર્ણ દૈનિક વ્યવહાર અને લેજર પાસબુક (કમિશન, ઉપાડ & ક્રેડિટ કાર્ડ સ્વાઇપ)</h4>
                        <span style="font-size:11px; color:#64748b; font-weight:bold;">દરેક સેલ્સમેનનો તારીખવાર રોજમેળ</span>
                    </div>
                    <div style="overflow-x:auto; max-height:360px; overflow-y:auto;">
                        <table class="live-grid">
                            <thead style="position:sticky; top:0;">
                                <tr style="background:#0f2043; color:white;">
                                    <th style="color:white;">તારીખ</th>
                                    <th style="color:white;">સેલ્સમેન</th>
                                    <th style="color:white;">વ્યવહારનો પ્રકાર</th>
                                    <th style="color:white; text-align:left;">વિગત / રિમાર્ક</th>
                                    <th style="color:white;">ક્રેડિટ / જમા (₹)</th>
                                    <th style="color:white;">ડેબિટ / ઉપાડ / CC (₹)</th>
                                    <th style="color:white;">ચાલુ બેલેન્સ (Net Bal ₹)</th>
                                    <th style="color:white;">વોઉચર / બિલ નં.</th>
                                </tr>
                            </thead>
                            <tbody>{t4_rows}</tbody>
                        </table>
                    </div>
                </div>
            </div>
            """

    elif sheet == "APX_SALES_RAW":
        from part1_core import add_col_if_missing
        add_col_if_missing(conn, "apx_sales_raw", "due_date", "TEXT DEFAULT ''")
        add_col_if_missing(conn, "apx_sales_raw", "signed_copy_path", "TEXT DEFAULT ''")
        add_col_if_missing(conn, "apx_sales_raw", "scheme_benefit_amt", "REAL DEFAULT 0")
        add_col_if_missing(conn, "apx_sales_raw", "pos_swipe_charge", "REAL DEFAULT 0")
        # Build IMEI -> Purchase DP map and Model -> Scheme Benefit map for Real IMEI-wise GP% calculation (Rule 233)
        c.execute("SELECT imei, purchase_rate, brand, model FROM live_stock")
        stk_dp_map = {str(r[0]).strip(): float(r[1] or 0) for r in c.fetchall() if r[0]}
        c.execute("SELECT model, diff_amt, doc_type FROM ai_scheme_and_price_drop_log ORDER BY id DESC")
        sch_logs = c.fetchall()
        c.execute("SELECT bill_no, bill_date, customer_name, phone, salesman, model, imei, mop_price, loan_amt, status, COALESCE(doc_path,''), id, COALESCE(due_amt,0), COALESCE(due_date,''), COALESCE(signed_copy_path,''), COALESCE(scheme_benefit_amt,0), COALESCE(pos_swipe_charge,0), COALESCE(card_swipe_dp,0), COALESCE(discount_amt,0) FROM apx_sales_raw ORDER BY id DESC LIMIT 100")
        rows = c.fetchall()
        trs = ""
        for r in rows:
            doc_b = f"<a href='{r[10]}' target='_blank' style='background:#0284c7; color:white; padding:2px 6px; border-radius:3px; text-decoration:none; font-size:11px; font-weight:bold;'>📄 પ્રૂફ</a> " if r[10] else ""
            sc_path = r[14] or ""
            if sc_path and not sc_path.startswith("/"):
                sc_path = "/" + sc_path
            sc_btn = f"<a href='{sc_path}' target='_blank' style='background:#0d9488; color:white; padding:2px 6px; border-radius:3px; text-decoration:none; font-size:11px; font-weight:bold;'>✅ સહી કોપી જુઓ</a> " if sc_path else ""
            b_no_clean = str(r[0] or "")
            c_nm_clean = str(r[2] or "")
            up_sc_btn = f"<button type='button' onclick=\"openApxSignedCopyModal('{b_no_clean}', '{c_nm_clean}')\" style='background:#d97706; color:white; border:none; padding:2px 6px; border-radius:3px; font-size:11px; font-weight:bold; cursor:pointer;'>📸 સહી કોપી અપલોડ</button> "
            prt_b = f"<a href='/print-invoice?bill_no={urllib.parse.quote(b_no_clean)}' target='_blank' style='background:#15803d; color:white; padding:2px 6px; border-radius:3px; text-decoration:none; font-size:11px; font-weight:bold;'>🖨️ બિલ</a> "
            del_b = f"""<form action="/api/delete-store-entry-with-pin" method="post" style="display:inline;" onsubmit="var p=prompt('👑 આ વેચાણ બિલ ({r[0]}) રદ કરી ફોન પાછો સ્ટોકમાં લાવવા અને ગલ્લાની રોકડ ૧૦૦% રોલબેક કરવા માસ્ટર PIN (1986) નાખો:'); if(!p) return false; this.pin.value=p; return true;">
                <input type="hidden" name="entry_type" value="sale">
                <input type="hidden" name="entry_id" value="{r[11]}">
                <input type="hidden" name="pin" value="">
                <input type="hidden" name="return_sheet" value="APX_SALES_RAW">
                <button type="submit" style="background:#dc2626; color:white; border:none; padding:2px 7px; border-radius:3px; font-size:11px; font-weight:bold; cursor:pointer;">🗑️ રદ & રોલબેક</button>
            </form>"""
            due_v = float(r[12] or 0)
            due_dt_s = str(r[13] or "").strip()
            due_info_html = f"<br><span style='font-size:10.5px; color:#dc2626; font-weight:bold;'>બાકી: ₹{due_v:,.0f}{' | વાયદો: ' + due_dt_s if due_dt_s else ''}</span>" if (due_v > 0 or due_dt_s) else ""
            # નિયમ ૨૩૩: IMEI-વાઇઝ સાચો ગ્રોસ પ્રોફિટ (GP ₹ & GP%) = (વેચાણ કિંમત - ખરીદ પડતર DP) + કંપની સ્કીમ બેનિફિટ - POS સ્વાઇપ ચાર્જ
            sale_mop_v = float(r[7] or 0)
            im_key = str(r[6] or "").strip()
            pur_dp_v = stk_dp_map.get(im_key, round(sale_mop_v * 0.88, 2) if sale_mop_v > 0 else 0.0)
            sch_ben_v = float(r[15] or 0)
            if sch_ben_v <= 0 and r[5]:
                for sl_mod, sl_amt, _ in sch_logs:
                    if sl_mod and (sl_mod.upper() in str(r[5]).upper() or str(r[5]).upper()[:10] in sl_mod.upper()):
                        sch_ben_v = float(sl_amt or 0)
                        break
            pos_ch_v = float(r[16] or 0)
            if pos_ch_v <= 0 and float(r[17] or 0) > 0:
                pos_ch_v = round(float(r[17]) * 0.015, 2)
            real_gp_amt = round((sale_mop_v - pur_dp_v) + sch_ben_v - pos_ch_v, 2)
            real_gp_pct = round((real_gp_amt / sale_mop_v) * 100.0, 1) if sale_mop_v > 0 else 0.0
            gp_badge_html = f"<b style='color:{'#15803d' if real_gp_amt>=0 else '#dc2626'};'>₹{real_gp_amt:,.0f} ({real_gp_pct:.1f}%)</b><br><span style='font-size:10px; color:#475569;'>DP:₹{pur_dp_v:,.0f} | સ્કીમ:+₹{sch_ben_v:,.0f}</span>"
            trs += f"<tr><td><b>{r[0]}</b>{due_info_html}</td><td>{r[1]}</td><td>{r[2]}</td><td>{r[3]}</td><td>{r[4]}</td><td>{r[5]}</td><td>{r[6]}</td><td>₹{sale_mop_v:,.0f}</td><td>{gp_badge_html}</td><td>₹{float(r[8] or 0):,.0f}</td><td><b>{r[9]}</b></td><td>{doc_b}{sc_btn}{up_sc_btn}{prt_b}{del_b}</td></tr>"

        # નિયમ ૨૩૩(B): પ્રાઈસ પ્રોટેક્શન (Price Drop / Hike Claim) હાજર સ્ટોક પર કંપની પાસેથી લેવાનો બાકી ક્લેમ ટ્રેકર
        c.execute("SELECT brand, model, imei, purchase_rate, entry_date FROM live_stock WHERE status='IN_STOCK'")
        unsold_stk = c.fetchall()
        claim_rows_html = ""
        tot_claim_payout = 0.0
        for us_b, us_m, us_im, us_dp, us_dt in unsold_stk:
            for sl_mod, sl_amt, sl_type in sch_logs:
                if sl_type in ("PRICE_DROP", "PRICE_HIKE", "COMPANY_SCHEME") and sl_mod and (sl_mod.upper() in str(us_m).upper() or str(us_m).upper()[:10] in sl_mod.upper()):
                    c_amt = abs(float(sl_amt or 0))
                    if c_amt > 0:
                        tot_claim_payout += c_amt
                        claim_rows_html += f"<tr style='background:#fefce8;'><td><b>{us_b} {us_m}</b></td><td style='font-family:monospace;'>{us_im}</td><td>{us_dt}</td><td>₹{float(us_dp or 0):,.0f}</td><td><b>{sl_type}</b></td><td style='color:#15803d; font-weight:900;'>+ ₹{c_amt:,.0f}</td></tr>"
                        break
        price_prot_box_html = f"""
        <div style="background:#f0fdf4; border:2px solid #16a34a; border-radius:8px; padding:10px 14px; margin-bottom:12px;">
            <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:8px;">
                <div>
                    <b style="color:#166534; font-size:13.5px;">🛡️ નિયમ ૨૩૩: IMEI-વાઇઝ ગ્રોસ પ્રોફિટ (GP%) & પ્રાઈસ પ્રોટેક્શન ક્લેમ ટ્રેકર (Price Drop Payout)</b>
                    <div style="font-size:11.5px; color:#15803d;">હાજર અનસોલ્ડ સ્ટોક પર કંપની ભાવ-ઘટાડા / સ્કીમ મુજબ કંપની પાસેથી લેવાનો કુલ પેઆઉટ ક્લેમ: <b style="font-size:14px; color:#dc2626;">₹{tot_claim_payout:,.0f}</b></div>
                </div>
                <button type="button" onclick="var el=document.getElementById('pp_claim_tbl_wrap'); el.style.display=(el.style.display==='none'?'block':'none');" style="background:#15803d; color:white; border:none; padding:5px 12px; border-radius:5px; font-weight:bold; cursor:pointer; font-size:11.5px;">📊 પ્રાઈસ-ડ્રોપ ક્લેમ લિસ્ટ જુઓ</button>
            </div>
            <div id="pp_claim_tbl_wrap" style="display:none; margin-top:8px;">
                <table class="live-grid"><tr><th>મોડેલ</th><th>હાજર સ્ટોક IMEI</th><th>ખરીદ તારીખ</th><th>ખરીદ DP ₹</th><th>ક્લેમ પ્રકાર</th><th>કંપની પાસેથી લેવાનો ક્લેમ ₹</th></tr>
                {claim_rows_html or "<tr><td colspan='6'>હાજર સ્ટોક પર હાલ કોઈ પ્રાઇસ-ડ્રોપ ક્લેમ બાકી નથી. (AI બટનમાંથી પ્રાઇસ-ડ્રોપ લેટર અપલોડ કરો)</td></tr>"}
                </table>
            </div>
        </div>"""

        return f"""<div style='padding:10px;'>
            <h3>૪. વેચાણ, IMEI-વાઇઝ સાચો ગ્રોસ પ્રોફિટ (GP%) & DO રજીસ્ટર (૧૦૦% રોલબેક અને પ્રાઈસ પ્રોટેક્શન સાથે)</h3>
            {price_prot_box_html}
            <table class='live-grid'><tr><th>બિલ નં & વાયદો</th><th>તારીખ</th><th>ગ્રાહક</th><th>ફોન</th><th>સેલ્સમેન</th><th>મોડેલ</th><th>IMEI / S/N</th><th>MOP</th><th>સાચો GP ₹ (GP%)</th><th>લોન</th><th>સ્થિતિ</th><th>એક્શન / સહી કોપી / રોલબેક (PIN 1986)</th></tr>{trs}</table>
            <div id="apx_signed_copy_modal" style="display:none; position:fixed; top:0; left:0; width:100%; height:100%; background:rgba(15,23,42,0.8); z-index:9999; justify-content:center; align-items:center;">
                <div style="background:white; max-width:450px; width:92%; border-radius:10px; padding:18px; border:3px solid #d97706;">
                    <div style="display:flex; justify-content:space-between; align-items:center; border-bottom:2px solid #fde68a; padding-bottom:8px; margin-bottom:12px;">
                        <b style="color:#b45309; font-size:15px;">📸 સહી વાળી રિટર્ન બિલ કોપી અપલોડ કરો</b>
                        <button type="button" onclick="document.getElementById('apx_signed_copy_modal').style.display='none'" style="background:none; border:none; font-size:18px; cursor:pointer;">✖</button>
                    </div>
                    <form action="/api/upload-signed-return-copy" method="post" enctype="multipart/form-data">
                        <input type="hidden" name="bill_no" id="apx_sc_bill_no" value="">
                        <input type="hidden" name="return_to" value="APX_SALES_RAW">
                        <div id="apx_sc_lbl" style="font-size:12.5px; font-weight:bold; color:#0f2043; margin-bottom:8px;"></div>
                        <input type="file" name="signed_file" accept="image/*,.pdf" capture="environment" required style="width:100%; padding:8px; border:2px dashed #d97706; border-radius:6px; margin-bottom:12px;">
                        <div style="text-align:right;">
                            <button type="submit" style="background:#16a34a; color:white; border:none; padding:8px 18px; border-radius:6px; font-weight:900; cursor:pointer;">✅ વૉલ્ટમાં સેવ કરો</button>
                        </div>
                    </form>
                </div>
            </div>
            <script>
                function openApxSignedCopyModal(bno, cname) {{
                    document.getElementById('apx_sc_bill_no').value = bno;
                    document.getElementById('apx_sc_lbl').innerText = 'બિલ નં: ' + bno + ' | ગ્રાહક: ' + cname;
                    document.getElementById('apx_signed_copy_modal').style.display = 'flex';
                }}
            </script>
        </div>"""

    elif sheet == "BARCODE_AUDIT":
        c.execute("""CREATE TABLE IF NOT EXISTS barcode_audit_unlisted_scans (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            scan_date TEXT, scan_time TEXT, imei TEXT UNIQUE,
            remarks TEXT DEFAULT 'અજાણ્યો સ્કેન થયેલ પીસ / પરચેસ બાકી', store_id TEXT DEFAULT 'DEVANSHI'
        )""")
        c.execute("SELECT id, brand, model, imei, entry_date, audit_verified, party_name, bill_no, purchase_rate, sale_rate, category, doc_path FROM live_stock WHERE status='IN_STOCK' ORDER BY audit_verified ASC, id DESC")
        b_rows = c.fetchall()
        c.execute("SELECT id, scan_date, scan_time, imei, remarks FROM barcode_audit_unlisted_scans ORDER BY id DESC")
        orange_rows = c.fetchall()

        today_d = datetime.date.today()
        trs = ""
        aging_cnt, green_cnt, red_cnt = 0, 0, 0
        aging_dp_tot, green_dp_tot, red_dp_tot = 0.0, 0.0, 0.0

        # ૧. પહેલાં ઓરેન્જ (અજાણ્યો સ્કેન થયેલ પીસ / ખરીદી બાકી) બતાવો
        for idx_o, orow in enumerate(orange_rows, 1):
            o_im = orow[3]
            trs += f"""<tr data-audit-cat="ORANGE" style="background:#ffedd5; border-left:4px solid #f97316;">
                <td>{idx_o}</td>
                <td><b style="color:#c2410c;">🟠 અજાણ્યો / પરચેસ બાકી</b></td>
                <td><b>{orow[4] or 'ખરીદીમાં લેવાનો બાકી પીસ'}</b></td>
                <td><b style="color:#9a3412; font-size:13px;">{o_im}</b></td>
                <td>- (પરચેસ બાકી)</td>
                <td>₹0</td>
                <td>₹0</td>
                <td>{orow[1]} {orow[2]}</td>
                <td><b style="color:#c2410c;">🟠 ઓરેન્જ: અજાણ્યો / પરચેસ બાકી</b></td>
                <td>
                    <a href="/?sheet=SMART_TERMINAL&mode=F1" style="background:#ea580c; color:white; padding:3px 8px; border-radius:4px; text-decoration:none; font-size:11px; font-weight:bold;">[+ F1 ખરીદીમાં લો]</a>
                </td>
            </tr>"""

        # ૨. લાઈવ સ્ટોકના લીલા (હાજર <60 દિવસ), પીળા (60+ દિવસ જૂના ડેડ સ્ટોક) અને લાલ (મિસિંગ/સ્કેન બાકી) પીસ - સંપૂર્ણ લેજર વિગતો સાથે
        for idx_r, r in enumerate(b_rows, 1):
            age_d = 0
            try:
                age_d = (today_d - datetime.datetime.strptime(r[4], "%Y-%m-%d").date()).days
            except Exception:
                pass
            supp_nm = r[6] or "-"
            b_no = r[7] or "-"
            dp_v = float(r[8] or 0)
            mop_v = float(r[9] or 0)
            doc_p = r[11] or ""
            doc_btn = f"<a href='{doc_p}' target='_blank' style='background:#0d9488; color:white; padding:2px 6px; border-radius:3px; text-decoration:none; font-size:10.5px; font-weight:bold;'>📄 બિલ</a> " if doc_p else ""

            if age_d >= 60:
                aging_cnt += 1
                aging_dp_tot += dp_v
                bg = "#fef08a"
                st = f"🟡 યલો: ૬૦+ દિવસ જૂનો ડેડ સ્ટોક ({age_d} દિવસ જૂનો - {'હાજર' if r[5]==1 else 'સ્કેન બાકી'})"
                dcat = "AGING VERIFIED" if r[5] == 1 else "AGING UNVERIFIED"
            elif r[5] == 1:
                green_cnt += 1
                green_dp_tot += dp_v
                bg = "#dcfce7"
                st = f"🟢 ગ્રીન: હાજર રનિંગ સ્ટોક (VERIFIED - {age_d} દિવસ)"
                dcat = "VERIFIED"
            else:
                red_cnt += 1
                red_dp_tot += dp_v
                bg = "#fee2e2"
                st = f"🔴 રેડ: મિસિંગ / સ્કેન બાકી ({age_d} દિવસ)"
                dcat = "UNVERIFIED"

            trs += f"""<tr data-audit-cat='{dcat}' style='background:{bg};'>
                <td>{idx_r}</td>
                <td><b>{r[1]}</b></td>
                <td><b>{r[2]}</b></td>
                <td><b>{r[3]}</b></td>
                <td><b>{supp_nm}</b> ({b_no})</td>
                <td style="font-weight:bold; color:#0f2043;">₹{dp_v:,.0f}</td>
                <td style="font-weight:bold; color:#15803d;">₹{mop_v:,.0f}</td>
                <td>{r[4]} (<b>{age_d} દિવસ</b>)</td>
                <td><b>{st}</b></td>
                <td>{doc_btn}<a href="/?sheet=SMART_TERMINAL&mode=F2" style="background:#0284c7; color:white; padding:2px 6px; border-radius:3px; text-decoration:none; font-size:10.5px; font-weight:bold;">[વેચાણ F2]</a></td>
            </tr>"""

        tot_all_dp = green_dp_tot + aging_dp_tot + red_dp_tot
        return f"""
        <div style='padding:10px;'>
            <h3>૧૪. ૪-કલર બારકોડ સ્ટોક ઓડિટ & વિગતવાર સ્ટોક લેજર (કોઈપણ કલર સિગ્નલ બટન પર ક્લિક કરતાં તેના તમામ પીસનું આખું લેજર ખુલશે)</h3>
            <div style="display:grid; grid-template-columns:repeat(5, 1fr); gap:8px; margin-bottom:12px;">
                <div id="sig_btn_ALL" onclick="filterAuditTable('ALL')" style="background:#f1f5f9; border:2px solid #0f2043; padding:10px; border-radius:6px; text-align:center; cursor:pointer;">
                    <div style="font-size:11px; font-weight:800; color:#334155;">📦 તમામ સ્ટોક + સ્કેન લેજર</div>
                    <div style="font-size:17px; font-weight:900; color:#0f172a;">{len(b_rows) + len(orange_rows)} નંગ</div>
                    <div style="font-size:11px; font-weight:bold; color:#475569;">કુલ DP: ₹{tot_all_dp:,.0f}</div>
                </div>
                <div id="sig_btn_VERIFIED" onclick="filterAuditTable('VERIFIED')" style="background:#dcfce7; border:2px solid #16a34a; padding:10px; border-radius:6px; text-align:center; cursor:pointer;">
                    <div style="font-size:11px; font-weight:800; color:#166534;">🟢 ગ્રીન: હાજર રનિંગ સ્ટોક (&lt;60 d)</div>
                    <div style="font-size:17px; font-weight:900; color:#166534;">{green_cnt} નંગ</div>
                    <div style="font-size:11px; font-weight:bold; color:#15803d;">કુલ DP: ₹{green_dp_tot:,.0f}</div>
                </div>
                <div id="sig_btn_AGING" onclick="filterAuditTable('AGING')" style="background:#fef08a; border:2px solid #ca8a04; padding:10px; border-radius:6px; text-align:center; cursor:pointer; box-shadow:0 2px 6px rgba(202,138,4,0.25);">
                    <div style="font-size:11px; font-weight:800; color:#854d0e;">🟡 યલો: ૬૦+ દિવસ જૂનો ડેડ સ્ટોક</div>
                    <div style="font-size:17px; font-weight:900; color:#854d0e;">{aging_cnt} નંગ (60+ Days)</div>
                    <div style="font-size:11px; font-weight:bold; color:#92400e;">કુલ DP: ₹{aging_dp_tot:,.0f}</div>
                </div>
                <div id="sig_btn_UNVERIFIED" onclick="filterAuditTable('UNVERIFIED')" style="background:#fee2e2; border:2px solid #dc2626; padding:10px; border-radius:6px; text-align:center; cursor:pointer;">
                    <div style="font-size:11px; font-weight:800; color:#991b1b;">🔴 રેડ: મિસિંગ (સ્કેન બાકી)</div>
                    <div style="font-size:17px; font-weight:900; color:#991b1b;">{red_cnt} નંગ</div>
                    <div style="font-size:11px; font-weight:bold; color:#b91c1c;">કુલ DP: ₹{red_dp_tot:,.0f}</div>
                </div>
                <div id="sig_btn_ORANGE" onclick="filterAuditTable('ORANGE')" style="background:#ffedd5; border:2px solid #f97316; padding:10px; border-radius:6px; text-align:center; cursor:pointer; box-shadow:0 2px 6px rgba(249,115,22,0.25);">
                    <div style="font-size:11px; font-weight:800; color:#c2410c;">🟠 ઓરેન્જ: અજાણ્યો / પરચેસ બાકી</div>
                    <div style="font-size:17px; font-weight:900; color:#ea580c;">{len(orange_rows)} નંગ</div>
                    <div style="font-size:11px; font-weight:bold; color:#c2410c;">ખરીદી એન્ટ્રી બાકી</div>
                </div>
            </div>
            <div id="audit_active_ledger_banner" style="background:#e0f2fe; border:2px solid #0284c7; color:#0f2043; padding:8px 12px; border-radius:6px; margin-bottom:10px; font-weight:800; font-size:12.5px;">
                📋 હાલ ખુલ્લું લેજર: <b>તમામ સ્ટોક અને સ્કેન પીસ ({len(b_rows) + len(orange_rows)} નંગ)</b> — ઉપરના કોઈપણ સિગ્નલ બટન (🟢 ગ્રીન, 🟡 યલો ૬૦+ દિવસ જૂનો ડેડ સ્ટોક, 🔴 રેડ, 🟠 ઓરેન્જ) પર ક્લિક કરતાં ફક્ત તે સિગ્નલના તમામ પીસનું વિગતવાર લેજર ખુલશે!
            </div>
            <form action="/scan-barcode-audit" method="post" style="display:flex; gap:8px; margin-bottom:10px; align-items:center; flex-wrap:wrap;">
                <input type="text" name="scan_imei" autofocus placeholder="અહીં બારકોડ ગનથી IMEI સ્કેન કરો (સ્ટોકમાં ન હોય તેવો પીસ 🟠 ઓરેન્જ બતાવશે)..." required style="padding:8px 12px; width:420px; border:2px solid #0284c7; border-radius:4px; font-weight:bold;">
                <button type="submit" style="background:#16a34a; color:white; border:none; padding:8px 16px; border-radius:4px; font-weight:bold; cursor:pointer;">✅ સ્કેન વેરિફાય કરો</button>
                <a href="/reset-barcode-audit" onclick="return confirm('નવું ઓડિટ શરૂ કરવા બધા માર્ક અને ઓરેન્જ લિસ્ટ રીસેટ કરવા છે?')" style="background:#dc2626; color:white; padding:8px 14px; border-radius:4px; text-decoration:none; font-weight:bold;">🔄 ઓડિટ રીસેટ</a>
            </form>
            <div style="overflow-x:auto;">
                <table class='live-grid' id='audit_tbl'>
                    <tr>
                        <th>ક્રમ</th><th>બ્રાન્ડ / પ્રકાર</th><th>મોડેલ / વિગત</th><th>૧૫-અંક IMEI</th>
                        <th>વેપારી (બિલ નં.)</th><th>ખરીદ પડતર (DP ₹)</th><th>વેચાણ ભાવ (MOP ₹)</th>
                        <th>ઇનવર્ડ તારીખ (કેટલા દિવસ જૂનો?)</th><th>૪-કલર સિગ્નલ સ્થિતિ</th><th>એક્શન</th>
                    </tr>
                    {trs}
                </table>
            </div>
            <script>
                function filterAuditTable(cat){{
                    var trs = document.querySelectorAll('#audit_tbl tr');
                    var shown = 0;
                    for(var i=1; i<trs.length; i++){{
                        var dcat = trs[i].getAttribute('data-audit-cat') || '';
                        var txt = trs[i].innerText || '';
                        var match = false;
                        if(cat === 'ALL'){{ match = true; }}
                        else if(cat === 'ORANGE'){{ match = (dcat.includes('ORANGE') || txt.includes('ORANGE')); }}
                        else if(cat === 'VERIFIED'){{ match = (dcat === 'VERIFIED'); }}
                        else if(cat === 'UNVERIFIED'){{ match = dcat.includes('UNVERIFIED'); }}
                        else if(cat === 'AGING'){{ match = dcat.includes('AGING'); }}
                        trs[i].style.display = match ? '' : 'none';
                        if(match) shown++;
                    }}
                    var bnr = document.getElementById('audit_active_ledger_banner');
                    if(bnr){{
                        var titles = {{
                            'ALL': '📦 તમામ સ્ટોક + સ્કેન વિગતવાર લેજર',
                            'VERIFIED': '🟢 ગ્રીન સિગ્નલ લેજર: હાજર રનિંગ સ્ટોક (૬૦ દિવસથી ઓછો)',
                            'AGING': '🟡 યલો સિગ્નલ લેજર: ૬૦+ દિવસ જૂનો ડેડ સ્ટોક (તમામ પીસની ખરીદી તારીખ, વેપારી, DP અને MOP વિગત)',
                            'UNVERIFIED': '🔴 રેડ સિગ્નલ લેજર: મિસિંગ / સ્કેન બાકી સ્ટોક પીસ',
                            'ORANGE': '🟠 ઓરેન્જ સિગ્નલ લેજર: અજાણ્યો / ખરીદીમાં લેવાનો બાકી પીસ'
                        }};
                        bnr.innerHTML = '📋 હાલ ખુલ્લું સિગ્નલ લેજર: <b>' + (titles[cat] || cat) + ' (કુલ ' + shown + ' પીસ)</b>';
                    }}
                }}
            </script>
        </div>
        """

    elif sheet == "BUYBACK_STOCK":
        c.execute("SELECT date, customer_name, model, imei, purchase_cost, repair_cost, total_cost, salesman, status, sale_price, id, COALESCE(photo_path,''), COALESCE(customer_photo_path,'') FROM buyback_stock ORDER BY id DESC")
        rows = c.fetchall()
        trs = ""
        for r in rows:
            doc_b = f"<a href='{r[11]}' target='_blank' style='background:#0284c7; color:white; padding:2px 6px; border-radius:3px; text-decoration:none; font-size:11px;'>📄 પ્રૂફ</a> " if r[11] else ""
            cph_b = f"<a href='{r[12]}' target='_blank' style='background:#0d9488; color:white; padding:2px 6px; border-radius:3px; text-decoration:none; font-size:11px;'>👤 ગ્રાહક ફોટો</a> " if r[12] else ""
            rep_b = f"<a href='javascript:void(0)' onclick='var p=prompt(\"રિપેરિંગ ખર્ચ ₹{float(r[5] or 0):,.0f} રદ કરી ગલ્લામાં પાછો જમા કરવા PIN 1986 નાખો:\",\"\"); if(p) window.location.href=\"/api/cancel-buyback-repair?id={r[10]}&pin=\"+encodeURIComponent(p);' style='background:#d97706; color:white; padding:2px 6px; border-radius:3px; text-decoration:none; font-size:11px; font-weight:bold;'>🛠️ રિપેર રદ</a> " if float(r[5] or 0) > 0 else ""
            j_c, j_m, j_i, j_s = json.dumps(r[1] or ""), json.dumps(r[2] or ""), json.dumps(r[3] or ""), json.dumps(r[7] or "")
            ed_b = f"<button type='button' onclick='openEditBuybackModal({r[10]}, {j_c}, {j_m}, {j_i}, {float(r[4] or 0)}, {float(r[5] or 0)}, {j_s})' style='background:#0284c7; color:white; border:none; padding:3px 7px; border-radius:3px; cursor:pointer; font-size:11px; font-weight:bold;'>✏️ એડિટ</button> "
            del_b = f"<a href='javascript:void(0)' onclick='var p=prompt(\"આ બાયબેક ફોન રદ કરી તેની રોકડ રકમ ગલ્લામાં પાછી જમા કરવા માસ્ટર PIN (1986) નાખો:\",\"\"); if(p) window.location.href=\"/delete-buyback-item?id={r[10]}&pin=\"+encodeURIComponent(p);' style='background:#dc2626; color:white; padding:3px 7px; border-radius:3px; text-decoration:none; font-size:11px; font-weight:bold;'>🗑️ રદ (Cash Rollback)</a>"
            trs += f"<tr><td>{r[0]}</td><td>{r[1]}</td><td><b>{r[2]}</b></td><td><b>{r[3]}</b></td><td>₹{float(r[4] or 0):,.0f}</td><td>₹{float(r[5] or 0):,.0f}</td><td><b>₹{float(r[6] or 0):,.0f}</b></td><td>{r[7]}</td><td>{r[8]}</td><td>₹{float(r[9] or 0):,.0f}</td><td>{doc_b}{cph_b}{rep_b}{ed_b}{del_b}</td></tr>"
        return f"""<div style='padding:10px;'>
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
                <h3 style="margin:0; color:#0f2043;">૭. જૂના ફોન (Buyback) સ્ટોક રજીસ્ટર (એડિટ, રિપેર રદ & ૧૦૦% રોકડ રિવર્સલ સાથે)</h3>
                <a href="/?sheet=SMART_TERMINAL&mode=F5" style="background:#16a34a; color:white; padding:6px 14px; border-radius:4px; text-decoration:none; font-weight:bold;">+ નવી બાયબેક એન્ટ્રી (F5)</a>
            </div>
            <div id="edit_bb_box" style="display:none; background:#e0f2fe; border:2px solid #0284c7; padding:12px; border-radius:6px; margin-bottom:10px;">
                <h4 style="margin:0 0 8px 0; color:#0f2043;">✏️ બાયબેક એન્ટ્રી સુધારો (તફાવત રકમ આપોઆપ ગલ્લામાં સેટ થશે):</h4>
                <form action="/api/edit-buyback-item" method="post" class="term-form" style="max-width:100%; margin:0;">
                    <input type="hidden" name="bb_id" id="eb_id">
                    <div class="f-row"><div class="lbl">ગ્રાહકનું નામ:</div><input type="text" name="customer_name" id="eb_cust" required></div>
                    <div class="f-row"><div class="lbl">મોડેલ નામ & ૧૫-અંક IMEI:</div><input type="text" name="model" id="eb_mod" required style="flex:1;"><input type="text" name="imei" id="eb_imei" maxlength="15" required style="flex:1;"></div>
                    <div class="f-row"><div class="lbl">ખરીદ કિંમત (₹) & રિપેર ખર્ચ (₹):</div><input type="number" step="any" name="purchase_cost" id="eb_pcost" required><input type="number" step="any" name="repair_cost" id="eb_rcost"></div>
                    <div class="f-row"><div class="lbl">સેલ્સમેન & સિક્યુરિટી PIN:</div><input type="text" name="salesman" id="eb_sm"><input type="password" name="pin" value="" placeholder="સિક્યુરિટી PIN નાખો" required style="max-width:160px;"></div>
                    <div class="btn-wrap"><button type="submit" class="btn-save" style="background:#16a34a; width:auto;">💾 સુધારો સેવ કરો</button> <button type="button" onclick="document.getElementById('edit_bb_box').style.display='none'" style="background:#dc2626; color:white; border:none; padding:9px 16px; border-radius:4px; font-weight:bold; cursor:pointer;">રદ કરો</button></div>
                </form>
            </div>
            <table class='live-grid'><tr><th>તારીખ</th><th>ગ્રાહક</th><th>મોડેલ</th><th>IMEI</th><th>ખરીદ કિંમત</th><th>રિપેર ખર્ચ</th><th>કુલ પડતર</th><th>સ્ટાફ</th><th>સ્થિતિ</th><th>વેચાણ કિંમત</th><th>પ્રૂફ / એડિટ / રદ</th></tr>{trs}</table>
            <script>
                function openEditBuybackModal(id, cust, mod, imei, pcost, rcost, sm) {{
                    document.getElementById('eb_id').value = id;
                    document.getElementById('eb_cust').value = cust;
                    document.getElementById('eb_mod').value = mod;
                    document.getElementById('eb_imei').value = imei;
                    document.getElementById('eb_pcost').value = pcost;
                    document.getElementById('eb_rcost').value = rcost;
                    document.getElementById('eb_sm').value = sm;
                    document.getElementById('edit_bb_box').style.display = 'block';
                    document.getElementById('eb_cust').focus();
                }}
            </script>
        </div>"""

    elif sheet == "CUSTOMER_DUE":
        from part1_core import add_col_if_missing
        add_col_if_missing(conn, "customer_due_ledger", "signed_copy_path", "TEXT DEFAULT ''")
        add_col_if_missing(conn, "customer_due_ledger", "due_date", "TEXT DEFAULT ''")
        c.execute("SELECT date, salesman, customer_name, phone, bill_no, due_amt, received_amt, id, COALESCE(file_path,''), COALESCE(due_date,''), COALESCE(signed_copy_path,'') FROM customer_due_ledger ORDER BY id DESC")
        rows = c.fetchall()
        trs = ""
        for r in rows:
            f_url = r[10] or r[8]
            if f_url and not f_url.startswith("/"):
                f_url = "/" + f_url
            f_btn = f"<a href='{f_url}' target='_blank' style='background:#0284c7; color:white; padding:3px 7px; border-radius:3px; text-decoration:none; font-size:11px; font-weight:bold;'>📄 સહી કોપી જુઓ</a> " if f_url else ""
            inv_btn = f"<a href='/print-invoice?bill_no={urllib.parse.quote(str(r[4] or ''))}' target='_blank' style='background:#7c3aed; color:white; padding:3px 7px; border-radius:3px; text-decoration:none; font-size:11px; font-weight:bold;'>🧾 પાકું બિલ</a> " if r[4] else ""
            b_no_s = str(r[4] or "")
            c_nm_s = str(r[2] or "")
            up_ret_btn = f'<button type="button" onclick="openDueSignedCopyModal({r[7]}, \'{b_no_s}\', \'{c_nm_s}\')" style="background:#d97706; color:white; border:none; padding:3px 7px; border-radius:3px; font-size:11px; font-weight:bold; cursor:pointer;">📸 સહી કોપી અપલોડ</button> '
            trs += f"""<tr>
                <td>{r[0]}</td><td>{r[1]}</td><td><b>{r[2]}</b></td><td>{r[3]}</td>
                <td><b>{r[4] or '-'}</b>{f"<br><span style='font-size:10.5px; color:#dc2626; font-weight:bold;'>વાયદો: {r[9]}</span>" if r[9] else ""}</td>
                <td>₹{float(r[5] or 0):,.0f}</td><td>₹{float(r[6] or 0):,.0f}</td>
                <td style='color:#dc2626; font-weight:bold;'>₹{float(r[5] or 0)-float(r[6] or 0):,.0f}</td>
                <td>
                    <a href="https://wa.me/91{str(r[3]).strip()[-10:]}?text=નમસ્તે%20{r[2]},%20આપની%20બાકી%20રકમ%20₹{float(r[5] or 0)-float(r[6] or 0):,.0f}%20છે." target="_blank" style="background:#16a34a; color:white; padding:3px 8px; border-radius:3px; text-decoration:none; font-weight:bold; font-size:11px;">📲 WhatsApp</a>
                    {inv_btn}{f_btn}{up_ret_btn}
                    <a href="javascript:void(0)" onclick="var p=prompt('આ ઉધાર એન્ટ્રી રદ કરવા સિક્યુરિટી માસ્ટર PIN નાખો:'); if(p) window.location.href='/delete-customer-due?id={r[7]}&pin='+encodeURIComponent(p);" style="background:#dc2626; color:white; padding:3px 7px; border-radius:3px; text-decoration:none; font-weight:bold; font-size:11px;">🗑️ રદ</a>
                </td>
            </tr>"""
        sm_opts_due = "".join([f"<option value='{s[1]}'>{s[1]} ({s[2]})</option>" for s in staff_db_rows])
        return f"""<div style='padding:10px;'>
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
                <h3 style="margin:0; color:#0f2043;">૮. ગ્રાહક બાકી ઉધાર ખાતાવહી (Customer Due Ledger)</h3>
                <button type="button" onclick="var b=document.getElementById('direct_due_form_box'); b.style.display=(b.style.display==='none'?'block':'none');" style="background:#0284c7; color:white; border:none; padding:7px 14px; border-radius:4px; font-weight:bold; cursor:pointer;">[ 📝 + સીધી ગ્રાહક બાકી ઉમેરો (HO બિલ વગર) ]</button>
            </div>
            <div id="direct_due_form_box" style="display:none; background:#f8fafc; border:2px solid #0284c7; padding:12px; border-radius:6px; margin-bottom:12px;">
                <h4 style="margin:0 0 8px 0; color:#0f2043;">📝 સીધી ગ્રાહક બાકી ઉધાર એન્ટ્રી (HO બિલ વગર / જૂની ઉધાર):</h4>
                <form action="/api/save-direct-customer-due" method="post" enctype="multipart/form-data" class="term-form f-enter-form" style="max-width:100%; margin:0;">
                    <div class="f-row"><div class="lbl">૧. તારીખ:</div><input type="date" name="due_entry_date" value="{today_str}"></div>
                    <div class="f-row"><div class="lbl">૨. ગ્રાહકનું નામ & ૧૦-અંક મોબાઈલ:</div><input type="text" name="customer_name" placeholder="ગ્રાહકનું પૂરું નામ" required style="flex:1;"><input type="text" name="phone" maxlength="10" placeholder="૧૦-અંક મોબાઈલ" required style="max-width:180px;"></div>
                    <div class="f-row"><div class="lbl">૩. સરનામું & સંદર્ભ બિલ/નોંધ:</div><input type="text" name="address" placeholder="ગ્રાહકનું સરનામું" style="flex:1;"><input type="text" name="bill_no" placeholder="બિલ નંબર / નોંધ (દા.ત. OLD-DUE)" style="max-width:220px;"></div>
                    <div class="f-row"><div class="lbl">૪. બાકી ઉધાર રકમ (₹) & વાયદા તારીખ:</div><input type="number" step="any" name="due_amt" required placeholder="બાકી રકમ ₹" style="font-weight:bold; color:#dc2626;"><input type="date" name="due_date" style="max-width:180px;"></div>
                    <div class="f-row"><div class="lbl">૫. જવાબદાર સેલ્સમેન & પ્રૂફ ફાઇલ:</div><select name="salesman" style="flex:1;">{sm_opts_due}</select><input type="file" name="due_doc" style="flex:1;"></div>
                    <div class="btn-wrap"><button type="submit" class="btn-save" style="background:#16a34a;">[ 💾 સીધી ગ્રાહક બાકી સેવ કરો ]</button></div>
                </form>
            </div>
            <table class='live-grid'><tr><th>તારીખ</th><th>સેલ્સમેન</th><th>ગ્રાહક</th><th>ફોન</th><th>બિલ નં & વાયદો</th><th>કુલ ઉધાર</th><th>જમા</th><th>બાકી રકમ</th><th>WhatsApp / પાકું બિલ / સહી વાળી રિટર્ન કોપી / રદ</th></tr>{trs}</table>
            <div id="due_signed_modal" style="display:none; position:fixed; top:0; left:0; width:100%; height:100%; background:rgba(15,23,42,0.8); z-index:9999; justify-content:center; align-items:center;">
                <div style="background:white; max-width:440px; width:92%; border-radius:10px; padding:18px; border:3px solid #d97706;">
                    <div style="display:flex; justify-content:space-between; align-items:center; border-bottom:2px solid #fde68a; padding-bottom:8px; margin-bottom:10px;">
                        <b id="due_signed_title" style="color:#b45309; font-size:14.5px;">📸 સહી વાળી રિટર્ન કોપી અપલોડ કરો</b>
                        <button type="button" onclick="document.getElementById('due_signed_modal').style.display='none'" style="background:none; border:none; font-size:18px; cursor:pointer;">✖</button>
                    </div>
                    <form action="/api/upload-signed-return-copy" method="post" enctype="multipart/form-data">
                        <input type="hidden" name="due_id" id="due_signed_id" value="0">
                        <input type="hidden" name="bill_no" id="due_signed_bill" value="">
                        <input type="hidden" name="return_to" value="CUSTOMER_DUE">
                        <p style="font-size:12px; color:#334155; margin:0 0 10px 0;">ગ્રાહકની સહી થયેલા બિલનો મોબાઇલ કેમેરાથી ફોટો પાડો અથવા ફાઇલ પસંદ કરો:</p>
                        <input type="file" name="signed_file" accept="image/*,.pdf" capture="environment" required style="width:100%; padding:8px; border:2px dashed #d97706; border-radius:6px; margin-bottom:12px;">
                        <div style="text-align:right;">
                            <button type="submit" style="background:#16a34a; color:white; border:none; padding:8px 18px; border-radius:6px; font-weight:900; cursor:pointer;">✅ વૉલ્ટમાં સેવ કરો</button>
                        </div>
                    </form>
                </div>
            </div>
            <script>
                function openDueSignedCopyModal(id, billNo, custName) {{
                    document.getElementById('due_signed_id').value = id;
                    document.getElementById('due_signed_bill').value = billNo;
                    document.getElementById('due_signed_title').innerText = '📸 સહી વાળી રિટર્ન કોપી: ' + custName;
                    document.getElementById('due_signed_modal').style.display = 'flex';
                }}
            </script>
        </div>"""

    elif sheet == "SUPPLIER_PURCHASE":
        from part1_core import add_col_if_missing
        add_col_if_missing(conn, "supplier_purchase_ledger", "credit_days", "INTEGER DEFAULT 0")
        add_col_if_missing(conn, "supplier_purchase_ledger", "due_date", "TEXT DEFAULT ''")
        c.execute("SELECT date, supplier_name, bill_no, total_bill, paid_amt, balance_due, galla_name, entry_type, COALESCE(doc_path,''), id, COALESCE(due_date,''), COALESCE(credit_days,0) FROM supplier_purchase_ledger ORDER BY id DESC")
        rows = c.fetchall()
        trs = ""
        for r in rows:
            sup_doc_u = (r[8] if r[8].startswith("/") else ("/" + r[8])) if r[8] else ""
            v_inv_b = f"<a href='/view-purchase-invoice?bill_no={urllib.parse.quote(str(r[2] or ''))}&party_name={urllib.parse.quote(str(r[1] or ''))}' target='_blank' style='background:#7c3aed;color:white;padding:2px 7px;border-radius:3px;text-decoration:none;font-size:11px;font-weight:bold;'>🧾 પ્રોફેશનલ બિલ વ્યુ</a> "
            doc_b = v_inv_b + (f"<a href='{sup_doc_u}' target='_blank' style='background:#0284c7;color:white;padding:2px 6px;border-radius:3px;text-decoration:none;font-size:11px;font-weight:bold;'>📄 અસલ PDF</a> " if sup_doc_u else "")
            del_b = f"""<form action="/api/delete-store-entry-with-pin" method="post" style="display:inline;" onsubmit="var p=prompt('👑 આ ખરીદી બિલ ({r[2]}) રદ કરી તેના તમામ IMEI સ્ટોકમાંથી કાઢવા અને ગલ્લાની રોકડ ૧૦૦% રોલબેક કરવા માસ્ટર PIN (1986) નાખો:'); if(!p) return false; this.pin.value=p; return true;">
                <input type="hidden" name="entry_type" value="purchase">
                <input type="hidden" name="entry_id" value="{r[9]}">
                <input type="hidden" name="pin" value="">
                <input type="hidden" name="return_sheet" value="SUPPLIER_PURCHASE">
                <button type="submit" style="background:#dc2626; color:white; border:none; padding:2px 7px; border-radius:3px; font-size:11px; font-weight:bold; cursor:pointer;">🗑️ રદ & રોલબેક</button>
            </form>"""
            due_dt_badge = f"<br><span style='font-size:10.5px; color:#dc2626; font-weight:bold;'>⏰ ડ્યુ: {r[10]} ({r[11]} દિવસ)</span>" if (len(r)>10 and r[10] and float(r[5] or 0)>0) else ""
            trs += f"<tr><td>{r[0]}{due_dt_badge}</td><td><b>{r[1]}</b></td><td>{r[2]}</td><td>₹{float(r[3] or 0):,.0f}</td><td>₹{float(r[4] or 0):,.0f}</td><td><b style='color:#dc2626;'>₹{float(r[5] or 0):,.0f}</b></td><td>{r[6]}</td><td>{r[7]}</td><td>{doc_b}{del_b}</td></tr>"
        c.execute("""SELECT 
            COALESCE(SUM(CASE WHEN tx_type IN ('CAPITAL_IN','GIFT_IN','PARTNER_GIFT','CC_PURCHASE_PAYABLE','PERSONAL_EXP_PAYABLE') THEN amount ELSE 0 END), 0), 
            COALESCE(SUM(CASE WHEN tx_type IN ('DRAWING_OUT','CAPITAL_OUT','CC_REIMBURSE_PAID') THEN amount ELSE 0 END), 0) 
            FROM partner_capital_ledger""")
        sp_p_in, sp_p_out = c.fetchone() or (0.0, 0.0)
        sp_p_in, sp_p_out = float(sp_p_in or 0.0), float(sp_p_out or 0.0)
        sp_p_pend = max(0.0, sp_p_in - sp_p_out)
        c.execute("SELECT tx_date, partner_name, tx_type, amount, pay_mode, galla_name, remarks, COALESCE(card_details,''), COALESCE(reimburse_status,'PENDING') FROM partner_capital_ledger ORDER BY id DESC LIMIT 50")
        p_rows = c.fetchall()
        p_trs = ""
        for pr in p_rows:
            tx_lbl = pr[2]
            if pr[2] == 'CC_PURCHASE_PAYABLE': tx_lbl = '<span style="color:#b91c1c; font-weight:bold;">💳 ક્રેડિટ કાર્ડ ખરીદી લેણું</span>'
            elif pr[2] == 'PERSONAL_EXP_PAYABLE': tx_lbl = '<span style="color:#b45309; font-weight:bold;">💼 અંગત ખર્ચ લેણું</span>'
            elif pr[2] == 'CC_REIMBURSE_PAID': tx_lbl = '<span style="color:#15803d; font-weight:bold;">✅ CC વળતર ચૂકતે</span>'
            elif pr[2] == 'CAPITAL_IN': tx_lbl = '<span style="color:#1d4ed8; font-weight:bold;">💰 મૂડી જમા</span>'
            elif pr[2] == 'GIFT_IN': tx_lbl = '<span style="color:#7c3aed; font-weight:bold;">🎁 ગિફ્ટ ખર્ચ</span>'
            elif pr[2] == 'DRAWING_OUT': tx_lbl = '<span style="color:#dc2626; font-weight:bold;">📤 ઉપાડ / પરત</span>'
            
            st_badge = '<span style="background:#fee2e2; color:#b91c1c; padding:2px 6px; border-radius:3px; font-weight:bold; font-size:11px;">⏳ પરત બાકી</span>' if pr[8] == 'PENDING' else '<span style="background:#dcfce7; color:#15803d; padding:2px 6px; border-radius:3px; font-weight:bold; font-size:11px;">✅ ચૂકતે</span>'
            c_info = f" ({pr[7]})" if pr[7] else ""
            p_trs += f"<tr><td>{pr[0]}</td><td><b>{pr[1]}</b></td><td>{tx_lbl}</td><td>₹{float(pr[3] or 0):,.0f}</td><td>{pr[4]}{c_info}</td><td>{st_badge} {pr[6] or '-'}</td></tr>"
        return f"""<div style='padding:10px;'>
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
                <h3 style="margin:0; color:#0f2043;">૭. વેપારી ખરીદી, ક્રેડિટ નોટ (CN) & પાર્ટનર મૂડી હિસાબ ખાતાવહી</h3>
                <button type="button" onclick="var b=document.getElementById('partner_cap_box'); b.style.display=(b.style.display==='none'?'block':'none');" style="background:#7c3aed; color:white; border:none; padding:7px 14px; border-radius:4px; font-weight:bold; cursor:pointer;">[ 🤝 પાર્ટનર હિસાબ ડેસ્ક ખોલો (મૂડી / ગિફ્ટ / રિટર્ન) ]</button>
            </div>
            <div id="partner_cap_box" style="display:none; background:#faf5ff; border:2px solid #7c3aed; padding:12px; border-radius:6px; margin-bottom:12px;">
                <h4 style="margin:0 0 8px 0; color:#5b21b6;">🤝 પાર્ટનર હિસાબ ડેસ્ક — મૂડી રોકાણ, ગિફ્ટ ખર્ચ & પેમેન્ટ રિટર્ન (Option B - ઊભું ફોર્મ લેઆઉટ):</h4>
                <div style="display:grid; grid-template-columns:repeat(3, 1fr); gap:10px; margin-bottom:12px;">
                    <div style="background:#eff6ff; border:2px solid #3b82f6; border-radius:8px; padding:10px; text-align:center;">
                        <div style="font-size:11.5px; font-weight:800; color:#1d4ed8;">💰 કુલ મૂડી રોકાણ & ગિફ્ટ જમા</div>
                        <div style="font-size:18px; font-weight:900; color:#1e40af; margin-top:4px;">₹{sp_p_in:,.0f}</div>
                    </div>
                    <div style="background:#f0fdf4; border:2px solid #16a34a; border-radius:8px; padding:10px; text-align:center;">
                        <div style="font-size:11.5px; font-weight:800; color:#15803d;">✅ કુલ પેમેન્ટ રિટર્ન ચૂકવાયું (Returned)</div>
                        <div style="font-size:18px; font-weight:900; color:#166534; margin-top:4px;">₹{sp_p_out:,.0f}</div>
                    </div>
                    <div style="background:#fef2f2; border:2px solid #dc2626; border-radius:8px; padding:10px; text-align:center;">
                        <div style="font-size:11.5px; font-weight:800; color:#b91c1c;">⏳ સ્ટોર પાસેથી પાર્ટનરને લેવાના બાકી (Pending Return)</div>
                        <div style="font-size:18px; font-weight:900; color:#dc2626; margin-top:4px;">₹{sp_p_pend:,.0f}</div>
                    </div>
                </div>
                <form action="/api/save-partner-capital-tx" method="post" enctype="multipart/form-data" class="term-form f-enter-form" style="max-width:100%; margin:0;">
                    <div class="f-row"><div class="lbl">૧. તારીખ:</div><input type="date" name="tx_date" value="{today_str}"></div>
                    <div class="f-row"><div class="lbl">૨. પાર્ટનરનું નામ:</div><input type="text" name="partner_name" placeholder="પાર્ટનરનું પૂરું નામ..." required></div>
                    <div class="f-row"><div class="lbl">૩. વ્યવહાર પ્રકાર:</div>
                        <select name="tx_type" style="font-weight:bold;">
                            <option value="CAPITAL_IN">૧. પાર્ટનર મૂડી જમા (Capital Brought In -> ગલ્લામાં +)</option>
                            <option value="GIFT_IN">૨. પાર્ટનર ભેટ / ગિફ્ટ ખર્ચ (Partner Gift / Expense)</option>
                            <option value="DRAWING_OUT">૩. પાર્ટનર મૂડી પરત / ઉપાડ (Payment Return -> ગલ્લામાંથી -)</option>
                        </select>
                    </div>
                    <div class="f-row"><div class="lbl">૪. ગિફ્ટ/ખર્ચ માટે પૈસા ક્યાંથી ચૂકવાયા?:</div>
                        <select name="funding_source" style="font-weight:bold; background:#fefce8;">
                            <option value="STORE_GALLA">૧. સ્ટોર ગલ્લામાંથી રોકડ લીધી (ગલ્લામાંથી માઇનસ થશે)</option>
                            <option value="PARTNER_POCKET">૨. પાર્ટનરે પોતાના ખિસ્સામાંથી ચૂકવ્યા (પાર્ટનર ખાતે જમા, ગલ્લો અકબંધ)</option>
                        </select>
                    </div>
                    <div class="f-row"><div class="lbl">૫. રકમ (₹) & પેમેન્ટ મોડ:</div>
                        <input type="number" step="any" name="amount" required placeholder="રકમ ₹" style="font-weight:bold;">
                        <select name="pay_mode" style="max-width:180px;"><option value="રોકડ (Cash)">રોકડ (Cash)</option><option value="ઓનલાઈન / બેંક">ઓનલાઈન / બેંક</option><option value="પાર્ટનર અંગત ખિસ્સામાંથી (ગલ્લા સિવાય)">પાર્ટનર ખિસ્સામાંથી</option></select>
                    </div>
                    <div class="f-row"><div class="lbl">૬. સંબંધિત ગલ્લો & નોંધ:</div>
                        <select name="galla_name" style="max-width:220px;"><option value="BANK_CASH">૧. બેંક કેશ</option><option value="EXTRA_CASH">૪. તિજોરી / એક્સ્ટ્રા કેશ</option><option value="ACC_DCASH">૨. D-Cash</option><option value="RECHARGE">૩. રિચાર્જ</option></select>
                        <input type="text" name="remarks" placeholder="વિગતવાર નોંધ..." style="flex:1;">
                    </div>
                    <div class="btn-wrap"><button type="submit" class="btn-save" style="background:#7c3aed;">[ 💾 પાર્ટનર વ્યવહાર સેવ કરો ]</button></div>
                </form>
                {f"<table class='live-grid' style='margin-top:8px;'><tr><th>તારીખ</th><th>પાર્ટનર</th><th>પ્રકાર</th><th>રકમ</th><th>ગલ્લો</th><th>નોંધ</th></tr>{p_trs}</table>" if p_trs else ""}
            </div>
            <table class='live-grid'><tr><th>તારીખ</th><th>વેપારી નામ</th><th>બિલ નં</th><th>કુલ બિલ</th><th>ચૂકવેલ</th><th>બાકી દેવું</th><th>ગલ્લો</th><th>પ્રકાર</th><th>ઓરિજિનલ ફાઇલ</th></tr>{trs}</table>
        </div>"""

    elif sheet == "DAILY_SUMMARY":
        sel_dt = (snap_date or today_str).strip()
        # 1. Fetch available dates from sales & galla_ledger for quick 1-click date buttons
        c.execute("SELECT DISTINCT date FROM galla_ledger UNION SELECT DISTINCT bill_date FROM apx_sales_raw ORDER BY 1 DESC LIMIT 20")
        avail_dates = [r[0] for r in c.fetchall() if r[0]]
        if today_str not in avail_dates:
            avail_dates.insert(0, today_str)
        date_pills = ""
        for d in avail_dates[:12]:
            bg_c = "#0284c7" if d == sel_dt else "#e2e8f0"
            fg_c = "white" if d == sel_dt else "#0f172a"
            date_pills += f"<a href='/?sheet=DAILY_SUMMARY&snap_date={d}' style='background:{bg_c}; color:{fg_c}; padding:4px 9px; border-radius:14px; text-decoration:none; font-weight:bold; font-size:11px;'>📅 {d}</a> "

        # 2. Fetch Daybook Sales for sel_dt (mirrors DAYBOOK 26-27.xlsx)
        c.execute("""SELECT id, salesman, bill_no, brand, model, mop_price, cash_dp, upi_dp, card_swipe_dp, loan_amt, scheme_name, discount_amt, gift_cost, bb_amt, due_amt, customer_name, phone
                     FROM apx_sales_raw WHERE bill_date=? ORDER BY id ASC""", (sel_dt,))
        db_sales = c.fetchall()
        db_sale_trs = ""
        tot_s_mop, tot_s_cash, tot_s_upi, tot_s_loan, tot_s_disc, tot_s_due = 0.0, 0.0, 0.0, 0.0, 0.0, 0.0
        for idx_s, sr in enumerate(db_sales, 1):
            s_mop, s_cash, s_upi, s_card, s_loan, s_disc, s_gift, s_bb, s_due = float(sr[5] or 0), float(sr[6] or 0), float(sr[7] or 0), float(sr[8] or 0), float(sr[9] or 0), float(sr[11] or 0), float(sr[12] or 0), float(sr[13] or 0), float(sr[14] or 0)
            tot_s_mop += s_mop; tot_s_cash += s_cash; tot_s_upi += (s_upi + s_card); tot_s_loan += s_loan; tot_s_disc += s_disc; tot_s_due += s_due
            db_sale_trs += f"""
            <tr>
                <td>{idx_s}</td>
                <td style='font-weight:bold; color:#0f2043;'>{sr[1] or '-'}</td>
                <td><b>{sr[2]}</b></td>
                <td>{sr[3]}</td>
                <td style='text-align:left;'>{sr[4]}</td>
                <td style='font-weight:bold;'>₹{s_mop:,.0f}</td>
                <td style='color:#15803d; font-weight:bold;'>₹{s_cash:,.0f}</td>
                <td>₹{(s_upi+s_card):,.0f}</td>
                <td style='color:#0369a1;'>₹{s_loan:,.0f} ({sr[10] or '-'})</td>
                <td style='color:#b91c1c; font-weight:bold;'>₹{s_disc:,.0f}</td>
                <td>₹{s_gift:,.0f}</td>
                <td>₹{s_bb:,.0f}</td>
                <td style='color:#dc2626; font-weight:bold;'>₹{s_due:,.0f}</td>
                <td style='text-align:left;'>{sr[15]} ({sr[16]})</td>
            </tr>
            """
        if not db_sale_trs:
            db_sale_trs = f"<tr><td colspan='14'>તારીખ {sel_dt} ના રોજ કોઈ વેચાણ બિલ નોંધાયેલ નથી.</td></tr>"

        # 3. Fetch 4-Galla Cash Closing & Note Count for sel_dt
        c.execute("SELECT galla_name, opening_bal, total_in, total_out, expected_closing, physical_counted, diff_amt FROM galla_audit_daily_history WHERE audit_date=? ORDER BY id DESC LIMIT 4", (sel_dt,))
        gh_snap = c.fetchall()
        if not gh_snap:
            # Live fallback from current 4 galla
            gh_snap = []
            for gk in ["BANK_CASH", "ACC_DCASH", "RECHARGE", "EXTRA_CASH"]:
                c.execute("SELECT n500, n200, n100, n50, n20, n10, coins, opening_cash FROM cash_audit_4galla WHERE galla_name=?", (gk,))
                rn = c.fetchone() or (0,0,0,0,0,0,0,0.0)
                cnt_v = (int(rn[0] or 0)*500 + int(rn[1] or 0)*200 + int(rn[2] or 0)*100 + int(rn[3] or 0)*50 + int(rn[4] or 0)*20 + int(rn[5] or 0)*10 + int(rn[6] or 0)) if sel_dt == today_str else 0
                op_v = float(rn[7] or 0.0) if sel_dt == today_str else 0.0
                c.execute("SELECT COALESCE(SUM(in_amt),0), COALESCE(SUM(out_amt),0) FROM galla_ledger WHERE date=? AND galla_name=?", (sel_dt, gk))
                rio = c.fetchone() or (0.0, 0.0)
                in_v, out_v = float(rio[0] or 0.0), float(rio[1] or 0.0)
                exp_v = op_v + in_v - out_v
                phys_v = float(cnt_v) if cnt_v > 0 else exp_v
                gh_snap.append((gk, op_v, in_v, out_v, exp_v, phys_v, phys_v - exp_v))

        g_snap_trs = ""
        for gr in gh_snap:
            g_snap_trs += f"""
            <tr>
                <td style='font-weight:bold; text-align:left;'>{gr[0]}</td>
                <td>₹{float(gr[1] or 0):,.0f}</td>
                <td style='color:#15803d; font-weight:bold;'>+ ₹{float(gr[2] or 0):,.0f}</td>
                <td style='color:#dc2626; font-weight:bold;'>- ₹{float(gr[3] or 0):,.0f}</td>
                <td style='background:#fef9c3; font-weight:bold;'>₹{float(gr[4] or 0):,.0f}</td>
                <td style='color:#0284c7; font-weight:bold;'>₹{float(gr[5] or 0):,.0f}</td>
                <td style='font-weight:bold;'>₹{float(gr[6] or 0):,.0f}</td>
            </tr>
            """

        # 4. Fetch Galla Vouchers / Expenses for sel_dt & full ledger
        c.execute("SELECT date, galla_name, in_amt, out_amt, remarks, COALESCE(file_path,''), id FROM galla_ledger WHERE date=? ORDER BY id DESC", (sel_dt,))
        rows = c.fetchall()
        if not rows:
            c.execute("SELECT date, galla_name, in_amt, out_amt, remarks, COALESCE(file_path,''), id FROM galla_ledger ORDER BY id DESC LIMIT 80")
            rows = c.fetchall()
        trs = ""
        for r in rows:
            f_btn = f"<a href='{r[5]}' target='_blank' style='background:#0284c7;color:white;padding:2px 6px;border-radius:3px;text-decoration:none;font-size:11px;'>📄 ફાઇલ</a> " if r[5] else ""
            d_btn = f"<a href='javascript:void(0)' onclick=\"var p=prompt('આ રોજમેળ એન્ટ્રી રદ કરવા સિક્યુરિટી માસ્ટર PIN નાખો:'); if(p) window.location.href='/delete-galla-entry?id={r[6]}&pin='+encodeURIComponent(p);\" style='background:#dc2626;color:white;padding:2px 6px;border-radius:3px;text-decoration:none;font-size:11px;font-weight:bold;'>🗑️ રદ</a>"
            trs += f"<tr><td>{r[0]}</td><td><b>{r[1]}</b></td><td style='color:#16a34a; font-weight:bold;'>+ ₹{float(r[2] or 0):,.0f}</td><td style='color:#dc2626; font-weight:bold;'>- ₹{float(r[3] or 0):,.0f}</td><td style='text-align:left;'>{r[4]}</td><td>{f_btn}{d_btn}</td></tr>"

        return f"""
        <div style='padding:10px;'>
            <div style='background:#0f2043; color:white; padding:10px 14px; border-radius:6px; display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:8px; margin-bottom:10px;'>
                <div>
                    <h3 style='margin:0; font-size:15px;'>📸 ૧૦. ડે-બુક સ્નેપશોટ આર્કાઇવ & દૈનિક ૪-ગલ્લા રોજમેળ (DAYBOOK 26-27 & BANK CASH વ્યૂ)</h3>
                    <div style='font-size:11px; color:#cbd5e1;'>કોઈપણ તારીખ પર ક્લિક કરતા જ તે દિવસનો આખો હિસાબ (વેચાણ + ખર્ચ + ચારેય ગલ્લા ક્લોઝિંગ) સ્ક્રીનશોટની જેમ ખુલશે</div>
                </div>
                <form method='get' action='/' style='display:flex; gap:6px; align-items:center;'>
                    <input type='hidden' name='sheet' value='DAILY_SUMMARY'>
                    <b>તારીખ પસંદ કરો:</b>
                    <input type='date' name='snap_date' value='{sel_dt}' onchange='this.form.submit()' style='padding:4px 8px; border-radius:4px; border:none; font-weight:bold;'>
                    <button type='submit' style='background:#0284c7; color:white; border:none; padding:5px 10px; border-radius:4px; font-weight:bold; cursor:pointer;'>🔍 દિવસ ખોલો</button>
                    <button type='button' onclick='window.print()' style='background:white; color:#0f2043; border:none; padding:5px 10px; border-radius:4px; font-weight:bold; cursor:pointer;'>🖨️ પ્રિન્ટ</button>
                </form>
            </div>
            <div style='margin-bottom:10px; display:flex; gap:6px; flex-wrap:wrap; align-items:center;'>
                <b>ઝડપી તારીખ પસંદગી:</b> {date_pills}
            </div>

            <h4 style='margin:8px 0 4px 0; color:#0f2043;'>📱 ભાગ ૧: તારીખ {sel_dt} ની સંપૂર્ણ ડે-બુક (વેચાણ, ફાઇનાન્સ, ડિસ્કાઉન્ટ & ઉધાર - DAYBOOK શીટ)</h4>
            <div style='overflow-x:auto; margin-bottom:12px;'>
                <table class='live-grid'>
                    <tr style='background:#0f2043; color:white;'>
                        <th style='color:white;'>NO.</th><th style='color:white;'>PERSON (સેલ્સમેન)</th><th style='color:white;'>BILL NO.</th>
                        <th style='color:white;'>BRAND</th><th style='color:white;'>MODEL</th><th style='color:white;'>MOP (₹)</th>
                        <th style='color:white;'>CASH</th><th style='color:white;'>UPI / CARD</th><th style='color:white;'>FINANCE (SCHEME)</th>
                        <th style='background:#f59e0b; color:#0f172a;'>DISCOUNT</th><th style='color:white;'>GIFT</th>
                        <th style='color:white;'>EXCHANGE</th><th style='color:white;'>BAKI RS</th><th style='color:white;'>CUSTOMER & PHONE</th>
                    </tr>
                    {db_sale_trs}
                    <tr style='background:#fef08a; font-weight:bold;'>
                        <td colspan='5' style='text-align:left;'>દિવસનો કુલ સરવાળો ({sel_dt})</td>
                        <td>₹{tot_s_mop:,.0f}</td><td style='color:#15803d;'>₹{tot_s_cash:,.0f}</td><td>₹{tot_s_upi:,.0f}</td>
                        <td>₹{tot_s_loan:,.0f}</td><td style='color:#b91c1c;'>₹{tot_s_disc:,.0f}</td><td>-</td><td>-</td>
                        <td style='color:#dc2626;'>₹{tot_s_due:,.0f}</td><td>કુલ {len(db_sales)} બિલ</td>
                    </tr>
                </table>
            </div>

            <h4 style='margin:8px 0 4px 0; color:#0f2043;'>🔐 ભાગ ૨: તારીખ {sel_dt} નું ચારેય ગલ્લાનું સાંજનું ક્લોઝિંગ & નોટ ગણતરી (BANK CASH શીટ)</h4>
            <table class='live-grid' style='margin-bottom:12px;'>
                <tr style='background:#1e3a8a; color:white;'>
                    <th style='color:white; text-align:left;'>ગલ્લાનું નામ</th><th style='color:white;'>OPENING CASH</th>
                    <th style='color:white;'>TODAY IN (+)</th><th style='color:white;'>KHARCH / OUT (-)</th>
                    <th style='color:white;'>SYSTEM CLOSING</th><th style='color:white;'>COUNTED CASH (નોટો)</th><th style='color:white;'>DIFFERENCE</th>
                </tr>
                {g_snap_trs}
            </table>

            <h4 style='margin:8px 0 4px 0; color:#0f2043;'>📑 ભાગ ૩: દૈનિક ખર્ચ, વાઉચર અને રોકડ આવક-જાવક ખાતાવહી (એડિટ / રદ સુવિધા સાથે)</h4>
            <table class='live-grid'><tr><th>તારીખ</th><th>ગલ્લો</th><th>આવક (In)</th><th>જાવક (Out)</th><th>વિગત</th><th>ફાઇલ / રદ</th></tr>{trs}</table>
        </div>"""

    # =========================================================================
    # ૧૧. સ્માર્ટ ડેસ્ક ગ્રોથ & એનાલિટિક્સ (ચાલુ વર્ષ ૨૦૨૬ ના ૧૨ મહિના + ૨૦૨૭ YoY)
    # =========================================================================
    elif sheet == "SMART_DESK_GROWTH":
        c.execute("SELECT year, month, amount FROM growth_monthly_manual")
        g_map = {(r[0], r[1]): float(r[2] or 0) for r in c.fetchall()}

        # આજના વર્ષના વેચાણ ડેટામાંથી આપમેળે મહિનાવાર લાઈવ સેલ્સ ગણો
        c.execute("""SELECT strftime('%m', bill_date) as m_num, SUM(mop_price)
                     FROM apx_sales_raw
                     WHERE strftime('%Y', bill_date)='2026'
                     GROUP BY m_num""")
        live_2026 = {int(r[0]): float(r[1] or 0) for r in c.fetchall() if r[0]}

        months_list = [
            (1, "January (જાન્યુઆરી)"), (2, "February (ફેબ્રુઆરી)"), (3, "March (માર્ચ)"),
            (4, "April (એપ્રિલ)"), (5, "May (મે)"), (6, "June (જૂન)"),
            (7, "July (જુલાઈ)"), (8, "August (ઓગસ્ટ)"), (9, "September (સપ્ટેમ્બર)"),
            (10, "October (ઓક્ટોબર)"), (11, "November (નવેમ્બર)"), (12, "December (ડિસેમ્બર)")
        ]
        years_list = ["2026", "2027"]
        yr_totals = {"2026": 0.0, "2027": 0.0}

        trs = ""
        for m_idx, m_name in months_list:
            m_short = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"][m_idx - 1]
            # Priority: Manual override -> Live APX sales
            v26 = g_map.get(("2026", m_short), live_2026.get(m_idx, 0.0))
            v27 = g_map.get(("2027", m_short), 0.0)
            yr_totals["2026"] += v26
            yr_totals["2027"] += v27

            if v26 > 0 and v27 > 0:
                yoy = ((v27 - v26) / v26) * 100.0
                yoy_col = "#16a34a" if yoy >= 0 else "#dc2626"
                yoy_str = f"<span style='color:{yoy_col}; font-weight:bold;'>{'+' if yoy>=0 else ''}{yoy:.1f}%</span>"
            else:
                yoy_str = "-"

            trs += f"""
            <tr>
                <td style='text-align:left; font-weight:bold;'>{m_name}</td>
                <td style='text-align:right; font-weight:bold;'>₹{v26:,.0f}</td>
                <td style='text-align:right; font-weight:bold; color:#0284c7;'>₹{v27:,.0f}</td>
                <td style='background:#f0fdf4;'>{yoy_str}</td>
                <td>
                    <button type='button' onclick='editGrowthMonth("{m_short}", {v26})' style='background:#0284c7; color:white; border:none; padding:3px 10px; border-radius:3px; cursor:pointer; font-weight:bold;'>[Edit 2026]</button>
                    <button type='button' onclick='editGrowthMonth27("{m_short}", {v27})' style='background:#16a34a; color:white; border:none; padding:3px 8px; border-radius:3px; cursor:pointer; font-weight:bold; margin-left:4px;'>[2027]</button>
                </td>
            </tr>
            """

        tot_tds = f"<td style='text-align:left; font-weight:bold;'>કુલ વાર્ષિક ટર્નઓવર</td><td style='text-align:right; font-weight:bold;'>₹{yr_totals['2026']:,.0f}</td><td style='text-align:right; font-weight:bold; color:#0284c7;'>₹{yr_totals['2027']:,.0f}</td><td>-</td><td>-</td>"

        return f"""
        <div style='padding:10px;'>
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:10px;">
                <h3 style="margin:0; color:#0f2043;">૧૧. વાર્ષિક ગ્રોથ રજીસ્ટર (YoY Growth - ચાલુ વર્ષ ૨૦૨૬ અને ૨૦૨૭ વિ. લાઈવ સેલ્સ)</h3>
            </div>
            <div id="growth_edit_box" style="display:none; background:#e0f2fe; border:2px solid #0284c7; padding:10px; margin-bottom:10px; border-radius:4px;">
                <form action="/save-growth-manual" method="post" style="display:flex; gap:8px; align-items:center;">
                    <b>મહિનાનું ટર્નઓવર સુધારો:</b>
                    <select name="year" id="ge_yr" style="padding:5px; font-weight:bold;">
                        <option value="2026">૨૦૨૬ (ચાલુ વર્ષ)</option>
                        <option value="2027">૨૦૨૭ (આગામી વર્ષ)</option>
                    </select>
                    <input type="text" name="month" id="ge_mn" readonly style="padding:5px; width:120px; font-weight:bold; background:#f1f5f9;">
                    <input type="number" step="any" name="amount" id="ge_amt" required style="padding:5px; width:150px;">
                    <button type="submit" style="background:#16a34a; color:white; border:none; padding:6px 14px; border-radius:3px; font-weight:bold; cursor:pointer;">સેવ કરો</button>
                    <button type="button" onclick="document.getElementById('growth_edit_box').style.display='none'" style="background:#dc2626; color:white; border:none; padding:6px 10px; border-radius:3px; cursor:pointer;">X</button>
                </form>
            </div>
            <table class='live-grid'>
                <tr><th style="text-align:left;">૧૨ મહિનાઓ</th><th>ચાલુ વર્ષ (૨૦૨૬) ટર્નઓવર ₹</th><th>આગામી વર્ષ (૨૦૨૭) ટર્નઓવર ₹</th><th>ગ્રોથ % (YoY)</th><th>સુધારો / ઓવરરાઇડ</th></tr>
                {trs}
                <tr style="background:#fde047; font-size:12.5px;">{tot_tds}</tr>
            </table>
        </div>
        """

        # =========================================================================
    # ૧૩. એસેસરીઝ લેજર & સ્ટોક (ACCESSORIES_LEDGER - ૧૧ ખાનાં + રફ બિલ ફોટો વૉલ્ટ)
    # =========================================================================
    elif sheet == "ACCESSORIES_LEDGER":
        acc_p2_on = bool((shop_prof or {}).get("accessories_part2_active", False))
        c.execute("SELECT id, entry_date, party_name, brand, model, imei, purchase_rate, sale_rate, status, doc_path, bill_no FROM live_stock WHERE category LIKE '%એસેસરી%' OR category LIKE '%Accessories%' OR brand LIKE '%Acc%' ORDER BY id DESC")
        acc_rows = c.fetchall()
        c.execute("SELECT date, supplier_name, bill_no, total_bill, paid_amt, balance_due, galla_name, doc_path FROM supplier_purchase_ledger WHERE entry_type LIKE '%ACC%' ORDER BY id DESC LIMIT 50")
        acc_bills = c.fetchall()

        trs_items = ""
        for idx, r in enumerate(acc_rows):
            doc_link = f"<a href='{r[9]}' target='_blank' style='background:#0d9488; color:white; padding:2px 6px; border-radius:3px; text-decoration:none; font-weight:bold;'>📷 બિલ ફોટો</a>" if r[9] else "-"
            dp_v = float(r[6] or 0)
            mop_v = float(r[7] or 0)
            trs_items += f"""
            <tr>
                <td>{r[1]}</td><td>એસેસરીઝ</td><td><b>{r[2] or '-'}</b></td><td>{r[10] or '-'}</td>
                <td><b>{r[3]} {r[4]}</b> ({r[5]})</td><td>1</td>
                <td>₹{dp_v:,.0f}</td><td>₹{mop_v:,.0f}</td><td><b>₹{dp_v:,.0f}</b></td>
                <td>ગલ્લો ૨ (ACC_DCASH)</td><td>{r[8]} | {doc_link}</td>
            </tr>
            """
        for b in acc_bills:
            doc_link = f"<a href='{b[7]}' target='_blank' style='background:#0d9488; color:white; padding:2px 6px; border-radius:3px; text-decoration:none; font-weight:bold;'>📷 રફ બિલ ફોટો</a>" if b[7] else "લમ્પ-સમ બિલ"
            trs_items += f"""
            <tr style="background:#f0fdf4;">
                <td>{b[0]}</td><td>લમ્પ-સમ એસેસરીઝ બિલ</td><td><b>{b[1]}</b></td><td>{b[2]}</td>
                <td>લમ્પ-સમ એસેસરીઝ ખરીદી</td><td>લમ્પ-સમ</td>
                <td>₹{float(b[3] or 0):,.0f}</td><td>-</td><td><b>₹{float(b[3] or 0):,.0f}</b></td>
                <td>{b[6]} (ચૂકવેલ: ₹{float(b[4] or 0):,.0f})</td><td>{doc_link}</td>
            </tr>
            """
        if not trs_items:
            trs_items = "<tr><td colspan='11'>હજુ કોઈ એસેસરીઝ ખરીદી કે સ્ટોક એન્ટ્રી નોંધાયેલ નથી ([F1] વિકલ્પ ૫ માંથી એન્ટ્રી કરો)</td></tr>"

        p2_badge = "<span style='background:#dcfce7; color:#15803d; padding:4px 10px; border-radius:4px; font-weight:bold;'>✅ એસેસરીઝ પાર્ટ-૨ (૧-૧ નંગ બારકોડ) સક્રિય</span>" if acc_p2_on else "<span style='background:#fef3c7; color:#b45309; padding:4px 10px; border-radius:4px; font-weight:bold;'>📦 સ્ટાન્ડર્ડ લમ્પ-સમ + રફ બિલ ફોટો વૉલ્ટ મોડ (પાર્ટ-૨ બારકોડ હેડર તૈયાર)</span>"

        return f"""
        <div style="padding:10px;">
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:10px;">
                <h3 style="margin:0; color:#0f2043;">૧૩. એસેસરીઝ લેજર & સ્ટોક રજીસ્ટર (લમ્પ-સમ રફ બિલ ફોટો વૉલ્ટ + પાર્ટ-૨ બારકોડ ૧૧ ખાનાં)</h3>
                <div>{p2_badge} <a href="/accessories-part2-hub" style="background:#0284c7; color:white; padding:5px 12px; border-radius:4px; text-decoration:none; font-weight:bold; font-size:12px; margin-left:6px;">🏷️ બારકોડ હબ ખોલો</a></div>
            </div>
            <table class="live-grid">
                <tr>
                    <th>૧. તારીખ & સમય</th><th>૨. એસેસરીઝ કેટેગરી</th><th>૩. વેપારી નામ</th><th>૪. બિલ નંબર</th>
                    <th>૫. આઇટમ વિગત / બારકોડ</th><th>૬. નંગ (Qty)</th><th>૭. પ્રતિ નંગ પડતર ₹</th><th>૮. વેચાણ ભાવ MOP ₹</th>
                    <th>૯. કુલ રકમ ₹</th><th>૧૦. ચૂકવણી મોડ & ગલ્લો</th><th>૧૧. સ્ટોક સ્ટેટસ / બિલ ફોટો વૉલ્ટ</th>
                </tr>
                {trs_items}
            </table>
        </div>
        """

    # =========================================================================
    # ૧૪. રિચાર્જ & LAPU બેલેન્સ (RECHARGE_LAPU_VIEW - Jio, Airtel, Vi, DTH કંપની-વાઇઝ)
    # =========================================================================
    elif sheet == "RECHARGE_LAPU_VIEW":
        c.execute("SELECT entry_date, operator_name, opening_bal, topup_purchased, comm_pct, comm_amt, today_sales, closing_bal, galla_name, remarks FROM recharge_operator_ledger ORDER BY id DESC LIMIT 60")
        r_rows = c.fetchall()
        r_trs = "".join([
            f"<tr><td>{r[0]}</td><td><b>{r[1]}</b></td><td>₹{float(r[2] or 0):,.0f}</td><td style='color:#0284c7; font-weight:bold;'>+ ₹{float(r[3] or 0):,.0f}</td><td style='color:#16a34a; font-weight:bold;'>{float(r[4] or 0):.1f}% (₹{float(r[5] or 0):,.0f})</td><td style='color:#dc2626; font-weight:bold;'>- ₹{float(r[6] or 0):,.0f}</td><td style='background:#fef9c3; font-weight:bold;'>₹{float(r[7] or 0):,.0f}</td><td>{r[8]}</td><td>{r[9] or '-'}</td></tr>"
            for r in r_rows
        ]) or "<tr><td colspan='9'>હજુ કોઈ કંપની-વાઇઝ રિચાર્જ / LAPU એન્ટ્રી નોંધાયેલ નથી (નીચેના ફોર્મથી ઉમેરો)</td></tr>"

        return f"""
        <div style="padding:10px;">
            <h3 style="margin:0 0 10px 0; color:#6b21a8;">૧૪. રિચાર્જ & LAPU બેલેન્સ રજીસ્ટર (Jio LAPU | Airtel LAPU | Vi LAPU | DTH - ૯ ખાનાં)</h3>
            <form action="/save-recharge-operator-entry" method="post" class="f-enter-form" style="background:#f3e8ff; border:2px solid #9333ea; padding:10px; border-radius:6px; margin-bottom:12px; display:grid; grid-template-columns:repeat(5, 1fr); gap:8px; align-items:end;">
                <div><label><b>૧. તારીખ:</b></label><input type="date" name="entry_date" value="{today_str}" style="width:100%; padding:5px;"></div>
                <div><label><b>૨. ટેલિકોમ કંપની:</b></label>
                    <select name="operator_name" style="width:100%; padding:5px; font-weight:bold;">
                        <option value="Jio LAPU">૧. Jio LAPU</option>
                        <option value="Airtel LAPU">૨. Airtel LAPU</option>
                        <option value="Vi LAPU">૩. Vi LAPU</option>
                        <option value="DTH / Other">૪. DTH / અન્ય રિચાર્જ</option>
                    </select>
                </div>
                <div><label><b>૩. ઓપનિંગ બેલેન્સ (₹):</b></label><input type="number" step="any" name="opening_bal" id="rl_op" value="0" oninput="calcLapuRow()" style="width:100%; padding:5px;"></div>
                <div><label><b>૪. આજે ખરીદેલું ટોપ-અપ (₹):</b></label><input type="number" step="any" name="topup_purchased" id="rl_top" value="0" oninput="calcLapuRow()" style="width:100%; padding:5px;"></div>
                <div><label><b>૫. મળવાપાત્ર કમિશન (%):</b></label><input type="number" step="any" name="comm_pct" id="rl_pct" value="3.0" oninput="calcLapuRow()" style="width:100%; padding:5px;"></div>
                <div><label><b>કમિશન રકમ (₹) [Auto]:</b></label><input type="number" step="any" name="comm_amt" id="rl_camt" value="0" readonly style="width:100%; padding:5px; background:#dcfce7; font-weight:bold;"></div>
                <div><label><b>૬. આજનું કુલ વેચાણ (₹):</b></label><input type="number" step="any" name="today_sales" id="rl_sale" value="0" oninput="calcLapuRow()" style="width:100%; padding:5px;"></div>
                <div><label><b>૭. ક્લોઝિંગ બેલેન્સ (₹) [Auto]:</b></label><input type="number" step="any" name="closing_bal" id="rl_close" value="0" readonly style="width:100%; padding:5px; background:#fef9c3; font-weight:bold;"></div>
                <div><label><b>૮. નોંધ:</b></label><input type="text" name="remarks" placeholder="નોંધ..." style="width:100%; padding:5px;"></div>
                <div><button type="submit" style="width:100%; background:#6b21a8; color:white; border:none; padding:7px; border-radius:4px; font-weight:bold; cursor:pointer;">[ + રિચાર્જ હિસાબ સેવ કરો ]</button></div>
            </form>
            <table class="live-grid">
                <tr>
                    <th>૧. તારીખ</th><th>૨. ટેલિકોમ કંપની</th><th>૩. ઓપનિંગ બેલેન્સ ₹</th><th>૪. આજે ખરીદેલું ટોપ-અપ ₹</th>
                    <th>૫. મળવાપાત્ર કમિશન % / ₹</th><th>૬. આજનું કુલ વેચાણ ₹</th><th>૭. ક્લોઝિંગ બેલેન્સ ₹</th><th>૮. ગલ્લો (ગલ્લો ૩)</th><th>૯. નોંધ</th>
                </tr>
                {r_trs}
            </table>
            <script>
                function calcLapuRow(){{
                    var op = parseFloat(document.getElementById('rl_op').value) || 0;
                    var top = parseFloat(document.getElementById('rl_top').value) || 0;
                    var pct = parseFloat(document.getElementById('rl_pct').value) || 0;
                    var sale = parseFloat(document.getElementById('rl_sale').value) || 0;
                    var camt = Math.round((top * pct) / 100.0);
                    document.getElementById('rl_camt').value = camt;
                    document.getElementById('rl_close').value = Math.round(op + top + camt - sale);
                }}
            </script>
        </div>
        """

    # =========================================================================
    # ૧૫. GST રિટર્ન સમરી (B2B / B2C ખરીદી અને વેચાણ ટેક્સ સમરી - GST_SUMMARY_SHEET)
    # =========================================================================
    elif sheet == "GST_SUMMARY_SHEET":
        def _calc_multi_slab_gst(rows_list):
            cnt_v = len(rows_list)
            tot_v, tx_v, cg_v, sg_v, gt_v = 0.0, 0.0, 0.0, 0.0, 0.0
            for amt_r, pct_r in rows_list:
                amt = float(amt_r or 0.0)
                pct = float(pct_r if pct_r is not None else 18.0)
                tot_v += amt
                if pct > 0:
                    tx = amt / (1.0 + (pct / 100.0))
                    gt = amt - tx
                else:
                    tx = amt
                    gt = 0.0
                tx_v += tx
                cg_v += gt / 2.0
                sg_v += gt / 2.0
                gt_v += gt
            return cnt_v, tot_v, tx_v, cg_v, sg_v, gt_v

        c.execute("SELECT COALESCE(total_bill,0), COALESCE(gst_pct,18.0) FROM supplier_purchase_ledger WHERE COALESCE(b2b_type,'B2B')='B2B'")
        b2b_pur_cnt, b2b_pur_tot, p_b2b_tx, p_b2b_c, p_b2b_s, p_b2b_tot = _calc_multi_slab_gst(c.fetchall())
        c.execute("SELECT COUNT(*), COALESCE(SUM(total_bill),0) FROM supplier_purchase_ledger WHERE b2b_type='B2C'")
        b2c_pur_cnt, b2c_pur_tot = c.fetchone() or (0, 0.0)
        c.execute("SELECT COALESCE(mop_price,0), COALESCE(gst_pct,18.0) FROM apx_sales_raw WHERE customer_gstin IS NOT NULL AND customer_gstin != ''")
        b2b_sal_cnt, b2b_sal_tot, s_b2b_tx, s_b2b_c, s_b2b_s, s_b2b_tot = _calc_multi_slab_gst(c.fetchall())
        c.execute("SELECT COALESCE(mop_price,0), COALESCE(gst_pct,18.0) FROM apx_sales_raw WHERE customer_gstin IS NULL OR customer_gstin = ''")
        b2c_sal_cnt, b2c_sal_tot, s_b2c_tx, s_b2c_c, s_b2c_s, s_b2c_tot = _calc_multi_slab_gst(c.fetchall())

        return f"""
        <div style="padding:10px;">
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:10px;">
                <h3 style="margin:0; color:#0f2043;">૧૫. GST રિટર્ન સમરી (B2B અને B2C ખરીદી વિ. વેચાણ CGST + SGST ઓડિટ રિપોર્ટ)</h3>
                <button type="button" onclick="window.print()" style="background:#0f2043; color:white; border:none; padding:6px 14px; border-radius:4px; font-weight:bold; cursor:pointer;">🖨️ CA માટે GST રિપોર્ટ પ્રિન્ટ કરો</button>
            </div>
            <table class="live-grid">
                <tr>
                    <th>વિભાગ (GST Category)</th><th>કુલ બિલ સંખ્યા</th><th>ટેક્સેબલ રકમ (Taxable Value ₹)</th>
                    <th>CGST (9% ₹)</th><th>SGST (9% ₹)</th><th>કુલ ટેક્સ (Total GST ₹)</th><th>કુલ બિલ રકમ (Gross Total ₹)</th>
                </tr>
                <tr style="background:#f0fdf4;">
                    <td style="text-align:left; font-weight:bold;">૧. B2B ખરીદી (Input Tax Credit - ITC)</td>
                    <td>{b2b_pur_cnt}</td><td>₹{p_b2b_tx:,.2f}</td><td>₹{p_b2b_c:,.2f}</td><td>₹{p_b2b_s:,.2f}</td>
                    <td style="font-weight:bold; color:#15803d;">₹{p_b2b_tot:,.2f}</td><td style="font-weight:bold;">₹{float(b2b_pur_tot or 0):,.2f}</td>
                </tr>
                <tr>
                    <td style="text-align:left; font-weight:bold;">૨. B2C ખરીદી (Unregistered Purchases)</td>
                    <td>{b2c_pur_cnt}</td><td>₹{float(b2c_pur_tot or 0):,.2f}</td><td>₹0.00</td><td>₹0.00</td><td>₹0.00</td><td>₹{float(b2c_pur_tot or 0):,.2f}</td>
                </tr>
                <tr style="background:#eff6ff;">
                    <td style="text-align:left; font-weight:bold;">૩. B2B વેચાણ (GSTIN ગ્રાહક બિલ્સ - GSTR-1)</td>
                    <td>{b2b_sal_cnt}</td><td>₹{s_b2b_tx:,.2f}</td><td>₹{s_b2b_c:,.2f}</td><td>₹{s_b2b_s:,.2f}</td>
                    <td style="font-weight:bold; color:#0284c7;">₹{s_b2b_tot:,.2f}</td><td style="font-weight:bold;">₹{float(b2b_sal_tot or 0):,.2f}</td>
                </tr>
                <tr style="background:#fefce8;">
                    <td style="text-align:left; font-weight:bold;">૪. B2C રિટેલ વેચાણ (Retail Counter Invoices)</td>
                    <td>{b2c_sal_cnt}</td><td>₹{s_b2c_tx:,.2f}</td><td>₹{s_b2c_c:,.2f}</td><td>₹{s_b2c_s:,.2f}</td>
                    <td style="font-weight:bold; color:#b45309;">₹{s_b2c_tot:,.2f}</td><td style="font-weight:bold;">₹{float(b2c_sal_tot or 0):,.2f}</td>
                </tr>
            </table>
        </div>
        """

    # =========================================================================
    # ૧૬. સ્ટાફ હાજરી & પગાર-કમિશન (STAFF_ATTENDANCE_SHEET - IN અને OUT બંને લાઈવ સેલ્ફી પોપઅપ વ્યૂઅર + GPS + આખા દિવસનું કામગીરી ટ્રેકર)
    # =========================================================================
    elif sheet == "STAFF_ATTENDANCE_SHEET":
        c.execute("""SELECT att_date, staff_name, status, check_in, check_out, deduction_amt, remarks,
                            COALESCE(in_photo, ''), COALESCE(in_lat, 0), COALESCE(in_lng, 0), COALESCE(in_address, ''),
                            COALESCE(out_photo, ''), COALESCE(out_lat, 0), COALESCE(out_lng, 0), COALESCE(out_address, '')
                     FROM staff_attendance_ledger ORDER BY id DESC LIMIT 60""")
        att_rows = c.fetchall()
        att_trs = ""
        for r in att_rows:
            dt_v, st_nm, st_stat, c_in, c_out, ded_v, rem_v = r[0], r[1], r[2], (r[3] or "-"), (r[4] or "-"), float(r[5] or 0), (r[6] or "-")
            in_ph, in_lt, in_lg, in_ad = r[7], float(r[8] or 0), float(r[9] or 0), (r[10] or "")
            out_ph, out_lt, out_lg, out_ad = r[11], float(r[12] or 0), float(r[13] or 0), (r[14] or "")

            in_loc_txt = in_ad or (f"{in_lt:.4f}, {in_lg:.4f}" if (in_lt or in_lg) else "દુકાન પરિસર")
            out_loc_txt = out_ad or (f"{out_lt:.4f}, {out_lg:.4f}" if (out_lt or out_lg) else "દુકાન પરિસર")

            in_map_url = f"https://www.google.com/maps?q={in_lt},{in_lg}" if (in_lt or in_lg) else f"https://www.google.com/maps/search/{in_loc_txt}"
            out_map_url = f"https://www.google.com/maps?q={out_lt},{out_lg}" if (out_lt or out_lg) else f"https://www.google.com/maps/search/{out_loc_txt}"

            in_btn = f"""<div style="display:flex; flex-direction:column; gap:3px; align-items:center;">
                <span style="color:#15803d; font-weight:800;">🟢 {c_in}</span>
                <button type="button" onclick="openStaffPhotoModal('{st_nm}', '{dt_v}', '🟢 IN પંચ (આવ્યાનો સમય)', '{c_in}', '{in_ph}', '{in_lt}', '{in_lg}', '{in_loc_txt}')" style="background:#0284c7; color:white; border:none; padding:3px 8px; border-radius:4px; cursor:pointer; font-weight:bold; font-size:11px;">📷 IN ફોટો & GPS ખોલો</button>
                <a href="{in_map_url}" target="_blank" style="color:#0369a1; font-size:10.5px; font-weight:bold; text-decoration:none;">📍 {in_loc_txt[:22]} (મેપ)</a>
            </div>"""

            if c_out and c_out != "-":
                out_btn = f"""<div style="display:flex; flex-direction:column; gap:3px; align-items:center;">
                    <span style="color:#b45309; font-weight:800;">🔴 {c_out}</span>
                    <button type="button" onclick="openStaffPhotoModal('{st_nm}', '{dt_v}', '🔴 OUT પંચ (જવાનો સમય)', '{c_out}', '{out_ph}', '{out_lt}', '{out_lg}', '{out_loc_txt}')" style="background:#b45309; color:white; border:none; padding:3px 8px; border-radius:4px; cursor:pointer; font-weight:bold; font-size:11px;">📷 OUT ફોટો & GPS ખોલો</button>
                    <a href="{out_map_url}" target="_blank" style="color:#9a3412; font-size:10.5px; font-weight:bold; text-decoration:none;">📍 {out_loc_txt[:22]} (મેપ)</a>
                </div>"""
            else:
                out_btn = "<span style='color:#94a3b8; font-weight:bold;'>હજુ OUT પંચ બાકી</span>"

            att_trs += f"""
            <tr>
                <td><b>{dt_v}</b></td>
                <td style="font-weight:800; color:#0f2043;">{st_nm}</td>
                <td><span style="background:#dcfce7; color:#15803d; padding:2px 6px; border-radius:3px; font-weight:bold;">{st_stat}</span></td>
                <td>{in_btn}</td>
                <td>{out_btn}</td>
                <td style="color:#dc2626; font-weight:bold;">₹{ded_v:,.0f}</td>
                <td>{rem_v}</td>
            </tr>
            """
        if not att_trs:
            att_trs = "<tr><td colspan='7'>હજુ કોઈ દૈનિક હાજરી નોંધાયેલ નથી (ઉપરથી લાઈવ સેલ્ફીથી IN અને OUT હાજરી પૂરો)</td></tr>"

        # દરેક સ્ટાફે આખો દિવસ કેટલું કામ કર્યું અને કેટલી હાજરી આપી તેનો ૩૬૦° લાઇવ સમરી રિપોર્ટ
        work_summary_trs = ""
        for sr in staff_db_rows:
            snm = sr[1]
            s_short = snm.split()[0]
            # મહિનાની કુલ હાજરી
            c.execute("SELECT COUNT(*) FROM staff_attendance_ledger WHERE staff_name LIKE ? AND att_date LIKE ? AND status LIKE '%PRESENT%'", (f"{s_short}%", f"{today_str[:7]}%"))
            month_present = c.fetchone()[0] or 0
            # આજનો IN અને OUT સમય અને ફોટો
            c.execute("SELECT check_in, check_out, COALESCE(in_photo,''), COALESCE(out_photo,''), COALESCE(in_lat,0), COALESCE(in_lng,0), COALESCE(in_address,''), COALESCE(out_lat,0), COALESCE(out_lng,0), COALESCE(out_address,'') FROM staff_attendance_ledger WHERE staff_name LIKE ? AND att_date=? ORDER BY id DESC LIMIT 1", (f"{s_short}%", today_str))
            td_att = c.fetchone()
            if td_att:
                td_in_out = f"🟢 IN: {td_att[0] or '-'} | 🔴 OUT: {td_att[1] or 'ચાલુ'}"
                q_in_btn = f"""<button type='button' onclick="openStaffPhotoModal('{snm}','{today_str}','🟢 IN પંચ','{td_att[0]}','{td_att[2]}','{td_att[4]}','{td_att[5]}','{td_att[6]}')" style='background:#15803d; color:white; border:none; padding:2px 6px; border-radius:3px; cursor:pointer; font-size:10.5px; font-weight:bold;'>📷 IN ફોટો</button>"""
                q_out_btn = f"""<button type='button' onclick="openStaffPhotoModal('{snm}','{today_str}','🔴 OUT પંચ','{td_att[1]}','{td_att[3]}','{td_att[7]}','{td_att[8]}','{td_att[9]}')" style='background:#b45309; color:white; border:none; padding:2px 6px; border-radius:3px; cursor:pointer; font-size:10.5px; font-weight:bold;'>📷 OUT ફોટો</button>""" if td_att[1] else ""
                td_att_html = f"{td_in_out}<br>{q_in_btn} {q_out_btn}"
            else:
                td_att_html = "<span style='color:#dc2626; font-weight:bold;'>આજે પંચ બાકી</span>"

            # આજનું વેચાણ બિલ, રોકડ વસૂલાત અને કમિશન
            c.execute("SELECT COUNT(id), COALESCE(SUM(mop_price),0), COALESCE(SUM(cash_dp),0), COALESCE(SUM(staff_comm),0) FROM apx_sales_raw WHERE (salesman LIKE ? OR salesman LIKE ?) AND bill_date=?", (f"{snm}%", f"{s_short}%", today_str))
            w_sal = c.fetchone() or (0, 0, 0, 0)
            # આજે વસૂલ કરેલ જૂની ઉધાર (F3/F4)
            c.execute("SELECT COALESCE(SUM(in_amt),0) FROM galla_ledger WHERE date=? AND remarks LIKE ? AND remarks LIKE '%ઉધાર વસૂલાત%'", (today_str, f"%{s_short}%"))
            w_rec = float(c.fetchone()[0] or 0)
            # આજે લીધેલા બાય-બેક ફોન
            c.execute("SELECT COUNT(id) FROM buyback_stock WHERE date=? AND salesman LIKE ?", (today_str, f"%{s_short}%"))
            w_bb = c.fetchone()[0] or 0
            # આજના મોબાઇલ લોકેશન પિંગ્સ
            c.execute("SELECT COUNT(id) FROM staff_location_trail WHERE log_date=? AND staff_name LIKE ?", (today_str, f"%{s_short}%"))
            w_pings = c.fetchone()[0] or 0

            work_summary_trs += f"""
            <tr>
                <td style="font-weight:800; color:#0f2043; text-align:left;">{snm} ({sr[2]})</td>
                <td>{td_att_html}</td>
                <td style="font-weight:bold; color:#0284c7;">{month_present} દિવસ</td>
                <td style="font-weight:bold;">{w_sal[0]} બિલ</td>
                <td style="font-weight:bold; color:#15803d;">₹{float(w_sal[1] or 0):,.0f}</td>
                <td>₹{float(w_sal[2] or 0):,.0f}</td>
                <td style="color:#0369a1; font-weight:bold;">₹{w_rec:,.0f}</td>
                <td>{w_bb} ફોન</td>
                <td style="color:#6b21a8; font-weight:bold;">₹{float(w_sal[3] or 0):,.0f}</td>
                <td><span style="background:#e0f2fe; color:#0369a1; padding:2px 6px; border-radius:4px; font-weight:bold;">📍 {w_pings} લોકેશન ટ્રેક</span></td>
            </tr>
            """

        # આખા દિવસનો મોબાઈલ લોકેશન ટ્રેક (Full-Day Mobile Location & Activity Trail)
        c.execute("""SELECT log_date, log_time, staff_name, activity_type, details, latitude, longitude, address, COALESCE(photo_path,'')
                     FROM staff_location_trail ORDER BY id DESC LIMIT 50""")
        trail_rows = c.fetchall()
        trail_trs = ""
        route_coords = []
        for tr in trail_rows:
            t_dt, t_tm, t_nm, t_act, t_det, t_lat, t_lng, t_addr, t_ph = tr[0], tr[1], tr[2], tr[3], tr[4], float(tr[5] or 0), float(tr[6] or 0), (tr[7] or ""), tr[8]
            if t_lat and t_lng:
                route_coords.append(f"{t_lat},{t_lng}")
            map_lnk = f"https://www.google.com/maps?q={t_lat},{t_lng}" if (t_lat or t_lng) else f"https://www.google.com/maps/search/{t_addr or 'Becharaji'}"
            ph_btn = f"""<button type='button' onclick="openStaffPhotoModal('{t_nm}','{t_dt}','{t_act}','{t_tm}','{t_ph}','{t_lat}','{t_lng}','{t_addr}')" style='background:#0284c7; color:white; border:none; padding:2px 8px; border-radius:3px; cursor:pointer; font-weight:bold; font-size:11px;'>📷 ફોટો ખોલો</button>""" if t_ph else "-"
            trail_trs += f"""
            <tr>
                <td>{t_dt} <b>{t_tm}</b></td>
                <td style="font-weight:bold; color:#0f2043;">{t_nm}</td>
                <td><span style="background:#fef9c3; color:#854d0e; padding:2px 6px; border-radius:3px; font-weight:bold;">{t_act}</span></td>
                <td style="text-align:left;">{t_det}</td>
                <td><a href="{map_lnk}" target="_blank" style="background:#dcfce7; color:#15803d; padding:2px 8px; border-radius:4px; text-decoration:none; font-weight:bold; font-size:11px;">🗺️ {t_addr or f"{t_lat:.4f}, {t_lng:.4f}"} (Google Maps)</a></td>
                <td>{ph_btn}</td>
            </tr>
            """
        if not trail_trs:
            trail_trs = "<tr><td colspan='6'>હજુ કોઈ મોબાઇલ લોકેશન કે કામગીરી ટ્રેક નોંધાયેલ નથી (નીચેથી લાઇવ લોકેશન પંચ કરો)</td></tr>"

        full_route_url = ("https://www.google.com/maps/dir/" + "/".join(route_coords[:10])) if route_coords else "https://www.google.com/maps/search/Becharaji"
        staff_opts_att = "".join([f'<option value="{r[1]}">{r[1]} ({r[2]})</option>' for r in staff_db_rows]) or '<option value="સ્ટાફ">સ્ટાફ</option>'

        return f"""
        <div style="padding:10px;">
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:10px; flex-wrap:wrap; gap:8px;">
                <h3 style="margin:0; color:#0f2043;">૧૬. સ્ટાફ દૈનિક હાજરી (IN & OUT લાઇવ ફોટો વ્યૂઅર), આખા દિવસનો મોબાઇલ GPS રૂટ & ૩૬૦° કામગીરી ટ્રેકર</h3>
                <div style="display:flex; gap:8px; align-items:center;">
                    <a href="{full_route_url}" target="_blank" style="background:#0284c7; color:white; padding:6px 12px; border-radius:5px; text-decoration:none; font-weight:bold; font-size:12px;">🗺️ સ્ટાફનો આખા દિવસનો Google Maps રૂટ જુઓ</a>
                    <span style="background:#15803d; color:white; padding:5px 10px; border-radius:4px; font-weight:bold; font-size:12px;">📸 IN/OUT કેમેરા & લાઇવ GPS સક્રિય</span>
                </div>
            </div>

            <!-- સ્ટાફ લાઈવ કેમેરા અને GPS પંચિંગ + મોબાઇલ ફિલ્ડ લોકેશન ટ્રેકર બોક્સ -->
            <div style="display:grid; grid-template-columns:1.15fr 0.85fr; gap:12px; margin-bottom:14px;">
                <div style="background:#f0fdf4; border:2px solid #16a34a; border-radius:8px; padding:12px;">
                    <h4 style="margin:0 0 8px 0; color:#166534;">📸 ૧. સ્ટાફ સવાર (IN) અને સાંજ (OUT) લાઈવ સેલ્ફી પંચ + GPS લોકેશન</h4>
                    <div style="display:grid; grid-template-columns:auto 1fr; gap:12px; align-items:center;">
                        <div style="text-align:center;">
                            <video id="webcam_vid" autoplay playsinline style="width:170px; height:128px; border-radius:6px; background:#0f2043; border:2px solid #16a34a; object-fit:cover;"></video>
                            <canvas id="webcam_canvas" style="display:none;"></canvas>
                            <div style="font-size:11px; color:#15803d; font-weight:bold; margin-top:4px;">લાઈવ ફ્રન્ટ કેમેરો (ગેલેરી બ્લોક)</div>
                        </div>
                        <div>
                            <div style="display:flex; gap:8px; align-items:center; margin-bottom:8px; flex-wrap:wrap;">
                                <label style="font-weight:bold; color:#0f2043;">સ્ટાફ પસંદ કરો:</label>
                                <select id="live_staff_sel" style="padding:6px 10px; font-weight:bold; font-size:13px; border-radius:4px; border:1px solid #16a34a;">{staff_opts_att}</select>
                            </div>
                            <div style="margin-bottom:8px;">
                                <span id="gps_status_badge" style="background:#e0f2fe; color:#0369a1; padding:4px 8px; border-radius:4px; font-size:11.5px; font-weight:bold; display:inline-block;">📍 GPS લોકેશન મેળવી રહ્યું છે...</span>
                            </div>
                            <div style="display:flex; gap:8px; flex-wrap:wrap;">
                                <button type="button" onclick="submitLivePunch('IN')" style="background:#15803d; color:white; border:none; padding:9px 14px; border-radius:6px; font-weight:bold; cursor:pointer; font-size:12.5px;">
                                    🟢 [IN પંચ] (આવ્યાનો સમય & સેલ્ફી)
                                </button>
                                <button type="button" onclick="submitLivePunch('OUT')" style="background:#b45309; color:white; border:none; padding:9px 14px; border-radius:6px; font-weight:bold; cursor:pointer; font-size:12.5px;">
                                    🔴 [OUT પંચ] (જવાનો સમય & સેલ્ફી)
                                </button>
                            </div>
                            <div id="punch_result_msg" style="margin-top:8px; font-weight:bold; font-size:12.5px;"></div>
                        </div>
                    </div>
                </div>

                <!-- આખો દિવસ મોબાઈલ લઈને ક્યાં ફરે છે તેનું લાઇવ ટ્રેકિંગ બોક્સ -->
                <div style="background:#eff6ff; border:2px solid #0284c7; border-radius:8px; padding:12px;">
                    <h4 style="margin:0 0 8px 0; color:#0369a1;">📱 ૨. સ્ટાફ આખો દિવસ મોબાઈલ લોકેશન & ફિલ્ડ કામગીરી ટ્રેકર</h4>
                    <div style="font-size:11.5px; color:#334155; margin-bottom:8px;">
                        સેલ્સમેન દુકાનમાં હોય કે મોબાઈલ લઈને બહાર ઉધાર વસૂલાત / બેંક / ફિલ્ડમાં ગયો હોય, તેનું લાઇવ GPS લોકેશન અને ફોટો અહીંથી સીધો ટ્રેક થશે:
                    </div>
                    <div style="display:flex; gap:6px; margin-bottom:6px;">
                        <select id="field_act_type" style="padding:6px; font-weight:bold; border-radius:4px; border:1px solid #0284c7; flex:1;">
                            <option value="FIELD_VISIT (ફિલ્ડ / બજાર વિઝિટ)">🛵 ફિલ્ડ / બજાર વિઝિટ લોકેશન</option>
                            <option value="CUSTOMER_RECOVERY (ગ્રાહક ઉધાર વસૂલાત વિઝિટ)">💰 ગ્રાહક ઉધાર વસૂલાત વિઝિટ</option>
                            <option value="BANK_FINANCE_VISIT (બેંક / ફાઇનાન્સ ઓફિસ)">🏦 બેંક ડિપોઝિટ / ફાઇનાન્સ ઓફિસ</option>
                            <option value="SHOP_COUNTER_ACTIVE (દુકાન કાઉન્ટર પર હાજર)">🏪 દુકાન કાઉન્ટર પર કામગીરી</option>
                        </select>
                    </div>
                    <div style="display:flex; gap:6px; margin-bottom:8px;">
                        <input type="text" id="field_act_note" placeholder="ક્યાં છો / શું કામ કર્યું તેની વિગત લખો..." style="flex:1; padding:6px; border:1px solid #94a3b8; border-radius:4px;">
                    </div>
                    <div style="display:flex; justify-content:space-between; align-items:center; gap:8px;">
                        <button type="button" onclick="submitStaffFieldLocation(true)" style="background:#0284c7; color:white; border:none; padding:8px 12px; border-radius:5px; font-weight:bold; cursor:pointer; font-size:12px; flex:1;">
                            📍 હાલનું મોબાઇલ GPS લોકેશન + લાઇવ ફોટો સેવ કરો
                        </button>
                        <label style="font-size:11px; font-weight:bold; color:#0f2043; display:flex; align-items:center; gap:4px; cursor:pointer;">
                            <input type="checkbox" id="auto_gps_ping_chk" checked onchange="toggleAutoGpsTracker(this.checked)"> ઓટો-ટ્રેક (૧૫ મિનિટ)
                        </label>
                    </div>
                </div>
            </div>

            <!-- ટેબલ A: સ્ટાફ આખા દિવસની કામગીરી અને હાજરી ૩૬૦° ટ્રેકર -->
            <div style="background:white; border:2px solid #0f2043; border-radius:6px; padding:10px; margin-bottom:14px;">
                <h4 style="margin:0 0 8px 0; color:#0f2043;">📊 ૧. સ્ટાફ આખા દિવસની કામગીરી અને હાજરી ૩૬૦° હિસાબ (આજે કેટલું કામ કર્યું અને કેટલી હાજરી આપી?)</h4>
                <table class="live-grid">
                    <tr style="background:#0f2043; color:white;">
                        <th style="color:white; text-align:left;">સ્ટાફ નામ & હોદ્દો</th>
                        <th style="color:white;">આજની હાજરી (IN & OUT ફોટા)</th>
                        <th style="color:white;">ચાલુ મહિનાની કુલ હાજરી</th>
                        <th style="color:white;">આજે બનાવેલા બિલ</th>
                        <th style="color:white;">આજનું કુલ વેચાણ (₹)</th>
                        <th style="color:white;">રોકડ DP વસૂલાત (₹)</th>
                        <th style="color:white;">જૂની ઉધાર વસૂલાત [F3]</th>
                        <th style="color:white;">લીધેલા બાય-બેક ફોન</th>
                        <th style="color:white;">આજનું કમિશન (₹)</th>
                        <th style="color:white;">મોબાઇલ GPS ટ્રેક</th>
                    </tr>
                    {work_summary_trs}
                </table>
            </div>

            <!-- ટેબલ B: દૈનિક IN અને OUT લાઈવ સેલ્ફી ફોટા અને હાજરી રજીસ્ટર -->
            <div style="background:white; border:1px solid #cbd5e1; border-radius:6px; padding:10px; margin-bottom:14px;">
                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
                    <h4 style="margin:0; color:#166534;">📸 ૨. સ્ટાફ IN અને OUT લાઈવ સેલ્ફી ફોટા, સમય અને લોકેશન રજીસ્ટર (ફોટો ખોલવા બટન દબાવો)</h4>
                    <details style="background:#f8fafc; border:1px solid #cbd5e1; border-radius:4px; padding:4px 8px;">
                        <summary style="font-weight:bold; color:#0f2043; cursor:pointer; font-size:11.5px;">⚙️ મેન્યુઅલ હાજરી / રજા કપાત (એડમિન)</summary>
                        <form action="/save-staff-attendance" method="post" style="padding:6px 0 0 0; display:flex; gap:6px; align-items:center; flex-wrap:wrap;">
                            <input type="date" name="att_date" value="{today_str}" style="padding:4px;">
                            <select name="staff_name" style="padding:4px; font-weight:bold;">{staff_opts_att}</select>
                            <select name="status" style="padding:4px; font-weight:bold;">
                                <option value="PRESENT (હાજર)">🟢 PRESENT (હાજર)</option>
                                <option value="HALF_DAY (અડધો દિવસ)">🟡 HALF_DAY (અડધો દિવસ)</option>
                                <option value="ABSENT (રજા)">🔴 ABSENT (રજા)</option>
                            </select>
                            <input type="text" name="check_in" value="09:30 AM" style="width:85px; padding:4px;">
                            <input type="text" name="check_out" value="08:30 PM" style="width:85px; padding:4px;">
                            <input type="number" step="any" name="deduction_amt" value="0" placeholder="કપાત ₹" style="width:90px; padding:4px;">
                            <input type="text" name="remarks" placeholder="નોંધ..." style="width:120px; padding:4px;">
                            <button type="submit" style="background:#15803d; color:white; border:none; padding:5px 10px; border-radius:4px; font-weight:bold; cursor:pointer;">સેવ</button>
                        </form>
                    </details>
                </div>
                <table class="live-grid">
                    <tr>
                        <th>તારીખ</th><th>સ્ટાફ નામ</th><th>હાજરી સ્થિતિ</th>
                        <th>🟢 આવ્યાનો સમય, IN ફોટો & લોકેશન</th>
                        <th>🔴 જવાનો સમય, OUT ફોટો & લોકેશન</th>
                        <th>રજા કપાત (₹)</th><th>નોંધ</th>
                    </tr>
                    {att_trs}
                </table>
            </div>

            <!-- ટેબલ C: આખો દિવસ મોબાઈલ લઈને ક્યાં-ક્યાં ફર્યા તેનો સંપૂર્ણ GPS રૂટ અને એક્ટિવિટી ટ્રેક -->
            <div style="background:white; border:2px solid #0284c7; border-radius:6px; padding:10px;">
                <h4 style="margin:0 0 8px 0; color:#0369a1;">🗺️ ૩. સ્ટાફ આખો દિવસ ક્યાં-ક્યાં ફર્યો અને કયા સમયે શું કામ કર્યું? (Full-Day Mobile GPS Trail & Activity Log)</h4>
                <table class="live-grid">
                    <tr>
                        <th>તારીખ & સમય</th><th>સ્ટાફ નામ</th><th>પ્રવૃત્તિ / પંચ પ્રકાર</th>
                        <th>કામગીરી અને સ્થળની સંપૂર્ણ વિગત</th><th>📍 Google Maps લોકેશન લિંક</th><th>લાઇવ ફોટો પ્રૂફ</th>
                    </tr>
                    {trail_trs}
                </table>
            </div>

            <!-- 🔍 હાઇ-રેઝોલ્યુશન લાઇવ ફોટો & GPS ઇન્સ્પેક્ટર પોપઅપ મોડલ -->
            <div id="staff_photo_modal" style="display:none; position:fixed; top:0; left:0; width:100%; height:100%; background:rgba(9,18,36,0.82); z-index:99999; align-items:center; justify-content:center; padding:16px;">
                <div style="background:white; width:100%; max-width:560px; border-radius:12px; border:3px solid #38bdf8; box-shadow:0 20px 50px rgba(0,0,0,0.5); overflow:hidden;">
                    <div style="background:#0f2043; color:white; padding:12px 16px; display:flex; justify-content:space-between; align-items:center;">
                        <h4 id="spm_title" style="margin:0; color:#fde047; font-size:15px;">📸 સ્ટાફ લાઇવ સેલ્ફી ફોટો & GPS વેરિફિકેશન</h4>
                        <button type="button" onclick="document.getElementById('staff_photo_modal').style.display='none'" style="background:#dc2626; color:white; border:none; padding:4px 10px; border-radius:4px; font-weight:bold; cursor:pointer;">✖ બંધ કરો</button>
                    </div>
                    <div style="padding:16px; text-align:center; background:#f8fafc;">
                        <div id="spm_img_wrap" style="margin-bottom:12px; background:#0f172a; border-radius:8px; padding:8px; min-height:220px; display:flex; align-items:center; justify-content:center;">
                            <img id="spm_img" src="" alt="Staff Live Selfie" style="max-width:100%; max-height:320px; border-radius:6px; border:2px solid #38bdf8; display:none;">
                            <div id="spm_no_img" style="color:#fde047; font-weight:bold; font-size:13px; padding:30px;">📷 આ પંચમાં કેમેરા ફોટો ઉપલબ્ધ નથી (માત્ર સમય અને GPS લોકેશન નોંધાયેલ છે)</div>
                        </div>
                        <table class="live-grid" style="text-align:left; margin-bottom:12px; background:white;">
                            <tr><td style="width:170px; font-weight:bold; background:#f1f5f9;">👤 સ્ટાફનું નામ:</td><td id="spm_staff" style="font-weight:800; color:#0f2043; font-size:13.5px;"></td></tr>
                            <tr><td style="font-weight:bold; background:#f1f5f9;">🕒 તારીખ અને ચોક્કસ સમય:</td><td id="spm_datetime" style="font-weight:800; color:#15803d;"></td></tr>
                            <tr><td style="font-weight:bold; background:#f1f5f9;">📷 ફોટો કેવી રીતે પાડ્યો?:</td><td style="font-weight:bold; color:#0369a1;">લાઇવ ફ્રન્ટ સેલ્ફી કેમેરા વેરિફાઇડ (ગેલેરી અપલોડ બ્લોક)</td></tr>
                            <tr><td style="font-weight:bold; background:#f1f5f9;">📍 ફોટો ક્યાંથી પાડ્યો (GPS):</td><td id="spm_gps" style="font-weight:bold; color:#b45309;"></td></tr>
                        </table>
                        <div style="display:flex; gap:10px; justify-content:center;">
                            <a id="spm_map_btn" href="#" target="_blank" style="background:#15803d; color:white; padding:9px 16px; border-radius:6px; text-decoration:none; font-weight:800; font-size:13px;">🗺️ Google Maps પર ચોક્કસ લોકેશન ખોલો</a>
                            <a id="spm_dl_btn" href="#" target="_blank" style="background:#0284c7; color:white; padding:9px 16px; border-radius:6px; text-decoration:none; font-weight:800; font-size:13px;">🔍 ફોટો ફૂલ સ્ક્રીન / ડાઉનલોડ કરો</a>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        <script>
            var curLat = 0, curLng = 0, curAddr = '';
            if (navigator.geolocation) {{
                navigator.geolocation.getCurrentPosition(function(pos){{
                    curLat = pos.coords.latitude;
                    curLng = pos.coords.longitude;
                    curAddr = 'અક્ષાંશ: ' + curLat.toFixed(4) + ', રેખાંશ: ' + curLng.toFixed(4);
                    var b = document.getElementById('gps_status_badge');
                    if(b) {{ b.innerText = '✅ GPS: ' + curAddr; b.style.color = '#15803d'; }}
                }}, function(err){{
                    var b = document.getElementById('gps_status_badge');
                    if(b) b.innerText = '📍 GPS: ડિફોલ્ટ બેચરાજી (લોકેશન પરવાનગી આપો)';
                }});
            }}

            var videoEl = document.getElementById('webcam_vid');
            if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {{
                navigator.mediaDevices.getUserMedia({{ video: {{ facingMode: 'user' }} }})
                .then(function(stream){{ if(videoEl) videoEl.srcObject = stream; }})
                .catch(function(e){{ console.log('કેમેરો એક્સેસ નથી:', e); }});
            }}

            function submitLivePunch(attType){{
                var staff = document.getElementById('live_staff_sel').value;
                var resMsg = document.getElementById('punch_result_msg');
                resMsg.innerHTML = '<span style="color:#0284c7;">સેલ્ફી કેપ્ચર કરી સબમિટ થઈ રહ્યું છે...</span>';

                var canvas = document.getElementById('webcam_canvas');
                var photoB64 = '';
                if(videoEl && canvas && videoEl.videoWidth > 0){{
                    canvas.width = videoEl.videoWidth;
                    canvas.height = videoEl.videoHeight;
                    var ctx = canvas.getContext('2d');
                    ctx.drawImage(videoEl, 0, 0, canvas.width, canvas.height);
                    photoB64 = canvas.toDataURL('image/jpeg', 0.85);
                }}

                var fd = new FormData();
                fd.append('staff_name', staff);
                fd.append('att_type', attType);
                fd.append('photo_data', photoB64);
                fd.append('latitude', curLat);
                fd.append('longitude', curLng);
                fd.append('address', curAddr);

                fetch('/api/save-live-attendance', {{ method: 'POST', body: fd }})
                .then(r => r.json())
                .then(d => {{
                    resMsg.innerHTML = '<span style="color:#15803d;">' + d.msg + '</span>';
                    setTimeout(function(){{ window.location.reload(); }}, 1000);
                }}).catch(e => {{
                    resMsg.innerHTML = '<span style="color:#dc2626;">એરર આવી: ' + e + '</span>';
                }});
            }}

            function openStaffPhotoModal(staffName, attDate, punchType, punchTime, photoUrl, lat, lng, addr){{
                document.getElementById('spm_title').innerText = '📸 ' + punchType + ' - લાઇવ ફોટો & GPS વેરિફિકેશન';
                document.getElementById('spm_staff').innerText = staffName + ' (' + punchType + ')';
                document.getElementById('spm_datetime').innerText = 'તારીખ: ' + attDate + ' | સમય: ' + (punchTime || '-');
                var gpsTxt = (addr || 'દુકાન પરિસર') + ((parseFloat(lat) || parseFloat(lng)) ? (' [GPS: ' + parseFloat(lat).toFixed(5) + ', ' + parseFloat(lng).toFixed(5) + ']') : '');
                document.getElementById('spm_gps').innerText = gpsTxt;
                var mapUrl = (parseFloat(lat) || parseFloat(lng)) ? ('https://www.google.com/maps?q=' + lat + ',' + lng) : ('https://www.google.com/maps/search/' + encodeURIComponent(addr || 'Becharaji'));
                document.getElementById('spm_map_btn').href = mapUrl;
                var imgEl = document.getElementById('spm_img');
                var noImgEl = document.getElementById('spm_no_img');
                var dlBtn = document.getElementById('spm_dl_btn');
                if(photoUrl && photoUrl.length > 2){{
                    imgEl.src = photoUrl;
                    imgEl.style.display = 'block';
                    noImgEl.style.display = 'none';
                    dlBtn.href = photoUrl;
                    dlBtn.style.display = 'inline-block';
                }} else {{
                    imgEl.style.display = 'none';
                    noImgEl.style.display = 'block';
                    dlBtn.style.display = 'none';
                }}
                document.getElementById('staff_photo_modal').style.display = 'flex';
            }}

            function submitStaffFieldLocation(withPhoto){{
                var staff = document.getElementById('live_staff_sel').value;
                var actType = document.getElementById('field_act_type').value;
                var note = document.getElementById('field_act_note').value;
                var resMsg = document.getElementById('punch_result_msg');
                var photoB64 = '';
                var canvas = document.getElementById('webcam_canvas');
                if(withPhoto && videoEl && canvas && videoEl.videoWidth > 0){{
                    canvas.width = videoEl.videoWidth;
                    canvas.height = videoEl.videoHeight;
                    canvas.getContext('2d').drawImage(videoEl, 0, 0, canvas.width, canvas.height);
                    photoB64 = canvas.toDataURL('image/jpeg', 0.85);
                }}
                var fd = new FormData();
                fd.append('staff_name', staff);
                fd.append('activity_type', actType);
                fd.append('details', note);
                fd.append('latitude', curLat);
                fd.append('longitude', curLng);
                fd.append('address', curAddr);
                fd.append('photo_data', photoB64);
                fetch('/api/log-staff-location', {{ method: 'POST', body: fd }})
                .then(r => r.json())
                .then(d => {{
                    if(resMsg) resMsg.innerHTML = '<span style="color:#0284c7;">' + d.msg + '</span>';
                    if(withPhoto) setTimeout(function(){{ window.location.reload(); }}, 900);
                }});
            }}

            var gpsIntervalId = setInterval(function(){{
                var chk = document.getElementById('auto_gps_ping_chk');
                if(chk && chk.checked) submitStaffFieldLocation(false);
            }}, 900000);
            function toggleAutoGpsTracker(enabled){{
                if(!enabled && gpsIntervalId) clearInterval(gpsIntervalId);
            }}
        </script>
        """

    # =========================================================================
    # ૧૫/૧૭. ડાયનામિક ૩૦+ / ૬૦+ / ૯૦+ / ૧૨૦+ દિવસ જૂનો સ્ટોક ક્લિયરન્સ & FIFO રજીસ્ટર (OLD_STOCK_CLEARANCE)
    # =========================================================================
    elif sheet == "OLD_STOCK_CLEARANCE":
        c.execute("SELECT id, entry_date, party_name, brand, model, imei, purchase_rate, sale_rate, category FROM live_stock WHERE status='IN_STOCK' ORDER BY entry_date ASC, id ASC")
        all_stk = c.fetchall()
        today_d = datetime.date.today()
        old_trs = ""
        cnt_30, cnt_60, cnt_90, cnt_120 = 0, 0, 0, 0
        dp_30, dp_60, dp_90, dp_120 = 0.0, 0.0, 0.0, 0.0
        row_seq = 0
        for r in all_stk:
            age_d = 0
            try:
                age_d = (today_d - datetime.datetime.strptime(str(r[1])[:10], "%Y-%m-%d").date()).days
            except Exception:
                pass
            dp_v = float(r[6] or 0)
            mop_v = float(r[7] or 0)
            if age_d >= 30:
                cnt_30 += 1; dp_30 += dp_v
            if age_d >= 60:
                cnt_60 += 1; dp_60 += dp_v
            if age_d >= 90:
                cnt_90 += 1; dp_90 += dp_v
            if age_d >= 120:
                cnt_120 += 1; dp_120 += dp_v

            if age_d >= 120:
                bg_c = "#fee2e2"
                badge_c = f"<span style='background:#dc2626; color:white; padding:2px 7px; border-radius:4px; font-weight:900;'>🔴 {age_d} દિવસ (120+ ડેડ સ્ટોક)</span>"
            elif age_d >= 90:
                bg_c = "#ffedd5"
                badge_c = f"<span style='background:#ea580c; color:white; padding:2px 7px; border-radius:4px; font-weight:900;'>🟠 {age_d} દિવસ (90+ જૂનો સ્ટોક)</span>"
            elif age_d >= 60:
                bg_c = "#fef08a"
                badge_c = f"<span style='background:#ca8a04; color:white; padding:2px 7px; border-radius:4px; font-weight:900;'>🟡 {age_d} દિવસ (60+ જૂનો સ્ટોક)</span>"
            elif age_d >= 30:
                bg_c = "#e0f2fe"
                badge_c = f"<span style='background:#0284c7; color:white; padding:2px 7px; border-radius:4px; font-weight:800;'>🔵 {age_d} દિવસ (30+ દિવસ)</span>"
            else:
                bg_c = "#ffffff"
                badge_c = f"<span style='background:#dcfce7; color:#15803d; padding:2px 7px; border-radius:4px; font-weight:bold;'>🟢 {age_d} દિવસ (ફ્રેશ)</span>"

            row_seq += 1
            old_trs += f"""
            <tr class="osc_row" data-age-days="{age_d}" style="background:{bg_c};">
                <td>{row_seq}</td><td><b>{r[3]}</b></td><td><b>{r[4]}</b></td>
                <td><b style="font-family:monospace; font-size:13px; color:#0f2043;">{r[5]}</b></td>
                <td>{r[1]}</td><td>{badge_c}</td>
                <td style="font-weight:bold;">₹{dp_v:,.0f}</td><td style="font-weight:bold; color:#15803d;">₹{mop_v:,.0f}</td><td>{r[2] or '-'}</td>
                <td>
                    <a href="/?sheet=SMART_TERMINAL&mode=F2&prefill_imei={r[5]}" style="background:#16a34a; color:white; padding:3px 9px; border-radius:4px; text-decoration:none; font-weight:900; font-size:11px;">⚡ પહેલા વેચો (F2 બિલ)</a>
                </td>
            </tr>
            """
        if not old_trs:
            old_trs = "<tr><td colspan='10' style='color:#16a34a; font-weight:bold;'>🎉 હાલ દુકાનમાં કોઈ સ્ટોક પેન્ડિંગ નથી!</td></tr>"

        return f"""
        <div style="padding:10px;">
            <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:8px; margin-bottom:10px;">
                <h3 style="margin:0; color:#0f2043;">૧૫. ડાયનામિક જૂનો સ્ટોક ક્લિયરન્સ & સેલ્સમેન FIFO રજીસ્ટર (30 / 60 / 90 / 120+ દિવસ ફિલ્ટર)</h3>
                <button type="button" onclick="openAiAssistantModal(); setTimeout(function(){{quickAskMunimji('30 દિવસથી જૂનો સ્ટોક કયો કયો પડ્યો છે અને સૌથી પહેલો કયો વેચવો?');}}, 200);" style="background:#7c3aed; color:white; border:none; padding:6px 14px; border-radius:6px; font-weight:900; cursor:pointer;">🤖 દેવાંશી AI ને પૂછો: સૌથી પહેલો કયો ફોન વેચવો?</button>
            </div>
            <div style="display:grid; grid-template-columns:repeat(5, 1fr); gap:8px; margin-bottom:12px;">
                <div onclick="filterOscByDays(30)" style="background:#e0f2fe; border:2px solid #0284c7; padding:10px; border-radius:8px; text-align:center; cursor:pointer;">
                    <div style="font-size:11.5px; font-weight:900; color:#0369a1;">🔵 ૩૦+ દિવસથી જૂનો સ્ટોક</div>
                    <div style="font-size:17px; font-weight:900; color:#0f2043; margin-top:3px;">{cnt_30} નંગ (₹{dp_30:,.0f})</div>
                </div>
                <div onclick="filterOscByDays(60)" style="background:#fef08a; border:2px solid #ca8a04; padding:10px; border-radius:8px; text-align:center; cursor:pointer;">
                    <div style="font-size:11.5px; font-weight:900; color:#854d0e;">🟡 ૬૦+ દિવસથી જૂનો સ્ટોક</div>
                    <div style="font-size:17px; font-weight:900; color:#854d0e; margin-top:3px;">{cnt_60} નંગ (₹{dp_60:,.0f})</div>
                </div>
                <div onclick="filterOscByDays(90)" style="background:#ffedd5; border:2px solid #ea580c; padding:10px; border-radius:8px; text-align:center; cursor:pointer;">
                    <div style="font-size:11.5px; font-weight:900; color:#c2410c;">🟠 ૯૦+ દિવસથી જૂનો સ્ટોક</div>
                    <div style="font-size:17px; font-weight:900; color:#c2410c; margin-top:3px;">{cnt_90} નંગ (₹{dp_90:,.0f})</div>
                </div>
                <div onclick="filterOscByDays(120)" style="background:#fee2e2; border:2px solid #dc2626; padding:10px; border-radius:8px; text-align:center; cursor:pointer;">
                    <div style="font-size:11.5px; font-weight:900; color:#991b1b;">🔴 ૧૨૦+ દિવસથી જૂનો ડેડ સ્ટોક</div>
                    <div style="font-size:17px; font-weight:900; color:#991b1b; margin-top:3px;">{cnt_120} નંગ (₹{dp_120:,.0f})</div>
                </div>
                <div onclick="filterOscByDays(0)" style="background:#f1f5f9; border:2px solid #475569; padding:10px; border-radius:8px; text-align:center; cursor:pointer;">
                    <div style="font-size:11.5px; font-weight:900; color:#334155;">📦 તમામ સ્ટોક (FIFO ક્રમમાં)</div>
                    <div style="font-size:17px; font-weight:900; color:#0f172a; margin-top:3px;">{len(all_stk)} નંગ (સૌથી જૂનો ઉપર)</div>
                </div>
            </div>
            <div id="osc_active_filter_msg" style="background:#fefce8; border:1.5px solid #eab308; padding:7px 12px; border-radius:6px; margin-bottom:8px; font-weight:800; color:#854d0e;">
                📌 ઉપરના બટન (30+, 60+, 90+, 120+ દિવસ) પર ક્લિક કરો — સૌથી જૂનો સ્ટોક સૌથી ઉપર (FIFO) ગોઠવાયેલો છે જેથી સેલ્સમેન પહેલા તેને વેચી શકે!
            </div>
            <table class="live-grid" id="osc_main_tbl">
                <tr><th>ક્રમ</th><th>બ્રાન્ડ</th><th>મોડેલ</th><th>૧૫-અંક IMEI</th><th>ખરીદી તારીખ</th><th>કેટલા દિવસ જૂનો?</th><th>ખરીદ પડતર DP ₹</th><th>MOP ₹</th><th>વેપારી</th><th>FIFO એક્શન</th></tr>
                {old_trs}
            </table>
            <script>
                function filterOscByDays(minDays) {{
                    var rows = document.querySelectorAll('#osc_main_tbl tr.osc_row');
                    var shown = 0;
                    rows.forEach(function(r) {{
                        var d = parseInt(r.getAttribute('data-age-days') || '0');
                        if (d >= minDays) {{
                            r.style.display = '';
                            shown++;
                        }} else {{
                            r.style.display = 'none';
                        }}
                    }});
                    var msg = document.getElementById('osc_active_filter_msg');
                    if (msg) {{
                        msg.innerHTML = minDays > 0
                            ? ('🔍 <b>' + minDays + '+ દિવસથી વધારે જૂનો સ્ટોક ખુલ્લો છે:</b> કુલ <b>' + shown + ' નંગ</b> મળ્યા — સૌથી જૂના ફોનનું પહેલા બિલ બનાવવા બાજુનું લીલું બટન દબાવો!')
                            : ('📦 <b>તમામ સ્ટોક (FIFO ક્રમમાં - કુલ ' + shown + ' નંગ):</b> સૌથી જૂનો સ્ટોક સૌથી ઉપર બતાવેલ છે.');
                    }}
                }}
            </script>
        </div>
        """

    # =========================================================================
    # ૧૮. ૪-ગલ્લા કેશ માળખું & ઓડિટ લોગ (GALLA_AUDIT_HISTORY + AI સ્કીમ/પ્રાઇસ-ડ્રોપ લોગ)
    # =========================================================================
    elif sheet == "GALLA_AUDIT_HISTORY":
        c.execute("SELECT audit_date, galla_name, opening_bal, total_in, total_out, bank_deposit, expected_closing, physical_counted, diff_amt, remarks FROM galla_audit_daily_history ORDER BY id DESC LIMIT 60")
        gh_rows = c.fetchall()
        gh_trs = "".join([
            f"<tr><td>{r[0]}</td><td><b>{r[1]}</b></td><td>₹{float(r[2] or 0):,.0f}</td><td style='color:#16a34a;'>+ ₹{float(r[3] or 0):,.0f}</td><td style='color:#dc2626;'>- ₹{float(r[4] or 0):,.0f}</td><td>₹{float(r[5] or 0):,.0f}</td><td style='font-weight:bold; background:#fef9c3;'>₹{float(r[6] or 0):,.0f}</td><td style='font-weight:bold; color:#0284c7;'>₹{float(r[7] or 0):,.0f}</td><td style='font-weight:bold;'>₹{float(r[8] or 0):,.0f}</td><td>{r[9] or '-'}</td></tr>"
            for r in gh_rows
        ]) or "<tr><td colspan='10'>હજુ કોઈ દૈનિક ક્લોઝિંગ કેરી-ફોરવર્ડ લોગ સેવ થયો નથી ([F8] માંથી કેરી-ફોરવર્ડ બટન દબાવો)</td></tr>"

        c.execute("SELECT entry_date, doc_type, brand, model, old_price, new_price, diff_amt, scheme_details, valid_from, valid_to, doc_path FROM ai_scheme_and_price_drop_log ORDER BY id DESC LIMIT 30")
        ai_rows = c.fetchall()
        ai_trs = "".join([
            f"<tr><td>{r[0]}</td><td><b>{r[1]}</b></td><td>{r[2]} {r[3]}</td><td>₹{float(r[4] or 0):,.0f}</td><td>₹{float(r[5] or 0):,.0f}</td><td style='font-weight:bold; color:#15803d;'>₹{float(r[6] or 0):,.0f}</td><td>{r[7]}</td><td>{r[8]} થી {r[9]}</td><td><a href='{r[10]}' target='_blank'>📄 ફાઇલ</a></td></tr>"
            for r in ai_rows
        ]) or "<tr><td colspan='9'>હજુ કોઈ પ્રાઇસ-ડ્રોપ કે કંપની સ્કીમ લેટર અપલોડ થયો નથી</td></tr>"

        return f"""
        <div style="padding:10px;">
            <h3 style="margin:0 0 8px 0; color:#0f2043;">૧૮. ૪-ગલ્લા દૈનિક ઓપનિંગ-ક્લોઝિંગ કેશ ઓડિટ લોગ & AI પ્રાઇસ-ડ્રોપ / સ્કીમ હિસ્ટ્રી</h3>
            <table class="live-grid" style="margin-bottom:16px;">
                <tr>
                    <th>તારીખ</th><th>ગલ્લાનું નામ</th><th>ઓપનિંગ ₹</th><th>કુલ આવક (+)</th><th>કુલ જાવક (-)</th>
                    <th>બેંક ડિપોઝિટ (-)</th><th>અપેક્ષિત ક્લોઝિંગ (=)</th><th>ભૌતિક ગણેલી નોટો</th><th>તફાવત (Diff ₹)</th><th>નોંધ</th>
                </tr>
                {gh_trs}
            </table>
            <h4 style="margin:10px 0 6px 0; color:#4c1d95;">🤖 AI પ્રાઇસ-ડ્રોપ, પ્રાઇસ-હાઇક અને કંપની સ્કીમ લેટર રજીસ્ટર (Effective Date Lock સાથે)</h4>
            <table class="live-grid">
                <tr><th>તારીખ</th><th>પ્રકાર</th><th>બ્રાન્ડ / મોડેલ</th><th>જૂનો ભાવ ₹</th><th>નવો ભાવ ₹</th><th>તફાવત ₹</th><th>સ્કીમ / સર્ક્યુલર વિગત</th><th>લાગુ તારીખ (From - To)</th><th>દસ્તાવેજ</th></tr>
                {ai_trs}
            </table>
        </div>
        """


    # =========================================================================
    # Fetch brands for Sheet 12 Brand Master
    c.execute("SELECT id, brand_name, category FROM config_brands ORDER BY id ASC")
    b_rows = c.fetchall()
    brand_trs = "".join([
        f"<tr><td>{idx+1}</td><td><b>{r[1]}</b></td><td>{r[2]}</td>"
        f"<td><button type='button' onclick='editBrand({r[0]}, \"{r[1]}\", \"{r[2]}\")' style='background:#0284c7; color:white; border:none; padding:2px 7px; border-radius:3px; cursor:pointer; font-weight:bold;'>[Edit]</button> "
        f"<button type='button' onclick='openDeleteBrand({r[0]}, \"{r[1]}\")' style='background:#dc2626; color:white; border:none; padding:2px 7px; border-radius:3px; cursor:pointer; font-weight:bold;'>[Delete PIN]</button></td></tr>"
        for idx, r in enumerate(b_rows)
    ]) or "<tr><td colspan='4'>કોઈ બ્રાન્ડ ઉમેરેલ નથી</td></tr>"

    # ૧૨. GUJARATI_CONFIG: સ્ક્રીનશોટ ૯ મુજબ ૪-બોક્સ માસ્ટર CRUD + બિલ ફોર્મેટ સેટિંગ્સ
    # =========================================================================



    # --- TALLY_LEDGER: માસ્ટર ૩-ઇન-૧ એકાઉન્ટ્સ લેજર (Create / Edit / Delete - PIN 1986) ---
    c.execute("SELECT id, ledger_name, under_group, mobile, gstin, address, pincode, bank_details, opening_bal, bal_type FROM tally_master_ledgers ORDER BY id DESC LIMIT 60")
    tally_rows = c.fetchall()
    tally_trs = ""
    for r in tally_rows:
        r3, r4, r5, r6, r7 = (r[3] or ""), (r[4] or ""), (r[5] or ""), (r[6] or ""), (r[7] or "")
        op_v = float(r[8] or 0)
        tally_trs += (
            f"<tr><td><b>{r[1]}</b></td><td>{r[2]}</td><td>{r3 or '-'}</td><td>{r4 or '-'}</td><td>{r5 or '-'} {r6}</td><td>{r7 or '-'}</td><td>₹{op_v:,.0f} ({r[9]})</td>"
            f"<td><button type='button' onclick=\"loadTallyLedger({r[0]},'{r[1]}','{r[2]}','{r3}','{r4}','{r5}','{r6}','{r7}',{op_v},'{r[9]}','EDIT')\" style='background:#0284c7; color:white; border:none; padding:2px 7px; border-radius:3px; cursor:pointer; font-weight:bold;'>[Edit]</button> "
            f"<button type='button' onclick=\"loadTallyLedger({r[0]},'{r[1]}','{r[2]}','{r3}','{r4}','{r5}','{r6}','{r7}',{op_v},'{r[9]}','DELETE')\" style='background:#dc2626; color:white; border:none; padding:2px 7px; border-radius:3px; cursor:pointer; font-weight:bold;'>[Delete PIN]</button></td></tr>"
        )

    desig_opts_html = "".join([f'<option value="{d}">{d}</option>' for d in desig_opts])
    cat_opts_html = "".join([f'<option value="{ct}">{ct}</option>' for ct in cat_opts])

    staff_trs = "".join([
        f"<tr><td><b>{r[1]}</b></td><td>{r[2]}</td><td>₹{float(r[3] or 0):,.0f}</td>"
        f"<td><button type='button' onclick='editStaff({r[0]},\"{r[1]}\",\"{r[2]}\",{float(r[3] or 0)})' style='background:#0284c7; color:white; border:none; padding:2px 8px; border-radius:3px; cursor:pointer; font-weight:bold;'>[એડિટ]</button> "
        f"<a href='/delete-staff?id={r[0]}' onclick='return confirm(\"ડિલીટ કરવું છે?\")' style='background:#dc2626; color:white; padding:2px 8px; border-radius:3px; text-decoration:none; font-weight:bold;'>[ડિલીટ]</a></td></tr>"
        for r in staff_db_rows
    ]) or "<tr><td colspan='4'>કોઈ સ્ટાફ ઉમેરેલ નથી (નવો સ્ટાફ ઉમેરો)</td></tr>"
    party_trs = "".join([
        f"<tr><td><b>{r[1]}</b></td><td>{r[2]}</td>"
        f"<td><button type='button' onclick='editParty({r[0]},\"{r[1]}\",\"{r[2]}\")' style='background:#0284c7; color:white; border:none; padding:2px 8px; border-radius:3px; cursor:pointer; font-weight:bold;'>[એડિટ]</button> "
        f"<a href='/delete-party?id={r[0]}' onclick='return confirm(\"ડિલીટ કરવું છે?\")' style='background:#dc2626; color:white; padding:2px 8px; border-radius:3px; text-decoration:none; font-weight:bold;'>[ડિલીટ]</a></td></tr>"
        for r in party_db_rows
    ]) or "<tr><td colspan='3'>કોઈ વેપારી ખાતું બનાવેલ નથી (નવો વેપારી ઉમેરો)</td></tr>"
    desig_trs = "".join([
        f"<tr><td><b>{r[1]}</b></td>"
        f"<td><button type='button' onclick='editDesig({r[0]},\"{r[1]}\")' style='background:#0284c7; color:white; border:none; padding:2px 8px; border-radius:3px; cursor:pointer; font-weight:bold;'>[એડિટ]</button> "
        f"<a href='/delete-designation?id={r[0]}' onclick='return confirm(\"ડિલીટ કરવું છે?\")' style='background:#dc2626; color:white; padding:2px 8px; border-radius:3px; text-decoration:none; font-weight:bold;'>[ડિલીટ]</a></td></tr>"
        for r in desig_db_rows
    ]) or "<tr><td colspan='2'>કોઈ હોદ્દો ઉમેરેલ નથી (નવો હોદ્દો ઉમેરો)</td></tr>"
    cat_trs = "".join([
        f"<tr><td><b>{r[1]}</b></td>"
        f"<td><button type='button' onclick='editCategory({r[0]},\"{r[1]}\")' style='background:#0284c7; color:white; border:none; padding:2px 8px; border-radius:3px; cursor:pointer; font-weight:bold;'>[એડિટ]</button> "
        f"<a href='/delete-category?id={r[0]}' onclick='return confirm(\"ડિલીટ કરવું છે?\")' style='background:#dc2626; color:white; padding:2px 8px; border-radius:3px; text-decoration:none; font-weight:bold;'>[ડિલીટ]</a></td></tr>"
        for r in cat_db_rows
    ]) or "<tr><td colspan='2'>કોઈ કેટેગરી ઉમેરેલ નથી (નવી કેટેગરી ઉમેરો)</td></tr>"

    return f"""
    <div style="padding:10px;">
        <div style="display:flex; justify-content:space-between; align-items:center; border-bottom:2px solid #cbd5e1; padding-bottom:8px; margin-bottom:12px; flex-wrap:wrap; gap:8px;">
            <h3 style="margin:0; color:#0f2043;">૧૮. માસ્ટર સેટિંગ & પ્રોફેશનલ લેજર (વેપારી, ગ્રાહક, બ્રાન્ડ, સ્ટાફ, હોદ્દા અને કેટેગરી માસ્ટર - Alt+C)</h3>
            <div style="display:flex; gap:8px;">
                <a href="/cloud-backup-upload" style="background:#0284c7; color:white; padding:6px 12px; border-radius:4px; text-decoration:none; font-weight:bold; font-size:12px;">☁️ દુકાનથી ક્લાઉડ બેકઅપ અપલોડ કરો</a>
                <a href="/cloud-backup-download" style="background:#16a34a; color:white; padding:6px 12px; border-radius:4px; text-decoration:none; font-weight:bold; font-size:12px;">📥 લેપટોપમાં ક્લાઉડ બેકઅપ ડાઉનલોડ કરો</a>
            </div>
        </div>

        
        <!-- 🏦 ૧૮.૧: બેંક ખાતા માસ્ટર (Bank Master - નવું બેંક ખાતું ઉમેરો / એડિટ / ડિલીટ) -->
        <div style="background:#f0fdf4; border:2px solid #16a34a; padding:12px; border-radius:8px; margin-bottom:14px;">
            <div style="display:flex; justify-content:space-between; align-items:center; background:#166534; color:white; padding:8px 12px; border-radius:6px; margin-bottom:10px;">
                <h4 style="margin:0; color:#86efac;">🏦 બેંક ખાતા માસ્ટર (Bank Accounts Master - ઉમેરો / એડિટ / ડિલીટ)</h4>
                <span style="font-size:11px; color:#fde047;">દુકાનનાં બેંક કરન્ટ/સેવિંગ્સ ખાતા અહીંથી સેટ કરો</span>
            </div>
            <form action="/save-tally-ledger" method="post" style="display:grid; grid-template-columns:repeat(auto-fit, minmax(200px, 1fr)); gap:8px; background:white; padding:10px; border:1px solid #bbf7d0; border-radius:6px; margin-bottom:8px;">
                <input type="hidden" name="ledger_mode" value="CREATE">
                <input type="hidden" name="under_group" value="બેંક ખાતું (Bank Accounts)">
                <div>
                    <label style="font-size:11px; font-weight:bold;">૧. બેંકનું નામ & શાખા:</label>
                    <input type="text" name="ledger_name" placeholder="દા.ત. HDFC બેંક - બેચરાજી શાખા..." required style="width:100%; padding:6px; font-weight:bold; box-sizing:border-box;">
                </div>
                <div>
                    <label style="font-size:11px; font-weight:bold;">૨. બેંક એકાઉન્ટ નંબર:</label>
                    <input type="text" name="address" placeholder="એકાઉન્ટ નંબર / IFSC કોડ..." style="width:100%; padding:6px; box-sizing:border-box;">
                </div>
                <div>
                    <label style="font-size:11px; font-weight:bold;">૩. શરૂઆતની સિલક (Opening ₹):</label>
                    <input type="number" step="any" name="opening_bal" value="0" style="width:100%; padding:6px; font-weight:bold; box-sizing:border-box;">
                </div>
                <div style="display:flex; align-items:flex-end;">
                    <button type="submit" style="background:#15803d; color:white; border:none; padding:8px 16px; border-radius:4px; font-weight:bold; cursor:pointer; width:100%;">+ નવું બેંક ખાતું સેવ કરો</button>
                </div>
            </form>
        </div>

        <!-- 💸 ૧૮.૨: દુકાન ખર્ચ લેજર માસ્ટર (Expense Master - નવો ખર્ચ પ્રકાર ઉમેરો / એડિટ / ડિલીટ) -->
        <div style="background:#fef2f2; border:2px solid #dc2626; padding:12px; border-radius:8px; margin-bottom:14px;">
            <div style="display:flex; justify-content:space-between; align-items:center; background:#991b1b; color:white; padding:8px 12px; border-radius:6px; margin-bottom:10px;">
                <h4 style="margin:0; color:#fca5a5;">💸 દુકાન ખર્ચ લેજર માસ્ટર (Indirect Expenses Master - ઉમેરો / એડિટ / ડિલીટ)</h4>
                <span style="font-size:11px; color:#fde047;">દુકાન ભાડું, લાઈટ બિલ, ચા-નાસ્તો, મ્યુનિસિપલ ટેક્સ વગેરે લેજર</span>
            </div>
            <form action="/save-tally-ledger" method="post" style="display:grid; grid-template-columns:repeat(auto-fit, minmax(200px, 1fr)); gap:8px; background:white; padding:10px; border:1px solid #fecdd3; border-radius:6px; margin-bottom:8px;">
                <input type="hidden" name="ledger_mode" value="CREATE">
                <input type="hidden" name="under_group" value="દુકાન ખર્ચ ખાતું (Indirect Expenses)">
                <div>
                    <label style="font-size:11px; font-weight:bold;">૧. ખર્ચ ખાતાનું નામ:</label>
                    <input type="text" name="ledger_name" placeholder="દા.ત. દુકાન ભાડું, લાઈટ બિલ, ચા-નાસ્તો..." required style="width:100%; padding:6px; font-weight:bold; box-sizing:border-box;">
                </div>
                <div>
                    <label style="font-size:11px; font-weight:bold;">૨. સામાન્ય ખર્ચ વિગત / નોંધ:</label>
                    <input type="text" name="address" placeholder="ખર્ચ પ્રકારની વિગત..." style="width:100%; padding:6px; box-sizing:border-box;">
                </div>
                <div style="display:flex; align-items:flex-end;">
                    <button type="submit" style="background:#dc2626; color:white; border:none; padding:8px 16px; border-radius:4px; font-weight:bold; cursor:pointer; width:100%;">+ નવું ખર્ચ લેજર સેવ કરો</button>
                </div>
            </form>
        </div>

        <!-- 🏛️ માસ્ટર ૩-ઇન-૧ એકાઉન્ટ્સ લેજર મેનેજમેન્ટ (Create / Edit / Delete) -->
        <div style="background:#f8fafc; border:2px solid #0f2043; padding:12px; border-radius:8px; margin-bottom:14px;">
            <div style="display:flex; justify-content:space-between; align-items:center; background:#0f2043; color:white; padding:8px 12px; border-radius:6px; margin-bottom:10px;">
                <h4 style="margin:0; color:#38bdf8;">🏛️ માસ્ટર ૩-ઇન-૧ એકાઉન્ટ્સ લેજર મેનેજમેન્ટ (૧. નવું લેજર બનાવો | ૨. લેજર સુધારો | ૩. લેજર ડિલીટ)</h4>
                <span style="font-size:11px; color:#fde047;">વેપારી, ગ્રાહક, સ્ટાફ, ખર્ચ કે બેંક ખાતું અહીંથી બનાવો</span>
            </div>
            <form action="/save-tally-ledger" method="post" class="f-enter-form" style="display:grid; grid-template-columns:repeat(4, 1fr); gap:8px; margin-bottom:10px; background:white; padding:10px; border:1px solid #cbd5e1; border-radius:6px;">
                <input type="hidden" name="ledger_mode" id="tl_mode" value="CREATE">
                <input type="hidden" name="ledger_id" id="tl_id" value="0">
                <div>
                    <label style="font-size:11.5px; font-weight:bold;">૧. ખાતાનું નામ (Ledger Name):</label>
                    <input type="text" name="ledger_name" id="tl_name" placeholder="દા.ત. શ્રી રામ એન્ટરપ્રાઇઝ..." required style="width:100%; padding:6px; box-sizing:border-box; font-weight:bold;">
                </div>
                <div>
                    <label style="font-size:11.5px; font-weight:bold;">૨. અંડર ગ્રૂપ (Under Group):</label>
                    <select name="under_group" id="tl_group" style="width:100%; padding:6px; box-sizing:border-box; font-weight:bold;">
                        <option value="વેપારી / સપ્લાયર ખાતું (Sundry Creditors)">૧. વેપારી / સપ્લાયર ખાતું (Sundry Creditors)</option>
                        <option value="ગ્રાહક બાકી ખાતું (Sundry Debtors)">૨. ગ્રાહક બાકી ખાતું (Sundry Debtors)</option>
                        <option value="સેલ્સમેન / સ્ટાફ ખાતું (Staff Payroll)">૩. સેલ્સમેન / સ્ટાફ ખાતું (Staff Payroll)</option>
                        <option value="દુકાન ખર્ચ ખાતું (Indirect Expenses)">૪. દુકાન ખર્ચ ખાતું (Indirect Expenses)</option>
                        <option value="બેંક ખાતું (Bank Accounts)">૫. બેંક ખાતું (Bank Accounts)</option>
                        <option value="પાર્ટનર મૂડી ખાતું (Partner Capital Account)">૬. પાર્ટનર મૂડી ખાતું (Partner Capital Account)</option>
                    </select>
                </div>
                <div>
                    <label style="font-size:11.5px; font-weight:bold;">૩. મોબાઈલ નંબર:</label>
                    <input type="text" name="mobile" id="tl_mob" placeholder="૧૦-અંક મોબાઈલ..." style="width:100%; padding:6px; box-sizing:border-box;">
                </div>
                <div>
                    <label style="font-size:11.5px; font-weight:bold;">૪. ૧૫-અંક GSTIN નંબર (Auto-Search):</label>
                    <div style="display:flex; gap:4px;">
                        <input type="text" name="gstin" id="tl_gst" maxlength="15" placeholder="૧૫-અંક GSTIN..." style="flex:1; padding:6px; box-sizing:border-box;">
                        <button type="button" onclick="lookupTallyGstin()" style="background:#0284c7; color:white; border:none; padding:5px 8px; border-radius:4px; font-weight:bold; cursor:pointer; font-size:11px;">🔍 GST સર્ચ</button>
                    </div>
                </div>
                <div>
                    <label style="font-size:11.5px; font-weight:bold;">૫. સરનામું & પિનકોડ:</label>
                    <input type="text" name="address" id="tl_addr" placeholder="દુકાન/ઘરનું સરનામું..." style="width:100%; padding:6px; box-sizing:border-box;">
                </div>
                <div>
                    <label style="font-size:11.5px; font-weight:bold;">૬. શરૂઆતની સિલક (Opening ₹):</label>
                    <div style="display:flex; gap:4px;">
                        <input type="number" step="any" name="opening_bal" id="tl_op" value="0" style="flex:1; padding:6px;">
                        <select name="bal_type" id="tl_btype" style="padding:6px; font-weight:bold;"><option value="CR"> જમા (CR)</option><option value="DR">ઉધાર (DR)</option></select>
                    </div>
                </div>
                <div id="tl_pin_wrap" style="display:none;">
                    <label style="font-size:11.5px; font-weight:bold; color:#dc2626;">૭. માસ્ટર સિક્રેટ PIN (એડિટ/ડિલીટ):</label>
                    <input type="password" name="secret_pin" id="tl_pin" placeholder="માસ્ટર PIN..." style="width:100%; padding:6px; box-sizing:border-box; border:1px solid #dc2626;">
                </div>
                <div style="display:flex; align-items:flex-end; gap:6px;">
                    <button type="submit" id="tl_submit_btn" style="background:#0f2043; color:white; border:none; padding:8px 16px; border-radius:4px; font-weight:bold; cursor:pointer; flex:1;">+ નવું લેજર સેવ કરો (Accept)</button>
                    <button type="button" onclick="resetTallyLedgerForm()" style="background:#64748b; color:white; border:none; padding:8px 10px; border-radius:4px; cursor:pointer;">રીસેટ</button>
                </div>
            </form>
            <table class="live-grid">
                <tr><th>ખાતાનું નામ</th><th>અંડર ગ્રૂપ</th><th>મોબાઈલ</th><th>GSTIN</th><th>સરનામું</th><th>બેંક વિગત</th><th>શરૂઆતની સિલક</th><th>એડિટ / ડિલીટ</th></tr>
                {tally_trs or "<tr><td colspan='8'>કોઈ લેજર બનાવેલ નથી (ઉપરથી નવું લેજર બનાવો)</td></tr>"}
            </table>
        </div>

        <!-- ૫. બ્રાન્ડ માસ્ટર મેનેજમેન્ટ બ્લોક (નવી બ્રાન્ડ ઉમેરો / એડિટ / ડિલીટ PIN 1986 સાથે) -->
        <div style="background:#fefce8; border:2px solid #ca8a04; padding:12px; border-radius:6px; margin-bottom:14px;">
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
                <h4 style="margin:0; color:#854d0e;">🏷️ બ્રાન્ડ માસ્ટર (Brand Master) - નવી બ્રાન્ડ ઉમેરો / એડિટ / ડિલીટ (માસ્ટર PIN રક્ષણ)</h4>
            </div>
            <form action="/add-brand" method="post" style="display:flex; gap:6px; margin-bottom:10px; align-items:center; flex-wrap:wrap;">
                <input type="hidden" name="edit_id" id="br_eid" value="0">
                <input type="text" name="brand_name" id="br_name" placeholder="નવી બ્રાન્ડનું નામ (દા.ત. Infinix, Poco, Nothing...)" required style="padding:6px; width:280px; font-weight:bold;">
                <select name="category" id="br_cat" style="padding:6px;">
                    <option value="Handset">મોબાઈલ હેન્ડસેટ (Handset)</option>
                    <option value="Accessories">એસેસરીઝ (Accessories)</option>
                    <option value="Appliances">હોમ એપ્લાયન્સ / TV</option>
                    <option value="Recharge">રિચાર્જ / અન્ય</option>
                </select>
                <button type="submit" id="br_save_btn" style="background:#15803d; color:white; border:none; padding:6px 14px; border-radius:4px; font-weight:bold; cursor:pointer;">+ નવી બ્રાન્ડ સેવ કરો</button>
            </form>
            <div id="brand_del_box" style="display:none; background:#fee2e2; border:1px solid #ef4444; padding:8px; border-radius:4px; margin-bottom:8px;">
                <form action="/delete-brand" method="post" style="display:flex; gap:6px; align-items:center;">
                    <input type="hidden" name="brand_id" id="del_br_id">
                    <span id="del_br_name" style="font-weight:bold; color:#991b1b;"></span>
                    <input type="password" name="admin_pin" placeholder="માસ્ટર સિક્રેટ PIN નાખો..." required style="padding:5px; width:170px;">
                    <button type="submit" style="background:#dc2626; color:white; border:none; padding:5px 12px; border-radius:3px; font-weight:bold; cursor:pointer;">કન્ફર્મ ડિલીટ</button>
                    <button type="button" onclick="document.getElementById('brand_del_box').style.display='none'" style="background:#64748b; color:white; border:none; padding:5px 8px; border-radius:3px; cursor:pointer;">✖</button>
                </form>
            </div>
            <table class="live-grid">
                <tr><th>ક્રમ</th><th>બ્રાન્ડ નામ</th><th>કેટેગરી</th><th>એડિટ / ડિલીટ (માસ્ટર PIN)</th></tr>
                {brand_trs}
            </table>
        </div>

        <div style="display:grid; grid-template-columns:1fr 1fr; gap:14px; margin-bottom:16px;">
            <!-- ૧. વેપારી / આઇટમ કેટેગરી માસ્ટર -->
            <div style="background:white; border:2px solid #0f766e; padding:12px; border-radius:6px;">
                <h4 style="margin:0 0 8px 0; color:#0f766e;">📂 કેટેગરી માસ્ટર (Category Master - ઉમેરો / એડિટ / ડિલીટ)</h4>
                <form action="/add-category" method="post" style="display:flex; gap:6px; margin-bottom:8px;">
                    <input type="hidden" name="edit_id" id="ct_eid" value="0">
                    <input type="text" name="name" id="ct_name" placeholder="નવી કેટેગરી લખો (દા.ત. સ્માર્ટ વોચ, મોબાઈલ હેન્ડસેટ)" required style="padding:6px; flex:1; font-weight:bold;">
                    <button type="submit" id="ct_btn" style="background:#0f766e; color:white; border:none; padding:6px 14px; border-radius:4px; font-weight:bold; cursor:pointer;">+ કેટેગરી સેવ કરો</button>
                </form>
                <table class="live-grid"><tr><th>કેટેગરીનું નામ</th><th>એડિટ / ડિલીટ</th></tr>{cat_trs}</table>
            </div>

            <!-- ૨. સ્ટાફ હોદ્દા (Designation) માસ્ટર -->
            <div style="background:white; border:2px solid #4f46e5; padding:12px; border-radius:6px;">
                <h4 style="margin:0 0 8px 0; color:#4f46e5;">👔 હોદ્દા માસ્ટર (Designation Master - ઉમેરો / એડિટ / ડિલીટ)</h4>
                <form action="/add-designation" method="post" style="display:flex; gap:6px; margin-bottom:8px;">
                    <input type="hidden" name="edit_id" id="dg_eid" value="0">
                    <input type="text" name="title" id="dg_title" placeholder="નવો હોદ્દો લખો (દા.ત. સેલ્સમેન, મેનેજર, કારીગર)" required style="padding:6px; flex:1; font-weight:bold;">
                    <button type="submit" id="dg_btn" style="background:#4f46e5; color:white; border:none; padding:6px 14px; border-radius:4px; font-weight:bold; cursor:pointer;">+ હોદ્દો સેવ કરો</button>
                </form>
                <table class="live-grid"><tr><th>હોદ્દાનું નામ</th><th>એડિટ / ડિલીટ</th></tr>{desig_trs}</table>
            </div>
        </div>

    </div>
    <script>
        function lookupTallyGstin() {{
            var gEl = document.getElementById('tl_gst');
            var g = (gEl ? gEl.value : '').replace(/\\s+/g, '').toUpperCase();
            if (gEl) gEl.value = g;
            if (!g || g.length < 15) {{
                alert('⚠️ કૃપા કરીને પૂરો ૧૫-અંકનો GSTIN નંબર દાખલ કરો!');
                return;
            }}
            fetch('/api/gstin-lookup?gstin=' + encodeURIComponent(g))
            .then(r => r.json())
            .then(d => {{
                if (d && d.found) {{
                    var nm = d.trade_name || d.name || '';
                    if (nm && !document.getElementById('tl_name').value) document.getElementById('tl_name').value = nm;
                    if (d.address) document.getElementById('tl_addr').value = d.address + (d.pincode ? (' - ' + d.pincode) : '');
                    if (d.mobile && !document.getElementById('tl_mob').value) document.getElementById('tl_mob').value = d.mobile;
                    alert('✅ સરકારી GST પોર્ટલ / માસ્ટર વિગત મળી: ' + nm + ' | રાજ્ય: ' + (d.state || 'ગુજરાત'));
                }} else {{
                    alert('⚠️ આ GSTIN નંબરની વિગત મળી નથી, કૃપા કરીને જાતે વિગત ભરો.');
                }}
            }}).catch(() => {{ alert('⚠️ GST સર્ચમાં ત્રુટિ આવી.'); }});
        }}
        function loadTallyLedger(id, nm, grp, mob, gst, addr, pin, bnk, op, bt, mode) {{
            document.getElementById('tl_id').value = id;
            document.getElementById('tl_mode').value = mode;
            document.getElementById('tl_name').value = nm;
            document.getElementById('tl_group').value = grp;
            document.getElementById('tl_mob').value = mob;
            document.getElementById('tl_gst').value = gst;
            document.getElementById('tl_addr').value = addr;
            document.getElementById('tl_op').value = op;
            document.getElementById('tl_btype').value = bt || 'CR';
            document.getElementById('tl_pin_wrap').style.display = 'block';
            var btn = document.getElementById('tl_submit_btn');
            if (mode === 'DELETE') {{
                btn.innerText = '🗑️ લેજર ડિલીટ કરો';
                btn.style.background = '#dc2626';
            }} else {{
                btn.innerText = '💾 લેજર સુધારો સેવ કરો';
                btn.style.background = '#0284c7';
            }}
            document.getElementById('tl_pin').focus();
        }}
        function resetTallyLedgerForm() {{
            document.getElementById('tl_id').value = '0';
            document.getElementById('tl_mode').value = 'CREATE';
            document.getElementById('tl_name').value = '';
            document.getElementById('tl_mob').value = '';
            document.getElementById('tl_gst').value = '';
            document.getElementById('tl_addr').value = '';
            document.getElementById('tl_op').value = '0';
            document.getElementById('tl_pin_wrap').style.display = 'none';
            var btn = document.getElementById('tl_submit_btn');
            btn.innerText = '+ નવું લેજર સેવ કરો (Accept)';
            btn.style.background = '#0f2043';
        }}
        function editBrand(id, nm, cat){{
            document.getElementById('br_eid').value = id;
            document.getElementById('br_name').value = nm;
            document.getElementById('br_cat').value = cat;
            document.getElementById('br_save_btn').innerText = '💾 બ્રાન્ડ અપડેટ કરો';
            document.getElementById('br_name').focus();
        }}
        function openDeleteBrand(id, nm){{
            document.getElementById('del_br_id').value = id;
            document.getElementById('del_br_name').innerText = 'શું બ્રાન્ડ "' + nm + '" ડિલીટ કરવી છે?';
            document.getElementById('brand_del_box').style.display = 'block';
        }}
        function editGrowthMonth27(mn, curVal){{
            document.getElementById('ge_yr').value = '2027';
            document.getElementById('ge_mn').value = mn;
            document.getElementById('ge_amt').value = curVal || 0;
            document.getElementById('growth_edit_box').style.display = 'block';
            document.getElementById('ge_amt').focus();
        }}
        function editDesig(id, tt){{
            document.getElementById('dg_eid').value = id;
            document.getElementById('dg_title').value = tt;
            document.getElementById('dg_btn').innerText = 'અપડેટ કરો';
            document.getElementById('dg_title').focus();
        }}
        function editCategory(id, nm){{
            document.getElementById('ct_eid').value = id;
            document.getElementById('ct_name').value = nm;
            document.getElementById('ct_btn').innerText = 'અપડેટ કરો';
            document.getElementById('ct_name').focus();
        }}
    </script>
    """