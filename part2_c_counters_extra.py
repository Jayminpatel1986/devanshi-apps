# -*- coding: utf-8 -*-
# =======================================================================================================================
# ⚠️ આવશ્યક એઆઈ ડાયરેક્ટિવ અને ડાયનામિક રૂલબુક ગવર્નન્સ (કાયમી અમર એઆઈ હેડર - માસ્ટર ૧૦ લોજિક અને મલ્ટી-સ્ટોર SaaS આવૃત્તિ)
# =======================================================================================================================
# [કડક ચેતવણી - Gemini, ChatGPT, Claude, Cursor અથવા અન્ય કોઈપણ AI મોડેલ અને ડેવલપર માટે બંધનકર્તા આદેશ]:
# ૧. આ હેડર 'અમર' (Immortal) છે. આ ફાઇલ part2_c_counters_extra.py છે (F5, F6, F7 અને F8 કાઉન્ટર્સ - શીટ ૪ મુજબ).
# ૨. જૂના કોડનું એક પણ ફંક્શન, ડ્રોપડાઉન, ગાણિતિક સૂત્ર કે CRUD બટન કાઢવું સખત પ્રતિબંધિત છે.
# =======================================================================================================================

from part1_core import get_galla_balance, get_cumulative_unbanked_cash
import sqlite3
import time
import datetime

def build_4galla_sel_c(name_attr, default_galla="BANK_CASH"):
    gallas = [
        ("BANK_CASH", "૧. બેંક કેશ (ગલ્લો ૧ - મુખ્ય કાઉન્ટર ગલ્લો)"),
        ("ACC_DCASH", "૨. એક્સેસરીઝ કેશ (ગલ્લો ૨)"),
        ("RECHARGE", "૩. રિચાર્જ કેશ (ગલ્લો ૩)"),
        ("EXTRA_CASH", "૪. એક્સ્ટ્રા કેશ (ગલ્લો ૪)")
    ]
    opts = "".join([
        f'<option value="{gk}" {"selected" if gk == default_galla else ""}>{gl}</option>'
        for gk, gl in gallas
    ])
    return f'<select name="{name_attr}" style="font-weight:bold; color:#15803d; background:#f0fdf4;">{opts}</select>'

def render_f5_to_f8(conn, c, mode, staff_opts_html, all_galla_options, bank_opts, exp_heads, today_str, shop_prof=None):
    c.execute("SELECT brand_name FROM config_brands ORDER BY id ASC")
    b_rows = [r[0] for r in c.fetchall()]
    brand_list = b_rows if b_rows else ["Vivo", "Oppo", "Samsung", "Realme", "OnePlus", "Redmi", "Xiaomi", "Apple", "Motorola", "Nothing", "Poco", "iQOO", "Tecno", "Infinix", "Nokia"]
    brand_opts_html = "".join([f'<option value="{b}">{b}</option>' for b in brand_list])
    st_mode = (shop_prof or {}).get("store_mode", "FRANCHISE_HO")
    active_subparts = (shop_prof or {}).get("active_subparts") or ["F5_1","F5_2","F5_3","F5_4","F6_1","F7_1","F7_2","F7_3","F8_1","F8_2","F8_3"]

    # =========================================================================
    # [F5] બાય-બેક (જૂના ફોન), રિપેરિંગ પડતર, વેચાણ (Resale), પોલીસ વૉલ્ટ (ભાગ ૧ થી ૩) & ભાગ ૪ (રિટર્ન & રિફંડ)
    # =========================================================================
    if mode == "F5":
        # In-Stock Buyback Phones (માત્ર Saleable In / IN_STOCK ફોન)
        c.execute("""SELECT id, date, customer_name, model, imei, purchase_cost, repair_cost, total_cost, salesman, photo_path
                     FROM buyback_stock WHERE status='IN_STOCK' ORDER BY id DESC""")
        in_stock_bb = c.fetchall()
        bb_instock_opts = '<option value="" data-cost="0" data-model="">-- [તારીખ] | [મોડેલ (IMEI)] | [સેલ્સમેન] | [કુલ પડતર ₹] --</option>'
        for b in in_stock_bb:
            t_cost = float(b[7] or b[5] or 0)
            bb_instock_opts += f'<option value="{b[4]}" data-cost="{t_cost}" data-model="{b[3]}">[{b[1]}] | [{b[3]} ({b[4]})] | [{b[8] or "-"}] | [કુલ પડતર: ₹{t_cost:,.0f}]</option>'

        # Sold Phones (ભાગ ૪ રિટર્ન અને રિફંડ માટે - બાયબેકમાં વેચાયેલા તેમજ F2 કાઉન્ટર પરથી વેચાયેલા તમામ SOLD ફોન બતાવો!)
        c.execute("""SELECT id, date, customer_name, model, imei, total_cost, sale_price, salesman
                     FROM buyback_stock WHERE status='SOLD' ORDER BY id DESC LIMIT 100""")
        sold_bb = c.fetchall()
        c.execute("""SELECT id, bill_date, customer_name, model, imei, mop_price, salesman, bill_no
                     FROM apx_sales_raw WHERE imei IS NOT NULL AND imei != '' AND imei != '-' ORDER BY id DESC LIMIT 100""")
        sold_apx = c.fetchall()
        c.execute("""SELECT id, entry_date, party_name, model, imei, sale_rate, brand
                     FROM live_stock WHERE status='SOLD' AND imei IS NOT NULL AND imei != '' ORDER BY id DESC LIMIT 100""")
        sold_ls = c.fetchall()

        bb_sold_opts = '<option value="" data-cust="" data-date="" data-model="" data-price="0">-- વેચાયેલા તમામ ફોન (SOLD Buyback & Handsets) માંથી સિલેક્ટ કરો --</option>'
        seen_sold_imeis = set()
        for sb in sold_bb:
            im_v = str(sb[4] or "").strip()
            if not im_v or im_v in seen_sold_imeis:
                continue
            seen_sold_imeis.add(im_v)
            s_price = float(sb[6] or sb[5] or 0)
            bb_sold_opts += f'<option value="{im_v}" data-cust="{sb[2] or ""}" data-date="{sb[1] or ""}" data-model="{sb[3] or ""}" data-price="{s_price}">[બાયબેક SOLD: {sb[1]}] | {sb[3]} ({im_v}) | ગ્રાહક: {sb[2] or "-"} | વેચાણ ₹{s_price:,.0f}</option>'
        for sa in sold_apx:
            im_v = str(sa[4] or "").strip()
            if not im_v or im_v in seen_sold_imeis:
                continue
            seen_sold_imeis.add(im_v)
            s_price = float(sa[5] or 0)
            bb_sold_opts += f'<option value="{im_v}" data-cust="{sa[2] or ""}" data-date="{sa[1] or ""}" data-model="{sa[3] or ""}" data-price="{s_price}">[બિલ SOLD ({sa[7]}): {sa[1]}] | {sa[3]} ({im_v}) | ગ્રાહક: {sa[2] or "-"} | વેચાણ ₹{s_price:,.0f}</option>'
        for sl in sold_ls:
            im_v = str(sl[4] or "").strip()
            if not im_v or im_v in seen_sold_imeis:
                continue
            seen_sold_imeis.add(im_v)
            s_price = float(sl[5] or 0)
            mod_full = f"{sl[6] or ''} {sl[3] or ''}".strip()
            bb_sold_opts += f'<option value="{im_v}" data-cust="{sl[2] or "ગ્રાહક"}" data-date="{sl[1] or ""}" data-model="{mod_full}" data-price="{s_price}">[સ્ટોક SOLD: {sl[1]}] | {mod_full} ({im_v}) | ₹{s_price:,.0f}</option>'

        # તાજેતરના બાય-બેક સ્ટોક અને રિટર્ન રજીસ્ટર (એડિટ અને રદ/રોકડ રિવર્સ બટન સાથે)
        c.execute("""SELECT date, model, imei, customer_name, purchase_cost, repair_cost, total_cost, sale_price, status, salesman, photo_path, id, COALESCE(customer_photo_path,'')
                     FROM buyback_stock ORDER BY id DESC LIMIT 25""")
        bb_all_rows = c.fetchall()
        bb_trs = ""
        for r in bb_all_rows:
            p_cost = float(r[4] or 0)
            r_cost = float(r[5] or 0)
            t_cost = float(r[6] or p_cost)
            s_prc = float(r[7] or 0)
            net_p = (s_prc - t_cost) if (r[8] == "SOLD" and s_prc > 0) else 0.0
            st_badge = "<span style='background:#dcfce7; color:#15803d; padding:2px 6px; border-radius:3px; font-weight:bold;'>IN_STOCK (હાજર)</span>" if r[8] == "IN_STOCK" else f"<span style='background:#fee2e2; color:#991b1b; padding:2px 6px; border-radius:3px; font-weight:bold;'>SOLD (નફો: ₹{net_p:,.0f})</span>"
            doc_btn = f"<a href='{r[10]}' target='_blank' style='background:#0284c7; color:white; padding:2px 5px; border-radius:3px; text-decoration:none; font-size:10.5px;'>📄 પ્રૂફ</a>" if r[10] else ""
            cust_ph_btn = f" <a href='{r[12]}' target='_blank' style='background:#0d9488; color:white; padding:2px 5px; border-radius:3px; text-decoration:none; font-size:10.5px;'>👤 ફોટો</a>" if r[12] else ""
            rep_cancel_btn = f" <a href='javascript:void(0)' onclick='var p=prompt(\"રિપેરિંગ ખર્ચ ₹{r_cost:,.0f} રદ કરી ગલ્લામાં પાછો જમા કરવા સિક્યુરિટી PIN નાખો:\",\"\"); if(p) window.location.href=\"/api/cancel-buyback-repair?id={r[11]}&pin=\"+encodeURIComponent(p);' style='background:#d97706; color:white; padding:2px 5px; border-radius:3px; text-decoration:none; font-size:10.5px; font-weight:bold;'>🛠️ રિપેર રદ</a>" if r_cost > 0 else ""
            act_btns = f"{doc_btn}{cust_ph_btn}{rep_cancel_btn} <a href='/?sheet=BUYBACK_STOCK&edit_bb_id={r[11]}' style='background:#0284c7; color:white; padding:2px 5px; border-radius:3px; text-decoration:none; font-size:10.5px; font-weight:bold;'>✏️ એડિટ</a> <a href='javascript:void(0)' onclick='var p=prompt(\"આ બાયબેક એન્ટ્રી રદ કરી ગલ્લાની રોકડ રિવર્સ કરવા સિક્યુરિટી માસ્ટર PIN નાખો:\",\"\"); if(p) window.location.href=\"/delete-buyback-item?id={r[11]}&pin=\"+encodeURIComponent(p);' style='background:#dc2626; color:white; padding:2px 5px; border-radius:3px; text-decoration:none; font-size:10.5px; font-weight:bold;'>🗑️ રદ</a>"
            bb_trs += f"""
            <tr>
                <td>{r[0]}</td><td><b>{r[1]}</b></td><td><b>{r[2]}</b></td><td>{r[3] or '-'}</td>
                <td>₹{p_cost:,.0f}</td><td style='color:#b45309;'>+ ₹{r_cost:,.0f}</td>
                <td style='font-weight:bold; color:#0f2043;'>₹{t_cost:,.0f}</td>
                <td style='font-weight:bold; color:#15803d;'>₹{s_prc:,.0f}</td>
                <td>{st_badge}</td><td>{r[9] or '-'}</td><td>{act_btns}</td>
            </tr>"""
        if not bb_trs:
            bb_trs = "<tr><td colspan='11'>હજુ કોઈ જૂનો બાય-બેક ફોન નોંધાયેલ નથી</td></tr>"

        galla_bb_in = build_4galla_sel_c("galla_name", "BANK_CASH")
        galla_bb_rep = build_4galla_sel_c("galla_name", "BANK_CASH")
        galla_bb_sale = build_4galla_sel_c("galla_name", "BANK_CASH")
        galla_bb_ret = build_4galla_sel_c("refund_galla", "BANK_CASH")

        return f"""
        <div class="mode-banner">
            <span>મોડ: [F5] બાય-બેક (જૂના ફોન), રિપેરિંગ પડતર, વેચાણ (Resale - નફો ગલ્લા ૪ માં) & ભાગ ૪: બાય-બેક રિટર્ન અને કેશ રિફંડ</span>
            <a href="/police-verification-form" target="_blank" style="background:#fde047; color:#0f2043; padding:3px 10px; border-radius:4px; text-decoration:none; font-weight:800; font-size:11.5px;">👮 પોલીસ વેરિફિકેશન વૉલ્ટ ખોલો</a>
        </div>

        <!-- TALLY PRIME SUB-SECTIONS STRIP (F5 ૧ થી ૫ લાઈનબદ્ધ પેટા વિભાગો) -->
        <div class="tally-subparts-bar">
            <span style="color:#fde047; font-weight:800; font-size:11px; margin-right:4px;">પેટા વિભાગ:</span>
            <button type="button" class="tally-sub-btn active" id="f5_sub_btn_ALL_4_GRID" onclick="setSubpartF5('ALL_4_GRID')">૧. ચારેય ભાગ ગ્રીડ (ALL)</button>
            <button type="button" class="tally-sub-btn" id="f5_sub_btn_PART1" onclick="setSubpartF5('PART1')">૨. ભાગ ૧: જૂનો ફોન ખરીદી</button>
            <button type="button" class="tally-sub-btn" id="f5_sub_btn_PART2" onclick="setSubpartF5('PART2')">૩. ભાગ ૨: રિપેરિંગ પડતર</button>
            <button type="button" class="tally-sub-btn" id="f5_sub_btn_PART3" onclick="setSubpartF5('PART3')">૪. ભાગ ૩: જૂના ફોન વેચાણ</button>
            <button type="button" class="tally-sub-btn" id="f5_sub_btn_PART4" onclick="setSubpartF5('PART4')">૫. ભાગ ૪: રિટર્ન & રિફંડ</button>
        </div>

        <div class="term-form">
            <div class="f-row" style="background:#0f2043; color:white; padding:6px 10px; border-radius:6px; margin-bottom:10px;">
                <div class="lbl" style="color:#fde047; width:240px;">F5 બાય-બેક વિભાગ પસંદ કરો (૪ ભાગ):</div>
                <select id="f5_part_sel" onchange="switchF5Part(this.value)" style="font-weight:800; font-size:13px; background:#fef08a; color:#0f2043; flex:1;">
                    <option value="ALL_4_GRID">📋 ચારેય ભાગ એકસાથે જુઓ (ભાગ ૧: ખરીદી | ભાગ ૨: રિપેરિંગ | ભાગ ૩: વેચાણ | ભાગ ૪: રિટર્ન & રિફંડ)</option>
                    <option value="PART1">ભાગ ૧: જૂનો ફોન ઇનવર્ડ / બાય-બેક ખરીદી (Buyback Inward - ૭ ખાનાં)</option>
                    <option value="PART2">ભાગ ૨: જૂના ફોનમાં રિપેરિંગ પડતર ઉમેરો (Repairing Cost Add - ૫ ખાનાં)</option>
                    <option value="PART3">ભાગ ૩: જૂના ફોનનું સીધું વેચાણ (Old Phone Resale - પડતર ગલ્લા ૧ માં, નફો ગલ્લા ૪ માં - ૬ ખાનાં)</option>
                    <option value="PART4">ભાગ ૪: બાય-બેક રિટર્ન અને કેશ રિફંડ ફોર્મ (Buyback Return & Cash Refund - ૯ ખાનાં)</option>
                    
                </select>
            </div>

            <style>#f5_grid_container .f-row {{ display:flex; align-items:center; gap:5px; flex-wrap:wrap; width:100%; box-sizing:border-box; }} #f5_grid_container .f-row .lbl {{ width:135px !important; min-width:120px !important; font-size:11.5px; flex-shrink:0; }} #f5_grid_container input, #f5_grid_container select {{ min-width:0 !important; max-width:100% !important; box-sizing:border-box !important; }} #f5_grid_container input[type="file"] {{ max-width:145px !important; font-size:10.5px !important; }}</style>
            <div id="f5_grid_container" style="display:grid; grid-template-columns:repeat(auto-fit, minmax(360px, 1fr)); gap:10px; width:100%; box-sizing:border-box;">
                <!-- ભાગ ૧: જૂનો ફોન ઇનવર્ડ / બાય-બેક ખરીદી (૮ કંડિશન + ગ્રાહક ફોટો + ડુપ્લિકેટ IMEI લોક) -->
                <div id="f5_box_p1" data-sub-allowed="{'1' if 'F5_1' in active_subparts else '0'}" style="display:{'block' if 'F5_1' in active_subparts else 'none'}; background:#f8fafc; border:2px solid #0284c7; border-radius:6px; padding:10px; min-width:0; overflow:hidden; box-sizing:border-box;">
                    <h4 style="margin:0 0 8px 0; color:#0369a1;">📥 ભાગ ૧: જૂનો ફોન ઇનવર્ડ / બાય-બેક ખરીદી (ડુપ્લિકેટ IMEI લોક સાથે)</h4>
                    <form class="f-enter-form" action="/save-f1" method="post" enctype="multipart/form-data">
                        <input type="hidden" name="tx_type" value="DIRECT_BB">
                        <input type="hidden" name="return_mode" value="F5">
                        <div class="f-row"><div class="lbl" style="width:135px;">૧. તારીખ & સમય:</div><input type="date" name="entry_date" value="{today_str}"></div>
                        <div class="f-row"><div class="lbl" style="width:135px;">૨. ગ્રાહક નામ & ૧૦-અંક મોબાઈલ:</div>
                            <input type="text" name="customer_name" placeholder="વેચનાર ગ્રાહકનું નામ..." required style="flex:1;">
                            <input type="text" name="customer_phone" maxlength="10" placeholder="૧૦-અંક મોબાઈલ" style="max-width:125px;">
                        </div>
                        <div class="f-row"><div class="lbl" style="width:135px;">૩. બ્રાન્ડ, મોડેલ & ૧૫-અંક IMEI:</div>
                            <div style="display:flex; gap:3px; align-items:center; max-width:185px;">
    <select name="bb_brand" id="f5_bb_brand_sel" style="flex:1; font-weight:bold;">{brand_opts_html}</select>
    <button type="button" onclick="openInlineQuickCreateModal('BRAND', 'f5_bb_brand_sel')" style="background:#0284c7; color:white; border:none; padding:3px 6px; border-radius:3px; font-size:10px; font-weight:bold; cursor:pointer;" title="નવી બ્રાન્ડ ઉમેરો (Alt+C)">[+ નવી બ્રાન્ડ]</button>
</div>
                            <input type="text" name="bb_model" placeholder="મોડેલ નામ" style="flex:1;" required>
                            <input type="text" name="bb_imei" maxlength="15" placeholder="૧૫-અંક IMEI" style="max-width:140px;" required>
                        </div>
                        <div class="f-row"><div class="lbl" style="width:135px;">૪. ફોન કંડિશન (૮ વિકલ્પો):</div>
                            <select name="bb_condition" style="font-weight:bold;">
                                <option value="૧. બિલ + બોક્સ + ઓરિજિનલ ચાર્જર સાથે (Full Kit)">૧. બિલ + બોક્સ + ઓરિજિનલ ચાર્જર સાથે (Full Kit)</option>
                                <option value="૨. માત્ર પાકું બિલ અને બોક્સ સાથે (Bill + Box)">૨. માત્ર પાકું બિલ અને બોક્સ સાથે (Bill + Box)</option>
                                <option value="૩. માત્ર ઓરિજિનલ બિલ સાથે (Bill Only)">૩. માત્ર ઓરિજિનલ બિલ સાથે (Bill Only)</option>
                                <option value="૪. માત્ર બોક્સ અને ચાર્જર સાથે (Box + Charger)">૪. માત્ર બોક્સ અને ચાર્જર સાથે (Box + Charger)</option>
                                <option value="૫. માત્ર ફોન - આધારકાર્ડ અને લાઈવ ફોટો પ્રૂફ સાથે">૫. માત્ર ફોન - આધારકાર્ડ અને લાઈવ ફોટો પ્રૂફ સાથે</option>
                                <option value="૬. કંપની વોરંટી ચાલુ ફોન (In-Warranty Mint)">૬. કંપની વોરંટી ચાલુ ફોન (In-Warranty Mint)</option>
                                <option value="૭. ગ્લાસ તૂટેલો / માઈનોર સ્ક્રેચ વાળો ફોન">૭. ગ્લાસ તૂટેલો / માઈનોર સ્ક્રેચ વાળો ફોન</option>
                                <option value="૮. ડિસ્પ્લે / બેટરી રિપેરિંગ જરૂરી ફોન">૮. ડિસ્પ્લે / બેટરી રિપેરિંગ જરૂરી ફોન</option>
                            </select>
                        </div>
                        <div class="f-row"><div class="lbl" style="width:135px;">૫. બાય-બેક ખરીદ પડતર (₹):</div><input type="number" step="any" name="bb_cost" value="0" required style="font-weight:bold; color:#dc2626;"></div>
                        <div class="f-row"><div class="lbl" style="width:135px;">૬. ચૂકવણી પદ્ધતિ (MOP) & ગલ્લો:</div><select name="pay_mode" id="f5_p1_mop" onchange="syncUniversalMopGalla(this, 'f5_p1_galla')" style="max-width:140px; font-weight:bold;"><option value="રોકડ (Cash)">💵 ૧. રોકડ (Cash)</option><option value="ઓનલાઈન UPI">📱 ૨. ઓનલાઈન UPI</option><option value="કાર્ડ સ્વાઇપ">💳 ૩. કાર્ડ સ્વાઇપ</option><option value="બેંક ટ્રાન્સફર">🏦 ૪. બેંક ટ્રાન્સફર</option></select><select name="paid_from_galla" id="f5_p1_galla" style="font-weight:bold; color:#0f2043; flex:1;"><option value="BANK_CASH" selected>૧. બેંક કેશ (ગલ્લો ૧)</option><option value="ACC_DCASH">૨. એક્સેસરીઝ કેશ (ગલ્લો ૨)</option><option value="RECHARGE">૩. રિચાર્જ કેશ (ગલ્લો ૩)</option><option value="EXTRA_CASH">૪. એક્સ્ટ્રા કેશ (ગલ્લો ૪)</option></select></div>
                        <div class="f-row"><div class="lbl" style="width:135px;">૭. આધાર/બિલ & ગ્રાહક ફોટો:</div>
                            <input type="file" name="bb_photo" accept=".pdf,image/*" title="આધાર/બિલ પ્રૂફ" style="flex:1;">
                            <input type="file" name="customer_face_photo" accept="image/*" capture="user" title="ગ્રાહકનો ફોટો" style="flex:1;">
                        </div>
                        <div class="f-row"><div class="lbl" style="width:135px;">૮. ખરીદનાર સ્ટાફ નામ:</div><select name="salesman">{staff_opts_html}</select></div>
                        <button type="submit" style="width:100%; background:#0284c7; color:white; border:none; padding:8px; border-radius:4px; font-weight:800; cursor:pointer; margin-top:4px;">[ ભાગ ૧: જૂનો ફોન સ્ટોકમાં સાચવો (Enter) ]</button>
                    </form>
                </div>

                <!-- ભાગ ૨: જૂના ફોનમાં રિપેરિંગ પડતર ઉમેરો (૫ ખાનાં) -->
                <div id="f5_box_p2" data-sub-allowed="{'1' if 'F5_2' in active_subparts else '0'}" style="display:{'block' if 'F5_2' in active_subparts else 'none'}; background:#fffbeb; border:2px solid #d97706; border-radius:6px; padding:10px; min-width:0; overflow:hidden; box-sizing:border-box;">
                    <h4 style="margin:0 0 8px 0; color:#b45309;">🛠️ ભાગ ૨: જૂના ફોનમાં રિપેરિંગ પડતર / અપડેટ (૫ ખાનાં)</h4>
                    <form class="f-enter-form" action="/save-f3" method="post" enctype="multipart/form-data">
                        <input type="hidden" name="f3_action" value="BB_REPAIR">
                        <div class="f-row"><div class="lbl" style="width:135px;">૧. હાજર (In-Stock) ફોન સિલેક્ટ:</div>
                            <select name="bb_imei" id="f5_p2_imei" onchange="calcF5P2NewCost()" required style="flex:1; font-weight:bold;">{bb_instock_opts}</select>
                        </div>
                        <div class="f-row"><div class="lbl" style="width:135px;">૨. રિપેરિંગ / સ્પેરપાર્ટ ખર્ચ (₹):</div>
                            <input type="number" step="any" name="repair_cost" id="f5_p2_rep" value="0" oninput="calcF5P2NewCost()" required style="font-weight:bold; color:#b45309;">
                            <span id="f5_p2_new_cost_badge" style="font-size:11.5px; font-weight:800; color:#0f2043; background:#fef08a; padding:4px 8px; border-radius:4px;">નવી કુલ પડતર: ₹0</span>
                        </div>
                        <div class="f-row"><div class="lbl" style="width:135px;">૩. ચૂકવણી પદ્ધતિ (MOP) & ગલ્લો:</div><select name="pay_mode" id="f5_p2_mop" onchange="syncUniversalMopGalla(this, 'f5_p2_galla')" style="max-width:140px; font-weight:bold;"><option value="રોકડ (Cash)">💵 ૧. રોકડ (Cash)</option><option value="ઓનલાઈન UPI">📱 ૨. ઓનલાઈન UPI</option><option value="કાર્ડ સ્વાઇપ">💳 ૩. કાર્ડ સ્વાઇપ</option><option value="બેંક ટ્રાન્સફર">🏦 ૪. બેંક ટ્રાન્સફર</option></select><select name="paid_from_galla" id="f5_p2_galla" style="font-weight:bold; color:#0f2043; flex:1;"><option value="EXTRA_CASH" selected>૪. એક્સ્ટ્રા કેશ (ગલ્લો ૪)</option><option value="BANK_CASH">૧. બેંક કેશ (ગલ્લો ૧)</option><option value="ACC_DCASH">૨. એક્સેસરીઝ કેશ (ગલ્લો ૨)</option><option value="RECHARGE">૩. રિચાર્જ કેશ (ગલ્લો ૩)</option></select></div>
                        <div class="f-row"><div class="lbl" style="width:135px;">૪. રિપેરિંગ વિગત & ફોટો/બિલ:</div>
                            <input type="text" name="remarks" placeholder="ડિસ્પ્લે, બેટરી કે રિપેરિંગ નોંધ..." style="flex:1;">
                            <input type="file" name="bb_doc" accept=".pdf,image/*" style="max-width:170px;">
                        </div>
                        <button type="submit" style="width:100%; background:#d97706; color:white; border:none; padding:8px; border-radius:4px; font-weight:800; cursor:pointer; margin-top:4px;">૫. [ ભાગ ૨: રિપેરિંગ પડતર ઉમેરો & અપડેટ કરો (Enter) ]</button>
                    </form>
                </div>

                <!-- ભાગ ૩: જૂના ફોનનું સીધું વેચાણ (Resale - ૬ ખાનાં) -->
                <div id="f5_box_p3" data-sub-allowed="{'1' if 'F5_3' in active_subparts else '0'}" style="display:{'block' if 'F5_3' in active_subparts else 'none'}; background:#f0fdf4; border:2px solid #16a34a; border-radius:6px; padding:10px; min-width:0; overflow:hidden; box-sizing:border-box;">
                    <h4 style="margin:0 0 8px 0; color:#15803d;">💰 ભાગ ૩: જૂના ફોનનું સીધું વેચાણ (Old Phone Resale - ૬ ખાનાં)</h4>
                    <form class="f-enter-form" action="/save-f3" method="post" enctype="multipart/form-data">
                        <input type="hidden" name="f3_action" value="BB_SALE">
                        <div class="f-row"><div class="lbl" style="width:135px;">૧. વેચવા માટે ફોન (In-Stock):</div>
                            <select name="bb_imei" id="f5_p3_imei" onchange="calcF5P3Split()" required style="flex:1; font-weight:bold;">{bb_instock_opts}</select>
                        </div>
                        <div class="f-row"><div class="lbl" style="width:135px;">૨. વેચાણ કિંમત (Sale Price ₹):</div>
                            <input type="number" step="any" name="sale_price" id="f5_p3_sale" value="0" oninput="calcF5P3Split()" required style="font-weight:bold; color:#15803d; font-size:13.5px;">
                        </div>
                        <div id="f5_p3_split_hint" style="background:#dcfce7; border:1px solid #86efac; padding:5px 8px; border-radius:4px; font-size:11.5px; font-weight:bold; color:#166534; margin-bottom:6px;">
                            💡 ઓટો-પ્રોફિટ સ્પ્લિટ: મૂળ કુલ પડતર પસંદ કરેલા ગલ્લામાં (ગલ્લો ૧) અને ઉપરનો ચોખ્ખો નફો સીધો ગલ્લો ૪ (તિજોરી) અને P&L માં જમા થશે!
                        </div>
                        <div class="f-row"><div class="lbl" style="width:135px;">૩. ખરીદનાર ગ્રાહક નામ & મોબાઈલ:</div>
                            <input type="text" name="customer_name" placeholder="ગ્રાહકનું નામ" required style="flex:1;">
                            <input type="text" name="phone" placeholder="૧૦-અંક મોબાઈલ" style="max-width:135px;">
                        </div>
                        <div class="f-row"><div class="lbl" style="width:135px;">૪. સેલ્સમેન નામ:</div><select name="salesman">{staff_opts_html}</select></div>
                        <div class="f-row"><div class="lbl" style="width:135px;">૫. પ્રાપ્તિ પદ્ધતિ (MOP) & ગલ્લો:</div><select name="pay_mode" id="f5_p3_mop" onchange="syncUniversalMopGalla(this, 'f5_p3_galla')" style="max-width:140px; font-weight:bold;"><option value="રોકડ (Cash)">💵 ૧. રોકડ (Cash)</option><option value="ઓનલાઈન UPI">📱 ૨. ઓનલાઈન UPI</option><option value="કાર્ડ સ્વાઇપ">💳 ૩. કાર્ડ સ્વાઇપ</option><option value="બેંક ટ્રાન્સફર">🏦 ૪. બેંક ટ્રાન્સફર</option></select><select name="received_galla" id="f5_p3_galla" style="font-weight:bold; color:#0f2043; flex:1;"><option value="BANK_CASH" selected>૧. બેંક કેશ (ગલ્લો ૧)</option><option value="ACC_DCASH">૨. એક્સેસરીઝ કેશ (ગલ્લો ૨)</option><option value="RECHARGE">૩. રિચાર્જ કેશ (ગલ્લો ૩)</option><option value="EXTRA_CASH">૪. એક્સ્ટ્રા કેશ (ગલ્લો ૪)</option></select></div>
                        <button type="submit" style="width:100%; background:#15803d; color:white; border:none; padding:8px; border-radius:4px; font-weight:800; cursor:pointer; margin-top:4px;">૬. [ ભાગ ૩: જૂનો ફોન વેચાણ સેવ કરો (ઓટો-પ્રોફિટ સ્પ્લિટ) ]</button>
                    </form>
                </div>

                <!-- ભાગ ૪: બાય-બેક રિટર્ન અને કેશ રિફંડ ફોર્મ (૯ ખાનાં) -->
                <div id="f5_box_p4" data-sub-allowed="{'1' if 'F5_4' in active_subparts else '0'}" style="display:{'block' if 'F5_4' in active_subparts else 'none'}; background:#fef2f2; border:2px solid #dc2626; border-radius:6px; padding:10px; min-width:0; overflow:hidden; box-sizing:border-box;">
                    <h4 style="margin:0 0 8px 0; color:#991b1b;">🔄 ભાગ ૪: બાય-બેક રિટર્ન અને કેશ રિફંડ ફોર્મ (૯ ખાનાં)</h4>
                    <form class="f-enter-form" action="/save-f5-bb-return" method="post">
                        <div class="f-row"><div class="lbl" style="width:135px;">૧. વેચાયેલ (SOLD) ફોન / IMEI:</div>
                            <select name="imei" id="f5_p4_imei" onchange="onF5SoldSelect()" required style="flex:1; font-weight:bold;">{bb_sold_opts}</select>
                        </div>
                        <div class="f-row"><div class="lbl" style="width:135px;">૨. ગ્રાહક, મોડેલ & વેચાણ તારીખ:</div>
                            <input type="text" name="customer_name" id="f5_p4_cust" placeholder="ગ્રાહક નામ" style="flex:1;">
                            <input type="text" name="model" id="f5_p4_model" placeholder="મોડેલ" style="max-width:120px;">
                            <input type="text" name="orig_sale_date" id="f5_p4_date" placeholder="તારીખ" style="max-width:100px;">
                        </div>
                        <div class="f-row"><div class="lbl" style="width:135px;">૩. મૂળ વેચાણ કિંમત (₹) [Auto]:</div>
                            <input type="number" step="any" name="orig_sale_price" id="f5_p4_orig" value="0" oninput="calcF5Refund()" required style="font-weight:bold;">
                        </div>
                        <div class="f-row"><div class="lbl" style="width:135px;">૪. કાપવાની રકમ / ઘસારો (₹):</div>
                            <input type="number" step="any" name="deduction_amt" id="f5_p4_ded" value="0" oninput="calcF5Refund()" style="font-weight:bold; color:#15803d;">
                        </div>
                        <div class="f-row" style="background:#fee2e2; padding:3px; border-radius:4px;">
                            <div class="lbl" style="width:195px; color:#991b1b;">૫. પરત કરવાની ચોખ્ખી રકમ (₹):</div>
                            <input type="number" step="any" name="net_refund_amt" id="f5_p4_net" value="0" readonly style="font-weight:800; color:#dc2626; font-size:13.5px;">
                        </div>
                        <div class="f-row"><div class="lbl" style="width:135px;">૬. ચૂકવણી મોડ & રિફંડ ગલ્લો:</div>
                            <select name="pay_mode" id="f5_p4_mop" onchange="syncUniversalMopGalla(this, 'f5_p4_galla')" style="max-width:140px; font-weight:bold;"><option value="રોકડ (Cash)">💵 ૧. રોકડ (Cash)</option><option value="ઓનલાઈન UPI">📱 ૨. ઓનલાઈન UPI</option><option value="કાર્ડ સ્વાઇપ">💳 ૩. કાર્ડ સ્વાઇપ</option><option value="ઓનલાઈન ટ્રાન્સફર">🏦 ૪. બેંક ટ્રાન્સફર</option></select>
                            <select name="refund_galla" id="f5_p4_galla" style="font-weight:bold; color:#0f2043; flex:1;"><option value="BANK_CASH" selected>૧. બેંક કેશ (ગલ્લો ૧)</option><option value="ACC_DCASH">૨. એક્સેસરીઝ કેશ (ગલ્લો ૨)</option><option value="RECHARGE">૩. રિચાર્જ કેશ (ગલ્લો ૩)</option><option value="EXTRA_CASH">૪. એક્સ્ટ્રા કેશ (ગલ્લો ૪)</option></select>
                        </div>
                        <div class="f-row"><div class="lbl" style="width:135px;">૮. સ્ટાફ નામ & રિટર્નનું કારણ:</div>
                            <select name="staff_name" style="max-width:150px;">{staff_opts_html}</select>
                            <input type="text" name="reason" placeholder="રિટર્નનું કારણ..." style="flex:1;">
                        </div>
                        <button type="submit" style="width:100%; background:#dc2626; color:white; border:none; padding:8px; border-radius:4px; font-weight:800; cursor:pointer; margin-top:4px;">૯. [ રિટર્ન સેવ કરો & રિફંડ આપો (IMEI પાછો In-Stock થશે) ]</button>
                    </form>
                </div>
            </div>

            <!-- બાય-બેક લાઈવ સ્ટોક અને વેચાણ રજીસ્ટર -->
            <div style="margin-top:12px; background:white; border:1px solid #cbd5e1; border-radius:6px; padding:10px; width:100%; box-sizing:border-box; overflow-x:auto;">
                <h4 style="margin:0 0 6px 0; color:#0f2043;">📱 જૂના ફોન (બાય-બેક) લાઈવ સ્ટોક, રિપેરિંગ પડતર અને વેચાણ રજીસ્ટર</h4>
                <table class="live-grid">
                    <tr><th>તારીખ</th><th>મોડેલ</th><th>IMEI</th><th>ગ્રાહક</th><th>ખરીદ કિંમત</th><th>રિપેરિંગ ખર્ચ</th><th>કુલ પડતર</th><th>વેચાણ કિંમત</th><th>સ્થિતિ / નફો</th><th>સેલ્સમેન</th><th>પ્રૂફ</th></tr>
                    {bb_trs}
                </table>
            </div>
        </div>

        <script>
            function syncUniversalMopGalla(mopEl, gallaElId) {{
                var gallaEl = (typeof gallaElId === 'string') ? document.getElementById(gallaElId) : gallaElId;
                if (!mopEl || !gallaEl) return;
                var mop = (mopEl.value || '').trim();
                var isDigital = (
                    mop.indexOf('UPI') !== -1 || mop.indexOf('બેંક') !== -1 || mop.indexOf('Bank') !== -1 ||
                    mop.indexOf('કાર્ડ') !== -1 || mop.indexOf('Card') !== -1 || mop.indexOf('NEFT') !== -1 ||
                    mop.indexOf('RTGS') !== -1 || mop.indexOf('IMPS') !== -1 || mop.indexOf('ઓનલાઇન') !== -1 ||
                    mop.indexOf('ઓનલાઈન') !== -1 || mop.indexOf('ચેક') !== -1 || mop.indexOf('Cheque') !== -1
                );
                if (isDigital) {{
                    var desc = (mop.indexOf('કાર્ડ') !== -1 || mop.indexOf('Card') !== -1) ? 'કાર્ડ સ્વાઇપ POS' :
                               (mop.indexOf('UPI') !== -1 ? 'UPI QR કોડ' : 'બેંક ખાતું');
                    gallaEl.innerHTML = '<option value="ONLINE_BANK" selected>🏦 ડિજિટલ બેંક એકાઉન્ટ (' + desc + ' - સીધા ખાતામાં)</option>';
                    gallaEl.style.background = '#e0f2fe';
                    gallaEl.style.borderColor = '#0284c7';
                    gallaEl.style.color = '#0369a1';
                }} else {{
                    var pref = (gallaElId.indexOf('p2') !== -1 || gallaElId.indexOf('extra') !== -1) ? 'EXTRA_CASH' : 'BANK_CASH';
                    gallaEl.innerHTML = '<option value="BANK_CASH"' + (pref === 'BANK_CASH' ? ' selected' : '') + '>૧. બેંક કેશ (ગલ્લો ૧)</option>' +
                                        '<option value="ACC_DCASH">૨. એક્સેસરીઝ કેશ (ગલ્લો ૨)</option>' +
                                        '<option value="RECHARGE">૩. રિચાર્જ કેશ (ગલ્લો ૩)</option>' +
                                        '<option value="EXTRA_CASH"' + (pref === 'EXTRA_CASH' ? ' selected' : '') + '>૪. એક્સ્ટ્રા કેશ (ગલ્લો ૪)</option>';
                    gallaEl.style.background = '#ffffff';
                    gallaEl.style.borderColor = '#15803d';
                    gallaEl.style.color = '#0f2043';
                }}
            }}
            window.syncUniversalMopGalla = syncUniversalMopGalla;
            window.syncF7MopGalla = syncUniversalMopGalla;
            function setSubpartF5(val){{
                var sel = document.getElementById('f5_part_sel');
                if (sel) sel.value = val;
                switchF5Part(val);
            }}

            function switchF5Part(val){{
                document.querySelectorAll('.tally-subparts-bar .tally-sub-btn').forEach(function(b){{
                    b.classList.remove('active');
                }});
                var curBtn = document.getElementById('f5_sub_btn_' + val);
                if (curBtn) curBtn.classList.add('active');
                var p1 = document.getElementById('f5_box_p1');
                var p2 = document.getElementById('f5_box_p2');
                var p3 = document.getElementById('f5_box_p3');
                var p4 = document.getElementById('f5_box_p4');
                var grid = document.getElementById('f5_grid_container');
                if(val === 'ALL_4_GRID'){{
                    grid.style.display = 'grid';
                    grid.style.gridTemplateColumns = 'repeat(auto-fit, minmax(390px, 1fr))';
                    p1.style.display = (p1.getAttribute('data-sub-allowed') !== '0') ? 'block' : 'none';
                    p2.style.display = (p2.getAttribute('data-sub-allowed') !== '0') ? 'block' : 'none';
                    p3.style.display = (p3.getAttribute('data-sub-allowed') !== '0') ? 'block' : 'none';
                    p4.style.display = (p4.getAttribute('data-sub-allowed') !== '0') ? 'block' : 'none';
                }} else {{
                    grid.style.display = 'block';
                    p1.style.display = (val === 'PART1') ? 'block' : 'none';
                    p2.style.display = (val === 'PART2') ? 'block' : 'none';
                    p3.style.display = (val === 'PART3') ? 'block' : 'none';
                    p4.style.display = (val === 'PART4') ? 'block' : 'none';
                }}
            }}
            function calcF5P2NewCost(){{
                var sel = document.getElementById('f5_p2_imei');
                var opt = sel.options[sel.selectedIndex];
                var baseCost = opt ? (parseFloat(opt.getAttribute('data-cost')) || 0) : 0;
                var rep = parseFloat(document.getElementById('f5_p2_rep').value) || 0;
                document.getElementById('f5_p2_new_cost_badge').innerText = 'નવી કુલ પડતર: ₹' + Math.round(baseCost + rep).toLocaleString('en-IN');
            }}
            function calcF5P3Split(){{
                var sel = document.getElementById('f5_p3_imei');
                var opt = sel.options[sel.selectedIndex];
                var totCost = opt ? (parseFloat(opt.getAttribute('data-cost')) || 0) : 0;
                var saleP = parseFloat(document.getElementById('f5_p3_sale').value) || 0;
                var netP = Math.max(0, saleP - totCost);
                document.getElementById('f5_p3_split_hint').innerHTML = '💡 <b>ઓટો-સ્પ્લિટ ગણતરી:</b> મૂળ પડતર <b>₹' + Math.round(totCost).toLocaleString('en-IN') + '</b> -> ગલ્લો ૧ માં જમા | ચોખ્ખો નફો <b>₹' + Math.round(netP).toLocaleString('en-IN') + '</b> -> સીધો ગલ્લો ૪ (તિજોરી) અને P&L માં જમા!';
            }}
            function onF5SoldSelect(){{
                var sel = document.getElementById('f5_p4_imei');
                var opt = sel.options[sel.selectedIndex];
                if(opt){{
                    document.getElementById('f5_p4_cust').value = opt.getAttribute('data-cust') || '';
                    document.getElementById('f5_p4_date').value = opt.getAttribute('data-date') || '';
                    document.getElementById('f5_p4_model').value = opt.getAttribute('data-model') || '';
                    document.getElementById('f5_p4_orig').value = opt.getAttribute('data-price') || 0;
                    calcF5Refund();
                }}
            }}
            function calcF5Refund(){{
                var orig = parseFloat(document.getElementById('f5_p4_orig').value) || 0;
                var ded = parseFloat(document.getElementById('f5_p4_ded').value) || 0;
                document.getElementById('f5_p4_net').value = Math.max(0, Math.round(orig - ded));
            }}
        </script>
        """

    # =========================================================================
    # [F6] આંતરિક ગલ્લા ટ્રાન્સફર ટેબલ (Vault-to-Vault Transfer - ૭ ખાનાં) + LAPU ઓડિટ
    # =========================================================================
    elif mode == "F6":
        c.execute("""SELECT date, galla_name, in_amt, out_amt, remarks FROM galla_ledger
                     WHERE remarks LIKE '%ટ્રાન્સફર%' ORDER BY id DESC LIMIT 15""")
        tr_rows = c.fetchall()
        tr_log_html = "".join([
            f"<tr><td>{r[0]}</td><td><b>{r[1]}</b></td><td style='color:#15803d; font-weight:bold;'>+ ₹{float(r[2] or 0):,.0f}</td><td style='color:#dc2626; font-weight:bold;'>- ₹{float(r[3] or 0):,.0f}</td><td>{r[4]}</td></tr>"
            for r in tr_rows
        ]) or "<tr><td colspan='5'>હજુ કોઈ આંતરિક ગલ્લા ટ્રાન્સફર નોંધાયેલ નથી</td></tr>"

        c.execute("""SELECT challan_no, transfer_date, from_store_id, to_store_id, COUNT(id), SUM(purchase_rate), carrier_name, status
                     FROM stock_transfer_ledger
                     GROUP BY challan_no, transfer_date, from_store_id, to_store_id, carrier_name, status
                     ORDER BY id DESC LIMIT 15""")
        st_history_rows = c.fetchall()
        st_history_trs = "".join([
            f"<tr><td><b>{r[0]}</b></td><td>{r[1]}</td><td><span style='background:#fef3c7; color:#b45309; padding:2px 6px; border-radius:4px; font-weight:bold;'>{r[2]}</span> ➔ <span style='background:#dcfce7; color:#166534; padding:2px 6px; border-radius:4px; font-weight:bold;'>{r[3]}</span></td><td style='text-align:center; font-weight:bold;'>{r[4]} ફોન</td><td style='font-weight:bold; color:#0284c7;'>₹{float(r[5] or 0):,.0f}</td><td>{r[6] or '-'}</td><td><span style='background:#dcfce7; color:#15803d; padding:2px 6px; border-radius:4px; font-weight:bold;'>{r[7]}</span></td><td><a href='/stock-transfer-challan?challan_no={r[0]}' target='_blank' style='background:#0284c7; color:white; padding:3px 8px; border-radius:4px; text-decoration:none; font-size:11px; font-weight:bold;'>🖨️ ચલણ પ્રિન્ટ</a></td></tr>"
            for r in st_history_rows
        ]) or "<tr><td colspan='8'>હજુ સુધી કોઈ બ્રાન્ચ સ્ટોક ટ્રાન્સફર નોંધાયેલ નથી</td></tr>"
        c.execute("SELECT company, current_demo_balance, pending_distributor_due FROM recharge_lapu_company_balances")
        cb_rows = {r[0]: (float(r[1] or 0), float(r[2] or 0)) for r in c.fetchall()}
        jio_demo, jio_due = cb_rows.get("Jio", (0.0, 0.0))
        airtel_demo, airtel_due = cb_rows.get("Airtel", (0.0, 0.0))
        vi_demo, vi_due = cb_rows.get("Vi", (0.0, 0.0))

        # Fix 20: Cross-Galla Borrowed Payment Ledger & 5-Day Cash Inflow Trigger Check
        from part1_core import get_galla_balance
        g_live_bals = {
            "BANK_CASH": get_galla_balance("BANK_CASH"),
            "ACC_DCASH": get_galla_balance("ACC_DCASH"),
            "RECHARGE": get_galla_balance("RECHARGE"),
            "EXTRA_CASH": get_galla_balance("EXTRA_CASH")
        }
        g_names_gu = {
            "BANK_CASH": "ગલ્લો ૧ (બેંક કેશ)",
            "ACC_DCASH": "ગલ્લો ૨ (એક્સેસરીઝ D-Cash)",
            "RECHARGE": "ગલ્લો ૩ (રિચાર્જ કેશ)",
            "EXTRA_CASH": "ગલ્લો ૪ (એક્સ્ટ્રા કેશ)"
        }
        c.execute("""SELECT id, tx_date, lender_galla, borrower_galla, amount, COALESCE(settled_amt,0), status, remarks, COALESCE(settled_date,'')
                     FROM inter_galla_debt_ledger ORDER BY CASE WHEN status='PENDING' THEN 0 ELSE 1 END, id DESC LIMIT 20""")
        ig_debt_rows = c.fetchall()
        cross_alert_items = []
        ig_table_trs = ""
        for igr in ig_debt_rows:
            ig_id, ig_dt, l_g, b_g, ig_amt, ig_set, ig_st, ig_rem, ig_sdt = igr
            rem_v = max(0.0, float(ig_amt or 0) - float(ig_set or 0))
            b_cash_now = float(g_live_bals.get(b_g, 0.0))
            if ig_st == "PENDING" and rem_v > 0:
                if b_cash_now > 0:
                    settle_btn = f"<a href='/api/settle-inter-galla-debt?debt_id={ig_id}' style='background:#16a34a; color:white; padding:3px 9px; border-radius:4px; text-decoration:none; font-weight:900; font-size:11px;'>⚡ ૧-ક્લિક પરત સેટલ (₹{min(rem_v, b_cash_now):,.0f})</a>"
                    cross_alert_items.append(
                        f"<div>🚨 <b>[કેશ આવક ટ્રીગર સક્રિય]</b> તારીખ <b>{ig_dt}</b> ના રોજ <b>{g_names_gu.get(b_g, b_g)}</b> માટે <b>{g_names_gu.get(l_g, l_g)}</b> માંથી ચૂકવેલા <b>₹{rem_v:,.0f}</b> ({ig_rem}) — "
                        f"હવે <b>{g_names_gu.get(b_g, b_g)}</b> માં <b>₹{b_cash_now:,.0f}</b> કેશ આવી ગઈ છે! {settle_btn}</div>"
                    )
                else:
                    settle_btn = f"<span style='color:#b45309; font-weight:bold; font-size:11px;'>⏳ {g_names_gu.get(b_g, b_g)} માં કેશ આવવાની રાહ (હાલ ₹0)</span>"
                    cross_alert_items.append(
                        f"<div>⏳ તારીખ <b>{ig_dt}</b>: <b>{g_names_gu.get(l_g, l_g)}</b> માંથી <b>{g_names_gu.get(b_g, b_g)}</b> માટે ઉછીના ચૂકવેલા <b>₹{rem_v:,.0f}</b> ({ig_rem}) — જેવી {g_names_gu.get(b_g, b_g)} માં કેશ આવશે એટલે ઓટો-ટ્રીગર વાગશે!</div>"
                    )
                st_html = "<span style='background:#fef3c7; color:#b45309; padding:2px 6px; border-radius:4px; font-weight:bold;'>PENDING (બાકી)</span>"
            else:
                settle_btn = f"<span style='color:#15803d; font-weight:bold; font-size:11px;'>✅ સેટલ ({ig_sdt or '-'})</span>"
                st_html = "<span style='background:#dcfce7; color:#166534; padding:2px 6px; border-radius:4px; font-weight:bold;'>SETTLED (ચૂકતે)</span>"
            ig_table_trs += f"""<tr>
                <td>{ig_dt}</td>
                <td><b>{g_names_gu.get(l_g, l_g)}</b></td>
                <td><b>{g_names_gu.get(b_g, b_g)}</b> (હાલ કેશ: ₹{b_cash_now:,.0f})</td>
                <td style='font-weight:bold; color:#dc2626;'>₹{float(ig_amt or 0):,.0f}</td>
                <td style='font-weight:bold; color:#15803d;'>₹{float(ig_set or 0):,.0f}</td>
                <td>{st_html}</td>
                <td>{ig_rem or '-'}</td>
                <td>{settle_btn}</td>
            </tr>"""
        if not ig_table_trs:
            ig_table_trs = "<tr><td colspan='8'>હજુ કોઈ ક્રોસ-ગલ્લા ઉછીનો વ્યવહાર નોંધાયેલ નથી</td></tr>"
        cross_alert_html = ""
        if cross_alert_items:
            cross_alert_html = f"""
            <div style="background:#fef3c7; border:2px solid #d97706; color:#92400e; padding:10px 14px; margin:6px 8px; border-radius:6px; font-size:12px; font-weight:bold; line-height:1.7;">
                🔔 <b>સ્માર્ટ ક્રોસ-ગલ્લા ઉછીના પેમેન્ટ & ૫-દિવસ કેશ-ઇનફ્લો ઓટો-ટ્રીગર:</b><br>
                {"".join(cross_alert_items)}
            </div>"""

        return f"""
        
        <!-- [F6 TABS] આંતરિક ગલ્લા કેશ ટ્રાન્સફર vs બ્રાન્ચ સ્ટોક ટ્રાન્સફર (Stock Journal Alt+F7) -->
        <div style="display:flex; gap:10px; margin:8px 8px 4px 8px; border-bottom:2px solid #0284c7; padding-bottom:6px;">
            <button type="button" onclick="switchF6Tab('galla')" id="f6_tab_btn_galla" style="background:#0284c7; color:white; border:none; padding:8px 18px; border-radius:6px 6px 0 0; font-weight:bold; cursor:pointer; font-size:13px; box-shadow:0 2px 4px rgba(2,132,199,0.3);">🔄 [F6-1] આંતરિક ગલ્લા કેશ ટ્રાન્સફર (Cash Vault Transfer)</button>
            <button type="button" onclick="switchF6Tab('stock')" id="f6_tab_btn_stock" style="background:#e2e8f0; color:#1e293b; border:none; padding:8px 18px; border-radius:6px 6px 0 0; font-weight:bold; cursor:pointer; font-size:13px;">🏬 [F6-2] બ્રાન્ચ સ્ટોક ટ્રાન્સફર (Stock Journal - Alt+F7) 📱</button>
        </div>

        <script>
        function switchF6Tab(tab) {{
            var gDiv = document.getElementById('f6_galla_section');
            var sDiv = document.getElementById('f6_stock_section');
            var btnG = document.getElementById('f6_tab_btn_galla');
            var btnS = document.getElementById('f6_tab_btn_stock');
            if (tab === 'stock') {{
                if (gDiv) gDiv.style.display = 'none';
                if (sDiv) sDiv.style.display = 'block';
                if (btnG) {{ btnG.style.background = '#e2e8f0'; btnG.style.color = '#1e293b'; btnG.style.boxShadow = 'none'; }}
                if (btnS) {{ btnS.style.background = '#0284c7'; btnS.style.color = 'white'; btnS.style.boxShadow = '0 2px 4px rgba(2,132,199,0.3)'; }}
            }} else {{
                if (gDiv) gDiv.style.display = 'block';
                if (sDiv) sDiv.style.display = 'none';
                if (btnG) {{ btnG.style.background = '#0284c7'; btnG.style.color = 'white'; btnG.style.boxShadow = '0 2px 4px rgba(2,132,199,0.3)'; }}
                if (btnS) {{ btnS.style.background = '#e2e8f0'; btnS.style.color = '#1e293b'; btnS.style.boxShadow = 'none'; }}
            }}
        }}
        </script>

        <div id="f6_galla_section">
        <div class="mode-banner">
            <span>મોડ: [F6] આંતરિક ગલ્લા ટ્રાન્સફર ટેબલ (Vault-to-Vault Transfer - ૭ ખાનાં)</span>
            <span style="font-size:11.5px;">ઇમરજન્સીમાં એક ગલ્લામાંથી બીજા ગલ્લામાં લીધેલી રોકડ પાછી મૂળ ગલ્લામાં જમા કરવા માટે</span>
        </div>

        <!-- TALLY PRIME SUB-SECTIONS STRIP (F6 ૧ થી ૩ લાઈનબદ્ધ પેટા વિભાગો) -->
        <div class="tally-subparts-bar">
            <span style="color:#fde047; font-weight:800; font-size:11px; margin-right:4px;">પેટા વિભાગ:</span>
            <button type="button" class="tally-sub-btn active" id="f6_sub_btn_ALL" onclick="setSubpartF6('ALL')">૧. બંને બોક્સ સાથે જુઓ</button>
            <button type="button" class="tally-sub-btn" id="f6_sub_btn_INTRA" onclick="setSubpartF6('INTRA')">૨. આંતરિક ગલ્લા કેશ ટ્રાન્સફર</button>
            <button type="button" class="tally-sub-btn" id="f6_sub_btn_STOCK" onclick="setSubpartF6('STOCK')">૩. સ્ટોક ચલણ ટ્રાન્સફર</button>
        </div>
        <script>
        function setSubpartF6(val) {{
            document.querySelectorAll('.tally-subparts-bar .tally-sub-btn').forEach(function(b){{
                b.classList.remove('active');
            }});
            var curBtn = document.getElementById('f6_sub_btn_' + val);
            if (curBtn) curBtn.classList.add('active');
            var gSec = document.getElementById('f6_galla_section');
            var sSec = document.getElementById('f6_stock_section');
            if (val === 'INTRA') {{
                if (gSec) gSec.style.display = 'block';
                if (sSec) sSec.style.display = 'none';
            }} else if (val === 'STOCK') {{
                if (gSec) gSec.style.display = 'none';
                if (sSec) sSec.style.display = 'block';
            }} else {{
                if (gSec) gSec.style.display = 'block';
                if (sSec) sSec.style.display = 'block';
            }}
        }}
        </script>
        {cross_alert_html}

        <div style="display:grid; grid-template-columns:1fr 1fr; gap:12px; padding:8px;">
            <!-- ડાબું બોક્સ: ૭-ખાનાં આંતરિક ગલ્લા ટ્રાન્સફર ટેબલ -->
            <div style="background:#f0f9ff; border:2px solid #0284c7; border-radius:6px; padding:12px;">
                <h4 style="margin:0 0 10px 0; color:#0f2043;">🔄 [F6] આંતરિક ગલ્લા કેશ ટ્રાન્સફર (Vault-to-Vault Transfer - ૭ ખાનાં)</h4>
                <form class="term-form f-enter-form" action="/save-f7" method="post">
                    <div class="f-row"><div class="lbl">૧. ટ્રાન્ઝેક્શન તારીખ:</div><input type="date" name="tx_date" value="{today_str}"></div>
                    <div class="f-row"><div class="lbl">૨. કયા ગલ્લામાંથી રકમ ઉપાડી (-):</div><select name="from_galla" style="font-weight:bold; color:#dc2626;">{all_galla_options}<option value="BANK_CASH">1. BANK_CASH (ગલ્લો ૧)</option><option value="ACC_DCASH">2. ACC_DCASH (ગલ્લો ૨)</option><option value="RECHARGE">3. RECHARGE (ગલ્લો ૩)</option><option value="EXTRA_CASH">4. EXTRA_CASH (ગલ્લો ૪)</option></select></div>
                    <div class="f-row"><div class="lbl">૩. કયા સાચા ગલ્લામાં જમા થઈ (+):</div><select name="to_galla" style="font-weight:bold; color:#15803d;">{all_galla_options}<option value="BANK_CASH">1. BANK_CASH (ગલ્લો ૧)</option><option value="ACC_DCASH">2. ACC_DCASH (ગલ્લો ૨)</option><option value="RECHARGE">3. RECHARGE (ગલ્લો ૩)</option><option value="EXTRA_CASH">4. EXTRA_CASH (ગલ્લો ૪)</option></select></div>
                    <div class="f-row"><div class="lbl">૪. ટ્રાન્સફર રકમ (₹):</div><input type="number" step="any" name="amount" value="0" required style="font-weight:bold; color:#0284c7; font-size:14px;"></div>
                    <div class="f-row"><div class="lbl">૫. ટ્રાન્સફર કરનાર સ્ટાફ નામ:</div><select name="staff_name">{staff_opts_html}</select></div>
                    <div class="f-row"><div class="lbl">૬. કારણ / વિગતવાર નોંધ:</div><input type="text" name="remarks" placeholder="દા.ત. ગલ્લા ૧ માંથી લીધેલ રકમ પાછી જમા..."></div>
                    <div class="btn-wrap"><button type="submit" class="btn-save" style="background:#b45309;">૭. [ ટ્રાન્સફર સેવ કરો (Enter) ]</button></div>
                </form>
            </div>

            <!-- જમણું બોક્સ: તાજેતરના ગલ્લા ટ્રાન્સફર વ્યવહારો -->
            <div style="background:white; border:1px solid #cbd5e1; border-radius:6px; padding:12px;">
                <h4 style="margin:0 0 8px 0; color:#0f2043;">📋 તાજેતરના આંતરિક ગલ્લા ટ્રાન્સફર વ્યવહારો</h4>
                <table class="live-grid">
                    <tr><th>તારીખ</th><th>ગલ્લો</th><th>જમા (+)</th><th>ઉપાડ (-)</th><th>વિગત / સ્ટાફ</th></tr>
                    {tr_log_html}
                </table>
            </div>
        </div>
        <div style="padding:0 8px 10px 8px;">
            <div style="background:white; border:2px solid #d97706; border-radius:6px; padding:12px;">
                <h4 style="margin:0 0 8px 0; color:#92400e;">🤝 ક્રોસ-ગલ્લા ઉછીના લેણ-દેણ ખાતાવહી (Inter-Galla Borrowed Payment & Auto-Trigger Register)</h4>
                <table class="live-grid">
                    <tr>
                        <th>તારીખ</th><th>આપનાર ગલ્લો (Lender)</th><th>લેનાર ગલ્લો (Borrower)</th>
                        <th>ઉછીની રકમ ₹</th><th>પરત ચૂકવેલ ₹</th><th>સ્થિતિ</th><th>વિગત</th><th>૧-ક્લિક પરત સેટલમેન્ટ</th>
                    </tr>
                    {ig_table_trs}
                </table>
            </div>
        </div>

                
        </div>

        <!-- [F6-2 PANEL] બ્રાન્ચ સ્ટોક ટ્રાન્સફર પેનલ (Stock Journal Alt+F7) -->
        <div id="f6_stock_section" style="display:none; padding:8px;">
            <div style="background:#eff6ff; border:2px solid #2563eb; border-radius:8px; padding:14px; margin-bottom:12px;">
                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:10px;">
                    <div>
                        <h3 style="margin:0; color:#1e3a8a; display:flex; align-items:center; gap:8px;">
                            🏬 બ્રાન્ચ સ્ટોક ટ્રાન્સફર (Tally Prime Stock Journal - Alt+F7)
                        </h3>
                        <div style="font-size:12px; color:#475569; margin-top:3px;">
                            એક સ્ટોરમાંથી બીજા સ્ટોરમાં ૧૫-અંક IMEI હેન્ડસેટ ટ્રાન્સફર કરો — લાઈવ સ્ટોક આપોઆપ શિફ્ટ થશે અને પાકું ડિલિવરી ચલણ (DC) બનશે!
                        </div>
                    </div>
                    <span style="background:#1e3a8a; color:#fde047; padding:4px 10px; border-radius:4px; font-weight:bold; font-size:12px;">
                        Tally Alt+F7 Inter-Branch DC
                    </span>
                </div>

                <form action="/save-stock-transfer" method="post" id="stock_transfer_form" onsubmit="return validateStockTransferSubmit()">
                    <div style="display:grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap:10px; background:white; padding:12px; border-radius:6px; border:1px solid #bfdbfe; margin-bottom:12px;">
                        <div>
                            <label style="font-size:11px; font-weight:bold; color:#1e3a8a;">૧. કઈ દુકાનમાંથી સ્ટોક મોકલવો છે (From):</label>
                            <select name="from_store_id" id="st_from_store" style="width:100%; padding:7px; border:1.5px solid #2563eb; border-radius:4px; font-weight:bold; color:#1e3a8a;">
                                <option value="DEVANSHI" selected>દેવાંશી (DEVANSHI)</option>
                                <option value="MANSHVI">મનસ્વી (MANSHVI)</option>
                                <option value="STORE_3">દુકાન ૩ (BRANCH 3)</option>
                                <option value="MAIN_WAREHOUSE">મેઇન ગોડાઉન (WAREHOUSE)</option>
                            </select>
                        </div>
                        <div>
                            <label style="font-size:11px; font-weight:bold; color:#15803d;">૨. કઈ દુકાનમાં સ્ટોક પહોંચાડવો છે (To):</label>
                            <select name="to_store_id" id="st_to_store" style="width:100%; padding:7px; border:1.5px solid #16a34a; border-radius:4px; font-weight:bold; color:#15803d;">
                                <option value="MANSHVI" selected>મનસ્વી (MANSHVI)</option>
                                <option value="DEVANSHI">દેવાંશી (DEVANSHI)</option>
                                <option value="STORE_3">દુકાન ૩ (BRANCH 3)</option>
                                <option value="MAIN_WAREHOUSE">મેઇન ગોડાઉન (WAREHOUSE)</option>
                            </select>
                        </div>
                        <div>
                            <label style="font-size:11px; font-weight:bold; color:#475569;">૩. ડિલિવરી ચલણ / DC નંબર:</label>
                            <input type="text" name="challan_no" id="st_challan_no" value="DC-{today_str.replace('-','')}-{int(time.time())%1000:03d}" style="width:100%; padding:7px; border:1px solid #cbd5e1; border-radius:4px; font-weight:bold; color:#0f172a;" readonly>
                        </div>
                        <div>
                            <label style="font-size:11px; font-weight:bold; color:#475569;">૪. ટ્રાન્સફર તારીખ:</label>
                            <input type="date" name="transfer_date" value="{today_str}" style="width:100%; padding:7px; border:1px solid #cbd5e1; border-radius:4px; font-weight:bold;">
                        </div>
                        <div>
                            <label style="font-size:11px; font-weight:bold; color:#475569;">૫. માલ લઈ જનાર વ્યક્તિ (Carrier / Staff):</label>
                            <input type="text" name="carrier_name" id="st_carrier_name" placeholder="દા.ત. મુકેશભાઈ (સ્ટાફ) / ડિલિવરી બોય" style="width:100%; padding:7px; border:1px solid #cbd5e1; border-radius:4px;">
                        </div>
                        <div>
                            <label style="font-size:11px; font-weight:bold; color:#475569;">૬. ટ્રાન્સફર કારણ / Purpose:</label>
                            <select name="purpose" style="width:100%; padding:7px; border:1px solid #cbd5e1; border-radius:4px; font-weight:bold;">
                                <option value="દિવાળી / ફેસ્ટિવલ સ્ટોક ડિમાન્ડ">દિવાળી / ફેસ્ટિવલ સ્ટોક ડિમાન્ડ</option>
                                <option value="બ્રાન્ચ સ્ટોક બેલેન્સિંગ">બ્રાન્ચ સ્ટોક બેલેન્સિંગ</option>
                                <option value="કસ્ટમર સ્પેશિયલ ઓર્ડર">કસ્ટમર સ્પેશિયલ ઓર્ડર</option>
                                <option value="ગોડાઉન રી-લોકેશન">ગોડાઉન રી-લોકેશન</option>
                            </select>
                        </div>
                    </div>

                    <!-- હેન્ડસેટ સ્કેનિંગ અને મલ્ટીપલ લિસ્ટ -->
                    <div style="background:white; padding:12px; border-radius:6px; border:1.5px solid #0284c7; margin-bottom:12px;">
                        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
                            <span style="font-weight:bold; color:#0369a1; font-size:12.5px;">🔍 ૧૫-અંક IMEI સ્કેન કરો (Auto-Fetch Stock Details):</span>
                            <span style="font-size:11px; color:#64748b;">બારકોડ ગનથી સ્કેન કરતા જ બ્રાન્ડ, મોડેલ અને ખરીદ ભાવ આપોઆપ આવી જશે!</span>
                        </div>
                        <div style="display:flex; gap:8px; flex-wrap:wrap; align-items:flex-end;">
                            <div style="flex:2; min-width:170px;">
                                <label style="font-size:11px; font-weight:bold; color:#475569;">૧૫-અંક IMEI:</label>
                                <input type="text" id="st_scan_imei" maxlength="15" placeholder="૧૫-અંક IMEI સ્કેન / ટાઈપ કરો..." onblur="lookupStockTransferImei(this.value)" onkeydown="if(event.key==='Enter'){{event.preventDefault(); lookupStockTransferImei(this.value);}}" style="width:100%; padding:7px; border:1.5px solid #0284c7; border-radius:4px; font-weight:bold; font-family:monospace; font-size:13px;">
                            </div>
                            <div style="flex:1; min-width:120px;">
                                <label style="font-size:11px; font-weight:bold; color:#475569;">બ્રાન્ડ:</label>
                                <input type="text" id="st_scan_brand" placeholder="બ્રાન્ડ..." style="width:100%; padding:7px; border:1px solid #cbd5e1; border-radius:4px; font-weight:bold;">
                            </div>
                            <div style="flex:2; min-width:180px;">
                                <label style="font-size:11px; font-weight:bold; color:#475569;">મોડેલ નામ:</label>
                                <input type="text" id="st_scan_model" placeholder="મોડેલ..." style="width:100%; padding:7px; border:1px solid #cbd5e1; border-radius:4px;">
                            </div>
                            <div style="flex:1; min-width:100px;">
                                <label style="font-size:11px; font-weight:bold; color:#475569;">ખરીદ DP (₹):</label>
                                <input type="number" id="st_scan_dp" value="0" style="width:100%; padding:7px; border:1px solid #cbd5e1; border-radius:4px; font-weight:bold; color:#0284c7;">
                            </div>
                            <div style="flex:1; min-width:100px;">
                                <label style="font-size:11px; font-weight:bold; color:#475569;">MOP વેચાણ (₹):</label>
                                <input type="number" id="st_scan_mop" value="0" style="width:100%; padding:7px; border:1px solid #cbd5e1; border-radius:4px; font-weight:bold; color:#15803d;">
                            </div>
                            <button type="button" onclick="addStockTransferItem()" style="background:#0284c7; color:white; border:none; padding:8px 16px; border-radius:4px; font-weight:bold; cursor:pointer; font-size:13px; display:inline-flex; align-items:center; gap:5px;">
                                ➕ લિસ્ટમાં ઉમેરો
                            </button>
                        </div>
                    </div>

                    <!-- ટ્રાન્સફર આઇટમ્સ ટેબલ -->
                    <div id="st_items_wrap" style="background:white; border:1px solid #cbd5e1; border-radius:6px; overflow:hidden; margin-bottom:12px; display:none;">
                        <table style="width:100%; border-collapse:collapse; font-size:12.5px;">
                            <thead>
                                <tr style="background:#1e3a8a; color:white;">
                                    <th style="padding:7px; border:1px solid #1e3a8a;">#</th>
                                    <th style="padding:7px; border:1px solid #1e3a8a;">૧૫-અંક IMEI</th>
                                    <th style="padding:7px; border:1px solid #1e3a8a;">બ્રાન્ડ</th>
                                    <th style="padding:7px; border:1px solid #1e3a8a;">મોડેલ</th>
                                    <th style="padding:7px; border:1px solid #1e3a8a; text-align:right;">ખરીદ પડતર (DP ₹)</th>
                                    <th style="padding:7px; border:1px solid #1e3a8a; text-align:right;">MOP ભાવ (₹)</th>
                                    <th style="padding:7px; border:1px solid #1e3a8a; text-align:center;">એકશન</th>
                                </tr>
                            </thead>
                            <tbody id="st_items_tbody"></tbody>
                            <tfoot>
                                <tr style="background:#f8fafc; font-weight:bold; font-size:13px;">
                                    <td colspan="4" style="padding:8px; text-align:right;">કુલ ટ્રાન્સફર હેન્ડસેટ: <span id="st_total_qty" style="color:#2563eb; font-size:14px;">0</span> ફોન</td>
                                    <td style="padding:8px; text-align:right; color:#0284c7; font-size:14px;">₹<span id="st_total_dp">0</span></td>
                                    <td style="padding:8px; text-align:right; color:#15803d; font-size:14px;">₹<span id="st_total_mop">0</span></td>
                                    <td></td>
                                </tr>
                            </tfoot>
                        </table>
                    </div>

                    <input type="hidden" name="items_json" id="st_items_json" value="">

                    <div style="display:flex; justify-content:space-between; align-items:center; background:white; padding:12px; border-radius:6px; border:1px solid #cbd5e1;">
                        <span style="font-size:12px; color:#64748b;">
                            🔒 અધિકૃતતા: <b>PIN 1986</b> (જયમીનભાઈ પટેલ - સુપર એડમિન)
                        </span>
                        <button type="submit" style="background:linear-gradient(135deg, #16a34a, #15803d); color:white; border:none; padding:10px 24px; border-radius:6px; font-weight:900; font-size:14px; cursor:pointer; box-shadow:0 3px 6px rgba(22,163,74,0.3); display:inline-flex; align-items:center; gap:8px;">
                            🚀 સ્ટોક ટ્રાન્સફર સેવ કરો & પાકું ડિલિવરી ચલણ (DC) બનાવો (Enter)
                        </button>
                    </div>
                </form>
            </div>

            <!-- તાજેતરના સ્ટોક ટ્રાન્સફર વ્યવહારો હિસ્ટ્રી -->
            <div style="background:white; border:1px solid #cbd5e1; border-radius:8px; padding:12px;">
                <h4 style="margin:0 0 10px 0; color:#1e3a8a; display:flex; align-items:center; gap:6px;">
                    📋 તાજેતરના બ્રાન્ચ સ્ટોક ટ્રાન્સફર ડિલિવરી ચલણ હિસ્ટ્રી (Stock Transfer History)
                </h4>
                <table class="live-grid" style="width:100%; border-collapse:collapse; font-size:12px;">
                    <thead>
                        <tr style="background:#f1f5f9;">
                            <th>ચલણ નં (DC No.)</th>
                            <th>તારીખ</th>
                            <th>મોકલનાર ➔ મેળવનાર</th>
                            <th>કુલ હેન્ડસેટ</th>
                            <th>કુલ સ્ટોક પડતર ₹</th>
                            <th>લઈ જનાર સ્ટાફ</th>
                            <th>સ્થિતિ</th>
                            <th>ચલણ પ્રિન્ટ</th>
                        </tr>
                    </thead>
                    <tbody>
                        {st_history_trs}
                    </tbody>
                </table>
            </div>
        </div>

        <script>
        var stTransferItems = [];

        function lookupStockTransferImei(imei) {{
            imei = (imei || '').trim();
            if (!imei || imei.length < 8) return;
            var fromStore = document.getElementById('st_from_store') ? document.getElementById('st_from_store').value : 'DEVANSHI';
            fetch('/api/lookup-stock-imei?imei=' + encodeURIComponent(imei) + '&from_store=' + encodeURIComponent(fromStore))
                .then(function(res) {{ return res.json(); }})
                .then(function(data) {{
                    if (data && data.found) {{
                        if (document.getElementById('st_scan_brand')) document.getElementById('st_scan_brand').value = data.brand || '';
                        if (document.getElementById('st_scan_model')) document.getElementById('st_scan_model').value = data.model || '';
                        if (document.getElementById('st_scan_dp')) document.getElementById('st_scan_dp').value = data.dp || 0;
                        if (document.getElementById('st_scan_mop')) document.getElementById('st_scan_mop').value = data.mop || data.dp || 0;
                    }}
                }})
                .catch(function(err) {{}});
        }}

        function addStockTransferItem() {{
            var imei = document.getElementById('st_scan_imei') ? document.getElementById('st_scan_imei').value.trim() : '';
            var brand = document.getElementById('st_scan_brand') ? document.getElementById('st_scan_brand').value.trim() : 'Phone';
            var model = document.getElementById('st_scan_model') ? document.getElementById('st_scan_model').value.trim() : '';
            var dp = parseFloat(document.getElementById('st_scan_dp') ? document.getElementById('st_scan_dp').value : 0) || 0;
            var mop = parseFloat(document.getElementById('st_scan_mop') ? document.getElementById('st_scan_mop').value : 0) || dp;

            if (!imei || imei.length < 8) {{
                alert("કૃપા કરીને સાચો IMEI નંબર સ્કેન કરો!");
                return;
            }}
            for (var i = 0; i < stTransferItems.length; i++) {{
                if (stTransferItems[i].imei === imei) {{
                    alert("આ IMEI પહેલેથી જ ટ્રાન્સફર લિસ્ટમાં છે!");
                    return;
                }}
            }}
            stTransferItems.push({{
                imei: imei,
                brand: brand,
                model: model,
                dp: dp,
                mop: mop
            }});

            if (document.getElementById('st_scan_imei')) {{
                document.getElementById('st_scan_imei').value = '';
                document.getElementById('st_scan_imei').focus();
            }}
            renderStockTransferItems();
        }}

        function removeStockTransferItem(idx) {{
            stTransferItems.splice(idx, 1);
            renderStockTransferItems();
        }}

        function renderStockTransferItems() {{
            var wrap = document.getElementById('st_items_wrap');
            var tbody = document.getElementById('st_items_tbody');
            var qtyEl = document.getElementById('st_total_qty');
            var dpEl = document.getElementById('st_total_dp');
            var mopEl = document.getElementById('st_total_mop');
            var hiddenInp = document.getElementById('st_items_json');

            if (!wrap || !tbody) return;

            if (stTransferItems.length === 0) {{
                wrap.style.display = 'none';
                if (hiddenInp) hiddenInp.value = '';
                return;
            }}

            wrap.style.display = 'block';
            var totalDp = 0;
            var totalMop = 0;
            var trs = '';
            for (var i = 0; i < stTransferItems.length; i++) {{
                var itm = stTransferItems[i];
                totalDp += itm.dp;
                totalMop += itm.mop;
                trs += '<tr>' +
                    '<td style="padding:6px; border:1px solid #cbd5e1; text-align:center;">' + (i + 1) + '</td>' +
                    '<td style="padding:6px; border:1px solid #cbd5e1; font-family:monospace; font-weight:bold; color:#1e3a8a;">' + itm.imei + '</td>' +
                    '<td style="padding:6px; border:1px solid #cbd5e1;"><b>' + itm.brand + '</b></td>' +
                    '<td style="padding:6px; border:1px solid #cbd5e1;">' + itm.model + '</td>' +
                    '<td style="padding:6px; border:1px solid #cbd5e1; text-align:right; font-weight:bold; color:#0284c7;">₹' + itm.dp.toLocaleString() + '</td>' +
                    '<td style="padding:6px; border:1px solid #cbd5e1; text-align:right; font-weight:bold; color:#15803d;">₹' + itm.mop.toLocaleString() + '</td>' +
                    '<td style="padding:6px; border:1px solid #cbd5e1; text-align:center;"><button type="button" onclick="removeStockTransferItem(' + i + ')" style="background:#dc2626; color:white; border:none; padding:2px 7px; border-radius:3px; cursor:pointer;">✖</button></td>' +
                    '</tr>';
            }}
            tbody.innerHTML = trs;
            if (qtyEl) qtyEl.innerText = stTransferItems.length;
            if (dpEl) dpEl.innerText = totalDp.toLocaleString();
            if (mopEl) mopEl.innerText = totalMop.toLocaleString();
            if (hiddenInp) hiddenInp.value = JSON.stringify(stTransferItems);
        }}

        function validateStockTransferSubmit() {{
            var fromS = document.getElementById('st_from_store').value;
            var toS = document.getElementById('st_to_store').value;
            if (fromS === toS) {{
                alert("મોકલનાર સ્ટોર અને મેળવનાર સ્ટોર અલગ હોવા જોઈએ!");
                return false;
            }}
            if (stTransferItems.length === 0) {{
                alert("કૃપા કરીને ઓછામાં ઓછો એક ફોન/IMEI ટ્રાન્સફર લિસ્ટમાં ઉમેરો!");
                return false;
            }}
            return true;
        }}
        </script>

        """

    # =========================================================================
    # [F7] ડાયરેક્ટ એક્સ્ટ્રા પ્રોફિટ સેટઅપ + બારોબાર ગ્રાહક રિપેરિંગ અને કારીગર પ્રોફિટ સ્પ્લિટ બોક્સ
    # =========================================================================
    elif mode == "F7":
        c.execute("""SELECT entry_date, entry_time, profit_type, ref_bill_customer, net_profit_amt, galla_name, salesman, staff_comm_amt, remarks
                     FROM direct_extra_profit_log ORDER BY id DESC LIMIT 10""")
        ep_rows = c.fetchall()
        ep_trs = "".join([
            f"<tr><td>{r[0]} {r[1] or ''}</td><td><b>{r[2]}</b></td><td>{r[3] or '-'}</td><td style='color:#15803d; font-weight:bold;'>₹{float(r[4] or 0):,.0f}</td><td>{r[5]}</td><td>{r[6] or '-'} (કમિશન: ₹{float(r[7] or 0):,.0f})</td><td>{r[8] or '-'}</td></tr>"
            for r in ep_rows
        ]) or "<tr><td colspan='7'>હજુ કોઈ ડાયરેક્ટ એક્સ્ટ્રા પ્રોફિટ એન્ટ્રી નોંધાયેલ નથી</td></tr>"

        c.execute("""SELECT entry_date, customer_name, model_and_issue, technician_name,
                            spare_part_cost, customer_charge, net_repair_profit, tech_share_pct, tech_share_amt, owner_share_amt
                     FROM out_of_store_repair_log ORDER BY id DESC LIMIT 10""")
        rep_rows = c.fetchall()
        rep_trs = ""
        for rx in rep_rows:
            rep_trs += f"""
            <tr>
                <td>{rx[0]}</td><td><b>{rx[1]}</b></td><td>{rx[2]}</td><td>{rx[3] or '-'}</td>
                <td style='color:#dc2626;'>₹{float(rx[4] or 0):,.0f}</td>
                <td style='color:#15803d; font-weight:bold;'>₹{float(rx[5] or 0):,.0f}</td>
                <td style='font-weight:bold;'>₹{float(rx[6] or 0):,.0f}</td>
                <td style='color:#0369a1;'>₹{float(rx[8] or 0):,.0f} ({rx[7]:.0f}%)</td>
                <td style='color:#15803d; font-weight:bold;'>₹{float(rx[9] or 0):,.0f}</td>
            </tr>"""
        if not rep_trs:
            rep_trs = "<tr><td colspan='9'>હજુ કોઈ રિપેરિંગ વ્યવહાર નોંધાયેલ નથી</td></tr>"

        galla_f7_prof = build_4galla_sel_c("galla_name", "EXTRA_CASH")

        return f"""
        <div class="mode-banner">
            <span>મોડ: [F7] ડાયરેક્ટ એક્સ્ટ્રા પ્રોફિટ સેટઅપ (ગલ્લો ૪) + બારોબાર ગ્રાહક રિપેરિંગ અને કારીગર પ્રોફિટ સ્પ્લિટ બોક્સ</span>
            <span style="font-size:11.5px;">ડાબું બોક્સ: ડાયરેક્ટ એક્સ્ટ્રા પ્રોફિટ | જમણું બોક્સ: ગ્રાહક રિપેરિંગ & કારીગર નફા વહેંચણી</span>
        </div>

        <!-- TALLY PRIME SUB-SECTIONS STRIP (F7 ૧ થી ૩ લાઈનબદ્ધ પેટા વિભાગો) -->
        <div class="tally-subparts-bar">
            <span style="color:#fde047; font-weight:800; font-size:11px; margin-right:4px;">પેટા વિભાગ:</span>
            <button type="button" class="tally-sub-btn active" id="f7_sub_btn_ALL" onclick="setSubpartF7('ALL')">૧. બંને બોક્સ સાથે જુઓ (Side-by-Side)</button>
            <button type="button" class="tally-sub-btn" id="f7_sub_btn_PROFIT" onclick="setSubpartF7('PROFIT')">૨. ડાયરેક્ટ એક્સ્ટ્રા પ્રોફિટ (ગલ્લો ૪ & P&L - Full Width)</button>
            <button type="button" class="tally-sub-btn" id="f7_sub_btn_REPAIR" onclick="setSubpartF7('REPAIR')">૩. ગ્રાહક રિપેરિંગ & કારીગર સ્પ્લિટ (Full Width)</button>
        </div>
        <script>
        function setSubpartF7(val) {{
            document.querySelectorAll('.tally-subparts-bar .tally-sub-btn').forEach(function(b){{
                b.classList.remove('active');
            }});
            var curBtn = document.getElementById('f7_sub_btn_' + val);
            if (curBtn) curBtn.classList.add('active');
            var gGrid = document.getElementById('f7_boxes_grid');
            var bProfit = document.getElementById('f7_box_profit');
            var bRepair = document.getElementById('f7_box_repair');
            if (!gGrid || !bProfit || !bRepair) return;
            if (val === 'PROFIT') {{
                bProfit.style.display = 'block';
                bRepair.style.display = 'none';
                gGrid.style.gridTemplateColumns = '1fr';
            }} else if (val === 'REPAIR') {{
                bProfit.style.display = 'none';
                bRepair.style.display = 'block';
                gGrid.style.gridTemplateColumns = '1fr';
            }} else {{
                bProfit.style.display = 'block';
                bRepair.style.display = 'block';
                gGrid.style.gridTemplateColumns = '1fr 1fr';
            }}
        }}
        </script>

        <div id="f7_boxes_grid" style="display:grid; grid-template-columns:1fr 1fr; gap:12px; padding:8px;">
            <!-- ડાબું બોક્સ (Box 1): [F7] ડાયરેક્ટ એક્સ્ટ્રા પ્રોફિટ સેટઅપ -->
            <div id="f7_box_profit" style="display:{'block' if 'F7_1' in active_subparts else 'none'}; background:#fffbeb; border:2px solid #b45309; border-radius:6px; padding:12px;">
                <h4 style="margin:0 0 10px 0; color:#b45309;">💎 ૧. [F7] ડાયરેક્ટ એક્સ્ટ્રા પ્રોફિટ સેટઅપ (સીધો ગલ્લા ૪ અને P&L માં જમા)</h4>
                <form class="term-form f-enter-form" action="/save-f7-extra-profit" method="post">
                    <div class="f-row"><div class="lbl" style="width:190px;">૧. તારીખ:</div><input type="date" name="entry_date" value="{today_str}"></div>
                    <div class="f-row"><div class="lbl" style="width:190px;">૨. એક્સ્ટ્રા પ્રોફિટ પ્રકાર:</div>
                        <select name="profit_type" style="font-weight:bold; color:#0f2043;">
                            <option value="FINANCE_EXTRA_DP">૧. ફાઇનાન્સ Extra DP (ઉપરનો નફો)</option>
                            <option value="BUYBACK_MARGIN">૨. બાય-બેક ડાયરેક્ટ માર્જિન નફો</option>
                            <option value="CC_CASHBACK">૩. ક્રેડિટ કાર્ડ (CC) કેશબેક નફો</option>
                            <option value="DEMO_PHONE_PROFIT">૪. ડેમો ફોન / સ્કીમ વેચાણ નફો</option>
                            <option value="OTHER_EXTRA_PROFIT">૫. અન્ય વધારાની આવક / નફો</option>
                        </select>
                    </div>
                    <div class="f-row"><div class="lbl" style="width:190px;">૩. સંદર્ભ બિલ / ગ્રાહક નામ:</div><input type="text" name="ref_bill_customer" placeholder="બિલ નંબર અથવા ગ્રાહકનું નામ..."></div>
                    <div class="f-row"><div class="lbl" style="width:190px;">૪. ચોખ્ખો નફો રકમ (₹):</div><input type="number" step="any" name="net_profit_amt" value="0" required style="font-weight:800; color:#15803d; font-size:14px;"></div>
                    <div class="f-row"><div class="lbl" style="width:190px;">૫. પ્રાપ્તિ પદ્ધતિ (MOP) & ગલ્લો:</div><select name="pay_mode" id="f7_b1_mop" onchange="syncF7MopGalla(this, 'f7_b1_galla')" style="max-width:145px; font-weight:bold;"><option value="રોકડ (Cash)">💵 ૧. રોકડ (Cash)</option><option value="ઓનલાઇન UPI / QR">📱 ૨. ઓનલાઇન UPI / QR</option><option value="કાર્ડ સ્વાઇપ">💳 ૩. કાર્ડ સ્વાઇપ</option><option value="નેટ બેંકિંગ / NEFT">🏦 ૪. NEFT / બેંક</option></select><select name="galla_name" id="f7_b1_galla" style="font-weight:bold; color:#0f2043; flex:1;"><option value="EXTRA_CASH" selected>૪. એક્સ્ટ્રા કેશ (ગલ્લો ૪)</option><option value="BANK_CASH">૧. બેંક કેશ (ગલ્લો ૧)</option><option value="ACC_DCASH">૨. એક્સેસરીઝ કેશ (ગલ્લો ૨)</option><option value="RECHARGE">૩. રિચાર્જ કેશ (ગલ્લો ૩)</option></select></div>
                    <div class="f-row"><div class="lbl" style="width:190px;">૬. સેલ્સમેન & કમિશન (₹):</div>
                        <select name="salesman" style="flex:1;">{staff_opts_html}</select>
                        <input type="number" step="any" name="staff_comm_amt" value="0" placeholder="સ્ટાફ કમિશન ₹" style="max-width:120px;">
                    </div>
                    <div class="f-row"><div class="lbl" style="width:190px;">૭. વિગત / નોંધ:</div><input type="text" name="remarks" placeholder="નફાની વિગતવાર નોંધ..."></div>
                    <button type="submit" style="width:100%; background:#b45309; color:white; border:none; padding:9px; border-radius:4px; font-weight:800; margin-top:6px; cursor:pointer;">૮. [ એક્સ્ટ્રા પ્રોફિટ સેવ કરો (ગલ્લો ૪ & P&L માં જમા) ]</button>
                </form>
            </div>

            <!-- જમણું બોક્સ (Box 2): 🛠️ બારોબાર ગ્રાહક રિપેરિંગ અને કારીગર પ્રોફિટ સ્પ્લિટ (૧૧ ખાનાં) -->
            <div id="f7_box_repair" style="display:{'block' if ('F7_2' in active_subparts or 'F7_3' in active_subparts) else 'none'}; background:#f0fdf4; border:2px solid #16a34a; border-radius:6px; padding:12px;">
                <h4 style="margin:0 0 8px 0; color:#166534;">🛠️ ૨. બારોબાર ગ્રાહક રિપેરિંગ & કારીગર પ્રોફિટ સ્પ્લિટ બોક્સ</h4>
                
                <div style="background:#fefce8; border:1px solid #fde047; padding:6px 10px; border-radius:4px; margin-bottom:10px;">
                    <div style="font-size:11px; font-weight:bold; color:#854d0e; margin-bottom:2px;">રિપેરિંગ મોડ પસંદ કરો (ડિફોલ્ટ વિકલ્પ ૧ - ૬ ખાનાં):</div>
                    <select id="f7_rep_submode" onchange="toggleF7RepairSubmode(this.value)" style="width:100%; padding:6px; font-weight:bold; color:#0f2043; border-radius:4px; border:1px solid #ca8a04;">
                        <option value="SIMPLE" selected>🛠️ વિકલ્પ (૧): સામાન્ય ગ્રાહક રિપેરિંગ એન્ટ્રી (Customer Repair Entry - ફક્ત ૬ ખાનાં)</option>
                        <option value="SPLIT">💰 વિકલ્પ (૨): સંપૂર્ણ કારીગર & દુકાનદાર નફા વહેંચણી હિસાબ (Technician Profit Share & Split - ૧૧ ખાનાં)</option>
                    </select>
                </div>

                <!-- વિકલ્પ (૧) ડિફોલ્ટ: સામાન્ય ગ્રાહક રિપેરિંગ એન્ટ્રી (૬ ખાનાં + MOP + ૪-ગલ્લા) -->
                <div id="f7_rep_simple_wrap" style="display:block;">
                    <form class="f-enter-form" action="/save-f7-simple-repair" method="post">
                        <div class="f-row"><div class="lbl" style="width:190px;">૧. તારીખ:</div><input type="date" name="entry_date" value="{today_str}"></div>
                        <div class="f-row"><div class="lbl" style="width:190px;">૨. ગ્રાહક નામ & મોબાઈલ:</div>
                            <input type="text" name="customer_name" placeholder="ગ્રાહકનું નામ" required style="flex:1;">
                            <input type="text" name="customer_phone" maxlength="10" placeholder="૧૦-અંક મોબાઈલ" style="max-width:130px;">
                        </div>
                        <div class="f-row"><div class="lbl" style="width:190px;">૩. મોડેલ & ખામી/વિગત:</div>
                            <input type="text" name="model_and_issue" placeholder="દા.ત. Vivo Y20 ડિસ્પ્લે..." required>
                        </div>
                        <div class="f-row"><div class="lbl" style="width:190px;">૪. કારીગર / ટેકનિશિયન:</div>
                            <select name="technician_name" style="flex:1;">{staff_opts_html}</select>
                        </div>
                        <div class="f-row"><div class="lbl" style="width:190px;">૫. સ્પેરપાર્ટ ખરીદ પડતર (₹):</div>
                            <input type="number" step="any" name="spare_part_cost" value="0" style="max-width:85px; font-weight:bold; color:#dc2626;">
                            <select name="part_pay_mode" id="f7_sp_pmode" onchange="syncF7MopGalla(this, 'f7_sp_pgalla')" style="max-width:130px; font-weight:bold;">
                                <option value="રોકડ (Cash)">💵 રોકડ (Cash)</option>
                                <option value="ઓનલાઈન UPI / QR">📱 ઓનલાઈન UPI</option>
                                <option value="કાર્ડ સ્વાઇપ (Card Swipe)">💳 કાર્ડ સ્વાઇપ</option>
                                <option value="નેટ બેંકિંગ (NEFT/RTGS)">🏦 NEFT / બેંક</option>
                            </select>
                            <select name="part_paid_galla" id="f7_sp_pgalla" style="font-weight:bold; color:#0f2043; flex:1;">
                                <option value="BANK_CASH">૧. બેંક કેશ (ગલ્લો ૧)</option>
                                <option value="ACC_DCASH">૨. એક્સેસરીઝ D-Cash (ગલ્લો ૨)</option>
                                <option value="RECHARGE">૩. રિચાર્જ કેશ (ગલ્લો ૩)</option>
                                <option value="EXTRA_CASH">૪. એક્સ્ટ્રા કેશ (ગલ્લો ૪)</option>
                            </select>
                        </div>
                        <div class="f-row"><div class="lbl" style="width:190px;">૬. ગ્રાહક પાસેથી લીધા (₹):</div>
                            <input type="number" step="any" name="customer_charge" value="0" required style="max-width:95px; font-weight:bold; color:#15803d;">
                            <select name="rec_pay_mode" id="f7_sp_rmode" onchange="syncF7MopGalla(this, 'f7_sp_rgalla')" style="max-width:130px; font-weight:bold;">
                                <option value="રોકડ (Cash)">💵 રોકડ (Cash)</option>
                                <option value="ઓનલાઈન UPI / QR">📱 ઓનલાઈન UPI</option>
                                <option value="કાર્ડ સ્વાઇપ">💳 કાર્ડ સ્વાઇપ</option>
                                <option value="નેટ બેંકિંગ / NEFT">🏦 NEFT / બેંક</option>
                            </select>
                            <select name="received_galla" id="f7_sp_rgalla" style="font-weight:bold; color:#15803d; flex:1;">
                                <option value="EXTRA_CASH" selected>૪. એક્સ્ટ્રા કેશ (ગલ્લો ૪)</option>
                                <option value="BANK_CASH">૧. બેંક કેશ (ગલ્લો ૧)</option>
                                <option value="ACC_DCASH">૨. એક્સેસરીઝ (ગલ્લો ૨)</option>
                                <option value="RECHARGE">૩. રિચાર્જ (ગલ્લો ૩)</option>
                            </select>
                        </div>
                        <button type="submit" style="width:100%; background:#15803d; color:white; border:none; padding:9px; border-radius:4px; font-weight:800; margin-top:8px; cursor:pointer;">[ સાચવો ગ્રાહક રિપેરિંગ એન્ટ્રી (Enter) ]</button>
                    </form>
                </div>

                <!-- વિકલ્પ (૨): કારીગર & દુકાનદાર નફા વહેંચણી હિસાબ (૧૧ ખાનાં) -->
                <div id="f7_rep_split_wrap" style="display:none;">
                    <form class="f-enter-form" action="/save-f7-out-repair-split" method="post">
                        <div class="f-row"><div class="lbl" style="width:190px;">૧. તારીખ & સમય [ઓટો]:</div>
                            <input type="date" name="entry_date" value="{today_str}" style="max-width:140px;">
                        </div>
                        <div class="f-row"><div class="lbl" style="width:190px;">૨. ગ્રાહક નામ & મોબાઈલ:</div>
                            <input type="text" name="customer_name" placeholder="ગ્રાહક નામ" required style="flex:1;">
                            <input type="text" name="customer_phone" maxlength="10" placeholder="૧૦-અંક મોબાઈલ" style="max-width:130px;">
                        </div>
                        <div class="f-row"><div class="lbl" style="width:190px;">૩. મોડેલ & રિપેરિંગ વિગત:</div>
                            <input type="text" name="model_and_issue" placeholder="મોડેલ & વિગત..." required>
                        </div>
                        <div class="f-row"><div class="lbl" style="width:190px;">૪. કારીગર / ટેકનિશિયન:</div>
                            <select name="technician_name" style="flex:1;">{staff_opts_html}</select>
                        </div>
                        <div class="f-row"><div class="lbl" style="width:190px;">૫. સ્પેરપાર્ટ ખર્ચ (₹) & ગલ્લો:</div>
                            <input type="number" step="any" name="spare_part_cost" id="f7_rep_cost" value="0" oninput="calcF7RepairSplit()" required style="max-width:85px; font-weight:bold; color:#dc2626;">
                            <select name="part_pay_mode" id="f7_spl_pmode" onchange="syncF7MopGalla(this, 'f7_spl_pgalla')" style="max-width:130px; font-weight:bold;">
                                <option value="રોકડ (Cash)">💵 રોકડ (Cash)</option>
                                <option value="ઓનલાઈન UPI / QR">📱 UPI</option>
                                <option value="કાર્ડ સ્વાઇપ (Card Swipe)">💳 કાર્ડ સ્વાઇપ</option>
                                <option value="નેટ બેંકિંગ (NEFT/RTGS)">🏦 NEFT</option>
                            </select>
                            <select name="part_paid_galla" id="f7_spl_pgalla" style="font-weight:bold; flex:1;">
                                <option value="BANK_CASH">૧. બેંક કેશ (ગલ્લો ૧)</option>
                                <option value="ACC_DCASH">૨. D-Cash (ગલ્લો ૨)</option>
                                <option value="RECHARGE">૩. રિચાર્જ (ગલ્લો ૩)</option>
                                <option value="EXTRA_CASH">૪. એક્સ્ટ્રા કેશ (ગલ્લો ૪)</option>
                            </select>
                        </div>
                        <div class="f-row"><div class="lbl" style="width:190px;">૬. ગ્રાહક ચાર્જ (₹):</div>
                            <input type="number" step="any" name="customer_charge" id="f7_rep_charge" value="0" oninput="calcF7RepairSplit()" required style="font-weight:bold; color:#0284c7;">
                        </div>
                        <div class="f-row" style="background:#fef9c3; padding:3px; border-radius:4px;">
                            <div class="lbl" style="width:190px; color:#854d0e;">૭. ચોખ્ખો રિપેરિંગ નફો [Auto]:</div>
                            <input type="number" step="any" name="net_repair_profit" id="f7_rep_net" value="0" readonly style="font-weight:800; color:#854d0e;">
                        </div>
                        <div class="f-row"><div class="lbl" style="width:190px;">૮. કારીગર ભાગ (% અને ₹):</div>
                            <input type="number" step="any" name="tech_share_pct" id="f7_tech_pct" value="50" oninput="calcF7RepairSplit()" style="max-width:70px; font-weight:bold;">
                            <input type="number" step="any" name="tech_share_amt" id="f7_tech_amt" value="0" readonly style="flex:1; font-weight:bold; color:#0369a1; background:#e0f2fe;">
                        </div>
                        <div class="f-row" style="background:#dcfce7; padding:3px; border-radius:4px;">
                            <div class="lbl" style="width:190px; color:#15803d;">૯. દુકાનદાર ચોખ્ખો નફો (₹):</div>
                            <input type="number" step="any" name="owner_share_amt" id="f7_owner_amt" value="0" readonly style="font-weight:800; color:#15803d; font-size:13.5px;">
                        </div>
                        <div class="f-row"><div class="lbl" style="width:190px;">૧૦. પ્રાપ્તિ પદ્ધતિ (MOP) & જમા ગલ્લો:</div>
                            <select name="pay_mode" id="f7_spl_rmode" onchange="syncF7MopGalla(this, 'f7_spl_rgalla')" style="max-width:130px; font-weight:bold;">
                                <option value="રોકડ (Cash)">💵 રોકડ (Cash)</option>
                                <option value="ઓનલાઈન UPI">📱 ઓનલાઈન UPI</option>
                                <option value="કાર્ડ સ્વાઇપ">💳 કાર્ડ સ્વાઇપ</option>
                                <option value="નેટ બેંકિંગ / NEFT">🏦 NEFT / બેંક</option>
                            </select>
                            <select name="profit_galla" id="f7_spl_rgalla" style="font-weight:bold; color:#b45309; flex:1;">
                                <option value="EXTRA_CASH" selected>૪. તિજોરી / એક્સ્ટ્રા કેશ (ગલ્લો ૪)</option>
                                <option value="BANK_CASH">૧. બેંક કેશ (ગલ્લો ૧)</option>
                                <option value="ACC_DCASH">૨. એક્સેસરીઝ (ગલ્લો ૨)</option>
                                <option value="RECHARGE">૩. રિચાર્જ (ગલ્લો ૩)</option>
                            </select>
                        </div>
                        <button type="submit" style="width:100%; background:#16a34a; color:white; border:none; padding:9px; border-radius:4px; font-weight:800; margin-top:6px; cursor:pointer;">૧૧. [ નફા વહેંચણી સેવ કરો (દુકાનદાર નફો -> ગલ્લો ૪ & કારીગર ભાગ -> સ્ટાફ) ]</button>
                    </form>
                </div>
            </div>
        </div>

        <div style="display:grid; grid-template-columns:1fr 1fr; gap:12px; padding:0 8px 8px;">
            <div style="background:white; border:1px solid #cbd5e1; border-radius:6px; padding:10px;">
                <h4 style="margin:0 0 6px 0; color:#b45309;">💎 તાજેતરના ડાયરેક્ટ એક્સ્ટ્રા પ્રોફિટ વ્યવહારો:</h4>
                <table class="live-grid">
                    <tr><th>તારીખ</th><th>પ્રકાર</th><th>સંદર્ભ/ગ્રાહક</th><th>નફો (₹)</th><th>ગલ્લો</th><th>સેલ્સમેન</th><th>નોંધ</th></tr>
                    {ep_trs}
                </table>
            </div>
            <div style="background:white; border:1px solid #cbd5e1; border-radius:6px; padding:10px;">
                <h4 style="margin:0 0 6px 0; color:#166534;">🛠️ તાજેતરના રિપેરિંગ અને કારીગર સ્પ્લિટ વ્યવહારો:</h4>
                <table class="live-grid">
                    <tr><th>તારીખ</th><th>ગ્રાહક</th><th>મોડેલ & વિગત</th><th>કારીગર</th><th>પાર્ટ ખર્ચ</th><th>ગ્રાહક ચાર્જ</th><th>કુલ નફો</th><th>કારીગર ભાગ</th><th>દુકાનદાર નફો</th></tr>
                    {rep_trs}
                </table>
            </div>
        </div>
        <script>
            function toggleF7RepairSubmode(val){{
                document.getElementById('f7_rep_simple_wrap').style.display = (val === 'SIMPLE') ? 'block' : 'none';
                document.getElementById('f7_rep_split_wrap').style.display = (val === 'SPLIT') ? 'block' : 'none';
            }}
            function syncF7MopGalla(mopEl, gallaElId) {{
                var gallaEl = (typeof gallaElId === 'string') ? document.getElementById(gallaElId) : gallaElId;
                if (!mopEl || !gallaEl) return;
                var mop = (mopEl.value || '').trim();
                var isCash = (mop.indexOf('રોકડ') !== -1 || mop.toUpperCase().indexOf('CASH') !== -1) && 
                             mop.indexOf('UPI') === -1 && mop.indexOf('બેંક') === -1 && mop.indexOf('કાર્ડ') === -1 && mop.indexOf('NEFT') === -1;
                if (isCash) {{
                    var isExtra = (gallaElId.indexOf('rec') !== -1 || gallaElId.indexOf('rgalla') !== -1 || gallaElId.indexOf('b1') !== -1);
                    gallaEl.innerHTML = `
                        <option value="EXTRA_CASH"` + (isExtra ? ' selected' : '') + `>૪. એક્સ્ટ્રા કેશ (ગલ્લો ૪)</option>
                        <option value="BANK_CASH"` + (!isExtra ? ' selected' : '') + `>૧. બેંક કેશ (ગલ્લો ૧)</option>
                        <option value="ACC_DCASH">૨. એક્સેસરીઝ કેશ (ગલ્લો ૨)</option>
                        <option value="RECHARGE">૩. રિચાર્જ કેશ (ગલ્લો ૩)</option>
                    `;
                    gallaEl.style.background = '#ffffff';
                    gallaEl.style.borderColor = '#15803d';
                }} else {{
                    var desc = mop.indexOf('કાર્ડ') !== -1 ? 'કાર્ડ સ્વાઇપ POS' : (mop.indexOf('UPI') !== -1 ? 'UPI QR કોડ' : 'બેંક ખાતું');
                    gallaEl.innerHTML = `
                        <option value="ONLINE_BANK" selected>🏦 ડિજિટલ બેંક એકાઉન્ટ (` + desc + ` - ખાતામાં સીધા જમા/ચુકવણી)</option>
                    `;
                    gallaEl.style.background = '#e0f2fe';
                    gallaEl.style.borderColor = '#0284c7';
                }}
            }}
            function calcF7RepairSplit(){{
                var cost = parseFloat(document.getElementById('f7_rep_cost').value) || 0;
                var chg = parseFloat(document.getElementById('f7_rep_charge').value) || 0;
                var net = Math.max(0, chg - cost);
                document.getElementById('f7_rep_net').value = Math.round(net);
                var pct = parseFloat(document.getElementById('f7_tech_pct').value) || 0;
                var techAmt = Math.round((net * pct) / 100.0);
                var ownerAmt = Math.round(net - techAmt);
                document.getElementById('f7_tech_amt').value = techAmt;
                document.getElementById('f7_owner_amt').value = ownerAmt;
            }}
        </script>
        """

    # =========================================================================
    # [F8] ૪-ગલ્લા ઓડિટ (ચારેય ગલ્લા સ્વતંત્ર ૧૨-લાઈન રિકોન્સિલેશન + શરતી HO ટેબલ)
    # =========================================================================
    galla_keys = ["BANK_CASH", "ACC_DCASH", "RECHARGE", "EXTRA_CASH"]
    t1_data = {}
    t2_data = {}
    for gk in galla_keys:
        c.execute("SELECT n500, n200, n100, n50, n20, n10, coins, opening_cash FROM cash_audit_4galla WHERE galla_name=?", (gk,))
        t1_data[gk] = c.fetchone() or (0, 0, 0, 0, 0, 0, 0, 0.0)
        c.execute("SELECT n500, n200, n100, n50, n20, n10, coins FROM total_cumulative_notes WHERE galla_name=?", (gk,))
        t2_data[gk] = c.fetchone() or (0, 0, 0, 0, 0, 0, 0)

    def calc_notes_sum(row_tuple):
        return (int(row_tuple[0] or 0)*500 + int(row_tuple[1] or 0)*200 + int(row_tuple[2] or 0)*100 +
                int(row_tuple[3] or 0)*50 + int(row_tuple[4] or 0)*20 + int(row_tuple[5] or 0)*10 + int(row_tuple[6] or 0))

    # રો ૧: ચારેય ગલ્લાની ગણેલી હાજર રોકડ (અથવા ગલ્લા ૧ માટે HO મેળવણી)
    l1_counted_cash_g1 = float(calc_notes_sum(t1_data["BANK_CASH"]))
    l1_counted_cash_all = sum(float(calc_notes_sum(t1_data[gk])) for gk in galla_keys)
    l1_counted_cash = l1_counted_cash_g1 if st_mode == "FRANCHISE_HO" else l1_counted_cash_all

    c.execute("SELECT COALESCE(SUM(out_amt),0) FROM galla_ledger WHERE date=? AND remarks LIKE '%ખર્ચ%' AND remarks NOT LIKE '%ટ્રાન્સફર%'", (today_str,))
    l2_exp = float(c.fetchone()[0] or 0.0)

    c.execute("SELECT COALESCE(SUM(bb_amt),0) FROM apx_sales_raw WHERE bill_date=?", (today_str,))
    bb_ex = float(c.fetchone()[0] or 0.0)
    c.execute("SELECT COALESCE(SUM(out_amt),0) FROM galla_ledger WHERE date=? AND remarks LIKE '%બાયબેક%' AND remarks NOT LIKE '%ટ્રાન્સફર%'", (today_str,))
    bb_dir = float(c.fetchone()[0] or 0.0)
    l3_buyback = bb_ex + bb_dir

    from part1_core import STORE_CFG
    sid = STORE_CFG.get("shop_id", "DEVANSHI")
    c.execute("SELECT COALESCE(SUM(amount),0) FROM bank_deposit_log WHERE date=? AND COALESCE(store_id, ?)=? AND COALESCE(source_type,'BANK_CASH') IN ('આજની ઓપનિંગ બેંક કેશ', 'આજની ફ્રેશ બેંક કેશ', 'BANK_CASH')", (today_str, sid, sid))
    l4_today_bank_dep_g1 = float(c.fetchone()[0] or 0.0)
    c.execute("SELECT COALESCE(SUM(amount),0) FROM bank_deposit_log WHERE date=? AND COALESCE(store_id, ?)=?", (today_str, sid, sid))
    l4_today_bank_dep_all = float(c.fetchone()[0] or 0.0)
    l4_today_bank_dep = l4_today_bank_dep_g1 if st_mode == "FRANCHISE_HO" else l4_today_bank_dep_all

    c.execute("SELECT COALESCE(SUM(paid_amt),0) FROM staff_commission_ledger WHERE date=?", (today_str,))
    l5_staff_upad = float(c.fetchone()[0] or 0.0)

    c.execute("SELECT COALESCE(SUM(due_amt),0) FROM apx_sales_raw WHERE bill_date=?", (today_str,))
    l6_cust_due = float(c.fetchone()[0] or 0.0)

    c.execute("SELECT COALESCE(SUM(upi_dp + card_swipe_dp + staff_cc_swipe + COALESCE(neft_rtgs_dp,0)),0) FROM apx_sales_raw WHERE bill_date=?", (today_str,))
    l7_upi_card = float(c.fetchone()[0] or 0.0)

    c.execute("SELECT COALESCE(SUM(in_amt),0) FROM galla_ledger WHERE date=? AND remarks LIKE '%ઉધાર વસૂલાત%' AND remarks NOT LIKE '%ટ્રાન્સફર%'", (today_str,))
    l8_old_due_rec = float(c.fetchone()[0] or 0.0)

    # સાચું ૧૨-લાઇન સૂત્ર: Total Cash = (રો ૧ + ૨ + ૩ + ૪ + ૫ + ૭) - (રો ૬ + ૮)
    # કાર્ડ સ્વાઇપ / ઓનલાઈન UPI / સ્ટાફ CC સ્વાઇપ (l7_upi_card) બેંકમાં જમા થતું હોવાથી રોકડ મેળવણીમાં પ્લસ (+) થાય છે!
    l9_total_derived = (l1_counted_cash + l2_exp + l3_buyback + l4_today_bank_dep + l5_staff_upad + l7_upi_card) - (l6_cust_due + l8_old_due_rec)

    c.execute("SELECT COALESCE(SUM(CASE WHEN bill_type='FINANCE_BILL' THEN (mop_price - COALESCE(NULLIF(net_disb_amt,0), loan_amt)) ELSE mop_price END), 0) FROM apx_sales_raw WHERE bill_date=?", (today_str,))
    apx_auto_day_cash = float(c.fetchone()[0] or 0.0)
    if st_mode != "FRANCHISE_HO" and apx_auto_day_cash <= 0:
        c.execute("SELECT COALESCE(SUM(in_amt),0) FROM galla_ledger WHERE date=? AND remarks NOT LIKE '%ઉધાર વસૂલાત%' AND remarks NOT LIKE '%ટ્રાન્સફર%'", (today_str,))
        apx_auto_day_cash = float(c.fetchone()[0] or 0.0)
    l10_apx_day_cash = apx_auto_day_cash
    l11_diff = l9_total_derived - l10_apx_day_cash
    l12_ho_closing = get_cumulative_unbanked_cash()

    # ૪-ગલ્લા સ્વતંત્ર ગણતરી (Four-Vault Independent Calculation)
    op_g1 = float(t1_data["BANK_CASH"][7] or 0)
    in_g1 = l10_apx_day_cash
    rec_g1 = l8_old_due_rec
    c.execute("SELECT COALESCE(SUM(out_amt),0) FROM galla_ledger WHERE date=? AND galla_name='BANK_CASH' AND remarks LIKE '%ખર્ચ%'", (today_str,))
    exp_g1 = float(c.fetchone()[0] or 0)
    c.execute("SELECT COALESCE(SUM(out_amt),0) FROM galla_ledger WHERE date=? AND galla_name='BANK_CASH' AND (remarks LIKE '%ઉપાડ%' OR remarks LIKE '%સ્ટાફ%')", (today_str,))
    upad_g1 = float(c.fetchone()[0] or 0)
    bb_g1 = l3_buyback
    dep_g1 = l4_today_bank_dep_g1
    due_g1 = l6_cust_due
    exp_close_g1 = op_g1 + in_g1 + rec_g1 - (exp_g1 + upad_g1 + bb_g1 + dep_g1 + due_g1)
    cnt_g1 = float(calc_notes_sum(t1_data["BANK_CASH"]))
    diff_g1 = cnt_g1 - exp_close_g1
    diff_col_g1 = "#15803d" if abs(diff_g1) < 1 else "#dc2626"

    op_g2 = float(t1_data["ACC_DCASH"][7] or 0)
    c.execute("SELECT COALESCE(SUM(in_amt),0) FROM galla_ledger WHERE date=? AND galla_name='ACC_DCASH'", (today_str,))
    in_g2 = float(c.fetchone()[0] or 0)
    c.execute("SELECT COALESCE(SUM(out_amt),0) FROM galla_ledger WHERE date=? AND galla_name='ACC_DCASH' AND remarks LIKE '%ખર્ચ%'", (today_str,))
    exp_g2 = float(c.fetchone()[0] or 0)
    c.execute("SELECT COALESCE(SUM(out_amt),0) FROM galla_ledger WHERE date=? AND galla_name='ACC_DCASH' AND (remarks LIKE '%ખરીદી%' OR remarks LIKE '%પર્ચેઝ%')", (today_str,))
    pur_g2 = float(c.fetchone()[0] or 0)
    c.execute("SELECT COALESCE(SUM(out_amt),0) FROM galla_ledger WHERE date=? AND galla_name='ACC_DCASH' AND (remarks LIKE '%બેંક%' OR remarks LIKE '%ડિપોઝિટ%')", (today_str,))
    dep_g2 = float(c.fetchone()[0] or 0)
    exp_close_g2 = op_g2 + in_g2 - (exp_g2 + pur_g2 + dep_g2)
    cnt_g2 = float(calc_notes_sum(t1_data["ACC_DCASH"]))
    diff_g2 = cnt_g2 - exp_close_g2
    diff_col_g2 = "#15803d" if abs(diff_g2) < 1 else "#dc2626"

    op_g3 = float(t1_data["RECHARGE"][7] or 0)
    c.execute("SELECT COALESCE(SUM(in_amt),0) FROM galla_ledger WHERE date=? AND galla_name='RECHARGE'", (today_str,))
    in_g3 = float(c.fetchone()[0] or 0)
    c.execute("SELECT COALESCE(SUM(out_amt),0) FROM galla_ledger WHERE date=? AND galla_name='RECHARGE' AND remarks LIKE '%ખર્ચ%'", (today_str,))
    exp_g3 = float(c.fetchone()[0] or 0)
    c.execute("SELECT COALESCE(SUM(out_amt),0) FROM galla_ledger WHERE date=? AND galla_name='RECHARGE' AND (remarks LIKE '%LAPU%' OR remarks LIKE '%ડિસ્ટ્રિબ્યુટર%')", (today_str,))
    lapu_g3 = float(c.fetchone()[0] or 0)
    c.execute("SELECT COALESCE(SUM(out_amt),0) FROM galla_ledger WHERE date=? AND galla_name='RECHARGE' AND (remarks LIKE '%બેંક%' OR remarks LIKE '%ડિપોઝિટ%')", (today_str,))
    dep_g3 = float(c.fetchone()[0] or 0)
    exp_close_g3 = op_g3 + in_g3 - (exp_g3 + lapu_g3 + dep_g3)
    cnt_g3 = float(calc_notes_sum(t1_data["RECHARGE"]))
    diff_g3 = cnt_g3 - exp_close_g3
    diff_col_g3 = "#15803d" if abs(diff_g3) < 1 else "#dc2626"

    op_g4 = float(t1_data["EXTRA_CASH"][7] or 0)
    c.execute("SELECT COALESCE(SUM(in_amt),0) FROM galla_ledger WHERE date=? AND galla_name='EXTRA_CASH'", (today_str,))
    in_g4 = float(c.fetchone()[0] or 0)
    c.execute("SELECT COALESCE(SUM(out_amt),0) FROM galla_ledger WHERE date=? AND galla_name='EXTRA_CASH' AND remarks LIKE '%ખર્ચ%'", (today_str,))
    exp_g4 = float(c.fetchone()[0] or 0)
    c.execute("SELECT COALESCE(SUM(out_amt),0) FROM galla_ledger WHERE date=? AND galla_name='EXTRA_CASH' AND (remarks LIKE '%ઉપાડ%' OR remarks LIKE '%પાર્ટનર%')", (today_str,))
    upad_g4 = float(c.fetchone()[0] or 0)
    c.execute("SELECT COALESCE(SUM(out_amt),0) FROM galla_ledger WHERE date=? AND galla_name='EXTRA_CASH' AND (remarks LIKE '%બેંક%' OR remarks LIKE '%ડિપોઝિટ%')", (today_str,))
    dep_g4 = float(c.fetchone()[0] or 0)
    exp_close_g4 = op_g4 + in_g4 - (exp_g4 + upad_g4 + dep_g4)
    cnt_g4 = float(calc_notes_sum(t1_data["EXTRA_CASH"]))
    diff_g4 = cnt_g4 - exp_close_g4
    diff_col_g4 = "#15803d" if abs(diff_g4) < 1 else "#dc2626"

    diff_tot = diff_g1 + diff_g2 + diff_g3 + diff_g4
    diff_col_tot = "#15803d" if abs(diff_tot) < 1 else "#dc2626"

    def build_galla_table(tbl_id, title_str, title_col, data_map, is_t1=True):
        denoms = [("n500", "૫૦૦"), ("n200", "૨૦૦"), ("n100", "૧૦૦"),
                  ("n50", "૫૦"), ("n20", "૨૦"), ("n10", "૧૦"), ("coins", "સિક્કા")]
        if is_t1:
            open_row = f"""
            <tr style="background:#fef9c3;">
                <td><b>Open ₹ (ઓપનિંગ)</b></td>
                <td><input type="number" step="any" class="vjump" data-col="1" name="op_BANK_CASH" value="{float(data_map['BANK_CASH'][7] or 0):.0f}" style="width:74px; padding:3px; text-align:center; font-weight:bold; color:#0f2043;"></td>
                <td><input type="number" step="any" class="vjump" data-col="2" name="op_ACC_DCASH" value="{float(data_map['ACC_DCASH'][7] or 0):.0f}" style="width:74px; padding:3px; text-align:center; font-weight:bold; color:#0369a1;"></td>
                <td><input type="number" step="any" class="vjump" data-col="3" name="op_RECHARGE" value="{float(data_map['RECHARGE'][7] or 0):.0f}" style="width:74px; padding:3px; text-align:center; font-weight:bold; color:#6b21a8;"></td>
                <td><input type="number" step="any" class="vjump" data-col="4" name="op_EXTRA_CASH" value="{float(data_map['EXTRA_CASH'][7] or 0):.0f}" style="width:74px; padding:3px; text-align:center; font-weight:bold; color:#b45309;"></td>
            </tr>
            """
        else:
            open_row = """
            <tr style="background:#f3e8ff;">
                <td><b>Open ₹ (વૉલ્ટ અનામત)</b></td>
                <td colspan="4" style="text-align:center; color:#6b21a8; font-weight:bold; font-size:11px;">ક્યુમ્યુલેટિવ વૉલ્ટ કેશ સિલક (ગલ્લા ૧ થી ૪ સાચવેલી નોટો)</td>
            </tr>
            """

        rows_str = open_row
        for idx_d, (d_key, d_lbl) in enumerate(denoms):
            rows_str += f"""
            <tr>
                <td><b>{d_lbl}</b></td>
                <td><input type="number" class="vjump" data-col="1" name="{d_key}_BANK_CASH" value="{data_map['BANK_CASH'][idx_d]}" oninput="recalcGallaTbl('{tbl_id}')" style="width:74px; padding:3px; text-align:center;"></td>
                <td><input type="number" class="vjump" data-col="2" name="{d_key}_ACC_DCASH" value="{data_map['ACC_DCASH'][idx_d]}" oninput="recalcGallaTbl('{tbl_id}')" style="width:74px; padding:3px; text-align:center;"></td>
                <td><input type="number" class="vjump" data-col="3" name="{d_key}_RECHARGE" value="{data_map['RECHARGE'][idx_d]}" oninput="recalcGallaTbl('{tbl_id}')" style="width:74px; padding:3px; text-align:center;"></td>
                <td><input type="number" class="vjump" data-col="4" name="{d_key}_EXTRA_CASH" value="{data_map['EXTRA_CASH'][idx_d]}" oninput="recalcGallaTbl('{tbl_id}')" style="width:74px; padding:3px; text-align:center;"></td>
            </tr>
            """
        t_type = "T1" if is_t1 else "T2"
        tot_bg = "#dcfce7" if is_t1 else "#f3e8ff"
        return f"""
        <div style="background:white; border:1px solid #cbd5e1; border-radius:6px; padding:10px;">
            <h4 style="margin:0 0 8px 0; color:{title_col};">{title_str}</h4>
            <form id="{tbl_id}" action="/save-f8-audit" method="post">
                <input type="hidden" name="table_type" value="{t_type}">
                <table class="live-grid">
                    <tr>
                        <th style="background:#f1f5f9; color:#1e293b;">દર / ચલણ</th>
                        <th style="background:#f1f5f9; color:#15803d;">૧. બેંક કેશ</th>
                        <th style="background:#f1f5f9; color:#0369a1;">૨. એક્સેસરીઝ</th>
                        <th style="background:#f1f5f9; color:#6b21a8;">૩. રીચાર્જ</th>
                        <th style="background:#f1f5f9; color:#b45309;">૪. તિજોરી/નફો</th>
                    </tr>
                    {rows_str}
                    <tr style="background:{tot_bg}; font-weight:bold;">
                        <td>કુલ નોટો ₹</td>
                        <td id="{tbl_id}_sum_BANK_CASH">₹{calc_notes_sum(data_map['BANK_CASH']):,.0f}</td>
                        <td id="{tbl_id}_sum_ACC_DCASH">₹{calc_notes_sum(data_map['ACC_DCASH']):,.0f}</td>
                        <td id="{tbl_id}_sum_RECHARGE">₹{calc_notes_sum(data_map['RECHARGE']):,.0f}</td>
                        <td id="{tbl_id}_sum_EXTRA_CASH">₹{calc_notes_sum(data_map['EXTRA_CASH']):,.0f}</td>
                    </tr>
                    <tr>
                        <td><b>સેવિંગ</b></td>
                        <td><button type="submit" id="{tbl_id}_btn_1" name="save_scope" value="BANK_CASH" style="background:#15803d; color:white; border:none; padding:4px 8px; border-radius:3px; cursor:pointer; font-weight:bold;">[સાચવો ૧]</button></td>
                        <td><button type="submit" id="{tbl_id}_btn_2" name="save_scope" value="ACC_DCASH" style="background:#1e3a8a; color:white; border:none; padding:4px 8px; border-radius:3px; cursor:pointer; font-weight:bold;">[સાચવો ૨]</button></td>
                        <td><button type="submit" id="{tbl_id}_btn_3" name="save_scope" value="RECHARGE" style="background:#7c3aed; color:white; border:none; padding:4px 8px; border-radius:3px; cursor:pointer; font-weight:bold;">[સાચવો ૩]</button></td>
                        <td><button type="submit" id="{tbl_id}_btn_4" name="save_scope" value="EXTRA_CASH" style="background:#b45309; color:white; border:none; padding:4px 8px; border-radius:3px; cursor:pointer; font-weight:bold;">[સાચવો ૪]</button></td>
                    </tr>
                </table>
                <div style="display:flex; gap:8px; margin-top:8px; justify-content:center;">
                    <button type="submit" name="save_scope" value="ALL" style="background:#0f2043; color:white; border:none; padding:6px 16px; border-radius:4px; font-weight:bold; cursor:pointer; font-size:12px;">[ ✅ એકસાથે સાચવો ({t_type}) ]</button>
                    <a href="/undo-f8-audit?table_type={t_type}" onclick="return confirm('છેલ્લો ફેરફાર Undo કરવો છે?')" style="background:#dc2626; color:white; padding:6px 14px; border-radius:4px; text-decoration:none; font-weight:bold; font-size:12px;">[ ↩️ Undo ]</a>
                </div>
            </form>
        </div>
        """

    tbl1_html = build_galla_table("f8_t1", "ટેબલ ૧: આજના દિવસની નવી રોકડ (૪-ગલ્લા ઓપનિંગ + નોટ ગણતરી)", "#0f2043", t1_data, True)
    tbl2_html = build_galla_table("f8_t2", "ટેબલ ૨: ૪-ગલ્લા ક્યુમ્યુલેટિવ વૉલ્ટ (અનામત સિલક ઓપનિંગ + નોટ ગણતરી)", "#6b21a8", t2_data, False)

    vault_recon_rows = ""
    galla_labels = [
        ("BANK_CASH", "૧. બેંક કેશ (ગલ્લો ૧)"),
        ("ACC_DCASH", "૨. એક્સેસરીઝ કેશ (ગલ્લો ૨)"),
        ("RECHARGE", "૩. રીચાર્જ કેશ (ગલ્લો ૩)"),
        ("EXTRA_CASH", "૪. એક્સ્ટ્રા કેશ (ગલ્લો ૪)")
    ]
    for gk, glbl in galla_labels:
        op_val = float(t1_data[gk][7] or 0.0)
        c.execute("SELECT COALESCE(SUM(in_amt),0), COALESCE(SUM(out_amt),0) FROM galla_ledger WHERE date=? AND galla_name=?", (today_str, gk))
        in_today, out_today = c.fetchone() or (0.0, 0.0)
        in_today = float(in_today or 0.0)
        out_today = float(out_today or 0.0)
        expected_close = op_val + in_today - out_today
        phys_t1 = float(calc_notes_sum(t1_data[gk]))
        phys_t2 = float(calc_notes_sum(t2_data[gk]))
        v_diff = (phys_t1 + phys_t2) - expected_close if (phys_t1 + phys_t2) > 0 else (phys_t1 - expected_close)
        d_col = "#16a34a" if abs(v_diff) < 1 else "#dc2626"
        vault_recon_rows += f"""
        <tr>
            <td style="text-align:left; font-weight:bold;">{glbl}</td>
            <td>₹{op_val:,.0f}</td>
            <td style="color:#16a34a; font-weight:bold;">+ ₹{in_today:,.0f}</td>
            <td style="color:#dc2626; font-weight:bold;">- ₹{out_today:,.0f}</td>
            <td style="background:#fef9c3; font-weight:bold;">₹{expected_close:,.0f}</td>
            <td style="font-weight:bold; color:#0284c7;">₹{phys_t1:,.0f} (વૉલ્ટ: ₹{phys_t2:,.0f})</td>
            <td style="font-weight:bold; color:{d_col};">₹{v_diff:,.0f}</td>
        </tr>
        """

    if st_mode == "FRANCHISE_HO":
        f8_mode_banner = """<div style="background:#eff6ff; border:1px solid #0284c7; padding:6px 12px; margin:0 8px 6px; border-radius:4px; font-size:12px; display:flex; justify-content:space-between; align-items:center;">
        <span>👑 <b>દુકાન પદ્ધતિ:</b> ફ્રેન્ચાઇઝી સ્ટોર મોડ (HO કાઉન્ટર કેશ લાયાબિલિટી + ચારેય ગલ્લાનું દૈનિક ઓપનિંગ-ક્લોઝિંગ)</span>
        <span style="background:#0284c7; color:white; padding:2px 8px; border-radius:3px; font-weight:bold;">FRANCHISE HO RECONCILIATION ACTIVE</span>
    </div>"""
        ho_recon_block = f"""
        <div style="background:#f0f9ff; border:2px solid #0284c7; border-radius:6px; padding:12px; margin:0 8px 12px;">
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
                <h4 style="margin:0; color:#0369a1;">👑 ટેબલ A: HO કેશ લાયાબિલિટી & ગ્રાઉન્ડ રિયાલિટી ગેપ વિશ્લેષણ (Franchise HO Reconciliation)</h4>
                <span style="font-size:11.5px; background:#0284c7; color:white; padding:3px 10px; border-radius:4px; font-weight:bold;">HO પોર્ટલ ચોપડે કેશ vs. ગ્રાઉન્ડ વાસ્તવિકતા</span>
            </div>
            <div style="display:grid; grid-template-columns:1fr 1fr; gap:12px;">
                <div style="background:white; border:1px solid #cbd5e1; padding:10px; border-radius:6px;">
                    <div style="font-weight:bold; color:#0f2043; border-bottom:1px solid #e2e8f0; padding-bottom:5px; margin-bottom:8px; font-size:12.5px;">૧. HO ચોપડે ચૂકવવાપાત્ર કુલ કેશ (HO Book Cash Due):</div>
                    <table style="width:100%; font-size:12px;">
                        <tr><td>અગાઉની અણભરેલ કેશ લાયાબિલિટી:</td><td style="text-align:right; font-weight:bold;">₹{l12_ho_closing:,.0f}</td></tr>
                        <tr><td>આજનું APX પોર્ટલ કેશ બિલિંગ (+):</td><td style="text-align:right; color:#15803d; font-weight:bold;">+ ₹{l10_apx_day_cash:,.0f}</td></tr>
                        <tr><td>સીધા HO બેંકમાં ભરેલ રકમ [F4] (-):</td><td style="text-align:right; color:#dc2626; font-weight:bold;">- ₹{l4_today_bank_dep:,.0f}</td></tr>
                        <tr style="background:#eff6ff; font-weight:bold; border-top:1px solid #93c5fd;"><td style="padding:6px 0;">કુલ HO ચોપડે બોલતી બાકી કેશ:</td><td style="text-align:right; color:#1d4ed8; font-size:13.5px;">₹{(l12_ho_closing + l10_apx_day_cash - l4_today_bank_dep):,.0f}</td></tr>
                    </table>
                </div>
                <div style="background:white; border:1px solid #cbd5e1; padding:10px; border-radius:6px;">
                    <div style="font-weight:bold; color:#b45309; border-bottom:1px solid #e2e8f0; padding-bottom:5px; margin-bottom:8px; font-size:12.5px;">૨. ગ્રાઉન્ડ રિયાલિટી (આ HO કેશ ક્યાં રોકાયેલી છે?):</div>
                    <table style="width:100%; font-size:12px;">
                        <tr><td>(a) ગ્રાહકો પાસે બાકી રહેલ ઉધાર:</td><td style="text-align:right; color:#dc2626; font-weight:bold;">₹{l6_cust_due:,.0f}</td></tr>
                        <tr><td>(b) દુકાને કરેલો ખર્ચ [F3]:</td><td style="text-align:right; color:#b45309; font-weight:bold;">₹{l2_exp:,.0f}</td></tr>
                        <tr><td>(c) સ્ટોકમાં પડેલા બાયબેક ફોનની કિંમત [F5]:</td><td style="text-align:right; color:#7c3aed; font-weight:bold;">₹{l3_buyback:,.0f}</td></tr>
                        <tr><td>(d) ગલ્લામાં હાજર ભૌતિક રોકડ (ગણેલી):</td><td style="text-align:right; color:#15803d; font-weight:bold;">₹{l1_counted_cash:,.0f}</td></tr>
                        <tr style="background:#fef3c7; font-weight:bold; border-top:1px solid #fde047;"><td style="padding:6px 0;">👉 માલિકે એડજસ્ટ કરવાની કેશ (Net Gap):</td><td style="text-align:right; color:#b45309; font-size:13.5px;">₹{max(0.0, (l12_ho_closing + l10_apx_day_cash - l4_today_bank_dep) - (l1_counted_cash + l6_cust_due + l3_buyback)):,.0f}</td></tr>
                    </table>
                </div>
            </div>
        </div>"""
    else:
        f8_mode_banner = """<div style="background:#f0fdf4; border:1px solid #16a34a; padding:6px 12px; margin:0 8px 6px; border-radius:4px; font-size:12px; display:flex; justify-content:space-between; align-items:center;">
        <span>🏪 <b>દુકાન પદ્ધતિ:</b> પર્સનલ રિટેલ સ્ટોર મોડ (ચારેય ગલ્લાની સ્વતંત્ર મેળવણી - HO લાયાબિલિટી બંધ છે)</span>
        <span style="background:#16a34a; color:white; padding:2px 8px; border-radius:3px; font-weight:bold;">RETAIL 4-GALLA AUDIT ACTIVE</span>
    </div>"""
        ho_recon_block = ""

    return f"""
    <div class="mode-banner">
        <span>મોડ: [F8] ૪-ગલ્લા ઓડિટ (ચારેય ગલ્લા ઓપનિંગ બેલેન્સ, નોટ ગણતરી, ૪-ગલ્લા ૧૨-લાઈન રિકોન્સિલેશન & વૉલ્ટ મેળવણી)</span>
        <form action="/carry-forward-f8-daily-closing" method="post" style="margin:0;">
            <button type="submit" onclick="return confirm('શું આજની ક્લોઝિંગ બેલેન્સ સેવ કરીને આવતીકાલની ઓપનિંગ બેલેન્સ તરીકે કેરી-ફોરવર્ડ કરવી છે?')" style="background:#15803d; color:white; border:none; padding:5px 12px; border-radius:4px; font-weight:bold; cursor:pointer; font-size:11.5px;">🔄 આજની ક્લોઝિંગ -> આવતીકાલની ઓપનિંગમાં કેરી-ફોરવર્ડ કરો</button>
        </form>
    </div>

    <!-- TALLY PRIME SUB-SECTIONS STRIP (F8 ૧ થી ૪ લાઈનબદ્ધ પેટા વિભાગો) -->
    <div class="tally-subparts-bar">
        <span style="color:#fde047; font-weight:800; font-size:11px; margin-right:4px;">પેટા વિભાગ:</span>
        <button type="button" class="tally-sub-btn active" id="f8_sub_btn_ALL" onclick="setSubpartF8('ALL')">૧. તમામ ઓડિટ ટેબલ સાથે જુઓ</button>
        <button type="button" class="tally-sub-btn" id="f8_sub_btn_AUDIT" onclick="setSubpartF8('AUDIT')">૨. ૪-ગલ્લા નોટ ગણતરી (Audit Log)</button>
        <button type="button" class="tally-sub-btn" id="f8_sub_btn_RECON" onclick="setSubpartF8('RECON')">૩. ૧૨-લાઇન મેળવણી (Reconciliation)</button>
        <button type="button" class="tally-sub-btn" id="f8_sub_btn_VAULT" onclick="setSubpartF8('VAULT')">૪. વૉલ્ટ કેરી-ફોરવર્ડ</button>
    </div>
    <script>
    function setSubpartF8(val) {{
        document.querySelectorAll('.tally-subparts-bar .tally-sub-btn').forEach(function(b){{
            b.classList.remove('active');
        }});
        var curBtn = document.getElementById('f8_sub_btn_' + val);
        if (curBtn) curBtn.classList.add('active');
        var bAudit = document.getElementById('f8_audit_tables_wrap');
        var bRecon = document.getElementById('f8_recon_wrap');
        if (val === 'AUDIT' && bAudit) {{
            bAudit.scrollIntoView({{ behavior:'smooth' }});
        }} else if (val === 'RECON' && bRecon) {{
            bRecon.scrollIntoView({{ behavior:'smooth' }});
        }}
    }}
    </script>
    {f8_mode_banner}
    <div id="f8_audit_tables_wrap" style="display:grid; grid-template-columns:1fr 1fr; gap:12px; padding:8px;">
        {tbl1_html}
        {tbl2_html}
    </div>

    {ho_recon_block}

    <div id="f8_recon_wrap" style="padding:0 8px 12px;">
        <div style="background:white; border:2px solid #0f2043; border-radius:6px; padding:12px;">
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
                <h4 style="margin:0; color:#0f2043; font-size:13.5px;">📊 ૧. ૪-ગલ્લા સ્વતંત્ર ૧૨-લાઈન દૈનિક રિકોન્સિલેશન (Four-Vault Independent Cash Reconciliation)</h4>
                <span style="font-size:11.5px; background:#0f2043; color:white; padding:3px 10px; border-radius:4px; font-weight:bold;">ચારેય ગલ્લાની સ્વતંત્ર મેળવણી</span>
            </div>
            <table class="live-grid" style="font-size:12px;">
                <thead>
                    <tr style="background:#0f2043; color:white;">
                        <th style="text-align:left;">લાઈન & વ્યવહાર વિગત</th>
                        <th style="color:#86efac; text-align:right;">૧. બેંક કેશ (ગલ્લો ૧)</th>
                        <th style="color:#7dd3fc; text-align:right;">૨. એક્સેસરીઝ D-Cash</th>
                        <th style="color:#d8b4fe; text-align:right;">૩. રીચાર્જ કેશ</th>
                        <th style="color:#fde047; text-align:right;">૪. તિજોરી / એક્સ્ટ્રા</th>
                        <th style="color:white; text-align:right; font-weight:800;">કુલ રોકડ (Total)</th>
                    </tr>
                </thead>
                <tbody>
                    <tr style="background:#fef9c3;">
                        <td><b>૧. શરૂઆતની રોકડ (Opening Cash)</b></td>
                        <td style="text-align:right; font-weight:bold;">₹{op_g1:,.0f}</td>
                        <td style="text-align:right; font-weight:bold;">₹{op_g2:,.0f}</td>
                        <td style="text-align:right; font-weight:bold;">₹{op_g3:,.0f}</td>
                        <td style="text-align:right; font-weight:bold;">₹{op_g4:,.0f}</td>
                        <td style="text-align:right; font-weight:800; color:#854d0e;">₹{(op_g1+op_g2+op_g3+op_g4):,.0f}</td>
                    </tr>
                    <tr>
                        <td>૨. આજનું રોકડ વેચાણ / ગ્રાહક આવક [F2/F7] (+)</td>
                        <td style="text-align:right; color:#15803d; font-weight:bold;">+ ₹{in_g1:,.0f}</td>
                        <td style="text-align:right; color:#15803d; font-weight:bold;">+ ₹{in_g2:,.0f}</td>
                        <td style="text-align:right; color:#15803d; font-weight:bold;">+ ₹{in_g3:,.0f}</td>
                        <td style="text-align:right; color:#15803d; font-weight:bold;">+ ₹{in_g4:,.0f}</td>
                        <td style="text-align:right; color:#15803d; font-weight:800;">+ ₹{(in_g1+in_g2+in_g3+in_g4):,.0f}</td>
                    </tr>
                    <tr>
                        <td>૩. જૂની બાકી ઉધાર વસૂલાત [F3] (+)</td>
                        <td style="text-align:right; color:#15803d; font-weight:bold;">+ ₹{rec_g1:,.0f}</td>
                        <td style="text-align:right; color:#64748b;">-</td>
                        <td style="text-align:right; color:#64748b;">-</td>
                        <td style="text-align:right; color:#64748b;">-</td>
                        <td style="text-align:right; color:#15803d; font-weight:bold;">+ ₹{rec_g1:,.0f}</td>
                    </tr>
                    <tr>
                        <td>૪. દૈનિક દુકાન ખર્ચ [F3] (-)</td>
                        <td style="text-align:right; color:#dc2626; font-weight:bold;">- ₹{exp_g1:,.0f}</td>
                        <td style="text-align:right; color:#dc2626; font-weight:bold;">- ₹{exp_g2:,.0f}</td>
                        <td style="text-align:right; color:#dc2626; font-weight:bold;">- ₹{exp_g3:,.0f}</td>
                        <td style="text-align:right; color:#dc2626; font-weight:bold;">- ₹{exp_g4:,.0f}</td>
                        <td style="text-align:right; color:#dc2626; font-weight:800;">- ₹{(exp_g1+exp_g2+exp_g3+exp_g4):,.0f}</td>
                    </tr>
                    <tr>
                        <td>૫. સ્ટાફ ઉપાડ / પગાર / વેપારી ચૂકવણી [F3] (-)</td>
                        <td style="text-align:right; color:#dc2626; font-weight:bold;">- ₹{upad_g1:,.0f}</td>
                        <td style="text-align:right; color:#64748b;">-</td>
                        <td style="text-align:right; color:#64748b;">-</td>
                        <td style="text-align:right; color:#dc2626; font-weight:bold;">- ₹{upad_g4:,.0f}</td>
                        <td style="text-align:right; color:#dc2626; font-weight:bold;">- ₹{(upad_g1+upad_g4):,.0f}</td>
                    </tr>
                    <tr>
                        <td>૬. બાયબેક / ખરીદી રોકડ ચૂકવણી [F1/F5] (-)</td>
                        <td style="text-align:right; color:#dc2626; font-weight:bold;">- ₹{bb_g1:,.0f}</td>
                        <td style="text-align:right; color:#dc2626; font-weight:bold;">- ₹{pur_g2:,.0f}</td>
                        <td style="text-align:right; color:#dc2626; font-weight:bold;">- ₹{lapu_g3:,.0f}</td>
                        <td style="text-align:right; color:#64748b;">-</td>
                        <td style="text-align:right; color:#dc2626; font-weight:800;">- ₹{(bb_g1+pur_g2+lapu_g3):,.0f}</td>
                    </tr>
                    <tr>
                        <td>૭. બેંક ડિપોઝિટ / જાવક [F4] (-)</td>
                        <td style="text-align:right; color:#dc2626; font-weight:bold;">- ₹{dep_g1:,.0f}</td>
                        <td style="text-align:right; color:#dc2626; font-weight:bold;">- ₹{dep_g2:,.0f}</td>
                        <td style="text-align:right; color:#dc2626; font-weight:bold;">- ₹{dep_g3:,.0f}</td>
                        <td style="text-align:right; color:#dc2626; font-weight:bold;">- ₹{dep_g4:,.0f}</td>
                        <td style="text-align:right; color:#dc2626; font-weight:800;">- ₹{(dep_g1+dep_g2+dep_g3+dep_g4):,.0f}</td>
                    </tr>
                    <tr>
                        <td>૮. ગ્રાહક બાકી ઉધાર / કાર્ડ [F2] (-)</td>
                        <td style="text-align:right; color:#dc2626; font-weight:bold;">- ₹{due_g1:,.0f}</td>
                        <td style="text-align:right; color:#64748b;">-</td>
                        <td style="text-align:right; color:#64748b;">-</td>
                        <td style="text-align:right; color:#64748b;">-</td>
                        <td style="text-align:right; color:#dc2626; font-weight:bold;">- ₹{due_g1:,.0f}</td>
                    </tr>
                    <tr style="background:#e0f2fe; font-weight:bold;">
                        <td><b>૯. ગણતરી મુજબ હોવી જોઈતી રોકડ (=)</b></td>
                        <td style="text-align:right; color:#0369a1;">₹{exp_close_g1:,.0f}</td>
                        <td style="text-align:right; color:#0369a1;">₹{exp_close_g2:,.0f}</td>
                        <td style="text-align:right; color:#0369a1;">₹{exp_close_g3:,.0f}</td>
                        <td style="text-align:right; color:#0369a1;">₹{exp_close_g4:,.0f}</td>
                        <td style="text-align:right; color:#1d4ed8; font-size:12.5px;">₹{(exp_close_g1+exp_close_g2+exp_close_g3+exp_close_g4):,.0f}</td>
                    </tr>
                    <tr style="background:#fef9c3; font-weight:bold;">
                        <td><b>૧૦. ગણેલી હાજર નોટો (T1 Total Count)</b></td>
                        <td style="text-align:right; color:#854d0e;">₹{cnt_g1:,.0f}</td>
                        <td style="text-align:right; color:#854d0e;">₹{cnt_g2:,.0f}</td>
                        <td style="text-align:right; color:#854d0e;">₹{cnt_g3:,.0f}</td>
                        <td style="text-align:right; color:#854d0e;">₹{cnt_g4:,.0f}</td>
                        <td style="text-align:right; color:#854d0e; font-size:12.5px;">₹{(cnt_g1+cnt_g2+cnt_g3+cnt_g4):,.0f}</td>
                    </tr>
                    <tr style="font-weight:bold;">
                        <td><b>૧૧. લાઈવ મેળવણી તફાવત (DIFF)</b></td>
                        <td style="text-align:right; color:{diff_col_g1};">₹{diff_g1:,.0f}</td>
                        <td style="text-align:right; color:{diff_col_g2};">₹{diff_g2:,.0f}</td>
                        <td style="text-align:right; color:{diff_col_g3};">₹{diff_g3:,.0f}</td>
                        <td style="text-align:right; color:{diff_col_g4};">₹{diff_g4:,.0f}</td>
                        <td style="text-align:right; color:{diff_col_tot}; font-size:12.5px;">₹{diff_tot:,.0f}</td>
                    </tr>
                    <tr style="background:#f1f5f9; font-weight:bold;">
                        <td><b>૧૨. આખર ક્લોઝિંગ સિલક (Final Closing)</b></td>
                        <td style="text-align:right; color:#0f2043;">₹{cnt_g1:,.0f}</td>
                        <td style="text-align:right; color:#0f2043;">₹{cnt_g2:,.0f}</td>
                        <td style="text-align:right; color:#0f2043;">₹{cnt_g3:,.0f}</td>
                        <td style="text-align:right; color:#0f2043;">₹{cnt_g4:,.0f}</td>
                        <td style="text-align:right; color:#0f2043; font-size:12.5px;">₹{(cnt_g1+cnt_g2+cnt_g3+cnt_g4):,.0f}</td>
                    </tr>
                </tbody>
            </table>
        </div>
    </div>

    <div style="padding:0 8px 12px;">
        <div style="background:white; border:1px solid #cbd5e1; border-radius:6px; padding:12px;">
            <h4 style="margin:0 0 8px 0; color:#6b21a8;">🔐 ૨. ૪-ગલ્લા ઓપનિંગ-ક્લોઝિંગ & ક્યુમ્યુલેટિવ વૉલ્ટ (અનામત કેશ) મેળવણી સમરી</h4>
            <table class="live-grid">
                <tr>
                    <th style="background:#f1f5f9; color:#1e293b;">ગલ્લાનું નામ</th>
                    <th style="background:#f1f5f9; color:#1e293b;">ઓપનિંગ ₹</th>
                    <th style="background:#f1f5f9; color:#16a34a;">આજની આવક (+)</th>
                    <th style="background:#f1f5f9; color:#dc2626;">જાવક/ડિપોઝિટ (-)</th>
                    <th style="background:#fef9c3; color:#854d0e;">અપેક્ષિત ક્લોઝિંગ (=)</th>
                    <th style="background:#f1f5f9; color:#0284c7;">ગણેલી નોટો (T1+T2)</th>
                    <th style="background:#f1f5f9; color:#1e293b;">તફાવત (Diff)</th>
                </tr>
                {vault_recon_rows}
            </table>
        </div>
    </div>

    <script>
        function recalcGallaTbl(tblId){{
            var f = document.getElementById(tblId);
            var gList = ['BANK_CASH', 'ACC_DCASH', 'RECHARGE', 'EXTRA_CASH'];
            var mults = [['n500',500], ['n200',200], ['n100',100], ['n50',50], ['n20',20], ['n10',10], ['coins',1]];
            gList.forEach(function(g){{
                var total = 0;
                mults.forEach(function(m){{
                    var el = f.querySelector('input[name="' + m[0] + '_' + g + '"]');
                    if(el) total += (parseInt(el.value) || 0) * m[1];
                }});
                var td = document.getElementById(tblId + '_sum_' + g);
                if(td) td.innerText = '₹' + total.toLocaleString('en-IN');
            }});
        }}
        document.querySelectorAll('#f8_t1, #f8_t2').forEach(function(tblForm){{
            var tblId = tblForm.id;
            for(var c=1; c<=4; c++){{
                (function(colNum){{
                    var colInputs = Array.from(tblForm.querySelectorAll('input.vjump[data-col="' + colNum + '"]'));
                    var saveBtn = document.getElementById(tblId + '_btn_' + colNum);
                    colInputs.forEach(function(inp, idx){{
                        inp.addEventListener('keydown', function(e){{
                            if(e.key === 'Enter'){{
                                e.preventDefault();
                                var nextInp = colInputs[idx + 1];
                                if(nextInp){{
                                    nextInp.focus();
                                    nextInp.select();
                                }} else if(saveBtn) {{
                                    saveBtn.focus();
                                }}
                            }}
                        }});
                    }});
                }})(c);
            }}
        }});
    </script>
    """
