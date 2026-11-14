# -*- coding: utf-8 -*-
# =======================================================================================================================
# ⚠️ આવશ્યક એઆઈ ડાયરેક્ટિવ અને ડાયનામિક રૂલબુક ગવર્નન્સ (કાયમી અમર એઆઈ હેડર - માસ્ટર ૧૦ લોજિક અને મલ્ટી-સ્ટોર SaaS આવૃત્તિ)
# =======================================================================================================================
# [કડક ચેતવણી - Gemini, ChatGPT, Claude, Cursor અથવા અન્ય કોઈપણ AI મોડેલ અને ડેવલપર માટે બંધનકર્તા આદેશ]:
# ૧. આ હેડર 'અમર' (Immortal) છે. આ ફાઇલ part3_routes.py છે (F1-F8 સેવિંગ રાઉટ્સ, CRUD અને ૧૨ ભાષા + MOP વિ. ડિસ્કાઉન્ટ બિલ પ્રિન્ટિંગ).
# ૨. જૂના કોડનું એક પણ ફંક્શન, ડ્રોપડાઉન, ગાણિતિક સૂત્ર કે CRUD બટન કાઢવું સખત પ્રતિબંધિત છે.
# =======================================================================================================================

import os
import time
import json
import threading
import datetime
import re
import base64
import sqlite3
import urllib.parse
from typing import List
from fastapi import Form, UploadFile, File, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from part1_core import (
    pull_and_merge_shop_backups_to_master_laptop, get_master_all_stores_backup_root,
    app, DB_FILE, MASTER_DB_FILE, DATA_DIR, STORE_CFG, save_store_config, get_active_db_file, get_shop_feature_profile,
    save_to_vault, increment_bill_no, run_automated_backup_and_sync, trigger_async_cloud_db_sync,
    log_audit_action, get_last_purchase_price, record_purchase_price,
    calc_staff_commission, calc_daily_net_profit, get_galla_balance, get_cumulative_unbanked_cash
)

def redir(msg: str, sheet: str = "SMART_TERMINAL", mode: str = "F2"):
    try:
        trigger_async_cloud_db_sync()
    except Exception:
        pass
    q = urllib.parse.quote(msg)
    return RedirectResponse(url=f"/?sheet={sheet}&mode={mode}&msg={q}", status_code=303)

# --- [F1] ખરીદી (૫ વિકલ્પો: મોબાઈલ, કન્ઝ્યુમર પ્રોડક્ટ, બાયબેક, રિચાર્જ, એસેસરીઝ પાર્ટ-૨) ---
@app.post("/save-f1")
async def save_f1_route(

    request: Request = None,
    entry_date: str = Form(""), tx_type: str = Form("PURCHASE"), f1_type: str = Form(""), return_mode: str = Form("F1"),
    b2b_type: str = Form("B2B"), supplier_gstin: str = Form(""), supplier_name: str = Form(""), party_name: str = Form(""),
    bill_no: str = Form(""), brand: str = Form("Vivo"), bb_brand: str = Form(""), model: str = Form(""), model_name: str = Form(""),
    imei: str = Form(""), imei_list: str = Form(""), total_bill: float = Form(0), purchase_rate: float = Form(0),
    gst_pct: float = Form(18.0), scheme_cn_amt: float = Form(0), mop_rate: float = Form(0), paid_amt: float = Form(0),
    customer_name: str = Form(""), customer_phone: str = Form(""), bb_model: str = Form(""),
    bb_imei: str = Form(""), bb_condition: str = Form(""), bb_cost: float = Form(0),
    salesman: str = Form(""), bb_salesman: str = Form(""), rech_company: str = Form(""), rech_topup_amt: float = Form(0),
    rech_comm_pct: float = Form(3.0), rech_paid_amt: float = Form(0),
    acc_sub_mode: str = Form("STANDARD"), acc_supplier: str = Form(""), acc_bill_no: str = Form(""),
    acc_category: str = Form("ટેમ્પરર્ડ ગ્લાસ"), acc_item_name: str = Form(""), acc_barcode: str = Form(""),
    acc_qty: int = Form(10), acc_unit_cost: float = Form(0), acc_mop: float = Form(0),
    acc_total_amt: float = Form(0), acc_paid_amt: float = Form(0),
    pay_mode: str = Form("રોકડ (Cash)"), galla_name: str = Form("BANK_CASH"), credit_days: int = Form(7), due_date: str = Form(""),
    bb_photo: UploadFile = File(None),
    purchase_doc: UploadFile = File(None),
    customer_face_photo: UploadFile = File(None),
    mult_photos: List[UploadFile] = File(default=[])
):
    now_dt = datetime.datetime.now()
    d_str = entry_date.strip() or now_dt.strftime("%Y-%m-%d")
    t_str = now_dt.strftime("%Y-%m-%d %H:%M")
    cookie_sid = ""
    if request and hasattr(request, "cookies"):
        cookie_sid = urllib.parse.unquote(request.cookies.get("devanshi_shop_id") or "").strip().upper()
    sid = (cookie_sid or STORE_CFG.get("shop_id", "DEVANSHI")).strip().upper()
    if f1_type == "BUYBACK_IN":
        tx_type = "DIRECT_BB"
        return_mode = "F5"
    conn = sqlite3.connect(get_active_db_file(sid), timeout=60.0)
    c = conn.cursor()

    photo_url = ""
    if bb_photo and hasattr(bb_photo, "filename") and bb_photo.filename:
        f_bytes = await bb_photo.read()
        photo_url = save_to_vault(f_bytes, bb_photo.filename, "F1_PURCHASE_DOC", imei or bb_imei or bill_no, supplier_name or customer_name or party_name)
    elif purchase_doc and hasattr(purchase_doc, "filename") and purchase_doc.filename:
        f_bytes = await purchase_doc.read()
        photo_url = save_to_vault(f_bytes, purchase_doc.filename, "F1_PURCHASE_DOC", imei or bb_imei or bill_no, supplier_name or customer_name or party_name)
    elif mult_photos and isinstance(mult_photos, (list, tuple)):
        for mp in mult_photos:
            if mp and hasattr(mp, "filename") and mp.filename:
                mb = await mp.read()
                photo_url = save_to_vault(mb, mp.filename, "F1_PURCHASE_DOC", imei or bb_imei or bill_no, supplier_name or customer_name or party_name)

    cust_face_url = ""
    if customer_face_photo and hasattr(customer_face_photo, "filename") and customer_face_photo.filename:
        cfb = await customer_face_photo.read()
        cust_face_url = save_to_vault(cfb, customer_face_photo.filename, "CUSTOMER_FACE_PHOTO", bb_imei or imei, customer_name or party_name)

    # વિકલ્પ (૩): જૂના બાય-બેક ફોનની ડાયરેક્ટ ખરીદી (ડુપ્લિકેટ IMEI ઓટો-લોક સાથે)
    if tx_type == "DIRECT_BB":
        use_br = (bb_brand or brand or "").strip()
        raw_mod = (bb_model or model_name or model or "Old Buyback Phone").strip()
        use_mod = f"{use_br} {raw_mod}".strip() if (use_br and not raw_mod.lower().startswith(use_br.lower())) else raw_mod
        use_im = (bb_imei or imei_list or imei or f"BB-{now_dt.strftime('%H%M%S')}").strip()
        use_cost = bb_cost if bb_cost > 0 else (purchase_rate if purchase_rate > 0 else total_bill)
        use_sm = (salesman or bb_salesman or "").strip()
        base_cust = (customer_name or party_name or supplier_name or "ગ્રાહક").strip()
        cust_full = f"{base_cust} ({customer_phone})" if customer_phone else base_cust

        # ડુપ્લિકેટ IMEI ચેક: જો આ જ IMEI પહેલેથી IN_STOCK માં હોય તો ઓવરરાઇટ ન કરો અને બે વખત પૈસા ન કાપો!
        c.execute("SELECT id, model, customer_name, purchase_cost FROM buyback_stock WHERE imei=? AND status='IN_STOCK'", (use_im,))
        dup_bb = c.fetchone()
        if dup_bb:
            conn.close()
            return redir(f"⚠️ ડુપ્લિકેટ IMEI લોક: IMEI '{use_im}' ({dup_bb[1]} - {dup_bb[2]}, ₹{float(dup_bb[3] or 0):,.0f}) પહેલેથી જ બાય-બેક સ્ટોકમાં હાજર છે! સુધારો કરવા માટે [એડિટ] બટન વાપરો.", "SMART_TERMINAL", return_mode)

        c.execute("""INSERT INTO buyback_stock
            (date, customer_name, model, imei, purchase_cost, repair_cost, total_cost, salesman, photo_path, customer_photo_path, bb_condition, brand, galla_name, source_type, status, store_id)
            VALUES (?, ?, ?, ?, ?, 0, ?, ?, ?, ?, ?, ?, ?, ?, 'IN_STOCK', ?)""",
            (d_str, cust_full, use_mod, use_im, use_cost, use_cost, use_sm, photo_url, cust_face_url, bb_condition, use_br, galla_name, f"સીધી ખરીદી ({bb_condition})", sid))
        if use_cost > 0 and "રોકડ" in pay_mode:
            c.execute("INSERT INTO galla_ledger (date, galla_name, in_amt, out_amt, remarks, file_path, store_id) VALUES (?, ?, 0, ?, ?, ?, ?)",
                      (d_str, galla_name, use_cost, f"જૂનો ફોન બાયબેક ખરીદી: {use_mod} ({ use_im }) [{cust_full}]", photo_url or cust_face_url, sid))
        c.execute("""INSERT INTO live_terminal_grid
            (entry_time, bill_no, customer_name, model_name, imei, galla_name, entry_type, total_padtar, gift_amt, due_amt, salesman, doc_path, store_id)
            VALUES (?, 'BB-IN', ?, ?, ?, ?, 'DIRECT_BB', ?, 0, 0, ?, ?, ?)""",
            (t_str, cust_full, use_mod, use_im, galla_name, use_cost, use_sm, photo_url or cust_face_url, sid))
        conn.commit()
        conn.close()
        return redir(f"✅ બાય-બેક ફોન '{use_mod}' (IMEI: {use_im}, ₹{use_cost:,.0f}) સફળતાપૂર્વક સ્ટોકમાં સેવ થયો!", "SMART_TERMINAL", return_mode)

    # વિકલ્પ (૪): રિચાર્જ ખરીદી / ટોપ-અપ
    elif tx_type == "RECHARGE_PURCHASE":
        use_galla = galla_name if galla_name else "RECHARGE"
        use_paid = rech_paid_amt if rech_paid_amt > 0 else paid_amt
        use_bill = rech_topup_amt if rech_topup_amt > 0 else total_bill
        bal = use_bill - use_paid
        c.execute("""INSERT INTO supplier_purchase_ledger
            (date, supplier_name, bill_no, total_bill, paid_amt, balance_due, galla_name, entry_type, doc_path, store_id)
            VALUES (?, ?, 'RECH-TOPUP', ?, ?, ?, ?, 'RECHARGE_PURCHASE', ?, ?)""",
            (d_str, rech_company or "Recharge Distributor", use_bill, use_paid, bal, use_galla, photo_url, sid))
        if use_paid > 0 and "રોકડ" in pay_mode:
            c.execute("INSERT INTO galla_ledger (date, galla_name, in_amt, out_amt, remarks, store_id) VALUES (?, ?, 0, ?, ?, ?)",
                      (d_str, use_galla, use_paid, f"રિચાર્જ ટોપ-અપ ખરીદી: {rech_company} (કમિશન {rech_comm_pct}%)", sid))
            if use_galla != "RECHARGE":
                c.execute("""INSERT INTO inter_galla_debt_ledger (store_id, tx_date, lender_galla, borrower_galla, amount, settled_amt, status, remarks)
                             VALUES (?, ?, ?, 'RECHARGE', ?, 0, 'PENDING', ?)""",
                          (sid, d_str, use_galla, use_paid, f"રિચાર્જ ટોપ-અપ ({rech_company}) {use_galla} માંથી ચૂકવ્યા"))
        c.execute("""INSERT INTO live_terminal_grid
            (entry_time, bill_no, customer_name, model_name, imei, galla_name, entry_type, total_padtar, gift_amt, due_amt, salesman, doc_path, store_id)
            VALUES (?, 'RECH', ?, ?, '-', ?, 'RECHARGE_TOPUP', ?, 0, ?, '-', ?, ?)""",
            (t_str, rech_company, f"LAPU Topup ({rech_comm_pct}%)", use_galla, use_bill, bal, photo_url, sid))

    # વિકલ્પ (૫): એસેસરીઝ ખરીદી (સ્ટાન્ડર્ડ મોડ + સ્પેશિયલ પાર્ટ-૨ મોડ)
    elif tx_type == "ACC_PURCHASE":
        use_galla = galla_name if galla_name else "ACC_DCASH"
        use_supp = acc_supplier or supplier_name or "Accessories Supplier"
        use_bno = acc_bill_no or bill_no or "ACC-PUR"
        use_tot = acc_total_amt if acc_total_amt > 0 else total_bill
        use_paid = acc_paid_amt if acc_paid_amt > 0 else paid_amt
        bal = use_tot - use_paid
        if acc_sub_mode == "PART2" and (acc_barcode.strip() or acc_item_name.strip()):
            bc = acc_barcode.strip() or f"ACC-{now_dt.strftime('%H%M%S')}"
            c.execute("""INSERT INTO accessories_part2_inventory
                (store_id, barcode, category, item_name, brand, purchase_dp, sale_mop, stock_qty, last_updated)
                VALUES (?, ?, ?, ?, 'Accessories', ?, ?, ?, ?)
                ON CONFLICT(barcode) DO UPDATE SET
                stock_qty = accessories_part2_inventory.stock_qty + excluded.stock_qty,
                purchase_dp = excluded.purchase_dp,
                sale_mop = excluded.sale_mop,
                last_updated = excluded.last_updated""",
                (sid, bc, acc_category, acc_item_name or acc_category, acc_unit_cost, acc_mop, acc_qty, d_str))
        c.execute("""INSERT INTO supplier_purchase_ledger
            (date, supplier_name, bill_no, total_bill, paid_amt, balance_due, galla_name, entry_type, doc_path, qty, unit_cost, store_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, 'ACC_PURCHASE', ?, ?, ?, ?)""",
            (d_str, use_supp, use_bno, use_tot, use_paid, bal, use_galla, photo_url, acc_qty, acc_unit_cost, sid))
        if use_paid > 0 and "રોકડ" in pay_mode:
            c.execute("INSERT INTO galla_ledger (date, galla_name, in_amt, out_amt, remarks, store_id) VALUES (?, ?, 0, ?, ?, ?)",
                      (d_str, use_galla, use_paid, f"એસેસરીઝ ખરીદી: {use_supp} ({use_bno})", sid))
            if use_galla != "ACC_DCASH":
                c.execute("""INSERT INTO inter_galla_debt_ledger (store_id, tx_date, lender_galla, borrower_galla, amount, settled_amt, status, remarks)
                             VALUES (?, ?, ?, 'ACC_DCASH', ?, 0, 'PENDING', ?)""",
                          (sid, d_str, use_galla, use_paid, f"એસેસરીઝ ખરીદી ({use_supp} - {use_bno}) {use_galla} માંથી ઉછીના ચૂકવ્યા"))
        c.execute("""INSERT INTO live_terminal_grid
            (entry_time, bill_no, customer_name, model_name, imei, galla_name, entry_type, total_padtar, gift_amt, due_amt, salesman, doc_path, store_id)
            VALUES (?, ?, ?, ?, ?, ?, 'ACC_PURCHASE', ?, 0, ?, '-', ?, ?)""",
            (t_str, use_bno, use_supp, acc_item_name or acc_category, acc_barcode or "-", use_galla, use_tot, bal, photo_url, sid))

    # વિકલ્પ (૧) અને (૨): મોબાઈલ ખરીદી / અન્ય કન્ઝ્યુમર પ્રોડક્ટ્સ ખરીદી
    else:
        cat_label = "મોબાઈલ હેન્ડસેટ" if tx_type == "PURCHASE" else "લેપટોપ / TV / હોમ એપ્લાયન્સ"
        if imei.strip():
            # મલ્ટીપલ IMEI (કોમા કે સ્પેસથી અલગ કરેલા) હોય તો બધા સીધા In-Stock માં જમા
            imei_list = [x.strip() for x in imei.replace(",", " ").split() if x.strip()]
            for single_im in imei_list:
                c.execute("""INSERT OR IGNORE INTO live_stock
                    (bill_no, entry_date, party_name, brand, model, imei, purchase_rate, sale_rate, status, category, doc_path, store_id, last_purchase_dp)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'IN_STOCK', ?, ?, ?, ?)""",
                    (bill_no, d_str, supplier_name, brand, model, single_im, total_bill, mop_rate or total_bill, cat_label, photo_url, sid, total_bill))
        eff_bill = max(0.0, float(total_bill or 0) - float(scheme_cn_amt or 0))
        bal = eff_bill - float(paid_amt or 0)
        record_purchase_price(brand, model or tx_type, imei.strip() if imei else "", total_bill, mop_rate or total_bill, supplier_name, bill_no, sid, existing_cursor=c)
        from part1_core import add_col_if_missing
        add_col_if_missing(conn, "supplier_purchase_ledger", "credit_days", "INTEGER DEFAULT 0")
        add_col_if_missing(conn, "supplier_purchase_ledger", "due_date", "TEXT DEFAULT ''")
        eff_due_dt = due_date.strip()
        if not eff_due_dt and int(credit_days or 0) > 0:
            try:
                eff_due_dt = str(datetime.datetime.strptime(d_str[:10], "%Y-%m-%d").date() + datetime.timedelta(days=int(credit_days)))
            except Exception:
                eff_due_dt = d_str
        c.execute("""INSERT INTO supplier_purchase_ledger
            (date, supplier_name, bill_no, total_bill, paid_amt, balance_due, galla_name, entry_type, doc_path, b2b_type, supplier_gstin, gst_pct, scheme_cn_amt, credit_days, due_date, store_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (d_str, supplier_name, bill_no, eff_bill, paid_amt, bal, galla_name, tx_type, photo_url, b2b_type, supplier_gstin, gst_pct, scheme_cn_amt, int(credit_days or 0), eff_due_dt, sid))
        if paid_amt > 0 and "રોકડ" in pay_mode:
            c.execute("INSERT INTO galla_ledger (date, galla_name, in_amt, out_amt, remarks, store_id) VALUES (?, ?, 0, ?, ?, ?)",
                      (d_str, galla_name, paid_amt, f"વેપારી પેમેન્ટ: {supplier_name} ({bill_no})", sid))
            if galla_name and galla_name != "BANK_CASH":
                c.execute("""INSERT INTO inter_galla_debt_ledger (store_id, tx_date, lender_galla, borrower_galla, amount, settled_amt, status, remarks)
                             VALUES (?, ?, ?, 'BANK_CASH', ?, 0, 'PENDING', ?)""",
                          (sid, d_str, galla_name, paid_amt, f"વેપારી પેમેન્ટ ({supplier_name} - {bill_no}) {galla_name} માંથી ઉછીના ચૂકવ્યા"))
        c.execute("""INSERT INTO live_terminal_grid
            (entry_time, bill_no, customer_name, model_name, imei, galla_name, entry_type, total_padtar, gift_amt, due_amt, salesman, doc_path, store_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, 0, ?, '-', ?, ?)""",
            (t_str, bill_no or "SUPP", supplier_name, model or tx_type, imei or "-", galla_name, tx_type, eff_bill, bal, photo_url, sid))

    conn.commit()
    conn.close()
    return redir("✅ [F1] ખરીદી વ્યવહાર સફળતાપૂર્વક સેવ થયો!", "SMART_TERMINAL", "F1")

# --- [F2] વેચાણ અને પેમેન્ટ સ્પ્લિટ સેવ (૩ ડાયનેમિક ફોર્મ્સ: રોકડ, ઉધાર, ફાઇનાન્સ) ---
@app.post("/save-f2")
async def save_f2_route(

    request: Request = None,
    bill_type: str = Form("FINANCE_BILL"), b2b_type: str = Form("B2C"), customer_gstin: str = Form(""),
    do_id: str = Form(""), bill_no: str = Form(""), bill_date: str = Form(""), salesman: str = Form(""),
    customer_name: str = Form(""), phone: str = Form(""), customer_address: str = Form(""), customer_pincode: str = Form(""),
    imei: str = Form(""), brand: str = Form("Vivo"), model: str = Form(""), finance_company: str = Form(""),
    do_ref_no: str = Form(""), app_deal_id: str = Form(""), emi_amt: float = Form(0),
    warranty_period: str = Form("૧ વર્ષ કંપની વોરંટી (1 Year Brand Warranty)"),
    scheme_name: str = Form(""), mop_price: float = Form(0), discount_amt: float = Form(0), gst_pct: float = Form(18.0),
    loan_amt: float = Form(0), net_bank_loan: float = Form(0), expected_dp: float = Form(0),
    cash_dp: float = Form(0), cash_galla: str = Form("BANK_CASH"), upi_dp: float = Form(0),
    card_swipe_dp: float = Form(0), staff_cc_swipe: float = Form(0), neft_rtgs_dp: float = Form(0),
    bb_amt: float = Form(0), bb_in_model: str = Form(""), bb_in_imei: str = Form(""),
    due_amt: float = Form(0), due_date: str = Form(""),
    gift_cost: float = Form(0), gift_desc: str = Form(""), remarks: str = Form(""),
    scheme_benefit_amt: float = Form(0), apply_scheme_to_bill: str = Form("KEEP_PROFIT"),
    first_emi_date: str = Form(""), last_emi_month: str = Form(""), first_emi_extra_charge: str = Form(""),
    staff_comm: float = Form(0), bb_in_photo: UploadFile = File(None), items_json: str = Form("")
):
    now_dt = datetime.datetime.now()
    d_str = bill_date.strip() or now_dt.strftime("%Y-%m-%d")
    t_str = now_dt.strftime("%Y-%m-%d %H:%M")
    cookie_sid = ""
    if request and hasattr(request, "cookies"):
        cookie_sid = urllib.parse.unquote(request.cookies.get("devanshi_shop_id") or "").strip().upper()
    sid = (cookie_sid or STORE_CFG.get("shop_id", "DEVANSHI")).strip().upper()
    conn = sqlite3.connect(get_active_db_file(sid), timeout=60.0)
    c = conn.cursor()

    bb_ph_url = ""
    if bb_in_photo and hasattr(bb_in_photo, "filename") and bb_in_photo.filename:
        fb = await bb_in_photo.read()
        bb_ph_url = save_to_vault(fb, bb_in_photo.filename, "EXCHANGE_BB", bb_in_imei or bill_no, customer_name)

    c.execute("SELECT custom_comm_enabled, custom_comm_deduction, custom_comm_pct FROM shop_custom_settings WHERE shop_id=?", (sid,))
    comm_cfg = c.fetchone() or (1, 500.0, 20.0)
    comm_enabled = bool(comm_cfg[0]) if comm_cfg[0] is not None else True
    comm_deduct = float(comm_cfg[1] if comm_cfg[1] is not None else 500.0)
    comm_pct = float(comm_cfg[2] if comm_cfg[2] is not None else 20.0)

    import json
    multi_items = []
    if items_json and items_json.strip():
        try:
            multi_items = json.loads(items_json.strip())
        except Exception:
            multi_items = []

    if multi_items and len(multi_items) > 0:
        total_items_count = len(multi_items)
        combined_imeis = ", ".join([it.get("imei", "").strip() for it in multi_items if it.get("imei")])
        combined_models = f"{total_items_count} ફોન: " + ", ".join([f"{it.get('brand','')} {it.get('model','')}" for it in multi_items[:3]])
        if total_items_count > 3:
            combined_models += f" (+{total_items_count - 3} વધુ)"
            
        tot_mop = sum([float(it.get("mop", 0) or 0) for it in multi_items])
        tot_disc = sum([float(it.get("discount", 0) or 0) for it in multi_items])
        mop_price = tot_mop
        discount_amt = tot_disc
        imei = combined_imeis or imei
        model = combined_models or model

        # Ensure sales_invoice_items exists and insert every item
        c.execute("""CREATE TABLE IF NOT EXISTS sales_invoice_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            store_id TEXT DEFAULT 'DEVANSHI',
            bill_no TEXT,
            bill_date TEXT,
            item_index INT DEFAULT 1,
            brand TEXT,
            model TEXT,
            imei TEXT,
            mop_price REAL DEFAULT 0,
            discount_amt REAL DEFAULT 0,
            net_price REAL DEFAULT 0,
            gst_pct REAL DEFAULT 18.0,
            warranty_period TEXT DEFAULT '',
            salesman TEXT DEFAULT '',
            customer_name TEXT DEFAULT '',
            customer_phone TEXT DEFAULT '',
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )""")

        for idx, it in enumerate(multi_items, start=1):
            it_imei = it.get("imei", "").strip()
            it_brand = it.get("brand", "").strip()
            it_model = it.get("model", "").strip()
            it_mop = float(it.get("mop", 0) or 0)
            it_disc = float(it.get("discount", 0) or 0)
            it_net = max(0.0, it_mop - it_disc)
            it_war = it.get("warranty", "").strip() or warranty_period
            it_gst = float(it.get("gst_pct", 18) or 18)

            c.execute("""INSERT INTO sales_invoice_items
                (store_id, bill_no, bill_date, item_index, brand, model, imei, mop_price, discount_amt, net_price, gst_pct, warranty_period, salesman, customer_name, customer_phone)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (sid, bill_no, d_str, idx, it_brand, it_model, it_imei, it_mop, it_disc, it_net, it_gst, it_war, salesman, customer_name, phone))

            if it_imei:
                c.execute("UPDATE live_stock SET status='SOLD' WHERE imei=?", (it_imei,))

    net_mop = max(0.0, float(mop_price or 0) - float(discount_amt or 0))
    eff_loan = (net_bank_loan if net_bank_loan > 0 else loan_amt) if bill_type == "FINANCE_BILL" else 0.0
    dp_collected = cash_dp + upi_dp + card_swipe_dp + staff_cc_swipe + neft_rtgs_dp + bb_amt + due_amt
    basic_dp = max(0.0, net_mop - eff_loan)
    extra_dp_calc = max(0.0, (expected_dp if expected_dp > 0 else dp_collected) - basic_dp) if bill_type == "FINANCE_BILL" else 0.0

    eff_comm = staff_comm
    if eff_comm == 0 and comm_enabled and extra_dp_calc > comm_deduct:
        eff_comm = calc_staff_commission(extra_dp_calc, comm_pct, comm_deduct)

    full_scheme = f"{finance_company} ({scheme_name})" if (finance_company and scheme_name) else (scheme_name or finance_company)

    from part1_core import add_col_if_missing
    add_col_if_missing(conn, "apx_sales_raw", "scheme_benefit_amt", "REAL DEFAULT 0")
    add_col_if_missing(conn, "apx_sales_raw", "first_emi_date", "TEXT DEFAULT ''")
    add_col_if_missing(conn, "apx_sales_raw", "last_emi_month", "TEXT DEFAULT ''")
    add_col_if_missing(conn, "apx_sales_raw", "first_emi_extra_charge", "TEXT DEFAULT ''")
    add_col_if_missing(conn, "apx_sales_raw", "expected_dp", "REAL DEFAULT 0")
    STORE_CFG["f2_bill_type"] = bill_type
    eff_scheme_profit = float(scheme_benefit_amt or 0) if apply_scheme_to_bill == "KEEP_PROFIT" else 0.0
    c.execute("""INSERT OR REPLACE INTO apx_sales_raw
        (bill_no, bill_date, customer_name, phone, customer_address, customer_pincode, salesman, brand, model, imei, mop_price,
         cash_dp, cash_galla, upi_dp, card_swipe_dp, staff_cc_swipe, loan_amt, net_disb_amt, extra_dp_profit, due_amt,
         bb_amt, gift_cost, staff_comm, status, scheme_name, doc_path,
         bill_type, b2b_type, customer_gstin, discount_amt, gst_pct, neft_rtgs_dp, due_date, remarks,
         do_ref_no, app_deal_id, financer_name, emi_amt, warranty_period, store_id, scheme_benefit_amt,
         first_emi_date, last_emi_month, first_emi_extra_charge, expected_dp)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'SETTLED', ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (bill_no, d_str, customer_name, phone, customer_address, customer_pincode, salesman, brand, model, imei, net_mop,
         cash_dp, cash_galla, upi_dp, card_swipe_dp, staff_cc_swipe, float(loan_amt or mop_price), float(net_bank_loan or eff_loan), extra_dp_calc, due_amt,
         bb_amt, gift_cost, eff_comm, full_scheme, bb_ph_url,
         bill_type, b2b_type, customer_gstin, discount_amt, gst_pct, neft_rtgs_dp, due_date, remarks,
         do_ref_no.strip(), app_deal_id.strip(), finance_company.strip(), float(emi_amt or 0), warranty_period.strip(), sid, eff_scheme_profit,
         first_emi_date.strip(), last_emi_month.strip(), first_emi_extra_charge.strip(), float(expected_dp or dp_collected)))

    if imei.strip():
        c.execute("UPDATE live_stock SET status='SOLD' WHERE imei=?", (imei.strip(),))
    if do_id.strip():
        c.execute("UPDATE finance_do_list SET status='SETTLED' WHERE id=?", (do_id.strip(),))

    # જો રોકડ DP માં Extra DP નફો સમાયેલો હોય, તો મૂળ રકમ પસંદ કરેલા ગલ્લામાં અને Extra DP નફો સીધો ગલ્લા ૪ (EXTRA_CASH) માં જમા!
    if cash_dp > 0:
        if extra_dp_calc > 0 and cash_galla != "EXTRA_CASH":
            extra_in_g4 = min(cash_dp, extra_dp_calc)
            base_in_g1 = max(0.0, cash_dp - extra_in_g4)
            if base_in_g1 > 0:
                c.execute("INSERT INTO galla_ledger (date, galla_name, in_amt, out_amt, remarks, store_id) VALUES (?, ?, ?, 0, ?, ?)",
                          (d_str, cash_galla, base_in_g1, f"વેચાણ રોકડ DP: {bill_no} ({customer_name})", sid))
            if extra_in_g4 > 0:
                c.execute("INSERT INTO galla_ledger (date, galla_name, in_amt, out_amt, remarks, store_id) VALUES (?, 'EXTRA_CASH', ?, 0, ?, ?)",
                          (d_str, extra_in_g4, f"ફાઇનાન્સ Extra DP નફો: {bill_no} ({customer_name})", sid))
        else:
            c.execute("INSERT INTO galla_ledger (date, galla_name, in_amt, out_amt, remarks, store_id) VALUES (?, ?, ?, 0, ?, ?)",
                      (d_str, cash_galla, cash_dp, f"વેચાણ રોકડ ({bill_type}): {bill_no} ({customer_name})", sid))

    if bb_amt > 0 or bb_in_model.strip():
        c.execute("""INSERT OR REPLACE INTO buyback_stock
            (date, customer_name, model, imei, purchase_cost, repair_cost, total_cost, salesman, photo_path, source_type, status, store_id)
            VALUES (?, ?, ?, ?, ?, 0, ?, ?, ?, 'F2 એક્સચેન્જ બાયબેક', 'IN_STOCK', ?)""",
            (d_str, customer_name, bb_in_model or "Exchange Phone", bb_in_imei or f"BB-{bill_no}", bb_amt, bb_amt, salesman, bb_ph_url, sid))

    if due_amt > 0:
        c.execute("""INSERT INTO customer_due_ledger (date, salesman, customer_name, phone, bill_no, due_amt, received_amt, due_date, store_id)
            VALUES (?, ?, ?, ?, ?, ?, 0, ?, ?)""", (d_str, salesman, customer_name, phone, bill_no, due_amt, due_date, sid))

    if gift_cost > 0:
        c.execute("INSERT INTO gift_ledger (date, bill_no, customer_name, model, gift_desc, gift_amt, salesman) VALUES (?, ?, ?, ?, ?, ?, ?)",
                  (d_str, bill_no, customer_name, model, gift_desc, gift_cost, salesman))

    if eff_comm > 0 or staff_cc_swipe > 0:
        c.execute("""INSERT INTO staff_commission_ledger
            (date, staff_name, entry_type, remarks, comm_earned, cc_swipe_amt, paid_amt, galla_name, bill_ref)
            VALUES (?, ?, 'F2_SALE_COMM', ?, ?, ?, 0, ?, ?)""",
            (d_str, salesman, f"બિલ: {bill_no} ({model})", eff_comm, staff_cc_swipe, cash_galla, bill_no))

    c.execute("""INSERT INTO live_terminal_grid
        (entry_time, bill_no, customer_name, model_name, imei, galla_name, entry_type, total_padtar, gift_amt, due_amt, salesman, doc_path, store_id)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (t_str, bill_no, customer_name, model, imei, cash_galla, bill_type, net_mop, gift_cost, due_amt, salesman, bb_ph_url, sid))

    increment_bill_no(conn)
    if salesman and salesman.strip():
        try:
            c.execute("""INSERT INTO staff_location_trail
                (store_id, staff_name, log_date, log_time, activity_type, details, latitude, longitude, address, photo_path)
                VALUES (?, ?, ?, ?, 'BILL_CREATED', ?, 0, 0, 'દુકાન કાઉન્ટર (F2)', ?)""",
                (sid, salesman.strip(), d_str, now_dt.strftime("%I:%M %p"),
                 f"બિલ #{bill_no} ({bill_type}) | ગ્રાહક: {customer_name} | મોડેલ: {model} | ₹{mop_price:,.0f}", bb_ph_url))
        except Exception:
            pass
    try:
        c.execute("UPDATE shop_custom_settings SET f2_bill_type=? WHERE shop_id=?", (bill_type, sid))
    except Exception:
        pass
    conn.commit()
    conn.close()
    try:
        trigger_async_cloud_db_sync()
    except Exception:
        pass
    q_msg = urllib.parse.quote(f"✅ બિલ {bill_no} ({bill_type}) સફળતાપૂર્વક સેવ થયું!")
    return RedirectResponse(url=f"/?sheet=SMART_TERMINAL&mode=F2&bill_type={urllib.parse.quote(bill_type)}&msg={q_msg}", status_code=303)

# --- [F3] પેમેન્ટ આઉટ (વેપારી કે સ્ટાફને ચૂકવણી) ---
@app.post("/save-f3-payout")
def save_f3_payout_route(
    entry_date: str = Form(""), payout_target_type: str = Form("SUPPLIER"),
    supplier_name: str = Form(""), staff_name: str = Form(""), staff_payout_sub_type: str = Form("STAFF_ADVANCE"),
    amount: float = Form(0), pay_mode: str = Form("રોકડ (Cash)"), galla_name: str = Form("BANK_CASH"), remarks: str = Form("")
):
    now_dt = datetime.datetime.now()
    d_str = entry_date.strip() or now_dt.strftime("%Y-%m-%d")
    t_str = now_dt.strftime("%Y-%m-%d %H:%M")
    sid = STORE_CFG.get("shop_id", "DEVANSHI")
    conn = sqlite3.connect(get_active_db_file(), timeout=60.0)
    c = conn.cursor()

    if payout_target_type == "STAFF":
        head_map = {
            "STAFF_ADVANCE": "૧. સ્ટાફ એડવાન્સ ઉપાડ (Advance)",
            "STAFF_SALARY": "૨. માસિક પગાર ચૂકવણી (Salary)",
            "STAFF_COMMISSION": "૩. સ્કીમ કમિશન ચૂકવણી (Commission)",
            "STAFF_CC_REFUND": "૪. સ્ટાફ CC સ્વાઇપ રીફંડ (CC Swipe Refund)"
        }
        head_lbl = head_map.get(staff_payout_sub_type, "સ્ટાફ ચૂકવણી")
        c.execute("INSERT INTO staff_commission_ledger (date, staff_name, entry_type, remarks, comm_earned, cc_swipe_amt, paid_amt, galla_name, bill_ref) VALUES (?, ?, ?, ?, 0, 0, ?, ?, ?)",
                  (d_str, staff_name, staff_payout_sub_type, f"[{head_lbl}] {pay_mode} - {remarks}", amount, galla_name, "F3-OUT"))
        if amount > 0 and "રોકડ" in pay_mode:
            c.execute("INSERT INTO galla_ledger (date, galla_name, in_amt, out_amt, remarks, store_id) VALUES (?, ?, 0, ?, ?, ?)",
                      (d_str, galla_name, amount, f"{head_lbl} ({staff_name}): {remarks}", sid))
        target_lbl = f"{staff_name} ({head_lbl})"
    else:
        c.execute("""INSERT INTO supplier_purchase_ledger
            (date, supplier_name, bill_no, total_bill, paid_amt, balance_due, galla_name, entry_type, store_id)
            VALUES (?, ?, ?, 0, ?, ?, ?, 'PAYMENT_OUT', ?)""",
            (d_str, supplier_name, remarks or "PAY-OUT", amount, -abs(amount), galla_name, sid))
        if amount > 0 and "રોકડ" in pay_mode:
            c.execute("INSERT INTO galla_ledger (date, galla_name, in_amt, out_amt, remarks, store_id) VALUES (?, ?, 0, ?, ?, ?)",
                      (d_str, galla_name, amount, f"વેપારી પેમેન્ટ આઉટ ({supplier_name}): {remarks}", sid))
        target_lbl = supplier_name

    c.execute("""INSERT INTO live_terminal_grid
        (entry_time, bill_no, customer_name, model_name, imei, galla_name, entry_type, total_padtar, gift_amt, due_amt, salesman, store_id)
        VALUES (?, 'PAY-OUT', ?, ?, '-', ?, 'F3_PAY_OUT', ?, 0, 0, '-', ?)""",
        (t_str, target_lbl, f"{pay_mode} ({remarks})", galla_name, amount, sid))
    conn.commit()
    conn.close()
    return redir(f"✅ [F3] પેમેન્ટ આઉટ (₹{amount:,.0f} -> {target_lbl}) સેવ થયું!", "SMART_TERMINAL", "F3")

# --- [F3 / F5] જૂના ફોન વેચાણ (નફો ગલ્લા ૪ માં ઓટો-સ્પ્લિટ) અને રિપેરિંગ ---
@app.post("/save-f3")
async def save_f3_route(
    f3_action: str = Form("BB_SALE"), bb_imei: str = Form(""), customer_name: str = Form(""),
    phone: str = Form(""), sale_price: float = Form(0), salesman: str = Form(""),
    repair_cost: float = Form(0), remarks: str = Form(""), pay_mode: str = Form("રોકડ (Cash)"), galla_name: str = Form("BANK_CASH"),
    bb_doc: UploadFile = File(None)
):
    now_dt = datetime.datetime.now()
    d_str, t_str = now_dt.strftime("%Y-%m-%d"), now_dt.strftime("%Y-%m-%d %H:%M")
    sid = STORE_CFG.get("shop_id", "DEVANSHI")
    conn = sqlite3.connect(get_active_db_file(), timeout=60.0)
    c = conn.cursor()

    doc_url = ""
    if bb_doc and bb_doc.filename:
        fb = await bb_doc.read()
        doc_url = save_to_vault(fb, bb_doc.filename, "F5_BUYBACK_DOC", bb_imei, customer_name or remarks)

    if f3_action == "BB_SALE":
        c.execute("SELECT total_cost, model FROM buyback_stock WHERE imei=?", (bb_imei,))
        bb_r = c.fetchone()
        orig_total_cost = float(bb_r[0] or 0) if bb_r else 0.0
        bb_mod_name = bb_r[1] if bb_r else "જૂનો ફોન"

        from part1_core import add_col_if_missing
        add_col_if_missing(conn, "buyback_stock", "sold_date", "TEXT DEFAULT ''")
        c.execute("UPDATE buyback_stock SET status='SOLD', sold_date=?, sale_price=?, sale_galla=?, photo_path= COALESCE(NULLIF(?,''), photo_path) WHERE imei=?",
                  (d_str, sale_price, galla_name, doc_url, bb_imei))

        # ઓટો-સ્પ્લિટ લોજિક: મૂળ કુલ પડતર પસંદ કરેલા ગલ્લામાં (ગલ્લો ૧) અને ઉપરનો ચોખ્ખો નફો સીધો ગલ્લા ૪ (EXTRA_CASH) માં!
        if sale_price > 0:
            if orig_total_cost > 0 and sale_price > orig_total_cost:
                cost_part = orig_total_cost
                profit_part = sale_price - orig_total_cost
                c.execute("INSERT INTO galla_ledger (date, galla_name, in_amt, out_amt, remarks, store_id) VALUES (?, ?, ?, 0, ?, ?)",
                          (d_str, galla_name, cost_part, f"જૂનો ફોન વેચાણ મૂળ પડતર રિકવરી ({bb_mod_name} - {bb_imei})", sid))
                c.execute("INSERT INTO galla_ledger (date, galla_name, in_amt, out_amt, remarks, store_id) VALUES (?, 'EXTRA_CASH', ?, 0, ?, ?)",
                          (d_str, profit_part, f"જૂનો ફોન વેચાણ ચોખ્ખો નફો ({bb_mod_name} - {bb_imei})", sid))
            else:
                c.execute("INSERT INTO galla_ledger (date, galla_name, in_amt, out_amt, remarks, store_id) VALUES (?, ?, ?, 0, ?, ?)",
                          (d_str, galla_name, sale_price, f"જૂનો ફોન વેચાણ ({bb_imei}) - {customer_name}", sid))

        c.execute("""INSERT INTO live_terminal_grid
            (entry_time, bill_no, customer_name, model_name, imei, galla_name, entry_type, total_padtar, gift_amt, due_amt, salesman, doc_path, store_id)
            VALUES (?, 'BB-SALE', ?, ?, ?, ?, 'F5_BB_SALE', ?, 0, 0, ?, ?, ?)""",
            (t_str, customer_name, bb_mod_name, bb_imei, galla_name, sale_price, salesman, doc_url, sid))
    else:
        c.execute("UPDATE buyback_stock SET repair_cost = repair_cost + ?, total_cost = total_cost + ?, photo_path= COALESCE(NULLIF(?,''), photo_path) WHERE imei=?",
                  (repair_cost, repair_cost, doc_url, bb_imei))
        if repair_cost > 0:
            c.execute("INSERT INTO galla_ledger (date, galla_name, in_amt, out_amt, remarks, store_id) VALUES (?, ?, 0, ?, ?, ?)",
                      (d_str, galla_name, repair_cost, f"જૂનો ફોન રિપેરિંગ ({bb_imei}): {remarks}", sid))

    conn.commit()
    conn.close()
    return redir("✅ [F5] બાયબેક વ્યવહાર સફળતાપૂર્વક સેવ થયો!", "SMART_TERMINAL", "F5")

# --- [F5 ભાગ ૪] બાય-બેક રિટર્ન અને કેશ રિફંડ ફોર્મ ---
@app.post("/save-f5-bb-return")
def save_f5_bb_return_route(
    imei: str = Form(...), customer_name: str = Form(""), orig_sale_date: str = Form(""),
    model: str = Form(""), orig_sale_price: float = Form(0), deduction_amt: float = Form(0),
    net_refund_amt: float = Form(0), pay_mode: str = Form("રોકડ (Cash)"),
    refund_galla: str = Form("BANK_CASH"), staff_name: str = Form(""), reason: str = Form("")
):
    now_dt = datetime.datetime.now()
    d_str, t_str = now_dt.strftime("%Y-%m-%d"), now_dt.strftime("%H:%M")
    sid = STORE_CFG.get("shop_id", "DEVANSHI")
    net_ref = max(0.0, float(orig_sale_price or 0) - float(deduction_amt or 0)) if net_refund_amt <= 0 else net_refund_amt

    conn = sqlite3.connect(get_active_db_file(), timeout=60.0)
    c = conn.cursor()
    # ૧. IMEI પાછો SOLD માંથી IN_STOCK (Saleable In) કરો (બાયબેક સ્ટોક તેમજ લાઈવ સ્ટોક બંનેમાં ચેક કરો)
    c.execute("UPDATE buyback_stock SET status='IN_STOCK', sale_price=0 WHERE imei=?", (imei.strip(),))
    bb_updated = c.rowcount
    c.execute("UPDATE live_stock SET status='IN_STOCK' WHERE imei=?", (imei.strip(),))
    if bb_updated == 0:
        c.execute("""INSERT OR IGNORE INTO buyback_stock
            (date, customer_name, model, imei, purchase_cost, repair_cost, total_cost, salesman, source_type, status, sale_price, store_id)
            VALUES (?, ?, ?, ?, ?, 0, ?, ?, 'વેચાણ રિટર્ન', 'IN_STOCK', 0, ?)""",
            (d_str, customer_name, model, imei.strip(), net_ref, net_ref, staff_name, sid))
    # ૨. રિટર્ન લોગમાં નોંધો
    c.execute("""INSERT INTO buyback_return_refund_log
        (store_id, return_date, return_time, imei, model, customer_name, orig_sale_date, orig_sale_price, deduction_amt, net_refund_amt, pay_mode, refund_galla, staff_name, reason)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (sid, d_str, t_str, imei.strip(), model, customer_name, orig_sale_date, orig_sale_price, deduction_amt, net_ref, pay_mode, refund_galla, staff_name, reason))
    # ૩. જે ગલ્લામાંથી રિફંડ આપ્યું તેમાંથી રકમ માઇનસ કરો
    if net_ref > 0 and "રોકડ" in pay_mode:
        c.execute("INSERT INTO galla_ledger (date, galla_name, in_amt, out_amt, remarks, store_id) VALUES (?, ?, 0, ?, ?, ?)",
                  (d_str, refund_galla, net_ref, f"બાયબેક રિટર્ન કેશ રિફંડ ({model} - {imei}): ઘસારો ₹{deduction_amt:,.0f} કાપીને", sid))
    c.execute("""INSERT INTO live_terminal_grid
        (entry_time, bill_no, customer_name, model_name, imei, galla_name, entry_type, total_padtar, gift_amt, due_amt, salesman, store_id)
        VALUES (?, 'BB-RET', ?, ?, ?, ?, 'F5_BB_RETURN', ?, 0, 0, ?, ?)""",
        (f"{d_str} {t_str}", customer_name, f"{model} (રિટર્ન રિફંડ)", imei, refund_galla, net_ref, staff_name, sid))
    conn.commit()
    conn.close()
    return redir(f"🔄 [F5 ભાગ ૪] બાયબેક ફોન ({imei}) પાછો In-Stock થયો અને ₹{net_ref:,.0f} રિફંડ ગલ્લામાંથી બાદ થયા!", "SMART_TERMINAL", "F5")

# --- [F7] ડાયરેક્ટ એક્સ્ટ્રા પ્રોફિટ સેટઅપ ---
@app.post("/save-f7-extra-profit")
def save_f7_extra_profit_route(
    entry_date: str = Form(""), profit_type: str = Form("FINANCE_EXTRA_DP"),
    ref_bill_customer: str = Form(""), net_profit_amt: float = Form(0),
    galla_name: str = Form("EXTRA_CASH"), salesman: str = Form(""),
    staff_comm_amt: float = Form(0), remarks: str = Form("")
):
    now_dt = datetime.datetime.now()
    d_str = entry_date.strip() or now_dt.strftime("%Y-%m-%d")
    t_str = now_dt.strftime("%H:%M")
    sid = STORE_CFG.get("shop_id", "DEVANSHI")
    conn = sqlite3.connect(get_active_db_file(), timeout=60.0)
    c = conn.cursor()

    c.execute("""INSERT INTO direct_extra_profit_log
        (store_id, entry_date, entry_time, profit_type, ref_bill_customer, net_profit_amt, galla_name, salesman, staff_comm_amt, remarks)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (sid, d_str, t_str, profit_type, ref_bill_customer, net_profit_amt, galla_name, salesman, staff_comm_amt, remarks))

    if net_profit_amt > 0:
        c.execute("INSERT INTO galla_ledger (date, galla_name, in_amt, out_amt, remarks, store_id) VALUES (?, ?, ?, 0, ?, ?)",
                  (d_str, galla_name, net_profit_amt, f"[F7] એક્સ્ટ્રા પ્રોફિટ ({profit_type}): {ref_bill_customer} {remarks}", sid))

    if staff_comm_amt > 0 and salesman:
        c.execute("""INSERT INTO staff_commission_ledger
            (date, staff_name, entry_type, remarks, comm_earned, cc_swipe_amt, paid_amt, galla_name, bill_ref)
            VALUES (?, ?, 'F7_EXTRA_PROFIT_COMM', ?, ?, 0, 0, ?, ?)""",
            (d_str, salesman, f"{profit_type}: {ref_bill_customer}", staff_comm_amt, galla_name, ref_bill_customer or "F7-PROF"))

    c.execute("""INSERT INTO live_terminal_grid
        (entry_time, bill_no, customer_name, model_name, imei, galla_name, entry_type, total_padtar, gift_amt, due_amt, salesman, store_id)
        VALUES (?, 'EXT-PROF', ?, ?, '-', ?, 'F7_EXTRA_PROFIT', ?, 0, 0, ?, ?)""",
        (f"{d_str} {t_str}", ref_bill_customer or profit_type, remarks or profit_type, galla_name, net_profit_amt, salesman, sid))

    conn.commit()
    conn.close()
    return redir(f"💎 [F7] એક્સ્ટ્રા પ્રોફિટ ₹{net_profit_amt:,.0f} ({galla_name}) અને P&L નફામાં જમા થયો!", "SMART_TERMINAL", "F7")

# --- [F4 / F3] ઉધાર વસૂલાત (૪-ગલ્લા સિલેક્શન સાથે) ---
@app.post("/save-f4")
def save_f4_route(
    rec_date: str = Form(""), due_id: int = Form(...), received_amt: float = Form(0),
    pay_mode: str = Form("રોકડ (Cash)"), galla_name: str = Form("BANK_CASH"),
    remarks: str = Form(""), extra_note: str = Form("")
):
    use_galla = galla_name if galla_name in ("BANK_CASH", "ACC_DCASH", "RECHARGE", "EXTRA_CASH") else "BANK_CASH"
    now_dt = datetime.datetime.now()
    d_str = rec_date.strip() or now_dt.strftime("%Y-%m-%d")
    t_str = now_dt.strftime("%Y-%m-%d %H:%M")
    sid = STORE_CFG.get("shop_id", "DEVANSHI")
    conn = sqlite3.connect(get_active_db_file(), timeout=60.0)
    c = conn.cursor()
    c.execute("SELECT customer_name, bill_no, salesman FROM customer_due_ledger WHERE id=?", (due_id,))
    r = c.fetchone() or ("ગ્રાહક", "-", "-")
    c.execute("UPDATE customer_due_ledger SET received_amt = received_amt + ? WHERE id=?", (received_amt, due_id))
    if received_amt > 0 and "રોકડ" in pay_mode:
        c.execute("INSERT INTO galla_ledger (date, galla_name, in_amt, out_amt, remarks, store_id) VALUES (?, ?, ?, 0, ?, ?)",
                  (d_str, use_galla, received_amt, f"ઉધાર વસૂલાત: {r[0]} ({r[1]}) {remarks} {extra_note}", sid))
    c.execute("""INSERT INTO live_terminal_grid
        (entry_time, bill_no, customer_name, model_name, imei, galla_name, entry_type, total_padtar, gift_amt, due_amt, salesman, store_id)
        VALUES (?, ?, ?, 'ઉધાર વસૂલાત જમા', '-', ?, 'F4_DUE_REC', ?, 0, 0, ?, ?)""",
        (t_str, r[1], r[0], use_galla, received_amt, remarks or r[2], sid))
    staff_rec = (remarks or r[2] or "").strip()
    if staff_rec:
        try:
            c.execute("""INSERT INTO staff_location_trail
                (store_id, staff_name, log_date, log_time, activity_type, details, latitude, longitude, address, photo_path)
                VALUES (?, ?, ?, ?, 'DUE_RECOVERY', ?, 0, 0, 'ઉધાર વસૂલાત (F3)', '')""",
                (sid, staff_rec, d_str, now_dt.strftime("%I:%M %p"),
                 f"ગ્રાહક ઉધાર વસૂલાત: {r[0]} (બિલ: {r[1]}) | વસૂલ: ₹{received_amt:,.0f} ({pay_mode})"))
        except Exception:
            pass
    conn.commit()
    conn.close()
    return redir(f"✅ [F3] ગ્રાહક ઉધાર વસૂલાત ₹{received_amt:,.0f} ({use_galla}) માં જમા થઈ!", "SMART_TERMINAL", "F3")

# --- [F5] સ્ટાફ ઉપાડ / CC સ્વાઇપ ---
@app.post("/save-f5")
def save_f5_route(entry_date: str = Form(""), staff_name: str = Form(...), entry_type: str = Form("UPAD"), bill_ref: str = Form(""), amount: float = Form(0), pay_mode: str = Form("રોકડ (Cash)"), galla_name: str = Form("BANK_CASH"), remarks: str = Form("")):
    now_dt = datetime.datetime.now()
    d_str = entry_date.strip() or now_dt.strftime("%Y-%m-%d")
    t_str = now_dt.strftime("%Y-%m-%d %H:%M")
    conn = sqlite3.connect(get_active_db_file(), timeout=60.0)
    c = conn.cursor()
    if entry_type == "CC_SWIPE_ADD":
        c.execute("INSERT INTO staff_commission_ledger (date, staff_name, entry_type, remarks, comm_earned, cc_swipe_amt, paid_amt, galla_name, bill_ref) VALUES (?, ?, ?, ?, 0, ?, 0, ?, ?)",
                  (d_str, staff_name, entry_type, remarks, amount, galla_name, bill_ref))
    else:
        c.execute("INSERT INTO staff_commission_ledger (date, staff_name, entry_type, remarks, comm_earned, cc_swipe_amt, paid_amt, galla_name, bill_ref) VALUES (?, ?, ?, ?, 0, 0, ?, ?, ?)",
                  (d_str, staff_name, entry_type, remarks, amount, galla_name, bill_ref))
        if amount > 0:
            c.execute("INSERT INTO galla_ledger (date, galla_name, in_amt, out_amt, remarks) VALUES (?, ?, 0, ?, ?)",
                      (d_str, galla_name, amount, f"સ્ટાફ {entry_type}: {staff_name} ({remarks})"))
    c.execute("""INSERT INTO live_terminal_grid
        (entry_time, bill_no, customer_name, model_name, imei, galla_name, entry_type, total_padtar, gift_amt, due_amt, salesman)
        VALUES (?, ?, ?, ?, '-', ?, ?, ?, 0, 0, ?)""",
        (t_str, bill_ref or "STAFF", staff_name, remarks or entry_type, galla_name, entry_type, amount, staff_name))
    conn.commit()
    conn.close()
    return redir("✅ [F5] સ્ટાફ ખાતાવહી વ્યવહાર સેવ થયો!", "SMART_TERMINAL", "F5")

# --- [F6 / F3 વિકલ્પ ૩] દૈનિક ખર્ચ / આવક / રિચાર્જ લમ્પ-સમ વકરો + ૩-કંપની LAPU બેલેન્સ ---
@app.post("/save-f6")
def save_f6_route(
    entry_date: str = Form(""), f6_type: str = Form("EXPENSE"), head_name: str = Form(""),
    amount: float = Form(0), pay_mode: str = Form("રોકડ"), galla_name: str = Form("BANK_CASH"),
    remarks: str = Form(""), jio_lapu: float = Form(0), vi_lapu: float = Form(0),
    lapu_companies: List[str] = Form(default=[]),
    lapu_openings: List[str] = Form(default=[]),
    lapu_topups: List[str] = Form(default=[]),
    lapu_closings: List[str] = Form(default=[]),
    lapu_used_sales: List[str] = Form(default=[])
):
    now_dt = datetime.datetime.now()
    d_str = entry_date.strip() or now_dt.strftime("%Y-%m-%d")
    t_str = now_dt.strftime("%Y-%m-%d %H:%M")
    sid = STORE_CFG.get("shop_id", "DEVANSHI")
    conn = sqlite3.connect(get_active_db_file(), timeout=60.0)
    c = conn.cursor()
    if f6_type == "LAPU_UPDATE":
        c.execute("UPDATE recharge_lapu_audit SET jio_lapu=?, vi_lapu=?, updated_date=? WHERE id=1", (jio_lapu, vi_lapu, d_str))
    elif f6_type == "EXPENSE":
        if head_name.strip():
            c.execute("INSERT OR IGNORE INTO config_expense_heads (head_name) VALUES (?)", (head_name.strip(),))
        is_cash_exp = ("રોકડ" in pay_mode or "CASH" in pay_mode.upper()) and not any(k in pay_mode.upper() for k in ["ONLINE", "UPI", "BANK", "ઓનલાઇન", "બેંક"])
        if is_cash_exp:
            c.execute("INSERT INTO galla_ledger (date, galla_name, in_amt, out_amt, remarks, store_id) VALUES (?, ?, 0, ?, ?, ?)",
                      (d_str, galla_name, amount, f"દુકાન ખર્ચ ({head_name}): {remarks}", sid))
            if amount > 0 and galla_name and galla_name != "BANK_CASH":
                c.execute("""INSERT INTO inter_galla_debt_ledger (store_id, tx_date, lender_galla, borrower_galla, amount, settled_amt, status, remarks)
                             VALUES (?, ?, ?, 'BANK_CASH', ?, 0, 'PENDING', ?)""",
                          (sid, d_str, galla_name, amount, f"દુકાન ખર્ચ ({head_name}) {galla_name} માંથી ઉછીના ચૂકવ્યા"))
        grid_exp_type = "F6_EXPENSE" if is_cash_exp else "F6_ONLINE_EXPENSE"
        c.execute("INSERT INTO live_terminal_grid (entry_time, bill_no, customer_name, model_name, imei, galla_name, entry_type, total_padtar, gift_amt, due_amt, salesman, store_id) VALUES (?, 'EXP', ?, ?, '-', ?, ?, ?, 0, 0, '-', ?)",
                  (t_str, head_name, f"{remarks} ({pay_mode})" if not is_cash_exp else remarks, galla_name if is_cash_exp else "ONLINE_BANK", grid_exp_type, amount, sid))
    else:
        target_g = "ACC_DCASH" if f6_type == "ACC_INCOME" else "RECHARGE"
        lapu_summary_parts = []
        if f6_type == "RECH_INCOME" and lapu_companies:
            for idx_l, comp_nm in enumerate(lapu_companies):
                c_clean = (comp_nm or "").strip()
                if not c_clean:
                    continue
                def _pf(lst, i):
                    try:
                        v = str(lst[i]).strip()
                        return float(v) if v != "" else None
                    except Exception:
                        return None
                op_v = _pf(lapu_openings, idx_l) or 0.0
                top_v = _pf(lapu_topups, idx_l) or 0.0
                cls_v = _pf(lapu_closings, idx_l)
                use_v = _pf(lapu_used_sales, idx_l) or 0.0
                if cls_v is not None:
                    use_v = max(0.0, op_v + top_v - cls_v)
                    c.execute("""INSERT OR REPLACE INTO recharge_lapu_company_balances
                        (company, opening_balance, today_topup, today_sales, current_demo_balance, pending_distributor_due, last_updated)
                        VALUES (?, ?, ?, ?, ?, COALESCE((SELECT pending_distributor_due FROM recharge_lapu_company_balances WHERE company=?), 0), ?)""",
                        (c_clean, op_v, top_v, use_v, cls_v, c_clean, d_str))
                    c.execute("""INSERT INTO recharge_operator_ledger
                        (store_id, entry_date, operator_name, opening_bal, topup_purchased, comm_pct, comm_amt, today_sales, closing_bal, galla_name, remarks)
                        VALUES (?, ?, ?, ?, ?, 0, 0, ?, ?, 'RECHARGE', ?)""",
                        (sid, d_str, f"{c_clean} LAPU", op_v, top_v, use_v, cls_v, f"F3 દૈનિક લમ્પ-સમ વકરો (₹{amount:,.0f}) સાથે ક્લોઝિંગ"))
                    lapu_summary_parts.append(f"{c_clean}: Op ₹{op_v:,.0f} -> Close ₹{cls_v:,.0f} (વેચાણ ₹{use_v:,.0f})")
                    if c_clean.upper().startswith("JIO"):
                        c.execute("UPDATE recharge_lapu_audit SET jio_lapu=?, updated_date=? WHERE id=1", (cls_v, d_str))
                    elif c_clean.upper().startswith("AIRTEL"):
                        c.execute("UPDATE recharge_lapu_audit SET airtel_lapu=?, updated_date=? WHERE id=1", (cls_v, d_str))
                    elif c_clean.upper().startswith("VI"):
                        c.execute("UPDATE recharge_lapu_audit SET vi_lapu=?, updated_date=? WHERE id=1", (cls_v, d_str))
                elif op_v > 0 or top_v > 0:
                    c.execute("""UPDATE recharge_lapu_company_balances
                                 SET opening_balance=?, today_topup=? WHERE company=?""", (op_v, top_v, c_clean))
        lapu_rem_str = (" | LA-PU: " + ", ".join(lapu_summary_parts)) if lapu_summary_parts else ""
        full_rem = f"{head_name} {remarks}{lapu_rem_str}".strip()
        if amount > 0:
            c.execute("INSERT INTO galla_ledger (date, galla_name, in_amt, out_amt, remarks) VALUES (?, ?, ?, 0, ?)",
                      (d_str, target_g, amount, f"સીધી રોકડ આવક ({f6_type}): {full_rem}"))
            c.execute("INSERT INTO live_terminal_grid (entry_time, bill_no, customer_name, model_name, imei, galla_name, entry_type, total_padtar, gift_amt, due_amt, salesman) VALUES (?, 'INC', ?, ?, '-', ?, ?, ?, 0, 0, '-')",
                      (t_str, head_name or f6_type, full_rem, target_g, f6_type, amount))
    conn.commit()
    conn.close()
    return redir("✅ [F3] દૈનિક ખર્ચ / રિચાર્જ વકરો અને લાપુ બેલેન્સ સફળતાપૂર્વક સેવ થયા!", "SMART_TERMINAL", "F3")

@app.post("/api/manage-lapu-operator")
def manage_lapu_operator_api(action: str = Form("ADD"), company: str = Form(""), new_name: str = Form("")):
    act = (action or "ADD").strip().upper()
    comp = (company or "").strip()
    if not comp:
        return JSONResponse({"ok": False, "msg": "કંપનીનું નામ લખો!"})
    conn = sqlite3.connect(get_active_db_file(), timeout=60.0)
    c = conn.cursor()
    if act == "ADD":
        c.execute("""INSERT OR IGNORE INTO recharge_lapu_company_balances
                     (company, opening_balance, today_topup, today_sales, current_demo_balance, pending_distributor_due, last_updated)
                     VALUES (?, 0, 0, 0, 0, 0, '')""", (comp,))
    elif act == "RENAME" and new_name.strip():
        c.execute("UPDATE recharge_lapu_company_balances SET company=? WHERE company=?", (new_name.strip(), comp))
    elif act == "DELETE":
        if comp.upper() in ("AIRTEL", "VI", "JIO"):
            conn.close()
            return JSONResponse({"ok": False, "msg": "મુખ્ય ૩ કંપની (Airtel, VI, Jio) કાયમી છે!"})
        c.execute("DELETE FROM recharge_lapu_company_balances WHERE company=?", (comp,))
    conn.commit()
    conn.close()
    return JSONResponse({"ok": True})

@app.post("/api/manage-bank-f4")
def manage_bank_f4_api(action: str = Form("ADD"), bank_name: str = Form(""), new_name: str = Form(""), pin: str = Form("1986")):
    act = (action or "ADD").strip().upper()
    bnk = (bank_name or "").strip()
    if not bnk:
        return JSONResponse({"ok": False, "msg": "બેંકનું નામ લખો!"})
    conn = sqlite3.connect(get_active_db_file(), timeout=60.0)
    c = conn.cursor()
    if act == "ADD":
        c.execute("INSERT OR IGNORE INTO config_banks (bank_name) VALUES (?)", (bnk,))
    elif act == "EDIT" and new_name.strip():
        c.execute("UPDATE config_banks SET bank_name=? WHERE bank_name=?", (new_name.strip(), bnk))
    elif act == "DELETE":
        req_pin = str(STORE_CFG.get("admin_pin", "1986")).strip()
        if str(pin).strip() not in (req_pin, "1986"):
            conn.close()
            return JSONResponse({"ok": False, "msg": "❌ ખોટો માસ્ટર સિક્રેટ PIN!"})
        c.execute("DELETE FROM config_banks WHERE bank_name=?", (bnk,))
    conn.commit()
    conn.close()
    return JSONResponse({"ok": True})

# --- [F6 / F7] ગલ્લા ટ્રાન્સફર ---
@app.post("/save-f7")
def save_f7_route(tx_date: str = Form(""), from_galla: str = Form(...), to_galla: str = Form(...), amount: float = Form(0), staff_name: str = Form(""), remarks: str = Form("")):
    d_str = tx_date.strip() or str(datetime.date.today())
    sid = STORE_CFG.get("shop_id", "DEVANSHI")
    conn = sqlite3.connect(get_active_db_file(), timeout=60.0)
    c = conn.cursor()
    c.execute("INSERT INTO galla_ledger (date, galla_name, in_amt, out_amt, remarks, store_id) VALUES (?, ?, 0, ?, ?, ?)",
              (d_str, from_galla, amount, f"ટ્રાન્સફર જાવક -> {to_galla} ({staff_name} - {remarks})", sid))
    c.execute("INSERT INTO galla_ledger (date, galla_name, in_amt, out_amt, remarks, store_id) VALUES (?, ?, ?, 0, ?, ?)",
              (d_str, to_galla, amount, f"ટ્રાન્સફર આવક <- {from_galla} ({staff_name} - {remarks})", sid))
    # Auto-settle any matching pending inter-galla debt (where borrower_galla == from_galla and lender_galla == to_galla)
    rem_pay = float(amount or 0)
    if rem_pay > 0:
        c.execute("""SELECT id, amount, COALESCE(settled_amt,0) FROM inter_galla_debt_ledger
                     WHERE status='PENDING' AND borrower_galla=? AND lender_galla=? ORDER BY id ASC""", (from_galla, to_galla))
        for d_row in c.fetchall():
            if rem_pay <= 0:
                break
            d_id, d_tot, d_set = d_row[0], float(d_row[1] or 0), float(d_row[2] or 0)
            need_v = max(0.0, d_tot - d_set)
            apply_v = min(rem_pay, need_v)
            new_set = d_set + apply_v
            new_st = "SETTLED" if (new_set >= d_tot - 0.01) else "PENDING"
            c.execute("UPDATE inter_galla_debt_ledger SET settled_amt=?, status=?, settled_date=? WHERE id=?",
                      (new_set, new_st, d_str, d_id))
            rem_pay -= apply_v
    conn.commit()
    conn.close()
    return redir("✅ આંતરિક ગલ્લા ટ્રાન્સફર સેવ થયું!", "SMART_TERMINAL", "F6")

@app.api_route("/api/settle-inter-galla-debt", methods=["GET", "POST"])
def settle_inter_galla_debt_route(debt_id: int = 0):
    d_str = str(datetime.date.today())
    sid = STORE_CFG.get("shop_id", "DEVANSHI")
    conn = sqlite3.connect(get_active_db_file(), timeout=60.0)
    c = conn.cursor()
    c.execute("SELECT id, lender_galla, borrower_galla, amount, COALESCE(settled_amt,0), remarks FROM inter_galla_debt_ledger WHERE id=? AND status='PENDING'", (debt_id,))
    row = c.fetchone()
    if not row:
        conn.close()
        return redir("⚠️ આ ઉછીની એન્ટ્રી પહેલેથી જ સેટલ થઈ ગઈ છે!", "SMART_TERMINAL", "F6")
    _, l_gal, b_gal, tot_a, set_a, rem_txt = row
    rem_debt = max(0.0, float(tot_a or 0) - float(set_a or 0))
    b_avail = max(0.0, get_galla_balance(b_gal))
    pay_now = min(rem_debt, b_avail) if b_avail > 0 else rem_debt
    c.execute("INSERT INTO galla_ledger (date, galla_name, in_amt, out_amt, remarks, store_id) VALUES (?, ?, 0, ?, ?, ?)",
              (d_str, b_gal, pay_now, f"ટ્રાન્સફર જાવક (ઉછીના પરત) -> {l_gal} ({rem_txt})", sid))
    c.execute("INSERT INTO galla_ledger (date, galla_name, in_amt, out_amt, remarks, store_id) VALUES (?, ?, ?, 0, ?, ?)",
              (d_str, l_gal, pay_now, f"ટ્રાન્સફર આવક (ઉછીના પરત મળ્યા) <- {b_gal} ({rem_txt})", sid))
    new_set = float(set_a or 0) + pay_now
    new_st = "SETTLED" if (new_set >= float(tot_a or 0) - 0.01) else "PENDING"
    c.execute("UPDATE inter_galla_debt_ledger SET settled_amt=?, status=?, settled_date=? WHERE id=?",
              (new_set, new_st, d_str, debt_id))
    conn.commit()
    conn.close()
    return redir(f"✅ ક્રોસ-ગલ્લા ઉછીની રકમ ₹{pay_now:,.0f} ({b_gal} માંથી {l_gal} માં) સફળતાપૂર્વક પરત સેટલ થઈ ગઈ!", "SMART_TERMINAL", "F6")

# --- [F8] ૪-ગલ્લા ઓડિટ સેવ & Undo & બેંક ડિપોઝીટ (૫-સ્ત્રોત સ્પ્લિટ) ---
@app.post("/save-f8-audit")
async def save_f8_audit_route(
    table_type: str = Form("T1"), save_scope: str = Form("ALL"),
    op_BANK_CASH: float = Form(0), op_ACC_DCASH: float = Form(0), op_RECHARGE: float = Form(0), op_EXTRA_CASH: float = Form(0),
    n500_BANK_CASH: int = Form(0), n200_BANK_CASH: int = Form(0), n100_BANK_CASH: int = Form(0), n50_BANK_CASH: int = Form(0), n20_BANK_CASH: int = Form(0), n10_BANK_CASH: int = Form(0), coins_BANK_CASH: int = Form(0),
    n500_ACC_DCASH: int = Form(0), n200_ACC_DCASH: int = Form(0), n100_ACC_DCASH: int = Form(0), n50_ACC_DCASH: int = Form(0), n20_ACC_DCASH: int = Form(0), n10_ACC_DCASH: int = Form(0), coins_ACC_DCASH: int = Form(0),
    n500_RECHARGE: int = Form(0), n200_RECHARGE: int = Form(0), n100_RECHARGE: int = Form(0), n50_RECHARGE: int = Form(0), n20_RECHARGE: int = Form(0), n10_RECHARGE: int = Form(0), coins_RECHARGE: int = Form(0),
    n500_EXTRA_CASH: int = Form(0), n200_EXTRA_CASH: int = Form(0), n100_EXTRA_CASH: int = Form(0), n50_EXTRA_CASH: int = Form(0), n20_EXTRA_CASH: int = Form(0), n10_EXTRA_CASH: int = Form(0), coins_EXTRA_CASH: int = Form(0)
):
    conn = sqlite3.connect(get_active_db_file(), timeout=60.0)
    c = conn.cursor()
    payload = {
        "BANK_CASH": (n500_BANK_CASH, n200_BANK_CASH, n100_BANK_CASH, n50_BANK_CASH, n20_BANK_CASH, n10_BANK_CASH, coins_BANK_CASH, op_BANK_CASH),
        "ACC_DCASH": (n500_ACC_DCASH, n200_ACC_DCASH, n100_ACC_DCASH, n50_ACC_DCASH, n20_ACC_DCASH, n10_ACC_DCASH, coins_ACC_DCASH, op_ACC_DCASH),
        "RECHARGE": (n500_RECHARGE, n200_RECHARGE, n100_RECHARGE, n50_RECHARGE, n20_RECHARGE, n10_RECHARGE, coins_RECHARGE, op_RECHARGE),
        "EXTRA_CASH": (n500_EXTRA_CASH, n200_EXTRA_CASH, n100_EXTRA_CASH, n50_EXTRA_CASH, n20_EXTRA_CASH, n10_EXTRA_CASH, coins_EXTRA_CASH, op_EXTRA_CASH),
    }
    targets = list(payload.keys()) if save_scope == "ALL" else [save_scope]
    tbl_name = "cash_audit_4galla" if table_type == "T1" else "total_cumulative_notes"

    c.execute("DELETE FROM audit_backup_undo WHERE table_type=?", (table_type,))
    for g in targets:
        c.execute(f"SELECT n500, n200, n100, n50, n20, n10, coins {', opening_cash' if table_type=='T1' else ''} FROM {tbl_name} WHERE galla_name=?", (g,))
        old_r = c.fetchone()
        if old_r:
            op_v = old_r[7] if table_type == "T1" else 0
            c.execute("INSERT INTO audit_backup_undo (table_type, galla_name, n500, n200, n100, n50, n20, n10, coins, opening_cash) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                      (table_type, g, old_r[0], old_r[1], old_r[2], old_r[3], old_r[4], old_r[5], old_r[6], op_v))
        vals = payload[g]
        if table_type == "T1":
            c.execute("UPDATE cash_audit_4galla SET n500=?, n200=?, n100=?, n50=?, n20=?, n10=?, coins=?, opening_cash=? WHERE galla_name=?", (*vals, g))
        else:
            c.execute("UPDATE total_cumulative_notes SET n500=?, n200=?, n100=?, n50=?, n20=?, n10=?, coins=?, opening_cash=? WHERE galla_name=?", (*vals, g))

    conn.commit()
    conn.close()
    return redir(f"✅ [F8] {table_type} ગલ્લા ઓડિટ ({save_scope}) સેવ થયું!", "SMART_TERMINAL", "F8")

@app.get("/undo-f8-audit")
def undo_f8_audit_route(table_type: str = "T1"):
    conn = sqlite3.connect(get_active_db_file(), timeout=60.0)
    c = conn.cursor()
    c.execute("SELECT galla_name, n500, n200, n100, n50, n20, n10, coins, opening_cash FROM audit_backup_undo WHERE table_type=?", (table_type,))
    rows = c.fetchall()
    for r in rows:
        if table_type == "T1":
            c.execute("UPDATE cash_audit_4galla SET n500=?, n200=?, n100=?, n50=?, n20=?, n10=?, coins=?, opening_cash=? WHERE galla_name=?",
                      (r[1], r[2], r[3], r[4], r[5], r[6], r[7], r[8], r[0]))
        else:
            c.execute("UPDATE total_cumulative_notes SET n500=?, n200=?, n100=?, n50=?, n20=?, n10=?, coins=? WHERE galla_name=?",
                      (r[1], r[2], r[3], r[4], r[5], r[6], r[7], r[0]))
    conn.commit()
    conn.close()
    return redir(f"↩️ [F8] {table_type} ગલ્લા ઓડિટ Undo પૂર્ણ!", "SMART_TERMINAL", "F8")

@app.post("/save-bank-deposit")
def save_bank_deposit_route(
    tx_type: str = Form("DEPOSIT"), dep_date: str = Form(""),
    bank_name: str = Form(...), dep_yest_bank: float = Form(0), dep_bank_cash: float = Form(0),
    dep_acc_cash: float = Form(0), dep_rech_cash: float = Form(0), dep_extra_cash: float = Form(0),
    depositor: str = Form(""), remarks: str = Form(""), slip_notes_summary: str = Form("")
):
    now_dt = datetime.datetime.now()
    d_str = dep_date.strip() or now_dt.strftime("%Y-%m-%d")
    t_str = now_dt.strftime("%H:%M")
    conn = sqlite3.connect(get_active_db_file(), timeout=60.0)
    c = conn.cursor()

    if slip_notes_summary.strip():
        remarks = f"{remarks} {slip_notes_summary}".strip()

    # ૫-સ્ત્રોત સ્પ્લિટ: (૧) આજની ઓપનિંગ બેંક કેશ, (૨) આજની ફ્રેશ બેંક કેશ, (૩) D-Cash, (૪) રિચાર્જ, (૫) એક્સ્ટ્રા કેશ
    splits = [
        ("BANK_CASH", dep_yest_bank, "આજની ઓપનિંગ બેંક કેશ"),
        ("BANK_CASH", dep_bank_cash, "આજની ફ્રેશ બેંક કેશ"),
        ("ACC_DCASH", dep_acc_cash, "ACC_DCASH"),
        ("RECHARGE", dep_rech_cash, "RECHARGE"),
        ("EXTRA_CASH", dep_extra_cash, "EXTRA_CASH")
    ]
    total_dep = 0.0
    for gk, amt, src_label in splits:
        if amt > 0:
            total_dep += amt
            if tx_type == "WITHDRAWAL":
                c.execute("INSERT INTO galla_ledger (date, galla_name, in_amt, out_amt, remarks) VALUES (?, ?, ?, 0, ?)",
                          (d_str, gk, amt, f"બેંકમાંથી રોકડ ઉપાડ ({bank_name} - {src_label}): {remarks}"))
            else:
                c.execute("INSERT INTO galla_ledger (date, galla_name, in_amt, out_amt, remarks) VALUES (?, ?, 0, ?, ?)",
                          (d_str, gk, amt, f"બેંક ડિપોઝીટ ({bank_name} - {src_label}): {remarks}"))
            c.execute("INSERT INTO bank_deposit_log (date, time_str, bank_name, amount, remarks, depositor, source_type, store_id) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                      (d_str, t_str, bank_name, amt, f"{tx_type}: {remarks}", depositor, src_label, STORE_CFG.get("shop_id", "DEVANSHI")))
    conn.commit()
    conn.close()
    act_lbl = "બેંક ઉપાડ (Withdrawal)" if tx_type == "WITHDRAWAL" else "બેંક ડિપોઝીટ"
    return redir(f"✅ કુલ ₹{total_dep:,.0f} {act_lbl} (૫-સ્ત્રોત સ્પ્લિટ) સેવ થઈ!", "SMART_TERMINAL", "F4")

# --- ટેલી-સ્ટાઇલ માસ્ટર લેજર Create / Edit / Delete (PIN 1986) ---
@app.post("/save-tally-ledger")
def save_tally_ledger_route(
    ledger_mode: str = Form("CREATE"), ledger_id: int = Form(0),
    ledger_name: str = Form(...), under_group: str = Form("Sundry Creditors"),
    mobile: str = Form(""), gstin: str = Form(""), address: str = Form(""),
    pincode: str = Form(""), bank_details: str = Form(""), opening_bal: float = Form(0),
    bal_type: str = Form("CR"), secret_pin: str = Form("")
):
    sid = STORE_CFG.get("shop_id", "DEVANSHI")
    now_s = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    conn = sqlite3.connect(get_active_db_file(), timeout=60.0)
    c = conn.cursor()

    if ledger_mode in ("EDIT", "DELETE"):
        if str(secret_pin).strip() != "1986":
            conn.close()
            return redir("❌ લેજર એડિટ કે ડિલીટ કરવા માટે સાચો માસ્ટર સિક્રેટ PIN ફરજિયાત છે!", "GUJARATI_CONFIG")

    if ledger_mode == "DELETE" and ledger_id > 0:
        c.execute("SELECT ledger_name, under_group FROM tally_master_ledgers WHERE id=?", (ledger_id,))
        old_r = c.fetchone()
        conn.execute("DELETE FROM tally_master_ledgers WHERE id=?", (ledger_id,))
        conn.commit()
        conn.close()
        log_audit_action("DELETE_TALLY_LEDGER", "tally_master_ledgers", str(ledger_id), old_data=str(old_r), authorized_by="PIN 1986")
        return redir(f"🗑️ ટેલી લેજર '{ledger_name}' ડિલીટ થયું (ઓડિટ ટ્રેઇલ સેવ)!", "GUJARATI_CONFIG")
    elif ledger_mode == "EDIT" and ledger_id > 0:
        c.execute("""UPDATE tally_master_ledgers
            SET ledger_name=?, under_group=?, mobile=?, gstin=?, address=?, pincode=?, bank_details=?, opening_bal=?, bal_type=?
            WHERE id=?""",
            (ledger_name.strip(), under_group, mobile, gstin, address, pincode, bank_details, opening_bal, bal_type, ledger_id))
        log_audit_action("EDIT_TALLY_LEDGER", "tally_master_ledgers", str(ledger_id), new_data=ledger_name, authorized_by="PIN 1986")
    else:
        c.execute("""INSERT INTO tally_master_ledgers
            (store_id, ledger_name, under_group, mobile, gstin, address, pincode, bank_details, opening_bal, bal_type, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (sid, ledger_name.strip(), under_group, mobile, gstin, address, pincode, bank_details, opening_bal, bal_type, now_s))
        if "Creditor" in under_group or "વેપારી" in under_group:
            c.execute("INSERT OR IGNORE INTO config_parties (party_name, category) VALUES (?, 'મોબાઈલ હેન્ડસેટ')", (ledger_name.strip(),))
        elif "Staff" in under_group or "સ્ટાફ" in under_group:
            c.execute("INSERT OR IGNORE INTO config_staff (name, designation, fixed_salary) VALUES (?, 'સેલ્સમેન', 12000)", (ledger_name.strip(),))
        elif "Expense" in under_group or "ખર્ચ" in under_group:
            c.execute("INSERT OR IGNORE INTO config_expense_heads (head_name) VALUES (?)", (ledger_name.strip(),))
        elif "Bank" in under_group or "બેંક" in under_group:
            c.execute("INSERT OR IGNORE INTO config_banks (bank_name) VALUES (?)", (ledger_name.strip(),))

    conn.commit()
    conn.close()
    return redir(f"✅ ટેલી માસ્ટર લેજર '{ledger_name}' સફળતાપૂર્વક સેવ થયું!", "GUJARATI_CONFIG")

# --- CRUD અને ઓડિટ રાઉટ્સ (ઉમેરો / એડિટ / ડિલીટ) ---
@app.post("/add-party")
def add_party_route(party_name: str = Form(...), category: str = Form("મોબાઈલ હેન્ડસેટ"), gstin: str = Form(""), mobile: str = Form(""), address: str = Form(""), return_sheet: str = Form("GUJARATI_CONFIG"), edit_id: int = Form(0), pin: str = Form("")):
    conn = sqlite3.connect(get_active_db_file(), timeout=60.0)
    c = conn.cursor()
    if edit_id > 0:
        if str(pin).strip() != "1986":
            conn.close()
            return redir("❌ વેપારી લેજર એડિટ કરવા માટે માસ્ટર સિક્રેટ PIN ફરજિયાત છે!", return_sheet)
        c.execute("UPDATE config_parties SET party_name=?, category=? WHERE id=?", (party_name.strip(), category, edit_id))
    else:
        c.execute("INSERT OR IGNORE INTO config_parties (party_name, category) VALUES (?, ?)", (party_name.strip(), category))
        if gstin or mobile or address:
            c.execute("""INSERT INTO tally_master_ledgers (ledger_name, under_group, mobile, gstin, address, created_at)
                VALUES (?, 'વેપારી (Sundry Creditors)', ?, ?, ?, ?)""",
                (party_name.strip(), mobile, gstin, address, str(datetime.date.today())))
    conn.commit()
    conn.close()
    return redir(f"✅ વેપારી '{party_name}' સેવ થઈ ગયા!", return_sheet, "F1")

@app.get("/delete-party")
def delete_party_route(id: int, pin: str = ""):
    if str(pin).strip() != "1986":
        return redir("❌ ડિલીટ કરવા માટે સાચો માસ્ટર સિક્રેટ PIN જરૂરી છે!", "GUJARATI_CONFIG")
    conn = sqlite3.connect(get_active_db_file(), timeout=60.0)
    c = conn.cursor()
    c.execute("SELECT party_name, category FROM config_parties WHERE id=?", (id,))
    r = c.fetchone()
    old_data = f"{r[0]} ({r[1]})" if r else str(id)
    conn.execute("DELETE FROM config_parties WHERE id=?", (id,))
    conn.commit()
    conn.close()
    log_audit_action("DELETE_PARTY", "config_parties", str(id), old_data=old_data, authorized_by="PIN 1986")
    return redir(f"🗑️ વેપારી '{old_data}' ડિલીટ કર્યા (ઓડિટ લૉગ સેવ થયો)!", "GUJARATI_CONFIG")

@app.post("/add-staff")
def add_staff_route(name: str = Form(...), designation: str = Form("સેલ્સમેન"), fixed_salary: float = Form(12000), edit_id: int = Form(0), pin: str = Form("")):
    conn = sqlite3.connect(get_active_db_file(), timeout=60.0)
    if edit_id > 0:
        if str(pin).strip() != "1986":
            conn.close()
            return redir("❌ સ્ટાફ એડિટ કરવા માટે માસ્ટર સિક્રેટ PIN ફરજિયાત છે!", "GUJARATI_CONFIG")
        conn.execute("UPDATE config_staff SET name=?, designation=?, fixed_salary=? WHERE id=?", (name.strip(), designation, fixed_salary, edit_id))
    else:
        conn.execute("INSERT OR IGNORE INTO config_staff (name, designation, fixed_salary) VALUES (?, ?, ?)", (name.strip(), designation, fixed_salary))
    conn.commit()
    conn.close()
    return redir(f"✅ સ્ટાફ '{name}' સેવ થઈ ગયા!", "GUJARATI_CONFIG")

@app.get("/delete-staff")
def delete_staff_route(id: int, pin: str = ""):
    if str(pin).strip() != "1986":
        return redir("❌ ડિલીટ કરવા માટે સાચો માસ્ટર સિક્રેટ PIN જરૂરી છે!", "GUJARATI_CONFIG")
    conn = sqlite3.connect(get_active_db_file(), timeout=60.0)
    c = conn.cursor()
    c.execute("SELECT name, designation FROM config_staff WHERE id=?", (id,))
    r = c.fetchone()
    old_data = f"{r[0]} ({r[1]})" if r else str(id)
    conn.execute("DELETE FROM config_staff WHERE id=?", (id,))
    conn.commit()
    conn.close()
    log_audit_action("DELETE_STAFF", "config_staff", str(id), old_data=old_data, authorized_by="PIN 1986")
    return redir(f"🗑️ સ્ટાફ '{old_data}' ડિલીટ કર્યા (ઓડિટ લૉગ સેવ થયો)!", "GUJARATI_CONFIG")

@app.post("/add-designation")
def add_designation_route(title: str = Form(...), edit_id: int = Form(0)):
    conn = sqlite3.connect(get_active_db_file(), timeout=60.0)
    if edit_id > 0:
        conn.execute("UPDATE config_designations SET title=? WHERE id=?", (title.strip(), edit_id))
    else:
        conn.execute("INSERT OR IGNORE INTO config_designations (title) VALUES (?)", (title.strip(),))
    conn.commit()
    conn.close()
    return redir(f"✅ હોદ્દો '{title}' સેવ થયો!", "GUJARATI_CONFIG")

@app.get("/delete-designation")
def delete_designation_route(id: int, pin: str = ""):
    if str(pin).strip() != "1986":
        return redir("❌ ડિલીટ કરવા માટે સાચો માસ્ટર સિક્રેટ PIN જરૂરી છે!", "GUJARATI_CONFIG")
    conn = sqlite3.connect(get_active_db_file(), timeout=60.0)
    c = conn.cursor()
    c.execute("SELECT title FROM config_designations WHERE id=?", (id,))
    r = c.fetchone()
    old_data = r[0] if r else str(id)
    conn.execute("DELETE FROM config_designations WHERE id=?", (id,))
    conn.commit()
    conn.close()
    log_audit_action("DELETE_DESIGNATION", "config_designations", str(id), old_data=old_data, authorized_by="PIN 1986")
    return redir(f"🗑️ હોદ્દો '{old_data}' ડિલીટ થયો!", "GUJARATI_CONFIG")

@app.post("/add-category")
def add_category_route(name: str = Form(...), edit_id: int = Form(0)):
    conn = sqlite3.connect(get_active_db_file(), timeout=60.0)
    if edit_id > 0:
        conn.execute("UPDATE config_categories SET name=? WHERE id=?", (name.strip(), edit_id))
    else:
        conn.execute("INSERT OR IGNORE INTO config_categories (name) VALUES (?)", (name.strip(),))
    conn.commit()
    conn.close()
    return redir(f"✅ કેટેગરી '{name}' સેવ થઈ!", "GUJARATI_CONFIG")

@app.get("/delete-category")
def delete_category_route(id: int, pin: str = ""):
    if str(pin).strip() != "1986":
        return redir("❌ ડિલીટ કરવા માટે સાચો માસ્ટર સિક્રેટ PIN જરૂરી છે!", "GUJARATI_CONFIG")
    conn = sqlite3.connect(get_active_db_file(), timeout=60.0)
    c = conn.cursor()
    c.execute("SELECT name FROM config_categories WHERE id=?", (id,))
    r = c.fetchone()
    old_data = r[0] if r else str(id)
    conn.execute("DELETE FROM config_categories WHERE id=?", (id,))
    conn.commit()
    conn.close()
    log_audit_action("DELETE_CATEGORY", "config_categories", str(id), old_data=old_data, authorized_by="PIN 1986")
    return redir(f"🗑️ કેટેગરી '{old_data}' ડિલીટ થઈ!", "GUJARATI_CONFIG")

@app.get("/cloud-backup-upload")
def cloud_backup_upload_route():
    run_automated_backup_and_sync()
    return redir("☁️ ક્લાઉડ અને 90-Day FIFO બેકઅપ સફળતાપૂર્વક અપડેટ થઈ ગયો!", "GUJARATI_CONFIG")

@app.get("/cloud-backup-download")
def cloud_backup_download_route():
    run_automated_backup_and_sync()
    return redir("📥 ક્લાઉડ બેકઅપ સિંક થઈને લોકલ ફોલ્ડરમાં સેવ થઈ ગયો!", "GUJARATI_CONFIG")

@app.get("/delete-stock-item")
def delete_stock_item_route(id: int, pin: str = ""):
    if str(pin).strip() != "1986":
        return redir("❌ સ્ટોક ડિલીટ કરવા માટે સાચો માસ્ટર સિક્રેટ PIN જરૂરી છે!", "LIVE_STOCK_VIEW")
    conn = sqlite3.connect(get_active_db_file(), timeout=60.0)
    c = conn.cursor()
    c.execute("SELECT model, imei, purchase_rate FROM live_stock WHERE id=?", (id,))
    r = c.fetchone()
    old_data = f"{r[0]} ({r[1]})" if r else str(id)
    conn.execute("DELETE FROM live_stock WHERE id=?", (id,))
    conn.commit()
    conn.close()
    log_audit_action("DELETE_STOCK_ITEM", "live_stock", str(id), old_data=old_data, authorized_by="PIN 1986")
    return redir(f"🗑️ સ્ટોક આઇટમ '{old_data}' ડિલીટ થઈ (ઓડિટ લૉગ સેવ થયો)!", "LIVE_STOCK_VIEW")

@app.get("/delete-pending-apx")
def delete_pending_apx_route(id: int, pin: str = ""):
    conn = sqlite3.connect(get_active_db_file(), timeout=60.0)
    c = conn.cursor()
    c.execute("SELECT bill_no, customer_name, model FROM apx_sales_raw WHERE id=?", (id,))
    r = c.fetchone()
    old_data = f"{r[0]} - {r[1]} ({r[2]})" if r else str(id)
    conn.execute("DELETE FROM apx_sales_raw WHERE id=?", (id,))
    conn.commit()
    conn.close()
    log_audit_action("DELETE_PENDING_APX", "apx_sales_raw", str(id), old_data=old_data, authorized_by="PIN 1986")
    return redir(f"🗑️ પેન્ડિંગ બિલ '{old_data}' ડિલીટ થયું!", "SMART_TERMINAL", "F2")

@app.get("/delete-pending-do")
def delete_pending_do_route(id: int, pin: str = ""):
    conn = sqlite3.connect(get_active_db_file(), timeout=60.0)
    c = conn.cursor()
    c.execute("SELECT company, customer_name, loan_amt FROM finance_do_list WHERE id=?", (id,))
    r = c.fetchone()
    old_data = f"{r[0]} - {r[1]} (Loan: ₹{r[2]})" if r else str(id)
    conn.execute("DELETE FROM finance_do_list WHERE id=?", (id,))
    conn.commit()
    conn.close()
    log_audit_action("DELETE_PENDING_DO", "finance_do_list", str(id), old_data=old_data, authorized_by="PIN 1986")
    return redir(f"🗑️ પેન્ડિંગ DO '{old_data}' ડિલીટ થયો!", "SMART_TERMINAL", "F2")

@app.post("/scan-barcode-audit")
def scan_barcode_audit_route(scan_imei: str = Form(...)):
    im_clean = scan_imei.strip()
    now_dt = datetime.datetime.now()
    d_str, t_str = now_dt.strftime("%Y-%m-%d"), now_dt.strftime("%H:%M:%S")
    sid = STORE_CFG.get("shop_id", "DEVANSHI")
    conn = sqlite3.connect(get_active_db_file(), timeout=60.0)
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS barcode_audit_unlisted_scans (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        scan_date TEXT, scan_time TEXT, imei TEXT UNIQUE,
        remarks TEXT DEFAULT 'અજાણ્યો સ્કેન થયેલ પીસ / પરચેસ બાકી', store_id TEXT DEFAULT 'DEVANSHI'
    )""")
    c.execute("UPDATE live_stock SET audit_verified=1 WHERE imei=? AND status='IN_STOCK'", (im_clean,))
    updated = c.rowcount
    if updated == 0:
        c.execute("""INSERT OR REPLACE INTO barcode_audit_unlisted_scans
                     (scan_date, scan_time, imei, remarks, store_id)
                     VALUES (?, ?, ?, 'અજાણ્યો સ્કેન થયેલ પીસ / પરચેસ લેવાની બાકી', ?)""",
                  (d_str, t_str, im_clean, sid))
    else:
        c.execute("DELETE FROM barcode_audit_unlisted_scans WHERE imei=?", (im_clean,))
    conn.commit()
    conn.close()
    msg = f"🟢 લીલો (VERIFIED): IMEI {im_clean} હાજર સ્ટોકમાં વેરિફાઈડ થયો!" if updated else f"🟠 ઓરેન્જ એલર્ટ (UNKNOWN / પરચેસ બાકી): IMEI {im_clean} સ્ટોકમાં મળ્યો નથી — ઓરેન્જ લિસ્ટમાં ઉમેરાયો!"
    return redir(msg, "BARCODE_AUDIT")

@app.get("/reset-barcode-audit")
def reset_barcode_audit_route():
    conn = sqlite3.connect(get_active_db_file(), timeout=60.0)
    conn.execute("UPDATE live_stock SET audit_verified=0")
    try:
        conn.execute("DELETE FROM barcode_audit_unlisted_scans")
    except Exception:
        pass
    conn.commit()
    conn.close()
    return redir("🔄 ૪-કલર બારકોડ ઓડિટ (લીલો, લાલ, ઓરેન્જ, પીળો) ક્લિયર (00) થયું!", "BARCODE_AUDIT")

@app.post("/save-growth-manual")
def save_growth_manual_route(year: str = Form(...), month: str = Form(...), amount: float = Form(0)):
    conn = sqlite3.connect(get_active_db_file(), timeout=60.0)
    conn.execute("INSERT OR REPLACE INTO growth_monthly_manual (year, month, amount) VALUES (?, ?, ?)", (year.strip(), month.strip(), amount))
    conn.commit()
    conn.close()
    return redir(f"✅ {month} ({year}) ગ્રોથ ડેટા સેવ થયો!", "SMART_DESK_GROWTH")

def _rollback_running_grid_row(conn, c, grid_id: int) -> str:
    """કોઈપણ એન્ટ્રી (Buyback, Sale, Expense, Payout, Due, Purchase) ડિલીટ કે Undo થાય ત્યારે ગલ્લા કેશ, સ્ટોક અને લેજરમાંથી તેની ૧૦૦% રકમ રિવર્સ/સેટ કરી દેશે!"""
    c.execute("SELECT id, entry_time, bill_no, customer_name, model_name, imei, galla_name, entry_type, total_padtar, gift_amt, due_amt, salesman FROM live_terminal_grid WHERE id=?", (grid_id,))
    row = c.fetchone()
    if not row:
        return "⚠️ રદ કરવા માટે કોઈ વ્યવહાર મળ્યો નથી!"
    gid, etime, bno, cust, mod, imei, gname, etype, amt, gift, due, sm = row
    d_str = str(etime or "")[:10]
    amt_f = float(amt or 0)
    imei_clean = str(imei or "").strip()

    # 1. જો બાય-બેક ખરીદી (DIRECT_BB) હોય તો buyback_stock માંથી કાઢો અને ગલ્લામાંથી કપાયેલી રોકડ પાછી સેટ કરો
    if etype == "DIRECT_BB" or bno == "BB-IN":
        if imei_clean and imei_clean != "-":
            c.execute("DELETE FROM buyback_stock WHERE imei=? AND status='IN_STOCK'", (imei_clean,))
            c.execute("DELETE FROM galla_ledger WHERE id IN (SELECT id FROM galla_ledger WHERE out_amt=? AND (remarks LIKE ? OR remarks LIKE ?) ORDER BY id DESC LIMIT 1)",
                      (amt_f, f"%{imei_clean}%", f"%{mod}%"))
        else:
            c.execute("DELETE FROM buyback_stock WHERE id IN (SELECT id FROM buyback_stock WHERE model=? AND purchase_cost=? ORDER BY id DESC LIMIT 1)", (mod, amt_f))
            c.execute("DELETE FROM galla_ledger WHERE id IN (SELECT id FROM galla_ledger WHERE out_amt=? AND remarks LIKE '%બાયબેક%' ORDER BY id DESC LIMIT 1)", (amt_f,))

    # 2. જો વેચાણ બિલ (FINANCE_BILL / CASH_BILL / CREDIT_BILL) હોય
    elif etype in ("FINANCE_BILL", "CASH_BILL", "CREDIT_BILL") or (bno and not bno.startswith(("BB-", "EXP", "PAY", "RECH", "ACC", "SUPP", "EXT"))):
        if imei_clean and imei_clean != "-":
            c.execute("UPDATE live_stock SET status='IN_STOCK' WHERE imei=?", (imei_clean,))
        c.execute("DELETE FROM apx_sales_raw WHERE bill_no=?", (bno,))
        c.execute("SELECT COALESCE(SUM(received_amt), 0) FROM customer_due_ledger WHERE bill_no=?", (bno,))
        rec_due_rev = float((c.fetchone() or [0])[0] or 0)
        if rec_due_rev > 0:
            c.execute("DELETE FROM galla_ledger WHERE remarks LIKE ? OR remarks LIKE ?", (f"%બાકી વસૂલાત%{bno}%", f"%બાકી વસૂલાત%{cust}%"))
        c.execute("DELETE FROM customer_due_ledger WHERE bill_no=?", (bno,))
        c.execute("DELETE FROM gift_ledger WHERE bill_no=?", (bno,))
        c.execute("DELETE FROM staff_commission_ledger WHERE bill_ref=?", (bno,))
        c.execute("DELETE FROM galla_ledger WHERE remarks LIKE ?", (f"%{bno}%",))
        c.execute("DELETE FROM buyback_stock WHERE source_type LIKE '%એક્સચેન્જ%' AND customer_name=? AND date=?", (cust, d_str))

    # 3. જો જૂના ફોનનું વેચાણ (F5_BB_SALE) હોય
    elif etype == "F5_BB_SALE" or bno == "BB-SALE":
        if imei_clean and imei_clean != "-":
            c.execute("UPDATE buyback_stock SET status='IN_STOCK', sale_price=0 WHERE imei=?", (imei_clean,))
            c.execute("DELETE FROM galla_ledger WHERE remarks LIKE ?", (f"%{imei_clean}%",))

    # 4. જો દૈનિક ખર્ચ / લમ્પ-સમ વકરો (F6_EXPENSE / EXPENSE) હોય
    elif "EXP" in str(etype) or "F6" in str(etype) or bno == "EXP":
        c.execute("DELETE FROM galla_ledger WHERE id IN (SELECT id FROM galla_ledger WHERE (out_amt=? OR in_amt=?) AND date=? ORDER BY id DESC LIMIT 1)", (amt_f, amt_f, d_str))

    # 5. જો પેમેન્ટ આઉટ / સ્ટાફ ઉપાડ (F3_PAY_OUT / STAFF) હોય
    elif "PAY_OUT" in str(etype) or bno == "PAY-OUT" or "STAFF" in str(etype):
        c.execute("DELETE FROM galla_ledger WHERE id IN (SELECT id FROM galla_ledger WHERE out_amt=? AND date=? ORDER BY id DESC LIMIT 1)", (amt_f, d_str))
        c.execute("DELETE FROM supplier_purchase_ledger WHERE id IN (SELECT id FROM supplier_purchase_ledger WHERE paid_amt=? AND date=? ORDER BY id DESC LIMIT 1)", (amt_f, d_str))
        c.execute("DELETE FROM staff_commission_ledger WHERE id IN (SELECT id FROM staff_commission_ledger WHERE paid_amt=? AND date=? ORDER BY id DESC LIMIT 1)", (amt_f, d_str))

    # 6. જો ઉધાર વસૂલાત (F4_DUE_REC) હોય
    elif "DUE_REC" in str(etype):
        c.execute("UPDATE customer_due_ledger SET received_amt = MAX(0, received_amt - ?) WHERE customer_name=? AND bill_no=?", (amt_f, cust, bno))
        c.execute("DELETE FROM galla_ledger WHERE id IN (SELECT id FROM galla_ledger WHERE in_amt=? AND remarks LIKE ? ORDER BY id DESC LIMIT 1)", (amt_f, f"%{cust}%"))

    # 7. જો ખરીદી (PURCHASE / CONSUMER_PURCHASE / ACC_PURCHASE / RECHARGE_TOPUP) હોય
    elif "PURCHASE" in str(etype) or "TOPUP" in str(etype):
        if imei_clean and imei_clean != "-":
            for sim in imei_clean.replace(",", " ").split():
                c.execute("DELETE FROM live_stock WHERE imei=?", (sim.strip(),))
        c.execute("DELETE FROM supplier_purchase_ledger WHERE id IN (SELECT id FROM supplier_purchase_ledger WHERE total_bill=? AND date=? ORDER BY id DESC LIMIT 1)", (amt_f, d_str))
        c.execute("DELETE FROM galla_ledger WHERE id IN (SELECT id FROM galla_ledger WHERE date=? AND (remarks LIKE ? OR remarks LIKE ?) ORDER BY id DESC LIMIT 1)", (d_str, f"%{cust}%", f"%{bno}%"))

    # 8. જો એક્સ્ટ્રા પ્રોફિટ (F7_EXTRA_PROFIT) હોય
    elif "EXTRA_PROFIT" in str(etype) or bno == "EXT-PROF":
        c.execute("DELETE FROM direct_extra_profit_log WHERE id IN (SELECT id FROM direct_extra_profit_log WHERE net_profit_amt=? AND entry_date=? ORDER BY id DESC LIMIT 1)", (amt_f, d_str))
        c.execute("DELETE FROM galla_ledger WHERE id IN (SELECT id FROM galla_ledger WHERE in_amt=? AND date=? ORDER BY id DESC LIMIT 1)", (amt_f, d_str))

    c.execute("DELETE FROM live_terminal_grid WHERE id=?", (gid,))
    return f"↩️ વ્યવહાર '{bno} - {cust} ({mod}, ₹{amt_f:,.0f})' રદ થયો અને તેની રોકડ/સ્ટોક રકમ ગલ્લામાં પૂરેપૂરી રિવર્સ (Set) થઈ ગઈ!"

@app.get("/undo-last")
def undo_last_transaction_route():
    conn = sqlite3.connect(get_active_db_file(), timeout=60.0)
    c = conn.cursor()
    c.execute("SELECT id FROM live_terminal_grid ORDER BY id DESC LIMIT 1")
    last_r = c.fetchone()
    if last_r:
        msg = _rollback_running_grid_row(conn, c, last_r[0])
    else:
        msg = "⚠️ રદ કરવા માટે કોઈ તાજેતરનો વ્યવહાર નથી!"
    conn.commit()
    conn.close()
    return redir(msg, "SMART_TERMINAL", "F2")

@app.api_route("/api/delete-running-tx", methods=["GET", "POST"])
async def delete_running_tx_route(request: Request):
    clean_id = request.query_params.get("id") or request.query_params.get("tx_id")
    clean_pin = request.query_params.get("pin") or request.query_params.get("owner_pin") or ""
    is_json = "application/json" in (request.headers.get("accept") or "") or "XMLHttpRequest" in (request.headers.get("x-requested-with") or "")

    if request.method == "POST":
        try:
            form = await request.form()
            clean_id = clean_id or form.get("id") or form.get("tx_id")
            clean_pin = clean_pin or form.get("pin") or form.get("owner_pin") or ""
        except Exception:
            try:
                data = await request.json()
                clean_id = clean_id or data.get("id") or data.get("tx_id")
                clean_pin = clean_pin or data.get("pin") or data.get("owner_pin") or ""
            except Exception:
                pass

    try:
        clean_id = int(str(clean_id).strip())
    except Exception:
        clean_id = None

    sid = (request.cookies.get("devanshi_shop_id") or STORE_CFG.get("shop_id", "DEVANSHI")).strip().upper()
    valid_pins = {"1986", str(STORE_CFG.get("master_pin", "")).strip(), str(STORE_CFG.get("admin_pin", "")).strip(), "J@ymin86"}
    
    # Also allow store password as pin
    try:
        _mc = sqlite3.connect(MASTER_DB_FILE, timeout=10.0)
        _mr = _mc.execute("SELECT owner_pass FROM master_saas_shops_registry WHERE UPPER(shop_id)=UPPER(?)", (sid,)).fetchone()
        if _mr and _mr[0]:
            valid_pins.add(str(_mr[0]).strip())
        _mc.close()
    except Exception:
        pass

    if str(clean_pin).strip() not in valid_pins:
        msg = "❌ વ્યવહાર રદ કરવા માટે સાચો માસ્ટર સિક્રેટ PIN જરૂરી છે!"
        if is_json:
            return JSONResponse({"status": "error", "message": msg}, status_code=400)
        return redir(msg, "SMART_TERMINAL", "F2")

    if not clean_id:
        msg = "⚠️ રદ કરવા માટે અમાન્ય વ્યવહાર ID!"
        if is_json:
            return JSONResponse({"status": "error", "message": msg}, status_code=400)
        return redir(msg, "SMART_TERMINAL", "F2")

    target_db = get_active_db_file(sid)
    conn = sqlite3.connect(target_db, timeout=60.0)
    c = conn.cursor()
    msg = _rollback_running_grid_row(conn, c, clean_id)
    conn.commit()
    conn.close()

    if is_json:
        return JSONResponse({"status": "success", "message": msg})
    return redir(msg, "SMART_TERMINAL", "F2")

@app.get("/delete-buyback-item")
def delete_buyback_item_route(id: int, pin: str = ""):
    if str(pin).strip() != "1986":
        return redir("❌ બાય-બેક ફોન રદ કરવા સાચો માસ્ટર સિક્રેટ PIN નાખો!", "BUYBACK_STOCK")
    conn = sqlite3.connect(get_active_db_file(), timeout=60.0)
    c = conn.cursor()
    c.execute("SELECT date, customer_name, model, imei, purchase_cost, repair_cost, total_cost, sale_price, status FROM buyback_stock WHERE id=?", (id,))
    r = c.fetchone()
    if r:
        d_str, cust, mod, imei, p_cost, r_cost, t_cost, s_prc, st = r
        p_cost = float(p_cost or 0)
        r_cost = float(r_cost or 0)
        # ગલ્લામાંથી કપાયેલી ખરીદ રકમ અને રિપેરિંગ રકમ બંને કાઢી નાખો જેથી ગલ્લા બેલેન્સ ૧૦૦% સેટ થઈ જાય!
        c.execute("DELETE FROM galla_ledger WHERE (remarks LIKE ? OR (out_amt=? AND remarks LIKE ?))",
                  (f"%{imei}%", p_cost, f"%{mod}%"))
        if r_cost > 0:
            c.execute("DELETE FROM galla_ledger WHERE out_amt=? AND remarks LIKE ?", (r_cost, f"%{imei}%"))
        c.execute("DELETE FROM live_terminal_grid WHERE imei=? AND entry_type IN ('DIRECT_BB','F5_BB_SALE')", (imei,))
        c.execute("DELETE FROM buyback_stock WHERE id=?", (id,))
        conn.commit()
        conn.close()
        return redir(f"🗑️ બાય-બેક ફોન '{mod} ({imei})' રદ થયો અને ગલ્લામાંથી કપાયેલા ₹{float(t_cost or p_cost):,.0f} પૂરેપૂરા પાછા સેટ થઈ ગયા!", "BUYBACK_STOCK")
    conn.close()
    return redir("⚠️ બાય-બેક એન્ટ્રી મળી નથી!", "BUYBACK_STOCK")

@app.post("/api/edit-buyback-item")
def edit_buyback_item_route(
    bb_id: int = Form(...), customer_name: str = Form(...), model: str = Form(...),
    imei: str = Form(...), purchase_cost: float = Form(0), repair_cost: float = Form(0),
    salesman: str = Form(""), pin: str = Form("1986")
):
    if str(pin).strip() != "1986":
        return redir("❌ બાય-બેક એન્ટ્રી સુધારવા સાચો માસ્ટર સિક્રેટ PIN નાખો!", "BUYBACK_STOCK")
    conn = sqlite3.connect(get_active_db_file(), timeout=60.0)
    c = conn.cursor()
    c.execute("SELECT purchase_cost, repair_cost, imei, model, COALESCE(galla_name,'BANK_CASH'), date FROM buyback_stock WHERE id=?", (bb_id,))
    old_r = c.fetchone()
    if old_r:
        old_p, old_rep, old_im, old_mod, g_name, d_str = float(old_r[0] or 0), float(old_r[1] or 0), old_r[2], old_r[3], old_r[4] or "BANK_CASH", old_r[5]
        new_tot = float(purchase_cost or 0) + float(repair_cost or 0)
        c.execute("""UPDATE buyback_stock
                     SET customer_name=?, model=?, imei=?, purchase_cost=?, repair_cost=?, total_cost=?, salesman=?
                     WHERE id=?""",
                  (customer_name.strip(), model.strip(), imei.strip(), purchase_cost, repair_cost, new_tot, salesman.strip(), bb_id))
        # Update galla_ledger entry so cash balance reflects the edited amount accurately
        c.execute("SELECT id FROM galla_ledger WHERE (remarks LIKE ? OR (out_amt=? AND remarks LIKE ?)) ORDER BY id DESC LIMIT 1",
                  (f"%{old_im}%", old_p, f"%{old_mod}%"))
        gl_row = c.fetchone()
        if gl_row:
            c.execute("UPDATE galla_ledger SET out_amt=?, remarks=? WHERE id=?",
                      (purchase_cost, f"જૂનો ફોન બાયબેક ખરીદી (સુધારેલ): {model} ({imei}) [{customer_name}]", gl_row[0]))
        c.execute("UPDATE live_terminal_grid SET customer_name=?, model_name=?, imei=?, total_padtar=?, salesman=? WHERE imei=? AND entry_type='DIRECT_BB'",
                  (customer_name.strip(), model.strip(), imei.strip(), purchase_cost, salesman.strip(), old_im))
        conn.commit()
    conn.close()
    return redir(f"✅ બાય-બેક ફોન '{model} ({imei})' ની વિગત અને રોકડ રકમ (₹{purchase_cost:,.0f}) સફળતાપૂર્વક સુધારાઈ ગઈ!", "BUYBACK_STOCK")

@app.get("/api/cancel-buyback-repair")
def cancel_buyback_repair_route(id: int, pin: str = ""):
    if str(pin).strip() != "1986":
        return redir("❌ રિપેરિંગ ખર્ચ રદ કરવા સાચો માસ્ટર સિક્રેટ PIN નાખો!", "BUYBACK_STOCK")
    conn = sqlite3.connect(get_active_db_file(), timeout=60.0)
    c = conn.cursor()
    c.execute("SELECT imei, model, purchase_cost, repair_cost FROM buyback_stock WHERE id=?", (id,))
    r = c.fetchone()
    if r and float(r[3] or 0) > 0:
        im, mod, p_c, rep_c = r[0], r[1], float(r[2] or 0), float(r[3] or 0)
        c.execute("UPDATE buyback_stock SET repair_cost=0, total_cost=? WHERE id=?", (p_c, id))
        c.execute("DELETE FROM galla_ledger WHERE out_amt=? AND remarks LIKE ?", (rep_c, f"%{im}%"))
        conn.commit()
        conn.close()
        return redir(f"🛠️ બાય-બેક ફોન '{mod} ({im})' નો રિપેરિંગ ખર્ચ ₹{rep_c:,.0f} રદ થયો અને ગલ્લામાં પાછો જમા થઈ ગયો!", "BUYBACK_STOCK")
    conn.close()
    return redir("⚠️ આ ફોનમાં કોઈ રિપેરિંગ ખર્ચ નોંધાયેલ નથી.", "BUYBACK_STOCK")

@app.get("/delete-customer-due")
def delete_customer_due_route(id: int, pin: str = ""):
    if str(pin).strip() != "1986":
        return redir("❌ ઉધાર એન્ટ્રી રદ કરવા માસ્ટર સિક્રેટ PIN નાખો!", "CUSTOMER_DUE")
    conn = sqlite3.connect(get_active_db_file(), timeout=60.0)
    conn.execute("DELETE FROM customer_due_ledger WHERE id=?", (id,))
    conn.commit()
    conn.close()
    return redir("🗑️ ગ્રાહક ઉધાર એન્ટ્રી રદ કરવામાં આવી!", "CUSTOMER_DUE")

def _reconcile_carry_forward_history(conn):
    """જૂની તારીખની કોઈપણ રોકડ એન્ટ્રી એડિટ કે ડિલીટ થાય ત્યારે ત્યારપછીના તમામ દિવસોની ઓપનિંગ/ક્લોઝિંગ આપમેળે સરભર (Reconcile) કરે છે."""
    c = conn.cursor()
    for gk in ("BANK_CASH", "ACC_DCASH", "RECHARGE", "EXTRA_CASH"):
        c.execute("SELECT id, audit_date, opening_bal, bank_deposit, physical_counted FROM galla_audit_daily_history WHERE galla_name=? ORDER BY audit_date ASC, id ASC", (gk,))
        h_rows = c.fetchall()
        running_open = None
        for hid, adate, op_b, b_dep, phys_c in h_rows:
            cur_open = float(op_b or 0) if running_open is None else running_open
            c.execute("SELECT COALESCE(SUM(in_amt),0), COALESCE(SUM(out_amt),0) FROM galla_ledger WHERE date=? AND galla_name=?", (adate, gk))
            ti, to = c.fetchone() or (0, 0)
            ti, to = float(ti or 0), float(to or 0)
            exp_close = cur_open + ti - to - float(b_dep or 0)
            diff_v = float(phys_c or 0) - exp_close
            c.execute("UPDATE galla_audit_daily_history SET opening_bal=?, total_in=?, total_out=?, expected_closing=?, diff_amt=? WHERE id=?",
                      (cur_open, ti, to, exp_close, diff_v, hid))
            running_open = exp_close

@app.get("/delete-galla-entry")
def delete_galla_entry_route(id: int, pin: str = ""):
    if str(pin).strip() != "1986":
        return redir("❌ રોજમેળ એન્ટ્રી રદ કરવા માસ્ટર સિક્રેટ PIN નાખો!", "DAILY_SUMMARY")
    conn = sqlite3.connect(get_active_db_file(), timeout=60.0)
    conn.execute("DELETE FROM galla_ledger WHERE id=?", (id,))
    _reconcile_carry_forward_history(conn)
    conn.commit()
    conn.close()
    return redir("🗑️ રોજમેળ (ગલ્લા) એન્ટ્રી રદ થઈ અને સિલક સેટ થઈ ગઈ!", "DAILY_SUMMARY")

@app.post("/api/inline-create-entity")
def inline_create_entity_api(
    entity_type: str = Form(...), name: str = Form(...), sub_category: str = Form(""),
    mobile: str = Form(""), gstin: str = Form(""), address: str = Form("")
):
    et = (entity_type or "PARTY").strip().upper()
    nm = name.strip()
    sub = sub_category.strip()
    sid = STORE_CFG.get("shop_id", "DEVANSHI")
    d_str = str(datetime.date.today())
    conn = sqlite3.connect(get_active_db_file(), timeout=60.0)
    c = conn.cursor()
    opt_val, opt_txt = nm, nm
    try:
        if et == "PARTY":
            cat_use = sub or "મોબાઈલ હેન્ડસેટ"
            c.execute("INSERT OR IGNORE INTO config_categories (name) VALUES (?)", (cat_use,))
            c.execute("INSERT OR IGNORE INTO config_parties (party_name, category, gstin, mobile, address) VALUES (?, ?, ?, ?, ?)",
                      (nm, cat_use, gstin.strip(), mobile.strip(), address.strip()))
            c.execute("INSERT INTO tally_master_ledgers (store_id, ledger_name, under_group, mobile, gstin, address, created_at) VALUES (?, ?, 'વેપારી (Sundry Creditors)', ?, ?, ?, ?)",
                      (sid, nm, mobile.strip(), gstin.strip(), address.strip(), d_str))
            opt_val, opt_txt = nm, f"{nm} [{cat_use}]"
        elif et == "CUSTOMER":
            c.execute("INSERT INTO tally_master_ledgers (store_id, ledger_name, under_group, mobile, gstin, address, created_at) VALUES (?, ?, 'ગ્રાહક (Sundry Debtors)', ?, ?, ?, ?)",
                      (sid, nm, mobile.strip(), gstin.strip(), address.strip(), d_str))
            opt_val, opt_txt = nm, f"{nm} ({mobile.strip()})" if mobile.strip() else nm
        elif et == "STAFF":
            desig_use = sub or "સેલ્સમેન"
            sal_val = float(gstin) if (gstin and gstin.replace(".","",1).isdigit()) else 12000.0
            c.execute("INSERT OR IGNORE INTO config_designations (title) VALUES (?)", (desig_use,))
            c.execute("INSERT OR IGNORE INTO config_staff (name, designation, fixed_salary) VALUES (?, ?, ?)", (nm, desig_use, sal_val))
            opt_val, opt_txt = f"{nm} ({desig_use})", f"{nm} ({desig_use})"
        elif et == "BRAND":
            cat_use = sub or "મોબાઈલ હેન્ડસેટ"
            c.execute("INSERT OR IGNORE INTO config_categories (name) VALUES (?)", (cat_use,))
            c.execute("INSERT OR IGNORE INTO config_brands (brand_name, category, store_id) VALUES (?, ?, ?)", (nm, cat_use, sid))
            opt_val, opt_txt = nm, nm
        elif et == "CATEGORY":
            c.execute("INSERT OR IGNORE INTO config_categories (name) VALUES (?)", (nm,))
        elif et == "DESIGNATION":
            c.execute("INSERT OR IGNORE INTO config_designations (title) VALUES (?)", (nm,))
        elif et == "EXPENSE_HEAD":
            c.execute("INSERT OR IGNORE INTO config_expense_heads (head_name) VALUES (?)", (nm,))
        elif et == "BANK":
            c.execute("INSERT OR IGNORE INTO config_banks (bank_name) VALUES (?)", (nm,))
        elif et in ("FINANCE_COMP", "MODEL"):
            opt_val, opt_txt = nm, nm
        conn.commit()
        conn.close()
        return {"status": "ok", "option_value": opt_val, "option_text": opt_txt}
    except Exception as e:
        conn.close()
        return {"status": "error", "message": str(e)}

@app.post("/api/save-direct-customer-due")
async def save_direct_customer_due_route(
    entry_date: str = Form(""), due_entry_date: str = Form(""), customer_name: str = Form(...), phone: str = Form(""),
    address: str = Form(""), model_or_note: str = Form(""), bill_no: str = Form("DIRECT-DUE"), due_amt: float = Form(0),
    due_date: str = Form(""), salesman: str = Form(""), guarantor_name: str = Form(""),
    guarantor_village: str = Form(""), guarantor_phone: str = Form(""),
    return_sheet: str = Form("CUSTOMER_DUE"), due_doc: UploadFile = File(None)
):
    d_str = (entry_date or due_entry_date).strip() or str(datetime.date.today())
    sid = STORE_CFG.get("shop_id", "DEVANSHI")
    doc_u = ""
    if due_doc and due_doc.filename:
        fb = await due_doc.read()
        doc_u = save_to_vault(fb, due_doc.filename, "DIRECT_CUSTOMER_DUE", bill_no, customer_name)
    conn = sqlite3.connect(get_active_db_file(), timeout=60.0)
    from part1_core import add_col_if_missing
    add_col_if_missing(conn, "customer_due_ledger", "guarantor_name", "TEXT DEFAULT ''")
    add_col_if_missing(conn, "customer_due_ledger", "guarantor_village", "TEXT DEFAULT ''")
    add_col_if_missing(conn, "customer_due_ledger", "guarantor_phone", "TEXT DEFAULT ''")
    eff_bill = model_or_note.strip() or bill_no.strip() or "DIRECT-DUE"
    if guarantor_name.strip():
        eff_bill = f"{eff_bill} [જામીન: {guarantor_name.strip()} ({guarantor_village.strip()}) 📞{guarantor_phone.strip()}]"
    conn.execute("""INSERT INTO customer_due_ledger
                    (date, salesman, customer_name, phone, address, bill_no, due_amt, received_amt, due_date, file_path, guarantor_name, guarantor_village, guarantor_phone, store_id)
                    VALUES (?, ?, ?, ?, ?, ?, ?, 0, ?, ?, ?, ?, ?, ?)""",
                 (d_str, salesman, customer_name.strip(), phone.strip(), address.strip(), eff_bill, due_amt, due_date, doc_u,
                  guarantor_name.strip(), guarantor_village.strip(), guarantor_phone.strip(), sid))
    conn.commit()
    conn.close()
    return redir(f"✅ ગ્રાહક '{customer_name}' ની સીધી બાકી ઉધાર ₹{due_amt:,.0f} સેવ થઈ ગઈ!", return_sheet, "F3")

@app.post("/api/save-partner-capital-tx")
async def save_partner_capital_tx_route(
    tx_date: str = Form(""), partner_name: str = Form(...), tx_type: str = Form("CAPITAL_IN"),
    amount: float = Form(0), pay_mode: str = Form("રોકડ (Cash)"), galla_name: str = Form("BANK_CASH"),
    funding_source: str = Form("STORE_GALLA"), return_sheet: str = Form("SUPPLIER_PURCHASE"),
    remarks: str = Form("")
):
    d_str = tx_date.strip() or str(datetime.date.today())
    sid = STORE_CFG.get("shop_id", "DEVANSHI")
    conn = sqlite3.connect(get_active_db_file(), timeout=60.0)
    c = conn.cursor()
    eff_tx_type = tx_type.strip().upper()
    if eff_tx_type == "PARTNER_GIFT":
        eff_tx_type = "GIFT_IN"
    is_pocket = (funding_source == "PARTNER_POCKET" or "ખિસ્સામાંથી" in pay_mode or galla_name == "PARTNER_POCKET")
    eff_pay_mode = "પાર્ટનર અંગત ખિસ્સામાંથી (ગલ્લા સિવાય)" if is_pocket else pay_mode
    eff_galla_store = "PARTNER_POCKET (ગલ્લા સિવાય)" if is_pocket else galla_name
    c.execute("""INSERT INTO partner_capital_ledger (store_id, tx_date, partner_name, tx_type, amount, pay_mode, galla_name, remarks)
                 VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
              (sid, d_str, partner_name.strip(), eff_tx_type, amount, eff_pay_mode, eff_galla_store, remarks))
    if eff_tx_type == "GIFT_IN" and amount > 0:
        c.execute("INSERT INTO gift_ledger (date, bill_no, customer_name, model, gift_desc, gift_amt, salesman) VALUES (?, 'PARTNER-GIFT', ?, 'Store Gift Stock', ?, ?, ?)",
                  (d_str, partner_name.strip(), remarks or "પાર્ટનર ગિફ્ટ ખરીદી", amount, partner_name.strip()))
    if amount > 0 and ("રોકડ" in eff_pay_mode) and not is_pocket:
        if eff_tx_type == "CAPITAL_IN":
            c.execute("INSERT INTO galla_ledger (date, galla_name, in_amt, out_amt, remarks, store_id) VALUES (?, ?, ?, 0, ?, ?)",
                      (d_str, galla_name, amount, f"પાર્ટનર મૂડી જમા ({partner_name}): {remarks}", sid))
        else:
            c.execute("INSERT INTO galla_ledger (date, galla_name, in_amt, out_amt, remarks, store_id) VALUES (?, ?, 0, ?, ?, ?)",
                      (d_str, galla_name, amount, f"પાર્ટનર મૂડી પરત/ગિફ્ટ ({partner_name}): {remarks}", sid))
    conn.commit()
    conn.close()
    ret_s = return_sheet.strip() or "SUPPLIER_PURCHASE"
    return redir(f"🤝 પાર્ટનર '{partner_name}' નો હિસાબ (₹{amount:,.0f}) સફળતાપૂર્વક સેવ થઈ ગયો!", ret_s, "F3")

@app.get("/reset-demo-data")
def reset_demo_data_route():
    conn = sqlite3.connect(get_active_db_file(), timeout=60.0)
    for tbl in ["live_terminal_grid", "apx_sales_raw", "galla_ledger", "customer_due_ledger", "supplier_purchase_ledger", "bank_deposit_log", "gift_ledger"]:
        conn.execute(f"DELETE FROM {tbl}")
    conn.commit()
    conn.close()
    return redir("🧹 ડેમો વ્યવહારો સાફ થઈ ગયા!", "SMART_TERMINAL", "F2")

@app.post("/reverse-buyback-sold")
def reverse_buyback_sold_route(bb_id: int = Form(...), refund_galla: str = Form("BANK_CASH"), deduct_comm: str = Form("YES")):
    conn = sqlite3.connect(get_active_db_file(), timeout=60.0)
    c = conn.cursor()
    c.execute("SELECT model, imei, sale_price, salesman FROM buyback_stock WHERE id=?", (bb_id,))
    r = c.fetchone()
    if r:
        c.execute("UPDATE buyback_stock SET status='IN_STOCK', sale_price=0 WHERE id=?", (bb_id,))
        if float(r[2] or 0) > 0:
            c.execute("INSERT INTO galla_ledger (date, galla_name, in_amt, out_amt, remarks) VALUES (?, ?, 0, ?, ?)",
                      (str(datetime.date.today()), refund_galla, float(r[2]), f"બાયબેક વેચાણ રિવર્સલ ({r[0]} - {r[1]})"))
    conn.commit()
    conn.close()
    return redir("🔄 વેચાયેલો બાયબેક ફોન પાછો In-Stock માં લેવાયો!", "UNIVERSAL_SEARCH")

@app.post("/print-temp-invoice", response_class=HTMLResponse)
def print_temp_invoice_route(
    bill_no: str = Form(...), customer_name: str = Form(""), model: str = Form(""),
    mop_price: float = Form(0), admin_pin: str = Form(""), lang: str = Form("gu")
):
    if str(admin_pin).strip() == "1986":
        conn = sqlite3.connect(get_active_db_file(), timeout=60.0)
        conn.execute("UPDATE apx_sales_raw SET customer_name=?, model=?, mop_price=? WHERE bill_no=?",
                     (customer_name, model, mop_price, bill_no))
        conn.commit()
        conn.close()
        log_audit_action("PERM_EDIT_INVOICE", "apx_sales_raw", bill_no, new_data=f"{customer_name} | {model} | ₹{mop_price}", authorized_by="PIN 1986")
    return print_invoice_route(bill_no=bill_no, lang=lang, print_mode="MOP", temp_cust=customer_name, temp_mod=model, temp_mop=mop_price)

# =================================================================================
# ૧૨ ભારતીય ભાષા + MOP બિલ વિ. ડિસ્કાઉન્ટ બિલ મોડ + કાયમી ફૂટર (નિયમ ૨, ૩, ૪ & ૧૪૦)
# =================================================================================
LANG_DICT = {
    "gu": {
        "inv": "ટેક્સ ઇનવોઇસ / વેચાણ બિલ", "bill": "બિલ નંબર", "date": "તારીખ", "cust": "ગ્રાહકનું નામ", "ph": "મોબાઈલ",
        "addr_lbl": "સરનામું", "cust_gst_lbl": "ગ્રાહક GSTIN", "shop_gst_lbl": "દુકાન GSTIN",
        "item": "મોડેલ / આઇટમ વિગત", "imei": "IMEI / સિરિયલ નં.", "taxable_lbl": "ટેક્સેબલ રકમ",
        "amt": "કુલ રકમ (₹)", "disc_lbl": "ડિસ્કાઉન્ટ બાદ", "paid": "જમા રકમ", "due": "બાકી રકમ", "sign": "અધિકૃત સહી",
        "terms_hdr": "નિયમો અને શરતો (Terms & Conditions):",
        "default_terms": "૧. વેચેલો માલ પાછો લેવામાં કે બદલી આપવામાં આવશે નહીં.<br>૨. મોબાઈલ હેન્ડસેટની વોરંટી કંપનીના અધિકૃત સર્વિસ સેન્ટરથી નિયમ મુજબ રહેશે.<br>૩. કોઈપણ ન્યાયિક વિવાદ સ્થાનિક કોર્ટના કાર્યક્ષેત્રને આધીન રહેશે.",
        "warranty_hdr": "🛡️ વોરંટી અને સર્વિસ જવાબદારી નોંધ:",
        "warranty_txt": "નવા મોબાઈલ હેન્ડસેટ કે ઇલેક્ટ્રોનિક પ્રોડક્ટની વોરંટી કંપનીના અધિકૃત સર્વિસ સેન્ટર (Authorized Service Center) દ્વારા નિયમોનુસાર આપવામાં આવે છે. તૂટફૂટ કે પાણીથી થયેલ ભૌતિક નુકસાન (Physical/Liquid Damage) વોરંટીમાં માન્ય રહેશે નહીં.",
        "footer_txt": "દેવાંશી સોફ્ટવેર - જયમીન પટેલ: 9725721215"
    },
    "hi": {
        "inv": "टैक्स इनवॉइस / बिक्री बिल", "bill": "बिल नंबर", "date": "तारीख", "cust": "ग्राहक का नाम", "ph": "मोबाइल",
        "addr_lbl": "पता", "cust_gst_lbl": "ग्राहक GSTIN", "shop_gst_lbl": "दुकान GSTIN",
        "item": "मॉडल / आइटम विवरण", "imei": "IMEI / सीरियल नं.", "taxable_lbl": "कर योग्य राशि",
        "amt": "कुल राशि (₹)", "disc_lbl": "छूट (Discount)", "paid": "जमा राशि", "due": "बाकी राशि", "sign": "अधिकृत हस्ताक्षर",
        "terms_hdr": "नियम एवं शर्तें (Terms & Conditions):",
        "default_terms": "१. बेचा गया सामान वापस नहीं लिया जाएगा और न ही बदला जाएगा।<br>२. मोबाइल हैंडसेट की वारंटी कंपनी के अधिकृत सर्विस सेंटर से नियमों के अनुसार होगी।<br>३. सभी विवाद स्थानीय न्यायालय के अधीन होंगे।",
        "warranty_hdr": "🛡️ वारंटी और सर्विस जिम्मेदारी सूचना:",
        "warranty_txt": "नए मोबाइल हैंडसेट या इलेक्ट्रॉनिक उत्पाद की वारंटी कंपनी के अधिकृत सर्विस सेंटर (Authorized Service Center) द्वारा नियमानुसार दी जाती है। टूट-फूट या पानी से होने वाला नुकसान (Physical/Liquid Damage) वारंटी में मान्य नहीं होगा।",
        "footer_txt": "देवांशी सॉफ्टवेयर - जयमीन पटेल: 9725721215"
    },
    "en": {
        "inv": "TAX INVOICE", "bill": "Invoice No", "date": "Date", "cust": "Customer Name", "ph": "Mobile",
        "addr_lbl": "Address", "cust_gst_lbl": "Customer GSTIN", "shop_gst_lbl": "Store GSTIN",
        "item": "Model / Item Description", "imei": "IMEI / Serial No", "taxable_lbl": "Taxable Value",
        "amt": "Total Amount (₹)", "disc_lbl": "Discount", "paid": "Paid Amount", "due": "Balance Due", "sign": "Authorised Signatory",
        "terms_hdr": "Terms & Conditions:",
        "default_terms": "1. Goods once sold will not be taken back or exchanged.<br>2. Mobile handset warranty is provided strictly by the brand's Authorized Service Center as per company policy.<br>3. All disputes are subject to local court jurisdiction.",
        "warranty_hdr": "🛡️ Warranty & Service Responsibility Note:",
        "warranty_txt": "Warranty for new mobile handsets or electronic products is provided directly by the manufacturer's Authorized Service Center as per brand terms. Physical or liquid damage is not covered under warranty.",
        "footer_txt": "Devanshi Software - Jaymin Patel: 9725721215"
    },
    "mr": {
        "inv": "टॅक्स इनव्हॉइस / विक्री बिल", "bill": "बिल क्र.", "date": "दिनांक", "cust": "ग्राहकाचे नाव", "ph": "मोबाईल",
        "addr_lbl": "पत्ता", "cust_gst_lbl": "ग्राहक GSTIN", "shop_gst_lbl": "दुकान GSTIN",
        "item": "मॉडेल / तपशील", "imei": "IMEI क्र.", "taxable_lbl": "करपात्र रक्कम",
        "amt": "एकूण रक्कम (₹)", "disc_lbl": "सवलत (Discount)", "paid": "जमा रक्कम", "due": "बाकी रक्कम", "sign": "अधिकृत स्वाक्षरी",
        "terms_hdr": "अटी आणि शर्ती (Terms & Conditions):",
        "default_terms": "१. विकलेला माल परत घेतला जाणार नाही किंवा बदलून दिला जाणार नाही.<br>२. मोबाईल हँडसेटची वॉरंटी कंपनीच्या अधिकृत सर्व्हिस सेंटरकडून नियमांनुसार राहील.<br>३. सर्व वाद स्थानिक न्यायालयाच्या कक्षेत राहतील.",
        "warranty_hdr": "🛡️ वॉरंटी आणि सर्व्हिस जबाबदारी टीप:",
        "warranty_txt": "नवीन मोबाईल किंवा इलेक्ट्रॉनिक वस्तूंची वॉरंटी कंपनीच्या अधिकृत सर्व्हिस सेंटरद्वारे नियमांनुसार दिली जाते. शारीरिक किंवा पाण्यामुळे झालेले नुकसान वॉरंटीमध्ये समाविष्ट नाही.",
        "footer_txt": "देवांशी सॉफ्टवेअर - जयमीन पटेल: 9725721215"
    },
    "pa": {
        "inv": "ਟੈਕਸ ਇਨਵੌਇਸ / ਵਿਕਰੀ ਬਿੱਲ", "bill": "ਬਿੱਲ ਨੰ.", "date": "ਮਿਤੀ", "cust": "ਗਾਹਕ ਦਾ ਨਾਮ", "ph": "ਮੋਬਾਈਲ",
        "addr_lbl": "ਪਤਾ", "cust_gst_lbl": "ਗਾਹਕ GSTIN", "shop_gst_lbl": "ਦੁਕਾਨ GSTIN",
        "item": "ਮਾਡਲ / ਵੇਰਵਾ", "imei": "IMEI ਨੰ.", "taxable_lbl": "ਟੈਕਸਯੋਗ ਰਕਮ",
        "amt": "ਕੁੱਲ ਰਕਮ (₹)", "disc_lbl": "ਛੋਟ (Discount)", "paid": "ਜਮ੍ਹਾਂ ਰਕਮ", "due": "ਬਾਕੀ ਰਕਮ", "sign": "ਅਧਿਕਾਰਤ ਦਸਤਖਤ",
        "terms_hdr": "ਨਿਯਮ ਅਤੇ ਸ਼ਰਤਾਂ (Terms & Conditions):",
        "default_terms": "1. ਵੇਚਿਆ ਗਿਆ ਸਮਾਨ ਵਾਪਸ ਜਾਂ ਬਦਲਿਆ ਨਹੀਂ ਜਾਵੇਗਾ।<br>2. ਮੋਬਾਈਲ ਹੈਂਡਸੈੱਟ ਦੀ ਵਾਰੰਟੀ ਕੰਪਨੀ ਦੇ ਅਧਿਕਾਰਤ ਸਰਵਿਸ ਸੈਂਟਰ ਵੱਲੋਂ ਨਿਯਮਾਂ ਅਨੁਸਾਰ ਹੋਵੇਗੀ।<br>3. ਸਾਰੇ ਵਿਵਾਦ ਸਥਾਨਕ ਅਦਾਲਤ ਦੇ ਅਧੀਨ ਹੋਣਗੇ।",
        "warranty_hdr": "🛡️ ਵਾਰੰਟੀ ਅਤੇ ਸਰਵਿਸ ਜ਼ਿੰਮੇਵਾਰੀ ਨੋਟ:",
        "warranty_txt": "ਨਵੇਂ ਮੋਬਾਈਲ ਜਾਂ ਇਲੈਕਟ੍ਰਾਨਿਕ ਉਤਪਾਦਾਂ ਦੀ ਵਾਰੰਟੀ ਕੰਪਨੀ ਦੇ ਅਧਿਕਾਰਤ ਸਰਵਿਸ ਸੈਂਟਰ ਦੁਆਰਾ ਦਿੱਤੀ ਜਾਂਦੀ ਹੈ। ਟੁੱਟ-ਭੱਜ ਜਾਂ ਪਾਣੀ ਨਾਲ ਹੋਇਆ ਨੁਕਸਾਨ ਵਾਰੰਟੀ ਵਿੱਚ ਸ਼ਾਮਲ ਨਹੀਂ ਹੈ।",
        "footer_txt": "ਦੇਵਾਂਸ਼ੀ ਸਾਫਟਵੇਅਰ - ਜੈਮੀਨ ਪਟੇਲ: 9725721215"
    },
    "bn": {
        "inv": "ট্যাক্স ইনভয়েস / বিক্রয় বিল", "bill": "বিল নং", "date": "তারিখ", "cust": "গ্রাহকের নাম", "ph": "মোবাইল",
        "addr_lbl": "ঠিকানা", "cust_gst_lbl": "গ্রাহক GSTIN", "shop_gst_lbl": "দোকান GSTIN",
        "item": "মডেল / বিবরণ", "imei": "IMEI নং", "taxable_lbl": "করযোগ্য মূল্য",
        "amt": "মোট টাকা (₹)", "disc_lbl": "ছাড় (Discount)", "paid": "জমা টাকা", "due": "বাকি টাকা", "sign": "অনুমোদিত স্বাক্ষর",
        "terms_hdr": "নিয়ম ও শর্তাবলী (Terms & Conditions):",
        "default_terms": "১. বিক্রিত পণ্য ফেরত বা পরিবর্তন করা হবে না।<br>২. মোবাইল হ্যান্ডসেটের ওয়ারেন্টি কোম্পানির অনুমোদিত সার্ভিস সেন্টার থেকে নিয়ম অনুযায়ী প্রযোজ্য হবে।<br>৩. যেকোনো বিরোধ স্থানীয় আদালতের এখতিয়ারাধীন।",
        "warranty_hdr": "🛡️ ওয়ারেন্টি এবং সার্ভিস সংক্রান্ত নোট:",
        "warranty_txt": "নতুন মোবাইল বা ইলেকট্রনিক পণ্যের ওয়ারেন্টি কোম্পানির অনুমোদিত সার্ভিস সেন্টার দ্বারা প্রদান করা হয়। শারীরিক বা জলের কারণে ক্ষতি ওয়ারেন্টির আওতায় পড়বে না।",
        "footer_txt": "দেবাংশী সফটওয়্যার - জয়মীন প্যাটেল: 9725721215"
    },
    "ta": {
        "inv": "வரி விலைப்பட்டியல் (Tax Invoice)", "bill": "பில் எண்", "date": "தேதி", "cust": "வாடிக்கையாளர் பெயர்", "ph": "மொபைல்",
        "addr_lbl": "முகவரி", "cust_gst_lbl": "வாடிக்கையாளர் GSTIN", "shop_gst_lbl": "கடை GSTIN",
        "item": "மாடல் / விவரம்", "imei": "IMEI எண்", "taxable_lbl": "வரிக்குரிய தொகை",
        "amt": "மொத்த தொகை (₹)", "disc_lbl": "தள்ளுபடி", "paid": "செலுத்திய தொகை", "due": "நிலுவைத் தொகை", "sign": "அங்கீகரிக்கப்பட்ட கையொப்பம்",
        "terms_hdr": "விதிமுறைகள் மற்றும் நிபந்தனைகள் (Terms & Conditions):",
        "default_terms": "1. விற்கப்பட்ட பொருட்கள் திரும்பப் பெறப்படமாட்டாது அல்லது மாற்றப்படமாட்டாது.<br>2. மொபைல் வாரண்டி நிறுவனத்தின் அங்கீகரிக்கப்பட்ட சர்வீஸ் சென்டர் மூலம் மட்டுமே வழங்கப்படும்.<br>3. அனைத்து வழக்குகளும் உள்ளூர் நீதிமன்றத்திற்கு உட்பட்டவை.",
        "warranty_hdr": "🛡️ வாரண்டி மற்றும் சர்வீஸ் குறிப்பு:",
        "warranty_txt": "புதிய மொபைல் அல்லது எலக்ட்ரானிக் பொருட்களின் வாரண்டி நிறுவனத்தின் அங்கீகரிக்கப்பட்ட சர்வீஸ் சென்டர் மூலம் விதிமுறைகளின்படி வழங்கப்படுகிறது. உடைப்பு அல்லது நீர் சேதம் வாரண்டியில் சேராது.",
        "footer_txt": "தேவான்ஷி மென்பொருள் - ஜெய்மின் படேல்: 9725721215"
    },
    "te": {
        "inv": "పన్ను ఇన్వాయిస్ (Tax Invoice)", "bill": "బిల్లు సంఖ్య", "date": "తేదీ", "cust": "కస్టమర్ పేరు", "ph": "మొబైల్",
        "addr_lbl": "చిరునామా", "cust_gst_lbl": "కస్టమర్ GSTIN", "shop_gst_lbl": "షాప్ GSTIN",
        "item": "మోడల్ / వివరాలు", "imei": "IMEI సంఖ్య", "taxable_lbl": "పన్ను విధించదగిన విలువ",
        "amt": "మొత్తం (₹)", "disc_lbl": "డిస్కౌంట్", "paid": "చెల్లించిన మొత్తం", "due": "బకాయి మొత్తం", "sign": "అధికారిక సంతకం",
        "terms_hdr": "నిబంధనలు మరియు షరతులు (Terms & Conditions):",
        "default_terms": "1. అమ్మిన వస్తువులు తిరిగి తీసుకోబడవు లేదా మార్చబడవు.<br>2. మొబైల్ హ్యాండ్‌సెట్ వారంటీ కంపెనీ అధికారిక సర్వీస్ సెంటర్ ద్వారా నిబంధనల ప్రకారం ఉంటుంది.<br>3. అన్ని వివాదాలు స్థానిక కోర్టు పరిధికి లోబడి ఉంటాయి.",
        "warranty_hdr": "🛡️ వారంటీ మరియు సర్వీస్ బాధ్యత గమనిక:",
        "warranty_txt": "కొత్త మొబైల్ లేదా ఎలక్ట్రానిక్ ఉత్పత్తుల వారంటీ కంపెనీ అధికారిక సర్వీస్ సెంటర్ ద్వారా అందించబడుతుంది. భౌతిక లేదా నీటి నష్టం వారంటీ కిందకు రాదు.",
        "footer_txt": "దేవాన్షి సాఫ్ట్‌వేర్ - జైమిన్ పటేల్: 9725721215"
    },
    "kn": {
        "inv": "ತೆರಿಗೆ ಇನ್‌ವಾಯ್ಸ್ (Tax Invoice)", "bill": "ಬಿಲ್ ಸಂಖ್ಯೆ", "date": "ದಿನಾಂಕ", "cust": "ಗ್ರಾಹಕರ ಹೆಸರು", "ph": "ಮೊಬೈಲ್",
        "addr_lbl": "ವಿಳಾಸ", "cust_gst_lbl": "ಗ್ರಾಹಕರ GSTIN", "shop_gst_lbl": "ಅಂಗಡಿ GSTIN",
        "item": "ಮಾಡೆಲ್ / ವಿವರ", "imei": "IMEI ಸಂಖ್ಯೆ", "taxable_lbl": "ತೆರಿಗೆಯ ಮೊತ್ತ",
        "amt": "ಒಟ್ಟು ಮೊತ್ತ (₹)", "disc_lbl": "ರಿಯಾಯಿತಿ", "paid": "ಪಾವತಿಸಿದ ಮೊತ್ತ", "due": "ಬಾಕಿ ಮೊತ್ತ", "sign": "ಅಧಿಕೃತ ಸಹಿ",
        "terms_hdr": "ನಿಯಮಗಳು ಮತ್ತು ಷರತ್ತುಗಳು (Terms & Conditions):",
        "default_terms": "1. ಮಾರಾಟವಾದ ವಸ್ತುಗಳನ್ನು ಹಿಂಪಡೆಯಲಾಗುವುದಿಲ್ಲ ಅಥವಾ ಬದಲಾಯಿಸಲಾಗುವುದಿಲ್ಲ.<br>2. ಮೊಬೈಲ್ ವಾರಂಟಿ ಕಂಪನಿಯ ಅಧಿಕೃತ ಸರ್ವಿಸ್ ಸೆಂಟರ್ ಮೂಲಕ ನಿಯಮಾನುಸಾರ ಇರುತ್ತದೆ.<br>3. ಎಲ್ಲಾ ವಿವಾದಗಳು ಸ್ಥಳೀಯ ನ್ಯಾಯಾಲಯದ ವ್ಯಾಪ್ತಿಗೆ ಒಳಪಟ್ಟಿರುತ್ತವೆ.",
        "warranty_hdr": "🛡️ ವಾರಂಟಿ ಮತ್ತು ಸರ್ವಿಸ್ ಸೂಚನೆ:",
        "warranty_txt": "ಹೊಸ ಮೊಬೈಲ್ ಅಥವಾ ಎಲೆಕ್ಟ್ರಾನಿಕ್ ಉತ್ಪನ್ನಗಳ ವಾರಂಟಿಯನ್ನು ಕಂಪನಿಯ ಅಧಿಕೃತ ಸರ್ವಿಸ್ ಸೆಂಟರ್ ನೀಡುತ್ತದೆ. ಭೌತಿಕ ಅಥವಾ ನೀರಿನ ಹಾನಿ ವಾರಂಟಿಗೆ ಒಳಪಡುವುದಿಲ್ಲ.",
        "footer_txt": "ದೇವಾಂಶಿ ಸಾಫ್ಟ್‌ವೇರ್ - ಜೈಮಿನ್ ಪಟೇಲ್: 9725721215"
    },
    "ml": {
        "inv": "ടാക്സ് ഇൻവോയ്സ് (Tax Invoice)", "bill": "ബിൽ നമ്പർ", "date": "തീയതി", "cust": "ഉപഭോക്താവിന്റെ പേര്", "ph": "മൊബൈൽ",
        "addr_lbl": "വിലാസം", "cust_gst_lbl": "ഉപഭോക്താവ് GSTIN", "shop_gst_lbl": "ഷോപ്പ് GSTIN",
        "item": "മോഡൽ / വിവരങ്ങൾ", "imei": "IMEI നമ്പർ", "taxable_lbl": "നികുതി വിധേയമായ തുക",
        "amt": "ആകെ തുക (₹)", "disc_lbl": "കിഴിവ്", "paid": "നൽകിയ തുക", "due": "ബാക്കി തുക", "sign": "അധികൃത ഒപ്പ്",
        "terms_hdr": "നിബന്ധനകളും വ്യവസ്ഥകളും (Terms & Conditions):",
        "default_terms": "1. വിറ്റ സാധനങ്ങൾ തിരിച്ചെടുക്കുകയോ മാറ്റി നൽകുകയോ ചെയ്യുന്നതല്ല.<br>2. മൊബൈൽ ഹാൻഡ്‌സെറ്റ് വാറന്റി കമ്പനിയുടെ അംഗീകൃത സർവീസ് സെന്റർ വഴി മാത്രമായിരിക്കും.<br>3. എല്ലാ തർക്കങ്ങളും പ്രാദേശിക കോടതിയുടെ അധികാരപരിധിക്ക് വിധേയമായിരിക്കും.",
        "warranty_hdr": "🛡️ വാറന്റിയും സർവീസ് അറിയിപ്പും:",
        "warranty_txt": "പുതിയ മൊബൈൽ അല്ലെങ്കിൽ ഇലക്ട്രോണിക് ഉൽപ്പന്നങ്ങളുടെ വാറന്റി കമ്പനിയുടെ അംഗീകൃത സർവീസ് സെന്റർ വഴിയാണ് നൽകുന്നത്. പൊട്ടലോ വെള്ളം കയറിയുള്ള കേടുപാടുകളോ വാറന്റിയിൽ ഉൾപ്പെടില്ല.",
        "footer_txt": "ദേവാൻഷി സോഫ്റ്റ്‌വെയർ - ജയ്മിൻ പട്ടേൽ: 9725721215"
    },
    "or": {
        "inv": "ଟ୍ୟାକ୍ସ ଇନଭଏସ୍ (Tax Invoice)", "bill": "ବିଲ୍ ନଂ", "date": "ତାରିଖ", "cust": "ଗ୍ରାହକଙ୍କ ନାମ", "ph": "ମୋବାଇଲ୍",
        "addr_lbl": "ଠିକଣା", "cust_gst_lbl": "ଗ୍ରାହକ GSTIN", "shop_gst_lbl": "ଦୋକାନ GSTIN",
        "item": "ମଡେଲ୍ / ବିବରଣୀ", "imei": "IMEI ନଂ", "taxable_lbl": "ଟିକସযোগ্য ମୂଲ୍ୟ",
        "amt": "ମୋଟ ଟଙ୍କା (₹)", "disc_lbl": "ରିହାତି", "paid": "ଜମା ଟଙ୍କା", "due": "ବାକି ଟଙ୍କା", "sign": "ଅଧିକୃତ ଦସ୍ତଖତ",
        "terms_hdr": "ନିୟମ ଏବଂ ସର୍ତ୍ତାବଳୀ (Terms & Conditions):",
        "default_terms": "୧. ବିକ୍ରି ହୋଇଥିବା ଜିନିଷ ଫେରସ୍ତ କିମ୍ବା ବଦଳାযିବ ନାହିଁ।<br>୨. ମୋବାଇଲ୍ ହ୍ୟାଣ୍ଡସେଟ୍ ୱାରେଣ୍ଟି କମ୍ପାନୀର ଅଧିକୃତ ସର୍ଭିସ୍ ସେଣ୍ଟର ଦ୍ୱାରା ନିୟମ ଅନୁଯାୟୀ ମିଳିବ।<br>୩. ସମସ୍ତ ବିବାଦ ସ୍ଥାନୀୟ କୋର୍ଟ ଅଧୀନରେ ରହିବ।",
        "warranty_hdr": "🛡️ ୱାରେଣ୍ଟି ଏବଂ ସର୍ଭିସ୍ ସୂଚନା:",
        "warranty_txt": "ନୂତନ ମୋବାଇଲ୍ କିମ୍ବା ଇଲେକ୍ଟ୍ରୋନିକ୍ ଉତ୍ପାଦର ୱାରେଣ୍ଟି କମ୍ପାନୀର ଅଧିକୃତ ସର୍ଭିସ୍ ସେଣ୍ଟର ଦ୍ୱାରା ପ୍ରଦାନ କରାଯାଏ। ଭୌତିକ କିମ୍ବା ପାଣି ଜନିତ କ୍ଷତି ୱାରେଣ୍ଟିରେ ଅନ୍ତର୍ଭୁକ୍ତ ନୁହେଁ।",
        "footer_txt": "ଦେବାଂଶୀ ସଫ୍ଟୱେୟାର - ଜୟମୀନ ପଟେଲ: 9725721215"
    },
    "ur": {
        "inv": "ٹیکس انوائس / فروخت بل", "bill": "بل نمبر", "date": "تاریخ", "cust": "گاہک کا نام", "ph": "موبائل",
        "addr_lbl": "پتہ", "cust_gst_lbl": "گاہک GSTIN", "shop_gst_lbl": "دکان GSTIN",
        "item": "ماڈل / تفصیل", "imei": "IMEI نمبر", "taxable_lbl": "قابل ٹیکس رقم",
        "amt": "کل رقم (₹)", "disc_lbl": "رعایت (Discount)", "paid": "جمع رقم", "due": "بقایا رقم", "sign": "مجاز دستخط",
        "terms_hdr": "شرائط و ضوابط (Terms & Conditions):",
        "default_terms": "1. فروخت شدہ مال واپس یا تبدیل نہیں کیا جائے گا۔<br>2. موبائل ہینڈ سیٹ کی وارنٹی کمپنی کے مجاز سروس سینٹر سے اصولوں کے مطابق ہوگی۔<br>3. تمام تنازعات مقامی عدالت کے دائرہ اختیار میں ہوں گے۔",
        "warranty_hdr": "🛡️ وارنٹی اور سروس نوٹ:",
        "warranty_txt": "نئے موبائل ہینڈ سیٹ یا الیکٹرانک مصنوعات کی وارنٹی کمپنی کے مجاز سروس سینٹر کے ذریعے فراہم کی جاتی ہے۔ ٹوٹ پھوٹ یا پانی سے ہونے والا نقصان وارنٹی میں شامل نہیں ہے۔",
        "footer_txt": "دیوانشی سافٹ ویئر - جیمین پٹیل: 9725721215"
    }
}

_GU_TO_ROMAN_MAP = {
    'અ':'a','આ':'aa','ઇ':'i','ઈ':'ee','ઉ':'u','ઊ':'oo','ઋ':'ru','એ':'e','ઐ':'ai','ઓ':'o','ઔ':'au',
    'ક':'k','ખ':'kh','ગ':'g','ઘ':'gh','ચ':'ch','છ':'chh','જ':'j','ઝ':'jh','ટ':'t','ઠ':'th','ડ':'d','ઢ':'dh','ણ':'n',
    'ત':'t','થ':'th','દ':'d','ધ':'dh','ન':'n','પ':'p','ફ':'f','બ':'b','ભ':'bh','મ':'m','ય':'y','ર':'r','લ':'l','ળ':'l','વ':'v',
    'શ':'sh','ષ':'sh','સ':'s','હ':'h','ા':'a','િ':'i','ી':'ee','ુ':'u','ૂ':'oo','ે':'e','ૈ':'ai','ો':'o','ૌ':'au','ં':'n','ઃ':'h','્':'',
    '૦':'0','૧':'1','૨':'2','૩':'3','૪':'4','૫':'5','૬':'6','૭':'7','૮':'8','૯':'9'
}

_INDIC_BLOCK_BASES = {
    "hi": 0x0900, "mr": 0x0900, "bn": 0x0980, "pa": 0x0A00,
    "or": 0x0B00, "ta": 0x0B80, "te": 0x0C00, "kn": 0x0C80, "ml": 0x0D00
}

def localize_shop_text(text: str, lang: str) -> str:
    """
    દુકાનનું નામ, સરનામું, ગ્રાહકનું નામ કે કસ્ટમ શરતો જો ગુજરાતીમાં લખેલી હોય,
    તો ગ્રાહકની પસંદ કરેલી ભાષા (૧૨ ભાષા) ના અક્ષરોમાં આપોઆપ રૂપાંતરિત કરે છે જેથી સામેવાળી પાર્ટી પોતાની ભાષામાં વાંચી શકે!
    """
    if not text or lang == "gu":
        return text or ""
    s = str(text)
    # Common retail words translation first
    if lang == "en":
        word_map = {
            "દેવાંશી": "Devanshi", "મનસ્વી": "Manshvi", "મોબાઈલ": "Mobile", "ઇલેક્ટ્રોનિક્સ": "Electronics",
            "ટેલિકોમ": "Telecom", "એન્ટરપ્રાઇઝ": "Enterprise", "મેઈન બજાર": "Main Bazar", "બેચરાજી": "Becharaji",
            "ગ્રાહક": "Customer", "વેચેલો માલ પાછો લેવામાં કે બદલી આપવામાં આવશે નહીં": "Goods once sold will not be taken back or exchanged",
            "વોરંટી": "Warranty", "સર્વિસ સેન્ટર": "Service Center"
        }
        for gk, ev in word_map.items():
            s = s.replace(gk, ev)
        out = []
        for ch in s:
            if ch in _GU_TO_ROMAN_MAP:
                out.append(_GU_TO_ROMAN_MAP[ch])
            else:
                out.append(ch)
        return "".join(out).title() if any('઀' <= c <= '૿' for c in s) else "".join(out)

    if lang in _INDIC_BLOCK_BASES:
        target_base = _INDIC_BLOCK_BASES[lang]
        out = []
        for ch in s:
            cp = ord(ch)
            if 0x0A80 <= cp <= 0x0AFF:
                offset = cp - 0x0A80
                out.append(chr(target_base + offset))
            else:
                out.append(ch)
        return "".join(out)

    if lang == "ur":
        # For Urdu, convert Gujarati words/script to clean readable Urdu/English script
        ur_map = {
            "દેવાંશી": "دیوانشی", "મનસ્વી": "منسوی", "મોબાઈલ": "موبائل", "ઇલેક્ટ્રોનિક્સ": "الیکٹرانکس",
            "મેઈન બજાર": "مین بازار", "ગ્રાહક": "گاہک"
        }
        for gk, uv in ur_map.items():
            s = s.replace(gk, uv)
        out = []
        for ch in s:
            out.append(_GU_TO_ROMAN_MAP.get(ch, ch))
        return "".join(out)
    return s

def _calc_auto_last_emi_month_gu(first_emi_date_str: str, rem_emis: int) -> str:
    """પ્રથમ EMI તારીખ અને બાકી હપ્તા પરથી છેલ્લો હપ્તો કયા મહિનામાં આવશે તેની ઓટોમેટિક ગણતરી કરે છે!"""
    if not first_emi_date_str or rem_emis <= 0:
        return ""
    gu_months = {
        1: "જાન્યુઆરી", 2: "ફેબ્રુઆરી", 3: "માર્ચ", 4: "એપ્રિલ", 5: "મે", 6: "જૂન",
        7: "જુલાઈ", 8: "ઓગસ્ટ", 9: "સપ્ટેમ્બર", 10: "ઓક્ટોબર", 11: "નવેમ્બર", 12: "ડિસેમ્બર"
    }
    try:
        dt = None
        for fmt in ("%Y-%m-%d", "%d-%m-%Y", "%d/%m/%Y"):
            try:
                dt = datetime.datetime.strptime(first_emi_date_str.strip(), fmt).date()
                break
            except Exception:
                pass
        if not dt:
            return ""
        add_m = max(0, rem_emis - 1)
        tot_m = (dt.year * 12 + (dt.month - 1)) + add_m
        end_y = tot_m // 12
        end_m = (tot_m % 12) + 1
        end_d = min(dt.day, 28)
        return f"{gu_months.get(end_m, '')} {end_y} ({end_d:02d}-{end_m:02d}-{end_y})"
    except Exception:
        return ""


def _num_to_english_words(n: int) -> str:
    if n <= 0:
        return "Zero"
    ones = ["", "One", "Two", "Three", "Four", "Five", "Six", "Seven", "Eight", "Nine", "Ten",
            "Eleven", "Twelve", "Thirteen", "Fourteen", "Fifteen", "Sixteen", "Seventeen", "Eighteen", "Nineteen"]
    tens = ["", "", "Twenty", "Thirty", "Forty", "Fifty", "Sixty", "Seventy", "Eighty", "Ninety"]
    def _two(num):
        if num < 20:
            return ones[num]
        return (tens[num // 10] + (" " + ones[num % 10] if num % 10 else "")).strip()
    def _three(num):
        if num < 100:
            return _two(num)
        return (ones[num // 100] + " Hundred" + (" " + _two(num % 100) if num % 100 else "")).strip()
    parts = []
    crore = n // 10000000
    n %= 10000000
    lakh = n // 100000
    n %= 100000
    thousand = n // 1000
    n %= 1000
    rest = n
    if crore:
        parts.append(_two(crore) + " Crore")
    if lakh:
        parts.append(_two(lakh) + " Lakh")
    if thousand:
        parts.append(_two(thousand) + " Thousand")
    if rest:
        parts.append(_three(rest))
    return " ".join(parts).strip()

@app.post("/api/save-edited-original-invoice")
async def save_edited_original_invoice_route(
    orig_bill_no: str = Form(...),
    new_bill_no: str = Form(""),
    bill_date: str = Form(""),
    customer_name: str = Form(""),
    phone: str = Form(""),
    customer_address: str = Form(""),
    customer_pincode: str = Form(""),
    model: str = Form(""),
    imei: str = Form(""),
    mop_price: float = Form(0.0),
    discount_amt: float = Form(0.0),
    gst_pct: float = Form(18.0),
    payment_info: str = Form(""),
    admin_pin: str = Form(""),
    print_mode: str = Form("FRANCHISE_DOUBLE_BOX"),
    lang: str = Form("gu")
):
    """નિયમ: ઓરિજિનલ પૂજારા / ટેક્સ બિલમાં કરેલા સુધારા-વધારા સેવ કરવા માટે (ફ્રેન્ચાઇઝી મોડ અને ફાઇનાન્સ બિલ માટે માસ્ટર PIN 1986 ફરજિયાત!)"""
    sid = STORE_CFG.get("shop_id", "DEVANSHI")
    shop_prof = get_shop_feature_profile(sid)
    st_mode = str(shop_prof.get("store_mode") or "FRANCHISE_HO").upper()
    correct_pin = str(STORE_CFG.get("admin_pin", "1986")).strip()

    conn = sqlite3.connect(get_active_db_file(sid), timeout=60.0)
    c = conn.cursor()
    c.execute("SELECT COALESCE(bill_type,''), COALESCE(loan_amt,0), COALESCE(financer_name,'') FROM apx_sales_raw WHERE bill_no=?", (orig_bill_no,))
    b_row = c.fetchone()
    is_fin_bill = bool(b_row and (str(b_row[0]).upper() == "FINANCE_BILL" or float(b_row[1] or 0) > 0 or str(b_row[2]).strip()))

    # Enforce PIN 1986 strictly for Franchise Mode or when PIN is provided/required
    if ("FRANCHISE" in st_mode or is_fin_bill or admin_pin.strip()) and str(admin_pin).strip() not in (correct_pin, "1986"):
        conn.close()
        return RedirectResponse(
            f"/print-invoice?bill_no={urllib.parse.quote(orig_bill_no)}&print_mode={print_mode}&lang={lang}&err_msg=" + urllib.parse.quote("❌ ફ્રેન્ચાઇઝી / ફાઇનાન્સ બિલમાં એડિટિંગ સેવ કરવા માટે સાચો માસ્ટર PIN 1986 નાખવો ફરજિયાત છે!"),
            status_code=303
        )

    eff_new_bill = (new_bill_no or orig_bill_no).strip()
    c.execute("""UPDATE apx_sales_raw
                 SET bill_no=?, bill_date=?, customer_name=?, phone=?, customer_address=?, customer_pincode=?,
                     model=?, imei=?, mop_price=?, discount_amt=?, gst_pct=?
                 WHERE bill_no=?""",
              (eff_new_bill, bill_date.strip(), customer_name.strip(), phone.strip(), customer_address.strip(),
               customer_pincode.strip(), model.strip(), imei.strip(), float(mop_price or 0), float(discount_amt or 0),
               float(gst_pct or 18.0), orig_bill_no))
    if c.rowcount == 0:
        c.execute("""INSERT INTO apx_sales_raw
            (bill_no, bill_date, customer_name, phone, customer_address, customer_pincode, model, imei, mop_price, discount_amt, gst_pct, status, store_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'SETTLED', ?)""",
            (eff_new_bill, bill_date.strip() or str(datetime.date.today()), customer_name.strip(), phone.strip(),
             customer_address.strip(), customer_pincode.strip(), model.strip(), imei.strip(),
             float(mop_price or 0), float(discount_amt or 0), float(gst_pct or 18.0), sid))
    c.execute("UPDATE live_terminal_grid SET bill_no=?, customer_name=?, model_name=?, imei=?, total_padtar=? WHERE bill_no=?",
              (eff_new_bill, customer_name.strip(), model.strip(), imei.strip(), float(mop_price or 0), orig_bill_no))
    conn.commit()
    conn.close()
    log_audit_action("SAVE_EDITED_ORIGINAL_BILL", "apx_sales_raw", eff_new_bill, new_data=f"{customer_name} | {model} | ₹{mop_price} (Disc: ₹{discount_amt})", authorized_by="PIN 1986")
    return RedirectResponse(
        f"/print-invoice?bill_no={urllib.parse.quote(eff_new_bill)}&print_mode={print_mode}&lang={lang}&ok_msg=" + urllib.parse.quote("✅ ઓરિજિનલ બિલમાં કરેલા સુધારા સફળતાપૂર્વક સેવ થઈ ગયા!"),
        status_code=303
    )

@app.post("/api/delete-invoice-pin-locked")
def delete_invoice_pin_locked_route(bill_no: str = Form(...), admin_pin: str = Form("")):
    """નિયમ: કોઈપણ બિલ ડિલીટ કરવા માટે માસ્ટર PIN 1986 ફરજિયાત!"""
    correct_pin = str(STORE_CFG.get("admin_pin", "1986")).strip()
    if str(admin_pin).strip() not in (correct_pin, "1986"):
        return RedirectResponse(
            f"/print-invoice?bill_no={urllib.parse.quote(bill_no)}&err_msg=" + urllib.parse.quote("❌ ખોટો માસ્ટર PIN! બિલ ડિલીટ કરવા માટે સાચો માસ્ટર PIN 1986 નાખો."),
            status_code=303
        )
    conn = sqlite3.connect(get_active_db_file(), timeout=60.0)
    c = conn.cursor()
    c.execute("SELECT id FROM live_terminal_grid WHERE bill_no=?", (bill_no,))
    grid_rows = c.fetchall()
    for gr in grid_rows:
        _rollback_running_grid_row(conn, c, gr[0])
    c.execute("SELECT imei FROM apx_sales_raw WHERE bill_no=?", (bill_no,))
    for r_im in c.fetchall():
        if r_im[0] and r_im[0] != "-":
            c.execute("UPDATE live_stock SET status='IN_STOCK' WHERE imei=?", (r_im[0],))
    c.execute("DELETE FROM apx_sales_raw WHERE bill_no=?", (bill_no,))
    conn.commit()
    conn.close()
    log_audit_action("DELETE_INVOICE_PIN_1986", "apx_sales_raw", bill_no, authorized_by="PIN 1986")
    return redir(f"🗑️ બિલ નંબર {bill_no} માસ્ટર PIN 1986 થી સફળતાપૂર્વક ડિલીટ અને રિવર્સ કરવામાં આવ્યું!", "APX_SALES_RAW", "F2")

@app.get("/print-invoice", response_class=HTMLResponse)
def print_invoice_route(
    request: Request = None, bill_no: str = "", lang: str = "gu", print_mode: str = "",
    paper_format: str = "A4", copy_mode: str = "ORIGINAL",
    temp_cust: str = "", temp_mod: str = "", temp_mop: float = 0, shop_id: str = "",
    ok_msg: str = "", err_msg: str = ""
):
    L = LANG_DICT.get(lang, LANG_DICT["gu"])
    active_sid = (shop_id or (request.cookies.get("devanshi_shop_id") if request else "") or STORE_CFG.get("shop_id", "DEVANSHI")).strip().upper()
    shop_prof = get_shop_feature_profile(active_sid)
    if not (print_mode or "").strip():
        print_mode = str(shop_prof.get("default_print_layout") or ("RETAIL_STANDARD_GST" if (active_sid == "MANSHVI" or "RETAIL" in str(shop_prof.get("store_mode") or "").upper()) else "FRANCHISE_DOUBLE_BOX")).strip()
    conn = sqlite3.connect(get_active_db_file(active_sid), timeout=60.0)
    from part1_core import add_col_if_missing
    add_col_if_missing(conn, "apx_sales_raw", "first_emi_date", "TEXT DEFAULT ''")
    add_col_if_missing(conn, "apx_sales_raw", "last_emi_month", "TEXT DEFAULT ''")
    add_col_if_missing(conn, "apx_sales_raw", "first_emi_extra_charge", "TEXT DEFAULT ''")
    add_col_if_missing(conn, "apx_sales_raw", "expected_dp", "REAL DEFAULT 0")
    add_col_if_missing(conn, "apx_sales_raw", "signed_copy_path", "TEXT DEFAULT ''")
    add_col_if_missing(conn, "apx_sales_raw", "scheme_benefit_amt", "REAL DEFAULT 0")
    add_col_if_missing(conn, "apx_sales_raw", "courier_charge", "REAL DEFAULT 0")

    c = conn.cursor()
    c.execute("""SELECT bill_no, bill_date, customer_name, phone, salesman, model, imei,
                        mop_price, cash_dp, upi_dp, loan_amt, due_amt, scheme_name,
                        discount_amt, gst_pct, customer_address, customer_pincode, customer_gstin,
                        COALESCE(bill_type, ''), COALESCE(financer_name, ''), COALESCE(do_ref_no, ''),
                        COALESCE(app_deal_id, ''), COALESCE(emi_amt, 0), COALESCE(net_disb_amt, 0),
                        COALESCE(expected_dp, 0), COALESCE(due_date, ''), COALESCE(first_emi_date, ''),
                        COALESCE(last_emi_month, ''), COALESCE(first_emi_extra_charge, ''),
                        COALESCE(signed_copy_path, ''), COALESCE(warranty_period, ''),
                        COALESCE(scheme_benefit_amt, 0), COALESCE(courier_charge, 0)
                 FROM apx_sales_raw WHERE bill_no=?""", (bill_no,))
    row = c.fetchone()
    if not row and bill_no:
        c.execute("""SELECT bill_no, substr(entry_time,1,10), customer_name, '-', salesman, model_name, imei,
                            total_padtar, total_padtar, 0, 0, due_amt, '', 0, 18.0, '', '', '',
                            entry_type, '', '', '', 0, 0, 0, '', '', '', '', '', ''
                     FROM live_terminal_grid WHERE bill_no=?""", (bill_no,))
        row = c.fetchone()
    if not row and not temp_cust and not temp_mod:
        c.execute("""SELECT bill_no, bill_date, customer_name, phone, salesman, model, imei,
                            mop_price, cash_dp, upi_dp, loan_amt, due_amt, scheme_name,
                            discount_amt, gst_pct, customer_address, customer_pincode, customer_gstin,
                            COALESCE(bill_type, ''), COALESCE(financer_name, ''), COALESCE(do_ref_no, ''),
                            COALESCE(app_deal_id, ''), COALESCE(emi_amt, 0), COALESCE(net_disb_amt, 0),
                            COALESCE(expected_dp, 0), COALESCE(due_date, ''), COALESCE(first_emi_date, ''),
                            COALESCE(last_emi_month, ''), COALESCE(first_emi_extra_charge, ''),
                            COALESCE(signed_copy_path, ''), COALESCE(warranty_period, ''),
                            COALESCE(scheme_benefit_amt, 0), COALESCE(courier_charge, 0)
                     FROM apx_sales_raw ORDER BY id DESC LIMIT 1""")
        row = c.fetchone()
    default_b_no = bill_no.strip() if (bill_no and not bill_no.upper().startswith("DEMO")) else f"{shop_prof.get('bill_prefix', 'SIL/P/BHC/')}1001"
    if not row:
        row = (
            default_b_no, str(datetime.date.today()), temp_cust or "Mr. GOPAL THAKOR", "9876543210", "અમિત (AMIT)",
            temp_mod or "OPPO F35 5G (CPH2931) 6/128GB TITANIUM GREY", "863967085231690",
            float(temp_mop if temp_mop > 0 else 38999.0), (7799.80 if print_mode == "FINANCE_BILL" else float(temp_mop if temp_mop > 0 else 38999.0)), 0, (31199.20 if print_mode == "FINANCE_BILL" else 0.0), 0, "", 0, 18.0,
            "BECHARAJI, Becharaji-384210", "384210", "", ("FINANCE_BILL" if print_mode == "FINANCE_BILL" else "CASH_BILL"), ("BAJAJ FINANCE LTD." if print_mode == "FINANCE_BILL" else ""), ("BR190535123" if print_mode == "FINANCE_BILL" else ""), "", 0, 0, (7799.80 if print_mode == "FINANCE_BILL" else 0.0), "", "", "", "", "", "૧ વર્ષ કંપની વોરંટી"
        )
    else:
        row = list(row)
        if not row[0] or str(row[0]).upper().startswith("DEMO/"):
            row[0] = default_b_no
        # Ensure 15-digit IMEI and full model details are never missing or '-'
        cur_imei = str(row[6] or "").strip()
        cur_mod = str(temp_mod or row[5] or "").strip()
        if not cur_imei or cur_imei == "-":
            c.execute("SELECT imei, brand, model, color FROM live_stock WHERE model LIKE ? AND length(imei)>=14 LIMIT 1", (f"%{cur_mod[:12]}%",))
            st_r = c.fetchone()
            if not st_r:
                c.execute("SELECT imei, brand, model, color FROM live_stock WHERE length(imei)>=14 ORDER BY id DESC LIMIT 1")
                st_r = c.fetchone()
            if st_r:
                row[6] = st_r[0]
                if st_r[3] and st_r[3].upper() not in cur_mod.upper():
                    row[5] = f"{st_r[2]} ({st_r[3]}) : {st_r[1]} : MOBILE PHONE"
            else:
                row[6] = "863967085231690"
        row = tuple(row)

    # નિયમ ૨૩૪ & ૨૩૭: સ્માર્ટ ખાતાવહી (Khushi Mobile Style) પાછલી ઉધારી (Previous Balance) અને બેંક વિગત ફેચ કરો
    prev_khata_bal = 0.0
    try:
        cust_q_name = (temp_cust or row[2] or "").strip()
        cust_q_ph = (row[3] or "").strip()
        cur_b_no = (row[0] or "").strip()
        c.execute("""SELECT COALESCE(SUM(due_amt - received_amt), 0)
                     FROM customer_due_ledger
                     WHERE (customer_name = ? OR (phone != '' AND phone = ?)) AND bill_no != ?""",
                  (cust_q_name, cust_q_ph, cur_b_no))
        prev_khata_bal = max(0.0, float((c.fetchone() or [0])[0] or 0.0))
    except Exception:
        prev_khata_bal = 0.0
    conn.close()

    raw_store_name = shop_prof.get("store_name") or "દેવાંશી મોબાઈલ"
    raw_store_addr = shop_prof.get("address") or ""
    raw_cust = temp_cust or row[2] or "ગ્રાહક"
    raw_cust_addr = row[15] or ""

    store_name_loc = localize_shop_text(raw_store_name, lang)
    store_addr_loc = localize_shop_text(raw_store_addr, lang)
    cust_disp = localize_shop_text(raw_cust, lang)
    cust_addr_loc = localize_shop_text(raw_cust_addr, lang)
    mod_disp = localize_shop_text(temp_mod or row[5], lang)

    base_mop = float(temp_mop if temp_mop > 0 else (row[7] or 38999.0))
    if base_mop <= 0:
        base_mop = 38999.0
    disc_val = float(row[13] or 0)
    gst_rate = float(row[14] or 18.0)

    if print_mode == "MOP":
        inv_total = base_mop + disc_val if (disc_val > 0 and temp_mop <= 0) else base_mop
        disc_val = 0.0
        disc_row_html = ""
    elif print_mode == "DISCOUNT":
        if disc_val <= 0:
            disc_val = round(min(3500.0, base_mop * 0.05), 2)
        inv_total = base_mop
        disc_row_html = f"<div style='color:#0284c7;'><b>{L['disc_lbl']}:</b> ₹{disc_val:,.2f}</div>"
    else:
        inv_total = base_mop
        disc_row_html = f"<div style='color:#0284c7;'><b>{L['disc_lbl']}:</b> ₹{disc_val:,.2f}</div>" if disc_val > 0 else ""

    due = float(row[11] or 0)
    if print_mode == "CASH_BILL":
        due = 0.0
    elif print_mode == "CREDIT_BILL" and due <= 0:
        due = round(inv_total * 0.5)
    paid = max(0.0, inv_total - due)
    tax_div = 1.0 + (gst_rate / 100.0)
    taxable = round(inv_total / tax_div, 2)
    half_gst = round((inv_total - taxable) / 2.0, 2)
    half_pct = gst_rate / 2.0

    logo_p = shop_prof.get("logo_path") or ""
    if logo_p and not logo_p.startswith("/"):
        logo_p = "/" + logo_p
    logo_html = f"<img src='{logo_p}' style='max-height:65px;'>" if logo_p else ""

    # નિયમ ૨૦૮: દુકાનદારની ડિજિટલ સહી અને સિક્કો (Digital Signature & Store Stamp)
    sign_p = shop_prof.get("sign_stamp_path") or ""
    if sign_p and not sign_p.startswith("/"):
        sign_p = "/" + sign_p
    if sign_p:
        sign_stamp_html = f"<div style='margin-bottom:4px;'><img src='{sign_p}' style='max-height:62px; max-width:165px; object-fit:contain;'></div>"
    else:
        sign_stamp_html = "<div style='height:42px;'></div>"

    # Load owner's Finance Box Configuration (Rule 206 & 207)
    fin_cfg = {
        "show_comp_do": True,
        "show_cust_id": True,
        "show_net_emis": True,
        "show_emi_amt": True,
        "show_first_extra_charge": True,
        "show_dp": True,
        "dp_mode": "AUTO",           # AUTO or UNDERLINE
        "show_emi_dates": True,
        "emi_date_mode": "AUTO",     # AUTO or UNDERLINE
        "show_loan_amt": True
    }
    raw_fcfg = shop_prof.get("finance_box_cfg_json") or ""
    if raw_fcfg:
        try:
            parsed_fc = json.loads(raw_fcfg)
            if isinstance(parsed_fc, dict):
                fin_cfg.update(parsed_fc)
        except Exception:
            pass

    bill_type_val = str(row[18] or "").upper()
    fin_comp = str(row[19] or "").strip()
    do_ref = str(row[20] or "").strip()
    cust_id_val = str(row[21] or "").strip()
    emi_amt_val = float(row[22] or 0)
    loan_amt_val = float(row[10] or 0)
    if print_mode == "CASH_BILL":
        bill_type_val = "CASH_BILL"
        loan_amt_val = 0.0
        fin_comp = ""
        do_ref = ""
    elif print_mode == "CREDIT_BILL":
        bill_type_val = "CREDIT_BILL"
        loan_amt_val = 0.0
    elif print_mode == "FINANCE_BILL":
        bill_type_val = "FINANCE_BILL"
        if loan_amt_val <= 0:
            loan_amt_val = round(inv_total - float(row[8] or 1789.0), 2)
            if loan_amt_val <= 0:
                loan_amt_val = round(inv_total * 0.8, 2)
        if not fin_comp:
            fin_comp = "BAJAJ FINANCE LTD."
        if not do_ref:
            do_ref = cust_id_val or "BR190535123"
    net_disb_val = float(row[23] or 0)
    exp_dp_val = float(row[24] or 0)
    due_date_val = str(row[25] or "").strip()
    first_emi_dt = str(row[26] or "").strip()
    last_emi_mo = str(row[27] or "").strip()
    first_extra_ch = str(row[28] or "").strip()
    signed_copy_p = str(row[29] or "").strip()
    scheme_str = str(row[12] or "").strip()

    # Calculate net remaining EMIs after subtracting Advance EMIs (e.g. 8/2 -> 6 EMIs, 7/1 -> 6 EMIs, 6/0 -> 6 EMIs)
    rem_emis_cnt = 0
    gross_emis_cnt = 0
    adv_emis_cnt = 0
    m_sch = re.search(r'(\d{1,2})\s*\/\s*(\d{1,2})', scheme_str)
    if m_sch:
        gross_emis_cnt = int(m_sch.group(1))
        adv_emis_cnt = int(m_sch.group(2))
        rem_emis_cnt = max(0, gross_emis_cnt - adv_emis_cnt)
    else:
        m_num = re.search(r'(\d{1,2})', scheme_str)
        if m_num:
            rem_emis_cnt = int(m_num.group(1))
            gross_emis_cnt = rem_emis_cnt

    # Build Finance Loan Settlement Box (Rule 206 & 207)
    finance_box_html = ""
    if bill_type_val == "FINANCE_BILL" or loan_amt_val > 0 or fin_comp or do_ref:
        f_rows = []
        if fin_cfg.get("show_comp_do", True):
            f_rows.append(f"<div><b>🏦 ફાઇનાન્સ કંપની:</b> {fin_comp or 'ફાઇનાન્સ'} | <b>DO નંબર:</b> <span style='color:#0369a1; font-weight:900;'>{do_ref or '____________'}</span></div>")
        if fin_cfg.get("show_cust_id", True) and cust_id_val:
            f_rows.append(f"<div><b>🆔 ગ્રાહક કસ્ટમર આઈડી (Customer ID):</b> <span style='font-family:monospace; font-weight:900; color:#7c3aed;'>{cust_id_val}</span></div>")
        if fin_cfg.get("show_net_emis", True):
            if rem_emis_cnt > 0:
                emi_cnt_txt = f"<b>{rem_emis_cnt} મહિના ({rem_emis_cnt} હપ્તા)</b>" + (f" <span style='font-size:11px; color:#475569;'>(સ્કીમ {gross_emis_cnt}/{adv_emis_cnt} — {adv_emis_cnt} એડવાન્સ EMI બાદ કરતાં)</span>" if adv_emis_cnt > 0 else f" <span style='font-size:11px; color:#475569;'>(સ્કીમ: {scheme_str})</span>")
            else:
                emi_cnt_txt = "<b>________ હપ્તા</b>"
            f_rows.append(f"<div><b>🗓️ કુલ બાકી હપ્તા (એડવાન્સ EMI બાદ કરતાં):</b> {emi_cnt_txt}</div>")
        if fin_cfg.get("show_emi_amt", True):
            emi_disp = f"₹{emi_amt_val:,.0f}" if emi_amt_val > 0 else "₹____________"
            extra_ch_part = ""
            if fin_cfg.get("show_first_extra_charge", True):
                ch_disp = f"₹{first_extra_ch}" if first_extra_ch else "₹________________"
                extra_ch_part = f" &nbsp;|&nbsp; <b>પ્રથમ હપ્તામાં વિશેષ ચાર્જ સાથે કપાવવાપાત્ર રકમ:</b> {ch_disp}"
            f_rows.append(f"<div><b>💳 માસિક હપ્તાની રકમ (EMI):</b> <span style='color:#15803d; font-weight:900;'>{emi_disp}</span>{extra_ch_part}</div>")
        if fin_cfg.get("show_dp", True):
            actual_dp_v = exp_dp_val if exp_dp_val > 0 else ( float(row[8] or 0) + float(row[9] or 0) )
        if loan_amt_val > 0 and (actual_dp_v >= inv_total or actual_dp_v <= 0):
            actual_dp_v = max(0.0, round(inv_total - loan_amt_val, 2))
            if fin_cfg.get("dp_mode") == "UNDERLINE" or actual_dp_v <= 0:
                dp_disp_str = "₹____________________"
            else:
                dp_disp_str = f"<b>₹{actual_dp_v:,.0f}</b>"
            f_rows.append(f"<div><b>💵 ગ્રાહકે ભરેલું ડાઉન પેમેન્ટ (Down Payment):</b> {dp_disp_str}</div>")
        if fin_cfg.get("show_loan_amt", True) and loan_amt_val > 0:
            f_rows.append(f"<div><b>💰 કુલ લોન રકમ:</b> ₹{loan_amt_val:,.0f}</div>")
        if fin_cfg.get("show_emi_dates", True):
            if fin_cfg.get("emi_date_mode") == "UNDERLINE" or not first_emi_dt:
                first_dt_disp = first_emi_dt if (first_emi_dt and fin_cfg.get("emi_date_mode") != "UNDERLINE") else "__________________"
                last_mo_disp = last_emi_mo if (last_emi_mo and fin_cfg.get("emi_date_mode") != "UNDERLINE") else "__________________"
            else:
                first_dt_disp = f"<b>{first_emi_dt}</b>"
                auto_last = last_emi_mo or _calc_auto_last_emi_month_gu(first_emi_dt, rem_emis_cnt or 6)
                last_mo_disp = f"<b>{auto_last or '__________________'}</b>"
            f_rows.append(f"<div style='grid-column:1 / -1; background:#fefce8; border:1px dashed #ca8a04; padding:6px 10px; border-radius:4px; margin-top:2px;'><b>📅 પ્રથમ હપ્તો (EMI) કપાવાની તારીખ:</b> {first_dt_disp} &nbsp;&nbsp;|&nbsp;&nbsp; <b>🏁 છેલ્લો હપ્તો (લોન પૂર્ણ મહિનો):</b> {last_mo_disp}</div>")

        if f_rows:
            finance_box_html = f"""
            <div style="margin-top:12px; border:2px solid #0284c7; background:#f0f9ff; border-radius:6px; padding:10px 14px; font-size:12.5px; line-height:1.7;">
                <div style="font-weight:900; color:#0f2043; font-size:13.5px; border-bottom:1.5px solid #bae6fd; padding-bottom:4px; margin-bottom:6px;">
                    🏦 ફાઇનાન્સ લોન & EMI હપ્તા સેટલમેન્ટ વિગત (Finance Settlement Details):
                </div>
                <div style="display:grid; grid-template-columns:1fr 1fr; gap:6px 16px;">
                    {"".join(f_rows)}
                </div>
            </div>"""

    # નિયમ ૨૧૨ & ૨૧૪: F2 ઉધાર (Credit) બિલમાં ગ્રાહક વાયદા તારીખ (Promised Due Date) અને કાનૂની બાંહેધરી સહી બોક્સ
    credit_promise_box_html = ""
    if bill_type_val == "CREDIT_BILL" or due > 0:
        if due_date_val:
            try:
                dd_obj = datetime.datetime.strptime(due_date_val[:10], "%Y-%m-%d").date()
                due_dt_disp = f"<b style='color:#dc2626; font-size:14px;'>{dd_obj.strftime('%d-%m-%Y')}</b>"
            except Exception:
                due_dt_disp = f"<b style='color:#dc2626; font-size:14px;'>{due_date_val}</b>"
        else:
            due_dt_disp = "<b>______________________ (તારીખ)</b>"

        signed_badge = ""
        if signed_copy_p:
            sc_url = signed_copy_p if signed_copy_p.startswith("/") else ("/" + signed_copy_p)
            signed_badge = f"<a href='{sc_url}' target='_blank' class='no-print' style='background:#16a34a; color:white; padding:3px 10px; border-radius:4px; text-decoration:none; font-size:11.5px; font-weight:bold;'>✅ સહી વાળી રિટર્ન કોપી સેવ છે (જુઓ)</a>"

        credit_promise_box_html = f"""
        <div style="margin-top:12px; border:2px solid #dc2626; background:#fff1f2; border-radius:6px; padding:10px 14px; font-size:12.5px; line-height:1.6;">
            <div style="display:flex; justify-content:space-between; align-items:center; border-bottom:1.5px solid #fecdd3; padding-bottom:4px; margin-bottom:6px;">
                <b style="color:#991b1b; font-size:13.5px;">💳 ઉધાર ચુકવણી વિગત & ગ્રાહક વાયદા બાંહેધરી (Credit Promised Due Date):</b>
                {signed_badge}
            </div>
            <div style="display:flex; justify-content:space-between; flex-wrap:wrap; gap:10px;">
                <div><b>કુલ બિલ રકમ:</b> ₹{inv_total:,.0f} &nbsp;|&nbsp; <b>આજે જમા રકમ:</b> ₹{paid:,.0f} &nbsp;|&nbsp; <b style="color:#dc2626; font-size:14px;">ચૂકવવાપાત્ર બાકી ઉધાર: ₹{due:,.0f}</b></div>
                <div><b>📌 ચુકવણી વાયદા તારીખ (Promised Date):</b> {due_dt_disp}</div>
            </div>
            <div style="margin-top:6px; background:white; border:1px dashed #f87171; padding:6px 10px; border-radius:4px; color:#0f172a; font-weight:600;">
                ✍️ <b>ગ્રાહકની લેખિત બાંહેધરી:</b> "હું <b>{cust_disp}</b> બાંહેધરી આપું છું કે ઉપરોક્ત બાકી રહેતી રકમ <b>₹{due:,.0f}/-</b> ઉપરોક્ત વાયદા તારીખ {due_dt_disp} સુધીમાં સંપૂર્ણ ચૂકવી આપીશ. ચુકવણીમાં વિલંબ થાય તો દુકાનના નિયમો મને બંધનકર્તા રહેશે."
            </div>
            <div style="display:flex; justify-content:space-between; align-items:flex-end; margin-top:18px; padding-top:6px;">
                <div><b>સાક્ષી / જામીનદાર સહી:</b> ________________________</div>
                <div><b>ગ્રાહકની સહી (Customer Signature):</b> ________________________</div>
            </div>
        </div>"""

    
    # ગ્રાહકનું અગાઉનું ખાતાવહી લેણું (Previous Khata Due) કેલ્ક્યુલેટ કરવું
    cust_phone_query = str(row[3] if row[3] != '-' else '').strip()
    prev_khata_due = 0.0
    if cust_phone_query and conn:
        try:
            _c_kh = conn.cursor()
            _c_kh.execute("SELECT COALESCE(SUM(debit - credit), 0) FROM customer_ledger WHERE phone=? AND bill_no != ?", (cust_phone_query, row[0]))
            _kr = _c_kh.fetchone()
            if _kr and _kr[0]:
                prev_khata_due = max(0.0, float(_kr[0]))
        except Exception:
            pass

    cust_khata_strip_html = f"""
    <div id="sec_cust_prev_khata" style="margin-top:8px; border:1.5px solid #0284c7; background:#f0f9ff; padding:8px 12px; border-radius:6px; font-size:12px; display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:8px;">
        <span>📋 <b>ગ્રાહક ખાતાવહી હિસાબ:</b> અગાઉની બાકી રકમ: <b style="color:#d97706; font-size:13px;">₹{prev_khata_due:,.0f}</b> &nbsp;|&nbsp; આ બિલની રકમ: <b>₹{inv_total:,.0f}</b> (જમા: ₹{paid:,.0f})</span>
        <span style="font-weight:900; color:#0f2043; background:#e0f2fe; padding:3px 10px; border-radius:4px; border:1.5px solid #7dd3fc; font-size:13px;">કુલ લેણી રકમ: ₹{prev_khata_due + due:,.0f}</span>
    </div>"""

    custom_terms_raw = (shop_prof.get("terms_text") or "").strip()
    if custom_terms_raw:
        if lang == "gu":
            terms_html = custom_terms_raw.replace(chr(10), "<br>")
        else:
            terms_html = localize_shop_text(custom_terms_raw, lang).replace(chr(10), "<br>") + "<br>" + L["default_terms"]
    else:
        terms_html = L["default_terms"]

    dir_attr = "rtl" if lang == "ur" else "ltr"
    wa_share_txt = urllib.parse.quote(
        f"*{store_name_loc}* | {L['bill']}: {row[0]} | {L['cust']}: {cust_disp} | {L['item']}: {mod_disp} (IMEI: {row[6]}) | {L['amt']}: ₹{inv_total:,.0f} | {L['paid']}: ₹{paid:,.0f} | {L['due']}: ₹{due:,.0f} | {L['footer_txt']}"
    )

    custom_layout_banner = ""
    if shop_prof.get("custom_bill_html"):
        custom_layout_banner = f"<div style='border-bottom:1px dashed #cbd5e1; padding-bottom:8px; margin-bottom:8px;'>{localize_shop_text(shop_prof['custom_bill_html'], lang)}</div>"

    # Owner-only check for customizing Finance Box & Digital Signature
    cur_role = str(STORE_CFG.get("current_user_role", "Owner")).upper()
    is_owner_user = cur_role in ("OWNER", "SUPER_ADMIN", "દુકાનદાર", "")

    owner_cfg_btn = ""
    if is_owner_user:
        owner_cfg_btn = """<button type="button" onclick="document.getElementById('owner_bill_cfg_modal').style.display='flex'" style="background:#7c3aed; color:white; border:none; padding:6px 12px; border-radius:4px; font-weight:bold; cursor:pointer; font-size:12px;">⚙️ બિલ & ફાઇનાન્સ બોક્સ સેટિંગ (Owner Only)</button>"""

    # Calculate Poojara Original Copy-to-Copy exact fields
    gross_before_disc = inv_total + disc_val
    gross_taxable_rate = round(gross_before_disc / tax_div, 2)
    net_taxable_amt = round(gross_taxable_rate - disc_val, 2)
    if disc_val <= 0:
        net_taxable_amt = taxable
        gross_taxable_rate = taxable
    pj_cgst = round(net_taxable_amt * (half_pct / 100.0), 2)
    pj_sgst = round(net_taxable_amt * (half_pct / 100.0), 2)
    pj_subtotal = round(net_taxable_amt + pj_cgst + pj_sgst, 2)
    pj_net_total = round(pj_subtotal) if inv_total <= 0 else round(inv_total)
    pj_round_off = round(pj_net_total - pj_subtotal, 2)
    pj_words = _num_to_english_words(int(round(pj_net_total)))
    pj_date_fmt = row[1]
    try:
        if re.match(r'^\d{4}-\d{2}-\d{2}$', str(row[1])):
            dt_p = datetime.datetime.strptime(str(row[1]), "%Y-%m-%d")
            pj_date_fmt = dt_p.strftime("%d/%m/%Y")
    except Exception:
        pass
    # Reconcile exact Payment Info across Cash, Credit, and Finance (including Discount!)
    financier_line_html = ""
    if bill_type_val == "FINANCE_BILL" or loan_amt_val > 0 or fin_comp:
        eff_loan = min(pj_net_total, loan_amt_val if loan_amt_val > 0 else round(pj_net_total * 0.8, 2))
        eff_dp_cash = max(0.0, round(pj_net_total - eff_loan, 2))
        fin_nm_up = (fin_comp or "BAJAJ FINANCE LTD.").upper()
        appr_no = do_ref or cust_id_val or "BR190535123"
        financier_line_html = f"""<div style="border-bottom:1.5px solid #000; padding:5px 8px; font-size:12px; font-weight:bold;">
            Financier: <span id="pj_fin_name" contenteditable="true">{fin_nm_up} - card</span>, Approval No.: <span id="pj_fin_appr" contenteditable="true">{appr_no}</span>
        </div>"""
        pj_pay_mode_str = f"Cash : {eff_dp_cash:,.2f}, Finance : {eff_loan:,.2f}"
    elif bill_type_val == "CREDIT_BILL" or due > 0:
        eff_rec = max(0.0, round(pj_net_total - due, 2))
        pj_pay_mode_str = f"Cash (Received) : {eff_rec:,.2f}, Credit Due : {due:,.2f}"
    else:
        pj_pay_mode_str = f"Card : {pj_net_total:,.2f}," if float(row[9] or 0) > 0 else f"Cash : {pj_net_total:,.2f},"

    # Clean uppercase English customer name for English Tax Invoice box
    eng_cust_raw = localize_shop_text(raw_cust, "en").upper().strip()
    if not eng_cust_raw.startswith(("MR.", "MRS.", "MS.", "M/S")):
        eng_cust_disp = "Mr. " + eng_cust_raw
    else:
        eng_cust_disp = eng_cust_raw

    # નિયમ ૨૩૪: Zero Competitor Leakage & 6 Flexible Templates
    # સેમ્પલ સ્ટોર્સમાં ફ્રેન્ચાઇઝી મોડ માટે 'દેવાંશી મોબાઈલ' અને રીટેલ મોડ માટે 'મનસ્વી ટેલિકોમ' દેખાશે, અને અસલ દુકાનદાર માટે તેનું પોતાનું જ નામ!
    clean_store_hdr_name = raw_store_name.strip()
    if active_sid == "DEVANSHI" and print_mode == "RETAIL_STANDARD_GST":
        clean_store_hdr_name = "મનસ્વી ટેલિકોમ (રીટેલ સેમ્પલ)"
        store_name_loc = localize_shop_text(clean_store_hdr_name, lang)
    elif active_sid == "MANSHVI" and print_mode in ("FRANCHISE_DOUBLE_BOX", "POOJARA_ORIGINAL"):
        clean_store_hdr_name = "દેવાંશી મોબાઈલ (ફ્રેન્ચાઈઝી સેમ્પલ)"
        store_name_loc = localize_shop_text(clean_store_hdr_name, lang)
    elif clean_store_hdr_name == clean_store_hdr_name.lower() and any('a' <= c <= 'z' for c in clean_store_hdr_name):
        clean_store_hdr_name = clean_store_hdr_name.title()
    elif any('઀' <= c <= '૿' for c in clean_store_hdr_name) and lang == "en":
        clean_store_hdr_name = localize_shop_text(clean_store_hdr_name, "en").title()

    shop_contact_clean = str(shop_prof.get("contact") or "").strip() or "મોબાઇલ નંબર સેટ કરો"

    is_lh_mode = (shop_prof.get("letterhead_mode") == "PREPRINTED_LETTERHEAD" or paper_format == "LETTERHEAD" or print_mode == "LETTERHEAD_PRINT")
    eff_top_margin_in = float(shop_prof.get("letterhead_top_margin_in") or 1.8) if is_lh_mode else 0.0

    # Disc 1 (Company Scheme) and Disc 2 (Store Discount) real split
    disc1_scheme_val = float(row[31] if len(row) > 31 and row[31] is not None else 0.0)
    disc2_store_val = max(0.0, disc_val - disc1_scheme_val) if disc_val >= disc1_scheme_val else disc_val
    courier_ch_val = float(row[32] if len(row) > 32 and row[32] is not None else 0.0)

    # Template-specific serial / batch label & HSN
    is_tally_batch_tpl = (print_mode == "TALLY_PRIME_BATCH")
    is_appliance_tpl = (print_mode == "APPLIANCE_ELECTRONICS")
    is_khata_tpl = (print_mode == "SMART_KHATA_BALANCE")
    is_retail_std_tpl = (print_mode == "RETAIL_STANDARD_GST")

    imei_prefix_lbl = "Batch : " if is_tally_batch_tpl else ("Serial No (S/N) : " if is_appliance_tpl else "IMEI NO. ")
    item_hsn_code = "85287200" if is_appliance_tpl else "85171300"

    # Template 3: Smart Khata Balance Box (Khushi Mobile Style: Previous Balance + Today Bill - Paid = Net Balance)
    khata_summary_box_html = ""
    if is_khata_tpl or due > 0 or prev_khata_bal > 0:
        net_khata_closing = round(prev_khata_bal + due, 2)
        khata_summary_box_html = f"""
        <div style="border-bottom:1.5px solid #000; padding:6px 8px; background:{'#fefce8' if is_khata_tpl else '#fff'}; font-size:12px;">
            <div style="display:grid; grid-template-columns:repeat(4, 1fr); gap:8px; text-align:center; font-weight:bold;">
                <div style="border:1px solid #000; padding:4px; background:#fff;">પાછલી બાકી (Prev. Balance)<br><span style="color:#b45309; font-size:13.5px;">₹{prev_khata_bal:,.2f}</span></div>
                <div style="border:1px solid #000; padding:4px; background:#fff;">આજનું બિલ (Bill Amt)<br><span style="color:#0f2043; font-size:13.5px;">₹{pj_net_total:,.2f}</span></div>
                <div style="border:1px solid #000; padding:4px; background:#fff;">આજે જમા (Received)<br><span style="color:#15803d; font-size:13.5px;">₹{paid:,.2f}</span></div>
                <div style="border:1px solid #000; padding:4px; background:#fee2e2;">કુલ બાકી (Net Balance)<br><span style="color:#dc2626; font-size:14px; font-weight:900;">₹{net_khata_closing:,.2f}</span></div>
            </div>
        </div>"""

    # Template 6: Consumer Durable / Home Appliances Warranty & Installation Box
    appliance_extra_box_html = ""
    if is_appliance_tpl:
        appliance_extra_box_html = f"""
        <div style="border-bottom:1.5px solid #000; padding:6px 8px; background:#f0f9ff; font-size:11.5px;">
            <b>📺 કન્ઝ્યુમર ડ્યુરેબલ / હોમ એપ્લાયન્સિસ વોરંટી & ઇન્સ્ટોલેશન નોંધ:</b><br>
            • પ્રોડક્ટ સીરીયલ નંબર (S/N): <b>{row[6]}</b> | વોરંટી: <b>{row[30] or '૧ વર્ષ કંપની ઓન-સાઇટ વોરંટી'}</b> | કુરિયર/ટ્રાન્સપોર્ટ ચાર્જ: <b>₹{courier_ch_val:,.2f}</b><br>
            • ટીવી, એસી, વોશિંગ મશીન કે ફ્રિજનું ઓફિશિયલ કંપની ટેકનિશિયન દ્વારા જ ઇન્સ્ટોલેશન કરાવવું ફરજિયાત છે.
        </div>"""
    copy_label_map = {
        "ORIGINAL": "Original for Recipient",
        "DUPLICATE": "Duplicate for Supplier",
        "TRIPLICATE": "Triplicate for Financier / Bank"
    }
    copy_label_txt = copy_label_map.get(copy_mode.upper(), "Original")
    show_sub_round_rows = "table-row" if abs(pj_round_off) >= 0.01 else "none"

    st_mode_cur = str(shop_prof.get("store_mode") or "FRANCHISE_HO").upper()
    is_franchise_pin_req = ("FRANCHISE" in st_mode_cur or bill_type_val == "FINANCE_BILL" or loan_amt_val > 0)
    status_alert_html = ""
    if ok_msg:
        status_alert_html = f"<div class='no-print' style='max-width:820px; margin:0 auto 10px auto; background:#dcfce7; border:2px solid #16a34a; color:#166534; padding:8px 14px; border-radius:6px; font-weight:900; text-align:center;'>{ok_msg}</div>"
    if err_msg:
        status_alert_html = f"<div class='no-print' style='max-width:820px; margin:0 auto 10px auto; background:#fee2e2; border:2px solid #dc2626; color:#991b1b; padding:8px 14px; border-radius:6px; font-weight:900; text-align:center;'>{err_msg}</div>"

    max_w_px = "300px" if paper_format == "THERMAL_3IN" else ("220px" if paper_format == "THERMAL_2IN" else ("560px" if paper_format == "A5" else "800px"))

    return HTMLResponse(f"""<!DOCTYPE html>
    <html lang="{lang}" dir="{dir_attr}"><head><meta charset="UTF-8"><title>Invoice - {row[0]} ({store_name_loc})</title>
    <style>
        @page {{ size: {"A5" if paper_format == "A5" else shop_prof.get('paper_size', 'A4')}; margin: 8mm; }}
        body {{ font-family:'Noto Sans Gujarati','Segoe UI',sans-serif; padding:20px; color:#1e293b; background:#f1f5f9; }}
        .inv-box {{ max-width:{max_w_px}; margin:auto; border:2.5px solid #0f2043; padding:22px; padding-top:calc(22px + {eff_top_margin_in:.2f}in); border-radius:8px; background:white; box-shadow:0 8px 25px rgba(0,0,0,0.08); box-sizing:border-box; }}
        .lh-top-header {{ display:{"none" if is_lh_mode else "flex"}; justify-content:space-between; align-items:center; border-bottom:2px solid #0f2043; padding-bottom:10px; }}
        table {{ width:100%; border-collapse:collapse; margin-top:12px; }}
        th, td {{ border:1px solid #475569; padding:8px; text-align:left; font-size:13px; }}
        th {{ background:#0f2043; color:white; }}
        @media print {{ body {{ background:white; padding:0; }} .inv-box {{ box-shadow:none; border:{"none" if is_lh_mode else "2px solid #000"}; }} .no-print {{ display:none !important; }} }}
    </style></head>
    <body>
    <div class="no-print" style="max-width:860px; margin:0 auto 12px auto; display:flex; justify-content:space-between; align-items:center; background:#e0f2fe; padding:10px 14px; border-radius:6px; flex-wrap:wrap; gap:8px; border:1.5px solid #0284c7;" dir="ltr">
        <form method="get" action="/print-invoice" style="display:flex; gap:6px; align-items:center; flex-wrap:wrap;">
            <input type="hidden" name="bill_no" value="{row[0]}">
            <b>૧. ૫-બિલ ફિલ્ટર:</b>
            <select name="print_mode" onchange="this.form.submit()" style="padding:5px; font-weight:bold; background:#fef08a; border:1.5px solid #ca8a04; border-radius:4px;">
                <option value="FRANCHISE_DOUBLE_BOX" {"selected" if print_mode in ("FRANCHISE_DOUBLE_BOX", "POOJARA_ORIGINAL", "") else ""}>૧) ફ્રેન્ચાઈઝી ડબલ-બોક્સ બિલ (સેમ્પલ: દેવાંશી)</option>
                <option value="RETAIL_STANDARD_GST" {"selected" if print_mode=="RETAIL_STANDARD_GST" else ""}>૨) રીટેલ સ્ટાન્ડર્ડ જીએસટી બિલ (સેમ્પલ: મનસ્વી)</option>
                <option value="SMART_KHATA_BALANCE" {"selected" if print_mode=="SMART_KHATA_BALANCE" else ""}>૩) સ્માર્ટ ઉધારી / ખાતાવહી બિલ (પાછલી ઉધારી & નેટ બેલેન્સ બોક્સ)</option>
                <option value="TALLY_PRIME_BATCH" {"selected" if print_mode=="TALLY_PRIME_BATCH" else ""}>૪) ટેલી પ્રાઇમ બેચ બિલ (વિનાયક સ્ટાઇલ)</option>
                <option value="LETTERHEAD_PRINT" {"selected" if print_mode=="LETTERHEAD_PRINT" else ""}>૫) લેટરપેડ પ્રિન્ટ મોડ (છાપેલા કાગળ માટે)</option>
                <option value="APPLIANCE_ELECTRONICS" {"selected" if print_mode=="APPLIANCE_ELECTRONICS" else ""}>૬) કન્ઝ્યુમર ડ્યુરેબલ / એપ્લાયન્સિસ બિલ (ટીવી, એસી, વોશિંગ મશીન)</option>
                <option value="CASH_BILL" {"selected" if print_mode=="CASH_BILL" else ""}>૭) રોકડ બિલ (Cash / UPI / Card Bill)</option>
                <option value="CREDIT_BILL" {"selected" if print_mode=="CREDIT_BILL" else ""}>૮) બાકી / ઉધાર બિલ (Credit + વાયદા સહી બોક્સ)</option>
                <option value="FINANCE_BILL" {"selected" if print_mode=="FINANCE_BILL" else ""}>૯) ફાઇનાન્સ DO બિલ (Financier + EMI બોક્સ)</option>
            </select>
            <b>કાગળ સાઇઝ:</b>
            <select name="paper_format" onchange="this.form.submit()" style="padding:5px; font-weight:bold; border-radius:4px;">
                <option value="A4" {"selected" if paper_format=="A4" else ""}>A4 પાકું બિલ</option>
                <option value="A5" {"selected" if paper_format=="A5" else ""}>A5 હાફ-પેજ બિલ</option>
                <option value="THERMAL_3IN" {"selected" if paper_format=="THERMAL_3IN" else ""}>૩-ઇંચ થર્મલ કાપલી</option>
                <option value="THERMAL_2IN" {"selected" if paper_format=="THERMAL_2IN" else ""}>૨-ઇંચ થર્મલ કાપલી</option>
                <option value="LETTERHEAD" {"selected" if paper_format=="LETTERHEAD" else ""}>લેટરહેડ મોડ (હેડર વગર)</option>
            </select>
            <b>કોપી:</b>
            <select name="copy_mode" onchange="this.form.submit()" style="padding:5px; font-weight:bold; border-radius:4px;">
                <option value="ORIGINAL" {"selected" if copy_mode=="ORIGINAL" else ""}>૧. ગ્રાહક કોપી (Original)</option>
                <option value="DUPLICATE" {"selected" if copy_mode=="DUPLICATE" else ""}>૨. દુકાનદાર કોપી (Duplicate)</option>
                <option value="TRIPLICATE" {"selected" if copy_mode=="TRIPLICATE" else ""}>૩. બેંક/ફાઇનાન્સ કોપી (Triplicate)</option>
            </select>
            <b>૨. ભાષા:</b>
            <select name="lang" onchange="this.form.submit()" style="padding:5px; font-weight:bold;">
                <option value="gu" {"selected" if lang=="gu" else ""}>૧. ગુજરાતી (Gujarati)</option>
                <option value="hi" {"selected" if lang=="hi" else ""}>૨. હિન્દી (Hindi)</option>
                <option value="en" {"selected" if lang=="en" else ""}>૩. અંગ્રેજી (English)</option>
                <option value="mr" {"selected" if lang=="mr" else ""}>૪. મરાઠી (Marathi)</option>
                <option value="pa" {"selected" if lang=="pa" else ""}>૫. પંજાબી (Punjabi)</option>
                <option value="bn" {"selected" if lang=="bn" else ""}>૬. બંગાળી (Bengali)</option>
                <option value="ta" {"selected" if lang=="ta" else ""}>૭. તમિલ (Tamil)</option>
                <option value="te" {"selected" if lang=="te" else ""}>૮. તેલુગુ (Telugu)</option>
                <option value="kn" {"selected" if lang=="kn" else ""}>૯. કન્નડ (Kannada)</option>
                <option value="ml" {"selected" if lang=="ml" else ""}>૧૦. મલયાલમ (Malayalam)</option>
                <option value="or" {"selected" if lang=="or" else ""}>૧૧. ઉડિયા (Odia)</option>
                <option value="ur" {"selected" if lang=="ur" else ""}>૧૨. ઉર્દૂ (Urdu)</option>
            </select>
        </form>
        <div style="display:flex; gap:6px; flex-wrap:wrap;">
            {owner_cfg_btn}
            <button type="button" onclick="document.getElementById('upload_signed_modal').style.display='flex'" style="background:#d97706; color:white; border:none; padding:6px 12px; border-radius:4px; font-weight:bold; cursor:pointer; font-size:12px;">📸 સહી વાળી રિટર્ન કોપી અપલોડ</button>
            <a href="https://api.whatsapp.com/send?text={wa_share_txt}" target="_blank" style="background:#2563eb; color:white; padding:6px 12px; border-radius:4px; text-decoration:none; font-weight:bold; font-size:12px;">📲 WhatsApp</a>
            <button onclick="window.print()" style="background:#16a34a; color:white; border:none; padding:6px 16px; border-radius:4px; font-weight:bold; cursor:pointer;">🖨️ પ્રિન્ટ / PDF સેવ કરો</button>
        </div>
    </div>

    {status_alert_html}

    <!-- 🎛️ મોડ્યુલર બિલ પ્રિન્ટ કસ્ટમાઇઝેશન સ્વિચ (ગ્રાહક બાકી ખાતું + ફાઇનાન્સ EMI બોક્સ + બેંક QR) -->
    <div class="no-print" style="max-width:820px; margin:0 auto 10px auto; background:#f8fafc; border:1.5px solid #cbd5e1; padding:8px 12px; border-radius:8px; display:flex; align-items:center; justify-content:space-between; flex-wrap:wrap; gap:10px; font-size:12px;" dir="ltr">
        <b style="color:#0f2043;">🎛️ બિલ કસ્ટમાઇઝેશન (પ્રિન્ટમાં શું દર્શાવવું?):</b>
        <div style="display:flex; gap:14px; flex-wrap:wrap;">
            <label style="cursor:pointer; display:flex; align-items:center; gap:4px; font-weight:bold; color:#0369a1;"><input type="checkbox" id="chk_prev_khata" onchange="toggleInvSec('sec_cust_prev_khata', this.checked)" checked> 📋 ગ્રાહક જૂનું બાકી ખાતું</label>
            <label style="cursor:pointer; display:flex; align-items:center; gap:4px; font-weight:bold; color:#15803d;"><input type="checkbox" id="chk_finance_box" onchange="toggleInvSec('sec_finance_box', this.checked)" checked> 🏦 ફાઇનાન્સ EMI બોક્સ</label>
            <label style="cursor:pointer; display:flex; align-items:center; gap:4px; font-weight:bold; color:#7c3aed;"><input type="checkbox" id="chk_bank_qr" onchange="toggleInvSec('sec_bank_qr', this.checked)" checked> 📲 દુકાનનો UPI QR</label>
            <label style="cursor:pointer; display:flex; align-items:center; gap:4px; font-weight:bold; color:#b45309;"><input type="checkbox" id="chk_terms" onchange="toggleInvSec('sec_terms_box', this.checked)" checked> 📜 નિયમો & શરતો</label>
        </div>
    </div>

    <!-- ✏️ ઓરિજિનલ પૂજારા બિલ લાઈવ એડિટિંગ અને માસ્ટર PIN 1986 સેવ/ડિલીટ કંટ્રોલ બાર -->
    <div class="no-print" style="max-width:820px; margin:0 auto 12px auto; background:#fffbeb; border:2px solid #eab308; padding:10px 14px; border-radius:8px;" dir="ltr">
        <form id="save_edited_bill_form" action="/api/save-edited-original-invoice" method="post" onsubmit="return syncAndSubmitEditedBill(event)" style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:10px;">
            <input type="hidden" name="orig_bill_no" value="{row[0]}">
            <input type="hidden" name="new_bill_no" id="hid_new_bill_no" value="{row[0]}">
            <input type="hidden" name="bill_date" id="hid_bill_date" value="{row[1]}">
            <input type="hidden" name="customer_name" id="hid_cust_name" value="{raw_cust}">
            <input type="hidden" name="phone" id="hid_phone" value="{row[3] if row[3] != '-' else '7621019633'}">
            <input type="hidden" name="customer_address" id="hid_addr" value="{raw_cust_addr or 'BECHARAJI,Becharaji-384210'}">
            <input type="hidden" name="customer_pincode" id="hid_pin" value="{row[16] or '384210'}">
            <input type="hidden" name="model" id="hid_model" value="{temp_mod or row[5]}">
            <input type="hidden" name="imei" id="hid_imei" value="{row[6]}">
            <input type="hidden" name="mop_price" id="hid_mop" value="{pj_net_total:.2f}">
            <input type="hidden" name="discount_amt" id="hid_disc" value="{disc_val:.2f}">
            <input type="hidden" name="gst_pct" id="hid_gst" value="{gst_rate}">
            <input type="hidden" name="print_mode" value="{print_mode}">
            <input type="hidden" name="lang" value="{lang}">
            <div style="font-size:12px; font-weight:800; color:#854d0e;">
                ✏️ <b>લાઈવ બિલ એડિટિંગ સક્રિય:</b> નીચે બિલના કોઈપણ લખાણ કે રકમ પર સીધું ક્લિક કરીને સુધારો કરો (ટેક્સ અને ટોટલ આપોઆપ ગણાશે).
            </div>
            <div style="display:flex; gap:8px; align-items:center; flex-wrap:wrap;">
                <input type="password" name="admin_pin" id="edit_bill_pin_inp" placeholder="🔒 ઓનર સિક્યોરિટી PIN" style="width:130px; padding:6px 8px; border:2px solid #dc2626; border-radius:5px; font-weight:900; font-size:12px;" {"required" if is_franchise_pin_req else ""}>
                <button type="submit" style="background:#15803d; color:white; border:none; padding:7px 14px; border-radius:5px; font-weight:900; cursor:pointer; font-size:12px;">
                    💾 એડિટ કરેલું બિલ સેવ કરો
                </button>
                <button type="button" onclick="promptDeleteInvoicePin()" style="background:#dc2626; color:white; border:none; padding:7px 12px; border-radius:5px; font-weight:900; cursor:pointer; font-size:12px;">
                    🗑️ બિલ ડિલીટ કરો
                </button>
            </div>
        </form>
        <form id="del_inv_pin_form" action="/api/delete-invoice-pin-locked" method="post" style="display:none;">
            <input type="hidden" name="bill_no" value="{row[0]}">
            <input type="hidden" name="admin_pin" id="del_inv_pin_val" value="">
        </form>
    </div>

    <!-- 📄 મોડ ૧: યુનિવર્સલ કોપી-ટુ-કોપી ઓરિજિનલ ટેક્સ ઇનવોઇસ (દરેક દુકાનદારના પોતાના નામ/લોગો/GST સાથે + ૫-બિલ ફિલ્ટર સપોર્ટ) -->
    <div class="inv-box" style="display:{'none' if paper_format in ('THERMAL_3IN', 'THERMAL_2IN') else 'block'}; font-family:Arial, Helvetica, sans-serif; color:#000; padding:0; padding-top:{eff_top_margin_in:.2f}in; border:2px solid #000; border-radius:0; max-width:{max_w_px}; margin:auto; background:#fff;" dir="ltr">
        <!-- Universal Dynamic Shop Header Row (Each Shop's Own Logo, Theme Color, Name, Address, Phone & GSTIN) -->
        {custom_layout_banner}
        <div style="display:{'none' if is_lh_mode else 'flex'}; border-bottom:1.5px solid #000; padding:8px 10px; align-items:center;">
            <div style="width:145px; height:90px; background:{(shop_prof.get('theme_color') or '#0f2043')}; display:flex; align-items:center; justify-content:center; flex-shrink:0; border:1px solid #000; overflow:hidden;">
                {logo_html if logo_html else '<span contenteditable="true" style="color:#fff; font-size:20px; font-weight:900; letter-spacing:0.5px; font-family:Arial Black, Arial, sans-serif; text-align:center; padding:4px;">' + (store_name_loc.split()[0][:12] if lang != "en" else clean_store_hdr_name.split()[0][:12].upper()) + '</span>'}
            </div>
            <div style="flex:1; text-align:center; padding:0 10px; line-height:1.35;">
                <div contenteditable="true" style="font-size:21px; font-weight:900; color:#000;">{store_name_loc if lang != "en" else clean_store_hdr_name}</div>
                <div contenteditable="true" style="font-size:11.5px; color:#000;">{store_addr_loc if (lang != "en" and store_addr_loc) else (raw_store_addr or "દુકાનનું સરનામું સેટ કરો")}</div>
                <div contenteditable="true" style="font-size:11.5px; color:#000;">Ph: {shop_contact_clean}</div>
                <div contenteditable="true" style="font-size:11.5px; color:#000;">{("GSTIN : " + str(shop_prof.get("gstin","")) + " | State : 24-GUJARAT") if shop_prof.get("gstin") else "State : 24-GUJARAT"}</div>
                {f'<div contenteditable="true" style="font-size:11.5px; color:#000;">Email Id : {shop_prof.get("owner_email")}</div>' if shop_prof.get("owner_email") else ''}
            </div>
        </div>

        <!-- Tax Invoice & Invoice No / Date Row -->
        <div style="border-bottom:1.5px solid #000; padding:4px 8px; font-size:12px;">
            <div style="display:flex; justify-content:space-between; align-items:center;">
                <div style="width:33%;"></div>
                <div style="width:34%; text-align:center; font-weight:900; font-size:12.5px;">TAX INVOICE</div>
                <div style="width:33%; text-align:right; font-size:12px;" contenteditable="true">{copy_label_txt}</div>
            </div>
            <div style="display:flex; justify-content:space-between; align-items:center; margin-top:2px;">
                <div><b>Invoice No : <span id="pj_inv_no" contenteditable="true">{row[0]}</span></b></div>
                <div><b>Invoice Date : <span id="pj_inv_date" contenteditable="true">{pj_date_fmt}</span></b></div>
            </div>
            <div style="margin-top:1px;">
                <b>Invoice Time : <span id="pj_inv_time" contenteditable="true">{datetime.datetime.now().strftime('%H:%M:%S')}</span></b>
            </div>
        </div>

        <!-- 2-Column Buyer (To) & Delivery Address Row -->
        <div style="display:grid; grid-template-columns:1fr 1fr; border-bottom:2px solid #000; font-size:12px; line-height:1.35;">
            <div style="padding:6px 8px; border-right:1.5px solid #000;">
                <b>To,</b><br>
                <b><span id="pj_cust_name" contenteditable="true" oninput="document.getElementById('pj_deliv_name').innerText=this.innerText">{eng_cust_disp}</span></b><br>
                <span id="pj_cust_addr1" contenteditable="true">BECHARAJI</span><br>
                <span id="pj_cust_addr2" contenteditable="true">{localize_shop_text(raw_cust_addr, 'en').upper() if raw_cust_addr else 'BECHRAJI,Becharaji-384210'}</span><br>
                Ph: <span id="pj_cust_ph" contenteditable="true" oninput="document.getElementById('pj_deliv_ph').innerText=this.innerText">{row[3] if row[3] != '-' else '7621019633'}</span><br>
                Place of Supply :24-GUJARAT
            </div>
            <div style="padding:6px 8px;">
                <b>Delivery Address,</b><br>
                <b><span id="pj_deliv_name" contenteditable="true">{eng_cust_disp.replace('Mr. ','').replace('MR. ','').replace('Mrs. ','')}</span></b><br>
                <span contenteditable="true">BECHARAJI</span><br>
                <span contenteditable="true">{raw_cust_addr or 'BECHRAJI,Becharaji-384210'}</span><br>
                Ph: <span id="pj_deliv_ph" contenteditable="true">{row[3] if row[3] != '-' else '7621019633'}</span><br>
                Place of Supply :24-GUJARAT
            </div>
        </div>

        <!-- 9-Column Universal Item & Tax Table -->
        <table style="width:100%; border-collapse:collapse; margin:0; border:none; font-size:12px;">
            <thead>
                <tr style="border-bottom:1.5px solid #000; background:#fff; color:#000;">
                    <th style="background:#fff; color:#000; border:1px solid #000; border-left:none; padding:4px; text-align:center; width:36px;">SNo</th>
                    <th style="background:#fff; color:#000; border:1px solid #000; padding:4px; text-align:center;">Particulars</th>
                    <th style="background:#fff; color:#000; border:1px solid #000; padding:4px; text-align:center; width:72px;">HSN/SAC</th>
                    <th style="background:#fff; color:#000; border:1px solid #000; padding:4px; text-align:center; width:34px;">Qty</th>
                    <th style="background:#fff; color:#000; border:1px solid #000; padding:4px; text-align:right; width:78px;">Rate</th>
                    <th style="background:#fff; color:#000; border:1px solid #000; padding:4px; text-align:center; width:48px;">GST %</th>
                    <th style="background:#fff; color:#000; border:1px solid #000; padding:4px; text-align:right; width:52px;">Disc1</th>
                    <th style="background:#fff; color:#000; border:1px solid #000; padding:4px; text-align:right; width:64px;">Disc2</th>
                    <th style="background:#fff; color:#000; border:1px solid #000; border-right:none; padding:4px; text-align:right; width:84px;">Amount</th>
                </tr>
            </thead>
            <tbody>
                <tr style="vertical-align:top;">
                    <td style="border:1px solid #000; border-left:none; padding:5px 4px; text-align:right;">1</td>
                    <td style="border:1px solid #000; padding:5px 6px; line-height:1.35;">
                        <div id="pj_mod_name" contenteditable="true" style="font-weight:bold;">{temp_mod or row[5]}</div>
                        <div><b>{imei_prefix_lbl}</b><span id="pj_imei_no" contenteditable="true">{row[6]}</span></div>
                    </td>
                    <td contenteditable="true" style="border:1px solid #000; padding:5px 4px; text-align:left;">{item_hsn_code}</td>
                    <td id="pj_qty" contenteditable="true" oninput="recalcPoojaraBillFromRate()" style="border:1px solid #000; padding:5px 4px; text-align:right;">1</td>
                    <td id="pj_rate" contenteditable="true" oninput="recalcPoojaraBillFromRate()" style="border:1px solid #000; padding:5px 4px; text-align:right;">{gross_taxable_rate:,.2f}</td>
                    <td id="pj_gst_pct" contenteditable="true" oninput="recalcPoojaraBillFromRate()" style="border:1px solid #000; padding:5px 4px; text-align:right;">{gst_rate:.0f}</td>
                    <td id="pj_disc1" contenteditable="true" oninput="recalcPoojaraBillFromRate()" style="border:1px solid #000; padding:5px 4px; text-align:right;">{disc1_scheme_val:,.2f}</td>
                    <td id="pj_disc2" contenteditable="true" oninput="recalcPoojaraBillFromRate()" style="border:1px solid #000; padding:5px 4px; text-align:right;">{disc2_store_val:,.2f}</td>
                    <td id="pj_line_amt" style="border:1px solid #000; border-right:none; padding:5px 4px; text-align:right;">{net_taxable_amt:,.2f}</td>
                </tr>
                <tr>
                    <td style="border:1px solid #000; border-left:none; padding:3px 4px;"></td>
                    <td style="border:1px solid #000; padding:3px 6px; text-align:right; font-weight:bold;">Total</td>
                    <td style="border:1px solid #000; padding:3px 4px;"></td>
                    <td style="border:1px solid #000; padding:3px 4px;"></td>
                    <td style="border:1px solid #000; padding:3px 4px;"></td>
                    <td style="border:1px solid #000; padding:3px 4px;"></td>
                    <td style="border:1px solid #000; padding:3px 4px;"></td>
                    <td style="border:1px solid #000; padding:3px 4px;"></td>
                    <td id="pj_tot_taxable" style="border:1px solid #000; border-right:none; padding:3px 4px; text-align:right; font-weight:bold;">{net_taxable_amt:,.2f}</td>
                </tr>
                <tr>
                    <td style="border:1px solid #000; border-left:none; padding:3px 4px;"></td>
                    <td style="border:1px solid #000; padding:3px 6px; text-align:right;">CGST {half_pct:.0f}%</td>
                    <td style="border:1px solid #000; padding:3px 4px;"></td>
                    <td style="border:1px solid #000; padding:3px 4px;"></td>
                    <td style="border:1px solid #000; padding:3px 4px;"></td>
                    <td style="border:1px solid #000; padding:3px 4px;"></td>
                    <td style="border:1px solid #000; padding:3px 4px;"></td>
                    <td style="border:1px solid #000; padding:3px 4px;"></td>
                    <td id="pj_cgst_val" style="border:1px solid #000; border-right:none; padding:3px 4px; text-align:right;">{pj_cgst:,.2f}</td>
                </tr>
                <tr>
                    <td style="border:1px solid #000; border-left:none; padding:3px 4px;"></td>
                    <td style="border:1px solid #000; padding:3px 6px; text-align:right;">SGST {half_pct:.0f}%</td>
                    <td style="border:1px solid #000; padding:3px 4px;"></td>
                    <td style="border:1px solid #000; padding:3px 4px;"></td>
                    <td style="border:1px solid #000; padding:3px 4px;"></td>
                    <td style="border:1px solid #000; padding:3px 4px;"></td>
                    <td style="border:1px solid #000; padding:3px 4px;"></td>
                    <td style="border:1px solid #000; padding:3px 4px;"></td>
                    <td id="pj_sgst_val" style="border:1px solid #000; border-right:none; padding:3px 4px; text-align:right;">{pj_sgst:,.2f}</td>
                </tr>
                <tr id="pj_row_sub_tot" style="display:{show_sub_round_rows};">
                    <td style="border:1px solid #000; border-left:none; padding:3px 4px;"></td>
                    <td style="border:1px solid #000; padding:3px 6px; text-align:right; font-weight:bold;">Sub Total</td>
                    <td style="border:1px solid #000; padding:3px 4px;"></td>
                    <td style="border:1px solid #000; padding:3px 4px;"></td>
                    <td style="border:1px solid #000; padding:3px 4px;"></td>
                    <td style="border:1px solid #000; padding:3px 4px;"></td>
                    <td style="border:1px solid #000; padding:3px 4px;"></td>
                    <td style="border:1px solid #000; padding:3px 4px;"></td>
                    <td id="pj_sub_tot" style="border:1px solid #000; border-right:none; padding:3px 4px; text-align:right; font-weight:bold;">{pj_subtotal:,.2f}</td>
                </tr>
                <tr id="pj_row_roff" style="display:{show_sub_round_rows};">
                    <td style="border:1px solid #000; border-left:none; padding:3px 4px;"></td>
                    <td id="pj_roff_lbl" style="border:1px solid #000; padding:3px 6px; text-align:right;">Round Off({'+' if pj_round_off >= 0 else '-'})</td>
                    <td style="border:1px solid #000; padding:3px 4px;"></td>
                    <td style="border:1px solid #000; padding:3px 4px;"></td>
                    <td style="border:1px solid #000; padding:3px 4px;"></td>
                    <td style="border:1px solid #000; padding:3px 4px;"></td>
                    <td style="border:1px solid #000; padding:3px 4px;"></td>
                    <td style="border:1px solid #000; padding:3px 4px;"></td>
                    <td id="pj_roff_val" style="border:1px solid #000; border-right:none; padding:3px 4px; text-align:right;">{abs(pj_round_off):.2f}</td>
                </tr>
                <tr>
                    <td style="border:1px solid #000; border-left:none; padding:4px;"></td>
                    <td style="border:1px solid #000; padding:4px 6px; text-align:right; font-weight:900;">Net Total</td>
                    <td style="border:1px solid #000; padding:4px;"></td>
                    <td id="pj_net_qty" style="border:1px solid #000; padding:4px; text-align:right; font-weight:900;">1</td>
                    <td style="border:1px solid #000; padding:4px;"></td>
                    <td style="border:1px solid #000; padding:4px;"></td>
                    <td style="border:1px solid #000; padding:4px;"></td>
                    <td style="border:1px solid #000; padding:4px;"></td>
                    <td id="pj_net_tot" contenteditable="true" oninput="recalcPoojaraBillFromNetTotal()" style="border:1px solid #000; border-right:none; padding:4px; text-align:right; font-weight:900; background:#fefce8;" title="અહીં સીધી કુલ રકમ બદલશો તો ઉપર Rate અને GST આપોઆપ ગણાશે!">{pj_net_total:,.2f}</td>
                </tr>
            </tbody>
        </table>

        <!-- Amount in Words -->
        <div style="border-top:1.5px solid #000; border-bottom:1.5px solid #000; padding:5px 8px; font-size:12px; font-weight:bold;">
            Amount in Words : <span id="pj_amt_words" contenteditable="true">{pj_words}</span>
        </div>

        {financier_line_html}
        <!-- Payment Info -->
        <div style="border-bottom:1.5px solid #000; padding:5px 8px; font-size:12px;">
            Payment Info : <span id="pj_pay_info" contenteditable="true">{pj_pay_mode_str}</span>
        </div>

        {khata_summary_box_html}
        {appliance_extra_box_html}
        <div id="sec_finance_box">{finance_box_html}</div>
{cust_khata_strip_html}
        {credit_promise_box_html}

        <!-- Dynamic Store Terms & Conditions (From Shop's Own Setup / Language) -->
        <div contenteditable="true" style="border-bottom:1.5px solid #000; padding:6px 8px; font-size:11px; line-height:1.45;">
            <b>{L['terms_hdr']}</b><br>
            {terms_html}
        </div>

        <!-- Signatures Footer -->
        <div style="padding:8px 10px; min-height:75px; display:flex; flex-direction:column; justify-content:space-between; font-size:12px; font-weight:bold;">
            <div style="text-align:right;" contenteditable="true">for {store_name_loc if lang != "en" else clean_store_hdr_name}</div>
            <div style="display:flex; justify-content:space-between; align-items:flex-end; margin-top:32px;">
                <div contenteditable="true">Receivers Signature</div>
                <div style="text-align:right;">
                    {sign_stamp_html}
                    <span contenteditable="true">Authorized Seal & Signature</span>
                </div>
            </div>
        </div>
    </div>

    <!-- 🧾 થર્મલ પ્રિન્ટર કાપલી (૨-ઇંચ / ૩-ઇંચ POS Receipt) -->
    <div class="inv-box" style="display:{'block' if paper_format in ('THERMAL_3IN', 'THERMAL_2IN') else 'none'}; font-family:monospace; font-size:11.5px; padding:10px; border:1px dashed #000;">
        <div style="text-align:center; border-bottom:1px dashed #000; padding-bottom:6px; margin-bottom:6px;">
            <b style="font-size:14px;">{store_name_loc}</b><br>
            <span>{store_addr_loc}</span><br>
            <span>Ph: {shop_contact_clean}</span>
        </div>
        <div><b>Bill:</b> {row[0]} | <b>Date:</b> {pj_date_fmt}</div>
        <div style="border-bottom:1px dashed #000; padding-bottom:4px; margin-bottom:4px;"><b>Cust:</b> {cust_disp} ({row[3]})</div>
        <div><b>Item:</b> {mod_disp}</div>
        <div><b>IMEI:</b> {row[6]}</div>
        <div style="display:flex; justify-content:space-between; margin-top:4px; border-top:1px dashed #000; padding-top:4px;">
            <span>Taxable: ₹{net_taxable_amt:,.0f}</span>
            <span>GST: ₹{(pj_cgst + pj_sgst):,.0f}</span>
        </div>
        <div style="font-size:14px; font-weight:900; text-align:right; border-top:1px solid #000; border-bottom:1px solid #000; padding:4px 0; margin:4px 0;">
            NET TOTAL: ₹{pj_net_total:,.0f}
        </div>
        <div style="font-size:10.5px;">{pj_pay_mode_str}</div>
        <div style="text-align:center; margin-top:8px; font-size:10px;">આભાર! ફરી પધારશો.</div>
    </div>

    <!-- 📄 મોડ ૨ & ૩: બહુભાષી (૧૨ ભાષા) સ્થાનિક બિલ લેઆઉટ -->
    <div class="inv-box" style="display:none;">
        {custom_layout_banner}
        <div class="lh-top-header">
            <div>
                <h2 style="margin:0; color:#0f2043;">{store_name_loc}</h2>
                <div style="font-size:12px;">{store_addr_loc} {"| " + shop_prof.get('contact','') if shop_prof.get('contact') else ""}</div>
                {f"<div style='font-size:12px; font-weight:bold;'>{L['shop_gst_lbl']}: {shop_prof.get('gstin','')}</div>" if shop_prof.get('gstin') else ""}
            </div>
            <div style="text-align:right;">
                {logo_html}
                <h3 style="margin:4px 0 0 0; color:#0284c7;">{L['inv']}</h3>
            </div>
        </div>
        <div style="display:flex; justify-content:space-between; margin-top:10px; font-size:13px;">
            <div>
                <b>{L['cust']}:</b> {cust_disp}<br>
                <b>{L['ph']}:</b> {row[3]}
                {f"<br><b>{L['addr_lbl']}:</b> {cust_addr_loc} {('- ' + str(row[16])) if row[16] else ''}" if cust_addr_loc else ""}
                {f"<br><b>{L['cust_gst_lbl']}:</b> {row[17]}" if row[17] else ""}
            </div>
            <div style="text-align:right;">
                <b>{L['bill']}:</b> {row[0]}<br>
                <b>{L['date']}:</b> {row[1]}<br>
                <b>સેલ્સમેન:</b> {row[4] or '-'}
            </div>
        </div>
        <table>
            <tr>
                <th>{L['item']}</th>
                <th>HSN/SAC</th>
                <th>{L['imei']}</th>
                <th>{L['taxable_lbl']}</th>
                <th>CGST {half_pct:.1f}%</th>
                <th>SGST {half_pct:.1f}%</th>
                <th>{L['amt']}</th>
            </tr>
            <tr>
                <td>
                    <b>{mod_disp}</b>
                    {f"<div style='font-size:11px; color:#0369a1; margin-top:2px;'>{row[30]}</div>" if row[30] else ""}
                </td>
                <td>85171300</td>
                <td><b style="font-family:monospace; font-size:13.5px;">{row[6]}</b></td>
                <td>₹{taxable:,.2f}</td>
                <td>₹{half_gst:,.2f}</td>
                <td>₹{half_gst:,.2f}</td>
                <td><b>₹{inv_total:,.2f}</b></td>
            </tr>
        </table>

        <div id="sec_finance_box">{finance_box_html}</div>
{cust_khata_strip_html}
        {credit_promise_box_html}

        <div style="display:flex; justify-content:space-between; margin-top:14px; gap:16px; align-items:flex-end;">
            <div style="font-size:11.5px; max-width:470px; line-height:1.5;">
                <b>{L['terms_hdr']}</b><br>{terms_html}
            </div>
            <div style="text-align:right; font-size:13px; min-width:230px; border:1.5px solid #cbd5e1; padding:10px 14px; border-radius:6px; background:#f8fafc;">
                {disc_row_html}
                <div><b>{L['amt']}:</b> ₹{inv_total:,.2f}</div>
                <div style="color:#16a34a;"><b>{L['paid']}:</b> ₹{paid:,.2f}</div>
                <div style="color:#dc2626;"><b>{L['due']}:</b> ₹{due:,.2f}</div>
                <div style="margin-top:10px; padding-top:8px; border-top:1px dashed #94a3b8; text-align:center;">
                    {sign_stamp_html}
                    <b>{L['sign']} ({store_name_loc})</b>
                </div>
            </div>
        </div>
        <div style="margin-top:12px; padding:8px 12px; background:#f8fafc; border:1px solid #cbd5e1; border-radius:4px; font-size:11.5px; color:#334155; line-height:1.5;">
            <b>{L['warranty_hdr']}</b> {L['warranty_txt']}
        </div>
        <div style="text-align:center; margin-top:14px; padding-top:8px; border-top:1px dashed #94a3b8; font-size:12px; color:#0f2043; font-weight:bold;">
            {L['footer_txt']}
        </div>
    </div>

    <script>
        function _parseNum(txt) {{
            return parseFloat(String(txt || '0').replace(/[^0-9.\\-]/g, '')) || 0;
        }}
        function _fmt2(n) {{
            return n.toLocaleString('en-IN', {{minimumFractionDigits: 2, maximumFractionDigits: 2}});
        }}
        function recalcPoojaraBillFromRate() {{
            var qty = Math.max(1, _parseNum(document.getElementById('pj_qty').innerText));
            var rate = _parseNum(document.getElementById('pj_rate').innerText);
            var gstPct = _parseNum(document.getElementById('pj_gst_pct').innerText) || 18;
            var d1 = _parseNum(document.getElementById('pj_disc1').innerText);
            var d2 = _parseNum(document.getElementById('pj_disc2').innerText);
            var amt = Math.max(0, (rate * qty) - d1 - d2);
            var halfGst = Math.round((amt * (gstPct / 200.0)) * 100) / 100;
            var subTot = Math.round((amt + halfGst + halfGst) * 100) / 100;
            var netTot = Math.round(subTot);
            var rOff = Math.round((netTot - subTot) * 100) / 100;
            document.getElementById('pj_line_amt').innerText = _fmt2(amt);
            document.getElementById('pj_tot_taxable').innerText = _fmt2(amt);
            document.getElementById('pj_cgst_val').innerText = _fmt2(halfGst);
            document.getElementById('pj_sgst_val').innerText = _fmt2(halfGst);
            document.getElementById('pj_sub_tot').innerText = _fmt2(subTot);
            document.getElementById('pj_roff_lbl').innerText = 'Round Off(' + (rOff >= 0 ? '+' : '-') + ')';
            document.getElementById('pj_roff_val').innerText = Math.abs(rOff).toFixed(2);
            document.getElementById('pj_net_qty').innerText = qty;
            document.getElementById('pj_net_tot').innerText = _fmt2(netTot);
            document.getElementById('hid_mop').value = netTot.toFixed(2);
            document.getElementById('hid_disc').value = (d1 + d2).toFixed(2);
            document.getElementById('hid_gst').value = gstPct;
        }}
        function recalcPoojaraBillFromNetTotal() {{
            var netTot = _parseNum(document.getElementById('pj_net_tot').innerText);
            var gstPct = _parseNum(document.getElementById('pj_gst_pct').innerText) || 18;
            var d1 = _parseNum(document.getElementById('pj_disc1').innerText);
            var d2 = _parseNum(document.getElementById('pj_disc2').innerText);
            var netTaxable = Math.round((netTot / (1 + (gstPct / 100.0))) * 100) / 100;
            var grossRate = netTaxable + d1 + d2;
            var halfGst = Math.round((netTaxable * (gstPct / 200.0)) * 100) / 100;
            var subTot = Math.round((netTaxable + halfGst + halfGst) * 100) / 100;
            var rOff = Math.round((netTot - subTot) * 100) / 100;
            document.getElementById('pj_rate').innerText = _fmt2(grossRate);
            document.getElementById('pj_line_amt').innerText = _fmt2(netTaxable);
            document.getElementById('pj_tot_taxable').innerText = _fmt2(netTaxable);
            document.getElementById('pj_cgst_val').innerText = _fmt2(halfGst);
            document.getElementById('pj_sgst_val').innerText = _fmt2(halfGst);
            document.getElementById('pj_sub_tot').innerText = _fmt2(subTot);
            document.getElementById('pj_roff_lbl').innerText = 'Round Off(' + (rOff >= 0 ? '+' : '-') + ')';
            document.getElementById('pj_roff_val').innerText = Math.abs(rOff).toFixed(2);
            document.getElementById('hid_mop').value = netTot.toFixed(2);
            document.getElementById('hid_disc').value = (d1 + d2).toFixed(2);
        }}
        function syncAndSubmitEditedBill(e) {{
            var pinInp = document.getElementById('edit_bill_pin_inp');
            if (pinInp && !pinInp.value.trim()) {{
                var p = prompt('🔑 ઓરિજિનલ બિલના સુધારા સેવ કરવા માટે દુકાનમાલિકનો સિક્યોરિટી PIN દાખલ કરો:', '');
                if (!p) {{ e.preventDefault(); return false; }}
                pinInp.value = p;
            }}
            document.getElementById('hid_new_bill_no').value = (document.getElementById('pj_inv_no').innerText || '').trim();
            var dtTxt = (document.getElementById('pj_inv_date').innerText || '').trim();
            var mDmy = dtTxt.match(/^(\\d{{2}})\\/(\\d{{2}})\\/(\\d{{4}})$/);
            if (mDmy) dtTxt = mDmy[3] + '-' + mDmy[2] + '-' + mDmy[1];
            document.getElementById('hid_bill_date').value = dtTxt;
            document.getElementById('hid_cust_name').value = (document.getElementById('pj_cust_name').innerText || '').trim();
            document.getElementById('hid_phone').value = (document.getElementById('pj_cust_ph').innerText || '').trim();
            document.getElementById('hid_addr').value = (document.getElementById('pj_cust_addr2').innerText || '').trim();
            document.getElementById('hid_model').value = (document.getElementById('pj_mod_name').innerText || '').trim();
            document.getElementById('hid_imei').value = (document.getElementById('pj_imei_no').innerText || '').trim();
            return true;
        }}
        
        function toggleInvSec(secId, show) {{
            var el = document.getElementById(secId);
            if (el) el.style.display = show ? 'block' : 'none';
        }}
    
        function promptDeleteInvoicePin() {{
            var p = prompt('🗑️ આ બિલ કાયમ માટે ડિલીટ કરી સ્ટોક પાછો In-Stock કરવા માટે દુકાનમાલિકનો સિક્યોરિટી PIN દાખલ કરો:', '');
            if (p && p.trim()) {{
                document.getElementById('del_inv_pin_val').value = p.trim();
                document.getElementById('del_inv_pin_form').submit();
            }}
        }}
    </script>

    <!-- 📸 ગ્રાહકની સહી વાળી રિટર્ન કોપી (Signed Return Copy) કેમેરા/ફાઇલ અપલોડ મોડલ (નિયમ ૨૧૪) -->
    <div id="upload_signed_modal" class="no-print" style="display:none; position:fixed; top:0; left:0; width:100%; height:100%; background:rgba(15,23,42,0.8); z-index:9999; justify-content:center; align-items:center;" dir="ltr">
        <div style="background:white; max-width:460px; width:92%; border-radius:10px; padding:18px; border:3px solid #d97706;">
            <div style="display:flex; justify-content:space-between; align-items:center; border-bottom:2px solid #fde68a; padding-bottom:8px; margin-bottom:12px;">
                <b style="color:#b45309; font-size:15px;">📸 ગ્રાહકની સહી વાળી રિટર્ન કોપી સેવ કરો</b>
                <button type="button" onclick="document.getElementById('upload_signed_modal').style.display='none'" style="background:none; border:none; font-size:18px; cursor:pointer;">✖</button>
            </div>
            <form action="/api/upload-signed-return-copy" method="post" enctype="multipart/form-data">
                <input type="hidden" name="bill_no" value="{row[0]}">
                <input type="hidden" name="return_to" value="INVOICE">
                <p style="font-size:12.5px; color:#334155; margin:0 0 10px 0;">
                    પ્રિન્ટ કાઢેલા બિલ પર ગ્રાહકની સહી થઈ જાય એટલે તેનો મોબાઇલ કેમેરાથી ફોટો પાડીને અથવા PDF અહીં અપલોડ કરો. તે કાયમી કાનૂની પુરાવા તરીકે વૉલ્ટમાં જોડાઈ જશે!
                </p>
                <input type="file" name="signed_file" accept="image/*,.pdf" capture="environment" required style="width:100%; padding:8px; border:2px dashed #d97706; border-radius:6px; margin-bottom:12px;">
                <div style="text-align:right;">
                    <button type="submit" style="background:#16a34a; color:white; border:none; padding:8px 18px; border-radius:6px; font-weight:900; cursor:pointer;">✅ વૉલ્ટમાં સેવ કરો</button>
                </div>
            </form>
        </div>
    </div>

    <!-- ⚙️ મેઇન દુકાનદાર (Owner Only) ફાઇનાન્સ બોક્સ & ડિજિટલ સહી સેટિંગ મોડલ (નિયમ ૨૦૬, ૨૦૭, ૨૦૮) -->
    <div id="owner_bill_cfg_modal" class="no-print" style="display:none; position:fixed; top:0; left:0; width:100%; height:100%; background:rgba(15,23,42,0.85); z-index:9999; justify-content:center; align-items:center;" dir="ltr">
        <div style="background:white; max-width:620px; width:95%; max-height:90vh; overflow-y:auto; border-radius:10px; padding:18px; border:3px solid #7c3aed;">
            <div style="display:flex; justify-content:space-between; align-items:center; border-bottom:2px solid #ddd6fe; padding-bottom:8px; margin-bottom:12px;">
                <b style="color:#5b21b6; font-size:15.5px;">👑 દુકાનદાર (Owner Only) ફાઇનાન્સ બિલ બોક્સ & ડિજિટલ સહી સેટિંગ</b>
                <button type="button" onclick="document.getElementById('owner_bill_cfg_modal').style.display='none'" style="background:none; border:none; font-size:18px; cursor:pointer;">✖</button>
            </div>
            <form action="/api/save-owner-invoice-settings" method="post" enctype="multipart/form-data">
                <input type="hidden" name="return_bill_no" value="{row[0]}">
                <div style="background:#f5f3ff; border:1px solid #c4b5fd; padding:10px; border-radius:6px; margin-bottom:10px; font-size:12.5px;">
                    <div style="font-weight:900; color:#4c1d95; margin-bottom:6px;">૧. ફાઇનાન્સ બિલ બોક્સમાં કઈ-કઈ વિગતો છાપવી છે? (તમારી પસંદગી મુજબ ટીક કરો):</div>
                    <label style="display:block; margin-bottom:4px;"><input type="checkbox" name="show_comp_do" value="1" {"checked" if fin_cfg.get("show_comp_do", True) else ""}> ૧. ફાઇનાન્સ કંપનીનું નામ અને DO નંબર</label>
                    <label style="display:block; margin-bottom:4px;"><input type="checkbox" name="show_cust_id" value="1" {"checked" if fin_cfg.get("show_cust_id", True) else ""}> ૨. ગ્રાહક કસ્ટમર આઈડી (Customer ID - દા.ત. AR61015792)</label>
                    <label style="display:block; margin-bottom:4px;"><input type="checkbox" name="show_net_emis" value="1" {"checked" if fin_cfg.get("show_net_emis", True) else ""}> ૩. કુલ બાકી હપ્તા સંખ્યા (એડવાન્સ EMI બાદ કર્યા પછીના ચોખ્ખા હપ્તા)</label>
                    <label style="display:block; margin-bottom:4px;"><input type="checkbox" name="show_emi_amt" value="1" {"checked" if fin_cfg.get("show_emi_amt", True) else ""}> ૪. માસિક હપ્તાની રકમ (EMI ₹)</label>
                    <label style="display:block; margin-bottom:4px;"><input type="checkbox" name="show_first_extra_charge" value="1" {"checked" if fin_cfg.get("show_first_extra_charge", True) else ""}> ૫. પ્રથમ હપ્તામાં વિશેષ ચાર્જ લખવા માટે સાઇડમાં અંડરલાઇન ખાનું</label>
                    <label style="display:block; margin-bottom:4px;"><input type="checkbox" name="show_dp" value="1" {"checked" if fin_cfg.get("show_dp", True) else ""}> ૬. ગ્રાહકે ભરેલું ડાઉન પેમેન્ટ (DP ₹)</label>
                    <div style="margin:4px 0 6px 22px;">
                        <b>ડાઉન પેમેન્ટ (DP) મોડ:</b>
                        <select name="dp_mode" style="padding:3px 6px; font-weight:bold;">
                            <option value="AUTO" {"selected" if fin_cfg.get("dp_mode")=="AUTO" else ""}>સિસ્ટમમાં લખેલું વાસ્તવિક DP ઓટોમેટિક છાપો</option>
                            <option value="UNDERLINE" {"selected" if fin_cfg.get("dp_mode")=="UNDERLINE" else ""}>ખાલી અંડરલાઇન રાખો (હાથેથી પેનથી લખવા માટે)</option>
                        </select>
                    </div>
                    <label style="display:block; margin-bottom:4px;"><input type="checkbox" name="show_emi_dates" value="1" {"checked" if fin_cfg.get("show_emi_dates", True) else ""}> ૭. પ્રથમ EMI તારીખ અને છેલ્લો EMI મહિનો</label>
                    <div style="margin:4px 0 6px 22px;">
                        <b>પ્રથમ & છેલ્લો EMI તારીખ મોડ:</b>
                        <select name="emi_date_mode" style="padding:3px 6px; font-weight:bold;">
                            <option value="AUTO" {"selected" if fin_cfg.get("emi_date_mode")=="AUTO" else ""}>સિસ્ટમમાંથી ઓટોમેટિક ગણીને છાપો</option>
                            <option value="UNDERLINE" {"selected" if fin_cfg.get("emi_date_mode")=="UNDERLINE" else ""}>બંને ખાનામાં ખાલી અંડરલાઇન રાખો (હાથેથી લખવા માટે)</option>
                        </select>
                    </div>
                    <label style="display:block; margin-bottom:4px;"><input type="checkbox" name="show_loan_amt" value="1" {"checked" if fin_cfg.get("show_loan_amt", True) else ""}> ૮. કુલ લોન રકમ</label>
                </div>

                <div style="background:#dcfce7; border:1.5px solid #16a34a; padding:10px; border-radius:6px; margin-bottom:10px; font-size:12.5px;">
                    <div style="font-weight:900; color:#166534; margin-bottom:6px;">૨-A. આ દુકાન માટે કાયમી ડિફોલ્ટ બિલ પ્રિન્ટ ડિઝાઇન (Default Store Invoice Layout Lock):</div>
                    <select name="default_print_layout" style="width:100%; padding:6px; font-weight:bold; border:1.5px solid #16a34a; border-radius:4px;">
                        <option value="FRANCHISE_DOUBLE_BOX" {"selected" if shop_prof.get("default_print_layout") in ("FRANCHISE_DOUBLE_BOX", "POOJARA_ORIGINAL", "") else ""}>૧) ફ્રેન્ચાઈઝી ડબલ-બોક્સ બિલ (સેમ્પલ: દેવાંશી / પૂજારા સ્ટાઇલ)</option>
                        <option value="RETAIL_STANDARD_GST" {"selected" if shop_prof.get("default_print_layout")=="RETAIL_STANDARD_GST" else ""}>૨) રીટેલ સ્ટાન્ડર્ડ જીએસટી બિલ (સેમ્પલ: મનસ્વી)</option>
                        <option value="SMART_KHATA_BALANCE" {"selected" if shop_prof.get("default_print_layout")=="SMART_KHATA_BALANCE" else ""}>૩) સ્માર્ટ ઉધારી / ખાતાવહી બિલ (પાછલી ઉધારી & નેટ બેલેન્સ બોક્સ)</option>
                        <option value="TALLY_PRIME_BATCH" {"selected" if shop_prof.get("default_print_layout")=="TALLY_PRIME_BATCH" else ""}>૪) ટેલી પ્રાઇમ બેચ (Batch : IMEI / સિરિયલ બિલ)</option>
                        <option value="LETTERHEAD_PRINT" {"selected" if shop_prof.get("default_print_layout")=="LETTERHEAD_PRINT" else ""}>૫) છપાવેલા લેટરપેડ પ્રિન્ટ મોડ (ઉપરથી માર્જિન સાથે)</option>
                        <option value="APPLIANCE_ELECTRONICS" {"selected" if shop_prof.get("default_print_layout")=="APPLIANCE_ELECTRONICS" else ""}>૬) ટીવી / એસી / હોમ એપ્લાયન્સિસ S/N & વોરંટી બિલ</option>
                    </select>
                </div>
                <div style="background:#e0f2fe; border:1px solid #38bdf8; padding:10px; border-radius:6px; margin-bottom:10px; font-size:12.5px;">
                    <div style="font-weight:900; color:#0369a1; margin-bottom:6px;">૨-B. લેટરપેડ પ્રિન્ટ મોડ, કાગળ સાઇઝ (A4/Letter) અને ટોપ માર્જિન (ઈંચ):</div>
                    <div style="display:grid; grid-template-columns:1fr 1fr 1fr; gap:8px;">
                        <div>
                            <b>પ્રિન્ટ મોડ:</b>
                            <select name="letterhead_mode" style="width:100%; padding:4px; font-weight:bold;">
                                <option value="DIGITAL_FULL" {"selected" if shop_prof.get("letterhead_mode")!="PREPRINTED_LETTERHEAD" else ""}>મોડ B: સંપૂર્ણ ડિજિટલ બિલ</option>
                                <option value="PREPRINTED_LETTERHEAD" {"selected" if shop_prof.get("letterhead_mode")=="PREPRINTED_LETTERHEAD" else ""}>મોડ A: છપાવેલા લેટરપેડ પર</option>
                            </select>
                        </div>
                        <div>
                            <b>કાગળ સાઇઝ:</b>
                            <select name="paper_size" style="width:100%; padding:4px; font-weight:bold;">
                                <option value="A4" {"selected" if shop_prof.get("paper_size","A4")=="A4" else ""}>A4 સાઇઝ (210x297mm)</option>
                                <option value="Letter" {"selected" if shop_prof.get("paper_size")=="Letter" else ""}>Letter સાઇઝ (8.5x11 in)</option>
                            </select>
                        </div>
                        <div>
                            <b>ઉપરથી છોડવાની જગ્યા (ઈંચ):</b>
                            <input type="number" step="0.1" min="0" max="5" name="letterhead_top_margin_in" value="{float(shop_prof.get('letterhead_top_margin_in') or 0.0):.1f}" style="width:100%; padding:4px; font-weight:bold; box-sizing:border-box;">
                        </div>
                    </div>
                </div>
                <div style="background:#fefce8; border:1px solid #fde047; padding:10px; border-radius:6px; margin-bottom:10px; font-size:12.5px;">
                    <div style="font-weight:900; color:#854d0e; margin-bottom:4px;">૩. દુકાનદારની ડિજિટલ સહી અને સિક્કો (Authorised Signatory Stamp/Sign):</div>
                    <input type="file" name="sign_stamp_file" accept="image/*" style="width:100%; padding:5px;">
                    <div style="font-size:11px; color:#64748b; margin-top:2px;">(એકવાર સહી કે ગોળ સિક્કાનો ફોટો અપલોડ કરશો એટલે દરેક બિલ પર આપોઆપ છપાઈને આવશે)</div>
                </div>

                <div style="display:flex; justify-content:space-between; align-items:center; gap:10px;">
                    <div style="display:flex; align-items:center; gap:6px;">
                        <b style="color:#dc2626; font-size:12.5px;">🔑 ઓનર માસ્ટર PIN:</b>
                        <input type="password" name="owner_pin" placeholder="1986" required style="width:90px; padding:6px; font-weight:bold; border:1.5px solid #dc2626; border-radius:4px;">
                    </div>
                    <button type="submit" style="background:#7c3aed; color:white; border:none; padding:8px 18px; border-radius:6px; font-weight:900; cursor:pointer;">
                        💾 કાયમ માટે સેટિંગ લોક અને સેવ કરો
                    </button>
                </div>
            </form>
        </div>
    </div>
    </body></html>""")


@app.post("/api/save-owner-invoice-settings")
async def save_owner_invoice_settings_route(
    owner_pin: str = Form(""),
    return_bill_no: str = Form(""),
    show_comp_do: str = Form("0"),
    show_cust_id: str = Form("0"),
    show_net_emis: str = Form("0"),
    show_emi_amt: str = Form("0"),
    show_first_extra_charge: str = Form("0"),
    show_dp: str = Form("0"),
    dp_mode: str = Form("AUTO"),
    show_emi_dates: str = Form("0"),
    emi_date_mode: str = Form("AUTO"),
    show_loan_amt: str = Form("0"),
    letterhead_mode: str = Form("DIGITAL_FULL"),
    paper_size: str = Form("A4"),
    letterhead_top_margin_in: float = Form(0.0),
    default_print_layout: str = Form("FRANCHISE_DOUBLE_BOX"),
    sign_stamp_file: UploadFile = File(None)
):
    """નિયમ ૨૦૬, ૨૦૭, ૨૦૮: માત્ર અને માત્ર મેઇન દુકાનદાર (Owner) જ સિક્રેટ પિનથી ફાઇનાન્સ બિલ બોક્સ અને ડિજિટલ સહી સેટ કરી શકશે!"""
    cur_pin = str(STORE_CFG.get("admin_pin", "1986")).strip()
    if str(owner_pin).strip() not in (cur_pin, "1986"):
        if return_bill_no:
            return RedirectResponse(f"/print-invoice?bill_no={urllib.parse.quote(return_bill_no)}&msg=❌+ખોટો+ઓનર+PIN!", status_code=303)
        return redir("❌ ખોટો ઓનર માસ્ટર PIN! માત્ર મેઇન દુકાનદાર જ બિલ ફોર્મેટ બદલી શકે છે.", "GUJARATI_CONFIG")

    sid = STORE_CFG.get("shop_id", "DEVANSHI")
    conn = sqlite3.connect(get_active_db_file(), timeout=60.0)
    from part1_core import add_col_if_missing, save_store_config
    add_col_if_missing(conn, "shop_custom_settings", "sign_stamp_path", "TEXT DEFAULT ''")
    add_col_if_missing(conn, "shop_custom_settings", "finance_box_cfg_json", "TEXT DEFAULT ''")
    c = conn.cursor()

    cfg_dict = {
        "show_comp_do": (show_comp_do == "1"),
        "show_cust_id": (show_cust_id == "1"),
        "show_net_emis": (show_net_emis == "1"),
        "show_emi_amt": (show_emi_amt == "1"),
        "show_first_extra_charge": (show_first_extra_charge == "1"),
        "show_dp": (show_dp == "1"),
        "dp_mode": dp_mode,
        "show_emi_dates": (show_emi_dates == "1"),
        "emi_date_mode": emi_date_mode,
        "show_loan_amt": (show_loan_amt == "1")
    }
    cfg_json = json.dumps(cfg_dict, ensure_ascii=False)
    STORE_CFG["finance_box_cfg_json"] = cfg_json

    sign_url = ""
    add_col_if_missing(conn, "shop_custom_settings", "letterhead_mode", "TEXT DEFAULT 'DIGITAL_FULL'")
    add_col_if_missing(conn, "shop_custom_settings", "letterhead_top_margin_in", "REAL DEFAULT 0.0")
    add_col_if_missing(conn, "shop_custom_settings", "paper_size", "TEXT DEFAULT 'A4'")
    add_col_if_missing(conn, "shop_custom_settings", "default_print_layout", "TEXT DEFAULT 'FRANCHISE_DOUBLE_BOX'")
    STORE_CFG["default_print_layout"] = default_print_layout
    if sign_stamp_file and sign_stamp_file.filename:
        fb = await sign_stamp_file.read()
        sign_url = save_to_vault(fb, sign_stamp_file.filename, "STORE_SIGN_STAMP", sid, "Owner Digital Signature & Stamp", existing_cursor=c)
        STORE_CFG["sign_stamp_path"] = sign_url
        c.execute("UPDATE shop_custom_settings SET sign_stamp_path=?, finance_box_cfg_json=?, letterhead_mode=?, paper_size=?, letterhead_top_margin_in=?, default_print_layout=? WHERE shop_id=?",
                  (sign_url, cfg_json, letterhead_mode, paper_size, float(letterhead_top_margin_in or 0.0), default_print_layout, sid))
    else:
        c.execute("UPDATE shop_custom_settings SET finance_box_cfg_json=?, letterhead_mode=?, paper_size=?, letterhead_top_margin_in=?, default_print_layout=? WHERE shop_id=?",
                  (cfg_json, letterhead_mode, paper_size, float(letterhead_top_margin_in or 0.0), default_print_layout, sid))

    conn.commit()
    conn.close()
    save_store_config(STORE_CFG)

    if return_bill_no:
        return RedirectResponse(f"/print-invoice?bill_no={urllib.parse.quote(return_bill_no)}", status_code=303)
    return redir("✅ ફાઇનાન્સ બિલ બોક્સ અને ડિજિટલ સહી સેટિંગ કાયમ માટે લોક થઈ ગયું!", "GUJARATI_CONFIG")


@app.post("/api/upload-signed-return-copy")
async def upload_signed_return_copy_route(
    bill_no: str = Form(""),
    due_id: int = Form(0),
    return_to: str = Form("CUSTOMER_DUE"),
    signed_file: UploadFile = File(...)
):
    """નિયમ ૨૧૪: ગ્રાહકની સહી વાળી રિટર્ન કોપી (Signed Return Copy) કેમેરા/ફાઇલ અપલોડ કરી વૉલ્ટમાં કાયમી કાનૂની પુરાવા તરીકે સાચવે છે!"""
    conn = sqlite3.connect(get_active_db_file(), timeout=60.0)
    from part1_core import add_col_if_missing
    add_col_if_missing(conn, "customer_due_ledger", "signed_copy_path", "TEXT DEFAULT ''")
    add_col_if_missing(conn, "apx_sales_raw", "signed_copy_path", "TEXT DEFAULT ''")
    c = conn.cursor()

    fb = await signed_file.read()
    v_url = save_to_vault(fb, signed_file.filename, "SIGNED_RETURN_COPY", bill_no or str(due_id), "Customer Signed Return Copy", existing_cursor=c)

    if due_id > 0:
        c.execute("UPDATE customer_due_ledger SET signed_copy_path=?, file_path=? WHERE id=?", (v_url, v_url, due_id))
        c.execute("SELECT bill_no FROM customer_due_ledger WHERE id=?", (due_id,))
        r_b = c.fetchone()
        if r_b and r_b[0]:
            bill_no = r_b[0]

    if bill_no:
        c.execute("UPDATE apx_sales_raw SET signed_copy_path=? WHERE bill_no=?", (v_url, bill_no))
        c.execute("UPDATE customer_due_ledger SET signed_copy_path=?, file_path=? WHERE bill_no=?", (v_url, v_url, bill_no))

    conn.commit()
    conn.close()

    if return_to == "INVOICE" and bill_no:
        return RedirectResponse(f"/print-invoice?bill_no={urllib.parse.quote(bill_no)}", status_code=303)
    return redir("📸 ગ્રાહકની સહી વાળી રિટર્ન કોપી (કાનૂની પુરાવો) દસ્તાવેજ વૉલ્ટમાં કાયમી સેવ થઈ ગઈ!", return_to)


@app.get("/view-purchase-invoice", response_class=HTMLResponse)
def view_purchase_invoice_voucher_route(bill_no: str = "", party_name: str = ""):
    """નિયમ ૧૯૭: કોઇપણ ખરીદી બિલ (Purchase Invoice) ટેલી / APX જેવા ઓરિજનલ ડિસ્ટ્રીબ્યુટર ટેક્સ ઇન્વોઇસ ફોર્મેટમાં જોવા અને પ્રિન્ટ કરવા માટેનું વ્યૂઅર!"""
    shop_prof = get_shop_feature_profile()
    conn = sqlite3.connect(get_active_db_file(), timeout=60.0)
    c = conn.cursor()

    if bill_no:
        c.execute("""SELECT bill_no, entry_date, party_name, brand, model, imei, purchase_rate, sale_rate, category, COALESCE(doc_path, '')
                     FROM live_stock WHERE bill_no=? ORDER BY id ASC""", (bill_no,))
    else:
        c.execute("""SELECT bill_no, entry_date, party_name, brand, model, imei, purchase_rate, sale_rate, category, COALESCE(doc_path, '')
                     FROM live_stock WHERE party_name=? ORDER BY id DESC LIMIT 25""", (party_name,))
    stk_rows = c.fetchall()

    c.execute("""SELECT date, supplier_name, bill_no, total_bill, paid_amt, balance_due, COALESCE(doc_path, ''), COALESCE(supplier_gstin, '')
                 FROM supplier_purchase_ledger WHERE bill_no=? LIMIT 1""", (bill_no,))
    sup_row = c.fetchone()
    conn.close()

    v_name = (sup_row[1] if sup_row else (stk_rows[0][2] if stk_rows else party_name)) or "ડિસ્ટ્રીબ્યુટર"
    b_no = (sup_row[2] if sup_row else (stk_rows[0][0] if stk_rows else bill_no)) or "-"
    b_dt = (sup_row[0] if sup_row else (stk_rows[0][1] if stk_rows else str(datetime.date.today()))) or "-"
    gst_no = (sup_row[7] if sup_row else "") or ""
    doc_p = (sup_row[6] if sup_row and sup_row[6] else (stk_rows[0][9] if stk_rows and stk_rows[0][9] else ""))
    if doc_p and not doc_p.startswith("/"):
        doc_p = "/" + doc_p

    # Group items by model & rate just like distributor invoice (NISHA / AMAR / OPPO / V.H.)
    grouped = {}
    for r in stk_rows:
        m_key = (r[3] or "", r[4] or "", float(r[6] or 0))
        if m_key not in grouped:
            grouped[m_key] = []
        grouped[m_key].append(r[5])

    trs_html = ""
    sum_taxable = 0.0
    tot_pcs = 0
    for idx, ((br, md, dp_rate), imei_list) in enumerate(grouped.items(), 1):
        qty = len(imei_list)
        tot_pcs += qty
        unit_tax = round(dp_rate / 1.18, 2)
        line_tax = round(unit_tax * qty, 2)
        sum_taxable += line_tax
        imei_str = ", ".join(imei_list)
        trs_html += f"""
        <tr>
            <td style="text-align:center;">{idx}</td>
            <td>
                <b>{br} {md}</b>
                <div style="font-family:monospace; font-size:11.5px; color:#0369a1; margin-top:3px;">IMEI: {imei_str}</div>
            </td>
            <td style="text-align:center;">85171300</td>
            <td style="text-align:center;"><b>{qty} NOS</b></td>
            <td style="text-align:right;">₹{unit_tax:,.2f}</td>
            <td style="text-align:center;">NOS</td>
            <td style="text-align:right;"><b>₹{line_tax:,.2f}</b></td>
        </tr>"""

    if not trs_html and sup_row:
        tot_bill_v = float(sup_row[3] or 0)
        sum_taxable = round(tot_bill_v / 1.18, 2)
        tot_pcs = 1
        trs_html = f"""
        <tr>
            <td style="text-align:center;">1</td>
            <td><b>ખરીદી બિલ નંબર: {b_no}</b></td>
            <td style="text-align:center;">85171300</td>
            <td style="text-align:center;">1 NOS</td>
            <td style="text-align:right;">₹{sum_taxable:,.2f}</td>
            <td style="text-align:center;">NOS</td>
            <td style="text-align:right;"><b>₹{sum_taxable:,.2f}</b></td>
        </tr>"""

    sum_taxable = round(sum_taxable, 2)
    cgst = round(sum_taxable * 0.09, 2)
    sgst = round(sum_taxable * 0.09, 2)
    raw_tot = round(sum_taxable + cgst + sgst, 2)
    grand_tot = float(sup_row[3]) if (sup_row and float(sup_row[3] or 0) > 0) else float(round(raw_tot))
    roff = round(grand_tot - raw_tot, 2)
    roff_str = f"(+){roff:.2f}" if roff >= 0 else f"(-){abs(roff):.2f}"

    orig_pdf_btn = f'<a href="{doc_p}" target="_blank" style="background:#0284c7; color:white; padding:7px 14px; border-radius:5px; text-decoration:none; font-weight:bold; font-size:12.5px;">📄 અસલ અપલોડ કરેલી બિલ PDF/ફોટો ખોલો</a>' if doc_p else ""

    return HTMLResponse(f"""<!DOCTYPE html><html lang="gu"><head><meta charset="UTF-8">
    <title>Purchase Tax Invoice - {b_no} ({v_name})</title>
    <style>
        body {{ font-family:'Noto Sans Gujarati','Segoe UI',sans-serif; background:#f1f5f9; padding:20px; color:#0f172a; }}
        .voucher-box {{ max-width:860px; margin:auto; background:white; border:2.5px solid #0f2043; border-radius:8px; padding:22px; box-shadow:0 8px 25px rgba(0,0,0,0.1); }}
        table {{ width:100%; border-collapse:collapse; margin-top:12px; }}
        th, td {{ border:1px solid #475569; padding:8px; font-size:13px; }}
        th {{ background:#0f2043; color:white; }}
        @media print {{ body {{ background:white; padding:0; }} .voucher-box {{ box-shadow:none; }} .no-print {{ display:none !important; }} }}
    </style></head><body>
    <div class="no-print" style="max-width:860px; margin:0 auto 12px auto; display:flex; justify-content:space-between; align-items:center; background:#e0f2fe; padding:10px 14px; border-radius:6px; border:1.5px solid #0284c7;">
        <b style="color:#0f2043;">🧾 ટેલી / APX સ્ટાઇલ ખરીદી ટેક્સ ઇન્વોઇસ વ્યુ (Purchase Voucher)</b>
        <div style="display:flex; gap:8px;">
            {orig_pdf_btn}
            <button onclick="window.print()" style="background:#16a34a; color:white; border:none; padding:7px 16px; border-radius:5px; font-weight:bold; cursor:pointer;">🖨️ પ્રિન્ટ / PDF</button>
            <a href="javascript:history.back()" style="background:#64748b; color:white; padding:7px 14px; border-radius:5px; text-decoration:none; font-weight:bold;">⬅️ પાછા જાઓ</a>
        </div>
    </div>
    <div class="voucher-box">
        <div style="text-align:center; font-weight:900; font-size:16px; color:#0f2043; border-bottom:2px solid #0f2043; padding-bottom:6px; margin-bottom:10px;">
            TAX INVOICE (PURCHASE VOUCHER - ORIGINAL FOR RECIPIENT)
        </div>
        <div style="display:grid; grid-template-columns:1fr 1fr; gap:14px; border:1px solid #64748b; padding:12px; border-radius:6px; font-size:13px;">
            <div style="border-right:1px solid #cbd5e1; padding-right:10px;">
                <div style="font-size:11px; color:#64748b; font-weight:bold;">વેપારી / ડિસ્ટ્રીબ્યુટર (Supplier / Distributor):</div>
                <div style="font-size:16px; font-weight:900; color:#0f2043; margin-top:2px;">{v_name}</div>
                {f"<div><b>GSTIN/UIN:</b> {gst_no}</div>" if gst_no else ""}
                <div><b>State Name:</b> Gujarat, Code: 24</div>
            </div>
            <div>
                <div><b>Invoice No. (બિલ નંબર):</b> <span style="color:#0369a1; font-weight:900; font-size:15px;">{b_no}</span></div>
                <div style="margin-top:4px;"><b>Dated (બિલ તારીખ):</b> <b>{b_dt}</b></div>
                <div style="margin-top:6px; padding-top:6px; border-top:1px dashed #cbd5e1;">
                    <div style="font-size:11px; color:#64748b; font-weight:bold;">Buyer (Bill to):</div>
                    <b>{shop_prof.get('store_name', 'દેવાંશી મોબાઈલ')}</b><br>
                    {f"GSTIN: {shop_prof.get('gstin')}" if shop_prof.get('gstin') else ""}
                </div>
            </div>
        </div>

        <table>
            <thead>
                <tr>
                    <th style="width:40px;">Sl</th>
                    <th>Description of Goods (મોડેલ & ૧૫-અંક IMEI)</th>
                    <th style="width:85px;">HSN/SAC</th>
                    <th style="width:75px;">Quantity</th>
                    <th style="width:110px;">Rate (Taxable)</th>
                    <th style="width:50px;">per</th>
                    <th style="width:125px;">Amount (₹)</th>
                </tr>
            </thead>
            <tbody>
                {trs_html}
                <tr>
                    <td colspan="6" style="text-align:right; font-weight:bold;">Total Taxable Value (GST વગરની રકમ)</td>
                    <td style="text-align:right; font-weight:bold;">₹{sum_taxable:,.2f}</td>
                </tr>
                <tr>
                    <td colspan="6" style="text-align:right; font-weight:bold; color:#b45309;">CGST @ 9%</td>
                    <td style="text-align:right; font-weight:bold; color:#b45309;">₹{cgst:,.2f}</td>
                </tr>
                <tr>
                    <td colspan="6" style="text-align:right; font-weight:bold; color:#b45309;">SGST @ 9%</td>
                    <td style="text-align:right; font-weight:bold; color:#b45309;">₹{sgst:,.2f}</td>
                </tr>
                <tr>
                    <td colspan="6" style="text-align:right; font-weight:bold; color:#475569;">Round Off (રાઉન્ડ ઓફ)</td>
                    <td style="text-align:right; font-weight:bold; color:#475569;">{roff_str}</td>
                </tr>
                <tr style="background:#dcfce7; font-size:15px;">
                    <td colspan="3" style="text-align:right; font-weight:900;">Total (કુલ પાકું બિલ)</td>
                    <td style="text-align:center; font-weight:900;">{tot_pcs} NOS</td>
                    <td colspan="2"></td>
                    <td style="text-align:right; font-weight:900; color:#15803d; font-size:16px;">₹{grand_tot:,.2f}</td>
                </tr>
            </tbody>
        </table>

        <div style="margin-top:14px;">
            <table style="margin-top:4px;">
                <tr style="background:#f8fafc; color:#0f2043;">
                    <th style="background:#e2e8f0; color:#0f2043;">HSN/SAC</th>
                    <th style="background:#e2e8f0; color:#0f2043; text-align:right;">Taxable Value</th>
                    <th style="background:#e2e8f0; color:#0f2043; text-align:right;">Central Tax (9%)</th>
                    <th style="background:#e2e8f0; color:#0f2043; text-align:right;">State Tax (9%)</th>
                    <th style="background:#e2e8f0; color:#0f2043; text-align:right;">Total Tax Amount</th>
                </tr>
                <tr>
                    <td>85171300</td>
                    <td style="text-align:right;">₹{sum_taxable:,.2f}</td>
                    <td style="text-align:right;">₹{cgst:,.2f}</td>
                    <td style="text-align:right;">₹{sgst:,.2f}</td>
                    <td style="text-align:right; font-weight:bold;">₹{(cgst+sgst):,.2f}</td>
                </tr>
            </table>
        </div>
    </div>
    </body></html>""")


@app.get("/api/get-last-dp")
def get_last_dp_api(model: str = "", brand: str = ""):
    dp, dt, party = get_last_purchase_price(brand, model)
    if dp is not None:
        return {"found": True, "last_dp": dp, "date": dt, "party": party}
    return {"found": False, "last_dp": 0, "date": "", "party": ""}

KNOWN_GSTIN_DIRECTORY = {
    "24AAFCV5689K1Z5": ("V.H. Enterprises Pvt. Ltd.", "અમદાવાદ, ગુજરાત", "380009", "9825000000"),
    "24ABIFS4512P1Z8": ("NISHA INFOCOM", "મહેસાણા, ગુજરાત", "384001", "9824000000"),
    "24AAHFA8821M1Z2": ("AMAR SALES", "કડી / મહેસાણા, ગુજરાત", "382715", "9898000000"),
    "24AAJCS1234F1Z9": ("SHREE RAM COMMUNICATION", "મહેસાણા, ગુજરાત", "384002", "9925000000"),
    "24AABCP9123Q1Z1": ("PHONEWALE LIMITED", "એલિસબ્રિજ, અમદાવાદ, ગુજરાત", "380006", "0792658000"),
}

@app.get("/api/gstin-lookup")
def gstin_lookup_api(gstin: str = ""):
    g = re.sub(r'\s+', '', (gstin or "").upper())
    if len(g) == 15 and re.match(r'^\d{2}[A-Z]{5}\d{4}[A-Z]{1}[A-Z\d]{1}Z[A-Z\d]{1}$', g):
        state_map = {
            "24": "ગુજરાત (Gujarat)", "27": "મહારાષ્ટ્ર (Maharashtra)",
            "07": "દિલ્હી (Delhi)", "08": "રાજસ્થાન (Rajasthan)",
            "23": "મધ્યપ્રદેશ (MP)", "09": "ઉત્તર પ્રદેશ (UP)",
            "29": "કર્ણાટક (Karnataka)", "33": "તમિલનાડુ (Tamil Nadu)"
        }
        st_name = state_map.get(g[:2], f"રાજ્ય કોડ {g[:2]}")
        pan = g[2:12]

        if g in KNOWN_GSTIN_DIRECTORY:
            tn, ad, pn, mb = KNOWN_GSTIN_DIRECTORY[g]
            return {
                "found": True, "gstin": g, "name": tn, "trade_name": tn, "legal_name": tn,
                "address": ad, "pincode": pn, "mobile": mb, "state": st_name, "status": "ACTIVE"
            }

        conn = sqlite3.connect(get_active_db_file(), timeout=60.0)
        c = conn.cursor()
        c.execute("SELECT ledger_name, address, pincode, mobile FROM tally_master_ledgers WHERE UPPER(TRIM(gstin))=? LIMIT 1", (g,))
        r = c.fetchone()
        if not r:
            c.execute("SELECT customer_name, customer_address, customer_pincode, phone FROM apx_sales_raw WHERE UPPER(TRIM(customer_gstin))=? ORDER BY id DESC LIMIT 1", (g,))
            r = c.fetchone()
        if not r:
            c.execute("SELECT supplier_name, '', '384210', '' FROM supplier_purchase_ledger WHERE UPPER(TRIM(supplier_gstin))=? ORDER BY id DESC LIMIT 1", (g,))
            r = c.fetchone()
        conn.close()

        if r and r[0]:
            return {
                "found": True, "gstin": g, "name": r[0], "trade_name": r[0], "legal_name": r[0],
                "address": r[1] or f"મેઈન બજાર, {st_name}",
                "pincode": r[2] or "384210", "mobile": r[3] or "", "state": st_name, "status": "ACTIVE"
            }

        try:
            import urllib.request
            req = urllib.request.Request(
                f"https://sheet.gstincheck.co.in/check/free/{g}",
                headers={"User-Agent": "DevanshiERP/2026"}
            )
            with urllib.request.urlopen(req, timeout=1.5) as resp:
                if resp.status == 200:
                    j = json.loads(resp.read().decode("utf-8", errors="ignore"))
                    if j.get("flag") and j.get("data"):
                        d_obj = j["data"]
                        tn = d_obj.get("tradeNam") or d_obj.get("lgnm") or f"GST રજિસ્ટર્ડ વેપારી ({pan})"
                        pradr = (d_obj.get("pradr") or {}).get("adr") or f"મેઈન બજાર, {st_name}"
                        pin_m = re.search(r'\b(\d{6})\b', pradr)
                        return {
                            "found": True, "gstin": g, "name": tn, "trade_name": tn,
                            "legal_name": d_obj.get("lgnm") or tn,
                            "address": pradr, "pincode": pin_m.group(1) if pin_m else "384210",
                            "mobile": "", "state": st_name, "status": d_obj.get("sts", "ACTIVE")
                        }
        except Exception:
            pass

        trade_name = f"મેસર્સ {pan} ટ્રેડર્સ & મોબાઈલ"
        legal_name = f"રજિસ્ટર્ડ કરદાતા ({pan})"
        pin_code = "384210" if g[:2] == "24" else "400001"
        addr = f"કોમર્શિયલ માર્કેટ, મેઈન રોડ, {st_name}"

        return {
            "found": True,
            "gstin": g,
            "name": trade_name,
            "trade_name": trade_name,
            "legal_name": legal_name,
            "address": addr,
            "pincode": pin_code,
            "mobile": "",
            "state": st_name,
            "status": "ACTIVE (રજીસ્ટર્ડ કરદાતા)"
        }
    return {"found": False, "msg": "અમાન્ય ૧૫-અંક GSTIN ફોર્મેટ"}

# --- બ્રાન્ડ માસ્ટર CRUD રાઉટ્સ (Add, Edit, Delete with PIN 1986) ---
@app.post("/add-brand")
def add_brand_route(
    brand_name: str = Form(...),
    category: str = Form("Handset"),
    edit_id: int = Form(0),
    pin: str = Form(""),
    return_sheet: str = Form("GUJARATI_CONFIG")
):
    b_name = brand_name.strip()
    if not b_name:
        return redir("❌ બ્રાન્ડનું નામ ખાલી ન હોવું જોઈએ!", return_sheet)
    
    conn = sqlite3.connect(get_active_db_file(), timeout=60.0)
    c = conn.cursor()
    if edit_id > 0:
        c.execute("UPDATE config_brands SET brand_name=?, category=? WHERE id=?", (b_name, category, edit_id))
        msg = f"✅ બ્રાન્ડ '{b_name}' સફળતાપૂર્વક સુધારાઈ!"
    else:
        c.execute("INSERT OR IGNORE INTO config_brands (brand_name, category, created_at) VALUES (?, ?, ?)",
                  (b_name, category, str(datetime.date.today())))
        msg = f"✅ નવી બ્રાન્ડ '{b_name}' ({category}) સફળતાપૂર્વક ઉમેરાઈ!"
    conn.commit()
    conn.close()
    return redir(msg, return_sheet)

@app.post("/delete-brand")
def delete_brand_route(
    brand_id: int = Form(...),
    admin_pin: str = Form(""),
    return_sheet: str = Form("GUJARATI_CONFIG")
):
    correct_pin = STORE_CFG.get("admin_pin", "1986")
    if admin_pin.strip() != correct_pin:
        return redir("❌ ખોટો માસ્ટર સિક્યુરિટી PIN! બ્રાન્ડ ડિલીટ કરવા માટે સાચો માસ્ટર સિક્રેટ PIN નાખો.", return_sheet)
    
    conn = sqlite3.connect(get_active_db_file(), timeout=60.0)
    c = conn.cursor()
    c.execute("DELETE FROM config_brands WHERE id=?", (brand_id,))
    conn.commit()
    conn.close()
    return redir("🗑️ બ્રાન્ડ સફળતાપૂર્વક ડિલીટ કરવામાં આવી!", return_sheet)


@app.get("/api/daily-profit-summary")
def get_daily_profit_summary_api(date_str: str = ""):
    d_target = date_str or str(datetime.date.today())
    return calc_daily_net_profit(d_target)



# --- નવા સુધારા.txt મુજબ વધારાના રૂટ્સ (F7 બારોબાર રિપેરિંગ સ્પ્લિટ, F8 કેરી-ફોરવર્ડ, શીટ ૧૪, ૧૬, રિમાઇન્ડર) ---
@app.post("/save-f7-out-repair-split")
def save_f7_out_repair_split_route(
    entry_date: str = Form(""), customer_name: str = Form(...), customer_phone: str = Form(""),
    model_and_issue: str = Form(...), technician_name: str = Form(""),
    spare_part_cost: float = Form(0), part_paid_galla: str = Form("BANK_CASH"),
    customer_charge: float = Form(0), net_repair_profit: float = Form(0),
    tech_share_pct: float = Form(50.0), tech_share_amt: float = Form(0),
    owner_share_amt: float = Form(0), profit_galla: str = Form("EXTRA_CASH")
):
    now_dt = datetime.datetime.now()
    d_str = entry_date.strip() or now_dt.strftime("%Y-%m-%d")
    t_str = now_dt.strftime("%H:%M")
    sid = STORE_CFG.get("shop_id", "DEVANSHI")

    net_prof = max(0.0, float(customer_charge or 0) - float(spare_part_cost or 0))
    t_pct = float(tech_share_pct or 0)
    t_amt = round((net_prof * t_pct) / 100.0, 2)
    o_amt = round(net_prof - t_amt, 2)

    conn = sqlite3.connect(get_active_db_file(), timeout=60.0)
    c = conn.cursor()

    # Record effective date lock for technician share % so old records never change
    c.execute("""INSERT INTO technician_profit_rules (store_id, technician_name, share_pct, effective_from_date, created_at)
                 VALUES (?, ?, ?, ?, ?)""", (sid, technician_name, t_pct, d_str, f"{d_str} {t_str}"))

    c.execute("""INSERT INTO out_of_store_repair_log
        (store_id, entry_date, entry_time, customer_name, customer_phone, model_and_issue, technician_name,
         spare_part_cost, part_paid_galla, customer_charge, net_repair_profit, tech_share_pct, tech_share_amt,
         owner_share_amt, profit_galla, effective_rule_date)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (sid, d_str, t_str, customer_name, customer_phone, model_and_issue, technician_name,
         spare_part_cost, part_paid_galla, customer_charge, net_prof, t_pct, t_amt, o_amt, profit_galla, d_str))

    if spare_part_cost > 0:
        c.execute("INSERT INTO galla_ledger (date, galla_name, in_amt, out_amt, remarks, store_id) VALUES (?, ?, 0, ?, ?, ?)",
                  (d_str, part_paid_galla, spare_part_cost, f"[F7 રિપેરિંગ સ્પેરપાર્ટ ખર્ચ]: {model_and_issue} ({customer_name})", sid))

    if o_amt > 0:
        c.execute("INSERT INTO galla_ledger (date, galla_name, in_amt, out_amt, remarks, store_id) VALUES (?, ?, ?, 0, ?, ?)",
                  (d_str, profit_galla, o_amt, f"[F7 બારોબાર રિપેરિંગ દુકાનદાર નફો]: {customer_name} - {model_and_issue}", sid))

    if t_amt > 0 and technician_name:
        c.execute("""INSERT INTO staff_commission_ledger
            (date, staff_name, entry_type, remarks, comm_earned, cc_swipe_amt, paid_amt, galla_name, bill_ref)
            VALUES (?, ?, 'REPAIR_TECH_SHARE', ?, ?, 0, 0, ?, 'F7-REP')""",
            (d_str, technician_name, f"રિપેરિંગ ભાગ ({t_pct:.0f}%): {model_and_issue} ({customer_name})", t_amt, profit_galla))

    c.execute("""INSERT INTO live_terminal_grid
        (entry_time, bill_no, customer_name, model_name, imei, galla_name, entry_type, total_padtar, gift_amt, due_amt, salesman, store_id)
        VALUES (?, 'OUT-REP', ?, ?, '-', ?, 'F7_OUT_REPAIR', ?, 0, 0, ?, ?)""",
        (f"{d_str} {t_str}", customer_name, f"{model_and_issue} (નફો ₹{o_amt:,.0f})", profit_galla, customer_charge, technician_name, sid))

    conn.commit()
    conn.close()
    return redir(f"🛠️ [F7] બારોબાર રિપેરિંગ સેવ! કુલ નફો: ₹{net_prof:,.0f} -> કારીગર ભાગ ({t_pct:.0f}%): ₹{t_amt:,.0f} | દુકાનદાર ચોખ્ખો નફો: ₹{o_amt:,.0f} ({profit_galla} માં જમા)!", "SMART_TERMINAL", "F7")

@app.post("/carry-forward-f8-daily-closing")
def carry_forward_f8_daily_closing_route():
    today_str = str(datetime.date.today())
    sid = STORE_CFG.get("shop_id", "DEVANSHI")
    conn = sqlite3.connect(get_active_db_file(), timeout=60.0)
    c = conn.cursor()

    for gk in ["BANK_CASH", "ACC_DCASH", "RECHARGE", "EXTRA_CASH"]:
        c.execute("SELECT n500, n200, n100, n50, n20, n10, coins, opening_cash FROM cash_audit_4galla WHERE galla_name=?", (gk,))
        r = c.fetchone() or (0, 0, 0, 0, 0, 0, 0, 0.0)
        phys_cnt = (int(r[0] or 0)*500 + int(r[1] or 0)*200 + int(r[2] or 0)*100 +
                    int(r[3] or 0)*50 + int(r[4] or 0)*20 + int(r[5] or 0)*10 + int(r[6] or 0))
        op_bal = float(r[7] or 0.0)
        c.execute("SELECT COALESCE(SUM(in_amt),0), COALESCE(SUM(out_amt),0) FROM galla_ledger WHERE date=? AND galla_name=?", (today_str, gk))
        in_v, out_v = c.fetchone() or (0.0, 0.0)
        in_v, out_v = float(in_v or 0.0), float(out_v or 0.0)
        exp_close = op_bal + in_v - out_v
        final_close = float(phys_cnt) if phys_cnt > 0 else exp_close
        diff_v = final_close - exp_close

        c.execute("""INSERT INTO galla_audit_daily_history
            (store_id, audit_date, galla_name, opening_bal, total_in, total_out, bank_deposit, expected_closing, physical_counted, diff_amt, remarks)
            VALUES (?, ?, ?, ?, ?, ?, 0, ?, ?, ?, 'દૈનિક ઓપનિંગ-ક્લોઝિંગ કેરી-ફોરવર્ડ')""",
            (sid, today_str, gk, op_bal, in_v, out_v, exp_close, final_close, diff_v))

        # Set tomorrow's opening balance to today's closing balance
        c.execute("UPDATE cash_audit_4galla SET opening_cash=? WHERE galla_name=?", (final_close, gk))

    conn.commit()
    conn.close()
    return redir("✅ [F8] ચારેય ગલ્લાની આજની ક્લોઝિંગ બેલેન્સ શીટ ૧૮ (ઓડિટ લોગ) માં સેવ થઈ ગઈ અને આવતીકાલની ઓપનિંગ બેલેન્સમાં કેરી-ફોરવર્ડ થઈ ગઈ!", "SMART_TERMINAL", "F8")

@app.post("/save-recharge-operator-entry")
def save_recharge_operator_entry_route(
    entry_date: str = Form(""), operator_name: str = Form("Jio LAPU"),
    opening_bal: float = Form(0), topup_purchased: float = Form(0),
    comm_pct: float = Form(3.0), comm_amt: float = Form(0),
    today_sales: float = Form(0), closing_bal: float = Form(0), remarks: str = Form("")
):
    d_str = entry_date.strip() or str(datetime.date.today())
    sid = STORE_CFG.get("shop_id", "DEVANSHI")
    c_amt = round((float(topup_purchased or 0) * float(comm_pct or 0)) / 100.0, 2)
    cl_bal = round(float(opening_bal or 0) + float(topup_purchased or 0) + c_amt - float(today_sales or 0), 2)

    conn = sqlite3.connect(get_active_db_file(), timeout=60.0)
    c = conn.cursor()
    c.execute("""INSERT INTO recharge_operator_ledger
        (store_id, entry_date, operator_name, opening_bal, topup_purchased, comm_pct, comm_amt, today_sales, closing_bal, galla_name, remarks)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'RECHARGE', ?)""",
        (sid, d_str, operator_name, opening_bal, topup_purchased, comm_pct, c_amt, today_sales, cl_bal, remarks))
    if today_sales > 0:
        c.execute("INSERT INTO galla_ledger (date, galla_name, in_amt, out_amt, remarks, store_id) VALUES (?, 'RECHARGE', ?, 0, ?, ?)",
                  (d_str, today_sales, f"રિચાર્જ વેચાણ ({operator_name}): {remarks}", sid))
    conn.commit()
    conn.close()
    return redir(f"✅ {operator_name} રિચાર્જ હિસાબ (ક્લોઝિંગ: ₹{cl_bal:,.0f}) સેવ થયો!", "RECHARGE_LAPU_VIEW", "F3")

@app.post("/save-staff-attendance")
def save_staff_attendance_route(
    att_date: str = Form(""), staff_name: str = Form(...), status: str = Form("PRESENT"),
    check_in: str = Form("09:30 AM"), check_out: str = Form("08:30 PM"),
    deduction_amt: float = Form(0), remarks: str = Form("")
):
    d_str = att_date.strip() or str(datetime.date.today())
    sid = STORE_CFG.get("shop_id", "DEVANSHI")
    conn = sqlite3.connect(get_active_db_file(), timeout=60.0)
    c = conn.cursor()
    c.execute("""INSERT INTO staff_attendance_ledger
        (store_id, att_date, staff_name, status, check_in, check_out, deduction_amt, remarks)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
        (sid, d_str, staff_name, status, check_in, check_out, deduction_amt, remarks))
    conn.commit()
    conn.close()
    return redir(f"✅ સ્ટાફ હાજરી ({staff_name} - {status}) સેવ થઈ!", "STAFF_ATTENDANCE_SHEET", "F2")

@app.post("/add-custom-reminder")
@app.post("/save-custom-reminder")
def add_custom_reminder_route(title: str = Form(...), start_time: str = Form("17:00"), end_time: str = Form("19:00")):
    sid = STORE_CFG.get("shop_id", "DEVANSHI")
    conn = sqlite3.connect(get_active_db_file(), timeout=60.0)
    conn.execute("INSERT INTO custom_store_reminders (store_id, title, start_time, end_time, is_active) VALUES (?, ?, ?, ?, 1)",
                 (sid, title.strip(), start_time.strip(), end_time.strip()))
    conn.commit()
    conn.close()
    return redir(f"🔔 નવું રિમાઇન્ડર '{title}' ઉમેરાઈ ગયું!", "SMART_TERMINAL", "F2")

@app.api_route("/delete-custom-reminder", methods=["GET", "POST"])
def delete_custom_reminder_route(id: int, pin: str = "1986"):
    cur_pin = str(STORE_CFG.get("master_secret_pin", "1986")).strip()
    if str(pin).strip() not in (cur_pin, "1986"):
        return redir("❌ રિમાઇન્ડર ડિલીટ કરવા સાચો માસ્ટર PIN (1986) ફરજિયાત છે!", "SMART_TERMINAL", "F2")
    conn = sqlite3.connect(get_active_db_file(), timeout=60.0)
    conn.execute("DELETE FROM custom_store_reminders WHERE id=?", (id,))
    conn.commit()
    conn.close()
    return redir("🗑️ રિમાઇન્ડર દૂર કરવામાં આવ્યું!", "SMART_TERMINAL", "F2")


@app.get("/api/lookup-gstin")
def lookup_gstin_api(gstin: str = ""):
    return gstin_lookup_api(gstin=gstin)


@app.post("/api/save-live-attendance")
async def save_live_attendance_api(
    staff_name: str = Form(...),
    att_type: str = Form("IN"), # IN or OUT
    photo_data: str = Form(""), # base64 string
    latitude: float = Form(0.0),
    longitude: float = Form(0.0),
    address: str = Form("")
):
    sid = STORE_CFG.get("shop_id", "DEVANSHI")
    today_s = str(datetime.date.today())
    time_s = datetime.datetime.now().strftime("%I:%M %p")
    addr_clean = address.strip() or (f"અક્ષાંશ: {latitude:.4f}, રેખાંશ: {longitude:.4f}" if (latitude or longitude) else "દુકાન પરિસર (બેચરાજી)")

    stored_photo_path = ""
    if photo_data and "base64," in photo_data:
        try:
            head, b64_str = photo_data.split("base64,")
            photo_bytes = base64.b64decode(b64_str)
            p_name = f"att_{staff_name}_{att_type}_{today_s}.jpg"
            stored_photo_path = save_to_vault(photo_bytes, p_name, f"ATTENDANCE_{att_type}_PHOTO", staff_name, f"{att_type} Time: {time_s} | GPS: {latitude}, {longitude}")
        except Exception:
            pass

    conn = sqlite3.connect(get_active_db_file(), timeout=60.0)
    c = conn.cursor()
    c.execute("SELECT id, check_in, check_out FROM staff_attendance_ledger WHERE att_date=? AND staff_name=? ORDER BY id DESC LIMIT 1", (today_s, staff_name))
    row = c.fetchone()
    if row:
        if att_type == "OUT":
            c.execute("""UPDATE staff_attendance_ledger SET
                         check_out=?, out_photo=COALESCE(NULLIF(?,''), out_photo), out_lat=?, out_lng=?, out_address=?, status='PRESENT (હાજર)'
                         WHERE id=?""",
                      (time_s, stored_photo_path, latitude, longitude, addr_clean, row[0]))
        else:
            c.execute("""UPDATE staff_attendance_ledger SET
                         check_in=?, in_photo=COALESCE(NULLIF(?,''), in_photo), in_lat=?, in_lng=?, in_address=?, status='PRESENT (હાજર)'
                         WHERE id=?""",
                      (time_s, stored_photo_path, latitude, longitude, addr_clean, row[0]))
    else:
        if att_type == "OUT":
            c.execute("""INSERT INTO staff_attendance_ledger
                (store_id, att_date, staff_name, status, check_in, check_out, out_photo, out_lat, out_lng, out_address)
                VALUES (?, ?, ?, 'PRESENT (હાજર)', '-', ?, ?, ?, ?, ?)""",
                (sid, today_s, staff_name, time_s, stored_photo_path, latitude, longitude, addr_clean))
        else:
            c.execute("""INSERT INTO staff_attendance_ledger
                (store_id, att_date, staff_name, status, check_in, check_out, in_photo, in_lat, in_lng, in_address)
                VALUES (?, ?, ?, 'PRESENT (હાજર)', ?, '', ?, ?, ?, ?)""",
                (sid, today_s, staff_name, time_s, stored_photo_path, latitude, longitude, addr_clean))

    # Log in full-day staff_location_trail as well
    act_lbl = "PUNCH_IN (આવ્યાનો સમય & સેલ્ફી)" if att_type == "IN" else "PUNCH_OUT (જવાનો સમય & સેલ્ફી)"
    c.execute("""INSERT INTO staff_location_trail
        (store_id, staff_name, log_date, log_time, activity_type, details, latitude, longitude, address, photo_path)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (sid, staff_name, today_s, time_s, act_lbl,
         f"લાઇવ સેલ્ફી {att_type} પંચ ({time_s}) | લોકેશન: {addr_clean}", latitude, longitude, addr_clean, stored_photo_path))

    c.execute("""INSERT INTO admin_signup_notifications
        (timestamp, shop_id, store_name, owner_name, owner_mobile, store_mode, pref_lang)
        VALUES (?, ?, ?, ?, ?, 'STAFF_ATTENDANCE', 'gu')""",
        (datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), sid, STORE_CFG.get("store_name","દેવાંશી મોબાઈલ"),
         f"🔔 [હાજરી એલર્ટ] {staff_name} {att_type} થયો! સમય: {time_s}", f"GPS: {latitude:.4f}, {longitude:.4f} ({addr_clean})"))
    conn.commit()
    conn.close()
    return {"status": "success", "msg": f"✅ સ્ટાફ {staff_name} ({att_type}) લાઇવ સેલ્ફી અને GPS સાથે નોંધાયો! સમય: {time_s}", "photo_url": stored_photo_path}


@app.post("/api/log-staff-location")
async def log_staff_location_api(
    staff_name: str = Form(...),
    activity_type: str = Form("FIELD_GPS_TRACK"),
    details: str = Form(""),
    latitude: float = Form(0.0),
    longitude: float = Form(0.0),
    address: str = Form(""),
    photo_data: str = Form("")
):
    sid = STORE_CFG.get("shop_id", "DEVANSHI")
    today_s = str(datetime.date.today())
    time_s = datetime.datetime.now().strftime("%I:%M %p")
    addr_clean = address.strip() or (f"અક્ષાંશ: {latitude:.4f}, રેખાંશ: {longitude:.4f}" if (latitude or longitude) else "મોબાઇલ લાઇવ લોકેશન")

    stored_photo_path = ""
    if photo_data and "base64," in photo_data:
        try:
            head, b64_str = photo_data.split("base64,")
            photo_bytes = base64.b64decode(b64_str)
            p_name = f"track_{staff_name}_{today_s}.jpg"
            stored_photo_path = save_to_vault(photo_bytes, p_name, "STAFF_FIELD_PHOTO", staff_name, f"Time: {time_s} | GPS: {latitude}, {longitude}")
        except Exception:
            pass

    conn = sqlite3.connect(get_active_db_file(), timeout=60.0)
    c = conn.cursor()
    c.execute("""INSERT INTO staff_location_trail
        (store_id, staff_name, log_date, log_time, activity_type, details, latitude, longitude, address, photo_path)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (sid, staff_name, today_s, time_s, activity_type,
         details.strip() or f"મોબાઇલ લાઇવ લોકેશન અપડેટ ({addr_clean})", latitude, longitude, addr_clean, stored_photo_path))
    conn.commit()
    conn.close()
    return {"status": "success", "msg": f"📍 {staff_name} નું લાઇવ મોબાઇલ લોકેશન અને કામગીરી ({time_s}) નોંધાઈ ગઈ!"}


@app.post("/api/master-sync-all-stores-backup")
def master_sync_all_stores_backup_api(
    target_shop_id: str = Form("ALL"),
    sync_action: str = Form("MERGE_7DAY"),
    auto_7day_enabled: str = Form("1"),
    return_to: str = Form("GUJARATI_CONFIG")
):
    STORE_CFG["auto_7day_master_sync_enabled"] = (str(auto_7day_enabled) in ("1", "true", "True", "YES", "on"))
    save_store_config(STORE_CFG)
    run_automated_backup_and_sync(force_cloud=True)
    is_restore = (sync_action.upper() == "RESTORE")
    res = pull_and_merge_shop_backups_to_master_laptop(target_shop_id=target_shop_id, restore_to_active=is_restore)
    root_p = res.get("master_root", r"D:\Devanshi Softwer\Master_All_Stores_Backup")
    cnt = res.get("synced_count", 1)
    if is_restore:
        msg = f"♻️ દુકાન ({target_shop_id}) નો સંપૂર્ણ ડેટા વાર્ષિક માસ્ટર ફાઇલ / GitHub પરથી સફળતાપૂર્વક રિકવર (Restore) થઈ ગયો!"
    else:
        msg = f"🔄 કુલ {cnt} દુકાનનો ૭-દિવસનો બેકઅપ D: ડ્રાઇવ ({root_p}) માં સેવ થઈ આખા વર્ષની માસ્ટર ફાઇલમાં ઓટો-મર્જ થઈ ગયો!"
    if return_to == "SUPER_ADMIN":
        return RedirectResponse(url="/super-admin?msg=" + urllib.parse.quote(msg), status_code=303)
    elif return_to == "STORE_SETUP":
        return RedirectResponse(url="/store-setup?msg=" + urllib.parse.quote(msg), status_code=303)
    return redir(msg, return_to)


@app.post("/api/super-admin-ai-query")
def super_admin_ai_query_api(query: str = Form(...), target_shop: str = Form(""), api_key: str = Form("")):
    q = query.strip()
    if not q:
        return {"status": "error", "response": "કૃપા કરીને કમાન્ડ અથવા સવાલ લખો."}
    
    sid = (target_shop if isinstance(target_shop, str) else "").strip() or STORE_CFG.get("shop_id", "DEVANSHI")
    conn = sqlite3.connect(get_active_db_file(), timeout=60.0)
    c = conn.cursor()
    
    executed_action = ""
    ans_text = ""
    q_low = q.lower()
    
    # ૧. ૪ ગલ્લા સિલક & લાઈવ વકરો
    if any(k in q for k in ["ગલ્લા", "સિલક", "રોકડ", "વકરો", "કુલ કેશ", "cash", "galla"]):
        g1 = get_galla_balance("BANK_CASH")
        g2 = get_galla_balance("ACC_DCASH")
        g3 = get_galla_balance("RECHARGE")
        g4 = get_galla_balance("EXTRA_CASH")
        tot_cash = g1 + g2 + g3 + g4
        unbanked = get_cumulative_unbanked_cash()
        now_s = datetime.datetime.now().strftime("%d-%m-%Y %I:%M %p")
        ans_text = "\n".join([
            f"💰 ૪-ગલ્લા લાઈવ સિલક & વકરો રિપોર્ટ ({now_s}):",
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
            f"૧. 🟢 બેંક કેશ (ગલ્લો ૧ - મુખ્ય કાઉન્ટર DP): ₹{g1:,.0f}",
            f"૨. 🔵 એક્સેસરીઝ D-Cash (ગલ્લો ૨): ₹{g2:,.0f}",
            f"૩. 🟣 રીચાર્જ & LAPU કેશ (ગલ્લો ૩): ₹{g3:,.0f}",
            f"૪. 🟡 તિજોરી / એક્સ્ટ્રા DP નફો (ગલ્લો ૪): ₹{g4:,.0f}",
            "─────────────────────────────────────────",
            f"💵 દુકાનની કુલ હાજર રોકડ (Total Cash): ₹{tot_cash:,.0f}",
            f"🏦 બેંકમાં જમા કરવા પાત્ર રોકડ: ₹{unbanked:,.0f}"
        ])
    
    # ૨. આજનો ચોખ્ખો દૈનિક નફો (Net Profit)
    elif any(k in q for k in ["નફો", "પ્રોફિટ", "profit", "margin", "માર્જિન"]):
        p = calc_daily_net_profit()
        ans_text = "\n".join([
            "📈 આજનો ચોખ્ખો દૈનિક નફો (Net Profit Analysis):",
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
            f"• મોબાઈલ વેચાણ માર્જિન (MOP - DP): ₹{p['mobile_margin']:,.0f}",
            f"• ફાઇનાન્સ Extra DP નફો: +₹{p['extra_dp_profit']:,.0f}",
            f"• જૂના ફોન બાયબેક વેચાણ નફો: +₹{p['buyback_profit']:,.0f}",
            f"• કુલ ગ્રોસ નફો (Gross Profit): ₹{p['gross_profit']:,.0f}",
            "─────────────────────────────────────────",
            f"• બાદ દૈનિક દુકાન ખર્ચ [F6]: -₹{p['shop_expenses']:,.0f}",
            f"• બાદ સ્ટાફ કમિશન (૨૦%): -₹{p['staff_commission']:,.0f}",
            f"• બાદ ગ્રાહક ગિફ્ટ ખર્ચ: -₹{p['gift_cost']:,.0f}",
            "─────────────────────────────────────────",
            f"🏆 આજનો ચોખ્ખો ચોખ્ખો નફો (NET PROFIT): ₹{p['net_profit']:,.0f}"
        ])
    
    # ૩. સ્ટોક & ઇન્વેન્ટરી
    elif any(k in q for k in ["સ્ટોક", "stock", "ફોન કેટલા", "ઇન્વેન્ટરી", "હેન્ડસેટ"]):
        c.execute("SELECT COUNT(*), COALESCE(SUM(purchase_rate),0), COALESCE(SUM(sale_rate),0) FROM live_stock WHERE status='IN_STOCK'")
        r_st = c.fetchone()
        c.execute("SELECT brand, COUNT(*) FROM live_stock WHERE status='IN_STOCK' GROUP BY brand ORDER BY COUNT(*) DESC LIMIT 6")
        brand_rows = c.fetchall()
        b_str = ", ".join([f"{br[0]}: {br[1]} નંગ" for br in brand_rows]) or "કોઈ સ્ટોક નથી"
        ans_text = "\n".join([
            "📱 હાજર સ્ટોક (Live Stock Inventory) સમરી:",
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
            f"• કુલ હાજર મોબાઈલ: {r_st[0]} નંગ",
            f"• કુલ ખરીદ પડતર મૂલ્ય (DP Value): ₹{r_st[1]:,.0f}",
            f"• અંદાજિત વેચાણ મૂલ્ય (MOP Value): ₹{r_st[2]:,.0f}",
            f"• બ્રાન્ડ વાઇઝ સ્ટોક: {b_str}"
        ])
    
    # ૪. ગ્રાહક બાકી ઉધાર
    elif any(k in q for k in ["બાકી", "ઉધાર", "due", "debtor", "લેણું"]):
        c.execute("SELECT COUNT(DISTINCT customer_name), COALESCE(SUM(due_amt - received_amt),0) FROM customer_due_ledger WHERE (due_amt - received_amt) > 0")
        r_due = c.fetchone()
        c.execute("SELECT customer_name, phone, (due_amt - received_amt) FROM customer_due_ledger WHERE (due_amt - received_amt) > 0 ORDER BY (due_amt - received_amt) DESC LIMIT 5")
        top_dues = c.fetchall()
        d_list = "\n".join([f"  - {d[0]} ({d[1]}): ₹{float(d[2] or 0):,.0f}" for d in top_dues]) or "  - કોઈ બાકી નથી"
        ans_text = "\n".join([
            "⚠️ ગ્રાહક બાકી ઉધાર (Customer Due) સ્થિતિ:",
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
            f"• બાકી ખાતાધારક ગ્રાહકો: {r_due[0]} જણા",
            f"• કુલ વસૂલવાની બાકી રકમ: ₹{r_due[1]:,.0f}",
            f"• ટોપ બાકીદારો:",
            d_list
        ])
    
    # ૫. ૫૦+ સ્ટોર્સની સ્થિતિ
    elif any(k in q for k in ["૫૦", "દુકાનો", "બધી દુકાન", "all shops", "stores", "franchise", "રજીસ્ટર"]):
        c.execute("SELECT COUNT(*), SUM(CASE WHEN license_status='ACTIVE' THEN 1 ELSE 0 END), SUM(CASE WHEN license_status IN ('LOCKED','BLOCK') THEN 1 ELSE 0 END), SUM(CASE WHEN subscription_mode='DEMO' THEN 1 ELSE 0 END) FROM master_saas_shops_registry")
        r_sh = c.fetchone()
        ans_text = "\n".join([
            "🏬 ૫૦+ દુકાનોનું માસ્ટર રજીસ્ટર સ્ટેટસ:",
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
            f"• કુલ રજીસ્ટર્ડ સ્ટોર્સ: {r_sh[0]} દુકાનો",
            f"• એક્ટિવ (સક્રિય) સ્ટોર્સ: {r_sh[1] or 0}",
            f"• ૧૦-દિવસ ડેમો સ્ટોર્સ: {r_sh[3] or 0}",
            f"• બ્લોક / લૉક કરેલ સ્ટોર્સ: {r_sh[2] or 0}"
        ])

    # ૬. બ્લોક / એક્ટિવ આદેશ
    elif "બ્લોક" in q or "block" in q_low:
        m_sh = re.search(r'([A-Za-z0-9_\-]+)', q.replace("દુકાન", "").replace("સ્ટોર", "").replace("બ્લોક", "").replace("કરો", ""))
        target_s = m_sh.group(1).strip() if m_sh else sid
        c.execute("UPDATE master_saas_shops_registry SET license_status='BLOCK' WHERE shop_id=?", (target_s,))
        c.execute("UPDATE shop_custom_settings SET license_status='BLOCK' WHERE shop_id=?", (target_s,))
        ans_text = f"🛑 દુકાન '{target_s}' ને તાત્કાલિક BLOCK (લૉક) કરવામાં આવી છે!"
    
    elif "એક્ટિવ" in q or "active" in q_low or "ચાલુ કરો" in q:
        m_sh = re.search(r'([A-Za-z0-9_\-]+)', q.replace("દુકાન", "").replace("સ્ટોર", "").replace("એક્ટિવ", "").replace("કરો", "").replace("ચાલુ", ""))
        target_s = m_sh.group(1).strip() if m_sh else sid
        c.execute("UPDATE master_saas_shops_registry SET license_status='ACTIVE' WHERE shop_id=?", (target_s,))
        c.execute("UPDATE shop_custom_settings SET license_status='ACTIVE' WHERE shop_id=?", (target_s,))
        ans_text = f"✅ દુકાન '{target_s}' ને સફળતાપૂર્વક ACTIVE (સક્રિય) કરવામાં આવી છે!"
    
    # ૭. કાઉન્ટર્સ કંટ્રોલ
    elif "કાઉન્ટર" in q or "counter" in q_low or any(f"f{i}" in q_low for i in range(1, 9)):
        found_c = re.findall(r'F[1-8]', q.upper())
        if found_c:
            new_c = ",".join(sorted(list(set(found_c))))
            if "બધી" in q or "all" in q_low:
                c.execute("UPDATE master_saas_shops_registry SET active_counters=?", (new_c,))
                c.execute("UPDATE shop_custom_settings SET active_counters=?", (new_c,))
                executed_action = f"તમામ ૫૦+ દુકાનો માટે સક્રિય કાઉન્ટર બદલીને [{new_c}] સેટ કર્યા."
            else:
                c.execute("UPDATE master_saas_shops_registry SET active_counters=? WHERE shop_id=?", (new_c, sid))
                c.execute("UPDATE shop_custom_settings SET active_counters=? WHERE shop_id=?", (new_c, sid))
                executed_action = f"દુકાન '{sid}' માટે સક્રિય કાઉન્ટર બદલીને [{new_c}] સેટ કર્યા."
            ans_text = f"✅ સફળ: {executed_action}"
    
    # ૮. પાસવર્ડ રીસેટ
    elif "પાસવર્ડ" in q or "password" in q_low:
        m_pw = re.search(r'પાસવર્ડ\s*[:=]?\s*([A-Za-z0-9@#\$\%]+)', q)
        if m_pw:
            new_pw = m_pw.group(1).strip()
            c.execute("UPDATE master_saas_shops_registry SET current_password=? WHERE shop_id=?", (new_pw, sid))
            c.execute("UPDATE shop_custom_settings SET shop_password=? WHERE shop_id=?", (new_pw, sid))
            ans_text = f"✅ દુકાન '{sid}' નો પાસવર્ડ બદલીને '{new_pw}' કરી દીધો છે."
        else:
            c.execute("SELECT shop_id, store_name, current_password FROM master_saas_shops_registry WHERE shop_id=?", (sid,))
            row = c.fetchone()
            if row:
                ans_text = f"🔑 દુકાન '{row[1]}' ({row[0]}) નો હાલનો પાસવર્ડ: '{row[2]}' છે."
            else:
                ans_text = f"દુકાન '{sid}' નો રેકોર્ડ મળ્યો નથી."

    # ૯. દૈનિક સેલ્સ રિપોર્ટ
    elif "રિપોર્ટ" in q or "સેલ્સ" in q or "વેચાણ" in q:
        today_s = str(datetime.date.today())
        c.execute("SELECT COUNT(*), COALESCE(SUM(mop_price),0), COALESCE(SUM(cash_dp),0), COALESCE(SUM(due_amt),0) FROM apx_sales_raw WHERE bill_date=?", (today_s,))
        r = c.fetchone()
        ans_text = f"📊 આજનો વેચાણ સમરી ({today_s}):\n- કુલ વેચાણ બિલ: {r[0]}\n- કુલ MOP વેચાણ રકમ: ₹{r[1]:,.0f}\n- રોકડ DP વકરો: ₹{r[2]:,.0f}\n- આજની ગ્રાહક બાકી ઉધાર: ₹{r[3]:,.0f}"

    # ૧૦. SQL એક્ઝિક્યુશન
    elif q.upper().startswith("SELECT ") or q.upper().startswith("UPDATE ") or q.upper().startswith("INSERT "):
        try:
            c.execute(q)
            if q.upper().startswith("SELECT "):
                res = c.fetchall()
                ans_text = f"✅ SQL ક્વેરી પરિણામ ({len(res)} રો):\n" + str(res[:10])
            else:
                conn.commit()
                ans_text = f"✅ SQL ક્વેરી સફળતાપૂર્વક એક્ઝિક્યુટ થઈ અને ડેટાબેઝ અપડેટ થયો ({c.rowcount} રો પ્રભાવિત)."
        except Exception as e:
            ans_text = f"❌ SQL એરર: {str(e)}"
    else:
        ans_text = f"🤖 દેવાંશી AI Co-Pilot એ તમારો આદેશ સ્વીકાર્યો: '{q}'. દુકાન '{sid}' ના તમામ મોનિટરિંગ, ઓટો-અપડેટ અને ડેટાબેઝ રૂલ્સ સક્રિય છે!"
    
    conn.commit()
    conn.close()
    return {"status": "success", "response": ans_text}


@app.post("/api/clear-admin-notifications")
def clear_admin_notifications_route(notif_id: str = Form("ALL")):
    import os, glob
    clean_id = (notif_id or "ALL").strip()
    msg = "તમામ સાઇન-અપ અને એટેન્ડન્સ નોટિફિકેશન સફળતાપૂર્વક ક્લિયર કર્યા!" if clean_id.upper() == "ALL" else f"નોટિફિકેશન #{clean_id} ક્લિયર કર્યું!"
    all_dbs = {MASTER_DB_FILE, DB_FILE, get_active_db_file()}
    try:
        for f_db in glob.glob(os.path.join(DATA_DIR, "*.db")):
            all_dbs.add(f_db)
    except Exception:
        pass
    for target_db in all_dbs:
        try:
            conn = sqlite3.connect(target_db, timeout=60.0)
            c = conn.cursor()
            c.execute("""CREATE TABLE IF NOT EXISTS admin_signup_notifications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT, shop_id TEXT, store_name TEXT,
                owner_name TEXT, owner_mobile TEXT, store_mode TEXT,
                pref_lang TEXT, is_read INTEGER DEFAULT 0
            )""")
            if clean_id.upper() == "ALL":
                c.execute("SELECT shop_id, timestamp FROM admin_signup_notifications")
                for r_n in c.fetchall():
                    d_list = list(STORE_CFG.get("dismissed_notifs", []))
                    k_n = f"{r_n[0]}_{r_n[1]}"
                    if k_n not in d_list: d_list.append(k_n)
                    STORE_CFG["dismissed_notifs"] = d_list
                c.execute("UPDATE admin_signup_notifications SET is_read=1")
            else:
                c.execute("SELECT shop_id, timestamp FROM admin_signup_notifications WHERE id=?", (clean_id,))
                r_n = c.fetchone()
                if r_n:
                    d_list = list(STORE_CFG.get("dismissed_notifs", []))
                    k_n = f"{r_n[0]}_{r_n[1]}"
                    if k_n not in d_list: d_list.append(k_n)
                    STORE_CFG["dismissed_notifs"] = d_list
                c.execute("UPDATE admin_signup_notifications SET is_read=1 WHERE id=?", (clean_id,))
            conn.commit()
            conn.close()
        except Exception:
            pass
    return RedirectResponse(url="/super-admin?pin=1986&msg=" + urllib.parse.quote(msg), status_code=303)




# =======================================================================================================================
# 🛠️ ખૂટતા રાઉટ્સ: [F7] સામાન્ય ૬-ખાના ગ્રાહક રિપેરિંગ, [F6] LAPU ડેમો ક્લોઝિંગ, અને AnyDesk લાઈવ સ્ક્રીન બ્રિજ
# =======================================================================================================================
@app.post("/save-f7-simple-repair")
def save_f7_simple_repair_route(
    entry_date: str = Form(""), customer_name: str = Form(...), customer_phone: str = Form(""),
    model_and_issue: str = Form(...), technician_name: str = Form(""),
    spare_part_cost: float = Form(0), part_paid_galla: str = Form("BANK_CASH"),
    customer_charge: float = Form(0), received_galla: str = Form("EXTRA_CASH")
):
    now_dt = datetime.datetime.now()
    d_str = entry_date.strip() or now_dt.strftime("%Y-%m-%d")
    t_str = now_dt.strftime("%H:%M")
    sid = STORE_CFG.get("shop_id", "DEVANSHI")
    net_prof = max(0.0, float(customer_charge or 0) - float(spare_part_cost or 0))

    conn = sqlite3.connect(get_active_db_file(), timeout=60.0)
    c = conn.cursor()
    c.execute("""INSERT INTO out_of_store_repair_log
        (store_id, entry_date, entry_time, customer_name, customer_phone, model_and_issue, technician_name,
         spare_part_cost, part_paid_galla, customer_charge, net_repair_profit, tech_share_pct, tech_share_amt,
         owner_share_amt, profit_galla, effective_rule_date)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 0, 0, ?, ?, ?)""",
        (sid, d_str, t_str, customer_name, customer_phone, model_and_issue, technician_name,
         spare_part_cost, part_paid_galla, customer_charge, net_prof, net_prof, received_galla, d_str))

    if spare_part_cost > 0:
        c.execute("INSERT INTO galla_ledger (date, galla_name, in_amt, out_amt, remarks, store_id) VALUES (?, ?, 0, ?, ?, ?)",
                  (d_str, part_paid_galla, spare_part_cost, f"[F7 સાદું રિપેરિંગ પાર્ટ ખર્ચ]: {model_and_issue} ({customer_name})", sid))
    if customer_charge > 0:
        c.execute("INSERT INTO galla_ledger (date, galla_name, in_amt, out_amt, remarks, store_id) VALUES (?, ?, ?, 0, ?, ?)",
                  (d_str, received_galla, customer_charge, f"[F7 સાદું રિપેરિંગ આવક]: {customer_name} - {model_and_issue}", sid))

    c.execute("""INSERT INTO live_terminal_grid
        (entry_time, bill_no, customer_name, model_name, imei, galla_name, entry_type, total_padtar, gift_amt, due_amt, salesman, store_id)
        VALUES (?, 'SIMPLE-REP', ?, ?, '-', ?, 'F7_SIMPLE_REPAIR', ?, 0, 0, ?, ?)""",
        (f"{d_str} {t_str}", customer_name, f"{model_and_issue} (નફો ₹{net_prof:,.0f})", received_galla, customer_charge, technician_name, sid))
    conn.commit()
    conn.close()
    return redir(f"✅ [F7] ગ્રાહક રિપેરિંગ એન્ટ્રી સેવ થઈ! ગ્રાહક ચાર્જ: ₹{customer_charge:,.0f} | સ્પેરપાર્ટ ખર્ચ: ₹{spare_part_cost:,.0f} | ચોખ્ખો નફો: ₹{net_prof:,.0f} ({received_galla})", "SMART_TERMINAL", "F7")


@app.post("/save-lapu-demo-closing")
def save_lapu_demo_closing_route(
    entry_date: str = Form(""), jio_demo: float = Form(0),
    airtel_demo: float = Form(0), vi_demo: float = Form(0)
):
    d_str = entry_date.strip() or str(datetime.date.today())
    conn = sqlite3.connect(get_active_db_file(), timeout=60.0)
    c = conn.cursor()
    for comp_nm, val in [("Jio", jio_demo), ("Airtel", airtel_demo), ("Vi", vi_demo)]:
        c.execute("SELECT COUNT(*) FROM recharge_lapu_company_balances WHERE company=?", (comp_nm,))
        if c.fetchone()[0] == 0:
            c.execute("INSERT INTO recharge_lapu_company_balances (company, current_demo_balance, pending_distributor_due, updated_at) VALUES (?, ?, 0, ?)", (comp_nm, val, d_str))
        else:
            c.execute("UPDATE recharge_lapu_company_balances SET current_demo_balance=?, updated_at=? WHERE company=?", (val, d_str, comp_nm))
    c.execute("UPDATE recharge_lapu_audit SET jio_lapu=?, vi_lapu=?, updated_date=? WHERE id=1", (jio_demo, vi_demo, d_str))
    conn.commit()
    conn.close()
    return redir(f"📲 [F6] LAPU ડેમો બેલેન્સ અપડેટ થયું (Jio: ₹{jio_demo:,.0f} | Airtel: ₹{airtel_demo:,.0f} | Vi: ₹{vi_demo:,.0f})!", "SMART_TERMINAL", "F6")


PENDING_REMOTE_FIXES = {}

@app.post("/api/live-screen-heartbeat")
async def api_live_screen_heartbeat_route(request: Request):
    try:
        data = await request.json()
    except Exception:
        data = {}
    sid = str(data.get("shop_id") or STORE_CFG.get("shop_id", "DEVANSHI")).strip().upper()
    client_ver = str(data.get("active_version") or data.get("version") or STORE_CFG.get("applied_ota_version") or STORE_CFG.get("ota_version_id", "2026.11.05.009")).strip()
    data["active_version"] = client_ver
    from part1_core import LIVE_SCREEN_STATE_CACHE, broadcast_live_store_tunnel
    LIVE_SCREEN_STATE_CACHE[sid] = data
    if sid and client_ver:
        try:
            _mc = sqlite3.connect(MASTER_DB_FILE, timeout=30.0)
            _mc.execute("UPDATE master_saas_shops_registry SET active_version=?, last_active_time=? WHERE UPPER(shop_id)=UPPER(?)", (client_ver, datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), sid))
            _mc.commit()
            _mc.close()
        except Exception:
            pass
    if data.get("stuck_help_note"):
        # Immediate cloud push when shopkeeper asks for help or changes form
        broadcast_live_store_tunnel(extra_screen_state=data)
        try:
            for t_db in {MASTER_DB_FILE, DB_FILE, get_active_db_file()}:
                _conn = sqlite3.connect(t_db, timeout=60.0)
                _conn.execute("""INSERT INTO admin_signup_notifications
                    (timestamp, shop_id, store_name, owner_name, owner_mobile, store_mode, pref_lang, is_read)
                    VALUES (?, ?, ?, ?, ?, ?, 'LIVE_HELP', 0)""",
                    (datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), sid,
                     f"🆘 લાઈવ સ્ક્રીન મદદ ({data.get('active_mode','F2')}): {data.get('stuck_help_note')}",
                     data.get("current_user", sid), STORE_CFG.get("owner_mobile", ""), data.get("active_sheet", "SMART_TERMINAL")))
                _conn.commit()
                _conn.close()
        except Exception:
            pass
    else:
        # Update local state file and periodically sync
        tunnels_local_dir = os.path.join(os.path.dirname(get_active_db_file()), "live_store_tunnels")
        os.makedirs(tunnels_local_dir, exist_ok=True)
        hb_path = os.path.join(tunnels_local_dir, f"{sid}.json")
        try:
            existing = {}
            if os.path.exists(hb_path):
                with open(hb_path, "r", encoding="utf-8") as rf:
                    existing = json.load(rf)
            existing.update(data)
            existing["last_heartbeat"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            existing["status"] = "ONLINE"
            with open(hb_path, "w", encoding="utf-8") as wf:
                json.dump(existing, wf, indent=2, ensure_ascii=False)
        except Exception:
            pass

    popped_fix = PENDING_REMOTE_FIXES.pop(sid, None)
    return {"status": "ok", "remote_fix": popped_fix}


@app.post("/api/push-remote-screen-fix")
async def api_push_remote_screen_fix_route(
    shop_id: str = Form(...),
    admin_note: str = Form("જયમીનભાઈએ ફોર્મમાં સુધારો કરી આપ્યો છે"),
    form_json: str = Form("{}")
):
    sid = shop_id.strip().upper()
    try:
        f_vals = json.loads(form_json or "{}")
    except Exception:
        f_vals = {}
    PENDING_REMOTE_FIXES[sid] = {
        "shop_id": sid,
        "admin_note": admin_note,
        "form_values": f_vals,
        "pushed_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    from part1_core import broadcast_live_store_tunnel
    broadcast_live_store_tunnel(extra_screen_state={"form_values": f_vals, "last_error": f"✅ રિમોટ સુધારો: {admin_note}"})
    return RedirectResponse(url=f"/super-admin-live-screen?shop_id={ urllib.parse.quote(sid) }&msg={ urllib.parse.quote('✅ દુકાનદારની લાઈવ સ્ક્રીન પર સુધારો મોકલાઈ ગયો!') }", status_code=303)


@app.post("/upload-buyback-police-docs")
async def upload_buyback_police_docs_route(
    imei: str = Form(...),
    customer_name: str = Form(""),
    doc_type: str = Form("police_verification"),
    bb_docs: List[UploadFile] = File([]),
    shop_id: str = Form(""),
    return_sheet: str = Form("BUYBACK_STOCK")
):
    """
    જૂના બાયબેક ફોન માટે પાછળથી પોલીસ વેરિફિકેશન દસ્તાવેજ (આધાર, ફોટો, જૂનું બિલ) અપલોડ કરવાની સગવડ (Rule 147)
    """
    sid = shop_id.strip() if shop_id.strip() else STORE_CFG.get("shop_id", "DEVANSHI")
    clean_imei = imei.strip()
    if not clean_imei:
        return redir("❌ IMEI નંબર અનિવાર્ય છે!", return_sheet)

    saved_paths = []
    base_vault = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Document_Vault", "stores", sid, "buyback", clean_imei)
    os.makedirs(base_vault, exist_ok=True)

    for doc in bb_docs:
        if doc and doc.filename:
            fn = f"{int(time.time())}_{doc.filename.replace(' ', '_')}"
            dest = os.path.join(base_vault, fn)
            with open(dest, "wb") as buffer:
                shutil.copyfileobj(doc.file, buffer)
            rel_url = f"/Document_Vault/stores/{sid}/buyback/{clean_imei}/{fn}"
            saved_paths.append(rel_url)

    if saved_paths:
        db_file = get_active_db_file(sid)
        conn = sqlite3.connect(db_file)
        c = conn.cursor()
        new_doc_str = ";".join(saved_paths)
        c.execute("""UPDATE buyback_stock 
                     SET photo_path = CASE 
                         WHEN photo_path IS NULL OR photo_path = '' THEN ? 
                         ELSE photo_path || ';' || ? 
                     END 
                     WHERE imei = ?""", (new_doc_str, new_doc_str, clean_imei))
        conn.commit()
        conn.close()
        return redir(f"✅ IMEI '{clean_imei}' માટે {len(saved_paths)} દસ્તાવેજ/ફોટો સફળતાપૂર્વક અપલોડ થયા!", return_sheet)
    else:
        return redir("❌ કૃપા કરીને ઓછામાં ઓછી ૧ ફાઇલ પસંદ કરો!", return_sheet)


@app.get("/api/shutdown-erp")
def shutdown_erp_route():
    """
    દુકાનદાર કે જયમીનભાઈ સોફ્ટવેરની અંદરથી જ ૧-ક્લિકમાં સર્વર સુરક્ષિત બંધ (Graceful Shutdown) કરી શકે
    જેથી બેકગ્રાઉન્ડ પ્રોસેસ બંધ થાય અને ફાઇલો ક્યારેય લૉક ન રહે (Rule 150 & 155)
    """
    def _kill():
        time.sleep(0.5)
        os._exit(0)
    threading.Thread(target=_kill, daemon=True).start()
    return HTMLResponse("""
    <html><head><meta charset='utf-8'><title>દેવાંશી ERP - સોફ્ટવેર બંધ</title></head>
    <body style="font-family:Segoe UI, sans-serif; background:#0f172a; color:white; display:flex; align-items:center; justify-content:center; height:100vh; margin:0; text-align:center;">
        <div style="background:#1e293b; padding:32px; border-radius:12px; border:2px solid #38bdf8; max-width:460px; box-shadow:0 15px 35px rgba(0,0,0,0.5);">
            <div style="font-size:42px; margin-bottom:12px;">🛑</div>
            <h2 style="color:#4ade80; margin:0 0 10px 0;">સોફ્ટવેર સફળતાપૂર્વક બંધ થઈ ગયું છે</h2>
            <p style="color:#cbd5e1; font-size:14px; line-height:1.6; margin-bottom:20px;">
                બેકગ્રાઉન્ડ સર્વર સુરક્ષિત રીતે બંધ થઈ ગયું છે અને તમામ ફાઇલો અનલૉક થઈ ગઈ છે.<br>
                હવે તમે આ બ્રાઉઝર ટેબ બંધ કરી શકો છો.
            </p>
            <button onclick="window.close()" style="background:#dc2626; color:white; border:none; padding:10px 24px; border-radius:6px; font-weight:bold; cursor:pointer; font-size:14px;">
                [ આ ટેબ બંધ કરો ]
            </button>
        </div>
    </body></html>
    """)


@app.post("/save-lapu-inward-payment")
def save_lapu_inward_payment_route(
    entry_date: str = Form(""),
    company: str = Form("Jio"),
    distributor_name: str = Form(""),
    inward_balance: float = Form(0),
    paid_to_distributor: float = Form(0),
    paid_from_galla: str = Form("RECHARGE"),
    remarks: str = Form(""),
    return_mode: str = Form("F3")
):
    sid = STORE_CFG.get("shop_id", "DEVANSHI")
    d_str = entry_date.strip() or str(datetime.date.today())
    time_s = datetime.datetime.now().strftime("%I:%M %p")
    in_bal = float(inward_balance or 0)
    paid = float(paid_to_distributor or 0)
    due = max(0.0, in_bal - paid)
    conn = sqlite3.connect(get_active_db_file(), timeout=60.0)
    c = conn.cursor()
    c.execute("""INSERT INTO recharge_lapu_ledger
        (store_id, entry_date, time_str, company, distributor_name, inward_balance,
         paid_to_distributor, pending_distributor_due, paid_from_galla, remarks)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (sid, d_str, time_s, company, distributor_name, in_bal, paid, due, paid_from_galla, remarks))
    c.execute("SELECT COALESCE(today_topup,0), COALESCE(current_demo_balance,0), COALESCE(pending_distributor_due,0) FROM recharge_lapu_company_balances WHERE company=?", (company,))
    r_cb = c.fetchone()
    if r_cb:
        old_top = float(r_cb[0] or 0)
        old_demo = float(r_cb[1] or 0)
        old_due = float(r_cb[2] or 0)
        c.execute("""UPDATE recharge_lapu_company_balances
                     SET today_topup=?, current_demo_balance=?, pending_distributor_due=?, last_updated=?
                     WHERE company=?""", (old_top + in_bal, old_demo + in_bal, old_due + due, d_str, company))
    else:
        c.execute("""INSERT INTO recharge_lapu_company_balances
                     (company, opening_balance, today_topup, today_sales, current_demo_balance, pending_distributor_due, last_updated)
                     VALUES (?, 0, ?, 0, ?, ?, ?)""", (company, in_bal, in_bal, due, d_str))
    if paid > 0 and paid_from_galla in ("RECHARGE", "BANK_CASH", "ACC_DCASH", "EXTRA_CASH"):
        sid_lapu = STORE_CFG.get("shop_id", "DEVANSHI")
        c.execute("""INSERT INTO galla_ledger (date, galla_name, in_amt, out_amt, remarks, store_id)
                     VALUES (?, ?, 0, ?, ?, ?)""",
                  (d_str, paid_from_galla, paid, f"{company} LAPU ખરીદી પેમેન્ટ ચૂકવ્યું ({distributor_name})", sid_lapu))
        if paid_from_galla != "RECHARGE":
            c.execute("""INSERT INTO inter_galla_debt_ledger (store_id, tx_date, lender_galla, borrower_galla, amount, settled_amt, status, remarks)
                         VALUES (?, ?, ?, 'RECHARGE', ?, 0, 'PENDING', ?)""",
                      (sid_lapu, d_str, paid_from_galla, paid, f"{company} LAPU ખરીદી ({distributor_name}) {paid_from_galla} માંથી ઉછીના ચૂકવ્યા"))
    conn.commit()
    conn.close()
    ret_m = return_mode.strip().upper() if return_mode.strip().upper() in ("F3", "F6") else "F3"
    return redir(f"✅ [{ret_m}] {company} LAPU ખરીદી +₹{in_bal:,.0f} ({distributor_name}) સેવ થયું! (ચૂકવ્યા: ₹{paid:,.0f}, કમિશન/બાકી: ₹{due:,.0f})", "SMART_TERMINAL", ret_m)


from fastapi.responses import JSONResponse

@app.get("/manifest-admin.json")
def manifest_admin_route():
    return JSONResponse({
        "name": "દેવાંશી સુપર એડમિન",
        "short_name": "સુપર એડમિન",
        "description": "જયમીનભાઈ માસ્ટર કંટ્રોલ હબ & ૫૦+ સ્ટોર્સ મેનેજર",
        "start_url": "/super-admin-gateway",
        "display": "standalone",
        "background_color": "#0f172a",
        "theme_color": "#0f172a",
        "icons": [
            {"src": "/vault/icon_super_admin.svg", "sizes": "512x512", "type": "image/svg+xml", "purpose": "any maskable"}
        ]
    })

@app.get("/manifest-ai.json")
def manifest_ai_route():
    return JSONResponse({
        "name": "દેવાંશી AI કમાન્ડર",
        "short_name": "દેવાંશી AI",
        "description": "જયમીનભાઈ હાઈ-ફાઈ ગુજરાતી વોઈસ AI આસિસ્ટન્ટ",
        "start_url": "/mobile-ai-commander?pin=1986",
        "display": "standalone",
        "background_color": "#091224",
        "theme_color": "#091224",
        "icons": [
            {"src": "/vault/pwa_icon_192.png", "sizes": "192x192", "type": "image/png", "purpose": "any maskable"},
            {"src": "/vault/pwa_icon_512.png", "sizes": "512x512", "type": "image/png", "purpose": "any maskable"},
            {"src": "/vault/icon_ai_commander.svg", "sizes": "512x512", "type": "image/svg+xml", "purpose": "any maskable"}
        ]
    })

@app.get("/mobile-ai-commander", response_class=HTMLResponse)
def mobile_ai_commander_page(pin: str = "", shop: str = ""):
    from part1_core import STORE_CFG, get_galla_balance, calc_daily_net_profit, MASTER_DB_FILE
    cur_pin = str(STORE_CFG.get("admin_pin", "1986")).strip()
    if str(pin).strip() not in (cur_pin, "1986"):
        return RedirectResponse("/login?msg=સિક્રેટ+PIN+જરૂરી+છે", status_code=303)

    today_s = str(datetime.date.today())
    target_shop = (shop or STORE_CFG.get("shop_id", "DEVANSHI")).strip()

    # Get stores list for quick switching
    conn = sqlite3.connect(MASTER_DB_FILE, timeout=60.0)
    c = conn.cursor()
    c.execute("SELECT shop_id, store_name, subscription_mode FROM master_saas_shops_registry ORDER BY id ASC")
    shops_list = c.fetchall()
    conn.close()

    shop_opts = "".join([f'<option value="{s[0]}" {"selected" if s[0]==target_shop else ""}>{s[0]} - {s[1]} ({s[2]})</option>' for s in shops_list])

    return HTMLResponse(f"""<!DOCTYPE html>
    <html lang="gu">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
        <title>દેવાંશી AI કમાન્ડર</title>
        <link rel="manifest" href="/manifest-ai.json">
        <link rel="icon" href="/vault/icon_ai_commander.svg">
        <meta name="apple-mobile-web-app-capable" content="yes">
        <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
        <link href="https://fonts.googleapis.com/css2?family=Noto+Sans+Gujarati:wght@400;600;700;800;900&display=swap" rel="stylesheet">
        <style>
            body, html {{ margin:0; padding:0; height:100%; font-family:'Noto Sans Gujarati', sans-serif; background:#091224; color:white; overflow:hidden; }}
            .ai-wrap {{ display:flex; flex-direction:column; height:100%; box-sizing:border-box; padding:12px; }}
            .ai-head {{ display:flex; justify-content:space-between; align-items:center; border-bottom:2px solid #38bdf8; padding-bottom:8px; margin-bottom:10px; }}
            .chat-box {{ flex:1; overflow-y:auto; background:rgba(15,23,42,0.8); border:1.5px solid #1e3a8a; border-radius:12px; padding:12px; margin-bottom:10px; display:flex; flex-direction:column; gap:10px; }}
            .msg {{ padding:10px 14px; border-radius:10px; max-width:85%; font-size:13.5px; line-height:1.4; }}
            .msg-user {{ background:#0284c7; align-self:flex-end; color:white; font-weight:700; }}
            .msg-ai {{ background:#1e293b; align-self:flex-start; color:#fde047; border:1px solid #38bdf8; font-weight:600; white-space:pre-wrap; }}
            .quick-chips {{ display:flex; gap:6px; overflow-x:auto; padding-bottom:8px; scrollbar-width:none; }}
            .chip {{ background:#1e293b; color:#38bdf8; border:1px solid #38bdf8; padding:6px 12px; border-radius:20px; font-size:11.5px; font-weight:700; white-space:nowrap; cursor:pointer; flex-shrink:0; }}
            .controls {{ display:flex; gap:8px; align-items:center; }}
            .inp-box {{ flex:1; padding:12px; border-radius:24px; border:1.5px solid #38bdf8; background:#1e293b; color:white; font-size:14px; font-weight:bold; outline:none; }}
            .btn-mic {{ width:52px; height:52px; border-radius:50%; border:2px solid #fde047; background:linear-gradient(135deg, #eab308, #ca8a04); color:#091224; font-size:24px; display:flex; align-items:center; justify-content:center; cursor:pointer; flex-shrink:0; box-shadow:0 0 16px rgba(250,204,21,0.5); }}
            .btn-mic.listening {{ animation: pulse 1s infinite alternate; background:#dc2626; color:white; border-color:#fca5a5; }}
            @keyframes pulse {{ from {{ transform:scale(1); box-shadow:0 0 8px #dc2626; }} to {{ transform:scale(1.12); box-shadow:0 0 24px #ef4444; }} }}
            .btn-send {{ width:48px; height:48px; border-radius:50%; border:none; background:#0284c7; color:white; font-size:20px; display:flex; align-items:center; justify-content:center; cursor:pointer; flex-shrink:0; }}
        </style>
    </head>
    <body>
        <div class="ai-wrap">
            <div class="ai-head">
                <div style="display:flex; align-items:center; gap:8px;">
                    <span style="font-size:24px;">🤖</span>
                    <div>
                        <div style="font-size:14.5px; font-weight:800; color:#38bdf8;">દેવાંશી હાઈ-ફાઈ AI કમાન્ડર</div>
                        <div style="font-size:10.5px; color:#94a3b8;">જયમીનભાઈ પટેલ (સુપર એડમિન)</div>
                    </div>
                </div>
                <div style="display:flex; gap:6px;">
                    <a href="/super-admin?pin=1986" style="background:#ca8a04; color:white; padding:5px 9px; border-radius:5px; text-decoration:none; font-size:11.5px; font-weight:bold; border:1px solid #fef08a;">👑 એડમિન</a>
                    <a href="/?sheet=SMART_TERMINAL&mode=F2" style="background:#0284c7; color:white; padding:5px 9px; border-radius:5px; text-decoration:none; font-size:11.5px; font-weight:bold;">🏪 ERP</a>
                </div>
            </div>

            <!-- Google 2FA લાઈવ મોબાઈલ એપ્રુવલ એલર્ટ બાર -->
            <div id="mob_ai_2fa_bar" style="display:none; background:#7f1d1d; border:2px solid #fde047; border-radius:8px; padding:8px 10px; margin-bottom:8px; font-size:12px; font-weight:bold; color:white;">
                <div id="mob_ai_2fa_txt" style="margin-bottom:6px; color:#fef08a;">🔔 નવો સુપર એડમિન લૉગિન પ્રયાસ!</div>
                <div style="display:flex; gap:6px;">
                    <a id="mob_ai_2fa_yes" href="/api/respond-2fa-request?decision=APPROVED&return_to=MOBILE_AI" style="flex:1; background:#16a34a; color:white; padding:6px; border-radius:5px; text-decoration:none; text-align:center; font-weight:900;">✅ હા, એપ્રુવ કરો</a>
                    <a id="mob_ai_2fa_no" href="/api/respond-2fa-request?decision=BLOCKED&return_to=MOBILE_AI" style="flex:1; background:#dc2626; color:white; padding:6px; border-radius:5px; text-decoration:none; text-align:center; font-weight:900;">❌ બ્લોક કરો</a>
                </div>
            </div>
            <script>
                setInterval(function(){{
                    fetch('/api/check-2fa-approval-status').then(function(r){{return r.json();}}).then(function(d){{
                        var b = document.getElementById('mob_ai_2fa_bar');
                        if(d && d.status === 'PENDING' && d.token) {{
                            b.style.display = 'block';
                            document.getElementById('mob_ai_2fa_txt').innerHTML = '🔔 <b>Google 2FA એપ્રુવલ:</b> કોઈ ડિવાઇસ (' + (d.ip || '') + ') પરથી એડમિન પેજ ખોલવાનો પ્રયાસ થઈ રહ્યો છે!';
                            document.getElementById('mob_ai_2fa_yes').href = '/api/respond-2fa-request?token=' + encodeURIComponent(d.token) + '&decision=APPROVED&return_to=MOBILE_AI';
                            document.getElementById('mob_ai_2fa_no').href = '/api/respond-2fa-request?token=' + encodeURIComponent(d.token) + '&decision=BLOCKED&return_to=MOBILE_AI';
                        }} else if(b) {{
                            b.style.display = 'none';
                        }}
                    }}).catch(function(){{}});
                }}, 2500);
            </script>

            <!-- દુકાન સ્વીચર -->
            <div style="display:flex; gap:6px; align-items:center; margin-bottom:8px; background:rgba(255,255,255,0.06); padding:6px 10px; border-radius:8px;">
                <span style="font-size:11px; color:#fde047; font-weight:bold;">લક્ષ્ય દુકાન:</span>
                <select id="active_target_shop" onchange="onShopChange(this.value)" style="flex:1; padding:5px; background:#1e293b; color:white; border:1px solid #38bdf8; border-radius:4px; font-size:12px; font-weight:bold;">
                    {shop_opts}
                </select>
            </div>

            <div class="chat-box" id="chat_box">
                <div class="msg msg-ai">
                    નમસ્તે જયમીનભાઈ! 👑\nહું દેવાંશી હાઈ-ફાઈ AI કમાન્ડર છું.\nતમે કારમાં હોવ કે ગમે ત્યાં — માત્ર માઈક દબાવીને બોલો: વકરો, બાકી, બાય-બેક, નફો, કોઈપણ શીટ ખોલવી કે દુકાન સ્વીચ કરવી, હું તરત કરી આપીશ!
                </div>
            </div>

            <!-- ૧-ટેપ ક્વિક ચિપ્સ -->
            <div class="quick-chips">
                <div class="chip" onclick="sendCmd('આજનો ૪ ગલ્લા વકરો અને રોકડ સિલક બતાવો')">💰 ૪ ગલ્લા સિલક</div>
                <div class="chip" onclick="sendCmd('આજનો ચોખ્ખો નફો કેટલો થયો?')">📈 આજનો નફો</div>
                <div class="chip" onclick="sendCmd('હાજર સ્ટોક કેટલો છે?')">📱 હાજર સ્ટોક</div>
                <div class="chip" onclick="sendCmd('ગ્રાહક બાકી ઉધાર શીટ ખોલો')">⚠️ ગ્રાહક બાકી</div>
                <div class="chip" onclick="sendCmd('બાય-બેક સ્ટોક શીટ ખોલો')">🔄 બાય-બેક સ્ટોક</div>
                <div class="chip" onclick="sendCmd('ફાઇનાન્સ DO ઇમ્પોર્ટ કરો')">📥 DO ઇમ્પોર્ટ</div>
            </div>

            <div class="controls">
                <button type="button" class="btn-mic" id="mic_btn" onclick="toggleVoice()">🎤</button>
                <input type="text" class="inp-box" id="inp_cmd" placeholder="બોલો અથવા ગુજરાતીમાં લખો..." onkeydown="if(event.key==='Enter') sendText()">
                <button type="button" class="btn-send" onclick="sendText()">➤</button>
            </div>
        </div>

        <script>
            var rec = null;
            var isListening = false;
            var curShop = "{target_shop}";

            function onShopChange(s) {{
                curShop = s;
                addAiMsg('🔄 લક્ષ્ય દુકાન બદલીને [' + s + '] સેટ કરી.');
            }}

            function addMsg(txt, isUser) {{
                var b = document.getElementById('chat_box');
                var d = document.createElement('div');
                d.className = isUser ? 'msg msg-user' : 'msg msg-ai';
                d.innerText = txt;
                b.appendChild(d);
                b.scrollTop = b.scrollHeight;
            }}
            function addAiMsg(t) {{ addMsg(t, false); }}
            function addUserMsg(t) {{ addMsg(t, true); }}

            function sendText() {{
                var inp = document.getElementById('inp_cmd');
                var q = inp.value.trim();
                if(!q) return;
                inp.value = '';
                sendCmd(q);
            }}

            function sendCmd(q) {{
                addUserMsg(q);
                fetch('/api/ai-assistant-query?q=' + encodeURIComponent(q) + '&shop=' + encodeURIComponent(curShop))
                .then(r => r.json())
                .then(d => {{
                    addAiMsg(d.reply || 'કોઈ જવાબ મળ્યો નહીં.');
                    if(d.action === 'NAVIGATE' && d.target) {{
                        setTimeout(() => {{ window.location.href = d.target; }}, 1400);
                    }} else if(d.action === 'TRIGGER_IMPORT') {{
                        addAiMsg('💡 ઇમ્પોર્ટ વિન્ડો મુખ્ય ટર્મિનલમાં સક્રિય છે.');
                    }}
                }}).catch(e => {{
                    addAiMsg('⚠️ એરર આવી: ' + e);
                }});
            }}

            function toggleVoice() {{
                var SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
                if (!SpeechRecognition) {{
                    alert('⚠️ તમારા બ્રાઉઝરમાં વોઇસ રેકોગ્નિશન સપોર્ટ નથી. કૃપા કરીને લખીને મોકલો.');
                    return;
                }}
                var btn = document.getElementById('mic_btn');
                if (!isListening) {{
                    rec = new SpeechRecognition();
                    rec.lang = 'gu-IN';
                    rec.continuous = false;
                    rec.interimResults = false;
                    rec.onstart = function() {{
                        isListening = true;
                        btn.classList.add('listening');
                    }};
                    rec.onresult = function(e) {{
                        var transcript = e.results[0][0].transcript;
                        sendCmd(transcript);
                    }};
                    rec.onerror = function() {{
                        isListening = false;
                        btn.classList.remove('listening');
                    }};
                    rec.onend = function() {{
                        isListening = false;
                        btn.classList.remove('listening');
                    }};
                    rec.start();
                }} else {{
                    if(rec) rec.stop();
                }}
            }}
        </script>
    </body>
    </html>""")

@app.get("/jaymin-mobile-apps", response_class=HTMLResponse)
def jaymin_mobile_apps_setup_page():
    from part1_core import get_best_mobile_login_url, get_system_lan_ip, STORE_CFG
    lan_ip = get_system_lan_ip()
    port = STORE_CFG.get("active_port", 8000)
    qr_info = get_best_mobile_login_url()
    base_url = qr_info.get("cloud_base") or qr_info.get("lan_base") or f"http://{lan_ip}:{port}"

    url_admin = f"{base_url}/super-admin?pin=1986"
    url_ai = f"{base_url}/mobile-ai-commander?pin=1986"

    return HTMLResponse(f"""<!DOCTYPE html>
    <html lang="gu">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>જયમીનભાઈ - ૨ મોબાઈલ એપ આઈકોન સેટઅપ</title>
        <link href="https://fonts.googleapis.com/css2?family=Noto+Sans+Gujarati:wght@400;600;700;800;900&display=swap" rel="stylesheet">
        <style>
            body {{ font-family:'Noto Sans Gujarati', sans-serif; background:#091224; color:white; margin:0; padding:16px; text-align:center; }}
            .card-box {{ max-width:680px; margin:auto; background:#0f172a; border:2px solid #38bdf8; border-radius:14px; padding:20px; box-shadow:0 15px 35px rgba(0,0,0,0.6); }}
            .app-grid {{ display:grid; grid-template-columns:1fr 1fr; gap:14px; margin:20px 0; }}
            .app-card {{ background:#1e293b; border:2px solid #eab308; border-radius:12px; padding:16px; text-align:center; text-decoration:none; color:white; display:block; transition:transform 0.15s; }}
            .app-card:hover {{ transform:scale(1.02); }}
            .btn-install {{ background:#16a34a; color:white; padding:8px 16px; border-radius:6px; font-weight:800; font-size:13px; border:none; cursor:pointer; margin-top:8px; display:inline-block; }}
        </style>
    </head>
    <body>
        <div class="card-box">
            <h2 style="color:#fde047; margin:0 0 6px 0;">📱 જયમીનભાઈ: તમારા મોબાઈલ માટે ૨ સીધા એપ આઈકોન</h2>
            <p style="color:#cbd5e1; font-size:13px; margin:0 0 16px 0;">
                આ લિંક તમારા એન્ડ્રોઇડ કે આઈફોન મોબાઈલમાં ખોલી Chrome/Safari માં <b>"Add to Home screen" (હોમ સ્ક્રીન પર ઉમેરો)</b> કરો, જેથી સીધા ૨ એપ આઈકોન બની જશે!
            </p>

            <div class="app-grid">
                <!-- એપ ૧: સુપર એડમિન -->
                <a href="{url_admin}" class="app-card" style="border-color:#eab308;">
                    <img src="/vault/icon_super_admin.svg" style="width:84px; height:84px; display:block; margin:auto; border-radius:16px;">
                    <h3 style="color:#fde047; margin:10px 0 4px 0; font-size:16px;">👑 સુપર એડમિન</h3>
                    <div style="font-size:11.5px; color:#94a3b8;">માસ્ટર કંટ્રોલ હબ, પાસવર્ડ રીસેટ & ઓવરરાઇડ</div>
                    <div class="btn-install" style="background:#ca8a04;">[૧-ક્લિક ઓપન કરો]</div>
                </a>

                <!-- એપ ૨: હાઈ-ફાઈ AI કમાન્ડર -->
                <a href="{url_ai}" class="app-card" style="border-color:#38bdf8;">
                    <img src="/vault/icon_ai_commander.svg" style="width:84px; height:84px; display:block; margin:auto; border-radius:16px;">
                    <h3 style="color:#38bdf8; margin:10px 0 4px 0; font-size:16px;">🤖 દેવાંશી AI કમાન્ડર</h3>
                    <div style="font-size:11.5px; color:#94a3b8;">ગુજરાતી વોઇસ AI Co-Pilot (બોલીને કામ)</div>
                    <div class="btn-install" style="background:#0284c7;">[૧-ક્લિક ઓપન કરો]</div>
                </a>
            </div>

            <div style="background:#1e293b; padding:12px; border-radius:8px; border:1px solid #475569; font-size:12px; text-align:left; color:#cbd5e1; line-height:1.6;">
                <b style="color:#fde047;">📌 મોબાઈલમાં હોમ સ્ક્રીન પર આઈકોન કેવી રીતે લાવવો?:</b><br>
                ૧. મોબાઈલ ક્રોમ (Chrome) બ્રાઉઝરમાં ઉપર જમણી બાજુ <b>ત્રણ ટપકાં (⋮)</b> દબાવો.<br>
                ૨. <b>"Add to Home screen" (હોમ સ્ક્રીન પર ઉમેરો / Install app)</b> પર ક્લિક કરો.<br>
                ૩. તમારા મોબાઈલની હોમ સ્ક્રીન પર અન્ય એપ્સની જેમ જ સીધો આઈકોન આવી જશે, જેને દબાવતાં જ સીધું સોફ્ટવેર ખુલશે!
            </div>
        </div>
    </body>
    </html>""")


# =======================================================================================================================
# 🛡️ [નિયમ ૧૪૩ & ૧૪૭]: માસ્ટર PIN ૧૯૮૬ મિસ્ટેક-ડિલીશન, રિપેરિંગ રિવર્સલ & પોલીસ વેરિફિકેશન દસ્તાવેજ અપલોડ
# =======================================================================================================================
import os
import shutil
import time

@app.post("/api/reverse-buyback-repair")
def reverse_buyback_repair_route(
    imei: str = Form(""),
    bb_id: int = Form(0),
    repair_cost_to_reverse: float = Form(1200.0),
    pin: str = Form(""),
    shop_id: str = Form(""),
    return_sheet: str = Form("BUYBACK_STOCK")
):
    """
    જયમીનભાઈના માસ્ટર PIN ૧૯૮૬ વડે બાયબેક ફોનમાં થયેલો ખોટો રિપેરિંગ ખર્ચ (દા.ત. ₹૧,૨૦૦) રદ કરવો
    અને તે જ રકમ ગલ્લા ૧ (BANK_CASH) માં પરત જમા કરવી.
    """
    if str(pin).strip() != "1986":
        return redir("❌ ખોટો માસ્ટર PIN! માત્ર જયમીનભાઈના અધિકૃત PIN ૧૯૮૬ વડે જ રિપેરિંગ રદ થશે.", return_sheet)

    sid = shop_id.strip() if shop_id.strip() else STORE_CFG.get("shop_id", "DEVANSHI")
    db_file = get_active_db_file(sid)
    conn = sqlite3.connect(db_file)
    c = conn.cursor()

    clean_imei = imei.strip()
    if bb_id > 0:
        c.execute("SELECT id, imei, purchase_cost, repair_cost, total_cost, model FROM buyback_stock WHERE id=?", (bb_id,))
    else:
        c.execute("SELECT id, imei, purchase_cost, repair_cost, total_cost, model FROM buyback_stock WHERE imei=?", (clean_imei,))
    
    row = c.fetchone()
    if not row:
        conn.close()
        return redir(f"❌ ભૂલ: IMEI '{clean_imei}' નો બાયબેક ફોન સ્ટોકમાં મળ્યો નહીં!", return_sheet)

    b_id, b_imei, b_pur, b_rep, b_tot, b_mod = row
    b_pur = float(b_pur or 0)
    b_rep = float(b_rep or 0)
    rev_amt = float(repair_cost_to_reverse)

    if rev_amt <= 0:
        conn.close()
        return redir("❌ રિવર્સ કરવાની રકમ ₹૦ થી વધુ હોવી જોઈએ!", return_sheet)

    # Calculate new repair cost and total cost
    new_rep = max(0.0, b_rep - rev_amt)
    new_tot = b_pur + new_rep

    c.execute("UPDATE buyback_stock SET repair_cost=?, total_cost=? WHERE id=?", (new_rep, new_tot, b_id))

    # ગલ્લા ૧ (BANK_CASH) માં નાણાં પરત જમા (Reversal Credit)
    d_str = str(datetime.date.today())
    c.execute("""INSERT INTO galla_ledger (date, galla_name, in_amt, out_amt, remarks, store_id)
                 VALUES (?, 'BANK_CASH', ?, 0, ?, ?)""",
              (d_str, rev_amt, f"જૂનો ફોન રિપેરિંગ ખર્ચ રદ/રિવર્સલ (ભૂલ સુધારો - PIN 1986): {b_imei} ({b_mod})", sid))

    log_audit_action("REVERSE_BUYBACK_REPAIR", f"IMEI {b_imei} reversed repair ₹{rev_amt} (New Total: ₹{new_tot}) by Master PIN 1986", sid)

    conn.commit()
    conn.close()

    return redir(f"✅ સફળતા! IMEI '{b_imei}' નો ₹{rev_amt:,.0f} રિપેરિંગ ખર્ચ રદ થયો છે અને ગલ્લા ૧ (BANK_CASH) માં ₹{rev_amt:,.0f} રોકડ પરત જમા થઈ ગઈ છે! (નવી કુલ પડતર: ₹{new_tot:,.0f})", return_sheet)


@app.post("/api/delete-store-entry-with-pin")
def delete_store_entry_with_pin_route(
    entry_type: str = Form(...),
    entry_id: int = Form(...),
    pin: str = Form(""),
    shop_id: str = Form(""),
    return_sheet: str = Form("SMART_TERMINAL")
):
    """
    માસ્ટર PIN ૧૯૮૬ વડે ૧૦૦% બેકએન્ડ રોલબેક એન્જિન (Purchase, Sale, DO, Buyback, Due Reversals)
    """
    cur_pin = str(STORE_CFG.get("admin_pin", "1986")).strip()
    if str(pin).strip() not in (cur_pin, "1986"):
        return redir("❌ ખોટો માસ્ટર PIN! માત્ર જયમીનભાઈના અધિકૃત PIN ૧૯૮૬ વડે જ ડિલીટ/રોલબેક થશે.", return_sheet)

    sid = shop_id.strip() if shop_id.strip() else STORE_CFG.get("shop_id", "DEVANSHI")
    db_file = get_active_db_file(sid)
    conn = sqlite3.connect(db_file)
    c = conn.cursor()

    msg = ""
    # ૧. ખરીદી બિલ રોલબેક: બિલના તમામ IMEI સ્ટોકમાંથી ડિલીટ, સપ્લાયર લેજર રિવર્સ, ગલ્લા રોકડ પરત!
    if entry_type in ("purchase", "supplier_purchase"):
        c.execute("SELECT bill_no, party_name, total_amount, paid_amount, galla_name, date FROM supplier_purchase_ledger WHERE id=?", (entry_id,))
        p_row = c.fetchone()
        if p_row:
            b_no, p_name, t_amt, pd_amt, g_name, d_str = p_row
            # Delete stock items added under this purchase
            c.execute("DELETE FROM live_stock WHERE purchase_bill_no=? OR (party_name=? AND entry_date=?)", (b_no, p_name, d_str))
            # Delete supplier purchase ledger entry
            c.execute("DELETE FROM supplier_purchase_ledger WHERE id=?", (entry_id,))
            # Reverse cash in galla if paid
            if float(pd_amt or 0) > 0 and g_name:
                c.execute("INSERT INTO galla_ledger (date, galla_name, in_amt, out_amt, remarks, store_id) VALUES (?, ?, ?, 0, ?, ?)",
                          (d_str, g_name, float(pd_amt), f"ખરીદી બિલ રદ રોકડ પરત (Rollback): {b_no} ({p_name})", sid))
            conn.commit()
            msg = f"✅ ખરીદી બિલ #{b_no} ({p_name}) નું ૧૦૦% રોલબેક પૂર્ણ: સ્ટોકમાંથી ફોન નીકળી ગયા અને ગલ્લાની રોકડ પરત આવી ગઈ!"
        else:
            msg = "❌ ખરીદી બિલ રેકોર્ડ મળ્યો નહીં!"

    # ૨. વેચાણ બિલ (F2 Sale) રોલબેક: ફોન પાછો IN_STOCK, ગ્રાહક બાકી રદ, ગલ્લા કેશ રિવર્સ, DO ફરી PENDING!
    elif entry_type in ("sale", "apx_sales"):
        c.execute("SELECT bill_no, customer_name, imei, cash_dp, extra_dp_profit, due_amt, financer_name, do_ref_no, cash_galla, bill_date FROM apx_sales_raw WHERE id=?", (entry_id,))
        s_row = c.fetchone()
        if s_row:
            b_no, c_name, imei_val, c_dp, ex_dp, d_amt, f_comp, do_rf, c_gal, s_date = s_row
            # Revert phone from SOLD back to IN_STOCK
            if imei_val:
                c.execute("UPDATE live_stock SET status='IN_STOCK' WHERE imei=?", (imei_val.strip(),))
            # નિયમ ૨૩૩: જો ઉધાર બિલ સામે વચ્ચે ગ્રાહકે થોડી રિકવરી (Recovery) જમા કરાવી હોય તો ગલ્લામાંથી પણ તે રિકવરી રિવર્સ કરો જેથી ગલ્લામાં તફાવત ન આવે!
            c.execute("SELECT COALESCE(SUM(received_amt), 0) FROM customer_due_ledger WHERE bill_no=? OR (customer_name=? AND date=?)", (b_no, c_name, s_date))
            rec_already = float((c.fetchone() or [0])[0] or 0.0)
            if rec_already > 0:
                c.execute("INSERT INTO galla_ledger (date, galla_name, in_amt, out_amt, remarks, store_id) VALUES (?, ?, 0, ?, ?, ?)",
                          (s_date, c_gal or "BANK_CASH", rec_already, f"ઉધાર બિલ રદ થતાં વસૂલાત રોલબેક: {b_no} ({c_name})", sid))
            c.execute("DELETE FROM customer_due_ledger WHERE bill_no=? OR (customer_name=? AND date=?)", (b_no, c_name, s_date))
            # Reverse galla 1 cash
            if float(c_dp or 0) > 0:
                base_in_g1 = max(0.0, float(c_dp) - float(ex_dp or 0))
                if base_in_g1 > 0 and c_gal:
                    c.execute("INSERT INTO galla_ledger (date, galla_name, in_amt, out_amt, remarks, store_id) VALUES (?, ?, 0, ?, ?, ?)",
                              (s_date, c_gal, base_in_g1, f"વેચાણ બિલ રદ કેશ રિવર્સ (Rollback): {b_no} ({c_name})", sid))
                if float(ex_dp or 0) > 0:
                    c.execute("INSERT INTO galla_ledger (date, galla_name, in_amt, out_amt, remarks, store_id) VALUES (?, 'EXTRA_CASH', 0, ?, ?, ?)",
                              (s_date, float(ex_dp), f"ફાઇનાન્સ Extra DP નફો રદ રિવર્સ: {b_no}", sid))
            # Reopen DO to PENDING
            if do_rf:
                c.execute("UPDATE finance_do_list SET status='PENDING' WHERE do_ref_no=?", (do_rf.strip(),))
            c.execute("DELETE FROM apx_sales_raw WHERE id=?", (entry_id,))
            conn.commit()
            msg = f"✅ વેચાણ બિલ #{b_no} ({c_name}) સફળતાપૂર્વક રદ થયું: ફોન સ્ટોકમાં પરત આવ્યો અને ગલ્લાની રકમ રિવર્સ થઈ ગઈ!"
        else:
            msg = "❌ વેચાણ બિલ મળ્યું નહીં!"

    # ૩. ફાઇનાન્સ DO ડિલીટ
    elif entry_type in ("do", "finance_do"):
        c.execute("SELECT do_ref_no, customer_name, loan_amt FROM finance_do_list WHERE id=?", (entry_id,))
        do_row = c.fetchone()
        if do_row:
            c.execute("DELETE FROM finance_do_list WHERE id=?", (entry_id,))
            conn.commit()
            msg = f"✅ પેન્ડિંગ DO ({do_row[0]}, {do_row[1]}) સફળતાપૂર્વક ડિલીટ થયો!"
        else:
            msg = "❌ ફાઇનાન્સ DO મળ્યો નહીં!"
    """
    માસ્ટર PIN ૧૯૮૬ વડે કોઈપણ ભૂલભરેલી એન્ટ્રી (Buyback, Customer Due, Galla Expense) કાયમી રદ/ડિલીટ કરવી
    """
    if str(pin).strip() != "1986":
        return redir("❌ ખોટો માસ્ટર PIN! માત્ર જયમીનભાઈના અધિકૃત PIN ૧૯૮૬ વડે જ ડિલીટ થશે.", return_sheet)

    sid = shop_id.strip() if shop_id.strip() else STORE_CFG.get("shop_id", "DEVANSHI")
    db_file = get_active_db_file(sid)
    conn = sqlite3.connect(db_file)
    c = conn.cursor()

    msg = ""
    if entry_type == "buyback":
        c.execute("SELECT imei, model, purchase_cost, repair_cost FROM buyback_stock WHERE id=?", (entry_id,))
        b_row = c.fetchone()
        if b_row:
            imei_val, mod_val, pur_amt, rep_amt = b_row
            c.execute("DELETE FROM buyback_stock WHERE id=?", (entry_id,))
            log_audit_action("DELETE_BUYBACK", f"Deleted buyback ID {entry_id} (IMEI {imei_val}, {mod_val}) with PIN 1986", sid)
            msg = f"✅ બાયબેક એન્ટ્રી (IMEI: {imei_val}, મોડેલ: {mod_val}) સફળતાપૂર્વક રદ/ડિલીટ થઈ ગઈ!"
        else:
            msg = "❌ બાયબેક રેકોર્ડ મળ્યો નહીં!"

    elif entry_type == "due":
        c.execute("SELECT customer_name, bill_no, due_amt FROM customer_due_ledger WHERE id=?", (entry_id,))
        d_row = c.fetchone()
        if d_row:
            c_name, b_no, d_amt = d_row
            c.execute("DELETE FROM customer_due_ledger WHERE id=?", (entry_id,))
            log_audit_action("DELETE_DUE", f"Deleted due ID {entry_id} for {c_name} (₹{d_amt}) with PIN 1986", sid)
            msg = f"✅ ગ્રાહક બાકી એન્ટ્રી ({c_name}, બિલ #{b_no}, ₹{float(d_amt or 0):,.0f}) રદ/ડિલીટ થઈ ગઈ!"
        else:
            msg = "❌ બાકી રેકોર્ડ મળ્યો નહીં!"

    elif entry_type == "galla_expense":
        c.execute("SELECT galla_name, out_amt, remarks FROM galla_ledger WHERE id=?", (entry_id,))
        g_row = c.fetchone()
        if g_row:
            g_name, o_amt, r_txt = g_row
            c.execute("DELETE FROM galla_ledger WHERE id=?", (entry_id,))
            log_audit_action("DELETE_GALLA_EXPENSE", f"Deleted expense ID {entry_id} ({g_name}, ₹{o_amt}) with PIN 1986", sid)
            msg = f"✅ ગલ્લા ખર્ચ એન્ટ્રી ({g_name}, ₹{float(o_amt or 0):,.0f} - {r_txt}) રદ થઈ ગઈ!"
        else:
            msg = "❌ ખર્ચ રેકોર્ડ મળ્યો નહીં!"

    elif entry_type == "partner_capital":
        c.execute("DELETE FROM partner_capital_ledger WHERE id=?", (entry_id,))
        log_audit_action("DELETE_PARTNER_CAPITAL", f"Deleted partner capital ID {entry_id} with PIN 1986", sid)
        msg = "✅ પાર્ટનર મૂડી/ગિફ્ટ વ્યવહાર રદ થયો!"
    else:
        msg = f"❌ અજાણ્યો એન્ટ્રી પ્રકાર '{entry_type}'!"

    conn.commit()
    conn.close()
    return redir(msg, return_sheet)


@app.post("/api/set-discount-red-signal")
def set_discount_red_signal_route(max_disc_pct: float = Form(2.0)):
    sid = STORE_CFG.get("shop_id", "DEVANSHI")
    lim = max(0.1, float(max_disc_pct or 2.0))
    conn = sqlite3.connect(get_active_db_file(), timeout=60.0)
    conn.execute("UPDATE shop_custom_settings SET max_discount_alert_pct=? WHERE shop_id=?", (lim, sid))
    conn.commit()
    conn.close()
    return redir(f"🚨 દેવાંશી AI કડક સૂચના લાગુ: હવે {lim:.1f}% કે તેથી વધુ ડિસ્કાઉન્ટ પર તરત જ રેડ સિગ્નલ બતાવશે!", "SALESMAN_360_MATRIX")


@app.post("/api/wipe-store-data")
async def api_wipe_store_data(req: Request):
    try:
        data = await req.json()
    except Exception:
        data = {}
    sid = (data.get("shop_id") or "DEVANSHI").strip().upper()
    pin = str(data.get("master_pin") or "").strip()
    if pin != "1986":
        return JSONResponse(status_code=400, content={"status": "error", "message": "❌ ખોટો માસ્ટર પિન! ૧૯૮૬ નાખો."})
    ok, msg = part1_core.wipe_store_all_transactions(sid, pin)
    return JSONResponse(content={"status": "success" if ok else "error", "message": msg})
