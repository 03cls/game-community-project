# -*- coding: utf-8 -*-
"""把 WebFetch 抓取的 Steam appdetails 原始 JSON 合并生成 steam_data.json。

用法：python -m app.db.build_steam_data
输出：app/db/steam_data.json  {appid: {desc, is_free, price_initial, price_final, discount, screenshots[]}}
"""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
TMP = r"C:\Users\ABC\AppData\Local\Temp\trae\toolcall-output"

# 持久化文件 -> appid
FILES = {
    "d75a53aa-48f6-4ecb-86ce-080a2182578b.txt": 1245620,
    "0e982af9-dff8-4bc0-b5b9-549017ff98ed.txt": 1086940,
    "07f3ee97-f7e3-46a6-9f9a-aa9eeecd8c07.txt": 2358720,
    "4ac409d5-c16e-4739-9a21-87e5fa860786.txt": 1091500,
    "b1b208bb-b0a9-461b-8aa9-3f8614eaef52.txt": 1174180,
    "07613951-0780-4f9d-a29b-00815f233147.txt": 292030,
    "7e642ebc-c44b-491e-ba14-f3d96a0ec217.txt": 730,
    "813b607c-aaf2-420e-9706-b608bf0bc619.txt": 1145360,
    "565a5dfe-cb25-4fa1-b91f-aeda90b43485.txt": 289070,
    "d9bd0946-41d5-40e7-a600-6ffa32ef38f9.txt": 1551360,
    "468cea1c-d324-43c8-a0a3-2164a7f10756.txt": 367520,
    "69ff216f-02fe-4dd4-824e-1a3dd8c86d19.txt": 578080,
    "1c8138b8-985c-4b96-b1fa-b5d2a203a759.txt": 1172470,
    "02d8442b-0036-462d-90d5-b08dc9392dc3.txt": 782330,
    "eec70d3b-ad4b-4f93-bd8b-58c91008d363.txt": 489830,
    "4e4fdcca-1938-4cd4-b633-a6834b43b208.txt": 377160,
    "f51aad88-3697-476e-82e7-0aa506e5c945.txt": 1328670,
    "d5d9037f-1efe-4883-81e9-fb1ef3fcd7ed.txt": 271590,
    "544ca07e-4315-4238-b267-148b7f206783.txt": 690790,
}

# 浏览器内联返回的小响应手工收录（前 5 张截图 + 价格）
INLINE = {
    413150: {"price": ("", "¥ 48.00", 0), "ss": [
        "https://shared.akamai.steamstatic.com/store_item_assets/steam/apps/413150/ss_b887651a93b0525739049eb4194f633de2df75be.1920x1080.jpg",
        "https://shared.akamai.steamstatic.com/store_item_assets/steam/apps/413150/ss_9ac899fe2cda15d48b0549bba77ef8c4a090a71c.1920x1080.jpg",
        "https://shared.akamai.steamstatic.com/store_item_assets/steam/apps/413150/ss_4fa0866709ede3753fdf2745349b528d5e8c4054.1920x1080.jpg",
        "https://shared.akamai.steamstatic.com/store_item_assets/steam/apps/413150/ss_d836f0a5b0447fb6a2bdb0a6ac5f954949d3c41e.1920x1080.jpg",
        "https://shared.akamai.steamstatic.com/store_item_assets/steam/apps/413150/ss_bf13aa0d1cb4064631931c7047748e2bd69c6c05.1920x1080.jpg"]},
    814380: {"price": ("", "¥ 268.00", 0), "ss": [
        "https://shared.akamai.steamstatic.com/store_item_assets/steam/apps/814380/ss_53d73aff4d439cbd9b9b69430f9b3b6db8d0ecd7.1920x1080.jpg",
        "https://shared.akamai.steamstatic.com/store_item_assets/steam/apps/814380/ss_2685dd844a2a523b6c7ec207d46a538db6a908cd.1920x1080.jpg",
        "https://shared.akamai.steamstatic.com/store_item_assets/steam/apps/814380/ss_15f0e9982621aed44900215ad283811af0779b1d.1920x1080.jpg",
        "https://shared.akamai.steamstatic.com/store_item_assets/steam/apps/814380/ss_1e6f5540866a5564d65df915c22fe1e57e336a6f.1920x1080.jpg",
        "https://shared.akamai.steamstatic.com/store_item_assets/steam/apps/814380/ss_3d6b38c382c0eafb02dc90d22f33fd292e4e5cf3.1920x1080.jpg"]},
    601150: {"price": ("¥ 148.00", "¥ 37.00", 75), "ss": [
        "https://shared.akamai.steamstatic.com/store_item_assets/steam/apps/601150/ss_4410bada2565843dae693b03ac3a50256ff5dd66.1920x1080.jpg",
        "https://shared.akamai.steamstatic.com/store_item_assets/steam/apps/601150/ss_4ce180ed8979a51c72de51f985e9e9ba13500508.1920x1080.jpg",
        "https://shared.akamai.steamstatic.com/store_item_assets/steam/apps/601150/ss_e2be70565f94a7f6c392cccddce08c67f2f87612.1920x1080.jpg",
        "https://shared.akamai.steamstatic.com/store_item_assets/steam/apps/601150/ss_d1e0b403f593f17ad195c5382a7788d71c6f406a.1920x1080.jpg",
        "https://shared.akamai.steamstatic.com/store_item_assets/steam/apps/601150/ss_f669d4627db07e61b87728d94d72bc1eabfd0349.1920x1080.jpg"]},
    582010: {"price": ("", "¥ 148.00", 0), "ss": [
        "https://shared.akamai.steamstatic.com/store_item_assets/steam/apps/582010/ss_a262c53b8629de7c6547933dc0b49d31f4e1b1f1.1920x1080.jpg",
        "https://shared.akamai.steamstatic.com/store_item_assets/steam/apps/582010/ss_6b4986a37c7b5c185a796085c002febcdd5357b5.1920x1080.jpg",
        "https://shared.akamai.steamstatic.com/store_item_assets/steam/apps/582010/ss_0dfb20f6f09c196bfc317bd517dc430ed6e6a2a4.1920x1080.jpg",
        "https://shared.akamai.steamstatic.com/store_item_assets/steam/apps/582010/ss_25902a9ae6977d6d10ebff20b87e8739e51c5b8b.1920x1080.jpg",
        "https://shared.akamai.steamstatic.com/store_item_assets/steam/apps/582010/ss_681cc5358ec55a997aee9f757ffe8b418dc79a32.1920x1080.jpg"]},
    588650: {"price": ("", "¥ 80.00", 0), "ss": [
        "https://shared.akamai.steamstatic.com/store_item_assets/steam/apps/588650/ss_ac28000ade40cc2fe5c128f32ac98ba33c008a7a.1920x1080.jpg",
        "https://shared.akamai.steamstatic.com/store_item_assets/steam/apps/588650/ss_7bde51ea6c8f6289e85ea1d8c1c941e1f8bfee91.1920x1080.jpg",
        "https://shared.akamai.steamstatic.com/store_item_assets/steam/apps/588650/ss_e87e72a247918d8493892e035d5e1b4b84470d2f.1920x1080.jpg",
        "https://shared.akamai.steamstatic.com/store_item_assets/steam/apps/588650/ss_a099416b9f3e09d47c42f87667e6ad6f394ba652.1920x1080.jpg",
        "https://shared.akamai.steamstatic.com/store_item_assets/steam/apps/588650/ss_a8b0439ad7750cab1bdec86ecef0daa280e9f93f.1920x1080.jpg"]},
    990080: {"price": ("", "¥ 384.00", 0), "ss": [
        "https://shared.akamai.steamstatic.com/store_item_assets/steam/apps/990080/ss_725bf58485beb4aa37a3a69c1e2baa69bf3e4653.1920x1080.jpg",
        "https://shared.akamai.steamstatic.com/store_item_assets/steam/apps/990080/ss_df93b5e8a183f7232d68be94ae78920a90de1443.1920x1080.jpg",
        "https://shared.akamai.steamstatic.com/store_item_assets/steam/apps/990080/ss_94058497bf0f8fabdde17ee8d59bece609a60663.1920x1080.jpg",
        "https://shared.akamai.steamstatic.com/store_item_assets/steam/apps/990080/ss_8e08976236d29b1897769257ac3c64e9264792a5.1920x1080.jpg",
        "https://shared.akamai.steamstatic.com/store_item_assets/steam/apps/990080/ss_d4930d675af053dc1e61a876a34fc003e85e261f.1920x1080.jpg"]},
    1151640: {"price": None, "ss": [
        "https://shared.akamai.steamstatic.com/store_item_assets/steam/apps/1151640/ss_d09106060fb7de8bf342c23df18b14debc8a15a3.1920x1080.jpg",
        "https://shared.akamai.steamstatic.com/store_item_assets/steam/apps/1151640/ss_271f850eec3f96b22aa17be35b948268e0771c7f.1920x1080.jpg",
        "https://shared.akamai.steamstatic.com/store_item_assets/steam/apps/1151640/ss_15f5759c441e4e5f51e1a8ee333e4ab9df9aa783.1920x1080.jpg",
        "https://shared.akamai.steamstatic.com/store_item_assets/steam/apps/1151640/ss_f7cf51f1ccd909264f2c5814f328e3f72e7b62bd.1920x1080.jpg",
        "https://shared.akamai.steamstatic.com/store_item_assets/steam/apps/1151640/ss_9db45aa04e8c8b5043b479f42ed36296bfc3a918.1920x1080.jpg"]},
    1190460: {"price": None, "ss": [
        "https://shared.akamai.steamstatic.com/store_item_assets/steam/apps/1190460/ss_ac7c64c8d10bb5786694891e4a22b07a5da7dd6f.1920x1080.jpg",
        "https://shared.akamai.steamstatic.com/store_item_assets/steam/apps/1190460/ss_4370916476e44c78b50bfee175f1d82285f6bfd7.1920x1080.jpg",
        "https://shared.akamai.steamstatic.com/store_item_assets/steam/apps/1190460/ss_39f107106c83eb3717a1061fa1da0f2f4bdf3993.1920x1080.jpg",
        "https://shared.akamai.steamstatic.com/store_item_assets/steam/apps/1190460/ss_c1d15216b7e8ccbcb73f462c4eaf6ef564679c94.1920x1080.jpg",
        "https://shared.akamai.steamstatic.com/store_item_assets/steam/apps/1190460/ss_a844f976c086d72f91de4a30a38c80e781988653.1920x1080.jpg"]},
    255710: {"price": ("", "¥ 138.00", 0), "ss": [
        "https://shared.akamai.steamstatic.com/store_item_assets/steam/apps/255710/ss_0754001c88ad4dbfff92faf9a97e8d87cf3f8840.1920x1080.jpg",
        "https://shared.akamai.steamstatic.com/store_item_assets/steam/apps/255710/ss_e0f842c9327df9defabf120b6c59e1ba42f54a75.1920x1080.jpg",
        "https://shared.akamai.steamstatic.com/store_item_assets/steam/apps/255710/ss_b5a4b72062b8c4ad677b242963e88c2e624cb1f9.1920x1080.jpg",
        "https://shared.akamai.steamstatic.com/store_item_assets/steam/apps/255710/ss_39f74526167020dfae4156945f24e7e49d5eedf8.1920x1080.jpg",
        "https://shared.akamai.steamstatic.com/store_item_assets/steam/apps/255710/ss_a4ebf2b3ad46e620d99fa471708d68b28ea4d7d1.1920x1080.jpg"]},
    294100: {"price": ("", "¥ 128.00", 0), "ss": [
        "https://shared.akamai.steamstatic.com/store_item_assets/steam/apps/294100/80e383ef19353058791efe17a6485849246c9c17/ss_80e383ef19353058791efe17a6485849246c9c17.1920x1080.jpg",
        "https://shared.akamai.steamstatic.com/store_item_assets/steam/apps/294100/a6158c5cef23ac8157b37dd3eb17f3c2d2649e93/ss_a6158c5cef23ac8157b37dd3eb17f3c2d2649e93.1920x1080.jpg",
        "https://shared.akamai.steamstatic.com/store_item_assets/steam/apps/294100/cccfece4c643fd32d438642fbea1b980bc519a48/ss_cccfece4c643fd32d438642fbea1b980bc519a48.1920x1080.jpg",
        "https://shared.akamai.steamstatic.com/store_item_assets/steam/apps/294100/57c3e8d556d47bb5ad048699643528aefc652aa6/ss_57c3e8d556d47bb5ad048699643528aefc652aa6.1920x1080.jpg",
        "https://shared.akamai.steamstatic.com/store_item_assets/steam/apps/294100/59a1400eff99e2b620d623d3d76a02c1592a72e7/ss_59a1400eff99e2b620d623d3d76a02c1592a72e7.1920x1080.jpg"]},
    268500: {"price": ("", "¥ 99.00", 0), "ss": [
        "https://shared.akamai.steamstatic.com/store_item_assets/steam/apps/268500/ss_a95cdbe487dbabf6621962fc92f438e26c5fdfd3.1920x1080.jpg",
        "https://shared.akamai.steamstatic.com/store_item_assets/steam/apps/268500/ss_ca76303e136d2ea500b8e6546d4319502ae8862a.1920x1080.jpg",
        "https://shared.akamai.steamstatic.com/store_item_assets/steam/apps/268500/ss_200cb06b3ff1b9af8d445d349391554ac48635b4.1920x1080.jpg",
        "https://shared.akamai.steamstatic.com/store_item_assets/steam/apps/268500/ss_b2694a32e6211c47b886ee76eabdbcc41cf4b408.1920x1080.jpg",
        "https://shared.akamai.steamstatic.com/store_item_assets/steam/apps/268500/ss_50b987ea0074e44de58a9b4df87efb529cc8f625.1920x1080.jpg"]},
}


def strip_tag(html: str) -> str:
    import re
    text = re.sub(r"<[^>]+>", " ", html or "")
    return re.sub(r"\s+", " ", text).strip()


def _extract_string(raw: str, key: str) -> str:
    """容忍控制字符/截断的 JSON 字符串提取（WebFetch 持久化文件非严格 JSON）。"""
    import re
    m = re.search(r'"' + key + r'"\s*:\s*"', raw)
    if not m:
        return ""
    i = m.end()
    out = []
    while i < len(raw):
        ch = raw[i]
        if ch == "\\" and i + 1 < len(raw):
            nxt = raw[i + 1]
            if nxt == '"':
                out.append('"')
            elif nxt == "n":
                out.append(" ")
            elif nxt == "/":
                out.append("/")
            elif nxt == "u":
                try:
                    out.append(chr(int(raw[i + 2:i + 6], 16)))
                    i += 4
                except ValueError:
                    pass
            else:
                out.append(nxt)
            i += 2
            continue
        if ch == '"':
            break
        out.append(ch)
        i += 1
    return "".join(out)


def _extract_price(raw: str):
    import re
    m = re.search(r'"price_overview"\s*:\s*\{', raw)
    if not m:
        return ("", "", 0)
    seg = raw[m.end():m.end() + 800].split("}", 1)[0]
    init = _extract_string(seg, "initial_formatted")
    fin = _extract_string(seg, "final_formatted")
    dm = re.search(r'"discount_percent"\s*:\s*(\d+)', seg)
    return (init, fin, int(dm.group(1)) if dm else 0)


def _extract_shots(raw: str):
    import re
    norm = raw.replace("\\/", "/")
    shots = re.findall(r'https://[^"\s]+?ss_[0-9a-f]{8,}\.1920x1080\.jpg', norm)
    seen, out = set(), []
    for s in shots:
        s = s.split("?t=")[0]
        if s not in seen:
            seen.add(s)
            out.append(s)
    return out[:6]


def _loose_extract(raw: str) -> dict:
    desc = _extract_string(raw, "short_description") or strip_tag(_extract_string(raw, "about_the_game"))
    init, fin, disc = _extract_price(raw)
    return {
        "desc": desc,
        "is_free": '"is_free":true' in raw,
        "price_initial": init,
        "price_final": fin,
        "discount": disc,
        "screenshots": _extract_shots(raw),
    }


def main() -> None:
    out = {}
    for fname, appid in FILES.items():
        path = os.path.join(TMP, fname)
        if not os.path.exists(path):
            print("missing:", fname)
            continue
        with open(path, "r", encoding="utf-8") as f:
            raw = f.read().strip()
        item = _loose_extract(raw)
        if not item["screenshots"]:
            print("warn: no screenshots in", fname)
        out[str(appid)] = item

    # 追加用 filters=price_overview,screenshots 精准补抓的数据（修正截断/美元价/缺图）
    _A = "https://shared.akamai.steamstatic.com/store_item_assets/steam/apps/%s/%s.1920x1080.jpg"
    PATCH = {
        "1086940": {"price_final": "¥ 298.00", "screenshots": [
            _A % ("1086940", "ss_c73bc54415178c07fef85f54ee26621728c77504"),
            _A % ("1086940", "ss_73d93bea842b93914d966622104dcb8c0f42972b"),
            _A % ("1086940", "ss_cf936d31061b58e98e0c646aee00e6030c410cda"),
            _A % ("1086940", "ss_b6a6ee6e046426d08ceea7a4506a1b5f44181543"),
            _A % ("1086940", "ss_6b8faba0f6831a406ce015648958da9612d14dbb"),
            _A % ("1086940", "ss_8fc5eba770b4a1639b31666908bdd2bbc1aa2ae4")]},
        "367520": {"price_final": "¥ 58.00", "screenshots": [
            _A % ("367520", "ss_5384f9f8b96a0b9934b2bc35a4058376211636d2"),
            _A % ("367520", "ss_d5b6edd94e77ba6db31c44d8a3c09d807ab27751"),
            _A % ("367520", "ss_a81e4231cc8d55f58b51a4a938898af46503cae5"),
            _A % ("367520", "ss_62e10cf506d461e11e050457b08aa0e2a1c078d0"),
            _A % ("367520", "ss_bd76bd88bc5334ee56ae3d5f0d8dec4455e8e3b8"),
            _A % ("367520", "ss_33a645903d6dd9beec39f272a3daf57174a6cc26")]},
        "377160": {"price_final": "¥ 83.00", "screenshots": [
            _A % ("377160", "ss_f7861bd71e6c0c218d8ff69fb1c626aec0d187cf"),
            _A % ("377160", "ss_910437ac708aed7c028f6e43a6224c633d086b0a"),
            _A % ("377160", "ss_f649b8e57749f380cca225db5074edbb1e06d7f5"),
            _A % ("377160", "ss_c310f858e6a7b02ffa21db984afb0dd1b24c1423"),
            _A % ("377160", "ss_5e2d136759e0ff4e0d74940fffc9c64e8cdcd833"),
            _A % ("377160", "ss_c6b798424a93617b4b825aea3bcd9547c0b0a5ce")]},
        "2358720": {"price_final": "¥ 268.00", "screenshots": [
            _A % ("2358720", "ss_86c4b7462bba219a0d0b89931a35812b9f188976"),
            _A % ("2358720", "ss_d9391ab31a4d15dddf7ba4949bfa44f5d9170580"),
            _A % ("2358720", "ss_524a39da392ee83dde091033562bc719d46b5838"),
            _A % ("2358720", "ss_968bbc9caceb7d798bd0c393e1e9b4c44ed6d835"),
            _A % ("2358720", "ss_415397426d4c939ebb8a93ac66831f28ee7199be"),
            _A % ("2358720", "ss_63477e8ce2c0582b81c6ed576377d78e692b5642")]},
        "1174180": {"price_initial": "¥ 279.00", "price_final": "¥ 69.75", "discount": 75},
    }
    for appid, patch in PATCH.items():
        tgt = out.setdefault(appid, {"desc": "", "is_free": False, "price_initial": "",
                                     "price_final": "", "discount": 0, "screenshots": []})
        for k, v in patch.items():
            if v:
                tgt[k] = v
    for appid, item in INLINE.items():
        price = item["price"]
        out[str(appid)] = {
            "desc": "",
            "is_free": False,
            "price_initial": price[0] if price else "",
            "price_final": price[1] if price else "",
            "discount": price[2] if price else 0,
            "screenshots": item["ss"],
        }
    dest = os.path.join(HERE, "steam_data.json")
    with open(dest, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    print("written:", dest, len(out), "games")


if __name__ == "__main__":
    main()
