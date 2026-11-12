# -*- coding: utf-8 -*-
# =======================================================================================================================
# ⚠️ આવશ્યક એઆઈ ડાયરેક્ટિવ અને ડાયનામિક રૂલબુક ગવર્નન્સ (કાયમી અમર એઆઈ હેડર - માસ્ટર ૧૦ લોજિક અને મલ્ટી-સ્ટોર SaaS આવૃત્તિ)
# =======================================================================================================================
# [કડક ચેતવણી - Gemini, ChatGPT, Claude, Cursor અથવા અન્ય કોઈપણ AI મોડેલ અને ડેવલપર માટે બંધનકર્તા આદેશ]:
# ૧. આ હેડર 'અમર' (Immortal) છે. આ ફાઇલ part2_b_counters.py છે (F1 થી F4 કાઉન્ટર્સ + Universal 360 Search).
# ૨. જૂના કોડનું એક પણ ફંક્શન, ડ્રોપડાઉન, ગાણિતિક સૂત્ર કે CRUD બટન કાઢવું સખત પ્રતિબંધિત છે.
# =======================================================================================================================

import json
import urllib.parse
import part2_c_counters_extra

def build_4galla_select(name_attr, default_galla="BANK_CASH", extra_style=""):
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
    return f'<select name="{name_attr}" style="font-weight:bold; color:#15803d; background:#f0fdf4; {extra_style}">{opts}</select>'

def render_smart_terminal(
    conn, c, mode, f4_sm_filter, staff_list, party_db_rows, cat_opts,
    bb_stock_opts, dos, pending_apx_bills, stock_inward_map, current_bill,
    all_galla_options, bank_opts, exp_heads, today_str, shop_prof=None
):
    st_mode = (shop_prof or {}).get("store_mode", "FRANCHISE_HO")
    acc_p2_enabled = bool((shop_prof or {}).get("accessories_part2_active", False))
    comm_enabled = bool((shop_prof or {}).get("custom_comm_enabled", True))
    comm_deduct = float((shop_prof or {}).get("custom_comm_deduction", 500.0))
    comm_pct = float((shop_prof or {}).get("custom_comm_pct", 20.0))

    active_counters = (shop_prof or {}).get("active_counters") or ["F1", "F2", "F3", "F4", "F5", "F6", "F7", "F8"]
    active_subparts = (shop_prof or {}).get("active_subparts") or [
        "F1_1","F1_2","F1_3","F1_5",
        "F2_1","F2_2","F2_3",
        "F3_1","F3_2","F3_3","F3_4","F3_5","F3_6",
        "F4_1","F4_2",
        "F5_1","F5_2","F5_3","F5_4",
        "F6_1",
        "F7_1","F7_2","F7_3",
        "F8_1","F8_2","F8_3"
    ]
    staff_opts_html = "".join([f'<option value="{s}">{s}</option>' for s in staff_list]) or '<option value="">-- નવો સેલ્સમેન / સ્ટાફ પસંદ કરો (શીટ ૧૩ અથવા ૧૮) --</option>'
    party_opts_html = "".join([f'<option value="{r[1]}">{r[1]}</option>' for r in party_db_rows]) or '<option value="">-- [+ નવો વેપારી] બટનથી ઉમેરો --</option>'
    cat_opts_html = "".join([f'<option value="{ct}">{ct}</option>' for ct in cat_opts]) or '<option value="મોબાઈલ હેન્ડસેટ">-- નવી કેટેગરી ઉમેરો --</option>'
    bank_opts_html = "".join([f'<option value="{b}">{b}</option>' for b in bank_opts]) or '<option value="">-- નવું બેંક ખાતું ઉમેરો --</option>'
    exp_opts_html = "".join([f'<option value="{h}">{h}</option>' for h in exp_heads]) or '<option value="પરચૂરણ ખર્ચ">-- નવું ખર્ચ ખાતું ઉમેરો --</option>'
    c.execute("SELECT brand_name FROM config_brands ORDER BY id ASC")
    brand_db_rows = [r[0] for r in c.fetchall()]
    brand_opts_html = "".join([f'<option value="{b}">{b}</option>' for b in brand_db_rows]) or '<option value="">-- નવી બ્રાન્ડ ઉમેરો (શીટ ૧૮ માંથી) --</option>'


    # સ્તર ૬: F1 થી F8 કાઉન્ટર બટનો (એક જ આડી સિંગલ લાઈનમાં - 8 columns)
    f_buttons_meta = [
        ("F1", "#15803d", "[F1] ખરીદી ડેસ્ક"),
        ("F2", "#0f2043", "[F2] વેચાણ સેટલમેન્ટ"),
        ("F3", "#4c1d95", "[F3] ઓલ-ઇન-વન લેજર & ખર્ચા"),
        ("F4", "#0369a1", "[F4] બેંક ડિપોઝિટ & વિડ્રોલ"),
        ("F5", "#991b1b", "[F5] બાય-બેક & રિપેરિંગ"),
        ("F6", "#b45309", "[F6] ગલ્લા ટ્રાન્સફર"),
        ("F7", "#1e3a8a", "[F7] એક્સ્ટ્રા પ્રોફિટ & રિપેરિંગ"),
        ("F8", "#0f766e", "[F8] ૪-ગલ્લા ઓડિટ")
    ]
    vis_f = [(fc, fcol, flbl) for fc, fcol, flbl in f_buttons_meta if fc in active_counters]
    f_strip_html = f'<div class="f-counters-grid" style="display:grid; grid-template-columns:repeat({max(1, len(vis_f))}, 1fr); gap:4px; padding:6px 8px; background:#0f172a; border-bottom:2px solid #0284c7;">' + "".join([
        f'<a href="/?sheet=SMART_TERMINAL&mode={fc}" class="f-btn" style="background:{fcol}; border:{("2px solid #38bdf8; box-shadow:0 0 8px rgba(56,189,248,0.7);" if mode==fc else "2px solid transparent")};">{flbl}</a>'
        for fc, fcol, flbl in vis_f
    ]) + '</div>'

    form_html = ""

    # =========================================================================
    # [F1] ખરીદી મોડ્યુલ (Purchase Desk - AI ઓટો-રીડિંગ અને ૫ ડ્રોપ-ડાઉન વિકલ્પો)
    # =========================================================================
    if mode == "F1":
        galla_sel_g1 = build_4galla_select("galla_name", "BANK_CASH")
        galla_sel_g2 = build_4galla_select("acc_galla_name", "ACC_DCASH")
        galla_sel_g3 = build_4galla_select("rech_galla_name", "RECHARGE")

        acc_part2_badge = (
            '<span style="background:#dcfce7; color:#15803d; padding:2px 8px; border-radius:4px; font-size:11px;">✅ એસેસરીઝ પાર્ટ-૨ (૧-૧ નંગ બારકોડ) સક્રિય</span>'
            if acc_p2_enabled else
            '<span style="background:#fef3c7; color:#b45309; padding:2px 8px; border-radius:4px; font-size:11px;">🔒 સ્ટાન્ડર્ડ એસેસરીઝ મોડ (પાર્ટ-૨ અનલૉક માટે જયમીનભાઈ: 9725721215)</span>'
        )

        form_html = f"""
        
            <div style="display:flex; gap:6px; align-items:center; flex-wrap:wrap; margin:6px 0;">
                <button type="button" onclick="startGujaratiVoiceBilling()" id="f2_voice_btn" style="background:linear-gradient(135deg, #7c3aed, #6d28d9); color:white; border:none; padding:5px 12px; border-radius:5px; font-weight:bold; font-size:12px; cursor:pointer; display:inline-flex; align-items:center; gap:5px; box-shadow:0 2px 4px rgba(109,40,217,0.3);">🎤 બોલીને બિલ બનાવો (ગુજરાતી)</button>
                <button type="button" onclick="openOnlinePriceSpyModal(document.getElementById('f2_mod') ? document.getElementById('f2_mod').value : '', document.getElementById('f2_mop') ? document.getElementById('f2_mop').value : 0)" style="background:linear-gradient(135deg, #ea580c, #c2410c); color:white; border:none; padding:5px 12px; border-radius:5px; font-weight:bold; font-size:12px; cursor:pointer; display:inline-flex; align-items:center; gap:5px; box-shadow:0 2px 4px rgba(234,88,12,0.3);">🛒 ઓનલાઈન MOP & બેંક ઓફર્સ</button>
                <button type="button" onclick="generateSalesmanClosingPitch()" style="background:linear-gradient(135deg, #0284c7, #0369a1); color:white; border:none; padding:5px 12px; border-radius:5px; font-weight:bold; font-size:12px; cursor:pointer; display:inline-flex; align-items:center; gap:5px;">🧠 AI સેલ્સ ક્લોઝિંગ પિચ</button>
                <span style="font-size:11px; background:#0f172a; color:#38bdf8; padding:4px 8px; border-radius:4px; margin-left:auto;">🚶‍♂️ આજનો સ્ટોર ફૂટફોલ: 14 | 🧾 બિલ: 8 | 🎯 કન્વર્ઝન: 57.1%</span>
            </div>

        <div class="mode-banner">
            <span>મોડ: [F1] ખરીદી મોડ્યુલ (AI ઓટો-રીડિંગ + ભાવ તફાવત એલર્ટ + ૫ ડ્રોપ-ડાઉન વિકલ્પો)</span>
            <div>
                <button type="button" onclick="document.getElementById('stock_import_file').click()" style="background:#0284c7; color:white; border:none; padding:5px 12px; border-radius:4px; font-weight:bold; cursor:pointer; font-size:11.5px;">📥 ખરીદી બિલ PDF / Excel / ફોટો AI ઇમ્પોર્ટ</button>
            </div>
        </div>

        <!-- ચાલુ ટેબલે [+ નવો વેપારી] ઉમેરવાનું બોક્સ -->
        <div id="quick_party_box" style="display:none; background:#f0f9ff; border:2px solid #0284c7; padding:10px; margin:8px; border-radius:6px; max-width:980px;">
            <form action="/add-party" method="post" style="display:flex; gap:6px; align-items:center; flex-wrap:wrap;">
                <input type="hidden" name="return_sheet" value="SMART_TERMINAL">
                <input type="text" name="party_name" placeholder="નવા વેપારીનું નામ..." required style="padding:6px; flex:1;">
                <input type="text" name="gstin" id="qp_gstin" placeholder="૧૫-અંક GSTIN (ઓટો-સર્ચ)" onblur="autoLookupGstin(this.value, 'qp')" style="padding:6px; width:160px;">
                <input type="text" name="mobile" placeholder="૧૦-અંક મોબાઈલ" style="padding:6px; width:130px;">
                <input type="text" name="address" id="qp_addr" placeholder="પૂરું સરનામું" style="padding:6px; flex:1;">
                <select name="category" style="padding:6px;">{cat_opts_html}</select>
                <button type="submit" style="background:#16a34a; color:white; border:none; padding:6px 14px; font-weight:bold; border-radius:4px; cursor:pointer;">+ વેપારી સેવ કરો</button>
                <button type="button" onclick="document.getElementById('quick_party_box').style.display='none'" style="background:#dc2626; color:white; border:none; padding:6px 10px; border-radius:4px; cursor:pointer;">✖</button>
            </form>
        </div>

        <form class="term-form f-enter-form" action="/save-f1" method="post" enctype="multipart/form-data">
            <div class="f-row"><div class="lbl">૧. તારીખ (ઓટો / મેન્યુઅલ):</div><input type="date" name="entry_date" value="{today_str}"></div>
            <div class="f-row" style="background:#e0f2fe; padding:5px; border-radius:4px;">
                <div class="lbl" style="color:#0369a1;">૨. ખરીદી પ્રકાર (૫ વિકલ્પો):</div>
                <select name="tx_type" id="f1_tx" onchange="toggleF1Mode()" style="font-weight:bold; color:#0f2043;">
                    {"".join([
                        opt_html for sub_k, opt_html in [
                            ("F1_1", '<option value="PURCHASE">વિકલ્પ (૧): નવો મોબાઈલ સ્ટોક ખરીદી (Mobile Handset Inward - ૧૫ ખાનાં)</option>'),
                            ("F1_2", '<option value="CONSUMER_PURCHASE">વિકલ્પ (૨): અન્ય કન્ઝ્યુમર પ્રોડક્ટ્સ ખરીદી (TV, AC, લેપટોપ, ટેબ્લેટ - ૧૫ ખાનાં)</option>'),
                            ("F1_3", '<option value="DIRECT_BB">વિકલ્પ (૩): ફ્રેન્ચાઇઝી / ડાયરેક્ટ એક્સચેન્જ જૂના ફોન ખરીદી (Direct Exchange / Buyback - ૯ ખાનાં)</option>'),
                            ("F1_5", '<option value="ACC_PURCHASE">વિકલ્પ (૪): એસેસરીઝ ખરીદી (સ્ટાન્ડર્ડ લમ્પ-સમ ખરીદી / સ્પેશિયલ પાર્ટ-૨ બારકોડ મોડ)</option>')
                        ] if sub_k in active_subparts
                    ]) or '<option value="PURCHASE">વિકલ્પ (૧): નવો મોબાઈલ સ્ટોક ખરીદી</option>'}
                </select>
            </div>

            <!-- વિકલ્પ (૧) અને (૨): મોબાઈલ ખરીદી / કન્ઝ્યુમર પ્રોડક્ટ્સ ખરીદી (૧૫ ખાનાં) -->
            <div id="f1_supplier_block">
                <div class="f-row">
                    <div class="lbl">૩. બિલિંગ પ્રકાર (B2B / B2C):</div>
                    <select name="b2b_type" id="f1_b2b" style="max-width:220px;">
                        <option value="B2B">B2B (GST નંબરવાળા વેપારી)</option>
                        <option value="B2C">B2C (સામાન્ય બિલ)</option>
                    </select>
                    <input type="text" name="supplier_gstin" id="f1_gstin" placeholder="૧૫-અંક GSTIN નાખી ઓટો-સર્ચ કરો અથવા હાથેથી લખો..." onblur="autoLookupGstin(this.value, 'f1')" style="flex:1;">
                    <button type="button" onclick="autoLookupGstin(document.getElementById('f1_gstin').value, 'f1')" style="background:#0284c7; color:white; border:none; padding:6px 12px; border-radius:4px; font-weight:bold; cursor:pointer; font-size:11.5px;">🔍 GSTIN સર્ચ (Auto-Fetch)</button>
                </div>
                <div class="f-row">
                    <div class="lbl">૪. વેપારી / સપ્લાયર નામ:</div>
                    <select name="supplier_name" id="f1_supp_sel" style="flex:1;">{party_opts_html}</select>
                    <button type="button" onclick="document.getElementById('quick_party_box').style.display='block'" style="background:#16a34a; color:white; border:none; padding:6px 12px; border-radius:4px; font-weight:bold; cursor:pointer;">[+ નવો વેપારી]</button>
                </div>
                <div class="f-row"><div class="lbl">૫. બિલ / ઇનવોઇસ નંબર:</div><input type="text" name="bill_no" placeholder="AI ઓટો-રીડ અથવા મેન્યુઅલ બિલ નંબર..."></div>
                <div class="f-row">
                    <div class="lbl">૬. બ્રાન્ડ અને મોડેલ નામ:</div>
                    <select name="brand" id="f1_brand_inp" style="max-width:165px; font-weight:bold;">{brand_opts_html}</select>
                    <button type="button" onclick="openInlineQuickCreateModal('BRAND', 'f1_brand_inp')" style="background:#0d9488; color:white; border:none; padding:6px 9px; border-radius:4px; font-weight:bold; cursor:pointer; font-size:11px;">[+ નવી બ્રાન્ડ]</button>
                    <input type="text" name="model" id="f1_mod_inp" list="f1_model_datalist" oninput="checkF1PriceDiff(); autoFetchOfficialMopAndGstF1();" placeholder="મોડેલ નામ લખો (દા.ત. Vivo V29e 5G 8/128) - ઓફિશિયલ MOP & GST આપોઆપ આવશે" style="flex:1; font-weight:bold;">
                    <button type="button" onclick="promptNewModelInlineF1()" style="background:#7c3aed; color:white; border:none; padding:6px 9px; border-radius:4px; font-weight:bold; cursor:pointer; font-size:11px;">[+ નવું મોડેલ]</button>
                    <datalist id="f1_model_datalist">
                        <option value="Vivo V29e 5G (8GB/128GB) Arctic Red">
                        <option value="Vivo V30 5G (8GB/128GB) Peacock Green">
                        <option value="Vivo Y200 5G (8GB/128GB) Jungle Green">
                        <option value="Vivo Y28 5G (6GB/128GB) Crystal Purple">
                        <option value="Samsung Galaxy A15 5G (8GB/128GB) Blue">
                        <option value="Samsung Galaxy A35 5G (8GB/128GB) Navy">
                        <option value="Samsung Galaxy S24 Ultra 5G (12GB/256GB)">
                        <option value="Oppo F25 Pro 5G (8GB/128GB) Lava Red">
                        <option value="Oppo Reno 11 5G (8GB/128GB) Wave Green">
                        <option value="Realme 12 Pro 5G (8GB/128GB) Submarine Blue">
                        <option value="OnePlus Nord CE 4 5G (8GB/128GB) Celadon Marble">
                        <option value="Apple iPhone 15 (128GB) Black">
                    </datalist>
                </div>
                <div class="f-row">
                    <div class="lbl">૭. ૧૫-અંક IMEI / સિરિયલ નંબર:</div>
                    <input type="text" name="imei" placeholder="AI ઓટો-રીડ / બલ્ક બારકોડ ગન સ્કેન / મેન્યુઅલ ટાઇપિંગ (સીધા In-Stock માં જમા)">
                </div>
                <div class="f-row">
                    <div class="lbl">૮. ખરીદ પડતર કિંમત (DP ₹):</div>
                    <input type="number" step="any" name="total_bill" id="f1_dp_inp" oninput="checkF1PriceDiff(); calcF1Gst();" value="0" style="font-weight:bold; color:#0f2043;">
                </div>
                <!-- ખરીદી ભાવ તફાવત એલર્ટ બોક્સ -->
                <div id="f1_price_diff_box" style="display:none; background:#fef3c7; border:2px solid #ca8a04; padding:8px 12px; margin:4px 0 6px 243px; border-radius:6px; font-size:12px; color:#854d0e; font-weight:bold;"></div>

                <div class="f-row">
                    <div class="lbl">૯. ઓટો-GST ટેક્સ (% અને ₹):</div>
                    <select name="gst_pct" id="f1_gst_pct" onchange="calcF1Gst()" style="max-width:260px;">
                        <option value="18">૧૮% GST (૯% CGST + ૯% SGST - મોબાઈલ/IT)</option>
                        <option value="28">૨૮% GST (૧૪% CGST + ૧૪% SGST - 42"+ TV/AC)</option>
                        <option value="5">૫% GST (ગિફ્ટ / પરચૂરણ)</option>
                        <option value="0">૦% (Exempt / Without GST)</option>
                    </select>
                    <input type="text" id="f1_gst_info" readonly value="CGST: ₹0 | SGST: ₹0" style="background:#f1f5f9; font-weight:bold; color:#0369a1;">
                </div>
                <div class="f-row"><div class="lbl">૧૦. કંપની સ્કીમ / કેશબેક / CN (₹):</div><input type="number" step="any" name="scheme_cn_amt" value="0" placeholder="કંપની સ્કીમ કે ક્રેડિટ નોટ રકમ..."></div>
                <div class="f-row">
                    <div class="lbl">૧૧. ઓફિશિયલ વેચાણ ભાવ (MOP ₹):</div>
                    <button type="button" onclick="openOnlinePriceSpyModal(document.getElementById('f1_mod_inp') ? document.getElementById('f1_mod_inp').value : '', document.getElementById('f1_mop_inp') ? document.getElementById('f1_mop_inp').value : 0)" style="background:linear-gradient(135deg, #ea580c, #c2410c); color:white; border:none; padding:4px 8px; border-radius:4px; font-weight:bold; font-size:11px; cursor:pointer;" title="Amazon / Flipkart / Brand e-Store લાઈવ MOP ચેક કરો">🛒 લાઈવ MOP</button> <input type="number" step="any" name="mop_rate" id="f1_mop_inp" value="0" placeholder="ઓફિશિયલ બ્રાન્ડ પોર્ટલ પરથી ઓટો-MOP (અથવા હાથેથી લખો)..." style="font-weight:bold; color:#15803d; flex:1;">
                    <button type="button" onclick="autoFetchOfficialMopAndGstF1(true)" style="background:#0284c7; color:white; border:none; padding:6px 10px; border-radius:4px; font-weight:bold; cursor:pointer; font-size:11px;">🌐 ઓફિશિયલ બ્રાન્ડ MOP લાવો</button>
                </div>
                <div class="f-row"><div class="lbl">૧૨. અત્યારે રોકડા ચૂકવ્યા (₹):</div><input type="number" step="any" name="paid_amt" value="0" placeholder="રોકડ ચૂકવેલ રકમ (બાકી રકમ આપોઆપ વેપારી લેજરમાં બાકી બોલશે)..."></div>
                <div class="f-row" style="background:#fff1f2; padding:4px 6px; border-radius:4px; border:1px dashed #e11d48;">
                    <div class="lbl" style="color:#be123c;">૧૨(B). વેપારી પેમેન્ટ ક્રેડિટ મુદત & ડ્યુ-ડેટ એલર્ટ:</div>
                    <select name="credit_days" id="f1_credit_days" onchange="calcF1VendorDueDate()" style="max-width:210px; font-weight:bold; color:#9f1239;">
                        <option value="0">રોકડ / તાત્કાલિક (0 દિવસ)</option>
                        <option value="7" selected>૭ દિવસ ક્રેડિટ (7 Days)</option>
                        <option value="15">૧૫ દિવસ ક્રેડિટ (15 Days)</option>
                        <option value="30">૩૦ દિવસ ક્રેડિટ (30 Days)</option>
                        <option value="45">૪૫ દિવસ ક્રેડિટ (45 Days)</option>
                    </select>
                    <span style="font-weight:bold; color:#881337; font-size:12px;">ચૂકવણી છેલ્લી તારીખ (Due Date):</span>
                    <input type="date" name="due_date" id="f1_vendor_due_date" value="{today_str}" style="max-width:170px; font-weight:bold; color:#dc2626;">
                </div>
                <script>
                    function calcF1VendorDueDate() {{
                        try {{
                            var days = parseInt(document.getElementById('f1_credit_days').value || '7');
                            var dInp = document.querySelector('input[name="entry_date"]');
                            var baseD = dInp && dInp.value ? new Date(dInp.value) : new Date();
                            baseD.setDate(baseD.getDate() + days);
                            var iso = baseD.toISOString().slice(0,10);
                            var dueEl = document.getElementById('f1_vendor_due_date');
                            if (dueEl) dueEl.value = iso;
                        }} catch(e) {{}}
                    }}
                    setTimeout(calcF1VendorDueDate, 120);
                </script>
            </div>

            <!-- વિકલ્પ (૩): જૂના બાય-બેક ફોનની ડાયરેક્ટ ખરીદી (૯ ખાનાં + ૮ કંડિશન + ગ્રાહક ફોટો) -->
            <div id="f1_bb_block" style="display:none; background:#f0fdf4; border:1px solid #16a34a; padding:10px; border-radius:6px; margin-bottom:6px;">
                <div class="f-row"><div class="lbl">૨. ગ્રાહકનું નામ અને મોબાઈલ:</div>
                    <input type="text" name="customer_name" placeholder="વેચનાર ગ્રાહકનું પૂરું નામ" style="flex:1;">
                    <input type="text" name="customer_phone" maxlength="10" placeholder="૧૦-અંક મોબાઈલ નંબર" style="max-width:180px;">
                </div>
                <div class="f-row"><div class="lbl">૩. જૂના ફોનનું બ્રાન્ડ અને મોડેલ:</div>
                    <select name="bb_brand" style="max-width:160px; font-weight:bold;">{brand_opts_html}</select>
                    <input type="text" name="bb_model" placeholder="દા.ત. Vivo Y20 (4/64)" style="flex:1;">
                </div>
                <div class="f-row"><div class="lbl">૪. ૧૫-અંક IMEI & ૮ કંડિશન:</div>
                    <input type="text" name="bb_imei" maxlength="15" placeholder="૧૫-અંક IMEI નંબર (ડુપ્લિકેટ ઓટો-લોક)" style="flex:1;">
                    <select name="bb_condition" style="max-width:310px; font-weight:bold;">
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
                <div class="f-row"><div class="lbl">૫. ખરીદ કિંમત (Buyback ₹):</div><input type="number" step="any" name="bb_cost" value="0" style="font-weight:bold; color:#15803d;"></div>
                <div class="f-row"><div class="lbl">૬. 📷 ગ્રાહકનો લાઈવ ફોટો પાડો:</div><input type="file" name="customer_face_photo" accept="image/*" capture="user"></div>
                <div class="f-row"><div class="lbl">૭. ખરીદનાર સ્ટાફ / સેલ્સમેન:</div><select name="salesman">{staff_opts_html}</select></div>
            </div>

            <!-- વિકલ્પ (૫): એસેસરીઝ ખરીદી (સ્ટાન્ડર્ડ મોડ + સ્પેશિયલ પેઇડ 'પાર્ટ-૨' મોડ) -->
            <div id="f1_acc_block" style="display:none; background:#f0f9ff; border:1px solid #0284c7; padding:10px; border-radius:6px; margin-bottom:6px;">
                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
                    <b style="color:#0369a1;">૫. એસેસરીઝ ખરીદી મોડ્યુલ:</b>
                    {acc_part2_badge}
                </div>
                <div class="f-row">
                    <div class="lbl">એસેસરીઝ મોડ પસંદગી:</div>
                    <select name="acc_sub_mode" id="f1_acc_submode" onchange="toggleAccPart2Fields()">
                        <option value="STANDARD">સ્ટાન્ડર્ડ મોડ (સામાન્ય દુકાનદાર માટે - લમ્પ-સમ કુલ બિલ)</option>
                        <option value="PART2" {"selected" if acc_p2_enabled else ""}>સ્પેશિયલ પેઇડ 'પાર્ટ-૨' મોડ (૧-૧ નંગ વાઇઝ બારકોડ ટ્રેકિંગ)</option>
                    </select>
                </div>
                <div class="f-row"><div class="lbl">વેપારીનું નામ & બિલ નંબર:</div>
                    <select name="acc_supplier" style="flex:1;">{party_opts_html}</select>
                    <input type="text" name="acc_bill_no" placeholder="બિલ નંબર" style="max-width:200px;">
                </div>
                <div id="f1_acc_part2_rows" style="display:{'block' if acc_p2_enabled else 'none'}; background:#e0f2fe; padding:8px; border-radius:4px; margin:6px 0;">
                    <div class="f-row"><div class="lbl">એસેસરીઝ કેટેગરી ડ્રોપ-ડાઉન:</div>
                        <select name="acc_category">
                            <option value="ટેમ્પરર્ડ ગ્લાસ">ટેમ્પરર્ડ ગ્લાસ (Tempered Glass)</option>
                            <option value="બેક કવર">બેક કવર (Back Cover)</option>
                            <option value="ફાસ્ટ ચાર્જર">ફાસ્ટ ચાર્જર (Charger)</option>
                            <option value="ડેટા કેબલ">ડેટા કેબલ (Data Cable)</option>
                            <option value="એરબડ્સ / નેકબેન્ડ">એરબડ્સ / નેકબેન્ડ</option>
                            <option value="સ્પીકર / પાવરબેંક">સ્પીકર / પાવરબેંક</option>
                        </select>
                    </div>
                    <div class="f-row"><div class="lbl">આઇટમ નામ & ૧-૧ નંગ બારકોડ:</div>
                        <input type="text" name="acc_item_name" placeholder="આઇટમ નામ (દા.ત. 11D Glass Vivo Y200)" style="flex:1;">
                        <input type="text" name="acc_barcode" placeholder="બારકોડ સ્કેન / કોડ" style="max-width:200px;">
                    </div>
                    <div class="f-row"><div class="lbl">નંગ (Qty), પડતર (₹) & વેચાણ ભાવ:</div>
                        <input type="number" name="acc_qty" id="acc_qty_inp" value="10" oninput="calcAccTot()" placeholder="નંગ (Qty)">
                        <input type="number" step="any" name="acc_unit_cost" id="acc_uc_inp" value="0" oninput="calcAccTot()" placeholder="પ્રતિ નંગ પડતર (₹)">
                        <input type="number" step="any" name="acc_mop" value="0" placeholder="વેચાણ ભાવ (MOP ₹)">
                    </div>
                </div>
                <div class="f-row"><div class="lbl">કુલ એસેસરીઝ ખરીદી રકમ (₹):</div><input type="number" step="any" name="acc_total_amt" id="acc_tot_inp" value="0" style="font-weight:bold;"></div>
                <div class="f-row"><div class="lbl">અત્યારે ચૂકવેલ રકમ (₹):</div><input type="number" step="any" name="acc_paid_amt" value="0"></div>
            </div>

            <div class="f-row" style="background:#f0fdf4; padding:4px; border:1px solid #86efac; border-radius:4px;">
                <div class="lbl" style="color:#15803d;">૧૩. ચૂકવણી પદ્ધતિ (MOP) & રોકડ ગલ્લો:</div>
                <select name="pay_mode" id="f1_pay_mode" onchange="document.getElementById('f1_galla_wrap').style.display=(this.value.indexOf('રોકડ')!==-1?'flex':'none')" style="max-width:230px; font-weight:bold; color:#0f2043;">
                    <option value="રોકડ (Cash)">૧. રોકડ (Cash - ગલ્લામાંથી)</option>
                    <option value="ઓનલાઈન UPI / QR">૨. ઓનલાઈન UPI / QR (બેંક ખાતામાંથી)</option>
                    <option value="બેંક ટ્રાન્સફર (NEFT/IMPS)">૩. બેંક ટ્રાન્સફર (NEFT/RTGS/IMPS)</option>
                    <option value="ક્રેડિટ/ડેબિટ કાર્ડ">૪. ક્રેડિટ / ડેબિટ કાર્ડ</option>
                </select>
                <div id="f1_galla_wrap" style="display:flex; flex:1;">{galla_sel_g1}</div>
            </div>
            <div class="f-row" style="background:#e0f2fe; padding:5px; border-radius:4px;">
                <div class="lbl">૧૪. બિલ / આધાર / ફોન ફોટા અપલોડ:</div>
                <input type="file" name="bb_photo" multiple>
            </div>
            <div class="btn-wrap"><button type="submit" class="btn-save" style="background:#15803d;">૧૫. [ સાચવો F1 ખરીદી (Enter -> Accept? Yes/No) ]</button></div>
        </form>

        <script>
            setTimeout(function(){{ if(typeof toggleF1Mode === 'function') toggleF1Mode(); }}, 20);
            function toggleF1Mode(){{
                var v = document.getElementById('f1_tx').value;
                document.getElementById('f1_supplier_block').style.display = (v === 'PURCHASE' || v === 'CONSUMER_PURCHASE') ? 'block' : 'none';
                document.getElementById('f1_bb_block').style.display = (v === 'DIRECT_BB') ? 'block' : 'none';
                
                document.getElementById('f1_acc_block').style.display = (v === 'ACC_PURCHASE') ? 'block' : 'none';
                var gSel = document.querySelector('select[name="galla_name"]');
                if(gSel){{
                    if(v === 'RECHARGE_PURCHASE') gSel.value = 'RECHARGE';
                    else if(v === 'ACC_PURCHASE') gSel.value = 'ACC_DCASH';
                    else gSel.value = 'BANK_CASH';
                }}
            }}
            function toggleAccPart2Fields(){{
                var sm = document.getElementById('f1_acc_submode').value;
                document.getElementById('f1_acc_part2_rows').style.display = (sm === 'PART2') ? 'block' : 'none';
            }}
            function calcAccTot(){{
                var q = parseFloat(document.getElementById('acc_qty_inp').value) || 0;
                var uc = parseFloat(document.getElementById('acc_uc_inp').value) || 0;
                if(q > 0 && uc > 0) document.getElementById('acc_tot_inp').value = Math.round(q * uc);
            }}
            function calcF1Gst(){{
                var dp = parseFloat(document.getElementById('f1_dp_inp').value) || 0;
                var pct = parseFloat(document.getElementById('f1_gst_pct').value) || 0;
                var taxable = pct > 0 ? (dp / (1 + (pct/100.0))) : dp;
                var totGst = dp - taxable;
                var half = totGst / 2.0;
                document.getElementById('f1_gst_info').value = 'Taxable: ₹' + taxable.toFixed(0) + ' | CGST: ₹' + half.toFixed(1) + ' + SGST: ₹' + half.toFixed(1);
            }}
            function applyOldDpF1(v){{ document.getElementById('f1_dp_inp').value = v; document.getElementById('f1_price_diff_box').style.display = 'none'; calcF1Gst(); }}
            function hideDiffBoxF1(){{ document.getElementById('f1_price_diff_box').style.display = 'none'; }}
            function promptNewModelInlineF1(){{
                var b = document.getElementById('f1_brand_inp').value || 'Vivo';
                var m = prompt('➕ ' + b + ' નું નવું મોડેલ નામ લખો (દા.ત. ' + b + ' V40 5G (8GB/128GB)):');
                if(m && m.trim()){{
                    var dl = document.getElementById('f1_model_datalist');
                    if(dl){{
                        var o = document.createElement('option');
                        o.value = m.trim();
                        dl.appendChild(o);
                    }}
                    document.getElementById('f1_mod_inp').value = m.trim();
                    autoFetchOfficialMopAndGstF1(true);
                }}
            }}
            function autoFetchOfficialMopAndGstF1(forceUpdate){{
                var mod = (document.getElementById('f1_mod_inp').value || '').trim();
                var dp = parseFloat(document.getElementById('f1_dp_inp').value) || 0;
                if(mod.length < 3) return;
                fetch('/api/lookup-model-mop-gst?model=' + encodeURIComponent(mod) + '&dp=' + dp)
                .then(r => r.json())
                .then(d => {{
                    if(d && d.brand){{
                        var bSel = document.getElementById('f1_brand_inp');
                        for(var i=0; i<bSel.options.length; i++){{
                            if(bSel.options[i].value.toLowerCase() === d.brand.toLowerCase()){{
                                bSel.selectedIndex = i;
                                break;
                            }}
                        }}
                    }}
                    if(d && d.gst_pct !== undefined){{
                        document.getElementById('f1_gst_pct').value = String(Math.round(d.gst_pct));
                        calcF1Gst();
                    }}
                    var mopEl = document.getElementById('f1_mop_inp');
                    if(mopEl && d.mop > 0 && (forceUpdate || !parseFloat(mopEl.value) || parseFloat(mopEl.value) === 0)){{
                        mopEl.value = d.mop;
                    }}
                }}).catch(()=>{{}});
            }}
            function checkF1PriceDiff(){{
                var mod = document.getElementById('f1_mod_inp').value.trim();
                var dp = parseFloat(document.getElementById('f1_dp_inp').value) || 0;
                var box = document.getElementById('f1_price_diff_box');
                if(!mod || dp <= 0){{ box.style.display = 'none'; return; }}
                fetch('/api/get-last-dp?model=' + encodeURIComponent(mod))
                .then(r => r.json())
                .then(d => {{
                    if(d.found && d.last_dp > 0 && Math.abs(d.last_dp - dp) >= 1){{
                        box.style.display = 'block';
                        box.innerHTML = '⚠️ ખરીદી ભાવ તફાવત એલર્ટ: આ મોડેલનો અગાઉનો છેલ્લો ખરીદ ભાવ ₹' + d.last_dp + ' હતો (વેપારી: ' + d.party + '). નવા ભાવે (₹' + dp + ') ખરીદી લેવી છે કે જૂના ભાવે રાખવી છે? ' +
                            '<button type="button" onclick="applyOldDpF1(' + d.last_dp + ')" style="background:#0f2043; color:white; border:none; padding:3px 8px; border-radius:3px; cursor:pointer; margin-left:6px;">[જૂનો ભાવ ₹' + d.last_dp + ' રાખો]</button>' +
                            '<button type="button" onclick="hideDiffBoxF1()" style="background:#16a34a; color:white; border:none; padding:3px 8px; border-radius:3px; cursor:pointer; margin-left:6px;">[નવો ભાવ ₹' + dp + ' માન્ય રાખો]</button>';
                    }} else {{ box.style.display = 'none'; }}
                }}).catch(()=>{{}});
            }}
            function autoLookupGstin(gstin, prefix){{
                var cleanG = (gstin || '').replace(/\\s+/g, '').toUpperCase();
                if(!cleanG || cleanG.length < 15){{
                    alert('⚠️ કૃપા કરીને પૂરો ૧૫-અંકનો GSTIN નંબર દાખલ કરો!');
                    return;
                }}
                fetch('/api/gstin-lookup?gstin=' + encodeURIComponent(cleanG))
                .then(r => r.json())
                .then(d => {{
                    if(d.found){{
                        if(prefix === 'qp'){{
                            document.querySelector('#quick_party_box input[name="party_name"]').value = d.trade_name;
                            document.getElementById('qp_addr').value = d.address;
                            alert('✅ GST વિગત મળી: ' + d.trade_name + ' (' + d.state + ')');
                        }} else if(prefix === 'f1'){{
                            var suppSel = document.getElementById('f1_supp_sel');
                            var foundOpt = false;
                            for(var i=0; i<suppSel.options.length; i++){{
                                if(suppSel.options[i].text.includes(d.trade_name)){{
                                    suppSel.selectedIndex = i;
                                    foundOpt = true;
                                    break;
                                }}
                            }}
                            if(!foundOpt){{
                                var opt = document.createElement('option');
                                opt.value = d.trade_name;
                                opt.text = d.trade_name + ' [GST Registered]';
                                opt.selected = true;
                                suppSel.add(opt);
                            }}
                            alert('✅ સપ્લાયર GST મળ્યો: ' + d.trade_name + ' | રાજ્ય: ' + d.state + ' | સ્ટેટસ: ' + d.status);
                        }}
                    }} else {{
                        alert('❌ આ GSTIN ની વિગત મળી નથી. કૃપા કરીને નંબર ચકાસો.');
                    }}
                }}).catch(()=>{{
                    alert('⚠️ GST પોર્ટલ સર્વર સાથે સંપર્ક થઈ શક્યો નથી.');
                }});
            }}
        </script>
        """

    # =========================================================================
    # [F2] વેચાણ અને પેમેન્ટ સ્પ્લિટ મોડ્યુલ (૩ ડાયનેમિક કન્ડિશનલ ફોર્મ્સ + ફ્રેન્ચાઇઝી વિ. રિટેલ)
    # =========================================================================
    elif mode == "F2":
        f2_banner_top = """<div style="background:linear-gradient(135deg, #0f172a 0%, #1e3a8a 100%); color:white; padding:8px 12px; border-radius:6px; margin:0 8px 8px; display:flex; justify-content:space-between; align-items:center; box-shadow:0 2px 8px rgba(0,0,0,0.15);">
            <div style="font-weight:bold; font-size:12px;">
                💡 <span style="color:#38bdf8;">નવા મોડ્યુલ્સ:</span> સેલ્સમેન 360° (ડિસ્કાઉન્ટ ટકાવારી & બ્રાન્ડ મેટ્રિક્સ) તથા ડે-બુક સ્નેપશોટ આર્કાઇવ
            </div>
            <div style="display:flex; gap:8px;">
                <a href="/?sheet=SALESMAN_360_MATRIX" style="background:#38bdf8; color:#0f172a; padding:4px 10px; border-radius:4px; text-decoration:none; font-weight:800; font-size:11px;">🖩 સેલ્સમેન 360° ખોલો</a>
                <a href="/?sheet=DAILY_SUMMARY" style="background:#10b981; color:white; padding:4px 10px; border-radius:4px; text-decoration:none; font-weight:800; font-size:11px;">📸 ડે-બુક સ્નેપશોટ ખોલો</a>
            </div>
        </div>"""
        apx_opts = '<option value="">-- પેન્ડિંગ સેલ્સ બિલ સિલેક્ટ કરો --</option>'
        for b in pending_apx_bills:
            b_addr = b[8] if len(b) > 8 else ""
            b_pin = b[9] if len(b) > 9 else ""
            apx_opts += f'<option value="{b[0]}" data-cust="{b[2]}" data-ph="{b[3]}" data-mod="{b[4]}" data-imei="{b[5]}" data-mop="{b[6]}" data-id="{b[7]}" data-addr="{b_addr}" data-pin="{b_pin}">{b[0]} | {b[2]} | {b[4]} (₹{b[6]:,.0f})</option>'

        do_opts = '<option value="" data-loan="0" data-net="0" data-scheme="" data-doc="" data-brand="Vivo" data-mod="" data-doref="" data-appid="" data-emi="0">-- પેન્ડિંગ ફાઇનાન્સ DO સિલેક્ટ કરો (12-Field Auto Fill) --</option>'
        for d in dos:
            net_v = float(d[7] or 0) if float(d[7] or 0) > 0 else float(d[4] or 0)
            d_addr = d[8] if len(d) > 8 else ""
            d_pin = d[9] if len(d) > 9 else ""
            d_doc = d[10] if len(d) > 10 else ""
            d_br = d[11] if len(d) > 11 and d[11] else "Vivo"
            d_md = d[12] if len(d) > 12 else ""
            d_ref = d[13] if len(d) > 13 else ""
            d_app = d[14] if len(d) > 14 else ""
            d_emi = float(d[15] or 0) if len(d) > 15 else 0.0
            do_opts += f'<option value="{d[0]}" data-comp="{d[1]}" data-loan="{d[4]}" data-net="{net_v}" data-cust="{d[2]}" data-imei="{d[3]}" data-ph="{d[5] or ""}" data-scheme="{d[6] or ""}" data-addr="{d_addr}" data-pin="{d_pin}" data-doc="{d_doc}" data-brand="{d_br}" data-mod="{d_md}" data-doref="{d_ref}" data-appid="{d_app}" data-emi="{d_emi}">{d[1]} | {d[2]} | DO: {d_ref or "-"} | MOP/Loan: ₹{d[4]:,.0f} | Net: ₹{net_v:,.0f}</option>'

        stock_json = json.dumps(stock_inward_map)
        galla_f2_sel = build_4galla_select("cash_galla", "BANK_CASH")

        # ફ્રેન્ચાઇઝી મોડ વિ. રિટેલ મોડ પેન્ડિંગ ડ્રોપ-ડાઉન બ્લોક
        if st_mode == "FRANCHISE_HO":
            pending_bar_html = f"""
            <div style="background:#fefce8; border:2px solid #eab308; padding:8px; border-radius:6px; margin-bottom:8px;">
                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:6px;">
                    <b style="color:#854d0e;">👑 ફ્રેન્ચાઇઝી સ્ટોર મોડ (સેલ્સ બિલ + ફાઇનાન્સ DO બંને બલ્ક ઇમ્પોર્ટ અને ઓટો-ક્રોસ-મેચિંગ):</b>
                    <div style="display:flex; gap:6px;">
                        <button type="button" onclick="document.getElementById('apx_import_file').click()" style="background:#d97706; color:white; border:none; padding:4px 10px; border-radius:4px; font-weight:bold; cursor:pointer; font-size:11px;">📥 બલ્ક સેલ્સ બિલ ઇમ્પોર્ટ</button>
                        <button type="button" onclick="document.getElementById('do_import_file').click()" style="background:#0284c7; color:white; border:none; padding:4px 10px; border-radius:4px; font-weight:bold; cursor:pointer; font-size:11px;">📥 બલ્ક ફાઇનાન્સ DO ઇમ્પોર્ટ (10-20 PDF)</button>
                    </div>
                </div>
                <div style="display:grid; grid-template-columns:1fr 1fr; gap:8px;">
                    <div style="display:flex; gap:4px; align-items:center;">
                        <select id="apx_sel" onchange="fillFromApx(true)" style="flex:1; padding:5px; font-weight:bold;">{apx_opts}</select>
                        <button type="button" onclick="unmatchApxSelection()" title="સેલ્સ બિલ અન-મેચ / રીસેટ કરો" style="background:#ca8a04; color:white; border:none; padding:5px 7px; border-radius:3px; cursor:pointer; font-weight:bold;">✖️</button>
                        <button type="button" onclick="deleteSelectedApx()" title="પેન્ડિંગ બિલ ડિલીટ કરો" style="background:#dc2626; color:white; border:none; padding:5px 7px; border-radius:3px; cursor:pointer; font-weight:bold;">🗑️</button>
                    </div>
                    <div style="display:flex; gap:4px; align-items:center;" id="f2_do_drop_wrap">
                        <select name="do_id" id="do_sel" onchange="fillFromDo(true)" style="flex:1; padding:5px; font-weight:bold;">{do_opts}</select>
                        <button type="button" onclick="previewSelectedDoPdf()" title="ઓરિજિનલ DO PDF જુઓ" style="background:#0284c7; color:white; border:none; padding:5px 7px; border-radius:3px; cursor:pointer; font-weight:bold;">👁️</button>
                        <button type="button" onclick="unmatchDoSelection()" title="DO અન-મેચ / રીસેટ કરો" style="background:#ca8a04; color:white; border:none; padding:5px 7px; border-radius:3px; cursor:pointer; font-weight:bold;">✖️</button>
                        <button type="button" onclick="deleteSelectedDo()" title="પેન્ડિંગ DO ડિલીટ કરો" style="background:#dc2626; color:white; border:none; padding:5px 7px; border-radius:3px; cursor:pointer; font-weight:bold;">🗑️</button>
                    </div>
                </div>
            </div>
            """
        else:
            pending_bar_html = f"""
            <div style="background:#e0f2fe; border:2px solid #0284c7; padding:8px; border-radius:6px; margin-bottom:8px;" id="f2_do_drop_wrap">
                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:6px;">
                    <b style="color:#0369a1;">🏪 પર્સનલ રિટેલ સ્ટોર મોડ (લાઈવ સ્ટોકમાંથી વેચાણ + બલ્ક ફાઇનાન્સ DO ઇમ્પોર્ટ):</b>
                    <button type="button" onclick="document.getElementById('do_import_file').click()" style="background:#0284c7; color:white; border:none; padding:4px 12px; border-radius:4px; font-weight:bold; cursor:pointer; font-size:11.5px;">📥 બલ્ક ફાઇનાન્સ DO ઇમ્પોર્ટ (10-20 PDF એકસાથે)</button>
                </div>
                <div style="display:flex; gap:6px; align-items:center;">
                    <span style="font-weight:bold; font-size:12px; color:#0f2043;">પેન્ડિંગ ફાઇનાન્સ DO ડ્રોપ-ડાઉન:</span>
                    <select name="do_id" id="do_sel" onchange="fillFromDo(false)" style="flex:1; padding:6px; font-weight:bold;">{do_opts}</select>
                    <button type="button" onclick="previewSelectedDoPdf()" style="background:#0284c7; color:white; border:none; padding:6px 10px; border-radius:4px; cursor:pointer; font-weight:bold;">[👁️ DO PDF જુઓ]</button>
                    <button type="button" onclick="unmatchDoSelection()" style="background:#ca8a04; color:white; border:none; padding:6px 10px; border-radius:4px; cursor:pointer; font-weight:bold;">[✖️ DO રીસેટ]</button>
                    <button type="button" onclick="deleteSelectedDo()" style="background:#dc2626; color:white; border:none; padding:6px 10px; border-radius:4px; cursor:pointer; font-weight:bold;">[🗑️ કાઢી નાખો]</button>
                </div>
            </div>
            """

        form_html = f"""
        {f2_banner_top}
        <div style="display:flex; gap:6px; align-items:center; flex-wrap:wrap; margin:6px 8px;">
            <button type="button" onclick="startGujaratiVoiceBilling()" id="f2_voice_btn" style="background:linear-gradient(135deg, #7c3aed, #6d28d9); color:white; border:none; padding:6px 14px; border-radius:5px; font-weight:bold; font-size:12px; cursor:pointer; display:inline-flex; align-items:center; gap:5px; box-shadow:0 2px 4px rgba(109,40,217,0.3);">🎤 બોલીને બિલ બનાવો (ગુજરાતી)</button>
            <button type="button" onclick="openOnlinePriceSpyModal(document.getElementById('f2_mod') ? document.getElementById('f2_mod').value : '', document.getElementById('f2_mop') ? document.getElementById('f2_mop').value : 0)" style="background:linear-gradient(135deg, #ea580c, #c2410c); color:white; border:none; padding:6px 14px; border-radius:5px; font-weight:bold; font-size:12px; cursor:pointer; display:inline-flex; align-items:center; gap:5px; box-shadow:0 2px 4px rgba(234,88,12,0.3);">🛒 ઓનલાઈન MOP & બેંક ઓફર્સ</button>
            <button type="button" onclick="generateSalesmanClosingPitch()" style="background:linear-gradient(135deg, #0284c7, #0369a1); color:white; border:none; padding:6px 14px; border-radius:5px; font-weight:bold; font-size:12px; cursor:pointer; display:inline-flex; align-items:center; gap:5px;">🧠 AI સેલ્સ ક્લોઝિંગ પિચ</button>
            <span style="font-size:11px; background:#0f172a; color:#38bdf8; padding:5px 10px; border-radius:5px; margin-left:auto; font-weight:bold;">🚶‍♂️ આજનો સ્ટોર ફૂટફોલ: 14 ગ્રાહકો | 🧾 બિલ: 8 | 🎯 કન્વર્ઝન રેટ: 57.1%</span>
        </div>
        <div class="mode-banner">
            <span>મોડ: [F2] વેચાણ અને પેમેન્ટ સ્પ્લિટ મોડ્યુલ (૩ ડાયનેમિક કન્ડિશનલ ફોર્મ્સ: ૧. રોકડ બિલ | ૨. ઉધાર બિલ | ૩. ફાઇનાન્સ બિલ)</span>
            <span style="font-size:11.5px; color:#0f2043;">Enter = આગળ વધો | છેલ્લે Accept? [Yes/No]</span>
        </div>

        <form class="term-form f-enter-form" action="/save-f2" method="post" enctype="multipart/form-data">
            <!-- મુખ્ય ડ્રોપ-ડાઉન: બિલનો પ્રકાર (૩ ડાયનેમિક કન્ડિશનલ ફોર્મ્સ) -->
            <div class="f-row" style="background:#0f2043; color:white; padding:6px 10px; border-radius:6px; margin-bottom:8px;">
                <div class="lbl" style="color:#fde047; font-size:13px;">૧. બિલનો પ્રકાર (ડાયનેમિક ફોર્મ):</div>
                <select name="bill_type" id="f2_bill_type" onchange="switchF2DynamicForm()" style="font-weight:800; font-size:13px; color:#0f2043; background:#fef08a; flex:1;">
                    {"".join([
                        opt_html for sub_k, opt_html in [
                            ("F2_1", f'<option value="CASH_BILL" {"selected" if (shop_prof or {}).get("f2_bill_type", "CASH_BILL") == "CASH_BILL" else ""}>૧. રોકડ બિલ (Cash Bill - ૧૫ ખાનાં)</option>'),
                            ("F2_2", f'<option value="CREDIT_BILL" {"selected" if (shop_prof or {}).get("f2_bill_type") == "CREDIT_BILL" else ""}>૨. ઉધાર બિલ (Credit Bill - ૧૮ ખાનાં)</option>'),
                            ("F2_3", f'<option value="FINANCE_BILL" {"selected" if (shop_prof or {}).get("f2_bill_type") == "FINANCE_BILL" else ""}>૩. ફાઇનાન્સ બિલ & DO સેટલમેન્ટ (Finance Bill - ૨૨ ખાનાં)</option>')
                        ] if sub_k in active_subparts
                    ]) or '<option value="CASH_BILL" selected>૧. રોકડ બિલ (Cash Bill)</option>'}
                </select>
                <select name="b2b_type" id="f2_b2b_type" onchange="toggleF2Gstin()" style="max-width:190px; font-weight:bold;">
                    <option value="B2C">B2C (રિટેલ ગ્રાહક)</option>
                    <option value="B2B">B2B (GST બિલ)</option>
                </select>
            </div>

            {pending_bar_html}

            <div class="f-row">
                <div class="lbl">૩. પાકું બિલ નંબર # & તારીખ:</div>
                <input type="text" name="bill_no" id="f2_bill" value="{current_bill}" style="background:#f1f5f9; font-weight:bold; max-width:220px;">
                <input type="date" name="bill_date" value="{today_str}" style="max-width:180px;">
            </div>

            <!-- ફાઇનાન્સ બિલ માટેના ખાનાં (Bajaj Customer ID AR61015792 / DMI / IDFC / TVS DO Auto-Fill & EMI Dates) -->
            <div id="f2_finance_only_top">
                <div class="f-row" style="background:#f0fdf4; padding:4px; border-radius:4px;">
                    <div class="lbl" style="color:#166534;">૫. કંપની, DO નંબર & કસ્ટમર આઈડી:</div>
                    <div style="display:flex; gap:3px; max-width:210px;">
                        <select name="finance_company" id="f2_fin_comp" style="flex:1; font-weight:bold; color:#0f2043; background:#fefce8; border:1.5px solid #ca8a04;">
                            <option value="">-- કંપની પસંદ કરો --</option>
                            <option value="Bajaj Finance">Bajaj Finance</option>
                            <option value="TVS Credit">TVS Credit</option>
                            <option value="IDFC First Bank">IDFC First Bank</option>
                            <option value="DMI Finance">DMI Finance</option>
                            <option value="HDB Financial Services">HDB Financial</option>
                            <option value="Kotak Mahindra Bank">Kotak Mahindra</option>
                            <option value="Samsung Finance+">Samsung Finance+</option>
                        </select>
                        <button type="button" onclick="openInlineQuickCreateModal('FINANCE_COMP', 'f2_fin_comp')" style="background:#0284c7; color:white; border:none; padding:3px 8px; border-radius:3px; font-weight:bold; font-size:11px; cursor:pointer;" title="નવી ફાઇનાન્સ કંપની ઉમેરો (Alt+C)">[+]</button>
                    </div>
                    <input type="text" name="do_ref_no" id="f2_do_ref" placeholder="DO ID / રેફરન્સ નંબર (દા.ત. BR1840...)" style="flex:1; font-weight:bold; color:#0369a1;">
                    <input type="text" name="app_deal_id" id="f2_app_id" placeholder="કસ્ટમર આઈડી (Customer ID: AR6101...)" style="max-width:210px; font-weight:bold; color:#7c3aed; border:1.5px solid #7c3aed;">
                </div>
                <div class="f-row" style="background:#f0fdf4; padding:4px; border-radius:4px;">
                    <div class="lbl" style="color:#166534;">સ્કીમ (Tenor), માસિક EMI & પ્રથમ ચાર્જ:</div>
                    <input type="text" name="scheme_name" id="f2_scheme" list="scheme_list_opts" oninput="autoCalcLastEmiF2()" placeholder="સ્કીમ (દા.ત. 6/0, 8/0, 7/1)" style="max-width:165px; font-weight:bold; color:#15803d;">
                    <input type="number" step="any" name="emi_amt" id="f2_emi_amt" value="0" placeholder="માસિક EMI ₹" style="max-width:140px; font-weight:bold;">
                    <input type="text" name="first_emi_extra_charge" id="f2_first_extra" placeholder="પ્રથમ હપ્તામાં વિશેષ ચાર્જ ₹ (ખાલી રાખશો તો બિલમાં અંડરલાઇન આવશે)" style="flex:1; font-size:11.5px;">
                    <datalist id="scheme_list_opts">
                        <option value="6/0">Bajaj / 6/0</option>
                        <option value="8/0">TVS / 8/0</option>
                        <option value="7/1">IDFC / 7/1</option>
                        <option value="9/0">DMI / 9/0</option>
                        <option value="10/2">10/2 સ્કીમ</option>
                        <option value="12/4">12/4 સ્કીમ</option>
                        <option value="NA">NA (ઝીરો ડાઉનપેમેન્ટ)</option>
                    </datalist>
                </div>
                <div class="f-row" style="background:#fefce8; padding:4px; border-radius:4px; border:1px dashed #ca8a04;">
                    <div class="lbl" style="color:#854d0e;">📅 પ્રથમ EMI તારીખ & છેલ્લો EMI મહિનો:</div>
                    <input type="text" name="first_emi_date" id="f2_first_emi_dt" oninput="autoCalcLastEmiF2()" placeholder="પ્રથમ EMI તારીખ (દા.ત. 05-10-2026 અથવા ખાલી રાખો)" style="max-width:230px; font-weight:bold;">
                    <input type="text" name="last_emi_month" id="f2_last_emi_mo" placeholder="છેલ્લો EMI મહિનો (ઓટો ગણાશે અથવા હાથેથી લખવા ખાલી રાખો)" style="flex:1; font-weight:bold; color:#0369a1;">
                </div>
            </div>

            <div class="f-row" style="background:#fdf2f8; padding:4px; border-radius:4px;">
                <div class="lbl">૪. ૧૫-અંક IMEI / બારકોડ સ્કેન:</div>
                <input type="text" name="imei" id="f2_imei" oninput="lookupImeiPassport()" placeholder="બારકોડ સ્કેન કરો અથવા મેન્યુઅલ ટાઇપ કરો (સેવ થતાં જ In-Stock માંથી Sold થશે)">
            </div>
            <div id="imei_passport_box" style="display:none; margin-left:243px; margin-bottom:6px; background:#ecfdf5; border:1px solid #059669; padding:6px 10px; border-radius:4px; font-size:11.5px; color:#065f46; font-weight:bold;"></div>

            <div class="f-row">
                <div class="lbl">૫. બ્રાન્ડ & હેન્ડસેટ / આઇટમ મોડેલ:</div>
                <div style="display:flex; gap:3px; max-width:185px;">
                    <select name="brand" id="f2_brand" style="flex:1; font-weight:bold; color:#0f2043; background:#f0fdf4; border:1.5px solid #16a34a;">
                        {brand_opts_html}
                    </select>
                    <button type="button" onclick="openInlineQuickCreateModal('BRAND', 'f2_brand')" style="background:#0284c7; color:white; border:none; padding:3px 8px; border-radius:3px; font-weight:bold; font-size:11px; cursor:pointer;" title="નવી બ્રાન્ડ ઉમેરો (Alt+C)">[+]</button>
                </div>
                <div style="display:flex; gap:3px; flex:1;">
                    <input type="text" name="model" id="f2_mod" oninput="checkActiveSchemeForModelF2()" placeholder="હેન્ડસેટ મોડેલ વિગત..." style="flex:1; font-weight:bold;" required>
                    <button type="button" onclick="openInlineQuickCreateModal('MODEL', 'f2_mod')" style="background:#0284c7; color:white; border:none; padding:3px 8px; border-radius:3px; font-weight:bold; font-size:11px; cursor:pointer;" title="નવું મોડેલ ઉમેરો">[+ મોડેલ]</button>
                </div>
                <button type="button" onclick="checkActiveSchemeForModelF2(true)" style="background:#0284c7; color:white; border:none; padding:6px 10px; border-radius:4px; font-weight:bold; cursor:pointer; font-size:11px;">🌐 ઓફિશિયલ MOP & સ્કીમ</button>
            </div>
            <div class="f-row" id="f2_scheme_profit_row" style="background:#fefce8; border:1.5px solid #eab308; padding:5px 8px; border-radius:6px;">
                <div class="lbl" style="color:#854d0e;">🎁 કંપની સ્કીમ / પ્રાઇસ-ડ્રોપ નફો (₹):</div>
                <input type="number" step="any" name="scheme_benefit_amt" id="f2_scheme_benefit" value="0" oninput="calcF2()" placeholder="તારીખ-લોક સ્કીમ / ભાવ ફરક એક્સ્ટ્રા પ્રોફિટ ₹" style="max-width:160px; font-weight:bold; color:#15803d;">
                <select name="apply_scheme_to_bill" id="f2_apply_scheme_sel" onchange="toggleSchemeInCustomerBill()" style="max-width:340px; font-weight:bold; color:#0f2043; background:white;">
                    <option value="KEEP_PROFIT">૧. દુકાનના ચોખ્ખા નફામાં જ રાખો (ગ્રાહક બિલમાં ડિસ્કાઉન્ટ ન આપો)</option>
                    <option value="PASS_TO_CUSTOMER">૨. ગ્રાહકને બિલમાં ડિસ્કાઉન્ટ તરીકે આપો (Bill Discount)</option>
                </select>
                <span id="f2_scheme_badge_txt" style="font-size:11px; color:#b45309; font-weight:bold; flex:1;">(ચાલુ તારીખની સ્કીમ નેટ પ્રોફિટમાં ઉમેરાશે)</span>
            </div>

            <div class="f-row">
                <div class="lbl">૬. ઓફિશિયલ MOP (₹) & ડિસ્કાઉન્ટ:</div>
                <input type="number" step="any" name="mop_price" id="f2_mop" value="0" oninput="autoCalcExpectedDp(); calcF2();" style="font-weight:bold; color:#0f2043;" title="ઓફિશિયલ વેબસાઈટ / સ્ટોક પરથી MOP (હાથેથી પણ સુધારી શકાય)">
                <input type="number" step="any" name="discount_amt" id="f2_disc" value="0" oninput="calcF2();" placeholder="ડિસ્કાઉન્ટ (₹)" style="max-width:150px;">
                <select name="gst_pct" id="f2_gst_pct" onchange="calcF2()" style="max-width:145px;">
                    <option value="18">GST 18% (મોબાઈલ)</option>
                    <option value="28">GST 28% (TV/AC)</option>
                    <option value="5">GST 5%</option>
                    <option value="0">GST 0% (નોન-GST)</option>
                </select>
                <select name="warranty_period" id="f2_warranty" style="max-width:210px; font-weight:bold; color:#0369a1;" title="બિલ પર છાપવાનો વોરંટી સમયગાળો">
                    <option value="૧ વર્ષ કંપની વોરંટી (1 Year Brand Warranty)">🛡️ ૧ વર્ષ કંપની વોરંટી</option>
                    <option value="૬ મહિના વોરંટી (6 Months Warranty)">🛡️ ૬ મહિના વોરંટી</option>
                    <option value="૩ મહિના ટેસ્ટિંગ વોરંટી (3 Months)">🛡️ ૩ મહિના વોરંટી</option>
                    <option value="વોરંટી વગર (No Warranty / As-Is)">⚠️ વોરંટી વગર (No Warranty)</option>
                </select>
            </div>

            <!-- ફાઇનાન્સ લોન અને DP ખાનાં (માત્ર ફાઇનાન્સ બિલ માટે) -->
            <div id="f2_finance_loan_block">
                <div class="f-row" style="background:#eff6ff; padding:4px; border-radius:4px;">
                    <div class="lbl" style="color:#1e3a8a;">૯. નેટ લોન (Net Disbursement ₹) & કુલ લોન:</div>
                    <input type="number" step="any" name="net_bank_loan" id="f2_net_loan" value="0" oninput="autoCalcExpectedDp(); calcF2();" placeholder="બેંકમાં જમા થતી નેટ લોન ₹" style="font-weight:bold; color:#1e3a8a;">
                    <input type="number" step="any" name="loan_amt" id="f2_loan" value="0" oninput="autoCalcExpectedDp(); calcF2();" placeholder="કુલ લોન રકમ ₹">
                </div>
                <div class="f-row" style="background:#eff6ff; padding:4px; border-radius:4px;">
                    <div class="lbl" style="color:#1d4ed8;">૧૦. ગ્રાહકનું કુલ DP (દુકાનદાર જાતે લખશે ₹):</div>
                    <input type="number" step="any" name="expected_dp" id="f2_exp_dp" value="0" oninput="this.dataset.manual='1'; calcF2();" style="border:2px solid #2563eb; font-weight:bold;" placeholder="ગ્રાહક પાસેથી લીધેલું વાસ્તવિક DP જાતે લખો...">
                    <span id="f2_basic_dp_hint" style="font-size:11px; color:#1e40af; font-weight:bold;">(Basic DP = MOP - Net Loan: ₹0)</span>
                </div>
            </div>

            <!-- ગ્રાહકની વિગતો -->
            <!-- ગ્રાહક GSTIN અને ઓટો-ફેચ બટન -->
            <div class="f-row" style="background:#f0fdf4; padding:4px; border:1px solid #86efac; border-radius:4px;">
                <div class="lbl" style="color:#166534;">ગ્રાહક GSTIN નંબર (જો B2B / વેપારી હોય):</div>
                <input type="text" name="customer_gstin" id="f2_gstin" placeholder="૧૫-અંક GSTIN નંબર દાખલ કરો..." style="flex:1; text-transform:uppercase; font-weight:bold;">
                <button type="button" onclick="autoLookupGstinF2()" style="background:#0284c7; color:white; border:none; padding:5px 12px; margin-left:6px; border-radius:4px; font-weight:bold; cursor:pointer;">[🔍 GSTIN સર્ચ (Auto-Fetch)]</button>
            </div>
            <div class="f-row">
                <div class="lbl">૭. ગ્રાહકનું પૂરું નામ & ૧૦-અંક મોબાઈલ:</div>
                <input type="text" name="customer_name" id="f2_cust" placeholder="ગ્રાહકનું પૂરેપૂરું નામ" style="flex:1;">
                <input type="text" name="phone" id="f2_ph" placeholder="૧૦-અંક મોબાઈલ નંબર" style="max-width:200px;">
            </div>
            <div class="f-row" id="f2_addr_pin_row" style="background:#eff6ff; padding:4px; border-radius:4px;">
                <div class="lbl" id="f2_addr_lbl">૧૧. સંપૂર્ણ સરનામું & ૬-અંક પિનકોડ:</div>
                <input type="text" name="customer_address" id="f2_addr" placeholder="ગ્રાહકનું સંપૂર્ણ સરનામું (ઉધાર/ફાઇનાન્સ માટે ફરજિયાત)" style="flex:1;">
                <input type="text" name="customer_pincode" id="f2_pin" placeholder="૬-અંક પિનકોડ" style="max-width:150px;">
            </div>

            <div class="f-row"><div class="lbl">૮. સેલ્સમેન / પ્રમોટર:</div><select name="salesman" id="f2_sm">{staff_opts_html}</select></div>

            <!-- સંપૂર્ણ પેમેન્ટ સ્પ્લિટ બોક્સ -->
            <div style="background:#f8fafc; border:2px solid #cbd5e1; border-radius:6px; padding:8px; margin:6px 0;">
                <div style="font-weight:800; color:#0f2043; margin-bottom:6px; font-size:12px;">💳 પેમેન્ટ સ્પ્લિટ વિભાજન (Payment Split Breakdown):</div>
                <div class="f-row" style="background:#ecfdf5; padding:4px; border-radius:4px;">
                    <div class="lbl" style="color:#065f46;">(a) રોકડ રકમ (Cash ₹) & જમા ગલ્લો:</div>
                    <input type="number" step="any" name="cash_dp" id="f2_cash" value="0" oninput="calcF2()" style="color:#16a34a; font-weight:bold; max-width:180px;">
                    {galla_f2_sel}
                </div>
                <div class="f-row">
                    <div class="lbl">(b) ઓનલાઈન UPI (₹) & (c) કાર્ડ (POS ₹):</div>
                    <input type="number" step="any" name="upi_dp" id="f2_upi" value="0" oninput="calcF2()" placeholder="UPI / QR રકમ ₹">
                    <input type="number" step="any" name="card_swipe_dp" id="f2_card" value="0" oninput="calcF2()" placeholder="કસ્ટમર કાર્ડ સ્વાઇપ ₹">
                </div>
                <div class="f-row" style="background:#fefce8; padding:4px; border-radius:4px;">
                    <div class="lbl">(d) સ્ટાફ CC સ્વાઇપ (₹) & NEFT/RTGS:</div>
                    <input type="number" step="any" name="staff_cc_swipe" id="f2_scc" value="0" oninput="calcF2()" placeholder="સ્ટાફનું ક્રેડિટ કાર્ડ સ્વાઇપ ₹">
                    <input type="number" step="any" name="neft_rtgs_dp" id="f2_neft" value="0" oninput="calcF2()" placeholder="NEFT / RTGS રકમ ₹">
                </div>
                <div class="f-row" style="background:#fef3c7; padding:4px; border-radius:4px;">
                    <div class="lbl">(e) Exchange / BB રકમ, મોડેલ & IMEI:</div>
                    <input type="number" step="any" name="bb_amt" id="f2_bb" value="0" oninput="calcF2()" style="color:#b45309; font-weight:bold; max-width:150px;" placeholder="BB કિંમત ₹">
                    <input type="text" name="bb_in_model" placeholder="જૂનો ફોન મોડેલ (ઓટો ઇનવર્ડ)" style="flex:1;">
                    <input type="text" name="bb_in_imei" placeholder="જૂનો ૧૫-અંક IMEI" style="max-width:170px;">
                </div>
                <div class="f-row" style="background:#e0f2fe; padding:4px; border-radius:4px;">
                    <div class="lbl">📁 BB ફોન / આધારકાર્ડ / બિલ PDF-ફોટા:</div>
                    <input type="file" name="bb_in_photo" multiple>
                </div>
                <div class="f-row" id="f2_due_row_wrap" style="background:#fee2e2; padding:4px; border-radius:4px;">
                    <div class="lbl" style="color:#991b1b;">(f) ગ્રાહક બાકી (ઉધાર ₹) & વાયદા તારીખ:</div>
                    <input type="number" step="any" name="due_amt" id="f2_due" value="0" style="color:#dc2626; font-weight:bold;" placeholder="બાકી ઉધાર રકમ ₹">
                    <input type="date" name="due_date" id="f2_due_date" style="max-width:180px;" title="ઉધાર વાયદા તારીખ (Due Date)">
                </div>
            </div>

            <div class="f-row">
                <div class="lbl">૧૦/૧૪. ગિફ્ટ વિગત, પડતર (₹) & રિમાર્કસ:</div>
                <input type="text" name="gift_desc" placeholder="ગિફ્ટ નામ" style="max-width:180px;">
                <input type="number" step="any" name="gift_cost" value="0" placeholder="ગિફ્ટ પડતર ₹" style="max-width:130px;">
                <input type="text" name="remarks" placeholder="રિમાર્કસ / વિશેષ નોંધ" style="flex:1;">
            </div>

            <div class="f-row" style="background:#dcfce7; padding:4px; border-radius:4px;">
                <div class="lbl">૧૧/૧૫. કુલ વસૂલાત (Total Collected ₹):</div>
                <input type="number" step="any" id="f2_total_rec" value="0" readonly style="font-weight:bold; color:#15803d; max-width:200px;">
                <div id="f2_extra_profit_wrap" style="display:flex; align-items:center; gap:6px; flex:1;">
                    <span style="font-weight:bold; color:#dc2626; font-size:12px;">Extra DP નફો (ગલ્લો ૪): ₹</span>
                    <input type="number" step="any" id="f2_extra_dp" value="0" oninput="calcStaff20Comm()" style="color:#dc2626; font-weight:bold; width:100px;">
                    <span style="font-size:11.5px; font-weight:bold; color:#92400e;">સ્ટાફ કમિશન: ₹</span>
                    <input type="number" step="any" name="staff_comm" id="f2_comm" value="0" style="width:90px; font-weight:bold; color:#15803d;">
                </div>
            </div>

            <div class="btn-wrap">
                <button type="submit" class="btn-save" style="background:#0f2043;">
                    [ પાકું બિલ સાચવો & પ્રિન્ટ / WhatsApp PDF લો (Enter -> Accept? Yes/No) ]
                </button>
            </div>
        </form>

        <script>
            var STOCK_MAP = {stock_json};
            var COMM_ENABLED = {'true' if comm_enabled else 'false'};
            var COMM_DEDUCT = {comm_deduct};
            var COMM_PCT = {comm_pct};

            function checkActiveSchemeForModelF2(forceMop){{
                var mod = (document.getElementById('f2_mod').value || '').trim();
                var bDate = (document.querySelector('input[name="bill_date"]').value || '').trim();
                if(mod.length < 3) return;
                fetch('/api/lookup-model-mop-gst?model=' + encodeURIComponent(mod) + '&bill_date=' + encodeURIComponent(bDate))
                .then(r => r.json())
                .then(d => {{
                    if(d && d.brand) document.getElementById('f2_brand').value = d.brand;
                    var mopInp = document.getElementById('f2_mop');
                    var curMopNum = parseFloat(mopInp.value) || 0;
                    if(d && d.mop > 0){{
                        // જો સ્ટોકમાં પહેલેથી સાચી MOP હોય (દા.ત. ૨૭,૪૯૯) તો તેને જેનરિક ૧૪,૯૯૯ થી ઓવરરાઇટ ન કરવી!
                        if(!curMopNum || curMopNum === 0 || (forceMop && d.mop_source === 'STOCK_AUTHENTIC')){{
                            mopInp.value = d.mop;
                            autoCalcExpectedDp();
                            calcF2();
                        }} else if(forceMop && curMopNum > 0 && d.mop !== 14999){{
                            mopInp.value = d.mop;
                            autoCalcExpectedDp();
                            calcF2();
                        }}
                    }}
                    if(d && d.active_scheme_amt > 0){{
                        document.getElementById('f2_scheme_benefit').value = d.active_scheme_amt;
                        document.getElementById('f2_scheme_badge_txt').innerText = '✅ લાગુ સ્કીમ: ' + d.active_scheme_title + ' (+₹' + d.active_scheme_amt + ' એક્સ્ટ્રા પ્રોફિટ)';
                    }}
                }}).catch(()=>{{}});
            }}
            function toggleSchemeInCustomerBill(){{
                var mode = document.getElementById('f2_apply_scheme_sel').value;
                var schAmt = parseFloat(document.getElementById('f2_scheme_benefit').value) || 0;
                if(mode === 'PASS_TO_CUSTOMER' && schAmt > 0){{
                    document.getElementById('f2_disc').value = schAmt;
                }} else if(mode === 'KEEP_PROFIT'){{
                    if(parseFloat(document.getElementById('f2_disc').value) === schAmt) document.getElementById('f2_disc').value = 0;
                }}
                calcF2();
            }}
            function toggleF2Gstin(){{
                var b = document.getElementById('f2_b2b_type').value;
                var gstInp = document.getElementById('f2_gstin');
                if(gstInp && b === 'B2B'){{ gstInp.focus(); }}
            }}

            setTimeout(function(){{ if(typeof switchF2DynamicForm === 'function') switchF2DynamicForm(); }}, 20);
            function switchF2DynamicForm(){{
                var bt = document.getElementById('f2_bill_type').value;
                var finTop = document.getElementById('f2_finance_only_top');
                var finLoan = document.getElementById('f2_finance_loan_block');
                var doWrap = document.getElementById('f2_do_drop_wrap');
                var addrRow = document.getElementById('f2_addr_pin_row');
                var dueRow = document.getElementById('f2_due_row_wrap');
                var exWrap = document.getElementById('f2_extra_profit_wrap');

                if(bt === 'CASH_BILL'){{
                    finTop.style.display = 'none';
                    finLoan.style.display = 'none';
                    if(doWrap) doWrap.style.display = 'none';
                    dueRow.style.display = 'none';
                    exWrap.style.display = 'none';
                    document.getElementById('f2_loan').value = 0;
                    document.getElementById('f2_net_loan').value = 0;
                    document.getElementById('f2_due').value = 0;
                    document.getElementById('f2_addr').required = false;
                    document.getElementById('f2_pin').required = false;
                }} else if(bt === 'CREDIT_BILL'){{
                    finTop.style.display = 'none';
                    finLoan.style.display = 'none';
                    if(doWrap) doWrap.style.display = 'none';
                    dueRow.style.display = 'flex';
                    exWrap.style.display = 'none';
                    document.getElementById('f2_loan').value = 0;
                    document.getElementById('f2_net_loan').value = 0;
                    document.getElementById('f2_addr').required = true;
                    document.getElementById('f2_pin').required = true;
                }} else {{
                    finTop.style.display = 'block';
                    finLoan.style.display = 'block';
                    if(doWrap) doWrap.style.display = 'flex';
                    dueRow.style.display = 'flex';
                    exWrap.style.display = 'flex';
                    document.getElementById('f2_addr').required = true;
                    document.getElementById('f2_pin').required = true;
                }}
                calcF2();
            }}

            function autoLookupGstinF2(){{
                var gEl = document.getElementById('f2_gstin');
                var g = (gEl ? gEl.value : '').replace(/\\s+/g, '').toUpperCase();
                if(gEl) gEl.value = g;
                if(!g || g.length < 15){{
                    alert('⚠️ કૃપા કરીને પૂરો ૧૫-અંકનો સાચો GSTIN નંબર દાખલ કરો!');
                    return;
                }}
                fetch('/api/lookup-gstin?gstin=' + encodeURIComponent(g))
                .then(r => r.json())
                .then(d => {{
                    if(d.found){{
                        var nm = d.name || d.trade_name || '';
                        if(nm) document.getElementById('f2_cust').value = nm;
                        if(d.address) document.getElementById('f2_addr').value = d.address;
                        if(d.pincode) document.getElementById('f2_pin').value = d.pincode;
                        if(d.mobile && !document.getElementById('f2_ph').value) document.getElementById('f2_ph').value = d.mobile;
                        var b2bSel = document.getElementById('f2_b2b_type');
                        if(b2bSel) b2bSel.value = 'B2B';
                        alert('✅ GSTIN વિગતો સફળતાપૂર્વક મળી: નામ: ' + nm + ' | સરનામું: ' + (d.address || '') + ' (' + (d.state || 'ગુજરાત') + ')');
                    }} else {{
                        alert('⚠️ આ GSTIN નંબરની વિગતો મળી નથી, કૃપા કરીને નંબર ચકાસો અથવા જાતે ટાઈપ કરો.');
                    }}
                }}).catch(e => {{
                    alert('GSTIN સર્ચમાં એરર આવી.');
                }});
            }}
            function lookupImeiPassport(){{
                var im = document.getElementById('f2_imei').value.trim();
                var box = document.getElementById('imei_passport_box');
                if(STOCK_MAP[im]){{
                    var s = STOCK_MAP[im];
                    document.getElementById('f2_brand').value = s.brand || 'Vivo';
                    document.getElementById('f2_mod').value = s.model;
                    document.getElementById('f2_mop').value = s.mop;
                    box.style.display = 'block';
                    box.innerHTML = '✅ 360° IMEI પાસપોર્ટ: વેપારી: ' + s.party + ' | ઇનવર્ડ: ' + s.date + ' | ખરીદ DP: ₹' + s.dp + ' | MOP: ₹' + s.mop;
                    autoCalcExpectedDp();
                    calcF2();
                }} else {{ box.style.display = 'none'; }}
            }}

            function autoCalcExpectedDp(){{
                var mop = parseFloat(document.getElementById('f2_mop').value) || 0;
                var netL = parseFloat(document.getElementById('f2_net_loan').value) || 0;
                var loan = parseFloat(document.getElementById('f2_loan').value) || 0;
                var effLoan = netL > 0 ? netL : loan;
                var basicDp = (mop > 0 && effLoan > 0) ? Math.max(0, Math.round(mop - effLoan)) : 0;
                var hint = document.getElementById('f2_basic_dp_hint');
                if(hint) hint.innerText = '(Basic DP = MOP - Net Loan: ₹' + basicDp + ')';
            }}

            // ફ્રેન્ચાઇઝી મોડમાં બિલ સિલેક્ટ કરતાં સામેનો DO ઓટો-મેચ થાય!
            function fillFromApx(autoMatchDo){{
                var sel = document.getElementById('apx_sel');
                if(!sel) return;
                var opt = sel.options[sel.selectedIndex];
                if(!opt || !opt.value) return;
                var cust = opt.getAttribute('data-cust') || '';
                var ph = opt.getAttribute('data-ph') || '';
                var imei = opt.getAttribute('data-imei') || '';
                document.getElementById('f2_bill').value = opt.value;
                document.getElementById('f2_cust').value = cust;
                document.getElementById('f2_ph').value = ph;
                document.getElementById('f2_mod').value = opt.getAttribute('data-mod') || '';
                document.getElementById('f2_imei').value = imei;
                document.getElementById('f2_mop').value = opt.getAttribute('data-mop') || 0;
                var rawDoAddr = opt.getAttribute('data-addr') || '';
                var rawDoPin = opt.getAttribute('data-pin') || '';
                if(!rawDoPin) {{
                    var pm = rawDoAddr.match(/\\b([1-9]\\d{{5}})\\b/);
                    if(pm) rawDoPin = pm[1];
                }}
                if(rawDoPin) {{
                    rawDoAddr = rawDoAddr.replace(new RegExp('[\\s,\\-]*' + rawDoPin + '[\\s,\\.]*', 'g'), ' ').trim().replace(/,+$/, '').trim();
                    document.getElementById('f2_pin').value = rawDoPin;
                }}
                if(rawDoAddr) document.getElementById('f2_addr').value = rawDoAddr;

                if(autoMatchDo){{
                    var doSel = document.getElementById('do_sel');
                    if(doSel){{
                        for(var i=1; i<doSel.options.length; i++){{
                            var doOpt = doSel.options[i];
                            var dImei = doOpt.getAttribute('data-imei') || '';
                            var dPh = doOpt.getAttribute('data-ph') || '';
                            var dCust = doOpt.getAttribute('data-cust') || '';
                            if((imei && dImei === imei) || (ph && dPh === ph) || (cust && dCust && dCust.toLowerCase() === cust.toLowerCase())){{
                                doSel.selectedIndex = i;
                                fillFromDo(false);
                                break;
                            }}
                        }}
                    }}
                }}
                lookupImeiPassport();
                autoCalcExpectedDp();
                calcF2();
            }}

            // DO સિલેક્ટ કરતાં સામેનું બિલ ઓટો-મેચ થાય!
            function autoCalcLastEmiF2(){{
                var dtStr = (document.getElementById('f2_first_emi_dt') ? document.getElementById('f2_first_emi_dt').value : '').trim();
                var schStr = (document.getElementById('f2_scheme') ? document.getElementById('f2_scheme').value : '').trim();
                var lastInp = document.getElementById('f2_last_emi_mo');
                if(!dtStr || !lastInp) return;
                var rem = 6;
                var m = schStr.match(/(\\d{1,2})\\s*\\/\\s*(\\d{1,2})/);
                if(m) rem = Math.max(1, parseInt(m[1]) - parseInt(m[2]));
                else {{
                    var m2 = schStr.match(/(\\d{1,2})/);
                    if(m2) rem = parseInt(m2[1]);
                }}
                var parts = dtStr.split(/[\\-\\/\\.]/);
                if(parts.length === 3){{
                    var d = parseInt(parts[0]), mo = parseInt(parts[1]), y = parseInt(parts[2]);
                    if(parts[0].length === 4){{ y = parseInt(parts[0]); mo = parseInt(parts[1]); d = parseInt(parts[2]); }}
                    if(y < 100) y += 2000;
                    if(mo >= 1 && mo <= 12 && y >= 2020){{
                        var guM = ["","જાન્યુઆરી","ફેબ્રુઆરી","માર્ચ","એપ્રિલ","મે","જૂન","જુલાઈ","ઓગસ્ટ","સપ્ટેમ્બર","ઓક્ટોબર","નવેમ્બર","ડિસેમ્બર"];
                        var totM = (y * 12 + (mo - 1)) + Math.max(0, rem - 1);
                        var endY = Math.floor(totM / 12);
                        var endM = (totM % 12) + 1;
                        lastInp.value = guM[endM] + ' ' + endY + ' (' + (d<10?'0'+d:d) + '-' + (endM<10?'0'+endM:endM) + '-' + endY + ')';
                    }}
                }}
            }}

            function fillFromDo(autoMatchBill){{
                var sel = document.getElementById('do_sel');
                if(!sel) return;
                var opt = sel.options[sel.selectedIndex];
                if(!opt || !opt.value) return;
                // નિયમ ૨૧૦: DO સિલેક્ટ કરતાં જ F2 આપોઆપ ૩. ફાઇનાન્સ બિલ મોડમાં આવી જશે અને રિસેટ નહીં થાય!
                var btSel = document.getElementById('f2_bill_type');
                if(btSel && btSel.value !== 'FINANCE_BILL'){{
                    btSel.value = 'FINANCE_BILL';
                    try {{ localStorage.setItem('devanshi_active_f2_bill_type', 'FINANCE_BILL'); }} catch(e){{}}
                    switchF2DynamicForm();
                }}
                var cust = opt.getAttribute('data-cust') || '';
                var ph = opt.getAttribute('data-ph') || '';
                var imei = opt.getAttribute('data-imei') || '';
                document.getElementById('f2_fin_comp').value = opt.getAttribute('data-comp') || 'Bajaj Finance';
                var loanVal = parseFloat(opt.getAttribute('data-loan') || 0);
                var netVal = parseFloat(opt.getAttribute('data-net') || 0);
                document.getElementById('f2_loan').value = loanVal;
                document.getElementById('f2_net_loan').value = netVal;
                if(document.getElementById('f2_do_ref')) document.getElementById('f2_do_ref').value = opt.getAttribute('data-doref') || '';
                if(document.getElementById('f2_app_id')) document.getElementById('f2_app_id').value = opt.getAttribute('data-appid') || '';
                if(document.getElementById('f2_emi_amt')) document.getElementById('f2_emi_amt').value = opt.getAttribute('data-emi') || 0;
                var mopEl = document.getElementById('f2_mop');
                if(mopEl && (parseFloat(mopEl.value || 0) <= 0) && loanVal > 0) {{
                    mopEl.value = loanVal;
                }}
                var sch = opt.getAttribute('data-scheme') || '';
                if(sch) document.getElementById('f2_scheme').value = sch;
                if(cust) document.getElementById('f2_cust').value = cust;
                if(ph) document.getElementById('f2_ph').value = ph;
                if(opt.getAttribute('data-addr')) document.getElementById('f2_addr').value = opt.getAttribute('data-addr');
                if(opt.getAttribute('data-pin')) document.getElementById('f2_pin').value = opt.getAttribute('data-pin');
                if(opt.getAttribute('data-brand')) document.getElementById('f2_brand').value = opt.getAttribute('data-brand');
                if(opt.getAttribute('data-mod')) document.getElementById('f2_mod').value = opt.getAttribute('data-mod');
                if(imei){{
                    document.getElementById('f2_imei').value = imei;
                    lookupImeiPassport();
                }}

                if(autoMatchBill){{
                    var apxSel = document.getElementById('apx_sel');
                    if(apxSel){{
                        for(var i=1; i<apxSel.options.length; i++){{
                            var bOpt = apxSel.options[i];
                            var bImei = bOpt.getAttribute('data-imei') || '';
                            var bPh = bOpt.getAttribute('data-ph') || '';
                            var bCust = bOpt.getAttribute('data-cust') || '';
                            if((imei && bImei === imei) || (ph && bPh === ph) || (cust && bCust && bCust.toLowerCase() === cust.toLowerCase())){{
                                apxSel.selectedIndex = i;
                                fillFromApx(false);
                                break;
                            }}
                        }}
                    }}
                }}
                autoCalcExpectedDp();
                calcF2();
            }}


            function unmatchDoSelection(){{
                var doSel = document.getElementById('do_sel');
                if(doSel) doSel.selectedIndex = 0;
                document.getElementById('f2_fin_comp').value = '';
                document.getElementById('f2_scheme').value = '';
                if(document.getElementById('f2_do_ref')) document.getElementById('f2_do_ref').value = '';
                if(document.getElementById('f2_app_id')) document.getElementById('f2_app_id').value = '';
                if(document.getElementById('f2_emi_amt')) document.getElementById('f2_emi_amt').value = 0;
                document.getElementById('f2_loan').value = 0;
                document.getElementById('f2_net_loan').value = 0;
                autoCalcExpectedDp();
                calcF2();
            }}
            function unmatchApxSelection(){{
                var apxSel = document.getElementById('apx_sel');
                if(apxSel) apxSel.selectedIndex = 0;
                document.getElementById('f2_cust').value = '';
                document.getElementById('f2_ph').value = '';
                document.getElementById('f2_mod').value = '';
                document.getElementById('f2_imei').value = '';
                document.getElementById('f2_mop').value = 0;
                calcF2();
            }}
            function previewSelectedDoPdf(){{
                var doSel = document.getElementById('do_sel');
                if(!doSel || !doSel.value){{ alert('પહેલા પેન્ડિંગ DO સિલેક્ટ કરો!'); return; }}
                var opt = doSel.options[doSel.selectedIndex];
                var docUrl = opt ? opt.getAttribute('data-doc') : '';
                if(docUrl) window.open(docUrl, '_blank');
                else alert('આ DO ની PDF ફાઇલ ઉપલબ્ધ નથી.');
            }}

            function deleteSelectedApx(){{
                var sel = document.getElementById('apx_sel');
                var opt = sel.options[sel.selectedIndex];
                if(!opt || !opt.value){{ alert('પહેલા સેલ્સ બિલ સિલેક્ટ કરો!'); return; }}
                if(confirm('શું આ પેન્ડિંગ બિલ ડિલીટ કરવું છે?')) window.location.href = '/delete-pending-apx?id=' + opt.getAttribute('data-id');
            }}
            function deleteSelectedDo(){{
                var sel = document.getElementById('do_sel');
                if(!sel || !sel.value){{ alert('પહેલા ફાઇનાન્સ DO સિલેક્ટ કરો!'); return; }}
                if(confirm('શું આ પેન્ડિંગ DO ડિલીટ કરવો છે?')) window.location.href = '/delete-pending-do?id=' + sel.value;
            }}

            function calcStaff20Comm(){{
                if(!COMM_ENABLED) return;
                var ex = parseFloat(document.getElementById('f2_extra_dp').value) || 0;
                var cVal = (ex > COMM_DEDUCT) ? Math.round((ex - COMM_DEDUCT) * (COMM_PCT / 100.0)) : 0;
                document.getElementById('f2_comm').value = cVal;
            }}

            function calcF2(){{
                var bt = document.getElementById('f2_bill_type').value;
                var mop = parseFloat(document.getElementById('f2_mop').value) || 0;
                var disc = parseFloat(document.getElementById('f2_disc').value) || 0;
                var netMop = Math.max(0, mop - disc);
                var netL = parseFloat(document.getElementById('f2_net_loan').value) || 0;
                var loan = parseFloat(document.getElementById('f2_loan').value) || 0;
                var effLoan = (bt === 'FINANCE_BILL') ? (netL > 0 ? netL : loan) : 0;

                var cash = parseFloat(document.getElementById('f2_cash').value) || 0;
                var upi = parseFloat(document.getElementById('f2_upi').value) || 0;
                var card = parseFloat(document.getElementById('f2_card').value) || 0;
                var scc = parseFloat(document.getElementById('f2_scc').value) || 0;
                var neft = parseFloat(document.getElementById('f2_neft').value) || 0;
                var bb = parseFloat(document.getElementById('f2_bb').value) || 0;

                var dpSplitSum = cash + upi + card + scc + neft + bb;
                var totalRec = effLoan + dpSplitSum;
                document.getElementById('f2_total_rec').value = Math.round(totalRec);

                if(bt === 'CREDIT_BILL'){{
                    var remDue = Math.max(0, netMop - dpSplitSum);
                    document.getElementById('f2_due').value = Math.round(remDue);
                    document.getElementById('f2_extra_dp').value = 0;
                }} else if(bt === 'FINANCE_BILL'){{
                    var custDp = parseFloat(document.getElementById('f2_exp_dp').value) || 0;
                    var basicDp = Math.max(0, netMop - effLoan);
                    if(custDp > 0){{
                        var extraDp = Math.max(0, custDp - basicDp);
                        var remFromDp = Math.max(0, custDp - dpSplitSum);
                        document.getElementById('f2_extra_dp').value = Math.round(extraDp);
                        document.getElementById('f2_due').value = Math.round(remFromDp);
                    }} else {{
                        var diff = netMop - totalRec;
                        if(diff > 0){{
                            document.getElementById('f2_due').value = Math.round(diff);
                            document.getElementById('f2_extra_dp').value = 0;
                        }} else {{
                            document.getElementById('f2_due').value = 0;
                            document.getElementById('f2_extra_dp').value = Math.round(Math.abs(diff));
                        }}
                    }}
                    calcStaff20Comm();
                }} else {{
                    document.getElementById('f2_due').value = 0;
                    document.getElementById('f2_extra_dp').value = 0;
                }}
            }}
        </script>
        """

    # =========================================================================
    # [F3] ઓલ-ઇન-વન લેજર અને ખર્ચા (Payment Receive, Payment Out & Daily Store Expenses)
    #      + જૂના ફોન રિપેરિંગ અને સીધું વેચાણ
    # =========================================================================
    elif mode == "F3":
        # 📱 રિચાર્જ માટેના ૩ મુખ્ય લાપુ (Airtel, VI, Jio) + દુકાનદારે ઉમેરેલી કંપનીઓનું ઓપનિંગ-ક્લોઝિંગ બેલેન્સ મેળવો
        for _def_op in ("Airtel", "Vi", "Jio"):
            c.execute("""INSERT OR IGNORE INTO recharge_lapu_company_balances
                         (company, opening_balance, today_topup, today_sales, current_demo_balance, pending_distributor_due, last_updated)
                         VALUES (?, 0, 0, 0, 0, 0, '')""", (_def_op,))
        c.execute("""SELECT company, COALESCE(opening_balance,0), COALESCE(today_topup,0),
                            COALESCE(today_sales,0), COALESCE(current_demo_balance,0), COALESCE(last_updated,'')
                     FROM recharge_lapu_company_balances
                     ORDER BY CASE
                        WHEN UPPER(company) LIKE 'AIRTEL%' THEN 1
                        WHEN UPPER(company) LIKE 'VI%' THEN 2
                        WHEN UPPER(company) LIKE 'JIO%' THEN 3
                        ELSE 4 END, company ASC""")
        lapu_comp_rows = c.fetchall()
        f3_lapu_trs_html = ""
        for _idx_l, _lr in enumerate(lapu_comp_rows):
            _cname = _lr[0]
            _db_op = float(_lr[1] or 0)
            _db_top = float(_lr[2] or 0)
            _db_sal = float(_lr[3] or 0)
            _db_cls = float(_lr[4] or 0)
            _last_dt = str(_lr[5] or "")
            # જો ગઈકાલે સાંજે ક્લોઝિંગ બેલેન્સ લખ્યું હોય અને આજે નવો દિવસ હોય -> ગઈકાલનું ક્લોઝિંગ = આજ સવારનું ઓપનિંગ!
            if _last_dt and _last_dt != today_str and _db_cls > 0:
                _eff_op = _db_cls
                _eff_top = 0.0
                _eff_cls_val = ""
                _eff_used = 0.0
            else:
                _eff_op = _db_op if _db_op > 0 else _db_cls
                _eff_top = _db_top
                _eff_cls_val = f"{_db_cls:.0f}" if (_last_dt == today_str and _db_cls > 0) else ""
                _eff_used = max(0.0, _eff_op + _eff_top - _db_cls) if (_last_dt == today_str and _db_cls > 0) else _db_sal
            _del_op_btn = "" if _cname.upper() in ("AIRTEL", "VI", "JIO") else f"<button type='button' onclick='deleteLapuOperatorF3({json.dumps(_cname)})' style='background:#dc2626; color:white; border:none; padding:2px 6px; border-radius:3px; cursor:pointer; font-size:10px; margin-left:4px;' title='આ કંપની કાઢી નાખો'>🗑️</button>"
            _edit_op_btn = f"<button type='button' onclick='renameLapuOperatorF3({json.dumps(_cname)})' style='background:#0284c7; color:white; border:none; padding:2px 6px; border-radius:3px; cursor:pointer; font-size:10px; margin-left:4px;' title='નામ સુધારો'>✏️</button>"
            f3_lapu_trs_html += f"""
            <tr class="f3-lapu-row" data-idx="{_idx_l}">
                <td style="text-align:left; font-weight:800; color:#4c1d95;">
                    <input type="hidden" name="lapu_companies" value="{_cname}">
                    📱 {_cname} LAPU {_edit_op_btn}{_del_op_btn}
                </td>
                <td>
                    <input type="number" step="any" name="lapu_openings" id="f3_lp_op_{_idx_l}" value="{_eff_op:.0f}" oninput="calcF3LapuTable()" style="width:110px; font-weight:bold; background:#f8fafc; text-align:center;" title="ગઈકાલ સાંજનું ક્લોઝિંગ = આજ સવારનું ઓપનિંગ">
                </td>
                <td>
                    <input type="number" step="any" name="lapu_topups" id="f3_lp_top_{_idx_l}" value="{_eff_top:.0f}" oninput="calcF3LapuTable()" style="width:105px; font-weight:bold; color:#0284c7; text-align:center;" title="આજે ખરીદેલું નવું રિચાર્જ ટોપ-અપ">
                </td>
                <td>
                    <input type="number" step="any" name="lapu_closings" id="f3_lp_cls_{_idx_l}" value="{_eff_cls_val}" placeholder="સાંજનું ક્લોઝિંગ (મરજિયાત)" oninput="calcF3LapuTable()" style="width:155px; font-weight:800; color:#15803d; background:#fefce8; border:2px solid #ca8a04; text-align:center;" title="ડેમોમાં સાંજે વધેલું લાપુ બેલેન્સ (ના લખવું હોય તો ખાલી રાખી શકાય)">
                </td>
                <td>
                    <input type="number" step="any" name="lapu_used_sales" id="f3_lp_use_{_idx_l}" value="{_eff_used:.0f}" readonly style="width:115px; font-weight:800; color:#dc2626; background:#fee2e2; text-align:center;" title="આજનું વપરાયેલું બેલેન્સ = ઓપનિંગ + ટોપઅપ - સાંજનું ક્લોઝિંગ">
                </td>
            </tr>
            """
        c.execute("SELECT COALESCE(SUM(CASE WHEN tx_type IN ('CAPITAL_IN','GIFT_IN') THEN amount ELSE 0 END), 0), COALESCE(SUM(CASE WHEN tx_type IN ('DRAWING_OUT','CAPITAL_OUT') THEN amount ELSE 0 END), 0) FROM partner_capital_ledger")
        _p_in_tot, _p_out_tot = c.fetchone() or (0.0, 0.0)
        _p_in_tot = float(_p_in_tot or 0.0)
        _p_out_tot = float(_p_out_tot or 0.0)
        _p_pend_ret = max(0.0, _p_in_tot - _p_out_tot)
        c.execute("SELECT DISTINCT partner_name FROM partner_capital_ledger WHERE partner_name IS NOT NULL AND partner_name != ''")
        _p_names = [r[0] for r in c.fetchall()]
        for _def_p in ["પાર્ટનર ૧ (મુખ્ય માલિક - જયમીનભાઈ પટેલ)", "પાર્ટનર ૨"]:
            if _def_p not in _p_names:
                _p_names.append(_def_p)
        partner_opts_html = "".join([f'<option value="{pn}">{pn}</option>' for pn in _p_names])

        if f4_sm_filter:
            c.execute("SELECT id, date, salesman, customer_name, phone, bill_no, due_amt, received_amt FROM customer_due_ledger WHERE (due_amt - received_amt) > 0 AND salesman LIKE ? ORDER BY id DESC", (f"%{f4_sm_filter}%",))
        else:
            c.execute("SELECT id, date, salesman, customer_name, phone, bill_no, due_amt, received_amt FROM customer_due_ledger WHERE (due_amt - received_amt) > 0 ORDER BY id DESC")
        due_rows = c.fetchall()
        due_opts = '<option value="" data-rem="0" data-ph="" data-name="">-- [તારીખ] | [નામ] | [મોબાઈલ] | [સેલ્સમેન] | [બાકી] --</option>'
        for d in due_rows:
            rem = float(d[6] or 0) - float(d[7] or 0)
            due_opts += f'<option value="{d[0]}" data-rem="{rem}" data-ph="{d[4]}" data-name="{d[3]}">{d[1]} | {d[3]} | {d[4]} | {d[2]} | બાકી: ₹{rem:,.0f}</option>'

        sm_filter_opts = '<option value="">-- તમામ સેલ્સમેન --</option>' + "".join([
            f'<option value="{s}" {"selected" if f4_sm_filter==s else ""}>{s}</option>' for s in staff_list
        ])

        galla_f3_rec = build_4galla_select("galla_name", "BANK_CASH")
        galla_f3_out = build_4galla_select("galla_name", "BANK_CASH")
        galla_f3_exp = build_4galla_select("galla_name", "BANK_CASH")

        form_html = f"""
        <div class="mode-banner">
            <span>મોડ: [F3] ઓલ-ઇન-વન લેજર અને ખર્ચા (૧. પેમેન્ટ રિસીવ | ૨. પેમેન્ટ આઉટ | ૩. દૈનિક સ્ટોર ખર્ચા)</span>
            <span style="font-size:11.5px;">એક જ ડ્રોપ-ડાઉનથી ત્રણેય કામ | ૪-ગલ્લા સિલેક્શન</span>
        </div>

        <div class="term-form">
            <div class="f-row" style="background:#0f2043; color:white; padding:6px 10px; border-radius:6px; margin-bottom:10px;">
                <div class="lbl" style="color:#fde047;">F3 મુખ્ય વિકલ્પ પસંદ કરો:</div>
                <select id="f3_master_mode" onchange="switchF3SubForm()" style="font-weight:800; font-size:13px; background:#fef08a; color:#0f2043;">
                    {"".join([
                        opt_html for is_vis, opt_html in [
                            (any(k in active_subparts for k in ("F3_1", "F3_1_CUST_DUE", "F3_1_ACC", "F3_1_RECH")), '<option value="PAY_RECEIVE">વિકલ્પ (૧): પેમેન્ટ રિસીવ (ગ્રાહક બાકી ઉધાર વસૂલાત + સાંજનો એસેસરીઝ અને રિચાર્જ લમ્પ-સમ વકરો - ૮ ખાનાં)</option>'),
                            ("F3_2" in active_subparts, '<option value="PAY_OUT">વિકલ્પ (૨): પેમેન્ટ આઉટ (વેપારી/સપ્લાયરને ચૂકવણી અથવા સ્ટાફ ઉપાડ/પગાર - ૭ ખાનાં)</option>'),
                            ("F3_3" in active_subparts, '<option value="STORE_EXPENSE">વિકલ્પ (૩): શુદ્ધ દૈનિક સ્ટોર ખર્ચા (૧૪ રેડીમેડ ખર્ચના નામ સાથે - ૭ ખાનાં)</option>'),
                            ("F3_4" in active_subparts, '<option value="DIRECT_UDHAR">વિકલ્પ (૪): ડાયરેક્ટ ગ્રાહક બાકી ઉધાર એન્ટ્રી (HO બિલ વગર સીધી ઉધાર નોંધ - ૭ ખાનાં)</option>'),
                            ("F3_5" in active_subparts, '<option value="PARTNER_CAPITAL">વિકલ્પ (૫): પાર્ટનર મૂડી (Capital In), પાર્ટનર ઉપાડ (Drawing) અને ભેટ/ગિફ્ટ (ઊભું Enter-Enter ફોર્મ)</option>'),
                            ("F3_6" in active_subparts, '<option value="LAPU_PURCHASE">વિકલ્પ (૬): 📲 ડિસ્ટ્રીબ્યુટર પાસેથી લાપુ બેલેન્સ ખરીદી (LAPU Purchase / Top-up) & ૩-કંપની લાપુ ટ્રેકર (Airtel, VI, Jio)</option>')
                        ] if is_vis
                    ]) or '<option value="PAY_RECEIVE">વિકલ્પ (૧): પેમેન્ટ રિસીવ</option>'}
                </select>
            </div>

            <!-- વિકલ્પ (૧): પેમેન્ટ રિસીવ (ગ્રાહક બાકી ઉધાર વસૂલાત + સાંજનો એસેસરીઝ અને રિચાર્જ લમ્પ-સમ વકરો - ૮ ખાનાં) -->
            <div id="f3_sub_receive">
                <form class="f-enter-form" action="/save-f4" method="post">
                    <div class="f-row"><div class="lbl">૧. તારીખ & સમય:</div><input type="date" name="rec_date" value="{today_str}"></div>
                    <div class="f-row" style="background:#e0f2fe; padding:5px; border-radius:4px;">
                        <div class="lbl" style="color:#0369a1;">૨. આવકનો પ્રકાર (Income Type):</div>
                        <select name="receive_type" id="f3_rec_type_sel" onchange="onF3ReceiveTypeChange()" style="font-weight:800; color:#0f2043; background:#fef08a;">
                            {"".join([
                                opt_h for show_opt, opt_h in [
                                    (("F3_1_CUST_DUE" in active_subparts or not any(x in active_subparts for x in ("F3_1_CUST_DUE","F3_1_ACC","F3_1_RECH"))), '<option value="CUST_DUE">૧. ગ્રાહક પાસેથી બાકી ઉધાર વસૂલાત (Customer Due Recovery - ગલ્લો ૧ In)</option>'),
                                    (("F3_1_ACC" in active_subparts or not any(x in active_subparts for x in ("F3_1_CUST_DUE","F3_1_ACC","F3_1_RECH"))), '<option value="ACC_INCOME">૨. સાંજનો એસેસરીઝ લમ્પ-સમ વકરો (Accessories Daily Lump-sum Income - ગલ્લો ૨ In)</option>'),
                                    (("F3_1_RECH" in active_subparts or not any(x in active_subparts for x in ("F3_1_CUST_DUE","F3_1_ACC","F3_1_RECH"))), '<option value="RECH_INCOME">૩. સાંજનો રિચાર્જ લમ્પ-સમ વકરો + ૩-લાપુ બેલેન્સ (Recharge Lump-sum Income - ગલ્લો ૩ In)</option>')
                                ] if show_opt
                            ]) or '<option value="CUST_DUE">૧. ગ્રાહક પાસેથી બાકી ઉધાર વસૂલાત</option>'}
                        </select>
                    </div>
                    <div id="f3_rec_cust_due_rows">
                        <div class="f-row">
                            <div class="lbl">૩(ક). સેલ્સમેન ફિલ્ટર ડ્રોપ-ડાઉન:</div>
                            <select onchange="window.location.href='/?sheet=SMART_TERMINAL&mode=F3&f4_sm_filter='+encodeURIComponent(this.value)">{sm_filter_opts}</select>
                        </div>
                        <div class="f-row">
                            <div class="lbl">૩(ખ). બાકી ગ્રાહક ડ્રોપ-ડાઉન:</div>
                            <select name="due_id" id="f3_due_sel" onchange="onF3DueSelect()" style="flex:1; font-weight:bold;">{due_opts}</select>
                            <button type="button" onclick="sendF3WhatsAppReminder()" style="background:#16a34a; color:white; border:none; padding:6px 10px; border-radius:4px; font-weight:bold; cursor:pointer;">📲 WhatsApp રિમાઇન્ડર</button>
                        </div>
                    </div>
                    <div class="f-row"><div class="lbl" id="f3_rec_amt_lbl">૪. આજે વસૂલ / કુલ વકરા રકમ (₹):</div><input type="number" step="any" name="received_amt" id="f3_rec_amt" value="0" oninput="calcF3LapuTable()" required style="font-weight:800; color:#0284c7; font-size:14px;"></div>

                    <!-- 📱 રિચાર્જ લમ્પ-સમ વકરો સિલેક્ટ થાય ત્યારે દેખાતું ૩-લાપુ બેલેન્સ (Airtel, VI, Jio) બોક્સ -->
                    <div id="f3_recharge_lapu_box" style="display:none; background:#faf5ff; border:2px solid #9333ea; border-radius:8px; padding:10px; margin:8px 0;">
                        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px; flex-wrap:wrap; gap:6px;">
                            <div>
                                <b style="color:#581c87; font-size:13px;">📱 ૩-કંપની લાપુ (LAPU) ડેમો બેલેન્સ & દૈનિક વકરા તાળો (Airtel, VI, Jio)</b>
                                <div style="font-size:11px; color:#6b21a8;">
                                    💡 ગઈકાલે સાંજનું ક્લોઝિંગ = આજે સવારનું ઓપનિંગ! સાંજનું બચેલું બેલેન્સ લખવું મરજિયાત છે.
                                </div>
                            </div>
                            <div style="display:flex; gap:6px; flex-wrap:wrap;">
                                <button type="button" onclick="document.getElementById('f3_master_mode').value='LAPU_PURCHASE'; switchF3SubForm();" style="background:#16a34a; color:white; border:none; padding:5px 12px; border-radius:4px; font-weight:800; font-size:11.5px; cursor:pointer;">[➕ ડિસ્ટ્રીબ્યુટર પાસેથી લાપુ ખરીદી એન્ટ્રી કરો]</button>
                                <button type="button" onclick="addNewLapuOperatorF3()" style="background:#7c3aed; color:white; border:none; padding:5px 12px; border-radius:4px; font-weight:bold; font-size:11.5px; cursor:pointer;">[+ નવી રિચાર્જ કંપની ઉમેરો]</button>
                            </div>
                        </div>
                        <table class="live-grid" style="margin-bottom:8px; background:white;">
                            <tr>
                                <th>રિચાર્જ કંપની (Airtel / VI / Jio)</th>
                                <th>સવારનું ઓપનિંગ બેલેન્સ (₹)<br><span style="font-size:10px; color:#fde047;">(ગઈકાલનું ક્લોઝિંગ)</span></th>
                                <th>આજે લીધેલું નવું ટોપ-અપ (+)</th>
                                <th>સાંજનું બચેલું ક્લોઝિંગ બેલેન્સ (₹)<br><span style="font-size:10px; color:#86efac;">(મરજિયાત - Optional)</span></th>
                                <th>આજનું વપરાયેલું / વેચાણ (=)</th>
                            </tr>
                            {f3_lapu_trs_html}
                        </table>
                        <div id="f3_lapu_reconcile_bar" style="background:#f3e8ff; border:1px solid #a855f7; padding:6px 10px; border-radius:6px; font-size:12px; font-weight:800; color:#4c1d95; display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap;">
                            <span>📊 લાપુ કુલ વપરાશ (Airtel+VI+Jio): <b id="f3_lp_tot_used" style="color:#dc2626;">₹0</b></span>
                            <span>💰 આજનો કુલ રિચાર્જ વકરો (હિસાબ): <b id="f3_lp_tot_cash" style="color:#15803d;">₹0</b></span>
                            <span id="f3_lp_diff_badge" style="background:#fef9c3; padding:2px 8px; border-radius:4px; border:1px solid #ca8a04; color:#854d0e;">તાળો / તફાવત: ₹0</span>
                        </div>
                    </div>

                    <div class="f-row"><div class="lbl">૫. ચૂકવણી પદ્ધતિ (MOP):</div>
                        <select name="pay_mode" onchange="document.getElementById('f3_rec_galla_row').style.display=(this.value.indexOf('રોકડ')!==-1?'flex':'none')">
                            <option value="રોકડ (Cash)">૧. રોકડ (Cash)</option>
                            <option value="ઓનલાઈન UPI / QR">૨. ઓનલાઈન UPI / QR</option>
                            <option value="બેંક ટ્રાન્સફર">૩. બેંક ટ્રાન્સફર</option>
                        </select>
                    </div>
                    <div class="f-row" id="f3_rec_galla_row"><div class="lbl">૬. રોકડ જમા ગલ્લો (૪-ગલ્લા):</div>{galla_f3_rec}</div>
                    <div class="f-row"><div class="lbl">૭. વસૂલ કરનાર સ્ટાફ & રિમાર્ક:</div>
                        <select name="remarks" style="max-width:220px;">{staff_opts_html}</select>
                        <input type="text" name="extra_note" id="f3_rec_note_inp" placeholder="રિમાર્ક / નોંધ..." style="flex:1;">
                    </div>
                    <div class="btn-wrap"><button type="submit" class="btn-save" style="background:#0369a1;">૮. [ પેમેન્ટ રિસીવ / આવક સેવ કરો (Enter) ]</button></div>
                </form>
            </div>

            <!-- વિકલ્પ (૨): પેમેન્ટ આઉટ (વેપારી કે સ્ટાફને ચૂકવણી - ૭ ખાનાં) -->
            <div id="f3_sub_payout" style="display:none;">
                <form class="f-enter-form" action="/save-f3-payout" method="post">
                    <div class="f-row"><div class="lbl">૧. તારીખ & સમય:</div><input type="date" name="entry_date" value="{today_str}"></div>
                    <div class="f-row"><div class="lbl">૨. પાર્ટી / વેપારી અથવા સ્ટાફ નામ:</div>
                        <select name="payout_target_type" id="f3_po_type" onchange="toggleF3PayoutTarget()" style="max-width:210px;">
                            <option value="SUPPLIER">વેપારી / સપ્લાયર પેમેન્ટ</option>
                            <option value="STAFF">સ્ટાફ ઉપાડ / પગાર / કમિશન</option>
                        </select>
                        <select name="supplier_name" id="f3_po_supp" style="flex:1;">{party_opts_html}</select>
                        <select name="staff_name" id="f3_po_staff" style="flex:1; display:none;">{staff_opts_html}</select>
                    </div>
                                        <div class="f-row" id="f3_po_staff_head_row" style="display:none; background:#fefce8; padding:6px; border-radius:5px; border:1.5px solid #ca8a04;">
                        <div class="lbl" style="color:#854d0e; font-weight:800;">૨(ખ). સ્ટાફ વ્યવહાર પ્રકાર (૪ અલગ હેડ):</div>
                        <select name="staff_payout_sub_type" style="flex:1; font-weight:bold; color:#0f2043; background:white; padding:5px; border:1px solid #ca8a04; border-radius:4px;">
                            <option value="STAFF_ADVANCE">૧. સ્ટાફ એડવાન્સ ઉપાડ (Advance Loan)</option>
                            <option value="STAFF_SALARY">૨. માસિક પગાર ચૂકવણી (Monthly Salary)</option>
                            <option value="STAFF_COMMISSION">૩. સ્કીમ કમિશન ચૂકવણી (Scheme Commission)</option>
                            <option value="STAFF_CC_REFUND">૪. સ્ટાફ ક્રેડિટ કાર્ડ સ્વાઇપ ચૂકવણી (Personal CC Swipe Refund)</option>
                        </select>
                    </div>
<div class="f-row"><div class="lbl">૩. ચૂકવેલ રકમ (₹):</div><input type="number" step="any" name="amount" value="0" required style="font-weight:bold; color:#dc2626;"></div>
                    <div class="f-row"><div class="lbl">૪. પેમેન્ટ મોડ:</div>
                        <select name="pay_mode">
                            <option value="રોકડ (Cash)">રોકડ (Cash)</option>
                            <option value="ચેક (Cheque)">ચેક (Cheque)</option>
                            <option value="ઓનલાઈન UPI">ઓનલાઈન UPI</option>
                            <option value="બેંક ટ્રાન્સફર">બેંક ટ્રાન્સફર</option>
                        </select>
                    </div>
                    <div class="f-row"><div class="lbl">૫. ચૂકવણી ગલ્લો (૪-ગલ્લા):</div>{galla_f3_out}</div>
                    <div class="f-row"><div class="lbl">૬. પર્ચેસ બિલ નંબર / રેફરન્સ / નોંધ:</div><input type="text" name="remarks" placeholder="બિલ નંબર અથવા રેફરન્સ નોંધ..."></div>
                    <div class="btn-wrap"><button type="submit" class="btn-save" style="background:#991b1b;">૭. [ પેમેન્ટ આઉટ સેવ કરો (Enter) ]</button></div>
                </form>
            </div>

            <!-- વિકલ્પ (૩): શુદ્ધ દૈનિક સ્ટોર ખર્ચા (૧૪ રેડીમેડ ખર્ચના નામ સાથે - ૭ ખાનાં) -->
            <div id="f3_sub_expense" style="display:none;">
                <form class="f-enter-form" action="/save-f6" method="post">
                    <input type="hidden" name="f6_type" value="EXPENSE">
                    <div class="f-row"><div class="lbl">૧. ખર્ચ તારીખ:</div><input type="date" name="entry_date" value="{today_str}"></div>
                    <div class="f-row">
                        <div class="lbl">૨. દૈનિક દુકાન ખર્ચનું નામ (૧૪ હેડ):</div>
                        <input type="text" name="head_name" id="f3_exp_head_inp" list="exp_heads_list" placeholder="ચા-નાસ્તો, ભાડું, લાઈટ બિલ, સ્ટેશનરી કે હાથેથી લખો..." style="flex:1; font-weight:bold;" required>
                        <datalist id="exp_heads_list">{exp_opts_html}</datalist>
                    </div>
                    <div class="f-row">
                        <div class="lbl" id="f3_exp_amt_lbl">૩. ખર્ચ રકમ (₹) *:</div>
                        <input type="number" step="any" name="amount" id="f3_exp_total_amt" value="0" required style="font-weight:800; color:#b45309; font-size:14px;">
                    </div>
                    <div class="f-row"><div class="lbl">૪. ચૂકવણી પદ્ધતિ (MOP):</div>
                        <select name="pay_mode"><option value="રોકડ">રોકડ (Cash)</option><option value="ઓનલાઈન / બેંક">ઓનલાઈન / બેંક</option></select>
                    </div>
                    <div class="f-row"><div class="lbl">૫. કયા ગલ્લામાંથી ખર્ચ ચૂકવ્યો (૪-ગલ્લા):</div>{galla_f3_exp}</div>
                    <div class="f-row"><div class="lbl">૬. વિગતવાર નોંધ / રિમાર્ક:</div><input type="text" name="remarks" placeholder="હાથેથી વિગતવાર ખર્ચ નોંધ લખો..."></div>
                    <div class="btn-wrap"><button type="submit" class="btn-save" id="f3_exp_submit_btn" style="background:#b45309;">૭. [ દૈનિક દુકાન ખર્ચ સેવ કરો (Enter) ]</button></div>
                </form>
            </div>

            <!-- વિકલ્પ (૪): ડાયરેક્ટ ગ્રાહક બાકી ઉધાર એન્ટ્રી (HO બિલ વગર સીધી ઉધાર નોંધ - ૭ ખાનાં) -->
            <div id="f3_sub_direct_udhar" style="display:none; background:#fff1f2; border:2px solid #e11d48; padding:12px; border-radius:6px;">
                <h4 style="margin:0 0 8px 0; color:#9f1239;">📝 વિકલ્પ (૪): ડાયરેક્ટ ગ્રાહક બાકી ઉધાર એન્ટ્રી (HO / APX બિલ વગર સીધી ઉધાર નોંધ)</h4>
                <form class="f-enter-form" action="/api/save-direct-customer-due" method="post">
                    <input type="hidden" name="return_sheet" value="SMART_TERMINAL">
                    <div class="f-row"><div class="lbl">૧. તારીખ:</div><input type="date" name="entry_date" value="{today_str}"></div>
                    <div class="f-row"><div class="lbl">૨. ગ્રાહકનું પૂરું નામ *:</div><input type="text" name="customer_name" placeholder="ગ્રાહકનું નામ લખો..." required></div>
                    <div class="f-row"><div class="lbl">૩. ૧૦-અંક મોબાઈલ નંબર *:</div><input type="text" name="phone" maxlength="10" placeholder="૧૦-અંક મોબાઈલ નંબર" required></div>
                    <div class="f-row"><div class="lbl">૪. આઇટમ / મોડેલ / ઉધાર વિગત:</div><input type="text" name="model_or_note" placeholder="દા.ત. જૂની બાકી / મોબાઈલ / એસેસરીઝ ઉધાર..." required></div>
                    <div class="f-row"><div class="lbl">૫. બાકી ઉધાર રકમ (₹) *:</div><input type="number" step="any" name="due_amt" value="0" required style="font-weight:800; color:#dc2626; font-size:14px;"></div>
                    <div class="f-row"><div class="lbl">૬. વાયદા તારીખ & જવાબદાર સેલ્સમેન:</div>
                        <input type="date" name="due_date" value="{today_str}" style="max-width:170px;">
                        <select name="salesman" style="flex:1;">{staff_opts_html}</select>
                    </div>
                    <div style="background:#fef2f2; border:1px dashed #dc2626; padding:8px; border-radius:5px; margin:8px 0;">
                        <b style="color:#991b1b; font-size:11.5px;">🤝 ત્રાહિત વ્યક્તિ (રેફરન્સ / જામીનદાર) વિગત:</b>
                        <div style="display:grid; grid-template-columns:1fr 1fr 1fr; gap:6px; margin-top:4px;">
                            <input type="text" name="guarantor_name" placeholder="જામીનદાર/રેફરન્સનું નામ..." style="padding:5px; font-size:11.5px;">
                            <input type="text" name="guarantor_village" placeholder="ગામ / રહેઠાણ..." style="padding:5px; font-size:11.5px;">
                            <input type="text" name="guarantor_phone" maxlength="10" placeholder="૧૦-અંક મોબાઈલ નંબર..." style="padding:5px; font-size:11.5px;">
                        </div>
                    </div>
                    <div class="btn-wrap"><button type="submit" class="btn-save" style="background:#e11d48;">૭. [ ડાયરેક્ટ ગ્રાહક ઉધાર ખાતાવહીમાં સેવ કરો (Enter) ]</button></div>
                </form>
            </div>

            <!-- વિકલ્પ (૫): પાર્ટનર મૂડી (Capital In), પાર્ટનર ઉપાડ/પરત (Drawing Out) અને ભેટ/ગિફ્ટ (Option B + ઊભું Enter-Enter ફોર્મ) -->
            <div id="f3_sub_partner_cap" style="display:none; background:#f0fdf4; border:2px solid #15803d; padding:12px; border-radius:6px;">
                <h4 style="margin:0 0 8px 0; color:#166534;">🤝 વિકલ્પ (૫): પાર્ટનર હિસાબ ડેસ્ક — મૂડી રોકાણ, ગિફ્ટ ખર્ચ & પેમેન્ટ રિટર્ન (Option B)</h4>
                <!-- ૩ ટોપ સમરી કાર્ડ્સ (સ્ક્રીનશોટ મુજબ) -->
                <div style="display:grid; grid-template-columns:repeat(3, 1fr); gap:10px; margin-bottom:12px;">
                    <div style="background:#eff6ff; border:2px solid #3b82f6; border-radius:8px; padding:10px; text-align:center;">
                        <div style="font-size:11.5px; font-weight:800; color:#1d4ed8;">💰 કુલ મૂડી રોકાણ & ગિફ્ટ જમા (Invested)</div>
                        <div style="font-size:18px; font-weight:900; color:#1e40af; margin-top:4px;">₹{_p_in_tot:,.0f}</div>
                    </div>
                    <div style="background:#f0fdf4; border:2px solid #16a34a; border-radius:8px; padding:10px; text-align:center;">
                        <div style="font-size:11.5px; font-weight:800; color:#15803d;">✅ કુલ પેમેન્ટ રિટર્ન ચૂકવાયું (Returned)</div>
                        <div style="font-size:18px; font-weight:900; color:#166534; margin-top:4px;">₹{_p_out_tot:,.0f}</div>
                    </div>
                    <div style="background:#fef2f2; border:2px solid #dc2626; border-radius:8px; padding:10px; text-align:center;">
                        <div style="font-size:11.5px; font-weight:800; color:#b91c1c;">⏳ સ્ટોર પાસેથી પાર્ટનરને લેવાના બાકી (Pending Return)</div>
                        <div style="font-size:18px; font-weight:900; color:#dc2626; margin-top:4px;">₹{_p_pend_ret:,.0f}</div>
                    </div>
                </div>
                <form class="f-enter-form" action="/api/save-partner-capital-tx" method="post">
                    <input type="hidden" name="return_sheet" value="SMART_TERMINAL">
                    <div class="f-row"><div class="lbl">૧. તારીખ:</div><input type="date" name="tx_date" value="{today_str}"></div>
                    <div class="f-row"><div class="lbl">૨. પાર્ટનરનું નામ સિલેક્ટ કરો *:</div>
                        <select name="partner_name" id="f3_part_name_sel" style="flex:1; font-weight:bold;">{partner_opts_html}</select>
                        <button type="button" onclick="promptNewPartnerF3()" style="background:#7c3aed; color:white; border:none; padding:6px 12px; border-radius:4px; font-weight:bold; cursor:pointer; font-size:11.5px;">[+ નવો પાર્ટનર ઉમેરો (Alt+C)]</button>
                    </div>
                    <div class="f-row"><div class="lbl">૩. એન્ટ્રી પ્રકાર (મૂડી / ગિફ્ટ / ઉપાડ):</div>
                        <select name="tx_type" id="f3_part_tx_type" onchange="onF3PartnerTxTypeChange()" style="font-weight:bold; color:#0f2043;">
                            <option value="CAPITAL_IN">૧. રોકડ મૂડી રોકાણ આપ્યું (Capital In - દુકાન ગલ્લામાં +)</option>
                            <option value="GIFT_IN">૨. સ્ટોર માટે ગિફ્ટ / ખર્ચ લાવ્યા (Gift / Expense In)</option>
                            <option value="DRAWING_OUT">૩. પાર્ટનરને પેમેન્ટ રિટર્ન આપ્યું / અંગત ઉપાડ (Payment Return Out -)</option>
                        </select>
                    </div>
                    <div class="f-row"><div class="lbl">૪. ગિફ્ટ / મૂડી / ખર્ચની વિગત *:</div><input type="text" name="remarks" placeholder="દા.ત. 50 નંગ નેકબેન્ડ ગિફ્ટ / રોકડ મૂડી રોકાણ / મૂડી પરત..." required></div>
                    <div class="f-row"><div class="lbl">૫. રકમ (₹) *:</div><input type="number" step="any" name="amount" value="0" required style="font-weight:800; color:#15803d; font-size:14px;"></div>
                    <div class="f-row" id="f3_part_funding_row">
                        <div class="lbl">૬. ગિફ્ટ/ખર્ચ માટે પૈસા ક્યાંથી ચૂકવાયા?:</div>
                        <select name="funding_source" id="f3_part_fund_sel" onchange="onF3PartnerFundChange()" style="font-weight:bold; color:#0f2043; background:#fefce8;">
                            <option value="STORE_GALLA">૧. સ્ટોર ગલ્લામાંથી રોકડ લીધી (ગલ્લામાંથી માઇનસ થશે)</option>
                            <option value="PARTNER_POCKET">૨. પાર્ટનરે પોતાના ખિસ્સામાંથી ચૂકવ્યા (પાર્ટનરના ખાતામાં લેણું જમા થશે, ગલ્લો અકબંધ)</option>
                        </select>
                    </div>
                    <div class="f-row" id="f3_part_galla_row"><div class="lbl">૭. ગલ્લો સિલેક્ટ કરો (૪-ગલ્લા):</div>{galla_f3_rec}</div>
                    <div class="f-row"><div class="lbl">૮. પેમેન્ટ મોડ:</div>
                        <select name="pay_mode" id="f3_part_pay_mode" onchange="onF3PartnerFundChange()">
                            <option value="રોકડ (Cash)">૧. રોકડ (Cash)</option>
                            <option value="ઓનલાઈન UPI / QR">૨. ઓનલાઈન UPI / QR</option>
                            <option value="બેંક ટ્રાન્સફર">૩. બેંક ટ્રાન્સફર</option>
                            <option value="પાર્ટનર અંગત ખિસ્સામાંથી (ગલ્લા સિવાય)">૪. પાર્ટનર અંગત ખિસ્સામાંથી (ગલ્લા સિવાય)</option>
                        </select>
                    </div>
                    <div class="btn-wrap"><button type="submit" class="btn-save" style="background:#15803d;">૯. [ 💾 પાર્ટનર હિસાબ સેવ કરો (Enter -> Accept? Yes/No) ]</button></div>
                </form>
            </div>

            <!-- વિકલ્પ (૬): 📲 ડિસ્ટ્રીબ્યુટર પાસેથી લાપુ બેલેન્સ ખરીદી (LAPU Purchase / Top-up Entry) -->
            <div id="f3_sub_lapu_purchase" style="display:none; background:#faf5ff; border:2px solid #7c3aed; padding:12px; border-radius:6px;">
                <h4 style="margin:0 0 8px 0; color:#581c87;">📲 વિકલ્પ (૬): ડિસ્ટ્રીબ્યુટર પાસેથી લાપુ બેલેન્સ ખરીદી (Airtel / VI / Jio LAPU Purchase & Top-up Entry)</h4>
                <div style="font-size:11.5px; color:#6b21a8; margin-bottom:8px;">
                    💡 જ્યારે કોઈપણ ડિસ્ટ્રીબ્યુટર પાસેથી Airtel, VI કે Jio નું લાપુ બેલેન્સ ખરીદો ત્યારે અહીં એન્ટ્રી પાડો — તે રકમ સીધી જ એ કંપનીના <b>'આજે લીધેલું નવું ટોપ-અપ (+)'</b> માં ઉમેરાઈ જશે!
                </div>
                <form class="f-enter-form" action="/save-lapu-inward-payment" method="post">
                    <input type="hidden" name="return_mode" value="F3">
                    <div class="f-row"><div class="lbl">૧. ખરીદી તારીખ:</div><input type="date" name="entry_date" value="{today_str}"></div>
                    <div class="f-row"><div class="lbl">૨. રિચાર્જ કંપની (Operator) *:</div>
                        <select name="company" required style="font-weight:800; color:#4c1d95; max-width:260px;">
                            <option value="Airtel">📱 Airtel LAPU</option>
                            <option value="Vi">📱 VI (Vodafone Idea) LAPU</option>
                            <option value="Jio">📱 Jio LAPU</option>
                        </select>
                    </div>
                    <div class="f-row"><div class="lbl">૩. ડિસ્ટ્રીબ્યુટર / વેપારીનું નામ *:</div>
                        <input type="text" name="distributor_name" list="f3_dist_party_list" placeholder="ડિસ્ટ્રીબ્યુટરનું નામ પસંદ કરો અથવા લખો (દા.ત. શ્રી રામ કોમ્યુનિકેશન)..." required style="flex:1; font-weight:bold;">
                        <datalist id="f3_dist_party_list">{party_opts_html}</datalist>
                    </div>
                    <div class="f-row"><div class="lbl">૪. મળેલ કુલ લાપુ બેલેન્સ (₹) *:</div>
                        <input type="number" step="any" name="inward_balance" id="f3_lp_in_bal" value="0" oninput="calcF3LapuPurchaseDiff()" required style="font-weight:800; color:#0284c7; font-size:14px;" placeholder="ડેમો ફોનમાં જમા થયેલ કુલ બેલેન્સ">
                    </div>
                    <div class="f-row"><div class="lbl">૫. ડિસ્ટ્રીબ્યુટરને ચૂકવેલ રકમ (₹):</div>
                        <input type="number" step="any" name="paid_to_distributor" id="f3_lp_paid_amt" value="0" oninput="calcF3LapuPurchaseDiff()" required style="font-weight:800; color:#15803d; font-size:14px;" placeholder="રોકડ કે બેંકથી ચૂકવેલ રકમ">
                        <span id="f3_lp_comm_badge" style="background:#dcfce7; border:1px solid #16a34a; color:#166534; padding:5px 10px; border-radius:4px; font-weight:800; font-size:12px;">કમિશન / બાકી: ₹0</span>
                    </div>
                    <div class="f-row"><div class="lbl">૫.૧. પેમેન્ટ પદ્ધતિ (Payment Mode):</div>
                        <select name="pay_mode" id="lapu_pay_mode_sel" style="font-weight:bold;">
                            <option value="CASH">૧. રોકડ (Cash)</option>
                            <option value="UPI">૨. ઓનલાઈન UPI / QR</option>
                            <option value="CHEQUE">૩. બેંક ચેક (Cheque)</option>
                            <option value="NEFT">૪. NEFT / RTGS / નેટબેંકિંગ</option>
                        </select>
                    </div>
                    <div class="f-row"><div class="lbl">૬. પેમેન્ટ કયા ગલ્લામાંથી ચૂકવ્યું:</div>
                        <select name="paid_from_galla" style="font-weight:bold;">
                            <option value="RECHARGE">૩. રિચાર્જ કેશ ગલ્લો (RECHARGE)</option>
                            <option value="BANK_CASH">૧. બેંક કેશ ગલ્લો (BANK_CASH)</option>
                            <option value="ACC_DCASH">૨. એક્સેસરીઝ કેશ ગલ્લો (ACC_DCASH)</option>
                            <option value="EXTRA_CASH">૪. એક્સ્ટ્રા કેશ ગલ્લો (EXTRA_CASH)</option>
                        </select>
                    </div>
                    <div class="f-row"><div class="lbl">૭. વિગતવાર નોંધ / કમિશન વિગત:</div>
                        <input type="text" name="remarks" placeholder="રેફરન્સ નંબર અથવા કમિશન નોંધ...">
                    </div>
                    <div class="btn-wrap"><button type="submit" class="btn-save" style="background:#6b21a8;">૮. [ 📲 ડિસ્ટ્રીબ્યુટર લાપુ ખરીદી સેવ કરો & બેલેન્સમાં ઉમેરો (Enter) ]</button></div>
                </form>
            </div>
        </div>

        <script>
            setTimeout(function(){{
                if(typeof switchF3SubForm === 'function') switchF3SubForm();
                if(typeof onF3ReceiveTypeChange === 'function') onF3ReceiveTypeChange();
            }}, 25);
            function onF3ReceiveTypeChange(){{
                var rt = (document.getElementById('f3_rec_type_sel') || {{}}).value || 'CUST_DUE';
                var custRows = document.getElementById('f3_rec_cust_due_rows');
                var lapuBox = document.getElementById('f3_recharge_lapu_box');
                var dueSel = document.getElementById('f3_due_sel');
                var amtLbl = document.getElementById('f3_rec_amt_lbl');
                var noteInp = document.getElementById('f3_rec_note_inp');
                var gSel = document.querySelector('#f3_sub_receive select[name="galla_name"]');
                if(rt === 'CUST_DUE'){{
                    if(custRows) custRows.style.display = 'block';
                    if(lapuBox) lapuBox.style.display = 'none';
                    if(dueSel) dueSel.required = true;
                    if(amtLbl) amtLbl.innerText = '૪. આજે વસૂલ રકમ (₹):';
                    if(gSel) gSel.value = 'BANK_CASH';
                }} else if(rt === 'ACC_INCOME'){{
                    if(custRows) custRows.style.display = 'none';
                    if(lapuBox) lapuBox.style.display = 'none';
                    if(dueSel) dueSel.required = false;
                    if(amtLbl) amtLbl.innerText = '૪. સાંજનો એસેસરીઝ લમ્પ-સમ વકરો (₹):';
                    if(noteInp && !noteInp.value) noteInp.value = 'એસેસરીઝ દૈનિક લમ્પ-સમ વકરો';
                    if(gSel) gSel.value = 'ACC_DCASH';
                }} else if(rt === 'RECH_INCOME'){{
                    if(custRows) custRows.style.display = 'none';
                    if(lapuBox) lapuBox.style.display = 'block';
                    if(dueSel) dueSel.required = false;
                    if(amtLbl) amtLbl.innerText = '૪. સાંજનો રિચાર્જ લમ્પ-સમ વકરો (₹):';
                    if(noteInp && !noteInp.value) noteInp.value = 'રિચાર્જ આખા દિવસનો લમ્પ-સમ વકરો';
                    if(gSel) gSel.value = 'RECHARGE';
                    calcF3LapuTable();
                }}
            }}
            function onF3ExpenseTypeChange(){{
                var tp = document.getElementById('f3_exp_type_sel').value;
                var lapuBox = document.getElementById('f3_recharge_lapu_box');
                var headInp = document.getElementById('f3_exp_head_inp');
                var amtLbl = document.getElementById('f3_exp_amt_lbl');
                var gSel = document.querySelector('#f3_sub_expense select[name="galla_name"]');
                if (tp === 'RECH_INCOME') {{
                    if (lapuBox) lapuBox.style.display = 'block';
                    if (headInp && !headInp.value) headInp.value = 'રિચાર્જ આખા દિવસનો લમ્પ-સમ વકરો';
                    if (amtLbl) amtLbl.innerText = '૩. રિચાર્જ આખા દિવસની ટોટલ અમાઉન્ટ (₹):';
                    if (gSel) gSel.value = 'RECHARGE';
                    calcF3LapuTable();
                }} else if (tp === 'ACC_INCOME') {{
                    if (lapuBox) lapuBox.style.display = 'none';
                    if (headInp && headInp.value === 'રિચાર્જ આખા દિવસનો લમ્પ-સમ વકરો') headInp.value = 'એસેસરીઝ દૈનિક લમ્પ-સમ વકરો';
                    if (amtLbl) amtLbl.innerText = '૩. એસેસરીઝ વકરાની કુલ રકમ (₹):';
                    if (gSel) gSel.value = 'ACC_DCASH';
                }} else {{
                    if (lapuBox) lapuBox.style.display = 'none';
                    if (amtLbl) amtLbl.innerText = '૩. ખર્ચ / વકરાની રકમ (₹):';
                }}
            }}
            function calcF3LapuTable(){{
                var rows = document.querySelectorAll('.f3-lapu-row');
                var totUsed = 0;
                rows.forEach(function(r){{
                    var idx = r.getAttribute('data-idx');
                    var op = parseFloat((document.getElementById('f3_lp_op_' + idx) || {{}}).value) || 0;
                    var top = parseFloat((document.getElementById('f3_lp_top_' + idx) || {{}}).value) || 0;
                    var clsEl = document.getElementById('f3_lp_cls_' + idx);
                    var useEl = document.getElementById('f3_lp_use_' + idx);
                    if (clsEl && clsEl.value !== '') {{
                        var cls = parseFloat(clsEl.value) || 0;
                        var used = Math.max(0, Math.round(op + top - cls));
                        if (useEl) useEl.value = used;
                        totUsed += used;
                    }} else if (useEl) {{
                        totUsed += (parseFloat(useEl.value) || 0);
                    }}
                }});
                var cashAmt = parseFloat((document.getElementById('f3_rec_amt') || {{}}).value) || 0;
                var uEl = document.getElementById('f3_lp_tot_used');
                var cEl = document.getElementById('f3_lp_tot_cash');
                var dEl = document.getElementById('f3_lp_diff_badge');
                if (uEl) uEl.innerText = '₹' + Math.round(totUsed).toLocaleString('en-IN');
                if (cEl) cEl.innerText = '₹' + Math.round(cashAmt).toLocaleString('en-IN');
                if (dEl) {{
                    var diff = Math.round(cashAmt - totUsed);
                    if (totUsed === 0) {{
                        dEl.innerText = '💡 સાંજનું ક્લોઝિંગ લખશો એટલે ₹' + Math.round(cashAmt) + ' નો તાળો બતાવશે (મરજિયાત)';
                    }} else if (diff === 0) {{
                        dEl.innerText = '✅ પરફેક્ટ તાળો મેચ! (તફાવત: ₹0)';
                        dEl.style.background = '#dcfce7';
                        dEl.style.color = '#166534';
                    }} else {{
                        dEl.innerText = 'તાળો / કમિશન તફાવત: ' + (diff > 0 ? '+' : '') + '₹' + diff;
                        dEl.style.background = '#fef9c3';
                        dEl.style.color = '#854d0e';
                    }}
                }}
            }}
            function addNewLapuOperatorF3(){{
                var nm = prompt('📱 નવી રિચાર્જ કંપની / ઓપરેટરનું નામ લખો (દા.ત. BSNL, DTH, Tata Play):');
                if (!nm || !nm.trim()) return;
                var fd = new FormData();
                fd.append('action', 'ADD');
                fd.append('company', nm.trim());
                fetch('/api/manage-lapu-operator', {{method:'POST', body:fd}}).then(r=>r.json()).then(d=>{{
                    if(d.ok) window.location.href='/?sheet=SMART_TERMINAL&mode=F3';
                    else alert(d.msg || 'એરર');
                }});
            }}
            function renameLapuOperatorF3(oldName){{
                var nm = prompt('✏️ "' + oldName + '" નું નવું નામ લખો:', oldName);
                if (!nm || !nm.trim() || nm.trim() === oldName) return;
                var fd = new FormData();
                fd.append('action', 'RENAME');
                fd.append('company', oldName);
                fd.append('new_name', nm.trim());
                fetch('/api/manage-lapu-operator', {{method:'POST', body:fd}}).then(r=>r.json()).then(d=>{{
                    if(d.ok) window.location.href='/?sheet=SMART_TERMINAL&mode=F3';
                    else alert(d.msg || 'એરર');
                }});
            }}
            function deleteLapuOperatorF3(compName){{
                if (!confirm('શું "' + compName + '" કંપની લિસ્ટમાંથી કાઢી નાખવી છે?')) return;
                var fd = new FormData();
                fd.append('action', 'DELETE');
                fd.append('company', compName);
                fetch('/api/manage-lapu-operator', {{method:'POST', body:fd}}).then(r=>r.json()).then(d=>{{
                    if(d.ok) window.location.href='/?sheet=SMART_TERMINAL&mode=F3';
                    else alert(d.msg || 'એરર');
                }});
            }}
            function switchF3SubForm(){{
                var m = document.getElementById('f3_master_mode').value;
                document.getElementById('f3_sub_receive').style.display = (m === 'PAY_RECEIVE') ? 'block' : 'none';
                document.getElementById('f3_sub_payout').style.display = (m === 'PAY_OUT') ? 'block' : 'none';
                document.getElementById('f3_sub_expense').style.display = (m === 'STORE_EXPENSE') ? 'block' : 'none';
                var du = document.getElementById('f3_sub_direct_udhar');
                var pc = document.getElementById('f3_sub_partner_cap');
                var lp = document.getElementById('f3_sub_lapu_purchase');
                if (du) du.style.display = (m === 'DIRECT_UDHAR') ? 'block' : 'none';
                if (pc) pc.style.display = (m === 'PARTNER_CAPITAL') ? 'block' : 'none';
                if (lp) lp.style.display = (m === 'LAPU_PURCHASE') ? 'block' : 'none';
            }}
            function calcF3LapuPurchaseDiff(){{
                var inB = parseFloat(document.getElementById('f3_lp_in_bal').value || 0);
                var pdB = parseFloat(document.getElementById('f3_lp_paid_amt').value || 0);
                var diff = inB - pdB;
                var bdg = document.getElementById('f3_lp_comm_badge');
                if(bdg) bdg.innerText = 'કમિશન / તફાવત: ₹' + diff.toLocaleString('en-IN');
            }}
            function toggleF3PayoutTarget(){{
                var t = document.getElementById('f3_po_type').value;
                document.getElementById('f3_po_supp').style.display = (t === 'SUPPLIER') ? 'inline-block' : 'none';
                document.getElementById('f3_po_staff').style.display = (t === 'STAFF') ? 'inline-block' : 'none';
                var sHead = document.getElementById('f3_po_staff_head_row');
                if (sHead) sHead.style.display = (t === 'STAFF') ? 'flex' : 'none';
            }}
            function onF3DueSelect(){{
                var sel = document.getElementById('f3_due_sel');
                var opt = sel.options[sel.selectedIndex];
                if(opt) document.getElementById('f3_rec_amt').value = opt.getAttribute('data-rem') || 0;
            }}
            function onF3PartnerTxTypeChange(){{
                var txType = (document.getElementById('f3_part_tx_type') || {{}}).value || 'CAPITAL_IN';
                var fundRow = document.getElementById('f3_part_funding_row');
                var fundSel = document.getElementById('f3_part_fund_sel');
                if(txType === 'GIFT_IN'){{
                    if(fundRow) fundRow.style.display = 'flex';
                }} else {{
                    if(fundRow) fundRow.style.display = 'none';
                    if(fundSel) fundSel.value = 'STORE_GALLA';
                }}
                onF3PartnerFundChange();
            }}
            function onF3PartnerFundChange(){{
                var txType = (document.getElementById('f3_part_tx_type') || {{}}).value || 'CAPITAL_IN';
                var fundSel = (document.getElementById('f3_part_fund_sel') || {{}}).value || 'STORE_GALLA';
                var payModeSel = document.getElementById('f3_part_pay_mode');
                var gallaRow = document.getElementById('f3_part_galla_row');
                var isPocket = (txType === 'GIFT_IN' && fundSel === 'PARTNER_POCKET') || (payModeSel && payModeSel.value.indexOf('ખિસ્સામાંથી') !== -1);
                if(isPocket){{
                    if(gallaRow) gallaRow.style.display = 'none';
                    if(payModeSel && payModeSel.value.indexOf('ખિસ્સામાંથી') === -1){{
                        payModeSel.value = 'પાર્ટનર અંગત ખિસ્સામાંથી (ગલ્લા સિવાય)';
                    }}
                }} else {{
                    if(gallaRow) gallaRow.style.display = 'flex';
                    if(payModeSel && payModeSel.value.indexOf('ખિસ્સામાંથી') !== -1){{
                        payModeSel.value = 'રોકડ (Cash)';
                    }}
                }}
            }}
            function promptNewPartnerF3(){{
                var nm = prompt('🤝 નવા પાર્ટનરનું પૂરું નામ અને હોદ્દો લખો (દા.ત. પાર્ટનર ૨ - ભાવેશભાઈ પટેલ):');
                if(nm && nm.trim()){{
                    var sel = document.getElementById('f3_part_name_sel');
                    if(sel){{
                        var o = document.createElement('option');
                        o.value = nm.trim();
                        o.text = nm.trim();
                        o.selected = true;
                        sel.add(o);
                    }}
                }}
            }}

            function sendF3WhatsAppReminder(){{
                var sel = document.getElementById('f3_due_sel');
                var opt = sel.options[sel.selectedIndex];
                if(!opt || !opt.value){{ alert('પહેલા બાકી ગ્રાહક સિલેક્ટ કરો!'); return; }}
                var ph = opt.getAttribute('data-ph') || '';
                var nm = opt.getAttribute('data-name') || 'ગ્રાહક';
                var rem = opt.getAttribute('data-rem') || '0';
                var msg = 'નમસ્તે ' + nm + ', આપની બાકી રકમ ₹' + rem + ' છે. કૃપા કરીને ચૂકવવા વિનંતી.';
                window.open('https://wa.me/91' + ph.replace(/\\D/g,'').slice(-10) + '?text=' + encodeURIComponent(msg), '_blank');
            }}
        </script>
        """

    # =========================================================================
    # [F4] બેંક ડિપોઝિટ અને વિડ્રોલ લોગ (૫-સ્ત્રોત મલ્ટી-ગલ્લા સ્પ્લિટ સાથે) + બાકી વસૂલાત
    # =========================================================================
    elif mode == "F4":
        if st_mode == "FRANCHISE_HO":
            tx_type_opts = '<option value="DEPOSIT">૧. બેંક ડિપોઝિટ (Bank Deposit - ફ્રેન્ચાઇઝી HO મોડમાં માત્ર ડિપોઝિટ)</option>'
        else:
            tx_type_opts = '<option value="DEPOSIT">૧. બેંક ડિપોઝિટ (Bank Deposit)</option><option value="WITHDRAWAL">૨. બેંક વિડ્રોલ (રોકડ ઉપાડ)</option>'

        c.execute("SELECT date, time_str, bank_name, amount, source_type, depositor, remarks FROM bank_deposit_log ORDER BY id DESC LIMIT 15")
        b_logs = c.fetchall()
        blog_trs = "".join([
            f"<tr><td>{r[0]} {r[1] or ''}</td><td><b>{r[2]}</b></td><td style='font-weight:bold; color:#15803d;'>₹{float(r[3] or 0):,.0f}</td><td>{r[4]}</td><td>{r[5] or '-'}</td><td>{r[6] or '-'}</td></tr>"
            for r in b_logs
        ]) or "<tr><td colspan='6'>આજે કોઈ બેંક ડિપોઝિટ કે વિડ્રોલ એન્ટ્રી થયેલ નથી</td></tr>"

        form_html = f"""
        <div class="mode-banner">
            <span>મોડ: [F4] બેંક ડિપોઝિટ & વિડ્રોલ લોગ (૫-સ્ત્રોત મલ્ટી-ગલ્લા સ્પ્લિટ - ૯ ખાનાં)</span>
            <span style="font-size:11.5px;">નોંધ: ગ્રાહક બાકી ઉધાર વસૂલાત [F3] વિકલ્પ (૧) માં છે; અહીં માત્ર શુદ્ધ બેંક ડિપોઝિટ અને વિડ્રોલ લોગ રહેશે</span>
        </div>

        <div style="display:grid; grid-template-columns:1.1fr 0.9fr; gap:12px; padding:8px;">
            <!-- ડાબો ભાગ: [F4] બેંક ડિપોઝિટ અને વિડ્રોલ લોગ (૫-સ્ત્રોત મલ્ટી-ગલ્લા સ્પ્લિટ) -->
            <div style="background:#f8fafc; border:2px solid #0284c7; border-radius:6px; padding:12px;">
                <h4 style="margin:0 0 8px 0; color:#0f2043;">🏦 [F4] બેંક ડિપોઝિટ & વિડ્રોલ લોગ (૫-સ્ત્રોત મલ્ટી-ગલ્લા સ્પ્લિટ - ૯ ખાનાં)</h4>
                <form class="f-enter-form" action="/save-bank-deposit" method="post">
                    <div class="f-row"><div class="lbl" style="width:210px;">૧. ટ્રાન્ઝેક્શન પ્રકાર:</div><select name="tx_type" style="font-weight:bold;">{tx_type_opts}</select></div>
                    <div class="f-row"><div class="lbl" style="width:210px;">૨. તારીખ & સમય:</div><input type="date" name="dep_date" value="{today_str}"></div>
                    <div class="f-row">
                        <div class="lbl" style="width:210px;">૩. બેંકનું નામ & ખાતા નંબર:</div>
                        <select name="bank_name" id="f4_bank_sel" style="flex:1; font-weight:bold;">{bank_opts_html}</select>
                        <button type="button" onclick="manageF4Bank('ADD')" style="background:#16a34a; color:white; border:none; padding:6px 9px; border-radius:4px; font-weight:bold; font-size:11px; cursor:pointer; white-space:nowrap;" title="નવી બેંક ઉમેરો">[+ બેંક ઉમેરો]</button>
                        <button type="button" onclick="manageF4Bank('EDIT')" style="background:#0284c7; color:white; border:none; padding:6px 8px; border-radius:4px; font-weight:bold; font-size:11px; cursor:pointer; white-space:nowrap;" title="પસંદ કરેલ બેંકનું નામ સુધારો">[✏️ એડિટ]</button>
                        <button type="button" onclick="manageF4Bank('DELETE')" style="background:#dc2626; color:white; border:none; padding:6px 9px; border-radius:4px; font-weight:bold; font-size:11px; cursor:pointer; white-space:nowrap;" title="પસંદ કરેલ બેંક કાઢી નાખો (સિક્યુરિટી PIN)">[🗑️ બેંક કાઢો]</button>
                    </div>
                    <div style="background:#ffffff; border:1px solid #94a3b8; border-radius:6px; padding:8px; margin:6px 0;">
                        <div style="font-weight:bold; color:#0369a1; margin-bottom:4px; font-size:11.5px;">૪. મલ્ટી-ગલ્લા સ્પ્લિટ ટેબલ (૫ સ્પષ્ટ ખાનાં):</div>
                        <div class="f-row" style="background:#fef9c3; padding:4px; border-radius:4px;">
                            <div class="lbl" style="width:225px; font-weight:800; color:#854d0e;">(ક) ગલ્લો ૧ - આજની ઓપનિંગ કેશ (₹):</div>
                            <input type="number" step="any" name="dep_yest_bank" id="f4_bd1" value="0" oninput="calcF4BankTot()" style="font-weight:bold;" title="ગઈકાલ સાંજની ક્લોઝિંગ = આજ સવારની ઓપનિંગ કેશ">
                        </div>
                        <div class="f-row" style="background:#dcfce7; padding:4px; border-radius:4px;">
                            <div class="lbl" style="width:225px; font-weight:800; color:#166534;">(ખ) ગલ્લો ૧ - આજની ફ્રેશ કાઉન્ટર કેશ (₹):</div>
                            <input type="number" step="any" name="dep_bank_cash" id="f4_bd2" value="0" oninput="calcF4BankTot()" style="font-weight:bold; color:#15803d;" title="આજે કાઉન્ટર પર આવેલી નવી ફ્રેશ બેંક કેશ">
                        </div>
                        <div class="f-row"><div class="lbl" style="width:225px;">(ગ) ગલ્લો ૨ - એક્સેસરીઝ D-Cash (₹):</div><input type="number" step="any" name="dep_acc_cash" id="f4_bd3" value="0" oninput="calcF4BankTot()"></div>
                        <div class="f-row"><div class="lbl" style="width:225px;">(ઘ) ગલ્લો ૩ - રિચાર્જ કેશ (₹):</div><input type="number" step="any" name="dep_rech_cash" id="f4_bd4" value="0" oninput="calcF4BankTot()"></div>
                        <div class="f-row"><div class="lbl" style="width:225px;">(ચ) ગલ્લો ૪ - એક્સ્ટ્રા કેશ / તિજોરી (₹):</div><input type="number" step="any" name="dep_extra_cash" id="f4_bd5" value="0" oninput="calcF4BankTot()"></div>
                    </div>

                    <!-- 💵 બેંક પે-ઇન સ્લીપ: ચલણી નોટોની વિગત (Denomination Breakdown Table) -->
                    <div style="background:#f0fdf4; border:1.5px solid #16a34a; border-radius:6px; padding:8px; margin:6px 0;">
                        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:6px;">
                            <b style="color:#166534; font-size:12px;">💵 બેંક પે-ઇન સ્લીપ: ભરેલી ચલણી નોટોની ગણતરી (Denomination Table):</b>
                            <span id="f4_notes_match_badge" style="background:#dcfce7; color:#15803d; padding:2px 8px; border-radius:4px; font-size:11px; font-weight:bold; border:1px solid #16a34a;">નોટો કુલ: ₹0</span>
                        </div>
                        <input type="hidden" name="slip_notes_summary" id="f4_slip_notes_summary" value="">
                        <div style="display:grid; grid-template-columns:repeat(4, 1fr); gap:6px; font-size:11.5px;">
                            <div style="background:white; padding:4px 6px; border:1px solid #cbd5e1; border-radius:4px; display:flex; align-items:center; justify-content:space-between;">
                                <b>₹500 ×</b>
                                <input type="number" id="f4_n500" value="0" min="0" oninput="calcF4NotesSlip()" style="width:52px; padding:2px; text-align:center; font-weight:bold;">
                            </div>
                            <div style="background:white; padding:4px 6px; border:1px solid #cbd5e1; border-radius:4px; display:flex; align-items:center; justify-content:space-between;">
                                <b>₹200 ×</b>
                                <input type="number" id="f4_n200" value="0" min="0" oninput="calcF4NotesSlip()" style="width:52px; padding:2px; text-align:center; font-weight:bold;">
                            </div>
                            <div style="background:white; padding:4px 6px; border:1px solid #cbd5e1; border-radius:4px; display:flex; align-items:center; justify-content:space-between;">
                                <b>₹100 ×</b>
                                <input type="number" id="f4_n100" value="0" min="0" oninput="calcF4NotesSlip()" style="width:52px; padding:2px; text-align:center; font-weight:bold;">
                            </div>
                            <div style="background:white; padding:4px 6px; border:1px solid #cbd5e1; border-radius:4px; display:flex; align-items:center; justify-content:space-between;">
                                <b>₹50 ×</b>
                                <input type="number" id="f4_n50" value="0" min="0" oninput="calcF4NotesSlip()" style="width:52px; padding:2px; text-align:center; font-weight:bold;">
                            </div>
                            <div style="background:white; padding:4px 6px; border:1px solid #cbd5e1; border-radius:4px; display:flex; align-items:center; justify-content:space-between;">
                                <b>₹20 ×</b>
                                <input type="number" id="f4_n20" value="0" min="0" oninput="calcF4NotesSlip()" style="width:52px; padding:2px; text-align:center; font-weight:bold;">
                            </div>
                            <div style="background:white; padding:4px 6px; border:1px solid #cbd5e1; border-radius:4px; display:flex; align-items:center; justify-content:space-between;">
                                <b>₹10 ×</b>
                                <input type="number" id="f4_n10" value="0" min="0" oninput="calcF4NotesSlip()" style="width:52px; padding:2px; text-align:center; font-weight:bold;">
                            </div>
                            <div style="background:white; padding:4px 6px; border:1px solid #cbd5e1; border-radius:4px; display:flex; align-items:center; justify-content:space-between; grid-column:span 2;">
                                <b>સિક્કા / પરચૂરણ (₹):</b>
                                <input type="number" id="f4_ncoins" value="0" min="0" oninput="calcF4NotesSlip()" style="width:75px; padding:2px; text-align:center; font-weight:bold;">
                            </div>
                        </div>
                    </div>
                    <div class="f-row" style="background:#e0f2fe; padding:4px; border-radius:4px;">
                        <div class="lbl" style="width:210px; color:#1d4ed8;">૫. કુલ રકમ (Total Amount ₹):</div>
                        <input type="number" step="any" id="f4_bd_tot" value="0" readonly style="font-weight:bold; color:#1d4ed8;">
                    </div>
                    <div class="f-row"><div class="lbl" style="width:210px;">૬. ભરનાર સ્ટાફ નામ:</div><select name="depositor">{staff_opts_html}</select> <a href="/?sheet=STAFF_ATTENDANCE_SHEET" target="_blank" style="margin-left:6px; background:#10b981; color:white; padding:4px 8px; border-radius:4px; text-decoration:none; font-size:11px; font-weight:bold;">[+ નવો સ્ટાફ (શીટ ૧૩)]</a></div>
                    <div class="f-row"><div class="lbl" style="width:210px;">૭. બેંક સ્લીપ / રેફરન્સ & રિમાર્ક:</div><input type="text" name="remarks" placeholder="સ્લીપ નંબર / નોંધ..."></div>
                    <button type="submit" style="width:100%; background:#0f2043; color:white; border:none; padding:9px; border-radius:4px; font-weight:bold; margin-top:6px; cursor:pointer;">૮. [ સેવ બેંક ટ્રાન્ઝેક્શન (Enter) ]</button>
                </form>
            </div>

            <!-- જમણો ભાગ: તાજેતરના બેંક ડિપોઝિટ અને વિડ્રોલ વ્યવહારોનું રજીસ્ટર -->
            <div style="background:#ffffff; border:1px solid #cbd5e1; border-radius:6px; padding:12px;">
                <h4 style="margin:0 0 8px 0; color:#0369a1;">📋 તાજેતરના બેંક ડિપોઝિટ & વિડ્રોલ વ્યવહારો (Live Bank Register)</h4>
                <table class="live-grid">
                    <tr><th>તારીખ</th><th>બેંક નામ</th><th>રકમ (₹)</th><th>ગલ્લા સ્ત્રોત</th><th>ભરનાર સ્ટાફ</th><th>નોંધ</th></tr>
                    {blog_trs}
                </table>
            </div>
        </div>
        <script>
            function calcF4BankTot(){{
                var s = 0;
                for(var i=1; i<=5; i++) s += (parseFloat(document.getElementById('f4_bd'+i).value) || 0);
                document.getElementById('f4_bd_tot').value = Math.round(s);
                calcF4NotesSlip();
            }}
            function calcF4NotesSlip(){{
                var n500 = parseInt(document.getElementById('f4_n500')?.value || 0);
                var n200 = parseInt(document.getElementById('f4_n200')?.value || 0);
                var n100 = parseInt(document.getElementById('f4_n100')?.value || 0);
                var n50  = parseInt(document.getElementById('f4_n50')?.value || 0);
                var n20  = parseInt(document.getElementById('f4_n20')?.value || 0);
                var n10  = parseInt(document.getElementById('f4_n10')?.value || 0);
                var coins = parseFloat(document.getElementById('f4_ncoins')?.value || 0);
                var notesSum = (n500*500) + (n200*200) + (n100*100) + (n50*50) + (n20*20) + (n10*10) + coins;
                var parts = [];
                if(n500>0) parts.push('500x'+n500);
                if(n200>0) parts.push('200x'+n200);
                if(n100>0) parts.push('100x'+n100);
                if(n50>0)  parts.push('50x'+n50);
                if(n20>0)  parts.push('20x'+n20);
                if(n10>0)  parts.push('10x'+n10);
                if(coins>0) parts.push('Coins:'+coins);
                var sumInp = document.getElementById('f4_slip_notes_summary');
                if(sumInp) sumInp.value = parts.length ? ('[નોટો: ' + parts.join(', ') + ' = ₹' + notesSum + ']') : '';
                var bdg = document.getElementById('f4_notes_match_badge');
                var totDep = parseFloat(document.getElementById('f4_bd_tot')?.value || 0);
                if(bdg){{
                    if(notesSum > 0 && totDep > 0 && Math.abs(notesSum - totDep) > 0.5){{
                        bdg.style.background = '#fef2f2';
                        bdg.style.color = '#dc2626';
                        bdg.style.borderColor = '#dc2626';
                        bdg.innerText = '⚠️ નોટો કુલ: ₹' + notesSum.toLocaleString('en-IN') + ' (તફાવત: ₹' + (notesSum - totDep).toLocaleString('en-IN') + ')';
                    }} else {{
                        bdg.style.background = '#dcfce7';
                        bdg.style.color = '#15803d';
                        bdg.style.borderColor = '#16a34a';
                        bdg.innerText = '✅ નોટો કુલ: ₹' + notesSum.toLocaleString('en-IN');
                    }}
                }}
            }}
            function manageF4Bank(act){{
                var sel = document.getElementById('f4_bank_sel');
                var curBank = sel ? sel.value : '';
                var fd = new FormData();
                fd.append('action', act);
                if (act === 'ADD') {{
                    var nm = prompt('🏦 નવી બેંકનું નામ અને ખાતા નંબર લખો (દા.ત. Kotak Bank - A/c 4512):');
                    if (!nm || !nm.trim()) return;
                    fd.append('bank_name', nm.trim());
                }} else if (act === 'EDIT') {{
                    if (!curBank) {{ alert('પહેલાં ડ્રોપડાઉનમાંથી બેંક પસંદ કરો!'); return; }}
                    var newNm = prompt('✏️ બેંક "' + curBank + '" નું નવું નામ લખો:', curBank);
                    if (!newNm || !newNm.trim() || newNm.trim() === curBank) return;
                    fd.append('bank_name', curBank);
                    fd.append('new_name', newNm.trim());
                }} else if (act === 'DELETE') {{
                    if (!curBank) {{ alert('પહેલાં ડ્રોપડાઉનમાંથી બેંક પસંદ કરો!'); return; }}
                    var pin = prompt('🗑️ બેંક "' + curBank + '" લિસ્ટમાંથી કાઢી નાખવા સિક્યુરિટી માસ્ટર PIN નાખો:');
                    if (!pin) return;
                    fd.append('bank_name', curBank);
                    fd.append('pin', pin.trim());
                }}
                fetch('/api/manage-bank-f4', {{method:'POST', body:fd}}).then(r=>r.json()).then(d=>{{
                    if(d.ok) window.location.href='/?sheet=SMART_TERMINAL&mode=F4';
                    else alert(d.msg || 'એરર');
                }});
            }}
        </script>
        """

    elif mode in ("F5", "F6", "F7", "F8"):
        form_html = part2_c_counters_extra.render_f5_to_f8(
            conn, c, mode, staff_opts_html, all_galla_options, bank_opts, exp_heads, today_str, shop_prof
        )

    c.execute("SELECT id, entry_time, bill_no, customer_name, model_name, imei, galla_name, entry_type, total_padtar, gift_amt, due_amt, salesman, doc_path FROM live_terminal_grid ORDER BY id DESC LIMIT 35")
    grid_rows = c.fetchall()
    tr_html = ""
    for r in grid_rows:
        doc_link = f" <a href='{r[12]}' target='_blank' style='background:#0d9488; color:white; padding:2px 6px; border-radius:3px; text-decoration:none;'>📄 ફાઇલ</a>" if r[12] else ""
        tr_html += f"""
        <tr>
            <td>{r[1]}</td><td><b>{r[2]}</b></td><td>{r[3]}</td><td>{r[4]}</td><td>{r[5]}</td>
            <td><b>{r[6]}</b></td><td><b>{r[7]}</b></td><td>₹{float(r[8] or 0):,.0f}</td>
            <td>₹{float(r[9] or 0):,.0f}</td><td style="color:#dc2626; font-weight:bold;">₹{float(r[10] or 0):,.0f}</td>
            <td>{r[11]}</td>
            <td>
                <a href="/print-invoice?bill_no={urllib.parse.quote(str(r[2]))}" target="_blank" style="background:#0284c7; color:white; padding:2px 6px; border-radius:3px; text-decoration:none; font-weight:bold;">🖨️ પ્રિન્ટ</a>{doc_link}
                <a href="javascript:void(0)" onclick="var p=prompt('આ એન્ટ્રી રદ કરી તેની રોકડ/સ્ટોક અસર રિવર્સ કરવા સિક્યુરિટી માસ્ટર PIN નાખો:'); if(p) window.location.href='/api/delete-running-tx?id={r[0]}&pin='+encodeURIComponent(p);" style="background:#dc2626; color:white; padding:2px 6px; border-radius:3px; text-decoration:none; font-weight:bold; margin-left:3px;">🗑️ રદ</a>
            </td>
        </tr>
        """

    return f"""
    {f_strip_html}
    {form_html}
    <div class="grid-head">
        <span>આજના જમા થયેલ વ્યવહારો (લાઈવ રનિંગ ટ્રાન્ઝેક્શન ગ્રીડ)</span>
        <span style="font-size:11px; color:#38bdf8;">સેવ થતાં જ અહીં નવી એન્ટ્રી લાઈવ ઉમેરાય છે</span>
    </div>
    <table class="live-grid">
        <tr><th>સમય</th><th>બિલ #</th><th>ગ્રાહક / પાર્ટી</th><th>મોડેલ / વિગત</th><th>IMEI</th><th>સંબંધિત ગલ્લો</th><th>પ્રકાર</th><th>રકમ (₹)</th><th>ગિફ્ટ</th><th>બાકી</th><th>સેલ્સમેન</th><th>પ્રિન્ટ / PDF / ફાઇલ</th></tr>
        {tr_html}
    </table>
    """

def render_universal_search(
    conn, c, search_q, u_tab, sel_cust, sel_sm_hist, sel_sm_due,
    sel_supp, bb_view, bb_stock_opts, staff_list, all_galla_options, indian_lang_options,
    shop_prof=None
):
    sid = (shop_prof or {}).get("shop_id") or "DEVANSHI"
    q_filter = f"%{(search_q or '').strip()}%"
    records_count = 0
    net_outstanding = 0.0
    grid_html = ""
    active_tab_title = ""
    dropdown_bar_html = ""

    # ૧. ગ્રાહક સર્ચ (Customer Passbook - Rule 115 સિંગલ-લાઇન ડ્રોપડાઉન)
    if u_tab == "customer":
        active_tab_title = "૧. ગ્રાહક સર્ચ (Customer Passbook - Rule 115 સિંગલ-લાઇન ડ્રોપડાઉન)"
        c.execute("""
            SELECT MAX(date), customer_name, phone, salesman, (SUM(due_amt) - SUM(received_amt)) as bal
            FROM customer_due_ledger WHERE customer_name != '' AND (store_id = ? OR store_id IS NULL OR store_id = '')
            GROUP BY customer_name ORDER BY bal DESC
        """, (sid,))
        cust_list_rows = c.fetchall()
        cust_opts = "".join([
            f'<option value="{r[1]}" {"selected" if sel_cust==r[1] else ""}>[{r[0]}] | [{r[1]}] | [{r[2] or "-"}] | [{r[3] or "-"}] | [છેલ્લી બાકી: ₹{float(r[4] or 0):,.0f}]</option>'
            for r in cust_list_rows
        ])

        dropdown_bar_html = f"""
        <div style="background:#f1f5f9; padding:8px; border:1px solid #cbd5e1; border-radius:4px; margin-bottom:8px; display:flex; gap:10px; align-items:center;">
            <b>ગ્રાહક ઉધાર પાસબુક ડ્રોપડાઉન (Rule 115):</b>
            <select onchange="window.location.href='/?sheet=UNIVERSAL_SEARCH&u_tab=customer&sel_cust='+encodeURIComponent(this.value)" style="padding:6px; flex:1; font-weight:bold;">
                <option value="">-- [તારીખ] | [ગ્રાહકનું નામ] | [મોબાઈલ નંબર] | [સેલ્સમેન] | [છેલ્લી બાકી રકમ] --</option>
                {cust_opts}
            </select>
        </div>
        """

        if sel_cust:
            c.execute("SELECT date, bill_no, customer_name, due_amt, received_amt, (due_amt - received_amt) as bal, salesman, phone FROM customer_due_ledger WHERE customer_name = ? AND (store_id = ? OR store_id IS NULL OR store_id = '') ORDER BY id DESC", (sel_cust, sid))
        elif search_q.strip():
            c.execute("SELECT date, bill_no, customer_name, due_amt, received_amt, (due_amt - received_amt) as bal, salesman, phone FROM customer_due_ledger WHERE (customer_name LIKE ? OR phone LIKE ? OR bill_no LIKE ?) AND (store_id = ? OR store_id IS NULL OR store_id = '') ORDER BY id DESC", (q_filter, q_filter, q_filter, sid))
        else:
            c.execute("SELECT date, bill_no, customer_name, due_amt, received_amt, (due_amt - received_amt) as bal, salesman, phone FROM customer_due_ledger WHERE (store_id = ? OR store_id IS NULL OR store_id = '') ORDER BY id DESC LIMIT 25", (sid,))

        rows = c.fetchall()
        records_count = len(rows)
        for r in rows:
            bal = float(r[5] or 0)
            net_outstanding += bal
            wa_btn = ""
            if r[7] and len(str(r[7])) >= 10:
                wa_msg = f"નમસ્તે {r[2]}, આપની બાકી રકમ ₹{bal:,.0f} છે. સંપર્ક: 9725721215."
                wa_btn = f"<a href='https://wa.me/91{str(r[7])[-10:]}?text={urllib.parse.quote(wa_msg)}' target='_blank' style='background:#16a34a; color:white; padding:2px 6px; border-radius:3px; text-decoration:none;'>WhatsApp</a>"
            grid_html += f"<tr><td>{r[0]}</td><td><b>{r[1]}</b></td><td>{r[2]} ({r[7]})</td><td>₹{float(r[3] or 0):,.0f}</td><td>₹{float(r[4] or 0):,.0f}</td><td style='color:red; font-weight:bold;'>₹{bal:,.0f}</td><td>{r[6]} {wa_btn}</td></tr>"

    # ૨. સેલ્સમેન સર્ચ (Salesman History & Due Customers)
    elif u_tab == "salesman":
        active_tab_title = "૨. સેલ્સમેન સર્ચ (Salesman History & Due Customers)"
        c.execute("SELECT DISTINCT name FROM config_staff ORDER BY name ASC")
        all_staff_names = [r[0] for r in c.fetchall()]
        sm_hist_opts = "".join([f'<option value="{sn}" {"selected" if sel_sm_hist==sn else ""}>{sn}</option>' for sn in all_staff_names])
        sm_due_opts = "".join([f'<option value="{sn}" {"selected" if sel_sm_due==sn else ""}>{sn}</option>' for sn in all_staff_names])

        dropdown_bar_html = f"""
        <div style="background:#f1f5f9; padding:8px; border:1px solid #cbd5e1; border-radius:4px; margin-bottom:8px; display:grid; grid-template-columns: 1fr 1fr; gap:10px;">
            <div>
                <b>૧. સેલ્સમેન પર્સનલ હિસ્ટ્રી:</b>
                <select onchange="window.location.href='/?sheet=UNIVERSAL_SEARCH&u_tab=salesman&sel_sm_hist='+encodeURIComponent(this.value)" style="width:100%; padding:6px; margin-top:4px;">
                    <option value="">-- સેલ્સમેન પસંદ કરો --</option>
                    {sm_hist_opts}
                </select>
            </div>
            <div>
                <b>૨. તે સેલ્સમેનના બાકી ગ્રાહકો:</b>
                <select onchange="window.location.href='/?sheet=UNIVERSAL_SEARCH&u_tab=salesman&sel_sm_due='+encodeURIComponent(this.value)" style="width:100%; padding:6px; margin-top:4px;">
                    <option value="">-- સેલ્સમેન વાઇઝ બાકી લિસ્ટ --</option>
                    {sm_due_opts}
                </select>
            </div>
        </div>
        """

        if sel_sm_due:
            c.execute("SELECT date, bill_no, customer_name, due_amt, received_amt, (due_amt - received_amt) as bal, salesman, phone FROM customer_due_ledger WHERE salesman LIKE ? AND (due_amt - received_amt) > 0 AND (store_id = ? OR store_id IS NULL OR store_id = '') ORDER BY id DESC", (f"%{sel_sm_due}%", sid))
            rows = c.fetchall()
            records_count = len(rows)
            for r in rows:
                bal = float(r[5] or 0)
                net_outstanding += bal
                wa_btn = f"<a href='https://wa.me/91{str(r[7])[-10:]}' target='_blank' style='background:#16a34a; color:white; padding:2px 6px; border-radius:3px; text-decoration:none;'>WhatsApp</a>" if (r[7] and len(str(r[7]))>=10) else ""
                grid_html += f"<tr><td>{r[0]}</td><td><b>{r[1]}</b></td><td>{r[2]} ({r[7]})</td><td>₹{float(r[3] or 0):,.0f}</td><td>₹{float(r[4] or 0):,.0f}</td><td style='color:red; font-weight:bold;'>₹{bal:,.0f}</td><td>{r[6]} {wa_btn}</td></tr>"
        else:
            sm_filter_val = sel_sm_hist if sel_sm_hist else (search_q if search_q.strip() else "")
            if sm_filter_val:
                c.execute("SELECT date, staff_name, entry_type, comm_earned, paid_amt, (comm_earned - paid_amt) as bal, remarks FROM staff_commission_ledger WHERE staff_name LIKE ? AND (store_id = ? OR store_id IS NULL OR store_id = '') ORDER BY id DESC", (f"%{sm_filter_val}%", sid))
            else:
                c.execute("SELECT date, staff_name, entry_type, comm_earned, paid_amt, (comm_earned - paid_amt) as bal, remarks FROM staff_commission_ledger WHERE (store_id = ? OR store_id IS NULL OR store_id = '') ORDER BY id DESC LIMIT 25", (sid,))
            rows = c.fetchall()
            records_count = len(rows)
            for r in rows:
                net_outstanding += float(r[5] or 0)
                grid_html += f"<tr><td>{r[0]}</td><td><b>{r[1]}</b></td><td>{r[2]}</td><td style='color:green;'>₹{float(r[3] or 0):,.0f}</td><td style='color:red;'>₹{float(r[4] or 0):,.0f}</td><td>₹{float(r[5] or 0):,.0f}</td><td>{r[6]}</td></tr>"

    # ૩. બાયબેક સ્ટોક સર્ચ (Rule 116 સિંગલ-લાઇન ડ્રોપડાઉન)
    elif u_tab == "buyback":
        active_tab_title = f"૩. બાયબેક સ્ટોક સર્ચ (Rule 116 સિંગલ-લાઇન ડ્રોપડાઉન) [{bb_view}]"
        c.execute("SELECT date, model, imei, salesman, total_cost FROM buyback_stock WHERE status = ? AND (store_id = ? OR store_id IS NULL OR store_id = '') ORDER BY id DESC", (bb_view, sid))
        bb_drop_rows = c.fetchall()
        bb_single_opts = "".join([
            f'<option value="{b[2]}">[{b[0]}] | [{b[1]}] | [{b[3] or "-"}] | [મૂળ પડતર: ₹{float(b[4] or 0):,.0f}]</option>'
            for b in bb_drop_rows
        ])
        dropdown_bar_html = f"""
        <div style="background:#f1f5f9; padding:8px; border:1px solid #cbd5e1; border-radius:4px; margin-bottom:8px; display:flex; gap:10px; align-items:center;">
            <b>સ્થિતિ:</b>
            <select onchange="window.location.href='/?sheet=UNIVERSAL_SEARCH&u_tab=buyback&bb_view='+this.value" style="padding:6px; width:190px;">
                <option value="IN_STOCK" {"selected" if bb_view=='IN_STOCK' else ""}>હાજર સ્ટોક (IN_STOCK)</option>
                <option value="SOLD" {"selected" if bb_view=='SOLD' else ""}>વેચાયેલા ફોન (SOLD)</option>
            </select>
            <b>બાયબેક પૂલ (Rule 116):</b>
            <select onchange="window.location.href='/?sheet=UNIVERSAL_SEARCH&u_tab=buyback&bb_view={bb_view}&search_q='+encodeURIComponent(this.value)" style="padding:6px; flex:1; font-weight:bold;">
                <option value="">-- [તારીખ] | [મોડેલ નામ] | [સેલ્સમેન] | [મૂળ પડતર કિંમત] --</option>
                {bb_single_opts}
            </select>
        </div>
        """
        c.execute("SELECT id, date, model, imei, purchase_cost, total_cost, status, customer_name, sale_price, sale_galla, salesman FROM buyback_stock WHERE status = ? AND (model LIKE ? OR imei LIKE ? OR customer_name LIKE ?) AND (store_id = ? OR store_id IS NULL OR store_id = '') ORDER BY id DESC", (bb_view, q_filter, q_filter, q_filter, sid))
        rows = c.fetchall()
        records_count = len(rows)
        for r in rows:
            cost = float(r[5] or 0)
            net_outstanding += cost
            re_inward_btn = ""
            if r[6] == "SOLD":
                btn_call = f"openReInwardModal({r[0]}, '{r[2]}', '{r[3]}', {r[8]}, '{r[9]}')"
                re_inward_btn = f"<button onclick='{btn_call}' style='background:#ea580c; color:white; border:none; padding:2px 6px; border-radius:3px; cursor:pointer;'>[પાછો સ્ટોકમાં લો]</button>"
            grid_html += f"<tr><td>{r[1]}</td><td>{r[3]}</td><td><b>{r[2]}</b> (ગ્રાહક: {r[7]} | સેલ્સમેન: {r[10] or '-'})</td><td>₹{cost:,.0f}</td><td>₹{float(r[8] or 0):,.0f}</td><td>{r[6]}</td><td>{re_inward_btn}</td></tr>"

    # ૪. વેપારી લેજર સર્ચ (Supplier Ledger & Credit Notes)
    elif u_tab == "supplier":
        active_tab_title = "૪. વેપારી લેજર સર્ચ (Supplier Ledger & Credit Notes)"
        c.execute("SELECT DISTINCT party_name FROM config_parties ORDER BY party_name ASC")
        all_supp_names = [r[0] for r in c.fetchall()]
        supp_opts = "".join([f'<option value="{sn}" {"selected" if sel_supp==sn else ""}>{sn}</option>' for sn in all_supp_names])

        dropdown_bar_html = f"""
        <div style="background:#f1f5f9; padding:8px; border:1px solid #cbd5e1; border-radius:4px; margin-bottom:8px; display:flex; gap:10px; align-items:center;">
            <b>વેપારી પસંદ કરો ડ્રોપડાઉન:</b>
            <select onchange="window.location.href='/?sheet=UNIVERSAL_SEARCH&u_tab=supplier&sel_supp='+encodeURIComponent(this.value)" style="padding:6px; flex:1;">
                <option value="">-- તમામ વેપારીઓમાંથી પસંદ કરો --</option>
                {supp_opts}
            </select>
        </div>
        """
        if sel_supp:
            c.execute("SELECT date, bill_no, supplier_name, total_bill, paid_amt, balance_due, entry_type, doc_path FROM supplier_purchase_ledger WHERE supplier_name = ? AND (store_id = ? OR store_id IS NULL OR store_id = '') ORDER BY id DESC", (sel_supp, sid))
        elif search_q.strip():
            c.execute("SELECT date, bill_no, supplier_name, total_bill, paid_amt, balance_due, entry_type, doc_path FROM supplier_purchase_ledger WHERE (supplier_name LIKE ? OR bill_no LIKE ?) AND (store_id = ? OR store_id IS NULL OR store_id = '') ORDER BY id DESC", (q_filter, q_filter, sid))
        else:
            c.execute("SELECT date, bill_no, supplier_name, total_bill, paid_amt, balance_due, entry_type, doc_path FROM supplier_purchase_ledger WHERE (store_id = ? OR store_id IS NULL OR store_id = '') ORDER BY id DESC LIMIT 25", (sid,))

        rows = c.fetchall()
        records_count = len(rows)
        for r in rows:
            bal = float(r[5] or 0)
            net_outstanding += bal
            doc_link = f"<a href='/{r[7]}' target='_blank' style='background:#0284c7; color:white; padding:2px 6px; border-radius:3px; text-decoration:none;'>PDF</a>" if r[7] else "-"
            grid_html += f"<tr><td>{r[0]}</td><td><b>{r[1]}</b></td><td>{r[2]}</td><td>₹{float(r[3] or 0):,.0f}</td><td>₹{float(r[4] or 0):,.0f}</td><td style='color:red;'>₹{bal:,.0f}</td><td>{r[6]} {doc_link}</td></tr>"

    # ૫. પાકા બિલ સર્ચ (Rule 127 - માસ્ટર PIN રક્ષણ)
    elif u_tab == "bill_search":
        active_tab_title = "૫. પાકા બિલ સર્ચ & ૧૨ ભારતીય ભાષામાં GST પ્રિન્ટ/PDF (Rule 127 - માસ્ટર PIN રક્ષણ)"
        c.execute("SELECT bill_no, bill_date, customer_name, phone, model, imei, mop_price, salesman FROM apx_sales_raw WHERE (bill_no LIKE ? OR customer_name LIKE ? OR phone LIKE ? OR imei LIKE ?) AND (store_id = ? OR store_id IS NULL OR store_id = '') ORDER BY id DESC LIMIT 35", (q_filter, q_filter, q_filter, q_filter, sid))
        rows = c.fetchall()
        records_count = len(rows)
        for r in rows:
            mop = float(r[6] or 0)
            net_outstanding += mop
            grid_html += f"""
            <tr>
                <td>{r[1]}</td><td><b>{r[0]}</b></td><td>{r[2]} ({r[3]})</td><td>₹{mop:,.0f}</td><td>{r[5]}</td><td>{r[4]}</td>
                <td>
                    <a href='/print-invoice?bill_no={r[0]}&lang=gu' target='_blank' style='background:#0284c7; color:white; padding:2px 6px; border-radius:3px; text-decoration:none; font-weight:bold;'>🖨️ બિલ / PDF (૧૨ ભાષા)</a>
                    <button onclick="openTempEditModal('{r[0]}', '{r[2]}', '{r[4]}', {mop})" style="background:#d97706; color:white; border:none; padding:2px 6px; border-radius:3px; cursor:pointer; font-weight:bold;">[ફાઇનાન્સ/PIN એડિટ]</button>
                </td>
            </tr>
            """

    # ૬. 📁 દસ્તાવેજ વૉલ્ટ (તમામ ફાઇલો)
    elif u_tab == "vault":
        active_tab_title = "૬. 📂 દસ્તાવેજ વૉલ્ટ (Document Vault - તમામ અપલોડ થયેલ ફાઇલો)"
        c.execute("SELECT id, upload_date, upload_time, category, original_name, stored_name, related_ref FROM document_vault WHERE (original_name LIKE ? OR category LIKE ? OR related_ref LIKE ?) AND (store_id = ? OR store_id IS NULL OR store_id = '') ORDER BY id DESC LIMIT 100", (q_filter, q_filter, q_filter, sid))
        rows = c.fetchall()
        records_count = len(rows)
        for r in rows:
            doc_link = f"<a href='/vault/{r[5]}' target='_blank' style='background:#0d9488; color:white; padding:3px 8px; border-radius:3px; text-decoration:none; font-weight:bold;'>📄 ફાઇલ જુઓ / ડાઉનલોડ</a>"
            grid_html += f"<tr><td>{r[1]} {r[2]}</td><td><b>{r[0]}</b></td><td>{r[3]} ({r[4]})</td><td>-</td><td>{r[6]}</td><td>-</td><td>{doc_link}</td></tr>"

    return f"""

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


    <div style="padding:10px;">
        <div style="background:#0f2043; color:white; padding:8px 12px; display:flex; justify-content:space-between; align-items:center; border-radius:4px;">
            <h3 style="margin:0;">યુનિવર્સલ સર્ચ એન્જિન & દસ્તાવેજ વૉલ્ટ (UNIVERSAL 360 SEARCH)</h3>
            <span style="font-size:12px;">ડ્રોપડાઉન અથવા સર્ચ બોક્સથી તુરંત શોધો</span>
        </div>

        <div style="display:grid; grid-template-columns: repeat(6, 1fr) 1.2fr 1.2fr; gap:4px; margin:8px 0;">
            <a href="/?sheet=UNIVERSAL_SEARCH&u_tab=customer" style="background:#0284c7; color:white; padding:8px; text-align:center; font-weight:bold; text-decoration:none; border-radius:3px; border:{('2px solid #38bdf8' if u_tab=='customer' else 'none')};">૧. ગ્રાહક સર્ચ</a>
            <a href="/?sheet=UNIVERSAL_SEARCH&u_tab=salesman" style="background:#dc2626; color:white; padding:8px; text-align:center; font-weight:bold; text-decoration:none; border-radius:3px; border:{('2px solid #38bdf8' if u_tab=='salesman' else 'none')};">૨. સેલ્સમેન સર્ચ</a>
            <a href="/?sheet=UNIVERSAL_SEARCH&u_tab=buyback&bb_view=IN_STOCK" style="background:#7c3aed; color:white; padding:8px; text-align:center; font-weight:bold; text-decoration:none; border-radius:3px; border:{('2px solid #38bdf8' if u_tab=='buyback' else 'none')};">૩. બાયબેક સ્ટોક</a>
            <a href="/?sheet=UNIVERSAL_SEARCH&u_tab=supplier" style="background:#15803d; color:white; padding:8px; text-align:center; font-weight:bold; text-decoration:none; border-radius:3px; border:{('2px solid #38bdf8' if u_tab=='supplier' else 'none')};">૪. વેપારી લેજર</a>
            <a href="/?sheet=UNIVERSAL_SEARCH&u_tab=bill_search" style="background:#ea580c; color:white; padding:8px; text-align:center; font-weight:bold; text-decoration:none; border-radius:3px; border:{('2px solid #38bdf8' if u_tab=='bill_search' else 'none')};">૫. બિલ સર્ચ</a>
            <a href="/?sheet=UNIVERSAL_SEARCH&u_tab=vault" style="background:#0d9488; color:white; padding:8px; text-align:center; font-weight:bold; text-decoration:none; border-radius:3px; border:{('2px solid #38bdf8' if u_tab=='vault' else 'none')};">૬. 📁 સેવ ફાઇલો (Vault)</a>

            <div style="background:#f1f5f9; border:1px solid #cbd5e1; text-align:center; padding:4px; border-radius:3px;">
                <div style="font-size:10px;">કુલ રેકોર્ડ મળ્યા:</div>
                <div style="font-size:15px; font-weight:bold;">{records_count}</div>
            </div>
            <div style="background:#fef3c7; border:1px solid #fde047; text-align:center; padding:4px; border-radius:3px;">
                <div style="font-size:10px;">ચોખ્ખી રકમ (₹):</div>
                <div style="font-size:15px; font-weight:bold; color:#b45309;">₹{net_outstanding:,.0f}</div>
            </div>
        </div>

        {dropdown_bar_html}

        <form action="/" method="get" style="display:flex; gap:6px; margin-bottom:10px;">
            <input type="hidden" name="sheet" value="UNIVERSAL_SEARCH">
            <input type="hidden" name="u_tab" value="{u_tab}">
            <input type="text" name="search_q" value="{search_q}" placeholder="અહીં શોધો (બિલ નં, ગ્રાહક નામ, ૧૦-અંક મોબાઈલ, ૧૫-અંક IMEI, ફાઇલ નામ)..." style="flex:1; padding:8px; background:#fef9c3; border:1px solid #ca8a04; border-radius:3px; font-weight:bold; font-size:13px;">
            <button type="submit" style="background:#0284c7; color:white; border:none; padding:8px 18px; border-radius:3px; font-weight:bold; cursor:pointer;">સર્ચ કરો</button>
            <a href="/?sheet=UNIVERSAL_SEARCH&u_tab={u_tab}" style="background:#64748b; color:white; padding:8px 14px; text-decoration:none; font-weight:bold; border-radius:3px;">સાફ કરો</a>
        </form>

        <div style="background:#0f2043; color:white; padding:6px 10px; font-weight:bold; font-size:12px;">{active_tab_title}</div>
        <table class="live-grid">
            <tr style="background:#1e293b; color:white;">
                <th style="color:white;">તારીખ / સમય</th>
                <th style="color:white;">સંદર્ભ / પ્રકાર / બિલ નં.</th>
                <th style="color:white;">વિગત / મોડેલ / ફાઇલ નામ</th>
                <th style="color:white;">જમા / રકમ / ફોર્મેટ</th>
                <th style="color:white;">ઉધાર / સંદર્ભ</th>
                <th style="color:white;">બાકી / નોંધ</th>
                <th style="color:white;">સ્થિતિ / એક્શન</th>
            </tr>
            {grid_html if grid_html else '<tr><td colspan="7" style="padding:14px; color:#64748b; font-weight:bold;">કોઈ રેકોર્ડ મળ્યો નથી</td></tr>'}
        </table>
    </div>

    <!-- Re-inward Modal -->
    <div id="reinward_modal" style="display:none; position:fixed; top:20%; left:50%; transform:translate(-50%, 0); background:white; padding:20px; border:2px solid #0f2043; border-radius:6px; z-index:999; width:360px; box-shadow:0 10px 25px rgba(0,0,0,0.3);">
        <h4 style="margin:0 0 10px 0; color:#ea580c;">ભૂલથી વેચાયેલો ફોન પાછો સ્ટોકમાં લો</h4>
        <form action="/reverse-buyback-sold" method="post">
            <input type="hidden" name="bb_id" id="re_bb_id">
            <div style="margin-bottom:6px;"><label>ફોન / IMEI:</label><input type="text" id="re_desc" readonly style="width:100%; padding:5px; background:#f1f5f9;"></div>
            <div style="margin-bottom:6px;"><label>વેચાણ રકમ કયા ગલ્લામાંથી બાદ કરવી:</label><select name="refund_galla" style="width:100%; padding:5px;">{all_galla_options}<option value="BANK_CASH">1. BANK_CASH (ગલ્લો ૧)</option><option value="ACC_DCASH">2. ACC_DCASH (ગલ્લો ૨)</option><option value="RECHARGE">3. RECHARGE (ગલ્લો ૩)</option><option value="EXTRA_CASH">4. EXTRA_CASH (ગલ્લો ૪)</option></select></div>
            <div style="margin-bottom:10px;"><label><b>શું સેલ્સમેન કમિશન બાદ કરવું છે?</b></label><select name="deduct_comm" style="width:100%; padding:5px;"><option value="YES">હા, કમિશન બાદ કરો</option><option value="NO">ના, કમિશન બાદ ન કરશો</option></select></div>
            <div style="display:flex; justify-content:space-between;">
                <button type="submit" style="background:#16a34a; color:white; border:none; padding:6px 14px; border-radius:3px; cursor:pointer; font-weight:bold;">કન્ફર્મ કરો</button>
                <button type="button" onclick="document.getElementById('reinward_modal').style.display='none'" style="background:#dc2626; color:white; border:none; padding:6px 14px; border-radius:3px; cursor:pointer;">રદ કરો</button>
            </div>
        </form>
    </div>

    <!-- Temp Edit / સિક્યુરિટી PIN Edit Modal -->
    <div id="temp_edit_modal" style="display:none; position:fixed; top:18%; left:50%; transform:translate(-50%, 0); background:white; padding:20px; border:2px solid #0f2043; border-radius:6px; z-index:999; width:380px; box-shadow:0 10px 25px rgba(0,0,0,0.3);">
        <h4 style="margin:0 0 10px 0; color:#0f2043;">બિલ એડિટ (ટેમ્પરરી પ્રિન્ટ અથવા માસ્ટર PIN કાયમી એડિટ - Rule 127)</h4>
        <form action="/print-temp-invoice" method="post" target="_blank">
            <input type="hidden" name="bill_no" id="temp_bill_no">
            <div style="margin-bottom:6px;"><label>ગ્રાહક નામ:</label><input type="text" name="customer_name" id="temp_cust" style="width:100%; padding:5px;"></div>
            <div style="margin-bottom:6px;"><label>મોડેલ નામ (દા.ત. Split AC 1.5T):</label><input type="text" name="model" id="temp_model" style="width:100%; padding:5px;"></div>
            <div style="margin-bottom:6px;"><label>રકમ (₹):</label><input type="number" step="any" name="mop_price" id="temp_mop" style="width:100%; padding:5px;"></div>
            <div style="margin-bottom:6px; background:#fef9c3; padding:5px;"><label><b>કાયમી ડેટાબેઝ સેવ માટે માસ્ટર PIN:</b></label><input type="password" name="admin_pin" placeholder="ખાલી રાખશો તો માત્ર ટેમ્પરરી પ્રિન્ટ નીકળશે" style="width:100%; padding:5px;"></div>
            <div style="margin-bottom:10px;"><label>ભાષા:</label><select name="lang" style="width:100%; padding:5px;"><option value="gu">ગુજરાતી</option><option value="en">English</option></select></div>
            <div style="display:flex; justify-content:space-between;">
                <button type="submit" style="background:#16a34a; color:white; border:none; padding:6px 14px; border-radius:3px; cursor:pointer; font-weight:bold;">પ્રિન્ટ / સેવ કરો</button>
                <button type="button" onclick="document.getElementById('temp_edit_modal').style.display='none'" style="background:#dc2626; color:white; border:none; padding:6px 14px; border-radius:3px; cursor:pointer;">રદ કરો</button>
            </div>
        </form>
    </div>
    <script>
        function openReInwardModal(id, m, im, p, g){{ document.getElementById('re_bb_id').value = id; document.getElementById('re_desc').value = m + ' (' + im + ') - ₹' + p; document.getElementById('reinward_modal').style.display = 'block'; }}
        function openTempEditModal(b, c, m, p){{ document.getElementById('temp_bill_no').value = b; document.getElementById('temp_cust').value = c; document.getElementById('temp_model').value = m; document.getElementById('temp_mop').value = p; document.getElementById('temp_edit_modal').style.display = 'block'; }}
    

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
        
        var numMatches = text.match(/\\d+/g);
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
    """
